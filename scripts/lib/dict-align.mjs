// Cross-dictionary alignment helpers (pure functions over the lemma index).
//
// The index maps a normalized lemma to per-dictionary evidence:
//   Map<normalized, { [code]: { records, raws:Set, genders:Set, example } }>
//
// Alignment is conservative and confidence-labeled. Homonyms are NOT merged
// away: each dictionary keeps its own record count for a lemma, so a later
// homonym-split level can use it.

const SPECIFIC_GENDERS = new Set(["m", "f", "n"]);

/** Sorted list of dictionary codes present for an index entry. */
export function presentDicts(entry, order) {
  return order.filter(code => entry[code]);
}

/**
 * Alignment confidence for a multi-dictionary lemma.
 * "high" when every contributing dictionary used the identical raw <k1>;
 * "medium" when they matched only after normalization (accent/digit stripping).
 */
export function lemmaConfidence(entry, codes) {
  const raws = new Set();
  for (const code of codes) for (const r of entry[code].raws) raws.add(r);
  return raws.size <= 1 ? "high" : "medium";
}

/**
 * Detect a gender conflict among the grammar-reliable dictionaries.
 * A conflict requires two dictionaries whose specific-gender sets ({m,f,n})
 * are both non-empty and disjoint. POS-only tags (adj/ind) never trigger one.
 */
export function genderConflict(entry, taggedCodes) {
  const byDict = {};
  for (const code of taggedCodes) {
    if (!entry[code]) continue;
    const g = [...entry[code].genders].filter(x => SPECIFIC_GENDERS.has(x));
    if (g.length) byDict[code] = g.sort();
  }
  const dicts = Object.keys(byDict);
  if (dicts.length < 2) return { conflict: false, byDict };
  for (let i = 0; i < dicts.length; i++) {
    for (let j = i + 1; j < dicts.length; j++) {
      const a = new Set(byDict[dicts[i]]);
      const shared = byDict[dicts[j]].some(x => a.has(x));
      if (!shared) return { conflict: true, byDict };
    }
  }
  return { conflict: false, byDict };
}
