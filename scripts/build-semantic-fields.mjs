// Build the H4 semantic-field chart input.
//
// H4 asks whether dictionaries show measurable topical bias when their
// headword sets are projected onto the Amarakosa's native varga taxonomy. This
// generator keeps the Observable payload compact and dictionary-first.
//
// Usage: npm run build-semantic-fields. No backend, no corpus data.

import fs from "node:fs";
import path from "node:path";
import { licenseFields, generatedAtForPayload, readJsonIfExists } from "./lib/dataset-meta.mjs";

const SCHEMA_VERSION = "1.0.0";
const REPORT_PATH = path.resolve(process.cwd(), "data", "lexico", "semantic_field_report.json");
const COVERAGE_PATH = path.resolve(process.cwd(), "data", "lexico", "semantic_field_coverage.csv");
const OUT_DIR = path.resolve(process.cwd(), "src", "data", "dicts");
const OUT_PATH = path.join(OUT_DIR, "semantic-fields.json");

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

const LABELS = {
  pw: "PWK"
};

const CORE_DICTS = ["mw", "pw", "yat", "wil", "vcp", "shs", "pwg", "ap", "skd"];
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

function parseCsv(text) {
  const lines = text.trimEnd().split(/\r?\n/);
  const header = lines.shift().split(",");
  return lines.filter(Boolean).map(line => {
    const cells = line.split(",");
    return Object.fromEntries(header.map((h, i) => [h, cells[i] ?? ""]));
  });
}

function label(code) {
  return LABELS[code] ?? code.toUpperCase();
}

function family(code) {
  return FAMILY_BY_SOURCE[code] ?? "unknown";
}

function toNumber(value, fallback = 0) {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

function validate(payload) {
  const errors = [];
  const dictCodes = new Set(payload.dictionaries.map(d => d.code));
  const fieldKeys = new Set(payload.fields.map(f => f.fieldKey));

  if (payload.counts.fieldCount !== payload.fields.length) {
    errors.push(`fieldCount ${payload.counts.fieldCount} != fields.length ${payload.fields.length}`);
  }
  if (payload.counts.coverageRows !== payload.coverage.length) {
    errors.push(`coverageRows ${payload.counts.coverageRows} != coverage.length ${payload.coverage.length}`);
  }
  for (const row of payload.dictionaries) {
    if (!FAMILY_LABELS.includes(row.familyLabel)) errors.push(`${row.code}: invalid family ${row.familyLabel}`);
    if (row.coveragePct < 0 || row.coveragePct > 1) errors.push(`${row.code}: coveragePct out of range`);
  }
  for (const row of payload.coverage) {
    if (!dictCodes.has(row.code)) errors.push(`coverage row uses unknown dict ${row.code}`);
    if (!fieldKeys.has(row.fieldKey)) errors.push(`coverage row uses unknown field ${row.fieldKey}`);
    if (row.coveredLemmas > row.amarLemmas) errors.push(`${row.code}/${row.fieldKey}: covered > total`);
    if (row.coveragePct < 0 || row.coveragePct > 1) errors.push(`${row.code}/${row.fieldKey}: pct out of range`);
  }

  if (errors.length) {
    console.error(`Semantic-field chart build failed with ${errors.length} error(s):`);
    for (const error of errors.slice(0, 25)) console.error(`  - ${error}`);
    process.exit(1);
  }
}

function main() {
  const report = readJson(REPORT_PATH);
  const coverageCsv = parseCsv(fs.readFileSync(COVERAGE_PATH, "utf8"));
  const fields = report.fields.map(f => ({
    fieldKey: f.field_key,
    fieldOrder: f.field_order,
    kanda: f.kanda,
    varga: f.varga,
    upavarga: f.upavarga,
    amarEntries: f.amar_entries,
    amarLemmas: f.amar_lemmas
  }));

  const dictionaries = Object.entries(report.dictionaries)
    .map(([code, d]) => ({
      code,
      label: label(code),
      familyLabel: family(code),
      records: d.records,
      distinctHeadwords: d.distinct_headwords,
      coveredAmarLemmas: d.covered_amar_lemmas,
      coveragePct: d.coverage_pct,
      topFields: d.top_fields.map(f => ({
        fieldKey: f.field_key,
        varga: f.varga,
        coveragePct: f.coverage_pct,
        coveredLemmas: f.covered_lemmas,
        amarLemmas: f.amar_lemmas
      }))
    }))
    .sort((a, b) => b.coveragePct - a.coveragePct || a.label.localeCompare(b.label));

  const coverage = coverageCsv.map(row => ({
    code: row.dict,
    label: label(row.dict),
    familyLabel: family(row.dict),
    fieldKey: row.field_key,
    fieldOrder: toNumber(row.field_order),
    kanda: row.kanda,
    varga: row.varga,
    upavarga: row.upavarga,
    amarLemmas: toNumber(row.amar_lemmas),
    coveredLemmas: toNumber(row.covered_lemmas),
    coveragePct: toNumber(row.coverage_pct),
    coveredExamples: row.covered_examples ? row.covered_examples.split("|") : [],
    missingExamples: row.missing_examples ? row.missing_examples.split("|") : []
  }));
  const counts = {
    ...report.counts,
    fieldCount: report.counts.field_count ?? fields.length,
    semanticFieldRows: report.counts.semantic_field_rows ?? 0,
    distinctAmarLemmas: report.counts.distinct_amar_lemmas ?? 0,
    dictCount: report.counts.dict_count ?? dictionaries.length,
    dictionaryRows: dictionaries.length,
    coverageRows: coverage.length
  };

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    ...licenseFields(),
    generatedAt: new Date().toISOString(),
    claim: "H4: dictionaries have measurable Amarakosa-native semantic-field coverage profiles.",
    evidenceLabel: "derived",
    reviewStatus: "machine-reviewed",
    sourceFiles: [
      "data/lexico/semantic_fields.csv",
      "data/lexico/semantic_field_coverage.csv",
      "data/lexico/semantic_field_report.json",
      "scripts/lexico/m8_semantic_fields.py",
      "scripts/build-semantic-fields.mjs"
    ],
    counts,
    familyLabels: FAMILY_LABELS,
    coreDicts: CORE_DICTS,
    fields,
    dictionaries,
    coverage,
    assumptions: [
      "Field taxonomy is the Amarakosa kanda/varga/upavarga hierarchy from the local AMAR repo.",
      "Coverage means a normalized AMAR synonym appears as a dictionary <k1> headword.",
      "Normalization strips AMAR gender suffixes, accent marks, and trailing homonym digits.",
      "No DCS, corpus frequency, passage occurrence, standards/export, GitHub, or organization metrics are inputs."
    ],
    warnings: [
      "Headword coverage is not sense coverage, corpus attestation, or prose citation coverage.",
      "SKD and other prose-heavy dictionaries may know AMAR material without exposing every synonym as a comparable <k1> headword.",
      "Family labels are interpretive aids for the chart, not proof of descent."
    ]
  };

  validate(payload);
  payload.generatedAt = generatedAtForPayload(readJsonIfExists(OUT_PATH, fs), payload);
  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(OUT_PATH, `${JSON.stringify(payload, null, 2)}\n`);
  console.log(`Wrote ${path.relative(process.cwd(), OUT_PATH)} (${coverage.length} coverage rows).`);
}

main();
