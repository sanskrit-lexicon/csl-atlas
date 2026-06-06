# R2 Non-Final Rebuild Experiment

Date: 2026-06-06

Status: baseline experiment note for the next R2 source-backed rebuild pass.
This is not the restored final R2 splitter, not a broadened sense-alignment
claim, and not a scholar-reviewed sense decision layer.

## Trust Block

- Evidence: `data/lexico/r2_source_anchor_summary.json`,
  `data/lexico/r2_source_anchor_senses.jsonl`,
  `data/lexico/r2_source_anchor_alignments.json`,
  `data/lexico/r2_parser_diagnostics.json`,
  `data/lexico/r2_review_packets.json`,
  `data/lexico/r2_packet_label_proposals.json`,
  `data/lexico/r2_checkpoint_review_packet.json`,
  `src/data/review/r2-checkpoint-review.json`,
  `docs/R2_CHECKPOINT_DECISIONS.md`,
  `docs/R2_CHECKPOINT_REVIEW.md`, and the five source-inspected proposal docs
  linked from `R2_REVIEW_PACKETS.md`.
- Evidence label: `source-vs-archive`.
- Limitations: the experiment is restricted to the five anchor lemmas and 14
  dictionaries already present in the prototype. It records parser drift and
  packet routing, not final sense equivalence.
- Validation: `npm run build-r2-source-anchors`,
  `npm run build-r2-parser-diagnostics`,
  `npm run build-r2-review-packets`,
  `npm run build-r2-label-proposals`,
  `npm run build-r2-checkpoint-packet`,
  `npm run build-r2-checkpoint-review`, `git diff --check`, `npm test`,
  `npm run validate-review-reports`, and `npm run build`.
- Review status: `machine-proposed`.
- Owner repo: `csl-atlas`.
- Boundary note: dictionary source rows and recovered R2 archive fixtures only;
  no DCS, corpus frequency, TEI/OntoLex, FrAC, backend, database,
  GitHub/org-process evidence, runtime LLM classification, or cross-repo
  content join.

## Baseline Rerun

The first experiment step reran the existing source-backed R2 pipeline from
current `main`:

```powershell
npm run build-r2-source-anchors
npm run build-r2-parser-diagnostics
npm run build-r2-review-packets
```

The regenerated content was stable against the committed artifacts. The working
tree saw only Windows line-ending/stat churn after regeneration, so the data
files were restored before this note was added.

| Output | Baseline result |
|---|---:|
| Anchor lemmas | 5 |
| Dictionaries | 14 |
| Source-backed rows | 1,811 |
| Archived R2 rows | 445 |
| Parser diagnostic rows | 70 |
| High-priority diagnostic rows | 17 |
| Review packets | 5 |

Diagnostic distribution:

| Drift class | Rows |
|---|---:|
| `archive-parity` | 28 |
| `no-anchor-evidence` | 12 |
| `indigenous-coarse-review` | 8 |
| `over-split-candidate` | 6 |
| `source-only-dictionary` | 6 |
| `mild-drift` | 5 |
| `reverse-overmatch` | 3 |
| `under-split-or-source-gap` | 2 |

Parser-family distribution:

| Parser family | Rows |
|---|---:|
| `western` | 55 |
| `indigenous` | 10 |
| `reverse` | 5 |

## Packet Gates

The machine-readable labels + checkpoint step keeps the packet order fixed:

| Order | Packet | Rows | High priority | Proposal layer | Gate |
|---:|---|---:|---:|---|---|
| 1 | `div-source-scope` | 10 | 4 | `R2_DIV_SOURCE_SCOPE_LABELS.md` | Only target-primary and target-subseries rows can move toward promoted splitting. Derivative, compound, source-expansion, and source-noise rows stay out of archive-parity claims. |
| 2 | `marker-run-scope` | 28 | 2 | `R2_MARKER_RUN_SCOPE_LABELS.md` | Archive-parity marker runs can become controls; over-split prefix rows and source-record aggregates need follow-up before promotion. |
| 3 | `ae-reverse-bands` | 5 | 3 | `R2_AE_REVERSE_BAND_LABELS.md` | Accept rank-1 exact reverse rows first, quarantine high-rank/common-equivalent noise, and review mid-rank rows separately. |
| 4 | `indigenous-iti-authority` | 10 | 8 | `R2_INDIGENOUS_ITI_AUTHORITY_LABELS.md` | Keep SKD/VCP `iti` units, authority quotations, raw sigla, and grammar/commentary units visible; do not flatten them into reviewed senses. |
| 5 | `source-gap-controls` | 17 | 0 | `R2_SOURCE_GAP_CONTROL_LABELS.md` | Use archive-parity rows as regression controls and keep source-only, no-anchor, homonym, lookup-bundle, and continuation rows separate. |

## Next Accepted Step

The next accepted step is **record checkpoint decisions in the shared review
report**, not parser promotion. The decision-capture package must:

1. generate `src/data/review/r2-checkpoint-review.json` from
   `data/lexico/r2_checkpoint_review_packet.json`;
2. preserve the exact ten checkpoint rows and their order by `diagnosticId`;
3. use canonical shared review-report fields with `queue: "r2-checkpoint"`;
4. keep `reviewedValue`, `reviewer`, `reviewedAt`, and `note` empty/null until
   a human reviewer supplies decisions;
5. preserve future human fields across rebuilds while refreshing machine fields;
6. keep H5 review rows, public R2 pages, source-anchor generation, and splitter
   behavior untouched.

Archive parity remains a comparison signal and regression-control cue. It is
not the optimization target; labels should explain source scope, marker scope,
reverse-rank risk, indigenous prose units, and controls without collapsing
source evidence just to match archived counts.

## Deferred Parser Pass

Parser promotion can be reconsidered only after the checkpoint rows have human
decisions. A future parser-change pass should:

1. rerun the R2 generator commands plus
   `npm run build-r2-label-proposals` and
   `npm run build-r2-checkpoint-packet` and
   `npm run build-r2-checkpoint-review`;
2. record changed row counts by packet, drift class, and parser family;
3. explain every high-priority diagnostic row whose source/archive comparison
   changes;
4. leave proposal labels as parser metadata, not `reviewedValue`;
5. keep H5 review rows untouched unless a human reviewer supplies decisions;
6. keep archive parity as a comparison signal rather than a row-count target;
7. avoid broadening beyond `gam`, `dharma`, `rama`, `iti`, and `bodhisattva`
   until the anchor run explains or reproduces the archived payloads.
