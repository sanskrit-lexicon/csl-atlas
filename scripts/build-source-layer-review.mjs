// Build the unknown-source-layer review queue (Phase 1 -> review layer).
//
// Emits review reports conforming to data/schema/review-report.schema.json for
// the MW source abbreviations that do not yet map to a diachronic layer
// (UC-DIA-07). A reviewer classifies each into a layer by adding it to
// src/data/mw-source-layers.json; once mapped it drops out of this queue.
//
// Reviews are an overlay preserved across rebuilds by reviewId (same contract
// as build-gender-conflict-review.mjs). No LLM inference.
//
// Usage: npm run build-source-layer-review

import fs from "node:fs";
import path from "node:path";
import { iterateRecords, MW_SOURCE } from "./lib/mw-parser.mjs";
import { extractCitations, normalizeSource } from "./lib/mw-classifiers.mjs";
import { layerForSource, isEditorialReference } from "./lib/mw-source-layers.mjs";

const SCHEMA_VERSION = "1.0.0";
const OUTPUT = path.resolve(process.cwd(), "src", "data", "review", "unknown-source-layers-review.json");
// Only sources cited at least this many times enter the queue; rarer sigla are
// dominated by parsing artifacts and one-off texts not worth a review row.
const MIN_FREQ = 5;
const HUMAN_STATUSES = new Set(["reviewed-ok", "reviewed-corrected", "blocked", "deferred"]);

function loadPreserved() {
  const preserved = new Map();
  if (!fs.existsSync(OUTPUT)) return preserved;
  try {
    const doc = JSON.parse(fs.readFileSync(OUTPUT, "utf8"));
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
    // ignore malformed prior file
  }
  return preserved;
}

function main() {
  const preserved = loadPreserved();
  const text = fs.readFileSync(MW_SOURCE, "utf8");

  const freq = new Map();
  const example = new Map(); // source -> { line, href }
  for (const rec of iterateRecords(text)) {
    for (const c of extractCitations(rec.body || "")) {
      const src = normalizeSource(c);
      if (!src || isEditorialReference(src)) continue;
      if (layerForSource(src) !== "unknown") continue;
      freq.set(src, (freq.get(src) || 0) + 1);
      if (!example.has(src)) example.set(src, { line: rec.startLine, href: rec.href });
    }
  }

  let preservedCount = 0;
  const items = [...freq.entries()]
    .filter(([, n]) => n >= MIN_FREQ)
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .map(([source, frequency]) => {
      const reviewId = `unknown-source-layer:${source}`;
      const carried = preserved.get(reviewId);
      if (carried) preservedCount += 1;
      const ex = example.get(source);
      return {
        reviewId,
        queue: "unknown-source-layer",
        subject: { kind: "source-abbreviation", source },
        sourcePointers: [{ dictionary: "MW", line: ex.line, href: ex.href }],
        machineValue: { source, frequency, currentLayer: "unknown" },
        evidenceLevel: "derived",
        reviewStatus: carried?.reviewStatus ?? "needs-review",
        reviewedValue: carried?.reviewedValue ?? null,
        reviewer: carried?.reviewer ?? null,
        reviewedAt: carried?.reviewedAt ?? null,
        note: carried?.note ?? ""
      };
    });

  const payload = {
    schemaVersion: SCHEMA_VERSION,
    generatedAt: new Date().toISOString(),
    sourcePath: "../csl-orig/v02/mw/mw.txt",
    recordCount: items.length,
    queue: "unknown-source-layer",
    minFrequency: MIN_FREQ,
    distinctUnknownSources: freq.size,
    assumptions: [
      `Lists MW <ls> source abbreviations that resolve to layer "unknown" (after editorial-reference and base-form fallback) and are cited at least ${MIN_FREQ} times.`,
      "To resolve an item, add the source to src/data/mw-source-layers.json; it then leaves this queue automatically.",
      "Reviews are an overlay keyed by reviewId; human-decided statuses are preserved across rebuilds.",
      "reviewedValue should record the chosen layer, e.g. { \"layer\": \"vedic\" }."
    ],
    warnings: [
      `${freq.size - items.length} rarer unmapped sources (frequency < ${MIN_FREQ}) are omitted; most are parsing fragments or one-off texts.`
    ],
    items
  };

  fs.mkdirSync(path.dirname(OUTPUT), { recursive: true });
  fs.writeFileSync(OUTPUT, `${JSON.stringify(payload, null, 2)}\n`);
  console.log(`Wrote ${items.length} unknown-source-layer review items (${preservedCount} human reviews preserved, ${freq.size} distinct unknown sources) to:`);
  console.log(`- ${path.relative(process.cwd(), OUTPUT)}`);
}

main();
