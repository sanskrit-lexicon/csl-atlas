// Build the shared review-report overlay for the 10-row R2 checkpoint.
//
// The MACHINE layer (buildPayload) creates no human decisions: it seeds the
// 10 rows with canonical empty review fields, deterministically, ignoring any
// prior decisions. The CLI wrapper (main) then re-applies the human overlay —
// every other review queue in this repo "treats human decisions as an overlay
// preserved across rebuilds by reviewId" (see lib/review-report.mjs), and the
// committed report carries a human review pass; a plain rebuild MUST NOT wipe
// it. So main preserves any reviewed-ok/blocked/deferred rows (and any row
// carrying a reviewer) from the existing file by default. Pass --reseed to
// deliberately blank the human overlay back to the machine-only seed.
//
// Usage: npm run build-r2-checkpoint-review            (preserves human overlay)
//        npm run build-r2-checkpoint-review -- --reseed (blanks human overlay)

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
    if (item.reviewStatus !== "needs-review") errors.push(`${item.reviewId}: reviewStatus must remain needs-review`);
    if (item.reviewedValue !== null) errors.push(`${item.reviewId}: reviewedValue must remain null`);
    if (item.reviewer !== null) errors.push(`${item.reviewId}: reviewer must remain null`);
    if (item.reviewedAt !== null) errors.push(`${item.reviewId}: reviewedAt must remain null`);
    if (item.note !== "") errors.push(`${item.reviewId}: note must remain empty`);
  }
  if (errors.length) {
    const error = new Error(`R2 checkpoint review payload failed with ${errors.length} error(s):\n${errors.map(e => `  - ${e}`).join("\n")}`);
    error.errors = errors;
    throw error;
  }
}

function reviewItemForRow(row) {
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
    ...reviewFields(new Map(), reviewId)
  };
}

export function buildPayload(checkpointPacket, _preserved = new Map(), generatedAt = new Date().toISOString()) {
  validateCheckpointPacket(checkpointPacket);
  const items = checkpointPacket.checkpointRows.map(row => reviewItemForRow(row));
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
      "Human decisions are intentionally absent in this machine-only package.",
      "Future reviewedValue objects should contain acceptedParserLabels and parserDisposition.",
      "Parser promotion remains deferred until human decisions exist."
    ],
    warnings: [
      "This generator creates no human decisions and does not preserve prior R2 checkpoint decisions.",
      "Proposed parser labels are review prompts, not accepted sense decisions.",
      "Archive parity is a comparison/control signal, not the optimization target."
    ]
  });
  payload.generatedAt = generatedAt;
  validateReportPayload(payload);
  return payload;
}

/**
 * Overlay preserved human decisions onto a machine-only payload by reviewId,
 * returning a new payload (the input is not mutated). The five human review
 * fields are taken from `preserved` when an entry exists for the reviewId;
 * machine fields are always left as generated. With an empty map this is a
 * no-op, so a first run or an explicit --reseed yields the machine-only seed.
 */
export function applyPreservedDecisions(payload, preserved) {
  if (!preserved || preserved.size === 0) return payload;
  return {
    ...payload,
    items: payload.items.map(item => {
      const decision = preserved.get(item.reviewId);
      if (!decision) return item;
      return {
        ...item,
        reviewStatus: decision.reviewStatus ?? "needs-review",
        reviewedValue: decision.reviewedValue ?? null,
        reviewer: decision.reviewer ?? null,
        reviewedAt: decision.reviewedAt ?? null,
        note: decision.note ?? ""
      };
    })
  };
}

function main() {
  if (!fs.existsSync(INPUT)) {
    console.error(`Missing ${path.relative(process.cwd(), INPUT)}; run "npm run build-r2-checkpoint-packet" first.`);
    process.exit(1);
  }
  try {
    const reseed = process.argv.includes("--reseed");
    const checkpointPacket = JSON.parse(fs.readFileSync(INPUT, "utf8"));
    const machinePayload = buildPayload(checkpointPacket);
    const preserved = reseed ? new Map() : loadPreserved(OUTPUT);
    const payload = applyPreservedDecisions(machinePayload, preserved);
    writeReport(OUTPUT, payload);
    const note = reseed
      ? "--reseed: human overlay blanked to machine seed"
      : `${preserved.size} human review${preserved.size === 1 ? "" : "s"} preserved`;
    console.log(`Wrote ${payload.items.length} R2 checkpoint review items (${note}) to:`);
    console.log(`- ${path.relative(process.cwd(), OUTPUT)}`);
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();
