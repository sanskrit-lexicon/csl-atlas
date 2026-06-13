// Build the gender model-crosscheck review queue (review layer).
//
// Takes every cross-dictionary gender conflict already in
// src/data/review/gender-conflicts-review.json and adds an INDEPENDENT third
// vote: the gender predicted by the Dharmamitra ByT5-Sanskrit analyzer
// (snapshot under src/data/external/dharmamitra-morphology.json, produced by
// `npm run import-dharmamitra-morphology`). For each conflicted lemma it emits
// which dictionaries the model agrees with — a tie-breaker for human review.
//
// This step is DETERMINISTIC and runs with no network and no model. If the
// snapshot is missing or a lemma is absent from it, the item is still emitted
// with modelGender=null and verdict="model-pending" — so the queue exists and
// validates before any model run, and simply fills in as the snapshot grows.
//
// CRITICAL: reviews are an overlay. A rebuild MUST NOT discard human decisions;
// human-set statuses are preserved by stable reviewId (see review-report.mjs).
//
// Usage: npm run build-gender-model-crosscheck. No LLM inference at build time.

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { loadPreserved, reviewFields, reviewPayload, writeReport } from "./lib/review-report.mjs";

const CONFLICTS = path.resolve(process.cwd(), "src", "data", "review", "gender-conflicts-review.json");
const SNAPSHOT = path.resolve(process.cwd(), "src", "data", "external", "dharmamitra-morphology.json");
const OUTPUT = path.resolve(process.cwd(), "src", "data", "review", "gender-model-crosscheck-review.json");

const MODEL_POINTER = {
  dictionary: "Dharmamitra ByT5",
  line: null,
  href: "https://github.com/dharmamitra/byt5-sanskrit-analyzers"
};

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

// machineValue.byDict is { LABEL: [genders] }. The model agrees with a label
// when that dictionary's asserted gender set contains the model's gender.
function partition(byDict, modelGender) {
  const agreesWith = [];
  const disagreesWith = [];
  if (!modelGender) return { agreesWith, disagreesWith };
  for (const [label, genders] of Object.entries(byDict)) {
    (genders.includes(modelGender) ? agreesWith : disagreesWith).push(label);
  }
  return { agreesWith, disagreesWith };
}

function verdictFor(modelGender, agreesWith, disagreesWith) {
  if (!modelGender) return "model-pending";             // not in snapshot yet
  if (agreesWith.length === 0) return "model-diverges";  // model backs neither side
  if (disagreesWith.length === 0) return "model-concurs"; // model matches all (rare here)
  return "model-favors";                                 // breaks the tie one way
}

function main() {
  const conflicts = readJson(CONFLICTS);
  const warnings = [];

  let byLemma = {};
  let snapshotMeta = null;
  if (fs.existsSync(SNAPSHOT)) {
    const snap = readJson(SNAPSHOT);
    byLemma = snap.byLemma || {};
    snapshotMeta = { generatedAt: snap.generatedAt, mode: snap.mode, lemmaCount: snap.lemmaCount };
  } else {
    warnings.push(
      "No Dharmamitra morphology snapshot found (src/data/external/dharmamitra-morphology.json); " +
      "all items emitted as model-pending. Run `npm run import-dharmamitra-morphology` to populate."
    );
  }

  const preserved = loadPreserved(OUTPUT);
  const items = [];
  const tally = {};
  let preservedCount = 0;

  for (const conflict of conflicts.items || []) {
    const lemma = conflict.subject?.lemma;
    if (!lemma) continue;
    const byDict = conflict.machineValue?.byDict || {};

    const modelGender = byLemma[lemma]?.gender ?? null;
    const { agreesWith, disagreesWith } = partition(byDict, modelGender);
    const verdict = verdictFor(modelGender, agreesWith, disagreesWith);
    tally[verdict] = (tally[verdict] || 0) + 1;

    const reviewId = `gender-model-crosscheck:${lemma}`;
    if (preserved.has(reviewId)) preservedCount += 1;

    items.push({
      reviewId,
      queue: "pos-gender-model-crosscheck",
      subject: {
        kind: "alignment",
        lemma,
        dictionaries: conflict.subject?.dictionaries || Object.keys(byDict)
      },
      // Reuse the conflict's dictionary source links and append the model.
      sourcePointers: [...(conflict.sourcePointers || []), MODEL_POINTER],
      machineValue: { byDict, modelInput: byLemma[lemma]?.input ?? null, modelGender, agreesWith, disagreesWith, verdict },
      evidenceLevel: "inferred", // probabilistic model output
      ...reviewFields(preserved, reviewId)
    });
  }

  items.sort((a, b) => a.subject.lemma.localeCompare(b.subject.lemma));

  const payload = reviewPayload({
    queue: "pos-gender-model-crosscheck",
    sourcePath: "src/data/review/gender-conflicts-review.json + src/data/external/dharmamitra-morphology.json",
    items,
    extra: { snapshot: snapshotMeta, verdictTally: tally },
    assumptions: [
      "Subjects are exactly the lemmas already in the gender-conflict queue; this queue never invents new conflicts.",
      "The model gender is an independent third vote (Dharmamitra ByT5 morphosyntax), used to triage — never to overwrite a dictionary.",
      "agreesWith/disagreesWith compare the model gender against each dictionary's asserted gender set.",
      "Reviews are an overlay keyed by reviewId; human-decided statuses are preserved across rebuilds."
    ],
    warnings: [
      "verdict=model-pending means the lemma is not in the morphology snapshot yet, not that the model abstained.",
      "ByT5 gender is a posterior estimate; model-favors is a hint for the reviewer, not a resolution.",
      ...warnings
    ]
  });

  writeReport(OUTPUT, payload);
  console.log(`Wrote ${items.length} gender model-crosscheck items (${preservedCount} human reviews preserved) to:`);
  console.log(`- ${path.relative(process.cwd(), OUTPUT)}`);
  console.log(`  verdicts: ${JSON.stringify(tally)}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
