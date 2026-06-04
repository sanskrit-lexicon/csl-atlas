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

## All dict-pairs — and a positive control (round 7: + Apte `cf.`)

Parsing the Apte `cf. {#…#}` slot (round 7, below) adds **AP, AP90 and CAE** as
cross-referencing dictionaries, so the same overlap measure runs on every pair. The
contrast is the validation:

| pair | overlap | a-rate / b-rate | Jaccard | reading |
|---|---:|---|---:|---|
| **AP × AP90** | 182 | **85.5% / 84.7%** | **0.74** | **same dictionary, two Apte editions → near-identical network (positive control)** |
| AP × PWG | 23 | 34.3% / 7.4% | 0.065 | |
| AP × MW | 19 | 28.8% / 23.2% | 0.147 | |
| CAE × MW | 11 | 24.4% / 20.0% | 0.124 | |
| **MW × PWG** | 641 | **21.8% / 9.1%** | 0.069 | **different traditions → shared core only** |
| AP90 × PWG | 11 | 14.7% / 2.8% | 0.024 | |
| CAE × PWG | 7 | 12.5% / 1.8% | 0.016 | |
| AP90 × MW | 10 | 11.2% / 8.6% | 0.051 | |

**The positive control validates the measure.** AP and AP90 are the *same* dictionary
(Apte, the 1890 edition and the revised Practical), and the method recovers **~85%**
overlap — what genuine descent looks like. Against that ceiling, MW × PWG's 21.8% is
unmistakably *not* inheritance but a shared scholarly core. (AP × CAE / AP90 × CAE share
≤2 source lemmas — too few to read.)

## Apte `cf.` parsing (round 7)

AP/AP90 mark cf. targets in `{#…#}` (SLP1), not `<s>`, mixing lemma pointers with
multi-word quotes, cognates and citations. The round-7 rule keeps a `{#…#}` as an **edge**
only if lemma-like (no space/period; each `/`,`,`-split atom a SLP1 word ≤ 24 chars) and
routes the rest to a **cf-quote side file** (`xref_cf_quotes.csv`, 517 rows: AP 432, AP90 79,
CAE 5). New clean lemma edges: **AP 609, AP90 446, CAE 196**. **BEN = 0** — its cf. is purely
cognate (`<lang>`) / roman, so BEN does no internal Sanskrit cross-referencing at all
(a *content* finding, not a markup gap).

## Caveats

- **Floor, not ceiling** — the normalization is conservative; unmatched messy targets
  only *lower* the measured overlap.
- **Directed edges** — `src→tgt`; a reciprocal `tgt→src` in the other dict is not counted as a match.
- **Density asymmetry** — PWG cross-references far more (22,937 vs 7,637 edges), which
  structurally caps its inheritance rate; the smaller-dict-side rate is the more meaningful number.
- Cross-referencing dicts: MW, PWG (heavy), AP, AP90, CAE (Apte `cf.`, modest); BEN does none;
  PW/MW72/WIL/indigenous use no cross-ref convention (the m1 "0 ≠ structureless" rule).

## Provenance

`scripts/lexico/m3_xrefs.py` (edges + Apte `cf.` parsing → `xref_edges.csv` +
`xref_cf_quotes.csv`) → `scripts/lexico/m6_xref_lineage.py` → `data/lexico/xref_lineage.json`
(all-pair stats) + `data/lexico/xref_shared_edges.csv` (the 641 MW∩PWG edges). Validated by
`validate_lexico.py` (m6 check). Deterministic, no deps.
