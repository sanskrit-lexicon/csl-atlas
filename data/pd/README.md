# PD × DCS corpus-coverage dataset

_Created: 20-07-2026 · Last updated: 26-10-2026_

What share of the **Poona Dictionary**'s cited source canon does the **Digital Corpus of
Sanskrit** hold? This directory is the first measurement — data, metrics, and crosswalk.
Full write-up: [reports/PD_DCS_CORPUS_COVERAGE_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_DCS_CORPUS_COVERAGE_2026.md).
Interactive page: `/tools/pd-dcs-coverage`. Handoff:
[H1336](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1336-Opus_csl-atlas_pd-abbrev-vs-dcs-corpus-coverage_19.07.26.md).

## The headline

Over PD's published letter-`a-` volumes (107,630 entries, 398,359 citation occurrences):

| Metric | Value | What it answers |
|---|---|---|
| PD-citation-weighted coverage | **25.2 %** | Of what PD actually cites, how much is in DCS? |
| DCS-token-weighted coverage | **77.9 %** (2026) · 74.1 % (2021) | Of DCS's own text mass, how much does PD also cite? |
| Title-level coverage | **~2.4–4.8 %** | 118 of ~2,445 distinct works PD cites under `a-` |

**DCS is representative of the archaic/classical core but not of PD's encyclopedic breadth.**
Its own bulk (Mahābhārata, Rāmāyaṇa, the Vedas) is 78 % PD-cited, yet it holds only a quarter
of PD's citation practice — missing the purāṇas (Padmapurāṇa alone is cited 3,506×), the
lexicographic tradition (Vaijayantī, Medinī, Nānārtha), classical kāvya (no Raghuvaṃśa,
Kādambarī, Śiśupālavadha), and the grammatical commentary layer (Mahābhāṣya). The residue is
75 % of PD's primary citation mass. DCS's 2021→2026 growth was concentrated in exactly PD's
Vedic core (+3.8 pp token-weighted coverage; Śatapathabrāhmaṇa grew 3,718→144,139 tokens).

## Files

| File | Rows | What it is |
|---|---|---|
| [pd_dcs_text_crosswalk.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_dcs_text_crosswalk.tsv) | 118 | one row per DCS text PD cites — DCS title, PD sigla, PD citation count, DCS 2021/2026 tokens, DCS chapters, coverage grade |
| [pd_siglum_families.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_siglum_families.tsv) | 5,106 | every PD siglum with its `class` (primary / secondary / structural) and `match_type` (covered / residue) |
| [pd_siglum_raw.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_siglum_raw.tsv) | 5,106 | raw extraction — siglum, occurrence count, 3 sample contexts |
| [pd_dcs_metrics.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_dcs_metrics.json) | — | the four headline metrics + mass breakdown |
| [pd_residue_source_status.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_residue_source_status.tsv) | 45 | H7298 frozen per-work source status (DCS / GRETIL / wisdomlib portal+estate, rights, annotation, fragment state) for the 44 named-residue works + the Skandapurāṇa context row |
| [pd_dcs_residue_status_queue.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_dcs_residue_status_queue.tsv) | 45 | H7298 status-aware queue: ingest-annotate (9/10,262), acquire-digitise (6/9,229 = H6722's missing-everywhere), fragment-completion (6), unverified (24/9,685) |
| [pd_dcs_residue_status_queue.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_dcs_residue_status_queue.json) | — | H7298 lane summary, input hashes and the Skandapurāṇa verdict digest |
| [pwg_quotation_linked_tags.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pwg_quotation_linked_tags.json) | — | PWG's raw `<ls>` tags (801,788) split into the 729,719 that close a quotation and the 72,069 that do not — the denominator any PD↔PWG attestation ratio must name |
| [pd_dcs_2021_baseline.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_dcs_2021_baseline.json) | — | the 2021 baseline in both ends: like-for-like 74.06 % (the committed denominator, 4,577,021) and raw 74.04 % (4,577,913), and the six texts DCS-2026 dropped (892 tokens) |
| [pd_aob_declared_works.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_aob_declared_works.tsv) | 1,112 works / 1,118 editions | declared AOB canon, work groups — a **clean-subset floor**, not the full declared list (see Caveats) |
| [pd_aob_declared_canon_audit.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_aob_declared_canon_audit.json) | — | H6923 denominator audit: what 1,419 / 1,118 / 1,464 each measure, and the 7.78–8.32 % band |
| [pd_aob_row_test_1473.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_aob_row_test_1473.json) | — | H6969 row test: per-page census of the 42 printed AOB pages, the 7 repeated column-header rows that inflate R1 1,476 → **1,469 entry rows**, and the verdict on the 2003 *Outlook* "1,473 texts" figure |
| [pd_aob_entries.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_aob_entries.tsv) | 1,444 (1,437 usable) | H6720/H6960 printed AOB entry inventory (one row per printed row, tails reassembled across OCR wraps) with its harvested match, route and exercise state |
| [pd_aob_declared_entries.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_aob_declared_entries.tsv) | 1,437 | H6932 declared-entry table — the usable inventory projected to siglum / title / year / page, reproducible with `python3 scripts/pd_aob_declared_entries.py --check`; the landed denominator point is 118/1,437 = 8.21 % |
| [pd_aob_declared_entries.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_aob_declared_entries.json) | — | H6932 counts, input hashes, the edition-to-work collapse and every candidate 118/N (landed point 1,437 / ruled central 1,476 / census 1,464 / header-corrected 1,469 / structural 1,476 / reparse 1,517) |
| [pd_aob_sigla_reconciliation.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_aob_sigla_reconciliation.tsv) | 2,955 | H6720/H6960 discrepancy list — `harvest_not_in_aob`, `join_unconfirmed_at_entry`, `aob_never_cited` (+ near-miss), `join_miss_siglum_equal`, OCR fragments |

| [pd_aob_sigla_reconciliation.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_aob_sigla_reconciliation.json) | — | H6720 aggregates: three presence measures, never-cited split, method, input hashes |
| [pd_inheritance_metrics.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_inheritance_metrics.tsv) | 6,866 | H6948 per-headword probe rows (sampled, stratified by marked × entry size) — citation Jaccard / strict subset / target coverage / gloss Jaccard per shared headword, with `marked`, `marked_strict`, `marked_mw`, `marked_pw` |
| [pd_inheritance_distributions.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_inheritance_distributions.json) | — | H6948 aggregates: sampling frame, input SHA-256s, marks census (broad and strict), macro inventory vs PWG/MW and DCS, shared-abbreviation `mappable_share`, calibration with bootstrap CIs, the three distributions, and the script's own verdict |
| [pd_quotations_by_entry.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_quotations_by_entry.tsv) | 107,630 | H6949 quotation-level unit — one row per entry: `{#...#}` blocks, quotations, siglum loci, further references, attestations |
| [pd_quotations_vs_pwg.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_quotations_vs_pwg.tsv) | 4,093 | H6949 PD against PWG on the same lemmas, both measured with the same quotation rule — counts and ratios |
| [pd_quotations_summary.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_quotations_summary.json) | — | H6949 totals, distribution, top-20, the PWG comparison block, input hashes |
| [pd_index_works.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_index_works.tsv) | 2,031 | H6992 vision transcription of the printed *Index of Works* (pp. LXXXIX–CXXVII = leaves 98–136), all 39 pages complete; 1,622 rows print a siglum, 409 do not |
| [pd_index_works_by_page.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_index_works_by_page.tsv) | 39 | H6992 page inventory: printed page, DjVu leaf, row count, blank-siglum count, subcodes and transcription status per page |
| [pd_index_works_siglum_delta.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_index_works_siglum_delta.tsv) | 2,528 | H6992 Index-vs-AOB-vs-harvest siglum delta (`in_both`, `in_aob_only`, `in_families_only`, `index_only`, `index_blank`, `aob_only`) with exact and near-match columns |
| [pd_index_works_summary.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_index_works_summary.json) | — | H6992 method, schema, verified/blank counts over the transcribed pages, printed subject subcodes kept separately from the 62 integer classes, reconciliation aggregates and backlog |
| [pd_canon_ledger.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_canon_ledger.tsv) | 14 | 24-10-2026: every canon base that has been quoted (1,118 / 1,419 / 1,437 / 1,464 / 1,469 / 1,476 / 1,517 / 1,622 / 2,031), its 118/N, the Index→AOB join (981 of 1,622 = 60.5 %), and the 562-row divergence between the two printed counts — one row per measure, `--check` green |
| [pd_canon_ledger.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_canon_ledger.json) | — | 24-10-2026: the ledger's input sha256s and the rule it encodes — no percentage without its base, and the 1,118 floor is never a denominator |
| [pd_publication_ledger.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_publication_ledger.tsv) | 35 | H6947 Deccan College ledger — fascicle-volume, year, general editor, opening/closing entry, pp; 24 measured + 11 print-only |
| [pd_volume_homogeneity.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_volume_homogeneity.tsv) | 35 | H6947 per-fascicle-volume entry size, chars, blocks, quotations and dictionary-source marking share |
| [pd_volume_homogeneity_bound.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_volume_homogeneity_bound.tsv) | 8 | H6947 the same measures for the 8 bound volumes |
| [pd_volume_homogeneity.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_volume_homogeneity.json) | — | H6947 totals, H6942/H6949 canaries, source decomposition, conversion diagnostics |
| [pd_policy_matched_class.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_policy_matched_class.tsv) | 104,950 | H7297 frozen per-headword class from the H7110 rule (`simplex` / `derivative` / `compound` / `unclassified`) with the printed analysis for the 4,093 shared lemmas — the join unit of the policy-matched table; rebuild with `--build --pd <pd.txt>` |
| [pd_policy_matched_density.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_policy_matched_density.tsv) | 6 | H7297 the policy-matched comparison: one row per stratum (simplex, derivative, compound, unclassified) with its PD/PWG denominators, ratio, bootstrap CI, median and below-parity count, plus the **standardised pooled** and **raw** rows side by side |
| [pd_policy_matched_inventory.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_policy_matched_inventory.tsv) | 11 | H7297 PD-only inventory policy — headwords, zero/≤1-attestation counts, median, mean and attestation mass by class for PD-only against the shared set; the 23.2× contrast is labelled `inventory_contrast` and is **not** a citation measure |
| [pd_policy_matched_density.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_policy_matched_density.json) | — | H7297 envelope: homograph policy, class rule and source hash, strata, the standardised/pd-mix/raw/simplex-only estimators, bootstrap settings, the frozen below-parity membership hash, inventory policy and canaries |

| [page_economics.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/page_economics.tsv) | 3 | H7109 PD / PWG / OED page economics — pages, entries, lines, characters, per-page rates, columns, page size, each row naming its own source and page basis; regenerate with `python3 scripts/pd_page_economics.py --pd <pd.txt> --pwg ../csl-orig/v02/pwg/pwg.txt` |
| [oed_page_sample.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/oed_page_sample.json) | 4 pages | H7109 the OED sample measured on page images — edition statement (1933 corrected re-issue of OED1 1928, vol. IV F–G), printed page and leaf IDs, columns, printed lines per column, visual entry counts, characters per column from the page's own OCR layer |
| [pd_family_composition.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_family_composition.tsv) | 11 | H7110 family composition — per family: `pd_headwords`, `pwg_headwords`, classified count, compound/derivative/simplex counts and shares, one example per class (SLP1 `k1`) |
| [pd_family_composition.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_family_composition.json) | — | H7110 envelope: the classification rule and suffix set, source SHA-256s, the 103,127 population reconciliation (102,747 analyses + 380 CORRECTIONS blocks), the whole-alphabet split, five examples per class per family, the privative recount under both rules, the density recompute, and the >15 pp ledger |

## Policy-matched density (H7297)

The raw 8.55× attestation / 9.53× quotation multiple over the 4,093 shared lemmas is not an
artefact of the shared set's family mix. Stratified by the H7110 class of each lemma, PD is
denser **inside every stratum** — 7.53× simplex, 8.56× derivative, 9.13× compound — and the
equal-weight standardised pool is **8.41×** (95 % CI 7.68–9.27, stratified lemma bootstrap),
against the unchanged raw **8.55×**. The 340 below-parity lemmas are frozen by membership
hash (simplex 110, derivative 17, compound 209, unclassified 4). PD-only headwords are a
separate, inventory-policy result: 100,866 extra headwords carrying a median of **one**
attestation each, so the **23.2×** headword-inventory contrast is a lemmatisation-choice
ratio and never a citation measure or a typical per-headword claim. Builder
[`scripts/pd_policy_matched_density.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_policy_matched_density.py)
(`--check` needs no source text); write-up
[reports/PD_POLICY_MATCHED_DENSITY_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_POLICY_MATCHED_DENSITY_2026.md).

## Family composition (H7110)

The A68 §6.2 table shows PD's lemmatisation policy on *anna* (877 headwords, 78.1 % compounds)
and *agni* (2,312, 74.6 %). H7110 classifies every family inside *a*–*apaca-* from PD's
printed analysis parenthesis and applies a 15 pp rule: only *atha* (173 headwords, 63.1 %
compounds, 29.4 % simplex) is a table-worthy exception; the privative *a‑* and negative
*an‑* sets are 99.9 % compounds by construction (8,894 entries under the draft's literal
prefix rule, 9,452 once accented privatives like *á-cyuta* are counted, which moves the
without-privatives density multiple 21.3× → 21.1×). Full write-up:
[reports/PD_FAMILY_COMPOSITION_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_FAMILY_COMPOSITION_2026.md).

## Two-layer validation (H7275)

The 25.2 % headline is **not stable as a fascicle-level constant**: across the 24
measured fascicles it ranges 16.9–36.9 % (12 of 24 outside ±2 pp), while
leave-one-fascicle-out stays at 24.9–25.6 % and a work-level bootstrap gives
19.2–31.5 %. The recomputed pooled value is 88,363 / 348,430 = 25.36 % over mapped
primary sigla (the pinned H1336 point is 25.16 %). The 11 print-only ledger rows
(2009–2019) are unmeasured: a 300-slot sample is frozen from the ledger alone and
recorded as **STOP_NO_PRINT_ACCESS**, not substituted with machine-text rows.
Tables: `pd_two_layer_fascicle.tsv`, `pd_two_layer_class.tsv`,
`pd_two_layer_stability.json`, `pd_print_only_sample_manifest.json`; builder
[`scripts/pd_two_layer_validation.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_two_layer_validation.py);
write-up [reports/PD_TWO_LAYER_VALIDATION_2026-10-26.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_TWO_LAYER_VALIDATION_2026-10-26.md).

## Silent inheritance (H6948)

The bracket mark is PD's only machine-visible trace of inheritance, so `1.67 %` needed a
ceiling. The probe measures it two ways. **The inventory is PD's own:** 92.5 % of PD's
104,773 letter-*a* headwords are absent from PWG and MW, and only 1.67 % of that residue is
a DCS lemma (40.3 % of the shared ones are — the control). **The bracket marks a gloss, not
an entry:** entries PD marks are *less* subsumed by the target's citations than unmarked
ones, while `[MW]`-marked entries overlap MW's gloss vocabulary 0.262 against 0.198, and a
marked entry is gloss-only (zero citations) 30.8 % of the time against 1.29 %. Read the
percentage as *marked* gloss attribution; it cannot be ranked. Write-up:
[reports/PD_SILENT_INHERITANCE_PROBE_2026-10-18.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_SILENT_INHERITANCE_PROBE_2026-10-18.md).
| [pd_dcs_earliest_lag.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_dcs_earliest_lag.tsv) | 2,458 | H6944 per-lemma lag between PD's first citation and DCS's earliest dated attestation, both in the Dharmamitra chronology |
| [pd_dcs_earliest_lag.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_dcs_earliest_lag.json) | — | H6944 join cascade, distribution and pinned input hashes |
| [pd_citation_order_sample.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_citation_order_sample.tsv) | 100 | H6943 sample: 100 letter-a sense divisions with per-entry citation order verdicts against PD/SWC, DCS and Dharmamitra clocks; builder [pd_citation_order_sample.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_citation_order_sample.py); report [PD_CITATION_ORDER_SAMPLE_2026-10-18.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_CITATION_ORDER_SAMPLE_2026-10-18.md) |
| [pd_citation_order_full.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_citation_order_full.tsv) | 9,689 | H7093 full population: one row per decidable letter-a sense division — citation sequence, per-clock dates, monotone/inverted verdict, direction, Kendall τ-a, adjacent-forward rate, decidable clocks; builder [pd_citation_order_full.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_citation_order_full.py); report [PD_CITATION_ORDER_FULL_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_CITATION_ORDER_FULL_2026.md) |
| [pd_citation_order_adjudication.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_citation_order_adjudication.tsv) | 200 | H7093 seeded adjudication frame — 100 flagged (mixed) + 100 monotone controls, stratified by deciding clock, DCS genre, citation-count bucket and position in *a-*; **unannotated**, so no κ and no adjudicated precision are reported yet |
| [pd_citation_order_full_summary.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_citation_order_full_summary.json) | — | H7093 population funnel, per-clock summary with exact CIs, the 10,000-replicate pooled permutation null and the hash-pinned inputs; `--check` recomputes every number from the TSV, `--refresh` re-derives it without the 55 MB PDScan text |
| [pd_sense_order_summary.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_sense_order_summary.json) | — | H7093 follow-up: per-clock test of whether a later sense's earliest quotation is later — two-sense forward rate, Kendall τ(position, earliest date) with a 5,000-replicate permutation null, median first→last drift; builder [pd_sense_order.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_sense_order.py); report [PD_SENSE_ORDER_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_SENSE_ORDER_2026.md) |
| [pd_sense_order_compare_summary.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_sense_order_compare_summary.json) | — | H7116 control: the same sense-order statistic on PWG, PW, MW and AP, joining their `<ls>` abbreviations to the same DCS/Dharmamitra clocks — per-dictionary entries, `<ls>`-resolution and dating denominators, two-sense forward rate with exact 95 % CI, τ with its 5,000-replicate null, τ by entry-size band, and the PD−control permutation test under a **pre-registered verdict rule** (result: withdrawn — PWG τ = +0.41 against PD's +0.32); builder [pd_sense_order_compare.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_sense_order_compare.py); report [PD_SENSE_ORDER_COMPARE_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_SENSE_ORDER_COMPARE_2026.md) |

## Method

Anchored on DCS's **bounded** 276-text inventory (not on PD's ~2,400-work long tail), so
*covered* mass is exact at any frequency rank and everything primary-but-not-in-DCS falls out
as the **residue** — the point of the study. Every one of the 398,359 occurrences carries an
adjudicated `match_type`. Scripts:
[scripts/pd_extract_sigla.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_extract_sigla.py)
(harvest) →
[scripts/pd_dcs_crosswalk.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_dcs_crosswalk.py)
(classify + join);
[scripts/pd_aob_sigla_reconciliation.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_aob_sigla_reconciliation.py)
reconciles the printed AOB authority against the harvest (H6720, write-up
[reports/PD_AOB_SIGLA_RECONCILIATION_2026-10-17.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_AOB_SIGLA_RECONCILIATION_2026-10-17.md)):
join-declared presence **63.32 %** of families (78.04 % of mass), **64.92 %** after 82
siglum-identity corrections the join missed, entry-located lower bound 51.65 %;
**26.61 %** of well-formed printed entries were never exercised under `a-`, half of them
only as OCR variants. H6941 re-confirms the join's unconfirmable rows against the printed
book's own text witnesses (PDF/A text layer + second OCR): **266 of 678 recovered, join
confirmation 79.03 % → 87.26 %.** H6960 repairs the wrap-fragment rule: 29 dated edition
entries the H6720 parser folded (Kādambarī, Aṣṭādhyāyī, the three Linganu editions …) are
back as rows and 15 part-word "recoveries" are folded, so the usable inventory is
1,437 (1,423 + 29 − 15), not 1,423.

**Quotations (H6949).** Everything above counts *sigla*; nothing above counts *quotations*.
The unit for that is defined in [reports/PD_QUOTATION_UNIT_2026-10-18.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_QUOTATION_UNIT_2026-10-18.md):
a quotation is a run of consecutive `{#...#}` blocks separated only by whitespace,
immediately followed by a siglum-plus-locus — **not** a block, which counts the headword,
etymology morphemes, and line-wrapped halves of one passage. Over the letter-*a* canon that
gives **302,442 quotations and 419,890 attestations** (384,217 siglum loci + 35,673 further
references), and against PWG measured the same way it puts PD's first letter at **52.4 % of
PWG's entire-alphabet attestation mass**. Rule: `scripts/lib/quotation_units.py`; pins:
`tests/forensic/test_quotation_units.py`.

**Volume homogeneity (H6947).** Entry size is stable at the median — **3 printed lines in
every measured fascicle-volume** — while the mean runs 4.36–6.21 lines by bound volume and
4.22–7.56 by fascicle. The H6942 dictionary-source marking share falls from **2.06 % in
vol. 1 to 0.39 % in vol. 8**, but not as a clean step after vol. 6: pre-v7 is 1.94 %, v7 is
0.88 %, v8 is 0.39 %, and the fascicle series is non-monotonic (7.2 = 1.88 %, 8.3 = 0.99 %
against 8.2 = 0.17 %). The fall is editorial/content, not a conversion artefact on the
machine-text evidence: general bracket use stays at 11–17 % of entries, long source
brackets are 29 in the whole corpus, and OCR near-misses of the seven sigla are 3 (none in
v7/v8). The print check that would falsify this is specified in
[reports/PD_VOLUME_HOMOGENEITY_2026-10-18.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_VOLUME_HOMOGENEITY_2026-10-18.md).
Rule: `scripts/lib/pd_marked_sources.py`; parser: `scripts/pd_volume_homogeneity.py`;
`--check` recomputes the tables and both baselines.

**Sources.** PD =
[PDScan 2020 `pdtxt.zip`](https://sanskrit-lexicon.uni-koeln.de/scans/PDScan/2020/downloads/pdtxt.zip)
(member `txt/pd.txt`, 55,122,076 B; © 2014 The Sanskrit Library / Thomas Malten, CC BY-NC-SA 3.0;
re-stage with SanskritSpellCheck's `detectors/get_external_source.py PD`). The older
`external_src/pd/pd.txt` path in `drdhaval2785/SanskritSpellCheck` no longer exists upstream —
the Cologne archive is the canonical copy. DCS token counts =
[VisualDCS Corpus-Delta 2021–2026](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Corpus-Delta-2021-2026/per_text_token_delta.csv)
(Digital Corpus of Sanskrit, Oliver Hellwig, CC BY 4.0).

## Caveats

- **Letter `a-` only.** PD is published a–~`apaca-` (6 of 37+ planned volumes), so these are
  PD's sources *as exercised under a-*, not its full declared canon — the single biggest
  caveat on every number.
- **Never prefix-cluster Sanskrit sigla.** `MahāBhā.` (Mahābhārata, 9,337) and `MahāBh.`
  (Mahābhāṣya, Patañjali's grammar, 1,934) differ by one vowel-length mark; a similarity
  merge fuses the largest epic with the most important grammatical commentary — one covered,
  one residue. Recorded as [SanskritLexicography FINDINGS §457](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).
- Siglum→title expansion is adjudicated by hand for the covered set, not sourced from PD's
  printed abbreviation list (a parked follow-up). `Kāśi.` and `Loc.` carry documented
  ambiguities, immaterial to the headline (report §6).
- **The declared-canon denominator is the central estimate 1,476 entry rows — 8.0 %, band 7.8–8.3 % (H6923 audit + MG ruling, applied H6933, 17-10-2026).** Metric 2's older
  1,419 is an *entry* count from the pass-1 parse, not the row count of any committed table;
  the committed re-parse gives 1,517 raw entries and the printed OCR supports 1,476 entry-like
  lines, so 118 / N = 7.78–8.32 % and the paper quotes 118/1,476 = 7.99 % (8.0 %, one in
  twelve and a half). `pd_aob_declared_works.tsv` (1,118 edition rows) is a
  *floor*: the pass-2 clean filter discarded 556 OCR-merged `Siglum Title` entry lines, so
  118 / 1,118 = 10.55 % overstates coverage and must not be quoted as the declared canon.
  Audit: [pd_aob_declared_canon_audit.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_aob_declared_canon_audit.json).
  H6932 (18-10-2026) makes the entry count reproducible: [pd_aob_declared_entries.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_aob_declared_entries.tsv)
  projects the H6720/H6960 inventory to **1,437 usable printed entries** —
  `118 / 1,437 = 8.21 %` — gated by `python3 scripts/pd_aob_declared_entries.py --check`.
  The ruled central estimate (1,476 → 8.0 %) stays the quoted denominator until MG re-rules;
  the 7.8–8.3 % band brackets both.
- **The printed AOB carries 1,469 entry rows, not 1,476 — the difference is the page's own repeated column header (H6969 row test, 18-10-2026).** The AOB prints
  `Abbreviation. Name of the Book, Author, Edition and Editor — Mode of Reference` at the top of its
  pages; the OCR catches it **7 times** (pp. 2, 13, 30, 37, 40, 41, 42) and every one of those lines
  passes the R1 entry-like rule, so the structural 1,476 is **1,469 entry rows + 7 header rows**.
  `118 / 1,469 = 8.03 %`, which still displays as the ruled **8.0 %** — no manuscript, figure or
  canary value moves; H6932 landed the reproducible point (1,437 → 8.21 %) and the choice between
  that point, 1,469 and the ruled ≈1,476 stays open for MG to re-rule. The corrected
  count is also the reference point for the 2003 *Outlook* figure of **1,473 texts**: it sits 4 rows
  above the recovered row floor and inside the OCR-loss ceiling (R2 = 99 un-recovered garbled
  lines), so it is *consistent* with the printed list but is **not an independent witness** for it —
  same producer (Deccan College), different time slice (a 1975-vintage corpus count) and a different
  object (texts excerpted, not books quoted). Test: [pd_aob_row_test_1473.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_aob_row_test_1473.json)
  ([`scripts/pd_aob_row_test_1473.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_aob_row_test_1473.py), `--check` green).

## Shared work-and-edition identity registry (H7296, Q3)

The identity layer over the Index, the AOB canon and the PW / PWG bibliographies:
2,031 Index rows → **1,923 work identities** (`PDW-…`), 6,072 edition-map records,
416 explicit unresolved rows (409 printed blank abbreviation cells + 7 structural
sigla), 57 siglum folds shared by more than one work and **never merged**.

| File | What it is |
|---|---|
| [pd_work_registry.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_work_registry.tsv) | works + unresolved identity rows; per-record provenance and `unresolved_class` |
| [pd_work_edition_map.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_work_edition_map.tsv) | every Index row, AOB edition, bibliography siglum, harvest attestation and `commentary_on` relation |
| [pd_work_registry.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_work_registry.json) | the same registry, machine-readable |
| [pd_work_registry_diagnostics.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_work_registry_diagnostics.json) | pinned input sha256, counts, canaries, validation contract |

Builder: `python3 scripts/pd_shared_work_registry.py --check`; pins:
`python3 -m pytest tests/forensic/test_pd_shared_work_registry.py -q`. All records
stay `unvalidated_pending_double_annotation` — no kappa and no adjudication are
claimed. The 3.11 % / 4.03 % and breadth/depth figures remain **preliminary until
rerun**; this layer does not recompute them. Write-up:
[reports/PD_SHARED_WORK_REGISTRY_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_SHARED_WORK_REGISTRY_2026.md).

_Dr. Mārcis Gasūns_
