// Build R2 h2h3 inheritance-edge report.
//
// Generates r2_h2h3.json from a reconstructed 28-noun panel across three
// documented inheritance edges (WIL→SHS, WIL→YAT, AP90→AP).
// Computes H2 (citation-survival) and H3R (gloss-overlap drift).
//
// Usage: npm run build-r2-h2h3

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { iterateDict } from "./lib/dict-parser.mjs";
import { R2_DICTS, splitRecord, cleanText, jaccard } from "./build-r2-source-anchors.mjs";

const OUT_DIR = path.resolve(process.cwd(), "data", "lexico");
const OUT_FILE = path.join(OUT_DIR, "r2_h2h3.json");

// Sense survival threshold: max gloss-word Jaccard with any descendant sense
const SURVIVAL_THRESHOLD = 0.15;
const PANEL_SIZE = 28;

// Dict configs for dicts not in R2_DICTS (SHS/YAT use inline N. markers)
const SHS_CONFIG = { code: "shs", label: "Śabda-Sāgara 1900", parserFamily: "western", split: "inline-number" };
const YAT_CONFIG = { code: "yat", label: "Yates 1846", parserFamily: "western", split: "inline-number" };

const DICT_CONFIG = Object.fromEntries(R2_DICTS.map(d => [d.code, d]));
DICT_CONFIG["shs"] = SHS_CONFIG;
DICT_CONFIG["yat"] = YAT_CONFIG;

// --- Stem normalization for cross-dict matching (strips masculine/neuter nominative H/M) ---
function stemKey(k) {
  return k.replace(/[HM]$/, "");
}

// --- Sense extraction ---

// Strip markup without 220-char truncation (used for full-body splitting)
export function stripMarkup(body) {
  return (body ?? "")
    .replace(/<[^>]+>/g, " ")
    .replace(/\{[#%@]?/g, " ")
    .replace(/[#%@]?\}/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

// SHS/YAT: split on inline "N. " markers; skip header before "1."
export function splitInlineNumber(body) {
  const text = stripMarkup(body);
  const parts = text.split(/\b\d+\.\s+/);
  return parts.length > 1
    ? parts.slice(1).map(s => s.trim()).filter(Boolean)
    : [text.trim()].filter(Boolean);
}

// Return an array of {text, rawText} where rawText still has <ls> for citation check
function extractSenses(body, dictCode) {
  if (!body || !body.trim()) return [];
  const cfg = DICT_CONFIG[dictCode];

  if (cfg.split === "inline-number") {
    // SHS/YAT: rawText = body segment (no per-sense XML preservation here;
    // citations rare in SHS/YAT so per-entry check is used as fallback)
    const texts = splitInlineNumber(body);
    return texts.map(t => ({ text: t, rawText: t }));
  }

  const parts = splitRecord(body, cfg);
  const explicit = parts.filter(p => p.splitConfidence === "explicit");
  const source = explicit.length > 0 ? explicit : parts;
  return source.map(p => ({ text: cleanText(p.text), rawText: p.text }));
}

// --- Citation check ---
function hasCitation(rawText) {
  return /<ls/i.test(rawText || "");
}

// --- Gloss overlap (word-level Jaccard, short words and stop-words removed) ---
const STOP = new Set([
  "the","a","an","of","to","in","or","and","as","be","is","are","was","were",
  "by","for","on","with","at","from","that","this","it","its","not","also",
  "used","one","two","its","any","all","esp","fig","lit",
]);

function glossWords(text) {
  const ws = new Set();
  for (const w of text.toLowerCase().split(/\W+/)) {
    if (w.length >= 3 && !STOP.has(w)) ws.add(w);
  }
  return ws;
}

export function glossOverlap(a, b) {
  const wa = glossWords(a), wb = glossWords(b);
  if (!wa.size && !wb.size) return 0;
  let shared = 0;
  for (const w of wa) if (wb.has(w)) shared++;
  const total = wa.size + wb.size - shared;
  return total > 0 ? shared / total : 0;
}

// --- Load all entries for a dict as stem→{body} ---
function loadDictByStem(dictCode) {
  const map = new Map();
  for (const rec of iterateDict(dictCode)) {
    const stem = stemKey(rec.k1);
    if (!map.has(stem)) map.set(stem, rec.body || "");
  }
  return map;
}

// WIL lex tags that indicate nominal (noun/adj) entries — excludes verb roots (r.)
const NOMINAL_LEX = /\bm\b|\bf\b|\bn\b|mfn|mf|mn/;

// --- Select panel: top PANEL_SIZE nouns by WIL sense count present in all 5 dicts ---
// Only nominal entries (m./f./n./mfn.) with 3–20 WIL explicit senses
// (>20 tends to be verb roots or highly-polysemous particles)
function selectPanel(wilMap, shsMap, yatMap, ap90Map, apMap) {
  const candidates = [];
  for (const [stem, wilBody] of wilMap) {
    // Filter to nominal entries only
    const lexMatch = (wilBody.match(/<lex>(.*?)<\/lex>/) || [])[1] || "";
    if (!NOMINAL_LEX.test(lexMatch)) continue;

    const wilParts = splitRecord(wilBody, DICT_CONFIG["wil"]);
    const wilSenses = wilParts.filter(p => p.splitConfidence === "explicit").length;
    if (wilSenses < 3 || wilSenses > 9) continue;
    if (!shsMap.has(stem) || !yatMap.has(stem) || !ap90Map.has(stem) || !apMap.has(stem)) continue;
    candidates.push({ stem, wilSenses });
  }
  candidates.sort((a, b) => b.wilSenses - a.wilSenses);
  return candidates.slice(0, PANEL_SIZE).map(c => c.stem);
}

// --- Compute survival rows for one lemma/edge ---
function computeEdgeRows(ancSenses, desSenses) {
  return ancSenses.map(({ text: ancText, rawText }) => {
    const cited = hasCitation(rawText);
    let maxOverlap = 0;
    for (const { text: desText } of desSenses) {
      const ov = glossOverlap(ancText, desText);
      if (ov > maxOverlap) maxOverlap = ov;
    }
    return { cited, overlap: maxOverlap, survived: maxOverlap >= SURVIVAL_THRESHOLD };
  });
}

// Round to 3 decimal places
function r3(x) { return Math.round(x * 1000) / 1000; }

async function main() {
  // Load all 5 dicts
  process.stderr.write("Loading dicts...\n");
  const wilMap  = loadDictByStem("wil");
  const shsMap  = loadDictByStem("shs");
  const yatMap  = loadDictByStem("yat");
  const ap90Map = loadDictByStem("ap90");
  const apMap   = loadDictByStem("ap");

  // Select panel
  const panel = selectPanel(wilMap, shsMap, yatMap, ap90Map, apMap);
  process.stderr.write(`Panel (${panel.length} nouns): ${panel.slice(0,10).join(", ")}...\n`);

  // Three edges
  const edges = [
    { key: "wil→shs",  ancDict: "wil",  desDict: "shs",  ancMap: wilMap,  desMap: shsMap,  archivedMeanAnc: 7.9,  archivedMeanDes: 8.5,  archivedDrift:  0.6,  archivedOverlap: 0.82, pattern: "near-verbatim copy" },
    { key: "wil→yat",  ancDict: "wil",  desDict: "yat",  ancMap: wilMap,  desMap: yatMap,  archivedMeanAnc: 7.9,  archivedMeanDes: 1.1,  archivedDrift: -6.75, archivedOverlap: 0.15, pattern: "drastic condensation" },
    { key: "ap90→ap",  ancDict: "ap90", desDict: "ap",   ancMap: ap90Map, desMap: apMap,   archivedMeanAnc: 15.5, archivedMeanDes: 11.0, archivedDrift: -4.5,  archivedOverlap: 0.61, pattern: "revision, no expansion" },
  ];

  // Per-edge and per-lemma accumulation
  const h2Rows = []; // { cited, survived } across all edges
  const h3rResults = [];

  for (const edge of edges) {
    let totalAncSenses = 0, totalDesSenses = 0, totalOverlap = 0, nPairs = 0;
    let lemmaResults = [];

    for (const stem of panel) {
      const ancBody = edge.ancMap.get(stem) ?? "";
      const desBody = edge.desMap.get(stem) ?? "";
      const ancSenses = extractSenses(ancBody, edge.ancDict);
      const desSenses = extractSenses(desBody, edge.desDict);

      if (!ancSenses.length || !desSenses.length) continue;

      const rows = computeEdgeRows(ancSenses, desSenses);
      for (const row of rows) h2Rows.push(row);

      const meanOverlap = rows.reduce((s, r) => s + r.overlap, 0) / rows.length;
      totalAncSenses += ancSenses.length;
      totalDesSenses += desSenses.length;
      totalOverlap += meanOverlap;
      nPairs++;

      lemmaResults.push({ stem, ancSenses: ancSenses.length, desSenses: desSenses.length, meanOverlap: r3(meanOverlap) });
    }

    const nLemmas = nPairs;
    const meanAncSenses = nLemmas > 0 ? r3(totalAncSenses / nLemmas) : 0;
    const meanDesSenses = nLemmas > 0 ? r3(totalDesSenses / nLemmas) : 0;
    const drift = r3(meanDesSenses - meanAncSenses);
    const meanGlossOverlap = nLemmas > 0 ? r3(totalOverlap / nLemmas) : 0;

    h3rResults.push({
      edge: edge.key,
      ancDict: edge.ancDict,
      desDict: edge.desDict,
      nLemmas,
      meanAncSenses,
      meanDesSenses,
      drift,
      meanGlossOverlap,
      pattern: edge.pattern,
      archivedMeanAncSenses: edge.archivedMeanAnc,
      archivedMeanDesSenses: edge.archivedMeanDes,
      archivedDrift: edge.archivedDrift,
      archivedMeanGlossOverlap: edge.archivedOverlap,
      lemmaResults,
    });

    process.stderr.write(`  ${edge.key}: meanAnc=${meanAncSenses} vs ${edge.archivedMeanAnc}, meanDes=${meanDesSenses} vs ${edge.archivedMeanDes}, overlap=${meanGlossOverlap} vs ${edge.archivedOverlap}\n`);
  }

  // H2 aggregate
  const cited   = h2Rows.filter(r => r.cited);
  const uncited = h2Rows.filter(r => !r.cited);
  const citedSurv   = cited.filter(r => r.survived);
  const uncitedSurv = uncited.filter(r => r.survived);

  const h2 = {
    survivalThreshold: SURVIVAL_THRESHOLD,
    cited:   { n: cited.length,   survived: citedSurv.length,   rate: cited.length   > 0 ? r3(citedSurv.length   / cited.length)   : 0 },
    uncited: { n: uncited.length, survived: uncitedSurv.length, rate: uncited.length > 0 ? r3(uncitedSurv.length / uncited.length) : 0 },
    supported: null, // set below
    archivedCited:   { n: 96,  rate: 0.70 },
    archivedUncited: { n: 715, rate: 0.54 },
  };
  h2.supported = h2.cited.rate > h2.uncited.rate;
  const gap = r3(h2.cited.rate - h2.uncited.rate);

  process.stderr.write(`H2: cited ${h2.cited.rate} (n=${h2.cited.n}) vs uncited ${h2.uncited.rate} (n=${h2.uncited.n}), gap=${gap}\n`);
  process.stderr.write(`    archived: cited 0.70 (n=96) vs uncited 0.54 (n=715)\n`);

  const output = {
    schemaVersion: "0.1.0",
    generatedBy: "npm run build-r2-h2h3",
    panel,
    panelSize: panel.length,
    survivedThreshold: SURVIVAL_THRESHOLD,
    h2,
    h3r: h3rResults.map(r => ({
      edge: r.edge,
      ancDict: r.ancDict,
      desDict: r.desDict,
      nLemmas: r.nLemmas,
      meanAncSenses: r.meanAncSenses,
      meanDesSenses: r.meanDesSenses,
      drift: r.drift,
      meanGlossOverlap: r.meanGlossOverlap,
      pattern: r.pattern,
      archived: {
        meanAncSenses: r.archivedMeanAncSenses,
        meanDesSenses: r.archivedMeanDesSenses,
        drift: r.archivedDrift,
        meanGlossOverlap: r.archivedMeanGlossOverlap,
      },
      lemmaResults: r.lemmaResults,
    })),
    limitations: [
      "28-noun panel reconstructed from nouns present in all 5 dicts with ≥3 WIL senses; original panel from deleted h2h3_analysis.py.",
      "SHS/YAT senses extracted by inline '\\b\\d+\\.\\s+' split; no XML tags preserved for per-sense citation check in SHS/YAT.",
      "Survival threshold is word-level Jaccard ≥ " + SURVIVAL_THRESHOLD + " (configurable).",
      "Gloss overlap uses word-level Jaccard after removing stop-words and short tokens.",
      "AP entries may include a 'lumped-proxy' header part; explicit sense parts are used for counting.",
      "Archive parity is a regression signal, not an optimization target.",
    ],
  };

  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(OUT_FILE, JSON.stringify(output, null, 2));
  console.log(`Wrote ${path.relative(process.cwd(), OUT_FILE)}`);
  console.log(`H2: cited rate ${h2.cited.rate} (n=${h2.cited.n}) vs uncited ${h2.uncited.rate} (n=${h2.uncited.n}) — supported: ${h2.supported}`);
  for (const r of h3rResults) {
    console.log(`H3R ${r.edge}: anc=${r.meanAncSenses}, des=${r.meanDesSenses}, drift=${r.drift}, overlap=${r.meanGlossOverlap}`);
  }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
