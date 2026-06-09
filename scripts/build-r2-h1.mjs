// Restore the H1R sense-granularity generator from local csl-orig.
//
// SCAFFOLD (Explorer+H1 slice, 2026-06-09). Reproduces the archived
// /tools/r2-h1 figure: sense-units-per-entry over each dictionary's WHOLE
// corpus, by dict / family / year, with the headline that pure temporal
// inflation is NOT supported (Pearson r near 0; variance is by family).
//
// Reuses the documented split heuristics from build-r2-source-anchors.mjs; it
// does NOT promote any parser rule. Archive parity is a regression signal —
// see R2_REBUILD_CONTRACT.md acceptance gate "H1R reproduced".
//
// >>> REMAINING FILL-IN (Sonnet): calibrate `senseUnits()` so the per-dict
//     senseUnitsPerEntry lands on (or documents drift from) the archived
//     values in data/lexico/r2_archive_h1.json. The explicit-marker count and
//     especially the lumped-proxy `;`-clause count are the sensitive knobs.
//     The loop, dict/year/family map, family means, and Pearson r are done.
//
// Usage: npm run build-r2-h1

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { iterateDict, dictExists } from "./lib/dict-parser.mjs";
import { R2_DICTS, splitRecord } from "./build-r2-source-anchors.mjs";

const OUT_DIR = path.resolve(process.cwd(), "data", "lexico");
const ARCHIVE_H1 = path.join(OUT_DIR, "r2_archive_h1.json");
const H1_OUT = path.join(OUT_DIR, "r2_h1.json");

// The 11 plotted dictionaries with year + family. Years/families are taken from
// the archived fixture so the restore targets the same points; split mode is
// reused from the prototype's R2_DICTS.
function dictMeta() {
  const archive = JSON.parse(fs.readFileSync(ARCHIVE_H1, "utf8"));
  const splitByCode = new Map(R2_DICTS.map(d => [d.code, d.split]));
  return (archive.rows ?? [])
    .filter(r => r.dict) // dict rows only; family-mean rows handled separately
    .map(r => ({
      code: r.dict,
      year: r.year,
      family: r.family,
      split: splitByCode.get(r.dict) ?? "lumped-proxy",
      archivedUnits: r.senseUnitsPerEntry,
      archivedEntries: r.entries
    }));
}

// Explicit-marker modes used for H1 sense counting. "div" (PWG/PWK) is
// intentionally excluded here: the <div> tags are structural markers at
// multiple nesting depths; treating them as sense boundaries over-counts by
// ~40%. PWG is therefore counted via the semi-clause proxy, giving 1.127 vs
// archived 1.161 (3% drift). See R2_REBUILD_CONTRACT.md "document drift" rule.
const EXPLICIT_MODES = new Set(["ap-bullet", "number-marker", "dot-squared"]);

// Sense-units for one entry body under the dictionary's convention.
// For explicit-marker dicts: count explicit marker hits (>=1).
// For lumped / indigenous / div-structural dicts: `;`-delimited meaning clauses
// after stripping tags and <ls> citations (>=1) — the documented proxy.
//
// Calibration notes (computed vs archived):
//   pwg   1.127 vs 1.161  — div excluded; semi-clause closest (3% under)
//   ben   2.420 vs 2.529  — numeric {@ N. @} only; ~5% under
//     (BEN Roman {@I.@}/{@II.@} are POS-class markers in compound blocks, not senses)
//   wil   1.706 vs 1.800  — dot-squared markers; ~5% under
//   ap90  2.517 vs 2.721  — number-marker; ~8% under
//   ap    1.726 vs 1.978  — bullet markers; ~13% under (sub-bullet ∙³ unclear)
//   cae   1.355 vs 1.355  — exact
//   sch   1.139 vs 1.135  — near-exact
//   mw72  2.852 vs 2.903  — near-exact
// Key results hold despite drift: Pearson(year, units) ≈ 0; family ordering
// preserved (Benfey > Apte > MW ≈ Wilson > Cappeller > Petersburg > indigenous).
export function senseUnits(body, dict) {
  if (EXPLICIT_MODES.has(dict.split)) {
    const parts = splitRecord(body || "", dict).filter(p => p.splitConfidence === "explicit");
    return Math.max(1, parts.length);
  }
  const meaning = (body || "")
    .replace(/<ls\b[^>]*>[\s\S]*?<\/ls>/g, " ") // strip citations
    .replace(/<[^>]+>/g, " ")
    .replace(/\{[#%@][\s\S]*?[#%@]?\}/g, " ");
  const clauses = meaning.split(";").map(s => s.trim()).filter(Boolean);
  return Math.max(1, clauses.length);
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

function round3(n) {
  return Number(n.toFixed(3));
}

function main() {
  const meta = dictMeta();
  const rows = [];
  for (const dict of meta) {
    if (!dictExists(dict.code)) {
      console.warn(`Missing source for ${dict.code}; skipped.`);
      continue;
    }
    let entries = 0, units = 0;
    for (const rec of iterateDict(dict.code)) {
      entries += 1;
      units += senseUnits(rec.body || "", dict);
    }
    rows.push({
      dict: dict.code,
      year: dict.year,
      family: dict.family,
      senseUnitsPerEntry: entries ? round3(units / entries) : 0,
      entries,
      archivedSenseUnitsPerEntry: dict.archivedUnits,
      archivedEntries: dict.archivedEntries
    });
  }

  // Family means (the 7 archived family rows).
  const byFamily = new Map();
  for (const r of rows) {
    if (!byFamily.has(r.family)) byFamily.set(r.family, []);
    byFamily.get(r.family).push(r.senseUnitsPerEntry);
  }
  const familyRows = [...byFamily]
    .map(([family, vals]) => ({ family, meanSenseUnitsPerEntry: round3(vals.reduce((a, b) => a + b, 0) / vals.length), dicts: vals.length }))
    .sort((a, b) => b.meanSenseUnitsPerEntry - a.meanSenseUnitsPerEntry);

  const r = pearson(rows.map(x => x.year), rows.map(x => x.senseUnitsPerEntry));

  const payload = {
    schemaVersion: "0.1.0",
    status: "source-backed-r2-h1",
    claim: "H1R sense-granularity rebuilt from current csl-orig: pure temporal inflation is not supported; family captures the variance.",
    generatedBy: "npm run build-r2-h1",
    sourceRoot: "../csl-orig/v02",
    limitations: [
      "senseUnits() is a first-cut proxy; lumped-proxy `;`-clause counting needs calibration against the archived fixture.",
      "Per-entry metric is confounded by headword-splitting policy (MW splits compounds into many short entries); a fixed-lemma panel removes it (r2_h1_panel.json, future slice).",
      "Archive parity is a regression signal, not an optimization target."
    ],
    stats: {
      pearsonYearVsUnits: r,
      archivedPearson: 0.06,
      dictRows: rows.length,
      familyRows: familyRows.length
    },
    rows,
    families: familyRows
  };

  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(H1_OUT, `${JSON.stringify(payload, null, 2)}\n`);
  console.log(`Wrote ${path.relative(process.cwd(), H1_OUT)} (${rows.length} dict rows, ${familyRows.length} families)`);
  console.log(`Pearson(year, units) = ${r} (archived 0.06)`);
  for (const row of rows) {
    console.log(`  ${row.dict.padEnd(5)} ${row.senseUnitsPerEntry} vs archived ${row.archivedSenseUnitsPerEntry} | entries ${row.entries} vs ${row.archivedEntries}`);
  }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
