// Build a maker-facing H5 correction proposal from the source-checked QA packet.
//
// This proposes no automatic dictionary edit. It extracts only rows where the
// source-check pass found a source-declared correction candidate.
//
// Usage: npm run build-h5-maker-correction-proposal

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { iterateDict, dictExists } from "./lib/dict-parser.mjs";
import { normalizeLemma } from "./lib/dict-normalize.mjs";

const SCHEMA_VERSION = "1.0.0";
const INPUT = path.resolve(process.cwd(), "data", "lexico", "h5_maker_qa_candidates.json");
const JSON_OUT = path.resolve(process.cwd(), "data", "lexico", "h5_maker_correction_proposal.json");
const MARKDOWN_OUT = path.resolve(process.cwd(), "docs", "H5_MAKER_CORRECTION_PROPOSAL.md");
const GENERATED_BY = "npm run build-h5-maker-correction-proposal";
const EXPECTED_PROPOSAL_REVIEW_IDS = Object.freeze(["h5:mw-pwg-shared-doublet:MW-PWG:divaraTa:devaraTa"]);

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
  return `${String(dict).toLowerCase()}:${norm(form)}`;
}

function buildSourceIndex(rows) {
  const needed = new Map();
  function add(dict, form) {
    const code = String(dict).toLowerCase();
    if (!needed.has(code)) needed.set(code, new Set());
    needed.get(code).add(norm(form));
  }
  for (const row of rows) {
    for (const dict of row.dictionaries ?? []) add(dict, row.acceptedCorrection);
  }

  const index = new Map();
  const warnings = [];
  for (const [code, forms] of needed) {
    if (!dictExists(code)) {
      warnings.push(`Missing source for ${code}; accepted-correction target pointers were preserved from prior output when available.`);
      continue;
    }
    for (const rec of iterateDict(code)) {
      const key = norm(rec.k1 || "");
      if (!forms.has(key)) continue;
      const id = `${code}:${key}`;
      if (!index.has(id)) {
        index.set(id, {
          role: "accepted-correction-form",
          form: rec.k1,
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

function sourcePointer(index, dict, form, fallback = []) {
  const pointer = index.get(pointerKey(dict, form));
  if (pointer) return pointer;
  return fallback.find(item => item.dictionary === String(dict).toUpperCase() && norm(item.form) === norm(form)) ?? null;
}

export function preservedCorrectionTargetMap(packet) {
  const preserved = new Map();
  for (const row of packet.proposalRows ?? []) {
    preserved.set(row.proposalId, row.correctionTargetSourcePointers ?? []);
  }
  return preserved;
}

function loadPreservedTargets(outputPath) {
  if (!fs.existsSync(outputPath)) return new Map();
  try {
    return preservedCorrectionTargetMap(JSON.parse(fs.readFileSync(outputPath, "utf8")));
  } catch {
    return new Map();
  }
}

function validateQaPacket(packet) {
  const errors = [];
  if (packet.status !== "h5-maker-qa-candidate-packet") errors.push("source packet must be h5-maker-qa-candidate-packet");
  if (packet.reviewStatus !== "source-checked") errors.push("source packet must be source-checked");
  if (packet.generatedBy !== "npm run build-h5-maker-qa-candidates") errors.push("source packet must come from npm run build-h5-maker-qa-candidates");
  if (packet.counts?.qaCandidateRows !== 10) errors.push(`expected 10 QA candidate rows, got ${packet.counts?.qaCandidateRows}`);
  if (packet.counts?.sourceCheckedRows !== 10) errors.push(`expected 10 source-checked rows, got ${packet.counts?.sourceCheckedRows}`);
  if (packet.counts?.acceptedCorrectionRows !== 1) errors.push(`expected 1 source-declared correction candidate, got ${packet.counts?.acceptedCorrectionRows}`);
  for (const row of packet.qaCandidateRows ?? []) {
    if (row.sourceCheckStatus === "needs-source-check") errors.push(`${row.reviewId}: source-check must be complete before proposal extraction`);
    if (!row.candidateSourcePointers?.length) errors.push(`${row.reviewId}: missing candidate source pointers`);
    if (!row.contrastSourcePointers?.length) errors.push(`${row.reviewId}: missing nearest-neighbor source pointers`);
    if (row.sourceCheckStatus === "source-declared-correction-candidate" && !row.acceptedCorrection) {
      errors.push(`${row.reviewId}: source-declared correction candidate is missing acceptedCorrection`);
    }
  }
  const proposalIds = (packet.qaCandidateRows ?? [])
    .filter(row => row.sourceCheckStatus === "source-declared-correction-candidate")
    .map(row => row.reviewId);
  if (proposalIds.join("|") !== EXPECTED_PROPOSAL_REVIEW_IDS.join("|")) {
    errors.push(`expected proposal rows ${EXPECTED_PROPOSAL_REVIEW_IDS.join(", ")}; got ${proposalIds.join(", ")}`);
  }
  if (errors.length) {
    const error = new Error(`H5 maker correction source packet failed with ${errors.length} error(s):\n${errors.map(e => `  - ${e}`).join("\n")}`);
    error.errors = errors;
    throw error;
  }
}

function proposalId(row, index) {
  return `h5-maker-correction:${String(index + 1).padStart(2, "0")}:${row.reviewId}`;
}

function proposalRow(row, index, sourceIndex, preservedTargets) {
  const id = proposalId(row, index);
  const preserved = preservedTargets.get(id) ?? [];
  const correctionTargetSourcePointers = (row.dictionaries ?? [])
    .map(dict => sourcePointer(sourceIndex, dict, row.acceptedCorrection, preserved))
    .filter(Boolean);
  return {
    proposalId: id,
    reviewId: row.reviewId,
    qaCandidateId: row.qaCandidateId,
    proposalStatus: "proposal-ready",
    proposalAction: "maker-correction-review",
    lemma: row.lemma,
    proposedCorrection: row.acceptedCorrection,
    rejectedNearestNeighbor: row.nearestReal,
    pair: row.pair,
    dictionaries: row.dictionaries,
    sourceCheckStatus: row.sourceCheckStatus,
    sourceCheckNote: row.sourceCheckNote,
    sourceCheckQuestion: row.sourceCheckQuestion,
    candidateSourcePointers: row.candidateSourcePointers,
    correctionTargetSourcePointers,
    rejectedNearestNeighborSourcePointers: row.contrastSourcePointers,
    makerDecision: {
      submittedBy: null,
      submittedAt: null,
      externalIssueUrl: null,
      makerDisposition: null,
      note: ""
    },
    proposalText: `Review whether ${row.pair} should treat ${row.lemma} as a source-declared wrong-reading/cross-reference candidate for ${row.acceptedCorrection}; ${row.nearestReal} is retained only as the detector's nearest-neighbor control.`
  };
}

function excludedRow(row) {
  return {
    reviewId: row.reviewId,
    qaCandidateId: row.qaCandidateId,
    lemma: row.lemma,
    nearestReal: row.nearestReal,
    pair: row.pair,
    sourceCheckStatus: row.sourceCheckStatus,
    exclusionReason: row.sourceCheckStatus === "source-declared-correction-candidate"
      ? "proposal-row"
      : "source-supported-non-correction"
  };
}

function validatePayload(payload) {
  const errors = [];
  if (payload.counts.qaCandidateRows !== 10) errors.push("expected 10 QA candidate rows");
  if (payload.counts.proposalRows !== 1) errors.push(`expected 1 proposal row, got ${payload.counts.proposalRows}`);
  if (payload.counts.excludedSourceSupportedRows !== 9) errors.push(`expected 9 excluded source-supported rows, got ${payload.counts.excludedSourceSupportedRows}`);
  const ids = payload.proposalRows.map(row => row.reviewId);
  if (ids.join("|") !== EXPECTED_PROPOSAL_REVIEW_IDS.join("|")) errors.push(`proposal row order changed: ${ids.join(", ")}`);
  for (const row of payload.proposalRows) {
    if (row.lemma !== "divaraTa") errors.push(`${row.reviewId}: expected lemma divaraTa`);
    if (row.proposedCorrection !== "diviraTa") errors.push(`${row.reviewId}: expected proposedCorrection diviraTa`);
    if (row.rejectedNearestNeighbor !== "devaraTa") errors.push(`${row.reviewId}: expected rejectedNearestNeighbor devaraTa`);
    if (row.sourceCheckStatus !== "source-declared-correction-candidate") errors.push(`${row.reviewId}: proposal row must be source-declared`);
    if (row.candidateSourcePointers.length < 2) errors.push(`${row.reviewId}: missing candidate source evidence`);
    if (row.correctionTargetSourcePointers.length < 2) errors.push(`${row.reviewId}: missing correction-target source evidence`);
    if (row.rejectedNearestNeighborSourcePointers.length < 2) errors.push(`${row.reviewId}: missing rejected-neighbor source evidence`);
    if (row.makerDecision.submittedBy !== null) errors.push(`${row.reviewId}: submittedBy must remain null`);
    if (row.makerDecision.submittedAt !== null) errors.push(`${row.reviewId}: submittedAt must remain null`);
    if (row.makerDecision.externalIssueUrl !== null) errors.push(`${row.reviewId}: externalIssueUrl must remain null`);
    if (row.makerDecision.makerDisposition !== null) errors.push(`${row.reviewId}: makerDisposition must remain null`);
    if (row.makerDecision.note !== "") errors.push(`${row.reviewId}: maker decision note must remain empty`);
  }
  for (const row of payload.excludedRows) {
    if (row.sourceCheckStatus === "source-declared-correction-candidate") {
      errors.push(`${row.reviewId}: source-declared correction row leaked into excludedRows`);
    }
  }
  if (errors.length) {
    const error = new Error(`H5 maker correction payload failed with ${errors.length} error(s):\n${errors.map(e => `  - ${e}`).join("\n")}`);
    error.errors = errors;
    throw error;
  }
}

export function buildPayload(qaPacket, generatedAt = new Date().toISOString(), preservedTargets = new Map()) {
  validateQaPacket(qaPacket);
  const proposalSourceRows = qaPacket.qaCandidateRows.filter(row => row.sourceCheckStatus === "source-declared-correction-candidate");
  const { index, warnings } = buildSourceIndex(proposalSourceRows);
  const proposalRows = proposalSourceRows.map((row, indexInList) => proposalRow(row, indexInList, index, preservedTargets));
  const unresolvedTargetPointers = proposalRows.some(row => row.correctionTargetSourcePointers.length === 0);
  const excludedRows = qaPacket.qaCandidateRows
    .filter(row => row.sourceCheckStatus !== "source-declared-correction-candidate")
    .map(excludedRow);
  const payload = {
    schemaVersion: SCHEMA_VERSION,
    status: "h5-maker-correction-proposal-packet",
    claim: "The source-checked H5 maker-QA packet yields one maker-facing correction proposal and no automatic dictionary edit.",
    evidenceLabel: "source-check-derived",
    proposalStatus: "proposal-ready",
    ownerRepo: "csl-atlas",
    generatedAt,
    generatedBy: GENERATED_BY,
    sourceFiles: ["data/lexico/h5_maker_qa_candidates.json"],
    sourcePacket: {
      path: "data/lexico/h5_maker_qa_candidates.json",
      generatedAt: qaPacket.generatedAt,
      status: qaPacket.status,
      reviewStatus: qaPacket.reviewStatus,
      counts: qaPacket.counts
    },
    counts: {
      qaCandidateRows: qaPacket.counts.qaCandidateRows,
      proposalRows: proposalRows.length,
      excludedSourceSupportedRows: excludedRows.length,
      byProposalAction: countBy(proposalRows, row => row.proposalAction),
      byPair: countBy(proposalRows, row => row.pair),
      excludedBySourceCheckStatus: countBy(excludedRows, row => row.sourceCheckStatus)
    },
    selectionPolicy: [
      "Read only data/lexico/h5_maker_qa_candidates.json.",
      "Select only rows with sourceCheckStatus = source-declared-correction-candidate.",
      "Require acceptedCorrection, candidate source pointers, correction-target source pointers, and rejected-neighbor control pointers.",
      "Keep source-supported distinct/variant rows out of the maker correction proposal.",
      "Do not edit dictionary source data or record a maker decision."
    ],
    proposalRows,
    excludedRows,
    limitations: [
      "This packet is a maker-facing proposal, not a dictionary edit.",
      "The proposal is based on dictionary source pointers and the H5 source-check pass only.",
      "The nearest-neighbor detector suggested devaraTa, but the source-check pass identifies diviraTa as the source-declared correction target.",
      "The other nine source-checked H5 rows are retained as non-correction evidence.",
      "No parser behavior, source-anchor generation, public page, backend/runtime LLM, corpus, DCS, or standards work is changed."
    ],
    boundaryNote: "Atlas evidence only: this packet drafts a correction proposal for maker review and leaves csl-orig/source edits to a separate human-maintained workflow.",
    warnings: unresolvedTargetPointers ? warnings : []
  };
  validatePayload(payload);
  return payload;
}

function markdownCell(value) {
  return String(value ?? "").replace(/\\/g, "\\\\").replace(/\|/g, "\\|");
}

function pointerMd(pointer) {
  const excerpt = pointer.bodyExcerpt ? ` - ${markdownCell(pointer.bodyExcerpt)}` : "";
  return `[${pointer.dictionary} L${pointer.L}](${pointer.href})${excerpt}`;
}

function sourceTable(row) {
  return [
    "| Evidence role | Source pointers |",
    "|---|---|",
    `| Candidate form \`${row.lemma}\` | ${row.candidateSourcePointers.map(pointerMd).join("<br>")} |`,
    `| Proposed correction \`${row.proposedCorrection}\` | ${row.correctionTargetSourcePointers.map(pointerMd).join("<br>")} |`,
    `| Rejected nearest neighbor \`${row.rejectedNearestNeighbor}\` | ${row.rejectedNearestNeighborSourcePointers.map(pointerMd).join("<br>")} |`,
    ""
  ].join("\n");
}

function excludedTable(payload) {
  return [
    "## Excluded Source-Checked Rows",
    "",
    "These rows stay out of the correction proposal because the source-check pass found source-supported variants or distinct headwords.",
    "",
    "| Review ID | Lemma | Detector neighbor | Source-check status |",
    "|---|---|---|---|",
    ...payload.excludedRows.map(row =>
      `| \`${markdownCell(row.reviewId)}\` | \`${markdownCell(row.lemma)}\` | \`${markdownCell(row.nearestReal)}\` | \`${markdownCell(row.sourceCheckStatus)}\` |`
    ),
    ""
  ].join("\n");
}

export function buildMarkdown(payload) {
  const row = payload.proposalRows[0];
  const lines = [
    "# H5 Maker Correction Proposal",
    "",
    "Date: 2026-06-07",
    "",
    "Status: generated maker-facing correction proposal; no dictionary source data is edited.",
    "",
    "## Trust Block",
    "",
    `- Claim: ${payload.claim}`,
    `- Evidence label: \`${payload.evidenceLabel}\`.`,
    `- Proposal status: \`${payload.proposalStatus}\`.`,
    `- Generated by: \`${payload.generatedBy}\`.`,
    `- Source files: ${payload.sourceFiles.map(file => `\`${file}\``).join(", ")}.`,
    `- Counts: ${payload.counts.proposalRows} proposal row from ${payload.counts.qaCandidateRows} source-checked H5 maker-QA rows; ${payload.counts.excludedSourceSupportedRows} source-supported rows excluded.`,
    `- Boundary note: ${payload.boundaryNote}`,
    "",
    "## Proposal",
    "",
    `- Proposal ID: \`${row.proposalId}\``,
    `- Review ID: \`${row.reviewId}\``,
    `- Proposed correction: \`${row.lemma}\` -> \`${row.proposedCorrection}\``,
    `- Rejected detector neighbor: \`${row.rejectedNearestNeighbor}\``,
    `- Dictionaries: ${row.dictionaries.map(dict => `\`${dict}\``).join(", ")}`,
    `- Source-check note: ${row.sourceCheckNote}`,
    `- Maker decision fields: submittedBy = null; submittedAt = null; externalIssueUrl = null; makerDisposition = null; note = ""`,
    "",
    "## Source Evidence",
    "",
    sourceTable(row),
    "## Suggested Maker Text",
    "",
    row.proposalText,
    "",
    excludedTable(payload),
    "## Limitations",
    "",
    ...payload.limitations.map(item => `- ${item}`),
    ""
  ];
  return `${lines.join("\n")}\n`;
}

function main() {
  if (!fs.existsSync(INPUT)) {
    console.error(`Missing ${path.relative(process.cwd(), INPUT)}; run "npm run build-h5-maker-qa-candidates" first.`);
    process.exit(1);
  }
  try {
    const qaPacket = JSON.parse(fs.readFileSync(INPUT, "utf8"));
    const preservedTargets = loadPreservedTargets(JSON_OUT);
    const payload = buildPayload(qaPacket, undefined, preservedTargets);
    fs.mkdirSync(path.dirname(JSON_OUT), { recursive: true });
    fs.writeFileSync(JSON_OUT, `${JSON.stringify(payload, null, 2)}\n`);
    fs.writeFileSync(MARKDOWN_OUT, buildMarkdown(payload));
    console.log(`Wrote ${payload.counts.proposalRows} H5 maker correction proposal to:`);
    console.log(`- ${path.relative(process.cwd(), JSON_OUT)}`);
    console.log(`- ${path.relative(process.cwd(), MARKDOWN_OUT)}`);
    console.log(`Counts: ${JSON.stringify(payload.counts)}`);
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
