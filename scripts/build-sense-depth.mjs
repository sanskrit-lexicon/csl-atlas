// Build the sense-depth comparison (Phase 2, UC-CD-06 / UC-LX-09).
//
// Compares how richly dictionaries treat a lemma's senses. Sense segmentation
// is structural only in AP (`∙` bullets) and PWG/PWK (<div>); MW segments
// senses in prose (<div> ~0.05/entry) and WIL/VCP/SKD are prose, so a
// structural sense count would misrepresent them — they are excluded.
//
// senseUnits(entry) = max(1, sense-marker count). Per lemma per dictionary we
// take the richest entry. The comparison reports per-dictionary sense richness,
// a "deepest treatment" leaderboard, and the largest cross-dictionary gaps.
//
// Usage: npm run build-sense-depth. No LLM inference.

import fs from "node:fs";
import path from "node:path";
import { DICTS, DICT_LABELS, SENSE_MARKER } from "./lib/dict-manifest.mjs";
import { iterateDict, dictExists } from "./lib/dict-parser.mjs";
import { normalizeLemma } from "./lib/dict-normalize.mjs";

const SCHEMA_VERSION = "1.0.0";
const OUT_DIR = path.resolve(process.cwd(), "src", "data", "dicts");
const TOP_DISPARITIES = 200;

const SENSE_DICTS = DICTS.filter(d => d.senseSegmented).map(d => d.code);

function senseUnits(body, marker) {
  marker.lastIndex = 0;
  const n = (body.match(marker) || []).length;
  return Math.max(1, n);
}

function main() {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const warnings = [];

  // index: normalized lemma -> { [code]: { senses, href } } (richest entry)
  const index = new Map();
  const perDict = {};

  for (const code of SENSE_DICTS) {
    if (!dictExists(code)) {
      warnings.push(`Missing source for ${code}; skipped.`);
      continue;
    }
    const marker = SENSE_MARKER[code];
    let recordCount = 0;
    let multiSense = 0;
    let totalSenses = 0;
    for (const rec of iterateDict(code)) {
      if (!rec.k1) continue;
      recordCount += 1;
      const s = senseUnits(rec.body || "", marker);
      totalSenses += s;
      if (s > 1) multiSense += 1;

      const { normalized } = normalizeLemma(rec.k1);
      if (!normalized) continue;
      let entry = index.get(normalized);
      if (!entry) {
        entry = {};
        index.set(normalized, entry);
      }
      if (!entry[code] || s > entry[code].senses) entry[code] = { senses: s, href: rec.href };
    }
    perDict[code] = {
      dict: DICT_LABELS[code],
      method: code === "ap" ? "bullet (∙)" : "div",
      recordCount,
      meanSensesPerEntry: recordCount ? Number((totalSenses / recordCount).toFixed(3)) : 0,
      multiSensePct: recordCount ? Number(((100 * multiSense) / recordCount).toFixed(1)) : 0
    };
    console.log(`  ${code}: mean ${perDict[code].meanSensesPerEntry} senses/entry, ${perDict[code].multiSensePct}% multi-sense`);
  }

  const present = SENSE_DICTS.filter(c => perDict[c]);

  // Per-lemma comparison among the sense-segmented dictionaries.
  const leaderboard = Object.fromEntries(present.map(c => [DICT_LABELS[c], 0]));
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
    else leaderboard[DICT_LABELS[maxC]] += 1;
    if (maxV - minV >= 2) {
      disparities.push({
        lemma,
        byDict: Object.fromEntries(here.map(c => [DICT_LABELS[c], entry[c].senses])),
        gap: maxV - minV,
        deepest: DICT_LABELS[maxC],
        examples: here.map(c => ({ dict: DICT_LABELS[c], senses: entry[c].senses, href: entry[c].href }))
      });
    }
  }
  disparities.sort((a, b) => b.gap - a.gap || a.lemma.localeCompare(b.lemma));

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    generatedAt: new Date().toISOString(),
    sourceRoot: "../csl-orig/v02",
    senseSegmentedDicts: present.map(c => DICT_LABELS[c]),
    perDict: present.map(c => perDict[c]),
    leaderboard,
    ties,
    disparityCount: disparities.length,
    shown: Math.min(TOP_DISPARITIES, disparities.length),
    topDisparities: disparities.slice(0, TOP_DISPARITIES),
    assumptions: [
      "Sense segmentation is structural only in AP (∙ bullets) and PWG/PWK (<div>); senseUnits = max(1, marker count).",
      "MW is excluded: it segments senses in prose (<div> ~0.05/entry), so a structural count would falsely make it sense-poor. WIL/VCP/SKD are prose too.",
      "Per lemma per dictionary the richest entry (max senseUnits) is used; the leaderboard counts lemmas where one dictionary is strictly deepest.",
      "These are sense-division proxies, not curated sense inventories; PWG/PWK <div> mixes major and sub-senses."
    ],
    warnings
  };

  fs.writeFileSync(path.join(OUT_DIR, "sense-depth.json"), `${JSON.stringify(payload, null, 2)}\n`);
  console.log(`\nWrote sense depth (${present.length} dicts, ${disparities.length} disparities) to:`);
  console.log(`- ${path.relative(process.cwd(), path.join(OUT_DIR, "sense-depth.json"))}`);
}

main();
