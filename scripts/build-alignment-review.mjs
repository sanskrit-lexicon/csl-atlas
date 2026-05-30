// Build the low-confidence alignment review queue (Phase 2 -> review layer).
//
// Reads the alignment-confidence output of the comparative dictionary build and
// emits a review report (queue "low-confidence-alignment", UC-RV-01 / UC-CD-09)
// for every lemma that aligned across dictionaries only after normalization.
//
// In practice this queue is intrinsically tiny: CDSL headwords are SLP1 and
// align byte-identically, so almost all multi-dictionary lemmas are high
// confidence. That is itself a result, surfaced on the alignment page.
//
// Depends on `npm run build-dict-comparison` having run. No LLM inference.
// Usage: npm run build-alignment-review

import fs from "node:fs";
import path from "node:path";
import { loadPreserved, reviewFields, reviewPayload, writeReport } from "./lib/review-report.mjs";

const INPUT = path.resolve(process.cwd(), "src", "data", "dicts", "alignment-confidence.json");
const OUTPUT = path.resolve(process.cwd(), "src", "data", "review", "low-confidence-alignment-review.json");

function main() {
  if (!fs.existsSync(INPUT)) {
    console.error(`Missing ${path.relative(process.cwd(), INPUT)}; run "npm run build-dict-comparison" first.`);
    process.exit(1);
  }
  const conf = JSON.parse(fs.readFileSync(INPUT, "utf8"));
  const preserved = loadPreserved(OUTPUT);
  const low = conf.lowConfidence || [];

  let preservedCount = 0;
  const items = low
    .map(entry => {
      const reviewId = `low-confidence-alignment:${entry.lemma}`;
      if (preserved.has(reviewId)) preservedCount += 1;
      return {
        reviewId,
        queue: "low-confidence-alignment",
        subject: { kind: "alignment", lemma: entry.lemma, dictionaries: entry.dicts.map(d => d.dict) },
        sourcePointers: entry.dicts.map(d => ({ dictionary: d.dict, href: d.href })),
        machineValue: { confidence: "medium", variants: entry.variants },
        evidenceLevel: "inferred",
        ...reviewFields(preserved, reviewId)
      };
    })
    .sort((a, b) => a.subject.lemma.localeCompare(b.subject.lemma));

  const payload = reviewPayload({
    queue: "low-confidence-alignment",
    sourcePath: "src/data/dicts/alignment-confidence.json",
    items,
    extra: { confidenceDistribution: conf.distribution },
    assumptions: [
      "An item is a multi-dictionary lemma whose raw <k1> headwords differ but match after normalization (accent/digit stripping).",
      "Confidence 'high' (identical raw headwords) is not queued; only 'medium' is.",
      "evidenceLevel is inferred: the alignment is a heuristic match across non-identical surface forms.",
      "Reviews are an overlay keyed by reviewId; human-decided statuses are preserved across rebuilds."
    ],
    warnings: [
      "This queue is intrinsically small because SLP1 headwords align byte-identically; see the high vs medium distribution."
    ]
  });

  writeReport(OUTPUT, payload);
  console.log(`Wrote ${items.length} low-confidence-alignment review items (${preservedCount} human reviews preserved) to:`);
  console.log(`- ${path.relative(process.cwd(), OUTPUT)}`);
}

main();
