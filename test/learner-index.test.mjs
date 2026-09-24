// Tests for the learner reading-layer v1 join (H5318).
//
// Synthetic fixtures only — no sibling VisualDCS/WhitneyRoots checkouts and no
// gitignored build output, so the suite runs green in CI (npm test → node --test).
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import {
  ABSENCE_CODES, SCHEMA_VERSION, SURVIVAL_THRESHOLD, VDCS_PIN,
  assignTier, parseCsv, rankSenses, readPinnedPayload,
  resolveParadigm, sha256LfCanonical, survivalCardField, whitneyCardField
} from "../scripts/lib/learner-join.mjs";
import { validateLearnerIndex } from "../scripts/validate-learner-index.mjs";

function basePayload(overrides = {}) {
  return {
    schemaVersion: SCHEMA_VERSION,
    claim: "Frequency-graded reader card.",
    survivalThreshold: SURVIVAL_THRESHOLD,
    survivalCaveat: "Per-sense survival only; the clean within-edge test is NOT significant (z = 1.80, p = 0.072) — no population claim is made.",
    absenceCodes: { ...ABSENCE_CODES },
    absenceNotes: Object.fromEntries(Object.values(ABSENCE_CODES).map(c => [c, "note"])),
    visualDcs: { releaseId: VDCS_PIN.releaseId, contractVersion: VDCS_PIN.contractVersion },
    counts: { recordCount: 0, withFrequency: 0, byBand: {}, tiers: { A: 0, B: 0, C: 0, D: 0 }, coverage: {
      frequency: 0, nominalParadigm: 0, verbParadigm: 0, paradigmTotal: 0,
      whitneyRoot: 0, withGana: 0, rootHomonyms: 0, survival: 0,
      homonymWarning: 0, paradigmAmbiguous: 0, allFour: 0
    } },
    entries: [],
    ...overrides
  };
}

function fullCounts(entries) {
  // recompute counts the way the builder does, so tier fixtures validate cleanly
  const tiers = { A: 0, B: 0, C: 0, D: 0 };
  const coverage = {
    frequency: 0, nominalParadigm: 0, verbParadigm: 0, paradigmTotal: 0,
    whitneyRoot: 0, withGana: 0, rootHomonyms: 0, survival: 0,
    homonymWarning: 0, paradigmAmbiguous: 0, allFour: 0
  };
  for (const e of entries) {
    tiers[e.tier] += 1;
    if (e.fb > 0) coverage.frequency += 1;
    if (e.p) {
      coverage.paradigmTotal += 1;
      const kinds = new Set([e.p.k, ...(e.p.alt ?? []).map(a => a.k)]);
      if (kinds.has("nominal")) coverage.nominalParadigm += 1;
      if (kinds.has("verb")) coverage.verbParadigm += 1;
      if (e.p.alt) coverage.paradigmAmbiguous += 1;
    }
    if (e.w) {
      coverage.whitneyRoot += 1;
      if (e.w.length > 1) coverage.rootHomonyms += 1;
      if (e.w.some(r => r.gana != null)) coverage.withGana += 1;
    }
    if (e.s) coverage.survival += 1;
    if (e.hm) coverage.homonymWarning += 1;
    if (e.p && e.w && e.s) coverage.allFour += 1;
  }
  return { tiers, coverage };
}

function countedPayload(entries) {
  const { tiers, coverage } = fullCounts(entries);
  return basePayload({ entries, counts: { recordCount: entries.length, withFrequency: 0, byBand: {}, tiers, coverage } });
}

test("rankSenses orders survived desc, overlap desc, position asc", () => {
  const ranked = rankSenses([
    { survived: true, overlap: 0.2, position: 3 },
    { survived: true, overlap: 0.9, position: 5 },
    { survived: false, overlap: 0.99, position: 1 },
    { survived: true, overlap: 0.9, position: 2 },
    { survived: false, overlap: 0.1, position: 0 }
  ]);
  assert.deepEqual(ranked.map(r => r.position), [2, 5, 3, 1, 0]);
});

test("resolveParadigm picks the highest-tokens contract across nominal and verb files and discloses the loser", () => {
  const nomById = new Map([["deva", [{ id: "86559", tokens: 100, cellsAttested: 20 }, { id: "42", tokens: 5, cellsAttested: 2 }]]]);
  const verbRoots = new Map([["deva", { id: "dev", tokens: 500, cells: 8 }]]);
  const p = resolveParadigm(nomById, verbRoots, "deva");
  assert.equal(p.k, "verb");
  assert.equal(p.id, "dev");
  assert.equal(p.tokens, 500);
  assert.deepEqual(p.alt, [{ k: "nominal", id: "86559" }, { k: "nominal", id: "42" }]);
  // no cross-file ambiguity → no alt key
  const solo = resolveParadigm(new Map([["agni", [{ id: "7", tokens: 10, cellsAttested: 3 }]]]), new Map(), "agni");
  assert.equal(solo.alt, undefined);
  assert.equal(resolveParadigm(new Map(), new Map(), "zzz"), null);
});

test("assignTier follows the spec §8 matrix", () => {
  assert.equal(assignTier({ hasSenses: true, hasParadigm: false, hasRoot: false }), "A");
  assert.equal(assignTier({ hasSenses: false, hasParadigm: true, hasRoot: true }), "B");
  assert.equal(assignTier({ hasSenses: false, hasParadigm: true, hasRoot: false }), "C");
  assert.equal(assignTier({ hasSenses: false, hasParadigm: false, hasRoot: true }), "C");
  assert.equal(assignTier({ hasSenses: false, hasParadigm: false, hasRoot: false }), "D");
});

test("whitneyCardField shows ALL homonym roots and never invents a gaṇa", () => {
  const ganaByNo = new Map([["501", { gana: "I", certainty: "high" }]]);
  const field = whitneyCardField([
    { no: "501", iast: "akṣ", hom: "1", cls: "", clsUnc: "" },
    { no: "502", iast: "akṣ", hom: "2", cls: "", clsUnc: "" }
  ], ganaByNo);
  assert.equal(field.length, 2);
  assert.equal(field[0].gana, "I");
  assert.equal(field[1].gana, undefined); // absent stays absent — never inferred
});

test("survivalCardField carries edge and survives/overlap/position per row", () => {
  const field = survivalCardField([{ lemma: "Aroha", edge: "wil→shs", cited: false, survived: true, overlap: 0.5, position: 0 }]);
  assert.deepEqual(field, [{ t: null, sv: true, ov: 0.5, e: "wil→shs", pos: 0, ci: false }]);
});

test("parseCsv handles quoted commas", () => {
  const rows = parseCsv('a,"b,c",d\n1,2,3');
  assert.deepEqual(rows[0], ["a", "b,c", "d"]);
  assert.deepEqual(rows[1], ["1", "2", "3"]);
});

test("sha256LfCanonical is stable over CRLF and matches a known digest", () => {
  const h = sha256LfCanonical(Buffer.from("x\r\ny\n"));
  assert.equal(h, sha256LfCanonical(Buffer.from("x\ny\n")));
  assert.equal(h, "09834d488008f5f1ef589a2d7cedc52425bee9dd23b2212e4c1d673c5cbb54e4");
  assert.match(sha256LfCanonical(Buffer.from("")), /^[0-9a-f]{64}$/);
});

test("readPinnedPayload fails closed on a digest mismatch (spec §9.2)", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "learner-join-"));
  const abs = path.join(dir, "visual", "contracts", "v1");
  fs.mkdirSync(abs, { recursive: true });
  const rel = "visual/contracts/v1/manifest.json";
  const originalPin = VDCS_PIN.payloads[rel]; // restored in finally — tests share the pin table
  fs.writeFileSync(path.join(abs, "manifest.json"), JSON.stringify({ contractVersion: "1.0.0" }));
  try {
    assert.throws(() => readPinnedPayload(dir, rel), /digest mismatch/);
    // payload carries an unknown future version → reject, keep the previous pin (spec §9.3)
    const exact = Buffer.from(JSON.stringify({ contractVersion: "9.9.9" }) + "\n");
    VDCS_PIN.payloads[rel] = sha256LfCanonical(exact);
    fs.writeFileSync(path.join(abs, "manifest.json"), exact);
    assert.throws(() => readPinnedPayload(dir, rel), /unknown contractVersion/);
  } finally {
    VDCS_PIN.payloads[rel] = originalPin;
  }
});

function cardEntry(overrides = {}) {
  return {
    l: "Aroha", fb: 5, at: true, c: 7, gr: 5, d: ["mw"], g: "m", src: ["mw", 1],
    p: { k: "nominal", id: "1", cells: 3, tokens: 9 },
    w: [{ no: "1", iast: "Aroha", hom: "1", gana: "I", certainty: "high" }],
    s: [{ t: "to ascend", sv: true, ov: 0.5, e: "wil→shs", pos: 0, ci: false }],
    tier: "A",
    ...overrides
  };
}

/** A payload shaped exactly like the spec §8 population (28 A / 541 B /
 *  16,508 C / 35,857 D = 52,934 cards), so the spec-tolerance tier check
 *  passes and population-level checks (coverage parity, allFour headline)
 *  can be exercised for real. */
function specShapedPayload(mutate = () => {}) {
  const entries = [];
  const aCard = i => cardEntry({ l: `a${i}`, w: undefined, tier: undefined });   // senses + paradigm, no root
  const bCard = i => cardEntry({ l: `b${i}`, s: undefined, tier: undefined });    // paradigm + root
  const cCard = i => cardEntry({ l: `c${i}`, s: undefined, w: undefined, tier: undefined }); // paradigm only
  const dCard = i => cardEntry({ l: `d${i}`, p: undefined, w: undefined, s: undefined, tier: undefined, hm: { mx: 2 } });
  entries.push(...Array.from({ length: 28 }, (_, i) => aCard(i)));
  entries.push(...Array.from({ length: 541 }, (_, i) => bCard(i)));
  entries.push(...Array.from({ length: 16508 }, (_, i) => cCard(i)));
  entries.push(...Array.from({ length: 35857 }, (_, i) => dCard(i)));
  for (const e of entries) e.tier = assignTier({ hasSenses: Boolean(e.s), hasParadigm: Boolean(e.p), hasRoot: Boolean(e.w) });
  mutate(entries);
  const { tiers, coverage } = fullCounts(entries);
  return basePayload({
    entries,
    counts: { recordCount: entries.length, withFrequency: 52934, byBand: { "5": 52934 }, tiers, coverage }
  });
}

test("validateLearnerIndex accepts a spec-shaped payload", () => {
  const { tiers, coverage } = validateLearnerIndex(specShapedPayload());
  assert.equal(tiers.A, 28);
  assert.equal(tiers.B, 541);
  assert.equal(coverage.paradigmTotal, 28 + 541 + 16508);
  assert.equal(coverage.survival, 28);
  assert.equal(coverage.rootHomonyms, 0);
  assert.equal(coverage.withGana, 541); // only the B cards carry a root, all with gana
});

test("validator fails when a survival rank lacks its edge (spec §11.2)", () => {
  const entry = cardEntry();
  entry.s = [{ t: "gloss", sv: true, ov: 0.5, e: "", pos: 0, ci: false }];
  const payload = countedPayload([entry]);
  assert.throws(() => validateLearnerIndex(payload), /survival rank without edge/);
});

test("validator fails when the pinned threshold drifts", () => {
  const payload = countedPayload([cardEntry()]);
  payload.survivalThreshold = 0.2;
  assert.throws(() => validateLearnerIndex(payload), /threshold is contract surface/);
});

test("validator fails on tier/field inconsistency", () => {
  const entry = cardEntry();
  entry.tier = "D"; // fields say A
  const payload = countedPayload([entry]);
  assert.throws(() => validateLearnerIndex(payload), /tier .* inconsistent/);
});

test("validator fails when counts.coverage disagrees with the entries", () => {
  const payload = specShapedPayload();
  payload.counts.coverage.homonymWarning += 99; // lie against the recounted truth
  assert.throws(() => validateLearnerIndex(payload), /counts\.coverage\.homonymWarning/);
});

test("validator fails when absenceCodes leave the closed vocabulary", () => {
  const payload = countedPayload([cardEntry()]);
  payload.absenceCodes.senses = "we-felt-like-it";
  assert.throws(() => validateLearnerIndex(payload), /closed vocabulary/);
});

test("validator fails when the VisualDCS pin is missing or foreign", () => {
  const payload = countedPayload([cardEntry()]);
  payload.visualDcs = { releaseId: "some-other-release" };
  assert.throws(() => validateLearnerIndex(payload), /pin missing or not/);
});

test("validator enforces the spec §8 headline: no card carries all four layers", () => {
  const payload = specShapedPayload(entries => {
    entries[0].w = [{ no: "1", iast: "a1", hom: "1", gana: "I", certainty: "high" }]; // A card gains a root → all four layers
    entries[0].tier = "A";
  });
  assert.throws(() => validateLearnerIndex(payload), /allFour .* ≠ 0/);
});
