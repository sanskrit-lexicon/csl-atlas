# LLM candidate policy — csl-atlas

_Created: 19-10-2026 · Last updated: 24-10-2026 (H7101 DeepSeek execution pass · policy first written)_

This policy governs every machine-generated candidate that touches a csl-atlas
review queue. It is normative: a script that violates it is a bug, not a
variant. Current standing decision for the H7101 lane is **NO-GO** until a
credentialed run beats the rule baseline on the frozen 500-row sample
([`data/llm-candidate-lane/`](../data/llm-candidate-lane), memo
[`H7101_GO_NO_GO_MEMO.md`](H7101_GO_NO_GO_MEMO.md)).

## 1. Candidates are not verdicts

A model output is a **candidate**: `provenance.revisionStatus` is exactly
`machine-candidate`, and `reviewedValue`, `reviewer`, `reviewedAt` are `null`.
`reviewStatus` on a review row is a human field. No script may write it from
model output, no matter how confident the model is, and no merge, import or
backfill may promote a candidate implicitly.

The validator enforces this on every committed output row:

```bash
npm run validate-llm-candidate-lane
```

A row that carries `revisionStatus: "reviewed"` or any non-null `reviewed*`
field fails validation and therefore fails any handoff that ships it.

## 2. What may be generated

- One call per row over a **frozen** sample. The H7101 sample is
  `sample-500.jsonl`, sealed by SHA-256 in `manifest.json` and `scores.json`.
- Six prompt designs are frozen in `prompts.json`. Adding a seventh design
  after seeing scores turns the held-out sample into training data.
- Abstention is a first-class output. A row that cannot be judged is
  `abstain: true`, `editType: null`, `span: null`, and it lowers coverage. It
  is never silently turned into a guessing prediction.
- No fine-tuning, no second model in the same evaluation, no full-corpus run
  before a GO decision.

## 3. Provenance that must travel with every candidate

`data/llm-candidate-lane/provenance.schema.json` is the contract:
`sourceRef` (repo, path, commit, dict, L, line, process, batch, or review
id/queue), `inputSha256`, `prompt{id,version,sha256}`, `model{provider,name,
revision,temperature}`, `prediction{editType,span.text,span.start,span.end,
confidence,abstain,rationale}`, and `provenance` as in §1. A row missing any of
these is invalid; a rationale without a span is a candidate that cannot be
reviewed.

## 4. Human adjudication path

A candidate may enter a human review queue only as a **suggestion** attached to
the source line it came from. The reviewer sees the input line, the candidate
label, the rationale span and the model identity, and records their own
decision through the normal review tools. The reviewer is not asked to accept
or reject the model; they decide the row. Two consequences:

- The review tool must never pre-select the candidate value.
- A reviewer may reject every candidate without further justification; there is
  no target acceptance rate.

Inter-rater reliability is computed only over human decisions. Model-vs-gold
kappa is reported separately and is not evidence about human agreement.

## 5. Evaluation bar

A lane is eligible for a GO only when, on the frozen 500 rows:

1. it beats the surface-rule baseline on macro-F1 (abstain counted as wrong);
2. the gain survives the paired bootstrap 95 % CI (the lower bound of the
   difference must be above zero);
3. coverage is reported alongside precision, because a high-precision lane that
   abstains on 80 % of rows is a triage toy, not a priority signal;
4. the same 500 rows are used for model and baseline, with no row dropped.

Current numbers (24-10-2026): baseline macro-F1 0.1284 (95 % CI 0.0977–0.1690),
Cohen's κ vs gold −0.1017 — i.e. the baseline is **worse than chance** on the
five-label task while its any-correction binary (F1 0.9293) is nearly trivial.
The LLM lane produced 500 abstentions (coverage 0), so it has no measured gain.
Krippendorff α is not computable: the sample carries one gold label per row, and
the second independent human key required by H7101 does not exist yet.

## 6. Stopping and reversal

- Stop at the first scored 500-row run. Do not tune on the same sample.
- The reversal condition is named in the GO/NO-GO memo: a credentialed run that
  beats 0.1284 macro-F1 with a positive lower confidence bound on the paired
  difference. That reopens the lane; it does not authorise promotion.
- Revoke the lane if any candidate reaches `reviewed` without a human decision,
  if the sample is changed after scoring, or if a prompt is edited after seeing
  scores.

## 7. Data and cost

Correction text may contain dictionary content, not personal data. Never send
student data, correspondence, credentials or any `stenogrammy/` material to a
model. Spend is capped per handoff (H7101: €5, 500 calls); the runner refuses
to start without credentials rather than fabricating output, and it records the
model revision returned by the provider.

## 8. Where the rules are enforced

| Rule | Enforcement |
|---|---|
| no promotion | `provenance.schema.json` (`const: machine-candidate`, `reviewed*: null`) + `scripts/validate-llm-candidate-lane.mjs` + `test/llm-candidate-lane.test.mjs` |
| frozen sample | SHA-256 in `manifest.json`; re-freeze requires `--freeze` and a new handoff |
| bounded run | `scripts/run-llm-candidate-lane.mjs` (one call per row, cache-aware, credential-gated) |
| honest scoring | `scripts/score-llm-candidate-lane.mjs` (abstain = missing coverage, seeded bootstrap, model-vs-gold kappa) |
| decision record | `docs/H7101_GO_NO_GO_MEMO.md` and `docs/H7101_LLM_CANDIDATE_LANE_REPORT.md` |
