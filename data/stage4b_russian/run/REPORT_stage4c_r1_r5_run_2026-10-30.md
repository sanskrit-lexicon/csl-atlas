# Stage 4c — R1–R5 run on the Russian Словарь XI–XVII dump

_Created: 30-10-2026 · Last updated: 31-10-2026_

H7523 · executes the [H7518 pre-registration](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/stage4b_russian/stage4b_executability_verdict.json)
(PR [csl-atlas#687](https://github.com/sanskrit-lexicon/csl-atlas/pull/687)) · licence gate
released by **MG ruling 30-10-2026** («yes» to the Stage 4b closer: private hash-verified
analysis of the unlicensed dump in scope; the DB is NOT redistributed) · executor GLM-5.3
(ZCode), effort hard · dump: re-clone 2026-10-30T20:56:44Z, sha256 `532cad47…`
(byte-identical to Stage 4b), identity tie re-verified at 21:05Z
([identity_recheck](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/stage4b_russian/run/identity_recheck_2026-10-30.md)).

Unit convention (pre-registered): citation mass by **normalised siglum** (first
comma-segment of `Sources.Sokr`) — 825 groups over the 10,318 joined examples.

## Adjudications

| ID | Verdict | Number | Falsifier (pre-registered) |
|---|---|---|---|
| **R1** right-skewed citation mass | **SUPPORTED** | top decile = **57.0%** of joined mass (5.7× the 10% uniform bar; Gini 0.697; bottom half ≈ 4%); top sigla: Библ. 442 · Шестоднев Ио.екз.¹ 269 · Пов.Мерк.Смол. 256 | <0.20 or linear deciles — NOT fired (linearity R²=0.51) |
| **R2** complete-vs-selective density | **UNTESTABLE-ON-THIS-SUBSTRATE** (pre-declared fallback) | zero declaration hits in the open-code clone; no excerption-class column in `Sources` | n/a — never computed, never adapted |
| **R3** partial-apparatus artefact | **SUPPORTED** | Spearman ρ = **0.744** (496 shared sigla, p≈1e-88) between С-half and Т-half source-density rankings — materially < 0.90 | ρ≥0.90 (halves agree) — NOT fired |
| **R4** weighting divergence | **SUPPORTED, family-structured** | count-family weightings mutually coincide (word/meaning/example ρ 0.9986–0.9996; top-100 Jaccard 0.98) while **row-density diverges from all three at ρ≈0.57** | all pairwise ρ≥0.95 — NOT fired (min 0.5698) |
| **R5** absence predictability | **UNTESTABLE-IN-PRE-REGISTERED-DIRECTION** | declared 8,400 rows, cited 8,399 — the never-exercised set is EMPTY (1 row); no negatives to predict | n/a — vacuous, no post-hoc pivot |

## What the run establishes

- **R1 replicates the P1 structure in a Slavic tradition**: citation mass is
  extreme-right-skewed with the Biblical/homiletic canon concentrating over half the mass
  in the top decile of sigla — the A68 coverage structure is not an Indic artefact.
- **R3 is the in-dump demonstration of the partial-apparatus lesson**: two letter-halves
  of the SAME apparatus rank the same sources materially differently (ρ=0.744) — any
  whole-dictionary claim from a partial apparatus is an artefact, the direct analogue of
  the ONP a–em 2.6× lesson, now measured rather than asserted.
- **R4 qualifies P4**: divergence exists but is *family-structured* — the three count
  weightings are near-interchangeable; only citations-per-source-row (density) carries
  independent information. Metric choice matters precisely at the density boundary.
- **R5's vacuousness is itself the finding**: the С–Т dump's `Sources` table is
  (essentially) exactly the exercised universe — 8,399/8,400 rows cited — while 14,087
  examples cite IDs *outside* it. The asymmetry runs OPPOSITE to ONP's
  declared-vs-exercised shape: the "corpus side" here reads as a by-product of the
  excerpting (a slice-generated list), not an independent catalogue. The Stage 4b
  independence-weakening is therefore stronger than assumed — R5-grade claims are
  impossible on this substrate without an independent corpus, and the pre-registered
  direction should not be re-tested on it.

Machine form: [r1_r5_results.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/stage4b_russian/run/r1_r5_results.json)
(adjudications, denominators, falsifier checks, coefficients) · compute script:
[compute_r1_r5.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/stage4b_russian/run/compute_r1_r5.py)
(seed 7523; siglum convention declared in-code) · check:
`python3 check_stage4c.py` → **OK: 41 checks**.

Programme impact: the §9 portability row for the Russian analogue now carries a
**measured internal-consistency result** (R1, R3, R4) — the closest any external
candidate has come to execution in this programme — while remaining a two-letter
unlicensed slice whose corpus side is not independent. Printed alongside §9, never
absorbed.

_Dr. Mārcis Gasūns_
