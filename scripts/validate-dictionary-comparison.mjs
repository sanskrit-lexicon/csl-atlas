// Validate Comparative Dictionary Lab outputs.
//
// Fails (exit 1) when a required output is missing/unparseable, the index is
// empty, a present dictionary contributed no lemmas, the all-dictionary
// intersection is empty, or gender conflicts lack source links.
//
// Usage: npm run validate-dict-comparison (after build-dict-comparison)

import fs from "node:fs";
import path from "node:path";

const OUT_DIR = path.resolve(process.cwd(), "src", "data", "dicts");
const REQUIRED = [
  "coverage-matrix.json",
  "pairwise-overlap.json",
  "all-intersection.json",
  "dictionary-unique.json",
  "pos-disagreement.json",
  "alignment-confidence.json",
  "homonym-split.json",
  "sense-depth.json",
  "lemma-dossier.json",
  "dictionary-comparison-validation.json"
];

const errors = [];
const notes = [];

function read(name) {
  const file = path.join(OUT_DIR, name);
  if (!fs.existsSync(file)) {
    errors.push(`Missing required output: src/data/dicts/${name}`);
    return null;
  }
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

const docs = Object.fromEntries(REQUIRED.map(n => [n, read(n)]));

const cov = docs["coverage-matrix.json"];
if (cov) {
  if (!(cov.distinctLemmas > 0)) errors.push("coverage-matrix has no lemmas.");
  for (const [label, n] of Object.entries(cov.lemmasByDict || {})) {
    if (!(n > 0)) errors.push(`Dictionary ${label} contributed 0 lemmas.`);
  }
  notes.push(`Indexed ${cov.distinctLemmas} distinct lemmas across ${Object.keys(cov.lemmasByDict || {}).length} dictionaries.`);
}

const inter = docs["all-intersection.json"];
if (inter && !(inter.count > 0)) errors.push("all-dictionary intersection is empty.");
else if (inter) notes.push(`${inter.count} lemmas shared by all target dictionaries.`);

const pos = docs["pos-disagreement.json"];
if (pos) {
  const missing = (pos.conflicts || []).filter(c => !Array.isArray(c.examples) || c.examples.some(e => !e.href));
  if (missing.length) errors.push(`${missing.length} gender conflicts lack source links.`);
  else notes.push(`${pos.conflictCount} gender conflicts (${pos.shown} sampled), all with source links.`);
}

const hom = docs["homonym-split.json"];
if (hom) {
  if (typeof hom.candidateCount !== "number") errors.push("homonym-split missing candidateCount.");
  const missing = (hom.candidates || []).filter(c => !Array.isArray(c.examples) || c.examples.some(e => !e.href));
  if (missing.length) errors.push(`${missing.length} homonym-split candidates lack source links.`);
  else notes.push(`${hom.candidateCount} homonym-split candidates (${hom.shown} shown), all with source links.`);
}

const sense = docs["sense-depth.json"];
if (sense) {
  if (!Array.isArray(sense.perDict) || sense.perDict.length < 2) errors.push("sense-depth needs >=2 dictionaries.");
  const missing = (sense.topDisparities || []).filter(c => !Array.isArray(c.examples) || c.examples.some(e => !e.href));
  if (missing.length) errors.push(`${missing.length} sense-depth disparities lack source links.`);
  else notes.push(`${sense.disparityCount} sense-depth disparities (${sense.shown} shown), all with source links.`);
}

const dossier = docs["lemma-dossier.json"];
if (dossier) {
  if (!(dossier.count > 0) || !Array.isArray(dossier.entries) || dossier.entries.length === 0) {
    errors.push("lemma-dossier has no entries.");
  } else if (dossier.entries.some(e => !e.l || !Array.isArray(e.d) || e.d.length < dossier.minDicts)) {
    errors.push("lemma-dossier has malformed entries (missing lemma or too few dictionaries).");
  } else {
    notes.push(`Dossier covers ${dossier.count} lemmas (>= ${dossier.minDicts} dictionaries).`);
  }
}

const report = docs["dictionary-comparison-validation.json"];
if (report && (report.warnings || []).length) {
  notes.push(`Validation report present with ${report.warnings.length} warning(s).`);
}

for (const n of notes) console.log(`ok  ${n}`);
if (report && (report.warnings || []).length) {
  console.log("\nwarnings (non-fatal):");
  for (const w of report.warnings) console.log(`  ! ${w}`);
}
if (errors.length) {
  console.error(`\nFAILED with ${errors.length} error(s):`);
  for (const e of errors) console.error(`  x ${e}`);
  process.exit(1);
}
console.log("\nDictionary comparison validation passed.");
