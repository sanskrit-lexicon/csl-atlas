# XREF_SHARED_CORE_LABEL_TAXONOMY.md — metadoc

_Created: 25-07-2026 · Last updated: 26-07-2026_

Companion record for
[`docs/XREF_SHARED_CORE_LABEL_TAXONOMY.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/XREF_SHARED_CORE_LABEL_TAXONOMY.md).

## Purpose

Give a human reviewer the decision rule for the MW/PWG shared-core review sheet: what
each label in the closed vocabulary asserts, what it explicitly does not assert, two
worked examples per label, and how the 40 sampled edges were selected — including the
selection bias.

## Languages

Kept in two files: [`XREF_SHARED_CORE_LABEL_TAXONOMY.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/XREF_SHARED_CORE_LABEL_TAXONOMY.md)
(English, repo-facing record) and [`.ru.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/XREF_SHARED_CORE_LABEL_TAXONOMY.ru.md)
(Russian, reviewer-facing). Prose may differ in wording; **every figure in both is pinned to
the committed data** by [`test/xref-taxonomy-docs.test.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/test/xref-taxonomy-docs.test.mjs),
which also fails if either file re-asserts the retracted independence justification, or if
the Russian file stops being Russian. Numeric drift between them is therefore a CI failure,
not something a reader has to notice.

## Audience

Whoever votes the 40-edge sheet (currently MG), and any later session adjudicating,
re-sampling, or extending the xref shared-core review. Not a public-site document.

## Provenance

- Handoffs: [H1646](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1646-Opus_csl-atlas_xref-sheet-reviewability-40edges_25.07.26.md)
  (created), [H1648](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1648-Opus_csl-atlas_xref-sheet-ru-and-mw-pwg-dependence_26.07.26.md)
  (independence correction, Patel grounding, Russian sheet)
- Model: Opus 5 (1M context) (`claude-opus-5[1m]`)
- Trigger: reviewer feedback in `Uprava/review/40edges.md` — eight numbered objections to
  the sheet, of which four were structural (no Cologne links, unreadable raw markup,
  undefined labels, undisclosed sampling).
- Source of truth for the content: `packetLabelVocabulary` and `selectionPolicy` in
  [`data/lexico/xref_source_check_packet.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/xref_source_check_packet.json).
  This document is the prose companion; if the two disagree, the packet wins and this
  file is stale.

## Limitations

- The worked examples are hand-picked from the current 40-row sample. Re-sampling
  (see backlog) invalidates the `mw-pwg-shared:NN` ids quoted in the tables.
- `normalization-risk` examples are *candidates* argued from string shape, not
  adjudicated cases — no human has yet voted them.
- The document describes the shared-core sheet only. The sibling H4, tradition and
  SKD-iti sheets have their own vocabularies and no equivalent prose companion.
- Cologne link behaviour (headword lookup, homonym fan-out) is stated but not
  exhaustively tested per row; two dictionaries were live-verified, not forty edges.

## Improvement backlog (ranked)

1. **Normalise per Patel 2016 before intersecting, then re-sample.** Two defects
   compound here: the alphabetical-head bias, and the four documented MW↔PWG headword
   convention divergences the pipeline does not reconcile (śatṛ, vatup/matup, ṛ-stems,
   vas/yas). The second means the 642-edge intersection is an *undercount* — a ṛ-stem
   edge cannot intersect at all — so a Patel-normalised re-run should be done before,
   or together with, a random/stratified draw.
2. **Adjudicate the `normalization-risk` candidates** (`:15`/`:30`, `:21`, and the other
   reciprocal length pairs) so the examples become decided cases rather than arguments.
3. **Backfill the 4 single-dictionary rows** — check whether the missing MW edge is
   genuinely absent or lost in `xref_edges.csv` parsing; if the latter, it is a parser
   bug, not a `too-sparse` row.
4. Extend the prose-companion pattern to the H4 / tradition / SKD-iti vocabularies if
   those sheets ever return to a human vote.
5. Fold the `<pe>`, `<srs>`, `<i>` CDSL tags into the anatomy palette
   (`scripts/lib/cdsl_anatomy.py`) — currently rendered as dim structural markup.

## Revision history

| Date | Change | Handoff |
|---|---|---|
| 25-07-2026 | Created alongside the sheet rebuild (Cologne links, entry anatomy, label definitions, sampling disclosure). | [H1646](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1646-Opus_csl-atlas_xref-sheet-reviewability-40edges_25.07.26.md) |
| 26-07-2026 | Added the Russian companion `.ru.md` + a docs-vs-data drift guard (5 tests). The guard immediately caught a real error: the candidate pool was quoted everywhere as **642** but is **641** — a `wc -l` counting the CSV header as data. The packet now computes it instead of carrying a literal. Also fixed a leftover "two independent editors recorded the same by-form link" line that had survived the retraction. | [H1648](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1648-Opus_csl-atlas_xref-sheet-ru-and-mw-pwg-dependence_26.07.26.md) |
| 26-07-2026 | **Retracted the "two independent witnesses" justification** after MG's ruling that MW depends on PW/PWG; added the measured non-independence (21.8% vs 0.007%, ≈2953×, p&nbsp;<&nbsp;0.005), grounded `normalization-risk` in the four documented MW↔PWG convention divergences from Patel 2016 (incl. that the 642-edge intersection is an undercount), and recorded that the sheet is now fully Russian. | [H1648](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1648-Opus_csl-atlas_xref-sheet-ru-and-mw-pwg-dependence_26.07.26.md) |

_Dr. Mārcis Gasūns_
