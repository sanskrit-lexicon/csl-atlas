_Created: 30-10-2026 · Last updated: 30-10-2026_

# data/pwg_dcs — the PWG↔DCS Stage 1 join dataset (H7463)

Row-level substrate of [PWG_DCS_JOIN_STAGE1_2026-10-30.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PWG_DCS_JOIN_STAGE1_2026-10-30.md).
Every published number regenerates from these TSVs under
[pwg_dcs_check.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pwg_dcs_check.py) (exit non-zero on drift);
pins in [test_pwg_dcs_join.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_pwg_dcs_join.py).

| File | Contents |
|---|---|
| `pwg_work_register.tsv` | 2,680 base sigla: raw/ql/α mass, entry counts, letter spread, LIDs, sample n |
| `pwg_work_by_letter.tsv` | siglum × letter mass (per-letter dispersion, H2) |
| `pwg_siglum_adjudications.tsv` | 97 manual rows: work identity, stratum, DCS mapping, notes |
| `pwg_dcs_works_joined.tsv` | the join: stratum, resolution, dcs_title/genre/held, anchor tokens |
| `pwg_dcs_coverage_by_letter.tsv` | letter-level stratum-excluded coverage (letters ≥1,000 ql) |
| `pwg_dcs_join_metrics.json` | every published number incl. G5 battery and grid verdicts |
| `pwg_substrate_pins.json` | pwg.txt sha256 + declared registers + α-frontier |
| `dcs_corpus_catalogue_2026-10-30.html` | verbatim DCS live-catalogue snapshot (sha `fcab8fb1…`) |
| `dcs_catalogue_2026-10-30.tsv` | parsed snapshot: title/author/period/genre/text_id (285 texts) |
| `dcs_catalogue_pins.json` | snapshot sha + row count |

Denominators: quotation-linked = 729,719 (pre-reg (a)); raw = 801,788
(extraction register); α-frontier = k1 ≤ `apacaya` (PD's last letter-a
headword). The 2,680-siglum register is built from the exercised layer
(payload sigla + n-attr continuation loci, canonical keys) — never from a
whitespace crosswalk (pre-reg (e)).

_Dr. Mārcis Gasūns_
