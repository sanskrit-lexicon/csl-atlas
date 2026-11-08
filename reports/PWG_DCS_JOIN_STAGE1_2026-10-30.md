# PWG↔DCS Stage 1: the join, and what it does to A68's headline

_Created: 30-10-2026 · Last updated: 30-10-2026_

**Handoff:** [H7463](https://github.com/gasyoun/Uprava/blob/main/handoffs/H7463-GLM_csl-atlas_pwg-dcs-join-stage1_30.10.26.md)
(H7462's queued successor) · **Model:** GLM 5.3 (`glm-5.3`, ZCode full tier) ·
**Protocol:** [pwg-nws-pd-dcs-8294e5 report §8](https://github.com/gasyoun/Uprava/blob/main/research/notes/final_report_pwg-nws-pd-dcs-8294e5.md)
— pre-registered before this join ran; the interpretation grid below was committed first and is not retuned.

---

## TL;DR

The first PWG↔DCS citation-inventory join — the replication A68's limitations
section pointed at — is executed under the report's five pre-registrations.
**coverage(PWG_Ω) = 63.53 % stratum-excluded** (59.00 % pooled): far **above**
PD's work-bootstrap band (19.15–31.52 %) and above the pre-registered
contradiction threshold. **The pre-registered contradiction branch fires:**
"three-quarters of citation practice points outside DCS" is **false for PWG**
— it is a property of PD's late-20th-century breadth-heavy programme, not of
citation apparatuses as a class. **Divergence (a) fires in the same stroke:**
coverage(PWG_α) = 63.59 % ≈ coverage(PWG_Ω) ≠ coverage(PD_α) = 25.16 % — the
alphabetical-scope artefact is *absent* between PWG's own letters, so A68's
25.2 % headline measures PD's reading programme, not DCS's structure. **H2
fires:** PWG per-letter dispersion (32.19 pp over 32 letters ≥1k ql) exceeds
PD's fascicle span (19.99 pp) — letter-level pooling is banned for PWG too.

Every number regenerates from committed row-level TSVs under
`scripts/pwg_dcs_check.py` (exit 0); pins in
`tests/forensic/test_pwg_dcs_join.py` (3/3).

## 1. Stage 0 — substrate

| Register | Value | Status |
|---|---|---|
| Machine text | 54,634,244 B, sha256 pinned in `data/pwg_dcs/pwg_substrate_pins.json` | pinned |
| Entries | 123,366 | pinned |
| Raw `<ls>` tags | 801,788 | **reproduced exactly** |
| Quotation-linked attestations | 729,719 | **reproduced exactly** (pre-reg (a) denominator) |
| Deprecated registers | 568,730 / 570,817 | declared, never used |
| Distinct base sigla | 2,680 | new (locus-stripped + payload-extracted, canonical keys) |
| PWG_α frontier | k1 ≤ `apacaya` (PD's last letter-a headword): 132,483 ql | pre-reg α/Ω split |
| DCS catalogue | live page fetched 30-10-2026, sha `fcab8fb1…`, 285 texts, committed verbatim + TSV | snapshot-dated |

The per-tag walk replicates `count_units` segmentation exactly — including
the 14 tags whose payloads embed `{#...#}` blocks (raw but never
quotation-linked) and the Elavila-class tails. Two extraction facts worth
naming: the dominant tag form carries the siglum in the **payload**
(`<ls>ṚV. 2,3,2</ls>`), and `n="…"` values are continuation loci.

## 2. The join

Resolution: 2,680 sigla → manual adjudication table (97 rows, mass-first) →
bibliography exact-title (26 auto-hits) → unresolved residue (2,165 sigla,
29,599 ql = 4.1 % of mass). 515 works resolved, **65 held by DCS** (12.6 %).

| Metric | Value | Denominator |
|---|---|---|
| coverage(PWG_Ω) pooled | **59.00 %** | 430,570 / 729,719 ql |
| coverage(PWG_Ω) stratum-excluded | **63.53 %** | 400,054 / 629,718 ql |
| coverage(PWG_α) stratum-excluded | **63.59 %** | 73,380 / 115,390 ql |
| Work-level held share | 12.62 % | 65 / 515 resolved works |
| Token view (118-text anchor) | 93.98 % | PWG-cited share of the anchored 2026 token mass |

Per-stratum holdings check (pre-reg (c) — reported separately, never pooled;
"works" counts register sigla incl. unresolved tail rows, so held-work shares
here are upper bounds on resolution, while the work-level row above is the
resolved-only figure):

| Stratum | Share of ql | Coverage | Held / sigla |
|---|---:|---:|---:|
| primary | 68.82 % | 67.23 % | 47 / 2,556 |
| kosha/lexicon | 12.55 % | 62.65 % | 6 / 9 |
| catalogue/journal | 6.32 % | 0 % (excluded) | 0 / 20 |
| second-hand | 6.09 % | 68.69 % | 8 / 65 |
| grammar | 4.23 % | 0 % | 0 / 6 |
| edition-marker | 0.83 % | 0 % (excluded) | 0 / 3 |
| edition-split | 0.69 % | 100 % | 4 / 4 |
| manuscript | 0.46 % | 0 % (excluded) | 0 / 17 |

The second-hand stratum's 68.69 % is the mediation channel made visible: the
Bhāgavatapurāṇa mass (cited "nach Anführungen im VP. und ŚKDR.") lands on a
DCS-held work, but through another book — coverage of mediated mass is
reported, never pooled into the headline.

The kośa class is the report's kośa-reversal made numeric on the dictionary
side: PWG's lexicon stratum is 91,560 ql (12.6 % of exercised mass) and is
**62.65 % DCS-covered** — Abhidhānacintāmaṇi (two sigla), Amarakośa,
Trikāṇḍaśeṣa (DCS: Nighaṇṭuśeṣa), Rājanighaṇṭu and the Nirukta are held;
ŚKDR, Medinī and Halāyudha's Abhidhānaratnamālā are not.

## 3. G5 battery and H2

- Leave-one-out (works): **59.46–66.04 %**.
- Work bootstrap (B=2000, seed 20261030): 95 % interval **46.62–76.08 %** —
  PD's entire bootstrap band (19.15–31.52) lies outside it.
- Denominator band: 59.00 % (pooled 2,680-canon) – 63.53 % (stratum-excluded).
- Per-letter dispersion (H2): **32.19 pp** (min 50.61 % on *ph*, max 82.80 %
  on *jñ*) over 32 letters with ≥1,000 ql — exceeds PD's fascicle span
  (19.99 pp): **letter-level pooling banned**; PWG's α≈Ω aggregate equality
  is a cancellation, not stability.

## 4. Grid verdicts (pre-registered, not retuned)

| Branch | Fired? | Reading |
|---|---|---|
| Convergence (inside PD band) | **no** | 63.53 % ∉ [19.15, 31.52] |
| Divergence (a) PWG_α≈PWG_Ω≠PD_α | **yes** | 63.59 ≈ 63.53 ≠ 25.16 — the 25.2 % is PD's reading programme |
| Divergence (b) α≠Ω scope artefact | no | 0.06 pp apart in the aggregate |
| Contradiction (>60 %) | **yes** | "three-quarters outside DCS" fails for PWG; the residue claim is apparatus-**specific**, not apparatus-class |
| H1 programme artefact | supported via (a) | the headline is programme-relative; the benchmark reading of A68's method now needs the apparatus-type asymmetry stated explicitly |
| H2 letter pooling ban | **yes** | 32.19 pp > 19.99 pp |

What survives untouched: A68's four measured numbers, their bands, the genre
residue composition (PWG's residue concentrates in the same purāṇa/kāvya/
grammar clusters plus PWG-specific strata), and the "deep, not broad"
characterization **for PD**. What dies: any sentence that generalises PD's
coverage level to historical-dictionary apparatuses as a class. The A68
revision that lands this should be scoped accordingly (follow-up to H7462).

## 5. Limits

Single-siglum attribution per tag (continuation aliases folded by canonical
key); work-level resolution covers 96 % of mass, the 4.1 % unresolved tail is
excluded from work-level shares only; the token view is bounded to the
118-text anchor (full-corpus token weighting needs a per-text DCS token
dump); stratum boundaries follow the report's mandatory list with the
holdings-check refinement (kośa/grammar are holdable classes, measured, not
pooled away). Rāmāyaṇa/Śakuntalā/Suśruta locus regimes (pre-reg (d)) are
recorded in the adjudication notes, not yet machine-verified per locus.

## 6. Artefacts

| File | What it is |
|---|---|
| [`scripts/pwg_work_register.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pwg_work_register.py) | Stage 0 register builder (pins 801,788/729,719) |
| [`scripts/dcs_catalogue_parse.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/dcs_catalogue_parse.py) | catalogue snapshot → TSV |
| [`scripts/pwg_dcs_join.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pwg_dcs_join.py) | the join, strata, G5, grid |
| [`scripts/pwg_dcs_check.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pwg_dcs_check.py) | regeneration gate (exit non-zero on drift) |
| [`data/pwg_dcs/pwg_work_register.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pwg_dcs/pwg_work_register.tsv) | 2,680 rows: mass, α-mass, letters, lids |
| [`data/pwg_dcs/pwg_work_by_letter.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pwg_dcs/pwg_work_by_letter.tsv) | siglum × letter mass |
| [`data/pwg_dcs/pwg_dcs_works_joined.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pwg_dcs/pwg_dcs_works_joined.tsv) | the row-level join (strata, holdings, genres) |
| [`data/pwg_dcs/pwg_dcs_join_metrics.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pwg_dcs/pwg_dcs_join_metrics.json) | every published number |
| [`data/pwg_dcs/pwg_siglum_adjudications.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pwg_dcs/pwg_siglum_adjudications.tsv) | 97 manual rows, mass-first, with notes |
| [`data/pwg_dcs/dcs_corpus_catalogue_2026-10-30.html`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pwg_dcs/dcs_corpus_catalogue_2026-10-30.html) | verbatim snapshot, sha-pinned |
| [`tests/forensic/test_pwg_dcs_join.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_pwg_dcs_join.py) | 3 pin suites |

Next in the programme: the NWS layer in its three delimited roles (Stage 2),
then PD/PWG/NWS triangulation where this apparatus-type asymmetry does the
diagnostic work.

_Dr. Mārcis Gasūns_
