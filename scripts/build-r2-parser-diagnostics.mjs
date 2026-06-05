// Build parser-drift diagnostics for the R2 source-backed anchor prototype.
//
// The source-backed R2 anchor rebuild intentionally exposes drift against the
// archived static pages. This artifact classifies that drift by parser family
// so the next rebuild work can tighten the right splitter without treating all
// row-count differences as the same problem.
//
// Usage: npm run build-r2-parser-diagnostics

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const SCHEMA_VERSION = "1.0.0";
const SUMMARY_PATH = path.resolve(process.cwd(), "data", "lexico", "r2_source_anchor_summary.json");
const SENSES_PATH = path.resolve(process.cwd(), "data", "lexico", "r2_source_anchor_senses.jsonl");
const OUT = path.resolve(process.cwd(), "data", "lexico", "r2_parser_diagnostics.json");

const CLASS_PRIORITY = {
  "over-split-candidate": 10,
  "reverse-overmatch": 9,
  "indigenous-coarse-review": 8,
  "archive-missing-from-source": 7,
  "under-split-or-source-gap": 6,
  "mild-drift": 5,
  "source-only-dictionary": 3,
  "archive-parity": 2,
  "no-anchor-evidence": 1
};

function round(value, digits = 4) {
  return Number(value.toFixed(digits));
}

function ratio(sourceRows, archivedRows) {
  if (!archivedRows) return null;
  return round(sourceRows / archivedRows, 3);
}

function isNearParity(sourceRows, archivedRows) {
  if (!archivedRows) return sourceRows === 0;
  return Math.abs(sourceRows - archivedRows) <= Math.max(1, archivedRows * 0.15);
}

export function classifyDrift(row) {
  const sourceRows = Number(row.sourceSenseRows || 0);
  const archivedRows = Number(row.archivedSenseRows || 0);

  if (sourceRows === 0 && archivedRows === 0) return "no-anchor-evidence";
  if (sourceRows === 0 && archivedRows > 0) return "archive-missing-from-source";
  if (row.parserFamily === "reverse" && sourceRows > 0) {
    return sourceRows > archivedRows + 3 ? "reverse-overmatch" : "mild-drift";
  }
  if (row.parserFamily === "indigenous" && sourceRows > 0) return "indigenous-coarse-review";
  if (archivedRows === 0 && sourceRows > 0) return "source-only-dictionary";
  if (isNearParity(sourceRows, archivedRows)) return "archive-parity";
  if (sourceRows >= archivedRows * 2) return "over-split-candidate";
  if (sourceRows < archivedRows) return "under-split-or-source-gap";
  return "mild-drift";
}

export function priorityForClass(driftClass) {
  if (CLASS_PRIORITY[driftClass] >= 8) return "high";
  if (CLASS_PRIORITY[driftClass] >= 5) return "medium";
  if (CLASS_PRIORITY[driftClass] >= 2) return "low";
  return "info";
}

function nextActionFor(row, driftClass) {
  if (driftClass === "over-split-candidate") {
    if (row.split === "div") return "Tighten PWG/PWK div splitting to top-level sense divisions before using rows as sense counts.";
    if (row.split === "number-marker") return "Constrain numbered-marker parsing so references or submarkers do not inflate BEN/AP90/BHS sense rows.";
    return "Tighten explicit marker scope before using rows as sense counts.";
  }
  if (driftClass === "reverse-overmatch") return "Use AE equivalent-position rank counts to choose review/filter bands before using reverse rows as alignments.";
  if (driftClass === "indigenous-coarse-review") return "Review iti-unit boundaries and authority quotations before treating rows as dictionary senses.";
  if (driftClass === "archive-missing-from-source") return "Resolve lookup-key, source-availability, or homonym-aggregation gap against the archived fixture.";
  if (driftClass === "under-split-or-source-gap") return "Check lookup variants, homonym aggregation, and marker coverage against the archived sense rows.";
  if (driftClass === "source-only-dictionary") return "Keep as source-backed rebuild expansion; no archived baseline exists for this dictionary/lemma pair.";
  if (driftClass === "archive-parity") return "Use as a positive parser-parity control while tightening higher-drift families.";
  if (driftClass === "mild-drift") return "Inspect after high-priority parser families; drift is visible but not currently blocking.";
  return "No current anchor evidence; revisit only when broadening R2 coverage.";
}

function countBy(rows, keyFn) {
  const counts = {};
  for (const row of rows) {
    const key = keyFn(row);
    counts[key] = (counts[key] || 0) + 1;
  }
  return Object.fromEntries(Object.entries(counts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
}

function readJsonl(file) {
  if (!fs.existsSync(file)) return [];
  return fs.readFileSync(file, "utf8")
    .split(/\r?\n/)
    .filter(Boolean)
    .map(line => JSON.parse(line));
}

function groupExamples(rows) {
  const grouped = new Map();
  for (const row of rows) {
    const key = `${row.lemma}:${row.dict}`;
    if (!grouped.has(key)) grouped.set(key, []);
    const bucket = grouped.get(key);
    if (bucket.length < 3) {
      bucket.push({
        rowId: row.rowId,
        senseId: row.senseId,
        sourceLine: row.sourceLine,
        href: row.href,
        splitConfidence: row.splitConfidence,
        limitations: row.limitations
      });
    }
  }
  return grouped;
}

function diagnosticRows(summary, senseRows) {
  const examples = groupExamples(senseRows);
  const rows = [];
  for (const lemma of summary.lemmas ?? []) {
    for (const row of lemma.byDict ?? []) {
      const driftClass = classifyDrift(row);
      const sourceRows = Number(row.sourceSenseRows || 0);
      const archivedRows = Number(row.archivedSenseRows || 0);
      rows.push({
        diagnosticId: `r2-drift:${lemma.lemma}:${row.dict}`,
        lemma: lemma.lemma,
        dict: row.dict,
        label: row.label,
        ownerRepo: "csl-atlas",
        parserFamily: row.parserFamily,
        split: row.split,
        sourceRecordCount: Number(row.sourceRecordCount || 0),
        sourceSenseRows: sourceRows,
        archivedSenseRows: archivedRows,
        sourceMinusArchive: sourceRows - archivedRows,
        sourceToArchiveRatio: ratio(sourceRows, archivedRows),
        splitConfidence: row.splitConfidence ?? [],
        ...(row.reverseRankCounts ? { reverseRankCounts: row.reverseRankCounts } : {}),
        sourceLines: row.sourceLines ?? [],
        driftClass,
        priority: priorityForClass(driftClass),
        nextAction: nextActionFor(row, driftClass),
        exampleRows: examples.get(`${lemma.lemma}:${row.dict}`) ?? []
      });
    }
  }
  return rows.sort((a, b) =>
    CLASS_PRIORITY[b.driftClass] - CLASS_PRIORITY[a.driftClass] ||
    Math.abs(b.sourceMinusArchive) - Math.abs(a.sourceMinusArchive) ||
    a.lemma.localeCompare(b.lemma) ||
    a.dict.localeCompare(b.dict)
  );
}

function worklistRows(rows) {
  return rows
    .filter(row => row.priority === "high" || row.priority === "medium")
    .slice(0, 30)
    .map(row => ({
      diagnosticId: row.diagnosticId,
      lemma: row.lemma,
      dict: row.dict,
      parserFamily: row.parserFamily,
      split: row.split,
      driftClass: row.driftClass,
      sourceSenseRows: row.sourceSenseRows,
      archivedSenseRows: row.archivedSenseRows,
      sourceToArchiveRatio: row.sourceToArchiveRatio,
      ...(row.reverseRankCounts ? { reverseRankCounts: row.reverseRankCounts } : {}),
      nextAction: row.nextAction
    }));
}

function validate(payload) {
  const errors = [];
  if (payload.ownerRepo !== "csl-atlas") errors.push("ownerRepo must be csl-atlas");
  if (!payload.diagnostics.length) errors.push("no diagnostic rows");
  for (const row of payload.diagnostics) {
    if (row.ownerRepo !== "csl-atlas") errors.push(`${row.diagnosticId}: ownerRepo must be csl-atlas`);
    if (!row.driftClass) errors.push(`${row.diagnosticId}: missing driftClass`);
    if (!row.nextAction) errors.push(`${row.diagnosticId}: missing nextAction`);
  }
  if (errors.length) {
    console.error(`R2 parser diagnostics failed with ${errors.length} error(s):`);
    for (const error of errors.slice(0, 25)) console.error(`  - ${error}`);
    process.exit(1);
  }
}

export function buildPayload(summary, senseRows) {
  const diagnostics = diagnosticRows(summary, senseRows);
  const payload = {
    schemaVersion: SCHEMA_VERSION,
    status: "r2-parser-diagnostics",
    claim: "R2 source/archive row-count drift is classified by parser family before the final splitter is restored.",
    evidenceLabel: "source-vs-archive",
    reviewStatus: "machine-reviewed",
    ownerRepo: "csl-atlas",
    generatedBy: "npm run build-r2-parser-diagnostics",
    sourceGeneratedBy: summary.generatedBy,
    sourceFiles: [
      "data/lexico/r2_source_anchor_summary.json",
      "data/lexico/r2_source_anchor_senses.jsonl",
      "data/lexico/r2_archive_explorer.json",
      "scripts/build-r2-source-anchors.mjs",
      "scripts/build-r2-parser-diagnostics.mjs"
    ],
    counts: {
      lemmaCount: summary.counts?.lemmaCount ?? 0,
      dictionaryCount: summary.counts?.dictionaryCount ?? 0,
      diagnosticRows: diagnostics.length,
      highPriorityRows: diagnostics.filter(row => row.priority === "high").length,
      mediumPriorityRows: diagnostics.filter(row => row.priority === "medium").length,
      byDriftClass: countBy(diagnostics, row => row.driftClass),
      byParserFamily: countBy(diagnostics, row => row.parserFamily)
    },
    method: [
      "Compare source-backed anchor row counts with recovered archived static-page counts for each lemma/dictionary pair.",
      "Classify drift into parser-work packages: explicit-marker over-splitting, reverse overmatching, indigenous iti review, source/archive gaps, source-only rebuild expansion, or parity controls.",
      "Rank rows by rebuild priority without changing the canonical R2 review-report schema or treating drift labels as philological decisions."
    ],
    priorityWorklist: worklistRows(diagnostics),
    diagnostics,
    limitations: [
      "This artifact diagnoses the prototype R2 rebuild; it is not the final sense corpus.",
      "Archived static pages are comparison fixtures, not regenerated source truth.",
      "Row-count parity does not prove semantic sense equivalence.",
      "Drift classes are machine labels for parser work, not scholar-reviewed sense decisions."
    ],
    boundary: [
      "This artifact uses dictionary source rows and recovered atlas R2 fixtures only.",
      "No DCS, corpus frequency, TEI/OntoLex, FrAC, GitHub, organization-process evidence, runtime LLM, database, or backend input is used."
    ]
  };
  validate(payload);
  return payload;
}

function main() {
  const summary = JSON.parse(fs.readFileSync(SUMMARY_PATH, "utf8"));
  const senseRows = readJsonl(SENSES_PATH);
  const payload = buildPayload(summary, senseRows);
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, `${JSON.stringify(payload, null, 2)}\n`);
  console.log(`Wrote ${path.relative(process.cwd(), OUT)} (${payload.counts.diagnosticRows} diagnostic rows).`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
