# Two Citation Registers and the Dictionary-to-Book Gap in the Cologne Digital Sanskrit Lexicon

*Draft manuscript for submission to a metalexicography venue (target: International
Journal of Lexicography). Empirical basis: the OBS-C finding
([`CITATION_REGISTERS.md`](../CITATION_REGISTERS.md)); siglum normalisation
[`scripts/lib/source-siglum.mjs`](../../scripts/lib/source-siglum.mjs) and the
reviewed alias table [`src/data/dict-source-aliases.json`](../../src/data/dict-source-aliases.json);
abbreviation-family candidate generator
[`scripts/obs/siglum_families.py`](../../scripts/obs/siglum_families.py). Companion to
the headword-redundancy study ([`paper_redundancy_and_descent.md`](paper_redundancy_and_descent.md))
and to the standing `INDIG-CITE` finding
([`MICROSTRUCTURE_ZERO_MEANING.md`](../MICROSTRUCTURE_ZERO_MEANING.md)). All counts are
reproducible from committed data; numbers herein are the 2026-06 snapshot.
Author: M. Gasūns (byline to finalise).*

---

## Abstract

A historical dictionary's authority rests in large part on its **source citations** —
the references to texts that license each sense. In a fully digitised dictionary
corpus these citations become a linking problem: how many can be resolved
automatically to the work and passage they name (the "dictionary-to-book" gap), and
do the constituent dictionaries even cite in the same way? We answer both questions
for the Cologne Digital Sanskrit Lexicon (CDSL), forty-three Sanskrit dictionaries in
a common markup. The European critical-apparatus tradition tags source references
explicitly: we count **1,234,530 such `<ls>` citations** (about 0.83 per entry), of
which **59.1–59.8 % carry a numeric locator** — book, chapter or verse — and are thus
resolvable in principle to a passage, while the remaining ~41 % (≈496,000 citations)
are bare source abbreviations. That bare-abbreviation residue is the measured ceiling
of the dictionary-to-book gap. The citations draw on a heavily skewed source
inventory: roughly 13,000 raw abbreviation strings fold to about 9,000 distinct
sigla, but only **2,166 sources are cited ten or more times** — the genuine working
apparatus — behind a long tail in which the fifty commonest sigla already account for
half of all citations. Critically, the `<ls>` tally measures only one **citation
register**. The indigenous Sanskrit-to-Sanskrit *kośa*s use **no `<ls>` tags at all**;
they cite by quoting a source work followed by the quotative particle *iti*. Counting
that construction shows the *Śabdakalpadruma* alone carrying ~69,000 source
references, the *Vācaspatya* ~22,000 and the *Kṛdantarūpamālā* ~6,000 — all invisible
to an `<ls>`-based measure. We conclude that the CDSL contains **two disjoint citation
systems**: a European apparatus that is roughly 60 % machine-resolvable and amenable
to a reviewed source-abbreviation registry, and an indigenous *iti*-quotation register
that is citation-dense but requires an entirely different resolution strategy. Per-
dictionary citation density is meaningless unless reported per register.

**Keywords:** historical lexicography; Sanskrit; source citation; reference linking;
citation apparatus; dictionary-to-book; abbreviation normalisation; digital
lexicography.

---

## 1. Introduction

Source citations are the evidential backbone of a scholarly dictionary: the
abbreviation *Rām.* or *MBh.* after a sense tells the reader on whose authority it
stands. When such a dictionary is digitised, its citations acquire a second life as
potential hyperlinks — from the lexical entry to the cited text and, ideally, to the
exact passage. Realising those links across a large historical corpus is the
"dictionary-to-book" problem, and its tractability is an empirical question: it
depends on how regular the citations are and on whether the source abbreviations can
be resolved to a controlled list of works.

This paper measures the problem for the Cologne Digital Sanskrit Lexicon (CDSL),
which encodes forty-three Sanskrit dictionaries in a shared markup with an explicit
source-citation tag. We ask three questions. *How many citations are there, and how
densely do the dictionaries cite?* *What fraction carry enough information — a
locator — to be resolved to a passage rather than merely to a work?* And *how large
and how skewed is the inventory of cited sources, once abbreviation variants are
normalised?* A fourth question proves to be prior to all of these: *do all the
dictionaries cite in the same way at all?* The answer — that two of the corpus's
lexicographic traditions use mutually unintelligible citation registers — reframes
every per-dictionary statistic and is, we argue, the paper's principal finding.

## 2. Background

### 2.1 The `<ls>` apparatus

The CDSL markup provides an `<ls>` ("literary source") element wrapping a source
reference within an entry. In the European Indological dictionaries this is the
machine-readable trace of the critical apparatus: *Rām.*, *MBh.*, *RV.*, *Pāṇ.*,
often with a locator (*Bhag. 10. 33*). A standing effort within the project — the
"dictionary-to-book" link-target work — aims to turn these into click-throughs to
scanned source pages; its feasibility is exactly what a corpus-level resolvability
measurement quantifies.

### 2.2 Two traditions of citing

The indigenous Sanskrit lexicographic tradition does not use a European apparatus.
The *kośa*s cite by quotation: a phrase or definition is given and closed with the
quotative particle *iti* followed by the name of the authority — *iti Śabdaratnāvalī*,
*ity Amaraḥ*, *iti Manuḥ*. The project has already recorded, qualitatively, that the
*Śabdakalpadruma* and *Vācaspatya* are "among the densest citers in the corpus yet
score zero on an `<ls>`-based counter" (the `INDIG-CITE` finding). The present study
supplies the numbers behind that observation and draws out its consequence for any
corpus-wide citation statistic.

## 3. Data and method

### 3.1 Counting `<ls>` citations and their resolvability

We extract every `<ls>…</ls>` element from the canonical source files
(`csl-orig/v02`) of all forty-three dictionaries. A citation is classed as
**locator-bearing** if its content contains a numeral (a book, chapter, verse or page
reference), and **bare** otherwise. Locator presence is a generous proxy for
resolvability — it is a necessary, not sufficient, condition for linking to a passage
— so the locator share is reported as the *upper* bound of a resolvability band. The
lower bound additionally requires the citation's source abbreviation to be a member
of the established source set (§3.2).

### 3.2 Normalising the source inventory

Source abbreviations vary by dictionary house style. Two folding layers reduce them
to canonical identities. The first is a **diacritic-and-case fold** (`foldSiglum`):
*MBh* and *MBH* both fold to *mbh*, *RV* and *ṚV* to *rv*. The second is a reviewed
**abbreviation-family** layer: length variants of one work — *R.*, *Rām.*, *Rāmāy.* →
Rāmāyaṇa — that the fold cannot catch. Because abbreviation merging is error-prone, it
is generated as *review candidates* (a prefix-clustering tool over the fold-keys) and
adjudicated by hand into a curated alias table; the tool deliberately surfaces false
candidates (the *Rājataraṅgiṇī* and *Rājanighaṇṭu* sigla share a prefix but are
distinct works) so that they are *split*, not merged.

### 3.3 The indigenous register

For the *kośa*s we count the quotative construction directly: occurrences of *iti*
and its pre-vocalic sandhi form *ity* at a word boundary (preceded by space or a
quotation mark), which excludes the many in-word substrings (*prīti*, *nīti*). This is
a register *indicator*, not an exact citation count — it includes some grammatical
*iti* — but the contrast it reveals between registers is too large to be an artefact.

### 3.4 What the method does not claim

Locator presence is not verified linkability; a numeral may be ambiguous without a
resolved siglum. The *iti* count is an upper proxy for indigenous citations. Siglum
disambiguation is intrinsically hard, which is why merges are reviewed rather than
automatic. These limits are revisited in §6.

## 4. Results

### 4.1 Volume and per-dictionary density (the `<ls>` register)

The European dictionaries carry **1,234,530 `<ls>` citations**, about **0.83 per
entry** corpus-wide, but density is very uneven (Table 1). The *Großes Petersburger
Wörterbuch* is the most citation-dense major dictionary at 4.63 citations per entry
(570,830 in total); Benfey, the Buddhist Hybrid Sanskrit dictionary and
Monier-Williams (311,933) follow.

**Table 1.** `<ls>` citation density, selected dictionaries.

| Dictionary | `<ls>` citations | per entry |
|---|---:|---:|
| PWG — Petersburg (große) | 570,830 | 4.63 |
| MW — Monier-Williams 1899 | 311,933 | 1.09 |
| BEN — Benfey 1866 | — | 2.81 |
| BHS — Buddhist Hybrid Sanskrit | — | 2.71 |
| AP — Apte 1957 | — | 0.69 |

### 4.2 The dictionary-to-book gap is ~41 %

**59.8 % of `<ls>` citations carry a locator**; requiring in addition an established
source siglum lowers this only marginally, to **59.1 %** — that is, almost every
locator-bearing citation already uses a recognised source. The resolvability band is
therefore tight, **59.1–59.8 %**, and robust. Its complement is the measured ceiling
of the **dictionary-to-book gap: ~41 % of citations, roughly 496,000, are bare source
abbreviations** that cannot be resolved to a passage without further work. The figure
is encouraging for automation — a clear majority of the European apparatus is
mechanically linkable — and it sizes the manual residue precisely.

### 4.3 A small working apparatus behind a long tail

The cited-source inventory is steeply skewed. About **13,000 raw abbreviation strings**
fold to roughly **9,000 distinct sigla**, but only **2,166 sources are cited ten or
more times** — the genuine working apparatus — while the remainder are rare or one-off
references. Concentration is extreme: the **fifty commonest sigla account for about
half of all citations**, led by the Rāmāyaṇa, the Mahābhārata, the lexicographers
(*L.*), Pāṇini, the Ṛgveda and the major *purāṇa*s. The diacritic/case fold alone
resolves the largest variant pairs (Mahābhārata *MBH*+*MBh* = 75,548; Ṛgveda *ṚV*+*RV*
= 32,316); abbreviation-family review then collapses length-variant families
(*Kathāsaritsāgara*, *Suśruta*, *Raghuvaṃśa* and others) further. We adjudicated the
high-frequency families into a reviewed alias table of canonical works, keeping
distinct works that merely share a prefix apart. The practical implication is that a
**reviewed source-abbreviation registry of low-thousands of entries suffices to
resolve the great majority of the European apparatus**.

### 4.4 The hidden register: indigenous *iti*-citation

The `<ls>` count omits an entire citation system. The Sanskrit-to-Sanskrit *kośa*s
carry **no `<ls>` tags whatever**, yet cite densely by quotation (Table 2): the
*Śabdakalpadruma* records ~69,000 *iti*-citations, the *Vācaspatya* ~22,000, and the
*Kṛdantarūpamālā* the highest density in the corpus at over three per entry. An
`<ls>`-only measure therefore mis-ranks precisely these dictionaries as
citation-poor when they are among the richest.

**Table 2.** Indigenous *iti*-register citation (zero `<ls>` in every case).

| Dictionary | `<ls>` | *iti*-citations | per entry |
|---|---:|---:|---:|
| KRM — *Kṛdantarūpamālā* | 0 | 6,449 | 3.13 |
| SKD — *Śabdakalpadruma* | 0 | 69,215 | 1.63 |
| VCP — *Vācaspatya* | 0 | 22,070 | 0.44 |

These dictionaries cite indigenous authorities — Amara, Trikāṇḍaśeṣa, Śabdaratnāvalī,
Viśva, Medinī, Manu — through the *iti* construction. Their dictionary-to-book problem
is different *in kind*: linking *iti X* to an indigenous source lexicon or text, not
resolving a chapter-and-verse locator.

### 4.5 Two disjoint citation systems

The corpus thus contains two non-overlapping citation registers. The 59 %
resolvability result and the source-abbreviation registry apply to the European
`<ls>` register alone; the indigenous register is invisible to them and requires its
own normaliser keyed on the *iti*-source construction. **Any per-dictionary citation
statistic that does not state its register is therefore ill-defined** — the apparent
"citation-poverty" of a *kośa* is an artefact of measuring the wrong tradition's
markup.

## 5. Discussion

**For digital lexicography.** The dictionary-to-book task is, for the European
apparatus, about 60 % mechanisable: a clear majority of citations carry a locator and
draw on a working set of ~2,000 sources that a reviewed registry can resolve. The
~41 % bare-abbreviation residue sizes the manual or heuristic effort that remains. The
abbreviation-normalisation pipeline — automatic diacritic/case fold plus a reviewed
alias table grown from machine-generated candidates — is reusable infrastructure for
any citation-linking project, and the deliberate refusal to auto-merge prefix-similar
sigla is the methodological safeguard that keeps distinct works distinct.

**For the history and typology of lexicography.** That two lexicographic traditions
cite in mutually unintelligible registers is a finding of comparative metalexicography,
not merely a markup detail. The European critical apparatus and the indigenous
*iti*-quotation are different technologies of authority, and the CDSL — by placing
them in one corpus — lets the difference be *measured*: register, density, and source
inventory are now quantities rather than impressions.

**A methodological warning.** Aggregated dictionary statistics that sum across
dictionaries of different citation traditions will systematically under-credit the
indigenous lexica. Register must be a controlled variable in any cross-dictionary
citation comparison.

## 6. Limitations and future work

Locator presence bounds resolvability from above; verifying that a located citation
actually links to a retrievable passage (matching the resolved siglum to a digitised
edition with the right reference scheme) is the next step and will lower the figure.
The *iti* proxy over-counts indigenous citations by including grammatical and
derivational *iti*; a parser keyed on *iti + proper-name* would tighten it. The
reviewed alias table covers the high-frequency families; the long tail of low-frequency
sigla remains in the review queue by design. Finally, the two registers should be
unified at the level of the cited *work*, so that a source cited as *MBh.* in the
apparatus register and quoted *iti …* in a *kośa* is recognised as the same authority —
the prerequisite for a corpus-wide, register-neutral citation graph.

## 7. Conclusion

The Cologne Digital Sanskrit Lexicon contains over 1.2 million explicit source
citations, of which a tight majority — about 59 % — are resolvable in principle to a
passage, leaving a measured dictionary-to-book gap of some 496,000 bare
abbreviations, all drawing on a working apparatus of roughly two thousand sources.
But this European apparatus is only one of two citation registers: the indigenous
*kośa*s cite as densely again through *iti*-quotation and are wholly invisible to it.
Citation density, resolvability, and source inventory are all well-defined only once
register is fixed. Recognising the two registers — and building a reviewed source
registry for each — is the precondition for turning a digitised dictionary corpus into
a navigable web of dictionary-to-source links.

---

## References (draft — author to finalise)

*Primary dictionaries* (as digitised in the Cologne Digital Sanskrit Lexicon):
Böhtlingk, O. and Roth, R., *Sanskrit-Wörterbuch* [PWG] (St Petersburg, 1855–1875);
Monier-Williams, M., *A Sanskrit-English Dictionary* (Oxford, 1899); Benfey, T.
(1866); Apte, V. S. (rev. edn 1957–1959); Edgerton, F., *Buddhist Hybrid Sanskrit
Dictionary* (1953); Rādhākānta Deva, *Śabdakalpadruma* (1822–1858); Tarkavācaspati,
*Vācaspatya* (1873–1884); Bhaṭṭoji Dīkṣita (attrib.), *Kṛdantarūpamālā*.

*Cited Sanskrit sources referenced in the apparatus* (selection): *Rāmāyaṇa*,
*Mahābhārata*, *Ṛgveda*, Pāṇini's *Aṣṭādhyāyī*, *Bhāgavata-purāṇa*,
*Kathāsaritsāgara*, *Suśruta-saṃhitā*, *Raghuvaṃśa*.

*Resource.* Kapp, D. and Malten, T., *Cologne Digital Sanskrit Dictionaries*,
University of Cologne (sanskrit-lexicon.uni-koeln.de).

*Secondary metalexicography (to be completed).* References on the citation/illustrative
apparatus of historical dictionaries, reference-linking in digital editions, and
comparative dictionary typology — to be added on submission.
[TODO: author to insert specific citations.]
