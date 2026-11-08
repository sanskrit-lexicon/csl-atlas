// H5334 — shape + internal-consistency contract for the etymology component
// census. The dataset is regenerated from csl-orig by
// `npm run build-etymology-census` (python), which CI has no source text for,
// so these tests validate the committed artefact rather than re-running it.

import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";

const CENSUS = path.resolve("data/etymology-census.json");
const census = JSON.parse(fs.readFileSync(CENSUS, "utf8"));

const TYPES = ["root-reference", "cognate", "vyutpatti", "affix", "nirukta-citation"];
const POSITIONS = ["initial", "medial", "final"];

test("census carries provenance and the declared type vocabulary", () => {
  for (const field of ["generatedAt", "license", "licenseUrl", "sourceRoot", "derivedFrom", "provenance", "note"]) {
    assert.ok(typeof census[field] === "string" && census[field].length > 0, `missing ${field}`);
  }
  assert.deepEqual(census.types, TYPES);
  assert.equal(census.dicts.length, census.dictionaryCount);
  assert.ok(census.dictionaryCount >= 9, "at least the nine derivation-bearing dictionaries");
});

test("every dictionary record is internally consistent", () => {
  for (const d of census.dicts) {
    assert.ok(d.entries > 0, `${d.code}: no entries scanned`);
    assert.ok(d.entriesWithEtymology > 0, `${d.code}: no etymology found at all`);
    assert.ok(d.entriesWithEtymology <= d.entries, `${d.code}: more etymologies than entries`);
    assert.ok(["european", "indigenous"].includes(d.family), `${d.code}: unknown family`);
    assert.ok(Math.abs(d.etymologyRate - d.entriesWithEtymology / d.entries) < 1e-4, `${d.code}: rate drift`);

    let maxType = 0;
    for (const [type, v] of Object.entries(d.byType)) {
      assert.ok(TYPES.includes(type), `${d.code}: undeclared type ${type}`);
      const summed = POSITIONS.reduce((s, p) => s + v.positions[p], 0);
      assert.equal(summed, v.entries, `${d.code}/${type}: positions do not sum to entries`);
      maxType = Math.max(maxType, v.entries);
    }
    // a type is credited once per entry, so no single type may outrun the union
    assert.ok(maxType <= d.entriesWithEtymology, `${d.code}: a type outruns entriesWithEtymology`);

    for (const m of d.markers) {
      assert.ok(TYPES.includes(m.type), `${d.code}/${m.label}: undeclared marker type`);
      assert.ok(m.entries >= 0 && m.entries <= d.entries, `${d.code}/${m.label}: impossible count`);
    }
  }
});

test("both traditions are represented and measurably different", () => {
  const families = new Set(census.dicts.map((d) => d.family));
  assert.ok(families.has("european") && families.has("indigenous"));
  // the indigenous pair states vyutpatti; no European dictionary derives that way
  for (const d of census.dicts.filter((x) => x.family === "indigenous")) {
    assert.ok((d.byType.vyutpatti?.entries ?? 0) > 0, `${d.code}: no vyutpatti formula found`);
  }
  const mw = census.dicts.find((d) => d.code === "MW");
  assert.ok((mw.byType["root-reference"]?.entries ?? 0) > 0, "MW states roots");
  assert.ok((mw.byType.vyutpatti?.entries ?? 0) === undefined || !mw.byType.vyutpatti,
    "MW is not credited with an indigenous derivation formula");
});

test("shared-lemma comparison partitions every shared lemma exactly once", () => {
  const s = census.sharedLemmas;
  assert.ok(s.lemmaCount > 0, "no shared lemmas");
  assert.deepEqual([...s.european, ...s.indigenous].sort(), [...s.dicts].sort());
  const sides = s.sides.both + s.sides.europeanOnly + s.sides.indigenousOnly + s.sides.neither;
  assert.equal(sides, s.lemmaCount, "side buckets do not partition the shared set");
  for (const code of s.dicts) {
    assert.ok(s.withEtymology[code] <= s.lemmaCount, `${code}: coverage above the shared set`);
  }
  const pairTotal = s.typePairs.reduce((n, r) => n + r.lemmas, 0);
  assert.ok(pairTotal > 0 && pairTotal <= s.lemmaCount, "type pairs exceed the shared set");
  for (const row of s.sample) {
    for (const code of s.dicts) {
      assert.ok(Array.isArray(row[code]) && row[code].length > 0,
        `${row.lemma}: sample rows must be etymologised in all four dictionaries`);
      for (const t of row[code]) assert.ok(TYPES.includes(t), `${row.lemma}/${code}: undeclared type ${t}`);
    }
  }
});

test("the site mirror matches the data-directory copy", () => {
  const mirror = JSON.parse(fs.readFileSync(path.resolve("src/data/etymology-census.json"), "utf8"));
  assert.deepEqual(mirror, census);
});
