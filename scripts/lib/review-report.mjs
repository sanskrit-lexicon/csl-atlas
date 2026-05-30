// Shared helpers for review-layer generators.
//
// Every review queue emits reports conforming to data/schema/review-report.schema.json
// and treats human decisions as an overlay preserved across rebuilds by reviewId.
// This module factors out that contract so each generator only describes its own
// machine fields. See docs/REVIEW_REPORTS.md.

import fs from "node:fs";
import path from "node:path";

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
    generatedAt: new Date().toISOString(),
    sourcePath,
    recordCount: items.length,
    queue,
    ...extra,
    assumptions,
    warnings,
    items
  };
}

export function writeReport(outputPath, payload) {
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, `${JSON.stringify(payload, null, 2)}\n`);
}
