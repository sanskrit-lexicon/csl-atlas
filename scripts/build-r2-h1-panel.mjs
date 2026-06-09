// Build R2 H1 fixed-lemma panel deconfounding check.
//
// Generates r2_h1_panel.json: the same H1 year-vs-sense-granularity trend as
// r2_h1.json but restricted to a fixed panel of 30 nouns. Removes the
// headword-splitting confound (MW splits ~286k compounds into separate short
// entries, diluting its units/entry). The panel is shared across all 11 dicts
// so each dict's data point is computed on the same lemmas.
//
// Expected result (R2_FINDINGS.md): Pearson r ≈ 0.01 (flat, archived 0.06).
// A weak r = 0.56 among the 5 explicit-marker dicts is n=5 non-significant.
//
// Usage: npm run build-r2-h1-panel

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { iterateDict, dictExists } from "./lib/dict-parser.mjs";
import { R2_DICTS } from "./build-r2-source-anchors.mjs";
import { senseUnits } from "./build-r2-h1.mjs";

const OUT_DIR = path.resolve(process.cwd(), "data", "lexico");
const ARCHIVE_H1 = path.join(OUT_DIR, "r2_archive_h1.json");
const OUT_FILE = path.join(OUT_DIR, "r2_h1_panel.json");

const PANEL_SIZE = 30;
// Minimum number of the 11 H1 dicts a lemma must appear in to qualify
const MIN_DICT_COVERAGE = 7;

// The 11 dicts used in r2_h1 (from r2_archive_h1.json)
const H1_DICTS_META = JSON.parse(fs.readFileSync(ARCHIVE_H1, "utf8")).rows
  .filter(r => r.dict)
  .map(r => ({ code: r.dict, year: r.year, family: r.family }));

const SPLIT_BY_CODE = new Map(R2_DICTS.map(d => [d.code, d]));

// Strip trailing nominative H/M for cross-dict matching
export function stemKey(k) {
  return k.replace(/[HM]$/, "");
}

// WIL lex tags indicating a nominal entry
const NOMINAL_LEX = /\bm\b|\bf\b|\bn\b|mfn|mf\b|mn\b/;

// Build a stem→{k1, bodies[]} map aggregating ALL L-blocks per stem.
// This is critical for MW 1899 which splits the same base lemma into many
// short sub-entries; summing their senseUnits recovers the true per-lemma count.
function loadStemMap(dictCode) {
  const map = new Map();
  if (!dictExists(dictCode)) return map;
  for (const rec of iterateDict(dictCode)) {
    const stem = stemKey(rec.k1);
    if (!map.has(stem)) map.set(stem, { k1: rec.k1, bodies: [] });
    map.get(stem).bodies.push(rec.body || "");
  }
  return map;
}

function pearson(xs, ys) {
  const n = xs.length;
  if (n < 2) return 0;
  const mx = xs.reduce((a, b) => a + b, 0) / n;
  const my = ys.reduce((a, b) => a + b, 0) / n;
  let num = 0, dx = 0, dy = 0;
  for (let i = 0; i < n; i++) {
    const a = xs[i] - mx, b = ys[i] - my;
    num += a * b; dx += a * a; dy += b * b;
  }
  return dx && dy ? Number((num / Math.sqrt(dx * dy)).toFixed(3)) : 0;
}

function r3(n) { return Number(n.toFixed(3)); }

async function main() {
  process.stderr.write("Loading stem maps for 11 H1 dicts...\n");

  const stemMaps = new Map();
  for (const dm of H1_DICTS_META) {
    stemMaps.set(dm.code, loadStemMap(dm.code));
    process.stderr.write(`  ${dm.code}: ${stemMaps.get(dm.code).size} stems\n`);
  }

  // Use WIL as reference to enumerate nominal candidate lemmas
  const wilDict = SPLIT_BY_CODE.get("wil");
  const wilMap  = stemMaps.get("wil");

  // Score each WIL nominal lemma by coverage across the 11 H1 dicts.
  // Restrict WIL sense count to 2–8: moderate-polysemy nouns representative
  // of the full corpus (WIL full-corpus mean ≈ 1.8; panel nouns are slightly
  // above mean to ensure multiple senses across dicts).
  const candidates = [];
  for (const [stem, { bodies, k1 }] of wilMap) {
    const body = bodies[0] || "";
    const lexMatch = (body.match(/<lex>(.*?)<\/lex>/) || [])[1] || "";
    if (!NOMINAL_LEX.test(lexMatch)) continue;

    const wilUnits = bodies.reduce((s, b) => s + senseUnits(b, wilDict), 0);
    if (wilUnits < 2 || wilUnits > 8) continue;

    let coverage = 0;
    for (const dm of H1_DICTS_META) {
      if (stemMaps.get(dm.code)?.has(stem)) coverage++;
    }
    if (coverage < MIN_DICT_COVERAGE) continue;

    candidates.push({ stem, k1, wilUnits, coverage });
  }

  // Sort by coverage (most-covered first), then by WIL sense count descending
  candidates.sort((a, b) => b.coverage - a.coverage || b.wilUnits - a.wilUnits);
  const panel = candidates.slice(0, PANEL_SIZE).map(c => c.stem);

  process.stderr.write(`Panel (${panel.length}): ${panel.slice(0, 10).join(", ")}...\n`);
  process.stderr.write(`Coverage range: ${candidates[0]?.coverage} – ${candidates[PANEL_SIZE - 1]?.coverage}\n`);

  // Per-dict: compute mean sense-units over panel lemmas
  const dictRows = [];
  for (const dm of H1_DICTS_META) {
    const dictCfg = SPLIT_BY_CODE.get(dm.code) ?? { code: dm.code, split: "lumped-proxy" };
    const map = stemMaps.get(dm.code);
    let sumUnits = 0, found = 0;

    for (const stem of panel) {
      const entry = map?.get(stem);
      if (!entry) continue;
      // Aggregate all L-blocks: sum senseUnits across all bodies for this stem
      const lemmaUnits = entry.bodies.reduce((s, b) => s + senseUnits(b, dictCfg), 0);
      sumUnits += Math.max(1, lemmaUnits);
      found++;
    }

    const meanUnits = found > 0 ? r3(sumUnits / found) : null;
    dictRows.push({
      dict: dm.code,
      year: dm.year,
      family: dm.family,
      meanPanelUnits: meanUnits,
      panelLemmasFound: found,
      panelLemmasTotal: panel.length,
    });
    process.stderr.write(`  ${dm.code} (${dm.year}): meanPanelUnits=${meanUnits} (${found}/${panel.length} lemmas)\n`);
  }

  // Pearson r for all 11 dicts (skip dicts with null meanUnits)
  const forPearson = dictRows.filter(r => r.meanPanelUnits !== null);
  const rAll = pearson(forPearson.map(r => r.year), forPearson.map(r => r.meanPanelUnits));

  // Pearson r for only explicit-marker dicts (wil, ben, mw72, ap90, ap)
  const EXPLICIT_MARKER_DICTS = new Set(["wil", "ben", "mw72", "ap90", "ap"]);
  const forPearsonExplicit = forPearson.filter(r => EXPLICIT_MARKER_DICTS.has(r.dict));
  const rExplicit = pearson(forPearsonExplicit.map(r => r.year), forPearsonExplicit.map(r => r.meanPanelUnits));

  process.stderr.write(`Pearson r (all 11): ${rAll} vs archived ~0.01\n`);
  process.stderr.write(`Pearson r (explicit-marker 5): ${rExplicit} vs archived ~0.56 (n=5, non-significant)\n`);

  const output = {
    schemaVersion: "0.1.0",
    generatedBy: "npm run build-r2-h1-panel",
    claim: "Fixed-lemma panel removes headword-splitting confound; year-trend stays flat (H1 not supported).",
    panel,
    panelSize: panel.length,
    minDictCoverage: MIN_DICT_COVERAGE,
    stats: {
      pearsonYearVsUnits: rAll,
      pearsonExplicitMarkerDicts: rExplicit,
      nDictsInPearson: forPearson.length,
      nExplicitMarkerDicts: forPearsonExplicit.length,
      archivedPearsonAll: 0.01,
      archivedPearsonExplicit: 0.56,
    },
    rows: dictRows,
    limitations: [
      "Panel selected from WIL nominal entries (m./f./n./mfn.) present in ≥" + MIN_DICT_COVERAGE + " of the 11 H1 dicts.",
      "Indigenous dicts (skd, vcp) use different headword conventions; stem-key matching may miss some panel lemmas.",
      "senseUnits() uses the same proxy as r2_h1 (unchanged); calibration drift documented there.",
      "r_explicit = 0.56 among 5 explicit-marker dicts is n=5 non-significant and convention-confounded.",
      "Archive parity is a regression signal, not an optimization target.",
    ],
  };

  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(OUT_FILE, JSON.stringify(output, null, 2));
  console.log(`Wrote ${path.relative(process.cwd(), OUT_FILE)}`);
  console.log(`Pearson r (all 11): ${rAll} (archived ~0.01) — explicit-marker (5): ${rExplicit} (archived ~0.56)`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
