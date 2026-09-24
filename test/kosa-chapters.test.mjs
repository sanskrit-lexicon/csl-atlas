// Tests for the kośa-chapters packet (H5329): cross-artifact reconciliation,
// determinism, and mutations that prove the validator can fail.
// Run: node --test test/kosa-chapters.test.mjs   (wired into `npm test`)

import test from "node:test";
import assert from "node:assert/strict";
import { buildPayload, loadArtifacts } from "../scripts/build-kosa-chapters.mjs";
import { validatePacket } from "../scripts/validate-kosa-chapters.mjs";

const FIXED_TS = "2026-09-24T00:00:00.000Z";
let artifacts;
let packet;

test("committed inputs build a packet that passes the validator", () => {
  artifacts = loadArtifacts();
  packet = buildPayload(artifacts, { generatedAt: FIXED_TS });
  validatePacket(packet);
});

test("cross-artifact reconciliation pins (record_count ↔ instance totals)", () => {
  assert.equal(packet.koshas.ABCH.totals.verseGroups, packet.koshas.ABCH.parseRules.recordCount);
  assert.equal(packet.koshas.ABCH.totals.verseGroups, 1965, "ABCH verse-groups moved — re-baseline this test deliberately");
  assert.equal(packet.koshas.ARMH.totals.members, packet.koshas.ARMH.parseRules.recordCount);
  assert.equal(packet.koshas.ARMH.totals.members, 7907, "ARMH member count moved — re-baseline deliberately");
  assert.equal(packet.koshas.AMAR.totals.verseGroups, 2359, "AMAR verse-groups moved — re-baseline deliberately");
  assert.equal(packet.koshas.AMAR.parseRules, null);
});

test("ARMH honesty panel data: absent devices present, grouped measures absent", () => {
  const absent = packet.koshas.ARMH.devices.filter((d) => d.evidence === "absent").map((d) => d.device);
  assert.ok(absent.includes("varga"), "ARMH varga must be evidence:absent");
  assert.ok(absent.includes("synonym-set"), "ARMH synonym-set must be evidence:absent");
  assert.equal(packet.koshas.ARMH.genderTags, null);
  assert.equal(packet.koshas.ARMH.numbering, null);
});

test("comparison table: 13 rows, no empty cells, values trace to artifacts", () => {
  assert.equal(packet.comparison.rows.length, 13);
  for (const row of packet.comparison.rows) {
    for (const code of ["AMAR", "ABCH", "ARMH"]) {
      assert.ok(typeof row[code] === "string" && row[code].length > 0, `empty cell ${row.aspect}/${code}`);
    }
  }
  const vg = packet.comparison.rows.find((r) => r.aspect.startsWith("Verse-groups"));
  assert.ok(vg.AMAR.includes("2,359"), `AMAR verse-groups cell should carry 2,359, got: ${vg.AMAR}`);
});

test("determinism: two builds with a fixed timestamp are deep-equal", () => {
  const again = buildPayload(artifacts, { generatedAt: FIXED_TS });
  assert.deepEqual(again, packet);
});

test("mutation: tampered division count is rejected", () => {
  const bad = structuredClone(packet);
  bad.koshas.ABCH.divisions[0].vargas[0].counts.members += 1;
  assert.throws(() => validatePacket(bad), /totals\.members/);
});

test("mutation: tampered parse-rules record count breaks reconciliation", () => {
  const bad = structuredClone(packet);
  bad.koshas.ARMH.parseRules.recordCount += 1;
  assert.throws(() => validatePacket(bad), /record_count/);
});

test("mutation: truncated or hollowed comparison table is rejected", () => {
  const short = structuredClone(packet);
  short.comparison.rows = short.comparison.rows.slice(0, 9);
  assert.throws(() => validatePacket(short), /comparison has only/);
  const hollow = structuredClone(packet);
  hollow.comparison.rows[3].ARMH = "";
  assert.throws(() => validatePacket(hollow), /empty ARMH cell/);
});

test("mutation: fabricated ARMH gender measure is rejected (model honesty)", () => {
  const bad = structuredClone(packet);
  bad.koshas.ARMH.genderTags = { distinctTags: 3, top: { puM: 10 } };
  assert.throws(() => validatePacket(bad), /grouped-model measures|must not carry/);
});
