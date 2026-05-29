// Shared headword normalization for cross-dictionary alignment.
//
// CDSL <k1> headwords are SLP1. Normalization is deliberately conservative:
// it removes accent marks and trailing homonym digits so the same lemma in
// different dictionaries aligns, while preserving SLP1 case (which is
// phonemic in Sanskrit). It never lowercases or transliterates.

const ACCENTS = /[\/\\^~]/g; // udatta / anudatta / svarita / nasal marks

/**
 * Normalize a raw <k1> headword.
 * @returns {{normalized: string, changed: boolean}}
 */
export function normalizeLemma(k1) {
  const raw = (k1 ?? "").trim();
  let n = raw.replace(ACCENTS, "");
  n = n.replace(/\d+$/, ""); // trailing homonym index, if any
  n = n.replace(/\s+/g, " ").trim();
  return { normalized: n, changed: n !== raw };
}
