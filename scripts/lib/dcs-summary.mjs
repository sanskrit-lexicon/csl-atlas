// scripts/lib/dcs-summary.mjs
//
// Optional read-only adapter for the VisualDCS corpus-frequency summary.
// Returns an empty map / null when dcs_lemma_summary.json is absent —
// never throws, never blocks a build. Per docs/VISUALDCS_CONSUMPTION_CONTRACT.md.

import { readFileSync } from "node:fs";
import { normalizeLemma } from "./dict-normalize.mjs";

const SUMMARY_PATH = "data/dcs/dcs_lemma_summary.json";

/**
 * Parse a dcs_lemma_summary.json file at the given path.
 * Returns {} when the file is absent or unreadable. Exported for testing.
 * @param {string} filePath
 * @returns {Record<string, {freqBand:number, attested:boolean, formCount?:number, firstAttestationEra?:string}>}
 */
export function parseDcsSummaryFile(filePath) {
  try {
    const raw = JSON.parse(readFileSync(filePath, "utf-8"));
    return raw.lemmas ?? {};
  } catch {
    return {};
  }
}

let _cache = null;

/**
 * Look up the DCS corpus summary record for a headword.
 * Returns null when the lemma is absent or the file has not been emitted yet.
 * @param {string} k1 Raw SLP1 <k1> headword (normalizeLemma applied internally).
 * @returns {{freqBand:number, attested:boolean, formCount?:number, firstAttestationEra?:string}|null}
 */
export function dcsSummary(k1) {
  if (_cache === null) _cache = parseDcsSummaryFile(SUMMARY_PATH);
  const { normalized } = normalizeLemma(k1);
  return _cache[normalized] ?? null;
}

/**
 * Full summary map (normalized SLP1 key → record), or {} when absent.
 * For batch joins; prefer dcsSummary() for single-lemma lookups.
 * @returns {Record<string, {freqBand:number, attested:boolean, formCount?:number, firstAttestationEra?:string}>}
 */
export function loadDcsSummary() {
  if (_cache === null) _cache = parseDcsSummaryFile(SUMMARY_PATH);
  return _cache;
}
