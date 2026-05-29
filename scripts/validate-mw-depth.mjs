// Validate MW Quantitative Depth outputs.
//
// Fails (exit 1) when:
// - parsed record count is unexpectedly far from 286561;
// - any required output JSON is missing;
// - deepest families have no source links;
// - type counts diverge from article-type-counts.json WITHOUT a warning.
//
// Usage: npm run validate-mw-depth (run after build-mw-depth)

import fs from "node:fs";
import path from "node:path";

const OUT_DIR = path.resolve(process.cwd(), "src", "data", "mw");
const EXPECTED_RECORD_COUNT = 286561;
const RECORD_TOLERANCE = 100;

const REQUIRED = [
  "mw-quantitative-summary.json",
  "mw-type-overlaps.json",
  "mw-depth-distribution.json",
  "mw-deepest-families.json",
  "mw-source-layer-summary.json",
  "mw-diachronic-profile.json",
  "mw-validation-report.json"
];

const errors = [];
const notes = [];

function read(name) {
  const file = path.join(OUT_DIR, name);
  if (!fs.existsSync(file)) {
    errors.push(`Missing required output: src/data/mw/${name}`);
    return null;
  }
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

// 1. All required files present + parseable.
const docs = Object.fromEntries(REQUIRED.map(n => [n, read(n)]));

// 2. Record count sane.
const summary = docs["mw-quantitative-summary.json"];
if (summary) {
  const rc = summary.recordCount;
  if (typeof rc !== "number" || Math.abs(rc - EXPECTED_RECORD_COUNT) > RECORD_TOLERANCE) {
    errors.push(`Record count ${rc} is far from expected ${EXPECTED_RECORD_COUNT}.`);
  } else {
    notes.push(`Record count ${rc} within tolerance of ${EXPECTED_RECORD_COUNT}.`);
  }
}

// 3. Deepest families have source links.
const fam = docs["mw-deepest-families.json"];
if (fam) {
  if (!Array.isArray(fam.families) || fam.families.length === 0) {
    errors.push("mw-deepest-families.json has no families.");
  } else {
    const missingLinks = fam.families.filter(
      f => !Array.isArray(f.topExamples) || f.topExamples.length === 0 || f.topExamples.some(e => !e.href)
    );
    if (missingLinks.length) {
      errors.push(`${missingLinks.length} deepest families lack source links in topExamples.`);
    } else {
      notes.push(`All ${fam.families.length} shown families carry source links.`);
    }
  }
}

// 4. Type-count divergences must be warned, not silent.
const report = docs["mw-validation-report.json"];
if (report) {
  const warned = new Set(
    (report.warnings || [])
      .map(w => (w.match(/Type "([^"]+)" diverges/) || [])[1])
      .filter(Boolean)
  );
  const tolerance = (type, exp) => Math.max(50, exp * 0.02);
  for (const d of report.typeDiffs || []) {
    if (Math.abs(d.diff) > tolerance(d.type, d.expected) && !warned.has(d.type)) {
      errors.push(`Type "${d.type}" diverges (diff ${d.diff}) without a warning.`);
    }
  }
  notes.push(`Validation report present with ${(report.warnings || []).length} warning(s).`);
}

// ---- Report. ----
for (const n of notes) console.log(`ok  ${n}`);
if (report && (report.warnings || []).length) {
  console.log("\nwarnings (non-fatal, expected from source drift):");
  for (const w of report.warnings) console.log(`  ! ${w}`);
}
if (errors.length) {
  console.error(`\nFAILED with ${errors.length} error(s):`);
  for (const e of errors) console.error(`  x ${e}`);
  process.exit(1);
}
console.log("\nMW depth validation passed.");
