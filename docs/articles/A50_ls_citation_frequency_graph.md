# What the Sanskrit lexicographic tradition cites: a citation-frequency graph of `<ls>` source tags across 11 Cologne dictionaries

_Created: 06-07-2026 · Last updated: 24-09-2026_

Mārcis Gasūns, independent scholar ([ORCID 0000-0003-4513-884X](https://orcid.org/0000-0003-4513-884X)), gasyoun@ya.ru

**Status: readiness 3/5 (full draft).** Data 4/5 (committed, reproducible); prose drafted in
one pass (11-07-2026, H677) over the committed dataset only;
author-voice pass 06-09-2026 ([SIGNOFF_A50_author_pass.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/SIGNOFF_A50_author_pass.md)).
Remaining gates before 4/5: human
review of the tradition map (§4 caveat), the Zenodo data release, secondary-reference
verification (flagged below), byline/venue.

## Abstract

Besides defining words, nineteenth- and twentieth-century Sanskrit dictionaries cite
authorities. In the Cologne Digital Sanskrit Dictionaries (CDSL) digitizations, those citations
are machine-readable: every `<ls>` ("literary source") tag names the text a lexicographer
invoked as evidence. I extract all 1,496,302 `<ls>` tags from the 11 CDSL dictionaries with a
usable abbreviation key, resolve and canonicalize them into a citation-frequency graph of
826,752 citations of 874 distinct source texts, and release the graph as a documented,
reproducible dataset. Three findings follow. First, the pooled citation mass is heavily
concentrated: the top 10 texts (led by the Mahābhārata, Ṛgveda, Rāmāyaṇa, and Manusmṛti) carry
34.9% of all citations and the top 50 carry 72.5% — in a pool that is 64.9% PWG's, so this is
a volume-weighted figure, not a tradition-wide average. Second, the shared canon is thin:
one text (the Ṛgveda) is cited by all 11 dictionaries, four more reach every dictionary with
a usable yield, only 38 texts (4.3%) appear in seven or more, and 567 of 874 nodes (64.9%)
are private to a single dictionary. Third, the arrangement of citations is significantly *modular*, not nested
(Barber bipartite Q = 0.4757 vs. degree-preserving null 0.4094, permutation p = 0.001; NODF
26.9 *below* the null 31.4): given each dictionary's breadth and each text's popularity, the
specific assignments cluster more than that constraint forces. The partition the test finds is
three pairs — the Apte line (`ap`, `ap90`) and Schmidt with the PW-*Nachträge* (`sch`, `pwkvn`),
both pairs that share an abbreviation key by construction, plus Macdonell's four-node row
attached to Edgerton's (`bhs`, `md`) — and five singletons; the tradition
profiles alongside the clustering (Buddhist, classical-kāvya, Vedic, the broad-spectrum Petersburg
lineage) are read from a curated text→tradition map, not from the partition. The graph is a
reusable evidence layer for studies of lexicographic descent, and its per-locus verification is
under way in companion censuses.

## 1 Introduction

A bilingual dictionary of a classical language is, among other things, a compressed claim about
a corpus: *these* are the texts worth excerpting, and *this* is how often each one settles a
question of meaning. For Sanskrit, the great nineteenth-century dictionaries made that claim
explicit on every page — Böhtlingk and Roth's *Sanskrit-Wörterbuch* (PWG) alone carries over
800,000 source citations. The Cologne Digital Sanskrit Dictionaries preserve these citations as
`<ls>` tags, each wrapping the lexicographer's own abbreviation for the work cited
(`<ls>MBH. 7,9283</ls>`, `<ls>Spr. 2790</ls>`). Read across dictionaries, the tags form a
bipartite citation network — dictionary × cited text — that lets me ask, quantitatively, a
question usually answered by impression: what does the Sanskrit lexicographic tradition
actually cite?

Two sub-questions structure the paper. (i) *Is there a shared canon?* — a core set of texts
every lexicon leans on, with idiosyncratic authorities as decoration. (ii) *Or do the
dictionaries partition into citation communities* — Vedic, classical-kāvya, Buddhist — whose
overlap is thinner than the "one tradition" framing suggests? These are distinguishable
topologically: a strictly shared canon predicts a *nested* matrix (small dictionaries cite
subsets of what large ones cite), while communities predict a *modular* one (blocks of texts
private to groups of dictionaries). I test both against degree-preserving nulls (§4) — with
the caveat, made explicit there, that a one-canon draw with the same breadths sits on such a
null (§4), so the test asks whether the arrangement is *more*
nested or *more* modular than that.

**Contributions.** (1) A documented, reproducible citation-frequency graph over 11 CDSL
dictionaries — 826,752 resolved citations, 874 canonical text nodes, 1,699 dictionary→text
edges — with per-dictionary abbreviation-key resolution, an audited non-text filter, and a
curated alias fold ([`data/citations/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/citations)).
(2) Headline distributional results: concentration, reach, and the single-dictionary tail (§3).
(3) A topology test (nestedness vs. modularity) showing the citation matrix is significantly
modular (§4), the partition it finds, the resolver-key alternative that partition admits, and
per-dictionary tradition profiles read from a curated text→tradition map. (4) An explicit
limitations model, including the per-locus verification program the graph feeds (§5).

**Related work and demarcation.** Within this project, two sibling papers use citations
*forensically*: A08 ([OBS-C, "Two citation registers"](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_citation_registers.md))
separates citational from grammatical registers of quotation, and A10
(["Apparatus, not errors"](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md))
uses shared-rare and shared-erroneous citations as descent evidence between specific dictionary
pairs. This paper is the *frequency* layer neither covers: whole-tradition counts, not
pair-level fingerprints. Methodologically, the topology test imports standard bipartite-network
measures — NODF nestedness (Almeida-Neto et al. 2008) and Barber's (2007) bipartite modularity —
under the permutation-testing discipline argued for NLP by Dror et al. (2018). On the
lexicographic side, the descriptive inventories of the Sanskrit dictionary tradition (Vogel
1979; Zgusta 1971 for the general theory) characterize each dictionary's sources qualitatively;
I am not aware of a prior quantitative citation census across the Sanskrit dictionaries.

## 2 Data and method

**Source.** The dictionary digitizations in
[`csl-orig`](https://github.com/sanskrit-lexicon/csl-orig) (`v02/<dict>/<dict>.txt`), the
per-dictionary abbreviation keys in
[`csl-guides/src/data/abbreviations.json`](https://github.com/sanskrit-lexicon/csl-guides/blob/main/src/data/abbreviations.json),
and the builder
[`build_ls_citation_graph.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/build_ls_citation_graph.py).
Full method detail and change log:
[`data/citations/README.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/README.md).

**Pipeline** (each step auditable in the committed artifacts):

1. **Extraction.** Every `<ls>…</ls>` span is read from each dictionary's csl-orig text
   (1,496,302 raw tags across the 11 dictionaries of Table 1).
2. **Abbreviation resolution.** The leading abbreviation is resolved by longest-prefix match
   against that dictionary's *own* published key (case-insensitive fallback). A dictionary's
   citation is thus interpreted by its own conventions, not a global gazetteer.
3. **Non-text filter (MW).** Monier-Williams reuses `<ls>` for grammatical voice/case markers
   (`A.`, `mn.`, `ind.`), editorial markers (`ibid.`, `Cat.`, `col.`), and the `L.` =
   "lexicographers" tag. 63,582 such markers are excluded via an explicit stoplist and counted
   in [`ls_citation_nontext_filtered.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_nontext_filtered.tsv)
   — an audited exclusion, not a silent drop.
4. **Placeholder filter.** Abbreviations whose Cologne expansion is `? [Cologne Addition]`
   (unidentified by the digitizers themselves) count as unresolved, never as a text node.
5. **Key-borrow.** Three `<ls>`-bearing dictionaries have no key of their own but a documented
   shared convention and borrow one: `ap`←`ap90` (same author), `sch`←`pwg` and `pwkvn`←`pwg`
   (the Petersburg *Nachträge* tradition). Borrowed-key resolution rates are reported
   separately (Table 1) and are a named limitation (§5).
6. **Canonical folding.** Editorial tails are stripped; nodes fold under a diacritic- and
   case-insensitive key (`ṚGVEDA` ≡ `Ṛg-veda` ≡ `Ṛgveda`); a small hand-verified alias table
   folds the highest-count author's-genitive and title-synonym forms (`MANU'S Gesetzbuch` +
   `Mānavadharmaśāstra` → *Manusmṛti*) and, since the 24-09-2026 re-freeze, the 37
   eye-checked transliteration-variant pairs of the H5295 fold table (`Raghuvanśa` →
   *Raghuvaṃśa*, `Naishadhacharita` → *Naiṣadhacarita*, `Rigveda` → *Ṛgveda*, …; §5.5).
   Every alias is a well-established identification; the long synonymy tail beyond
   transliteration is deliberately left unmerged and quantified in §5.

**Table 1 — corpus and coverage.** Source:
[`data/citations/README.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/README.md)
coverage table (raw/filtered/resolved) and
[`ls_citation_edges.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_edges.tsv)
(distinct texts, recomputed 24-09-2026; where the README's per-dictionary distinct-text counts
differ by a few units, the committed edge list is authoritative). `% text` =
resolved ÷ (raw − non-text). `*` = borrowed key.

| Code | Dictionary | Raw `<ls>` | Non-text filtered | Resolved text citations | % text | Distinct texts |
|---|---|--:|--:|--:|--:|--:|
| pwg | Böhtlingk & Roth, *Sanskrit-Wörterbuch* (1855–1875) | 801,790 | 0 | 536,172 | 66.9% | 475 |
| ap\* | Apte, *Practical Sanskrit-English Dictionary*, revised ed. (1957–1959) | 68,273 | 0 | 57,112 | 83.7% | 155 |
| pw | Böhtlingk, *Sanskrit-Wörterbuch in kürzerer Fassung* (1879–1889) | 98,484 | 0 | 50,701 | 51.5% | 243 |
| ben | Benfey, *Sanskrit-English Dictionary* (1866) | 49,389 | 0 | 47,251 | 95.7% | 94 |
| bhs | Edgerton, *Buddhist Hybrid Sanskrit Dictionary* (1953) | 48,419 | 0 | 40,875 | 84.4% | 136 |
| ap90 | Apte, *Practical Sanskrit-English Dictionary* (1890) | 43,894 | 0 | 37,993 | 86.6% | 149 |
| mw | Monier-Williams, *Sanskrit-English Dictionary* (1899) | 320,830 | 63,582 | 20,250 | 7.9% | 5 |
| lrv | Vaidya, *Standard Sanskrit-English Dictionary* (1889) | 16,650 | 0 | 16,469 | 98.9% | 106 |
| sch\* | Schmidt, *Nachträge zum Sanskrit-Wörterbuch* (1928) | 31,041 | 0 | 11,496 | 37.0% | 160 |
| pwkvn\* | *Petersburger Wörterbuch* (PW) *Nachträge und Verbesserungen* | 17,629 | 0 | 8,386 | 47.6% | 172 |
| md | Macdonell, *Sanskrit-English Dictionary* (1893) | 58 | 0 | 47 | 81.0% | 4 |
| **total** | | **1,496,457** | **63,582** | **826,752** | **57.7%** | **874** |

The overall resolution ceiling — 57.7% of non-filtered tags resolve to a canonical text — and
its two largest causes (MW's tag reuse, partial borrowed keys) are treated as limitations in
§5, not hidden in the denominator.

## 3 Results I — the shape of the shared canon

**Concentration.** Citation mass is strongly top-heavy. Computed from
[`ls_citation_nodes.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_nodes.tsv)
(n = 874 texts, 826,752 citations, data as of 24-09-2026): the top 10 texts carry 34.9% of
all citations, the top 20 carry 50.9%, the top 50 carry 72.5%, and the top 100 carry 85.9%.
These are properties of the *pool*, and the pool is 64.9% PWG (next: Apte 6.9%, pw 6.1%,
Benfey 5.7%), so they are volume-weighted toward Böhtlingk's habits. Excluding PWG the pooled
top 10 carry 40.3% and the top 50 75.5% (623 texts) — the same order of concentration, so the
direction does not depend on PWG. Per-dictionary top-*k* shares are not compared here: a top-10
share depends on how many texts a dictionary cites (Macdonell's four texts give 100%), so those
figures are not comparable with each other or with the pool
([f12 ledger](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/A50_CLAIM_FALSIFICATION_LEDGER.md) C1).
A working lexicographer's evidentiary world was, in volume terms, a few dozen texts deep.

**Table 2 — the most-cited texts.** Source: `ls_citation_nodes.tsv` (n = 874; folded canonical
nodes; 24-09-2026). `#dicts` = how many of the 11 dictionaries cite the text at least once.

| Citations | #dicts | Text |
|--:|--:|---|
| 56,822 | 8 | Mahābhārata |
| 39,025 | 11 | Ṛgveda |
| 38,154 | 9 | Rāmāyaṇa |
| 28,140 | 8 | Manusmṛti |
| 24,300 | 8 | Bhāgavata-Purāṇa |
| 24,025 | 8 | Raghuvaṃśa |
| 21,791 | 3 | Aṣṭādhyāyī (Pāṇini) |
| 20,232 | 7 | Śabdakalpadruma |
| 18,073 | 3 | Abhidhānacintāmaṇi |
| 18,030 | 4 | Indische Sprüche |
| 17,015 | 9 | Kathāsaritsāgara |
| 14,918 | 8 | Amarakoṣa |
| 14,853 | 7 | Pañcatantra |
| 13,685 | 7 | Harivaṃśa |
| 13,246 | 6 | Medinīkośa |

Three genre observations sit on the surface of Table 2. The epics and dharmaśāstra dominate raw
volume (Mahābhārata, Rāmāyaṇa, Manusmṛti). The indigenous lexica — Śabdakalpadruma, Amarakoṣa,
Abhidhānacintāmaṇi, Medinīkośa — are themselves among the most-cited *sources*. This is
Böhtlingk's method made visible, not a habit of the Western dictionaries at large: PWG
supplies 99.5% of the Śabdakalpadruma's citations, 97.3% of the Amarakoṣa's, 98.8% of the
Medinīkośa's and 88.9% of the Abhidhānacintāmaṇi's (the rest of that one is Schmidt's
*Nachträge*, 2,000); no other dictionary cites any kośa more than 187 times. And two entries
are artifacts of a single dominant citer amplified through the fold: Aṣṭādhyāyī's 21,791 is
almost entirely PWG (21,509, its third-largest source), and *Indische Sprüche* is Böhtlingk
citing his own anthology (see §5 on its verification).

**Reach: the canon is thin.** Reach is nearly the inverse of volume. Computed from
`ls_citation_nodes.tsv` (n = 874; 24-09-2026):

| Cited by *k* dictionaries | Texts |
|--:|--:|
| 11 | 1 |
| 10 | 0 |
| 9 | 4 |
| 8 | 19 |
| 7 | 14 |
| 6 | 23 |
| 5 | 16 |
| 4 | 30 |
| 3 | 97 |
| 2 | 103 |
| 1 | 567 |

Exactly one text, the **Ṛgveda, is cited by every one of the 11 dictionaries** — since the
24-09-2026 re-freeze folds `Rigveda` (837 citations; Benfey, Edgerton, Vaidya, Macdonell) into
it; on the earlier labels none reached 11 — a count that leans on the two thin rows
(Monier-Williams contributes 5 nodes, Macdonell 4; §5.2, §5.4), which is why the sturdier
statement is the next one. Over the nine dictionaries with a usable yield, five texts reach
every row: the Ṛgveda, the Rāmāyaṇa, the Kathāsaritsāgara, the Bhagavadgītā, and the
Mārkaṇḍeya-Purāṇa. Only 38 texts (4.3%) reach seven or more dictionaries — but those 38 carry
52.4% of all citation volume. Meanwhile 567 of 874 nodes (64.9%) are private to a single
dictionary, jointly carrying 9.6% of the volume (on the 06-07-2026 labels, before the 37-pair
fold of §5.5: 608 of 912, 66.7%, 11.1% of volume). The picture is a thin, heavily-cited universal head
over a long private tail — which raises the topological question of §4: is the tail
structured?

## 4 Results II — clustering beyond one canon, and what the partition is

**The topology test (PH1 CANON-CORE).** If the dictionaries shared one canon, the binarized
dictionary × text matrix should be *nested*: a dictionary citing few texts should cite a subset
of what broader dictionaries cite. If instead each lexicographic tradition kept its own
authorities, the matrix should be *modular*: blocks of texts co-cited by a group of
dictionaries and absent elsewhere. Following the committed test
([`scripts/build-citation-canon.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-citation-canon.mjs)
→ [`citation_canon.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/citations/citation_canon.json),
generated 24-09-2026; matrix 11 × 874, 1,699 edges, fill 0.177), I compute NODF nestedness
(Almeida-Neto et al. 2008) and Barber (2007) bipartite modularity Q (label propagation, best of
6 restarts), each against 1,000 degree-preserving (fixed-fixed) permutation nulls; permutation
p = (r+1)/(n+1).

**Result: the matrix is significantly modular and, if anything, *less* nested than chance.**
NODF = 26.86 vs. null mean 31.36 ± 0.19 (z = −24.3, p = 1.0); Barber Q = 0.4757 (8 modules)
vs. null mean 0.4094 ± 0.0008 (z = 81.9, p = 0.001). The degree-preserving null holds each
dictionary's breadth and each text's popularity fixed, so this is a statement about
*arrangement*, not about the concentration already reported in §3: given how many texts each
dictionary cites and how popular each text is, the specific assignments cluster more than
that constraint forces. Note what the null can and cannot tell apart: it is the margins-only
ensemble, and a one-canon matrix (one ranked list, real breadths sampled from it with weight
1/(rank + 1), no communities by construction) sits on it on both statistics (NODF p =
0.71, Q p = 0.28); so "less nested than the null" means less nested than a one-canon random
draw, not that the shared-canon reading runs the other way, and "more modular than the null"
is the finding.

**What the partition is.** The optimiser's eight modules on the committed matrix (same seed
as the committed run) are `ap`+`ap90` · `pwkvn`+`sch` · `bhs`+`md` · `ben` · `lrv` · `mw` ·
`pw` · `pwg` — three pairs and five singletons. The "Petersburg lineage" is *not* a
module (PWG and pw each stand alone), and there is no "Vedic" pair: `mw` is a singleton in every
real-data arm that keeps it, and the `bhs`+`md` pair is Macdonell's four Vedic nodes attached
to Edgerton's Buddhist row — a heuristic placement of a four-node row with no shared profile
(Table 3); on the 06-07-2026 labels `md` was a singleton and the count was nine. The read-out is one run of a heuristic label-propagation
optimiser (§5.7) and moves under input drift alone; it is the partition the statistic *found*,
not a fact about the dictionaries. The tradition *names* below come from the profiles of
Table 3, not from that partition.

**The alternative the partition admits.** The two non-singleton modules that carry any weight
are exactly the two pairs that share an abbreviation key by construction (§2, step 5: `ap` borrows `ap90`'s key,
`sch` and `pwkvn` borrow PWG's). A pair resolved through one key is co-cited under one set of
canonical labels while every other pair is resolved through two — a resolver artefact that is
sufficient for both observed pairs. Until the borrowed keys are unified (H5407), "citation
community" and "shared key" are not distinguishable in this graph.

**Is the modular margin a label artefact? Not of the known variants, nor of per-dictionary
spelling privacy.** The 37 known variants are folded in the committed data since 24-09-2026;
the margin was flat under that fold (below). A control
then isolates what an unfolded *private* variant changes — the node label: take the one-canon matrix above and relabel a
fraction of each dictionary's texts to a dictionary-private spelling (text and row breadth
unchanged; the column margins change, so the null is re-drawn). Over 12 runs (three
seeds × fractions 0.05–0.3) the margin over the null never exceeds 0.0016 (z ≤
1.97), against 0.066 and z = 81.9 here; the *verdict* at that margin is seed- and
fraction-sensitive (of 14 constructed runs including the two arm-seed runs, two read modular
alone at p ≤ 0.027, three nested-and-modular, three nested, six neither; at two fractions the
three sweep seeds return three different readings), which is a warning about reading a p-value near 0.05 on a matrix like this, not a
mechanism. Private labels inflate *raw* Q in observed and null alike: on the 06-07-2026
labels Q was 0.4995 against a null of 0.4295 (margin 0.070, z 83.8); folding the 37 variant
pairs — the committed data since 24-09-2026 — lowers both (0.4757 vs. 0.4094) and leaves the
margin at 0.066; dropping the two thin rows leaves it at 0.067
([f12 ledger](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/A50_CLAIM_FALSIFICATION_LEDGER.md) C3–C4, C7;
arms in [`f12_a50_topology_arms.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f12_a50_topology_arms.json)).

**Tradition profiles.** A curated 114-text text→tradition map
([`tradition_tags.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/tradition_tags.tsv),
confidence-scored, covering 80.6% of total citation volume) gives each dictionary a tradition
profile. It does not name the optimiser's modules (listed above); it says what each row cites.
**Table 3 — per-dictionary tradition profile.** Source: `tradition_tags.tsv` joined to
`ls_citation_edges.tsv` (tagged volume per dictionary; recomputed 24-09-2026). Shares are of
each dictionary's *tagged* volume; the tagged fraction is given per row.

| Dict | Tagged volume (share of dict) | Leading traditions |
|---|--:|---|
| pwg | 416,050 (78%) | lexical-kośa 21% · classical-kāvya 20% · epic 19% · vedic 14% |
| ap | 52,230 (91%) | classical-kāvya 59% · epic 15% · dharmaśāstra 11% |
| ben | 43,486 (92%) | classical-kāvya 40% · epic 31% · dharmaśāstra 15% |
| pw | 35,859 (71%) | classical-kāvya 27% · epic 20% · dharmaśāstra 17% · vedic 15% |
| ap90 | 34,494 (91%) | classical-kāvya 79% · dharmaśāstra 10% · epic 5% |
| bhs | 32,405 (79%) | **buddhist 98%** |
| mw | 20,250 (100%) | vedic 87% · buddhist 9% |
| lrv | 15,065 (91%) | classical-kāvya 77% · dharmaśāstra 15% |
| sch | 9,944 (86%) | classical-kāvya 26% · lexical-kośa 24% · epic 12% |
| pwkvn | 6,755 (81%) | classical-kāvya 27% · epic 18% · dharmaśāstra 13% |
| md | 47 (100%) | vedic 100% |

The profiles are the ones a historian of the discipline would draw freehand, now with
magnitudes attached — read as descriptions of what each dictionary cites, not as the
partition of §4. Edgerton's BHS dictionary is almost hermetically Buddhist in
profile — 98% of its tagged citation volume (Mahāvastu, Mahāvyutpatti, Lalitavistara lead its
edge list), with effectively zero Vedic or epic citation. The Apte line (`ap90` → `ap`) and
Vaidya share a classical-kāvya profile: 59–79% kāvya, led by the Raghuvaṃśa in all three
(only the Apte pair is a module of §4; `lrv` is a singleton). The Petersburg lineage (`pwg`,
`pw`, `pwkvn`, and Schmidt's *Nachträge*) shares a broad-spectrum profile — no tradition
exceeds 28% in any of the four; `pwg` and `pw` are singletons in §4 — and is alone in citing the indigenous
kośas at scale (a fifth of PWG's tagged volume). Monier-Williams' small tagged residue and
Macdonell read as Vedic, though both on unrepresentative yields (§5). Benfey sits between the
kāvya and epic profiles, consistent with its chrestomathy-anchored design.

**Caveat (blocking for submission).** The tradition map is `inferred`: 0 of its 114 rows are
human-reviewed as of 24-09-2026 (119 rows before the H5407 fold removed five duplicate
variant labels). The *topology* result (modularity) is independent of the map;
only the tradition *names* in Table 3 depend on it. The review sheet is queued
([agenda backlog #9](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/ATLAS_RESEARCH_AGENDA.md));
this section must be re-stated over the reviewed map before submission.

## 5 Limitations

1. **Resolution ceiling.** 57.8% of non-filtered `<ls>` tags resolve to a canonical text. The
   unresolved remainder is dominated by unkeyed abbreviations and is inventoried per dictionary
   in [`ls_citation_unresolved_top.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_unresolved_top.tsv)
   — a worklist. Results in §3–§4 describe the resolved graph.
2. **MW's yield is structurally low (7.9%).** After the audited removal of 63,582
   grammatical/editorial markers, MW contributes only ~20k text citations under 5 coarse nodes
   (78.6% of them "Ṛgveda"). MW's `<ls>` habits make it a poor frequency source; its
   tradition profile in Table 3 should be read as *tagged residue*, not as MW's true canon.
3. **Borrowed keys resolve partially.** Schmidt (37.0%) and PW-*Nachträge* (47.6%) share only
   part of the PWG abbreviation set; `ap`←`ap90` is clean (83.7%). Under-resolution biases
   these rows toward the *shared* Petersburg conventions and against their idiosyncratic
   sources.
4. **Keyless dictionaries are excluded**, notably Grassmann (`gra`, Vedic-specific), and `ieg`
   is an epigraphic outlier citing inscription corpora (Epigraphia Indica, South Indian
   Inscriptions) — a separate citation universe, deliberately out of the text graph.
5. **Transliteration variants are folded since 24-09-2026; the title-synonymy tail beyond
   them is unmerged.** The curated alias table folds only hand-verified identifications. Until
   the re-freeze ([H5407](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5407-Fable_csl-atlas_a50-citation-graph-refreeze-recorded-revision-alias-fold_24.09.26.md))
   spelling variants outside it were separate nodes — Vaidya's `Raghuvanśa` (4,101 citations)
   beside *Raghuvaṃśa* (19,922), `Manusmṛiti` (1,762) beside *Manusmṛti*, `Rigveda` (837)
   beside *Ṛgveda*, `Bhāgavata` (2,968) beside *Bhāgavata-Purāṇa* — each miss understating a
   major text's reach and adding a spurious single-dictionary "text" to the private tail (608 of
   912 labels on the 06-07-2026 freeze; 567 of 874 now). The H5295 ledger's fold table listed 37
   such pairs (those four plus 33 ASCII-digraph collisions: `sh`/`ṣ`, `ch`/`c`, `ri`/`ṛ`), all
   eye-checked; all 37 are now `CANON_ALIAS` entries of the builder and the residual table
   [`f12_a50_variant_fold.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f12_a50_variant_fold.tsv)
   is empty. The direction of the earlier bias was *against* the shared-canon reading on reach
   and privacy. On topology, measured rather than guessed: on the old labels folding the four
   names left the margin over the null unchanged (Q − null 0.070 → 0.070, z 83.8 → 89.5) and
   folding all 37 pairs lowered it to 0.067; the committed matrix now carries the fold (§4:
   0.4757 − 0.4094 = 0.066) and the verdict "modular, p = 0.001" is unchanged. Raw Q fell with
   the fold (0.4995 → 0.4759) only because the null fell with it. What remains unmerged is a
   text under a second, lesser-used title — and `AUFRECHT` (12,718 citations, a scholar
   shorthand of ambiguous referent), left unresolved rather than guessed.
6. **Counts are per text, not per locus.** The graph discards the book/verse locus, so it
   cannot say whether a citation is *correct* — only that it was made. Per-locus verification
   is a companion program, with first waves executed: the Harivaṃśa resolution census
   ([`HARIVAMSA_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/HARIVAMSA_CITATION_RESOLUTION_CENSUS.md),
   H488, 10-07-2026) and the *Indische Sprüche* verification census
   ([`SPRUECHE_CITATION_VERIFICATION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/SPRUECHE_CITATION_VERIFICATION_CENSUS.md),
   H611, 11-07-2026), which checked all 15,877 PWG citations of Böhtlingk's own anthology and
   found, for the 6,320 second-edition references with a typed text to check against, 2,621
   corroborated vs. 443 text mismatches (plus 3,255 verse-without-quote references) — i.e.
   roughly one in seven checkable quotations diverges from the cited verse. Mahābhārata locus
   resolution (the largest single edge in this graph, 39,130 PWG citations) is queued as its
   own handoff (H610). The frequency graph should be read with that error floor in mind.
7. **Topology statistics are presence/absence.** NODF and Q are computed on the binarized
   matrix; count weighting appears in the exploratory heatmap
   ([`/tools/citation-canon`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/citation-canon.md))
   but not in the significance tests. Barber Q via label propagation is a heuristic lower
   bound, not an exhaustive optimum.
8. **The tradition map is inferred and unreviewed** (§4 caveat): the tradition *names* await the
   114-row human review; the modularity statistic does not depend on them.

## 6 Conclusion

Read as a citation network, the Sanskrit dictionary tradition does not read from one list.
Its pooled citation mass concentrates on a few dozen texts, but the *arrangement* of citations
is significantly modular: given how widely each dictionary read and how popular each text was,
the specific assignments cluster beyond what a one-canon draw forces. What the test partitions
is three pairs — two of them key-sharing — and five singletons; read through the tradition map, a Buddhist
lexicon, a kāvya-schoolroom line, a Vedic profile, and the omnivorous Petersburg lineage each
show their own profile of authorities, sharing a thin universal head — Rāmāyaṇa, Mahābhārata,
Ṛgveda, Manusmṛti — of which one text, the Ṛgveda, reaches all eleven dictionaries and four
reach every dictionary with a usable yield. The partition is softer than its names: two of
the three pairs it finds are the two pairs resolved through a borrowed abbreviation key, and
the third attaches Macdonell's four-node row to Edgerton's (§4). The "canon
of Sanskrit literature" implied by the dictionaries is a set of dictionary-specific reading lists with a
very small intersection.

Beyond its own findings, the graph is built to be consumed. It gives descent studies (A10) a
frequency baseline against which shared-rare citations are surprising; it gives the
citation-register work (A08) the volume denominators its registers divide; and its per-locus
extension — the verification censuses of §5.6 — turns the lexicographers' apparatus into
checkable claims against digital corpora. The dataset, builder, and audit trails are committed
in [`data/citations/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/citations);
a versioned data release (Zenodo DOI) is the remaining packaging step before submission.

## Data availability and reproducibility

All tables and statistics in this paper are computed from committed artifacts in
[csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas):
[`ls_citation_edges.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_edges.tsv)
(1,699 edges),
[`ls_citation_nodes.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_nodes.tsv)
(874 nodes),
[`tradition_tags.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/tradition_tags.tsv)
(114 rows),
[`citation_canon.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/citations/citation_canon.json)
(topology statistics + provenance sidecar),
[`ls_citation_graph.source.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_graph.source.json)
(the revision binding below). The graph rebuilds in ~1 minute with
`python data/citations/build_ls_citation_graph.py` against sibling `csl-orig` and `csl-guides`
checkouts; the topology statistics with `npm run build-citation-canon`. **Revision binding.**
The committed TSVs were re-frozen on 24-09-2026 (H5407) at a recorded sibling revision pair —
`csl-orig@f4c08c578b330e2379e38f54d3a541f1564b8eee` and
`csl-guides@64c967d1d08d26868bbbc289b4aacec7f4a8f3ff`, both clean, `abbreviations.json`
SHA-256 `dfd9fb68…8a48` — and the builder writes that binding to `ls_citation_graph.source.json`
(csl-atlas and sibling revisions, dirty flags, key, builder and output hashes) on every run;
two runs at that pair are byte-identical. Every figure in this paper is bound to those files
by hash (`ls_citation_edges.tsv` SHA-256 `41bee931…3bd0`, `ls_citation_nodes.tsv`
`6039af4d…e474`) and reproduces from them byte-for-byte. The previous freeze (06-07-2026)
recorded no revision; its figures differ from these by Benfey's `<ls>` edits in `csl-orig`
between 06-07 and 09-07-2026 (BEN issues #19, #21, #27: the bare `Chr.` tag for *my Sanskrit
Chrestomathy* 3,017 → 1,602 and `Gorr.` 347 → 15 after page numbers were folded into fewer
tags), one Apte citation, a `Weber`/`WEBER` key-case change, and the 37-pair variant fold of
§5.5 — 828,505 citations / 912 nodes / 1,701 edges → 826,752 / 874 / 1,699; top-50 share
71.0 → 72.5; Q 0.4995 → 0.4757 with the null 0.4295 → 0.4094; every verdict and p-value
unchanged. Claim-by-claim falsification of this paper, with the drift
table and the constructed controls behind §4:
[`A50_CLAIM_FALSIFICATION_LEDGER.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/A50_CLAIM_FALSIFICATION_LEDGER.md).
An interactive view
(nested-order heatmap, canon curve, per-dictionary fingerprints, CSV downloads) is deployed at
[`/tools/citation-canon`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/citation-canon.md).

## References

Secondary references below are cited from standard editions; bibliographic details flagged
`[author-verify]` await the author's check against physical copies.

- Almeida-Neto, M., P. Guimarães, P. R. Guimarães Jr., R. D. Loyola & W. Ulrich (2008). A
  consistent metric for nestedness analysis in ecological systems: reconciling concept and
  measurement. *Oikos* 117(8), 1227–1239.
- Apte, V. S. (1890). *The Practical Sanskrit-English Dictionary.* Poona.
- Apte, V. S. (1957–1959). *The Practical Sanskrit-English Dictionary.* Revised and enlarged
  edition, ed. P. K. Gode & C. G. Karve. Poona: Prasad Prakashan. `[author-verify]`
- Barber, M. J. (2007). Modularity and community detection in bipartite networks. *Physical
  Review E* 76, 066102.
- Benfey, T. (1866). *A Sanskrit-English Dictionary.* London: Longmans, Green. `[author-verify]`
- Böhtlingk, O. (1870–1873). *Indische Sprüche.* 2nd ed. St. Petersburg. `[author-verify]`
- Böhtlingk, O. (1879–1889). *Sanskrit-Wörterbuch in kürzerer Fassung.* St. Petersburg.
- Böhtlingk, O. & R. Roth (1855–1875). *Sanskrit-Wörterbuch.* St. Petersburg: Kaiserliche
  Akademie der Wissenschaften.
- Cologne Digital Sanskrit Dictionaries (CDSL). Cologne University,
  [https://www.sanskrit-lexicon.uni-koeln.de](https://www.sanskrit-lexicon.uni-koeln.de).
- Dror, R., G. Baumer, S. Shlomov & R. Reichart (2018). The hitchhiker's guide to testing
  statistical significance in natural language processing. *Proceedings of ACL 2018*,
  1383–1392.
- Edgerton, F. (1953). *Buddhist Hybrid Sanskrit Grammar and Dictionary.* New Haven: Yale
  University Press.
- Macdonell, A. A. (1893). *A Sanskrit-English Dictionary.* London: Longmans, Green.
- Monier-Williams, M. (1899). *A Sanskrit-English Dictionary.* Oxford: Clarendon Press.
- Schmidt, R. (1928). *Nachträge zum Sanskrit-Wörterbuch in kürzerer Fassung von Otto
  Böhtlingk.* Leipzig: Harrassowitz. `[author-verify]`
- Vaidya, L. R. (1889). *The Standard Sanskrit-English Dictionary.* Bombay. `[author-verify]`
- Vogel, C. (1979). *Indian Lexicography.* Wiesbaden: Harrassowitz.
- Zgusta, L. (1971). *Manual of Lexicography.* The Hague: Mouton.

## Venue candidates

DH / computational-lexicography methods venue (*Digital Scholarship in the Humanities*,
*Cultural Analytics*) or a data journal (*Journal of Open Humanities Data*) paired with the
Zenodo release. `/venue-scout` later.

## Provenance

- Scaffolded 06-07-2026 by Opus 4.8 (`claude-opus-4-8`) under
  [H213](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H213-Opus_csl-atlas_ls_citation_graph_canonicalization_06.07.26.md);
  dataset built + merged in [csl-atlas PR #220](https://github.com/sanskrit-lexicon/csl-atlas/pull/220)
  (v1 in [PR #219](https://github.com/sanskrit-lexicon/csl-atlas/pull/219)).
- Canon topology test (H305) and tradition map (H340) by Fable 5 (`claude-fable-5`),
  07/08-07-2026.
- Full prose draft 11-07-2026 by Fable 5 (`claude-fable-5`) under
  [H677](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H677-Fable_csl-atlas_a50-citation-graph-prose_11.07.26.md);
  all figures recomputed from the committed dataset in the same pass.
- Re-freeze at a recorded `csl-orig`/`csl-guides` revision pair, 37-pair transliteration
  fold and five duplicate tradition-map rows removed, 24-09-2026, by Fable 5.1
  (`claude-fable-5-1`) under [H5407](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5407-Fable_csl-atlas_a50-citation-graph-refreeze-recorded-revision-alias-fold_24.09.26.md);
  every table and figure recomputed from the re-frozen dataset in the same pass.

_Dr. Mārcis Gasūns_
