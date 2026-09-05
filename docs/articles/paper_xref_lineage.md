_Created: 16-06-2026 · Last updated: 05-09-2026_

# Pointing Inward: Cross-Reference Graphs as a Signal of Dictionary Descent

*Draft manuscript for a digital-humanities / metalexicography venue (target: a DH or
lexicography methods journal; WSC 2027 alternate). Empirical companion (P5) in this
series, alongside* Condensation, Not Inflation *(sense inheritance, P2),* Three Axes of
Descent *(inheritance methodology, P3),* Grammar Without Tags *(indigenous
microstructure, P4), and* Order Is the Dictionary *(kośa macrostructure, P6); the cross-reference-overlap metric
itself is owned by the series' methods paper (P1, §3.6). Empirical
basis: the cross-reference lineage layer
([`data/lexico/xref_lineage.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/xref_lineage.json),
[`data/lexico/xref_edges.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/xref_edges.csv),
[`data/lexico/xref_shared_edges.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/xref_shared_edges.csv)) and the
hub-review packet
([`data/lexico/xref_hub_review.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/xref_hub_review.json)),
documented in [`MICROSTRUCTURE_XREF_LINEAGE.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_XREF_LINEAGE.md) and
[`MICROSTRUCTURE_XREF_HUB_REVIEW.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_XREF_HUB_REVIEW.md), with the
public chart at [`/tools/xref-lineage`](https://sanskrit-lexicon.github.io/csl-atlas/tools/xref-lineage).
All numbers are the 2026-06 snapshot and
reproducible from committed data; every figure was re-verified against the artifacts in
the 2026-07-03 referee pass
([A05_review_fable5.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/A05_review_fable5.md)),
which also corrected an AP/AP90 edition-label swap in the abstract and Table 1;
author-voice pass 2026-07-11
([SIGNOFF_A05_author_pass.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/SIGNOFF_A05_author_pass.md)).
Author: Mārcis Gasūns, independent scholar
([ORCID 0000-0003-4513-884X](https://orcid.org/0000-0003-4513-884X)), gasyoun@ya.ru.*

---

## Abstract

Every dictionary points inward: an entry says "compare *X*," "see *Y*," and those
pointers form a directed graph over the headword list. If a later dictionary inherits
from an earlier one, it should inherit the pointers too — so the overlap of two
cross-reference graphs is a candidate signal of descent. The difficulty is reading the
overlap: two dictionaries of the same language share variant and cognate pointers by
common scholarly knowledge, and they share prefix-marking conventions that manufacture
spurious hubs, so a raw overlap number conflates inheritance with coincidence and with
house style. We make the signal legible with a **positive control**. Parsing the
cross-reference slots of the Cologne Digital Sanskrit Lexicon yields directed pointer
graphs for the Petersburg lexicon (PWG `Vgl.`, 22,937 normalised edges over 11,857
source lemmas), Monier-Williams (MW `cf.`, 7,637 edges / 6,974 sources), and the Apte
editions (`cf.` in SLP1, 444 clean lemma edges for Apte 1890 and 609 for the revised
1957 Apte).
Two editions of the *same* dictionary — Apte 1890 and the revised Apte — overlap at
**85 % inheritance rate (Jaccard 0.74)**: that is the calibrated signature of descent.
Against that ceiling, the cross-tradition Monier-Williams × Petersburg pair reaches only
**21.8 % (Jaccard 0.069)** on the lemmas both cross-reference — far above chance in the
~300,000-lemma union of the two key spaces, so the two networks
are *not* independent, yet the overlap sits nowhere near the
edition-continuity ceiling. The cross-reference relationship between MW and the
Petersburg lexicon is therefore a **shared core, not wholesale inheritance**: a common
substrate of variant/cognate pointers over which each tradition cross-referenced largely
on its own (PWG's network is three times denser). We further show that the apparent
overlap must be cleaned of **prefix-convention hubs** (PWG points 320 times to *a°*, 254
to *mahā°*) — a *convention* artefact in the sense of the companion methods paper — and
that one dictionary, Benfey, does no internal Sanskrit cross-referencing at all, a fact
about its content rather than its markup. Cross-reference overlap is a floor for
structural relatedness, calibrated by an edition-continuity control; it earns a descent
claim only against that ceiling and only after the convention hubs are removed.

**Keywords:** cross-reference; dictionary inheritance; digital lexicography; graph
overlap; Sanskrit; Monier-Williams; Petersburg lexicon; Apte; computational stemmatics;
positive control.

---

## 1. Introduction

A cross-reference is the dictionary talking to itself — the pointer apparatus that
lexicographic theory treats as a designed component of entry structure (Wiegand 1989;
Atkins and Rundell 2008) and classical metalexicography as part of the dictionary's
information economy (Zgusta 1971). *Cf.*, *see*, *Vgl.* — each
pointer links one headword to another and asserts that the two belong together: variant
spellings, cognate roots, members of a compound family, semantically related words. Over
a whole dictionary these pointers form a directed graph, and that graph is a structural
fingerprint distinct from the word list and from the prose of the entries. It is also a
plausible vehicle of descent: a lexicographer who works from an earlier dictionary
inherits not only its headwords but its sense of which words point to which, so two
related dictionaries should share cross-reference edges.

The question this paper asks is the one posed in the project roadmap: are the
Monier-Williams `cf.` network and the Petersburg `Vgl.` network the *same graph*? The
methodological obstacle is that cross-reference graphs overlap for three different
reasons, only one of which is descent. Two Sanskrit dictionaries will independently
record that *Ayu* is a variant of *Ayus* or that *bala* relates to the root *bal*,
because both lexicographers know the language — a **content coincidence**. Both will
point many entries to high-frequency prefixes and compound heads — *a°*, *mahā°*, *su°*
— because both mark compound families that way, a **convention artefact** that
manufactures graph hubs out of house style rather than shared knowledge. And only some
overlap is genuine **inheritance**, one network built on the other. A single overlap
number cannot tell these apart.

Our solution is calibration by a positive control (§3). Two editions of the same
dictionary must, by construction, share most of their cross-references; measuring how
much they actually share tells us what a descent signal *looks like* on this data and
this method, and gives every other pair a ceiling to be read against. With that ceiling
in hand, the cross-tradition comparisons become interpretable — and the answer to the
roadmap question is a qualified no: a shared core, not the same graph.

## 2. Data

Cross-reference markup differs by dictionary, so the graphs are extracted per source
convention. The Petersburg lexicon marks comparisons with `Vgl.`; Monier-Williams with
`cf.` in `<s>` tags; the Apte editions and Cappeller put `cf.` targets in `{#…#}` SLP1,
mixing true lemma pointers with multi-word quotes and cognates, which a parsing rule
(round 7) separates — a `{#…#}` is kept as a graph **edge** only when it is lemma-like
(a single SLP1 word, no spaces or periods), and everything else is routed to a
cross-reference-quote side file. The resulting directed networks (Table 1) are the unit
of analysis: each node is a normalised headword, each edge a `source → target` pointer.

**Table 1. Cross-reference networks by dictionary (normalised).**

| Dictionary | Marker | Edges | Source lemmas |
|---|---|---:|---:|
| Petersburg (PWG) | `Vgl.` | 22,937 | 11,857 |
| Monier-Williams (MW) | `cf.` | 7,637 | 6,974 |
| Apte revised, 1957 (AP) | `cf.` `{#…#}` | 609 | 604 |
| Apte 1890 (AP90) | `cf.` `{#…#}` | 444 | 432 |
| Cappeller (CAE) | `cf.` `{#…#}` | 190 | 160 |
| Benfey (BEN) | `cf.` | **0** | — |

*Source: [`xref-lineage.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dicts/xref-lineage.json)
(normalised graphs) and [`MICROSTRUCTURE_XREF_LINEAGE.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_XREF_LINEAGE.md);
raw pre-normalisation scan counts (AP90 446, CAE 196) are in
[`xref_hub_review.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/xref_hub_review.json)
(PWG: 123,366 entries scanned, 12,283 carrying a cross-reference). Note the CDSL codes:
**AP90 is the 1890 edition, AP the 1957 revision**. Benfey's `cf.` is purely cognate /
Roman-script, so it does **no internal Sanskrit cross-referencing** — a content fact,
not a markup gap.*

## 3. Method

### 3.1 Normalisation and intersection

Both ends of every edge are reduced to a common key: strip the compound-family marker
(PWG writes it `°`, MW writes it `-`, so `a°` ≡ `a-`), strip SLP1 accents and stray
hyphens, and deduplicate per dictionary. Two networks are then intersected on the set of
**source lemmas both dictionaries cross-reference** — there is no point asking whether
MW and PWG agree about a lemma only one of them points from. On that shared-source set we
report the number of identical `source → target` edges, the directed **inheritance rate**
for each dictionary (what fraction of *its* cross-references from shared sources the other
also makes), and the Jaccard overlap (Jaccard 1912). Edges are **directed**: a reciprocal
pointer in the
other dictionary does not count as a match. (The metric's definition and limits are
stated once for the series in P1, §3.6; this paper is its dedicated instantiation, and
treating structural overlap as multi-dimensional descent evidence follows the
digital-stemmatology precedent of Andrews and Macé 2013.) The normalisation is deliberately
conservative — a messy multi-part target that does not reduce cleanly simply fails to
match — so every number is a **floor**.

### 3.2 The positive control

Because overlap has no absolute scale, the method is anchored by a pair whose answer is
known. Apte 1890 (AP90) and the revised Apte (AP) are the same dictionary in two
editions; whatever descent does to a cross-reference graph, it must leave most of it
intact across an edition boundary. The overlap measured on AP × AP90 is therefore the
**edition-continuity ceiling** — the value the method assigns to genuine, near-total
inheritance — and every cross-tradition pair is read as a fraction of it.

### 3.3 The prefix-hub control

Before any pair is read, the most-referenced targets of each dictionary are classified.
A target that is a bare prefix or compound head — *a°*, *mahā°*, *su°*, *vi°* — is a
**prefix-convention hub**: it accumulates hundreds of incoming edges because the
dictionary marks compound families that way, not because those edges carry rare lexical
information. Such hubs inflate raw overlap between any two dictionaries that share the
convention, so they are labelled and held out of the lexical-core reading. This is the
*convention* axis of the companion methods paper (P3) intruding on the *content* signal,
and it must be subtracted before cross-reference overlap can speak to descent.

## 4. Results

### 4.1 The spectrum, against the control

**Table 2. Cross-reference overlap for every measurable dictionary pair.** Inheritance
rate is directed (a-rate / b-rate); the reading is the machine review label.

| Pair | Overlapping edges | a-rate / b-rate | Jaccard | Reading |
|---|---:|---|---:|---|
| **AP × AP90** | 182 | **85.5 % / 84.7 %** | **0.740** | edition-continuity (positive control) |
| AP × PWG | 23 | 34.3 % / 7.4 % | 0.065 | too sparse to read |
| AP × MW | 19 | 28.8 % / 23.2 % | 0.147 | sparse |
| CAE × MW | 11 | 24.4 % / 20.0 % | 0.124 | sparse |
| **MW × PWG** | 641 | **21.8 % / 9.1 %** | 0.069 | lexical shared core |
| AP90 × PWG | 11 | 14.7 % / 2.8 % | 0.024 | too sparse |
| CAE × PWG | 7 | 12.5 % / 1.8 % | 0.016 | too sparse |
| AP90 × MW | 10 | 11.2 % / 8.6 % | 0.051 | sparse |

*Source: [`xref-lineage.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dicts/xref-lineage.json)
and [`MICROSTRUCTURE_XREF_LINEAGE.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_XREF_LINEAGE.md).
The two remaining packet pairs, AP × CAE (1 edge) and AP90 × CAE (0 edges), are omitted
as empty.*

The control behaves as it must: two editions of Apte recover **~85 %** of each other's
cross-references, at Jaccard 0.74. That is the shape of descent — near-total preservation
of the pointer graph across an edition. Every other pair is read against it.

### 4.2 Monier-Williams and the Petersburg lexicon: a shared core

The headline pair is the largest. MW and PWG share 2,538 source lemmas; on those, MW
makes 2,946 cross-references and PWG makes 7,022, of which **641 are identical** edges.
That is an inheritance rate of **21.8 %** from the MW side (and 9.1 % from the denser PWG
side), at Jaccard 0.069. The number cuts both ways. It is far above chance — in the
≈300,000-headword union of the two dictionaries' key spaces, 641 coincident directed
pointers on a 2,538-lemma overlap is not what independent networks produce — so MW and
PWG are demonstrably **related**, as the
philology has always held. But it is barely a quarter of the edition-continuity ceiling,
and roughly four in five of MW's cross-references — even from lemmas PWG also
cross-references — go where PWG does not. The sample of genuinely shared edges is telling:
*ARi → aRi*, *Ayu → Ayus*, *Bala → bal* — variant-form and cognate-root pointers that two
competent Sanskrit lexicographers would each record independently. The verdict is a
**shared cross-reference core with large independent expansion in each tradition** —
common scholarly substrate, very possibly some borrowing, but not a network MW lifted
from Petersburg.

### 4.3 The hubs are convention, not content

The raw overlap would be higher, and misleadingly so, without the prefix-hub control.
PWG's most-referenced targets are not rare words but compound markers — *a°* (320 incoming
edges), *mahā°* (254), *su°* (160), *vi°* — each a hub that exists because Petersburg
records compound families by pointing to the bare prefix. Any dictionary that shares the
convention will appear to "agree" with PWG on these hubs while sharing no lexical
knowledge at all. Held out as convention artefacts, they stop inflating the lexical-core
reading, leaving the 641 shared edges to be adjudicated on their lexical merits.

### 4.4 A content finding: Benfey points nowhere inward

Benfey's dictionary records **zero** internal Sanskrit cross-references: its `cf.` slot
holds only cognates in other languages and Roman-script comparanda. This is not a markup
limitation the parser failed to read but a property of the dictionary — Benfey simply does
not build an internal pointer graph — and it means cross-reference descent is undefined
for any edge into or out of Benfey, however close the two dictionaries are on content or
convention.

## 5. Discussion

### 5.1 What cross-reference overlap can and cannot show

Read naively, the MW × PWG overlap could be told either way — "21.8 % shared, the networks
are related!" or "78 % divergent, MW built its own graph!" — and both spins are true and
useless. The positive control dissolves the ambiguity: 21.8 % is not "high" or "low" in
the abstract, it is *a quarter of what descent looks like* on this method, measured on the
same data. Calibration, not the raw number, is what licenses the reading. This is the
general lesson — a structural-overlap measure means nothing without a known-answer pair to
scale it, and the cheapest such pair is two editions of one dictionary.

### 5.2 Relation to the companion findings

The cross-reference graph is a fourth coordinate on the inheritance problem the series
studies, and it decomposes the same way the methods companion (P3) requires. The
prefix-convention hubs (§4.3) are a pure *convention*-axis effect — shared marking style
that fakes content overlap — and must be subtracted before the graph speaks to descent;
the 641 shared lexical edges are a *content*-axis signal, a floor for relatedness, never
on their own proof of copying. The AP × AP90 control is the same edition-continuity edge
that the sense-inheritance study (P2) reads as an Apte revision and the three-axis packet
(P3) scores at high content and microstructure: across senses, axes, and now pointer
graphs, the two Apte editions behave as one dictionary, which is exactly why they
calibrate the others. And Benfey's empty pointer graph (§4.4) is the cross-reference
analogue of the indigenous-microstructure paper's (P4) central move — a structural zero
that is a fact about the instrument's content, not a gap to be filled.

## 6. Limitations

- **Floor, not ceiling.** Conservative normalisation means unmatched messy targets only
  *lower* the measured overlap; the true shared core is at least as large as reported.
- **Directed edges.** Only `source → target` matches count; a reciprocal pointer in the
  other dictionary is not credited, which understates symmetric relatedness.
- **Density asymmetry.** PWG cross-references roughly three times as densely as MW
  (22,937 vs 7,637 edges), so the two directed inheritance rates are not comparable in
  magnitude and are reported separately rather than averaged.
- **Sparse pairs are unreadable.** Every cross-tradition pair except MW × PWG and the
  Apte control shares too few source lemmas (7–23 overlapping edges) to support a reading;
  they are reported for completeness only.
- **The labels are review prompts.** Edition-continuity, lexical-shared-core, prefix-
  convention, and too-sparse are machine triage classes over a 40-edge shared-core sample;
  the packet records no human lineage decision.
- **One positive control.** The calibration rests on a single same-dictionary pair (Apte);
  a second edition-continuity pair would strengthen the ceiling.

## 7. Conclusion

The graph a dictionary makes by pointing at itself is a real and measurable signal of
descent — but only once it is calibrated and cleaned. Two editions of Apte preserve 85 %
of their cross-references; against that ceiling, Monier-Williams and the Petersburg lexicon
share just 21.8 %, and that fraction, stripped of the prefix-convention hubs that
manufacture false agreement, resolves into a common scholarly core of variant and cognate
pointers rather than an inherited network. The same discipline the rest of this series
insists on holds here: overlap is a floor, not a copy; a structural signal earns a descent
claim only against a known-answer control and only after convention is subtracted from
content. Cross-references point inward, and read this way they point, faintly but
measurably, back along the line of descent.

## References (draft — author to finalise)

Andrews, Tara L., and Caroline Macé. 2013. "Beyond the Tree of Texts: Building an
Empirical Model of Scribal Variation through Graph Analysis of Texts and Stemmata."
*Literary and Linguistic Computing* 28 (4): 504–521.

Atkins, B. T. Sue, and Michael Rundell. 2008. *The Oxford Guide to Practical
Lexicography.* Oxford: Oxford University Press.

Jaccard, Paul. 1912. "The Distribution of the Flora in the Alpine Zone." *New
Phytologist* 11 (2): 37–50.

Wiegand, Herbert Ernst. 1989. "Der Begriff der Mikrostruktur: Geschichte, Probleme,
Perspektiven." In Hausmann, Reichmann, Wiegand and Zgusta (eds.), *Wörterbücher /
Dictionaries / Dictionnaires,* vol. 1 (HSK 5.1), 409–461. Berlin and New York: Walter de
Gruyter.

Zgusta, Ladislav. 1971. *Manual of Lexicography.* (Janua Linguarum, Series Maior 39.)
Prague: Academia; The Hague and Paris: Mouton.

**Primary digital source.** Cologne Digital Sanskrit Dictionaries (CDSL). Institute of
Indology and Tamil Studies, University of Cologne.
[`sanskrit-lexicon.uni-koeln.de`](https://www.sanskrit-lexicon.uni-koeln.de/).

**Companion papers (this series).**

Gasūns, M. (in preparation). *Measuring the Dictionary Family: A Traceable Measurement
Framework for Computational Lexicography* (P1 — owns the cross-reference-overlap metric
this paper instantiates, §3.6 there).

Gasūns, M. (in preparation). *Condensation, Not Inflation: Sense Inheritance in the
Sanskrit Dictionary Family, 1822–1957* (P2).

Gasūns, M. (in preparation). *Three Axes of Descent: Separating Content, Convention, and
Microstructure in Dictionary Inheritance* (P3).

Gasūns, M. (in preparation). *Grammar Without Tags: The Verbal-Root Microstructure of the
Indigenous Sanskrit Kośa* (P4).

Gasūns, M. (in preparation). *Order Is the Dictionary: A Macrostructural Model of the
Versified Synonymic Kośa* (P6).

*Bibliographic details are to be verified against the sources before submission.*

_Dr. Mārcis Gasūns_
