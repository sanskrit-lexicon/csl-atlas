import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { parseTsv, buildPayload, TRADITION_VOCAB } from "../scripts/build-tradition-tags.mjs";

const FIXED_AT = "2026-07-08T00:00:00.000Z";

const EDGES = [
  { dict: "bhs", canonical_text: "Mahāvastu", count: "100" },
  { dict: "bhs", canonical_text: "Rāmāyaṇa", count: "5" },
  { dict: "mw", canonical_text: "Rāmāyaṇa", count: "40" },
  { dict: "mw", canonical_text: "Ṛgveda", count: "60" }
];
const NODES = [
  { canonical_text: "Mahāvastu", total_cites: "100", n_dicts: "1", variant_forms: "" },
  { canonical_text: "Rāmāyaṇa", total_cites: "45", n_dicts: "2", variant_forms: "" },
  { canonical_text: "Ṛgveda", total_cites: "60", n_dicts: "1", variant_forms: "" }
];
const TAGS = [
  { canonical_text: "Mahāvastu", tradition: "buddhist", confidence: "high", reviewed: "no", note: "" },
  { canonical_text: "Rāmāyaṇa", tradition: "epic", confidence: "high", reviewed: "no", note: "" },
  { canonical_text: "Ṛgveda", tradition: "vedic", confidence: "medium", reviewed: "no", note: "" }
];

test("parseTsv maps header to fields", () => {
  const rows = parseTsv("canonical_text\ttradition\tconfidence\treviewed\tnote\nMahāvastu\tbuddhist\thigh\tno\tx\n");
  assert.equal(rows.length, 1);
  assert.equal(rows[0].canonical_text, "Mahāvastu");
  assert.equal(rows[0].tradition, "buddhist");
  assert.equal(rows[0].note, "x");
});

test("buildPayload derives per-dict tradition communities", () => {
  const p = buildPayload(EDGES, NODES, TAGS, FIXED_AT);
  assert.equal(p.reviewState.taggedTexts, 3);
  assert.equal(p.reviewStatus, "inferred-pending-review");
  assert.equal(p.evidenceLabel, "inferred");

  const bhs = p.perDict.find((d) => d.dict === "bhs");
  assert.equal(bhs.dominantTradition, "buddhist");
  assert.equal(bhs.taggedCites, 105);
  const bud = bhs.byTradition.find((s) => s.tradition === "buddhist");
  assert.equal(bud.cites, 100);
  assert.equal(bud.share, Number((100 / 105).toFixed(4)));

  const mw = p.perDict.find((d) => d.dict === "mw");
  assert.equal(mw.dominantTradition, "vedic"); // 60 vedic > 40 epic
  assert.equal(mw.taggedCoverage, 1); // all mw cites are to tagged texts

  // Per-dict shares each sum to 1.
  for (const d of p.perDict) {
    const s = d.byTradition.reduce((a, x) => a + x.share, 0);
    assert.ok(Math.abs(s - 1) < 0.001);
  }
});

test("buildPayload rejects a tradition outside the closed vocabulary", () => {
  const bad = [{ canonical_text: "Mahāvastu", tradition: "made-up", confidence: "high", reviewed: "no", note: "" }];
  assert.throws(() => buildPayload(EDGES, NODES, bad, FIXED_AT), /outside the closed vocabulary/);
});

test("reviewStatus rises to human-reviewed only when every row is reviewed BY A HUMAN", () => {
  const reviewedTags = TAGS.map((t) => ({ ...t, reviewed: "yes", reviewed_by: "human" }));
  const p = buildPayload(EDGES, NODES, reviewedTags, FIXED_AT);
  assert.equal(p.reviewStatus, "human-reviewed");
  assert.equal(p.evidenceLabel, "human-verified");
  assert.equal(p.reviewState.reviewed, 3);
  assert.equal(p.reviewState.humanReviewed, 3);
  assert.equal(p.reviewState.agentReviewed, 0);
});

test("a fully reviewed map with any agent-attributed row never claims human-reviewed (H1684)", () => {
  // The failure this guards: promoting agent verdicts into the bare `reviewed`
  // boolean used to flip reviewStatus to human-reviewed, asserting that a human
  // had read rows no human ever saw.
  const mixed = TAGS.map((t, i) => ({
    ...t, reviewed: "yes", reviewed_by: i === 0 ? "agent-h1684" : "human"
  }));
  const p = buildPayload(EDGES, NODES, mixed, FIXED_AT);
  assert.equal(p.reviewStatus, "agent-adjudicated-human-gated");
  assert.equal(p.evidenceLabel, "agent-adjudicated");
  assert.equal(p.reviewState.reviewed, 3);
  assert.equal(p.reviewState.agentReviewed, 1);
  assert.equal(p.reviewState.humanReviewed, 2);
});

test("a reviewed row with no provenance counts as agent-attributed, not human", () => {
  // Unattributed review is not evidence of human review — fail closed.
  const unattributed = TAGS.map((t) => ({ ...t, reviewed: "yes" }));
  const p = buildPayload(EDGES, NODES, unattributed, FIXED_AT);
  assert.equal(p.reviewStatus, "agent-adjudicated-human-gated");
  assert.equal(p.reviewState.humanReviewed, 0);
  assert.equal(p.reviewState.byReviewer.unattributed, 3);
});

test("partially reviewed stays inferred-pending-review regardless of provenance", () => {
  const partial = TAGS.map((t, i) => (i === 0 ? { ...t, reviewed: "yes", reviewed_by: "human" } : t));
  const p = buildPayload(EDGES, NODES, partial, FIXED_AT);
  assert.equal(p.reviewStatus, "inferred-pending-review");
  assert.equal(p.evidenceLabel, "inferred");
});

test("confidence tally is correct", () => {
  const p = buildPayload(EDGES, NODES, TAGS, FIXED_AT);
  assert.equal(p.reviewState.byConfidence.high, 2);
  assert.equal(p.reviewState.byConfidence.medium, 1);
  assert.equal(p.reviewState.byConfidence.low, 0);
});

test("committed packet is internally consistent", () => {
  const file = path.resolve(process.cwd(), "src", "data", "citations", "tradition_tags.json");
  assert.ok(fs.existsSync(file), "committed tradition_tags.json missing");
  const packet = JSON.parse(fs.readFileSync(file, "utf8"));
  assert.equal(packet.schemaVersion, "1.0.0");
  assert.equal(packet.evidenceLabel, "inferred");
  for (const t of packet.taggedTexts) assert.ok(TRADITION_VOCAB.includes(t.tradition), `bad tradition ${t.tradition}`);
  for (const d of packet.perDict) {
    const sum = d.byTradition.reduce((a, s) => a + s.cites, 0);
    assert.equal(sum, d.taggedCites);
    assert.ok(d.taggedCites <= d.totalInGraphCites);
  }
});
