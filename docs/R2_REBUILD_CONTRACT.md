# R2 Rebuild Contract

Date: 2026-06-05

Status: reconstruction contract for the archived R2 sense-alignment package.
This document does not claim the generator has been restored. It defines the
minimum reproducible package needed before new H1R/H2/H3R claims are broadened
or submitted.

## Trust Block

- Evidence: archived findings in `R2_FINDINGS.md`, static pages
  `/tools/r2-h1` and `/tools/r2-explorer`, and the paper draft
  `PAPER_SENSE_ALIGNMENT.md`.
- Limitations: the old generator files and JSON outputs are not present in this
  branch; static pages preserve results but are not a reproducibility package.
- Validation target: restored scripts must run from current sibling `csl-orig`
  and reproduce the archived headline numbers or explicitly document drift.
- Owner repo: `csl-atlas`.

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

1. Restore or reimplement the entry loader and headword resolver.
2. Aggregate all homonym blocks for the requested lemma before splitting.
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

Start with the five archived anchor lemmas: `gam`, `dharma`, `rama`, `iti`, and
`bodhisattva`. Reproduce the old explorer payload first; then broaden only
after the generator can be rerun from current `csl-orig`.
