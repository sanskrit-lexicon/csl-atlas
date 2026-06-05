# R2 Parser Diagnostics

Date: 2026-06-05

Status: machine-generated rebuild worklist for the source-backed R2 anchor
prototype. This is not the final sense corpus and not a scholar-reviewed sense
alignment result.

## Trust Block

- Evidence: `data/lexico/r2_parser_diagnostics.json`,
  `data/lexico/r2_source_anchor_summary.json`,
  `data/lexico/r2_source_anchor_senses.jsonl`, and recovered archive fixtures
  from `data/lexico/r2_archive_explorer.json`.
- Limitations: row-count drift is a parser signal, not proof that a dictionary
  added, lost, or merged meanings.
- Validation: `npm run build-r2-source-anchors`,
  `npm run build-r2-parser-diagnostics`, `npm test`.
- Owner repo: `csl-atlas`.

## What The Artifact Does

`npm run build-r2-parser-diagnostics` compares the five source-backed R2
anchor lemmas against the recovered static R2 explorer counts and classifies
each lemma/dictionary pair into a parser work package.

Current artifact:

| Measure | Count |
|---|---:|
| Anchor lemmas | 5 |
| Dictionaries | 14 |
| Diagnostic rows | 70 |
| High-priority rows | 17 |
| Medium-priority rows | 7 |

## Drift Classes

| Drift class | Rows | Meaning | Next action |
|---|---:|---|---|
| `archive-parity` | 28 | Source-backed rows are close to the archived static count. | Use as positive parser controls. |
| `no-anchor-evidence` | 12 | Neither source-backed nor archived row exists for that pair. | Ignore until coverage broadens. |
| `indigenous-coarse-review` | 8 | SKD/VCP `iti` units are source-backed but too coarse for sense claims. | Review boundaries and authority quotations. |
| `over-split-candidate` | 6 | Explicit-marker parser emits far more rows than the archive. | Tighten PWG/PWK `div` and BEN/AP90/BHS number-marker scope. |
| `source-only-dictionary` | 6 | Source-backed rows exist where no archived baseline exists. | Treat as rebuild expansion, not drift. |
| `mild-drift` | 5 | Visible but lower-priority count drift. | Inspect after high-priority parser families. |
| `reverse-overmatch` | 3 | AE reverse lookup overmatches common Sanskrit equivalents. | Add equivalent-position and exactness ranking. |
| `under-split-or-source-gap` | 2 | Source rows fall below the archived static count. | Check lookup variants, source availability, and homonym aggregation. |

## Highest-Priority Parser Work

The top worklist points to four concrete parser tasks:

1. **PWG/PWK top-level division scope.** `gam`, `dharma`, `rama`, and `iti`
   show that the current `<div>` splitter is counting nested divisions as
   sense rows.
2. **BEN numbered-marker scope.** `gam` and `rama` show number-marker inflation
   and should be checked before BEN is used in H1R/H2/H3R row counts.
3. **AE reverse ranking.** `gam`, `dharma`, and `iti` need equivalent-position
   and exactness ranking before reverse rows are treated as alignment evidence.
4. **Indigenous `iti` review.** SKD/VCP rows remain useful, but the artifact
   labels them as review prompts rather than sense decisions.

## Boundary

This diagnostic layer is dictionary evidence only. It does not import DCS,
corpus frequency, TEI/OntoLex, FrAC, GitHub, organization-process evidence,
runtime LLM classification, a database, or a backend.
