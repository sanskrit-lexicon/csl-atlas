// Deterministic typology for a cross-dictionary gender disagreement.
//
// Pure function over the per-dictionary specific-gender map produced by
// genderConflict() in dict-align.mjs. Four independent axes, each a small enum,
// plus a compact human-readable label. No LLM and no external data — the
// classification is derived entirely from which genders each dictionary asserts
// and whether that assertion came from a <lex> tag or a prose marker.

import { CORE_COMPARISON_DICTS } from "./dict-scope.mjs";

// Dictionary LABELS whose gender is read from prose markers (VCP, SKD) rather
// than a <lex> tag. Prose-derived genders are extraction-fragile, so a conflict
// that involves one is "softer" evidence than a lex-vs-lex disagreement.
export const PROSE_LABELS = new Set(
  CORE_COMPARISON_DICTS.filter(d => !d.grammarReliable).map(d => d.label)
);

const GENDER_ORDER = { m: 0, f: 1, n: 2 };

/**
 * Classify a gender conflict.
 * @param {Object<string,string[]>} byDict - label -> sorted specific genders,
 *   e.g. { MW: ["m", "n"], PWK: ["n"] }.
 * @returns {{ genderPair, basis, cardinality, dictCount, overlap, label }}
 */
export function genderTypology(byDict) {
  const labels = Object.keys(byDict);
  const dictCount = labels.length;

  // Axis 1 — gender pair: the set of specific genders in play, ordered m/f/n.
  const genders = [...new Set(labels.flatMap(l => byDict[l]))]
    .sort((a, b) => GENDER_ORDER[a] - GENDER_ORDER[b]);
  const genderPair = genders.join("/");

  // Axis 2 — evidence basis: lex-only (grammar-reliable both sides) vs any
  // prose-derived (VCP/SKD) contributor.
  const basis = labels.some(l => PROSE_LABELS.has(l)) ? "prose-mixed" : "lex";

  // Axis 3 — cardinality: exactly two dictionaries disagree, or three or more.
  const cardinality = dictCount > 2 ? "multi" : "binary";

  // Axis 4 — overlap: every dictionary asserts a single gender and they are
  // fully disjoint, or some dictionary asserts several genders so one side's
  // set only partially clashes ("includes"-style conflict).
  const overlap = labels.some(l => byDict[l].length > 1) ? "partial" : "disjoint";

  const label = `${genderPair} · ${cardinality} · ${basis} · ${overlap}`;
  return { genderPair, basis, cardinality, dictCount, overlap, label };
}
