// H7101 — the LLM candidate lane stays frozen, bounded, and non-promoting.
//
// Run with: npm test  (node --test)

import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { classifyEdit, compositionOf, renderPrompt } from "../scripts/build-llm-candidate-lane.mjs";
import { scoreOutputs } from "../scripts/score-llm-candidate-lane.mjs";
import { bootstrapCI, cohenKappa, metricsFromPairs, pairedBootstrapDelta } from "../scripts/score-llm-candidate-lane.mjs";
import { validateAgainstSchema, validateLane } from "../scripts/validate-llm-candidate-lane.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const lane = path.join(root, "data", "llm-candidate-lane");

function readJsonl(rel) {
  return fs
    .readFileSync(path.join(lane, rel), "utf8")
    .split(/\r?\n/)
    .filter(Boolean)
    .map(line => JSON.parse(line));
}

const sample = readJsonl("sample-500.jsonl");
const rule = readJsonl("outputs/rule-baseline.jsonl");
const llm = readJsonl("outputs/llm-abstain.jsonl");
const prompts = JSON.parse(fs.readFileSync(path.join(lane, "prompts.json"), "utf8"));

test("the eval sample is exactly 500 frozen rows with the declared composition", () => {
  assert.equal(sample.length, 500);
  assert.equal(new Set(sample.map(row => row.id)).size, 500);
  assert.ok(sample.every(row => row.split === "eval"));
  const composition = compositionOf(sample);
  assert.deepEqual(composition.byType, {
    "ocr-error": 122,
    "markup-normalization": 235,
    "source-mismatch": 60,
    "sense-split": 17,
    "no-correction": 66
  });
  assert.deepEqual(composition.bySource, { "correction-loci": 400, "review-queue": 100 });
});

test("weak labels follow the correction diff, not a post-hoc guess", () => {
  assert.equal(classifyEdit("a b", "a b"), "no-correction");
  assert.equal(classifyEdit("a b", "a, b"), "markup-normalization");
  assert.equal(classifyEdit("one two", "one; two"), "sense-split");
  assert.equal(classifyEdit("<ls>Chāṇakya.</ls>", "<ls>Cāṇakya.</ls>"), "source-mismatch");
  assert.equal(classifyEdit("abhava", "abhavat"), "ocr-error");
});

test("prompts never receive the held-out new text or gold hashes", () => {
  const prompt = prompts.variants.find(variant => variant.id === prompts.selectedVariant);
  assert.ok(prompt);
  for (const row of sample.slice(0, 25)) {
    const rendered = renderPrompt(prompt, row);
    assert.ok(rendered.includes(row.input.text));
    assert.ok(!rendered.includes(row.gold.newSha256));
    assert.ok(!rendered.includes(row.gold.oldSha256));
    assert.ok(!rendered.includes('"gold"'));
  }
});

test("no sample row carries a review status or reviewed value", () => {
  for (const row of sample) {
    assert.equal(row.reviewStatus, undefined);
    assert.equal(row.reviewedValue, undefined);
    assert.equal(row.reviewer, undefined);
  }
});

test("the selected prompt is one of six recorded tries and the try budget is not exceeded", () => {
  assert.equal(prompts.variants.length, 6);
  assert.equal(prompts.selectedVariant, "P6");
  assert.ok(prompts.variants.some(variant => variant.id === prompts.selectedVariant));
});

test("rule baseline predicts something; LLM lane abstains without promoting", () => {
  assert.equal(rule.length, 500);
  assert.equal(llm.length, 500);
  assert.ok(rule.some(record => record.prediction.abstain === false));
  assert.ok(llm.every(record => record.prediction.abstain === true));
  for (const record of [...rule, ...llm]) {
    assert.equal(record.provenance.revisionStatus, "machine-candidate");
    assert.equal(record.provenance.reviewedValue, null);
    assert.equal(record.provenance.reviewer, null);
    assert.equal(record.provenance.reviewedAt, null);
  }
});

test("scoring treats abstention as missing coverage, not as a false positive", () => {
  const scores = scoreOutputs(sample, llm);
  assert.equal(scores.coverage, 0);
  assert.equal(scores.abstained, 500);
  assert.equal(scores.accuracyAll, 0);
  assert.equal(scores.macroF1AbstainZero, 0);
});

// --- agreement, uncertainty, and the no-promotion gate (H7101 DeepSeek pass) ---

const schema = JSON.parse(fs.readFileSync(path.join(lane, "provenance.schema.json"), "utf8"));

function pairsOf(rows, records) {
  const byId = new Map(records.map(record => [record.id, record]));
  return rows.map(row => {
    const record = byId.get(row.id);
    const prediction = record?.prediction ?? {};
    const abstain = !record || prediction.abstain !== false || prediction.editType === null;
    return { gold: row.gold.editType, predicted: abstain ? null : prediction.editType };
  });
}

test("the resampling kernel reproduces the authoritative point estimate", () => {
  const points = scoreOutputs(sample, rule);
  const metrics = metricsFromPairs(pairsOf(sample, rule));
  assert.equal(Number(metrics.accuracyAll.toFixed(4)), points.accuracyAll);
  assert.equal(metrics.macroF1AbstainZero, points.macroF1AbstainZero);
  assert.equal(Number(metrics.coverage.toFixed(4)), points.coverage);
  assert.equal(Number(metrics.targetErrorF1.toFixed(4)), points.binaryTargetError.f1);
  assert.equal(Number(metrics.anyCorrectionF1.toFixed(4)), points.binaryAnyCorrection.f1);
});

test("bootstrap CIs are seeded, ordered, and cover the point estimate", () => {
  const pairs = pairsOf(sample, rule);
  const first = bootstrapCI(pairs, { iterations: 300, seed: "H7101-test" });
  const second = bootstrapCI(pairs, { iterations: 300, seed: "H7101-test" });
  assert.deepEqual(first, second);
  const accuracy = first.intervals.accuracyAll;
  assert.ok(accuracy.low <= 0.216 && 0.216 <= accuracy.high);
  assert.ok(accuracy.low < accuracy.high);
  const macro = first.intervals.macroF1AbstainZero;
  assert.ok(macro.low <= 0.1284 && 0.1284 <= macro.high);
});

test("kappa is model-vs-gold and alpha is a named null, not a number", () => {
  const baselineAgreement = scoreOutputs(sample, rule).agreement;
  assert.equal(baselineAgreement.modelVsGoldKappa, -0.1017);
  assert.equal(baselineAgreement.modelVsGoldN, 500);
  assert.equal(cohenKappa(pairsOf(sample, llm)).kappa, null);
  assert.equal(baselineAgreement.alpha, null);
  assert.match(baselineAgreement.alphaReason, /two independent human rater columns/);
});

test("every committed row validates against the provenance schema", () => {
  const report = validateLane();
  assert.deepEqual(report.errors, []);
  assert.equal(report.sampleRows, 500);
  for (const row of [...rule, ...llm]) {
    assert.deepEqual(validateAgainstSchema(schema, row), []);
  }
});

test("a promoted row and a broken provenance row fail the gate", () => {
  const promoted = JSON.parse(JSON.stringify(rule[0]));
  promoted.provenance.revisionStatus = "reviewed";
  assert.ok(validateAgainstSchema(schema, promoted).length > 0);

  const broken = JSON.parse(JSON.stringify(rule[0]));
  delete broken.prompt.sha256;
  assert.ok(validateAgainstSchema(schema, broken).length > 0);

  const leaked = JSON.parse(JSON.stringify(rule[0]));
  leaked.provenance.reviewer = "someone";
  assert.ok(validateAgainstSchema(schema, leaked).length > 0);
});

test("the validator refuses a schema keyword it cannot enforce", () => {
  assert.throws(() => validateAgainstSchema({ oneOf: [{ type: "string" }] }, "x"), /unsupported schema keyword/);
});

test("the paired delta CI is one-sided evidence, not a bare point gain", () => {
  const delta = pairedBootstrapDelta(pairsOf(sample, rule), pairsOf(sample, llm));
  assert.equal(delta.metric, "macroF1AbstainZero");
  assert.equal(delta.delta, -0.1284);
  assert.equal(delta.positive, false);
  assert.ok(delta.high < 0);
  assert.equal(delta.iterations, 2000);
});
