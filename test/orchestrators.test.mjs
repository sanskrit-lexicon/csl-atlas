// Unit tests for decision-bearing helpers in the build orchestrators.
//
// The orchestrators read large source files in main(); they are guarded to run
// only when executed directly, so importing them here is side-effect-free and
// we can test their pure helpers with synthetic inputs.

import { test } from "node:test";
import assert from "node:assert/strict";

import { compareCounts } from "../scripts/build-mw-quantitative-depth.mjs";
import { classifyGram } from "../scripts/build-dcs-corpus.mjs";
import { senseUnits } from "../scripts/build-sense-depth.mjs";
import { classify, fitBand, median, percent } from "../scripts/build-dictionary-coverage.mjs";
import { topForm } from "../scripts/build-citation-apparatus.mjs";

// ---- MW depth: count-divergence validation ----
test("compareCounts: no warnings when counts match", () => {
  const expected = { total: 100, types: new Map([["root", 10], ["compound", 50]]) };
  const r = compareCounts({ root: 10, compound: 50 }, expected, 100);
  assert.equal(r.warnings.length, 0);
  assert.ok(r.typeDiffs.every(d => d.diff === 0));
});

test("compareCounts: warns on a large type divergence", () => {
  const expected = { total: 100, types: new Map([["root", 10]]) };
  const r = compareCounts({ root: 9000 }, expected, 100);
  assert.ok(r.warnings.some(w => /root/.test(w)));
});

test("compareCounts: tolerates small drift without warning", () => {
  const expected = { total: 286561, types: new Map([["compound", 126360]]) };
  const r = compareCounts({ compound: 126359 }, expected, 286560); // -1, within tolerance
  assert.equal(r.warnings.length, 0);
});

test("compareCounts: warns when record count is far from expected", () => {
  const expected = { total: 286561, types: new Map() };
  const r = compareCounts({}, expected, 200000);
  assert.ok(r.warnings.some(w => /Record count/.test(w)));
});

test("compareCounts: flags missing expected file", () => {
  const r = compareCounts({ root: 1 }, null, 100);
  assert.ok(r.warnings.some(w => /No expected counts/.test(w)));
});

// ---- DCS: grammar-category grouping ----
test("classifyGram groups DCS categories", () => {
  assert.equal(classifyGram("m"), "nominal");
  assert.equal(classifyGram("f"), "nominal");
  assert.equal(classifyGram("mn"), "nominal");
  assert.equal(classifyGram("adj"), "adjectival");
  assert.equal(classifyGram("ind"), "indeclinable");
  assert.equal(classifyGram("10. P."), "verbal");
  assert.equal(classifyGram("Denom. P."), "verbal");
  assert.equal(classifyGram("1. ?."), "verbal"); // encoding-damaged pada still verbal
  assert.equal(classifyGram(""), "unspecified");
  assert.equal(classifyGram("weird"), "other");
});

// ---- Sense depth: sense-unit counting ----
test("senseUnits counts markers with a floor of 1", () => {
  assert.equal(senseUnits("<div n='1'> a <div n='2'> b", /<div\b/g), 2);
  assert.equal(senseUnits("single sense, no marker", /<div\b/g), 1);
  assert.equal(senseUnits("∙²1 a ∙²2 b ∙²3 c", /∙/g), 3);
  assert.equal(senseUnits("", /<div\b/g), 1);
});

test("senseUnits is repeatable (does not leak regex lastIndex)", () => {
  const re = /<div\b/g;
  assert.equal(senseUnits("<div><div>", re), 2);
  assert.equal(senseUnits("<div><div>", re), 2); // second call must match the first
});

// ---- All-dictionary coverage: classify + fit bands ----
test("coverage classify: priority root > compound > proper > gender", () => {
  assert.equal(classify("<L>1<k1>aMS<lex></lex> <info verb=\"genuineroot\"/>"), "rootVerb");
  assert.equal(classify("<L>1<k1>a-kAra body"), "compoundOrSubentry"); // hyphen in k1
  assert.equal(classify("<L>1<k1>deva <lex>m.</lex>"), "nounMasculine");
  assert.equal(classify("<L>1<k1>nadI <lex>f.</lex>"), "nounFeminine");
  assert.equal(classify("<L>1<k1>vana <lex>n.</lex>"), "nounNeuter");
  assert.equal(classify("<L>1<k1>x <lex>ind.</lex>"), "indeclinable");
  assert.equal(classify("<L>1<k1>x plain body"), "other");
});

test("coverage fitBand thresholds", () => {
  assert.equal(fitBand(0, 0, {}, 0), "empty");
  assert.equal(fitBand(50, 100, { head: 95, body: 95, gram: 25 }, 4), "full structured fit");
  assert.equal(fitBand(50, 100, { head: 85, body: 85, citeTagged: 0, citeInlineIti: 6 }, 1), "prose / iti fit");
  assert.equal(fitBand(50, 100, { head: 95, body: 95, gram: 6 }, 2), "partial structured fit");
  assert.equal(fitBand(10, 100, { head: 85, body: 85, citeTagged: 0, citeInlineIti: 0 }, 0), "entry-shell fit");
  assert.equal(fitBand(25, 100, { head: 10, body: 10 }, 0), "weak fit");
  assert.equal(fitBand(5, 100, { head: 10, body: 10 }, 0), "outside scheme");
});

test("coverage median and percent", () => {
  assert.equal(median([3, 1, 2]), 2);
  assert.equal(median([1, 2, 3, 4]), 2.5);
  assert.equal(median([]), 0);
  assert.equal(percent(1, 4), 25);
  assert.equal(percent(1, 0), 0);
});

// ---- Citation apparatus: most-frequent raw form ----
test("topForm picks the most frequent raw form for a canonical id", () => {
  assert.equal(topForm({ count: 7, forms: new Map([["MBh", 5], ["Mbh", 2]]) }), "MBh");
  assert.equal(topForm({ count: 1, forms: new Map([["RV", 1]]) }), "RV");
});
