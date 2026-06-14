// Build the sense-depth comparison (Phase 2, UC-LX-04).
//
// Compares how richly dictionaries treat a lemma's senses/sections using only
// validated structural adapters. Missing or unvalidated prose markup is
// unavailable, never counted as one or zero evidence.
//
// senseUnits(entry) is adapter-specific with a floor of 1. Per lemma per
// dictionary we take the richest entry. The comparison reports per-dictionary
// sense richness, a "deepest treatment" leaderboard, and the largest
// cross-dictionary gaps.
//
// Usage: npm run build-sense-depth. No LLM inference.

import fs from "node:fs";
import { generatedAtForPayload, generatedAtNow, licenseFields, readJsonIfExists } from "./lib/dataset-meta.mjs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { iterateDict, dictExists } from "./lib/dict-parser.mjs";
import { normalizeLemma } from "./lib/dict-normalize.mjs";
import { buildBroadHeadwordDictionaries, coreComparisonDictionaries } from "./lib/dict-scope.mjs";
import { featureSupport, senseMethodForDict, senseUnitsForDict, supportedFeatureCodes } from "./lib/dict-feature-adapters.mjs";
import { dictSourcePath, sourceHrefForDict } from "./lib/source-links.mjs";

const SCHEMA_VERSION = "1.0.0";
const OUT_DIR = path.resolve(process.cwd(), "src", "data", "dicts");
const OUT_FILE = path.join(OUT_DIR, "sense-depth.json");
const TOP_DISPARITIES = 200;

const CORE_ORDER = coreComparisonDictionaries().map(d => d.code);
const BROAD_HEADWORD_DICTS = buildBroadHeadwordDictionaries();
const BROAD_BY_CODE = new Map(BROAD_HEADWORD_DICTS.map(d => [d.code, d]));
const BROAD_SENSE_DICTS = supportedFeatureCodes("senses", { scope: "broadHeadword" });
const SENSE_DICTS = [
  ...CORE_ORDER.filter(code => BROAD_SENSE_DICTS.includes(code)),
  ...BROAD_SENSE_DICTS.filter(code => !CORE_ORDER.includes(code))
];
const SENSE_DICTIONARIES = SENSE_DICTS.map(code => BROAD_BY_CODE.get(code) ?? { code, label: code.toUpperCase(), sourceLinkMode: "github" });
const SENSE_LABELS = Object.fromEntries(SENSE_DICTIONARIES.map(d => [d.code, d.label]));

export function senseUnits(body, marker) {
  marker.lastIndex = 0;
  const n = (body.match(marker) || []).length;
  return Math.max(1, n);
}

function sourcePointer(dict, line) {
  return sourceHrefForDict(dict, line);
}

function sourcePath(dict) {
  return dictSourcePath(dict.code);
}

function sourceExample(dict, rec) {
  return {
    href: sourcePointer(dict, rec.startLine),
    line: rec.startLine,
    sourceLinkMode: dict.sourceLinkMode,
    sourcePath: sourcePath(dict)
  };
}

function orderIncludedDictionaries(support, codes) {
  const byCode = new Map(support.includedDictionaries.map(dict => [dict.code, dict]));
  return {
    ...support,
    includedDictionaries: codes.map(code => byCode.get(code)).filter(Boolean)
  };
}

function main() {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const warnings = [];

  // index: normalized lemma -> { [code]: { senses, source pointer } } (richest entry)
  const index = new Map();
  const perDict = {};

  for (const dict of SENSE_DICTIONARIES) {
    const { code } = dict;
    if (!dictExists(code)) {
      warnings.push(`Missing source for ${code}; skipped.`);
      continue;
    }
    const adapter = senseMethodForDict(code);
    let recordCount = 0;
    let multiSense = 0;
    let totalSenses = 0;
    for (const rec of iterateDict(code)) {
      if (!rec.k1) continue;
      recordCount += 1;
      const s = senseUnitsForDict(code, rec.body || "");
      totalSenses += s;
      if (s > 1) multiSense += 1;

      const { normalized } = normalizeLemma(rec.k1);
      if (!normalized) continue;
      let entry = index.get(normalized);
      if (!entry) {
        entry = {};
        index.set(normalized, entry);
      }
      if (!entry[code] || s > entry[code].senses) entry[code] = { senses: s, ...sourceExample(dict, rec) };
    }
    perDict[code] = {
      code,
      dict: SENSE_LABELS[code] ?? code.toUpperCase(),
      method: adapter?.methodLabel ?? "unavailable",
      methodId: adapter?.methodId ?? null,
      methodStatus: adapter?.status ?? "missing",
      sourceLinkMode: dict.sourceLinkMode,
      recordCount,
      meanSensesPerEntry: recordCount ? Number((totalSenses / recordCount).toFixed(3)) : 0,
      multiSensePct: recordCount ? Number(((100 * multiSense) / recordCount).toFixed(1)) : 0
    };
    console.log(`  ${code}: mean ${perDict[code].meanSensesPerEntry} senses/entry, ${perDict[code].multiSensePct}% multi-sense`);
  }

  const present = SENSE_DICTS.filter(c => perDict[c]);

  // Per-lemma comparison among the sense-segmented dictionaries.
  const leaderboard = Object.fromEntries(present.map(c => [SENSE_LABELS[c] ?? c.toUpperCase(), 0]));
  let ties = 0;
  const disparities = [];
  for (const [lemma, entry] of index) {
    const here = present.filter(c => entry[c]);
    if (here.length < 2) continue;
    let maxC = null, maxV = -1, minV = Infinity, tie = false;
    for (const c of here) {
      const v = entry[c].senses;
      if (v > maxV) { maxV = v; maxC = c; tie = false; }
      else if (v === maxV) tie = true;
      if (v < minV) minV = v;
    }
    if (tie || maxV === minV) ties += 1;
    else leaderboard[SENSE_LABELS[maxC] ?? maxC.toUpperCase()] += 1;
    if (maxV - minV >= 2) {
      disparities.push({
        lemma,
        byDict: Object.fromEntries(here.map(c => [SENSE_LABELS[c] ?? c.toUpperCase(), entry[c].senses])),
        gap: maxV - minV,
        deepest: SENSE_LABELS[maxC] ?? maxC.toUpperCase(),
        examples: here.map(c => ({
          dict: SENSE_LABELS[c] ?? c.toUpperCase(),
          senses: entry[c].senses,
          href: entry[c].href,
          line: entry[c].line,
          sourceLinkMode: entry[c].sourceLinkMode,
          sourcePath: entry[c].sourcePath
        }))
      });
    }
  }
  disparities.sort((a, b) => b.gap - a.gap || a.lemma.localeCompare(b.lemma));

  const senseSupport = orderIncludedDictionaries(featureSupport("senses", { scope: "broadHeadword" }), SENSE_DICTS);

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    ...licenseFields(),
    generatedAt: generatedAtNow(),
    sourceRoot: "../csl-orig/v02",
    feature: senseSupport.feature,
    featureLabel: senseSupport.featureLabel,
    adapterScope: senseSupport.adapterScope,
    includedDictionaries: senseSupport.includedDictionaries,
    unavailableDictionaries: senseSupport.unavailableDictionaries,
    diagnosticDictionaries: senseSupport.diagnosticDictionaries,
    methodNotes: senseSupport.methodNotes,
    senseSegmentedDicts: present.map(c => SENSE_LABELS[c] ?? c.toUpperCase()),
    perDict: present.map(c => perDict[c]),
    leaderboard,
    ties,
    disparityCount: disparities.length,
    shown: Math.min(TOP_DISPARITIES, disparities.length),
    topDisparities: disparities.slice(0, TOP_DISPARITIES),
    assumptions: [
      `Sense segmentation uses validated adapters only: ${present.map(c => SENSE_LABELS[c] ?? c.toUpperCase()).join(", ")}.`,
      "Unavailable dictionaries are excluded from this metric, never counted as single-sense or zero evidence.",
      "Per lemma per dictionary the richest entry (max senseUnits) is used; the leaderboard counts lemmas where one dictionary is strictly deepest.",
      "These are sense/article-section proxies, not curated sense inventories; adapter method notes identify dictionary-specific marker semantics."
    ],
    warnings
  };

  payload.generatedAt = generatedAtForPayload(readJsonIfExists(OUT_FILE, fs), payload);
  fs.writeFileSync(OUT_FILE, `${JSON.stringify(payload, null, 2)}\n`);
  console.log(`\nWrote sense depth (${present.length} dicts, ${disparities.length} disparities) to:`);
  console.log(`- ${path.relative(process.cwd(), OUT_FILE)}`);
}

// Run only when executed directly, not when imported by tests.
if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
