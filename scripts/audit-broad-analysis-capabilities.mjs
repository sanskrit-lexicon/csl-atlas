// Audit how far the broad Sanskrit/BHS dictionary set can participate in the
// deep comparative Atlas analyses.
//
// This is intentionally diagnostic. It does not promote a dictionary to deep
// parity merely because a marker appears once; it records the observed evidence
// so dictionary-specific adapters can be added without guessing.

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import {
  CORE_COMPARISON_DICTS,
  buildBroadHeadwordDictionaries,
  excludedBroadHeadwordDictionaries
} from "./lib/dict-scope.mjs";
import { KOSHA_SYNONYM_CODES, iterateHeadwords } from "./lib/dict-headwords.mjs";
import { dictExists, genderForDict } from "./lib/dict-parser.mjs";
import { normalizeLemma } from "./lib/dict-normalize.mjs";
import { extractCitations } from "./lib/mw-classifiers.mjs";
import { featureAdapter } from "./lib/dict-feature-adapters.mjs";

const OUT = path.resolve(process.cwd(), "src", "data", "dicts", "analysis-capability-audit.json");
const SCHEMA_VERSION = "1.0.0";

const NUMBERED_SENSE_RE = /\{@\d+\.@\}/g;
const BULLET_RE = /∙/g;
const DIV_RE = /<div\b/g;
const LEX_RE = /<lex>[^<]*<\/lex>/g;
const ITI_RE = /\biti\b/g;

function countMatches(text, re) {
  re.lastIndex = 0;
  return (text.match(re) || []).length;
}

function pct(n, d) {
  return d ? Number(((100 * n) / d).toFixed(2)) : 0;
}

function familyUsesSanskritProse(dict) {
  const pair = String(dict.languagePair || "").toLowerCase();
  return pair === "skt-skt" || pair.includes("skt") && pair.endsWith("-skt");
}

function classifyGrammar(dict, stats) {
  const adapter = featureAdapter("grammar", dict.code);
  if (adapter?.status === "supported") return { status: "supported", method: adapter.methodId };
  if (KOSHA_SYNONYM_CODES.has(dict.code) && stats.genderRecords >= 100) {
    return { status: "candidate", method: "kosha-synonym-suffix" };
  }
  if (stats.genderRecords >= 100 && pct(stats.genderRecords, stats.records) >= 5) {
    return { status: "candidate", method: "lex-tag" };
  }
  return { status: "missing", method: null };
}

function classifyCitations(dict, stats) {
  const adapter = featureAdapter("citations", dict.code);
  if (adapter?.status === "supported") return { status: "supported", method: adapter.methodId };
  if (adapter) return { status: adapter.status, method: adapter.methodId };
  if (stats.lsCount >= 100) return { status: "candidate", method: "ls-tag" };
  if (familyUsesSanskritProse(dict) && stats.itiCount >= 100) {
    return { status: "candidate", method: "iti-prose" };
  }
  if (stats.lsCount || stats.itiCount) return { status: "weak", method: stats.lsCount ? "ls-tag" : "iti-prose" };
  return { status: "missing", method: null };
}

function classifyHomonyms(dict, stats) {
  const adapter = featureAdapter("homonyms", dict.code);
  if (adapter?.status === "supported") return { status: "supported", method: adapter.methodId };
  if (stats.hRecords >= 20) return { status: "candidate", method: "h-tag" };
  if (stats.hRecords) return { status: "weak", method: "h-tag" };
  return { status: "missing", method: null };
}

function classifySenses(dict, stats) {
  const adapter = featureAdapter("senses", dict.code);
  if (adapter?.status === "supported") return { status: "supported", method: adapter.methodId };
  if (stats.divCount >= 100) return { status: "candidate", method: "div" };
  if (stats.numberedSenseCount >= 100) return { status: "candidate", method: "numbered-brace" };
  if (stats.bulletCount >= 100) return { status: "candidate", method: "bullet" };
  if (stats.divCount || stats.numberedSenseCount || stats.bulletCount) {
    return {
      status: "weak",
      method: stats.divCount ? "div" : stats.numberedSenseCount ? "numbered-brace" : "bullet"
    };
  }
  return { status: "missing", method: null };
}

function auditDict(dict) {
  const stats = {
    records: 0,
    sourceRecords: 0,
    distinctLemmas: 0,
    hRecords: 0,
    lexRecords: 0,
    genderRecords: 0,
    lsRecords: 0,
    lsCount: 0,
    itiRecords: 0,
    itiCount: 0,
    divRecords: 0,
    divCount: 0,
    bulletRecords: 0,
    bulletCount: 0,
    numberedSenseRecords: 0,
    numberedSenseCount: 0
  };
  const lemmas = new Set();
  const seenSourceRecords = new Set();

  if (!dictExists(dict.code)) {
    return {
      ...dict,
      ...stats,
      capabilities: {
        grammar: { status: "missing", method: null },
        citations: { status: "missing", method: null },
        homonyms: { status: "missing", method: null },
        senses: { status: "missing", method: null }
      },
      warning: "Source file missing."
    };
  }

  for (const rec of iterateHeadwords(dict)) {
    if (!rec.k1) continue;
    stats.records += 1;
    const { normalized } = normalizeLemma(rec.k1);
    if (normalized) lemmas.add(normalized);

    const body = rec.body || "";
    if (genderForDict(dict.code, body) || rec.genderHint) stats.genderRecords += 1;

    const sourceKey = `${rec.startLine}:${rec.L ?? ""}`;
    if (seenSourceRecords.has(sourceKey)) continue;
    seenSourceRecords.add(sourceKey);
    stats.sourceRecords += 1;

    if (rec.h) stats.hRecords += 1;

    const lex = countMatches(body, LEX_RE);
    if (lex) stats.lexRecords += 1;

    const citations = extractCitations(body);
    if (citations.length) stats.lsRecords += 1;
    stats.lsCount += citations.length;

    const iti = countMatches(body, ITI_RE);
    if (iti) stats.itiRecords += 1;
    stats.itiCount += iti;

    const div = countMatches(body, DIV_RE);
    if (div) stats.divRecords += 1;
    stats.divCount += div;

    const bullet = countMatches(body, BULLET_RE);
    if (bullet) stats.bulletRecords += 1;
    stats.bulletCount += bullet;

    const numbered = countMatches(body, NUMBERED_SENSE_RE);
    if (numbered) stats.numberedSenseRecords += 1;
    stats.numberedSenseCount += numbered;
  }

  stats.distinctLemmas = lemmas.size;

  return {
    ...dict,
    ...stats,
    markerRates: {
      hRecordPct: pct(stats.hRecords, stats.sourceRecords || stats.records),
      lexRecordPct: pct(stats.lexRecords, stats.sourceRecords || stats.records),
      genderRecordPct: pct(stats.genderRecords, stats.records),
      lsRecordPct: pct(stats.lsRecords, stats.sourceRecords || stats.records),
      itiRecordPct: pct(stats.itiRecords, stats.sourceRecords || stats.records),
      divRecordPct: pct(stats.divRecords, stats.sourceRecords || stats.records),
      bulletRecordPct: pct(stats.bulletRecords, stats.sourceRecords || stats.records),
      numberedSenseRecordPct: pct(stats.numberedSenseRecords, stats.sourceRecords || stats.records)
    },
    capabilities: {
      grammar: classifyGrammar(dict, stats),
      citations: classifyCitations(dict, stats),
      homonyms: classifyHomonyms(dict, stats),
      senses: classifySenses(dict, stats)
    }
  };
}

function summarize(rows) {
  const features = ["grammar", "citations", "homonyms", "senses"];
  return Object.fromEntries(features.map(feature => {
    const counts = { supported: 0, candidate: 0, partial: 0, weak: 0, missing: 0 };
    for (const row of rows) {
      const status = row.capabilities[feature].status;
      counts[status] = (counts[status] || 0) + 1;
    }
    return [feature, counts];
  }));
}

function main() {
  const dictionaries = buildBroadHeadwordDictionaries();
  const rows = dictionaries.map(auditDict);
  const payload = {
    schemaVersion: SCHEMA_VERSION,
    generatedAt: new Date().toISOString(),
    sourceRoot: "../csl-orig/v02",
    dictionaryCount: rows.length,
    coreComparisonCount: CORE_COMPARISON_DICTS.length,
    summary: summarize(rows),
    dictionaries: rows,
    excludedFromSanskritHeadwordLookup: excludedBroadHeadwordDictionaries(),
    statusMeanings: {
      supported: "A validated feature adapter exists and public deep metrics may include it.",
      partial: "Diagnostic evidence exists, but it is not yet a supported public deep-metric adapter.",
      candidate: "Enough encoded evidence exists to build or validate a parser.",
      weak: "Some markers exist, but not enough to treat as reliable without inspection.",
      missing: "No useful marker evidence found by this audit."
    },
    assumptions: [
      "This audit measures encoded evidence, not philological quality.",
      "A candidate result means the dictionary deserves an adapter or parser validation pass before it is promoted.",
      "Equal-depth analysis requires dictionary-specific parsing for grammar, citations, homonymy, and sense segmentation; headword coverage alone is insufficient."
    ]
  };

  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, `${JSON.stringify(payload, null, 2)}\n`);

  console.log(`Audited ${rows.length} broad Sanskrit/BHS dictionaries.`);
  for (const [feature, counts] of Object.entries(payload.summary)) {
    console.log(`  ${feature}: ${Object.entries(counts).map(([k, v]) => `${k}=${v}`).join(", ")}`);
  }
  console.log(`Wrote ${path.relative(process.cwd(), OUT)}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
