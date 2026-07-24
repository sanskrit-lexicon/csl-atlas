import test from "node:test";
import assert from "node:assert/strict";
import { applyAutoTriage, applyPreservedReviews, preservedReviewsMap } from "../scripts/build-h4-review-packet.mjs";

const skdVocab = ["true-low", "variant-headword", "prose-present", "parser-gap"];
function row(over) {
  return {
    sampleType: "skd-false-low", machineState: "missing", dictionary: { code: "skd" },
    lemma: "Danya", expectedDecisionLabels: skdVocab, reviewStatus: "needs-review", ...over
  };
}

test("applyAutoTriage resolves a missing lemma present under a looser fold", () => {
  const rows = [row({})];
  // SKD holds "DanyaH" (visarga variant); strict key keeps the visarga, the fold drops it.
  applyAutoTriage(rows, () => [{ k1: "DanyaH" }], () => true);
  assert.equal(rows[0].autoTriage.resolved, true);
  assert.equal(rows[0].autoTriage.proposedDecision, "variant-headword");
  assert.equal(rows[0].autoTriage.evidence.matchedHeadword, "DanyaH");
  assert.equal(rows[0].reviewStatus, "auto-resolved");
});

test("applyAutoTriage resolves an ap-ap90 delta as normalization-risk via the comparison edition", () => {
  const rows = [{
    sampleType: "ap-ap90-delta", machineState: "delta", reviewId: "d1",
    dictionary: { code: "ap" }, comparisonDictionary: { code: "ap90" }, lemma: "ananta",
    expectedDecisionLabels: ["edition-delta", "parser-gap", "normalization-risk", "true-delta"],
    reviewStatus: "needs-review"
  }];
  // AP90 holds "anaMta" (anusvāra variant of "ananta"); the delta is a fold artifact.
  applyAutoTriage(rows, () => [{ k1: "anaMta" }], () => true);
  assert.equal(rows[0].autoTriage.resolved, true);
  assert.equal(rows[0].autoTriage.proposedDecision, "normalization-risk");
  assert.equal(rows[0].autoTriage.evidence.matchedHeadword, "anaMta");
  assert.equal(rows[0].autoTriage.evidence.dictionary, "ap90");
});

test("applyAutoTriage leaves a genuinely-missing lemma for human review", () => {
  const rows = [row({ lemma: "qwxzpq" })];
  applyAutoTriage(rows, () => [{ k1: "DanyaH" }], () => true);
  assert.equal(rows[0].autoTriage.resolved, false);
  assert.equal(rows[0].reviewStatus, "needs-review");
});

test("applyAutoTriage never fires where the decision isn't in the vocabulary", () => {
  // a sample type with no variant-headword option (e.g. an index-reverse control)
  const rows = [row({ sampleType: "index-reverse-control", expectedDecisionLabels: ["direction-artifact"] })];
  applyAutoTriage(rows, () => [{ k1: "DanyaH" }], () => true);
  assert.equal(rows[0].autoTriage.resolved, false);
});

test("applyAutoTriage reuses preserved auto-triage and never reads the dictionary", () => {
  // This is what keeps the regeneration test green on the csl-orig-less CI runner.
  const r = row({ reviewId: "h4-x" });
  const preserved = new Map([["h4-x", { resolved: true, proposedDecision: "variant-headword", basis: "preserved", evidence: { matchedHeadword: "DanyaH" } }]]);
  const throwIterate = () => { throw new Error("must not read the dictionary when preserved"); };
  applyAutoTriage([r], throwIterate, () => true, preserved);
  assert.equal(r.autoTriage.proposedDecision, "variant-headword");
  assert.equal(r.reviewStatus, "auto-resolved");
});

test("applyAutoTriage does not resolve when only the strict key already matches", () => {
  // matched headword equals the lemma's strict key -> not a *variant*, leave it
  const rows = [row({ lemma: "DanyaH" })];
  applyAutoTriage(rows, () => [{ k1: "DanyaH" }], () => true);
  assert.equal(rows[0].autoTriage.resolved, false);
});

test("applyPreservedReviews rehydrates agent/human overlays by reviewId", () => {
  const rows = [row({
    reviewId: "h4-x",
    reviewStatus: "needs-review",
    reviewedValue: null,
    reviewer: "",
    reviewedAt: "",
    note: ""
  })];
  const packet = {
    sampleRows: [{
      reviewId: "h4-x",
      reviewStatus: "reviewed-ok",
      reviewedValue: "true-low",
      reviewer: "grok-4.5",
      reviewedAt: "2026-07-24",
      note: "evidence"
    }]
  };
  applyPreservedReviews(rows, preservedReviewsMap(packet));
  assert.equal(rows[0].reviewStatus, "reviewed-ok");
  assert.equal(rows[0].reviewedValue, "true-low");
  assert.equal(rows[0].reviewer, "grok-4.5");
  assert.equal(rows[0].note, "evidence");
});
