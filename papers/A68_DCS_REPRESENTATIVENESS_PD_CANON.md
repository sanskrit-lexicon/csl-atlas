# How representative is DCS of the Sanskrit lexicographic canon? Measuring corpus coverage of the Poona Dictionary's cited source canon

_Created: 05-08-2026 · Last updated: 05-08-2026_

**Paper ID:** A68 ([ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md)) ·
**Status:** draft 1 ·
**Data + first measurement:** [H1336](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1336-Opus_csl-atlas_pd-abbrev-vs-dcs-corpus-coverage_19.07.26.md),
Opus 4.8 (`claude-opus-4-8`), [PR #276](https://github.com/sanskrit-lexicon/csl-atlas/pull/276) ·
**Draft:** [H1867](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1867-Fable_csl-atlas_a68-pd-dcs-canon-paper-draft_29.07.26.md),
Fable 5 (`claude-fable-5`) ·
**Venue (TBD):** eLex / IJL / DSH / LREC ·
**Figures:** regenerate with `python scripts/build_a68_figures.py` — the script re-derives
every plotted number from the committed row-level data in
[data/pd/](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/pd) and refuses to
draw if any number drifts from
[pd_dcs_metrics.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_dcs_metrics.json).

---

## Abstract

The Digital Corpus of Sanskrit (DCS) is the largest lemmatised Sanskrit corpus and the
de-facto evidence base for computational work on the language. How representative is it of
the Sanskrit literary canon? We answer this by measuring DCS against the source canon of
*An Encyclopaedic Dictionary of Sanskrit on Historical Principles* (the "Poona Dictionary",
PD, Deccan College) — the most source-exhaustive lexicographic project ever attempted for
Sanskrit, whose citation apparatus constitutes a de-facto declaration of the canon. From
PD's published letter-*a* volumes we extract 398,359 citation-siglum occurrences (5,106
distinct sigla), adjudicate 100 % of the occurrence mass into primary / structural /
secondary classes, and join the primary works against DCS's bounded 276-text inventory at
two snapshots (2021, 2026). The answer is a study in two numbers that point in opposite
directions: DCS holds only **25.2 %** of PD's citation-weighted canon and roughly **one in
twenty** (118 of ~2,445) of its distinct works — yet **77.9 %** of DCS's own token mass
lies in PD-cited works. DCS is a deep sample of the archaic/classical core, not a broad
sample of the canon: what it misses, with high structure, is the purāṇas, the indigenous
lexicographic (kośa) tradition, classical kāvya, and the grammatical commentary layer. The
2021→2026 delta shows the gap closing from the Vedic end (+3.8 pp in five years). The
residue list, ranked by PD citation frequency, doubles as a priority queue for future
corpus digitisation. To our knowledge this is the first quantitative alignment of a
historical dictionary's citation apparatus with a digital corpus inventory, for Sanskrit or
elsewhere.

**Keywords:** Sanskrit, corpus representativeness, historical lexicography, citation
apparatus, canon, Digital Corpus of Sanskrit, Poona Dictionary

---

## 1. Introduction

Every corpus-based claim about a language is bounded by what the corpus holds. For
Sanskrit, the Digital Corpus of Sanskrit (DCS; Hellwig 1999–) has become the standard
substrate: lemmatised, morphologically analysed, and freely available, it underlies
frequency lists, dependency treebanks, word-embedding models, and the evidence layers of
digital dictionary projects. Yet the question of *what fraction of Sanskrit literature DCS
represents* has, to our knowledge, never been measured — partly because "Sanskrit
literature" has no agreed enumeration to measure against.

We propose that such an enumeration exists, hiding in plain sight: the citation apparatus
of the most ambitious dictionary ever undertaken for the language. *An Encyclopaedic
Dictionary of Sanskrit on Historical Principles* (Deccan College, Pune; hereafter **PD**)
was conceived by S. M. Katre in 1948 explicitly to document the whole written tradition on
historical principles, and its editors assembled a reading programme of unmatched breadth.
Every sense in PD is supported by dated citations, each pointing at a source via a siglum.
The set of works PD cites is therefore a de-facto declaration of the Sanskrit literary
canon — not as a theoretical ideal, but as *exercised*, citation by citation, by the most
source-exhaustive lexicographic project in the field.

This paper welds the two resources together. We extract and classify every
citation-siglum occurrence in PD's published volumes, resolve which cited works exist in
DCS, and compute coverage under three deliberately different weightings. Three questions
structure the study:

1. **Of what PD cites, how much does DCS hold?** (dictionary-weighted coverage)
2. **How many of PD's distinct cited works exist in DCS at all?** (title-level coverage)
3. **Of what DCS holds, how much does PD cite?** (corpus-weighted coverage)

The first two measure DCS against the canon; the third measures the canon-alignment of
DCS's own bulk. Their divergence — 25 % against 78 % — turns out to be the finding.

## 2. Related work

Corpus representativeness is a classical concern of corpus linguistics (Biber 1993;
McEnery & Hardie 2012), usually addressed prospectively at design time — balancing
registers, genres, and periods. Our problem is retrospective: given an existing
opportunistic corpus, measure its coverage against an external canon. For historical
languages the canon problem is acute, since no sampling frame of "all texts" exists;
proxies used elsewhere include library catalogues and national bibliographies. Using a
historical dictionary's *citation apparatus* as the canon proxy appears to be novel. It has
attractive properties: the apparatus is finite, frequency-weighted (a work cited 3,000
times is more canonical, in the dictionary's practice, than one cited once), and curated by
philologists whose explicit mandate was exhaustiveness.

For Sanskrit specifically, DCS's composition has been described by its creator (Hellwig,
various) and its texts enumerated in its own metadata, but we find no prior quantitative
alignment of DCS — or any Sanskrit corpus — against an external canon declaration. The
closest relatives are alignment studies between dictionaries (headword-overlap
measurements) and the practice, within digital lexicography, of linking dictionary
citations to corpus attestations (e.g. OED–corpus linkage work); neither measures corpus
representativeness against a citation apparatus. *(Related-work sweep to be deepened for
the venue version; this section is a sketch of the claim's novelty perimeter.)*

## 3. Data

**PD side.** The machine-readable PD text
([pd.txt](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/external_src/pd/pd.txt),
55 MB, 107,630 `<L>` entries; read-only external source) covers PD's published range —
letter *a-* to approximately *apaca-*, i.e. the six bound volumes issued 1976–2026,
~104,959 lemmas. All PD-side numbers in this paper are therefore **PD's canon as exercised
under the letter *a-***, not its full declared canon (§7).

**DCS side.** The bounded inventory of 276 token-bearing DCS texts with token counts at
two snapshots — DCS 2021 (4.58 M tokens) and DCS 2026 (5.69 M tokens) — from
[per_text_token_delta.csv](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Corpus-Delta-2021-2026/per_text_token_delta.csv),
with chapter counts from the DCS 2021 metadata and the
[DCS abbreviation list](https://github.com/sanskrit-lexicon/DCS/blob/master/DCS-abbreviation-list.txt).

**Committed intermediate data.** All derived tables are committed under
[data/pd/](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/pd):
the raw siglum census
([pd_siglum_raw.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_siglum_raw.tsv):
5,106 distinct sigla, 398,359 occurrences), the classified census
([pd_siglum_families.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_siglum_families.tsv)),
the DCS join
([pd_dcs_text_crosswalk.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_dcs_text_crosswalk.tsv):
118 covered texts with per-snapshot token counts and a coverage grade), and the headline
metrics ([pd_dcs_metrics.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_dcs_metrics.json)).
Extraction and join scripts
([pd_extract_sigla.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_extract_sigla.py),
[pd_dcs_crosswalk.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_dcs_crosswalk.py))
are committed alongside.

## 4. Method

### 4.1 Canon-membership criteria

Because "the canon" does the load-bearing work in this study, its membership criteria are
stated here explicitly rather than left implicit in the pipeline:

> **The PD canon**, as operationalised in this paper, is **the set of Sanskrit works that
> PD's published letter-*a-* volumes cite as primary sources**, weighted by citation
> occurrence count. A citation-siglum occurrence enters the canon denominator **iff** it is
> adjudicated class `primary` under the three-way scheme of §4.2. A *work* is a member of
> the canon iff at least one `primary` occurrence resolves to it.

Three consequences of this definition are intended and worth surfacing:

1. **The canon is frequency-weighted by the dictionary's own practice.** A work PD cites
   3,506 times (Padmapurāṇa) counts 3,506× in the citation-weighted metric. This reflects
   canonicity *as exercised* — the dictionary's revealed preference — not an editorial
   ranking we impose.
2. **Books *in* Sanskrit, not books *on* Sanskrit.** Modern scholarship PD cites
   (etymological dictionaries, epigraphic corpora, concordances) is excluded from the
   canon as class `secondary` (§4.2). The canon is the object-language literature.
3. **The canon is scoped to the published fascicules.** PD under letter *a-* exercises
   ~2,445 distinct works (skeleton-merged estimate; §5.2); the full dictionary's declared
   reading list is larger. We measure the exercised canon, which is what the data
   supports; the scope caveat is carried explicitly throughout (§7).

### 4.2 Classification of siglum occurrences

Every one of the 398,359 siglum occurrences is assigned exactly one class:

| Class | Criterion | Examples |
|---|---|---|
| **primary** | the siglum names a Sanskrit work (any period, any genre, including commentaries and śāstra) | `MahāBhā.`, `ṚV.`, `PadmP.`, `Kāśi.` |
| **structural** | the token is citation apparatus, not a work: grammatical case labels, locus sub-parts, Roman-numeral book/volume numbers, editorial markers | `Acc.`, `A.`, `iii.`, `Ed.`, `App.` |
| **secondary** | the siglum names modern scholarship *about* Sanskrit | `EI.` (Epigraphia Indica), `MW.`, `PW.`, `POK.`, `VIŚVA.` |

Primary occurrences are further split by the DCS join into **covered** (the work exists in
DCS's 276-text inventory) and **residue** (it does not). The classification achieves 100 %
adjudication of occurrence mass — every occurrence carries a class, clearing the ≥95 %
stop-condition set in the study design — with two conservative calls documented in §7
(`Kāśi.`, `Loc.`).

### 4.3 Design: anchor on the bounded side

PD's citation mass has a very long tail: the top 300 sigla carry only ~74 % of it, so
expanding every siglum to a title (5,106 sigla, most rare, many abbreviation variants) is
infeasible and unnecessary. The join is therefore anchored on **DCS**, which is bounded:
each of the 276 DCS texts is mapped to its PD siglum(s), making the *covered* mass exact
at any frequency rank. Everything primary that no DCS text claims falls out as the
residue. The cost of this design is asymmetric confidence — covered-set identifications
are individually adjudicated and high-confidence, while the residue's *title-level
denominator* (how many distinct works the residue represents) must be estimated from
siglum-variant merging (§5.2) — and we accept that cost because both headline metrics
(citation-weighted, token-weighted) depend only on the exact covered mass.

### 4.4 Metrics

1. **PD-citation-weighted coverage** = covered primary occurrences / all primary
   occurrences. *Of what PD cites, how much is in DCS?*
2. **Title-level coverage** = covered distinct works / distinct works PD cites (lower
   bound over raw sigla; estimate over consonant-skeleton-merged sigla). *How many of
   PD's works exist in DCS at all?*
3. **DCS-token-weighted coverage** = tokens in PD-cited DCS texts / all DCS tokens,
   at each snapshot. *Of DCS's own mass, how much does PD also cite?*
4. **Partial-coverage grade** — per covered text, whether DCS holds the work or a
   fragment, sized by `dcs_tok_2026` against the work's known extent.

### 4.5 Reproducibility

All four figures and every number in §5 regenerate from the committed data via
`python scripts/build_a68_figures.py`
([scripts/build_a68_figures.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build_a68_figures.py)).
The script re-derives the metrics from the row-level TSVs and cross-checks 12 values
against the committed
[pd_dcs_metrics.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_dcs_metrics.json),
aborting on any mismatch — so the paper's figures cannot silently drift from the data.

## 5. Results

### 5.1 Mass breakdown

Of 398,359 siglum occurrences in PD's letter-*a-* volumes
(Figure 1, [a68_fig1_mass_breakdown.svg](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/papers/figures/a68_fig1_mass_breakdown.svg)):

| Class | Occurrences | Share of all |
|---|---:|---:|
| **primary** — the canon denominator | 353,512 | 88.7 % |
| — of which covered by DCS | 88,929 | 22.3 % |
| — of which residue (not in DCS) | 264,583 | 66.4 % |
| **structural** (apparatus tokens) | 39,987 | 10.0 % |
| **secondary** (modern scholarship) | 4,860 | 1.2 % |

The "books in Sanskrit, not books on Sanskrit" framing survives contact with the data:
secondary scholarship is a real but small (1.2 %) minority, now quantified and excluded
from the canon.

### 5.2 The three coverage metrics

Figure 2
([a68_fig2_two_lenses.svg](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/papers/figures/a68_fig2_two_lenses.svg))
shows the headline result:

| # | Metric | Value |
|---|---|---|
| 1 | PD-citation-weighted coverage | **25.2 %** |
| 2 | Title-level coverage | **2.4 – 4.8 %** (118 of ~2,445 works) |
| 3 | DCS-token-weighted coverage | **77.9 %** (2026) · 74.1 % (2021) |

**Metric 1.** Of PD's 353,512 primary citation occurrences, 88,929 (25.2 %) point at works
DCS contains. Three-quarters of the dictionary's citation practice points at texts the
corpus does not hold.

**Metric 2.** DCS contains 118 of the distinct works PD cites. The denominator is
inherently fuzzy — unmerged spelling variants inflate a raw siglum count — so we report a
band: 118 / 4,986 raw primary sigla = **2.4 %** (lower bound; denominator over-counts), and
118 / ~2,445 consonant-skeleton-merged works = **4.8 %** (estimate). Either way the order
of magnitude is robust: even under the single letter *a-*, PD's exercised canon runs to
roughly 2,400 distinct works, of which DCS holds about **one in twenty**.

**Metric 3.** Weighting by DCS's *own* token mass inverts the picture: of DCS 2026's
5,688,416 tokens, 4,430,111 (77.9 %) lie in PD-cited texts. DCS's bulk — the Mahābhārata
(1.15 M tokens alone), Rāmāyaṇa, the Vedic corpus, the large medical saṃhitās — sits
squarely inside PD's canon. DCS is not a random sample of Sanskrit; it is a deep sample of
exactly the archaic/classical core the dictionary leans on hardest.

**Metric 4.** Most covered texts are graded `present`; two carry an explicit partial flag.
The Skandapurāṇa — 3,335 PD citations — is "covered" by ~16.5 k DCS tokens (≈ fragments of
one khaṇḍa) against a full text of hundreds of thousands of ślokas; the Kāśikāvṛtti by
~2.9 k tokens of a large grammar commentary. The crosswalk carries per-text token and
chapter counts so any "covered" claim can be sized against the work's real extent.

### 5.3 The residue: what DCS structurally misses

The most informative output is the ranked list of works PD cites most that DCS lacks
(Figure 3,
[a68_fig3_residue_top20.svg](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/papers/figures/a68_fig3_residue_top20.svg);
full data in
[pd_siglum_families.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_siglum_families.tsv)).
The top of the list: Padmapurāṇa (3,506 citations), Mahābhāṣya (1,934), Brahmāṇḍapurāṇa
(1,857), Rājataraṅgiṇī (1,840), Bhaviṣyapurāṇa (1,558), Vaijayantī (1,155),
Śiśupālavadha (916), Kādambarī (884), Raghuvaṃśa (616). Four clusters account for nearly
all high-frequency residue, and they *name* what DCS is structurally missing relative to a
historical dictionary's canon:

1. **Purāṇas.** DCS holds ~12 purāṇas; PD cites at least a dozen more it lacks (Padma,
   Brahmāṇḍa, Bhaviṣya, Brahma, Mārkaṇḍeya, Vāyu, Gaṇeśa, Viṣṇudharmottara…). The single
   largest residue item, the Padmapurāṇa, outweighs all but three *covered* texts.
2. **The indigenous lexicographic tradition (kośa).** Vaijayantī, Medinī,
   Nānārthasaṃgraha, Anekārthasaṃgraha, Viśvaprakāśa — a dictionary naturally cites other
   dictionaries; a corpus of running text holds almost none.
3. **Classical kāvya and nāṭaka.** No Raghuvaṃśa, no Kādambarī, no Śiśupālavadha, no
   Naiṣadhīyacarita, no Mṛcchakaṭika, no Mudrārākṣasa: the mahākāvya/drama backbone of
   classical literature is largely outside DCS.
4. **The grammatical/śāstric commentary layer.** The Mahābhāṣya, the Vārttikas, and the
   dense bhāṣya/ṭīkā apparatus a historical-principles dictionary leans on.

Because the residue is ranked by PD's own citation frequency, it doubles as a
**ready-made priority queue for digitisation**: the highest-leverage additions to any
future Sanskrit corpus are, in order, exactly these works (§6.3).

### 5.4 The 2021→2026 delta: the gap closes from the Vedic end

Token-weighted coverage rose from 74.1 % to 77.9 % (+3.8 pp) across the two snapshots
because DCS's growth was concentrated in PD-core texts — overwhelmingly Vedic prose
(Figure 4,
[a68_fig4_dcs_growth.svg](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/papers/figures/a68_fig4_dcs_growth.svg)):
the Śatapathabrāhmaṇa grew 3.7 k → 144.1 k tokens, the Harivaṃśa 0 → 86.0 k, the
Maitrāyaṇīsaṃhitā 5.7 k → 65.4 k, the Jaiminīyabrāhmaṇa 2.5 k → 53.7 k, the
Taittirīyasaṃhitā 1.9 k → 48.0 k. Covered-text tokens grew +30.7 % (3.39 M → 4.43 M) in
five years. The corpus is actively closing its gap with the dictionary's canon — from the
archaic end first, while the purāṇic/kāvya/kośa residue is so far untouched.

## 6. Discussion

### 6.1 Why the two headline numbers are both true

Metric 1 (25 %) and metric 3 (78 %) are not in tension; they answer different questions.
PD's citation practice is spread across an encyclopedic ~2,400-work canon, so a corpus
holding the frequent core still misses three-quarters of the citation mass. Conversely,
DCS's own bulk is a deep, non-random sample of the archaic/classical core, and that core
is precisely PD's most-cited material. The one-line synthesis: **DCS is representative of
the *core* of the Sanskrit canon but not of its *breadth*.** For corpus-linguistic tasks
grounded in the high-frequency classical core — frequency norms, morphology, the epic
register — DCS is well-aligned with the lexicographic gold standard. For any task needing
the purāṇic, lexicographic, or classical-kāvya breadth a historical dictionary documents —
sense inventories, historical semantics, intertextuality — DCS covers a quarter of the
ground and must be supplemented, and §5.3 says with what.

### 6.2 A dictionary and a corpus grow by different laws

The residue is not a permanent deficit but a moving front. DCS grew 4.58 M → 5.69 M tokens
in five years (+4.45 %/yr compounding); PD, hand-editing on historical principles, has
published its letter-*a-* volumes over five decades — a companion study in this repository
([PD_DCS_CORPUS_COVERAGE_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_DCS_CORPUS_COVERAGE_2026.md)
§8) works out the completion-horizon arithmetic and the comparative history of long
dictionary projects in detail. The implication that matters for this paper is
directional, and §5.4 shows it empirically underway: a corpus that grows by ingestion
closes coverage of the dictionary's canon from the high-frequency end within years, while
the dictionary deepens *analysis* — historical sense-development, etymology, homonym
adjudication — that no corpus supplies. They are complements, and the crosswalk built here
is the bridge: it lets corpus-based work state, per claim, whether its evidence base
covers the canonical ground the claim quantifies over.

### 6.3 The residue as a digitisation agenda

Because canon membership is frequency-weighted by the dictionary's own practice, the
residue ranking of §5.3 is an *evidence-based* priority list for Sanskrit corpus
development: digitising and lemmatising the Padmapurāṇa alone would move metric 1 more
than any other single text; the top-20 residue works together carry ~24 k citation
occurrences. No comparable prioritisation existed for Sanskrit; it falls out of the
crosswalk for free.

## 7. Limitations

- **Letter *a-* only.** PD is published *a-* to ~*apaca-* (6 bound volumes, ~105 k
  lemmas). Every number here is PD's canon **as exercised under letter *a-***, not its
  full declared canon. This is the single biggest caveat. Whether the *a-* sample is
  representative of PD's whole citation practice is untested — though *a-*'s known
  composition bias (privative and preverb compounds, hence more śāstra and kāvya
  citation contexts) gives no obvious reason to expect the covered/residue *structure*
  to invert. Locating the printed PD front-matter "List of Works and Abbreviations"
  would convert the exercised canon into the declared one; parked as follow-up.
- **No sourced siglum→title expansion.** The expected machine-readable MW
  abbreviation→title table turned out to be a coverage manifest, not an expansion
  dictionary, so siglum→title identification for the covered set is expert-adjudicated
  by hand (anchored on DCS's bounded inventory) rather than sourced from a printed list.
  Covered-set identifications are high-confidence; the residue's title-level
  denominator is an estimate band (§5.2), not a count.
- **One material ambiguous merge.** `Kāśi.` (1,380 occurrences) is read as the
  Kāśikāvṛtti — its two-volume pagination pattern matches the grammar commentary, not
  the Kāśīkhaṇḍa. Under the alternative reading it moves to residue and metric 1 drops
  from 25.2 % to ~24.8 % — immaterial to the finding. `Loc.` (646) is genuinely
  ambiguous between the *Locana* and the locative case label and is classed structural
  (conservative: it affects neither covered mass nor the result direction).
- **Coverage ≠ locus alignment.** We measure whether DCS *holds* a work PD cites, not
  whether DCS's edition matches PD's cited edition line-for-line; partial-coverage
  grades (§5.2, metric 4) bound but do not eliminate this gap.
- **Two snapshots only.** The growth-law observation (§5.4, §6.2) rests on the
  2021/2026 pair; a longer time-series would firm the rate.

## 8. Conclusion

Measured against the citation canon of the most source-exhaustive Sanskrit dictionary ever
attempted, the largest Sanskrit corpus is **deep, not broad**: it holds the Vedic-epic-
śāstric spine that carries 78 % of its own token mass and a quarter of the dictionary's
citation practice, while the purāṇic, lexicographic, and classical-kāvya breadth — some
2,300 works, three-quarters of the citation mass — remains outside it. The gap has
structure, a ranked priority list, and a measured closing rate. The method — reading a
historical dictionary's citation apparatus as a frequency-weighted canon declaration and
joining it against a corpus inventory — is portable to any language with a
historical-principles dictionary and a digital corpus, and the asymmetric-anchor design
(§4.3) makes it tractable even when the apparatus runs to thousands of sigla.

## Data availability

All inputs, intermediates, scripts, and figures are public:
[data/pd/](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/pd) (this
repository) · PD source text via
[SanskritSpellCheck](https://github.com/drdhaval2785/SanskritSpellCheck) · DCS token
inventories via
[VisualDCS](https://github.com/gasyoun/VisualDCS) and the
[DCS abbreviation list](https://github.com/sanskrit-lexicon/DCS/blob/master/DCS-abbreviation-list.txt).
Figures regenerate deterministically with `python scripts/build_a68_figures.py`.

## References (to be completed for the venue version)

- Biber, D. 1993. Representativeness in corpus design. *Literary and Linguistic
  Computing* 8(4).
- Hellwig, O. *The Digital Corpus of Sanskrit (DCS).* Electronic resource, 1999–.
- Katre, S. M. (founding ed.). *An Encyclopaedic Dictionary of Sanskrit on Historical
  Principles.* Deccan College, Pune, 1976–.
- McEnery, T. & A. Hardie. 2012. *Corpus Linguistics: Method, Theory and Practice.*
  Cambridge University Press.

---

_Dr. Mārcis Gasūns_
