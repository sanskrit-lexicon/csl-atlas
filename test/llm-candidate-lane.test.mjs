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
