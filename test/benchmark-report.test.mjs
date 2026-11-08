import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {
  evaluatePredictions,
  macroScores,
  negativeControlCanary,
  bootstrapCI
} from "../scripts/lib/benchmark-metrics.mjs";

const report = JSON.parse(fs.readFileSync(new URL("../src/data/benchmark-report.json", import.meta.url), "utf8"));
const manifest = JSON.parse(fs.readFileSync(new URL("../src/data/benchmark/split-manifest.json", import.meta.url), "utf8"));

test("macro scores are 1.0 on a perfect classifier", () => {
  const scores = macroScores(["a", "b", "a", "b"], ["a", "b", "a", "b"], ["a", "b"]);
  assert.equal(scores.macroPrecision, 1);
  assert.equal(scores.macroRecall, 1);
  assert.equal(scores.macroF1, 1);
});

test("Cohen kappa and Krippendorff alpha see perfect agreement", () => {
  const metrics = evaluatePredictions(["a", "b", "a", "b"], ["a", "b", "a", "b"], ["a", "b"]);
  assert.equal(metrics.cohenKappa, 1);
  assert.equal(metrics.krippendorffAlpha, 1);
  assert.deepEqual(metrics.bootstrapCI95.macroF1, [1, 1]);
});

test("the negative control fails as expected (inverted oracle)", () => {
  const canary = negativeControlCanary();
  assert.equal(canary.passes, true);
  assert.ok(canary.observed.macroF1 < 0.5, `expected failing macroF1, got ${canary.observed.macroF1}`);
  assert.ok(canary.observed.cohenKappa <= 0 || canary.observed.cohenKappa == null);
});

test("bootstrap CI is seeded and therefore reproducible", () => {
  const rows = ["a", "b"].flatMap(label => [{ prediction: label, gold: label }, { prediction: "a", gold: label }]);
  const statistic = draw => draw.filter(row => row.prediction === row.gold).length / draw.length;
  assert.deepEqual(bootstrapCI(rows, statistic), bootstrapCI(rows, statistic));
});

test("benchmark v2 has three tasks and no self-graded precision", () => {
  assert.equal(report.schemaVersion, "2.0.0");
  assert.equal(report.summary.taskCount, 3);
  assert.equal(report.summary.noSelfGradedPrecision, true);
  assert.equal(Object.prototype.hasOwnProperty.call(report.summary, "overallPrecision"), false);
  assert.deepEqual(report.tasks.map(task => task.taskId), ["encoding-ocr", "gender-conflict", "citation-link-target"]);
  for (const task of report.tasks) {
    assert.equal(Object.prototype.hasOwnProperty.call(task, "precision"), false);
    assert.equal(task.evaluation.status, "not_evaluable");
    assert.equal(task.evaluation.metrics.f1, null);
    assert.equal(task.split.trainRows, 0);
    assert.equal(task.split.heldOutRows, 100);
  }
});

test("gold coverage is honestly below target, with named blocking rows", () => {
  assert.equal(report.summary.totalGold, 0);
  assert.ok(report.summary.goldCoverage < report.summary.goldCoverageTarget);
  assert.equal(report.summary.goldCoverageMet, false);
  assert.equal(report.summary.status, "gold-insufficient-honest-report");
  for (const task of report.tasks) {
    assert.ok(task.gold.blockingRows.length > 0, `${task.taskId} names blocking rows`);
    assert.ok(task.gold.additionalKeysNeeded > 0);
    assert.match(task.gold.recruitmentNeed, /Recruit/);
  }
  assert.equal(report.negativeControl.passes, true);
});

test("the frozen split manifest is a deterministic, disjoint held-out sample", () => {
  assert.equal(manifest.tasks.length, 3);
  for (const split of manifest.tasks) {
    assert.equal(split.heldOutRows, 100);
    assert.equal(split.trainRows, 0);
    assert.equal(new Set(split.rows.map(row => row.reviewId)).size, 100);
    const source = JSON.parse(fs.readFileSync(new URL(`../${split.source}`, import.meta.url), "utf8"));
    const known = new Set((source.items ?? []).map(item => item.reviewId));
    for (const row of split.rows) assert.ok(known.has(row.reviewId), `${row.reviewId} is in ${split.source}`);
    assert.equal(split.strata.reduce((sum, stratum) => sum + stratum.sampled, 0), 100);
  }
});
