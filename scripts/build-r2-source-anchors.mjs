// Build a source-backed R2 anchor prototype from local csl-orig.
//
// This is not the restored final R2 splitter. It implements the next
// reproducibility rung: resolve the archived anchor lemmas against source
// records, aggregate all matching homonym blocks, emit provisional sense rows,
// and compare the source-backed rows to the recovered static fixtures.
//
// Usage: npm run build-r2-source-anchors

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { iterateDict, dictExists } from "./lib/dict-parser.mjs";
import { normalizeLemma } from "./lib/dict-normalize.mjs";

const OUT_DIR = path.resolve(process.cwd(), "data", "lexico");
const SUMMARY_OUT = path.join(OUT_DIR, "r2_source_anchor_summary.json");
const ROWS_OUT = path.join(OUT_DIR, "r2_source_anchor_senses.jsonl");
const ALIGN_OUT = path.join(OUT_DIR, "r2_source_anchor_alignments.json");
const ARCHIVE_EXPLORER = path.join(OUT_DIR, "r2_archive_explorer.json");

export const R2_ANCHOR_LEMMAS = [
  { lemma: "gam", lookupKeys: ["gam"] },
  { lemma: "dharma", lookupKeys: ["Darma", "DarmaH", "Darmma", "DarmmaH", "dharma"] },
  { lemma: "rama", lookupKeys: ["rAma", "rama"] },
  { lemma: "iti", lookupKeys: ["iti"] },
  { lemma: "bodhisattva", lookupKeys: ["boDisattva", "boDisattvaH", "boDisattvaM", "bodhisattva"] }
];

const R2_DICTS = [
  { code: "mw", label: "MW 1899", parserFamily: "western", cluster: "western", split: "lumped-proxy" },
  { code: "mw72", label: "MW 1872", parserFamily: "western", cluster: "western", split: "lumped-proxy" },
  { code: "pwg", label: "PWG 1855", parserFamily: "western", cluster: "western", split: "div" },
  { code: "pw", label: "PWK", parserFamily: "western", cluster: "western", split: "div" },
  { code: "ap", label: "Apte 1957", parserFamily: "western", cluster: "western", split: "ap-bullet" },
  { code: "ap90", label: "Apte 1890", parserFamily: "western", cluster: "western", split: "number-marker" },
  { code: "ben", label: "Benfey 1866", parserFamily: "western", cluster: "western", split: "number-marker" },
  { code: "sch", label: "Schmidt 1928", parserFamily: "western", cluster: "western", split: "lumped-proxy" },
  { code: "bhs", label: "Edgerton BHS 1953", parserFamily: "western", cluster: "western", split: "number-marker" },
  { code: "wil", label: "Wilson 1832", parserFamily: "western", cluster: "western", split: "dot-squared" },
  { code: "cae", label: "Cappeller 1891", parserFamily: "western", cluster: "western", split: "lumped-proxy" },
  { code: "vcp", label: "Vacaspatya 1873", parserFamily: "indigenous", cluster: "indigenous", split: "iti-unit" },
  { code: "skd", label: "Sabdakalpadruma 1822", parserFamily: "indigenous", cluster: "indigenous", split: "iti-unit" },
  { code: "ae", label: "Apte EN->SA 1884", parserFamily: "reverse", cluster: "reverse", split: "reverse-equivalent" }
];

const MARKERS = {
  div: /<div\b(?:[^>]*?\bn=["']?([^"'>\s]+))?[^>]*>/g,
  "ap-bullet": /\u2219\u00B2\s*(\d+)/g,
  "number-marker": /\{@\s*(?:--)?(\d+)\.?\s*@\}/g,
  "dot-squared": /\.\u00B2\s*(\d+)/g
};

const SLP_TOKEN = /[A-Za-z][A-Za-z~/\\^']*/g;
const MARKED_SANSKRIT = [
  /\{#([\s\S]*?)#\}/g,
  /\{@([A-Za-z][^@{}]{1,80})@\}/g,
  /<s>([\s\S]*?)<\/s>/g
];
const LS_TAG = /<ls(?:\s+n=["']([^"']+)["'])?[^>]*>([\s\S]*?)<\/ls>/g;

export function lookupKeysForLemma(lemma) {
  return R2_ANCHOR_LEMMAS.find(row => row.lemma === lemma)?.lookupKeys ?? [lemma];
}

export function jaccard(left, right) {
  const a = new Set(left);
  const b = new Set(right);
  if (!a.size && !b.size) return 0;
  let intersection = 0;
  for (const value of a) if (b.has(value)) intersection += 1;
  return intersection / (a.size + b.size - intersection);
}

export function splitExplicitMarkers(body, marker, options = {}) {
  const { useMarkerLabelAsLocalId = true } = options;
  marker.lastIndex = 0;
  const matches = [...body.matchAll(marker)];
  if (!matches.length) {
    return [{ localId: "bundle", splitConfidence: "lumped-proxy", text: body }];
  }

  const parts = [];
  const preface = body.slice(0, matches[0].index).trim();
  if (preface) {
    parts.push({ localId: "preface", splitConfidence: "lumped-proxy", text: preface });
  }

  let markerRunIndex = 0;
  let previousMarkerNumber = null;
  for (let i = 0; i < matches.length; i++) {
    const start = matches[i].index;
    const end = i + 1 < matches.length ? matches[i + 1].index : body.length;
    const markerLabel = matches[i][1] ? String(matches[i][1]).replace(/[^\w.-]+/g, "_") : null;
    const localId = useMarkerLabelAsLocalId && markerLabel ? markerLabel : String(i + 1);
    const markerNumber = Number(markerLabel);
    if (
      Number.isFinite(markerNumber) &&
      Number.isFinite(previousMarkerNumber) &&
      markerNumber === 1 &&
      previousMarkerNumber > 1
    ) {
      markerRunIndex += 1;
    }
    if (Number.isFinite(markerNumber)) previousMarkerNumber = markerNumber;
    const text = body.slice(start, end).trim();
    if (text) {
      parts.push({
        localId,
        ...(markerLabel ? { markerLabel } : {}),
        ...(Number.isFinite(markerNumber) ? { markerRunIndex } : {}),
        splitConfidence: "explicit",
        text
      });
    }
  }
  return parts;
}

function splitIndigenous(body) {
  const parts = [];
  const marker = /\biti\b\s*\.?/g;
  let start = 0;
  let count = 0;
  for (const match of body.matchAll(marker)) {
    const end = match.index + match[0].length;
    const text = body.slice(start, end).trim();
    if (text) {
      count += 1;
      parts.push({ localId: String(count), splitConfidence: "iti-unit", text });
    }
    start = end;
  }
  const tail = body.slice(start).trim();
  if (tail) {
    count += 1;
    parts.push({ localId: String(count), splitConfidence: count > 1 ? "iti-unit" : "lumped-proxy", text: tail });
  }
  return parts.length ? parts : [{ localId: "bundle", splitConfidence: "iti-unit", text: body }];
}

function splitRecord(body, dict) {
  if (dict.split === "iti-unit") return splitIndigenous(body);
  const marker = MARKERS[dict.split];
  if (dict.split === "div" && marker) return splitExplicitMarkers(body, marker, { useMarkerLabelAsLocalId: false });
  return marker ? splitExplicitMarkers(body, marker) : [{ localId: "bundle", splitConfidence: dict.split, text: body }];
}

function cleanText(text, max = 220) {
  const cleaned = (text ?? "")
    .replace(/<[^>]+>/g, " ")
    .replace(/\{[#%@]?/g, " ")
    .replace(/[#%@]?\}/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  return cleaned.length > max ? `${cleaned.slice(0, max - 1)}...` : cleaned;
}

function normalizeAnchor(token) {
  return normalizeLemma(token).normalized.replace(/^[-.]+|[-.]+$/g, "");
}

function tokenList(text) {
  const out = [];
  for (const match of text.matchAll(SLP_TOKEN)) {
    const token = normalizeAnchor(match[0]);
    if (token.length >= 2 && !/^\d+$/.test(token)) out.push(token);
  }
  return out;
}

function uniqueSorted(values) {
  return [...new Set(values.filter(Boolean))].sort((a, b) => a.localeCompare(b));
}

function countValues(values) {
  const counts = {};
  for (const value of values.filter(value => value !== undefined && value !== null && value !== "")) {
    counts[value] = (counts[value] || 0) + 1;
  }
  return Object.fromEntries(Object.entries(counts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
}

export function sourceRecordCounts(rows, limit = 8) {
  const counts = new Map();
  for (const row of rows) {
    const blockId = row.blockIds?.[0] ?? "";
    const sourceLine = row.sourceLine ?? "";
    const key = `${blockId}\t${sourceLine}\t${row.href ?? ""}`;
    const current = counts.get(key) ?? { blockId, rawHeadword: row.rawHeadword, sourceLine, href: row.href, rowCount: 0 };
    current.rowCount += 1;
    counts.set(key, current);
  }
  return [...counts.values()]
    .sort((a, b) =>
      b.rowCount - a.rowCount ||
      String(a.blockId).localeCompare(String(b.blockId), undefined, { numeric: true }) ||
      Number(a.sourceLine || 0) - Number(b.sourceLine || 0)
    )
    .slice(0, limit);
}

function extractMarkedSanskritGroups(body) {
  const matches = [];
  for (const pattern of MARKED_SANSKRIT) {
    pattern.lastIndex = 0;
    for (const match of body.matchAll(pattern)) {
      if (/^\s*(?:--)?\d+\.?\s*$/.test(match[1])) continue;
      matches.push({ index: match.index, text: match[1] });
    }
  }

  const groups = [];
  matches.sort((a, b) => a.index - b.index);
  for (const match of matches) {
    const tokens = tokenList(match.text);
    if (tokens.length) groups.push(tokens);
  }
  return groups;
}
function extractMarkedSanskrit(body) {
  const tokens = [];
  for (const group of extractMarkedSanskritGroups(body)) tokens.push(...group);
  return tokens;
}

export function reverseMatchProfile(body, lookupKeySet) {
  const groups = extractMarkedSanskritGroups(body);
  const matchingGroupIndexes = [];
  for (let index = 0; index < groups.length; index++) {
    if (groups[index].some(token => lookupKeySet.has(normalizeAnchor(token)))) matchingGroupIndexes.push(index);
  }
  if (!matchingGroupIndexes.length) {
    return {
      rank: "no-match",
      firstGroupIndex: null,
      matchGroupCount: 0,
      equivalentGroupCount: groups.length,
      score: 0
    };
  }

  const firstGroupIndex = matchingGroupIndexes[0];
  const rank = firstGroupIndex <= 2
    ? "high"
    : firstGroupIndex <= 4
      ? "medium"
      : firstGroupIndex <= 9
        ? "low"
        : "tail";
  return {
    rank,
    firstGroupIndex,
    matchGroupCount: matchingGroupIndexes.length,
    equivalentGroupCount: groups.length,
    score: Number((1 / (firstGroupIndex + 1)).toFixed(3))
  };
}

function extractIndigenousTokens(body) {
  return tokenList(body).filter(token => token.length >= 4);
}

function extractCitationAnchors(body) {
  const anchors = [];
  LS_TAG.lastIndex = 0;
  for (const match of body.matchAll(LS_TAG)) {
    const value = cleanText(match[1] || match[2], 80).replace(/[.;:,]+$/g, "");
    if (value) anchors.push(`ls:${value}`);
  }
  return anchors;
}

function extractAuthoritySigla(body) {
  const sigla = [];
  for (const match of body.matchAll(/\b([A-Za-z][A-Za-z]+)0\b/g)) sigla.push(`sig:${match[1]}`);
  return sigla;
}

function anchorSets(text, dict, lookupKeySet) {
  const citationAnchors = extractCitationAnchors(text);
  if (dict.parserFamily === "indigenous") citationAnchors.push(...extractAuthoritySigla(text));

  const rawSanskrit = dict.parserFamily === "indigenous"
    ? extractIndigenousTokens(text)
    : extractMarkedSanskrit(text);
  const sanskritAnchors = uniqueSorted(rawSanskrit)
    .filter(token => !lookupKeySet.has(normalizeAnchor(token)))
    .slice(0, 80);

  return {
    sanskritAnchors,
    citationAnchors: uniqueSorted(citationAnchors).slice(0, 80)
  };
}

function hasEquivalent(body, lookupKeySet) {
  return extractMarkedSanskrit(body).some(token => lookupKeySet.has(normalizeAnchor(token)));
}

function rowFromPart(target, dict, rec, part, extra = {}) {
  const lookupKeySet = new Set(target.lookupKeys.map(normalizeAnchor));
  const blockId = rec.L || `line:${rec.startLine}`;
  const anchors = anchorSets(part.text, dict, lookupKeySet);
  return {
    rowId: `${target.lemma}:${dict.code}:${blockId}:${part.localId}`,
    dict: dict.code,
    dictLabel: dict.label,
    lemma: target.lemma,
    lookupKeys: target.lookupKeys,
    rawHeadword: rec.k1,
    blockIds: [blockId],
    sourceLine: rec.startLine,
    href: rec.href,
    senseId: `${blockId}:${part.localId}`,
    parserFamily: dict.parserFamily,
    splitConfidence: part.splitConfidence,
    ...(part.markerLabel != null ? { markerLabel: part.markerLabel } : {}),
    ...(part.markerRunIndex != null ? { markerRunIndex: part.markerRunIndex } : {}),
    text: cleanText(part.text),
    ...anchors,
    ...extra,
    limitations: limitationsFor(dict, part)
  };
}

function limitationsFor(dict, part) {
  const limitations = [];
  if (part.splitConfidence === "lumped-proxy") limitations.push("No explicit sense marker in this source span; row is a source block proxy.");
  if (dict.split === "iti-unit") limitations.push("Indigenous prose split on coarse iti-units; requires philological review.");
  if (dict.split === "reverse-equivalent") limitations.push("Reverse dictionary row selected by Sanskrit equivalent, not by headword.");
  if (dict.code === "ae") limitations.push("Common roots over-match in reverse lookup; equivalent-position rank is provided but filtering remains future work.");
  return limitations;
}

function buildNormalRows(target, dict) {
  const lookupKeySet = new Set(target.lookupKeys.map(normalizeAnchor));
  const rows = [];
  let sourceRecordCount = 0;
  for (const rec of iterateDict(dict.code)) {
    const normalized = normalizeAnchor(rec.k1 || "");
    if (!lookupKeySet.has(normalized)) continue;
    sourceRecordCount += 1;
    for (const part of splitRecord(rec.body || "", dict)) rows.push(rowFromPart(target, dict, rec, part));
  }
  return { rows, sourceRecordCount };
}

function buildReverseRows(target, dict) {
  const lookupKeySet = new Set(target.lookupKeys.map(normalizeAnchor));
  const rows = [];
  let sourceRecordCount = 0;
  for (const rec of iterateDict(dict.code)) {
    const reverseMatch = reverseMatchProfile(rec.body || "", lookupKeySet);
    if (reverseMatch.rank === "no-match") continue;
    sourceRecordCount += 1;
    const part = { localId: "equiv", splitConfidence: "reverse-equivalent", text: rec.body || "" };
    rows.push(rowFromPart(target, dict, rec, part, { reverseMatch }));
  }
  return { rows, sourceRecordCount };
}

function alignmentAnchors(row) {
  return [
    ...row.sanskritAnchors.map(value => `s:${value}`),
    ...row.citationAnchors
  ];
}

function strongShared(shared) {
  return shared.filter(value => {
    if (value.startsWith("ls:") || value.startsWith("sig:")) return true;
    return value.replace(/^s:/, "").length >= 4;
  });
}

function buildAlignments(rows) {
  const byLemma = new Map();
  for (const row of rows) {
    if (!byLemma.has(row.lemma)) byLemma.set(row.lemma, []);
    byLemma.get(row.lemma).push(row);
  }

  const lemmas = [];
  for (const [lemma, lemmaRows] of byLemma) {
    const alignments = [];
    for (let i = 0; i < lemmaRows.length; i++) {
      const left = lemmaRows[i];
      const leftAnchors = alignmentAnchors(left);
      if (!leftAnchors.length) continue;
      for (let j = i + 1; j < lemmaRows.length; j++) {
        const right = lemmaRows[j];
        if (left.dict === right.dict) continue;
        const rightAnchors = alignmentAnchors(right);
        if (!rightAnchors.length) continue;
        const shared = uniqueSorted(leftAnchors.filter(value => rightAnchors.includes(value)));
        const strong = strongShared(shared);
        if (!strong.length) continue;
        const score = jaccard(leftAnchors, rightAnchors);
        if (score < 0.02 && strong.length < 2) continue;
        alignments.push({
          a: left.rowId,
          b: right.rowId,
          dictA: left.dict,
          dictB: right.dict,
          parserFamilyA: left.parserFamily,
          parserFamilyB: right.parserFamily,
          jaccard: Number(score.toFixed(3)),
          shared: shared.slice(0, 24),
          crossTradition: left.parserFamily !== right.parserFamily
        });
      }
    }
    alignments.sort((a, b) =>
      b.jaccard - a.jaccard ||
      Number(b.crossTradition) - Number(a.crossTradition) ||
      a.a.localeCompare(b.a) ||
      a.b.localeCompare(b.b)
    );
    lemmas.push({
      lemma,
      rowCount: lemmaRows.length,
      alignmentCount: alignments.length,
      crossTraditionAlignmentCount: alignments.filter(row => row.crossTradition).length,
      alignments: alignments.slice(0, 80)
    });
  }
  return {
    schemaVersion: "0.1.0",
    status: "source-backed-r2-prototype",
    claim: "Prototype R2 alignments regenerated from current csl-orig anchor rows.",
    limitations: [
      "Rows are source-backed but the final R2 splitter is not restored.",
      "Alignment ranking uses provisional anchors and should be treated as a review worklist.",
      "AE reverse rows intentionally expose common-root overmatching and now carry equivalent-position rank metadata."
    ],
    lemmas: lemmas.sort((a, b) => a.lemma.localeCompare(b.lemma))
  };
}

function archiveCounts() {
  if (!fs.existsSync(ARCHIVE_EXPLORER)) return {};
  const archive = JSON.parse(fs.readFileSync(ARCHIVE_EXPLORER, "utf8"));
  const out = {};
  for (const lemma of archive.lemmas ?? []) {
    out[lemma.lemma] = {};
    for (const [dict, senses] of Object.entries(lemma.senses ?? {})) out[lemma.lemma][dict] = senses.length;
  }
  return out;
}

function summarize(rows, sourceRecordsByLemmaDict) {
  const archive = archiveCounts();
  const lemmaRows = [];
  for (const target of R2_ANCHOR_LEMMAS) {
    const byDict = [];
    for (const dict of R2_DICTS) {
      const here = rows.filter(row => row.lemma === target.lemma && row.dict === dict.code);
      const archiveSenseRows = archive[target.lemma]?.[dict.code] ?? 0;
      byDict.push({
        dict: dict.code,
        label: dict.label,
        parserFamily: dict.parserFamily,
        split: dict.split,
        sourceRecordCount: sourceRecordsByLemmaDict.get(`${target.lemma}:${dict.code}`) ?? 0,
        sourceRecordCounts: sourceRecordCounts(here),
        sourceSenseRows: here.length,
        archivedSenseRows: archiveSenseRows,
        splitConfidence: uniqueSorted(here.map(row => row.splitConfidence)),
        markerLabelCounts: countValues(here.map(row => row.markerLabel)),
        markerRunCounts: countValues(here.map(row => row.markerRunIndex)),
        sourceLines: here.slice(0, 5).map(row => row.sourceLine),
        ...(dict.parserFamily === "reverse" ? {
          reverseRankCounts: countValues(here.map(row => row.reverseMatch?.rank))
        } : {})
      });
    }
    lemmaRows.push({
      lemma: target.lemma,
      lookupKeys: target.lookupKeys,
      sourceSenseRows: byDict.reduce((sum, row) => sum + row.sourceSenseRows, 0),
      archivedSenseRows: byDict.reduce((sum, row) => sum + row.archivedSenseRows, 0),
      byDict
    });
  }

  return {
    schemaVersion: "0.1.0",
    status: "source-backed-r2-prototype",
    claim: "R2 anchor lemmas resolved against current local csl-orig sources.",
    sourceRoot: "../csl-orig/v02",
    generatedBy: "npm run build-r2-source-anchors",
    outputs: [
      "data/lexico/r2_source_anchor_summary.json",
      "data/lexico/r2_source_anchor_senses.jsonl",
      "data/lexico/r2_source_anchor_alignments.json"
    ],
    limitations: [
      "This is a prototype rebuild rung, not the restored final R2 package.",
      "Western explicit markers are split where source markup is clear; MW-family and other lumped dictionaries remain source-block proxies.",
      "Indigenous prose uses coarse iti-unit splitting and needs review labels.",
      "AE reverse lookup is source-backed but noisy for common roots."
    ],
    counts: {
      lemmaCount: R2_ANCHOR_LEMMAS.length,
      dictionaryCount: R2_DICTS.length,
      sourceSenseRows: rows.length,
      archivedSenseRows: lemmaRows.reduce((sum, row) => sum + row.archivedSenseRows, 0)
    },
    lemmas: lemmaRows
  };
}

function writeJson(file, payload) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, `${JSON.stringify(payload, null, 2)}\n`);
}

function main() {
  const rows = [];
  const sourceRecordsByLemmaDict = new Map();
  const warnings = [];

  for (const dict of R2_DICTS) {
    if (!dictExists(dict.code)) {
      warnings.push(`Missing source for ${dict.code}; skipped.`);
      continue;
    }
    for (const target of R2_ANCHOR_LEMMAS) {
      const result = dict.split === "reverse-equivalent"
        ? buildReverseRows(target, dict)
        : buildNormalRows(target, dict);
      sourceRecordsByLemmaDict.set(`${target.lemma}:${dict.code}`, result.sourceRecordCount);
      rows.push(...result.rows);
    }
  }

  rows.sort((a, b) =>
    a.lemma.localeCompare(b.lemma) ||
    a.dict.localeCompare(b.dict) ||
    a.sourceLine - b.sourceLine ||
    a.senseId.localeCompare(b.senseId)
  );

  const summary = summarize(rows, sourceRecordsByLemmaDict);
  if (warnings.length) summary.warnings = warnings;
  const alignments = buildAlignments(rows);

  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(ROWS_OUT, rows.map(row => JSON.stringify(row)).join("\n") + "\n");
  writeJson(SUMMARY_OUT, summary);
  writeJson(ALIGN_OUT, alignments);

  console.log(`Wrote ${path.relative(process.cwd(), SUMMARY_OUT)}`);
  console.log(`Wrote ${path.relative(process.cwd(), ROWS_OUT)} (${rows.length} rows)`);
  console.log(`Wrote ${path.relative(process.cwd(), ALIGN_OUT)}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
