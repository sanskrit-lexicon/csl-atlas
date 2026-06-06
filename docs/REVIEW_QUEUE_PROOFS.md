# Review Queue Proofs

Date: 2026-06-04

Audience: reviewers, scholars, and maintainers. This document explains what
each review queue proves before it explains how a reviewer should act.

## Trust Block

- Evidence: implemented review queues under `src/data/review/`, their
  generators in `scripts/`, and the shared review schema.
- Limitations: a queue is a sample or detector output, not a complete inventory
  of all dictionary problems.
- Validation: `npm run validate-review-reports`; queue-specific generators
  preserve human review fields across rebuilds.
- Owner repo: `csl-atlas`.

## Principle

Review queues are not just chores. Each queue is an argument about dictionary
evidence:

```text
machine signal -> uncertainty class -> review proof -> improved dictionary claim
```

The proof question comes first. The procedure question comes second.

## Implemented Queue Proofs

| Queue | Output | What this queue proves | What it does not prove | Current review use |
|---|---|---|---|---|
| Low-confidence dictionary alignment | `src/data/review/low-confidence-alignment-review.json` | The alignment model can identify cases where same-lemma matching is plausible but not safe enough to trust silently. | It does not prove the machine alignment is wrong; it proves the case needs source-facing judgment. | Review all 7 low-confidence alignments. |
| Unknown MW source layer | `src/data/review/unknown-source-layers-review.json` | Frequency-ranked unknown sigla show where MW diachronic/source-layer coverage is blocked by missing source metadata. | It does not prove the source is unknowable; it proves the atlas has not yet mapped it. | Review top 50 by frequency. |
| Source-siglum alias candidates | `src/data/review/source-siglum-review.json` | Repeated alias candidates show where citation normalization can improve cross-dictionary source evidence. | It does not prove an alias is valid across every dictionary; scope must remain source- and dictionary-aware. | Review top 50 by citation frequency. |
| POS/gender conflicts | `src/data/review/gender-conflicts-review.json` | Conflicts reveal dictionary disagreement, parser convention gaps, and cases where prose extraction needs review. | It does not prove one dictionary is wrong; many conflicts are legitimate convention differences. | Review a representative 25-item sample and document conflict types. |
| H5 anomaly review | `src/data/review/h5-anomaly-review.json` | F0/F2 forensic candidates can be separated into lineage signals, correction targets, parser artifacts, null controls, and legitimate morphology. | It does not prove any queued headword is wrong; every item remains a review candidate until classified. | Start with known corrections and null controls, then classify raw-headword-exclusive and shared-doublet rows. |

## Future Queue Proofs

These are not yet release review queues, but they should use the same proof-first
shape when implemented.

| Future queue | What it should prove | Boundary |
|---|---|---|
| Sense divergence | Whether cross-dictionary sense disagreement reflects copying, condensation, family style, or parser weakness; see [`R2_REBUILD_CONTRACT.md`](R2_REBUILD_CONTRACT.md). | `csl-atlas`; dictionary sense evidence only. |
| R2 parser-drift diagnostics | Whether source/archive row-count drift is a parser-family problem before it becomes a sense-alignment claim; see [`R2_PARSER_DIAGNOSTICS.md`](R2_PARSER_DIAGNOSTICS.md). | `csl-atlas`; dictionary source rows and recovered R2 fixtures only. |
| Cross-reference lineage candidates | Whether shared Sanskrit cross-reference targets preserve lineage beyond headword overlap; see [`MICROSTRUCTURE_XREF_HUB_REVIEW.md`](MICROSTRUCTURE_XREF_HUB_REVIEW.md). | `csl-atlas`; dictionary graph evidence only; `data/lexico/xref_hub_review.json` built as the review-prompt artifact. |
| SKD anubandha adjudication | Whether indigenous it-marker coding can be decoded safely enough to emit reviewed grammatical columns. | `csl-atlas`; philological review required. |
| H4 semantic-field review | Whether Amarakosa-native fields classify dictionary evidence without importing corpus categories; see [`H4_SEMANTIC_FIELD_INTERPRETATION.md`](H4_SEMANTIC_FIELD_INTERPRETATION.md) and [`H4_SEMANTIC_FIELD_REVIEW.md`](H4_SEMANTIC_FIELD_REVIEW.md). | `csl-atlas`; M8 data package, chart, family-profile artifact, and scholar review packet built. |

## Proof Types

| Proof type | Queue examples | Scholarly value |
|---|---|---|
| Boundary proof | Unknown source layers, source-siglum aliases | Shows where a generated claim needs clearer source authority. |
| Disagreement proof | POS/gender conflicts, sense divergence | Shows where dictionaries disagree or encode the same fact differently. |
| Lineage proof | Low-confidence alignments, xref lineage candidates, H5 rare-anomaly samples | Shows where inheritance or copying needs direct evidence. |
| Parser proof | POS/gender conflicts involving SKD/VCP, SKD anubandha, R2 parser-drift diagnostics | Shows where a detector is blind to a dictionary convention. |

## How To Read Review Counts

Review progress is a release signal, not a claim that the remaining machine rows
are useless. Counts should be reported with three distinctions:

- `needs-review`: useful machine queue, not yet human-confirmed;
- `reviewed-ok` or `reviewed-corrected`: human-reviewed evidence;
- `blocked` or `deferred`: real uncertainty preserved instead of hidden.

For large queues, review a representative sample and document the conflict
types. Do not exhaust thousands of rows just to make the count look finished.

## Required Page Text For Queue Pages

Every review queue page should include:

```md
## This Queue Proves

...

## This Queue Does Not Prove

...

## Trust Block

- Evidence:
- Limitations:
- Validation:
- Owner repo:
```

Then link to the procedure in [`REVIEW_REPORTS.md`](REVIEW_REPORTS.md) or
[`LIGHT_REVIEW_SPRINT.md`](LIGHT_REVIEW_SPRINT.md).

## Public Queue Page Coverage

These public queue pages now carry the required proof-first text and trust
block:

| Page | Queue proof covered |
|---|---|
| `/tools/review-alignment` | low-confidence dictionary alignment |
| `/tools/review-source-layers` | unknown MW source-layer sigla |
| `/tools/review-source-siglum` | source-siglum alias candidates |
| `/tools/review-gender-conflicts` | POS/gender conflicts |

## Validation Commands

```sh
npm run build-gender-review
npm run build-source-layer-review
npm run build-alignment-review
npm run build-citation-apparatus
npm run build-h5-anomaly-review
npm run build-r2-parser-diagnostics
npm run validate-review-reports
```

Run only the relevant generator when editing one queue, then always run
`validate-review-reports`.

## Related Docs

- [`REVIEW_REPORTS.md`](REVIEW_REPORTS.md)
- [`LIGHT_REVIEW_SPRINT.md`](LIGHT_REVIEW_SPRINT.md)
- [`USE_CASES.md`](USE_CASES.md)
- [`CHART_TRUST_TEMPLATE.md`](CHART_TRUST_TEMPLATE.md)
- [`EVIDENCE_LABELS.md`](EVIDENCE_LABELS.md)
