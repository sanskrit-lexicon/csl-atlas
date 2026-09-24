// Validate the learner reading-layer v1 dataset (docs/LEARNER_LAYER_V1_SPEC.md §11.2).
//
// Read-only over the committed src/data/learner/learner-index.json. Asserts:
//   1. the §8 card-completeness tier counts hold within tolerance, and
//   2. no card claims a survival rank without its edge + the pinned threshold
//      ("a survival claim without its edge and threshold is a defect", §9.4),
// plus the join-contract invariants: closed absence vocabulary, tier/field
// consistency, coverage counts recomputed from the entries, the VisualDCS pin
// recorded, and the honest-null survival caveat present (no population claim).
//
// Usage: npm run validate-learner-index

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { ABSENCE_CODES, SCHEMA_VERSION, SURVIVAL_THRESHOLD, VDCS_PIN } from "./lib/learner-join.mjs";

const PAYLOAD_PATH = path.resolve("src", "data", "learner", "learner-index.json");

// Spec §8 measured tiers (24-09-2026) — the baseline the validator pins.
const SPEC_TIERS = { A: 28, B: 541, C: 16508, D: 35857 };

function toleranceFor(tier) {
  // Small tiers (A) get an absolute slack; large tiers 5% relative — inputs are
  // consumed at pinned releases, so drift should be nil, but a refreshed
  // sibling must not silently redefine the card population.
  return tier === "A" ? 4 : Math.max(5, Math.round(SPEC_TIERS[tier] * 0.05));
}

/** Pure validation core — exported for tests. Throws on the first defect with
 *  a named message; returns the recomputed counts on success. */
export function validateLearnerIndex(payload) {
  if (payload.schemaVersion !== SCHEMA_VERSION) {
    throw new Error(`schemaVersion ${payload.schemaVersion} ≠ ${SCHEMA_VERSION}`);
  }
  if (payload.entries.length !== payload.counts?.recordCount) {
    throw new Error(`recordCount ${payload.counts?.recordCount} ≠ entries ${payload.entries.length}`);
  }
  if (payload.survivalThreshold !== SURVIVAL_THRESHOLD) {
    throw new Error(`survivalThreshold ${payload.survivalThreshold} ≠ pinned ${SURVIVAL_THRESHOLD} — threshold is contract surface`);
  }
  if (!payload.survivalCaveat || !/not significant|NOT significant/.test(payload.survivalCaveat)) {
    throw new Error("survivalCaveat missing or does not carry the honest null (within-edge test not significant)");
  }
  // The negated quotation inside survivalCaveat is fine; the CLAIM itself may not.
  if (/survive more often|survive better|more likely to survive/i.test(String(payload.claim))) {
    throw new Error("population survival claim detected in the dataset claim — forbidden by spec §6 (edge-concentrated effect, honest null)");
  }
  if (JSON.stringify(Object.keys(payload.absenceCodes ?? {}).sort())
      !== JSON.stringify(Object.keys(ABSENCE_CODES).sort())
      || Object.values(payload.absenceCodes ?? {}).some(v => !Object.values(ABSENCE_CODES).includes(v))) {
    throw new Error("absenceCodes do not match the closed vocabulary of spec §9.1");
  }
  if (!payload.visualDcs?.releaseId || payload.visualDcs.releaseId !== VDCS_PIN.releaseId) {
    throw new Error(`visualDcs pin missing or not ${VDCS_PIN.releaseId} — paradigm provenance unrecorded (§11.1)`);
  }

  const tiers = { A: 0, B: 0, C: 0, D: 0 };
  const coverage = {
    frequency: 0, nominalParadigm: 0, verbParadigm: 0, paradigmTotal: 0,
    whitneyRoot: 0, withGana: 0, rootHomonyms: 0, survival: 0,
    homonymWarning: 0, paradigmAmbiguous: 0, allFour: 0
  };
  for (const e of payload.entries) {
    if (!(e.tier in tiers)) throw new Error(`${e.l}: bad tier ${e.tier}`);
    const hasSenses = Array.isArray(e.s) && e.s.length > 0;
    const hasParadigm = Boolean(e.p);
    const hasRoot = Array.isArray(e.w) && e.w.length > 0;
    const expectedTier = hasSenses ? "A" : (hasParadigm && hasRoot) ? "B" : (hasParadigm || hasRoot) ? "C" : "D";
    if (e.tier !== expectedTier) throw new Error(`${e.l}: tier ${e.tier} inconsistent with its fields (expected ${expectedTier})`);
    tiers[e.tier] += 1;
    if (e.fb > 0) coverage.frequency += 1;
    if (e.p) {
      coverage.paradigmTotal += 1;
      if (e.p.k !== "nominal" && e.p.k !== "verb") throw new Error(`${e.l}: bad paradigm kind ${e.p.k}`);
      // per-file basis, recomputable from the payload: resolved kind + disclosed alternatives
      const kinds = new Set([e.p.k, ...(e.p.alt ?? []).map(a => a.k)]);
      if (kinds.has("nominal")) coverage.nominalParadigm += 1;
      if (kinds.has("verb")) coverage.verbParadigm += 1;
      if (e.p.alt) coverage.paradigmAmbiguous += 1;
    }
    if (hasRoot) {
      coverage.whitneyRoot += 1;
      if (e.w.length > 1) coverage.rootHomonyms += 1;
      if (e.w.some(r => r.gana != null)) coverage.withGana += 1;
    }
    if (hasSenses) {
      coverage.survival += 1;
      for (const s of e.s) {
        if (typeof s.e !== "string" || !s.e.includes("→")) {
          throw new Error(`${e.l}: survival rank without edge — a defect by spec §9.4`);
        }
        if (typeof s.ov !== "number" || typeof s.sv !== "boolean" || !Number.isInteger(s.pos)) {
          throw new Error(`${e.l}: survival rank missing overlap/survived/position triple fields`);
        }
      }
    }
    if (e.hm) coverage.homonymWarning += 1;
    if (hasParadigm && hasRoot && hasSenses) coverage.allFour += 1;
  }

  for (const tier of ["A", "B", "C", "D"]) {
    const tol = toleranceFor(tier);
    if (Math.abs(tiers[tier] - SPEC_TIERS[tier]) > tol) {
      throw new Error(`tier ${tier}: ${tiers[tier]} vs spec ${SPEC_TIERS[tier]} (±${tol}) — card population drifted beyond tolerance; re-measure against the spec before re-pinning`);
    }
  }
  for (const [k, v] of Object.entries(coverage)) {
    if (payload.counts?.coverage?.[k] !== v) {
      throw new Error(`counts.coverage.${k}: payload ${payload.counts?.coverage?.[k]} ≠ recomputed ${v}`);
    }
  }
  // The spec's headline, still true: no card carries every layer (§8).
  if (coverage.allFour !== 0) {
    throw new Error(`allFour ${coverage.allFour} ≠ 0 — the spec's headline (§8) changed; update the spec and the validator together, never one alone`);
  }
  return { tiers, coverage };
}

function main() {
  if (!fs.existsSync(PAYLOAD_PATH)) {
    console.error(`validate-learner-index: ${PAYLOAD_PATH} not found — run npm run build-learner-index first (needs the sibling VisualDCS/WhitneyRoots checkouts).`);
    process.exit(2);
  }
  const payload = JSON.parse(fs.readFileSync(PAYLOAD_PATH, "utf8"));
  const { tiers, coverage } = validateLearnerIndex(payload);
  console.log(`validate-learner-index: PASS (${payload.entries.length} cards; schema ${payload.schemaVersion}; pin ${payload.visualDcs.releaseId})`);
  console.log(`  tiers: A ${tiers.A} / B ${tiers.B} / C ${tiers.C} / D ${tiers.D} (spec ±tolerance)`);
  console.log(`  coverage: paradigm ${coverage.paradigmTotal}, root ${coverage.whitneyRoot} (gaṇa ${coverage.withGana}), survival ${coverage.survival}, all-four ${coverage.allFour}`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();
