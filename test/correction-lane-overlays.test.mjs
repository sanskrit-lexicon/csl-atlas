import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import {
  buildSharedErrorOverlay,
  buildCorrectionFront,
  buildQaPressure
} from "../scripts/build-correction-lane-overlays.mjs";

const FIXED_AT = "2026-07-24T00:00:00.000Z";
const OUT = path.resolve(process.cwd(), "src", "data", "corrections");

test("buildSharedErrorOverlay aggregates pet→MW edges and attaches F4b", () => {
  const rows = [
    { headword: "Adya", pet_dict: "pw", in_pwgissues: "False" },
    { headword: "Ap", pet_dict: "pwg", in_pwgissues: "True" },
    { headword: "BI", pet_dict: "pwg", in_pwgissues: "False" }
  ];
  const f4b = {
    ahlborn_total: 123,
    ahlborn_shares_error: 2,
    ahlborn_shares_error_pct: 1.6,
    ahlborn_status: { mw_correct: 90, mw_absent: 31 },
    null_observed: 256,
    null_expected: 102.79,
    null_lift: 2.491,
    null_p: 1e-40,
    null_verdict: "convergence"
  };
  const p = buildSharedErrorOverlay(rows, f4b, { generatedAt: FIXED_AT });
  assert.equal(p.totals.sharedCorrectionRows, 3);
  assert.equal(p.edges.length, 2);
  const pwg = p.edges.find((e) => e.source === "PWG");
  assert.equal(pwg.sharedCorrectedHeadwords, 2);
  assert.equal(pwg.inPwgissuesBundle, 1);
  assert.equal(p.ahlbornDirectTest.sharesError, 2);
  assert.equal(p.nullModel.lift, 2.491);
  assert.equal(p.ownerRepo, "csl-atlas");
});

test("buildCorrectionFront bins month×dict×component and era-splits", () => {
  const events = [
    { dict: "mw", date: "2016-05-01", error_component: "sense" },
    { dict: "mw", date: "2016-05-12", error_component: "markup" },
    { dict: "mw", date: "2022-01-03", error_component: "sense" },
    { dict: "pw", date: "2020-07-01", error_component: "headword" },
    { dict: "pw", date: "2020-07-02", error_component: "headword" },
    { dict: "tiny", date: "2021-01-01", error_component: "sense" }
  ];
  const p = buildCorrectionFront(events, { generatedAt: FIXED_AT, topDicts: 2 });
  assert.equal(p.totals.events, 6);
  assert.equal(p.topDicts.length, 2);
  assert.ok(p.topDicts.includes("mw"));
  assert.ok(p.topDicts.includes("pw"));
  assert.ok(!p.monthly.some((r) => r.dict === "tiny"), "tiny dict excluded from strip");
  const eraMw = p.eraOverview.filter((r) => r.dict === "mw");
  assert.equal(eraMw.find((r) => r.era === "2014-2018")?.count, 2);
  assert.equal(eraMw.find((r) => r.era === "2019-2026")?.count, 1);
  assert.equal(p.dataOwnerRepo, "csl-observatory");
});

test("buildQaPressure joins lemma + nearestReal and ranks pressure", () => {
  const h5 = {
    calibrationRows: [
      { reviewId: "cal:1", lemma: "Adya", pair: "MW/PW" }
    ],
    qaCandidateRows: [
      {
        reviewId: "qa:1",
        lemma: "ghostForm",
        nearestReal: "Adya",
        pair: "MW/PW",
        sampleClass: "mw-pw-shared-doublet"
      },
      {
        reviewId: "qa:2",
        lemma: "lonely",
        nearestReal: "alsoLonely",
        pair: "MW/PWG",
        sampleClass: "mw-pwg-shared-doublet"
      }
    ]
  };
  const loci = [
    { k1: "Adya", dict: "mw", process: "human", batch_date: "2025-01-01" },
    { k1: "Adya", dict: "pw", process: "human", batch_date: "2025-06-01" },
    { k1: "Adya", dict: "lrv", process: "bulk", batch_date: "2026-01-01" },
    { k1: "other", dict: "mw", process: "human", batch_date: "2021-01-01" }
  ];
  const p = buildQaPressure(h5, loci, { generatedAt: FIXED_AT });
  assert.equal(p.totals.candidateRows, 2);
  assert.equal(p.totals.calibrationRows, 1);
  const qa1 = p.candidates.find((c) => c.reviewId === "qa:1");
  assert.equal(qa1.pressure, "high");
  assert.equal(qa1.pressureSource, "nearestReal");
  assert.equal(qa1.nearestRealHumanCorrections, 2);
  assert.equal(qa1.nearestRealSamePairHumanCorrections, 2);
  const qa2 = p.candidates.find((c) => c.reviewId === "qa:2");
  assert.equal(qa2.pressure, "none");
  const cal = p.calibration[0];
  assert.equal(cal.humanCorrections, 2);
  assert.equal(cal.pressure, "high");
});

test("committed overlay packets exist and are internally consistent", () => {
  for (const name of ["shared_error_overlay", "correction_front", "qa_pressure"]) {
    const file = path.join(OUT, `${name}.json`);
    assert.ok(fs.existsSync(file), `missing ${name}.json`);
    const packet = JSON.parse(fs.readFileSync(file, "utf8"));
    assert.equal(packet.schemaVersion, "1.0.0");
    assert.ok(packet.generatedBy.includes("build-correction-lane-overlays"));
    assert.ok(Array.isArray(packet.limitations) && packet.limitations.length >= 2);
  }

  const shared = JSON.parse(fs.readFileSync(path.join(OUT, "shared_error_overlay.json"), "utf8"));
  assert.ok(shared.edges.length >= 1);
  assert.equal(shared.ahlbornDirectTest.sharesError, 2);
  assert.ok(shared.nullModel.lift > 1);

  const front = JSON.parse(fs.readFileSync(path.join(OUT, "correction_front.json"), "utf8"));
  assert.ok(front.totals.events > 1000);
  assert.ok(front.monthly.length > 0);
  assert.ok(front.eraOverview.length > 0);
  const monthSum = front.monthly.reduce((a, r) => a + r.count, 0);
  assert.ok(monthSum > 0);
  assert.ok(front.topDicts.every((d) => typeof d === "string"));

  const qa = JSON.parse(fs.readFileSync(path.join(OUT, "qa_pressure.json"), "utf8"));
  assert.equal(qa.totals.candidateRows, qa.candidates.length);
  assert.equal(
    qa.totals.high + qa.totals.medium + qa.totals.low + qa.totals.none,
    qa.totals.candidateRows
  );
  for (const c of qa.candidates) {
    assert.ok(["none", "low", "medium", "high"].includes(c.pressure));
  }
});
