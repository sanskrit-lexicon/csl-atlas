# PD × DCS corpus-coverage dataset

_Created: 20-07-2026 · Last updated: 20-07-2026_

What share of the **Poona Dictionary**'s cited source canon does the **Digital Corpus of
Sanskrit** hold? This directory is the first measurement — data, metrics, and crosswalk.
Full write-up: [reports/PD_DCS_CORPUS_COVERAGE_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_DCS_CORPUS_COVERAGE_2026.md).
Interactive page: `/tools/pd-dcs-coverage`. Handoff:
[H1336](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1336-Opus_csl-atlas_pd-abbrev-vs-dcs-corpus-coverage_19.07.26.md).

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

## Method

Anchored on DCS's **bounded** 276-text inventory (not on PD's ~2,400-work long tail), so
*covered* mass is exact at any frequency rank and everything primary-but-not-in-DCS falls out
as the **residue** — the point of the study. Every one of the 398,359 occurrences carries an
adjudicated `match_type`. Scripts:
[scripts/pd_extract_sigla.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_extract_sigla.py)
(harvest) →
[scripts/pd_dcs_crosswalk.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_dcs_crosswalk.py)
(classify + join).

**Sources.** PD =
[pd.txt](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/external_src/pd/pd.txt)
(external, read-only). DCS token counts =
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

_Dr. Mārcis Gasūns_
