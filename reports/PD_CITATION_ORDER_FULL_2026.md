# PD citation order on the full letter-*a* population (H7093)

_Created: 19-10-2026 · Executor: DeepSeek v4.1 Flash (`deepseek/deepseek-flash`)_

## Question

PD's Preface claims strict chronological order **within the smallest division**. H6943 sampled 100 entries and found 49 % mixed (exact 95 % CI 38.9–59.2). This report tests the claim on every real `{@n@}` division of the letter-*a* text, adds an imprint clock, and asks whether the observed order is better or worse than random.

## Inputs (hash-pinned)

| Input | SHA-256 | Bytes |
|---|---|--:|
| `pd_txt` (`/tmp/pdtxt/txt/pd.txt`) | `4ee75e6619ee2bd86a331586bb922101e0ae090f9edd981752cfac36ed724442` | 55,122,076 |
| `swc` (`/opt/GitHub-worktrees/csl-atlas/csl-atlas-h7093-drain/test/_h6943_swc.md`) | `b7bde4b84c7b9b13208f0e25db04e0902e7c01cbda4d4b9cf5a9de3506421a13` | 35,002 |
| `dcs_texts_clean` (`/opt/GitHub-worktrees/csl-atlas/csl-atlas-h7093-drain/test/_h6943_dcs_texts_clean.json`) | `cebe99c07084f22dee02905c5edf801ee685e9d10aec05c88ed98265f2dd67d4` | 76,576 |
| `dharmamitra` (`/opt/GitHub-worktrees/csl-atlas/csl-atlas-h7093-drain/src/data/external/dharmamitra-chronology.json`) | `e8ad4988651b179a3e63d8a61928e6f240758c7dfa6d22d81e3b7a4d7df201e5` | 1,195,186 |
| `aob_declared_entries` (`/opt/GitHub-worktrees/csl-atlas/csl-atlas-h7093-drain/data/pd/pd_aob_declared_entries.tsv`) | `323fae0d2c83e8c3edd5974d61e097091367654502b68764ebfa4aac012ed6c9` | 249,781 |
| `pd_siglum_families` (`/opt/GitHub-worktrees/csl-atlas/csl-atlas-h7093-drain/data/pd/pd_siglum_families.tsv`) | `d5d0b32ae2f380cd8a0d38dce7bc1adf88b3c6891a9a6fdf7db3cdd434254871` | 164,737 |

## Population funnel

* `<L>` entries parsed: **107,620**
* entries with at least one real `{@n@}` marker: **12,770**
* real sense divisions (preamble and whole-entry chunks excluded): **36,449**
* divisions with at least two citation sigla: **13,358**
* divisions with at least two citations datable by ≥1 of the three H6943 clocks: **4,148**
* divisions with at least two citations datable by ≥1 of the four clocks (imprint included): **9,689**
* **H6943 reconciliation anchor:** entries with at least two datable citations in their best real division = **2,118** (target 2,118; MATCH).

H6943 picked one division per entry, so its 2,118 is an **entry** count. The full-population unit here is the division; the two counts differ by construction and the entry count is the reconciliation anchor.

## Method

* **Unit.** Smallest numbered sense division; `{@n@}`, `{@1B@}`, `{@ii@}` … are labels. The preamble (`0`) and marker-less whole entries are excluded.
* **Sequence.** Citation sigla in order of appearance; consecutive repeats of the same siglum collapsed.
* **Binary.** `monotone` = non-decreasing **or** non-increasing; `inverted` = at least one direction change. Ascending, descending and mixed are reported separately, because a wholly newest-first division is monotone.
* **Continuous.** Kendall τ-a and the adjacent-pair forward rate per division.
* **Clocks.** PD/SWC (Dice ≥ 0.80), DCS (Dice ≥ 0.90), Dharmamitra (Dice ≥ 0.82, earliest stratum per base title), AOB imprint (earliest declared imprint year per harvested siglum). Clocks are never blended; `any` is the H6943 decision rule, not a clock.
* **Null.** For each of 10,000 pooled permutations, every datable sequence of every division is shuffled uniformly and the mixed indicators are recomputed. The null distribution is the resulting mixed rate per clock and for `any`.
* **CI.** Clopper–Pearson exact intervals at 95 %.

## Results

| Clock / rule | Decidable divisions | Mixed (inverted) | Mixed rate, exact 95 % CI | Asc / desc / mixed | Mean τ | Mean adjacent-forward rate |
|---|--:|--:|---|---|--:|--:|
| PD/SWC | 1,047 | 428 | 40.9 % (37.9–43.9) | 208 / 411 / 428 | -0.253 | 37.8 % |
| DCS | 2,989 | 1,027 | 34.4 % (32.7–36.1) | 1,803 / 159 / 1,027 | 0.610 | 70.3 % |
| Dharmamitra | 3,877 | 1,840 | 47.5 % (45.9–49.0) | 1,587 / 450 / 1,840 | 0.483 | 69.2 % |
| AOB imprint | 9,501 | 5,614 | 59.1 % (58.1–60.1) | 2,052 / 1,835 / 5,614 | 0.027 | 50.2 % |
| Any clock (H6943 rule) | 9,689 | 5,676 | 58.6 % (57.6–59.6) | 2,074 / 1,939 / 5,676 | 0.080 | 52.5 % |

The `any` row is the composite decision rule used by H6943 and is therefore the closest like-for-like continuation of the sample.

## Null model

Observed mixed rate versus 10,000 pooled within-division permutations. `P(null ≥ observed)` is the share of null replicates at or above the observed rate; a small value means the observed order is more chronological than random. `P(null ≤ observed)` is the one-sided test that the observed order is no worse than random.

| Clock / rule | Observed | Null mean | Null 2.5–97.5 % | P(null ≥ observed) | P(null ≤ observed) |
|---|---|---|---|--:|--:|
| PD/SWC | 40.9 % | 36.6 % | 35.1 %–38.1 % | 0.0 % | 1 |
| DCS | 34.4 % | 47.8 % | 47.0 %–48.6 % | 100.0 % | 9.999e-05 |
| Dharmamitra | 47.5 % | 52.9 % | 52.2 %–53.6 % | 100.0 % | 9.999e-05 |
| AOB imprint | 59.1 % | 59.2 % | 58.7 %–59.6 % | 65.6 % | 0.3595 |
| Any clock | 58.6 % | 59.0 % | 58.6 %–59.4 % | 97.4 % | 0.0297 |

## Verdict

* **Strong form (strict ascending in every division):** refuted. Under the `any` rule, 7,615 of 9,689 decidable divisions are not ascending (78.6 %).

The weak form has to be read clock by clock, because the `any` rule is dominated by the imprint clock (9,501 of 9,689 decidable divisions) and the work-date clocks pull in different directions:

| Work-date clock | Mixed vs null | Mean τ | Adjacent-forward rate | Weak chronological tendency? |
|---|---|--:|--:|---|
| PD/SWC | 40.9 % vs 36.6 % | -0.253 | 37.8 % | no |
| DCS | 34.4 % vs 47.8 % | 0.610 | 70.3 % | yes |
| Dharmamitra | 47.5 % vs 52.9 % | 0.483 | 69.2 % | yes |

* **Weak form (a chronological tendency):** survives for the work-date clocks DCS (τ = 0.610) and Dharmamitra (τ = 0.483), both well below the random-order mixed rate. It does **not** survive for PD's own SWC clock (τ = -0.253; mixed rate 40.9 % against a null mean of 36.6 %), which leans descending rather than ascending.
* **Composite caveat.** The H6943 `any` rule gives 58.6 % against a null mean of 59.0 % (P(null ≤ observed) = 0.0297). That marginal difference is carried by the imprint clock, which is structurally unable to speak about work chronology; it must not be read as support for the Preface claim.
* **What does not follow.** A mixed sequence is not by itself an editorial error. The adjudication sheet separates real inversions from date-proxy artefacts, edition mismatch, non-chronological ordering principles and OCR-siglum errors.

## Adjudication

**Status: sheet drawn, human annotation outstanding.** The 200 rows in `data/pd/pd_citation_order_adjudication.tsv` are the seeded adjudication frame. No human annotator has filled it in this run, so no κ and no adjudicated precision are reported, and the verdict above is a verdict about the dating clocks, not yet about editorial practice.

The sheet `data/pd/pd_citation_order_adjudication.tsv` contains 100 flagged (mixed) and 100 monotone controls drawn with a seeded RNG, stratified by deciding clock, DCS genre (or `undetermined`), citation-count bucket and position in *a-*. Annotators fill `annotator_1`, `annotator_2` and `adjudicated_class` with one of: `real inversion`, `date-proxy error`, `edition mismatch`, `non-chronological ordering principle`, `OCR-siglum error`. Cohen's κ is computed on the two independent annotator columns; precision of inversion is `real inversion / all flagged rows` after adjudication.

## Confounds and unknowns

* Citations may be ordered by grammatical construction, text type or relevance, not date.
* Runs of one siglum are collapsed; the raw run count is still a grouping signature, not chronology.
* PD/SWC dates are coarse and OCR-noisy and the clock covers only **15 distinct works** (the *Subject-Wise Class* page of PD's front matter); DCS is structurally sparse (120 of 4,988 primary sigla have a coverage row, 70 works appear here); Dharmamitra is work-level, not edition-level (93 works); imprint years date the editor's copy, not the work (1,459 works). A row of 1,047 decidable divisions is not 1,047 works, and the PD/SWC row must be read as a 15-work Vedic-subject proxy, not as PD's dating apparatus.
* DCS and Dharmamitra are separately published chronologies with one joint publication behind them (56 shared works here, Spearman ρ = 0.94, median offset +3 years). They are not independent instruments, so their agreement is cross-validation within one scholarly lineage, not two independent confirmations.
* The eligible base is itself a selection: divisions with ≥2 datable citations are better-cited and may be atypical. The funnel above reports the eligible/ineligible contrast.
* Missing edition years (325 of 1,437 AOB declared rows), SWC OCR noise, sparse DCS coverage and eligible-base selection are named, not corrected.

## Refutation condition (stated in advance)

* If the adjudicated precision of `inversion` as a claim about editorial practice falls below 50 %, the negative result is withdrawn.
* If the null comparison reverses (observed mixed rate at or above the random-order mean), the weak-form survival is withdrawn.
* If the H6943 entry anchor does not reconcile to 2,118, the parser is wrong and no verdict is valid.

## Reproduce

```bash
curl -L -o pdtxt.zip https://www.sanskrit-lexicon.uni-koeln.de/scans/PDScan/2020/downloads/pdtxt.zip
unzip pdtxt.zip
python scripts/pd_citation_order_full.py --pd-txt txt/pd.txt --build
python scripts/pd_citation_order_full.py --check
```

_Dr. Mārcis Gasūns_
