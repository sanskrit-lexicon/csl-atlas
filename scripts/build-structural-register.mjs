// Build the H6 structural-register scatter input.
//
// H6 asks whether citation style plus grammar marking predicts dictionary
// family. This generator keeps the claim dictionary-first and static: it joins
// the all-dictionary coverage layer with the M1-M5 microstructure fingerprint
// and emits one compact chart row per dictionary.
//
// Usage: npm run build-structural-register. No backend and no external repo data.

import fs from "node:fs";
import path from "node:path";

const SCHEMA_VERSION = "1.0.0";
const COVERAGE_PATH = path.resolve(process.cwd(), "data", "dictionary-coverage.json");
const FINGERPRINT_PATH = path.resolve(process.cwd(), "data", "lexico", "microstructure_fingerprint.json");
const OUT_DIR = path.resolve(process.cwd(), "src", "data", "dicts");
const OUT_PATH = path.join(OUT_DIR, "structural-register.json");

const FAMILY_BY_SOURCE = {
  abch: "specialized",
  acc: "index-catalogue",
  acph: "specialized",
  acsj: "specialized",
  ae: "reverse-bilingual",
  ap: "western-tagged",
  ap90: "western-tagged",
  armh: "specialized",
  ben: "western-tagged",
  bhs: "specialized",
  bop: "western-tagged",
  bor: "specialized",
  bur: "western-tagged",
  cae: "western-tagged",
  ccs: "western-tagged",
  fri: "specialized",
  gra: "western-tagged",
  gst: "specialized",
  ieg: "index-catalogue",
  inm: "index-catalogue",
  krm: "indigenous-prose",
  lan: "western-tagged",
  lrv: "western-tagged",
  mci: "index-catalogue",
  md: "western-tagged",
  mw: "western-tagged",
  mw72: "western-tagged",
  mwe: "reverse-bilingual",
  pe: "specialized",
  pgn: "specialized",
  pui: "index-catalogue",
  pw: "western-tagged",
  pwg: "western-tagged",
  pwkvn: "western-tagged",
  sch: "western-tagged",
  shs: "western-tagged",
  skd: "indigenous-prose",
  snp: "index-catalogue",
  stc: "western-tagged",
  vcp: "indigenous-prose",
  vei: "index-catalogue",
  wil: "western-tagged",
  yat: "western-tagged"
};

const FAMILY_LABELS = [
  "western-tagged",
  "indigenous-prose",
  "index-catalogue",
  "reverse-bilingual",
  "specialized",
  "unknown"
];

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function pct(value, label, errors) {
  const n = Number(value ?? 0);
  if (!Number.isFinite(n) || n < 0 || n > 100) {
    errors.push(`${label} must be a percentage in 0..100, got ${value}`);
    return 0;
  }
  return n;
}

function citationRegisterMode(taggedCitationPct, inlineItiPct) {
  const tagged = taggedCitationPct >= 5;
  const iti = inlineItiPct >= 5;
  if (tagged && iti) return "mixed";
  if (tagged) return "tagged";
  if (iti) return "iti";
  return "low";
}

function warningsFor(row) {
  const warnings = [];
  if (row.taggedCitationPct < 1 && row.inlineItiPct >= 5) {
    warnings.push("Citation evidence is prose/iti, not <ls>.");
  }
  if (row.grammarPct < 5 && row.dominantLayer === "root") {
    warnings.push("Grammar may live in indigenous root/prose conventions.");
  }
  if (row.records < 1000) {
    warnings.push("Small specialized source; structural percentages may be unstable.");
  }
  if (row.familyLabel === "index-catalogue") {
    warnings.push("Index/catalogue genre; compare cautiously with narrative dictionaries.");
  }
  if (!row.dominantLayer) {
    warnings.push("No M1-M5 microstructure layer detected; this may be a convention gap.");
  }
  return warnings;
}

function validateRows(rows) {
  const errors = [];
  const modes = new Set(["tagged", "iti", "mixed", "low"]);
  const families = new Set(FAMILY_LABELS);
  const seen = new Set();

  for (const row of rows) {
    for (const field of ["code", "sourceCode"]) {
      if (!row[field]) errors.push(`Missing ${field} in row ${JSON.stringify(row)}`);
    }
    if (seen.has(row.sourceCode)) errors.push(`Duplicate sourceCode ${row.sourceCode}`);
    seen.add(row.sourceCode);
    if (!(row.records >= 0)) errors.push(`${row.code}: records must be >= 0`);
    for (const field of ["grammarPct", "taggedCitationPct", "inlineItiPct", "citationRegisterPct"]) {
      pct(row[field], `${row.code}.${field}`, errors);
    }
    if (!modes.has(row.citationRegisterMode)) {
      errors.push(`${row.code}: invalid citationRegisterMode ${row.citationRegisterMode}`);
    }
    if (!families.has(row.familyLabel)) {
      errors.push(`${row.code}: invalid familyLabel ${row.familyLabel}`);
    }
  }

  if (errors.length) {
    console.error(`Structural-register validation failed with ${errors.length} error(s):`);
    for (const error of errors) console.error(`  - ${error}`);
    process.exit(1);
  }
}

function main() {
  const coverage = readJson(COVERAGE_PATH);
  const fingerprint = readJson(FINGERPRINT_PATH).dicts ?? {};
  const rows = [];
  const warnings = [];

  for (const d of coverage.dicts ?? []) {
    const sourceCode = d.sourceCode;
    const fp = fingerprint[sourceCode] ?? {};
    const blockPct = d.blockPct ?? {};
    const grammarPct = pct(blockPct.gram, `${d.code}.blockPct.gram`, warnings);
    const taggedCitationPct = pct(blockPct.citeTagged, `${d.code}.blockPct.citeTagged`, warnings);
    const inlineItiPct = pct(blockPct.citeInlineIti, `${d.code}.blockPct.citeInlineIti`, warnings);
    const citationRegisterPct = Math.max(taggedCitationPct, inlineItiPct);
    const familyLabel = FAMILY_BY_SOURCE[sourceCode] ?? "unknown";

    const row = {
      code: d.code,
      sourceCode,
      title: d.title,
      records: d.records,
      grammarPct,
      taggedCitationPct,
      inlineItiPct,
      citationRegisterPct,
      citationRegisterMode: citationRegisterMode(taggedCitationPct, inlineItiPct),
      fitBand: d.fitBand,
      fitScore: d.fitScore,
      dominantLayer: fp.dominant_layer ?? "",
      subentryPer1k: fp.subentry?.per_1k_entries ?? 0,
      xrefEdges: fp.xref?.edges ?? 0,
      rootEntries: fp.root?.entries ?? 0,
      familyLabel,
      warnings: []
    };
    row.warnings = warningsFor(row);
    rows.push(row);

    if (familyLabel === "unknown") warnings.push(`${d.code} has no curated family label.`);
    if (!fingerprint[sourceCode]) warnings.push(`${d.code} has no microstructure fingerprint row.`);
  }

  validateRows(rows);

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    generatedAt: new Date().toISOString(),
    claim: "H6: structural register predicts dictionary family.",
    evidenceLabel: "derived",
    reviewStatus: "machine-reviewed",
    sourceFiles: [
      "data/dictionary-coverage.json",
      "data/lexico/microstructure_fingerprint.json"
    ],
    familyLabels: FAMILY_LABELS,
    rowCount: rows.length,
    rows,
    assumptions: [
      "citationRegisterPct = max(blockPct.citeTagged, blockPct.citeInlineIti).",
      "citationRegisterMode is tagged, iti, mixed, or low using a 5% threshold.",
      "familyLabel is a curated interpretation aid, not proof of descent.",
      "dominantLayer comes from the M1-M5 microstructure fingerprint.",
      "No corpus, DCS, standards/export, GitHub, or organization metrics are inputs."
    ],
    warnings
  };

  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(OUT_PATH, `${JSON.stringify(payload, null, 2)}\n`);
  console.log(`Wrote ${path.relative(process.cwd(), OUT_PATH)} (${rows.length} dictionaries).`);
}

main();
