# Cross-reference lineage: does MW `cf.` inherit PWG `Vgl.`? (issue #30 §3.1)

m3 captured each dictionary's internal cross-reference edges (source lemma → target
lemma) but left targets raw SLP1 and deferred the cross-dict join. **m6**
(`scripts/lexico/m6_xref_lineage.py`) does that join and answers the
LEXICOGRAPHY_ROADMAP §3.1 question: are the Monier-Williams `cf.` network and the
Petersburg `Vgl.` network the same graph?

## Method

Normalise both ends of every edge to a common key — strip the compound-family marker
(**PWG `°`** vs **MW `-`**: `a°` ≡ `a-` ≡ `a/-`), SLP1 accents, and stray hyphens —
dedupe per dict, then intersect the two edge sets **restricted to the source lemmas
both dictionaries cross-reference**. Overlap is a **floor**: messy multi-part targets
that don't reduce cleanly simply fail to match.

## Result

| | MW (`cf.`) | PWG (`Vgl.`) |
|---|---:|---:|
| normalized edges | 7,637 | 22,937 |
| distinct source lemmas | 6,974 | 11,857 |
| **shared source lemmas** | colspan | **2,538** |
| edges on those shared sources | 2,946 | 7,022 |
| **overlapping edges (same src→tgt)** | colspan | **641** |
| inheritance rate on shared sources | **21.8%** | 9.1% |
| Jaccard on shared sources | colspan | 0.069 |
| shared-source lemmas agreeing on ≥1 target | colspan | 640 |

Sample shared edges (genuine — mostly variant-form and cognate-root pointers both
traditions independently record): `ARi→aRi`, `Adinava→AdInava`, `Ali→ali`,
`Anuzak→anuzak`, `Ayu→Ayus`, `BI→Byas`, `Bala→bal`, `Bas→psA`.

## Verdict — partial, not wholesale

**A shared cross-reference CORE plus large independent expansion in each tradition.**
Of the cross-references MW makes from lemmas PWG also cross-references, **21.8%** point
to the same target — far above what chance would give in a ~300k-lemma space, so the
two networks are *not* independent. But ~78% of MW's cross-refs (even on shared source
lemmas) go where PWG does not, and PWG's network is ~3× denser (only 9.1% of its
cross-refs are shared). So this is **not** evidence that MW was built on the Petersburg
cross-references wholesale — rather a common substrate (shared scholarly knowledge of
variants/cognates, and likely some borrowing) over which each dictionary cross-referenced
largely on its own.

## Caveats

- **Floor, not ceiling** — the normalization is conservative; unmatched messy targets
  only *lower* the measured overlap.
- **Directed edges** — `src→tgt`; a reciprocal `tgt→src` in the other dict is not counted as a match.
- **Density asymmetry** — PWG cross-references far more (22,937 vs 7,637 edges), which
  structurally caps its inheritance rate; the MW-side rate (21.8%) is the more meaningful number.
- Only MW and PWG carry enough edges to compare (AE has 2; PW/WIL/indigenous use neither convention — the m1 "0 ≠ structureless" rule).

## Provenance

`scripts/lexico/m6_xref_lineage.py` → `data/lexico/xref_lineage.json` (stats) +
`data/lexico/xref_shared_edges.csv` (the 641 shared edges). Validated by
`validate_lexico.py` (m6 check). Deterministic, no deps.
