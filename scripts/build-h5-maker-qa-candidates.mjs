// Build a compact H5 maker-QA candidate packet from the reviewed anomaly queue.
//
// This is a source-check worksheet. It records no dictionary corrections and
// does not change parser behavior, source anchors, public pages, backend/runtime
// work, corpus/DCS joins, or standards output.
//
// Usage: npm run build-h5-maker-qa-candidates

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { iterateDict, dictExists } from "./lib/dict-parser.mjs";
import { normalizeLemma } from "./lib/dict-normalize.mjs";

const SCHEMA_VERSION = "1.0.0";
const REVIEW_PATH = path.resolve(process.cwd(), "src", "data", "review", "h5-anomaly-review.json");
const JSON_OUT = path.resolve(process.cwd(), "data", "lexico", "h5_maker_qa_candidates.json");
const MARKDOWN_OUT = path.resolve(process.cwd(), "docs", "H5_MAKER_QA_CANDIDATES.md");
const GENERATED_BY = "npm run build-h5-maker-qa-candidates";
const QA_ROW_LIMIT = 10;

const SOURCE_FILES = Object.freeze(["src/data/review/h5-anomaly-review.json"]);
const SOURCE_CHECK_STATUSES = new Set([
  "needs-source-check",
  "source-supported-variant",
  "source-supported-distinct",
  "source-declared-correction-candidate",
  "deferred"
]);

function countBy(rows, keyFn) {
  const counts = {};
  for (const row of rows) {
    const key = keyFn(row);
    counts[key] = (counts[key] || 0) + 1;
  }
  return Object.fromEntries(Object.entries(counts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
}

function norm(value) {
  return normalizeLemma(value ?? "").normalized;
}

function compactText(value, length = 280) {
  const text = String(value ?? "").replace(/\s+/g, " ").trim();
  return text.length > length ? `${text.slice(0, length - 1)}...` : text;
}

function pointerKey(dict, form) {
  return `${dict.toLowerCase()}:${norm(form)}`;
}

function collectNeededForms(rows) {
  const needed = new Map();
  function add(dict, form) {
    const code = String(dict).toLowerCase();
    if (!needed.has(code)) needed.set(code, new Set());
    needed.get(code).add(norm(form));
  }
  for (const row of rows) {
    for (const dict of row.subject.dictionaries ?? []) {
      add(dict, row.subject.lemma);
      add(dict, row.machineValue.nearestReal);
    }
  }
  return needed;
}

function buildSourceIndex(needed) {
  const index = new Map();
  const warnings = [];
  for (const [code, forms] of needed) {
    if (!dictExists(code)) {
      warnings.push(`Missing source for ${code}; H5 maker-QA pointers from that dictionary were skipped.`);
      continue;
    }
    for (const rec of iterateDict(code)) {
      const key = norm(rec.k1 || "");
      if (!forms.has(key)) continue;
      const id = `${code}:${key}`;
      if (!index.has(id)) {
        index.set(id, {
          dictionary: code.toUpperCase(),
          L: rec.L ?? null,
          line: rec.startLine,
          href: rec.href,
          bodyExcerpt: compactText(rec.body)
        });
      }
    }
  }
  return { index, warnings };
}

function pointerFor(index, dict, form, role) {
  const pointer = index.get(pointerKey(dict, form));
  if (!pointer) return null;
  return {
    role,
    form,
    dictionary: pointer.dictionary,
    L: pointer.L,
    line: pointer.line,
    href: pointer.href,
    bodyExcerpt: pointer.bodyExcerpt
  };
}

function rankedQaRows(rows) {
  return rows
    .filter(row => row.reviewedValue === "possible-typo")
    .filter(row => row.machineValue.sampleClass !== "known-correction")
    .sort((a, b) =>
      Number(a.machineValue.nRealNeighbours ?? Infinity) - Number(b.machineValue.nRealNeighbours ?? Infinity) ||
      String(a.machineValue.sampleClass).localeCompare(String(b.machineValue.sampleClass)) ||
      String(a.subject.lemma).localeCompare(String(b.subject.lemma)) ||
      a.reviewId.localeCompare(b.reviewId)
    );
}

function calibrationRows(rows) {
  return rows
    .filter(row => row.reviewedValue === "possible-typo")
    .filter(row => row.machineValue.sampleClass === "known-correction")
    .sort((a, b) => String(a.subject.lemma).localeCompare(String(b.subject.lemma)) || a.reviewId.localeCompare(b.reviewId));
}

function compactReviewFields(row) {
  return {
    reviewStatus: row.reviewStatus,
    reviewedValue: row.reviewedValue,
    reviewer: row.reviewer,
    reviewedAt: row.reviewedAt,
    note: row.note
  };
}

function defaultSourceCheckFields() {
  return {
    sourceCheckStatus: "needs-source-check",
    acceptedCorrection: null,
    checkedBy: "",
    checkedAt: "",
    sourceCheckNote: ""
  };
}

function sourceCheckFields(preserved, qaCandidateId) {
  const fields = preserved?.get(qaCandidateId) ?? defaultSourceCheckFields();
  return {
    sourceCheckStatus: fields.sourceCheckStatus,
    acceptedCorrection: fields.acceptedCorrection,
    checkedBy: fields.checkedBy,
    checkedAt: fields.checkedAt,
    sourceCheckNote: fields.sourceCheckNote
  };
}

export function preservedSourceCheckMap(packet) {
  const preserved = new Map();
  for (const row of packet.qaCandidateRows ?? []) {
    const fields = {
      sourceCheckStatus: row.sourceCheckStatus ?? "needs-source-check",
      acceptedCorrection: row.acceptedCorrection ?? null,
      checkedBy: row.checkedBy ?? "",
      checkedAt: row.checkedAt ?? "",
      sourceCheckNote: row.sourceCheckNote ?? "",
      candidateSourcePointers: row.candidateSourcePointers ?? [],
      contrastSourcePointers: row.contrastSourcePointers ?? []
    };
    const isDefault = fields.sourceCheckStatus === "needs-source-check"
      && fields.acceptedCorrection === null
      && fields.checkedBy === ""
      && fields.checkedAt === ""
      && fields.sourceCheckNote === "";
    if (!isDefault) preserved.set(row.qaCandidateId, fields);
  }
  return preserved;
}

function loadPreservedSourceChecks(outputPath) {
  if (!fs.existsSync(outputPath)) return new Map();
  try {
    return preservedSourceCheckMap(JSON.parse(fs.readFileSync(outputPath, "utf8")));
  } catch {
    return new Map();
  }
}

function sourceCheckQuestion(row) {
  return `Do the ${row.machineValue.pair} source records support \`${row.subject.lemma}\` as a real headword, or should it be treated as a correction candidate against \`${row.machineValue.nearestReal}\`?`;
}

function compactQaRow(row, index, rank, preservedSourceChecks = new Map()) {
  const dictionaries = row.subject.dictionaries ?? [];
  const candidatePointers = dictionaries
    .map(dict => pointerFor(index, dict, row.subject.lemma, "candidate-form"))
    .filter(Boolean);
  const contrastPointers = dictionaries
    .map(dict => pointerFor(index, dict, row.machineValue.nearestReal, "nearest-real-form"))
    .filter(Boolean);
  const qaCandidateId = `h5-maker-qa:${String(rank).padStart(2, "0")}:${row.reviewId}`;
  const preserved = preservedSourceChecks.get(qaCandidateId);
  return {
    qaCandidateId,
    rank,
    reviewId: row.reviewId,
    sampleClass: row.machineValue.sampleClass,
    pair: row.machineValue.pair,
    lemma: row.subject.lemma,
    nearestReal: row.machineValue.nearestReal,
    nRealNeighbours: row.machineValue.nRealNeighbours,
    dictionaries,
    reviewDecision: compactReviewFields(row),
    sourceCheckQuestion: sourceCheckQuestion(row),
    candidateSourcePointers: candidatePointers.length ? candidatePointers : preserved?.candidateSourcePointers ?? [],
    contrastSourcePointers: contrastPointers.length ? contrastPointers : preserved?.contrastSourcePointers ?? [],
    ...sourceCheckFields(preservedSourceChecks, qaCandidateId)
  };
}

function compactCalibrationRow(row) {
  return {
    reviewId: row.reviewId,
    sampleClass: row.machineValue.sampleClass,
    lemma: row.subject.lemma,
    pair: `MW/${String(row.machineValue.petDict).toUpperCase()}`,
    reviewDecision: compactReviewFields(row),
    oldNewEvidence: {
      petOld: row.machineValue.petOld,
      petNew: row.machineValue.petNew,
      mwOld: row.machineValue.mwOld,
      mwNew: row.machineValue.mwNew
    },
    sourcePointers: row.sourcePointers
  };
}

function validateReviewReport(reviewReport) {
  const errors = [];
  if (reviewReport.queue !== "encoding-ocr") errors.push("H5 source report must use queue encoding-ocr");
  if (reviewReport.reviewFamily !== "h5-ghost-anomaly") errors.push("H5 source report must use reviewFamily h5-ghost-anomaly");
  if (reviewReport.recordCount !== 130) errors.push(`expected 130 H5 rows, got ${reviewReport.recordCount}`);
  if ((reviewReport.items ?? []).length !== 130) errors.push(`expected 130 H5 items, got ${(reviewReport.items ?? []).length}`);
  for (const item of reviewReport.items ?? []) {
    if (item.reviewStatus !== "reviewed-ok") errors.push(`${item.reviewId}: expected reviewed-ok before maker QA packet`);
    if (!item.reviewedValue) errors.push(`${item.reviewId}: missing reviewedValue before maker QA packet`);
    if (!item.reviewer) errors.push(`${item.reviewId}: missing reviewer before maker QA packet`);
    if (!item.reviewedAt) errors.push(`${item.reviewId}: missing reviewedAt before maker QA packet`);
    if (!item.note) errors.push(`${item.reviewId}: missing review note before maker QA packet`);
    if (!item.sourcePointers?.length) errors.push(`${item.reviewId}: missing source pointers`);
  }
  const possibleTypoRows = (reviewReport.items ?? []).filter(item => item.reviewedValue === "possible-typo");
  const inferredRows = possibleTypoRows.filter(item => item.machineValue.sampleClass !== "known-correction");
  const calibration = possibleTypoRows.filter(item => item.machineValue.sampleClass === "known-correction");
  if (possibleTypoRows.length !== 22) errors.push(`expected 22 possible-typo rows, got ${possibleTypoRows.length}`);
  if (inferredRows.length !== 16) errors.push(`expected 16 inferred possible-typo rows, got ${inferredRows.length}`);
  if (calibration.length !== 6) errors.push(`expected 6 known-correction calibration rows, got ${calibration.length}`);
  if (errors.length) {
    const error = new Error(`H5 maker QA source report failed with ${errors.length} error(s):\n${errors.map(e => `  - ${e}`).join("\n")}`);
    error.errors = errors;
    throw error;
  }
}

function validatePayload(payload) {
  const errors = [];
  if (payload.counts.qaCandidateRows !== QA_ROW_LIMIT) errors.push(`expected ${QA_ROW_LIMIT} QA candidates`);
  if (payload.counts.possibleTypoRows !== 22) errors.push(`expected 22 possible-typo source rows`);
  if (payload.counts.inferredPossibleTypoRows !== 16) errors.push(`expected 16 inferred possible-typo source rows`);
  if (payload.counts.knownCorrectionCalibrationRows !== 6) errors.push(`expected 6 known-correction calibration rows`);
  for (const row of payload.qaCandidateRows) {
    if (row.reviewDecision.reviewedValue !== "possible-typo") errors.push(`${row.reviewId}: QA row must come from possible-typo`);
    if (row.sampleClass === "known-correction") errors.push(`${row.reviewId}: known corrections must stay calibration rows`);
    if (!row.candidateSourcePointers.length) errors.push(`${row.reviewId}: missing candidate source pointers`);
    if (!row.contrastSourcePointers.length) errors.push(`${row.reviewId}: missing nearest-real contrast source pointers`);
    if (!SOURCE_CHECK_STATUSES.has(row.sourceCheckStatus)) {
      errors.push(`${row.reviewId}: unexpected sourceCheckStatus ${row.sourceCheckStatus}`);
    }
    if (row.sourceCheckStatus === "needs-source-check") {
      if (row.acceptedCorrection !== null) errors.push(`${row.reviewId}: acceptedCorrection must stay null before source check`);
      if (row.checkedBy !== "") errors.push(`${row.reviewId}: checkedBy must stay empty before source check`);
      if (row.checkedAt !== "") errors.push(`${row.reviewId}: checkedAt must stay empty before source check`);
      if (row.sourceCheckNote !== "") errors.push(`${row.reviewId}: sourceCheckNote must stay empty before source check`);
    } else {
      if (!row.checkedBy) errors.push(`${row.reviewId}: checkedBy is required after source check`);
      if (!row.checkedAt) errors.push(`${row.reviewId}: checkedAt is required after source check`);
      if (!row.sourceCheckNote) errors.push(`${row.reviewId}: sourceCheckNote is required after source check`);
      if (row.sourceCheckStatus === "source-declared-correction-candidate") {
        if (!row.acceptedCorrection) errors.push(`${row.reviewId}: source-declared correction candidates require acceptedCorrection`);
      } else if (row.acceptedCorrection !== null) {
        errors.push(`${row.reviewId}: acceptedCorrection must stay null unless the source declares a correction candidate`);
      }
    }
  }
  if (errors.length) {
    const error = new Error(`H5 maker QA payload failed with ${errors.length} error(s):\n${errors.map(e => `  - ${e}`).join("\n")}`);
    error.errors = errors;
    throw error;
  }
}

export function buildPayload(reviewReport, generatedAt = new Date().toISOString(), preservedSourceChecks = new Map()) {
  validateReviewReport(reviewReport);
  const possibleTypoRows = reviewReport.items.filter(item => item.reviewedValue === "possible-typo");
  const inferredRows = rankedQaRows(reviewReport.items);
  const selectedRows = inferredRows.slice(0, QA_ROW_LIMIT);
  const calibration = calibrationRows(reviewReport.items);
  const { index, warnings } = buildSourceIndex(collectNeededForms(selectedRows));
  const qaCandidateRows = selectedRows.map((row, indexInList) =>
    compactQaRow(row, index, indexInList + 1, preservedSourceChecks)
  );
  const pointerWarnings = qaCandidateRows.some(row =>
    row.candidateSourcePointers.length === 0 || row.contrastSourcePointers.length === 0
  ) ? warnings : [];
  const sourceCheckedRows = qaCandidateRows.filter(row => row.sourceCheckStatus !== "needs-source-check").length;
  const payload = {
    schemaVersion: SCHEMA_VERSION,
    status: "h5-maker-qa-candidate-packet",
    claim: "The reviewed H5 anomaly sample yields a small source-checkable maker QA subset without editing dictionary data or accepting ghost-entry claims.",
    evidenceLabel: "review-derived",
    reviewStatus: sourceCheckedRows === qaCandidateRows.length ? "source-checked" : "needs-source-check",
    ownerRepo: "csl-atlas",
    generatedAt,
    generatedBy: GENERATED_BY,
    sourceFiles: SOURCE_FILES,
    sourceReviewReport: {
      path: "src/data/review/h5-anomaly-review.json",
      generatedAt: reviewReport.generatedAt,
      recordCount: reviewReport.recordCount,
      reviewFamily: reviewReport.reviewFamily
    },
    counts: {
      reviewRows: reviewReport.items.length,
      possibleTypoRows: possibleTypoRows.length,
      inferredPossibleTypoRows: inferredRows.length,
      knownCorrectionCalibrationRows: calibration.length,
      qaCandidateRows: qaCandidateRows.length,
      sourceCheckedRows,
      acceptedCorrectionRows: qaCandidateRows.filter(row => row.acceptedCorrection !== null).length,
      bySampleClass: countBy(qaCandidateRows, row => row.sampleClass),
      byPair: countBy(qaCandidateRows, row => row.pair),
      byNRealNeighbours: countBy(qaCandidateRows, row => String(row.nRealNeighbours)),
      bySourceCheckStatus: countBy(qaCandidateRows, row => row.sourceCheckStatus),
      calibrationByPair: countBy(calibration, row => `MW/${String(row.machineValue.petDict).toUpperCase()}`)
    },
    selectionPolicy: [
      "Read only the reviewed H5 anomaly report.",
      "Use rows with reviewedValue = possible-typo as the source pool.",
      "Keep known-correction possible-typo rows as calibration controls, not new maker QA candidates.",
      "Rank inferred shared-doublet rows by fewer nRealNeighbours, then sample class, lemma, and reviewId.",
      `Emit the first ${QA_ROW_LIMIT} rows as a compact source-check worksheet.`
    ],
    calibrationRows: calibration.map(compactCalibrationRow),
    qaCandidateRows,
    limitations: [
      "This packet records source-check dispositions when present, but it does not edit dictionary data.",
      "Rows are candidates for maker QA; they are not proven errors.",
      "No ghost-candidate label is accepted by this packet.",
      "The packet is intentionally small and ranked for a first source-check session, not a complete H5 inventory.",
      "No parser behavior, source-anchor generation, public page, backend/runtime LLM, corpus, DCS, or standards work is changed."
    ],
    boundaryNote: "Dictionary source pointers and the reviewed H5 anomaly report only; source-check dispositions are review metadata, not automatic dictionary edits.",
    warnings: pointerWarnings
  };
  validatePayload(payload);
  return payload;
}

function pointerMd(pointer) {
  const excerpt = pointer.bodyExcerpt ? ` - ${pointer.bodyExcerpt.replace(/\|/g, "\\|")}` : "";
  return `[${pointer.dictionary} L${pointer.L}](${pointer.href})${excerpt}`;
}

function mdList(values) {
  return values.map(value => `\`${value}\``).join(", ");
}

function countTable(title, counts) {
  return [
    `## ${title}`,
    "",
    "| Key | Rows |",
    "|---|---:|",
    ...Object.entries(counts).map(([key, count]) => `| \`${key}\` | ${count} |`),
    ""
  ].join("\n");
}

function candidateSection(row) {
  const acceptedCorrection = row.acceptedCorrection === null ? "null" : `\`${row.acceptedCorrection}\``;
  return [
    `### ${row.rank}. \`${row.lemma}\` -> \`${row.nearestReal}\``,
    "",
    `- Review ID: \`${row.reviewId}\``,
    `- Sample class: \`${row.sampleClass}\`; pair: \`${row.pair}\`; near-neighbor count: ${row.nRealNeighbours}`,
    `- Review decision: \`${row.reviewDecision.reviewedValue}\` (${row.reviewDecision.note})`,
    `- Source-check question: ${row.sourceCheckQuestion}`,
    `- Source-check disposition: \`${row.sourceCheckStatus}\`; accepted correction: ${acceptedCorrection}; checked by: \`${row.checkedBy || ""}\`; checked at: \`${row.checkedAt || ""}\``,
    row.sourceCheckNote ? `- Source-check note: ${row.sourceCheckNote}` : "- Source-check note: _empty_",
    "",
    "| Role | Source pointers |",
    "|---|---|",
    `| Candidate form | ${row.candidateSourcePointers.map(pointerMd).join("<br>")} |`,
    `| Nearest real form | ${row.contrastSourcePointers.map(pointerMd).join("<br>")} |`,
    ""
  ].join("\n");
}

function calibrationTable(payload) {
  return [
    "## Calibration Rows",
    "",
    "Known corrections remain calibration controls. They explain what reviewed `possible-typo` looked like in already observed old/new strings, but they are not new maker QA candidates.",
    "",
    "| Review ID | Lemma | Pair | Source pointers |",
    "|---|---|---|---|",
    ...payload.calibrationRows.map(row => {
      const pointers = row.sourcePointers.map(pointer => `[${pointer.dictionary} L${pointer.L}](${pointer.href})`).join("<br>");
      return `| \`${row.reviewId}\` | \`${row.lemma}\` | \`${row.pair}\` | ${pointers} |`;
    }),
    ""
  ].join("\n");
}

export function buildMarkdown(payload) {
  const lines = [
    "# H5 Maker QA Candidate Packet",
    "",
    "Date: 2026-06-07",
    "",
    `Status: generated source-check worksheet from the reviewed H5 anomaly sample. Current review status: \`${payload.reviewStatus}\`; this does not edit dictionary data.`,
    "",
    "## Trust Block",
    "",
    `- Claim: ${payload.claim}`,
    `- Evidence label: \`${payload.evidenceLabel}\`.`,
    `- Review status: \`${payload.reviewStatus}\`.`,
    `- Generated by: \`${payload.generatedBy}\`.`,
    `- Source files: ${payload.sourceFiles.map(file => `\`${file}\``).join(", ")}.`,
    `- Counts: ${payload.counts.qaCandidateRows} QA candidate rows from ${payload.counts.possibleTypoRows} reviewed possible-typo rows; ${payload.counts.sourceCheckedRows} source-checked rows; ${payload.counts.acceptedCorrectionRows} source-declared correction candidate row.`,
    `- Boundary note: ${payload.boundaryNote}`,
    "",
    "## Selection Policy",
    "",
    ...payload.selectionPolicy.map(item => `- ${item}`),
    "",
    countTable("Counts By Sample Class", payload.counts.bySampleClass),
    countTable("Counts By Pair", payload.counts.byPair),
    countTable("Counts By Near-Neighbor Count", payload.counts.byNRealNeighbours),
    countTable("Counts By Source-Check Status", payload.counts.bySourceCheckStatus),
    calibrationTable(payload),
    "## QA Candidate Rows",
    "",
    ...payload.qaCandidateRows.flatMap(row => [candidateSection(row)]),
    "## Limitations",
    "",
    ...payload.limitations.map(item => `- ${item}`),
    ""
  ];
  return `${lines.join("\n")}\n`;
}

function main() {
  const reviewReport = JSON.parse(fs.readFileSync(REVIEW_PATH, "utf8"));
  const preservedSourceChecks = loadPreservedSourceChecks(JSON_OUT);
  const payload = buildPayload(reviewReport, undefined, preservedSourceChecks);
  fs.mkdirSync(path.dirname(JSON_OUT), { recursive: true });
  fs.writeFileSync(JSON_OUT, `${JSON.stringify(payload, null, 2)}\n`);
  fs.writeFileSync(MARKDOWN_OUT, buildMarkdown(payload));
  console.log(`Wrote ${payload.counts.qaCandidateRows} H5 maker QA candidates to:`);
  console.log(`- ${path.relative(process.cwd(), JSON_OUT)}`);
  console.log(`- ${path.relative(process.cwd(), MARKDOWN_OUT)}`);
  console.log(`Counts: ${JSON.stringify(payload.counts)}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
