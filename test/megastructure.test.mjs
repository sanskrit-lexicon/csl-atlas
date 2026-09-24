import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { checkSchema, expandRef, parseInventory, semanticChecks, summarize } from "../scripts/lib/megastructure.mjs";
import { INVENTORY_PATH, JSON_OUT, SCHEMA_PATH, buildPayload, loadAndCheck } from "../scripts/build-megastructure.mjs";

const schema = JSON.parse(fs.readFileSync(SCHEMA_PATH, "utf8"));
const inventory = parseInventory(fs.readFileSync(INVENTORY_PATH, "utf8"));
const clone = (value) => JSON.parse(JSON.stringify(value));

function tinyCatalogue() {
  return {
    schemaVersion: "1.0.0",
    dict: "xx",
    dictName: "Test",
    edition: { label: "First", year: null, imprint: null, evidenceLevel: "observed", evidence: "scan" },
    scanSets: [{ id: "xx-scan", kind: "other-scan", description: "d", baseUrl: "https://example.org/", inventory: null }],
    components: [
      {
        id: "xx.fm.title", sequence: 1, position: "front", componentType: "title-page", componentTypeNote: null,
        function: "identify", secondaryFunctions: [], title: { asPrinted: "T", iast: null, english: "Title" },
        languages: ["eng"], extent: { pages: 1, printedRange: null, items: null, itemsUnit: null }, decodes: [],
        scanLocus: [{ scanSet: "xx-scan", ref: "01", image: null, printedPage: null }], digitalDisposition: "not-digitized",
        transcriptions: [], parent: null, evidenceLevel: "observed", evidence: "viewed", notes: null
      }
    ],
    excludedScans: [],
    knownGaps: [],
    misfits: []
  };
}
const TINY_INVENTORY = [
  { dict: "xx", scanSet: "xx-scan", ref: "01" },
  { dict: "xx", scanSet: "xx-scan", ref: "02" }
];

test("the committed pilot catalogues pass the schema and every semantic check", () => {
  const { catalogues, errors, coverage } = loadAndCheck();
  assert.deepEqual(errors, []);
  assert.deepEqual(catalogues.map((c) => c.dict).sort(), ["mw", "skd"]);
  for (const row of coverage) assert.equal(row.covered, row.pages, `${row.dict} ${row.scanSet} fully covered`);
});

test("stop condition: every pilot component carries a scan locus, and MW records back matter", () => {
  const { catalogues } = loadAndCheck();
  for (const catalogue of catalogues) {
    for (const component of catalogue.components) assert.ok(component.scanLocus.length > 0, component.id);
  }
  const mw = catalogues.find((c) => c.dict === "mw");
  assert.ok(mw.components.some((c) => c.position === "back" && c.componentType === "supplement"));
  const skd = catalogues.find((c) => c.dict === "skd");
  assert.ok(skd.knownGaps.length > 0, "SKD records its unscanned back matter as a known gap");
});

test("the committed build output matches a fresh build", () => {
  const { catalogues, coverage } = loadAndCheck();
  const committed = JSON.parse(fs.readFileSync(JSON_OUT, "utf8"));
  const fresh = buildPayload(catalogues, coverage, { generatedAt: committed.generatedAt });
  assert.deepEqual(committed, fresh);
  assert.equal(committed.license, "CC-BY-SA-4.0");
});

test("checkSchema accepts a minimal catalogue and names each violation", () => {
  assert.deepEqual(checkSchema(schema, tinyCatalogue()), []);
  const bad = tinyCatalogue();
  delete bad.misfits;
  bad.components[0].function = "decorate";
  bad.components[0].extent.pages = 0;
  bad.components[0].surprise = true;
  bad.components[0].scanLocus = [];
  const errors = checkSchema(schema, bad).join("\n");
  assert.match(errors, /missing required "misfits"/);
  assert.match(errors, /"decorate" not in enum/);
  assert.match(errors, /must exceed 0/);
  assert.match(errors, /unexpected property "surprise"/);
  assert.match(errors, /fewer than 1 items/);
});

test("checkSchema refuses a keyword it does not implement", () => {
  const errors = checkSchema({ type: "string", format: "uri" }, "x");
  assert.match(errors.join(), /"format" is not supported/);
});

test("semanticChecks flags an uncovered page until it is excluded", () => {
  const catalogue = tinyCatalogue();
  let result = semanticChecks(catalogue, TINY_INVENTORY);
  assert.match(result.errors.join(), /no component and no exclusion: 02/);
  catalogue.excludedScans.push({ scanSet: "xx-scan", ref: "02", reason: "blank" });
  result = semanticChecks(catalogue, TINY_INVENTORY);
  assert.deepEqual(result.errors, []);
  assert.deepEqual(result.coverage, [{ scanSet: "xx-scan", pages: 2, covered: 2, excluded: 1 }]);
});

test("semanticChecks catches id, parent, sequence and 'other' mistakes", () => {
  const catalogue = tinyCatalogue();
  catalogue.excludedScans.push({ scanSet: "xx-scan", ref: "02", reason: "blank" });
  const second = clone(catalogue.components[0]);
  Object.assign(second, { id: "yy.bm.note", sequence: 1, componentType: "other", parent: "xx.fm.missing" });
  catalogue.components.push(second);
  const errors = semanticChecks(catalogue, TINY_INVENTORY).errors.join("\n");
  assert.match(errors, /id prefix "yy"/);
  assert.match(errors, /id section "bm" disagrees with position "front"/);
  assert.match(errors, /sequence 1 used twice/);
  assert.match(errors, /needs componentTypeNote/);
  assert.match(errors, /parent xx.fm.missing is not a component/);
});

test("expandRef resolves single refs and inventory-order ranges", () => {
  const rows = inventory.filter((row) => row.dict === "mw" && row.scanSet === "mw-scan-pdf");
  assert.deepEqual(expandRef("t05", rows), ["t05"]);
  assert.equal(expandRef("1308..1333", rows).length, 26);
  assert.equal(expandRef("t99", rows), null);
  assert.equal(expandRef("1333..1308", rows), null);
});

test("summarize counts components by position and function", () => {
  const summary = summarize(tinyCatalogue());
  assert.equal(summary.components, 1);
  assert.equal(summary.front, 1);
  assert.deepEqual(summary.byFunction, { identify: 1 });
});
