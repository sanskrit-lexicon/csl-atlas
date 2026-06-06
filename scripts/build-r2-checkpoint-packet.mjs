// Build the reviewer-facing R2 checkpoint packet from the label proposals.
//
// This is intentionally a data/docs review packet. It does not promote parser
// behavior, record human decisions, or update public R2 pages.
//
// Usage: npm run build-r2-checkpoint-packet

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const SCHEMA_VERSION = "1.0.0";
const LABEL_PROPOSALS_PATH = path.resolve(process.cwd(), "data", "lexico", "r2_packet_label_proposals.json");
const JSON_OUT = path.resolve(process.cwd(), "data", "lexico", "r2_checkpoint_review_packet.json");
const MARKDOWN_OUT = path.resolve(process.cwd(), "docs", "R2_CHECKPOINT_REVIEW.md");

export const CHECKPOINT_DIAGNOSTIC_IDS = Object.freeze([
  "r2-drift:gam:pwg",
  "r2-drift:dharma:pwg",
  "r2-drift:gam:ben",
  "r2-drift:rama:ben",
  "r2-drift:gam:ae",
  "r2-drift:dharma:ae",
  "r2-drift:dharma:vcp",
  "r2-drift:dharma:skd",
  "r2-drift:iti:ap",
  "r2-drift:gam:ap"
]);

function countBy(rows, keyFn) {
  const counts = {};
  for (const row of rows) {
    const key = keyFn(row);
    counts[key] = (counts[key] || 0) + 1;
  }
  return Object.fromEntries(Object.entries(counts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
}

function packetTitleFor(labelPayload, packetId) {
  const proposal = Object.values(labelPayload.rowProposals ?? {}).find(row => row.packetId === packetId);
  return proposal?.packetTitle ?? packetId;
}

function packetContextFor(labelPayload, checkpointRows) {
  const contexts = {};
  for (const row of checkpointRows) {
    if (contexts[row.packetId]) continue;
    const packetVocabulary = labelPayload.packetLabelVocabulary?.[row.packetId];
    contexts[row.packetId] = {
      packetId: row.packetId,
      title: packetTitleFor(labelPayload, row.packetId),
      vocabularyDoc: packetVocabulary?.doc ?? null,
      proposedLabelsInCheckpoint: [...new Set(checkpointRows
        .filter(checkpointRow => checkpointRow.packetId === row.packetId)
        .flatMap(checkpointRow => checkpointRow.proposedParserLabels))]
    };
  }
  return contexts;
}

function dedupeSourcePointers(sourcePointers) {
  const seen = new Set();
  const compacted = [];
  for (const pointer of sourcePointers) {
    const key = JSON.stringify(pointer);
    if (seen.has(key)) continue;
    seen.add(key);
    compacted.push(pointer);
  }
  return compacted;
}

function compactCheckpointRow(labelPayload, row) {
  const proposal = labelPayload.rowProposals?.[row.diagnosticId];
  return {
    checkpointId: row.checkpointId,
    diagnosticId: row.diagnosticId,
    packetId: row.packetId,
    packetTitle: proposal?.packetTitle ?? packetTitleFor(labelPayload, row.packetId),
    lemma: row.lemma,
    dict: row.dict,
    driftClass: row.driftClass,
    priority: row.priority,
    archiveComparison: row.archiveComparison,
    proposedParserLabels: row.proposedParserLabels,
    sourcePointers: dedupeSourcePointers(row.sourcePointers ?? []),
    reviewQuestion: row.reviewQuestion,
    nextAction: proposal?.nextAction ?? null,
    reviewedValue: null,
    reviewer: "",
    reviewedAt: "",
    note: ""
  };
}

function vocabularyLabelsFor(labelPayload, packetId) {
  return new Set(Object.keys(labelPayload.packetLabelVocabulary?.[packetId]?.labels ?? {}));
}

function validateLabelPayload(labelPayload) {
  const errors = [];
  const rows = labelPayload.checkpointRows ?? [];
  const actualIds = rows.map(row => row.diagnosticId);
  if (actualIds.join("|") !== CHECKPOINT_DIAGNOSTIC_IDS.join("|")) {
    errors.push(`checkpoint row order must be ${CHECKPOINT_DIAGNOSTIC_IDS.join(", ")}; got ${actualIds.join(", ")}`);
  }
  for (const expectedId of CHECKPOINT_DIAGNOSTIC_IDS) {
    if (!actualIds.includes(expectedId)) errors.push(`${expectedId}: missing checkpoint row`);
  }
  for (const row of rows) {
    if (row.reviewedValue !== null) errors.push(`${row.diagnosticId}: reviewedValue must be null`);
    if (row.reviewer !== "") errors.push(`${row.diagnosticId}: reviewer must be empty`);
    if (row.reviewedAt !== "") errors.push(`${row.diagnosticId}: reviewedAt must be empty`);
    if (row.note !== "") errors.push(`${row.diagnosticId}: note must be empty`);
    if (!row.sourcePointers?.length) errors.push(`${row.diagnosticId}: missing source pointers`);
    if (!row.reviewQuestion) errors.push(`${row.diagnosticId}: missing review question`);
    const allowed = vocabularyLabelsFor(labelPayload, row.packetId);
    if (!allowed.size) errors.push(`${row.diagnosticId}: missing packet vocabulary for ${row.packetId}`);
    for (const label of row.proposedParserLabels ?? []) {
      if (!allowed.has(label)) errors.push(`${row.diagnosticId}: label "${label}" is outside ${row.packetId} vocabulary`);
    }
    if (!row.proposedParserLabels?.length) errors.push(`${row.diagnosticId}: missing proposed parser labels`);
  }
  return errors;
}

function validatePayload(payload, labelPayload) {
  const errors = validateLabelPayload(labelPayload);
  const actualIds = payload.checkpointRows.map(row => row.diagnosticId);
  if (actualIds.join("|") !== CHECKPOINT_DIAGNOSTIC_IDS.join("|")) {
    errors.push(`output checkpoint row order changed: ${actualIds.join(", ")}`);
  }
  if (payload.counts.checkpointRows !== CHECKPOINT_DIAGNOSTIC_IDS.length) {
    errors.push(`checkpointRows count must be ${CHECKPOINT_DIAGNOSTIC_IDS.length}`);
  }
  for (const row of payload.checkpointRows) {
    if (row.reviewedValue !== null) errors.push(`${row.diagnosticId}: output reviewedValue must be null`);
    if (row.reviewer !== "") errors.push(`${row.diagnosticId}: output reviewer must be empty`);
    if (row.reviewedAt !== "") errors.push(`${row.diagnosticId}: output reviewedAt must be empty`);
    if (row.note !== "") errors.push(`${row.diagnosticId}: output note must be empty`);
  }
  if (errors.length) {
    const error = new Error(`R2 checkpoint review packet failed with ${errors.length} error(s):\n${errors.map(e => `  - ${e}`).join("\n")}`);
    error.errors = errors;
    throw error;
  }
}

export function buildPayload(labelPayload) {
  const checkpointRows = (labelPayload.checkpointRows ?? []).map(row => compactCheckpointRow(labelPayload, row));
  const payload = {
    schemaVersion: SCHEMA_VERSION,
    status: "r2-checkpoint-review-packet",
    claim: "The R2 machine-label checkpoint is packaged as a 10-row reviewer worksheet before any parser promotion.",
    evidenceLabel: "derived",
    reviewStatus: "needs-human-review",
    ownerRepo: "csl-atlas",
    generatedBy: "npm run build-r2-checkpoint-packet",
    sourceGeneratedBy: labelPayload.generatedBy,
    sourceFiles: ["data/lexico/r2_packet_label_proposals.json"],
    counts: {
      checkpointRows: checkpointRows.length,
      sourcePointers: checkpointRows.reduce((sum, row) => sum + row.sourcePointers.length, 0),
      byPacket: countBy(checkpointRows, row => row.packetId),
      byPriority: countBy(checkpointRows, row => row.priority),
      byDriftClass: countBy(checkpointRows, row => row.driftClass)
    },
    packetContext: packetContextFor(labelPayload, checkpointRows),
    archiveParityPolicy: "Archive parity is a comparison signal and regression-control cue for review; it is not the optimization target.",
    limitations: [
      "Checkpoint rows are derived from machine label proposals and remain unreviewed.",
      "Human-decision fields intentionally remain empty until a reviewer supplies decisions.",
      "This packet is a worksheet for parser-scope review, not a restored R2 splitter or a broadened sense-alignment claim.",
      "No public R2 page, source-anchor generator, H5 review row, backend, runtime LLM, corpus, DCS, or standards work is changed by this artifact."
    ],
    boundaryNote: "Dictionary source rows, existing R2 source anchors, recovered archive fixtures, and machine label proposals only.",
    checkpointRows
  };
  validatePayload(payload, labelPayload);
  return payload;
}

function mdList(items) {
  return items.map(item => `\`${item}\``).join(", ");
}

function sourcePointerLine(pointer) {
  const label = pointer.kind === "source-record"
    ? `source record ${pointer.blockId}${pointer.rawHeadword ? ` (${pointer.rawHeadword})` : ""}`
    : `example row ${pointer.rowId ?? pointer.senseId}`;
  const parts = [
    label,
    pointer.sourceLine ? `line ${pointer.sourceLine}` : null,
    pointer.rowCount ? `${pointer.rowCount} row(s)` : null,
    pointer.splitConfidence ? `split: ${pointer.splitConfidence}` : null
  ].filter(Boolean);
  return `- ${parts.join("; ")}: ${pointer.href}`;
}

function docsRelativeHref(file) {
  return file?.startsWith("docs/") ? file.slice("docs/".length) : file;
}

function rowSection(row) {
  return [
    `#### \`${row.diagnosticId}\``,
    "",
    `- Packet: \`${row.packetId}\` (${row.packetTitle})`,
    `- Lemma/dictionary: \`${row.lemma}\` / \`${row.dict}\``,
    `- Drift/priority: \`${row.driftClass}\` / \`${row.priority}\``,
    `- Archive comparison: source ${row.archiveComparison.sourceSenseRows}, archive ${row.archiveComparison.archivedSenseRows}, ratio ${row.archiveComparison.sourceToArchiveRatio}`,
    `- Proposed parser labels: ${mdList(row.proposedParserLabels)}`,
    `- Review question: ${row.reviewQuestion}`,
    `- Next action: ${row.nextAction ?? "n/a"}`,
    "- Human fields: `reviewedValue = null`, `reviewer = \"\"`, `reviewedAt = \"\"`, `note = \"\"`",
    "",
    "Source pointers:",
    "",
    ...row.sourcePointers.map(sourcePointerLine)
  ].join("\n");
}

export function buildMarkdown(payload) {
  const lines = [
    "# R2 Checkpoint Review Packet",
    "",
    "Date: 2026-06-06",
    "",
    "Status: generated reviewer worksheet for the 10-row R2 machine-label checkpoint. This is not parser promotion, not a public R2 page update, and not a scholar-reviewed sense decision layer.",
    "",
    "## Trust Block",
    "",
    `- Claim: ${payload.claim}`,
    `- Evidence label: \`${payload.evidenceLabel}\`.`,
    `- Review status: \`${payload.reviewStatus}\`.`,
    `- Generated by: \`${payload.generatedBy}\`.`,
    `- Source files: ${payload.sourceFiles.map(file => `\`${file}\``).join(", ")}.`,
    `- Counts: ${payload.counts.checkpointRows} checkpoint rows, ${payload.counts.sourcePointers} source pointers.`,
    `- Boundary note: ${payload.boundaryNote}`,
    `- Archive parity policy: ${payload.archiveParityPolicy}`,
    "",
    "## Review Rules",
    "",
    "- Record no decisions in this packet until a human reviewer supplies them.",
    "- Keep `reviewedValue`, `reviewer`, `reviewedAt`, and `note` empty for every row.",
    "- Treat proposed parser labels as review prompts, not accepted sense decisions.",
    "- Use archive parity as a comparison/control signal, not as a row-count optimization target.",
    "",
    "## Checkpoint Rows",
    ""
  ];
  for (const [packetId, context] of Object.entries(payload.packetContext)) {
    const rows = payload.checkpointRows.filter(row => row.packetId === packetId);
    lines.push(
      `### ${context.title}`,
      "",
      `Packet: \`${packetId}\``,
      "",
      `Vocabulary doc: ${context.vocabularyDoc ? `[\`${context.vocabularyDoc}\`](${docsRelativeHref(context.vocabularyDoc)})` : "n/a"}`,
      "",
      `Checkpoint labels in this packet: ${mdList(context.proposedLabelsInCheckpoint)}`,
      "",
      ...rows.flatMap(row => [rowSection(row), ""]),
      ""
    );
  }
  lines.push(
    "## Limitations",
    "",
    ...payload.limitations.map(limitation => `- ${limitation}`),
    ""
  );
  return `${lines.join("\n")}\n`;
}

function main() {
  try {
    const labelPayload = JSON.parse(fs.readFileSync(LABEL_PROPOSALS_PATH, "utf8"));
    const payload = buildPayload(labelPayload);
    const markdown = buildMarkdown(payload);
    fs.mkdirSync(path.dirname(JSON_OUT), { recursive: true });
    fs.mkdirSync(path.dirname(MARKDOWN_OUT), { recursive: true });
    fs.writeFileSync(JSON_OUT, `${JSON.stringify(payload, null, 2)}\n`);
    fs.writeFileSync(MARKDOWN_OUT, markdown);
    console.log(`Wrote ${path.relative(process.cwd(), JSON_OUT)} (${payload.counts.checkpointRows} checkpoint rows).`);
    console.log(`Wrote ${path.relative(process.cwd(), MARKDOWN_OUT)}.`);
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();
