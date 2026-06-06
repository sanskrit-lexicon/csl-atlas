# Light Review Sprint

Date: 2026-06-03

Status: worklist for the 3-month review release. This document prepares human review; it does not claim that the cases are already philologically resolved.

## Principle

Review decisions are overlays. A reviewer edits the review fields in the queue file or the reviewed mapping table; generators preserve those decisions by stable ID on rebuild.

Do not edit generated source data directly.

For the proof value of each queue, see
[`REVIEW_QUEUE_PROOFS.md`](REVIEW_QUEUE_PROOFS.md). This sprint records reviewer
actions; the proof page records why each queue matters.

## Worklists

| Sprint item | Scope | File | Reviewer action |
|---|---:|---|---|
| Low-confidence alignments | 7 total | `src/data/review/low-confidence-alignment-review.json` | Decide same lemma vs separate lemma; set `reviewStatus` and `reviewedValue`. |
| MW source layers | top 50 by frequency | `src/data/review/unknown-source-layers-review.json` | Add confirmed source layer to `src/data/mw-source-layers.json`. |
| Source-siglum aliases | top 50 by citations | `src/data/review/source-siglum-review.json` | Add confirmed alias to `src/data/dict-source-aliases.json` or mark deferred/blocked. |
| Gender conflicts | 25 representative cases | `src/data/review/gender-conflicts-review.json` | Classify disagreement type; correct only when source evidence is clear. |

## Selection Rules

- Source-layer and siglum worklists are already frequency-sorted by their generators; review the first 50 `needs-review` items.
- Gender conflicts are numerous and heterogeneous. For the 25-case sample, take the first 10 two-dictionary conflicts, first 10 conflicts involving VCP/SKD prose extraction, and first 5 conflicts involving three or more dictionaries.
- TEI/OntoLex cases are reviewed in `csl-standards`, not in this atlas sprint.

## Recording A Decision

For review queue files, update only these trailing fields:

```json
{
  "reviewStatus": "reviewed-ok",
  "reviewedValue": null,
  "reviewer": "initials-or-id",
  "reviewedAt": "2026-06-03",
  "note": "Short source-based rationale."
}
```

Use `reviewed-corrected` when supplying a corrected machine value, `blocked` when the evidence is insufficient, and `deferred` when the case is valid but outside the release.

## Rebuild Check

After recording decisions:

```bash
npm run build-mw-depth
npm run build-citation-apparatus
npm run build-gender-review
npm run build-alignment-review
npm run validate-review-reports
npm run build
```

The exact generator depends on the edited queue, but `validate-review-reports` should always pass.

## Expected Release Result

The release should report:

- how many review decisions were completed;
- which queues remain machine-only;
- which mappings improved downstream data;
- which cases were blocked or deferred.

It should not hide unresolved machine output.
