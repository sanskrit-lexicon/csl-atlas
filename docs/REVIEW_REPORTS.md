# Review Reports

Date: 2026-05-29

Audience: reviewers, developers, and maintainers. This document defines the shared shape and workflow for review reports across the atlas.

Review is part of the design, not an afterthought (`ARCHITECTURE.md`, "Review Architecture"). Review reports are how machine-derived data becomes reliable scholarship: they let a human accept, correct, defer, or block a machine claim **without editing generated source data directly.**

## Principle

```text
machine output -> review report -> trusted claim
```

A review report is an overlay. The generator stays deterministic and reproducible; the report records the human judgment layered on top. Re-running the build never erases a review, because reviews live in separate report files keyed by stable IDs.

This mirrors the org-wide correction pattern: source files are never edited in place; corrections are expressed as separate change records applied on top.

## Canonical Review Status Vocabulary

All review reports use this status set (from `ARCHITECTURE.md`):

| Status | Meaning |
|---|---|
| `machine` | Produced by heuristics; no human has looked at it |
| `needs-review` | Flagged for a human because confidence is low or sources conflict |
| `reviewed-ok` | A human confirmed the machine value is correct |
| `reviewed-corrected` | A human supplied a corrected value |
| `blocked` | Cannot be resolved yet (bad source data, missing evidence) |
| `deferred` | Valid but postponed to a later phase |

### Reconciliation With Existing Reports

Two narrower status sets already exist in the pilot and must be read as subsets of the canonical vocabulary:

- **Loss reports** (`docs/LOSS_REPORT_SCHEMA.md`) use `machine`, `reviewed`, `published`. Here `reviewed` corresponds to `reviewed-ok` / `reviewed-corrected`, and `published` is an additional downstream flag meaning "used in the paper/demo narrative."
- **Pilot review files** (`data/pilot/*-review.json`, e.g. `tei-review.json`, `ontolex-review.json`, `external-validation-review.json`) predate this vocabulary. New reports should adopt the canonical set; old files may be migrated when next touched.

When in doubt, use the canonical six-status set above and add `published` only as a separate boolean or downstream flag, not as a review status.

## What Gets A Review Report

Review reports back the review use cases in `docs/USE_CASES.md`:

| Queue | Use case | Triggered by |
|---|---|---|
| Low-confidence dictionary alignment | UC-RV-01 | alignment confidence below threshold |
| POS / gender conflict | UC-RV-02 | dictionaries disagree on grammar |
| Unknown source layer | UC-RV-03 / UC-DIA-07 | source abbreviation maps to `unknown` |
| Corpus lemma mismatch | UC-RV-04 | corpus lemma fails to align with a dictionary |
| Encoding / OCR problem | UC-RV-05 | parser emits a source-quality warning |
| Generated TEI / OntoLex review | UC-RV-06 / UC-RV-07 | loss report `status` is `partial`, `lossy`, or `failure` |
| Over-broad inferred family | — | `inferred` family exceeds a size/divergence heuristic |

A claim labeled `observed` rarely needs a queue. A claim labeled `inferred` almost always does. See [`docs/EVIDENCE_LABELS.md`](EVIDENCE_LABELS.md).

## JSON Shape

Review reports are JSON-first and reproducible. A single review record:

```json
{
  "reviewId": "mw-align:agni:pwg-mw",
  "queue": "low-confidence-alignment",
  "subject": {
    "kind": "alignment",
    "lemma": "agni",
    "dictionaries": ["mw", "pwg"]
  },
  "sourcePointers": [
    { "dictionary": "mw",  "L": "1767", "line": 6284,
      "href": "https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw.txt#L6284" },
    { "dictionary": "pwg", "L": "...",  "line": 0, "href": "..." }
  ],
  "machineValue": { "aligned": true, "confidence": 0.42 },
  "evidenceLevel": "inferred",
  "reviewStatus": "needs-review",
  "reviewedValue": null,
  "reviewer": null,
  "reviewedAt": null,
  "note": ""
}
```

When a human acts, they fill the trailing fields and change `reviewStatus`:

```json
{
  "reviewStatus": "reviewed-corrected",
  "reviewedValue": { "aligned": false },
  "reviewer": "initials-or-id",
  "reviewedAt": "2026-05-30",
  "note": "Different homonym; PWG splits where MW merges."
}
```

### Fields

| Field | Required | Meaning |
|---|---|---|
| `reviewId` | yes | Stable identifier; survives rebuilds |
| `queue` | yes | Which review queue this belongs to |
| `subject` | yes | What is under review (alignment, entry, source abbreviation, family, …) |
| `sourcePointers` | yes | One or more links back to source records |
| `machineValue` | yes | What the generator produced |
| `evidenceLevel` | yes | `observed` / `derived` / `inferred` / `reviewed` |
| `reviewStatus` | yes | Canonical status from the table above |
| `reviewedValue` | no | The corrected value, if `reviewed-corrected` |
| `reviewer` | no | Who reviewed it |
| `reviewedAt` | no | ISO date of review |
| `note` | no | Free-text rationale |

Every review report **file** also carries the standard generated-output envelope used elsewhere in the project: `schemaVersion`, `generatedAt`, `sourcePath`, `recordCount`, `assumptions`, `warnings`.

## File Layout

Follow the directory strategy in `ARCHITECTURE.md`:

```text
src/data/review/        review reports consumed by Observable pages
data/pilot/*-review.json existing pilot reviews (TEI, OntoLex, external validation)
data/schema/            JSON schemas (add review-report.schema.json here)
```

A formal `review-report.schema.json` should be added under `data/schema/` alongside the existing `loss-report.schema.json`, `hard-case.schema.json`, and `neutral-model.schema.json`, and validated the same way.

## Workflow

```text
1. build        generator emits machine values with evidenceLevel + warnings
2. select       a script collects low-confidence/conflicting cases into a queue
3. review       a human sets reviewStatus and (if needed) reviewedValue
4. apply        downstream builds prefer reviewedValue over machineValue
5. report       a coverage dashboard shows machine vs reviewed counts (UC-RV-09)
```

Steps 2 already has precedent in `scripts/select-review-cases.mjs` (→ `data/pilot/review-cases.json`) and `scripts/sample-hard-cases.mjs`. New queues should reuse that pattern rather than inventing one-off report formats.

## Rules

- A review never edits generated source data — it overlays it.
- A rebuild must not discard reviews; reports are keyed by stable `reviewId`.
- No lossy or low-confidence claim silently passes as trusted (mirrors the loss-report principle).
- Every report points back to a source record so a reviewer can verify, not just accept.
- Reviewed values flow downstream and their effect must be visible (UC-RV-09, Milestone D).

## Related Documents

- [`docs/EVIDENCE_LABELS.md`](EVIDENCE_LABELS.md) — evidence labels vs review status.
- `docs/LOSS_REPORT_SCHEMA.md` — the loss-report shape that review reports generalize.
- `docs/DICTIONARY_COMPARISON_PLAN.md` — the alignment queues that produce most reviews.
- `docs/USE_CASES.md` — UC-RV-01 through UC-RV-09 and Milestone D.
- `ARCHITECTURE.md` — the review architecture and status list.
