// Learner reading layer v1 — the join library.
//
// Implements the join contract of docs/LEARNER_LAYER_V1_SPEC.md §§4–9 on top of
// the v0 index (scripts/build-learner-index.mjs):
//   one normalised SLP1 lemma key, four joins, three of them via slp1ToIast()
//   from src/lib/lookup-normalize.js (the repo's single normaliser — never a
//   hand-rolled second copy), VisualDCS payload pins verified fail-closed,
//   Whitney roots shown-all-never-picked, and the P2 survival-ranked sense
//   export rendered only as its triple + provenance.
//
// All loaders take explicit roots so tests can point them at fixtures and the
// builder at the standard sibling checkouts (VDCS_REPO / WHITNEY_REPO env,
// same convention as scripts/measure-learner-layer-coverage.mjs).

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { slp1ToIast } from "../../src/lib/lookup-normalize.js";

export const SCHEMA_VERSION = "2.0.0";

// Pin rule (spec §4): I4–I6 are consumed at the envelope's releaseId. Digests
// are the lf-canonical sha256 values recorded in
// VisualDCS/visual/contracts/envelopes/learner-contracts-v1-2026-08-09.envelope.json.
// A VisualDCS release bump is a deliberate, reviewed change: mismatch → build
// fails (spec §9.2), unknown contractVersion → reject (spec §9.3).
export const VDCS_PIN = {
  releaseId: "vdcs-learner-v1-20260809",
  contractVersion: "1.0.0",
  commit: "6d19eed11a75076c3639cfb2f9e6f5ff9c6648cf",
  envelope: "visual/contracts/envelopes/learner-contracts-v1-2026-08-09.envelope.json",
  payloads: {
    "visual/contracts/v1/manifest.json": "2782ef35c784c8ebc0e523fa8532f2ef4470736d8f8f87b625ac8fee1d6a3eeb",
    "visual/contracts/v1/nominal-trainer.json": "13b5a16f5b45e886744f56f3464e8122730d60e1a677323f5b67024684de6663",
    "visual/contracts/v1/verb-trainer.json": "5276b7d04ee409c58c8fe7426b26efdabc2cbc1d3d4d05082f5ed1d593f2d4f6"
  }
};

// Survival threshold: max gloss-word Jaccard ≥ 0.15, pinned in
// scripts/build-r2-h2h3.mjs and swept 0.10–0.25 in the paper's sensitivity grid.
export const SURVIVAL_THRESHOLD = 0.15;

// Closed absence vocabulary (spec §9.1). Rendering an empty slot without its
// reason would make the most common card a silent lie (spec §8).
export const ABSENCE_CODES = {
  frequency: "not-in-dcs",
  paradigm: "no-paradigm-contract",
  root: "not-a-root",
  senses: "outside-survival-panel",
  homonyms: "homonym-payload-truncated"
};

// Spec §6: rank survived desc, overlap desc, position asc. Ties break on
// position — never on gloss length (correlates with the parser, not importance).
export function rankSenses(rows) {
  return [...rows].sort((a, b) =>
    (Number(b.survived) - Number(a.survived))
    || (b.overlap - a.overlap)
    || (a.position - b.position));
}

// Spec §7.3: resolve contract-ID collisions to the highest-`tokens` candidate
// and disclose the alternatives; the stable ID on the card is the resolved one
// so a later re-resolution is visible as an ID change. Candidates span BOTH
// VisualDCS contract files: a lemma string may be attested both as a nominal
// lemma and as a verb root, and the same corpus-tokens rule picks between
// them as within one file.
export function resolveParadigm(nomById, verbRoots, iast) {
  const candidates = [];
  for (const c of nomById.get(iast) ?? []) {
    candidates.push({ k: "nominal", id: c.id, tokens: c.tokens, cells: c.cellsAttested });
  }
  const root = verbRoots.get(iast);
  if (root) candidates.push({ k: "verb", id: root.id, tokens: root.tokens, cells: root.cells });
  if (!candidates.length) return null;
  const ranked = [...candidates].sort((a, b) => b.tokens - a.tokens || a.id.localeCompare(b.id));
  const best = ranked[0];
  return {
    k: best.k,
    id: best.id,
    cells: best.cells,
    tokens: best.tokens,
    ...(ranked.length > 1 ? { alt: ranked.slice(1).map(c => ({ k: c.k, id: c.id })) } : {})
  };
}

// Spec §8 tiers: A = survival senses present; B = paradigm AND Whitney root;
// C = paradigm OR root; D = neither (frequency + dictionaries only).
export function assignTier({ hasSenses, hasParadigm, hasRoot }) {
  if (hasSenses) return "A";
  if (hasParadigm && hasRoot) return "B";
  if (hasParadigm || hasRoot) return "C";
  return "D";
}

/** lf-canonical sha256 (CRLF normalised; every pinned blob is LF-only, so this
 *  equals raw blob bytes — same digest form as the VisualDCS envelope). */
export function sha256LfCanonical(bytes) {
  return crypto.createHash("sha256").update(bytes.toString("utf8").replace(/\r\n/g, "\n")).digest("hex");
}

/** Read a VisualDCS payload, verify its pinned digest and its contractVersion,
 *  fail closed on either. Returns the parsed payload plus its record count. */
export function readPinnedPayload(vdcsRoot, relPath, expectContractVersion = VDCS_PIN.contractVersion) {
  const abs = path.join(vdcsRoot, relPath);
  const bytes = fs.readFileSync(abs);
  const digest = sha256LfCanonical(bytes);
  const expected = VDCS_PIN.payloads[relPath];
  if (!expected) throw new Error(`learner-join: no pin recorded for ${relPath} — refusing to read unverified payload`);
  if (digest !== expected) {
    throw new Error(`learner-join: digest mismatch for ${relPath}: expected ${expected}, got ${digest} — VisualDCS release bump is a deliberate reviewed change (spec §9.2); refusing to build`);
  }
  const payload = JSON.parse(bytes.toString("utf8"));
  if (payload.contractVersion !== expectContractVersion) {
    throw new Error(`learner-join: unknown contractVersion ${payload.contractVersion} in ${relPath} (expected ${expectContractVersion}) — rejecting, keep the previous pin (spec §9.3)`);
  }
  return payload;
}

/** Verify the pinned manifest, then the two trainer payloads it restates.
 *  Returns the envelope block stored in the dataset (fail-closed path). */
export function verifyVisualDcsPins(vdcsRoot) {
  const manifest = readPinnedPayload(vdcsRoot, "visual/contracts/v1/manifest.json");
  if (manifest.releaseId !== VDCS_PIN.releaseId) {
    throw new Error(`learner-join: manifest releaseId ${manifest.releaseId} ≠ pinned ${VDCS_PIN.releaseId} — refusing to build`);
  }
  const nominal = readPinnedPayload(vdcsRoot, "visual/contracts/v1/nominal-trainer.json");
  const verb = readPinnedPayload(vdcsRoot, "visual/contracts/v1/verb-trainer.json");
  if (nominal.lemmaCount !== nominal.lemmas.length || verb.rootCount !== verb.roots.length) {
    throw new Error("learner-join: VisualDCS payload record count disagrees with its declared count — refusing to build");
  }
  return { manifest, nominal, verb };
}

/** Index the VisualDCS trainers for the IAST-side join (one map per side). */
export function buildParadigmIndexes(nominal, verb) {
  const nomById = new Map(); // IAST → [{id, tokens, cellsAttested}]
  for (const l of nominal.lemmas) {
    if (!nomById.has(l.lemma)) nomById.set(l.lemma, []);
    nomById.get(l.lemma).push({ id: String(l.lemmaId), tokens: l.tokens ?? 0, cellsAttested: l.cellsAttested ?? 0 });
  }
  const verbRoots = new Map(); // IAST root → {id, tokens, cells}
  for (const r of verb.roots) {
    verbRoots.set(r.rootId, { id: r.rootId, tokens: r.totalTokens ?? 0, cells: (r.cells ?? []).filter(c => (c.forms ?? []).length > 0).length });
  }
  return { nomById, verbRoots };
}

/** Minimal CSV parser (quoted fields, comma-separated) — same shape as the
 *  one in scripts/measure-learner-layer-coverage.mjs. */
export function parseCsv(text) {
  return text.trim().split(/\r?\n/).map(row => {
    const out = []; let cur = "", q = false;
    for (const ch of row) {
      if (ch === '"') q = !q; else if (ch === "," && !q) { out.push(cur); cur = ""; } else cur += ch;
    }
    out.push(cur); return out;
  });
}

/** Load WhitneyRoots crosswalk (I7 roots.csv + I8 root_class.csv), grouped by
 *  exact SLP1 root. All matching rows travel together — homonyms are shown,
 *  never picked (spec §7.2). Gaṇa comes only from I8 via whitney_no, with its
 *  certainty; `class_uncertain` marks the rest. Never inferred. */
export function loadWhitney(wrRoot) {
  const rootsRows = parseCsv(fs.readFileSync(path.join(wrRoot, "crosswalk", "roots.csv"), "utf8"));
  const rh = rootsRows[0];
  const col = n => rh.indexOf(n);
  const roots = rootsRows.slice(1).filter(r => r.length > 1).map(r => ({
    no: r[col("whitney_no")], slp1: r[col("root_slp1")], iast: r[col("root_iast")],
    hom: r[col("homonym")], cls: r[col("class")], clsUnc: r[col("class_uncertain")]
  }));
  const classRows = parseCsv(fs.readFileSync(path.join(wrRoot, "crosswalk", "root_class.csv"), "utf8"));
  const ch = classRows[0];
  const ganaByNo = new Map(classRows.slice(1).filter(r => r.length > 1).map(r => [r[ch.indexOf("whitney_no")],
    { gana: r[ch.indexOf("gana")], certainty: r[ch.indexOf("certainty")] }]));
  const rootsBySlp1 = new Map();
  for (const r of roots) {
    if (!rootsBySlp1.has(r.slp1)) rootsBySlp1.set(r.slp1, []);
    rootsBySlp1.get(r.slp1).push(r);
  }
  return { rootsBySlp1, ganaByNo, rootRowCount: roots.length, ganaRowCount: ganaByNo.size };
}

/** Card-side Whitney root field: every matching row with its gaṇa (or the
 *  honest marker that the gaṇa is not recorded / uncertain). */
export function whitneyCardField(rows, ganaByNo) {
  return rows.map(r => {
    const g = ganaByNo.get(r.no);
    return {
      no: r.no, iast: r.iast, hom: r.hom,
      ...(g ? { gana: g.gana, certainty: g.certainty }
        : r.cls ? { gana: r.cls, clsUnc: true } : {}),
      ...(r.clsUnc && !g ? { clsUnc: true } : {})
    };
  });
}

/** Load the P2 survival panel (I9 r2_h2h3.json) and per-sense rows (I10
 *  r2_h2_senses.json), grouped per lemma and pre-ranked (spec §6). */
export function loadSurvival(dataRoot) {
  const h2h3 = JSON.parse(fs.readFileSync(path.join(dataRoot, "data", "lexico", "r2_h2h3.json"), "utf8"));
  const senses = JSON.parse(fs.readFileSync(path.join(dataRoot, "data", "lexico", "r2_h2_senses.json"), "utf8"));
  const threshold = h2h3.survivedThreshold;
  if (threshold !== SURVIVAL_THRESHOLD) {
    throw new Error(`learner-join: P2 survival threshold ${threshold} ≠ pinned ${SURVIVAL_THRESHOLD} — the threshold is contract surface; re-pin deliberately`);
  }
  const byLemma = new Map();
  for (const row of senses.rows) {
    if (!byLemma.has(row.lemma)) byLemma.set(row.lemma, []);
    byLemma.get(row.lemma).push(row);
  }
  // rankSenses returns a NEW array — assign it back or the pre-ranking is a no-op
  for (const [lemma, rows] of byLemma) byLemma.set(lemma, rankSenses(rows));
  return { threshold, panel: new Set(h2h3.panel), byLemma, rowCount: senses.rows.length };
}

/** Card-side survival field: the ranked triple + provenance, exactly as the
 *  spec renders it. `text` comes from the harvested ancestor sense text —
 *  null when the ancestor article could not be re-read (named in warnings,
 *  never fabricated). `cited` travels because the P2 analysis is about it. */
export function survivalCardField(rows) {
  return rankSenses(rows).map(r => ({
    t: r.text ?? null,
    sv: Boolean(r.survived),
    ov: r.overlap,
    e: r.edge,
    pos: r.position,
    ci: Boolean(r.cited)
  }));
}
