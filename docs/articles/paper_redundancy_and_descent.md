# Redundancy and Descent in a Digitised Dictionary Family: A Headword-Level Stemma of the Cologne Digital Sanskrit Lexicon

*Draft manuscript for submission to a metalexicography venue (target: International
Journal of Lexicography). Empirical basis: the OBS-R finding
([`CORPUS_REDUNDANCY_GENEALOGY.md`](../CORPUS_REDUNDANCY_GENEALOGY.md)); generator
[`scripts/obs/headword_multiplicity.py`](../../scripts/obs/headword_multiplicity.py);
containment data `data/sanhw1_jaccard.csv`; inventory `data/dictionary_inventory.csv`.
Companion to Paper H (convention lineage,
[`paper_H_convention_vs_content_lineage.md`](paper_H_convention_vs_content_lineage.md)).
All counts are reproducible from committed data; numbers herein are the 2026-07
corpus snapshot (44 dictionaries, including the *Nāmamālikā* digitised 2026-06;
aggregate figures from `data/obs/headword_collapse.json`). Author: M. Gasūns.*

---

## Abstract

The Cologne Digital Sanskrit Lexicon (CDSL) aggregates forty-four historical
Sanskrit dictionaries into a single freely available corpus of roughly 1.5 million
lexical entries. That figure is routinely cited as a measure of the resource's
scale, but it conflates the size of the *digitised record* with the size of the
*lexical record*: a headword attested in nine dictionaries is counted nine times.
We measure, for the first time at the level of the whole corpus, how much of the
CDSL is independent attestation and how much is re-lexicalisation. Extracting the
canonical headword (`<k1>`, SLP1) from every entry — and, for four indigenous
*kośa*s that use a different markup, the synonym lemmas they list — we reduce
1,496,157 entries to **410,259 distinct headwords, a collapse of 3.65 : 1**. A
**majority (57.8 %) of distinct headwords occur in two or more dictionaries**; only
42.2 % (≈173,000 lemmas) are unique to a single work. Crucially, redundancy is not
uniform but *structured*: the general bilingual dictionaries re-lexicalise one
another almost completely (the Petersburg *kürzere Fassung* contributes 4.4 %
unique headwords, Monier-Williams 12.9 %), whereas specialised and corpus-bound
lexica retain large independent cores (the Buddhist Hybrid Sanskrit dictionary
57.6 %, the epigraphical glossary 57.5 %). Pairwise asymmetric containment, directed
by publication year and set size, recovers a coherent inheritance stemma in which
**Monier-Williams (1899) is a near-total absorber** of its predecessors (containing
88–94 % of nine other dictionaries' headword stock) and the Petersburg tradition
forms a second hub. We argue that headword multiplicity is a simple, reproducible
diagnostic for editing and consolidating aggregated digital dictionaries, and that
the structured-redundancy profile distinguishes derivative compilations from
dictionaries of genuine documentary value.

**Keywords:** historical lexicography; Sanskrit; dictionary aggregation; headword
overlap; dictionary genealogy; digital lexicography; redundancy.

---

## 1. Introduction

Aggregated digital dictionary portals present many historical dictionaries through
one interface and report their scale as a single summed entry count. The Cologne
Digital Sanskrit Lexicon (Kapp and Malten; *Cologne Digital Sanskrit Dictionaries*)
is a mature example: forty-four dictionaries whose printed editions span 1822–1993,
in Sanskrit-to-
English, -German, -French, -Latin and Sanskrit-to-Sanskrit, encoded in a common
markup and downloadable in full. Its often-quoted headline — on the order of 1.5
million entries — measures the digitisation effort, not the language. Two questions
follow that the summed count cannot answer. *How much of the aggregate is
independent lexical attestation, and how much is the same headword re-entered by
successive compilers?* And, where headwords recur, *can the direction of borrowing
be recovered from the data itself?*

These are classical questions of dictionary genealogy, normally pursued
philologically — through prefaces, known editorial dependencies, and spot
comparison. The CDSL makes them tractable quantitatively for an entire dictionary
family at once. This paper supplies the corpus-level measurement: a headword-multiplicity
census across all forty-four dictionaries, a profile of which dictionaries
contribute independent material, and a headword-containment stemma whose directed
edges reproduce, and extend, the derivation relationships recorded piecemeal in the
philological literature.

Our claim is deliberately bounded. Headword overlap is a *floor* for structural
relatedness, not proof of copying: two dictionaries may share a headword because one
copied the other, or because both record the same well-known word independently.
We therefore treat the stemma as the skeleton onto which finer, copying-specific
evidence — citation truncation, rare-term and hapax sharing, sense-level alignment
— is to be layered (Paper H; the `PET-MW-CITE` programme). What the headword level
*does* settle is the economics of the aggregate: how much of it is lexically novel.

## 2. Background

### 2.1 The dictionaries

The CDSL's bilingual core is the European Indological tradition: Wilson (1832),
Yates (1846), Goldstücker (1856, *a-* only), Benfey (1866), the first and second
editions of Monier-Williams (1872, 1899), Macdonell (1893), Cappeller (1891), and
Apte (1890; revised three-volume edition 1957–59). The German Petersburg tradition
comprises Böhtlingk and Roth's *Großes Petersburger Wörterbuch* (PWG, seven volumes
1855–1875) and Böhtlingk's *kürzere Fassung* (PW/PWK, seven volumes 1879–1889), with
Schmidt's *Nachträge* (1928) and Cappeller's German dictionary (1887). Alongside
these stand the indigenous Sanskrit-to-Sanskrit *kośa*s — the *Śabdakalpadruma*
(Rādhākānta Deva, 1822–58), the *Vācaspatya* (Tarkavācaspati, 1873–84),
Hemacandra's *Abhidhānacintāmaṇi* and its supplements, and the *Nāmamālikā*
(digitised into the CDSL in 2026) — and the specialised lexica:
Edgerton's Buddhist Hybrid Sanskrit dictionary (1953), Grassmann's *Wörterbuch zum
Rig-Veda* (1873), epigraphical and Purāṇic glossaries, and others.

### 2.2 Known dependencies

The philological record already documents specific borrowings, several of them noted
in the CDSL's own dictionary inventory: Yates is widely held to derive from Wilson;
the *Śabda-Sāgara* (1900) reproduces Wilson at the sense level; Cappeller's German
dictionary draws on the *kürzere Fassung*; and Monier-Williams's preface
acknowledges use of the early Petersburg fascicles. These are point observations.
What has been missing is a single, reproducible measurement that places every
dictionary in one quantitative relationship to every other.

## 3. Data and method

### 3.1 Source and headword key

We work directly from the canonical CDSL source files (`csl-orig/v02`), one per
dictionary. Each entry is delimited by an `<L>` marker; the canonical headword is the
`<k1>` field, already normalised to the SLP1 transliteration scheme and to a
canonical citation form (homonyms carry a separate `<h>` index, so the `<k1>` of
homographs is identical). We take, per dictionary, the **set of distinct `<k1>`
values** as its headword inventory.

Four dictionaries carry no `<k1>` field. The Hemacandra *kośa* family (`abch`,
`acph`, `acsj`) encodes synonym groups in a `<syns><s>…</s>` structure in which each
member is a lemma followed by a part-of-speech tag; the *Nāmamālikā* (`nmmb`) uses
the same `<syns>` field as a bare comma-separated lemma-POS list without the `<s>`
wrapper. For these we extract the synonym
lemmas, stripping the POS suffix. This format-aware extraction reproduces the
independently computed *sanhw1* lemma counts for these dictionaries exactly (e.g.
*Abhidhānacintāmaṇi* 11,584 lemmas), confirming that the two markup styles are being
read to the same standard.

A lemma's **multiplicity** is the number of dictionaries whose headword set contains
it. A lemma of multiplicity 1 is **dictionary-unique**; multiplicity ≥ 2 is
**shared**. We also report the **entry-to-lemma collapse ratio** (raw `<L>` count
divided by distinct headwords) and an **entry split-inflation** figure (raw `<L>`
count divided by the sum, over dictionaries, of distinct `<k1>` per dictionary),
which isolates the contribution of homonym and sub-entry splitting.

### 3.2 Containment and the direction of descent

For each ordered pair of dictionaries (A, B) we compute the **containment**
of A in B, `a_in_b = |A ∩ B| / |A|`: the fraction of A's headwords that recur in B.
High `a_in_b` with low `b_in_a` means A is largely a subset of B. To orient such an
edge into a descent claim we apply a conservative rule: where A ⊂ B and the two
differ in publication date, the **earlier (and typically larger superset)** member
is the ancestor. Contemporaneous or symmetric pairs are left undirected. This rule
reconstructs, rather than assumes, the dependencies of §2.2.

### 3.3 What the method does not claim

The measurement is at the level of the *headword*, not the sense or the gloss; two
dictionaries that list the same lemma with entirely different treatments still count
as sharing it. Containment is a floor for overlap and is not, by itself, evidence of
direct copying. Variant-folding is limited to the canonical `<k1>`/synonym forms;
finer normalisation (folding a final anusvāra or visarga) raises overlap and lowers
the corpus-wide independence figure from 42.2 % to 38.8 % (−3.4 points); this is
treated as a sensitivity bound rather than the headline, for the reasons given in
§6.

## 4. Results

### 4.1 The aggregate collapses by 3.65 : 1

Across the forty-four dictionaries, 1,496,157 `<L>` entries reduce to **410,259
distinct headwords** — a collapse of **3.65 : 1**. Homonym-normalisation alone (the
sum of per-dictionary distinct headword sets, before cross-dictionary merging) is
1,307,338, an **entry split-inflation of 1.144**: roughly one entry in eight is a
homonym or sub-entry split rather than a distinct headword. This split-inflation is
the corpus-wide reflex of the macrostructural trade-off documented elsewhere in this
project (Paper on microstructure, M1–M2): Monier-Williams promotes derivatives and
preverb forms to headword status (194,084 distinct `<k1>`) where the Petersburg
dictionaries nest them.

### 4.2 The record is majority-redundant

**57.8 % of distinct headwords occur in two or more dictionaries; 42.2 %
(173,139 lemmas) are unique to a single dictionary.** The multiplicity
distribution has a long high-frequency tail — a pan-lexical core of common words
recorded by almost every dictionary — and a large body of singletons. The headline
re-framing is therefore: the CDSL's ~1.5 million entries reduce to ~410,000 distinct
headwords, of which only some **173,000 are dictionary-unique**, the rest being
re-lexicalisation of a shared core. "Dictionary-unique" is a floor for novelty, not a
count of independent attestation: a headword shared by several dictionaries may be
independently recorded in each rather than copied (§3.3), so the count of
*independently attested* lemmas lies somewhere above 173,000 — its exact value is a
copying-level question, not a headword-level one.

### 4.3 Redundancy is structured, not uniform

Per-dictionary **unique contribution** — the count and share of a dictionary's
headwords found in no other CDSL dictionary — separates two clear populations
(Table 1).

**Table 1.** Unique-headword share, selected dictionaries (mutually derivative core
vs. independent lexica).

| Dictionary | Unique % | Reading |
|---|---:|---|
| PWG — Petersburg (große) | 1.9 | re-lexicalised by the family |
| YAT — Yates 1846 | 2.8 | derivative (see §4.4) |
| PW — Petersburg (kürzere) | 4.4 | re-lexicalised by the family |
| MW72 — Monier-Williams 1872 | 4.7 | subsumed by MW 1899 |
| MW — Monier-Williams 1899 | 12.9 | the great compiler-hub |
| AP — Apte 1957 | 34.7 | idiom/compound expansion |
| SKD — Śabdakalpadruma | 37.1 | indigenous kośa |
| PUI — Purāṇa Index | 38.6 | corpus-bound proper names |
| ACC — Aufrecht catalogue | 43.3 | bibliographic |
| IEG — Indian Epigraphical Glossary | 57.5 | epigraphic vocabulary |
| BHS — Buddhist Hybrid Sanskrit | 57.6 | a distinct register |

The general bilingual dictionaries we expect on philological grounds to be
derivative score very low; the specialised and corpus-bound lexica score high. The
metric thus validates itself against prior knowledge and supplies a quantitative
criterion: *a dictionary's independent contribution to the aggregate is indexed by
its unique headwords, not by its entry count.* This indexes independence, not worth:
a comprehensive general dictionary scores low unique-% precisely because it records
the shared core that other dictionaries also record, which is a service, not a
defect. What the metric does isolate is irreplaceability — Edgerton's Buddhist
Hybrid Sanskrit dictionary and the epigraphical glossary, modest in size, hold
vocabulary no other CDSL member supplies.

### 4.4 An inheritance stemma rooted in Monier-Williams

Directed containment (§3.2) recovers a coherent stemma (Table 2). **Monier-Williams
(1899) is a near-total absorber**: it contains 88–94 % of the headword stock of nine
other dictionaries, with the reverse containment small in every case — the signature
of a late, large compiler that gathered its predecessors. A **second hub** is the
Petersburg *kürzere Fassung* (PW, 1879), which contains the bulk of Cappeller's
German dictionary (0.945), Macdonell, and Benfey; PW itself stands downstream of the
*Großes Petersburger Wörterbuch* (1855–75). The English line runs Wilson (1832) →
Yates (1846) (mutual containment ≈ 0.91) and Wilson → *Śabda-Sāgara* (1900)
(Wilson ⊆ SHS = 0.953).

**Table 2.** Strongest directed containment edges (A ⊂ B; direction by year + size),
with the reverse-containment column and both denominators — the pair that turns "MW
is a near-total absorber" from asserted into shown: `a_in_b` is large while `b_in_a`
is small in every row.

| A ⊂ B | `a_in_b` (\|A∩B\|/\|A\|) | `b_in_a` (\|A∩B\|/\|B\|) | \|A\| | \|B\| | \|A∩B\| | Years (A / B) | Reading |
|---|---:|---:|---:|---:|---:|---|---|
| BOP ⊂ MW | 0.940 | 0.041 | 8,505 | 194,084 | 7,995 | 1847 / 1899 | absorbed by MW |
| BEN ⊂ MW | 0.937 | 0.082 | 17,036 | 194,084 | 15,969 | 1866 / 1899 | absorbed by MW |
| MD ⊂ MW | 0.927 | 0.096 | 20,103 | 194,084 | 18,637 | 1893 / 1899 | absorbed by MW |
| ARMH ⊂ MW | 0.929 | 0.032 | 6,673 | 194,084 | 6,196 | 1861 / 1899 | kośa stock taken into MW |
| ABCH ⊂ MW | 0.925 | 0.055 | 11,584 | 194,084 | 10,711 | 1896 / 1899 | kośa stock taken into MW |
| GRA ⊂ MW | 0.878 | 0.050 | 11,108 | 194,084 | 9,752 | 1873 / 1899 | Vedic stock taken into MW |
| CCS ⊂ PW | 0.945 | 0.180 | 28,751 | 151,349 | 27,176 | 1887 / 1879 | Cappeller (Ger.) from the *kürzere Fassung* |
| WIL ⊂ SHS | 0.953 | 0.896 | 43,939 | 46,730 | 41,854 | 1832 / 1900 | Śabda-Sāgara reproduces Wilson |

*Source: [`data/sanhw1_jaccard.csv`](../../data/sanhw1_jaccard.csv) (intersection,
`a_in_b`, `b_in_a`, `size_a`, `size_b` columns), already committed by the containment
generator; no new computation. At these set sizes the containment ratios are stable
point estimates: for the smallest numerator set in the table (BOP, |A| = 8,505), the
Wilson 95 % confidence interval on `a_in_b` = 0.940 is [0.935, 0.945], and every
other row's interval is at least as tight, so intervals are omitted from the table.*

Read against the reverse column, the asymmetry that "absorption" only asserted before
is now visible directly: MW contains 88–94 % of nine smaller/earlier dictionaries'
headwords while those dictionaries contain at most 9.6 % of MW's — a near-total,
one-directional absorption, not a coincidental overlap. The WIL ⊂ SHS edge is the
exception that proves the rule: with `b_in_a` = 0.896 alongside `a_in_b` = 0.953, the
two dictionaries are near-mutual supersets of each other, which is exactly the
near-verbatim reproduction the microstructural companion study (gloss overlap 0.906,
Paper P2 §6) independently confirms. The stemma is consistent with the philological
record (§2.2) and quantifies it: the Monier-Williams dictionary is not merely *a*
large dictionary but the documentary sink of the nineteenth-century tradition, while
the Petersburg works form the upstream reservoir.

### 4.5 The kośas re-group, they do not extend

A striking corollary emerges once the indigenous *kośa*s are parsed correctly. The
*Abhidhānacintāmaṇi* supplies 11,584 synonym lemmas but **only 3.3 % are unique** to
it (its supplements 14.1 % and 7.6 %). A synonym thesaurus, by its nature, re-groups
words that are *already attested* elsewhere into semantic sets; it adds organisation,
not vocabulary. The newly digitised *Nāmamālikā* is the partial exception (23.0 %
of its 2,265 lemmas are unique), a reminder that the re-grouping profile is a
tendency of the genre, strongest in the large thesauri, not a law. This is the mirror image of the citation-driven specialised lexica
of §4.3, and it cautions against reading a *kośa*'s size as documentary breadth.

## 5. Discussion

**For digital lexicography.** Headword multiplicity is a cheap, reproducible audit
for any aggregated dictionary portal. It converts an undifferentiated "entry count"
into an actionable map: which dictionaries are largely subsumed by others (and could
be presented as views rather than independent sources), where consolidation or
de-duplication would reduce maintenance burden without lexical loss, and which small
dictionaries carry disproportionate unique value and warrant priority in curation and
quality control. The 3.65 : 1 collapse and 57.8 % redundancy quantify what portal
users intuit — that "more dictionaries" is not "more words."

**For Indology.** The independent core — on the order of 173,000 dictionary-unique
lemmas, concentrated in the specialised and indigenous lexica — is the part of the
CDSL that no other member can supply. Identifying it is a prerequisite for any corpus
or treebank that needs a defensible lexical inventory, and for editorial decisions
about which dictionaries to prioritise for correction (a question taken up, on the
process side, by the companion OBS-Q study of correction sustainability).

**For dictionary history.** The headword stemma offers an objective, whole-family
complement to preface-based genealogy. It does not replace philology — containment is
a floor, not proof — but it tells the philologist exactly where to look: the directed
edges of Table 2 are the hypotheses that citation-truncation and rare-term tests
(Paper H) should now confirm or refute as *copying* rather than mere *overlap*.

## 6. Limitations and future work

The analysis is at the headword level; sense-level redundancy (whether shared
headwords also share glosses) is the natural next measurement and is under way in the
sense-alignment work (R2). Containment establishes overlap, not direction of copying:
the year-plus-size heuristic orients edges plausibly but conflates "B absorbed A"
with "B and A drew on a common source"; the discriminating evidence is
copying-specific (citation truncation, shared rare readings), addressed in Paper H.
Variant-folding is conservative (canonical `<k1>`/synonym forms only); a final
anusvāra/visarga-folding pass (stripping a trailing SLP1 `M` or `H` before comparing
headwords —
[`headword_multiplicity.py fold_sensitivity()`](../../scripts/obs/headword_multiplicity.py))
lowers the independence figure by **3.4 points** (42.2 % → 38.8 %; 410,259 →
363,552 distinct folded lemmas). This is
a sensitivity bound reported here rather than adopted as the headline: the fold
conflates grammatically distinct forms (a nominative-neuter *-am* and a genuine
visarga-final *-aḥ* headword are different words, not spelling variants), so the
post-fold figure is a lower bound on independence, not a better estimate of it.
Finally, multiplicity treats all
attestations as equal; weighting by corpus frequency (via a future
dictionary-to-corpus join) would distinguish a lemma shared because it is common from
one shared because it was copied.

## 7. Conclusion

Behind the Cologne Digital Sanskrit Lexicon's 1.5 million entries lie roughly 410,000
distinct headwords, of which a majority are shared across dictionaries and only some
173,000 are unique. Redundancy is structured: the general bilingual dictionaries
re-lexicalise one another, with Monier-Williams (1899) as their documentary sink and
the Petersburg dictionaries as the upstream reservoir, while specialised and
indigenous lexica retain the corpus's irreplaceable independent vocabulary.
Headword multiplicity is thus both a practical audit for aggregated digital
dictionaries and an objective entry point to the genealogy of a historical dictionary
family.

---

## References

*Primary dictionaries* (as digitised in the Cologne Digital Sanskrit Lexicon):
Wilson, H. H. (1832); Yates, W. (1846); Benfey, T. (1866); Böhtlingk, O. and Roth, R.,
*Sanskrit-Wörterbuch* [PWG] (St Petersburg, 1855–1875); Böhtlingk, O.,
*Sanskrit-Wörterbuch in kürzerer Fassung* [PWK] (St Petersburg, 1879–1889);
Monier-Williams, M., *A Sanskrit-English Dictionary* (Oxford, 1872; 2nd edn 1899);
Macdonell, A. A. (1893); Cappeller, C. (1891); Apte, V. S. (1890; rev. edn, ed.
P. K. Gode et al., Poona, 1957–1959); Edgerton, F., *Buddhist Hybrid Sanskrit
Dictionary* (New Haven, 1953); Grassmann, H., *Wörterbuch zum Rig-Veda* (1873);
Rādhākānta Deva, *Śabdakalpadruma* (1822–1858); Tarkavācaspati, *Vācaspatya*
(1873–1884); Hemacandra, *Abhidhānacintāmaṇi*; *Nāmamālikā* (as digitised in the
CDSL, 2026).

*Resource.* Kapp, D. and Malten, T., *Cologne Digital Sanskrit Dictionaries*,
University of Cologne (sanskrit-lexicon.uni-koeln.de).

*Secondary metalexicography.* Zgusta, Ladislav. 1971. *Manual of Lexicography.*
(Janua Linguarum, Series Maior 39.) Prague: Academia; The Hague and Paris: Mouton.
Hausmann, Franz Josef, Oskar Reichmann, Herbert Ernst Wiegand, and Ladislav Zgusta,
eds. 1989–1991. *Wörterbücher / Dictionaries / Dictionnaires: An International
Encyclopedia of Lexicography.* 3 vols. Berlin and New York: Walter de Gruyter.
Atkins, B. T. Sue, and Michael Rundell. 2008. *The Oxford Guide to Practical
Lexicography.* Oxford: Oxford University Press. [Same core metalexicography set as the
companion sense-inheritance paper (P2); a dictionary-aggregation-specific comparator —
a published entry-to-lemma ratio for another multi-dictionary portal — would
strengthen §4.1's collapse figure further but is not required for this paper's claims
and is not pursued here to avoid building a comparator dataset outside this study's
scope.]
