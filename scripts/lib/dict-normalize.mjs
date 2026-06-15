// Shared headword normalization for cross-dictionary alignment.
//
// CDSL <k1> headwords are SLP1. Normalization removes accent marks and trailing
// homonym digits so the same lemma aligns across dictionaries, while preserving
// SLP1 case (phonemic). This is now the canonical sanskrit-util `slp1_norm`
// (vendored at src/lib/sanskrit-util.js; see SHARED_CODE.md) — verified
// byte-identical to the previous local fold over 1,424,745 real CDSL k1
// headwords, so all committed normalized keys are unchanged.
import { slp1_norm } from "../../src/lib/sanskrit-util.js";

/**
 * Normalize a raw <k1> headword.
 * @returns {{normalized: string, changed: boolean}}
 */
export function normalizeLemma(k1) {
  const normalized = slp1_norm(k1);
  return { normalized, changed: normalized !== (k1 ?? "").trim() };
}
