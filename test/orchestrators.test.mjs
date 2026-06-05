// Unit tests for decision-bearing helpers in the build orchestrators.
//
// The orchestrators read large source files in main(); they are guarded to run
// only when executed directly, so importing them here is side-effect-free and
// we can test their pure helpers with synthetic inputs.

import { test } from "node:test";
import assert from "node:assert/strict";

import { compareCounts } from "../scripts/build-mw-quantitative-depth.mjs";
import { senseUnits } from "../scripts/build-sense-depth.mjs";
import { jaccard, lookupKeysForLemma, reverseMatchProfile, sourceRecordCounts, splitExplicitMarkers } from "../scripts/build-r2-source-anchors.mjs";
import { classifyDrift, markerRunPrefixMatch, priorityForClass, sourceRecordExactMatches } from "../scripts/build-r2-parser-diagnostics.mjs";
import { parseCsv } from "../scripts/build-h5-anomaly-review.mjs";
import { mean as h4Mean, rankFamilyFields, roundPct } from "../scripts/build-h4-family-profiles.mjs";
import { edgeReviewClass, structuralDistance } from "../scripts/build-h6-structural-review.mjs";
import { classifyHubTarget } from "../scripts/build-xref-hub-review.mjs";
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

// ---- R2 source anchors: lookup keys, marker splitting, alignment score ----
test("lookupKeysForLemma carries historical source spellings", () => {
  assert.deepEqual(lookupKeysForLemma("dharma"), ["Darma", "DarmaH", "Darmma", "DarmmaH", "dharma"]);
  assert.deepEqual(lookupKeysForLemma("bodhisattva"), ["boDisattva", "boDisattvaH", "boDisattvaM", "bodhisattva"]);
});

test("splitExplicitMarkers keeps preface and numbered parts stable", () => {
  const parts = splitExplicitMarkers("grammar {@1@} first {@--2@} second", /\{@\s*(?:--)?(\d+)\.?\s*@\}/g);
  assert.deepEqual(parts.map(part => part.localId), ["preface", "1", "2"]);
  assert.equal(parts[0].splitConfidence, "lumped-proxy");
  assert.equal(parts[1].splitConfidence, "explicit");
  assert.deepEqual(parts.map(part => part.markerLabel ?? null), [null, "1", "2"]);
  assert.deepEqual(parts.map(part => part.markerRunIndex ?? null), [null, 0, 0]);
});

test("splitExplicitMarkers records numeric marker-run resets", () => {
  const parts = splitExplicitMarkers("grammar {@1@} first {@2@} second {@1@} derived", /\{@\s*(?:--)?(\d+)\.?\s*@\}/g);
  assert.deepEqual(parts.map(part => part.localId), ["preface", "1", "2", "1"]);
  assert.deepEqual(parts.map(part => part.markerRunIndex ?? null), [null, 0, 0, 1]);
});

test("splitExplicitMarkers captures div n labels while keeping ordinal ids", () => {
  const marker = /<div\b(?:[^>]*?\bn=["']?([^"'>\s]+))?[^>]*>/g;
  const parts = splitExplicitMarkers("lead <div n=\"1\"> first <div type=\"x\" n=\"p\"> preverb <div n=\"2\"> second", marker, {
    useMarkerLabelAsLocalId: false
  });
  assert.deepEqual(parts.map(part => part.localId), ["preface", "1", "2", "3"]);
  assert.deepEqual(parts.map(part => part.markerLabel ?? null), [null, "1", "p", "2"]);
  assert.deepEqual(parts.map(part => part.markerRunIndex ?? null), [null, 0, null, 0]);
});

test("jaccard scores anchor overlap", () => {
  assert.equal(jaccard(["a", "b"], ["b", "c"]), 1 / 3);
  assert.equal(jaccard([], []), 0);
});

test("sourceRecordCounts keeps the largest source records first", () => {
  const rows = [
    { blockIds: ["2"], rawHeadword: "b", sourceLine: 20, href: "b" },
    { blockIds: ["1"], rawHeadword: "a", sourceLine: 10, href: "a" },
    { blockIds: ["2"], rawHeadword: "b", sourceLine: 20, href: "b" },
    { blockIds: ["3"], rawHeadword: "c", sourceLine: 30, href: "c" }
  ];
  assert.deepEqual(sourceRecordCounts(rows, 2), [
    { blockId: "2", rawHeadword: "b", sourceLine: 20, href: "b", rowCount: 2 },
    { blockId: "1", rawHeadword: "a", sourceLine: 10, href: "a", rowCount: 1 }
  ]);
});

test("reverseMatchProfile ranks AE equivalents by first matching group", () => {
  const lookup = new Set(["gam"]);
  assert.deepEqual(
    reverseMatchProfile("{@Approach@} {#upa gam#} {#yA#}", lookup),
    { rank: "high", firstGroupIndex: 1, matchGroupCount: 1, equivalentGroupCount: 3, score: 0.5 }
  );
  assert.equal(
    reverseMatchProfile("{@A@} {#foo#} {#bar#} {#baz#} {#gam#}", lookup).rank,
    "medium"
  );
  assert.equal(
    reverseMatchProfile("{@A@} {#one#} {#two#} {#three#} {#four#} {#five#} {#six#} {#gam#}", lookup).rank,
    "low"
  );
  assert.equal(
    reverseMatchProfile("{@A@} {#one#} {#two#} {#three#} {#four#} {#five#} {#six#} {#seven#} {#eight#} {#nine#} {#ten#} {#gam#}", lookup).rank,
    "tail"
  );
  assert.equal(reverseMatchProfile("{@No match@} {#yA#}", lookup).rank, "no-match");
});

test("R2 parser diagnostics classify drift by rebuild work package", () => {
  assert.equal(
    classifyDrift({ parserFamily: "western", split: "ap-bullet", sourceSenseRows: 16, archivedSenseRows: 16 }),
    "archive-parity"
  );
  assert.equal(
    classifyDrift({ parserFamily: "western", split: "number-marker", sourceSenseRows: 172, archivedSenseRows: 23 }),
    "over-split-candidate"
  );
  assert.equal(
    classifyDrift({ parserFamily: "western", split: "div", sourceSenseRows: 367, archivedSenseRows: 0 }),
    "source-only-dictionary"
  );
  assert.equal(
    classifyDrift({ parserFamily: "reverse", split: "reverse-equivalent", sourceSenseRows: 243, archivedSenseRows: 30 }),
    "reverse-overmatch"
  );
  assert.equal(
    classifyDrift({ parserFamily: "indigenous", split: "iti-unit", sourceSenseRows: 27, archivedSenseRows: 9 }),
    "indigenous-coarse-review"
  );
});

test("R2 parser diagnostics keep parser priorities stable", () => {
  assert.equal(priorityForClass("over-split-candidate"), "high");
  assert.equal(priorityForClass("mild-drift"), "medium");
  assert.equal(priorityForClass("archive-parity"), "low");
  assert.equal(priorityForClass("no-anchor-evidence"), "info");
});

test("R2 parser diagnostics detects marker-run prefixes that match archive counts", () => {
  assert.deepEqual(
    markerRunPrefixMatch({ archivedSenseRows: 23, markerRunCounts: { 0: 9, 1: 14, 2: 4 } }),
    { maxRunIndex: 1, runCount: 2, countedRows: 23 }
  );
  assert.equal(markerRunPrefixMatch({ archivedSenseRows: 10, markerRunCounts: { 0: 9, 1: 14 } }), null);
});

test("R2 parser diagnostics detects source records that match archive counts", () => {
  assert.deepEqual(sourceRecordExactMatches({
    archivedSenseRows: 7,
    sourceRecordCounts: [
      { blockId: "1", rowCount: 8 },
      { blockId: "2", rowCount: 7 }
    ]
  }), [{ blockId: "2", rowCount: 7 }]);
  assert.deepEqual(sourceRecordExactMatches({ archivedSenseRows: 0, sourceRecordCounts: [{ blockId: "1", rowCount: 1 }] }), []);
});

// ---- H5 anomaly queue: quoted CSV parsing ----
test("parseCsv handles quoted commas and escaped quotes", () => {
  const rows = parseCsv('a,b,c\nx,"y, z","q ""quoted"""\n');
  assert.deepEqual(rows, [{ a: "x", b: "y, z", c: 'q "quoted"' }]);
});

// ---- H4 family profiles: stable ranking helpers ----
test("H4 mean and percentage rounding are stable", () => {
  assert.ok(Math.abs(h4Mean([0.1, 0.2, Number.NaN, 0.3]) - 0.2) < 1e-12);
  assert.equal(h4Mean([]), 0);
  assert.equal(roundPct(1 / 3), 0.3333);
});

test("rankFamilyFields chooses high and low fields deterministically", () => {
  const rows = [
    { fieldKey: "a", fieldOrder: 2, meanCoveragePct: 0.5, dictionariesWithCoverage: 1 },
    { fieldKey: "b", fieldOrder: 1, meanCoveragePct: 0.5, dictionariesWithCoverage: 3 },
    { fieldKey: "c", fieldOrder: 3, meanCoveragePct: 0.1, dictionariesWithCoverage: 1 }
  ];
  assert.deepEqual(rankFamilyFields(rows, "high", 2).map(row => row.fieldKey), ["b", "a"]);
  assert.deepEqual(rankFamilyFields(rows, "low", 2).map(row => row.fieldKey), ["c", "b"]);
});

// ---- H6 structural-register review: stable distance labels ----
test("structuralDistance normalizes H6 chart coordinates", () => {
  assert.deepEqual(
    structuralDistance({ citationRegisterPct: 0, grammarPct: 0 }, { citationRegisterPct: 100, grammarPct: 100 }),
    { citationDeltaPct: 100, grammarDeltaPct: 100, structuralDistance01: 1 }
  );
  assert.equal(
    structuralDistance({ citationRegisterPct: 10, grammarPct: 20 }, { citationRegisterPct: 10, grammarPct: 20 }).structuralDistance01,
    0
  );
});

test("edgeReviewClass separates controls, tensions, and convergence", () => {
  assert.equal(
    edgeReviewClass({ consensus_support: 0.8 }, { structuralDistance01: 0.1 }, true, true),
    "positive-control"
  );
  assert.equal(
    edgeReviewClass({ consensus_support: 0.8 }, { structuralDistance01: 0.4 }, true, true),
    "genealogy-structure-tension"
  );
  assert.equal(
    edgeReviewClass({ consensus_support: 0.05 }, { structuralDistance01: 0.1 }, false, true),
    "structural-convergence"
  );
});

// ---- Xref hub review: target-class labels ----
test("classifyHubTarget separates prefix hubs, lexical targets, and normalization risks", () => {
  assert.equal(classifyHubTarget("a-"), "prefix-convention");
  assert.equal(classifyHubTarget("mahA\u02da"), "prefix-convention");
  assert.equal(classifyHubTarget("narasiMha"), "lexical-target");
  assert.equal(classifyHubTarget("paropadeSe pAMqityaM"), "normalization-risk");
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
