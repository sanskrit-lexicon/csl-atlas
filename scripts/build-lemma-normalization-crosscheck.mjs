// Build the lemma-normalization cross-check review queue (review layer).
//
// The atlas aligns the seven dictionaries by an ORTHOGRAPHIC key:
// normalizeSlp1Lemma() strips SLP1 accents and homonym digits. It is not a
// lemmatizer. This queue cross-checks that key against an INDEPENDENT
// linguistic lemma from the Dharmamitra ByT5 `lemma` task: for each core
// headword, does the model's lemma (normalized back to SLP1 through the very
// same module) match the atlas key? Disagreement flags a headword that is keyed
// as a base lemma but the model reads as something else (an inflected/derived
// form, or an orthographic edge case).
//
// First slice: the 1,913 lemmas attested in ALL seven dictionaries — the core
// shared vocabulary, where a mis-key propagates across every alignment.
//
// Two-step pattern (docs/DHARMAMITRA_INTEGRATION.md): this build writes the
// candidate headwords, emits the queue (model-pending until the snapshot
// exists), and joins src/data/external/dharmamitra-lemma.json once present.
//
// Model output is review EVIDENCE only — it never rewrites the normalizer or a
// dictionary headword. No LLM inference at build time.
//
// Usage: npm run build-lemma-normalization-crosscheck

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { normalizeSlp1Lemma, iastToSlp1 } from "../src/lib/lookup-normalize.js";
import { dictHref, DICT_LABELS } from "./lib/dict-manifest.mjs";
import { loadPreserved, reviewFields, reviewPayload, writeReport } from "./lib/review-report.mjs";

const ALL_DICTS = 7; // first slice: lemmas attested in every dictionary

const DOSSIER = path.resolve(process.cwd(), "src", "data", "dicts", "lemma-dossier.json");
const CANDIDATES = path.resolve(process.cwd(), "src", "data", "external", "lemma-normalization-candidates.json");
const SNAPSHOT = path.resolve(process.cwd(), "src", "data", "external", "dharmamitra-lemma.json");
const OUTPUT = path.resolve(process.cwd(), "src", "data", "review", "lemma-normalization-crosscheck-review.json");

const MODEL_POINTER = {
  dictionary: "Dharmamitra ByT5 (lemma)",
  line: null,
  href: "https://github.com/dharmamitra/byt5-sanskrit-analyzers"
};

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

// Normalize a model IAST lemma to an SLP1 key with the module under test, so
// the comparison is apples-to-apples with the atlas key.
function modelToSlp1(iastLemma) {
  if (!iastLemma) return null;
  return normalizeSlp1Lemma(iastToSlp1(iastLemma)).normalized || null;
}

function verdictFor(atlasNorm, modelNorm) {
  if (modelNorm == null) return "model-pending";
  return modelNorm === atlasNorm ? "agree" : "disagree";
}

function main() {
  const dossier = readJson(DOSSIER);
  const warnings = [];

  // 1. Core candidates: lemmas in all seven dictionaries.
  const candidates = dossier.entries
    .filter(e => e.c >= ALL_DICTS)
    .map(e => {
      const mw = e.d.find(t => t[0] === "mw") ?? e.d[0]; // [code, records, firstLine, gender]
      return { lemma: e.l, pointerCode: mw[0], pointerLine: mw[2], dictCount: e.c };
    })
    .sort((a, b) => a.lemma.localeCompare(b.lemma));

  fs.mkdirSync(path.dirname(CANDIDATES), { recursive: true });
  fs.writeFileSync(CANDIDATES, `${JSON.stringify({
    schemaVersion: "1.0.0",
    generatedAt: new Date().toISOString(),
    generatedBy: "npm run build-lemma-normalization-crosscheck",
    note: "Atlas lemma keys (SLP1) for Dharmamitra `lemma`; consumed by import-dharmamitra-lemma.py.",
    minDicts: ALL_DICTS,
    count: candidates.length,
    candidates: candidates.map(c => ({ key: c.lemma, lemmaSlp1: c.lemma }))
  }, null, 2)}\n`);

  // 2. Model snapshot, if present.
  let byLemma = {};
  let snapshotMeta = null;
  if (fs.existsSync(SNAPSHOT)) {
    const snap = readJson(SNAPSHOT);
    byLemma = snap.byLemma || {};
    snapshotMeta = { generatedAt: snap.generatedAt, lemmaCount: snap.lemmaCount };
  } else {
    warnings.push(
      "No Dharmamitra lemma snapshot found (src/data/external/dharmamitra-lemma.json); " +
      "all items model-pending. Run `npm run import-dharmamitra-lemma` over the candidates file."
    );
  }

  // 3. Emit the queue.
  const preserved = loadPreserved(OUTPUT);
  const items = [];
  const tally = {};
  let preservedCount = 0;

  for (const c of candidates) {
    const atlasNorm = normalizeSlp1Lemma(c.lemma).normalized;
    const modelLemmaIast = byLemma[c.lemma]?.modelLemmaIast ?? null;
    const modelNorm = modelToSlp1(modelLemmaIast);
    const verdict = verdictFor(atlasNorm, modelNorm);
    tally[verdict] = (tally[verdict] || 0) + 1;

    const reviewId = `lemma-normalization-crosscheck:${c.lemma}`;
    if (preserved.has(reviewId)) preservedCount += 1;

    items.push({
      reviewId,
      queue: "lemma-normalization-crosscheck",
      subject: { kind: "entry", lemma: c.lemma, dictionaries: Object.values(DICT_LABELS) },
      sourcePointers: [
        { dictionary: DICT_LABELS[c.pointerCode] ?? c.pointerCode, line: c.pointerLine, href: dictHref(c.pointerCode, c.pointerLine) },
        MODEL_POINTER
      ],
      machineValue: {
        lemma: c.lemma,
        atlasNorm,
        modelLemmaIast,
        modelNorm,
        agree: verdict === "agree" ? true : verdict === "disagree" ? false : null,
        dictCount: c.dictCount,
        verdict
      },
      evidenceLevel: "inferred", // model lemma is probabilistic
      ...reviewFields(preserved, reviewId)
    });
  }

  const payload = reviewPayload({
    queue: "lemma-normalization-crosscheck",
    sourcePath: "src/data/dicts/lemma-dossier.json + src/data/external/dharmamitra-lemma.json",
    items,
    extra: { minDicts: ALL_DICTS, candidateCount: candidates.length, snapshot: snapshotMeta, verdictTally: tally },
    assumptions: [
      `Candidates are the ${candidates.length} lemmas attested in all ${ALL_DICTS} comparison dictionaries.`,
      "atlasNorm = normalizeSlp1Lemma(headword); modelNorm = normalizeSlp1Lemma(iastToSlp1(ByT5 lemma)). Both use src/lib/lookup-normalize.js, so the comparison tests that module too.",
      "The model lemma is an independent linguistic opinion used to flag headwords keyed as base lemmas that may not be — it never rewrites the normalizer.",
      "Reviews are an overlay keyed by reviewId; human-decided statuses are preserved across rebuilds."
    ],
    warnings: [
      "verdict=model-pending means the lemma is not in the snapshot yet, not that the model abstained.",
      "Most core headwords are already base lemmas, so high agreement is expected; the disagreements are the signal.",
      ...warnings
    ]
  });

  writeReport(OUTPUT, payload);
  console.log(`Wrote ${items.length} lemma-normalization crosscheck items (${preservedCount} human reviews preserved) to:`);
  console.log(`- ${path.relative(process.cwd(), OUTPUT)}`);
  console.log(`  candidates -> ${path.relative(process.cwd(), CANDIDATES)}`);
  console.log(`  verdicts: ${JSON.stringify(tally)}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main();
