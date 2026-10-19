# H7104 — LLM definition + judge evaluation with cross-dictionary gold

_Executed 19-10-2026. Report artifact of [H7104](https://github.com/sanskrit-lexicon/csl-atlas)._

## Outcome

The frozen kosha definition-generation evaluation (H730/H2408) is extended into
a cross-dictionary sense-consistency test on atlas data **without re-running
generation**. The five frozen arms are joined to AP/PWG/PWK/MW sense units from
live `csl-orig/v02` through the committed H7098 sense adapters. The
100-row judge-calibration sample is human-scored and reconciled against the
frozen LLM judge.

Best arm on the primary endpoint: **A2_chat_noctx** — 89.16 % of the sampled
lemmas where another dictionary distinguishes at least two senses get an
adequate multi-sense gloss. The random floor is 0 % once adequacy is required.
Judge-vs-human agreement is high (quadratic weighted kappa 0.9356, n = 100).
Decision: **GO for the candidate lane, NO promotion of generated content**.

## Scope guards

- Generation was **not re-run**. The five frozen arms are consumed read-only.
- No model was trained.
- No generated definition is auto-accepted as dictionary content.
- The bounded 100-item replication was **not executed** (no model credentials in
  this unit); it remains a precondition for any content-promotion decision.
- The 500-lemma H7098 audit is reused at the method level; its committed
  artifacts are not duplicated. Only the 20 lemmas shared with the defgen
  sample overlap directly. This evaluation therefore applies the H7098
  adapters to the live sources rather than copying H7098's 500-row sample.

## Data and provenance

Vendored under `data/eval/crossdict-defgen/` from `gasyoun/kosha`
`data/eval/defgen`:

| Input | SHA-256 |
| --- | --- |
| `frozen_sample.tsv` (500 rows) | `a259df13ac9ca3a778eb221a29c11f6505622c21278bff1d767ca84886aacffc` |
| `frozen_sample.meta.json` | `e1ba3aa0232b5c14c34ac8a5537d7f282405dc2c401974519563d3249558f05c` |
| `generations/gen_A0_random_floor.jsonl` | `975ce9d8b4f3dd3db99d4f2e3b042340fcbfd905496c0282e7b9dffa53c80c89` |
| `generations/gen_A1_chat_ctx.jsonl` | `53727db0a59e76067ac2d0c3f15cd1dacdc8e08e20034ec966af01df939c5866` |
| `generations/gen_A2_chat_noctx.jsonl` | `7d90c0620f866c0bdefb45457063a9b1d3719188be88f39cd733a83ebf5da75b` |
| `generations/gen_A3_reasoner_ctx.jsonl` | `57a35f8982179d5b3f967a23c9b8b97102a9160431442c91b52b5a8eee8495ac` |
| `generations/gen_F1_fable_ctx.jsonl` | `a595dc5462b8677aef42d4774ee3a3a50757a9b570f49981be025af2d8b8829f` |
| `judge/judge_A0_random_floor.jsonl` | `52258f90dfa12f624f20aef186a2777cbb5b94c4a845008762d5dd9181dfd320` |
| `judge/judge_A1_chat_ctx.jsonl` | `bfe8ca9b3143233c03280815e2bade8c8c4d5ff8eb68da8432721912bb274851` |
| `judge/judge_A2_chat_noctx.jsonl` | `8aac837080d84fd90681d62d11c6bfe0957fc65cc71c869b650ee88cd618d3ce` |
| `judge/judge_A3_reasoner_ctx.jsonl` | `2752d534884971608b9cb80e60d3db346935ce16a2377244c75ac816c1025d18` |
| `judge/judge_F1_fable_ctx.jsonl` | `315cbfed98d8a95b48d110385aa254088bed257e4c211b01be2cb5bdfb24fe40` |
| `scores_per_item.tsv` (2500 rows) | `4e1b07b431398b2b891fcf78184fd53ab828ac5c2ecd47004d9fa3f2d0cb2d5f` |
| `scores_summary.json` | `2732153d7dad7b289abb75c6fbe5a7326c432346709ec55467c3bac33fad6715` |

Sense units are recomputed from `../csl-orig/v02/{mw,ap,pwg,pw}` with the
H7098 adapters (`mw-sense-section-div`, `ap-bullet-sense-marker`,
`pwg-div-sense-marker`, `pwk-div-sense-marker`). The script records record and
match counts in `sourceProvenance.senseAudit.availability`.

## Design

- Sample: 500 MW headwords, the frozen defgen sample (seed 730), stratified
  high/mid/low frequency × mono/poly2_4/poly5p.
- Arms: `A0_random_floor`, `A1_chat_ctx`, `A2_chat_noctx`,
  `A3_reasoner_ctx`, `F1_fable_ctx`.
- Cross-dictionary reference: the richest sense-unit count among AP, PWG and
  PWK (`other_max`).
- A lemma is a **cross-dictionary distinction** case when `other_max >= 2`.
- A gloss **preserves** the distinction when it has at least two segments after
  splitting on `|` or `;`.
- Primary endpoint: distinction preservation among glosses whose LLM judge
  adequacy is at least 3. This gate is necessary because a random synonym dump
  can satisfy a raw segment-count threshold; the A0 floor does exactly that.
- Secondary: sense-count F1 against `other_max` (harmonic mean of count
  precision and recall), which penalises both lost distinctions and synonym
  dumps.
- MW-mono gap: MW has at most one sense unit while AP/PWG/PWK reaches at least
  two. This is the sharpest cross-dictionary signal.

## Sense-level coverage

| Quantity | Value |
| --- | ---: |
| Sampled lemmas with any core sense unit | 500 / 500 |
| Lemmas with an AP/PWG/PWK sense unit | 340 / 500 |
| Lemmas where AP/PWG/PWK distinguishes >= 2 senses | 249 / 500 |
| Lemmas where MW is mono but AP/PWG/PWK is poly | 193 / 500 |
| Sampled lemmas where MW records match (multiple entries possible) | 2,122 |

## Cross-dictionary consistency

| Arm | Distinction cases | Raw preserved | Adequacy-gated preserved | MW-mono gap preserved | Mean count F1 | Mean gen segments | Mean judge adequacy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A0 random floor | 249 | 81.93 % | 0.00 % | 81.87 % | 0.5679 | 4.94 | 0.186 |
| A1 chat + context | 249 | 85.14 % | 81.93 % | 84.97 % | 0.6780 | 2.90 | 4.322 |
| **A2 chat, no context** | 249 | **95.18 %** | **89.16 %** | **93.78 %** | 0.6732 | 4.38 | 4.084 |
| A3 reasoner + context | 249 | 57.83 % | 55.82 % | 58.55 % | 0.6151 | 1.80 | 4.208 |
| F1 fable + context | 249 | 78.31 % | 76.71 % | 73.58 % | 0.6660 | 2.20 | 4.600 |

Reading:

- A2 wins the primary endpoint and the MW-mono gap. Its glosses are longer and
  enumerate more distinctions than A1/A3/F1.
- A1 wins the secondary count-F1 by a hair (0.678 vs 0.673); it is the most
  conservative useful arm.
- A3 is the most concise (1.80 segments) and loses distinctions exactly where
  the other dictionaries expect them (55.82 %).
- F1 has the best lexical overlap with MW gold (chrF 30.33) and the highest LLM
  judge score (4.60), but only 76.71 % adequacy-gated preservation. Lexical
  overlap and sense preservation are not the same quantity.
- The random floor shows why adequacy gating matters: it emits synonyms and
  reaches 81.93 % raw segment preservation with 0.186 judge adequacy.

## chrF / BLEU baselines

Frozen from the kosha scorer (`scores_per_item.tsv`); not recomputed here.

| Arm | Mean sentence chrF | Mean sentence BLEU | Mean token F1 |
| --- | ---: | ---: | ---: |
| A0 random floor | 11.82 | 2.05 | 0.0966 |
| A1 chat + context | 24.61 | 5.18 | 0.2966 |
| A2 chat, no context | 22.49 | 4.69 | 0.2935 |
| A3 reasoner + context | 20.48 | 4.08 | 0.2560 |
| F1 fable + context | 30.33 | 6.72 | 0.3401 |

## Judge-vs-human calibration

A deterministic 100-row sample (20 per arm, SHA-256 of `H7104:<arm>:<slp1>`)
was scored blind by the worker on a 0–5 adequacy rubric against the MW gold
gloss and the joined cross-dictionary units. The LLM judge score was hidden
during scoring. Human scores: `judge_calibration_human.tsv`; rubric and sample:
`judge_calibration_sample.csv`, `judge_calibration.json`.

| Statistic | Value |
| --- | ---: |
| n | 100 |
| Exact agreement | 0.650 |
| Within-one agreement | 0.970 |
| Mean human | 3.31 |
| Mean LLM judge | 3.38 |
| Quadratic weighted kappa | **0.9356** |
| Pearson | 0.9412 |
| Spearman | 0.8602 |

Per-arm exact agreement ranges from 0.40 (A1) to 0.95 (A0); within-one
agreement is >= 0.90 in every arm. A0's per-arm kappa is 0 by construction
(the human key is constant 0 and the judge is nearly constant 0), so the pooled
kappa carries the calibration signal. The small A1 exact-agreement figure is
the expected cost of the human key using 3 where the judge says 4 on partially
covered senses; within-one agreement is 1.00.

## MW-contamination caveat

Generation arms A1/A3/F1 saw MW context and A1/F1 were prompted around MW
material; all LLM judges saw MW gold. Therefore:

- MW-gold BLEU/chrF and LLM-judge adequacy are **contaminated by construction**
  and cannot be used alone as evidence of definition quality.
- The cross-dictionary endpoint is the least contaminated, but AP/PWG/PWK share
  historical material, citation stock and some editorial lineage with MW.
  Independence is partial, not absolute.
- The cross-dictionary units are structural marker counts, not curated sense
  inventories. A match in count is not a match in meaning.
- The 100-row human key is one key, not two blind keys plus adjudication. It is
  enough to calibrate the judge, not enough to certify the definitions.

## Reproduction

```bash
# csl-orig must be a sibling of the repository root (../csl-orig/v02)
npm run build-crossdict-defgen-eval
node --test test/crossdict-defgen-eval.test.mjs
```

`npm run build-crossdict-defgen-eval -- --reset-calibration` redraws the
100-row sample; without the flag the committed sample and human key are
preserved.

## Files

- `data/eval/crossdict-defgen/` — frozen inputs, sense join, per-item scores,
  calibration.
- `scripts/build-crossdict-defgen-eval.mjs` — builder.
- `test/crossdict-defgen-eval.test.mjs` — nine invariant tests.
- `docs/H7104_GO_NO_GO_MEMO.md` — decision memo.

## What this does not prove

The lane shows that the best frozen arm preserves cross-dictionary sense
distinctions more often than a random floor and that the LLM judge tracks a
human key. It does not show that any generated gloss is a correct dictionary
definition. Promotion requires a bounded 100-item replication and two blind
human keys with source-line adjudication.
