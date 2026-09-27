// The one cross-reference target normaliser the JS side shares with
// scripts/lexico/m6_xref_lineage.py `normalize()` — keep the two in lockstep.
//
// m3 emits every edge target RAW: MW keeps its SLP1 accent marks (`a/nAkzit`,
// `Are/`, `Basa/d`) and cites compound members with a leading or trailing hyphen
// (`-DArmyAyaRa`, `aBi-`); PWG marks the compound family with `°`. m6 folds both
// ends to one key before intersecting, so data/lexico/xref_shared_edges.csv and the
// hub-review sample carry NORMALISED lemmas. Any consumer that looks a sample edge
// back up in xref_edges.csv must fold the raw row the same way, or every accented or
// hyphen-prefixed MW target silently reads as "exact edge missing in MW" (H5408:
// 4 of the 40 shared-core rows were flagged that way while MW printed the cf.).
const ACCENT = /[/\\^]/g; // SLP1 udātta / anudātta / svarita marks — hwnorm1 drops these

export function normalizeXrefKey(value) {
  let s = String(value ?? "").trim().replace(ACCENT, "").replace(/°/g, "");
  s = s.split(/\s+/).filter(Boolean).join(" ");
  return s.replace(/^[\s-]+|[\s-]+$/g, "");
}
