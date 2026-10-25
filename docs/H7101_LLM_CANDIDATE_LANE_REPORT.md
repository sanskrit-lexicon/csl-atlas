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

### Agreement and uncertainty

`score-llm-candidate-lane.mjs` now reports a paired, seeded percentile
bootstrap (2 000 resamples, seed `H7101-2026-10-19`) and Cohen's κ between each
lane's non-abstained predictions and the gold label. Both lanes are resampled
with the same indices, so the intervals are comparable.

| Lane | Accuracy (all) | 95 % CI | Macro-F1 (abstain=0) | 95 % CI | Target-error F1 | 95 % CI | Binary any-correction F1 | 95 % CI | κ vs gold |
|---|---:|---|---:|---|---:|---|---:|---|---:|
| Rule baseline | 0.2160 | 0.1800–0.2520 | 0.1284 | 0.0977–0.1690 | 0.3589 | 0.3018–0.4131 | 0.9293 | 0.9119–0.9451 | −0.1017 (n=500) |
| LLM lane (500 abstentions) | 0.0000 | 0.0000–0.0000 | 0.0000 | 0.0000–0.0000 | 0.0000 | 0.0000–0.0000 | 0.0000 | 0.0000–0.0000 | undefined (n=0) |

The baseline κ is **negative**: on the five-label task it agrees with the gold
less often than chance would (observed 0.216 vs expected 0.288). Its high
any-correction F1 measures only that it almost never abstains and almost always
says "a correction happened", which is true for 434 of 500 rows.

Krippendorff α is **not reported**: computing it requires two independent human
rater columns, and the frozen sample carries one gold label per row (weak diff
label for the 400 correction-loci rows, human `reviewedValue` for the 100 H5
rows). `scores.json` records this as a named null (`agreement.alphaReason`), not
as a number. κ above is model-vs-gold agreement, not inter-human agreement, and
must not be read as an annotation-quality statistic.


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
npm run score-llm-candidate            # alias of score-llm-candidate-lane
npm run validate-llm-candidate-lane
node --test test/llm-candidate-lane.test.mjs

# Credentialed run (the only path that may replace the abstain outputs):
H7101_LLM_API_KEY=... H7101_LLM_MODEL=... \
  npm run run-llm-candidate-lane -- --out data/llm-candidate-lane/outputs/llm-run.jsonl
npm run score-llm-candidate -- --llm data/llm-candidate-lane/outputs/llm-run.jsonl
```

The tests lock the 500-row count, composition, no-gold-leak prompt rendering,
six-variant cap, machine-candidate provenance, abstention semantics, seeded-CI
determinism, κ reporting, and the refusal to validate a schema keyword the
checker cannot enforce (14 tests). `validate-llm-candidate-lane.mjs` is part of
the `npm run verify` chain since 25-10-2026, so the provenance contract is
enforced on every PR and on every push to `main` — not only when someone
remembers to run it by hand.

### Verification receipt — 25-10-2026

Fresh clone of `main` (`e8e5771`), portable Node v20.19.0, Windows:

| Check | Command | Result |
|---|---|---|
| Lane tests | `node --test test/llm-candidate-lane.test.mjs` | 14 pass / 0 fail |
| Schema + provenance gate | `node scripts/validate-llm-candidate-lane.mjs` | `status: OK`, 500 sample rows, 2 output files valid, 0 violations |
| Scorer reproduction | `npm run score-llm-candidate` | rewrites `data/llm-candidate-lane/scores.json` byte-identically (`git status` clean; only the preserved `generatedAt`) |
| Generator determinism | `npm run build-llm-candidate-lane` | sample, prompts, both output files and scores unchanged (`git status` clean) |
| Verdict | — | NO-GO, unchanged; `llm.coverage = 0`, 500 explicit abstentions |

The `build-llm-candidate-lane`, `run-llm-candidate-lane` and
`score-llm-candidate-lane` npm entries were added by #604 but removed by the
H7100 fix (#613) as a package.json merge side-effect; the 24-10-2026 pass
restored them and added the handoff's exact `score-llm-candidate` /
`run-llm-candidate-eval` aliases. The `import.meta.url === file://${argv[1]}`
main-guard in both scripts also silently skipped `main()` on Windows; it now
uses `pathToFileURL`, so `npm run score-llm-candidate` actually reproduces the
tables above instead of printing nothing.

## Limitations

1. **One gold key, not two.** H7101 asks for two independent human labels and
   adjudication per row. The frozen sample has one label per row. Krippendorff α
   is therefore a named null, and the 400 correction-loci labels are weak diff
   labels over human corrections, not a fresh editorial judgement.
2. **The LLM lane is unrun, not scored.** All 500 LLM rows are explicit
   abstentions (`runStatus: not-run-no-credentials`). The NO-GO is a NO-GO on
   evidence, not a measured loss; a credentialed run is the only way to change
   it, and it must use the frozen sample and P6.
3. **The baseline is worse than chance on the five-label task** (κ −0.1017).
   Its binary any-correction F1 0.9293 is largely the base rate (434/500 rows
   need correction), so "beats the baseline" is a low bar that still requires a
   positive paired lower bound.
4. **The two strata are not interchangeable.** 400 rows are weak-label
   correction loci; 100 are human-adjudicated H5 queue rows with different
   semantics. Per-source scores are reported separately and no pooled number
   should be read as a single task's precision.
5. **Spend and call caps are untested.** The €5 / 500-call limits are enforced
   by the runner's design, not by an executed run in this unit.

## Handoff-spec path mapping

H7101 named its deliverables before the lane's JSONL layout was chosen. The
landed names below are canonical; the spec names are kept here so a later
reader can reconcile the two without hunting.

| H7101 spec path | Landed path |
|---|---|
| `data/llm_candidate/eval_sample.tsv` | `data/llm-candidate-lane/sample-500.jsonl` |
| `data/llm_candidate/outputs.jsonl` | `data/llm-candidate-lane/outputs/llm-abstain.jsonl` (+ `rule-baseline.jsonl`) |
| `data/schema/llm-candidate.schema.json` | `data/llm-candidate-lane/provenance.schema.json` |
| `scripts/run-llm-candidate-eval.mjs` | `scripts/run-llm-candidate-lane.mjs` (`npm run run-llm-candidate-eval`) |
| `scripts/score-llm-candidate.mjs` | `scripts/score-llm-candidate-lane.mjs` (`npm run score-llm-candidate`) |
| `reports/LLM_CANDIDATE_LANE_2026.md` | `docs/H7101_LLM_CANDIDATE_LANE_REPORT.md` |
| `docs/LLM_CANDIDATE_POLICY.md` | `docs/LLM_CANDIDATE_POLICY.md` (added 24-10-2026) |

No TSV mirror was added: the sample is schema-bearing JSONL, and a second
serialisation would be a second source of truth for the same 500 rows.

## Boundary


- Atlas consumes correction events; `csl-corrections` owns them.
- Candidate generation only; no auto-promotion, no review-status mutation.
- The 500-row sample is held out; do not use it for prompt selection after
  seeing scores (that would turn the evaluation into training). P6 was selected
  before any scored run.
- A future credentialed run must use the exact frozen sample and record the
  returned model revision. Any change to the sample requires a new handoff.
