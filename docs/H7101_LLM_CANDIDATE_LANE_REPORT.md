# H7101 — LLM candidate lane with span provenance and abstention

_Status: experiment frozen · 19-10-2026_

This is an offline, bounded candidate-generation lane for atlas review queues.
It freezes a 500-row held-out evaluation sample, records six prompt designs,
scores a deterministic surface-rule baseline, and keeps the LLM lane behind an
explicit abstention/null boundary. **No row is promoted to reviewed and no
full-corpus run is allowed before this evaluation is scored.**

## What was built

| Artifact | Path |
|---|---|
| Frozen 500-row sample | `data/llm-candidate-lane/sample-500.jsonl` |
| Six prompt variants (P6 selected) | `data/llm-candidate-lane/prompts.json` |
| Span-provenance schema | `data/llm-candidate-lane/provenance.schema.json` |
| Rule-baseline outputs | `data/llm-candidate-lane/outputs/rule-baseline.jsonl` |
| LLM-lane outputs (abstain/null) | `data/llm-candidate-lane/outputs/llm-abstain.jsonl` |
| Scores | `data/llm-candidate-lane/scores.json` |
| Build / score scripts | `scripts/build-llm-candidate-lane.mjs`, `scripts/score-llm-candidate-lane.mjs` |
| Credentialed runner (not executed here) | `scripts/run-llm-candidate-lane.mjs` |
| Tests | `test/llm-candidate-lane.test.mjs` |

## Frozen sample

Source: `csl-corrections` commit `307bad2631a0f764138bbc98f77b04b92dfb7c41`,
`data/derived/correction_loci.tsv` (sha256
`4e89b93f48859c73c0eee9d41ab9c802888693cf651125bcc31504899399a907`).
Seed: `H7101-2026-10-19`. Selection is a sorted SHA-256 order over the row key,
so the sample is deterministic and can be re-derived but never silently
reshuffled by an ordinary rebuild.

| Source | Rows | Gold provenance |
|---|---:|---|
| Correction loci (human process only) | 400 | weak diff label over the human old→new correction pair |
| H5 anomaly review queues | 100 | human `reviewedValue` (possible-typo, parser-artifact, variant-convention, legitimate-form, lineage-only) |

| Gold edit type | Rows |
|---|---:|
| `ocr-error` | 122 |
| `markup-normalization` | 235 |
| `source-mismatch` | 60 |
| `sense-split` | 17 |
| `no-correction` | 66 |

The correction-loci part is a **weak-label** set: the type is inferred from
what the human correction changed (letter change, sense boundary, `<ls>`
citation content, punctuation/tag churn). It is evidence of what editors did,
not a second independent adjudication. The H5 part is genuinely
human-adjudicated but covers different queue semantics. Both facts are carried
in `gold.labelProvenance`; neither is silently upgraded.

## Evaluation definitions

- **Coverage**: non-abstained predictions / 500.
- **All-row accuracy**: abstain counted as wrong.
- **Selective accuracy**: correct / non-abstained.
- **Macro-F1 (abstain = 0)**: all five labels, missing predictions score zero.
- **Binary target error**: `ocr-error`, `sense-split`, `source-mismatch` vs the
  rest.
- **Binary any correction**: every label except `no-correction` vs
  `no-correction`.

The rule baseline is independent of the gold span: it reads only the input
line and fires on mixed-script/replacement characters, trailing punctuation
inside `<ls>`, or several sense separators without a `<div>` boundary, and
defaults to `markup-normalization`.

## Results

Run: `npm run build-llm-candidate-lane && npm run score-llm-candidate-lane`.

| Lane | Coverage | Accuracy (all rows) | Macro-F1 (abstain=0) | Target-error F1 | Any-correction F1 |
|---|---:|---:|---:|---:|---:|
| Surface-rule baseline (all 500) | 1.000 | 0.216 | 0.1284 | 0.3589 | 0.9293 |
| Surface-rule baseline (human H5 subset) | 1.000 | 0.120 | 0.0432 | 0.0870 | 0.5075 |
| LLM lane (this unit) | 0.000 | 0.000 | 0.0000 | null | null |

The LLM lane did not run in this offline unit: no provider credentials and no
local inference runtime were available. Its honest output is 500 explicit
abstentions (`runStatus: not-run-no-credentials`), not a fabricated
prediction. Consequently the LLM has **no evidence of gain** over the rule
baseline, and the lane must not be expanded.

The rule baseline is deliberately weak — it never predicts `ocr-error` or
`no-correction`, and its `<ls>` punctuation cue over-fires (252 source-mismatch
predictions for 60 gold rows). That is the point of keeping it: it is a named
floor, not a tuned target. On the 100-row human-adjudicated H5 subset it scores
macro-F1 0.0432 and all-row accuracy 0.120, so the human-adjudication stratum is
harder than the weak-label stratum, not easier.

## Span provenance schema

`provenance.schema.json` records, for each candidate:

`id`, `sourceRef` (repo, commit/path, dict, locus, correction batch, or review
id/queue), `inputSha256`, `prompt` id/version/hash, `model`
provider/name/revision/temperature, `prediction` (`editType`, exact `span`
text/start/end, `confidence`, `abstain`, `rationale`), and `provenance`
(`editType`, source, model, confidence, abstain, `revisionStatus:
machine-candidate`, `reviewedValue: null`, `reviewer: null`, `reviewedAt:
null`). The schema forbids a human-review status on a machine candidate.

## Reproduction and checks

```bash
npm run build-llm-candidate-lane
npm run score-llm-candidate-lane
node --test test/llm-candidate-lane.test.mjs

# Credentialed run (the only path that may replace the abstain outputs):
H7101_LLM_API_KEY=... H7101_LLM_MODEL=... \
  npm run run-llm-candidate-lane -- --out data/llm-candidate-lane/outputs/llm-run.jsonl
npm run score-llm-candidate-lane -- --llm data/llm-candidate-lane/outputs/llm-run.jsonl
```

The tests lock the 500-row count, composition, no-gold-leak prompt rendering,
six-variant cap, machine-candidate provenance, and abstention semantics.

## Boundary

- Atlas consumes correction events; `csl-corrections` owns them.
- Candidate generation only; no auto-promotion, no review-status mutation.
- The 500-row sample is held out; do not use it for prompt selection after
  seeing scores (that would turn the evaluation into training). P6 was selected
  before any scored run.
- A future credentialed run must use the exact frozen sample and record the
  returned model revision. Any change to the sample requires a new handoff.
