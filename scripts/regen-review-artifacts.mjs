/**
 * Regenerate the committed review evidence in dependency order.
 *
 * This is deliberately an orchestrator, not a second implementation of the
 * individual generators.  In particular, it never calls the R2 `--reseed`
 * escape hatch: human decisions are an overlay, not machine-owned data.
 */
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

import {
  buildMarkdown as buildR2DriftMarkdown,
  buildPayload as buildR2DriftPayload
} from "./build-r2-drift-explanation.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const HUMAN_FIELDS = new Set([
  "reviewStatus", "reviewedValue", "reviewer", "reviewedAt", "note",
  "sourceCheckStatus", "sourceCheckNote", "sourceCheckedBy", "sourceCheckedAt",
  "correctionTarget", "submittedBy", "submittedAt", "externalIssueUrl",
  "makerDisposition", "makerNote"
]);
const HUMAN_REVIEW_FILES = [
  "src/data/review/r2-checkpoint-review.json",
  "src/data/review/h5-anomaly-review.json",
  "data/lexico/h5_maker_qa_candidates.json",
  "data/lexico/h5_maker_correction_proposal.json",
  "data/lexico/h4_semantic_field_review_packet.json",
  "data/lexico/xref_source_check_packet.json"
];
const STEPS = [
  // R2
  "build-r2-label-proposals.mjs",
  "build-r2-checkpoint-packet.mjs",
  "build-r2-checkpoint-review.mjs",
  "build-r2-drift-explanation.mjs",
  // H5
  "build-h5-anomaly-review.mjs",
  "build-h5-maker-qa-candidates.mjs",
  "build-h5-maker-correction-proposal.mjs",
  // H4
  "build-semantic-fields.mjs",
  "build-h4-family-profiles.mjs",
  "build-h4-review-packet.mjs",
  // Cross references
  "build-xref-lineage.mjs",
  "build-xref-hub-review.mjs",
  "build-xref-source-check-packet.mjs",
  "build-review-worksheets.mjs"
];

function stable(value) {
  return JSON.stringify(value);
}

function collectHumanFields(value, trail = "", found = {}) {
  if (Array.isArray(value)) {
    value.forEach((item, index) => collectHumanFields(item, `${trail}[${index}]`, found));
  } else if (value && typeof value === "object") {
    for (const [key, item] of Object.entries(value)) {
      const next = trail ? `${trail}.${key}` : key;
      if (HUMAN_FIELDS.has(key)) found[next] = item;
      collectHumanFields(item, next, found);
    }
  }
  return found;
}

function snapshotHumanFields() {
  return Object.fromEntries(HUMAN_REVIEW_FILES.filter(file => fs.existsSync(path.join(ROOT, file))).map(file => {
    const payload = JSON.parse(fs.readFileSync(path.join(ROOT, file), "utf8"));
    return [file, collectHumanFields(payload)];
  }));
}

function run(script) {
  const result = spawnSync(process.execPath, [path.join(ROOT, "scripts", script)], {
    cwd: ROOT,
    encoding: "utf8",
    stdio: "inherit"
  });
  if (result.status !== 0) throw new Error(`${script} failed with exit code ${result.status}`);
}

function writeMachineOnlyFixture() {
  const read = relative => JSON.parse(fs.readFileSync(path.join(ROOT, relative), "utf8"));
  const review = read("src/data/review/r2-checkpoint-review.json");
  const machineOnly = {
    ...review,
    items: review.items.map(item => ({
      ...item,
      reviewStatus: "needs-review",
      reviewedValue: null,
      reviewer: null,
      reviewedAt: null,
      note: ""
    }))
  };
  const payload = buildR2DriftPayload(
    read("data/lexico/r2_packet_label_proposals.json"),
    read("data/lexico/r2_checkpoint_review_packet.json"),
    machineOnly
  );
  fs.writeFileSync(
    path.join(ROOT, "test/fixtures/R2_DRIFT_EXPLANATION.machine-only.md"),
    buildR2DriftMarkdown(payload)
  );
}

export function regenerateReviewArtifacts() {
  const before = snapshotHumanFields();
  for (const step of STEPS) run(step);
  writeMachineOnlyFixture();
  const after = snapshotHumanFields();
  if (stable(before) !== stable(after)) {
    throw new Error("Refusing to continue: regeneration changed preserved human review fields.");
  }
  console.log("Review artifacts regenerated; preserved human review fields are byte-equivalent.");
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    regenerateReviewArtifacts();
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}
