# R2 Rebuild Contract

Date: 2026-06-05

Status: reconstruction contract for the archived R2 sense-alignment package.
The archived page payload has been recovered as JSON fixtures, and the five
anchor lemmas now have a source-backed prototype rebuild. The original splitter
has not yet been fully restored. This document defines the minimum reproducible
package needed before new H1R/H2/H3R claims are broadened or submitted.

## Trust Block

- Evidence: archived findings in `R2_FINDINGS.md`, static pages
  `/tools/r2-h1` and `/tools/r2-explorer`, recovered fixtures
  `data/lexico/r2_archive_explorer.json` and
  `data/lexico/r2_archive_h1.json`, source-backed prototype outputs
  `data/lexico/r2_source_anchor_summary.json`,
  `data/lexico/r2_source_anchor_senses.jsonl`, and
  `data/lexico/r2_source_anchor_alignments.json`, parser-drift diagnostics
  in `data/lexico/r2_parser_diagnostics.json`, and the paper draft
  `PAPER_SENSE_ALIGNMENT.md`. Machine label and checkpoint review artifacts are
  `data/lexico/r2_packet_label_proposals.json`,
  `data/lexico/r2_checkpoint_review_packet.json`, and
  `src/data/review/r2-checkpoint-review.json`, with reviewer guides
  `docs/R2_CHECKPOINT_REVIEW.md` and `docs/R2_CHECKPOINT_DECISIONS.md`. The
  current machine-only drift control is
  `data/lexico/r2_drift_explanation.json` with
  `docs/R2_DRIFT_EXPLANATION.md`.
- Limitations: the old generator files and JSON outputs are not present in this
  branch; static pages preserve results, and the source-backed anchor prototype
  is not yet the final reproducibility package.
- Validation: restored scripts must run from current sibling `csl-orig`
  and reproduce the archived headline numbers or explicitly document drift.
- Owner repo: `csl-atlas`.
- Next use: use the machine-only drift explanation as the control handoff for
  checkpoint review. Parser promotion remains deferred until human checkpoint
  decisions exist.

## Recovered Archive Fixtures

`npm run recover-r2-archive` extracts machine-readable fixtures from the two
static R2 pages. These files are source-page recoveries, not regenerated
dictionary analysis.

| Output | Source | Recovered content |
|---|---|---|
| `data/lexico/r2_archive_explorer.json` | `src/tools/r2-explorer.md` | 5 lemmas, 445 sense rows, 104 alignment rows, 46 cross-tradition alignments. |
| `data/lexico/r2_archive_h1.json` | `src/tools/r2-h1.md` | 11 plotted dictionary rows and 7 family means for the H1R static scatter. |

Use these fixtures as tests and comparison targets while rebuilding the real
R2 package from `csl-orig`.

## Source-Backed Anchor Prototype

`npm run build-r2-source-anchors` reads current local `../csl-orig/v02` sources
and emits the next rebuild rung for the five archived anchor lemmas. It resolves
source headword variants, aggregates all matching `<L>` blocks, writes compact
sense rows, and builds provisional Sanskrit-anchor alignments.

| Output | Role | Current content |
|---|---|---|
| `data/lexico/r2_source_anchor_summary.json` | Count and drift summary against archive fixtures. | 5 lemmas, 14 dictionaries, 1,811 source-backed rows versus 445 archived rows, with top source-record counts per lemma/dictionary. |
| `data/lexico/r2_source_anchor_senses.jsonl` | Minimal source-backed sense-row worklist. | One provisional row per split source span, with `<L>` ids, source links, anchors, limitations, explicit-marker labels/run indexes, indigenous authority hints, and AE reverse-match rank metadata where applicable. |
| `data/lexico/r2_source_anchor_alignments.json` | Prototype alignment worklist. | Jaccard-ranked shared Sanskrit/citation anchors, capped to top rows per lemma. |
| `data/lexico/r2_parser_diagnostics.json` | Parser-drift worklist for the next rebuild slice. | 70 lemma/dictionary diagnostics; 17 high-priority rows classify PWG/PWK div splitting, BEN/AP90/BHS marker/source-record scope, AE reverse overmatch, and SKD/VCP `iti` review. |
| `data/lexico/r2_review_packets.json` | Reviewer-facing packet layer over diagnostics. | Five parser-decision packets: div/source-record scope, marker-run scope, AE reverse bands, indigenous `iti` authority review, and source-gap controls. Source-inspected proposal docs now label all five packets. |
| `data/lexico/r2_packet_label_proposals.json` | Machine-readable packet vocabulary and row proposals. | 70 diagnostic proposals and the stable 10-row checkpoint with empty human-decision fields. |
| `data/lexico/r2_checkpoint_review_packet.json` / `docs/R2_CHECKPOINT_REVIEW.md` | Reviewer packet and worksheet for the checkpoint rows. | Ten source-linked checkpoint rows grouped by packet; no human decisions recorded yet. |
| `src/data/review/r2-checkpoint-review.json` / `docs/R2_CHECKPOINT_DECISIONS.md` | Shared review-report overlay for checkpoint decisions. | Ten `r2-checkpoint` review records keyed by `diagnosticId`, with canonical empty human fields and preservation across rebuilds. |
| `data/lexico/r2_drift_explanation.json` / `docs/R2_DRIFT_EXPLANATION.md` | Machine-only drift explanation/control packet. | All 70 diagnostic rows counted by packet, drift class, priority, and proposed label; the 10 checkpoint rows remain `needs-review`. |

The row-count drift is expected. The prototype includes PWK from source, exposes
AE reverse-dictionary overmatching with equivalent-position rank counts, and
splits some PWG/PWK/BEN source markers more finely than the archived static
explorer. Use the drift table in
`r2_source_anchor_summary.json` and the classified worklist in
[`R2_PARSER_DIAGNOSTICS.md`](R2_PARSER_DIAGNOSTICS.md) to decide which parser
family to tighten next.

## Required Outputs

The restored package should emit these files under `data/lexico/` or a clearly
named successor directory:

| Output | Role | Required status |
|---|---|---|
| `senses_<dict>.jsonl` | One sense-unit record per dictionary sense. | **restored** (`npm run build-r2-explorer`) |
| `r2_align_<lemma>.json` | Sense-alignment payload for selected anchor lemmas. | **restored** (`npm run build-r2-explorer`) |
| `r2_summary.json` | Corpus-level parser and coverage summary. | **restored** (`npm run build-r2-explorer`) |
| `r2_h1.json` | Sense-granularity by dictionary/family/year. | **restored** (`npm run build-r2-h1`) |
| `r2_h2h3.json` | Citation-survival and drift results on inheritance edges. | required (deferred — next slice) |
| `r2_h1_panel.json` | Fixed-panel deconfounding check. | recommended (deferred — next slice) |

The public pages may remain static until the data contract stabilizes, but they
must be regenerated from the restored outputs before paper submission.

**Restored (2026-06-09) — Explorer + H1 slice.** `senses_<dict>.jsonl`,
`r2_align_<lemma>.json`, `r2_summary.json`, `r2_h1.json` are now generated from
`csl-orig`. Acceptance gates met: H1R reproduced (Pearson 0.036, archived 0.06;
same conclusion); Explorer reproduced (cross-tradition AP↔SKD/VCP, ap#4~ap90#4
J=1 preserved); Preservation: pages marked archived with live-data pointers;
121 unit tests pass. Documented drift: senseRows 1,811 vs 445 (PWK added,
finer splitting); alignmentRows 128 vs 104 (24-row PWK residual); per-dict
H1 values within ≤13% with family ordering identical. Parser-rule changes are
still deferred to checkpoint review (unchanged).

## Minimal Record Schema

Each sense row should be compact and deterministic:

| Field | Meaning |
|---|---|
| `dict` | Dictionary code. |
| `lemma` | Requested normalized lemma. |
| `rawHeadword` | Source headword or homonym block headword. |
| `blockIds` | Source `<L>` identifiers included in the aggregate. |
| `senseId` | Stable sense identifier within the aggregated lemma. |
| `parserFamily` | `western`, `indigenous`, `reverse`, or `index-excluded`. |
| `splitConfidence` | `explicit`, `lumped-proxy`, `iti-unit`, `reverse-equivalent`, or `excluded`. |
| `text` | Short source span or normalized gloss span. |
| `sanskritAnchors` | SLP1 content tokens excluding the lemma itself. |
| `citationAnchors` | `<ls>` sigla or indigenous authority sigla. |
| `limitations` | Per-row caveats, especially for verbs and indigenous prose. |

## Rebuild Order

0. Recover archived static fixtures with `npm run recover-r2-archive`.
1. Restore or reimplement the entry loader and headword resolver. Prototype
   evidence: `npm run build-r2-source-anchors`.
2. Aggregate all homonym blocks for the requested lemma before splitting.
   Prototype evidence: source rows carry `<L>` block IDs and source links.
3. Rebuild parser families in this order: western explicit, western lumped,
   reverse, indigenous.
4. Rebuild anchor extraction and strong-anchor filtering.
5. Reproduce `/tools/r2-explorer` from `r2_align_<lemma>.json`.
6. Reproduce `/tools/r2-h1` from `r2_h1.json`.
7. Rebuild H2/H3R inheritance-edge reports from `r2_h2h3.json`.

## Current Decision Queue

The generated packet layer in [`R2_REVIEW_PACKETS.md`](R2_REVIEW_PACKETS.md)
is the current implementation queue. All five packets now have
source-inspected proposal layers and a machine-only drift explanation packet.
These labels are machine-proposed parser labels, not scholar-reviewed sense
decisions or `reviewedValue` fields. The current no-human action is
[`R2_DRIFT_EXPLANATION.md`](R2_DRIFT_EXPLANATION.md), which explains all 70
diagnostic rows and marks the checkpoint rows still `needs-review`. The next
human action is checkpoint review, guided by
[`R2_CHECKPOINT_DECISIONS.md`](R2_CHECKPOINT_DECISIONS.md) and
[`R2_CHECKPOINT_REVIEW.md`](R2_CHECKPOINT_REVIEW.md), keeping parser promotion
deferred until human decisions exist.

| Order | Packet | Rows | High priority | Decision before code promotion |
|---:|---|---:|---:|---|
| 1 | `div-source-scope` | 10 | 4 | Decide which PWG/PWK source records and `<div n>` label classes belong to the target sense series. |
| 2 | `marker-run-scope` | 28 | 2 | Decide whether marker-run prefix matches identify main sense runs or only archive-parity clues. |
| 3 | `ae-reverse-bands` | 5 | 3 | Choose rank bands for AE reverse rows before using them as alignment evidence. |
| 4 | `indigenous-iti-authority` | 10 | 8 | Review SKD/VCP `iti` boundaries and authority hints before promoting indigenous rows. |
| 5 | `source-gap-controls` | 17 | 0 | Use parity/source-gap rows as controls after the blocking parser families are handled. |

Proposal layers:

- [`R2_DIV_SOURCE_SCOPE_LABELS.md`](R2_DIV_SOURCE_SCOPE_LABELS.md)
- [`R2_MARKER_RUN_SCOPE_LABELS.md`](R2_MARKER_RUN_SCOPE_LABELS.md)
- [`R2_AE_REVERSE_BAND_LABELS.md`](R2_AE_REVERSE_BAND_LABELS.md)
- [`R2_INDIGENOUS_ITI_AUTHORITY_LABELS.md`](R2_INDIGENOUS_ITI_AUTHORITY_LABELS.md)
- [`R2_SOURCE_GAP_CONTROL_LABELS.md`](R2_SOURCE_GAP_CONTROL_LABELS.md)

## Acceptance Gates

| Gate | Expected evidence |
|---|---|
| H1R reproduced | Year trend remains weak after family/headword-policy controls. |
| H2 reproduced | Cited ancestor senses survive more often than uncited senses. |
| H3R reproduced | Tested descendants copy or condense rather than systematically expand. |
| Explorer reproduced | German, English, Sanskrit, and reverse-index examples align through Sanskrit anchors, not translation. |
| Preservation | Static archived pages are replaced or clearly marked as archived. |
| Boundary | No corpus/DCS frequency, TEI/OntoLex, GitHub metrics, runtime LLM, database, or backend input. |

## Known Risks

- MW and MW72 split many compounds and homonyms into separate entries; per-entry
  averages must not be read as pure sense counts.
- Very common roots such as `gam` over-match in reverse dictionaries.
- Indigenous `iti` segmentation is useful but coarse; it needs review labels.
- Verb entries need parser rules distinct from nominal entries.

## Next Implementation Slice

Use the source-backed anchor prototype and the machine-only drift explanation
packet to prepare for a non-final rebuild experiment against the archived
fixtures. Before testing parser changes, review the checkpoint report generated
by `npm run build-r2-checkpoint-review`. Parser changes can be considered only
after those checkpoint rows have human decisions. The later parser experiment
order remains:

1. Apply `div-source-scope` labels to PWG/PWK source-record and `<div n>`
   boundaries.
2. Apply `marker-run-scope` labels to BEN/AP90/BHS western marker runs.
3. Apply `ae-reverse-bands` labels before accepting AE reverse rows as
   alignment evidence.
4. Apply `indigenous-iti-authority` labels to SKD/VCP `iti` units without
   treating authority quotations as reviewed senses.
5. Use `source-gap-controls` labels as parity, source-only, and no-anchor
   controls while the high-risk parser families change.

The later experiment should rerun `npm run build-r2-drift-explanation` before
any public R2 claim changes. Broaden beyond `gam`, `dharma`, `rama`, `iti`, and
`bodhisattva` only after the generator can explain or reproduce the archived
payloads from source.

The current baseline experiment note is
[`R2_REBUILD_EXPERIMENT.md`](R2_REBUILD_EXPERIMENT.md). It records the stable
rerun baseline, the packet gates, and the promotion rule for the first parser
pass.
