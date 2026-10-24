# PD citation order within the smallest division — 100-entry sample against three clocks (H6943)

_Created: 18-10-2026 · Executor: DeepSeek v4.1 Flash (`deepseek/deepseek-flash`)_
_Source data: Cologne PDScan `pdtxt.zip` (PD digital edition, read-only) · SWC: [PD/SWC.md](https://github.com/sanskrit-lexicon/PD/blob/main/SWC.md) · DCS dates: [VisualDCS `dcs_texts_clean.json`](https://github.com/gasyoun/VisualDCS/blob/main/visual/dcs_texts_clean.json) · Dharmamitra: [dharmamitra-chronology.json](src/data/external/dharmamitra-chronology.json) · Artifact: [pd_citation_order_sample.tsv](data/pd/pd_citation_order_sample.tsv) · Builder: [pd_citation_order_sample.py](scripts/pd_citation_order_sample.py)_

## Which Dharmamitra dataset was used — and which was not

The handoff named `data/compound-depth/typography-probe-2026-10-17.json` as the
"Dharmamitra-derived data" and asked to confirm it first. **It is not the intended
dataset.** That file is a ByT5 compound-segmentation/typography probe: its rows are
`surface · k2 · markupSegments · status · modelSegments`, with no work title and no
date, so it cannot date a citation. The Dharmamitra chronology actually used is the
committed [`src/data/external/dharmamitra-chronology.json`](src/data/external/dharmamitra-chronology.json)
(1,618 works, `postMedian` years). This confirmation is part of the result, not a
side note.

## Design

* **Population.** All 107,620 `<L>` entries of the PD digital edition (letter `a-`,
  `apacaya` last). 12,770 carry at least one `{@n@}` sense marker. 6,418 have at least
  two citation sigla inside one real sense division (preamble and whole-entry chunks
  excluded). 2,118 of those have at least two citations datable by at least one clock.
* **Sample.** 100 entries drawn with `random.Random(20261018).sample` from the sorted
  2,118, deterministic. Each row records the division label (`{@1@}`, `{@2@}`,
  `{@1B@}`, `{@ii@}` …), the citation sequence, and the dated sequences per clock.
* **Citation extraction.** Longest exact match of a primary PD siglum (5,106-siglum
  harvest, `pd_siglum_families.tsv`) in the division text. Consecutive repeats of the
  same siglum are collapsed.
* **Verdict.** For a dated sequence, `monotone` = non-decreasing **or** non-increasing
  (chronology in either direction); `inverted` = mixed direction (a later-dated work
  followed by an earlier-dated one, and vice versa); `undecidable` = fewer than two
  dated citations in that division.

## Three clocks

| Clock | Operationalisation | Decidable in sample |
|---|---|---|
| **PD/SWC** | Work-date pairs extracted from the OCR of `PD/SWC.md` (Subject-wise Classification, 62 classes), matched to the PD display title with Dice ≥ 0.80; ranges/centuries reduced to a midpoint, BC negative. | 25 / 100 |
| **DCS** | `dcs_texts_clean.json` (144 bound texts) middle dates, joined through the PD siglum's `dcs_title` (Dice ≥ 0.90). | 75 / 100 |
| **Dharmamitra** | `postMedian` of each work, base title before `:`/`—`, earliest stratum (minimum) per base title; Dice ≥ 0.82 to the PD display title. | 93 / 100 |

Only 120 of PD's 4,988 primary sigla have a DCS coverage row, so the DCS clock is
structurally unable to decide most entries; that is a property of the sources, not a
sampling failure.

## Result

**Overall: 49 of 100 sampled divisions (49.0 %) show a mixed citation order under at
least one clock. Exact 95 % Clopper–Pearson CI 38.9–59.2 %.**

| Clock | Decidable | Inverted (mixed) | Rate | 95 % CI | Ascending / descending / mixed |
|---|--:|--:|--:|---|---|
| PD/SWC | 25 | 15 | 60.0 % | 38.7–78.9 % | 5 / 5 / 15 |
| DCS | 75 | 30 | 40.0 % | 28.9–52.0 % | 37 / 8 / 30 |
| Dharmamitra | 93 | 49 | 52.7 % | 42.1–63.1 % | 35 / 9 / 49 |
| Overall (any clock) | 100 | 49 | 49.0 % | 38.9–59.2 % | — |

The descending share is reported separately because a wholly newest-first division
is *monotone* under the stated rule: 5 PD/SWC, 8 DCS and 9 Dharmamitra divisions are
descending, not mixed. If one instead demands ascending order only, the
non-ascending shares are 20/25 (PD/SWC), 38/75 (DCS) and 44/93 (Dharmamitra).

## Reading

The Preface claim (PD 1976, p. VI) that strict chronology is observed in citing the
examples **within the smallest division is not supported by this sample**. At the
coarsest, almost half of the sampled divisions contain at least one citation-order
inversion (49 %, CI 38.9–59.2 %), and all three clocks land in the same 40–60 % band.
The claim is not rescued by choosing a single clock: PD's own SWC chronology is the
most inverted of the three (60 %, CI 38.7–78.9 %), though its decidable base is the
smallest (25 entries) and its OCR-derived dates are the noisiest.

This is a first measurement, not a final refutation. The date proxies are coarse
(century midpoints, edition-level work dates, fuzzy title joins), citation order can
serve relevance or grammar rather than chronology, and the PD/SWC extraction covers
only 25 of 100 sampled divisions. What the sample does establish is that the strong
form of the Preface claim — strict monotone order in the smallest division — cannot
be taken as a working assumption for PD's apparatus.

## Join loss and caveats

* 107,620 entries parsed; 12,770 with sense markers; 6,418 with ≥2 citations in a
  real division; 2,118 with ≥2 datable citations; 100 sampled.
* PD/SWC: OCR lines are two-column; a work name is taken from the text immediately
  before a date on the same line and then confirmed by Dice similarity. Mis-assigned
  dates are possible, especially where two columns interleave. The 62-class table is
  used as a chronology of works, not as 62 single dates.
* DCS: only bound DCS texts have a date; 120 primary PD sigla are covered.
* Dharmamitra: a work split into chapters is represented by its earliest `postMedian`;
  this is deliberate (earliest stratum) and is stated rather than hidden.
* Sense divisions: `{@n@}` markers only; the preamble (`0`) and marker-less whole
  entries are excluded from the test because they are not the smallest division.
* The citation token matcher is exact-siglum; a siglum OCR-garbled in `pd.txt` is
  dropped, never guessed.

## Reproduce

```bash
curl -L -o pdtxt.zip https://www.sanskrit-lexicon.uni-koeln.de/scans/PDScan/2020/downloads/pdtxt.zip
unzip pdtxt.zip
python scripts/pd_citation_order_sample.py --pd-txt txt/pd.txt
```

The committed TSV is the artifact; the script prints the population counters and the
same rate/CI JSON.

_Dr. Mārcis Gasūns_
