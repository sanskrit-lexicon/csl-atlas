# Implementation — Cross-dictionary macrostructure anatomy (wave-ordered build sequence)

_Created: 21-07-2026 · Last updated: 21-07-2026_

File-level, step-ordered build sequence. Each step names the files it touches and its dependency
on prior steps. Sibling of
[ARCHITECTURE](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/ARCHITECTURE_csl-atlas_dictionary-macrostructure-anatomy.md)
and
[PLAN](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/PLAN_csl-atlas_dictionary-macrostructure-anatomy_2026.md).
Work in a fresh worktree off `origin/main` (csl-atlas is guarded); prime the Observable build
cache by copying `src/.observablehq/cache/_npm/` from the main checkout (offline-build trick,
[[csl-atlas-observable-offline-build]] memory).

## Step 0 — Spike (first 30 min, de-risks Wave A)

- **0.1** Confirm the ByT5 segmentation model runs locally: `python scripts/import-dharmamitra-segmentation.py --help` and a 5-headword smoke run via `--source local`. If the model/weights are unavailable offline and cannot be fetched → **Wave A falls back to dash-truth-only** (MW/GRA) per the autonomy contract; log it and proceed to Wave B. Files: read `scripts/import-dharmamitra-segmentation.py`, `scripts/lib/dharmamitra_infer.py`, `docs/DHARMAMITRA_INTEGRATION.md`.
- **0.2** Time a 300-form segmentation run; if throughput implies the full stratified sample won't finish in budget, shrink the per-letter target (300 → 150 → 100) and log the choice.

## Wave A — Cross-dictionary compound law

- **A1** `scripts/lib/dict_sample.py` (**new**) — `stratified_sample(hw_list, per_letter=300, seed_offset=…)` returning a reproducible per-letter sample (no `random` — index-deterministic: take every ⌈n/target⌉-th headword per letter). Depends on: `letter_anatomy.py` `base_letter`. Note: `Math.random`/`random` are banned in the deterministic path — use stride sampling.
- **A2** `scripts/import_compound_segmentation.py` (**new**, thin wrapper over `scripts/lib/dharmamitra_infer.py`) — feed the A1 sample rows `(dict, key1, slp1)`; write `data/dharmamitra/compound_segmentation_sample.json` with `{model, revision, date, license, rows:[{dict,key1,n_segments}]}`. Import-once; commit the JSON. Depends on: A1, Step 0.
- **A3** `scripts/compound_share.py` (**new**) — read the committed JSON; `is_compound = n_segments >= 2`. **Calibrate on MW:** join to MW key2 dash-truth (dash ⇒ compound), compute per-letter + overall precision/recall/F1 of the splitter vs dash-truth. Depends on: A2, `letter_anatomy.py` dash logic.
- **A4** Same script — emit `data/pd/compound_share_by_letter.tsv` (+ `src/data/pd/` mirror): dash_truth_pct (MW/GRA), splitter_pct + Wilson CI per (dict×letter), calib columns on MW rows, trailing MW-calibration summary. Depends on: A3.
- **A5** Edit `reports/LETTER_ANATOMY_AND_ENTRY_SIZE_2026.md` — new §"Cross-dictionary compound law" (dash-vs-splitter table, calibration F1, the generalised law verdict); edit `src/tools/letter-anatomy.md` — a compound-share-by-letter chart faceted by dict, with the calibration caveat. Depends on: A4.

## Wave B — Entry-size chronology

- **B1** `scripts/entry_year_map.py` (**new**) — `PWG_VOLUME_YEARS = {1:1855,2:1858,3:1861,4:1865,5:1868,6:1871,7:1875}`; `pwg_entry_year(pc)` parses the `<pc>` leading digit. Validate: bucket counts per volume are non-empty and total = PWG entry count. Depends on: `letter_anatomy.py` `parse_entries` (extend it to also yield the raw `<pc>` field — small edit to the parser's yield tuple).
- **B2** `scripts/entry_size_chronology.py` (**new**) — for PWG, join entry body-length (tag-stripped, reuse the H1416 measure) to year; regress mean entry-size on year; report chars/decade slope + CI; cross-check sign against the H1416 alphabetical-position slope. Depends on: B1.
- **B3** Same script — compression counter-test: compute vol-1 `a-` mean size vs later-volume entries of comparable letters; state whether decay is smooth vs a one-time vol-1 break, or indistinguishable. Depends on: B2.
- **B4** Same script — best-effort PWK/SKD/VCP: map to years where a source exists, tag `date_quality`; emit `data/pd/entry_size_by_year.tsv` (+ mirror) with the `YEAR_SLOPE` trailing rows carrying `date_quality`. Depends on: B2. Then report §"Entry-size over real time" + a page time-series chart (`entry_size_by_year.tsv`).

## Wave D — Density fingerprint

- **D1** `scripts/density_fingerprint.py` (**new**) — reuse `parse_entries`; add senses/entry (per-dict sense-division marker set — document it) and blocks/entry (port the block definition from `scripts/build-mw-quantitative-depth.mjs`). Depends on: `letter_anatomy.py`.
- **D2** Emit `data/pd/density_fingerprint.tsv` (+ mirror): dict-level chars/senses/blocks per entry + per-letter rows. Depends on: D1.
- **D3** `src/tools/dictionary-density.md` (**new** page) — stat tiles + a per-dict density table + a per-letter small-multiple; load the new TSV via `FileAttachment`. Register in `observablehq.config.js` (nav `pages` under "Dictionary structure" + the page-title map). Depends on: D2.

## Step F — Finalise (every wave that shipped)

- **F1** Run the generator(s); confirm all TSVs + `src/data/pd/` mirrors written.
- **F2** `npm run build` — must be green (retry ≤6, prime `_npm` cache first). Both `/tools/letter-anatomy` and `/tools/dictionary-density` must render with 0 error markers.
- **F3** CHANGELOG `[Unreleased]` entries (csl-atlas batches — do NOT `/cut-release`).
- **F4** Hub sweep (fence-allowed): SanskritLexicography `FINDINGS.md` new § (+ Index entry + bump next-free marker, run `tools/epistemic_integrity_check.py --structural-only` locally — the H1416 gotcha); Uprava `PROJECT_INTERLINKS.md` feed rows; Uprava handoff registry close. Each via its own worktree off origin.
- **F5** Commit → PR → merge (authorized). Remove worktrees same pass.

## Ordering & dependency summary

`0 → A1 → A2 → A3 → A4 → A5`; `B1 → B2 → B3 → B4`; `D1 → D2 → D3`; then `F1..F5`. A/B/D are
independent after Step 0 — a hard block in one (e.g. ByT5 unavailable ⇒ A degrades to dash-truth)
does not stop the others. Parser edits (raw `<pc>` in the yield tuple) land once in
`letter_anatomy.py` at B1 and are backward-compatible with the H1416 callers.

_Dr. Mārcis Gasūns_
