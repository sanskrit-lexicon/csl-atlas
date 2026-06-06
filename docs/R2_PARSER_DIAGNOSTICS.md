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
- Next use: feed the generated review packets; do not broaden H1R/H2/H3R until
  high-priority parser families have source-reviewed decisions.

## What The Artifact Does

`npm run build-r2-parser-diagnostics` compares the five source-backed R2
anchor lemmas against the recovered static R2 explorer counts and classifies
each lemma/dictionary pair into a parser work package.

`npm run build-r2-review-packets` groups the same diagnostics into
reviewer-facing parser-decision packets. See
[`R2_REVIEW_PACKETS.md`](R2_REVIEW_PACKETS.md).

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
| `over-split-candidate` | 6 | Explicit-marker parser emits far more rows than the archive. | Tighten PWG/PWK `div` scope and use marker-run prefixes for BEN/AP90/BHS-style numbered markers. |
| `source-only-dictionary` | 6 | Source-backed rows exist where no archived baseline exists. | Treat as rebuild expansion, not drift. |
| `mild-drift` | 5 | Visible but lower-priority count drift. | Inspect after high-priority parser families. |
| `reverse-overmatch` | 3 | AE reverse lookup overmatches common Sanskrit equivalents. | Use rank counts to choose review/filter bands. |
| `under-split-or-source-gap` | 2 | Source rows fall below the archived static count. | Check lookup variants, source availability, and homonym aggregation. |

## Highest-Priority Parser Work

The top worklist points to four concrete parser tasks:

1. **PWG/PWK division marker scope.** `gam`, `dharma`, `rama`, and `iti`
   now expose `<div n>` labels and numeric runs, but still need source-record
   grouping and marker-class review before row counts are treated as senses.
2. **Numbered-marker run scope.** BEN `gam`, AP90 `gam`, and several nominal
   rows show that archived counts can match a prefix of numbered marker runs,
   while later runs represent participles, derived forms, or preverb material.
3. **AE reverse filtering/review.** `gam`, `dharma`, and `iti` now carry
   equivalent-position rank metadata; the next step is deciding which rank bands
   are safe enough for alignment use.
4. **Indigenous `iti` review.** SKD/VCP rows remain useful, but the artifact
   labels them as review prompts rather than sense decisions.

## Current Implementation Order

| Order | Packet | Why it comes here | Promotion rule |
|---:|---|---|---|
| 1 | `div-source-scope` | Largest row-count drift is PWG/PWK source-record and `<div n>` scope. | Promote only after source records and label classes are marked target series, derivative/prefixed series, or separate block. |
| 2 | `marker-run-scope` | Prefix matches explain several archived counts but may hide later derived runs. | Promote only when dictionary-specific marker-run rules preserve excluded/lower-confidence runs as worklist rows. |
| 3 | `ae-reverse-bands` | Reverse lookup overmatches common Sanskrit equivalents. | Promote only after rank bands are chosen and tail rows are not silently discarded. |
| 4 | `indigenous-iti-authority` | SKD/VCP rows carry authority hints but not normalized `<ls>` citations. | Promote only after `iti` boundaries and authority hints have source-facing review labels. |
| 5 | `source-gap-controls` | Parity rows and gaps are useful controls, not current blockers. | Use after high-priority parser decisions are documented. |

## Boundary

This diagnostic layer is dictionary evidence only. It does not import DCS,
corpus frequency, TEI/OntoLex, FrAC, GitHub, organization-process evidence,
runtime LLM classification, a database, or a backend.

## AE Reverse Rank Counts

AE rows are preserved, but the source-backed prototype now records where the
queried Sanskrit equivalent first appears among marked equivalent groups:

| Lemma | Source rows | Archived rows | High | Medium | Low | Tail |
|---|---:|---:|---:|---:|---:|---:|
| `gam` | 243 | 30 | 37 | 54 | 72 | 80 |
| `dharma` | 66 | 24 | 18 | 12 | 11 | 25 |
| `iti` | 76 | 30 | 9 | 7 | 23 | 37 |
| `rama` | 6 | 4 | 1 | 0 | 1 | 4 |

High-rank rows are not automatically accepted, and tail rows are not discarded.
The rank is a deterministic review and filtering aid for the reverse dictionary
only.

## Explicit Marker Run Counts

Explicit numbered markers now carry `markerRunIndex`. A new run starts when a
numeric sequence resets after a higher number. This exposes cases where the old
archive appears to have counted only a prefix of the marked runs. Current exact
prefix matches are:

| Diagnostic row | Source rows | Archived rows | Matching prefix |
|---|---:|---:|---|
| `r2-drift:gam:ben` | 172 | 23 | Runs 0-1: 9 + 14 rows = 23. |
| `r2-drift:rama:wil` | 22 | 12 | Runs 0-1: 5 + 7 rows = 12. |
| `r2-drift:bodhisattva:ap` | 3 | 2 | Run 0: 2 rows. |
| `r2-drift:dharma:ap` | 24 | 23 | Run 0: 23 rows. |
| `r2-drift:dharma:ap90` | 23 | 22 | Run 0: 22 rows. |
| `r2-drift:dharma:ben` | 12 | 11 | Run 0: 11 rows. |
| `r2-drift:dharma:wil` | 21 | 20 | Runs 0-1: 12 + 8 rows = 20. |
| `r2-drift:gam:ap90` | 15 | 14 | Runs 0-1: 6 + 8 rows = 14. |
| `r2-drift:iti:ben` | 6 | 5 | Run 0: 5 rows. |
| `r2-drift:iti:wil` | 10 | 9 | Run 0: 9 rows. |

These prefix matches are parser evidence, not automatic filters. They identify
where a future splitter can separate main sense runs from later derived or
preverb runs without discarding the latter from the worklist.

## PWG/PWK Div Marker Labels

The `<div>` splitter now captures the `n` label while keeping row identifiers
ordinal. This fixes the previous tag-loss bug and records whether a span came
from numeric labels (`1`, `2`, `3`) or lettered labels such as `p`, `v`, `m`,
and `o`.

| Diagnostic row | Source rows | Archived rows | Label counts | Numeric run counts |
|---|---:|---:|---|---|
| `r2-drift:gam:pwg` | 353 | 30 | `1`: 180, `2`: 29, `3`: 8, `p`: 111, `v`: 21 | Runs 0-4: 12, 31, 7, 108, 59. |
| `r2-drift:rama:pwg` | 44 | 6 | `1`: 10, `2`: 19, `3`: 10, `v`: 2 | Runs 0-2: 27, 8, 4. |
| `r2-drift:dharma:pwg` | 21 | 5 | `1`: 16, `2`: 3 | Run 0: 5 rows matches archive. |
| `r2-drift:iti:pwg` | 16 | 4 | `1`: 11, `v`: 1 | Run 0: 11 rows; no archive prefix match. |

For PWK, the archive has no baseline rows for these lemma/dictionary pairs, so
the same labels are retained as source-backed rebuild evidence rather than
drift evidence.

## PWG Source-Record Scope

The diagnostics now include `sourceRecordCounts`, capped to the largest source
records for each lemma/dictionary pair. For PWG, the main over-split rows are
not single-record problems; several same-headword `<L>` blocks are being
aggregated before splitting:

| Diagnostic row | Source records | Largest source records |
|---|---:|---|
| `r2-drift:gam:pwg` | 4 | `<L>21814` `gam`: 252 rows; `<L>72578` `gam`: 88 rows; `<L>119742` `gam`: 12 rows; `<L>21815` `gam`: 1 row. |
| `r2-drift:rama:pwg` | 3 | `<L>84468` `rAma`: 19 rows; `<L>84469` `rAma`: 14 rows; `<L>83557` `rama`: 11 rows. |
| `r2-drift:dharma:pwg` | 2 | `<L>36241` `Darma`: 14 rows; `<L>76490` `Darma`: 7 rows. |
| `r2-drift:iti:pwg` | 4 | `<L>10029` `iti`: 10 rows; `<L>67185` `iti`: 3 rows; `<L>67186` `iti`: 2 rows; `<L>10030` `iti`: 1 row. |

The next parser decision is therefore not just "count fewer `<div>` tags"; it
must decide which source records represent the target headword sense series and
which records are derivative, prefixed, cross-reference, or separately keyed
material.

The diagnostics also flag `sourceRecordExactMatches` when a single source
record's row count equals the archived count. These are scope clues, not
automatic filters:

| Diagnostic row | Source rows | Archived rows | Exact source-record clue |
|---|---:|---:|---|
| `r2-drift:rama:ben` | 15 | 7 | `<L>11986` `rama` has 7 rows; `<L>12079` `rAma` adds 8 more. |
| `r2-drift:dharma:skd` | 15 | 4 | `<L>17667` `DarmmaH` has 4 rows inside the SKD/VCP `iti` review class. |
| `r2-drift:bodhisattva:pwg` | 3 | 2 | `<L>53245` `boDisattva` has 2 rows; the extra row is another source-backed block. |

These matches identify candidate record-scope decisions for review. They do not
prove that the excluded same-headword records are wrong or irrelevant.

## Indigenous Authority Hints

SKD/VCP `iti` rows now carry `indigenousAuthorityHints` as review aids. These
are not `<ls>` citations and are not used as alignment anchors. SKD hints come
from a conservative list of prose authority names; VCP hints come from `...0`
markers after excluding obvious grammar labels.

| Diagnostic row | Source rows | Archived rows | Authority hints |
|---|---:|---:|---|
| `r2-drift:dharma:skd` | 15 | 4 | `hemacandra`, `matsyapurana`, `medini`, `sribhagavatam` x2; plus `amara`, `bhagavata`, `dharmadipika`, `hitopadesa`, `mahabharata`, `padmapurana`, `yogasara`. |
| `r2-drift:iti:skd` | 7 | 1 | `manu` x2; plus `amara`, `medini`, `ramayana`. |
| `r2-drift:bodhisattva:skd` | 2 | 1 | `hemacandra`, `kathasaritsagara`. |
| `r2-drift:dharma:vcp` | 27 | 9 | Raw VCP hint codes include `hemaca`, `medi`, `manava`, `vamanapu`, `varahapu`, and others for review. |

This makes the indigenous review class more informative without claiming that
SKD/VCP prose has been fully parsed into a normalized citation apparatus.
