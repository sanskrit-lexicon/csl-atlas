// Build the compound-depth cross-check review queue (review layer).
//
// The atlas measures compound depth from MW MARKUP: compoundSegmentCount splits
// the <k2> field on compound markers (em dash / hyphen / plus) and counts the
// pieces. That is a typographic heuristic, not a linguistic parse. This queue
// cross-checks it against an INDEPENDENT linguistic segmentation from the
// Dharmamitra ByT5 analyzer (`unsandhied` mode): for each deep compound, does
// the model split the surface into the same number of members the markup does?
//
// Two-step pattern (see docs/DHARMAMITRA_INTEGRATION.md):
//   1. This build parses mw.txt, writes the candidate surfaces the model must
//      segment (src/data/external/compound-depth-candidates.json), and emits the
//      review queue — joining the model snapshot if it already exists.
//   2. `import-dharmamitra-segmentation.py` reads those candidates, runs the
//      model, and writes src/data/external/dharmamitra-segmentation.json.
//   Re-running this build then fills in the model column. Until then every item
//   is verdict="model-pending" — the queue is real and valid before any run.
//
// First slice: deep compounds only (atlasSegments >= MIN_SEGMENTS). The 2-/3-
// segment majority (~178k of 182k) is mostly trivially corroborated; markup
// depth is most error-prone, and most worth a second opinion, at depth >= 4.
//
// Model output is probabilistic and is review EVIDENCE only — it never rewrites
// the depth metric or mw.txt. No LLM inference at build time.
//
// Usage: npm run build-compound-depth-crosscheck

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { parseMwFile, MW_HREF_BASE } from "./lib/mw-parser.mjs";
import { compoundSegmentCount } from "./lib/mw-depth-graph.mjs";
import { loadPreserved, reviewFields, reviewPayload, writeReport } from "./lib/review-report.mjs";

const MIN_SEGMENTS = 4; // first slice: deep compounds
const COMPOUND_MARKER = /[—\-+]/g;

const CANDIDATES = path.resolve(process.cwd(), "src", "data", "external", "compound-depth-candidates.json");
const SNAPSHOT = path.resolve(process.cwd(), "src", "data", "external", "dharmamitra-segmentation.json");
const OUTPUT = path.resolve(process.cwd(), "src", "data", "review", "compound-depth-crosscheck-review.json");

const MODEL_POINTER = {
  dictionary: "Dharmamitra ByT5 (unsandhied)",
  line: null,
  href: "https://github.com/dharmamitra/byt5-sanskrit-analyzers"
};

// Marker- and accent-stripped <k2> == the joined surface the model must segment.
function surfaceOf(k2) {
  return (k2 || "").replace(/\//g, "").replace(COMPOUND_MARKER, "").trim();
}

function verdictFor(atlas, model) {
  if (model == null) return "model-pending";
  if (model === atlas) return "agree";
  return model < atlas ? "model-splits-fewer" : "model-splits-more";
}

function main() {
  // 1. Collect deep-compound candidates from MW markup, deduped by surface.
  const byKey = new Map(); // surface -> { surface, atlasSegments, line, recordCount }
  for (const r of parseMwFile()) {
    const atlasSegments = compoundSegmentCount(r);
    if (atlasSegments < MIN_SEGMENTS) continue;
    const surface = surfaceOf(r.k2);
    if (!surface) continue;
    let entry = byKey.get(surface);
    if (!entry) {
      entry = { surface, atlasSegments, line: r.startLine, recordCount: 0 };
      byKey.set(surface, entry);
    }
    entry.recordCount += 1;
    // Keep the deepest markup reading if records disagree (rare).
    if (atlasSegments > entry.atlasSegments) entry.atlasSegments = atlasSegments;
  }
  const candidates = [...byKey.values()].sort((a, b) => a.surface.localeCompare(b.surface));

  // Persist the candidate surfaces for the model importer to consume.
  fs.mkdirSync(path.dirname(CANDIDATES), { recursive: true });
  fs.writeFileSync(CANDIDATES, `${JSON.stringify({
    schemaVersion: "1.0.0",
    generatedAt: new Date().toISOString(),
    generatedBy: "npm run build-compound-depth-crosscheck",
    note: "Surfaces (SLP1) for Dharmamitra `unsandhied` segmentation; consumed by import-dharmamitra-segmentation.py.",
    minSegments: MIN_SEGMENTS,
    count: candidates.length,
    candidates: candidates.map(c => ({ key: c.surface, surfaceSlp1: c.surface, atlasSegments: c.atlasSegments }))
  }, null, 2)}\n`);

  // 2. Load the model snapshot if present.
  let bySurface = {};
  let snapshotMeta = null;
  const warnings = [];
  if (fs.existsSync(SNAPSHOT)) {
    const snap = JSON.parse(fs.readFileSync(SNAPSHOT, "utf8"));
    bySurface = snap.bySurface || {};
    snapshotMeta = { generatedAt: snap.generatedAt, count: snap.count };
  } else {
    warnings.push(
      "No Dharmamitra segmentation snapshot found (src/data/external/dharmamitra-segmentation.json); " +
      "all items model-pending. Run `npm run import-dharmamitra-segmentation` over the candidates file."
    );
  }

  // 3. Emit the review queue.
  const preserved = loadPreserved(OUTPUT);
  const items = [];
  const tally = {};
  let preservedCount = 0;

  for (const c of candidates) {
    const modelSegments = bySurface[c.surface]?.modelSegments ?? null;
    const verdict = verdictFor(c.atlasSegments, modelSegments);
    tally[verdict] = (tally[verdict] || 0) + 1;

    const reviewId = `compound-depth-crosscheck:${c.surface}`;
    if (preserved.has(reviewId)) preservedCount += 1;

    items.push({
      reviewId,
      queue: "compound-depth-crosscheck",
      subject: { kind: "entry", lemma: c.surface, dictionaries: ["MW"] },
      sourcePointers: [
        { dictionary: "MW", line: c.line, href: `${MW_HREF_BASE}#L${c.line}` },
        MODEL_POINTER
      ],
      machineValue: {
        surfaceSlp1: c.surface,
        atlasSegments: c.atlasSegments,
        modelSegments,
        modelSegmentation: bySurface[c.surface]?.segments ?? null,
        delta: modelSegments == null ? null : modelSegments - c.atlasSegments,
        recordCount: c.recordCount,
        verdict
      },
      evidenceLevel: "inferred", // model segmentation is probabilistic
      ...reviewFields(preserved, reviewId)
    });
  }

  const payload = reviewPayload({
    queue: "compound-depth-crosscheck",
    sourcePath: "../csl-orig/v02/mw/mw.txt + src/data/external/dharmamitra-segmentation.json",
    items,
    extra: { minSegments: MIN_SEGMENTS, candidateCount: candidates.length, snapshot: snapshotMeta, verdictTally: tally },
    assumptions: [
      `Candidates are MW compounds whose markup splits <k2> into >= ${MIN_SEGMENTS} segments; the 2-/3-segment majority is excluded from this first slice.`,
      "atlasSegments counts <k2> compound markers (em dash / hyphen / plus); modelSegments is the Dharmamitra `unsandhied` token count over the joined surface.",
      "The model segmentation is an independent linguistic opinion used to flag markup that may over- or under-split — it never rewrites the depth metric.",
      "Reviews are an overlay keyed by reviewId; human-decided statuses are preserved across rebuilds."
    ],
    warnings: [
      "verdict=model-pending means the surface is either not in the snapshot yet OR the model returned degenerate/junk output (filtered). The first ByT5 pass used the remote dharmamitra.org API in a degraded state (~38% failed/filtered); re-run on a healthy API or a local GPU for fuller, reproducible coverage.",
      "model-splits-fewer with model=1 (no split) may be a soft model failure rather than a linguistic judgment; weight it accordingly.",
      "Expect systematic disagreement on bound morphemes (e.g. privative a-, -tva, -tA): the markup often counts them as members; the model may attach them. That is signal, not noise.",
      ...warnings
    ]
  });

  writeReport(OUTPUT, payload);
  console.log(`Wrote ${items.length} compound-depth crosscheck items (${preservedCount} human reviews preserved) to:`);
  console.log(`- ${path.relative(process.cwd(), OUTPUT)}`);
  console.log(`  candidates -> ${path.relative(process.cwd(), CANDIDATES)}`);
  console.log(`  verdicts: ${JSON.stringify(tally)}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
