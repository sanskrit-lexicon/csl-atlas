import test from "node:test";
import assert from "node:assert/strict";
import {
  mulberry32,
  orderedDictionaries,
  maskCensus,
  dictSizes,
  noveltyForOrder,
  heapsFit,
  curveForOrder,
  kSubsets,
  buildPayload
} from "../scripts/build-heap-sat.mjs";

const INVENTORY = [
  { code: "pwg", year: 1855, family: "Sanskrit-German" },
  { code: "pw", year: 1879, family: "Sanskrit-German" },
  { code: "mw", year: 1899, family: "Sanskrit-English" },
  { code: "bhs", year: 1953, family: "Specialized" }
];

function unionRow(slp1, dicts) {
  const list = dicts.split(" ");
  return { slp1, iast: slp1, n_dicts: String(list.length), dicts, gender: "", fem_fold: "" };
}

test("mulberry32 is deterministic and in [0,1)", () => {
  const a = mulberry32(42);
  const b = mulberry32(42);
  for (let i = 0; i < 100; i++) {
    const va = a();
    assert.equal(va, b());
    assert.ok(va >= 0 && va < 1);
  }
});

test("orderedDictionaries sorts by year with siglum tie-break and maps union PWK to inventory pw", () => {
  const dicts = orderedDictionaries(["MW", "PWK", "BHS", "PWG"], INVENTORY);
  assert.deepEqual(dicts.map((d) => d.code), ["PWG", "PWK", "MW", "BHS"]);
  assert.equal(dicts[1].inventoryCode, "pw");
  assert.equal(dicts[1].year, 1879);
  assert.throws(() => orderedDictionaries(["XX"], INVENTORY), /no row/);
});

test("maskCensus folds lemmas to dictionary bitmasks and rejects inconsistent rows", () => {
  const rows = [
    unionRow("deva", "MW"),
    unionRow("agni", "MW PWG"),
    unionRow("soma", "PWG"),
    unionRow("deva", "MW") // duplicate normalized key -> ignored
  ];
  const census = maskCensus(rows, ["MW", "PWG"]);
  assert.equal(census.get(0b01), 1); // MW only
  assert.equal(census.get(0b11), 1); // MW + PWG
  assert.equal(census.get(0b10), 1); // PWG only
  assert.deepEqual(dictSizes(census, 2), [2, 2]);
  assert.throws(() => maskCensus([{ ...unionRow("x", "MW PWG"), n_dicts: "1" }], ["MW", "PWG"]), /disagrees/);
  assert.throws(() => maskCensus([unionRow("y", "ZZ")], ["MW", "PWG"]), /unknown dictionary code/);
});

test("noveltyForOrder credits each lemma to its earliest dictionary in the ordering", () => {
  const rows = [unionRow("a", "MW"), unionRow("b", "MW PWG"), unionRow("c", "PWG")];
  const census = maskCensus(rows, ["MW", "PWG"]);
  assert.deepEqual(noveltyForOrder(census, [0, 1]), [2, 1]); // MW first: a+b, then c
  assert.deepEqual(noveltyForOrder(census, [1, 0]), [2, 1]); // PWG first: b+c, then a
});

test("heapsFit recovers an exact power law", () => {
  const tokens = [10, 100, 1000, 10000];
  const distinct = tokens.map((n) => 2 * Math.sqrt(n));
  const fit = heapsFit(tokens, distinct);
  assert.ok(Math.abs(fit.beta - 0.5) < 1e-12, `beta ${fit.beta}`);
  assert.ok(Math.abs(fit.K - 2) < 1e-12, `K ${fit.K}`);
  assert.ok(Math.abs(fit.r2 - 1) < 1e-12);
});

test("curveForOrder accumulates and residuals are relative to the fitted increments", () => {
  const rows = [unionRow("a", "MW"), unionRow("b", "MW PWG"), unionRow("c", "PWG"), unionRow("d", "PWG")];
  const census = maskCensus(rows, ["MW", "PWG"]);
  const sizes = dictSizes(census, 2);
  const c = curveForOrder(census, sizes, [0, 1]);
  assert.deepEqual(c.cumTokens, [2, 5]);
  assert.deepEqual(c.cumDistinct, [2, 4]);
  assert.equal(c.residuals.length, 2);
});

test("kSubsets enumerates all size-k subsets", () => {
  const subsets = kSubsets(4, 2);
  assert.equal(subsets.length, 6);
  assert.deepEqual(subsets[0], [0, 1]);
  assert.deepEqual(subsets[5], [2, 3]);
});

test("buildPayload: totals cohere, steps in publication order, p-values in (0,1]", () => {
  const rows = [
    unionRow("a", "PWG"),
    unionRow("b", "PWG PWK"),
    unionRow("c", "PWK MW"),
    unionRow("d", "MW"),
    unionRow("e", "BHS"),
    unionRow("f", "MW BHS"),
    unionRow("g", "PWG MW"),
    unionRow("h", "PWK")
  ];
  const payload = buildPayload(rows, INVENTORY, { generatedAt: "2026-07-25T00:00:00.000Z", nPermutations: 200 });
  assert.equal(payload.totals.unionLemmas, 8);
  assert.deepEqual(payload.steps.map((s) => s.code), ["PWG", "PWK", "MW", "BHS"]);
  assert.deepEqual(payload.totals.specialised, ["BHS"]);
  const last = payload.steps[payload.steps.length - 1];
  assert.equal(last.cumulativeDistinct, 8);
  for (const s of payload.steps) assert.ok(s.novelty <= s.lemmas);
  const brk = payload.specialisedBreak;
  assert.ok(brk.orderPermutation.pOneSided > 0 && brk.orderPermutation.pOneSided <= 1);
  assert.ok(brk.labelPermutation.pOneSided > 0 && brk.labelPermutation.pOneSided <= 1);
  assert.equal(brk.labelPermutation.subsets, 4); // C(4,1)
  // deterministic: same inputs, same seed -> identical payload
  const again = buildPayload(rows, INVENTORY, { generatedAt: "2026-07-25T00:00:00.000Z", nPermutations: 200 });
  assert.deepEqual(again, payload);
});
