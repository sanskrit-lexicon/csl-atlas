// MICRO — one headword across every dictionary.
//
// Builds a microstructure feature matrix for a single lemma (default `gam`):
// for each dictionary that carries the headword, aggregate its entries and count
// the structural features (size, tagged `<ls>` vs inline `iti` citations, grammar,
// etymology, cross-reference, homonym, division/subentry/root markers), plus a
// side-by-side entry excerpt. This is the per-lemma cut that complements the
// per-dictionary MACRO profile already in `structural-register.json` /
// `dictionary-coverage.json` (no need to recompute that).
//
// Reuses iterateDict + normalizeLemma; reads sibling csl-orig directly; no model,
// no network. Output goes to data/lexico/micro-<lemma>.json.
//
// Usage: npm run build-micro-entry [-- <lemma>]   (default lemma: gam)

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { iterateDict, dictExists } from "./lib/dict-parser.mjs";
import { normalizeLemma } from "./lib/dict-normalize.mjs";
import { licenseFields, generatedAtForPayload, readJsonIfExists } from "./lib/dataset-meta.mjs";

const ROOT = process.cwd();
const HEADWORDS = path.join(ROOT, "data", "headwords.json");
const SCHEMA_VERSION = "1.0.0";

const norm = value => normalizeLemma(value ?? "").normalized;

// Dictionary codes from the committed headword inventory (drop the _summary meta key).
export function dictCodes(file = HEADWORDS) {
  return Object.keys(JSON.parse(fs.readFileSync(file, "utf8"))).filter(code => code !== "_summary");
}

const count = (body, re) => (body.match(re) ?? []).length;

// Per-entry structural feature counts. Pure (string in, numbers out) so it is
// testable without csl-orig. Regexes mirror build-dictionary-coverage's blocks.
export function featureCounts(body) {
  const text = body ?? "";
  return {
    chars: text.length,
    ls: count(text, /<ls\b/gi),
    iti: count(text, /\biti\b/gi),
    gram: count(text, /<lex\b|<ab\b/gi),
    etym: count(text, /<etym\b|<ab\b[^>]*>\s*cf\.|cognate/gi),
    xref: count(text, /<srs\b|<xr\b|q\.v\./gi),
    hom: count(text, /<hom\b|<h>\s*[2-9]/gi),
    div: count(text, /<div\b/gi),
    subentry: count(text, /<k2\b/gi),
    root: count(text, /<root\b|DhAtu/gi)
  };
}

const FEATURE_KEYS = ["chars", "ls", "iti", "gram", "etym", "xref", "hom", "div", "subentry", "root"];

// Aggregate all entries of `lemma` in each dictionary into one feature row.
export function buildLemmaMatrix(lemma, { iterate = iterateDict, exists = dictExists, codes = dictCodes() } = {}) {
  const target = norm(lemma);
  const rows = [];
  for (const code of codes) {
    if (!exists(code)) continue;
    const totals = Object.fromEntries(FEATURE_KEYS.map(key => [key, 0]));
    let entries = 0;
    let firstExcerpt = null, firstHref = null, firstL = null;
    for (const rec of iterate(code)) {
      if (norm(rec.k1) !== target) continue;
      entries += 1;
      const f = featureCounts(rec.body ?? "");
      for (const key of FEATURE_KEYS) totals[key] += f[key];
      if (firstExcerpt === null) {
        firstExcerpt = (rec.body ?? "").replace(/\s+/g, " ").trim().slice(0, 280);
        firstHref = rec.href ?? null;
        firstL = rec.L ?? null;
      }
    }
    if (!entries) continue;
    rows.push({
      dictionary: code.toUpperCase(),
      dict: code,
      entries,
      ...totals,
      citations: totals.ls + totals.iti,
      citationDensityPer1k: totals.chars ? Number((1000 * (totals.ls + totals.iti) / totals.chars).toFixed(2)) : 0,
      citationRegister: totals.ls > 0 && totals.iti > 0 ? "mixed" : totals.ls > 0 ? "tagged" : totals.iti > 0 ? "iti" : "none",
      firstL,
      href: firstHref,
      excerpt: firstExcerpt
    });
  }
  // Most substantial entries first (chars desc), then by dict code for stability.
  rows.sort((a, b) => b.chars - a.chars || a.dict.localeCompare(b.dict));
  return rows;
}

export function buildPayload(lemma, options = {}, generatedAt = new Date().toISOString()) {
  const rows = buildLemmaMatrix(lemma, options);
  return {
    schemaVersion: SCHEMA_VERSION,
    ...licenseFields(),
    generatedAt,
    generatedBy: "npm run build-micro-entry",
    claim: "MICRO: one headword's microstructure varies sharply across dictionaries (size, citation register, grammar, etymology).",
    evidenceLabel: "derived",
    lemma: norm(lemma),
    featureKeys: FEATURE_KEYS,
    sourceFiles: ["../csl-orig/v02/<dict>/<dict>.txt", "data/headwords.json"],
    counts: {
      dictionariesWithLemma: rows.length,
      totalEntries: rows.reduce((sum, row) => sum + row.entries, 0),
      taggedCiting: rows.filter(row => row.ls > 0).length,
      itiCiting: rows.filter(row => row.iti > 0).length
    },
    assumptions: [
      "A dictionary's row aggregates every entry whose headword normalizes (slp1_norm) to the lemma.",
      "Feature counts are regex tallies over the raw entry body; `chars` includes markup.",
      "Tagged `<ls>` and inline `iti` are counted separately — an iti-citing dictionary is not citation-free."
    ],
    warnings: [
      "Counts are structural tallies, not validated citation resolutions; a high `<ls>` count is density, not correctness.",
      "Per-lemma evidence; do not generalize a single headword's profile to a dictionary's whole register (use MACRO / structural-register.json for that)."
    ],
    dictionaries: rows
  };
}

function main() {
  const lemma = process.argv[2] || "gam";
  const out = path.join(ROOT, "data", "lexico", `micro-${norm(lemma)}.json`);
  const payload = buildPayload(lemma);
  payload.generatedAt = generatedAtForPayload(readJsonIfExists(out, fs), payload);
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, `${JSON.stringify(payload, null, 2)}\n`);
  console.log(`Wrote ${path.relative(ROOT, out)} — lemma ${payload.lemma} across ${payload.counts.dictionariesWithLemma} dictionaries (${payload.counts.totalEntries} entries).`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
