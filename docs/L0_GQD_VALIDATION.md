# Phase L0 — GQD validation of the convention stemma

_Created: 26-07-2026 · Last updated: 26-07-2026_

**Date**: 2026-07-26 · **Status**: computed on the committed L0 trees; evidence label `derived`
**Handoff**: H1578 · **Model**: Fable 5 (`claude-fable-5`)
**Method**: Generalized Quartet Distance (Pompei, Loreto & Tria 2011, eq. 8), the tree-evaluation metric of [Rama, List, Wahle & Jäger 2018](https://aclanthology.org/N18-2063/)
**Script**: [`scripts/L0/s7_gqd.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/L0/s7_gqd.py) (`--selftest`: 21/21)
**Data**: [`data/L0/gqd_validation.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/L0/gqd_validation.csv), [`gqd_clade_recovery.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/L0/gqd_clade_recovery.csv), [`gqd_tree_matrix.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/L0/gqd_tree_matrix.csv), [`gqd_report.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/L0/gqd_report.json), [`data/L0/gold/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/L0/gold)
**Reads with**: [`L0_RESULTS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/L0_RESULTS.md) (the finding this quantifies), [`L0_DESIGN.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/L0_DESIGN.md)

---

## Trust Block

- **Evidence**: committed L0 trees only — no re-annotation, no re-run of the cladogram
  pipeline. Inputs by git blob:
  `canonical_consensus.newick` `bfbdf371`, `B_whamming_nj` `56bf6675`,
  `A_jaccard_upgma` `fc6e20e4`, `bayesian_map` `08b2d239`,
  `preview/common_convention.newick` `8e81c859`, `preview/common_lemma.newick` `7c630a04`,
  `data/dictionary_inventory.csv` `1c327268`.
- **Limitations**: the expert reference is a *tree*, and documented dictionary descent is
  *reticulate* — five documented edges cannot be encoded at all (§7). The stemma gold's
  warrants partly cite lemma containment, which advantages the content tree in §4 and never
  the convention tree. The permutation test bounds accidental agreement; it is not a
  likelihood-ratio test. n = 32 dictionaries, only 14 of them inside a documented group.
- **Validation**: `python scripts/L0/s7_gqd.py --selftest` (21 checks: quartet coding,
  star handling, hand-counted GQD values on 4- and 6-leaf fixtures, branch-length and
  trifurcating-root invariance, gold assembly). Deterministic — seed `20260726`,
  999 permutations; re-running the stage reproduces every number.
- **Owner repo**: `csl-atlas`.
- **Next use**: cite the 0.146 figure as the reviewer-facing agreement statistic for the L0
  stemma in Paper H §5 / Paper M §4.1.5; cite §4 as the topology-level form of the
  convention-≠-content finding. Do **not** re-canonicalise the tree on these numbers (§3).

---

## 1. What the metric is, and why this one

The L0 layer had a *pairwise* validation (known-edge bootstrap support, nearest-neighbour
LOO) but no statistic that answers a reviewer's actual question: **how much of the
documented genealogy does the whole tree get right?** The historical-linguistics literature
answers it with the **Generalized Quartet Distance**, introduced by Pompei, Loreto & Tria
(2011) and used as the standard evaluation metric by Rama, List, Wahle & Jäger (2018) when
scoring automatically inferred language trees against an expert classification.

A *quartet* is any 4 leaves. A tree either resolves it into two pairs — a **butterfly**,
`ab|cd` — or leaves it unresolved at a polytomy — a **star**. With `T_I` the inferred tree
and `T_E` the expert tree, GQD is

```
GQD(T_I, T_E) = |butterflies of T_E resolved differently in T_I| / |butterflies of T_E|
```

Stars of `T_E` are excluded from both numerator and denominator. That is the whole point of
the *generalized* form: an expert classification is deliberately under-resolved, and its
silence must not be scored as an error. GQD = 0 means the inferred tree agrees with every
expert-resolved quartet; 1 means it contradicts all of them.

The implementation is written from the published definition — quartet topologies are read
off each tree with the four-point condition on unit-weight topological distances (branch
lengths ignored, as the metric is topological). No phylogenetics package is involved, so
there is no black-box dependency and nothing to reproduce blind; `dendropy` and `scikit-bio`
are in [`scripts/L0/requirements.txt`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/L0/requirements.txt)
but are not used here. Two readings are reported because the candidate set can contain
non-binary trees: `gqd` (strict — an expert butterfly the inferred tree leaves unresolved
counts as an error) and `gqd_pompei` (literal eq. 8 — such quartets are dropped). Every L0
tree turns out to be fully binary, so the two coincide and `n_inferred_star = 0` throughout.

## 2. The two expert references

Neither reference is built from convention characters, so neither is circular with respect
to the trees under test.

**`gold_stemma`** — documented bibliographic descent, deliberately polytomous. Only groups
with a documentary warrant are resolved; the other 18 dictionaries hang at the root and
cost nothing. Warrants, one row each, in
[`data/L0/gold/gold_stemma_warrants.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/L0/gold/gold_stemma_warrants.csv).

```
((SHS,WIL,YAT),(PW,PWG,SCH,(CAE,CCS)),(MW,MW72),(AP,AP90),ACC,AE,BEN,BHS,BOP,BOR,
 BUR,FRI,GRA,GST,INM,KRM,LRV,MCI,MD,PUI,SKD,STC,VCP,VEI);
```

| group | members | warrant |
|---|---|---|
| Wilson | WIL, YAT, SHS | Wilson 1832 heads the English line; YAT (1846) and SHS (1900) re-lexicalise it (inventory notes; `KNOWN_EDGES` tier A) |
| Petersburg | PWG, PW, SCH, (CAE, CCS) | PWG 1855–75 → PW 1879–89 → SCH 1928 *Nachträge*, with the Cappeller pair descending from PW |
| Cappeller | CCS, CAE | one compiler, two target languages (1887 / 1891) |
| Monier-Williams | MW72, MW | same compiler, 1st and 2nd editions |
| Apte | AP90, AP | 1890 original and its 1957–59 Pune revision |

**`gold_tradition`** — the `family` column of
[`data/dictionary_inventory.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/dictionary_inventory.csv),
assembled mechanically: Sanskrit-English (12), Sanskrit-German (5), Specialized (8),
English-Sanskrit (2), Sanskrit-French (2), Sanskrit-Sanskrit (2), Sanskrit-Latin (1). This is
a **coarse control, not a genealogy** — its 21,980 butterflies are dominated by one 12-member
target-language family that was never a descent unit, so no structured tree can score well
against it. It is included precisely to show what the convention signal is *not* tracking.

## 3. The L0 stemma against documented descent

32 dictionaries; 35,960 quartets; the stemma gold resolves **5,625** of them, the tradition
gold 21,980. Null = 999 leaf-label permutations of the same tree (seed 20260726); `p` is the
one-sided empirical fraction of permutations scoring at least as well, floored at 1/1000.
Each tree is scored on its own leaves: the ten gated trees carry all 32, and the final
(preview) row carries the 30-leaf tanglegram set, where the same gold resolves 4,830
butterflies. Read that row against §4's like-for-like comparison, not against the rows above
it.

| tree | grade | GQD vs **descent** | null mean ± sd | z | p | GQD vs tradition |
|---|---|---|---|---|---|---|
| **`canonical_consensus`** (published) | gated | **0.1456** | 0.666 ± 0.068 | −7.67 | 0.001 | 0.5708 |
| `B_whamming_upgma` | gated | 0.1456 | 0.666 ± 0.067 | −7.76 | 0.001 | 0.5708 |
| `B_whamming_nj` | gated | 0.1426 | 0.672 ± 0.065 | −8.11 | 0.001 | 0.5635 |
| `B_hamming_upgma` | gated | 0.1723 | 0.669 ± 0.065 | −7.60 | 0.001 | 0.5788 |
| `B_hamming_nj` | gated | 0.1561 | 0.666 ± 0.066 | −7.75 | 0.001 | 0.5640 |
| `A_jaccard_upgma` | gated | **0.1102** | 0.666 ± 0.065 | −8.55 | 0.001 | 0.5325 |
| `A_jaccard_nj` | gated | 0.1227 | 0.667 ± 0.066 | −8.19 | 0.001 | 0.5574 |
| `C_chamming_upgma` | gated | 0.1506 | 0.669 ± 0.066 | −7.89 | 0.001 | 0.6062 |
| `C_chamming_nj` | gated | 0.1701 | 0.665 ± 0.065 | −7.58 | 0.001 | 0.5574 |
| `bayesian_map` | gated | 0.1643 | 0.667 ± 0.066 | −7.59 | 0.001 | 0.5802 |
| `preview_common_convention` | preview | 0.4292 | 0.665 ± 0.068 | −3.44 | 0.008 | 0.6014 |

**The published stemma agrees with 85.4% of the expert-resolved quartets** (GQD 0.1456), and
every gated tree lands in a narrow 0.110–0.172 band — encoding, metric and algorithm move the
figure by at most 0.06, so the agreement is a property of the convention characters, not of
UPGMA. All ten clear the permutation null by 7.6–8.6 standard deviations.

Three things this table says that the existing L0 validation could not:

1. **The 55% directed-edge recovery in [`L0_RESULTS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/L0_RESULTS.md) §3 understated the tree.** Edge recovery asks whether each documented parent-child pair is a sister pair — an all-or-nothing test that a large, otherwise-correct clade fails. GQD scores the same trees at 0.85 agreement because it measures *topological* agreement with the documented groups rather than sisterhood.
2. **The Patel-2016 gold-convention ingest is worth ≈0.28 GQD.** The preview tree (19 mechanical dims, no Patel conventions) scores 0.4292 against the same gold on the same leaves where the gated tree scores 0.1468 (§4). This independently corroborates §2 of `L0_RESULTS.md` ("the Patel ingest doubled the signal") on a metric that was not used to tune anything.
3. **The tradition gold is barely beaten** (0.53–0.61, z ≈ −1.7 to −4.4). Convention similarity does *not* reduce to "dictionaries with the same target language look alike" — if it did, the tradition column would be the strong one. It is the weak one.

Two honesty notes. `canonical_consensus.newick` and `B_whamming_upgma.newick` are
**byte-identical** in the committed data (blob `bfbdf371`): the 1000× dimension-bootstrap
consensus recovered the point estimate exactly, so their rows coincide by construction, not
by coincidence. And `A_jaccard_upgma` scores *better* than the published canonical
(0.1102 vs 0.1456). The canonical config was **pre-registered** in `L0_DESIGN.md` §5–§6 and
is not re-opened on the strength of a metric computed after the fact — selecting the
best-scoring config post hoc is exactly the overfitting the pre-registration exists to
prevent. The spread is recorded; the tree is unchanged.

## 4. Convention versus content, at the level of the whole topology

`L0_RESULTS.md` §3 argues that convention-lineage ≠ content-lineage from pairwise residuals.
GQD tests the same claim on entire topologies: the convention tree and the lemma-overlap
(sanhw1 Jaccard) tree from
[`tanglegram.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/L0/tanglegram.py)
share 30 leaves, so both can be scored against the same two expert references.

| tree | axis | GQD vs **descent** | GQD vs tradition |
|---|---|---|---|
| `canonical_consensus` | convention | **0.1468** | 0.5773 |
| `preview_common_convention` | convention (preview-grade) | 0.4292 | 0.6014 |
| `preview_common_lemma` | **content** (lemma overlap) | 0.4302 | **0.4943** |

The two axes **cross over**. Against documented descent the convention tree is nearly three
times closer (0.147 vs 0.430); against target-language tradition the content tree wins
(0.494 vs 0.577). Shared house style tracks who copied whose *editorial practice*; shared
lemma stock tracks what corpus a dictionary covers — which is largely what the tradition
families encode.

The convention result is **conservative**, because the comparison is rigged mildly against
it: two of the five gold groups (Wilson, Petersburg) cite sanhw1 lemma containment among
their warrants, so the content tree is being scored partly against evidence of its own kind,
and the convention tree is not. A content-tree win should be discounted for that; the
convention-tree win at 0.147 should not.

## 5. Which families each axis recovers

Per documented group, the fraction of its {2-inside, 2-outside} quartets the tree resolves
as the group (`data/L0/gqd_clade_recovery.csv`). This is where the crossover becomes legible.

| documented group | convention (canonical) | content (lemma) |
|---|---|---|
| Petersburg (PWG, PW, SCH, CCS, CAE) | **1.000** (3510/3510) | 0.395 |
| Cappeller (CCS, CAE) | **1.000** (435/435) | 1.000 |
| Apte (AP90, AP) | 0.933 (406/435) | 1.000 |
| Monier-Williams (MW72, MW) | **0.747** (325/435) | 0.286 |
| Wilson (WIL, YAT, SHS) | 0.442 (538/1218) | **1.000** |

Neither axis dominates, and the failures are the informative part:

- **Petersburg is perfect on conventions and 0.395 on content** — the formatting family is
  recovered completely by house style, while lemma overlap scatters it (PW and PWG's stock is
  common core that everything else also carries).
- **Wilson inverts**: 1.000 on content, 0.442 on conventions. YAT re-styled Wilson — the
  `WIL→YAT` residual already flagged in `L0_RESULTS.md` §L0.7 — so the convention tree
  correctly refuses to group a dictionary that shares Wilson's lemmas under a different house
  style. The "failure" is the instrument working.
- **Monier-Williams sits at 0.747 on conventions and 0.286 on content**, both below their
  family's neighbours. MW is the corpus's great reformatter *and* its great absorber; a tree
  on either single axis under-represents it. This is the reticulation limit of §7 showing up
  as a number.

## 6. Quartet distance between the L0 trees

[`gqd_tree_matrix.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/L0/gqd_tree_matrix.csv)
is the quartet analogue of the committed Robinson–Foulds matrix — normalised over all
quartets on each pair's shared leaves, so it is comparable across the 30/32-leaf split that
RF cannot handle. Convention trees sit 0.05–0.46 from one another; the content tree sits
**0.59–0.66 from every one of them**, its own nearest convention neighbour (0.590) still
farther than the two most distant convention trees are from each other (0.462). Quartet
distance separates the axes more sharply than RF did (RF put UPGMA–NJ at 0.59, i.e. inside
the same range it gives cross-axis pairs).

## 7. Limitations

1. **The gold is a tree; dictionary descent is a network.** Five documented edges cannot be
   encoded and are listed as `UNREPRESENTABLE` rows in `gold_stemma_warrants.csv`:
   `PWG→MW72` and `PWG→MW` (tier A), `BOP→MW` and `BEN→MW` (tier B), and `YAT→SHS` (collapsed
   into a flat Wilson group to keep the gold conservative). Every one of the tier-A
   unrepresentable edges runs *into* Monier-Williams — precisely the reformatted edges
   `L0_RESULTS.md` §3 identifies. **GQD structurally cannot reward a tree for recovering
   them**, so 0.1456 is a floor on agreement with the documented record, not a ceiling.
2. **Partial circularity, in the content tree's favour.** Wilson and Petersburg group
   warrants cite sanhw1 containment. Read §4's content column as optimistic.
3. **The permutation test randomises leaf labels only.** It answers "could this tree shape
   match the classification this well by accident" — it is not a model comparison and yields
   no likelihood. p is floored at 0.001 by the 999-permutation budget.
4. **n = 32, of which 14 are inside a documented group.** The other 18 contribute no
   butterflies of their own; the stemma gold's 5,625 butterflies all involve at least one
   documented group. Sub-clade differences among the unplaced 18 are invisible to this metric.
5. **European-tradition skew.** The corpus, the documented edges, and hence the gold all
   over-represent the 19th-century European lexicographical line (see `L0_DESIGN.md`
   limitations). KNA, KOW and AMAR are absent from the L0 matrix entirely.
6. **Bootstrap support is not an independent control** here either — per the `THREE-AXIS-INDEP`
   row of [`HYPOTHESIS_INDEX.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/HYPOTHESIS_INDEX.md),
   it tracks convention similarity at r = 0.92. GQD *is* independent of it in the sense that
   it consults the expert classification rather than the character matrix, but it consults the
   same trees.

## 8. Reproduce

```
python scripts/L0/s7_gqd.py --selftest     # 21 checks, no data needed
python scripts/L0/s7_gqd.py                # ~40 s; rewrites data/L0/gqd_* and data/L0/gold/
node scripts/validate-l0-gqd.mjs           # invariants; also runs inside npm run verify
```

The stage reads only committed artifacts and writes only under `data/L0/`. It does not touch
the fingerprint, the Patel annotations, or any tree — re-running it can never change the
cladogram.

_Dr. Mārcis Gasūns_
