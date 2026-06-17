import test from "node:test";
import assert from "node:assert/strict";
import { applyAutoTriage } from "../scripts/build-xref-source-check-packet.mjs";

test("applyAutoTriage resolves a ring-truncation target as prefix-convention", () => {
  const rows = [{ controlId: "c1", target: "a˚", reviewStatus: "needs-source-check", proposedLabels: ["prefix-convention"] }];
  applyAutoTriage(rows);
  assert.equal(rows[0].autoTriage.resolved, true);
  assert.equal(rows[0].autoTriage.proposedDecision, "prefix-convention");
  assert.equal(rows[0].autoTriage.evidence.target, "a˚");
  assert.equal(rows[0].reviewStatus, "auto-resolved");
});

test("applyAutoTriage resolves a hyphen-truncation target as prefix-convention", () => {
  const rows = [{ controlId: "c2", target: "aBi-", reviewStatus: "needs-source-check" }];
  applyAutoTriage(rows);
  assert.equal(rows[0].autoTriage.resolved, true);
  assert.equal(rows[0].reviewStatus, "auto-resolved");
});

test("applyAutoTriage leaves a plain lexical target for human source-check", () => {
  const rows = [{ sampleId: "s1", sourceLemma: "ARi", target: "aRi", reviewStatus: "needs-source-check", proposedLabels: ["lexical-shared-core"] }];
  applyAutoTriage(rows);
  assert.equal(rows[0].autoTriage.resolved, false);
  assert.equal(rows[0].reviewStatus, "needs-source-check");
});
