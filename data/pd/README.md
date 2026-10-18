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
| [pd_aob_entries.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_aob_entries.tsv) | 1,430 | H6720 printed AOB entry inventory (one row per printed row, tails reassembled across OCR wraps) with its harvested match, route and exercise state |
| [pd_aob_sigla_reconciliation.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_aob_sigla_reconciliation.tsv) | 2,954 | H6720 discrepancy list — `harvest_not_in_aob`, `join_unconfirmed_at_entry`, `aob_never_cited` (+ near-miss), `join_miss_siglum_equal`, OCR fragments |
| [pd_aob_sigla_reconciliation.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_aob_sigla_reconciliation.json) | — | H6720 aggregates: three presence measures, never-cited split, method, input hashes |
| [pd_quotations_by_entry.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_quotations_by_entry.tsv) | 107,630 | H6949 quotation-level unit — one row per entry: `{#...#}` blocks, quotations, siglum loci, further references, attestations |
| [pd_quotations_vs_pwg.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_quotations_vs_pwg.tsv) | 4,093 | H6949 PD against PWG on the same lemmas, both measured with the same quotation rule — counts and ratios |
| [pd_quotations_summary.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_quotations_summary.json) | — | H6949 totals, distribution, top-20, the PWG comparison block, input hashes |

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
join-declared presence **63.32 %** of families (78.04 % of mass), **64.88 %** after 80
siglum-identity corrections the join missed, entry-located lower bound 51.55 %;
**26.36 %** of well-formed printed entries were never exercised under `a-`, half of them
only as OCR variants. H6941 re-confirms the join's unconfirmable rows against the printed
book's own text witnesses (PDF/A text layer + second OCR): **269 of 681 recovered, join
confirmation 78.94 % → 87.26 %.

**Quotations (H6949).** Everything above counts *sigla*; nothing above counts *quotations*.
The unit for that is defined in [reports/PD_QUOTATION_UNIT_2026-10-18.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_QUOTATION_UNIT_2026-10-18.md):
a quotation is a run of consecutive `{#...#}` blocks separated only by whitespace,
immediately followed by a siglum-plus-locus — **not** a block, which counts the headword,
etymology morphemes, and line-wrapped halves of one passage. Over the letter-*a* canon that
gives **302,442 quotations and 419,890 attestations** (384,217 siglum loci + 35,673 further
references), and against PWG measured the same way it puts PD's first letter at **52.4 % of
PWG's entire-alphabet attestation mass**. Rule: `scripts/lib/quotation_units.py`; pins:
`tests/forensic/test_quotation_units.py`.

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

_Dr. Mārcis Gasūns_
