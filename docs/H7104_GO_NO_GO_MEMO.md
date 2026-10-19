# H7104 — GO/NO-GO memo

_19-10-2026 · decision owner: handoff executor · evidence: `data/eval/crossdict-defgen/crossdict_scores.json`_

## Decision

**GO** for the cross-dictionary definition-candidate lane. **NO-GO** for
promoting any generated definition into dictionary content.

## Why GO

1. **Cross-dictionary preservation clears the floor.** On the 249 lemmas where
   AP/PWG/PWK distinguish at least two senses, A2_chat_noctx preserves an
   adequate multi-sense gloss in 89.16 % of cases; the random floor scores 0 %
   once adequacy is required. A1 81.93 %, F1 76.71 %, A3 55.82 %.
2. **The sharpest cross-dictionary signal survives.** On the 193 lemmas where
   MW is mono-sense but AP/PWG/PWK are poly-sense, A2 preserves 93.78 %.
3. **The judge is calibrated.** The 100-row human key agrees with the frozen
   LLM judge at quadratic weighted kappa 0.9356, within-one agreement 0.970.
4. **Count consistency beats the floor.** A2 sense-count F1 against the
   cross-dictionary maximum is 0.673 vs 0.568 for the random floor.

## Why not promote

- The generation and judge are MW-contaminated by construction.
- Sense units are structural marker counts, not curated senses.
- The human calibration is one key, not two blind keys plus adjudication.
- No bounded 100-item replication was run in this unit.
- No generated definition may be auto-accepted as dictionary content (mission
  guard).

## Stopping rule

Stop after six tries and publish the null if either condition fails:

- the best arm does not beat the random floor on adequacy-gated preservation
  and sense-count F1, or its preservation rate is below 0.50; or
- judge-vs-human quadratic weighted kappa is below 0.40.

Both conditions passed on the first evaluation of the frozen arms. The next
try is therefore **not** another generation sweep; it is the bounded 100-item
replication plus a second blind human key, run only if a promotion decision is
requested.

## Repro

```bash
npm run build-crossdict-defgen-eval
node --test test/crossdict-defgen-eval.test.mjs
```

## Inspect first

- `data/eval/crossdict-defgen/crossdict_scores.json` → `verdict`,
  `summary.byArm`, `judgeCalibration`.
- `docs/H7104_CROSSDICT_DEFGEN_EVAL_REPORT.md` → results and caveats.
- `data/eval/crossdict-defgen/judge_calibration_sample.csv` and
  `judge_calibration_human.tsv` → the 100 human scores.
