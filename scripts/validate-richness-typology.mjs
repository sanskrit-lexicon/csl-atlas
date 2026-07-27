// Validate the M1 data-richness typology packet (H1511).
//
// Fails (exit 1) when:
// - the output JSON is missing or unparseable;
// - a row is missing a required field, or `level` disagrees with a fresh
//   recompute of the cumulative L1..L9 chain from its own `criteria`;
// - `level` is outside 0..9 (L10 can never be the reported `level` — it is
//   always `met:false` by design) or `levelName` disagrees with `levels`;
// - L9 rows are not qualified "partial", or L10's criterion is not met:false;
// - every locally-present csl-orig/v02 dict (per data/dictionary-coverage.json
//   plus the documented NMMB fallback) has exactly one row — no duplicates,
//   no silent drops;
// - the row-count-by-level summary disagrees with a recount of `rows`.
//
// Usage: npm run validate-richness-typology (run after build-richness-typology)

import fs from "node:fs";
import path from "node:path";

const OUT_PATH = path.resolve(process.cwd(), "src", "data", "dicts", "richness-typology.json");
const COVERAGE_PATH = path.resolve(process.cwd(), "data", "dictionary-coverage.json");

const errors = [];
const notes = [];

function readJson(file) {
  if (!fs.existsSync(file)) {
    errors.push(`Missing required output: ${path.relative(process.cwd(), file)}`);
    return null;
  }
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch (e) {
    errors.push(`Unparseable JSON: ${path.relative(process.cwd(), file)} (${e.message})`);
    return null;
  }
}

const packet = readJson(OUT_PATH);
const coverage = readJson(COVERAGE_PATH);

if (packet && coverage) {
  const levelNames = new Map((packet.levels ?? []).map(l => [l.level, l.name]));
  if (levelNames.size !== 11) errors.push(`levels should enumerate L0..L10 (11 entries), found ${levelNames.size}`);

  const seenSourceCodes = new Set();
  const byLevelRecount = {};

  for (const row of packet.rows ?? []) {
    for (const field of ["code", "sourceCode", "level", "levelName", "levelQualifier", "criteria"]) {
      if (row[field] === undefined || row[field] === null) errors.push(`${row.code ?? "?"}: missing field ${field}`);
    }
    if (seenSourceCodes.has(row.sourceCode)) errors.push(`Duplicate sourceCode ${row.sourceCode}`);
    seenSourceCodes.add(row.sourceCode);

    if (!(row.level >= 0 && row.level <= 9)) errors.push(`${row.code}: level ${row.level} out of range 0..9 (L10 is never a reported level)`);
    if (levelNames.get(row.level) !== row.levelName) errors.push(`${row.code}: levelName "${row.levelName}" does not match levels[${row.level}].name "${levelNames.get(row.level)}"`);

    // Recompute the cumulative chain from this row's own criteria and check it matches.
    let recomputed = 0;
    for (let n = 1; n <= 9; n += 1) {
      const c = row.criteria?.[`l${n}`];
      if (!c) { errors.push(`${row.code}: criteria.l${n} missing`); break; }
      if (c.met) recomputed = n;
      else break;
    }
    if (recomputed !== row.level) errors.push(`${row.code}: level ${row.level} != recomputed ${recomputed} from criteria.l1..l9`);

    const l10 = row.criteria?.l10;
    if (!l10 || l10.met !== false) errors.push(`${row.code}: criteria.l10.met must be false (L10 is out of atlas scope by design)`);

    if (row.level === 9 && row.levelQualifier !== "partial") {
      errors.push(`${row.code}: level 9 must carry levelQualifier "partial" (M0a live-site scrape has not run) — got "${row.levelQualifier}"`);
    }

    byLevelRecount[row.level] = (byLevelRecount[row.level] ?? 0) + 1;
  }

  // Every dict in the coverage packet, plus the documented NMMB fallback, has exactly one row.
  const coverageCodes = new Set((coverage.dicts ?? []).map(d => d.sourceCode));
  for (const code of coverageCodes) {
    if (!seenSourceCodes.has(code)) errors.push(`Dict "${code}" present in data/dictionary-coverage.json but missing a richness-typology row`);
  }
  for (const code of seenSourceCodes) {
    if (!coverageCodes.has(code) && code !== "nmmb") {
      errors.push(`Row "${code}" is not in data/dictionary-coverage.json and is not the documented NMMB fallback`);
    }
  }
  if (packet.rowCount !== (packet.rows ?? []).length) errors.push(`rowCount ${packet.rowCount} != rows.length ${(packet.rows ?? []).length}`);

  for (const [level, count] of Object.entries(byLevelRecount)) {
    if (packet.summary?.byLevel?.[level] !== count) {
      errors.push(`summary.byLevel[${level}]=${packet.summary?.byLevel?.[level]} != recounted ${count}`);
    }
  }

  if (packet.evidenceLabel !== "derived") errors.push(`evidenceLabel is "${packet.evidenceLabel}", expected "derived"`);

  notes.push(`${packet.rowCount} dictionaries classified; by level: ${JSON.stringify(packet.summary?.byLevel)}`);
}

for (const n of notes) console.log(`note: ${n}`);
if (errors.length) {
  console.error(`\nvalidate-richness-typology FAILED with ${errors.length} error(s):`);
  for (const e of errors) console.error(`  - ${e}`);
  process.exit(1);
}
console.log("validate-richness-typology OK.");
