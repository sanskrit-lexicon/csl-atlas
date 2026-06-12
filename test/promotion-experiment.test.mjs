import test from "node:test";
import assert from "node:assert/strict";
import {
  classifyItiUnit,
  divSourceWindow,
  markerRunWindow,
  aeReverseWindow,
  DIV_SOURCE_RECORD_ROLES
} from "../scripts/build-r2-promotion-experiment.mjs";

test("classifyItiUnit labels authority hints as quotation units", () => {
  assert.equal(classifyItiUnit("puRyam 2 SreyaH 3 ityamaraH .", "skd"), "authority-quotation-unit");
  assert.equal(classifyItiUnit("yaTA, hitodeSe . 1 . 59 iti .", "skd"), "authority-quotation-unit");
});

test("classifyItiUnit labels short plain prose as definition units", () => {
  assert.equal(classifyItiUnit("SuBAdfzwam iti .", "skd"), "definition-iti-unit");
});

test("classifyItiUnit labels long plain prose as commentarial discussion", () => {
  const long = "DarmaH prasidDo vA syAt aprasidDo vA ".repeat(12);
  assert.equal(classifyItiUnit(long, "vcp"), "commentarial-discussion-unit");
});

test("divSourceWindow keeps target-primary rows and labels supplements", () => {
  const roles = DIV_SOURCE_RECORD_ROLES["r2-drift:gam:pwg"];
  const rows = [
    { blockIds: ["21814"], markerLabel: "1" },
    { blockIds: ["21814"], markerLabel: "p" },
    { blockIds: ["72578"], markerLabel: "1" },
    { blockIds: ["21815"], markerLabel: null }
  ];
  const labeled = divSourceWindow(rows, roles, ["target-primary-series", "prefixed-or-derived-series"]);
  assert.deepEqual(labeled.map(item => item.inWindow), [true, false, false, false]);
  assert.equal(labeled[1].windowLabel, "prefixed-or-derived-series");
  assert.equal(labeled[2].windowLabel, "same-headword-supplement");
  assert.equal(labeled[3].windowLabel, "separate-homonym");
});

test("markerRunWindow keeps only first-run explicit rows", () => {
  const rows = [
    { rawHeadword: "gam", splitConfidence: "lumped-proxy" },
    { rawHeadword: "gam", splitConfidence: "explicit", markerRunIndex: 0 },
    { rawHeadword: "gam", splitConfidence: "explicit", markerRunIndex: 2 }
  ];
  const labeled = markerRunWindow(rows, ["archive-prefix-runs", "reset-run-expansion"]);
  assert.deepEqual(labeled.map(item => item.inWindow), [false, true, false]);
  assert.equal(labeled[2].windowLabel, "reset-run-expansion");
});

test("markerRunWindow splits lookup bundles on exact headword", () => {
  const rows = [
    { rawHeadword: "rama", splitConfidence: "explicit", markerRunIndex: 0 },
    { rawHeadword: "rAma", splitConfidence: "explicit", markerRunIndex: 0 }
  ];
  const labeled = markerRunWindow(rows, ["source-record-exact-target"], "rama");
  assert.deepEqual(labeled.map(item => item.inWindow), [true, false]);
  assert.equal(labeled[1].windowLabel, "lookup-bundle-split");
});

test("aeReverseWindow promotes high band and labels the tail", () => {
  const rows = [
    { reverseMatch: { rank: "high", firstGroupIndex: 0 } },
    { reverseMatch: { rank: "high", firstGroupIndex: 2 } },
    { reverseMatch: { rank: "medium", firstGroupIndex: 4 } },
    { reverseMatch: { rank: "tail", firstGroupIndex: 12 } }
  ];
  const labeled = aeReverseWindow(rows);
  assert.deepEqual(labeled.map(item => item.inWindow), [true, true, false, false]);
  assert.equal(labeled[0].windowLabel, "direct-equivalent-candidate");
  assert.equal(labeled[1].windowLabel, "reverse-high-candidate");
  assert.equal(labeled[3].windowLabel, "reverse-tail-overmatch");
});
