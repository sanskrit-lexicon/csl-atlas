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
  `PAPER_SENSE_ALIGNMENT.md`.
- Limitations: the old generator files and JSON outputs are not present in this
  branch; static pages preserve results, and the source-backed anchor prototype
  is not yet the final reproducibility package.
- Validation target: restored scripts must run from current sibling `csl-orig`
  and reproduce the archived headline numbers or explicitly document drift.
- Owner repo: `csl-atlas`.

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
| `data/lexico/r2_source_anchor_senses.jsonl` | Minimal source-backed sense-row worklist. | One provisional row per split source span, with `<L>` ids, source links, anchors, limitations, explicit-marker labels/run indexes, and AE reverse-match rank metadata where applicable. |
| `data/lexico/r2_source_anchor_alignments.json` | Prototype alignment worklist. | Jaccard-ranked shared Sanskrit/citation anchors, capped to top rows per lemma. |
| `data/lexico/r2_parser_diagnostics.json` | Parser-drift worklist for the next rebuild slice. | 70 lemma/dictionary diagnostics; 17 high-priority rows classify PWG/PWK div splitting, BEN/AP90/BHS marker/source-record scope, AE reverse overmatch, and SKD/VCP `iti` review. |

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
| `senses_<dict>.jsonl` | One sense-unit record per dictionary sense. | required |
| `r2_align_<lemma>.json` | Sense-alignment payload for selected anchor lemmas. | required |
| `r2_summary.json` | Corpus-level parser and coverage summary. | required |
| `r2_h1.json` | Sense-granularity by dictionary/family/year. | required |
| `r2_h2h3.json` | Citation-survival and drift results on inheritance edges. | required |
| `r2_h1_panel.json` | Fixed-panel deconfounding check. | recommended |

The public pages may remain static until the data contract stabilizes, but they
must be regenerated from the restored outputs before paper submission.

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

Use the source-backed anchor prototype to tighten parser-family parity with the
archive fixtures. Run `npm run build-r2-parser-diagnostics` after
`npm run build-r2-source-anchors` and use the high-priority rows to drive the
next parser changes. Current priority order: PWG/PWK `div` marker-label and
source-record scope, BEN/AP90/BHS marker-run prefix filtering/review, AE reverse rank
filtering/review for common roots, then indigenous `iti` review labels. Broaden beyond `gam`, `dharma`, `rama`, `iti`,
and `bodhisattva` only after the generator can explain or reproduce the
archived payloads from source.
