// IAST <-> SLP1 transcoding is delegated to the canonical, cross-repo
// sanskrit-util package (vendored verbatim as ./sanskrit-util.js; see
// SHARED_CODE.md). The previous hand-rolled tables here were behaviour-identical
// to to_slp1/from_slp1 over 197k real lemmas EXCEPT the Vedic retroflex `L`/ḻ,
// which the old maps left untranslated — sanskrit-util fixes that. The SLP1
// headword normalizers below stay local: they are CDSL-headword-specific
// (strip SLP1 accent marks + trailing homonym digits), not generic translit.
import { to_slp1, from_slp1, slp1_norm } from "./sanskrit-util.js";

const IAST_MARKS = /[āīūṛṝḷḹṅñṭḍṇśṣṃṁḥĀĪŪṚṜḶḸṄÑṬḌṆŚṢṂṀḤ]/;

// CDSL SLP1 headword key, delegated to the canonical sanskrit-util slp1_norm (same key the
// build uses in scripts/lib/dict-normalize.mjs, so queries match the committed index).
export function normalizeSlp1Lemma(value) {
  const normalized = slp1_norm(value);
  return { normalized, changed: normalized !== (value ?? "").trim() };
}

export function iastToSlp1(value) {
  return to_slp1((value ?? "").normalize("NFC").trim().toLowerCase());
}

export function slp1ToIast(value) {
  return from_slp1(value ?? "");
}

export function normalizeLookupQuery(value) {
  const raw = (value ?? "").trim();
  const hasIast = IAST_MARKS.test(raw);
  const primary = hasIast ? iastToSlp1(raw) : raw;
  const normalized = normalizeSlp1Lemma(primary).normalized;
  const candidates = new Set();
  if (normalized) candidates.add(normalized);

  if (!hasIast && /^[a-z][a-z-]*$/.test(raw)) {
    const asciiIast = normalizeSlp1Lemma(iastToSlp1(raw)).normalized;
    if (asciiIast) candidates.add(asciiIast);
  }

  // A reader may type an IAST-looking ASCII word with an initial capital.
  // Preserve SLP1 as the primary candidate, but try the lower-case form too.
  if (!hasIast && /^[A-Z][a-z][A-Za-z-]*$/.test(raw)) {
    const lower = normalizeSlp1Lemma(raw.toLowerCase()).normalized;
    if (lower) candidates.add(lower);
    const lowerIast = normalizeSlp1Lemma(iastToSlp1(raw.toLowerCase())).normalized;
    if (lowerIast) candidates.add(lowerIast);
  }

  return {
    raw,
    normalized,
    candidates: [...candidates],
    inputScheme: hasIast ? "iast" : "slp1"
  };
}
