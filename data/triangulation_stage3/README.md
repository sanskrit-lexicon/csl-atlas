_Created: 30-10-2026 · Last updated: 30-10-2026_

# data/triangulation_stage3 — the PD/PWG/NWS Stage 3 triangulation (H7484)

Row-anchored substrate of
[TRIANGULATION_STAGE3_2026-10-30.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/TRIANGULATION_STAGE3_2026-10-30.md).
The interpretation grid was committed **before** the triangulation ran
(commit `b531f96`, sha-pinned) and is not retuned; every published number
regenerates under
[triangulation_stage3_check.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/triangulation_stage3_check.py)
(exit non-zero on drift); pins in
[test_triangulation_stage3.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_triangulation_stage3.py).

| File | Contents |
|---|---|
| `grid_preregistration.md` | the pre-registered interpretation grid: branches BR1–BR6, §12-row outcome space, kill-exits; sha-pinned, machine-read |
| `triangulation_metrics.json` | every published Stage-3 number: inputs, row-level anchors, derived quantities, branch verdicts, §12-row verdicts |

Stage 3 adds no new measurement: it consumes the committed Stage-1/Stage-2
substrates ([data/pwg_dcs/](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pwg_dcs/README.md),
[data/nws_layer/](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/nws_layer/README.md),
data/pd/pd_dcs_metrics.json) and combines them under the grid. Rebuild:
`python3 scripts/triangulation_stage3_join.py` (deterministic, read-only
over inputs).

_Dr. Mārcis Gasūns_
