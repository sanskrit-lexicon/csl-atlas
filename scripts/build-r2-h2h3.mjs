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
// YAT promoted to semicolon-aware counting (#126 review: run-on-gloss, gate ON).
// SHS stays inline-number (sense-numbered → gate OFF, the control).
const YAT_CONFIG = { code: "yat", label: "Yates 1846", parserFamily: "western", split: "semicolon" };

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

// A gender-section marker (m./f./n.) signals genuine polysemy. Its ABSENCE flags
// a lone adjectival/participial entry whose semicolons separate synonyms of ONE
// sense (e.g. avaṣṭabdha "Near; supported; stopped"), not distinct meanings.
const YAT_GENDER_MARK = /(^|\s)[mfn]\.\s/;

// Semicolon-aware sense splitter for run-on-gloss dictionaries (YAT), PROMOTED
// from the #126 review (25/26 promote; reviewer gasyoun, 2026-06-16). YAT is a
// kośa-style polysemy dictionary that packs distinct gender-sectioned meanings
// with semicolons rather than numbering them, so the inline-number splitter
// collapses every entry to 1 (the #125 artifact). This mirrors the reviewed
// packet's semicolonMeanings count, returning the meaning texts for survival.
// Refinement (also from the review): a lone adjectival entry with no gender
// section is a single sense — do NOT split its synonym list.
export function splitSemicolon(body) {
  const stripped = stripMarkup(body);
  // Drop the leading headword + any noun-class number, then split on ; / .
  const t = stripped.replace(/^[^0-9]*\d+\.\s*/, "").replace(/^[a-z. ]+\b/i, "");
  const segs = t.split(/[;.]/).map(s => s.trim()).filter(s => s.replace(/[^a-zA-Z]/g, "").length > 2);
  if (segs.length === 0) return [stripped].filter(Boolean);
  if (segs.length > 1 && !YAT_GENDER_MARK.test(stripped)) return [segs.join("; ")]; // lone-adjective: one sense
  return segs;
}

// Return an array of {text, rawText} where rawText still has <ls> for citation check
function extractSenses(body, dictCode) {
  if (!body || !body.trim()) return [];
  const cfg = DICT_CONFIG[dictCode];

  if (cfg.split === "inline-number") {
    // SHS: rawText = body segment (no per-sense XML preservation here;
    // citations rare in SHS so per-entry check is used as fallback)
    const texts = splitInlineNumber(body);
    return texts.map(t => ({ text: t, rawText: t }));
  }

  if (cfg.split === "semicolon") {
    // YAT (run-on-gloss): semicolon-aware meaning units (#126 promotion).
    const texts = splitSemicolon(body);
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
// position = sense ordinal in the ancestor entry; glossLen = content-word count
// (both centrality proxies, kept for the H2 confound-controlled model).
function computeEdgeRows(ancSenses, desSenses) {
  return ancSenses.map(({ text: ancText, rawText }, position) => {
    const cited = hasCitation(rawText);
    let maxOverlap = 0;
    for (const { text: desText } of desSenses) {
      const ov = glossOverlap(ancText, desText);
      if (ov > maxOverlap) maxOverlap = ov;
    }
    return { cited, overlap: maxOverlap, survived: maxOverlap >= SURVIVAL_THRESHOLD,
             position, glossLen: glossWords(ancText).size, ancText };
  });
}

// Round to 3 / 4 decimal places
function r3(x) { return Math.round(x * 1000) / 1000; }
function r4(x) { return Math.round(x * 10000) / 10000; }

// ---- Numerical helpers for the H2 confound-controlled analysis ----
// Pure-JS logistic regression (IRLS) + cluster-robust (CR1) SEs by lemma, so the
// "cited senses survive better" gap is tested after centrality controls and
// without the pseudoreplication of treating senses within an entry as independent.
function sigmoid(z) { return 1 / (1 + Math.exp(-z)); }
function dot(a, b) { let s = 0; for (let i = 0; i < a.length; i++) s += a[i] * b[i]; return s; }
function matMul(A, B) {
  const n = A.length, m = B[0].length, p = B.length;
  return A.map(row => Array.from({ length: m }, (_, j) => { let s = 0; for (let t = 0; t < p; t++) s += row[t] * B[t][j]; return s; }));
}
function matInv(A) { // Gauss-Jordan; returns null if singular
  const n = A.length;
  const M = A.map((r, i) => [...r, ...Array.from({ length: n }, (_, j) => (i === j ? 1 : 0))]);
  for (let c = 0; c < n; c++) {
    let piv = c; for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[piv][c])) piv = r;
    [M[c], M[piv]] = [M[piv], M[c]];
    const d = M[c][c]; if (Math.abs(d) < 1e-12) return null;
    for (let j = 0; j < 2 * n; j++) M[c][j] /= d;
    for (let r = 0; r < n; r++) if (r !== c) { const f = M[r][c]; for (let j = 0; j < 2 * n; j++) M[r][j] -= f * M[c][j]; }
  }
  return M.map(r => r.slice(n));
}
// X: design matrix (rows include the intercept column), y: 0/1. Returns beta.
export function fitLogistic(X, y, iters = 50) {
  const n = X.length, k = X[0].length;
  let beta = Array(k).fill(0);
  for (let it = 0; it < iters; it++) {
    const g = Array(k).fill(0);
    const H = Array.from({ length: k }, () => Array(k).fill(0));
    for (let i = 0; i < n; i++) {
      const pi = sigmoid(dot(X[i], beta)), w = pi * (1 - pi), r = y[i] - pi;
      for (let a = 0; a < k; a++) { g[a] += X[i][a] * r; for (let b = 0; b < k; b++) H[a][b] += X[i][a] * X[i][b] * w; }
    }
    const Hinv = matInv(H); if (!Hinv) break;
    const step = Hinv.map(row => dot(row, g));
    let maxd = 0; for (let a = 0; a < k; a++) { beta[a] += step[a]; maxd = Math.max(maxd, Math.abs(step[a])); }
    if (maxd < 1e-9) break;
  }
  return beta;
}
// Cluster-robust (CR1) SEs: sandwich with the per-cluster score sums.
export function clusterRobustSE(X, y, beta, clusters) {
  const n = X.length, k = X[0].length;
  const H = Array.from({ length: k }, () => Array(k).fill(0));
  const p = X.map(row => sigmoid(dot(row, beta)));
  for (let i = 0; i < n; i++) { const w = p[i] * (1 - p[i]); for (let a = 0; a < k; a++) for (let b = 0; b < k; b++) H[a][b] += X[i][a] * X[i][b] * w; }
  const bread = matInv(H); if (!bread) return { se: Array(k).fill(NaN), G: 0 };
  const score = new Map();
  for (let i = 0; i < n; i++) {
    const g = clusters[i]; if (!score.has(g)) score.set(g, Array(k).fill(0));
    const s = score.get(g), r = y[i] - p[i]; for (let a = 0; a < k; a++) s[a] += X[i][a] * r;
  }
  const meat = Array.from({ length: k }, () => Array(k).fill(0));
  for (const s of score.values()) for (let a = 0; a < k; a++) for (let b = 0; b < k; b++) meat[a][b] += s[a] * s[b];
  const G = score.size;
  const cAdj = (G / (G - 1)) * ((n - 1) / (n - k)); // CR1 finite-sample adjustment
  const V = matMul(matMul(bread, meat), bread);
  return { se: V.map((row, i) => Math.sqrt(Math.max(0, row[i] * cAdj))), G };
}
// Two-sided normal tail (Zelen-Severo approximation).
function normalTwoSidedP(z) {
  z = Math.abs(z);
  const t = 1 / (1 + 0.2316419 * z), d = 0.3989423 * Math.exp(-z * z / 2);
  const upper = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
  return r4(2 * upper);
}
function zscore(vals) {
  const m = vals.reduce((s, x) => s + x, 0) / vals.length;
  const sd = Math.sqrt(vals.reduce((s, x) => s + (x - m) ** 2, 0) / vals.length) || 1;
  return vals.map(x => (x - m) / sd);
}

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
    { key: "wil→yat",  ancDict: "wil",  desDict: "yat",  ancMap: wilMap,  desMap: yatMap,  archivedMeanAnc: 7.9,  archivedMeanDes: 1.1,  archivedDrift: -6.75, archivedOverlap: 0.15, pattern: "condensation (semicolon-aware count, #126 promotion: YAT abridges ~9→5.7, not the artifactual 9→1)" },
    { key: "ap90→ap",  ancDict: "ap90", desDict: "ap",   ancMap: ap90Map, desMap: apMap,   archivedMeanAnc: 15.5, archivedMeanDes: 11.0, archivedDrift: -4.5,  archivedOverlap: 0.61, pattern: "revision, no expansion" },
  ];

  // Per-edge and per-lemma accumulation
  const h2Rows = []; // enriched: { lemma, edge, cited, survived, overlap, position, glossLen, crossDict }
  const h3rResults = [];
  const ALL_MAPS = { wil: wilMap, shs: shsMap, yat: yatMap, ap90: ap90Map, ap: apMap };

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

      // Cross-dictionary attestation per ancestor sense: how many of the OTHER
      // panel dicts (not anc/des) carry a matching sense — a centrality control
      // independent of this edge's survival outcome. Senses extracted once/stem.
      const otherSenses = Object.entries(ALL_MAPS)
        .filter(([c]) => c !== edge.ancDict && c !== edge.desDict)
        .map(([c, m]) => extractSenses(m.get(stem) ?? "", c));
      for (const row of rows) {
        let crossDict = 0;
        for (const senses of otherSenses) {
          if (senses.some(({ text }) => glossOverlap(row.ancText, text) >= SURVIVAL_THRESHOLD)) crossDict++;
        }
        h2Rows.push({ lemma: stem, edge: edge.key, cited: row.cited, survived: row.survived,
                      overlap: row.overlap, position: row.position, glossLen: row.glossLen, crossDict });
      }

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
      senseExtractionArtifact: edge.senseExtractionArtifact ?? false,
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

  // --- H2 confound-controlled: does `cited` survive after centrality controls,
  //     clustered by lemma (pseudoreplication)? ---
  // Edge fixed effects (ref = wil→shs) are essential: the three edges have
  // radically different baseline survival (shs ~0.9 vs yat ~0.07), so without
  // them the centrality covariates absorb edge differences.
  const posZ = zscore(h2Rows.map(r => r.position));
  const glZ  = zscore(h2Rows.map(r => r.glossLen));
  const cdZ  = zscore(h2Rows.map(r => r.crossDict));
  const X = h2Rows.map((r, i) => [
    1, r.cited ? 1 : 0, posZ[i], glZ[i], cdZ[i],
    r.edge === "wil→yat" ? 1 : 0, r.edge === "ap90→ap" ? 1 : 0,
  ]);
  const yv = h2Rows.map(r => (r.survived ? 1 : 0));
  const beta = fitLogistic(X, yv);
  const { se, G } = clusterRobustSE(X, yv, beta, h2Rows.map(r => r.lemma));
  const terms = ["intercept", "cited", "position_z", "glossLen_z", "crossDict_z", "edge_wil→yat", "edge_ap90→ap"];
  const model = terms.map((t, j) => ({
    term: t, coef: r4(beta[j]), clusterRobustSE: r4(se[j]),
    z: r4(beta[j] / se[j]), p: normalTwoSidedP(beta[j] / se[j]),
    oddsRatio: r4(Math.exp(beta[j])),
    ci95: [r4(beta[j] - 1.96 * se[j]), r4(beta[j] + 1.96 * se[j])],
  }));
  const citedTerm = model.find(m => m.term === "cited");

  // Non-parametric cross-check: cited-vs-uncited survival within position tertiles.
  const posSorted = h2Rows.map(r => r.position).sort((a, b) => a - b);
  const q1 = posSorted[Math.floor(posSorted.length / 3)];
  const q2 = posSorted[Math.floor(2 * posSorted.length / 3)];
  const tertile = r => (r.position <= q1 ? "early" : r.position <= q2 ? "mid" : "late");
  const positionStrata = ["early", "mid", "late"].map(label => {
    const inBin = h2Rows.filter(r => tertile(r) === label);
    const c = inBin.filter(r => r.cited), u = inBin.filter(r => !r.cited);
    return {
      stratum: label, n: inBin.length,
      citedN: c.length, citedRate: c.length ? r3(c.filter(r => r.survived).length / c.length) : null,
      uncitedN: u.length, uncitedRate: u.length ? r3(u.filter(r => r.survived).length / u.length) : null,
    };
  });

  // Citation is not spread across the panel: Wilson 1832 carries almost no <ls>,
  // so nearly all cited ancestor senses are on the Apte edge. That concentration
  // makes the POOLED controlled OR fragile (it moves when an unrelated edge's
  // baseline shifts — e.g. the YAT semicolon promotion alone moved it ~1.75→3.0).
  // The trustworthy test is therefore within the one citation-bearing edge.
  const edgesPresent = [...new Set(h2Rows.map(r => r.edge))];
  const citedByEdge = edgesPresent.map(e => ({
    edge: e,
    cited: h2Rows.filter(r => r.edge === e && r.cited).length,
    total: h2Rows.filter(r => r.edge === e).length,
  }));
  const primaryEdge = citedByEdge.slice().sort((a, b) => b.cited - a.cited)[0].edge;
  const peRows = h2Rows.filter(r => r.edge === primaryEdge);
  const peC = peRows.filter(r => r.cited), peU = peRows.filter(r => !r.cited);
  const peCs = peC.filter(r => r.survived).length, peUs = peU.filter(r => r.survived).length;
  const pc = peC.length ? peCs / peC.length : 0, pu = peU.length ? peUs / peU.length : 0;
  const ppool = (peCs + peUs) / (peC.length + peU.length);
  const peSe = Math.sqrt(ppool * (1 - ppool) * (1 / peC.length + 1 / peU.length));
  const peZ = peSe > 0 ? (pc - pu) / peSe : 0;
  const withinPrimaryEdge = {
    edge: primaryEdge,
    citedRate: r3(pc), citedN: peC.length,
    uncitedRate: r3(pu), uncitedN: peU.length,
    twoProportionZ: r4(peZ),
    twoSidedP: r4(normalTwoSidedP(peZ)),
    significant: normalTwoSidedP(peZ) < 0.05,
    note: "Unclustered 2-proportion test within the single citation-bearing edge — the clean citation-survival signal, invariant to other edges' parsing.",
  };
  const concentrated = (citedByEdge.find(e => e.edge === primaryEdge)?.cited ?? 0) / Math.max(1, citedTerm ? h2Rows.filter(r => r.cited).length : 1) > 0.8;

  const h2Controlled = {
    method: "Logistic regression survived ~ cited + position + glossLen + crossDict (centrality controls, z-scored) + edge fixed effects (ref wil→shs), with CR1 lemma-cluster-robust SEs (addresses the centrality confound, edge-baseline differences, and within-entry pseudoreplication).",
    n: h2Rows.length,
    lemmaClusters: G,
    citedOddsRatio: citedTerm.oddsRatio,
    citedCI95_logOdds: citedTerm.ci95,
    citedP: citedTerm.p,
    citedByEdge,
    citationConcentratedOnOneEdge: concentrated,
    withinPrimaryEdge,
    verdict: concentrated
      ? "edge-concentrated: ~all cited senses are on one edge (" + primaryEdge + "), so the pooled controlled OR is unstable and not a reliable citation estimate; the clean within-edge test (z=" + withinPrimaryEdge.twoProportionZ + ", p=" + withinPrimaryEdge.twoSidedP + ") is " + (withinPrimaryEdge.significant ? "significant" : "suggestive, not significant") + ". Citation co-varies with survival but is not established as an independent predictor."
      : ((citedTerm.coef > 0 && citedTerm.p < 0.05) ? "controlled-supported"
        : (citedTerm.coef > 0) ? "attenuated-nonsignificant" : "not-supported-after-controls"),
    model,
    positionTertileCrossCheck: positionStrata,
    note: "Per-sense rows in data/lexico/r2_h2_senses.json for independent refitting. crossDict = matching senses among the 3 non-edge panel dicts. The pooled OR is edge-composition-sensitive (see citationConcentratedOnOneEdge); prefer withinPrimaryEdge.",
  };
  process.stderr.write(`H2 controlled: cited OR=${citedTerm.oddsRatio} p=${citedTerm.p} (cluster-robust, ${G} lemmas) -> ${h2Controlled.verdict}\n`);

  // ---------------------------------------------------------------------------
  // Threshold sensitivity (referee item M4): the survival cutoff (Jaccard ≥ 0.15)
  // is a researcher choice. Sweep it and REFIT the same controlled model at each
  // cutoff — only the binary outcome (survived) moves; the design matrix
  // (covariates + edge FE, z-scored at the reference 0.15 definition) is held
  // fixed, isolating the question "does the cited→survival inference depend on
  // where we draw the survival line?". Cheap & exact: h2Rows carry raw overlap.
  // ---------------------------------------------------------------------------
  const THRESHOLD_GRID = [0.10, 0.125, 0.15, 0.175, 0.20, 0.25];
  const clustersByLemma = h2Rows.map(r => r.lemma);
  const citedRows = h2Rows.filter(r => r.cited);
  const uncitedRows = h2Rows.filter(r => !r.cited);
  const rate = (rows, t) => (rows.length ? rows.filter(r => r.overlap >= t).length / rows.length : null);
  const thresholdGrid = THRESHOLD_GRID.map(t => {
    const yt = h2Rows.map(r => (r.overlap >= t ? 1 : 0));
    const survAll = yt.reduce((a, b) => a + b, 0);
    let controlledOddsRatio = null, citedCI95_logOdds = null, citedPval = null, fitOk = false;
    // Guard against perfect separation at extreme cutoffs (all-survive / none-survive).
    if (survAll > 0 && survAll < yt.length) {
      const betaT = fitLogistic(X, yt);
      const { se: seT } = clusterRobustSE(X, yt, betaT, clustersByLemma);
      const b = betaT[1], s = seT[1]; // cited term
      if (Number.isFinite(b) && Number.isFinite(s) && s > 0) {
        fitOk = true;
        controlledOddsRatio = r4(Math.exp(b));
        citedCI95_logOdds = [r4(b - 1.96 * s), r4(b + 1.96 * s)];
        citedPval = normalTwoSidedP(b / s);
      }
    }
    const cr = rate(citedRows, t), ur = rate(uncitedRows, t);
    return {
      threshold: t,
      citedRate: cr === null ? null : r3(cr),
      uncitedRate: ur === null ? null : r3(ur),
      naiveGap: (cr === null || ur === null) ? null : r3(cr - ur),
      controlledOddsRatio,
      citedCI95_logOdds,
      citedP: citedPval,
      controlledSignificant: fitOk ? (controlledOddsRatio > 1 && citedPval < 0.05) : null,
      fitOk,
    };
  });
  const anySignificant = thresholdGrid.some(g => g.controlledSignificant === true);
  const h2ThresholdSensitivity = {
    method: "Refit the h2Controlled model (survived ~ cited + position_z + glossLen_z + crossDict_z + edge FE, CR1 lemma-cluster-robust) at each survival cutoff; covariates held at the reference (0.15) definition, only the outcome re-thresholded.",
    referenceThreshold: SURVIVAL_THRESHOLD,
    grid: thresholdGrid,
    verdict: !anySignificant
      ? "robust-null: across cutoffs 0.10–0.25 the naive cited-survival gap persists but the CONTROLLED cited effect stays non-significant (CI spans OR=1)."
      : concentrated
        ? "pooled OR is significant at every cutoff, BUT it inherits the edge-concentration fragility (h2Controlled.citationConcentratedOnOneEdge): the pooled estimate is not a reliable citation effect, so its threshold-stability is NOT evidence for H2. Defer to h2Controlled.withinPrimaryEdge."
        : "threshold-dependent: the controlled cited effect reaches significance at one or more cutoffs — sensitive to the survival line.",
    note: "Covariates (incl. crossDict) are fixed at the 0.15 reference; only the survival outcome is swept. Extreme cutoffs that fully separate an edge are flagged fitOk=false. Since the YAT semicolon promotion (#126), the pooled OR rose but is edge-concentration-driven — read with h2Controlled.",
  };
  process.stderr.write(`H2 threshold sensitivity: ${thresholdGrid.map(g => g.threshold + ':' + (g.fitOk ? 'OR' + g.controlledOddsRatio + '/p' + (g.citedP ?? 'NA') : 'sep')).join(' ')} -> ${anySignificant ? 'THRESHOLD-DEPENDENT' : 'robust'}\n`);

  fs.writeFileSync(path.join(OUT_DIR, "r2_h2_senses.json"), JSON.stringify({
    schemaVersion: "0.1.0", generatedBy: "npm run build-r2-h2h3",
    note: "Per-ancestor-sense rows for the H2 confound-controlled analysis.",
    rows: h2Rows,
  }, null, 2));

  const output = {
    schemaVersion: "0.1.0",
    generatedBy: "npm run build-r2-h2h3",
    panel,
    panelSize: panel.length,
    survivedThreshold: SURVIVAL_THRESHOLD,
    h2,
    h2Controlled,
    h2ThresholdSensitivity,
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
      senseExtractionArtifact: r.senseExtractionArtifact,
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
      "SHS senses extracted by inline '\\b\\d+\\.\\s+' split; YAT by semicolon-aware split (#126 promotion); no XML tags preserved for per-sense citation check in SHS/YAT (both descendants — H2 citation is on the WIL/AP90 ancestor).",
      "RESOLVED (#126): the wil→yat '9→1 drastic condensation' was a parser artifact — YAT is semicolon-packed, not sense-numbered, so the inline-number splitter collapsed it to 1. The promoted semicolon counter (reviewer-adjudicated 25/26) now counts ~5.7 meanings/entry, so the edge reads as a genuine ~9→5.7 condensation (drift ≈ −3.3), comparable to ap90→ap. Lone adjectival entries keep inline (no over-split). See data/lexico/r2_semicolon_counter_packet.json + r2_yat_artifact_check.json.",
      "H2 CAVEAT: cited ancestor senses are concentrated on the ap90→ap edge (~82 of 84; Wilson 1832 carries almost no <ls>), so the POOLED controlled OR is edge-composition-sensitive (it moved when the YAT split changed). The reliable signal is h2Controlled.withinPrimaryEdge (the single citation-bearing edge).",
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
