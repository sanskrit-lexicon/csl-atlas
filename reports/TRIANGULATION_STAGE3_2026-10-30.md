_Created: 30-10-2026 · Last updated: 30-10-2026_

# PD/PWG/NWS Stage 3: the triangulation, and what apparatus-type asymmetry decides

**Protocol:** `research/notes/final_report_pwg-nws-pd-dcs-8294e5.md` §8/§12/§13
(hyperresearch run, committed before Stage 1).
**Pre-registered grid:** [data/triangulation_stage3/grid_preregistration.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/triangulation_stage3/grid_preregistration.md)
— committed at `b531f96` **before** this run, sha-pinned, not retuned.
**Regeneration:** `python3 scripts/triangulation_stage3_check.py` → exit 0.
**Substrates:** [Stage 1 PWG↔DCS](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PWG_DCS_JOIN_STAGE1_2026-10-30.md) (H7463) ·
[Stage 2 NWS layer](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/NWS_LAYER_STAGE2_2026-10-30.md) (H7476) ·
PD metrics (data/pd/pd_dcs_metrics.json, H1336 lineage).

## TL;DR

The triangulation is decided. Five of six pre-registered branches fired, and
the one that did not fire is itself a finding: **BR1 (contradiction)** —
coverage(PWG_Ω) = 63.53 % stands 32.01 pp above PD's band top (31.52), with
the entire 95 % work-bootstrap interval (46.62–76.08) outside it — so
**"three-quarters of citation practice outside DCS" is overturned as an
apparatus-class claim and localizes to PD's late-20th-century breadth-heavy
programme**. **BR2** — on the shared letter-a frontier two *primary-text*
apparatuses differ by 38.43 pp, more than three times PD's own band width:
coverage **level** is programme-relative within the type, so programme, not
apparatus type, is the explanatory axis. **BR3 (scope artefact) does not
fire** — PWG_α and PWG_Ω sit 0.06 pp apart, so letter-a anchoring is
level-safe in a completed dictionary: PD's low number is its programme, not
its alphabet slice. **BR4** — NWS holds PWG's inventory (82.57 % key1
containment) but not its attestation allocation (ρ = 0.3414; letter
envelope ρ = 0.9782): the secondary/primary type line carries real
information — divergence along type lines measures the transfer artefact,
and NWS corroborates nothing at coverage level. **BR5** — letter-volatility
replicates across both primary-text apparatuses (32.19 pp vs PD's 19.99 pp
fascicle span): the dispersion structure is corpus-side, letter pooling
banned for the class. **BR6** — within the 118-text DCS anchor, PWG
independently cites 93.98 % of token mass against PD's 77.88 % whole-corpus
share: the corpus-side concentration converges across programmes.

## 1. Inputs (all committed before Stage 3)

| Apparatus (type) | Quantity | Value | Source |
|---|---|---|---|
| PD (primary, partial letter-a) | coverage(PD_α) | 25.16 % (88,929/353,512) | pd_dcs_metrics.json |
| PD | work-bootstrap band | 19.15–31.52 % (width 12.37 pp) | Stage-1 grid input |
| PD | token-weighted 2026/2021 | 77.88 %/74.06 % | pd_dcs_metrics.json |
| PWG (primary, complete) | coverage(PWG_Ω) stratum-excluded | 63.53 % (400,054/629,718) | pwg_dcs rows |
| PWG | coverage(PWG_α) stratum-excluded | 63.59 % (73,380/115,390) | pwg_dcs rows |
| PWG | 95 % bootstrap (B=2000) | 46.62–76.08 % | Stage-1 G5 |
| PWG | per-letter dispersion | 32.19 pp | Stage-1 H2 |
| PWG | cited share of 118-text anchor | 93.98 % | Stage-1 token view |
| NWS (secondary meta) | headword ρ vs PWG | 0.3414 (divergent) | Stage-2 H5 |
| NWS | letter-aggregate ρ | 0.9782 | Stage-2 |
| NWS | key1 containment in PWG | 82.57 % (28,158 shared) | Stage-2 |
| NWS | declared-vs-exercised | 82/174 = 47.13 % | Stage-2 H6 |
| NWS | purely MW-mediated entries | 3,356 (9.84 %) | Stage-2 tracer |

Row-level anchors regenerate from
[data/pwg_dcs/pwg_dcs_works_joined.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pwg_dcs/pwg_dcs_works_joined.tsv)
and
[data/nws_layer/nws_works_attestation.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/nws_layer/nws_works_attestation.tsv)
inside the gate.

## 2. Branch verdicts (pre-registered conditions, evaluated)

| Branch | Condition | Measured | Fired |
|---|---|---|---|
| BR1 contradiction localisation | Ω > 31.52 ∧ bootstrap p2.5 > 31.52 | 63.53; 46.62 (margin +32.01; interval non-overlap +15.10) | **yes** |
| BR2 within-type programme gap | \|PWG_α − PD_α\| > 12.37 pp | 38.43 pp | **yes** |
| BR3 scope artefact | \|PWG_α − PWG_Ω\| > 12.37 pp | 0.06 pp | **no** |
| BR4 type-line reality | containment ≥ 80 % ∧ ρ < 0.40 | 82.57 %; 0.3414 | **yes** |
| BR5 dispersion convergence | PWG dispersion > PD fascicle span | 32.19 > 19.99 pp | **yes** |
| BR6 token-level convergence | PWG anchor share ≥ PD 2026 ∧ both > 50 % | 93.98 ≥ 77.88 | **yes** |

## 3. The triangulated reading

**Where the three apparatuses diverge along type lines (BR4), the divergence
itself measures the editorial artefact.** NWS's 82.57 % inventory containment
with ρ = 0.3414 allocation divergence is the transfer-vs-excerption artefact
made visible: a secondary meta-apparatus reproduces *what* its parent
inventory holds but not *where* primary mass sits. NWS therefore cannot test
coverage structure (as pre-registered), and its evidence value stays in its
three delimited roles — H6's 82/174 corroborates the declared-vs-exercised
distinction A68's declared-canon 8.0 % rests on, and its ~40 primary-edition
registry rows keep marking the DCS-thin zone.

**Where the two primary-text apparatuses contradict (BR1), the finding
localizes to one programme.** The residue claim dies as a class fact: PD's
residue share is 74.84 % of its primary mass; PWG's stratum-excluded residue
is 36.47 % — a 2.05× ratio on comparable citation masses. The A68 headline
"25.2 %" is now triangulated as a property of PD's reading programme, with
the class-level statement inverted: a completed 1855–1875 edition-anchored
apparatus points **into** DCS at 63.53 %.

**What survives as corpus-structural (BR5, BR6).** Letter-volatility exceeds
PD's own fascicle dispersion in both primary-text apparatuses — the
dispersion structure is shared, corpus-side; and within the 118-text anchor
both programmes concentrate on the same core (PD 77.88 % of whole-corpus
tokens; PWG 93.98 % of anchor tokens, construction note in the metrics).
Depth differs by programme; the existence of a concentrated shared core does
not.

**BR3's non-firing is the design's sharpest aside:** the alphabetical-scope
artefact, pre-registered as divergence (b), is **refuted at the level
dimension** — PWG_α ≈ PWG_Ω to 0.06 pp. Letter-a anchoring did not distort
A68's *level*; PD's programme did. (Letter-level pooling stays banned — H2.)

## 4. §12-row verdicts

| A68 conclusion | Stage-3 verdict |
|---|---|
| Citation-weighted 25.16 % | **localized to PD's programme** (BR1+BR2) |
| "Three-quarters outside DCS" | **overturned as class claim; apparatus-specific to PD** (BR1) |
| Residue four-cluster structure | not triangulable at row level here (no genre rows for PWG residue; Stage-1 qualitative remark stands) |
| Declared-canon 8.0 % | declared-vs-exercised distinction corroborated by NWS H6 (82/174); PWG 527/2,665 analogue not row-committed |
| Token-weighted 77.88 %/74.06 % | **corroborated within the anchored core** (BR6) |
| Density multiple 8.55× | already corroborated and bounded (Stage 1); not re-measured |
| Chronological order | open — H4 not executed in Stages 1–2; no Stage-3 claim |
| "Deep, not broad" | **survives for PD; dies as a class claim** (BR1+BR2) |

Unconditional (§12): the kośa reframing stands regardless; no Stage-3 result
upgrades genre-level certification into task adequacy. Kill-exits respected:
the stage-3 contradiction fired and localizes the headline to PD's
programme; the H5 confirmation that would have reduced NWS to transfer noise
did not fire; the NWS↔DCS inventory join stays pre-registered out; the H5
upgrade stays H5940-gated.

## 5. What this does to the programme

Stage 3 closes the within-Sanskrit triangulation: the apparatus-type
asymmetry did the diagnostic work §13 assigned it, and every verdict above
was fixed by the grid before the run. The A68 revision this licenses
(follow-up to H7462/H7475): scope the coverage headline to PD's programme,
keep the measured numbers and bands untouched, carry the corpus-structural
dispersion finding and the doubly-attested anchored core forward, and drop
any sentence generalising PD's coverage level to historical-dictionary
apparatuses as a class. Stage 4 (external portability) remains gated as §9
states — ONP↔Menota behind its permission gate, CAD on ISAC's release.

Reversal triggers carried unchanged (§8/§12): a committed PWG↔DCS artefact
predating the protocol; a PWG supplementary-fascicle reprint shrinking the
declared/exercised gap; the H5940 gate opening (quantified Halle remainder →
the NWS upgrade conditional becomes testable); a print check showing PD's
marking-share fall is a conversion artefact.

## 6. Artefacts

| File | What it is |
|---|---|
| [`data/triangulation_stage3/grid_preregistration.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/triangulation_stage3/grid_preregistration.md) | the pre-registered grid (sha-pinned, machine-read) |
| [`scripts/triangulation_stage3_join.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/triangulation_stage3_join.py) | the triangulation (deterministic, read-only over inputs) |
| [`scripts/triangulation_stage3_check.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/triangulation_stage3_check.py) | regeneration gate (exit non-zero on drift) |
| [`data/triangulation_stage3/triangulation_metrics.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/triangulation_stage3/triangulation_metrics.json) | every published Stage-3 number |
| [`tests/forensic/test_triangulation_stage3.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_triangulation_stage3.py) | forensic pins (grid sha + values) |

_Dr. Mārcis Gasūns_
