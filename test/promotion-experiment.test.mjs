import test from "node:test";
import assert from "node:assert/strict";
import {
  classifyItiUnit,
  divSourceWindow,
  markerRunWindow,
  benBoundaryFromParts,
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

test("divSourceWindow keeps numbered top-level senses and labels supplements", () => {
  const roles = DIV_SOURCE_RECORD_ROLES["r2-drift:gam:pwg"];
  const rows = [
    { blockIds: ["21814"], markerLabel: "1", splitConfidence: "explicit", text: "— 1) gehen, sich bewegen" },
    { blockIds: ["21814"], markerLabel: "2", splitConfidence: "explicit", text: "a) mit dem acc." },
    { blockIds: ["21814"], markerLabel: "p", splitConfidence: "explicit", text: "— partic. gata" },
    { blockIds: ["21814"], markerLabel: "1", splitConfidence: "explicit", text: "1) adj. gegangen" },
    { blockIds: ["72578"], markerLabel: "1", splitConfidence: "explicit", text: "— 3) a) gacCasva" },
    { blockIds: ["21815"], markerLabel: null, splitConfidence: "lumped-proxy", text: "2. gam = kzam Erde" }
  ];
  const labeled = divSourceWindow(rows, roles, ["target-primary-series", "prefixed-or-derived-series"]);
  assert.deepEqual(labeled.map(item => item.inWindow), [true, false, false, false, false, false]);
  assert.equal(labeled[1].windowLabel, "candidate-sense-marker");
  assert.equal(labeled[2].windowLabel, "prefixed-or-derived-series");
  // numbered n="1" AFTER the first preverb block stays derived material
  assert.equal(labeled[3].windowLabel, "prefixed-or-derived-series");
  assert.equal(labeled[4].windowLabel, "same-headword-supplement");
  assert.equal(labeled[5].windowLabel, "separate-homonym");
});

test("divSourceWindow excludes unnumbered prefaces and counts dharma-style enumeration", () => {
  const roles = DIV_SOURCE_RECORD_ROLES["r2-drift:dharma:pwg"];
  const rows = [
    { blockIds: ["36241"], markerLabel: null, splitConfidence: "lumped-proxy", text: "Da/rma (von Dar) m. n." },
    { blockIds: ["36241"], markerLabel: "1", splitConfidence: "explicit", text: "1) Satzung, Ordnung" },
    { blockIds: ["36241"], markerLabel: "2", splitConfidence: "explicit", text: "a) Sitte, Recht" },
    { blockIds: ["36241"], markerLabel: "1", splitConfidence: "explicit", text: "— 11) in der Astrol." }
  ];
  const labeled = divSourceWindow(rows, roles, ["target-primary-series", "same-headword-supplement"]);
  assert.deepEqual(labeled.map(item => item.inWindow), [false, true, false, true]);
  assert.equal(labeled[0].windowLabel, "preface-or-proxy");
});

test("markerRunWindow keeps the bare root and splits derivative vs preverb runs", () => {
  const rows = [
    { splitConfidence: "lumped-proxy" },                          // preface
    { splitConfidence: "explicit", markerRunIndex: 0 },           // bare finite root
    { splitConfidence: "explicit", markerRunIndex: 2 },           // primary derivative (gamya)
    { splitConfidence: "explicit", markerRunIndex: 4 }            // preverb lexeme (adhi-gam)
  ];
  const labeled = markerRunWindow(rows, ["archive-prefix-runs", "reset-run-expansion"], null, 4);
  assert.deepEqual(labeled.map(item => item.inWindow), [false, true, false, false]);
  assert.equal(labeled[0].windowLabel, "preface-or-proxy");
  assert.equal(labeled[1].windowLabel, "bare-root-run");
  assert.equal(labeled[2].windowLabel, "primary-derivative-run");
  assert.equal(labeled[3].windowLabel, "preverb-lexeme-run");
});

test("benBoundaryFromParts locates the preverb zone one run after the cue", () => {
  const parts = [
    { markerRunIndex: 0, text: "1. To go, Man." },
    { markerRunIndex: 3, text: "gamayām āsa. -- With aDi adhi," },  // cue in run-3 tail
    { markerRunIndex: 4, text: "1. To go to, MBh." }
  ];
  assert.equal(benBoundaryFromParts(parts), 4);
  // lowercase "(with acc.)" in a gloss must not trigger a boundary
  assert.equal(benBoundaryFromParts([{ markerRunIndex: 0, text: "To go to (with acc.)" }]), Infinity);
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
