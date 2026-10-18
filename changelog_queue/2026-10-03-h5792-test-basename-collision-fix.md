- **H5792: duplicate test basename unblock — `scripts/lexico/test_review_pool_kappa.py` renamed so `pytest` collects all 178 tests again (03-10-2026, OxAlpha `zai-individual-coding-plan/glm-5.3`).**
  [scripts/lexico/test_lexico_review_pool_kappa.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/test_lexico_review_pool_kappa.py)
  is the renamed file (was `scripts/lexico/test_review_pool_kappa.py`, H5483, 25-09-2026): it had introduced a
  second `test_review_pool_kappa.py` basename into a repo with no test
  packaging (`__init__.py` exists only under `scripts/L0/`), so bare `python3 -m pytest` from the root hit
  pytest's import-file-mismatch after 162 collected tests and aborted — CI never noticed because
  [test.yml](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/.github/workflows/test.yml) scopes pytest
  to `tests/forensic`. The newcomer yields to the H5309 incumbent
  ([scripts/test_review_pool_kappa.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/test_review_pool_kappa.py),
  24-09-2026); the new name's `lexico` prefix follows the directory's `validate_lexico.py` naming. Test content
  unchanged — both
  kappa test files load their sibling module via location-relative `importlib`, so no import edits were needed.
  References updated: [scripts/verify.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/verify.mjs)
  (`scripts.lexico.test_lexico_review_pool_kappa`) and
  [package.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/package.json) — the rename also fixed a
  latent duplicate JSON key: `test-review-pool-kappa` was declared twice (npm's last-wins parsing silently ran
  only the top-level module); the lexico entry now lives as its own `test-review-pool-kappa-lexico` key.
  Receipts: `python3 -m pytest --collect-only -q` → 178 tests collected, 0 errors (before: 162 collected,
  1 collection error, interrupted); `find -name 'test_*.py' -exec basename {} \; | sort | uniq -d` → empty;
  full suite `python3 -m pytest -q` → 178 passed (0 pre-existing reds: pristine origin/main baseline was green
  with the collision file ignored, 163 passed, plus 15 lexico tests via unittest). Closes H5792.
