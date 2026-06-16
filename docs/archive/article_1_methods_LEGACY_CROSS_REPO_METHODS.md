# Legacy Cross-Repo Article 1 Methods Draft

Status: legacy reference only. This file predates the 2026-06-04 boundary
cleanup and mixes GitHub/org observatory metrics, dictionary-atlas evidence,
external usage signals, and broad publication planning. Use
`article_1_methods.md` for the current ownership pointer.

---

# Article 1 — Methods section (DRAFT)

Boundary note 2026-06-04: this is a legacy observatory/publication draft kept
for research continuity. GitHub/org measurement implementation belongs in
`csl-observatory`; dictionary-structure evidence now belongs in `csl-atlas`.

**Full title** (working): *Quantifying digital lexicography: a measurement framework for the Cologne Digital Sanskrit Lexicon*
**Target venue**: World Sanskrit Conference 2028 (long paper) + *Digital Scholarship in the Humanities* (Oxford)
**Authors** (draft order): M. Gasūns, J. Funderburk, D. Patel, + Claude (with appropriate disclosure)
**Status**: METHODS SECTION DRAFT — Results to be added after Phases L0 (full) and M1 complete; §3.5 *Inheritance detection* drafted from the L0 preview (2026-05-28).
**Date**: 2026-05-28

---

## 3. Methodology

This section describes our four-dimensional KPI framework, the data sources, the volunteer-hour estimation methodology, and the reproducibility guarantees of the open observatory.

### 3.1 The four-dimensional KPI catalog

We organise lexicographic-project measurements into four orthogonal dimensions, each populated with a set of computable KPIs. The four dimensions and their rationale are:

**Activity** — measures *what was done and when*: issues opened, issues closed, commits authored, pull requests reviewed, releases tagged. This is the temporal pulse of the project. Activity KPIs are derivable from any git-hosted project's API metadata; they require no domain knowledge.

**Coverage** — measures *what is included in the lexicographic record*: which lemmata appear in which dictionaries, with what density, with what citation backing. Coverage KPIs require parsing of source XML and a canonical headword index (in our case, the pre-computed `sanhw1.txt` from Cologne's `hwnorm1` repository, which normalises ~470,000 headword variants into a single SLP1 namespace per Patel's (2016) conventions).

**Community** — measures *who contributed, when, and how their work is distributed*: contributor counts, retention curves, geographic distribution, bus-factor concentration, specialisation patterns. Community KPIs require the same git metadata as Activity, augmented by curated identity information (in our case, `data/people.yaml`, generated from project-wide CITATION.cff files).

**Ecosystem** — measures *what depends on or cites the lexicographic record*: web-display traffic (where available), external citations in academic literature, Wikipedia and Wiktionary backlinks, downstream tool consumption (mobile apps, JSON exports, SQLite snapshots). Ecosystem KPIs require ingest from external sources (web analytics, Semantic Scholar API, MediaWiki `exturlusage` endpoints).

Each KPI in our framework is **defined by a tuple** `(name, dimension, data source, computation method, visualisation type, frequency of refresh)`. The full catalogue contains 30+ KPIs across the four dimensions; we provide it as a downloadable CSV at `https://sanskrit-lexicon.github.io/csl-observatory/data/kpi_catalog.csv`. Section 5 (below) applies this framework to CDSL and reports headline findings.

### 3.2 Data sources

Our measurements draw on five categories of source:

1. **GitHub REST and GraphQL APIs** for the `sanskrit-lexicon` organisation (77 repositories, 12 years of history). We fetch issues (state=all), pull requests, commits since 2014, repository metadata, contributors, releases, and language statistics. Full snapshots are archived monthly in our `observatory/snapshots/YYYY-MM/` directory; snapshots are append-only and dated, so any chart can be reproduced from any historical state.

2. **The canonical CDSL master headword index** (`sanhw1.txt`, 469,844 unique normalised SLP1 lemmas across 41 dictionaries). This file is produced and maintained by the Cologne team and applies Patel's (2016) headword normalisation conventions. Use of this pre-computed index spares us the substantial effort of rebuilding lemma overlap matrices from the raw dictionary XML.

3. **Source XML of individual dictionaries** in `csl-orig/v02/<dict>/<dict>.txt`, for entry-level microstructure analysis (subentries, citations, etymology markers, grammatical tags). We process these per-dictionary using regex-based extraction calibrated against a manual annotation of a 10-entry sample.

4. **CITATION.cff files** in each dictionary's GitHub repository, providing authorship + publication-year metadata. We enriched all 34 dictionary-repo CITATION.cff files in May 2026 to include publication years, author lists, and preferred-citation blocks; the enrichment script is `observatory/enrich_citations.py`.

5. **External usage signals**: the Cologne University web analytics (Matomo, when accessible), Wikipedia and Wiktionary `exturlusage` queries across all language editions, and the Semantic Scholar API for academic citation tracking. These are deferred to a later phase (Phase F/G/M0a of the project roadmap) and reported here as future work.

All snapshots, intermediate transformations, and final chart data are version-controlled in the public `csl-observatory` repository and exported as CSV/Parquet from a stable URL namespace under `https://sanskrit-lexicon.github.io/csl-observatory/data/`.

### 3.3 Volunteer-hour estimation

We report a sensitivity range, not a point estimate, for the equivalent monetary value of CDSL volunteer labour. Our method has three steps.

**Step 1: classify each commit by effort class.** We use a heuristic combining commit-message regex, diff size, and file count to assign each commit to one of five effort classes: `trivial` (5-min, e.g. typo fixes), `small` (15-min, single-file edits under 50 lines), `medium` (60-min, multi-file edits with design decisions), `large` (180-min, substantial code or schema changes), `huge` (480-min, major refactors or new pipelines). Classification accuracy was validated against a 100-commit hand-labeled sample (Cohen's κ = TBD).

**Step 2: add issue/PR effort.** Each issue receives 5 minutes of triage time plus 45 minutes of resolution time (if closed). Each PR receives 30 minutes of review time. Comments add 5 minutes each. These per-activity time estimates derive from Beller et al. (2017) and Mockus & Herbsleb (2002).

**Step 3: apply three cost scenarios.** We multiply total estimated hours by three hourly rates:
- **Low**: €45/hour (PhD researcher in Germany, fully-loaded employer cost)
- **Mid**: €80/hour (senior software engineer market rate in Germany)
- **High**: €150/hour (Sanskrit-specialist consulting rate reflecting skill rarity)

The result is a range, e.g. "between €X million and €Y million across 12 years," rather than a single number. We argue this range *understates* the true cost because:
- It excludes unpaid time spent reading issues but not acting (typically 2-3× the acting time in OSS projects).
- It excludes offline correspondence and meetings (substantial in academic projects).
- The Sanskrit-specialist rate is conservative for the rarest skills (no Russian / Tamil / Czech-Sanskrit specialist rate is included).

We disclose all assumptions in a single table (§4.5) so reviewers can adjust the numbers.

### 3.4 Reproducibility

Every published chart is reproducible from public artifacts:

- **Source data** is in our `snapshots/YYYY-MM/` directories, append-only and dated.
- **Transformer code** is in `observatory/transform.py` and related scripts, all GPL-3.0.
- **Chart code** is in our Observable Framework site (`observatory/site/src/*.md`); the source markdown plus the CSV input produces the rendered SVG.
- **Annual data snapshots** are deposited to Zenodo with DOI minting via GitHub-Zenodo integration on release tags.
- **Code is preserved** at Software Heritage via SWH's GitHub crawler.

To reproduce any chart in this paper, the reader retrieves the named snapshot (`snapshot 2026-NN`), runs `python observatory/transform.py`, and rebuilds the site via `observable build` from the `observatory/site/` directory. We provide a Dockerfile that pins all dependencies.

A reader who wishes to extend the framework to a different lexicographic project would (1) configure the GitHub-fetch script for the target organisation, (2) adapt the headword-normalisation step to the project's conventions (or apply Patel's framework if Sanskrit), and (3) re-run the pipeline. The estimated effort to apply our framework to a comparable project (e.g. CDLI for Cuneiform, Perseus for Greek-Latin) is 2-3 weeks.

### 3.5 Inheritance detection: two complementary signals

The framework offers two formally distinct derivation signals. *Lemma overlap* measures **content inheritance**: the directed Jaccard containment of headword sets, computed over Cologne's 469,844-entry normalised SLP1 master index. *Convention fingerprint* measures **editorial register**: a 30-dimensional categorical vector covering sense-numbering style, citation format, etymology marking, grammar conventions, accent preservation, Pāṇinian-sūtra citation, and related features, of which dimensions 1–8 and 16 follow Patel's (2016) transcription schema and the remaining 21 are extracted from the CDSL source `.txt` files by deterministic regex with a per-dimension variance check. A priori, content and style should coincide; in our data they do not.

We compared UPGMA trees from both signals over the 30 dictionaries present in both data sources (the intersection excludes three Russian/kośa dictionaries not yet in `sanhw1`, and two reverse-direction English-Sanskrit dictionaries with no Sanskrit-side lemma signal). Three congruence measures agree. A Mantel test returns Pearson r = 0.228 with permutation p = 0.006 over 999 label-shufflings — significant but weak: convention explains roughly five percent of descent-distance variance. The Robinson-Foulds distance between the two topologies is 50 of a maximum 56, against a label-permutation random baseline of 56 ± 1, meaning only **three of twenty-eight internal clades appear in both trees**. Inversions between the two leaf orderings are 214 of 435, close to the 0.5 random expectation.

The three surviving clades are diagnostic of the condition under which both signals coincide. They are (CAE, CCS) — Cappeller's German (1887) and English (1891) editions of the same work; (AP, AP90) — Apte's 1890 original and its 1957 revised reissue by the same hand; and (SHS, WIL) — Shabda-Sagara (1900) and H. H. Wilson's *Dictionary, Sanscrit and English* (1832), with 95.3% lemma containment and the unusually close convention Gower distance of 0.053. The first two are same-author direct revisions; the third is a same-tradition derivation in which Shabda-Sagara adopts Wilson's distinctive Nirukta etymology convention — the `.E. {#…#}` particle introducing a Pāṇinian-style derivation, written as bare ` E. {#…#}` in Shabda-Sagara — intact. The pattern across all three is the same: convention recovers descent **where the editorial register is preserved across the lineage** — whether through same-authorship or through faithful adoption of the source's house conventions. Wherever a lineage crosses an author, language, or major re-editing boundary that *breaks* register, the signals diverge — most informatively within the Wilson tradition itself: W. Yates's 1846 octavo digest carries 91% of Wilson's lemmas but discards the Nirukta etymology, placing Yates at convention Gower 0.39 from both WIL and SHS while WIL and SHS remain tightly paired. The dictionaries whose position differs most between the trees overall are the specialised indexes (the Mahābhārata names index INM, Edgerton's Buddhist Hybrid Sanskrit dictionary BHS, and the Puranic indices PUI and MCI: distinctive content, generic formatting) and Monier-Williams 1899, whose distinctive house style places it peripherally in convention space while its near-universal lemma overlap places it centrally in lemma space.

This complementarity is the methodological justification for reporting both signals jointly. Convention-only evidence can be defeated by *convergent minimalism* — two compact bilingual glossaries from unrelated traditions may share a minimal-markup register without sharing material, as Yates (1846, an octavo digest of Wilson) and Stchoupak (1932, a Paris digest of the Petersburg dictionaries) do in our data. Lemma-only evidence says nothing about whether subsequent editors regarded the source as authoritative enough to adopt its house style. Joint agreement on both axes is the strong inheritance claim, and §5.2.1 reports the small set of dictionary pairs in our corpus that pass it.

Dictionary-structure artifacts are released under CC-BY-SA-4.0 from the atlas
data outputs; the deterministic extractor and comparison code are
`scripts/L0/s2_fingerprint.py` and `scripts/L0/tanglegram.py`. The current
phase-L0 validation protocol is documented in `docs/L0_HANDOFF.md` and
`ARCHITECTURE.md`.

**Figure 3.5.** Tanglegram of the convention fingerprint (left tree, UPGMA over a 19-dimension Gower distance with missing-cell handling) and the `sanhw1` lemma-overlap distance (right tree, UPGMA over Jaccard) for the 30 dictionaries present in both data sources. Leaf positions within each tree are planar by construction; connector thickness and colour intensity scale with each dictionary's rank displacement between the two trees, so the largest movers are visually emphasised. Only three internal clades — (CAE, CCS), (AP, AP90), and (SHS, WIL) — appear in both topologies; the remaining twenty-five of twenty-eight differ. All three surviving clades are direct-descent relationships in which the editorial register is preserved across the lineage. Source: `data/L0/preview/tanglegram.png`; metrics: `data/L0/preview/homoplasy_metrics.json`.

---

### 3.6 What this framework does NOT measure (limitations)

We are explicit about the boundaries of our methodology:

1. **Editorial quality** is not measured. We count corrections issued and resolved, but we do not assess whether the corrections improved the dictionary; that requires expert review beyond automated metrics.
2. **Linguistic accuracy** is not validated. Our lemma counts assume the published headwords are linguistically correct; errors in the source dictionary propagate to our counts.
3. **Citation appropriateness** is not assessed. We count literary-source citations but do not judge whether they support the gloss provided.
4. **Inter-dictionary derivation** is *suggested* by the framework's two complementary signals — lemma containment and convention fingerprint (§3.5) — but full chronological proof requires the additional analyses described in Papers L and H of our series.
5. **Volunteer-hour estimates** are inherently uncertain (we report a range to acknowledge this) and do not capture the intellectual leadership of long-term maintainers, which exceeds what time-on-task can quantify.

These limitations are mitigated by our open-data approach: any researcher who wishes to substitute different assumptions can do so using our raw snapshots.

---

## 5. Results: applying the framework to CDSL

We apply the four-dimension KPI framework of §3 to CDSL in four subsections (one per dimension) plus a headline equivalent-volunteer-hour estimate (§5.5). Each subsection's tables and figures are populated incrementally as the underlying data phases complete; the present draft reports only those results whose inputs are in hand. The Activity (§5.1), Community (§5.3), and Ecosystem (§5.4) subsections, and seven of the eight Coverage KPIs (§5.2), draw on Phase A–G data tracked by the external `csl-observatory` roadmap. One Coverage result — the joint inheritance test introduced in §3.5 — is fully populated and is reported below as §5.2.1.

### 5.2 Coverage

Of the eight Coverage KPIs planned for this subsection — headword count per dictionary, definition density, citation density, intra-dictionary cross-reference networks, print-page digitisation coverage, markup richness, encoding-roundtrip success, and issue-typology evolution — seven await the Phase B microstructure extraction. The single result available now is the joint convention/descent inheritance test introduced in §3.5, reported here as §5.2.1.

#### 5.2.1 Dictionary pairs that pass the joint inheritance test

We define a pair (A, B) to **pass the joint test** if (i) at least one direction of lemma containment between A and B reaches 0.85 in `data/sanhw1_inheritance_edges.csv`, and (ii) the convention Gower distance between A and B falls in the lowest quartile of pairwise convention distances over the 32 L0-subset dictionaries (in our data, conv distance ≤ 0.333; median = 0.444; n = 496 pairs). Twenty-two of the thirty-three published inheritance edges have both endpoints in the L0 subset; of these, **seven pass the joint test** (Table 5.2.1). (One pair identified as a shared topological clade in §3.5 — Apte's AP90 (1890) and AP (1957) by the same author — is absent from this candidate set: the published inheritance-edges file requires directed containment ≥ 0.85, which the substantially expanded AP does not reach against AP90 at the normalised lemma level, likely an artefact of normalisation across the two editions. The topology-level test of §3.5 is correspondingly more inclusive than the pair-level test reported here.)

The seven joint-passing pairs cluster into the three best-attested lineages of nineteenth-century Sanskrit lexicography. The Wilson tradition contributes WIL → SHS (95.3% containment, convention Gower **0.053**) — Shabda-Sagara (1900) inheriting both H. H. Wilson's lemmas and his distinctive Nirukta etymology convention from the 1832 quarto. The Petersburg tradition contributes PWG → PW (93.8% / 0.22) — Böhtlingk and Roth's seven-volume *grosses* Wörterbuch being abridged into Böhtlingk's *kürzere* edition (1879–1889) — together with CCS → PW (94.5% / 0.33) and CAE → PW (88.7% / 0.33) for Cappeller drawing on it. The Cappeller pair CCS → CAE (94.0% / 0.111) — the same author's German (1887) and English (1891) editions of the same work — is the second-strongest joint signal in the corpus, behind only WIL → SHS. The Macdonell → PW (88.7% / 0.22) and Grassmann → MW (87.8% / 0.29) edges close out the seven. Notably absent is YAT → SHS (89.4% / 0.39): Yates's 1846 octavo digest of Wilson dropped the Nirukta etymology in condensing the quarto, so although Shabda-Sagara incorporates Yates as well as Wilson on the content side, the convention signal places Yates outside the Wilson–Shabda-Sagara cluster — a fine-grained editorial-history finding the joint test is designed to surface.

**Table 5.2.1.** Inheritance pairs passing the joint convention/descent test (n = 7 of 22 candidates), sorted by convention Gower distance.

| Pair (A – B) | Best direction | Containment | Conv. Gower | Source year → Inheritor year |
|---|---|---:|---:|---|
| SHS – WIL | WIL → SHS | 0.953 | 0.053 | 1832 → 1900 |
| CAE – CCS | CCS → CAE | 0.940 | 0.111 | 1887 → 1891 |
| PW – PWG  | PWG → PW  | 0.938 | 0.222 | 1855 → 1879 |
| MD – PW   | MD → PW   | 0.887 | 0.222 | 1893 → 1879 |
| GRA – MW  | GRA → MW  | 0.878 | 0.294 | 1873 → 1899 |
| CCS – PW  | CCS → PW  | 0.945 | 0.333 | 1887 → 1879 |
| CAE – PW  | CAE → PW  | 0.887 | 0.333 | 1891 → 1879 |

The fifteen remaining inheritance edges in the L0 intersection fail the joint test — all because their convention distance, despite demonstrable content inheritance, exceeds the lowest-quartile threshold. The clearest single case is **Wilson → Yates (1832 → 1846): 92.6% containment but a convention Gower of 0.39, just above the lowest-quartile cut-off**. Yates condensed Wilson's quarto into a school octavo and adopted different sense-numbering, citation, and gloss-styling conventions in the process — most consequentially dropping the Nirukta etymology that Wilson and Shabda-Sagara share. The lineage is unambiguous but the editorial register diverged at the first generation. Ten of the remaining fourteen failures share a single inheritor: Monier-Williams 1899 (MW72 → MW, BOP → MW, BEN → MW, MD → MW, CAE → MW, PW → MW, PWG → MW, CCS → MW, VEI → MW, STC → MW, all with containment ≥ 0.85 and convention Gower between 0.39 and 0.61). Monier-Williams's published synthesis absorbed material from every available predecessor but standardised it to a distinctive house style — Vedic accent preservation, Pāṇinian-sūtra citation, cognate-language tagging, three-level grammar marking — that none of the source dictionaries used. The result is a systematic high-containment / high-convention-distance asymmetry centred on MW. The remaining four failures are SHS → YAT (the reverse-direction Wilson-tradition case discussed above) and three intra-Petersburg asymmetries (GRA → PW, BEN → PWG, BEN → PW), of the same flavour at smaller scale.

Conversely, eight unordered pairs are convention-close (Gower ≤ 0.12, in the bottom two percent of pairwise distances) yet absent from the inheritance edges entirely. They cluster around the indigenous Sanskrit–Sanskrit kośas (VCP–SKD at convention Gower 0.00, VCP–KRM and SKD–KRM both at 0.06), the minimal-markup bilingual glossaries discussed in §3.5 (YAT–STC, now at convention Gower 0.00 — perfectly identical across the seventeen dimensions both have populated, despite being an 1846 Calcutta digest of Wilson in English and a 1932 Paris digest of the Petersburg dictionaries in French, with no content overlap), and a Petersburg-adjacent cluster (PW–SCH 0.12, PW–INM 0.12). These are precisely the convergent-minimalism cases the joint test is designed to exclude from inheritance claims despite their proximity in convention space.

Seven of twenty-two candidate inheritance pairs — 32% — therefore carry both signals; the remaining fifteen (68%) carry only content inheritance, and a convention-fingerprint inheritance claim made about them would, on these numbers, fail the test. The full ranked table (all 22 pairs with both signals) is released as `data/L0/preview/joint_inheritance_table.csv` and the computation as `scripts/L0/joint_inheritance_table.py`.

---

## NEXT STEPS (TO DO BEFORE THIS PAPER IS COMPLETE)

- [x] **Phase L0 preview** (convention fingerprint over 19 informative dims × 32 dicts, missing-aware Gower, UPGMA + NJ; tanglegram vs sanhw1 lemma signal over the 30 common dicts; joint inheritance test over the 22 candidate inheritance pairs in the L0 subset): drafted as §3.5 (method) and §5.2.1 (8 joint-pass pairs + the 14 convention-divergent failures + 8 convergent-minimalism counterpoints). **Full Phase L0** (Patel annotation of the 9 transcription dims, KNA/KOW/AMAR sourcing, the gated Stage 3/4 with bootstrap CIs) still pending.
- [ ] **Phase M1 (data-richness typology)**: produces the L0-L10 placement of each dict — required for §4.3 Results
- [ ] **Phase A (volunteer-hour computation with finer commit classification)**: produces the headline numbers for §4.4 Results
- [ ] **References section**: pull Beller, Mockus, Patel, Huet, CHAOSS, plus 30-40 DH-lexicography references
- [ ] **Abstract** (200 words, written last)
- [ ] **Introduction** (700 words)
- [ ] **Related work** (500 words)
- [ ] **Results** (3000 words)
- [ ] **Discussion** (1000 words)
- [ ] **Conclusion** (250 words)

This Methods section is ~1700 words; the target overall length is ~8500 words (15-20 pages).
