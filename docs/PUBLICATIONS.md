# Publications: 19-article track, book, manual, and Sanskrit-Russian dictionary

**Version**: 1.0 · **Date**: 2026-05-16
**Companion to**: [`MICROSTRUCTURE-MACROSTRUCTURE.md`](MICROSTRUCTURE-MACROSTRUCTURE.md), [`LEXICOGRAPHY_ROADMAP.md`](LEXICOGRAPHY_ROADMAP.md), [`OBSERVATORY_DESIGN.md`](OBSERVATORY_DESIGN.md)

This doc captures the **publication strategy and end-products** of the project:

1. **19 articles in 10 years** (the article schedule for higher-doctorate qualification — 15 original + 4 added 2026-05-16, see §6.2)
2. **Scientific monograph** (the Book)
3. **Practical manual** for Sanskrit lexicographers
4. **Sanskrit-Russian dictionary** (corpus-based, successor to Kochergina 1978)
5. **DH + Digital Lexicography trends-tracking infrastructure** (quarterly digest + annual briefing supporting the research program)

---

## 1. The 10-year publication plan

**Goal**: 19 peer-reviewed articles + scientific monograph + practical manual + Sanskrit-Russian dictionary by 2035. (15 articles scheduled below; Articles 16-19 added 2026-05-16, see §6.2 — schedule integration pending.)

**Author**: M. Gasūns, working toward higher-doctorate qualification.

### 1.1 Article schedule (15 articles, 10 years)

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

**Russian-language target**: 5 articles (33%).
**English-language target**: 10 articles (66%).
**Mixed publication count**: ~9 in Scopus/WoS, ~6 in Russian peer-reviewed.

**New (2026-05-31) — standalone methods paper**: *Anchoring on Sanskrit: deterministic cross-language sense alignment* (outline → [PAPER_SENSE_ALIGNMENT.md](PAPER_SENSE_ALIGNMENT.md)). Spun out of the R2 sense-splitter work; its empirical core — H1 (granularity is a tradition trait, not temporal), H2 (citation density predicts sense survival), H3 (derivatives copy/condense; Śabda-Sāgara reproduces Wilson **82% word-identical**) — see [R2_FINDINGS.md](R2_FINDINGS.md). Directly supplies evidence for **articles 3** (stemmatics WIL→SHS) and **9** (microstructure). Target: a short DH / computational-lexicography venue (~2027), EN.

### 1.2 Pre-requisite chain

Each article requires data from earlier phases. The dependency graph:

```
Phase A (Volunteer-hours)            → Article 1
Phase L0 (Convention cladogram)      → Articles 1, 3
Phase L2 (Lemma cladogram, sanhw1)   → Articles 2, 3 [DONE in part]
Phase L0.5 (Nirukta deep-dive)       → Article 4
Phase L1.5 (KOW⇄WIL study)           → Article 11
Phase L4 (Per-family analysis)       → Articles 2, 6
Phase M1 (Data-richness typology)    → Articles 7, 8
Phase M3-Bopp                        → Article 5 (MW-Bopp dependence test)
Phase L0.6 (Subentry analysis)       → Article 9
Phase L (compound coverage)          → Article 10
Phase F (Wikipedia backlinks)        → Article 12
Phase L9 (Specialized dicts)         → Article 13
KCH ingestion + L1.5+                → Articles 14, 15 + Dictionary

Phase P (Preface analysis)           → Articles 3, 5 (lineage ground-truth)

Book = synthesis of all 15 articles
Manual = practical extraction from research findings
Dictionary = end product of methodology applied
```

### 1.3 Strategic considerations

**Journal choice rationale:**
- **DSH, IJDL, D-Lib**: top DH / lexicography venues; methodologically focused
- **Indo-Iranian Journal, JAOS, WZKS, BSOAS**: prestigious Indological journals
- **Voprosy yazykoznaniya, Vestnik IVRAN, Vostok, Indoiranskie issledovaniya**: Russian flagship venues

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

## 2. The scientific monograph (the Book)

### 2.1 Working title

*Quantitative Sanskrit lexicography: 170 years of CDSL analysed computationally*

(working title; Russian/English versions both anticipated)

### 2.2 Vision

A scientific monograph that synthesises the 15 articles into a coherent narrative spanning:

- the history of Sanskrit lexicography from Wilson (1832) to the present
- the computational methods developed for measuring and comparing dictionaries
- the empirical findings about inheritance, coverage, and editorial style
- the practical lessons for future digital-lexicography projects

### 2.3 Target

| Item | Value |
|---|---|
| Year | 2033 |
| Length | ~400-500 pages |
| Languages | English (primary), Russian translation |
| Publisher | Brill (international) or Russian academic press |
| Audience | Specialists in Indology, DH, lexicography, history of linguistics |

### 2.4 Chapter outline (provisional)

| Chapter | Topic | Drawing from articles |
|---|---|---|
| 1 | Introduction: why measure lexicography? | 1 |
| 2 | The 170-year history of Sanskrit lexicography (Wilson to today) | 5, 6, 11 |
| 3 | A measurement framework: KPIs across four dimensions | 1, 7 |
| 4 | Lemma overlap and inheritance: the genealogy of CDSL | 2, 3 |
| 5 | The convention-fingerprint approach to dictionary stemmatics | 3, 8 |
| 6 | Indian Nirukta and Western etymology: comparative analysis | 4 |
| 7 | Microstructure: verbs, nominals, and their subentries | 9 |
| 8 | Macrostructure: how dictionaries organise themselves | 13 |
| 9 | Compound coverage (samāsa) in Sanskrit lexicography | 10 |
| 10 | Citation networks and literary-source coverage | 12 |
| 11 | The MW exception: one dictionary's gravitational pull | 7 |
| 12 | Sanskrit-Russian tradition: Kossovich, Knauer, Kochergina | 6, 11 |
| 13 | The data-richness typology L0-L10 | 8 |
| 14 | Toward a new Sanskrit-Russian dictionary | 14, 15 |
| 15 | Conclusions and implications for DH | synthesis |

### 2.5 Publishing logistics

- Use open-access where venue permits (CC-BY)
- Companion data + reproducibility materials at csl-observatory
- DOI minted via publisher
- Targeted reviewers: senior Indologists + DH-methodology experts

---

## 3. The practical manual

### 3.1 Working title

*A handbook for Sanskrit lexicographers: methods, tools, conventions*

(working title; multilingual editions anticipated)

### 3.2 Vision

A **practical manual** for working Sanskrit lexicographers — distilled from the research findings into actionable guidance. Audience: working lexicographers, graduate students, Wikipedians, OpenSanskrit contributors, anyone building or maintaining a Sanskrit dictionary.

### 3.3 Target

| Item | Value |
|---|---|
| Year | 2034 |
| Length | ~200-300 pages |
| Languages | English (primary), Russian translation |
| Publisher | Motilal Banarsidass (Indological canonical) or Russian academic press |
| Audience | Lexicography practitioners (academic + amateur) |

### 3.4 Chapter outline (provisional)

| Chapter | Topic |
|---|---|
| 1 | What is a dictionary? (theoretical framing, drawing on classical manuals) |
| 2 | Headword normalisation: the 7+ Patel conventions and their tradeoffs |
| 3 | Entry microstructure: what fields to include and how to mark them |
| 4 | Subentry typology: when to nest, when to separate |
| 5 | Citation conventions: full vs abbreviated, when and why |
| 6 | Etymology and Nirukta: the two traditions and their use cases |
| 7 | Macrostructure: alphabetisation, sectioning, indices |
| 8 | Digital encoding: TEI Lex-0, OntoLex-Lemon, native XML schemas |
| 9 | Quality assurance: validation, normalisation, roundtripping |
| 10 | Reproducibility: snapshots, version control, archival |
| 11 | Collaboration: how to run a distributed lexicography project (lessons from CDSL) |
| 12 | Tool ecosystem: csl-orig, csl-apidev, csl-observatory, transcoders |

### 3.5 Source materials

- The 15 research articles (provide empirical backing)
- Classical lexicography manuals (provided by M. Gasūns as .txt for ingest; see §5 below for how Claude will analyse them)
- The runbooks (cologne-issue-runbook + cologne-tooling-runbook) as exemplars of distributed-lexicography process

---

## 4. The Sanskrit-Russian dictionary (the end-product)

### 4.1 Vision

A quantitatively-grounded, corpus-based Sanskrit-Russian dictionary that supersedes Kochergina 1978 with:

- **~50,000 headwords** (vs KCH's ~30k — a 1.7× expansion)
- Per-headword **frequency** from a Sanskrit corpus (GRETIL, DCS, Sanskrit Heritage)
- Per-meaning **citations** from a curated corpus
- **Russian translations** validated against the existing Russian Indology tradition (KOW 1854, KNA 1893, KCH 1978, FRI 1956)
- **Etymology blocks** where applicable (Nirukta where Indian, comparative where Western)
- **Cross-references** to other CDSL dicts (lemma-linking)
- Digital-first (web + mobile + print); open data (CC-BY-SA 4.0)

### 4.2 Methodology (drawn from this entire research stream)

1. Use **sanhw1** as canonical lemma list (~470k SLP1 forms → ~150k canonical lemmas after normalisation) → select top ~50k by frequency
2. For each lemma, extract glosses from all CDSL Skt-Eng / Skt-Ger / Skt-Fra dicts
3. Machine-translate English/German/French → Russian, validate against KOW/KNA/KCH/FRI
4. Calibrate frequency from a Sanskrit corpus
5. Curate citations from CDSL's cited literature
6. Format per the practical manual (Book #2)

### 4.3 Target

| Item | Value |
|---|---|
| Year | 2035 |
| Working title | TBD (suggestion: *Санскритско-русский словарь нового поколения* / *A new generation Sanskrit-Russian dictionary*) |
| Headword count | ~50,000 |
| Languages | Sanskrit (source) → Russian (target) |
| Format | Digital primary (web + mobile + JSON/SQLite), print companion |
| License | CC-BY-SA 4.0 (data), GPL-3.0 (tooling) |
| Publisher | Russian academic press + open-access digital edition |
| Audience | Russian Sanskritists, students, public |

### 4.4 Effort estimate

**5-year project** (2030-2035), part-time, with 2-3 collaborators. Phased:
- 2030: Methodology design, prototype for letter `a-` (5-10k headwords)
- 2031-2032: Scale to 20k headwords across multiple letters
- 2033-2034: Complete the 50k entries
- 2035: Editorial review, publication, defense

---

## 5. DH + Digital Lexicography trends tracking

Per author request: help track trends in **(a) Digital Humanities** and **(b) Digital Lexicography**. Classical lexicography manuals will be provided as .txt by author for separate analysis (handled in the practical manual workstream, §3 above).

### 5.1 What I (Claude) can produce

| Cadence | Output | Where |
|---|---|---|
| **Monthly** | Bibliography curation: `data/dh_lexicography_bibliography.csv` updated with ~20-40 new papers per month, tagged by category and relevance | `data/` |
| **Quarterly** | Trend digest: tiered (top-20 + appendix), with implications-for-our-research section | `docs/trends/YYYY-QN.md` |
| **Annually** | Briefing document: ~10 pages, December each year, synthesising the trends + their implications for the dissertation + book + dictionary | `docs/trends/YYYY-annual.md` |
| **Quarterly** | Conference watch list: upcoming CFP dates and relevance | `docs/trends/YYYY-QN.md` (last section) |

### 5.2 What I CAN'T directly do (requires M. Gasūns)

- **Read classical lexicography manuals** (Hartmann & James 2001; Wiegand 1989-2017; Atkins & Rundell 2008; Apresjan; Karaulov; Geeraerts) — to be provided as .txt by author
- **Travel-conferenced reports** — only Claude reads, doesn't attend
- **Networking** with active researchers — your domain
- **Editorial / political reads** of journal-policy shifts — needs human judgement

### 5.3 Trend categories to track

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

### 5.4 Action items

1. **Now**: set up tracking infrastructure (Google Scholar alerts, arXiv RSS, conference calendar)
2. **Quarterly**: produce digest (Q1, Q2, Q3, Q4 each year)
3. **Annually**: produce briefing document (December)
4. **When you provide manuals**: ingest the .txt manuals, build `data/lexicography_principles.csv` mapping classical principles to digital implementations

---

## 6. Research questions

This section is **open for additions** — please list research questions you want included in the publication plan.

### 6.1 Confirmed (already in article schedule)

- Article 1: How do you measure a 170-year-old volunteer-driven lexicography project?
- Article 2: Which dictionaries inherit lemmata from which others, empirically?
- Article 3: Can computational stemmatics reconstruct CDSL's genealogy?
- Article 4: What is Wilson's Nirukta etymology and what Pāṇinian concepts does it use?
- Article 5: Did Monier-Williams (1899) inherit from Bopp (1847) — and how can we test it without direct citation?
- Article 6: What are the three Sanskrit-Russian dictionary traditions and how do they relate?
- Article 7: Why does MW receive disproportionate digital investment — and can we prove it?
- Article 8: How can we typologise data-richness in digital lexicography (L0-L10)?
- Article 9: What is the verb-derivation matrix across 35 dictionaries — and what does it reveal about completeness?
- Article 10: How does samāsa (compound) coverage differ between 19th-century and 20th-century dictionaries?
- Article 11: Is KOW (Kossovich 1854) a Russian translation of WIL (1832) — and what is the forensic evidence?
- Article 12: What are the citation networks in 19th-century Sanskrit lexicography — which texts are most-cited, by whom, when?
- Article 13: How do specialised dictionaries (Vedic, Buddhist, Mahābhārata) differ from general dictionaries in coverage and structure?
- Article 14: What is the Sanskrit-Russian dictionary tradition and how should a new corpus-based dictionary build on it?
- Article 15: What are the principles and prototype for a new corpus-based Sanskrit-Russian dictionary?

### 6.2 Additional research questions (captured 2026-05-16, prompting round 2)

Four publication-strategy and methodology questions surfaced via `AskUserQuestion` and answered by M. Gasūns. Each becomes a new article, comparison study, or named research thread as noted.

**Q5. Additional paper topics beyond the 15 already scheduled** — *all four selected*
- **Article 16: PWG as the European-Sanskrit backbone** — documents PWG → MW72, PWG → SHS, PWG → CCS, and the wider European tradition. Builds directly on the Round-1 lineage answers in [MICROSTRUCTURE-MACROSTRUCTURE §5.2](MICROSTRUCTURE-MACROSTRUCTURE.md#52-new--added-by-author-captured-2026-05-16-prompting-round-1).
- **Article 17: Hapax-legomena-as-copying-evidence — a forensic method** — methodology paper establishing rare-word overlap as the primary forensic instrument for derivation claims. Foundational for Articles 2, 3, 11, 16, 19.
- **Article 18: Grammatical-info coding variation across CDSL** — inventory of how gender, paradigm, and root-class are recorded per dict; ties to the 24 verb-entry + 10 nominal dimensions. Feeds the grammatical-metadata subsystem of the new Skt-Rus dictionary (Article 15).
- **Article 19: The Cappeller-to-Kochergina edge (CCS → KCH)** — standalone treatment of this cross-language, cross-century inheritance. Surprising enough to merit its own paper rather than a subsection of Article 11.
- **Article 20: Two axes of descent — separating content-inheritance from convention-inheritance** *(added 2026-06-03, decision "both")* — standalone DH-methods note from Phase L0/L0.7: the convention fingerprint (Patel 2016 gold) + the **content↔convention reformatting residual** as a reusable instrument for any corpus of related editions. Empirical core: MW absorbed PWG's lexicon (size-corrected: **70–82% of PWG's *rare* headwords** recur in MW; the raw 89–94% containment was size-confounded and is de-confounded in L0.8) but recoded its conventions (PWG→MW convention-bootstrap 0.02 vs formatting edges 0.70–0.81). Reuses the same result as **Paper H §5** ([`articles/paper_H_convention_vs_content_lineage.md`](articles/paper_H_convention_vs_content_lineage.md)). Venue: DSH / *Journal of Cultural Analytics*.
- **Article 21: Apparatus, not errors — how Monier-Williams inherited the Petersburg lexicon** *(added 2026-06-03, Phase L3 forensic suite)* — MW inherited Böhtlingk's **apparatus** (citation source-Jaccard 10–40× the null, 587 rare exact references shared for the same headword, 41,552 verse-truncations; deep homonym-split agreement 64–77% vs ~33% null; 70–82% of PWG's rare headwords) but **not his errors** (shares ≈0% of M. Ahlborn's 123 curated PWG headword typos — where PWG erred MW is correct; 0 shared print errors; English prose recomposed not translated). Decomposes "did X copy Y" into inventory / apparatus / error descent and tests each separately. Forensic complement to Article 20 / Paper H §5; builds on Article 17's hapax method. Remaining decisive test = shared *erroneous* citations vs DCS ground truth (Phase F4). Note + data: [`articles/article_21_apparatus_not_errors.md`](articles/article_21_apparatus_not_errors.md). Venue: DSH / *Journal of Cultural Analytics*.

**Q6. Comparison studies with non-CDSL Sanskrit projects to formalise** — *all selected, with refinements from M.G.*
- **Sanskrit Heritage (G. Huet)** — bundle with Hyderabad (Amba Kulkarni) as one combined thread; the two share coding lineage.
- **DCS (Digital Corpus of Sanskrit, O. Hellwig)** — used *instead of* pure GRETIL ("DCS is an advanced GRETIL"). Corpus-attestation reality check for CDSL headwords.
- **Hyderabad (Amba Kulkarni)** — bundled with Sanskrit Heritage above.
- **Pandanus (Prague)** — included as one more non-CDSL Sanskrit comparison target. M.G. notes: not yet familiar with this project. **TODO**: produce a one-page brief on Pandanus's scope/status before scoping the comparison study.

**Q7. Methodological questions to test explicitly in dedicated article sections**
- **Distance-metric choice (Jaccard vs. Bray-Curtis vs. Hamming)** — requires an explicit comparison section in Article 3 (computational stemmatics). Particularly important given dict-size asymmetry (WIL ~35k vs. MW ~165k entries) — Jaccard penalises large/small overlaps differently than Bray-Curtis. Bootstrap stability across distance choices should be reported.

**Q8. Russian-tradition / IVRAN research thread**
- **The Petersburg school as a Russian, not just German, institutional tradition** — re-frame Böhtlingk, Roth, Kossovich, and Minayeff as a Russian-institutional lineage, not "German Sanskritists who happened to live in Russia". Coherent with MICROSTRUCTURE §5.2 Q4 (Petersburg lexicographer thread) and Q1 (PWG-as-backbone). Becomes a **named research thread** (Petersburg Thread), not merely a section of Article 6. Threads into Articles 6, 11, 14, 16, 19.

### 6.3 Further questions — open for input

Templates for any additional research questions:

- *"Article N: How does X feature in Y dict family compare to Z feature in W dict family?"*
- *"Article N: Is hypothesis H about CDSL supported by signal S?"*
- *"Article N: What is the relationship between [structural dimension] and [historical fact]?"*

Each additional question becomes one of:
- A new article in the schedule (potentially shifting the timeline)
- A book chapter
- A dashboard chart
- A new phase in the lexicography roadmap

---

## 7. Open questions (next round)

1. **Russian co-authors**: who would you invite as named co-author on the Russian-language articles (4, 6, 11, 14, 15)?
2. **Funding strategy**: is the work entirely unfunded, or is there RSCI / RNF / similar funding to pursue?
3. **Dictionary working title**: any preferred Russian title for the planned Skt-Rus dictionary (Article 15 + Chapter 14 + the dictionary itself)?
4. **Article 1 timing**: should we start drafting now with current data, or wait for L0 / M1 to complete? (Methods draft already created at [`docs/articles/article_1_methods.md`](articles/article_1_methods.md).)
5. **Manual scope**: is the practical manual aimed at academics, or also at independent / amateur lexicographers (Wikipedians, OpenSanskrit contributors)?
6. **Defense timing**: do you have a target year for the higher-doctorate defense (2034? 2035?), affecting whether to compress or expand the 15-article schedule?
