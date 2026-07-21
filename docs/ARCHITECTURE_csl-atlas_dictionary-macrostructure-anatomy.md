# Architecture — Cross-dictionary macrostructure anatomy

_Created: 21-07-2026 · Last updated: 21-07-2026_

Component boundaries, data model, interfaces, and the build-vs-reuse verdict per piece (with the
prior-art evidence). Sibling of
[ROADMAP](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/ROADMAP_csl-atlas_dictionary-macrostructure-anatomy_2026.md)
and
[PLAN](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/PLAN_csl-atlas_dictionary-macrostructure-anatomy_2026.md).

## Component map

```
                 HeadwordLists/now-2026 (key1/key2)   csl-orig v02 (<L>..<LEND>, <pc>, <k1>)
                            │                                   │
                            ▼                                   ▼
   ┌─────────────────────────────────────────────────────────────────────┐
   │  scripts/letter_anatomy.py   (EXISTING — extend, do not fork)        │
   │   parse_entries()  ·  read_hw_list()  ·  base_letter()  ·  UPASARGAS │
   └───────────┬───────────────────────┬───────────────────────┬─────────┘
        Wave A │                 Wave B │                 Wave D │
   ┌───────────▼─────────┐  ┌──────────▼──────────┐  ┌─────────▼──────────┐
   │ sample_headwords.py │  │ entry_year_map.py   │  │ density_build.py   │
   │  stratified sample  │  │ <pc>→vol→year (PWG) │  │ chars+senses+blocks│
   └───────────┬─────────┘  └──────────┬──────────┘  └─────────┬──────────┘
   ┌───────────▼─────────┐             │                       │
   │ ByT5 segmentation   │             │                       │
   │ (import-once, local)│             │                       │
   │  → committed JSON    │             │                       │
   └───────────┬─────────┘             │                       │
   ┌───────────▼─────────┐  ┌──────────▼──────────┐  ┌─────────▼──────────┐
   │ compound_share_by_  │  │ entry_size_by_year  │  │ density_fingerprint│
   │ letter.tsv (+CI+cal)│  │ .tsv                │  │ .tsv               │
   └───────────┬─────────┘  └──────────┬──────────┘  └─────────┬──────────┘
               └───────────────────────┼───────────────────────┘
                                       ▼
             reports/  +  src/tools/letter-anatomy.md (A,B)  +  /tools/dictionary-density (D)
```

## Data model (the three new feeds)

**`data/pd/compound_share_by_letter.tsv`** (Wave A) — one row per (dict × letter):
`dict · letter_slp1 · letter_iast · n_sampled · dash_truth_pct · splitter_pct · splitter_ci_lo ·
splitter_ci_hi · calib_precision · calib_recall` — dash_truth_pct blank where no dash convention;
calib_* filled only for the calibration dict (MW). Trailing rows: per-dict overall + the
MW-calibration summary (precision/recall/F1).

**`data/pd/entry_size_by_year.tsv`** (Wave B) — one row per (dict × year-or-volume):
`dict · volume · year · n_entries · mean_chars · median_chars`, plus trailing `YEAR_SLOPE` rows
per dict: slope in chars/decade + CI + `date_quality ∈ {exact, approx, absent}`.

**`data/pd/density_fingerprint.tsv`** (Wave D) — one row per (dict [× letter]):
`dict · letter_slp1 · n_entries · chars_per_entry · senses_per_entry · blocks_per_entry`, dict-
level summary rows first, per-letter rows below.

All TSVs mirror to `src/data/pd/` (the H1416 pattern, `SRC_OUT` in the generator).

## Interfaces & contracts

- **Splitter contract (Wave A).** The ByT5 model is invoked **once** by an `import-*` step that
  writes a committed `data/dharmamitra/compound_segmentation_sample.json` carrying `{model,
  revision, date, license, rows:[{dict,key1,slp1,segments,n_segments}]}`. Normal `npm run build`
  never re-calls the model — it reads the committed JSON. This is the csl-atlas house pattern
  (`docs/DHARMAMITRA_INTEGRATION.md`). **A headword is "compound" iff n_segments ≥ 2.**
- **Model output is evidence, not truth.** Per the house rule, splitter compound-share is
  labelled an *estimate* and always carries the MW-measured error bar. The dash-truth % (MW/GRA)
  is the only ground-truth column.
- **Year contract (Wave B).** `entry_year_map.py` exposes `pwg_entry_year(pc_field) -> (volume,
  year)` from the `<pc>` leading digit + a hard-coded `PWG_VOLUME_YEARS = {1:1855, 2:1858,
  3:1861, 4:1865, 5:1868, 6:1871, 7:1875}`. For PWK/SKD/VCP a `date_quality` flag records that
  the mapping is approximate or absent.
- **Density contract (Wave D).** `blocks_per_entry` counts structural `<div>`/sense-division
  markers; the exact marker set is per-dict (reuse the mw-depth block definition for MW, adapt
  per format, and record the marker set used per dict in the report).

## Build-vs-reuse verdicts (with prior-art evidence)

| Piece | Verdict | Evidence |
|---|---|---|
| Entry/headword parsing, letter bucketing, upasarga classify | **REUSE** `scripts/letter_anatomy.py` | H1416 shipped it; extend, don't fork |
| Compound splitter | **REUSE** `scripts/lib/dharmamitra_infer.py` + `import-dharmamitra-segmentation.py` | audit: local ByT5 `chronbmm/sanskrit5-multitask`, F1 0.70–0.80; vidyut-cheda unusable (F1 0.22) |
| Block-count / depth logic (Wave D) | **REUSE** `scripts/build-mw-quantitative-depth.mjs` | audit: existing MW block-count machinery |
| PWG volume→year | **BUILD** (small) | audit: `<pc>` encodes volume; no existing map |
| Compound-share-by-letter feed | **BUILD** | genuinely new; not in coverage/cladogram assets |
| Density fingerprint page | **BUILD** `/tools/dictionary-density` | new surface; MW-depth is MW-only |
| GRA dash-truth | **REUSE** H1416 dash logic | GRA has 36.6% dashed key2 |

## Non-obvious constraints

- **PWG file order is only ~0.76 alphabetical** (H1416 Spearman) — but volume→year is exact
  regardless, so the Wave B year-regression is unaffected by the ordering noise. The
  *within-letter* robust decay test (H1416) is the position-based twin; Wave B adds the
  time-based one.
- **SKD/VCP are heavy-tailed** (single articles >300k chars) — density means must report median
  alongside mean, and any regression must use the H1416 outlier-robust per-letter estimator, not
  a parametric mean model.
- **Sample stratification** must cap at the letter's own size (small letters like `x`/`E` have
  <300 headwords) and record `n_sampled` for the CI.

_Dr. Mārcis Gasūns_
