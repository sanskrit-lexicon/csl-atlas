// Build the shared review-report overlay for the 10-row R2 checkpoint.
//
// This records no human decisions. It seeds src/data/review/ with canonical
// empty review fields so future reviewer edits can be preserved across rebuilds.
//
// Usage: npm run build-r2-checkpoint-review

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { loadPreserved, reviewFields, reviewPayload, writeReport } from "./lib/review-report.mjs";

const INPUT = path.resolve(process.cwd(), "data", "lexico", "r2_checkpoint_review_packet.json");
const OUTPUT = path.resolve(process.cwd(), "src", "data", "review", "r2-checkpoint-review.json");

export const QUEUE = "r2-checkpoint";

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

export const PARSER_DISPOSITIONS = Object.freeze([
  "promote-parser-candidate",
  "retain-side-evidence",
  "control-only",
  "defer",
  "block"
]);

function asUpperDict(dict) {
  return String(dict || "").toUpperCase();
}

function pointerL(pointer) {
  return pointer.blockId ?? pointer.rowId ?? pointer.senseId ?? null;
}

function compactSourcePointer(row, pointer) {
  return {
    dictionary: asUpperDict(row.dict),
    L: pointerL(pointer),
    line: pointer.sourceLine ?? null,
    href: pointer.href ?? null,
    kind: pointer.kind ?? null,
    rawHeadword: pointer.rawHeadword ?? null,
    rowCount: pointer.rowCount ?? null,
    splitConfidence: pointer.splitConfidence ?? null
  };
}

function validateCheckpointPacket(packet) {
  const errors = [];
  if (packet.sourceFiles?.join("|") !== "data/lexico/r2_packet_label_proposals.json") {
    errors.push("checkpoint packet must be derived from data/lexico/r2_packet_label_proposals.json");
  }
  const rows = packet.checkpointRows ?? [];
  const actualIds = rows.map(row => row.diagnosticId);
  if (actualIds.join("|") !== CHECKPOINT_DIAGNOSTIC_IDS.join("|")) {
    errors.push(`checkpoint row order must be ${CHECKPOINT_DIAGNOSTIC_IDS.join(", ")}; got ${actualIds.join(", ")}`);
  }
  for (const expectedId of CHECKPOINT_DIAGNOSTIC_IDS) {
    if (!actualIds.includes(expectedId)) errors.push(`${expectedId}: missing checkpoint row`);
  }
  for (const row of rows) {
    const at = row.diagnosticId ?? "(missing diagnosticId)";
    if (row.reviewedValue !== null) errors.push(`${at}: checkpoint reviewedValue must be null`);
    if (row.reviewer !== "") errors.push(`${at}: checkpoint reviewer must be empty string`);
    if (row.reviewedAt !== "") errors.push(`${at}: checkpoint reviewedAt must be empty string`);
    if (row.note !== "") errors.push(`${at}: checkpoint note must be empty string`);
    if (!row.reviewQuestion) errors.push(`${at}: missing review question`);
    if (!row.proposedParserLabels?.length) errors.push(`${at}: missing proposed parser labels`);
    if (!row.sourcePointers?.length) errors.push(`${at}: missing source pointers`);
    for (const pointer of row.sourcePointers ?? []) {
      if (!pointer.href) errors.push(`${at}: source pointer is missing href`);
    }
    const contextLabels = new Set(packet.packetContext?.[row.packetId]?.proposedLabelsInCheckpoint ?? []);
    if (!contextLabels.size) errors.push(`${at}: missing packet context labels for ${row.packetId}`);
    for (const label of row.proposedParserLabels ?? []) {
      if (!contextLabels.has(label)) errors.push(`${at}: label "${label}" is outside checkpoint packet context`);
    }
  }
  if (errors.length) {
    const error = new Error(`R2 checkpoint review report failed with ${errors.length} error(s):\n${errors.map(e => `  - ${e}`).join("\n")}`);
    error.errors = errors;
    throw error;
  }
}

function validateReportPayload(payload) {
  const errors = [];
  if (payload.queue !== QUEUE) errors.push(`report queue must be ${QUEUE}`);
  if (payload.recordCount !== CHECKPOINT_DIAGNOSTIC_IDS.length) {
    errors.push(`recordCount must be ${CHECKPOINT_DIAGNOSTIC_IDS.length}`);
  }
  const ids = payload.items.map(item => item.reviewId);
  if (ids.join("|") !== CHECKPOINT_DIAGNOSTIC_IDS.join("|")) {
    errors.push(`review item order changed: ${ids.join(", ")}`);
  }
  for (const item of payload.items) {
    if (item.queue !== QUEUE) errors.push(`${item.reviewId}: item queue must be ${QUEUE}`);
    if (item.subject.kind !== "entry") errors.push(`${item.reviewId}: subject.kind must be entry`);
    if (!item.sourcePointers.length) errors.push(`${item.reviewId}: missing source pointers`);
    if (item.sourcePointers.some(pointer => !pointer.href)) errors.push(`${item.reviewId}: source pointer missing href`);
    if (!item.machineValue.proposedParserLabels?.length) errors.push(`${item.reviewId}: missing machine proposed labels`);
    if (!item.machineValue.reviewQuestion) errors.push(`${item.reviewId}: missing machine review question`);
    if (!item.machineValue.allowedParserDispositions?.length) {
      errors.push(`${item.reviewId}: missing parser disposition vocabulary`);
    }
  }
  if (errors.length) {
    const error = new Error(`R2 checkpoint review payload failed with ${errors.length} error(s):\n${errors.map(e => `  - ${e}`).join("\n")}`);
    error.errors = errors;
    throw error;
  }
}

function reviewItemForRow(row, preserved) {
  const reviewId = row.diagnosticId;
  return {
    reviewId,
    queue: QUEUE,
    subject: {
      kind: "entry",
      lemma: row.lemma,
      dictionaries: [asUpperDict(row.dict)]
    },
    sourcePointers: row.sourcePointers.map(pointer => compactSourcePointer(row, pointer)),
    machineValue: {
      diagnosticId: row.diagnosticId,
      checkpointId: row.checkpointId,
      packetId: row.packetId,
      packetTitle: row.packetTitle,
      driftClass: row.driftClass,
      priority: row.priority,
      archiveComparison: row.archiveComparison,
      proposedParserLabels: row.proposedParserLabels,
      reviewQuestion: row.reviewQuestion,
      nextAction: row.nextAction,
      allowedParserDispositions: [...PARSER_DISPOSITIONS],
      reviewedValueShape: {
        acceptedParserLabels: "Array of accepted labels from proposedParserLabels, or an empty array when none are accepted.",
        parserDisposition: "One of allowedParserDispositions."
      }
    },
    evidenceLevel: "derived",
    ...reviewFields(preserved, reviewId)
  };
}

export function buildPayload(checkpointPacket, preserved = new Map(), generatedAt = new Date().toISOString()) {
  validateCheckpointPacket(checkpointPacket);
  const items = checkpointPacket.checkpointRows.map(row => reviewItemForRow(row, preserved));
  const payload = reviewPayload({
    queue: QUEUE,
    sourcePath: "data/lexico/r2_checkpoint_review_packet.json",
    items,
    extra: {
      reviewFamily: "r2-checkpoint",
      sourceGeneratedBy: checkpointPacket.generatedBy,
      checkpointCounts: checkpointPacket.counts,
      packetContext: checkpointPacket.packetContext,
      archiveParityPolicy: checkpointPacket.archiveParityPolicy,
      boundaryNote: checkpointPacket.boundaryNote,
      decisionValueSchema: {
        acceptedParserLabels: "array<string>",
        parserDisposition: PARSER_DISPOSITIONS
      }
    },
    assumptions: [
      "This report is seeded from the generated 10-row R2 checkpoint packet.",
      "Each reviewId is the stable diagnosticId from the checkpoint packet.",
      "Human decisions are an overlay: reviewStatus, reviewedValue, reviewer, reviewedAt, and note are preserved across rebuilds.",
      "Future reviewedValue objects should contain acceptedParserLabels and parserDisposition.",
      "Parser promotion remains deferred until human decisions exist."
    ],
    warnings: [
      "This report intentionally records no human decisions.",
      "Proposed parser labels are review prompts, not accepted sense decisions.",
      "Archive parity is a comparison/control signal, not the optimization target."
    ]
  });
  payload.generatedAt = generatedAt;
  validateReportPayload(payload);
  return payload;
}

function main() {
  if (!fs.existsSync(INPUT)) {
    console.error(`Missing ${path.relative(process.cwd(), INPUT)}; run "npm run build-r2-checkpoint-packet" first.`);
    process.exit(1);
  }
  try {
    const checkpointPacket = JSON.parse(fs.readFileSync(INPUT, "utf8"));
    const preserved = loadPreserved(OUTPUT);
    const payload = buildPayload(checkpointPacket, preserved);
    const preservedCount = payload.items.filter(item => preserved.has(item.reviewId)).length;
    writeReport(OUTPUT, payload);
    console.log(`Wrote ${payload.items.length} R2 checkpoint review items (${preservedCount} human reviews preserved) to:`);
    console.log(`- ${path.relative(process.cwd(), OUTPUT)}`);
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();
