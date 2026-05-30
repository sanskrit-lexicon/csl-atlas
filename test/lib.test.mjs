// Unit tests for the deterministic atlas libraries.
// Run with: npm test  (node --test, no external dependency)
//
// These cover the pure logic the generators depend on. They do not read the
// large source files; inputs are small synthetic records modeled on real CDSL
// markup seen during development.

import { test } from "node:test";
import assert from "node:assert/strict";
import os from "node:os";
import fs from "node:fs";
import path from "node:path";

import { parseHeader, iterateRecords } from "../scripts/lib/mw-parser.mjs";
import { classifyTypes, normalizeSource, isLexicographerOnly, extractCitations } from "../scripts/lib/mw-classifiers.mjs";
import { baseForm, layerForSource, isEditorialReference, recordSourceLayers } from "../scripts/lib/mw-source-layers.mjs";
import { compoundSegmentCount, familyBase } from "../scripts/lib/mw-depth-graph.mjs";
import { normalizeLemma } from "../scripts/lib/dict-normalize.mjs";
import { genderFromLex } from "../scripts/lib/dict-parser.mjs";
import { lemmaConfidence, genderConflict, presentDicts } from "../scripts/lib/dict-align.mjs";
import { foldSiglum, canonicalSiglum } from "../scripts/lib/source-siglum.mjs";
import { loadPreserved, reviewFields, reviewPayload } from "../scripts/lib/review-report.mjs";

// ---- mw-parser ----
test("parseHeader extracts flat header fields", () => {
  const h = parseHeader("<L>2<pc>1,1<k1>akAra<k2>a—kAra<h>1<e>3");
  assert.equal(h.L, "2");
  assert.equal(h.pc, "1,1");
  assert.equal(h.k1, "akAra");
  assert.equal(h.k2, "a—kAra");
  assert.equal(h.h, "1");
  assert.equal(h.ecode, "3");
});

test("iterateRecords yields records with line numbers and href", () => {
  const text = ["<L>1<pc>1,1<k1>a<k2>a<e>1", "<s>a</s> ¦ first letter", "<LEND>"].join("\n");
  const recs = [...iterateRecords(text)];
  assert.equal(recs.length, 1);
  assert.equal(recs[0].k1, "a");
  assert.equal(recs[0].startLine, 1);
  assert.match(recs[0].href, /#L1$/);
  assert.match(recs[0].body, /first letter/);
});

// ---- mw-classifiers ----
test("classifyTypes: structural types from ecode/k2", () => {
  assert.deepEqual(classifyTypes({ ecode: "2", k2: "x", body: "" }), ["derived"]);
  assert.deepEqual(classifyTypes({ ecode: "1A", k2: "x", body: "" }), ["continuation"]);
  assert.ok(classifyTypes({ ecode: "3", k2: "a—b", body: "" }).includes("compound"));
  assert.ok(classifyTypes({ ecode: "1", k2: "x", body: "x genuineroot x" }).includes("root"));
});

test("classifyTypes: grammar types attach only to primary entries", () => {
  assert.deepEqual(classifyTypes({ ecode: "1", k2: "x", body: "<lex>m.</lex>" }), ["noun-m"]);
  // a compound with a gender tag stays compound only (grammar excluded)
  assert.deepEqual(classifyTypes({ ecode: "3", k2: "a—b", body: "<lex>m.</lex>" }), ["compound"]);
});

test("classifyTypes: grammar genders are mutually exclusive by priority", () => {
  assert.deepEqual(classifyTypes({ ecode: "1", k2: "x", body: "<lex>m.</lex> ... <lex>f.</lex>" }), ["noun-m"]);
  assert.deepEqual(classifyTypes({ ecode: "1", k2: "x", body: "<lex>mfn.</lex>" }), ["adjective-mfn"]);
});

test("classifyTypes: lexicographer-only, vedic-accented, other", () => {
  assert.ok(classifyTypes({ ecode: "1", k2: "x", body: "<ls>L.</ls>" }).includes("lexicographer-only"));
  assert.ok(!classifyTypes({ ecode: "1", k2: "x", body: "<ls>RV.</ls>" }).includes("lexicographer-only"));
  assert.ok(classifyTypes({ ecode: "1", k2: "a/MSa", body: "" }).includes("vedic-accented"));
  assert.deepEqual(classifyTypes({ ecode: "1", k2: "x", body: "" }), ["other"]);
});

test("normalizeSource and isLexicographerOnly", () => {
  assert.equal(normalizeSource(" MBh. "), "MBh");
  assert.equal(normalizeSource("L."), "L");
  assert.equal(isLexicographerOnly(["L"]), true);
  assert.equal(isLexicographerOnly(["L", "RV"]), false);
  assert.equal(isLexicographerOnly([]), false);
});

test("extractCitations pulls <ls> values", () => {
  assert.deepEqual(extractCitations("x <ls>RV. x, 1</ls> y <ls>L.</ls>"), ["RV. x, 1", "L."]);
});

// ---- mw-source-layers ----
test("baseForm strips locus to base sigla", () => {
  assert.equal(baseForm("MBh. iii,5"), "MBh");
  assert.equal(baseForm("P. 1,1,14"), "P");
  assert.equal(baseForm("RV"), "RV");
  assert.equal(baseForm("Yājñ., Sch"), "Yājñ");
});

test("layerForSource maps known sources and falls back to base form", () => {
  assert.equal(layerForSource("RV"), "vedic");
  assert.equal(layerForSource("MBh"), "epic");
  assert.equal(layerForSource("MBh. i"), "epic"); // base-form fallback
  assert.equal(layerForSource("L"), "lexicographic");
  assert.equal(layerForSource("ZZZ-unmapped"), "unknown");
});

test("isEditorialReference recognizes editorial markers", () => {
  assert.equal(isEditorialReference("ib"), true);
  assert.equal(isEditorialReference("RV"), false);
});

test("recordSourceLayers computes span ignoring unknown", () => {
  const r = recordSourceLayers({ body: "<ls>RV.</ls> <ls>MBh.</ls>" });
  assert.equal(r.citationCount, 2);
  assert.equal(r.earliestLayer, "vedic");
  assert.equal(r.latestLayer, "epic");
  assert.ok(r.sourceLayerSpan >= 1);
});

// ---- mw-depth-graph ----
test("compoundSegmentCount and familyBase", () => {
  assert.equal(compoundSegmentCount({ k2: "a—tra—koSa" }), 3);
  assert.equal(compoundSegmentCount({ k2: "agni" }), 1);
  assert.equal(familyBase({ k2: "a/Msa—tra—koSa" }), "aMsa");
  assert.equal(familyBase({ k1: "agni", k2: "" }), "agni");
});

// ---- dict-normalize ----
test("normalizeLemma strips accents and trailing digits", () => {
  assert.deepEqual(normalizeLemma("a/MSa"), { normalized: "aMSa", changed: true });
  assert.deepEqual(normalizeLemma("agni"), { normalized: "agni", changed: false });
  assert.equal(normalizeLemma("agni2").normalized, "agni");
});

// ---- dict-parser ----
test("genderFromLex maps <lex> to coarse tokens", () => {
  assert.equal(genderFromLex("<lex>m.</lex>"), "m");
  assert.equal(genderFromLex("<lex>mfn.</lex>"), "adj");
  assert.equal(genderFromLex("<lex>Adj.</lex>"), "adj");
  assert.equal(genderFromLex("<lex>ind.</lex>"), "ind");
  assert.equal(genderFromLex("no tag"), null);
});

// ---- dict-align ----
test("lemmaConfidence: high when raws identical, medium otherwise", () => {
  const high = { mw: { raws: new Set(["agni"]) }, pwg: { raws: new Set(["agni"]) } };
  const med = { mw: { raws: new Set(["o"]) }, pwg: { raws: new Set(["o~"]) } };
  assert.equal(lemmaConfidence(high, ["mw", "pwg"]), "high");
  assert.equal(lemmaConfidence(med, ["mw", "pwg"]), "medium");
});

test("genderConflict: disjoint specific genders only", () => {
  const conflict = { mw: { genders: new Set(["m"]) }, pwg: { genders: new Set(["f"]) } };
  const overlap = { mw: { genders: new Set(["m"]) }, pwg: { genders: new Set(["m", "f"]) } };
  const adjOnly = { mw: { genders: new Set(["adj"]) }, pwg: { genders: new Set(["m"]) } };
  assert.equal(genderConflict(conflict, ["mw", "pwg"]).conflict, true);
  assert.equal(genderConflict(overlap, ["mw", "pwg"]).conflict, false);
  assert.equal(genderConflict(adjOnly, ["mw", "pwg"]).conflict, false);
});

test("presentDicts respects order", () => {
  assert.deepEqual(presentDicts({ pwg: {}, mw: {} }, ["mw", "ap", "pwg"]), ["mw", "pwg"]);
});

// ---- source-siglum ----
test("foldSiglum folds case and diacritics", () => {
  assert.equal(foldSiglum("MBh"), "mbh");
  assert.equal(foldSiglum("MBH"), "mbh");
  assert.equal(foldSiglum("ṚV"), "rv");
  assert.equal(foldSiglum("RV"), "rv");
});

test("canonicalSiglum applies the reviewed alias table", () => {
  assert.equal(canonicalSiglum("MBh"), "mbh");
  // bhag -> bhp via src/data/dict-source-aliases.json
  assert.equal(canonicalSiglum("Bhāg"), "bhp");
  assert.equal(canonicalSiglum("BhP"), "bhp");
});

// ---- review-report ----
test("reviewFields defaults to needs-review, preserves human decisions", () => {
  const empty = reviewFields(new Map(), "x");
  assert.equal(empty.reviewStatus, "needs-review");
  assert.equal(empty.reviewedValue, null);
  const preserved = new Map([["x", { reviewStatus: "reviewed-corrected", reviewedValue: { g: "n" }, reviewer: "ab", reviewedAt: "2026-01-01", note: "ok" }]]);
  assert.equal(reviewFields(preserved, "x").reviewStatus, "reviewed-corrected");
  assert.equal(reviewFields(preserved, "x").reviewer, "ab");
});

test("reviewPayload assembles envelope with recordCount = items.length", () => {
  const p = reviewPayload({ queue: "pos-gender-conflict", sourcePath: "x", items: [{}, {}], extra: { foo: 1 } });
  assert.equal(p.queue, "pos-gender-conflict");
  assert.equal(p.recordCount, 2);
  assert.equal(p.foo, 1);
  assert.ok(Array.isArray(p.items) && Array.isArray(p.assumptions) && Array.isArray(p.warnings));
});

test("loadPreserved returns empty map for a missing file", () => {
  const p = path.join(os.tmpdir(), `nope-${Date.now()}.json`);
  assert.equal(loadPreserved(p).size, 0);
});

test("loadPreserved carries only human-decided items", () => {
  const file = path.join(os.tmpdir(), `rev-${Date.now()}.json`);
  fs.writeFileSync(file, JSON.stringify({ items: [
    { reviewId: "a", reviewStatus: "needs-review" },
    { reviewId: "b", reviewStatus: "reviewed-ok" },
    { reviewId: "c", reviewStatus: "machine", reviewer: "x" }
  ] }));
  const m = loadPreserved(file);
  fs.unlinkSync(file);
  assert.equal(m.has("a"), false);
  assert.equal(m.has("b"), true);
  assert.equal(m.has("c"), true);
});
