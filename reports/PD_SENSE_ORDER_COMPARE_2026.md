# PD sense-order against four non-historical dictionaries — 2026-10-19

_Handoff [H7116] · script `scripts/pd_sense_order_compare.py` · summary `data/pd/pd_sense_order_compare_summary.json`_

**Verdict (DM clock, pre-registered rule): WITHDRAWN — the claim that PD's chronological sense ordering is distinctive is withdrawn: PWG, MW fail(s) the pre-registered floor (worst Δτ = -0.082, Holm p = 1.0000 against a floor of +0.10); the tendency is shared with non-historical dictionaries and the A68 footnote must say so.**

## What was measured

The object is the order of **senses** inside an entry, not the order of citations inside a sense (that is `PD_CITATION_ORDER_FULL_2026.md`, H7093). Each sense division contributes the earliest datable citation filed under it; the sequence of those dates in sense order is then tested for a rising tendency. Both sides use the same statistic, imported from `scripts/pd_sense_order.py`, and the same two date instruments H7093 joined: DCS (Dice ≥ 0.90) and Dharmamitra (Dice ≥ 0.82, earliest stratum of a base title). Thresholds are fixed in the script and never relaxed per dictionary.

## PD side — own-data canary

Recomputed from `data/pd/pd_citation_order_full.tsv` before any control was read. Every count and both τ values reproduce `data/pd/pd_sense_order_summary.json` exactly, so the control columns below are comparable to the published PD figure rather than to a re-implementation.

| clock | entries ≥3 senses | τ | null 2.5–97.5 % | median first→last | two-sense forward rate |
|---|---|---|---|---|---|
| dcs | 590 | +0.322 | -0.046 … +0.046 | 150 y | 0.495 (252/509) |
| dm | 706 | +0.323 | -0.041 … +0.040 | 265 y | 0.601 (350/582) |

## Control side — per dictionary, per clock

| dict | clock | records | sense divisions w/ citations | `<ls>` resolved | dated citations | entries w/ series | two-sense forward rate (exact 95 % CI) | entries ≥3 | τ | null band | median drift |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PWG | dcs | 123,366 | 140,435 | 483,000/720,203 (67.1%) | 162,766 | 42,964 | 0.483 (0.470–0.496) | 3,104 | 0.395 | -0.020 … 0.022 | 150 y |
| PWG | dm | 123,366 | 140,435 | 483,000/720,203 (67.1%) | 196,843 | 46,966 | 0.548 (0.535–0.560) | 3,343 | 0.406 | -0.020 … 0.020 | 184 y |
| PW | dcs | 170,556 | 75,604 | 50,337/97,781 (51.5%) | 10,364 | 8,913 | 0.246 (0.195–0.303) | 142 | 0.089 | -0.094 … 0.096 | 0 y |
| PW | dm | 170,556 | 75,604 | 50,337/97,781 (51.5%) | 23,006 | 18,960 | 0.373 (0.341–0.406) | 281 | -0.041 | -0.064 … 0.066 | 0 y |
| MW | dcs | 286,525 | 236,519 | 310,664/320,828 (96.8%) | 108,551 | 72,942 | 0.440 (0.424–0.456) | 3,156 | 0.256 | -0.021 … 0.021 | 0 y |
| MW | dm | 286,525 | 236,519 | 310,664/320,828 (96.8%) | 130,992 | 86,441 | 0.497 (0.482–0.512) | 3,882 | 0.227 | -0.018 … 0.018 | 10 y |
| AP | dcs | 90,851 | 41,547 | 55,766/66,809 (83.5%) | 21,193 | 14,262 | 0.305 (0.282–0.328) | 1,004 | -0.147 | -0.040 … 0.038 | 0 y |
| AP | dm | 90,851 | 41,547 | 55,766/66,809 (83.5%) | 31,823 | 17,162 | 0.369 (0.348–0.390) | 1,622 | -0.042 | -0.029 … 0.029 | 0 y |

## The pre-registered comparison (DM clock, primary)

Effect floor Δτ ≥ +0.10; family α = 0.05 with Holm across the scored dictionaries; a dictionary is scored at ≥30 entries with ≥3 datable senses.

| dict | entries ≥3 | τ_dict | Δτ = τ_PD − τ_dict | bootstrap 95 % CI | one-sided p | Holm p | floor | α |
|---|---|---|---|---|---|---|---|---|
| PWG | 3,343 | 0.406 | -0.082 | -0.125 … -0.040 | 1.0000 | 1.0000 | no | no |
| PW | 281 | -0.041 | +0.364 | 0.290 … 0.440 | 0.0002 | 0.0008 | yes | yes |
| MW | 3,882 | 0.227 | +0.096 | 0.054 … 0.138 | 0.0002 | 0.0008 | no | yes |
| AP | 1,622 | -0.042 | +0.365 | 0.316 … 0.414 | 0.0002 | 0.0008 | yes | yes |


**How the verdict is reached.** The decisive row is **PWG**: τ = 0.406 against PD's 0.323 — PD is *below* a dictionary without the OED's historical remit, and the bootstrap CI on Δτ (-0.125 … -0.040) excludes zero. MW is the second failure and the closer call: Δτ = +0.096, 0.004 below the floor, so it would not decide the verdict alone. PW and AP clear the floor comfortably — they show no chronological order at all. The `dcs` replication clock gives the same ordering (PWG 0.395, MW 0.256, PW +0.089, AP -0.147).

### What this changes in the A68 footnote (`[^chronology]`)

The footnote's closing sentence says the partly-forced order is one "that no comparative test has yet separated". That test now exists, so the sentence is replaced by:

> A rising sense sequence is not by itself editorial chronology — senses carry a partly-forced order (literal → figurative → technical) — and the comparative test now separates it: run on PWG, PW, MW and AP with the same statistic and the same date joins (19-10-2026), PD's τ = +0.32 is **not** distinctive. PWG, a dictionary without the OED's historical remit, orders its senses at least as chronologically (τ = +0.41, Δτ = −0.08 against PD, one-sided permutation P = 1.00), and MW sits at +0.23, short of the pre-registered +0.10 floor by 0.004. On this evidence the *historical principles* reading of PD's sense order is withdrawn; the tendency is shared with non-historical dictionaries ([comparison report](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_SENSE_ORDER_COMPARE_2026.md)). This paper uses the citations as canon evidence, not as a chronology, and no number here depends on the order being monotone.


### Robustness — τ by entry size (primary clock)

PWG root entries can carry 100+ Bedeutungen; this split keeps them from carrying the result alone. A size band with no entries is reported as such, never omitted.

| dict | 3–7 senses: entries | τ | ≥8 senses: entries | τ |
|---|---|---|---|---|
| PWG | 3,037 | 0.421 | 306 | 0.258 |
| PW | 216 | -0.057 | 65 | 0.013 |
| MW | 3,442 | 0.227 | 440 | 0.227 |
| AP | 1,525 | -0.042 | 97 | -0.046 |
| PD | 625 | 0.333 | 81 | 0.247 |

τ_PD on the primary clock: +0.323 (n = 706 entries).

## Pre-registered rule (verbatim from the script's header)

1. Primary clock **dm** (the clock the A68 footnote quotes); `dcs` replicates.
2. A dictionary is scored at ≥30 entries with ≥3 datable senses.
3. Δτ = τ_PD − τ_dictionary, one-sided permutation p (5,000 relabellings, H0: PD is not higher), bootstrap 95 % CI, Holm across the scored family at α = 0.05.
4. **STAND** iff every scored dictionary shows Δτ ≥ +0.10 and Holm p ≤ 0.05.
5. **WITHDRAWN** if any scored dictionary fails either condition — then the A68 footnote says the tendency is shared with non-historical dictionaries and the 'historical principles' name is not evidenced by sense order.
6. **INCONCLUSIVE**, footnote unchanged, if fewer than two dictionaries are scored.

## Limits that travel with these numbers

* **Unit is the quotation, not the editor's date.** A sense's date is its earliest quoted passage; a sense can be historically early and filed under a late quotation.
* **Undated senses are skipped, not imputed.** An entry contributes a series only if it has two or more senses that resolve to a dated work, so coverage is a fraction of the dictionary and the denominators above are the honest population.
* **Resolution ceiling is the binding constraint.** Non-historical dictionaries cite lexicographers, grammarians and medieval compendia that the DCS/Dharmamitra chronologies do not date; the per-dictionary `<ls>`-resolved and dated-citation columns say how much of each dictionary this instrument can actually see.
* **Sense unit is the numbered meaning.** PD's unit is its numbered `{@n@}` division; the control's unit is therefore the numbered Bedeutung (`— 12〉` in PWG/PW, the numbered sub-record in MW, the weapon-point bullet in AP). A lettered sub-sense (`a〉`, `— β〉`) folds into its parent, so its quotations still count towards the parent's earliest date — the same nesting PD's division rows have. On PWG the fold *raises* τ (0.372 → 0.406 on dm), i.e. the verdict does not rest on the split.
* **Homonyms are merged per headword family** (one entry = headword + homonym tag), matching f10's grouping; a split-homonym convention would change sequence lengths, not the direction.
* **MW segmentation** follows f10: numbered sub-records are senses, and a root record's `<div n="to">` glosses are additional senses; MW's plain numbered senses inside one record are not split, so MW's series are more conservative (longer, fewer entries) than PWG's.
* **DCS and Dharmamitra are one lineage, not two instruments** (ρ = 0.94 on 56 shared works), so the two clocks replicate a chronology; they do not double the evidence.
* **The forced canonical order** (literal → figurative → technical) is shared by every dictionary and is exactly what the control measures; it is reported, never corrected away.

## Reproduction

```sh
python scripts/pd_sense_order_compare.py --build   # writes the JSON + this report
python scripts/pd_sense_order_compare.py --check   # recomputes and compares (slow: nulls)
python -m pytest tests/forensic/test_pd_sense_order_compare.py -q   # pinned rows, seconds
```

Inputs are read-only: `../csl-orig/v02/{pwg,pw,mw,ap}`, `../csl-guides/src/data/abbreviations.json`, `data/citations/mw-source-abbreviations.tsv`, `test/_h6943_dcs_texts_clean.json`, `src/data/external/dharmamitra-chronology.json`.

_Handoff H7116 · Dr. Mārcis Gasūns_
