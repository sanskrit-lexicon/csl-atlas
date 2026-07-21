# Roadmap — Cross-dictionary macrostructure anatomy (compound law · entry-size chronology · density fingerprint)

_Created: 21-07-2026 · Last updated: 21-07-2026_

Phase-2 of the H1416 letter-anatomy study
([LETTER_ANATOMY_AND_ENTRY_SIZE_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/LETTER_ANATOMY_AND_ENTRY_SIZE_2026.md)).
H1416 established, for **MW only**, that a dictionary's big letters are big because they head
preverb families, and that entry-size "funding-decay" is real in PWG/PWK/GRA but not SKD/VCP.
This roadmap generalises those results across dictionaries and deepens the decay finding into
real publication time. Index + decisions + autonomy contract:
[PLAN_csl-atlas_dictionary-macrostructure-anatomy_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/PLAN_csl-atlas_dictionary-macrostructure-anatomy_2026.md).

**Scope of dictionaries (all waves):** primary completed comparators **MW, AP, PWG, PWK**; the
Sanskrit→Sanskrit encyclopedics **SKD, VCP** reported as an explicit contrast, never pooled with
the completed set. GRA where the dash convention gives ground truth.

**Output shape (all waves):** derived TSV feed(s) + a report (extending or siblinged to the
H1416 report) + an Observable page — the self-contained csl-atlas deliverable shape, exactly as
H1416 shipped. No paper in this span (the write-up path is a separate future step).

---

## Wave A — Cross-dictionary compound/preverb law

**Deliverable:** `data/pd/compound_share_by_letter.tsv` — per (dict × letter): dash-truth
compound % where available (MW, GRA), splitter-estimated compound % for every dict, the
splitter's calibration error measured on MW, and a CI on the sample estimate. Report section +
`/tools/letter-anatomy` page section. **Unblocked by:** the DharmaMitra ByT5 splitter already
wired in csl-atlas (`scripts/lib/dharmamitra_infer.py`, `import-dharmamitra-segmentation.py`).

- **A1** — Extend the H1416 `parse_entries`/headword loader to emit a **stratified per-letter
  sample** of headwords per dict (target ~300/letter, capped at the letter's size).
- **A2** — Run the ByT5 segmentation model over the sample (local HF path, pinned commit), write
  a committed `data/dharmamitra/compound_segmentation_sample.json` (model, revision, date,
  license) — the "import-once" pattern; normal builds never re-call the model.
- **A3** — **Calibrate against MW dash-truth:** on MW's sampled headwords, compare the splitter's
  "is-compound" verdict to the dash-mark ground truth; report precision/recall/F1 per letter and
  overall. This calibration is itself a finding (how trustworthy is the neural splitter for
  headword compound-detection?).
- **A4** — Emit `compound_share_by_letter.tsv` carrying **both** measures: the conservative
  dash-truth % (MW/GRA) and the splitter-estimate % (all dicts) **with the measured MW error bar
  always attached** — so the reader can weigh reliability. Test whether the preverb-family law
  (big letters head preverbs → high compound share) holds cross-dictionary.
- **A5** — Report + page section: cross-dict compound-share-by-letter, dash-vs-splitter
  agreement, and the generalised law statement.

**Unblocks:** the paper-grade "is `a`'s compound-heaviness universal?" claim.

## Wave B — Entry-size chronology (the funding-decay "why")

**Deliverable:** `data/pd/entry_size_by_year.tsv` — per dict, per publication year/volume: mean
entry size + the fitted decay slope on **real calendar time** (not just alphabetical position).
Report section + `/tools/letter-anatomy` time-series chart. **Unblocked by:** PWG's `<pc>` field
encodes volume 1–7 (confirmed), each with a known year (1855…1875) — every PWG entry maps
directly to a publication year, no hand table needed.

- **B1** — Build the PWG entry→volume→year map from `<pc>` (leading digit = volume) + the
  per-volume years in
  [data/dictionary_inventory.csv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/dictionary_inventory.csv)
  notes. Validate: the 7 volume buckets must match the known volume→letter spans.
- **B2** — Regress PWG entry-size on **real year**; express decay as **% per decade**; compare to
  the H1416 alphabetical-position slope (they should agree in sign, now with a time unit).
- **B3** — **Test the editorial-compression counter-explanation:** is the decay a smooth
  funding-fade, or a one-time policy break after the over-detailed vol-1 `a-`? Compare vol-1
  entry sizes to later volumes' treatment of comparable material; report which story the data
  supports (or that it cannot distinguish them).
- **B4** — Best-effort extension to **PWK, SKD, VCP**: source whatever volume/fascicule date
  granularity exists (PWK 1879–1889; SKD 1886 ed.; VCP 1873–1884), map entries to years where
  possible, and **flag reliability explicitly** — these dates are weak/absent versus PWG's clean
  per-volume mapping.

**Unblocks:** separating the *statistical* decay from its *historical cause* — the honest limit
H1416 flagged.

## Wave D — Cross-dictionary density fingerprint

**Deliverable:** `data/pd/density_fingerprint.tsv` — per dict: chars/entry, senses/entry,
block-count/entry (+ per-letter breakdowns). New page `/tools/dictionary-density`. **Reuses:**
the block-counting logic in
[scripts/build-mw-quantitative-depth.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-mw-quantitative-depth.mjs)
(don't rebuild) and the H1416 entry-body parser.

- **D1** — Generalise the H1416 char-count to a **multi-signal density**: chars/entry (have it),
  senses/entry (sense-division markers per dict format), block-count/entry (structural blocks,
  reusing mw-depth logic).
- **D2** — Emit `density_fingerprint.tsv` (dict-level + per-letter) and a **new** page
  `/tools/dictionary-density` — a cross-dictionary "how deep is each dictionary" fingerprint.
- **D3** — Register the new page in `observablehq.config.js` nav + page-title map.

**Unblocks:** a reusable cross-dictionary depth metric that feeds the existing MW-depth / sense-
depth work rather than duplicating it.

---

## Non-goals (explicit)

- **No paper draft** — the write-up toward book Ch.7 / article A68 is a *separate* future step,
  not in this span.
- **No csl-orig edits** — source dictionaries are read-only (fence).
- **No model training / fine-tuning** — the ByT5 splitter is used as-is, import-once.
- **No full-corpus neural split** — stratified per-letter sample only (compute budget).
- **No new dictionaries** — the 8 key1 dicts of H1416 are the universe; the analysis set is
  MW/AP/PWG/PWK (+ SKD/VCP contrast, + GRA for dash-truth).
- **No changes to other repos' pipelines** — kosha/VisualDCS assets are consumed, not edited.

## Sequencing

Wave A → Wave B → Wave D is the recommended order (A exercises the splitter infra and the
sampling loop; B is data-clean and independent; D reuses A/B's parser). Each wave is
independently shippable; a wave that hard-blocks (e.g. ByT5 unavailable for A) falls back per the
autonomy contract and does not block B or D.

_Dr. Mārcis Gasūns_
