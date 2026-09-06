_Created: 11-06-2026 · Last updated: 06-09-2026_

# Two Citation Registers and the Dictionary-to-Book Gap in the Cologne Digital Sanskrit Lexicon

*Draft manuscript for submission to a metalexicography venue (target: International
Journal of Lexicography). Empirical basis: the OBS-C finding
([`CITATION_REGISTERS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/CITATION_REGISTERS.md)); siglum normalisation
[`scripts/lib/source-siglum.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/source-siglum.mjs) and the
reviewed alias table [`src/data/dict-source-aliases.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dict-source-aliases.json);
abbreviation-family candidate generator
[`scripts/obs/siglum_families.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/obs/siglum_families.py). Companion to
the headword-redundancy study ([`paper_redundancy_and_descent.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_redundancy_and_descent.md))
and to the standing `INDIG-CITE` finding
([`MICROSTRUCTURE_ZERO_MEANING.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_ZERO_MEANING.md)). All corpus
counts are regenerated from the committed artifact
[`data/obs/citation_registers.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/obs/citation_registers.json)
(built by [`citation_register_gaps.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/obs/citation_register_gaps.py));
numbers herein are the 2026-07 snapshot. Siglum-inventory figures (§4.3) are the
2026-06 siglum pass. Referee pass 2026-06-13
([REFEREE_OBS_RC.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/REFEREE_OBS_RC.md));
revision executed 2026-07-02 ([PR #184](https://github.com/sanskrit-lexicon/csl-atlas/pull/184))
with counts regenerated from the committed artifact
([PR #187](https://github.com/sanskrit-lexicon/csl-atlas/pull/187)); author-voice pass 2026-07-11
([SIGNOFF_A08_author_pass.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/SIGNOFF_A08_author_pass.md));
second author-voice pass 2026-09-06 (Pass 2 in the same
[SIGNOFF_A08_author_pass.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/SIGNOFF_A08_author_pass.md)).
Author: Mārcis Gasūns, independent scholar
([ORCID 0000-0003-4513-884X](https://orcid.org/0000-0003-4513-884X)), gasyoun@ya.ru.*

---

## Abstract

A historical dictionary's authority rests in large part on its source citations —
the references to texts that license each sense. In a fully digitised dictionary
corpus these citations become a linking problem: how many can be resolved
automatically to the work and passage they name (the "dictionary-to-book" gap), and
do the constituent dictionaries even cite in the same way? I answer both questions
for the Cologne Digital Sanskrit Lexicon (CDSL), forty-four Sanskrit dictionaries in
a common markup. The European critical-apparatus tradition tags source references
explicitly: I count 1,245,644 such `<ls>` citations (about 0.83 per entry), of
which 59.3 % carry a numeric locator — book, chapter or verse — and are thus
resolvable in principle to a passage, while the remaining ~41 % (≈507,000 citations)
are bare source abbreviations. That bare-abbreviation residue is the measured ceiling
of the dictionary-to-book gap. The citations draw on a heavily skewed source
inventory: roughly 13,000 raw abbreviation strings fold to about 9,000 distinct
sigla, but only 2,166 sources are cited ten or more times — the genuine working
apparatus — behind a long tail in which the fifty commonest sigla already account for
half of all citations. But the `<ls>` tally measures only one citation
register. The indigenous Sanskrit-to-Sanskrit *kośa*s use no `<ls>` tags at all;
they cite by quoting a source work followed by the quotative particle *iti*. Counting
that construction shows the *Śabdakalpadruma* alone carrying ~80,000 source
references, the *Vācaspatya* ~15,600 and the *Kṛdantarūpamālā* ~12,400 — all invisible
to an `<ls>`-based measure. I conclude that the CDSL contains two disjoint citation
systems: a European apparatus that is roughly 60 % machine-resolvable and amenable
to a reviewed source-abbreviation registry, and an indigenous *iti*-quotation register
that is citation-dense but requires an entirely different resolution strategy.
Per-dictionary citation density is meaningless unless reported per register.

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
which encodes forty-four Sanskrit dictionaries in a shared markup with an explicit
source-citation tag. I ask three questions. *How many citations are there, and how
densely do the dictionaries cite?* *What fraction carry enough information — a
locator — to be resolved to a passage rather than merely to a work?* And *how large
and how skewed is the inventory of cited sources, once abbreviation variants are
normalised?* A fourth question proves to be prior to all of these: *do all the
dictionaries cite in the same way at all?* The answer — that two of the corpus's
lexicographic traditions use mutually unintelligible citation registers — reframes
every per-dictionary statistic and is, I argue, the paper's principal finding.

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

I extract every `<ls>…</ls>` element from the canonical source files
(`csl-orig/v02`) of all forty-four dictionaries. A citation is classed as
*locator-bearing* if its content contains a numeral (a book, chapter, verse or page
reference), and *bare* otherwise. Locator presence is a generous proxy for
resolvability — it is a necessary, not sufficient, condition for linking to a passage
— so the locator share is reported as the *upper* bound of a resolvability band. The
lower bound additionally requires the citation's source abbreviation to be a member
of the established source set (§3.2).

### 3.2 Normalising the source inventory

Source abbreviations vary by dictionary house style. Two folding layers reduce them
to canonical identities. The first is a *diacritic-and-case fold* (`foldSiglum`):
*MBh* and *MBH* both fold to *mbh*, *RV* and *ṚV* to *rv*. The second is a reviewed
*abbreviation-family* layer: length variants of one work — *R.*, *Rām.*, *Rāmāy.* →
Rāmāyaṇa — that the fold cannot catch. Because abbreviation merging is error-prone, it
is generated as *review candidates* (a prefix-clustering tool over the fold-keys) and
adjudicated by hand into a curated alias table; the tool deliberately surfaces false
candidates (the *Rājataraṅgiṇī* and *Rājanighaṇṭu* sigla share a prefix but are
distinct works) so that they are *split*, not merged.

### 3.3 The indigenous register

For the *kośa*s I count the quotative construction directly: occurrences of *iti*
and its pre-vocalic sandhi form *ity* at a word boundary — not adjacent to a Latin
letter on either side — which excludes the many in-word substrings (*prīti*, *nīti*)
while still counting quotatives that sit directly after markup or punctuation. The
markup-aware boundary matters: the *Kṛdantarūpamālā* wraps its Sanskrit in `<s>…</s>`
tags, so most of its sūtra-citing *iti* follows a tag close, and a naive
space-preceded rule would miss some two-thirds of it. This is a register *indicator*,
not an exact citation count — it includes some grammatical *iti* — but the contrast
it reveals between registers is too large to be an artefact.

### 3.4 What the method does not claim

Locator presence is not verified linkability; a numeral may be ambiguous without a
resolved siglum. The *iti* count is an upper proxy for indigenous citations. Siglum
disambiguation is intrinsically hard, which is why merges are reviewed rather than
automatic. These limits are revisited in §6.

## 4. Results

### 4.1 Volume and per-dictionary density (the `<ls>` register)

The European dictionaries carry 1,245,644 `<ls>` citations, about 0.83 per
entry corpus-wide, but density is very uneven (Table 1). The *Großes Petersburger
Wörterbuch* is the most citation-dense major dictionary at 4.61 citations per entry
(568,730 in total); Benfey, the Buddhist Hybrid Sanskrit dictionary and
Monier-Williams (312,160) follow.

**Table 1.** `<ls>` citation density, selected dictionaries.

| Dictionary | `<ls>` citations | per entry |
|---|---:|---:|
| PWG — Petersburg (große) | 568,730 | 4.61 |
| MW — Monier-Williams 1899 | 312,160 | 1.09 |
| BEN — Benfey 1866 | 48,603 | 2.81 |
| BHS — Buddhist Hybrid Sanskrit | 48,419 | 2.71 |
| AP — Apte 1957 | 62,672 | 0.69 |

*All figures from the committed artifact
[`data/obs/citation_registers.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/obs/citation_registers.json),
generated by [`citation_register_gaps.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/obs/citation_register_gaps.py) —
an `<ls>` count over `csl-orig/v02` reusing the extraction convention of
[`parse_cslorig.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/parse_cslorig.py).*

### 4.2 The dictionary-to-book gap is ~41 %

59.3 % of `<ls>` citations carry a locator (738,173 of 1,245,644); requiring in
addition an established source siglum lowers this only marginally — by 0.7
percentage points in the 2026-06 siglum pass (then 59.8 % → 59.1 %) — that is,
almost every locator-bearing citation already uses a recognised source. The
resolvability band is therefore tight, ≈58.6–59.3 %, and stable. Its complement
is the measured ceiling of the dictionary-to-book gap: ~41 % of citations, roughly
507,000, are bare source abbreviations that cannot be resolved to a passage
without further work. The figure
is encouraging for automation — a clear majority of the European apparatus is
mechanically linkable — and it sizes the manual residue precisely. I am not aware of
a published corpus-level locator-resolvability figure for a comparable historical
dictionary portal to set this against; the closest available comparator is
qualitative, not quantitative. Pre-critical (pre-twentieth-century) lexicography
treats locator-bearing citation as the exception rather than the rule, favouring bare
authority names over chapter-and-verse references, so a ~59 % locator rate, on a
nineteenth-century corpus, already exceeds the pre-digital expectation rather than
falling short of it.

### 4.3 A small working apparatus behind a long tail

The cited-source inventory is steeply skewed. About 13,000 raw abbreviation strings
fold to roughly 9,000 distinct sigla, but only 2,166 sources are cited ten or
more times — the genuine working apparatus — while the remainder are rare or one-off
references. Concentration is extreme: the fifty commonest sigla account for about
half of all citations, led by the Rāmāyaṇa, the Mahābhārata, the lexicographers
(*L.*), Pāṇini, the Ṛgveda and the major *purāṇa*s. The diacritic/case fold alone
resolves the largest variant pairs (Mahābhārata *MBH*+*MBh* = 75,548; Ṛgveda *ṚV*+*RV*
= 32,316); abbreviation-family review then collapses length-variant families
(*Kathāsaritsāgara*, *Suśruta*, *Raghuvaṃśa* and others) further. I adjudicated the
high-frequency families into a reviewed alias table of canonical works, keeping
distinct works that merely share a prefix apart. The practical implication is that a
reviewed source-abbreviation registry of low-thousands of entries suffices to
resolve the great majority of the European apparatus.

### 4.4 The hidden register: indigenous *iti*-citation

The `<ls>` count omits an entire citation system. The Sanskrit-to-Sanskrit *kośa*s
carry no `<ls>` tags whatever, yet cite densely by quotation (Table 2): the
*Śabdakalpadruma* records ~80,000 *iti*-citations, the *Vācaspatya* ~15,600, and the
*Kṛdantarūpamālā* the highest density in the corpus at six per entry. An
`<ls>`-only measure therefore mis-ranks precisely these dictionaries as
citation-poor when they are among the richest.

**Table 2.** Indigenous *iti*-register citation (zero `<ls>` in every case).

| Dictionary | `<ls>` | *iti*-citations | per entry |
|---|---:|---:|---:|
| KRM — *Kṛdantarūpamālā* | 0 | 12,359 | 6.00 |
| SKD — *Śabdakalpadruma* | 0 | 80,164 | 1.88 |
| VCP — *Vācaspatya* | 0 | 15,619 | 0.31 |

These dictionaries cite indigenous authorities — Amara, Trikāṇḍaśeṣa, Śabdaratnāvalī,
Viśva, Medinī, Manu — through the *iti* construction. Their dictionary-to-book problem
is different *in kind*: linking *iti X* to an indigenous source lexicon or text, not
resolving a chapter-and-verse locator.

The mis-ranking is not a rhetorical figure but a measured swap. Ranking all
forty-four CDSL dictionaries by `<ls>` density places the *Śabdakalpadruma*
tied for last — twenty-eight of the forty-four source files carry no `<ls>` tag
at all, and this measure cannot distinguish SKD from any of them, that is, from a
dictionary that cites nothing. Ranking the same forty-four by *iti*-density instead
places it 2nd of 44
([`data/obs/citation_registers.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/obs/citation_registers.json)) — behind
only the *Kṛdantarūpamālā*, ahead of every European dictionary in the corpus,
including the *Großes Petersburger Wörterbuch* that leads Table 1. A single-register
citation statistic therefore does not merely under-count SKD; it inverts its standing
in the corpus, from apparently citation-poorest to among the two or three most
citation-dense dictionaries in CDSL.

### 4.5 Two disjoint citation systems

The corpus thus contains two non-overlapping citation registers. The 59 %
resolvability result and the source-abbreviation registry apply to the European
`<ls>` register alone; the indigenous register is invisible to them and requires its
own normaliser keyed on the *iti*-source construction. Any per-dictionary citation
statistic that does not state its register is therefore ill-defined — the apparent
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
citations, all drawing on a working apparatus of roughly two thousand sources. Up to
a tight majority of them — 59.3 %, the locator-bearing upper bound — are resolvable
in principle to a passage, leaving a measured dictionary-to-book gap of at least some
507,000 bare abbreviations.
But this European apparatus is only one of two citation registers: the indigenous
*kośa*s cite densely through *iti*-quotation — on an indicator that includes some
grammatical *iti* and so bounds their citation rate from above — and are wholly
invisible to an `<ls>`-based measure.
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

*Secondary metalexicography.* Zgusta, Ladislav. 1971. *Manual of Lexicography.*
(Janua Linguarum, Series Maior 39.) Prague: Academia; The Hague and Paris: Mouton.
Hausmann, Franz Josef, Oskar Reichmann, Herbert Ernst Wiegand, and Ladislav Zgusta,
eds. 1989–1991. *Wörterbücher / Dictionaries / Dictionnaires: An International
Encyclopedia of Lexicography.* 3 vols. Berlin and New York: Walter de Gruyter.
Vogel, Claus. 1979. *Indian Lexicography.* (A History of Indian Literature, ed. Jan
Gonda, vol. 5, fasc. 4.) Wiesbaden: Otto Harrassowitz. [Same core metalexicography set
as the companion sense-inheritance paper (P2); Vogel is the standard reference for the
indigenous *kośa* citation tradition discussed in §4.4.]

_Dr. Mārcis Gasūns_
