// Build a machine-only R2 drift explanation/control packet.
//
// This reads the existing machine label proposals, checkpoint packet, and
// checkpoint review overlay. It records no human decisions and does not promote
// parser behavior.
//
// Usage: npm run build-r2-drift-explanation

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { CHECKPOINT_DIAGNOSTIC_IDS } from "./build-r2-label-proposals.mjs";

const SCHEMA_VERSION = "1.0.0";
const LABEL_PROPOSALS_PATH = path.resolve(process.cwd(), "data", "lexico", "r2_packet_label_proposals.json");
const CHECKPOINT_PACKET_PATH = path.resolve(process.cwd(), "data", "lexico", "r2_checkpoint_review_packet.json");
const CHECKPOINT_REVIEW_PATH = path.resolve(process.cwd(), "src", "data", "review", "r2-checkpoint-review.json");
const JSON_OUT = path.resolve(process.cwd(), "data", "lexico", "r2_drift_explanation.json");
const MARKDOWN_OUT = path.resolve(process.cwd(), "docs", "R2_DRIFT_EXPLANATION.md");

const SOURCE_FILES = Object.freeze([
  "data/lexico/r2_packet_label_proposals.json",
  "data/lexico/r2_checkpoint_review_packet.json",
  "src/data/review/r2-checkpoint-review.json"
]);

const PACKET_EXPLANATION_ROLES = Object.freeze({
  "div-source-scope": "Separates target source records, supplements, homonyms, derived series, and candidate division markers before any row is counted as a target sense series.",
  "marker-run-scope": "Distinguishes archive-prefix marker runs, reset expansions, preface proxies, exact-record controls, lumped parity controls, and no-anchor controls.",
  "ae-reverse-bands": "Explains reverse-dictionary drift by equivalent-position rank, direct-equivalent cues, phrase/collocation matches, and broad-headword overmatch controls.",
  "indigenous-iti-authority": "Keeps definition units, authority quotations or sigla, grammar units, discussion prose, record splits, and indigenous controls visible before sense counting.",
  "source-gap-controls": "Separates mild drift, under-split marker gaps, source-only expansion, parity controls, homonym controls, continuation proxies, and no-anchor controls."
});

function countBy(rows, keyFn) {
  const counts = {};
  for (const row of rows) {
    const key = keyFn(row);
    counts[key] = (counts[key] || 0) + 1;
  }
  return Object.fromEntries(Object.entries(counts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
}

function countLabels(rows) {
  const counts = {};
  for (const row of rows) {
    for (const label of row.proposedParserLabels ?? []) counts[label] = (counts[label] || 0) + 1;
  }
  return Object.fromEntries(Object.entries(counts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
}

function mapBy(rows, keyFn) {
  const mapped = new Map();
  for (const row of rows) mapped.set(keyFn(row), row);
  return mapped;
}

function labelsForPacket(labelPayload, packetId) {
  return new Set(Object.keys(labelPayload.packetLabelVocabulary?.[packetId]?.labels ?? {}));
}

function labelExplanationFor(labelPayload, packetId, label) {
  const info = labelPayload.packetLabelVocabulary?.[packetId]?.labels?.[label];
  return {
    label,
    meaning: info?.meaning ?? null,
    parserConsequence: info?.parserConsequence ?? null
  };
}

function sortedProposalRows(labelPayload) {
  return Object.values(labelPayload.rowProposals ?? {});
}

function hasEmptyCheckpointPacketHumanFields(row) {
  return row.reviewedValue === null && row.reviewer === "" && row.reviewedAt === "" && row.note === "";
}

function hasEmptyReviewReportHumanFields(item) {
  return item.reviewStatus === "needs-review"
    && item.reviewedValue === null
    && item.reviewer === null
    && item.reviewedAt === null
    && item.note === "";
}

function compactCheckpointRow(row, reviewItem) {
  return {
    diagnosticId: row.diagnosticId,
    packetId: row.packetId,
    packetTitle: row.packetTitle,
    lemma: row.lemma,
    dict: row.dict,
    driftClass: row.driftClass,
    priority: row.priority,
    reviewId: reviewItem.reviewId,
    reviewStatus: reviewItem.reviewStatus,
    sourcePointerCount: row.sourcePointers.length,
    proposedParserLabels: row.proposedParserLabels,
    reviewQuestion: row.reviewQuestion,
    reviewedValue: reviewItem.reviewedValue,
    reviewer: reviewItem.reviewer,
    reviewedAt: reviewItem.reviewedAt,
    note: reviewItem.note
  };
}

function explanationRowFor(proposal, labelPayload, checkpointById, reviewById) {
  const checkpointRow = checkpointById.get(proposal.diagnosticId) ?? null;
  const reviewItem = reviewById.get(proposal.diagnosticId) ?? null;
  return {
    diagnosticId: proposal.diagnosticId,
    packetId: proposal.packetId,
    packetTitle: proposal.packetTitle,
    lemma: proposal.lemma,
    dict: proposal.dict,
    parserFamily: proposal.parserFamily,
    split: proposal.split,
    driftClass: proposal.driftClass,
    priority: proposal.priority,
    archiveComparison: proposal.archiveComparison,
    sourcePointerCount: proposal.sourcePointers?.length ?? 0,
    proposedParserLabels: proposal.proposedParserLabels,
    proposedLabelExplanations: proposal.proposedParserLabels.map(label =>
      labelExplanationFor(labelPayload, proposal.packetId, label)
    ),
    explanationRole: PACKET_EXPLANATION_ROLES[proposal.packetId] ?? null,
    checkpoint: checkpointRow ? {
      reviewId: reviewItem?.reviewId ?? proposal.diagnosticId,
      reviewStatus: reviewItem?.reviewStatus ?? null,
      reviewedValue: reviewItem?.reviewedValue ?? null,
      reviewer: reviewItem?.reviewer ?? null,
      reviewedAt: reviewItem?.reviewedAt ?? null,
      note: reviewItem?.note ?? ""
    } : null
  };
}

function packetContextFor(labelPayload, explanationRows, checkpointRows) {
  const contexts = {};
  for (const [packetId, vocabulary] of Object.entries(labelPayload.packetLabelVocabulary ?? {})) {
    const packetRows = explanationRows.filter(row => row.packetId === packetId);
    const checkpointPacketRows = checkpointRows.filter(row => row.packetId === packetId);
    contexts[packetId] = {
      packetId,
      title: packetRows[0]?.packetTitle ?? packetId,
      vocabularyDoc: vocabulary.doc ?? null,
      diagnosticRows: packetRows.length,
      checkpointRows: checkpointPacketRows.length,
      explanationRole: PACKET_EXPLANATION_ROLES[packetId] ?? null,
      byDriftClass: countBy(packetRows, row => row.driftClass),
      byPriority: countBy(packetRows, row => row.priority),
      byProposedLabel: countLabels(packetRows)
    };
  }
  return contexts;
}

function validateInputs(labelPayload, checkpointPacket, checkpointReview) {
  const errors = [];
  const proposals = sortedProposalRows(labelPayload);
  const checkpointRows = checkpointPacket.checkpointRows ?? [];
  const reviewItems = checkpointReview.items ?? [];
  const labelCheckpointRows = labelPayload.checkpointRows ?? [];
  const proposalIds = proposals.map(row => row.diagnosticId);

  if (labelPayload.generatedBy !== "npm run build-r2-label-proposals") {
    errors.push("label proposal source must be generated by npm run build-r2-label-proposals");
  }
  if (checkpointPacket.generatedBy !== "npm run build-r2-checkpoint-packet") {
    errors.push("checkpoint packet source must be generated by npm run build-r2-checkpoint-packet");
  }
  if (checkpointReview.queue !== "r2-checkpoint") {
    errors.push("checkpoint review source must use queue r2-checkpoint");
  }
  if (proposals.length !== 70) errors.push(`expected 70 diagnostic proposal rows, got ${proposals.length}`);
  if (proposalIds.length !== new Set(proposalIds).size) errors.push("diagnostic proposal ids must be unique");

  const labelCheckpointIds = labelCheckpointRows.map(row => row.diagnosticId);
  const checkpointIds = checkpointRows.map(row => row.diagnosticId);
  const reviewIds = reviewItems.map(item => item.reviewId);
  const expected = CHECKPOINT_DIAGNOSTIC_IDS.join("|");
  if (labelCheckpointIds.join("|") !== expected) errors.push(`label proposal checkpoint row order changed: ${labelCheckpointIds.join(", ")}`);
  if (checkpointIds.join("|") !== expected) errors.push(`checkpoint packet row order changed: ${checkpointIds.join(", ")}`);
  if (reviewIds.join("|") !== expected) errors.push(`checkpoint review item order changed: ${reviewIds.join(", ")}`);
  if (checkpointRows.length !== CHECKPOINT_DIAGNOSTIC_IDS.length) errors.push(`expected 10 checkpoint packet rows, got ${checkpointRows.length}`);
  if (reviewItems.length !== CHECKPOINT_DIAGNOSTIC_IDS.length) errors.push(`expected 10 checkpoint review rows, got ${reviewItems.length}`);

  for (const proposal of proposals) {
    const allowed = labelsForPacket(labelPayload, proposal.packetId);
    if (!allowed.size) errors.push(`${proposal.diagnosticId}: missing packet vocabulary for ${proposal.packetId}`);
    if (!proposal.proposedParserLabels?.length) errors.push(`${proposal.diagnosticId}: missing proposed labels`);
    for (const label of proposal.proposedParserLabels ?? []) {
      if (!allowed.has(label)) errors.push(`${proposal.diagnosticId}: label "${label}" is outside ${proposal.packetId} vocabulary`);
    }
  }

  for (const row of labelCheckpointRows) {
    if (!hasEmptyCheckpointPacketHumanFields(row)) errors.push(`${row.diagnosticId}: label checkpoint human fields must stay empty`);
    if (!row.sourcePointers?.length) errors.push(`${row.diagnosticId}: label checkpoint row lacks source pointers`);
    if (!row.reviewQuestion) errors.push(`${row.diagnosticId}: label checkpoint row lacks review question`);
  }

  for (const row of checkpointRows) {
    if (!hasEmptyCheckpointPacketHumanFields(row)) errors.push(`${row.diagnosticId}: checkpoint packet human fields must stay empty`);
    if (!row.sourcePointers?.length) errors.push(`${row.diagnosticId}: checkpoint packet row lacks source pointers`);
    if (!row.reviewQuestion) errors.push(`${row.diagnosticId}: checkpoint packet row lacks review question`);
    const allowed = labelsForPacket(labelPayload, row.packetId);
    for (const label of row.proposedParserLabels ?? []) {
      if (!allowed.has(label)) errors.push(`${row.diagnosticId}: checkpoint label "${label}" is outside ${row.packetId} vocabulary`);
    }
  }

  for (const item of reviewItems) {
    if (!hasEmptyReviewReportHumanFields(item)) {
      errors.push(`${item.reviewId}: checkpoint review item must remain needs-review with empty human fields`);
    }
    if (!item.sourcePointers?.length) errors.push(`${item.reviewId}: checkpoint review item lacks source pointers`);
    if (!item.machineValue?.reviewQuestion) errors.push(`${item.reviewId}: checkpoint review item lacks review question`);
    if (!item.machineValue?.proposedParserLabels?.length) errors.push(`${item.reviewId}: checkpoint review item lacks proposed labels`);
  }

  if (errors.length) {
    const error = new Error(`R2 drift explanation inputs failed with ${errors.length} error(s):\n${errors.map(e => `  - ${e}`).join("\n")}`);
    error.errors = errors;
    throw error;
  }
}

function validatePayload(payload, labelPayload) {
  const errors = [];
  const proposalIds = Object.keys(labelPayload.rowProposals ?? {});
  const explanationIds = payload.explanationRows.map(row => row.diagnosticId);
  if (explanationIds.join("|") !== proposalIds.join("|")) {
    errors.push("explanation rows must cover proposal diagnostic ids in source order");
  }
  if (payload.counts.diagnosticRows !== 70) errors.push(`diagnostic row count must be 70, got ${payload.counts.diagnosticRows}`);
  if (payload.counts.checkpointRows !== 10) errors.push(`checkpoint row count must be 10, got ${payload.counts.checkpointRows}`);
  if (payload.counts.checkpointNeedsReview !== 10) {
    errors.push(`checkpoint needs-review count must be 10, got ${payload.counts.checkpointNeedsReview}`);
  }
  for (const key of ["byPacket", "byDriftClass", "byPriority"]) {
    if (JSON.stringify(payload.counts[key]) !== JSON.stringify(labelPayload.counts?.[key])) {
      errors.push(`counts.${key} does not match label proposal artifact`);
    }
  }
  const checkpointIds = payload.checkpointRows.map(row => row.diagnosticId);
  if (checkpointIds.join("|") !== CHECKPOINT_DIAGNOSTIC_IDS.join("|")) {
    errors.push(`output checkpoint row order changed: ${checkpointIds.join(", ")}`);
  }
  for (const row of payload.checkpointRows) {
    if (row.reviewStatus !== "needs-review") errors.push(`${row.diagnosticId}: checkpoint status must be needs-review`);
    if (row.reviewedValue !== null) errors.push(`${row.diagnosticId}: reviewedValue must stay null`);
    if (row.reviewer !== null) errors.push(`${row.diagnosticId}: reviewer must stay null`);
    if (row.reviewedAt !== null) errors.push(`${row.diagnosticId}: reviewedAt must stay null`);
    if (row.note !== "") errors.push(`${row.diagnosticId}: note must stay empty`);
  }
  for (const row of payload.explanationRows) {
    const allowed = labelsForPacket(labelPayload, row.packetId);
    for (const label of row.proposedParserLabels) {
      if (!allowed.has(label)) errors.push(`${row.diagnosticId}: output label "${label}" is outside ${row.packetId} vocabulary`);
    }
  }
  if (errors.length) {
    const error = new Error(`R2 drift explanation payload failed with ${errors.length} error(s):\n${errors.map(e => `  - ${e}`).join("\n")}`);
    error.errors = errors;
    throw error;
  }
}

export function buildPayload(labelPayload, checkpointPacket, checkpointReview) {
  validateInputs(labelPayload, checkpointPacket, checkpointReview);
  const checkpointById = mapBy(checkpointPacket.checkpointRows, row => row.diagnosticId);
  const reviewById = mapBy(checkpointReview.items, item => item.reviewId);
  const explanationRows = sortedProposalRows(labelPayload).map(proposal =>
    explanationRowFor(proposal, labelPayload, checkpointById, reviewById)
  );
  const checkpointRows = CHECKPOINT_DIAGNOSTIC_IDS.map(id =>
    compactCheckpointRow(checkpointById.get(id), reviewById.get(id))
  );
  const payload = {
    schemaVersion: SCHEMA_VERSION,
    status: "r2-drift-explanation-packet",
    claim: "Existing R2 machine proposal labels explain current source/archive drift classes and identify checkpoint rows blocked on human review without accepting labels or promoting parser behavior.",
    evidenceLabel: "derived",
    reviewStatus: "machine-explained",
    ownerRepo: "csl-atlas",
    generatedBy: "npm run build-r2-drift-explanation",
    sourceGeneratedBy: {
      labelProposals: labelPayload.generatedBy,
      checkpointPacket: checkpointPacket.generatedBy,
      checkpointReview: "npm run build-r2-checkpoint-review"
    },
    sourceFiles: SOURCE_FILES,
    counts: {
      packetCount: new Set(explanationRows.map(row => row.packetId)).size,
      diagnosticRows: explanationRows.length,
      checkpointRows: checkpointRows.length,
      checkpointNeedsReview: checkpointRows.filter(row => row.reviewStatus === "needs-review").length,
      proposedLabelAssignments: explanationRows.reduce((sum, row) => sum + row.proposedParserLabels.length, 0),
      byPacket: countBy(explanationRows, row => row.packetId),
      byDriftClass: countBy(explanationRows, row => row.driftClass),
      byPriority: countBy(explanationRows, row => row.priority),
      byProposedLabel: countLabels(explanationRows)
    },
    packetContext: packetContextFor(labelPayload, explanationRows, checkpointRows),
    checkpointRows,
    explanationRows,
    archiveParityPolicy: "Archive parity is a comparison/control signal for drift review and regression checks, not the optimization target.",
    limitations: [
      "This artifact is machine-only and records no human checkpoint decisions.",
      "Proposed parser labels explain drift classes and review scope; they are not accepted labels or reviewedValue.",
      "All 10 checkpoint rows remain needs-review with empty human fields.",
      "Parser promotion remains deferred until human checkpoint decisions exist.",
      "No R2 splitter behavior, source-anchor generation, H5 review rows, public R2 pages, backend, runtime LLM, corpus, DCS, or standards work is changed."
    ],
    boundaryNote: "Dictionary source rows, existing R2 source anchors, recovered archive fixtures, machine label proposals, and the empty R2 checkpoint review overlay only."
  };
  validatePayload(payload, labelPayload);
  return payload;
}

function docsRelativeHref(file) {
  return file?.startsWith("docs/") ? file.slice("docs/".length) : file;
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

function labelCountTable(payload) {
  return [
    "## Counts By Proposed Label",
    "",
    "| Label | Assignments | Packets |",
    "|---|---:|---|",
    ...Object.entries(payload.counts.byProposedLabel).map(([label, count]) => {
      const packets = [...new Set(payload.explanationRows
        .filter(row => row.proposedParserLabels.includes(label))
        .map(row => row.packetId))]
        .map(packetId => `\`${packetId}\``)
        .join(", ");
      return `| \`${label}\` | ${count} | ${packets} |`;
    }),
    ""
  ].join("\n");
}

function checkpointTable(payload) {
  return [
    "## Checkpoint Rows Still Needs-Review",
    "",
    "| Diagnostic ID | Packet | Drift class | Priority | Proposed labels |",
    "|---|---|---|---|---|",
    ...payload.checkpointRows.map(row => {
      const labels = row.proposedParserLabels.map(label => `\`${label}\``).join(", ");
      return `| \`${row.diagnosticId}\` | \`${row.packetId}\` | \`${row.driftClass}\` | \`${row.priority}\` | ${labels} |`;
    }),
    "",
    "All checkpoint rows keep `reviewedValue = null`, `reviewer = null`, `reviewedAt = null`, and `note = \"\"`.",
    ""
  ].join("\n");
}

function packetContextSections(payload) {
  const lines = ["## Packet Explanation Roles", ""];
  for (const context of Object.values(payload.packetContext)) {
    lines.push(
      `### ${context.title}`,
      "",
      `- Packet: \`${context.packetId}\``,
      `- Vocabulary: ${context.vocabularyDoc ? `[\`${context.vocabularyDoc}\`](${docsRelativeHref(context.vocabularyDoc)})` : "n/a"}`,
      `- Diagnostic rows: ${context.diagnosticRows}`,
      `- Checkpoint rows: ${context.checkpointRows}`,
      `- Role: ${context.explanationRole}`,
      ""
    );
  }
  return lines.join("\n");
}

export function buildMarkdown(payload) {
  const lines = [
    "# R2 Drift Explanation Packet",
    "",
    "Date: 2026-06-06",
    "",
    "Status: generated machine-only drift explanation/control packet. It explains current source/archive drift with machine proposal labels, marks the checkpoint rows still blocked on human review, and keeps parser promotion deferred.",
    "",
    "## Trust Block",
    "",
    `- Claim: ${payload.claim}`,
    `- Evidence label: \`${payload.evidenceLabel}\`.`,
    `- Review status: \`${payload.reviewStatus}\`.`,
    `- Generated by: \`${payload.generatedBy}\`.`,
    `- Source files: ${payload.sourceFiles.map(file => `\`${file}\``).join(", ")}.`,
    `- Counts: ${payload.counts.diagnosticRows} diagnostic rows, ${payload.counts.packetCount} packets, ${payload.counts.checkpointRows} checkpoint rows, ${payload.counts.checkpointNeedsReview} still \`needs-review\`.`,
    `- Boundary note: ${payload.boundaryNote}`,
    `- Archive parity policy: ${payload.archiveParityPolicy}`,
    "",
    "## Interpretation Rules",
    "",
    "- Proposed parser labels explain why rows drift by source scope, marker scope, reverse-rank risk, indigenous prose segmentation, and control/gap status.",
    "- The labels are explanatory metadata only; they are not accepted decisions and they do not populate `reviewedValue`.",
    "- Parser promotion remains deferred until a human reviewer records checkpoint decisions.",
    "- Archive parity stays a comparison/control signal rather than a row-count optimization target.",
    "",
    countTable("Counts By Packet", payload.counts.byPacket),
    countTable("Counts By Drift Class", payload.counts.byDriftClass),
    countTable("Counts By Priority", payload.counts.byPriority),
    labelCountTable(payload),
    checkpointTable(payload),
    packetContextSections(payload),
    "## Limitations",
    "",
    ...payload.limitations.map(limitation => `- ${limitation}`),
    ""
  ];
  return `${lines.join("\n")}\n`;
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function main() {
  for (const input of [LABEL_PROPOSALS_PATH, CHECKPOINT_PACKET_PATH, CHECKPOINT_REVIEW_PATH]) {
    if (!fs.existsSync(input)) {
      console.error(`Missing ${path.relative(process.cwd(), input)}; run the prerequisite R2 build scripts first.`);
      process.exit(1);
    }
  }
  try {
    const payload = buildPayload(
      readJson(LABEL_PROPOSALS_PATH),
      readJson(CHECKPOINT_PACKET_PATH),
      readJson(CHECKPOINT_REVIEW_PATH)
    );
    const markdown = buildMarkdown(payload);
    fs.mkdirSync(path.dirname(JSON_OUT), { recursive: true });
    fs.mkdirSync(path.dirname(MARKDOWN_OUT), { recursive: true });
    fs.writeFileSync(JSON_OUT, `${JSON.stringify(payload, null, 2)}\n`);
    fs.writeFileSync(MARKDOWN_OUT, markdown);
    console.log(`Wrote ${path.relative(process.cwd(), JSON_OUT)} (${payload.counts.diagnosticRows} diagnostics).`);
    console.log(`Wrote ${path.relative(process.cwd(), MARKDOWN_OUT)}.`);
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();
