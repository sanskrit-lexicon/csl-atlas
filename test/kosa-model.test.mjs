// H5328 — kośa macrostructure model: the committed instances validate, and the
// validator rejects each class of defect it claims to catch (mutation tests), so a
// PASS is evidence rather than a validator that cannot fail.

import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";

import { validateKosaModel } from "../scripts/validate-kosa-model.mjs";

const LEXICO = path.resolve("data", "lexico");
const load = name => JSON.parse(fs.readFileSync(path.join(LEXICO, name), "utf8"));
const clone = v => structuredClone(v);

const amar = load("kosa_model_amar_sample.json");
const armh = load("kosa_model_armh_sample.json");
const measures = load("kosa_model_measures.json");

function firstExpanded(doc, sectionType) {
  for (const k of doc.kandas) for (const v of k.vargas) {
    if (v.groups.length && (!sectionType || v.sectionType === sectionType)) return v;
  }
  throw new Error(`no expanded ${sectionType ?? ""} varga`);
}

test("every committed kośa instance validates", () => {
  for (const f of fs.readdirSync(LEXICO).filter(f => /^kosa_model_.*_sample\.json$/.test(f))) {
    assert.deepEqual(validateKosaModel(load(f)), [], f);
  }
});

test("the Amarakośa sample covers all three kāṇḍas and all three section types", () => {
  assert.equal(amar.kandas.length, 3);
  const expanded = amar.kandas.flatMap(k => k.vargas).filter(v => v.groups.length);
  assert.deepEqual([...new Set(expanded.map(v => v.sectionType))].sort(), ["homonymic", "indeclinable", "synonymic"]);
  assert.ok(amar.kandas.every(k => k.vargas.some(v => v.groups.length)), "each kāṇḍa has an expanded varga");
});

const MUTATIONS = [
  ["unknown gender tag", d => { firstExpanded(d, "synonymic").groups[0].sets[0].members[0].gender.tag = "xyz"; }, /does not match/],
  ["missing required counts", d => { delete firstExpanded(d).counts; }, /missing required "counts"/],
  ["unexpected property", d => { firstExpanded(d).groups[0].extra = 1; }, /unexpected property "extra"/],
  ["duplicate eid", d => {
    const g = firstExpanded(d, "synonymic").groups;
    g[1].sets[0].eid = g[0].sets[0].eid;
  }, /duplicate eid|not increasing/],
  ["homonym-sense inside a synonymic section", d => { firstExpanded(d, "homonymic").sectionType = "synonymic"; }, /not allowed in a synonymic section/],
  ["genders disagree with the tag", d => {
    const m = firstExpanded(d, "synonymic").groups[1].sets[0].members[0];
    m.gender.genders = ["f"];
  }, /disagree with tag/],
  ["inferred device claimed from the source text", d => {
    d.orderingDevices.find(x => x.device === "alphabetical-order").layer = "source-text";
  }, /inferred evidence must come from the measurement layer/],
  ["verse order broken", d => {
    const g = firstExpanded(d, "synonymic").groups;
    g[0].verseRefs = [{ n: 999, half: false }];
  }, /verse order broken/],
  ["required device dropped", d => { d.orderingDevices = d.orderingDevices.filter(x => x.device !== "verse"); }, /missing "verse"/]
];

for (const [name, mutate, expected] of MUTATIONS) {
  test(`validator rejects: ${name}`, () => {
    const doc = clone(amar);
    mutate(doc);
    const errors = validateKosaModel(doc);
    assert.ok(errors.some(e => expected.test(e)), `${name}: got ${JSON.stringify(errors.slice(0, 3))}`);
  });
}

test("validator rejects a segmented set in the exploded (ARMH) model", () => {
  const doc = clone(armh);
  firstExpanded(doc).groups[0].sets[0].kind = "synonym-set";
  assert.ok(validateKosaModel(doc).some(e => /exploded model admits only unsegmented-verse/.test(e)));
});

test("measured contrast: kośas show no alphabetical device, MW does", () => {
  const m = measures.measures;
  assert.ok(m.MW.alphabeticalAdjacency.nondecreasing > 0.9);
  for (const code of ["AMAR", "ABCH", "ARMH"]) assert.ok(m[code].alphabeticalAdjacency.nondecreasing < 0.55, code);
});

test("measured devices: nānārtha a-tergo order and Amara gender contiguity beat their baselines", () => {
  const a = measures.measures.AMAR;
  assert.ok(a.nanarthaOrder.finalConsonantNondecreasing > 0.95);
  assert.ok(a.nanarthaOrder.initialLetterNondecreasing < 0.6);
  const [nominal, indeclinable] = a.nanarthaOrder.series;
  assert.equal(a.nanarthaOrder.series.length, 2, "two a-tergo series: nominal, then indeclinable homonyms");
  assert.ok(nominal.indeclinableShare < 0.05 && indeclinable.indeclinableShare > 0.9);
  const firstSeries = a.nanarthaOrder.violations.filter(v => v.series === 1);
  assert.ok(firstSeries.filter(v => v.explainedBy).length >= firstSeries.length - 1, "all but one step explained by ḍ=l / b=v");
  assert.ok(a.genderContiguity.contiguousObserved > a.genderContiguity.contiguousExpectedUnderPermutation + 0.15);
  assert.ok(a.verseNumbering.every(r => r.otherSteps.length === 0), "verse numbers run in steps of one per varga");
});
