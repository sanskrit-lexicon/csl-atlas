# A10 "Apparatus, not errors" — reproducibility audit

_Created: 03-07-2026 · Last updated: 03-07-2026_

Data-verification pass over [`docs/articles/article_21_apparatus_not_errors.md`](articles/article_21_apparatus_not_errors.md)
(A10), checking every headline figure against the committed forensic artifacts and,
where an artifact was absent, against a faithful reconstruction from the same inputs.
**Verdict: five of the six signals — including both decisive ones (F4b shared-error,
F5 citation-order) — reproduce to the digit. One signal, §3.1's size-corrected
rare-lemma containment ratios, is currently unreproducible: its generator was never
committed.**

## Reproduces exactly (committed artifact → paper)

| Paper § | Signal | Paper claim | Committed value | Source |
|---|---|---|---|---|
| §3.1 | MW∩PW-only headwords | 17,007 | **17,007** | `csl-observatory/observatory/snapshots/sanhw1.txt` (df=2, {MW,PW}) |
| §3.2 | F1 citation source-Jaccard | PWG/PW 0.16–0.19; nulls 0.004–0.017 | PWG→MW **0.1594**, PW→MW **0.1875**; BHS **0.0038**, AP **0.0168** | [`f1_report.json`](../data/forensic/f1_report.json) |
| §3.4 | F5 citation-order concordance | PWG 0.811 / 47.8% identical; PW 0.73; BEN 0.68; AP 0.42 | PWG **0.8107** / **47.8%** (n=3,593); PW **0.7303**; BEN **0.677**; AP **0.4167** | [`f5_report.json`](../data/forensic/f5_report.json) |
| §4.1 | F4b decisive shared-error | 2/123 (1.6%); null 256 vs 102.8, lift 2.49, p≈4×10⁻⁴¹ | **2/123**, 90 correct, 31 absent; null **256** vs **102.79**, lift **2.491**, p **4.01×10⁻⁴¹** | [`f4b_report.json`](../data/forensic/f4b_report.json) |
| §4.3 | F3 gloss-length tracking | PWG 0.564 vs AP 0.576 (Δ −0.01) | PWG→MW **0.5636**, AP→MW **0.5757** | [`f3_report.json`](../data/forensic/f3_report.json) |
| §4.3 | F6 gloss DE→EN overlap | ALL .104/.129, VERB .044/.098, PHIL .086/.086 | ALL **.1042/.1289**, VERB **.0445/.0979**, PHIL **.086/.0858** | [`f6_report.json`](../data/forensic/f6_report.json) |

The paper's two **decisive** claims — that MW shares ≈0 % of Böhtlingk's mechanical
errors (F4b) and that it reproduced Böhtlingk's citation *order* (F5) — are the ones
that reproduce most cleanly. The forensic case for "heir of the scholarship, author of
the prose" stands on committed, reproducing data.

## Does NOT reproduce — §3.1 rare-lemma containment ratios

The paper's §3.1 reports **size-corrected** rare-lemma containment: PWG→MW 0.70 (df≤3) /
0.82 (df≤5), PW→MW 0.71, MW72→MW 0.57, against unrelated BOP→MW 0.35. §7 states these
"regenerate from … `scripts/L0/s6_content_lift.py`."

**That script was never committed** (empty `git log --all -- scripts/L0/s6_content_lift.py`)
and its output `data/L0/content_lift.csv` is absent; `scripts/L0/` holds only
`_provenance.py`. A faithful reconstruction from the same `sanhw1.txt` snapshot
reproduces the *count* claim (17,007 MW∩PW-only, exact) but **no natural definition of
"rare-lemma containment" reproduces the published ratios** — every variant tried
(df window 2–3/2–5; excluding the source and/or MW from the df count) yields
PWG→MW ≈0.75–0.85, MW72→MW ≈0.79–0.88, BOP→MW ≈0.58–0.70, i.e. a *compressed, wrongly
ordered* gradient (the paper's discriminating BOP→MW 0.35 and MW72→MW 0.57 never appear).
The published numbers therefore encode a size-correction the prose does not fully specify,
and which is not recoverable without the original script.

This is **not a refutation** — §3.1 is a *corroborating* signal, and the descent case is
carried by the decisive F4b/F5 (both reproducing). But as it stands the §7 reproducibility
claim is false for §3.1, and the five headline ratios cannot be independently checked.

## Recommended author action (before submission)

1. **Recover `scripts/L0/s6_content_lift.py`** from wherever it was run (author's local
   tree / another repo) and commit it plus `data/L0/content_lift.csv`; OR
2. **Recompute §3.1** with a committed generator and update the five ratios to whatever
   the reproducible method yields; OR
3. **Down-weight §3.1** to the reproducible count claim (17,007) and drop the
   unverifiable ratios, leaning §3.1 on the size-corrected *lift* language already used
   elsewhere.
4. Either way, correct §7 so it lists only committed generators.

## External-evidence gate (unchanged, out of scope)

§6's "one remaining decisive test" — a shared *erroneous* citation verified against the
DCS/VisualDCS corpus — remains outside `csl-atlas` per the boundary rules, and is not
part of this audit.

_Dr. Mārcis Gasūns_
