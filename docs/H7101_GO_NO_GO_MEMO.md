# H7101 — GO/NO-GO memo

_19-10-2026 · Decision owner: csl-atlas · Evidence: `data/llm-candidate-lane/scores.json`_

## Decision

**NO-GO** for expanding the LLM candidate lane, running the model over the full
corpus, or promoting any candidate row.

## Why

1. The LLM lane produced **zero predictions** in this offline unit. There were
   no provider credentials and no local inference runtime, so the lane emitted
   500 explicit abstentions (`runStatus: not-run-no-credentials`) rather than
   invented output.
2. Coverage is therefore 0.000 and there is **no measured gain** over the
   surface-rule baseline (macro-F1 0.1284, all-row accuracy 0.216 on the frozen
   500-row sample).
3. The acceptance rule is explicit: fail = no gain over baseline; publish the
   null and the stopping rule. This memo is that publication.
4. The gold labels for the correction-loci stratum are weak diff labels over
   human correction events, not a fresh second adjudication. Even a positive
   LLM score would need human adjudication of the candidate rows before any
   promotion.
5. The baseline itself is weak evidence of difficulty: κ vs gold is −0.1017
   (worse than chance on the five-label task), macro-F1 95 % CI 0.0977–0.1690.
   Krippendorff α is not computable — the sample has one gold label per row and
   the second independent human key required by H7101 does not exist yet. This
   gap is a named residual, not a silent substitution.

## What is allowed next

A **single credentialed evaluation run** on the already-frozen
`data/llm-candidate-lane/sample-500.jsonl` using prompt P6 and the recorded
model revision. That run may only replace the abstain outputs; it may not
change the sample, add prompt variants after seeing scores, or mutate review
statuses. It is scored by `npm run score-llm-candidate`, which now emits paired
bootstrap CIs and model-vs-gold κ.

The lane flips only if the LLM's macro-F1 beats 0.1284 **and** the paired
bootstrap 95 % CI of the difference excludes zero. Beating a −0.10-κ baseline
by a hair is not a GO: the baseline is a floor, and a two-point gain over a
floor this low is not evidence of a usable triage signal.

## Stopping rule

- Six prompt designs are frozen; no seventh design in this handoff.
- Stop after the first scored 500-row run; do not tune prompts on the same
  held-out sample.
- Zero full-corpus runs until a separate GO decision.
- No auto-promotion at any stage: `revisionStatus` stays `machine-candidate`,
  and `reviewedValue` / `reviewer` / `reviewedAt` stay null.

## Evidence links

- Report: `docs/H7101_LLM_CANDIDATE_LANE_REPORT.md`
- Scores: `data/llm-candidate-lane/scores.json`
- Manifest: `data/llm-candidate-lane/manifest.json`
- Test: `test/llm-candidate-lane.test.mjs`
