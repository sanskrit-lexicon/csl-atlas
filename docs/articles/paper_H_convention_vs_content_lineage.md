# Paper H §5 — Convention-lineage is not content-lineage

*Draft section for Paper H (historical transmission). Empirical basis: Phase L0
([`L0_RESULTS.md`](../L0_RESULTS.md)); data in `data/L0/`. Companion to the sanhw1
content-containment results (Paper L §4 / dashboard `/lexicography`).*

---

## 5.1 Two independent signals of descent

A digital dictionary inherits from its predecessors along two separable axes. The
first is **content**: which lemmas, glosses, and citations it reproduces — measured
here by sanhw1 headword containment (the fraction of a source's lemmas recurring in a
later work). The second is **convention**: the orthographic and citation *house style*
in which that content is rendered — anusvāra vs. homorganic nasal, gemination after
*r*, the citation form of ṛ-stems and *-vas/-yas* participles, inflected vs. uninflected
headwords. We operationalise the second axis as a 25-dimensional **convention
fingerprint**, of which the seven canonical dimensions are Dhaval Patel's (2016)
normalization conventions, populated from Patel's own per-dictionary classification.

The central historical finding of this phase is that **the two axes are orthogonal,
and their divergence is itself diagnostic of editorial intervention.**

## 5.2 The Petersburg formatting family

Where a later dictionary inherited *both* the content and the house style of its source,
the convention fingerprint recovers the lineage at high confidence. The clearest case is
the Böhtlingk–Roth Petersburg tradition. PWG (1855), its abridgement PW (1879), and
Schmidt's *Nachträge* (1928) carry an **identical** seven-convention fingerprint
(1.2+1.5 · 2.2 · 3.2+3.5 · 4.2 · 5.2 · 6.1 · 7.4); Cappeller's *Sanskrit-Wörterbuch*
(CCS, 1887) differs on a single convention. In the convention cladogram these four form
a single tight clade, with 1000× bootstrap support of **0.79** for PWG→PW and **0.70**
for PWG→SCH — values an order of magnitude above what the mechanically-extractable
dimensions alone yielded (0.38 and 0.31). The Anglo-Indian popular line behaves likewise:
WIL (1832) → SHS (1900) recovers at **0.81**. These are *formatting* genealogies: each
heir adopted not only its predecessor's entries but its predecessor's way of writing them.

## 5.3 Monier-Williams absorbed content but recoded convention

The instructive counter-cases are the lineages the convention fingerprint **fails** to
recover — and they fail for a reason. By content, Monier-Williams (1899) is the
convergence point of the German scholarly tradition: 89.3% of PWG's *headwords* and the bulk
of MW72's recur in MW (sanhw1 lemma containment).¹ Yet PWG→MW draws only **0.02** bootstrap
support in the convention tree, and MW72→MW only **0.29**. The fingerprint is not in
error: Monier-Williams *reformatted*. Where PWG cites ṛ-stems as *-ar* (convention 6.1,
`kartar`), MW uses *-ṛ* (6.2, `kartṛ`); where PWG writes śatṛ participles as *-ant*
(3.2), MW writes *-at* (3.1); where PWG uses *-vaṃs* (7.4), MW uses *-vas* (7.1). MW thus
imported the Petersburg *lexicon* while imposing its own *orthographic standard*. The
divergence between a near-unity content-containment and a near-zero convention-similarity
is precisely the quantitative signature of a re-edited, re-typeset descendant — exactly
the editorial act the historical record attributes to Monier-Williams. Yates (YAT, 1846)
shows a milder version of the same: derived from Wilson by content, it re-styled the
anusvāra and duplication conventions (uniquely adopting convention 1.4) and so sits apart
from WIL in the convention tree.

## 5.4 Consequence for the transmission model

Content-containment and convention-similarity must therefore enter the inheritance model
as **separate axes, not a single similarity score**. Their *agreement* marks faithful
reproduction (the Petersburg and Wilson lines); their *disagreement* — high content
overlap with low convention overlap — localises the points where an editor consolidated
sources into a new house style (Monier-Williams; to a lesser degree Yates). A unified
inheritance score that collapsed the two would misread MW as either unrelated to PWG
(if convention-weighted) or as a faithful copy (if content-weighted); the historically
correct reading — *faithful in substance, independent in form* — is legible only in the
gap between them.

We make this gap a single scalar, the **reformatting residual**
`r(A→B) = content_containment(A→B) − convention_similarity(A,B)`, computed over the 25
documented containment edges. The ranking is unambiguous: the five largest residuals are
**CAE→MW (0.68)**, **MD→MW (0.65)**, **CCS→MW (0.62)**, GRA→PW (0.58), and **WIL→YAT (0.54)**
— every high-content edge *into Monier-Williams*, plus Yates's restyling of Wilson. The five
smallest are SHS↔WIL (0.12–0.17), PWG→PW (0.19), CCS→CAE (0.23), and CAE→PW (0.30) — the
faithful formatting lineages. Monier-Williams is thus quantitatively the corpus's principal
reformatter: it drew 89–93% of CAE's, Macdonell's, and Cappeller's lemmas into a house style
those sources do not share (convention similarity 0.23–0.28). We accordingly report the two
matrices side by side and treat the residual as a first-class historical variable — the same
instrument carries the standalone methods note (PUBLICATIONS Article 20).

¹ **Caveat on the content figure.** Raw sanhw1 containment is confounded by dictionary size:
MW's ~194k headwords contain almost any older work's common-core vocabulary, so containment
ranks track *source size/rarity* rather than descent (the unrelated Latin glossary BOP scores
a *higher* 0.94; containment falls monotonically from small to large sources). The content
axis as used here is therefore lemma-set **presence**, adequate to contrast with the *direct*
convention dissimilarity but not a measure of content-copying. A precise content-inheritance
figure requires size-corrected association (lift over a coverage null), rare/exclusive-lemma
containment, and entry-text + citation-set comparison (Phases L4/L6) — pending; see
[`L0_HANDOFF.md`](../L0_HANDOFF.md) §3. The §5 finding does not depend on the magnitude.

> **Numbers in this section** are from `data/L0/bootstrap_support.csv` and
> `validation_report.json` (convention axis) and `data/sanhw1_inheritance_edges.csv`
> (content axis). Convention assignments: Patel 2016, `data/L0/patel2016_assignments.csv`.
> Figure: `data/L0/trees/canonical_consensus.png` (convention cladogram).
