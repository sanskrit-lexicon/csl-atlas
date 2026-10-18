# PD × DCS corpus-coverage dataset

_Created: 20-07-2026 · Last updated: 18-10-2026_

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
| [pd_publication_ledger.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_publication_ledger.tsv) | 35 | H6947 Deccan College ledger — fascicle-volume, year, general editor, opening/closing entry, pp; 24 measured + 11 print-only |
| [pd_volume_homogeneity.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_volume_homogeneity.tsv) | 35 | H6947 per-fascicle-volume entry size, chars, blocks, quotations and dictionary-source marking share |
| [pd_volume_homogeneity_bound.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_volume_homogeneity_bound.tsv) | 8 | H6947 the same measures for the 8 bound volumes |
| [pd_volume_homogeneity.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_volume_homogeneity.json) | — | H6947 totals, H6942/H6949 canaries, source decomposition, conversion diagnostics |

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

_Dr. Mārcis Gasūns_
