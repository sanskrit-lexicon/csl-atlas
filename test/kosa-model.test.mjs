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
  ["required device dropped", d => { d.orderingDevices = d.orderingDevices.filter(x => x.device !== "verse"); }, /missing "verse"/],
  // verifier round 1 (H5328): every field of the gender object must follow from its tag
  ["avyaya member not flagged indeclinable", d => {
    const m = firstExpanded(d, "indeclinable").groups[0].sets[0].members.find(x => x.gender?.tag === "a");
    m.gender.indeclinable = false;
  }, /indeclinable false disagree with tag a/],
  ["optional flag without vA", d => { firstExpanded(d, "synonymic").groups[1].sets[0].members[0].gender.optional = true; }, /optional true disagree/],
  ["number without dvi/ba", d => { firstExpanded(d, "synonymic").groups[1].sets[0].members[0].gender.number = "pl"; }, /number "pl" disagree/],
  ["parsed false on a clean tag", d => { firstExpanded(d, "synonymic").groups[1].sets[0].members[0].gender.parsed = false; }, /parsed false disagree/],
  ["kāṇḍa stated-in-text without a label", d => { d.kandas[0].label = null; }, /kandas\[0\]: labelStatus stated-in-text needs a label/],
  ["counts.sets below the expanded sets", d => { firstExpanded(d, "synonymic").counts.sets = 1; }, /expanded sets exceed counts.sets/],
  ["counts.members below the expanded members", d => { firstExpanded(d, "synonymic").counts.members = 1; }, /expanded members exceed counts.members/],
  // verifier round 2
  ["counts.fullVerses below the expanded verses", d => { firstExpanded(d, "synonymic").counts.fullVerses = 0; }, /expanded fullVerses exceed/],
  ["section type contradicting its label", d => {
    const v = firstExpanded(d, "synonymic");
    v.sectionType = "homonymic";
    v.groups.forEach(g => g.sets.forEach(s => { s.kind = "homonym-sense"; }));
  }, /contradicts its section label/],
  ["upavarga without its IAST", d => {
    const g = firstExpanded(d, "synonymic").groups[0];
    g.upavarga = "x";
    g.upavargaIast = null;
  }, /upavarga and upavargaIast/]
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

const ARMH_MUTATIONS = [
  ["duplicate locator", d => { const g = firstExpanded(d).groups; g[1].locator = g[0].locator; }, /duplicate locator/],
  ["two unsegmented-verse sets in one group", d => {
    const g = firstExpanded(d).groups[0];
    g.sets.push(structuredClone(g.sets[0]));
  }, /exactly one unsegmented-verse set/],
  ["eid in the exploded model", d => { firstExpanded(d).groups[0].sets[0].eid = 7; }, /eid must be null/],
  ["locator of another kāṇḍa", d => { firstExpanded(d).groups[0].locator = "5.1.1.3"; }, /does not belong to kāṇḍa 1/]
];

for (const [name, mutate, expected] of ARMH_MUTATIONS) {
  test(`validator rejects (ARMH): ${name}`, () => {
    const doc = clone(armh);
    mutate(doc);
    const errors = validateKosaModel(doc);
    assert.ok(errors.some(e => expected.test(e)), `${name}: got ${JSON.stringify(errors.slice(0, 3))}`);
  });
}

test("ARMH verse-groups keep their whole verse block (a locator may span two verses)", () => {
  const byLocator = new Map(firstExpanded(armh).groups.map(g => [g.locator, g]));
  assert.deepEqual(byLocator.get("1.1.1.6").verseRefs.map(r => r.n), [6, 7]);
  assert.ok(armh.kandas.flatMap(k => k.vargas).flatMap(v => v.groups).every(g => g.verseLines.length > 0));
});

test("device notes agree with the measures they summarise", () => {
  const notes = code => Object.fromEntries(measures.devices[code].map(d => [d.device, d.note]));
  const col = measures.measures.AMAR.sectionColophons;
  assert.equal(col.sections, 24);
  assert.deepEqual(col.withoutClosing, ["avyayavargaḥ"], "only the avyaya-varga lacks a closing iti");
  assert.deepEqual(col.withoutOpening, ["bhūmivargaḥ"], "aTAvyayavargaH is atha + avyaya- in sandhi");
  assert.match(notes("AMAR").varga, new RegExp(`${col.withOpeningAtha} open with atha`));
  assert.match(notes("AMAR")["indeclinable-section"], /liṅgādisaṅgraha/, "the text names a varga after avyaya");
  assert.equal(measures.measures.AMAR.verseNumberingScope.scope, "per-section");
  assert.equal(measures.measures.ABCH.verseNumberingScope.scope, "continuous");
  assert.match(notes("ABCH").verse, /continuously/);
  assert.match(notes("AMAR").verse, /restarts/);
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
