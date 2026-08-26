// Shared helpers for review-layer generators.
//
// Every review queue emits reports conforming to data/schema/review-report.schema.json
// and treats human decisions as an overlay preserved across rebuilds by reviewId.
// This module factors out that contract so each generator only describes its own
// machine fields. See docs/REVIEW_REPORTS.md.

import fs from "node:fs";
import path from "node:path";
import { generatedAtForPayload, generatedAtNow, licenseFields, readJsonIfExists } from "./dataset-meta.mjs";

export const SCHEMA_VERSION = "1.0.0";

// Statuses that mean a human has acted; such items are carried forward verbatim.
export const HUMAN_STATUSES = new Set(["reviewed-ok", "reviewed-corrected", "blocked", "deferred"]);

/**
 * Load human-decided items from an existing report file so a rebuild preserves
 * them. Returns Map<reviewId, {reviewStatus, reviewedValue, reviewer, reviewedAt, note}>.
 */
export function loadPreserved(outputPath) {
  const preserved = new Map();
  if (!fs.existsSync(outputPath)) return preserved;
  try {
    const doc = JSON.parse(fs.readFileSync(outputPath, "utf8"));
    for (const item of doc.items || []) {
      if (HUMAN_STATUSES.has(item.reviewStatus) || item.reviewer) {
        preserved.set(item.reviewId, {
          reviewStatus: item.reviewStatus,
          reviewedValue: item.reviewedValue ?? null,
          reviewer: item.reviewer ?? null,
          reviewedAt: item.reviewedAt ?? null,
          note: item.note ?? ""
        });
      }
    }
  } catch {
    // ignore malformed prior file; machine fields are regenerated anyway
  }
  return preserved;
}

/**
 * The five trailing review fields for an item: a preserved human decision if
 * one exists for reviewId, otherwise the machine default (needs-review).
 */
export function reviewFields(preserved, reviewId) {
  const c = preserved.get(reviewId);
  return {
    reviewStatus: c?.reviewStatus ?? "needs-review",
    reviewedValue: c?.reviewedValue ?? null,
    reviewer: c?.reviewer ?? null,
    reviewedAt: c?.reviewedAt ?? null,
    note: c?.note ?? ""
  };
}

/**
 * Assemble the report envelope in the canonical field order. `extra` is spread
 * after `queue` and before assumptions/warnings/items.
 */
export function reviewPayload({ queue, sourcePath, items, assumptions = [], warnings = [], extra = {} }) {
  return {
    schemaVersion: SCHEMA_VERSION,
    ...licenseFields(),
    generatedAt: generatedAtNow(),
    sourcePath,
    recordCount: items.length,
    queue,
    ...extra,
    assumptions,
    warnings,
    items
  };
}

// ── The reseed lock (H2892) ────────────────────────────────────────────────
//
// Thirteen of the fourteen review generators call loadPreserved and are
// overlay-preserving by construction. The fourteenth,
// scripts/build-r2-checkpoint-review.mjs, takes --reseed, which skips
// loadPreserved and blanks the human overlay back to the machine seed. That is
// the Uprava DANGER_FACTS "never --reseed" row, and until now the row was prose.
//
// The H2890 census measured what is behind it: of 19,368 review rows, 147 carry
// a reviewed-* status and only 10 of those are human-attributed. Ten human
// rulings is a small enough number to lose in one careless rebuild and a large
// enough number that nobody will reconstruct them from memory.

/** The one escape hatch, exact-matched on "1". */
export const OVERLAY_WIPE_HATCH = "ALLOW_OVERLAY_WIPE";

/** Refusal exit code, deliberately distinct from the scripts' own failures (1). */
export const RESEED_REFUSAL_EXIT = 2;

/** Verbatim from the Uprava danger row this lock enforces. */
export const RESEED_DANGER_SENTENCE =
  "--reseed blanks the human review overlay back to the machine seed";

/** True only for the exact string "1" — a half-set hatch is not consent. */
export function reseedIsHatched(env = process.env) {
  return env[OVERLAY_WIPE_HATCH] === "1";
}

export function reseedRefusalMessage({ script, outputPath }) {
  const target = outputPath ? path.relative(process.cwd(), outputPath) : "the review report";
  return [
    `REFUSED: ${script} --reseed is a guarded overlay wipe (H2892).`,
    "",
    RESEED_DANGER_SENTENCE,
    `  ${target}`,
    "",
    "Nothing was written. A plain rebuild is always allowed and preserves every",
    "human decision:",
    "",
    `    node ${script}`,
    "",
    "If the overlay genuinely has to go back to the machine seed, say so",
    "explicitly and re-pin the tripwire in the same commit:",
    "",
    `    ${OVERLAY_WIPE_HATCH}=1 node ${script} --reseed`,
    "    python -m csl_pyutil.integrity_tripwire --extract \\",
    "           --pin data/integrity/csl_atlas_review.pin.json --write-pin \\",
    '           --reason "what changed and why" --updated DD-MM-YYYY',
    ""
  ].join("\n");
}

/**
 * Refuse a --reseed run unless the hatch is set. Returns true when it refused
 * (the caller should stop), false when the run may proceed. `exit` and `log`
 * are injectable so the lock can be tested without ending the test process.
 */
export function refuseReseedWithoutHatch({
  script,
  outputPath,
  env = process.env,
  exit = code => process.exit(code),
  log = message => console.error(message)
} = {}) {
  if (reseedIsHatched(env)) return false;
  log(reseedRefusalMessage({ script, outputPath }));
  exit(RESEED_REFUSAL_EXIT);
  return true;
}

export function writeReport(outputPath, payload) {
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  const previous = readJsonIfExists(outputPath, fs);
  const finalPayload = payload?.generatedAt
    ? { ...payload, generatedAt: generatedAtForPayload(previous, payload) }
    : payload;
  fs.writeFileSync(outputPath, `${JSON.stringify(finalPayload, null, 2)}\n`);
}
