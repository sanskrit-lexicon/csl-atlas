import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { wilson, fitLogistic, foldCrosswalkCoverage, familyByUnionCode, buildPayload } from "../scripts/build-ghost-stock.mjs";

const FIXED_AT = "2026-07-25T00:00:00.000Z";

const INVENTORY = [
  { code: "mw", family: "Sanskrit-English" },
  { code: "pw", family: "Sanskrit-German" },
  { code: "pwg", family: "Sanskrit-German" },
  { code: "bhs", family: "Specialized" }
];

function unionRow(overrides = {}) {
  return { slp1: "deva", iast: "deva", n_dicts: "2", dicts: "MW PWG", gender: "m", fem_fold: "", ...overrides };
}

test("wilson brackets the point estimate and stays in [0,1]", () => {
  const ci = wilson(8, 10);
  assert.ok(ci.lo > 0.49 && ci.lo < 0.50, `lo ${ci.lo}`);
  assert.ok(ci.hi > 0.94 && ci.hi < 0.95, `hi ${ci.hi}`);
  assert.deepEqual(wilson(0, 0), { lo: null, hi: null });
  const extreme = wilson(10, 10);
  assert.ok(extreme.hi <= 1 && extreme.lo < 1);
});

test("fitLogistic recovers the closed-form single-binary-predictor solution", () => {
  // x=0: 10 of 100 positive (odds 1/9); x=1: 50 of 100 positive (odds 1).
  // Closed form: intercept = log(1/9), slope = log(9).
  const X = [];
  const y = [];
  for (let i = 0; i < 100; i++) {
    X.push([1, 0]);
    y.push(i < 10 ? 1 : 0);
  }
  for (let i = 0; i < 100; i++) {
    X.push([1, 1]);
    y.push(i < 50 ? 1 : 0);
  }
  const fit = fitLogistic(X, y);
  assert.ok(fit.converged);
  assert.ok(Math.abs(fit.beta[0] - Math.log(1 / 9)) < 1e-6, `intercept ${fit.beta[0]}`);
  assert.ok(Math.abs(fit.beta[1] - Math.log(9)) < 1e-6, `slope ${fit.beta[1]}`);
  assert.ok(fit.mcFaddenR2 > 0 && fit.mcFaddenR2 < 1);
});

test("foldCrosswalkCoverage: anchor beats covered-no-anchor beats absent across homonym rows", () => {
  const byKey = foldCrosswalkCoverage([
    { mw_key1: "aMSaka1", covered_flag: "0", heritage_entry_anchor: "" },
    { mw_key1: "aMSaka2", covered_flag: "1", heritage_entry_anchor: "DICO/1.html#a.mzaka" },
    { mw_key1: "deva", covered_flag: "1", heritage_entry_anchor: "" }
  ]);
  assert.equal(byKey.get("aMSaka"), "anchored");
  assert.equal(byKey.get("deva"), "covered-no-anchor");
});

test("familyByUnionCode maps PWK onto the inventory's pw row and rejects unknown codes", () => {
  const familyOf = familyByUnionCode(INVENTORY);
  assert.equal(familyOf("PWK"), "Sanskrit-German");
  assert.equal(familyOf("MW"), "Sanskrit-English");
  assert.throws(() => familyOf("XX"));
});

test("buildPayload strata, per-dict shares, cube, and triple filter agree on a small fixture", () => {
  const unionRows = [
    // MW-unique, Heritage explicitly uncovered, DCS-unattested -> triple filter (explicit tier)
    unionRow({ slp1: "GoRawaka", n_dicts: "1", dicts: "MW" }),
    // MW-unique, absent from the crosswalk entirely, unattested -> triple filter (missing tier)
    unionRow({ slp1: "kalpanikaTa", n_dicts: "1", dicts: "MW" }),
    // MW-unique but attested -> not in the queue
    unionRow({ slp1: "deva", n_dicts: "1", dicts: "MW" }),
    // shared MW lemma, Heritage-covered, attested
    unionRow({ slp1: "agni", n_dicts: "2", dicts: "MW PWG" }),
    // non-MW lemma: counts for strata/per-dict, invisible to the cube
    unionRow({ slp1: "buddhaBASA", n_dicts: "1", dicts: "BHS" })
  ];
  const dcsLemmas = {
    deva: { freqBand: 5, attested: true },
    agni: { freqBand: 5, attested: true }
  };
  const crosswalkRows = [
    { mw_key1: "GoRawaka", covered_flag: "0", heritage_entry_anchor: "" },
    { mw_key1: "deva", covered_flag: "1", heritage_entry_anchor: "DICO/24.html#deva" },
    { mw_key1: "agni", covered_flag: "1", heritage_entry_anchor: "DICO/2.html#agni" }
  ];
  const p = buildPayload(unionRows, dcsLemmas, crosswalkRows, INVENTORY, { generatedAt: FIXED_AT });

  assert.equal(p.totals.unionLemmas, 5);
  assert.equal(p.totals.unionAttested, 2);
  assert.equal(p.totals.mwLemmas, 4);
  assert.equal(p.totals.mwUnique, 3);
  assert.equal(p.totals.mwHeritageCovered, 2);
  assert.equal(p.totals.mwCrosswalkMissing, 1); // kalpanikaTa (buddhaBASA is non-MW and invisible to the cube)

  const s1 = p.byMultiplicity.find((r) => r.nDicts === 1);
  assert.equal(s1.lemmas, 4);
  assert.equal(s1.attested, 1);

  const mw = p.perDict.find((d) => d.code === "MW");
  assert.equal(mw.lemmas, 4);
  assert.equal(mw.unique, 3);
  assert.equal(mw.uniqueAttested, 1);
  const bhs = p.perDict.find((d) => d.code === "BHS");
  assert.equal(bhs.unique, 1);
  assert.equal(bhs.family, "Specialized");

  const cubeSum = p.heritageCube.cells.reduce((a, c) => a + c.lemmas, 0);
  assert.equal(cubeSum, p.totals.mwLemmas);

  assert.equal(p.tripleFilter.evidenceGrade, "inferred");
  assert.deepEqual(p.tripleFilter.explicitUncovered, ["GoRawaka"]);
  assert.deepEqual(p.tripleFilter.crosswalkMissing, ["kalpanikaTa"]);
  assert.equal(p.tripleFilter.total, 2);
  assert.equal(p.totals.tripleFilter, 2);
});

test("buildPayload rejects a union row whose n_dicts disagrees with its dicts list", () => {
  assert.throws(() => buildPayload([unionRow({ n_dicts: "3", dicts: "MW PWG" })], {}, [], INVENTORY, { generatedAt: FIXED_AT }));
});

test("committed packet is internally consistent", () => {
  const file = path.resolve(process.cwd(), "src", "data", "ghost-stock", "ghost_stock.json");
  assert.ok(fs.existsSync(file), "committed ghost_stock.json missing");
  const packet = JSON.parse(fs.readFileSync(file, "utf8"));
  assert.equal(packet.schemaVersion, "1.0.0");
  const sum = packet.byMultiplicity.reduce((a, r) => a + r.lemmas, 0);
  assert.equal(sum, packet.totals.unionLemmas);
  const cubeSum = packet.heritageCube.cells.reduce((a, c) => a + c.lemmas, 0);
  assert.equal(cubeSum, packet.totals.mwLemmas);
  assert.equal(
    packet.tripleFilter.explicitUncovered.length + packet.tripleFilter.crosswalkMissing.length,
    packet.totals.tripleFilter
  );
  assert.equal(packet.tripleFilter.evidenceGrade, "inferred");
  assert.ok(packet.logistic.converged);
  assert.ok(packet.limitations.length >= 4);
});
