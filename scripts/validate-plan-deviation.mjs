// Validate the committed plan-deviation table and the report that quotes it (H6984).
//
// The table (data/plan_deviation.tsv) is the source of truth: one row per
// (dictionary, axis), 17 dictionaries x 3 axes. The report
// (reports/DICTIONARY_PLAN_DEVIATION_2026-10-18.md) quotes aggregates computed
// from it, so the aggregates are pinned here — a data edit that moves a quoted
// number fails CI instead of leaving the prose stale.
//
// Fails (exit 1) when:
// - the TSV header or row width disagrees with the declared schema;
// - a dictionary does not carry exactly the three axes volumes/pages/years;
// - a ratio does not recompute from plan_value/delivered_value;
// - a classification disagrees with its own ratio band (PLAN-KEPT < 1.5,
//   PLAN-MISSED 1.5-4, PLAN-BROKEN > 4);
// - a row with no documented plan carries a plan value, a source class, or a
//   ratio, or a plan-bearing row carries an empty source;
// - a source class falls outside {literature, secondary, none};
// - a pinned aggregate (counts, medians, means) no longer matches the table;
// - the report no longer contains the pinned strings it must quote.
//
// Usage: npm run validate-plan-deviation

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const TSV = path.join(ROOT, "data", "plan_deviation.tsv");
const REPORT = path.join(ROOT, "reports", "DICTIONARY_PLAN_DEVIATION_2026-10-18.md");

const COLUMNS = [
  "dict_id", "name", "group", "axis", "plan_value", "plan_unit", "plan_declared",
  "plan_source", "plan_source_class", "delivered_value", "delivered_unit",
  "outcome_source", "outcome_source_class", "ratio", "classification", "status",
  "basis", "caveat"
];
const AXES = ["volumes", "pages", "years"];
const OPTIONAL_AXES = ["entries"];
const CLASSES = ["PLAN-KEPT", "PLAN-MISSED", "PLAN-BROKEN", "NO-DOCUMENTED-PLAN", "IN-PROGRESS"];
const SOURCE_CLASSES = ["literature", "secondary", "none"];

// Aggregates the report quotes. If the table moves, these must move with it —
// and so must the matching strings in the report (checked below).
const PINNED = {
  rows: 52,
  dictionaries: 17,
  documented_dictionaries: 6,
  undocumented_dictionaries: 11,
  no_documented_plan_rows: 41,
  plan_missed_rows: 3,
  plan_broken_rows: 5,
  in_progress_rows: 3,
  size_ratios: 3,
  duration_ratios: 4,
  size_median: 2.50,
  size_mean: 3.28,
  duration_median: 8.90,
  duration_mean: 8.75
};

const REPORT_PINS = [
  "41 of 52",
  "6 of 17",
  "2.50",
  "8.90",
  "3.28",
  "8.75"
];

const errors = [];
function fail(message) { errors.push(message); }

function readTsv(file) {
  const text = fs.readFileSync(file, "utf8").replace(/\r\n/g, "\n");
  const lines = text.split("\n").filter((line) => line.length > 0);
  const header = lines[0].split("\t");
  const rows = lines.slice(1).map((line, index) => {
    const cells = line.split("\t");
    if (cells.length !== header.length) fail(`row ${index + 2}: ${cells.length} cells, header has ${header.length}`);
    const record = {};
    header.forEach((column, i) => { record[column] = cells[i]; });
    return record;
  });
  return { header, rows };
}

function num(value) {
  if (value === undefined || value === "") return null;
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) { fail(`non-numeric value ${JSON.stringify(value)}`); return null; }
  return parsed;
}

function median(values) {
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}

function mean(values) {
  return values.reduce((a, b) => a + b, 0) / values.length;
}

const { header, rows } = readTsv(TSV);

if (header.join("|") !== COLUMNS.join("|")) {
  fail(`header mismatch:\n  expected ${COLUMNS.join("|")}\n  found    ${header.join("|")}`);
}

// --- per-row integrity ---
const byDict = new Map();
for (const [index, row] of rows.entries()) {
  const where = `row ${index + 2} (${row.dict_id || "?"}/${row.axis || "?"})`;
  const plan = num(row.plan_value);
  const delivered = num(row.delivered_value);
  const ratio = num(row.ratio);

  if (!AXES.includes(row.axis) && !OPTIONAL_AXES.includes(row.axis)) fail(`${where}: unknown axis ${JSON.stringify(row.axis)}`);
  if (!CLASSES.includes(row.classification)) fail(`${where}: unknown classification ${JSON.stringify(row.classification)}`);
  if (!SOURCE_CLASSES.includes(row.plan_source_class)) fail(`${where}: unknown plan_source_class ${JSON.stringify(row.plan_source_class)}`);
  if (!SOURCE_CLASSES.includes(row.outcome_source_class)) fail(`${where}: unknown outcome_source_class ${JSON.stringify(row.outcome_source_class)}`);

  if (!byDict.has(row.dict_id)) byDict.set(row.dict_id, []);
  byDict.get(row.dict_id).push(row.axis);

  if (row.classification === "NO-DOCUMENTED-PLAN") {
    if (plan !== null) fail(`${where}: NO-DOCUMENTED-PLAN must carry no plan value`);
    if (row.plan_source !== "") fail(`${where}: NO-DOCUMENTED-PLAN must carry no plan source`);
    if (row.plan_source_class !== "none") fail(`${where}: NO-DOCUMENTED-PLAN must be source_class none`);
    if (ratio !== null) fail(`${where}: NO-DOCUMENTED-PLAN must carry no ratio`);
    continue;
  }

  if (!row.plan_source) fail(`${where}: a documented plan needs a source`);
  if (row.plan_source_class === "none") fail(`${where}: a documented plan needs a source class`);
  if (plan === null) fail(`${where}: missing plan value`);

  if (ratio !== null && plan !== null && delivered !== null) {
    const recomputed = delivered / plan;
    if (Math.abs(recomputed - ratio) > 0.011) {
      fail(`${where}: ratio ${ratio} disagrees with delivered/plan = ${recomputed.toFixed(4)}`);
    }
  }

  if (row.basis === "outcome" || row.basis === "outcome so far (floor)" || row.basis === "projection") {
    if (ratio === null) { fail(`${where}: a deviation basis needs a ratio`); continue; }
    const expected = ratio < 1.5 ? "PLAN-KEPT" : ratio <= 4 ? "PLAN-MISSED" : "PLAN-BROKEN";
    if (row.classification !== expected) {
      fail(`${where}: ratio ${ratio} bands as ${expected}, table says ${row.classification}`);
    }
  }
}

// --- shape: every dictionary carries all three axes exactly once ---
for (const [dict, axes] of byDict.entries()) {
  // Every dictionary carries the three core axes exactly once; `entries` is an
  // optional fourth, present only where an entry plan is documented (CDPL).
  for (const axis of AXES) {
    const n = axes.filter((a) => a === axis).length;
    if (n !== 1) fail(`${dict}: axis ${axis} appears ${n} times, expected 1`);
  }
  for (const axis of OPTIONAL_AXES) {
    if (axes.filter((a) => a === axis).length > 1) fail(`${dict}: axis ${axis} appears more than once`);
  }
  const unknown = axes.filter((a) => !AXES.includes(a) && !OPTIONAL_AXES.includes(a));
  if (unknown.length) fail(`${dict}: unknown axes ${unknown.join(", ")}`);
  if (axes.length !== AXES.length + axes.filter((a) => OPTIONAL_AXES.includes(a)).length) {
    fail(`${dict}: ${axes.length} rows for ${axes.length} distinct axes — duplicates?`);
  }
}

// --- pinned aggregates ---
const count = (predicate) => rows.filter(predicate).length;
const documentedDicts = new Set(
  rows.filter((r) => r.classification !== "NO-DOCUMENTED-PLAN").map((r) => r.dict_id)
);

// "outcome" covers the finished ratio and the still-running floor ("outcome so
// far (floor)"); projections and progress are deliberately excluded.
const isOutcome = (r) => r.basis.startsWith("outcome");
const sizeRows = rows.filter((r) => isOutcome(r) && (r.axis === "volumes" || r.axis === "pages" || r.axis === "entries") && r.ratio !== "");
const durationRows = rows.filter((r) => isOutcome(r) && r.axis === "years" && r.ratio !== "");
const sizeRatios = sizeRows.map((r) => Number(r.ratio));
const durationRatios = durationRows.map((r) => Number(r.ratio));

const computed = {
  rows: rows.length,
  dictionaries: byDict.size,
  documented_dictionaries: documentedDicts.size,
  undocumented_dictionaries: byDict.size - documentedDicts.size,
  no_documented_plan_rows: count((r) => r.classification === "NO-DOCUMENTED-PLAN"),
  plan_missed_rows: count((r) => r.classification === "PLAN-MISSED"),
  plan_broken_rows: count((r) => r.classification === "PLAN-BROKEN"),
  in_progress_rows: count((r) => r.classification === "IN-PROGRESS"),
  size_ratios: sizeRatios.length,
  duration_ratios: durationRatios.length
};

for (const [key, expected] of Object.entries(computed)) {
  if (expected !== PINNED[key]) fail(`pinned ${key}: table has ${expected}, validator pins ${PINNED[key]}`);
}

const sizeMedian = median(sizeRatios);
const sizeMean = mean(sizeRatios);
const durationMedian = median(durationRatios);
const durationMean = mean(durationRatios);
for (const [label, value, pinned] of [
  ["size median", sizeMedian, PINNED.size_median],
  ["size mean", sizeMean, PINNED.size_mean],
  ["duration median", durationMedian, PINNED.duration_median],
  ["duration mean", durationMean, PINNED.duration_mean]
]) {
  if (Math.abs(value - pinned) > 0.006) fail(`pinned ${label}: computed ${value.toFixed(3)}, pinned ${pinned.toFixed(2)}`);
}

// --- report pins: the prose must still quote what the table now holds ---
if (!fs.existsSync(REPORT)) {
  fail(`report missing: ${REPORT}`);
} else {
  const report = fs.readFileSync(REPORT, "utf8");
  for (const pin of REPORT_PINS) {
    if (!report.includes(pin)) fail(`report no longer contains the pinned string ${JSON.stringify(pin)}`);
  }
}

if (errors.length > 0) {
  console.error("validate-plan-deviation: FAIL");
  for (const error of errors) console.error("  - " + error);
  process.exit(1);
}

console.log(
  `validate-plan-deviation: PASS — ${rows.length} rows / ${byDict.size} dictionaries; ` +
  `${computed.documented_dictionaries} with a documented plan, ${computed.undocumented_dictionaries} without; ` +
  `size median ${sizeMedian.toFixed(2)}x (n=${sizeRatios.length}), duration median ${durationMedian.toFixed(2)}x (n=${durationRatios.length}).`
);
