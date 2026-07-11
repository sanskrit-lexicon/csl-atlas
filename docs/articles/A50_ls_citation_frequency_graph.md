# What the Sanskrit lexicographic tradition cites: a citation-frequency graph of `<ls>` source tags across 11 Cologne dictionaries

_Created: 06-07-2026 · Last updated: 11-07-2026_

**Status: readiness 3/5 (full draft).** Data 4/5 (committed, reproducible); prose drafted in
one pass (11-07-2026, H677) over the committed dataset only. Remaining gates before 4/5: human
review of the tradition map (§4 caveat), the Zenodo data release, secondary-reference
verification (flagged below), byline/venue.

## Abstract

Nineteenth- and twentieth-century Sanskrit dictionaries do not merely define words — they cite
authorities. In the Cologne Digital Sanskrit Dictionaries (CDSL) digitizations, those citations
are machine-readable: every `<ls>` ("literary source") tag names the text a lexicographer
invoked as evidence. We extract all 1,496,302 `<ls>` tags from the 11 CDSL dictionaries with a
usable abbreviation key, resolve and canonicalize them into a citation-frequency graph of
828,505 citations of 912 distinct source texts, and release the graph as a documented,
reproducible dataset. Three findings. First, the tradition's citation mass is heavily
concentrated: the top 10 texts (led by the Mahābhārata, Ṛgveda, Rāmāyaṇa, and Manusmṛti) carry
33.7% of all citations and the top 50 carry 71.0%. Second, the shared canon is thin: no text is
cited by all 11 dictionaries, only 29 texts (3.2%) appear in seven or more, and 608 of 912
texts (66.7%) are private to a single dictionary. Third, the arrangement of citations is
significantly *modular*, not nested (Barber bipartite Q = 0.4995 vs. degree-preserving null
0.4295, permutation p = 0.001; NODF 24.4 *below* the null 29.0): the dictionaries fall into
partly disjoint citation communities — Buddhist (Edgerton), classical-kāvya (the Apte line),
Vedic (Monier-Williams' tagged residue, Macdonell), and the Petersburg lineage — rather than
strata of one shared reading list. The graph is a reusable evidence layer for studies of
lexicographic descent, and its per-locus verification is under way in companion censuses.

## 1 Introduction

A bilingual dictionary of a classical language is, among other things, a compressed claim about
a corpus: *these* are the texts worth excerpting, and *this* is how often each one settles a
question of meaning. For Sanskrit, the great nineteenth-century dictionaries made that claim
explicit on every page — Böhtlingk and Roth's *Sanskrit-Wörterbuch* (PWG) alone carries over
800,000 source citations. The Cologne Digital Sanskrit Dictionaries preserve these citations as
`<ls>` tags, each wrapping the lexicographer's own abbreviation for the work cited
(`<ls>MBH. 7,9283</ls>`, `<ls>Spr. 2790</ls>`). Read across dictionaries, the tags form a
bipartite citation network — dictionary × cited text — that lets us ask, quantitatively, a
question usually answered by impression: **what does the Sanskrit lexicographic tradition
actually cite?**

Two sub-questions structure the paper. (i) *Is there a shared canon?* — a core set of texts
every lexicon leans on, with idiosyncratic authorities as decoration. (ii) *Or do the
dictionaries partition into citation communities* — Vedic, classical-kāvya, Buddhist — whose
overlap is thinner than the "one tradition" framing suggests? These are distinguishable
topologically: a shared canon predicts a *nested* matrix (small dictionaries cite subsets of
what large ones cite), while communities predict a *modular* one (blocks of texts private to
groups of dictionaries). We test both against degree-preserving nulls (§4).

**Contributions.** (1) A documented, reproducible citation-frequency graph over 11 CDSL
dictionaries — 828,505 resolved citations, 912 canonical text nodes, 1,701 dictionary→text
edges — with per-dictionary abbreviation-key resolution, an audited non-text filter, and a
curated alias fold ([`data/citations/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/citations)).
(2) Headline distributional results: concentration, reach, and the single-dictionary tail (§3).
(3) A topology test (nestedness vs. modularity) showing the citation canon is significantly
modular (§4), with the communities named by a curated text→tradition map. (4) An explicit
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
we are not aware of a prior quantitative citation census across the Sanskrit dictionaries.

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
   `Mānavadharmaśāstra` → *Manusmṛti*). Every alias is a well-established identification;
   the long synonymy tail is deliberately left unmerged and quantified in §5.

**Table 1 — corpus and coverage.** Source:
[`data/citations/README.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/README.md)
coverage table (raw/filtered/resolved) and
[`ls_citation_edges.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_edges.tsv)
(distinct texts, recomputed 11-07-2026; where the README's per-dictionary distinct-text counts
differ by a few units, the committed edge list is authoritative). `% text` =
resolved ÷ (raw − non-text). `*` = borrowed key.

| Code | Dictionary | Raw `<ls>` | Non-text filtered | Resolved text citations | % text | Distinct texts |
|---|---|--:|--:|--:|--:|--:|
| pwg | Böhtlingk & Roth, *Sanskrit-Wörterbuch* (1855–1875) | 801,790 | 0 | 536,172 | 66.9% | 475 |
| ap\* | Apte, *Practical Sanskrit-English Dictionary*, revised ed. (1957–1959) | 68,273 | 0 | 57,113 | 83.7% | 155 |
| pw | Böhtlingk, *Sanskrit-Wörterbuch in kürzerer Fassung* (1879–1889) | 98,484 | 0 | 50,701 | 51.5% | 243 |
| ben | Benfey, *Sanskrit-English Dictionary* (1866) | 49,234 | 0 | 49,003 | 99.5% | 96 |
| bhs | Edgerton, *Buddhist Hybrid Sanskrit Dictionary* (1953) | 48,419 | 0 | 40,875 | 84.4% | 136 |
| ap90 | Apte, *Practical Sanskrit-English Dictionary* (1890) | 43,894 | 0 | 37,993 | 86.6% | 149 |
| mw | Monier-Williams, *Sanskrit-English Dictionary* (1899) | 320,830 | 63,582 | 20,250 | 7.9% | 5 |
| lrv | Vaidya, *Standard Sanskrit-English Dictionary* (1889) | 16,650 | 0 | 16,469 | 98.9% | 106 |
| sch\* | Schmidt, *Nachträge zum Sanskrit-Wörterbuch* (1928) | 31,041 | 0 | 11,496 | 37.0% | 160 |
| pwkvn\* | *Petersburger Wörterbuch* (PW) *Nachträge und Verbesserungen* | 17,629 | 0 | 8,386 | 47.6% | 172 |
| md | Macdonell, *Sanskrit-English Dictionary* (1893) | 58 | 0 | 47 | 81.0% | 4 |
| **total** | | **1,496,302** | **63,582** | **828,505** | **57.8%** | **912** |

The overall resolution ceiling — 57.8% of non-filtered tags resolve to a canonical text — and
its two largest causes (MW's tag reuse, partial borrowed keys) are treated as limitations in
§5, not hidden in the denominator.

## 3 Results I — the shape of the shared canon

**Concentration.** Citation mass is strongly top-heavy. Computed from
[`ls_citation_nodes.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_nodes.tsv)
(n = 912 texts, 828,505 citations, data as of 11-07-2026): the top 10 texts carry **33.7%** of
all citations, the top 20 carry 49.7%, the top 50 carry **71.0%**, and the top 100 carry 84.9%.
A working lexicographer's evidentiary world was, in volume terms, a few dozen texts deep.

**Table 2 — the most-cited texts.** Source: `ls_citation_nodes.tsv` (n = 912; folded canonical
nodes; 11-07-2026). `#dicts` = how many of the 11 dictionaries cite the text at least once.

| Citations | #dicts | Text |
|--:|--:|---|
| 56,818 | 8 | Mahābhārata |
| 38,187 | 7 | Ṛgveda |
| 38,155 | 9 | Rāmāyaṇa |
| 26,365 | 7 | Manusmṛti |
| 21,791 | 3 | Aṣṭādhyāyī (Pāṇini) |
| 21,330 | 5 | Bhāgavata-Purāṇa |
| 20,232 | 7 | Śabdakalpadruma |
| 19,922 | 7 | Raghuvaṃśa |
| 18,073 | 3 | Abhidhānacintāmaṇi |
| 18,030 | 4 | Indische Sprüche |
| 17,015 | 9 | Kathāsaritsāgara |
| 14,918 | 8 | Amarakoṣa |
| 14,743 | 6 | Pañcatantra |
| 13,685 | 7 | Harivaṃśa |
| 13,246 | 6 | Medinīkośa |

Three genre observations sit on the surface of Table 2. The epics and dharmaśāstra dominate raw
volume (Mahābhārata, Rāmāyaṇa, Manusmṛti). The indigenous lexica — Śabdakalpadruma, Amarakoṣa,
Abhidhānacintāmaṇi, Medinīkośa — are themselves among the most-cited *sources*: the Western
dictionaries cite the Indian dictionaries, descent made visible as citation. And two entries
are artifacts of a single dominant citer amplified through the fold: Aṣṭādhyāyī's 21,791 is
almost entirely PWG (21,509, its third-largest source), and *Indische Sprüche* is Böhtlingk
citing his own anthology (see §5 on its verification).

**Reach: the canon is thin.** Reach is nearly the inverse of volume. Computed from
`ls_citation_nodes.tsv` (n = 912; 11-07-2026):

| Cited by *k* dictionaries | Texts |
|--:|--:|
| 11 | 0 |
| 10 | 0 |
| 9 | 4 |
| 8 | 13 |
| 7 | 12 |
| 6 | 20 |
| 5 | 25 |
| 4 | 31 |
| 3 | 102 |
| 2 | 97 |
| 1 | 608 |

**No text is cited by all 11 dictionaries.** The widest-reach texts, at 9 of 11, are the
Rāmāyaṇa, the Kathāsaritsāgara, the Bhagavadgītā, and the Mārkaṇḍeya-Purāṇa. Only 29 texts
(3.2%) reach seven or more dictionaries — but those 29 carry 44.1% of all citation volume.
Meanwhile **608 of 912 texts (66.7%) are private to a single dictionary**, jointly carrying
11.1% of the volume. The picture is a thin, heavily-cited universal head over a long private
tail — which raises the topological question of §4: is the tail structured?

## 4 Results II — tradition communities, not one canon

**The topology test (PH1 CANON-CORE).** If the dictionaries shared one canon, the binarized
dictionary × text matrix should be *nested*: a dictionary citing few texts should cite a subset
of what broader dictionaries cite. If instead each lexicographic tradition kept its own
authorities, the matrix should be *modular*: blocks of texts co-cited by a group of
dictionaries and absent elsewhere. Following the committed test
([`scripts/build-citation-canon.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-citation-canon.mjs)
→ [`citation_canon.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/citations/citation_canon.json),
generated 07-07-2026; matrix 11 × 912, 1,701 edges, fill 0.170), we compute NODF nestedness
(Almeida-Neto et al. 2008) and Barber (2007) bipartite modularity Q (label propagation, best of
6 restarts), each against 1,000 degree-preserving (fixed-fixed) permutation nulls; permutation
p = (r+1)/(n+1).

**Result: the matrix is significantly modular and, if anything, *less* nested than chance.**
NODF = 24.44 vs. null mean 28.98 ± 0.18 (z = −25.7, p = 1.0); Barber Q = 0.4995 (9 modules)
vs. null mean 0.4295 ± 0.0008 (z = 83.8, **p = 0.001**). The shared-canon hypothesis is not
merely unsupported — the arrangement of citations runs the other way. The degree-preserving
null holds each dictionary's breadth and each text's popularity fixed, so this is a statement
about *arrangement*, not about the concentration already reported in §3: given how many texts
each dictionary cites and how popular each text is, the specific assignments cluster into
communities more than that constraint forces.

**Naming the communities.** A curated 119-text text→tradition map
([`tradition_tags.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/tradition_tags.tsv),
confidence-scored, covering 80.3% of total citation volume) makes the modules legible.
**Table 3 — per-dictionary tradition profile.** Source: `tradition_tags.tsv` joined to
`ls_citation_edges.tsv` (tagged volume per dictionary; recomputed 11-07-2026). Shares are of
each dictionary's *tagged* volume; the tagged fraction is given per row.

| Dict | Tagged volume (share of dict) | Leading traditions |
|---|--:|---|
| pwg | 416,050 (78%) | lexical-kośa 21% · classical-kāvya 20% · epic 19% · vedic 14% |
| ap | 52,231 (91%) | classical-kāvya 59% · epic 15% · dharmaśāstra 11% |
| ben | 44,859 (92%) | classical-kāvya 39% · epic 30% · dharmaśāstra 15% |
| ap90 | 34,494 (91%) | classical-kāvya 79% · dharmaśāstra 10% · epic 5% |
| pw | 34,034 (67%) | classical-kāvya 28% · epic 21% · dharmaśāstra 18% · vedic 14% |
| bhs | 32,405 (79%) | **buddhist 98%** |
| mw | 20,250 (100%) | vedic 87% · buddhist 9% |
| lrv | 14,304 (87%) | classical-kāvya 76% · dharmaśāstra 15% |
| sch | 9,944 (86%) | classical-kāvya 26% · lexical-kośa 24% · epic 12% |
| pwkvn | 6,755 (81%) | classical-kāvya 27% · epic 18% · dharmaśāstra 13% |
| md | 47 (100%) | vedic 100% |

The communities are exactly the ones a historian of the discipline would draw freehand, now
with magnitudes attached. Edgerton's BHS dictionary is an almost hermetically Buddhist
community — 98% of its tagged citation volume (Mahāvastu, Mahāvyutpatti, Lalitavistara lead its
edge list), with effectively zero Vedic or epic citation. The Apte line (`ap90` → `ap`) and
Vaidya are the classical-kāvya school: 59–79% kāvya, led by the Raghuvaṃśa in all three. The
Petersburg lineage (`pwg`, `pw`, `pwkvn`, and Schmidt's *Nachträge*) is the broad-spectrum
community — no tradition exceeds 28% in any of the four — and is alone in citing the indigenous
kośas at scale (a fifth of PWG's tagged volume). Monier-Williams' small tagged residue and
Macdonell read as Vedic, though both on unrepresentative yields (§5). Benfey sits between the
kāvya and epic profiles, consistent with its chrestomathy-anchored design.

**Caveat (blocking for submission).** The tradition map is `inferred`: 0 of its 119 rows are
human-reviewed as of 11-07-2026. The *topology* result (modularity) is independent of the map;
only the community *names* in Table 3 depend on it. The review sheet is queued
([agenda backlog #9](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/ATLAS_RESEARCH_AGENDA.md));
this section must be re-stated over the reviewed map before submission.

## 5 Limitations

1. **Resolution ceiling.** 57.8% of non-filtered `<ls>` tags resolve to a canonical text. The
   unresolved remainder is dominated by unkeyed abbreviations and is inventoried per dictionary
   in [`ls_citation_unresolved_top.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_unresolved_top.tsv)
   — a worklist, not a mystery. Results in §3–§4 describe the resolved graph.
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
5. **The title-synonymy tail is unmerged and inflates the private tail.** The curated alias
   table folds only hand-verified identifications, so spelling variants outside it remain
   separate nodes: Vaidya's `Raghuvanśa` (4,101 citations) does not fold into *Raghuvaṃśa*
   (19,922), nor `Manusmṛiti` (1,762) into *Manusmṛti*, nor `Rigveda` (837) into *Ṛgveda*, nor
   `Bhāgavata` (2,968) into *Bhāgavata-Purāṇa*. Each such miss both understates a major text's
   reach and adds spurious single-dictionary "texts" to the 608 of §3. The direction of the
   bias is therefore *against* the shared-canon reading; the modularity result (§4) is computed
   on the matrix as committed and would only sharpen if variants of shared texts were folded.
   The residual is quantifiable from the `variant_forms` column and is the dataset's top QA
   item.
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
8. **The tradition map is inferred and unreviewed** (§4 caveat): community *names* await the
   119-row human review; the modularity statistic does not depend on them.

## 6 Conclusion

Read as a citation network, the Sanskrit dictionary tradition is not one tradition. Its
citation mass concentrates on a few dozen texts, but the *arrangement* of citations is
significantly modular: a Buddhist lexicon, a kāvya-schoolroom line, a Vedic profile, and the
omnivorous Petersburg lineage each kept their own authorities, sharing only a thin universal
head — Rāmāyaṇa, Mahābhārata, Ṛgveda, Manusmṛti — that no single text of which reaches all
eleven dictionaries. The "canon of Sanskrit literature" implied by the dictionaries is a union
of school reading lists, not an intersection.

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
(1,701 edges),
[`ls_citation_nodes.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_nodes.tsv)
(912 nodes),
[`tradition_tags.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/tradition_tags.tsv)
(119 rows),
[`citation_canon.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/citations/citation_canon.json)
(topology statistics + provenance sidecar). The graph rebuilds in ~1 minute with
`python data/citations/build_ls_citation_graph.py` against sibling `csl-orig` and `csl-guides`
checkouts; the topology statistics with `npm run build-citation-canon`. An interactive view
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
  [H213](https://github.com/gasyoun/Uprava/blob/main/handoffs/H213-Opus_csl-atlas_ls_citation_graph_canonicalization_06.07.26.md);
  dataset built + merged in [csl-atlas PR #220](https://github.com/sanskrit-lexicon/csl-atlas/pull/220)
  (v1 in [PR #219](https://github.com/sanskrit-lexicon/csl-atlas/pull/219)).
- Canon topology test (H305) and tradition map (H340) by Fable 5 (`claude-fable-5`),
  07/08-07-2026.
- Full prose draft 11-07-2026 by Fable 5 (`claude-fable-5`) under
  [H677](https://github.com/gasyoun/Uprava/blob/main/handoffs/H677-Fable_csl-atlas_a50-citation-graph-prose_11.07.26.md);
  all figures recomputed from the committed dataset in the same pass.

_Dr. Mārcis Gasūns_
