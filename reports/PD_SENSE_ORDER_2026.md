# PD sense order — does a later sense's earliest quotation come later?

_Created: 19-10-2026 · Basis: H7093 full-population run (`data/pd/pd_citation_order_full.tsv`), script [`scripts/pd_sense_order.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_sense_order.py)_

**Question.** H7093 measured the order of *citations inside* a sense division. PD's title makes a
different claim — *on historical principles*, the OED model: the **senses themselves** are ordered
by the chronological development of the meaning. This is a first measurement of that claim on the
machine-readable text.

## Method

For every entry, each sense division contributes **the earliest datable citation filed under it**
(one date per division, under one clock). The sequence of those dates, in sense order, is then
tested: for two-sense entries, the share where the later sense carries the later date; for entries
with three or more senses, Kendall τ between sense position and earliest date, against a
5,000-replicate permutation null (seed `20261019`) that shuffles the sense dates within each entry.

## Result

| Clock | Entries with ≥2 senses | 2-sense: later→later | Entries with ≥3 senses | Mean τ (position, earliest date) | Null 95 % band | Median first→last |
|---|--:|--:|--:|--:|---|--:|
| DCS | 509 | 49.5 % (150 ties) | 590 | **+0.322** | −0.046 … +0.046 | +150 y |
| Dharmamitra | 582 | **60.1 %** | 706 | **+0.323** | −0.041 … +0.040 | **+265 y** |
| AOB imprint | 852 | 50.1 % | 1,009 | +0.134 | −0.032 … +0.032 | +5 y |
| PD/SWC | 344 | 32.0 % (116 ties) | 359 | −0.002 | −0.064 … +0.063 | 0 y |

The work-date clocks put the sense sequence well outside the null band (τ ≈ +0.32 against a band of
±0.05), and the median drift from the first to the last sense is **+265 years** under Dharmamitra.
So PD's senses are chronologically ordered **as a tendency, not as a rule**: about 40 % of two-sense
entries run backwards, and for entries with ≥3 senses the mean τ is positive but far from 1.

The PD/SWC row is not evidence either way: that clock sees only 15 works (the *Subject-Wise Class*
page of PD's front matter), and 116 of its 344 two-sense entries are ties.

## What this does not establish

- **A rising sequence is not proof of editorial chronology.** Senses carry a partly-forced
  canonical order — literal → figurative → technical — that any competent lexicographer shares. The
  estate already measures that floor across dictionaries: MW vs PWG sense-order concordance
  **0.767** against an independent Apte control **0.751**, with a shuffled-sense floor of 0.50
  ([SENSE_ORDER_TEST.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/SENSE_ORDER_TEST.md)).
  Until the same test is run on PWG and MW with dated citations, the +0.32 **cannot be attributed
  to PD's historical principle rather than to the semantic structure of meanings**. That comparative
  run is the refutation condition: if PWG (not an OED-model dictionary) shows the same τ, the
  editorial reading is withdrawn. **It has been run (19-10-2026): PWG τ = +0.41, i.e. higher than
  PD's, so the editorial reading is withdrawn** —
  [PD_SENSE_ORDER_COMPARE_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_SENSE_ORDER_COMPARE_2026.md). Nor can a second dating authority serve as the control: DCS and
  Dharmamitra are one lineage — Hellwig & Nehrdich 2018 (word segmentation, EMNLP) is their only joint
  publication, and there is no joint chronology — so agreement between the two dates is
  cross-validation, not evidence. The dates are only the common measuring stick, and they must be
  identical on both sides so the difference is not a clock artefact.
- The date of a sense is the earliest **quotation filed under it**, not a date the editors recorded;
  a sense can be perfectly defensible and still be illustrated from later texts.
- Only entries with ≥2 datable divisions are decidable (about a quarter of the entries in the
  population); entries with a single well-cited sense are invisible here.
- All clocks are work-level; no edition-level refinement.

## Reproduce

```bash
python scripts/pd_sense_order.py --check   # recomputes the summary from the committed TSV
python scripts/pd_sense_order.py --build   # rewrites data/pd/pd_sense_order_summary.json
```

The output is rounded to 1e-10 and therefore byte-reproducible across platforms.

_Dr. Mārcis Gasūns_
