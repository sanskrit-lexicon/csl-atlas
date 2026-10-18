# H4/H5 packet fixtures vs the local `csl-orig` checkout — recorded design note

_Created: 18-10-2026 · Status: known coupling, deliberately unchanged_

This note records BUGHUNT finding 3 from
[BUGHUNT-FINDINGS-csl-atlas-07.10.2026.md](../BUGHUNT-FINDINGS-csl-atlas-07.10.2026.md):
the H5/H4 orchestrator packet tests that regenerate line-pinned `csl-orig` links
from the local sibling checkout can disagree with the committed fixtures by one
line when that checkout is stale.

## Observed

- Tests: `test/orchestrators.test.mjs` (H5 maker QA, H5 maker correction,
  H4 review packet; the three failures noted at hunt time).
- Symptom: a uniform +1 delta on pinned `mw.txt` line numbers (for example
  expected `#L246835`, generated `#L246834`).
- Cause: the local `../csl-orig` checkout was 8 commits behind `origin/main`,
  while the committed fixtures were frozen against a newer revision. CI has no
  sibling checkout, so the source-derived steps skip and the same SHA is green.

## Decision (H7006)

Do not change the fixtures. They are correct against their freeze revision; the
test environment is what moved. This is the same coupling already recorded in
the H5318 changelog entry ("3 pre-existing H4/H5 packet failures on clean main,
local `csl-orig` drift") and is not a regression from the sanskrit-util
re-vendor (finding 1).

## Cure (design-level, not done here)

Pin the `csl-orig` revision used for each fixture-freeze run, the way the
citation re-freeze chain already does, so the source-derived tests either run
against exactly that revision or skip with a named reason. Until then, treat
these three failures as environment, not product, signal.
