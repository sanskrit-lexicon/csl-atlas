- **H5309: review-pool kappa report tool — Cohen's κ between two double-keyed decisions files (24-09-2026, OxAlpha `zai-coding-plan/glm-5.3-flash`).** New
  [scripts/review_pool_kappa.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/review_pool_kappa.py)
  joins two review-sheet decisions.json exports (shared emitter payload: `{sheet_id, items:[{id, decision, note}]}`,
  decision ∈ approve/reject/defer or null) of the same packet on item id and reports raw agreement, Cohen's κ with a
  95% asymptotic-normal CI (Fleiss SE, clipped to [-1, 1]), the confusion table (A rows × B columns) and the
  disagreement rows with both notes for adjudication. Degenerate inputs are reported honestly, never fudged: the
  single-class case (pe = 1) carries `cohenKappa: null` with an explanatory note while raw agreement stands; items
  seen by only one annotator or unvoted by either are excluded from κ and listed under coverage warnings; unknown
  decision values and duplicate ids fail loud (exit 2). 15 stdlib-unittest fixture tests in
  [scripts/test_review_pool_kappa.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/test_review_pool_kappa.py)
  cover the handoff's three required fixtures — perfect agreement (κ = 1, CI [1, 1]), chance level (κ = 0 on a
  balanced 2×2), degenerate single class — plus join/coverage semantics, schema rejection and a CLI end-to-end smoke.
  Run via `npm run review-pool-kappa -- A.json B.json` / `npm run test-review-pool-kappa`. Prior art consumed:
  scripts/lexico/root_agreement_kappa.py (marginal pe, Landis-Koch bands) and csl-observatory obs_t_gold.py (paired
  κ + confusion Counter); schema aligned with scripts/validate_review_decisions.py. Companion to the E014
  review-pool double-keying chain (H5307/H5308) and the H5312/H5313 obs-t second-annotator units.
