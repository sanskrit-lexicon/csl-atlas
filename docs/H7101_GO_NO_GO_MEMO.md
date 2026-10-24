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

## What is allowed next

A **single credentialed evaluation run** on the already-frozen
`data/llm-candidate-lane/sample-500.jsonl` using prompt P6 and the recorded
model revision. That run may only replace the abstain outputs; it may not
change the sample, add prompt variants after seeing scores, or mutate review
statuses. If its macro-F1 does not beat 0.1284, the lane stays NO-GO and the
null is final for this design.

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
