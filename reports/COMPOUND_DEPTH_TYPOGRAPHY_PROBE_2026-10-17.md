# Compound depth is not (only) typography — Dharmamitra ByT5 probe

_Generated 2026-10-17 by `scripts/probe-compound-depth-privative.py` (Dharmamitra ByT5 `unsandhied`, remote API). Model output is review evidence, not a build input._

## Why this probe

The atlas counts compound members from MW markup. A **strict** bracket counts only em-dash-separated members; a **loose** bracket also lets a privative hyphen (`a-dharma`) contribute a member. This probe asks the independent segmenter whether single-hyphen privatives are two-member compounds (strict stands) or 3+ members (loose bracket applies).

**Decision rule (the brief's):** p3>=0.50 LOOSE; else STRICT (p2 reported as corroboration).

## Populations

| | definition | records | distinct surfaces |
|---|---|---:|---:|
| A | `<k2>` with ≥2 em dashes (3+ members) | 8,638 | 8,394 |
| B | single-hyphen privative (`a-`/`an-`, no other marker) | 6,096 | 4,032 |

B was read on a stratified sample (stem-initial strata, proportional allocation, n = 1,000, seed 20261017) and then on the full frame.

## The bracket arithmetic

| bracket | numerator | denominator | share |
|---|---:|---:|---:|
| strict (em-dash 3+) | 8,638 | 127,528 em-dash entries | 6.8% |
| loose (any marker, 3+) | 30,703 | 182,003 marker entries | 16.9% |
| loose + every single-hyphen privative counted a member | 36,799 | 182,003 marker entries | 20.2% |

The 7 % anchor reproduces exactly (6.8 % of em-dash entries). But the quoted pair also changes denominator: 6.8 % is of em-dash entries, 16.9 % is of *all* marker entries. On one basis the gap is smaller:

| basis | strict | loose |
|---|---:|---:|
| all marker entries (182,003) | 8,638 (4.7 %) | 30,703 (16.9%) |
| em-dash entries (127,528) | 8,638 (6.8 %) | 30,703 (24.1%) |

A 20.2 % figure appears only if the loose bracket adds **all 6,096** single-hyphen privatives to the 3+ numerator (36,799 / 182,003). That is the step this probe tests: p3 is the share of those privatives that actually parse as 3+ members, so the defensible loose count is `30,703 + p3 × 6,096`, not 36,799. If the brief's 20 % came from some other denominator, the surviving conclusion is unchanged — see the decision below, which does not depend on the 20 % arithmetic.

## Coverage

| population | rows | valid | valid rate | empty | truncated | garbage |
|---|---:|---:|---:|---:|---:|---:|
| A | 8,394 | 5,489 | 65.4 % | 712 | 1,273 | 920 |
| B sample | 1,000 | 692 | 69.2 % | 30 | 163 | 115 |
| B full | 4,032 | 2,713 | 67.3 % | 155 | 694 | 470 |

`truncated` = the model returned only the tail of the compound (first member dropped); `empty` = underscores/no output. Both are model failures, left null, never scored.

## Result 1 — the privative branch (B)

| read | valid | 1 token | 2 tokens | 3+ tokens | p3 (95 % CI) | verdict |
|---|---:|---:|---:|---:|---|---|
| sample | 692 | 75.0% | 23.5% | 1.5% | 1.5% (0.8%–2.6%) | STRICT |
| full frame | 2,713 | 75.6% | 22.9% | 1.5% | 1.5% (1.1%–2.0%) | STRICT |

**Verdict: STRICT.** The loose trigger fails: the model almost never splits these privatives to 3+ members, so the strict figure stands.

### Decision under the brief's rule

The brief's trigger for the loose bracket is 'they split to 3+'. They do not: p3 = 1.5% (95 % CI 1.1%–2.0%), 48.5 points below the 50 % threshold. **The strict figure stands.**

Hand audit of the 41 three-plus outputs: roughly two thirds are genuine `a + compound-stem` parses (`a-danta-āghātin`, `an-āplutā-aṅga`, `a-māṃsa-aśana`); the rest duplicate the privative (`a_a_bahu`) or split a simplex (`a_vṛ_jina`). Even the most generous count leaves p3 at 1.5 %; the defensible range is 0.9–1.5 %.

The support for that call is asymmetric and must be stated: the model **rejects the third member** decisively, but it does not positively affirm the two-member reading either — it returns one token for three quarters of the privatives, i.e. it treats `a-` as a bound prefix. What the probe settles is the loose bracket's licence to count a privative as deepening the compound; that licence is absent.

## Result 2 — the strict population (A)

| model vs markup | rows | share of valid |
|---|---:|---:|
| agrees (model = markup) | 1,782 | 32.5 % |
| model splits fewer | 3,588 | 65.4 % |
| model splits more | 119 | 2.2 % |


**Markup-3 breakdown (n = 4,488):**

| markup-3 read | rows | share |
|---|---:|---:|
| of markup-3 rows: model = 1 | 745 | 16.6 % |
| of markup-3 rows: model = 2 | 2,121 | 47.3 % |
| of markup-3 rows: model = 3 | 1,544 | 34.4 % |
| of markup-3 rows: model >= 4 | 78 | 1.7 % |

Disagreement here is a separate bias from the hyphen question, and it points the other way. When the model reads a 3-em-dash entry as 2 members it treats the first two markup members as one lexicalised compound — `agni—zwoma—yAjin` → `agniṣṭoma_yājin`, `agni—hotra—sTAlI` → `agnihotra_sthālī`. That is the dominant mode: 47 % of valid markup-3 rows parse as 2, against 34 % that parse as 3. So the strict numerator counts **every internal joint**, not immediate constituents; if 'depth' means the latter, 8,638 is an upper bound. The strict figure survives the hyphen test and still fails a constituency test it was never designed to pass.

## Local replication (robustness)

The remote API's failure rate is mostly an **endpoint** artifact, not the model's. A deterministic slice (80 A + 80 B rows) re-run on the pinned local HF model (`chronbmm/sanskrit5-multitask@c0d2ada54f3d`) gives:

| slice | API valid | local valid | local 1 / 2 / 3+ | local p3 (95 % CI) |
|---|---:|---:|---|---|
| A | 65.4% | 74/80 (92.5%) | 18 / 33 / 23 | — |
| B | 67.3% | 80/80 (100.0%) | 50 / 25 / 5 | 6.2% (2.7%–13.8%) |

Agreement on the 116 rows valid in both runs: 92 (79.3%). The local model over-splits some simplexes (`akaca` → `a_ka_ca`, `akali` → `a_ka_li`), so its 6.2 % is itself an over-count: a hand audit leaves 2 genuine `a + compound-stem` parses in 80 (`a-karṇa-dhāra`, `a-karmānvita`), i.e. ~2.5–3.8 %.

**The verdict does not move.** Even the local upper bound (13.8 %) is 36 points below the loose trigger. What changes is the confidence in the coverage caveat: the model is clean on these inputs; the API is not.

## Caveats

- Remote-API coverage is 65.4% (A) / 67.3% (B full): the endpoint truncates or empties on a substantial minority of out-of-sentence compounds. The local replication (92.5 % / 100 %) shows this is an endpoint artifact, not a model limit. Rates are among valid rows only.
- The API is not reproducible; a pinned local HF revision is the reproducible path (`--source local`).
- The model is trained on running text; a bare compound is out of distribution, so disagreement is a flag, not a linguistic verdict.

## Provenance

- Model: Dharmamitra ByT5-Sanskrit analyzer (unsandhied)
- Mode: `unsandhied`
- Endpoint/revision: `https://dharmamitra.org/api/tagging/`
- Snapshot: `data/compound-depth/typography-probe-2026-10-17.json`
- Raw rows: 12,426
- Local replication: `data/compound-depth/local-replication-2026-10-17.json`
