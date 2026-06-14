// Validate Comparative Dictionary Lab outputs.
//
// Fails (exit 1) when a required output is missing/unparseable, the index is
// empty, a present dictionary contributed no lemmas, the all-dictionary
// intersection is empty, or deep examples lack link-safe source pointers.
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
  "lemma-lookup.json",
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

function scope(doc, id) {
  return doc?.scopes?.[id] ?? doc;
}

function validateFeatureSupport(doc, name) {
  if (!Array.isArray(doc.includedDictionaries)) {
    errors.push(`${name} missing includedDictionaries.`);
    return new Set();
  }
  if (!Array.isArray(doc.unavailableDictionaries)) {
    errors.push(`${name} missing unavailableDictionaries.`);
    return new Set();
  }
  if (!Array.isArray(doc.methodNotes) || doc.methodNotes.length === 0) {
    errors.push(`${name} missing methodNotes.`);
  }
  if (!doc.includedDictionaries.length) errors.push(`${name} has no included feature adapters.`);
  notes.push(`${name} uses ${doc.includedDictionaries.length} adapter(s); ${doc.unavailableDictionaries.length} unavailable in this feature.`);
  return new Set(doc.unavailableDictionaries.map(d => d.label));
}

function hasSourcePointer(example) {
  if (example?.href) return true;
  return example?.sourceLinkMode === "local-only" &&
    typeof example?.sourcePath === "string" &&
    example.sourcePath.length > 0 &&
    Number.isFinite(example?.line) &&
    example.line > 0;
}

const cov = docs["coverage-matrix.json"];
if (cov) {
  const broad = scope(cov, "broadHeadword");
  const core = scope(cov, "coreComparison");
  if (cov.defaultScope && cov.defaultScope !== "broadHeadword") errors.push(`coverage-matrix defaultScope is ${cov.defaultScope}, expected broadHeadword.`);
  if (broad.dictionaryCount !== 40) errors.push(`Broad coverage has ${broad.dictionaryCount} dictionaries, expected 40.`);
  if (core.dictionaryCount !== 7) errors.push(`Core coverage has ${core.dictionaryCount} dictionaries, expected 7.`);
  if (!(broad.distinctLemmas > 0)) errors.push("broad coverage-matrix has no lemmas.");
  for (const [label, n] of Object.entries(broad.lemmasByDict || {})) {
    if (!(n > 0)) errors.push(`Dictionary ${label} contributed 0 lemmas.`);
  }
  notes.push(`Indexed ${broad.distinctLemmas} broad distinct lemmas across ${Object.keys(broad.lemmasByDict || {}).length} dictionaries.`);
  notes.push(`Core coverage keeps ${core.distinctLemmas} distinct lemmas across ${Object.keys(core.lemmasByDict || {}).length} dictionaries.`);
}

const inter = docs["all-intersection.json"];
if (inter) {
  const broad = scope(inter, "broadHeadword");
  const core = scope(inter, "coreComparison");
  if (typeof broad.count !== "number") errors.push("broad all-dictionary intersection missing numeric count.");
  if (!(core.count > 0)) errors.push("core all-dictionary intersection is empty.");
  else notes.push(`${core.count} lemmas shared by all core target dictionaries.`);
  notes.push(`${broad.count} lemmas shared by all broad target dictionaries (zero is allowed).`);
}

const pairDoc = docs["pairwise-overlap.json"];
if (pairDoc) {
  const broad = scope(pairDoc, "broadHeadword");
  const core = scope(pairDoc, "coreComparison");
  if ((broad.pairwise || []).length !== 780) errors.push(`Broad pairwise overlap has ${(broad.pairwise || []).length} rows, expected 780.`);
  if ((core.pairwise || []).length !== 21) errors.push(`Core pairwise overlap has ${(core.pairwise || []).length} rows, expected 21.`);
  else notes.push("Pairwise overlap has broad 40 and core 7 row counts.");
}

const pos = docs["pos-disagreement.json"];
if (pos) {
  const unavailableLabels = validateFeatureSupport(pos, "pos-disagreement");
  const missing = (pos.conflicts || []).filter(c => !Array.isArray(c.examples) || c.examples.some(e => !hasSourcePointer(e)));
  if (missing.length) errors.push(`${missing.length} gender conflicts lack link-safe source pointers.`);
  const unavailableEvidence = (pos.conflicts || []).filter(c => Object.keys(c.byDict || {}).some(label => unavailableLabels.has(label)));
  if (unavailableEvidence.length) errors.push(`${unavailableEvidence.length} gender conflicts include unavailable dictionaries.`);
  if (!missing.length && !unavailableEvidence.length) notes.push(`${pos.conflictCount} gender conflicts (${pos.shown} sampled), all with link-safe source pointers.`);
}

const hom = docs["homonym-split.json"];
if (hom) {
  const unavailableLabels = validateFeatureSupport(hom, "homonym-split");
  if (typeof hom.candidateCount !== "number") errors.push("homonym-split missing candidateCount.");
  const missing = (hom.candidates || []).filter(c => !Array.isArray(c.examples) || c.examples.some(e => !hasSourcePointer(e)));
  if (missing.length) errors.push(`${missing.length} homonym-split candidates lack link-safe source pointers.`);
  const unavailableEvidence = (hom.candidates || []).filter(c => Object.keys(c.byDict || {}).some(label => unavailableLabels.has(label)));
  if (unavailableEvidence.length) errors.push(`${unavailableEvidence.length} homonym-split candidates include unavailable dictionaries.`);
  if (!missing.length && !unavailableEvidence.length) notes.push(`${hom.candidateCount} homonym-split candidates (${hom.shown} shown), all with link-safe source pointers.`);
}

const sense = docs["sense-depth.json"];
if (sense) {
  const unavailableLabels = validateFeatureSupport(sense, "sense-depth");
  if (!Array.isArray(sense.perDict) || sense.perDict.length < 2) errors.push("sense-depth needs >=2 dictionaries.");
  const missing = (sense.topDisparities || []).filter(c => !Array.isArray(c.examples) || c.examples.some(e => !e.href));
  if (missing.length) errors.push(`${missing.length} sense-depth disparities lack source links.`);
  const unavailableEvidence = (sense.topDisparities || []).filter(c => Object.keys(c.byDict || {}).some(label => unavailableLabels.has(label)));
  if (unavailableEvidence.length) errors.push(`${unavailableEvidence.length} sense-depth disparities include unavailable dictionaries.`);
  if (!missing.length && !unavailableEvidence.length) notes.push(`${sense.disparityCount} sense-depth disparities (${sense.shown} shown), all with source links.`);
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

const lookup = docs["lemma-lookup.json"];
if (lookup) {
  if (!(lookup.count > 0) || !Array.isArray(lookup.entries) || lookup.entries.length === 0) {
    errors.push("lemma-lookup has no entries.");
  } else if (lookup.count !== lookup.entries.length) {
    errors.push(`lemma-lookup count ${lookup.count} does not match entries length ${lookup.entries.length}.`);
  } else {
    const malformed = lookup.entries.filter(e =>
      !Array.isArray(e) ||
      typeof e[0] !== "string" ||
      !Array.isArray(e[1]) ||
      e[1].length === 0 ||
      (lookup.minDicts && e[1].length < lookup.minDicts) ||
      e[1].some(d =>
        !Array.isArray(d) ||
        d.length < 3 ||
        !Number.isInteger(d[0]) ||
        d[0] < 0 ||
        d[0] >= (lookup.dictionaries || []).length ||
        !(d[1] > 0) ||
        !(d[2] > 0)
      )
    );
    if (malformed.length) errors.push(`${malformed.length} malformed lemma-lookup entries.`);
    else notes.push(`Reader lookup covers ${lookup.count} normalized lemmas (>= ${lookup.minDicts ?? 1} dictionaries).`);
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
