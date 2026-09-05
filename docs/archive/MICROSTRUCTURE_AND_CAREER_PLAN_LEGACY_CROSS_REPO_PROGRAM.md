_Created: 04-06-2026 · Last updated: 05-09-2026_

# Legacy Cross-Repo Microstructure And Career Plan

Status: legacy reference only. This file predates the 2026-06-04 boundary
cleanup and mixes dictionary microstructure with career planning, publication
scheduling, standards tracking, and corpus-based dictionary plans. Use
`MICROSTRUCTURE_AND_CAREER_PLAN.md` for the current atlas pointer.

---

# Microstructure typology + Doktor Nauk career plan

**Version**: 1.0 · **Date**: 2026-05-16 · **Owner**: M. Gasūns + Claude Code
**Companion to**: [`LEXICOGRAPHY_ROADMAP.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/LEXICOGRAPHY_ROADMAP.md), [`L0_DESIGN.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/L0_DESIGN.md), [`METALEXICOGRAPHY_ROADMAP.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/METALEXICOGRAPHY_ROADMAP.md)

Boundary note 2026-06-04: atlas owns the dictionary microstructure,
macrostructure, and dictionary-publication evidence in this plan. Corpus
frequency, DCS/GRETIL/Heritage comparisons, TEI/OntoLex standards, and GitHub/org
tracking are external implementation paths.

This document captures three interconnected layers:

1. **Microstructure typology** of Sanskrit dictionary entries (verbs vs nominals)
2. **Subentry analysis expansion** (beyond Caus./Pass./Desid.)
3. **Visualisation catalog** (40+ chart types)
4. **10-year publication plan** for Doktor Nauk (15 articles)
5. **Book + manual + Sanskrit-Russian dictionary roadmap**

---

## 1. Microstructure typology — empirical findings from gam

Based on direct extraction of entries headworded "gam" from MW, MW72, AP, AP90, PWG, BEN, BOP (six gam entries across six dicts). The `gam` verbal root is **the most-structured possible entry** — it's the canonical test case for microstructure complexity.

### 1.1 What's actually in MW's gam entry

```
<L>63409<pc>346,3<k1>gam<k2>gam<h>1<e>1
<hom>1.</hom> <s>gam</s> ¦ <lang>Ved.</lang> <ab>cl.</ab> 1. <ab>P.</ab> <s>ga/mati</s>
(<ls>Naigh.</ls>; <ab>Subj.</ab> <s>gamam</s>, <s>ga/mat</s>; <ab>Pot.</ab> <s>game/ma</s>;
<ab>inf.</ab> <s>ga/maDyE</s>, <ls>RV. i, 154, 6</ls>);
<ab>cl.</ab> 2. <ab>P.</ab> <s>ga/nti</s> (<ls>Naigh.</ls>; <ab>Impv.</ab> 3. <ab>sg.</ab> <s>gantu</s>...)
...
[hundreds of meaning blocks with citations]
...
<ab>Caus.</ab> <s>gamayati</s> (<ls>Pāṇ. ii, 4, 46</ls>; ...) [9 sub-meanings]
<ab>Desid.</ab> <s>ji/gamizati</s> [4 sub-meanings]
<ab>Intens.</ab> <s>ja/Nganti</s> [2 sub-meanings]
<info whitneyroots="gam,34"/>
<info verb="genuineroot" cp="1P,2P,3P,1Ā"/>
<LEND>
```

**MW has THREE separate entries for gam**:
- Entry 1: the main verb (huge, all senses)
- Entry 2: just etymology (`[cf. βαίνω; Goth. qvam; Eng. come; Lat. venio]`)
- Entry 3: the homonym "gam = earth" (cross-references kṣam)

### 1.2 Verb-entry microstructure dimensions (24 found)

Every verbal entry in CDSL dicts may have:

| # | Dimension | Example in MW gam | Present in (sample) |
|---|---|---|---|
| 1 | Homonym number | `<hom>1.</hom>` | MW, MW72, PWG |
| 2 | Lemma in SLP1 | `<s>gam</s>` | all |
| 3 | Verbal class | `<ab>cl.</ab> 1.` | all |
| 4 | Voice | `<ab>P.</ab>` (parasmaipada) | all |
| 5 | Primary present form | `gacchati` | all |
| 6 | Multi-class display | cl. 1, cl. 2, cl. 3 alternatives | MW, MW72, PWG |
| 7 | Tense/mood paradigm dump | Subj., Impv., Pot., impf., perf., aor. | MW, PWG, BOP |
| 8 | Vedic vs Classical distinction | `<lang>Ved.</lang>` | MW only (explicit tag) |
| 9 | Pāṇinian sūtra cross-references | `<ls>Pāṇ. viii, 2, 65</ls>` | MW, MW72, PWG |
| 10 | Native commentary references | Naighantuka, Padapāṭha, Kāś. | MW, PWG |
| 11 | Substitution forms | `gacch` for `gam` | MW, MW72, PWG, BOP |
| 12 | Meaning blocks (numbered) | 17+ meaning lines | all |
| 13 | Literary citations per meaning | `<ls>RV.</ls>`, `<ls>MBh.</ls>` etc. | all (density varies) |
| 14 | Verbal-phrase / idiom subentries | "jānubhyām avanīṃ-√gam = to kneel" | MW (heavy), AP (some), PWG (sparse) |
| 15 | Causative subentry (Caus.) | `<ab>Caus.</ab>` block with sub-meanings | all |
| 16 | Desiderative subentry (Desid.) | `<ab>Desid.</ab>` block | all (when attested) |
| 17 | Intensive / Frequentative (Intens. / Freq.) | `<ab>Intens.</ab>` block | MW, AP (with freq.) |
| 18 | Passive subentry (Pass.) | mentioned inline | MW, AP, MW72 |
| 19 | Denominative subentry (Den.) | not in gam (verb root) | applicable to nominals |
| 20 | Preverb-prefixed subentries (anu-, abhi-, ati-) | extensive in PWG ("`— anu`", "`— aDi`", etc.) | **PWG is dominant** |
| 21 | Past participle subentry | "gata" with own meanings | BEN (heavy), PWG (in supplements) |
| 22 | Compound subentry (Comp.) | "Tad-gat-" etc. | BEN (explicit Comp.), MW (inline) |
| 23 | Etymology (Western: cognates) | Goth., Eng., Lat., Gk. | MW, MW72, BOP (extensive) |
| 24 | Cross-references (cf., see) | "cf. kṣam" | all |

### 1.3 Nominal-entry microstructure (10 dimensions — simpler)

From the inventory of common nominal entries (rāma, deva, dharma, etc.):

| # | Dimension | Notes |
|---|---|---|
| 1 | Homonym number | for polysemous nominals |
| 2 | Lemma in SLP1 | `<s>rAma</s>` |
| 3 | Inflection sample | `(rāmaḥ)` — masculine -a stem in MW |
| 4 | Gender markers | `m.` / `f.` / `n.` / `mfn.` (= all three) |
| 5 | Numbered meanings | senses 1, 2, 3 ... |
| 6 | Literary citations per meaning | RV., MBh., etc. |
| 7 | Compound listings | nominals that take rāma as first/last element |
| 8 | Derivatives | rāmaka, rāmin, rāmaṇa etc. |
| 9 | Etymology | rare in nominal entries (more common in verb entries) |
| 10 | Cross-references | "see X", "cf. Y" |

### 1.4 Per-dict microstructure signatures

| Dict | gam entry character | Distinctive structural features |
|---|---|---|
| **MW** | Hugely deep + polished | 3 separate L-entries; modern <info whitneyroots> tags; densest Pāṇinian cross-refs |
| **MW72** | Prose-heavy, less granular | Single mega-entry with prose subsections; transitional to MW's structure |
| **AP** | Indian-edited, citation-rich | Numbered meanings (∙²1); ~7-8 sub-meanings per Caus.; heavy classical poetry citations |
| **AP90** | Pre-AP version | Same skeleton, different formatting ({@1@} vs ∙²1); more page-break artifacts |
| **PWG** | Citation-dense, preverb-rich | Hierarchical `<div n>` numbering; extensive preverb subentries (anu-, abhi-, ati-, vyapa-, api-, …); German prose |
| **BEN** | Etymology-comparative | English caps for root (GAM); Greek cognates; explicit `Ptcple.`, `Comp.` subentries; numbered meanings {@1@}-{@13@} |
| **BOP** | Latin-comparative | Latin definitions; IE comparative (Goth., Gk., Lat., Lith., Irish); Pott citation; older Indological prose style |
| **WIL** (not in sample but Nirukta-rich) | Nirukta `.E.` etymology in 89% of entries | Indian semantic etymology not Western linguistic |

---

## 2. Subentry analysis expansion — 15 categories (was 7)

The user's initial list (Caus./Pass./Desid./Inten./Den./Periphr./preverbs+verb) is 7 categories. The gam analysis reveals **8 more** sub-structure dimensions worth measuring:

### 2.1 Verbal-derivative subentries (the original 6)
1. **Caus.** (causative) — `gamayati`
2. **Pass.** (passive) — `gamyate`
3. **Desid.** (desiderative) — `jigamiṣati`
4. **Intens.** / **Frequent.** — `jaṅgamīti`
5. **Den.** (denominative) — N/A for `gam` (applies to nominals like `kāmayate` from `kāma`)
6. **Periphr.** (periphrastic conjugation) — when attested

### 2.2 Preverb-derived subentries (PWG's signature)
7. **`anu-`** + verb (anugacchati = follow)
8. **`abhi-`** + verb (abhigacchati = approach)
9. **`ati-`** + verb (atigacchati = surpass)
10. **`vyapa-`**, **`api-`**, **`vi-`**, **`upa-`**, **`pra-`**, **`prati-`**, **`adhi-`**, **`abhy-ā-`**, **`upā-`**, **`saṃ-`**, etc.

Each preverb × verb pair could be a separate "sublemma" with its own meanings + citations + Pāṇinian refs.

### 2.3 Idiom / verbal-phrase subentries (MW's signature)
11. **Object + verb idioms** — e.g. `manasā gam` ("to observe"), `jānubhyām avanīṃ gam` ("to kneel"), `doṣeṇa gam` ("to accuse")

### 2.4 Participle-as-subentry (BEN's signature)
12. **`gata`** (past passive participle) — with its own meanings + compounds + citations
13. **`gantum`** (infinitive), **`gatvā`** (absolutive), **`gamya`** / **`gatya`** (with preverbs) — derived forms as separate sub-lemmata

### 2.5 Compound / samāsa subentries (BEN's, MW's)
14. **Compound types**: bahuvrīhi, dvandva, tatpuruṣa, karmadhāraya — derived compounds containing the lemma
15. **Compounded preverbs** — `pratīpaṃ gam` ("go against") — adverbial + verb constructions

### 2.6 Subentry counting strategy

For each dict, count per entry:
- Total subentries
- Subentries by category (the 15 above)
- Depth (does Caus. have its own Pass.? does abhi-gam have its own Caus.?)
- Subentry-to-main-entry ratio
- Per-letter density (do verb roots in the first letters have more subentries because they're better-studied?)

Output: `data/microstructure_subentries.csv` with columns:
`dict, lemma, n_subentries, subentry_categories, max_depth, total_chars_subentries`

---

## 3. Visualisation catalog (40+ chart types)

### 3.1 Already produced
1. **Bar**: per-dict lemma counts (sanhw1) — published
2. **Heatmap**: 41×41 Jaccard distance matrix — published
3. **Bar**: inheritance edges by containment — published
4. **Cladogram** (text-only Newick) — published; needs SVG render
5. **Heatmap**: contributor × repo commits — published
6. **Heatmap**: per-letter coverage per dict — published
7. **Stacked area**: issue typology over time — published

### 3.2 Microstructure-specific (NEW)
8. **Anatomy diagram** per entry: radial chart showing which dimensions present (out of 24 verb-microstructure features)
9. **Side-by-side entry comparison**: same lemma across 5 dicts, color-coded by feature
10. **Subentry tree** per verb (root → Caus. → Pass-of-Caus → …)
11. **Preverb × verb matrix** per dict (which preverb-prefixed forms attested)
12. **Verb-class distribution** per dict (cl. 1 vs 2 vs 3 vs 4 vs 5 vs 6 vs 10)
13. **Subentry density** per dict (subentries per verb-root entry, distribution)
14. **Subentry-category proportion** per dict (stacked-bar)
15. **Meaning-count distribution** per entry per dict
16. **Citation-density per meaning** distribution
17. **Compound coverage** per nominal entry per dict

### 3.3 Etymology / Nirukta (NEW)
18. **Nirukta-tradition heatmap**: which Pāṇinian terms (aff., neg., causal, krt, taddhita, upasarga, dhātu) appear per dict
19. **Bopp-cognate overlap heatmap**: MW × BOP cognate-set similarity
20. **Cognate-language coverage**: which languages (Goth., Gk., Lat., Lith., Slav., Russ.) cited per dict
21. **Etymology presence rate** per dict bar chart
22. **WIL .E. token cloud**: most-frequent Nirukta abbreviations

### 3.4 Genealogy / inheritance (planned)
23. **Bayesian DAG** of derivation: source → inheritor edges with confidence intervals
24. **Time-anchored stratigraphic plot**: dicts on vertical time axis, derivation arrows
25. **Animated cladogram**: growing tree as new dicts added 1822-2026
26. **Phylogenetic dendrogram** (rooted UPGMA / NJ / Bayesian comparison)
27. **Convention-fingerprint clustermap**

### 3.5 Citation analysis (planned)
28. **Citation truncation Sankey**: PWG `Rv. 1.22.16` → MW72 `Rv. 1.22.` → MW `RV.`
29. **Cited-source heatmap**: 35 dicts × ~100 Sanskrit texts cited
30. **Co-citation network**: text A frequently cited with text B in entries
31. **Per-letter citation density** (rare letters cite more from rare texts?)
32. **Pāṇinian sūtra reference network**: which sūtras most-cited per dict
33. **Vedic vs Classical citation balance** per dict

### 3.6 Coverage / completeness (planned)
34. **UpSet plot**: multi-set lemma intersections across top 10 dicts
35. **Per-letter publication-year matrix**: PWG vol1 1855 covered a-, vol4 1865 covered n-p…
36. **Coverage-tier histogram**: lemmas appearing in N dicts (N=1..41)
37. **Lemma exclusivity** per dict (unique contribution to canonical set)
38. **Print-page-to-digital-line ratio** per dict (density)

### 3.7 Cross-language (planned for L1.5+)
39. **Translation chains**: lemma → German (PWG) → English (MW) → Latin (BOP) → Russian (KCH/KOW)
40. **KOW vs WIL similarity matrix** for shared lemmas
41. **Bilingual gloss alignment** (per-lemma side-by-side)

### 3.8 Community / engineering (already partial)
42. **Force-directed dict-similarity network**
43. **Per-dict richness radar** (10 KPIs on radar per dict)
44. **Specialisation matrix**: contributor × dict commits
45. **Tech-stack evolution timeline**

---

## 4. The 10-year publication plan for Doktor Nauk

**Goal**: 15 peer-reviewed articles + scientific monograph + practical manual + Sanskrit-Russian dictionary by 2035.

**Author**: M. Gasūns (Kandidat Nauk, working toward Doktor Nauk — Russia's higher doctorate).

### 4.1 Article schedule (15 articles, 10 years)

| Year | # | Title | Audience / Journal | Lang |
|---|---|---|---|---|
| 2026 | 1 | Quantifying digital lexicography: a measurement framework for CDSL | DSH (Oxford) | EN |
| 2026 | 2 | The 41-dictionary CDSL lemma-overlap matrix: empirical evidence for inheritance | Indo-Iranian Journal (Brill) | EN |
| 2027 | 3 | Computational stemmatics of Sanskrit lexicography: WIL → SHS, PWG → PW, MW72 → MW | Historiographia Linguistica | EN |
| 2027 | 4 | Nirukta in Wilson's Sanskrit-English Dictionary (1832): corpus analysis of 39,701 etymological notations | Voprosy yazykoznaniya | RU |
| 2028 | 5 | From Petersburg to Cologne: 170 years of Sanskrit lexicography traced computationally | Bulletin of SOAS | EN |
| 2028 | 6 | Russian Sanskrit lexicography: Kossovich, Knauer, Kochergina — three Sanskrit-Russian traditions | Vestnik IVRAN | RU |
| 2029 | 7 | The MW exception: empirical proof of disproportionate digital investment in one dictionary | Digital Scholarship in the Humanities | EN |
| 2029 | 8 | Data-richness typology L0-L10 for digital lexicography | IJDL (Oxford) or D-Lib Magazine | EN |
| 2030 | 9 | Subentry microstructure in Sanskrit dictionaries: a verb-derivation matrix across 35 CDSL dicts | International Journal of Lexicography | EN |
| 2030 | 10 | Compound (samāsa) coverage in Sanskrit lexicography: 19th vs 20th century comparison | Indo-Iranian Journal | EN |
| 2031 | 11 | KOW = Russian Wilson: forensic evidence for cross-language inheritance | Wiener Zeitschrift / Vestnik MGU | EN/RU |
| 2031 | 12 | Citation networks in 19th-century Sanskrit lexicography | JAOS | EN |
| 2032 | 13 | Specialized vs general Sanskrit dictionaries: typology, coverage, and editorial signatures | IJDL | EN |
| 2032 | 14 | Sanskrit-Russian dictionary tradition: synthesis and a corpus-based proposal | Vostok | RU |
| 2033 | 15 | A new corpus-based Sanskrit-Russian dictionary: principles and prototype | Indoiranskie issledovaniya | RU |

**Russian-language target**: 5 articles (33%) — sufficient for VAK requirements.
**English-language target**: 10 articles (66%) — international visibility.
**Mixed publication count**: ~9 in Scopus/WoS, ~6 in VAK Russian.

### 4.2 Book + manual + dictionary

| Year | Deliverable | Audience |
|---|---|---|
| 2033 | **Scientific monograph**: *Quantitative Sanskrit lexicography: 170 years of CDSL analysed computationally* (Brill or Russian academic press) | Specialists in Indology, DH, lexicography |
| 2034 | **Practical manual**: *A handbook for Sanskrit lexicographers: methods, tools, conventions* (Motilal Banarsidass or Russian academic press) | Lexicography practitioners |
| 2035 | **Sanskrit-Russian dictionary** (corpus-based, quantitatively grounded — successor to Kochergina 1978) | Russian Sanskritists, students, public |
| 2035 | **Doktor Nauk defense** | Academy of Sciences |

### 4.3 Pre-requisite chain

Each article requires data from earlier phases. The dependency graph:

```
Phase A (Volunteer-hours) → Article 1
Phase L0 (Convention cladogram) → Articles 1, 3
Phase L2 (Lemma cladogram from sanhw1) → Articles 2, 3 [DONE in part]
Phase L0.5 (Nirukta deep-dive) → Article 4
Phase L1.5 (KOW⇄WIL study) → Article 11
Phase L4 (Per-family analysis) → Articles 2, 6
Phase M1 (Data-richness typology) → Articles 7, 8
Phase M3-Bopp → Article 5 (testing MW-Bopp dependence)
Phase L0.6 (Subentry analysis) → Article 9
Phase L (compound coverage) → Article 10
Phase F (Wikipedia backlinks) → Article 12
Phase L9 (Specialized dicts) → Article 13
KCH ingestion + L1.5+ → Articles 14, 15 + Dictionary

Phase P (Preface analysis) → Articles 3, 5 (lineage ground-truth)

Book = synthesis of all 15 articles
Manual = practical extraction from research findings
Dictionary = end product of methodology applied
```

### 4.4 Strategic considerations

**Journal choice rationale:**
- **DSH, IJDL, D-Lib**: top DH / lexicography venues; methodologically focused
- **Indo-Iranian Journal, JAOS, WZKS, BSOAS**: prestigious Indological journals
- **Voprosy yazykoznaniya, Vestnik IVRAN, Vostok, Indoiranskie issledovaniya**: Russian flagship venues (VAK)

**Article-pair pattern**: each year has one international (EN) + one Russian (RU) where possible, building both English citation footprint AND Russian academic-system credit.

**Authorship strategy** (per CONTRIBUTING.md):
- M. Gasūns first author on all 15 (primary intellectual lead)
- funderburkjim, drdhaval2785 as co-authors on data-foundation papers (1, 2, 3)
- Domain-specialist co-authors per topic:
  - Russian-tradition articles (4, 6, 11, 14, 15): Russian Sanskritist co-author
  - Compound article (10): IIT Hyderabad Sanskrit team
  - Bibliographic / citation network article (12): bibliometrics expert
- Claude (with appropriate disclosure) listed as methodological-assistant on each

**Velocity**: 1.5 articles per year average. Achievable with the data infrastructure now in place.

---

## 5. The end-product: Sanskrit-Russian dictionary (KCH successor)

**Vision**: a quantitative-grounded, corpus-based Sanskrit-Russian dictionary that supersedes Kochergina 1978 with:
- ~50,000-100,000 headwords (vs KCH's ~30k)
- Per-headword frequency from a Sanskrit corpus
- Per-meaning citations from a curated corpus
- Russian translations validated against existing Russian Indology tradition
- Etymology blocks where applicable
- Cross-references to other CDSL dicts (lemma-linking)
- Digital-first (web + mobile + print)
- Open data (CC-BY-SA 4.0)

**Methodology** (drawn from this entire research stream):
1. Use sanhw1 as canonical lemma list (~470k SLP1 forms → ~150k canonical lemmas after normalisation)
2. For each lemma, extract glosses from all CDSL Skt-Eng / Skt-Ger dicts
3. Machine-translate English/German → Russian, validate against KOW/KNA/KCH/FRI
4. Calibrate frequency from a Sanskrit corpus (GRETIL, DCS, Sanskrit Heritage)
5. Curate citations from CDSL's cited literature
6. Format per the practical manual (the Book #2)

**Estimated effort**: 5-year project (2030-2035), part-time, with 2-3 collaborators.

---

## 6. Macrostructure typology (added 2026-05-16 per author request)

While **microstructure** is what's INSIDE an entry, **macrostructure** is how the dictionary as a whole is ORGANISED.

### 6.1 Macrostructure dimensions to measure

| # | Dimension | Examples / values |
|---|---|---|
| 1 | Alphabetisation order | Sanskrit varṇamālā / IAST / German alphabetical (PWG) / English (WIL, MW) |
| 2 | Entry granularity | one lemma = one entry (MW) vs lemma + variants combined (PWG `gam (vgl. gā)`) |
| 3 | Homonym treatment | separate `<L>` entries (MW: 3× gam) vs hom-numbered same entry (PWG: 1. gam, 2. gam) |
| 4 | Compound treatment | each compound a headword (MW) vs nested under primary lemma (PWG `gata` subentries) |
| 5 | Section division | preface + body + indices + appendices structure |
| 6 | Volume division | by letter (PWG vol1=a-, vol4=n-p) vs by alphabet section vs by topic |
| 7 | Cross-referencing system | "see X" prose / `q.v.` / `<L>` reference numbers / hyperlinks |
| 8 | Index types | etymological / semantic / frequency / source-text / Pāṇinian-sūtra |
| 9 | Appendix presence | abbreviations / list of authors / citation conventions / errata |
| 10 | Numbering scheme | entry numbers / line numbers / page numbers (and granularity) |
| 11 | Headword normalisation convention | Patel-1 through Patel-7 (already measured) |
| 12 | Inclusion criteria | scope: classical only / Vedic only / Buddhist (BHS) / Mahābhārata (MCI, INM) |
| 13 | Exclusion criteria | what kinds of words explicitly omitted (vulgar, dialectal, post-classical) |
| 14 | Source-language acknowledgement | preface acknowledges which prior dicts used (foundational ground-truth) |
| 15 | Editorial-voice strategy | translator (e.g. Wilson translates Indian sources) vs original lexicographer (Apte composes) |
| 16 | Citation-format strategy | full reference (PWG) / abbreviated (MW) / minimal (newer dicts) |
| 17 | Typography / display | Devanagari + Roman / Roman-only / SLP1-tagged / IAST |
| 18 | Front-matter richness | preface length + introduction + grammar primer + abbreviations list |
| 19 | Versioning / edition history | first ed / revised / new ed / posthumous (per dict CITATION.cff) |
| 20 | Per-entry uniformity | every entry follows same template (modern) vs ad-hoc (older) |

### 6.2 Macrostructure × microstructure interaction

A dict at **macro-level "1 entry per compound"** (e.g. MW) will have **many more total entries** but **shorter individual microstructure** per entry. A dict at **macro-level "compounds nested under primary"** (PWG) will have **fewer total entries** but **deeper microstructure** per primary entry.

This explains the lemma-count differences:
- MW: 194k lemmas (many compounds as separate entries)
- PWG: 106k lemmas (compounds often nested)
- AP: 88k lemmas (mixed)

**KPI**: lemma-to-microstructure-depth ratio per dict.

### 6.3 Macrostructure-specific charts (added to §3 catalog)

46. **Front-matter length distribution** (preface chars per dict)
47. **Index-types-present matrix** (which dicts have which index appendices)
48. **Per-section type detection** (preface / body / appendices breakdown per dict)
49. **Volume × letter coverage matrix** (when each letter was first published per dict)
50. **Editorial-voice classification** (translator-style vs original-author-style)

---

## 7. DH + Digital Lexicography trends tracking (added 2026-05-16)

Per author request: help track trends in **(a) Digital Humanities** and **(b) Digital Lexicography**. Classical lexicography manuals will be provided as .txt by author for separate analysis.

### 7.1 What I can produce

**(a) Quarterly DH + Lexicography trend digest** — a markdown report each quarter (~2-3 pages) covering:

1. **New venues / papers** in DSH, JCA, IJDL, JoCCH, JADH (Japan), DLfM, DH/DH-Russia conferences
2. **Tool / platform releases** — TEI Lex-0 versions, OntoLex-Lemon updates, ELEXIS milestones, DARIAH developments
3. **Standards / methodology shifts** — FAIR principles, CARE principles, linked-open-data conventions
4. **LLM / NLP applications to lexicography** — recent papers using GPT/Claude/Llama for definition generation, headword alignment, sense disambiguation
5. **Open-data movements** — Wikidata-lexemes, OmegaWiki, Wiktionary statistics
6. **Sanskrit-specific DH** — WSC programs, ICOSAL, Sanskrit Computational Linguistics workshops, GRETIL/DCS/Heritage updates
7. **Russian-language DH** — DH-Russia conference, Russian-led Sanskrit projects

**(b) Bibliography curation** — a structured `data/dh_lexicography_bibliography.csv` updated monthly with new relevant papers, automatically scraped from:
- arXiv.cs.DL (Digital Libraries)
- arXiv.cs.CL (Computation and Language)
- DOAJ + DSH RSS feeds
- Google Scholar alerts (manual setup, you receive)
- Semantic Scholar API queries

**(c) Briefing document** — annual "state of digital lexicography" report (~10 pages, December each year) synthesising the trends + their implications for CDSL / your dissertation work.

**(d) Conference watch list** — quarterly calendar of upcoming relevant conferences with CFP dates.

### 7.2 What I CAN'T directly do (requires you)

- **Read classical lexicography manuals** (Hartmann & James 2001; Wiegand 1989-2017; Atkins & Rundell 2008; Apresjan; Karaulov; Geeraerts) — you'll provide as .txt
- **Travel-conferenced reports** — I can't attend conferences
- **Networking** with active researchers — your domain
- **Editorial / political reads** of journal-policy shifts — needs human judgement

### 7.3 Trend categories to track (the taxonomy)

| Category | Examples |
|---|---|
| **Standards** | TEI Lex-0, OntoLex-Lemon, LMF (ISO 24613) |
| **Infrastructure** | ELEXIS, CLARIN, DARIAH, OpenAIRE |
| **Methods** | computational stemmatics, phylogenetic methods in textual scholarship, LLM applications |
| **Open data** | Wikidata lexemes, BabelNet, ConceptNet, OmegaWiki |
| **Crowdsourcing** | Wiktionary growth metrics, citizen-lexicographer platforms |
| **AI / NLP** | sense embedding, headword disambiguation, automated dictionary creation |
| **Reproducibility** | snapshot strategies, version control for dictionaries, citation systems |
| **Sanskrit-specific** | GRETIL, DCS, Heritage Hub, Sanskrit Heritage Reader, OpenSanskrit |
| **Russian DH** | Compreno, Russian NLP corpora, Russian lexicography (RAS) |

### 7.4 Action items

1. **Now**: set up tracking infrastructure (Google Scholar alerts, arXiv RSS, conference calendar)
2. **Quarterly**: produce digest (deliverable Q1, Q2, Q3, Q4 each year)
3. **Annually**: produce briefing document (December)
4. **When you provide manuals**: ingest the .txt manuals, build a `data/lexicography_principles.csv` mapping classical principles to digital implementations

---

## 8. Open questions for next round

1. **Russian co-authors**: who would you invite as named co-author on the Russian-language articles (4, 6, 11, 14, 15)?
2. **Funding strategy**: is the work entirely unfunded, or is there RFFI / RNF / RSCI funding to pursue? Affects acknowledgements.
3. **Dictionary working title**: any preferred Russian title for the planned Skt-Rus dictionary (Article 15 + book)?
4. **Article 1 status**: should we start drafting Article 1 (Quantifying) NOW with the data we already have, or wait for L0 / M1 to complete?
5. **Manual scope**: is the practical manual aimed at academics, or also at independent / amateur lexicographers (e.g. Wikipedians, OpenSanskrit contributors)?
6. **Defense timing**: do you have a target year for Doktor Nauk defense (2034? 2035?), affecting whether to compress or expand the 15-article schedule?

_Dr. Mārcis Gasūns_
