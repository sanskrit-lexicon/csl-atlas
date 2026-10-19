import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { cohenKappa, largestRemainder, mwGlossClauseUnits, wilson } from "../scripts/build-sense-inventory-audit.mjs";

const ROOT = process.cwd();
const JSON_PATH = path.join(ROOT, "data", "sense", "inventory_audit.json");
const CSV_PATH = path.join(ROOT, "data", "sense", "inventory_audit.csv");
const SOURCE_PATH = path.join(ROOT, "data", "sense", "inventory_audit.source.json");
const TSV_PATH = path.join(ROOT, "data", "sense", "inventory_audit_sample.tsv");
const audit = JSON.parse(fs.readFileSync(JSON_PATH, "utf8"));
const source = JSON.parse(fs.readFileSync(SOURCE_PATH, "utf8"));

test("H7098 sample is 500 unique lemmas in a 200/300 stratified design", () => {
  assert.equal(audit.sampleDesign.target, 500);
  assert.equal(audit.sampleDesign.achieved, 500);
  assert.equal(audit.sampleDesign.strata.disparity, 200);
  assert.equal(audit.sampleDesign.strata.coverage, 300);
  assert.equal(audit.rows.length, 500);
  assert.equal(new Set(audit.rows.map(row => row.k1)).size, 500);
  assert.equal(audit.rows.filter(row => row.stratum === "disparity").length, 200);
  assert.equal(audit.rows.filter(row => row.stratum === "coverage").length, 300);
});

test("H7098 reports a kappa or an honest n/CI, never a missing metric", () => {
  const dk = audit.doubleKey;
  assert.equal(dk.status, "automated-double-key");
  assert.ok(dk.n > 0);
  assert.ok(dk.kappa >= -1 && dk.kappa <= 1);
  assert.ok(dk.kappaBootstrapCi95.lo <= dk.kappa);
  assert.ok(dk.kappaBootstrapCi95.hi >= dk.kappa);
  assert.match(dk.note, /not human inter-annotator/i);
});

test("H7098 core sense dictionaries are the four validated adapters", () => {
  assert.deepEqual(audit.coreSenseDicts, ["mw", "ap", "pwg", "pw"]);
  for (const code of audit.coreSenseDicts) {
    assert.ok(audit.senseDictionaries[code], `missing ${code}`);
    assert.equal(audit.senseDictionaries[code].scope, "core");
  }
});

test("H7098 disagreement rate is recomputable from the published rows", () => {
  const core = audit.coreSenseDicts;
  const senseRows = audit.rows.filter(row => row.stratum === "disparity");
  const eligible = senseRows.filter(row => core.filter(code => row.senseUnits[code]).length >= 2);
  const differing = eligible.filter(row => {
    const values = core.map(code => row.senseUnits[code]?.units).filter(v => v != null);
    return new Set(values).size > 1;
  });
  assert.equal(eligible.length, audit.disagreement.lemmasWithAtLeastTwoCoreSenseDicts);
  assert.equal(differing.length, audit.disagreement.lemmasWithAnyCountDifference);
  assert.equal(Number((differing.length / eligible.length).toFixed(4)), audit.disagreement.rate);
});

test("H7098 MW double-key rows carry a source line", () => {
  const keyed = audit.rows.filter(row => row.mwDoubleKey);
  assert.ok(keyed.length > 0);
  for (const row of keyed) {
    assert.ok(row.mwDoubleKey.href, `missing MW source for ${row.k1}`);
    assert.ok(row.mwDoubleKey.line > 0);
    assert.ok(row.mwDoubleKey.adapterUnits >= 1);
    assert.ok(row.mwDoubleKey.boundaryUnits >= 1);
  }
});

test("H7098 MWSA vocabulary is complete and external MWSA is honestly unavailable", () => {
  assert.deepEqual(audit.mwsRelationAlignment.vocabulary, ["=", "superset", "subset", "related"]);
  assert.equal(audit.mwsRelationAlignment.status, "partial");
  assert.equal(audit.externalInventories.elexisMwsa.status, "unavailable");
  assert.match(audit.externalInventories.isclsWsd.citation, /2026\.iscls-1\.2/);
  assert.match(audit.externalInventories.isclsMwSenseInventory.citation, /2026\.iscls-1\.3/);
});

test("H7098 sample TSV carries two keys and an explicit unadjudicated label", () => {
  const lines = fs.readFileSync(TSV_PATH, "utf8").trim().split(/\r?\n/);
  assert.equal(lines.length, 501);
  assert.match(lines[0], /^lemma\tstratum\tn_core_dicts\tkey_a_mw_adapter_units/);
  assert.equal(audit.humanGold.status, "blocked");
  const rows = lines.slice(1).map(line => line.split("\t"));
  const keyed = rows.filter(cells => cells[7] !== "no-mw-row");
  assert.ok(keyed.length > 0);
  for (const cells of keyed) {
    assert.equal(cells.length, 9);
    assert.equal(cells[7], "unadjudicated-automated");
    assert.ok(cells[8].includes("csl-orig"));
  }
});

test("H7098 reconciliation names the B3 boundary", () => {
  assert.match(audit.reconciliation.h5950.lane, /B3/);
  assert.match(audit.reconciliation.h6843.lane, /B3/);
  assert.match(audit.reconciliation.boundary, /No WSD model/);
});

test("H7098 CSV and source hashes pin the published artifacts", () => {
  const lines = fs.readFileSync(CSV_PATH, "utf8").trim().split(/\r?\n/);
  assert.equal(lines.length, 501);
  assert.match(lines[0], /^lemma,stratum,n_core_dicts/);
  const byPath = new Map(source.outputs.map(row => [row.path, row.sha256]));
  for (const [relative, file] of [
    ["data/sense/inventory_audit.json", JSON_PATH],
    ["data/sense/inventory_audit.csv", CSV_PATH],
    ["data/sense/inventory_audit_sample.tsv", TSV_PATH]
  ]) {
    const actual = crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
    assert.equal(byPath.get(relative), actual, `stale source hash for ${relative}`);
  }
});

test("cohenKappa and wilson agree with hand-computed fixtures", () => {
  const kappa = cohenKappa([[true, true], [true, true], [false, false], [false, false]]);
  assert.equal(kappa.kappa, 1);
  assert.equal(kappa.po, 1);
  const zero = cohenKappa([[true, false], [false, true]]);
  assert.equal(zero.kappa, -1);
  const ci = wilson(1, 2);
  assert.ok(ci.lo < ci.p && ci.p < ci.hi);
});

test("mwGlossClauseUnits and largestRemainder are deterministic", () => {
  assert.equal(mwGlossClauseUnits("one gloss"), 1);
  assert.equal(mwGlossClauseUnits("one; two; three"), 2);
  assert.deepEqual(largestRemainder({ a: 1, b: 1 }, 3), { a: 2, b: 1 });
});
