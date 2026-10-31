_Created: 31-10-2026 · Last updated: 31-10-2026_

# data/mw_vs_pw — MW missing-entries scan vs PWG/pwk (H7513)

Row-level substrate of
[MW_VS_PW_MISSING_ENTRIES_SCAN_2026-10-31.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/MW_VS_PW_MISSING_ENTRIES_SCAN_2026-10-31.md).
Every published number regenerates from the committed TSV + JSON under
[mw_vs_pw_check.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/mw_vs_pw_check.py)
(exit non-zero on drift); pins in
[test_mw_vs_pw_missing.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_mw_vs_pw_missing.py).

The two-class candidate list answering KnbRao's csl-corrections #119 proposal:

| Class | Meaning | Count |
|---|---|---|
| `a_missing_by_error` | PWG/pwk cite it, MW lacks it (or has it under a form that no longer resolves — `form_unresolved_stem` / `form_unresolved_nearform` review subclasses) | 19,465 |
| `b_expected_absence` | MW lacks it AND PWG/pwk never cite it (derivative entries) | 6,245 |

Denominator for both classes: **157,994** = |distinct base k1 headwords in
PWG ∪ pwk| (pwk = `pw` + `pwkvn`), of which 132,284 resolve verbatim in MW.

| File | Contents |
|---|---|
| `mw_missing_candidates.tsv` | the 25,710-row two-class candidate list, keyed to evidence (source file, `<L>`-header line, L/pc/k1, first `<ls>` payload) + MW resolution tier + 39-dictionary corroboration |
| `mw_vs_pw_metrics.json` | every published number incl. per-source denominators and the kAritra canary |
| `substrate_pins.json` | sha256 of mw/pwg/pw/pwkvn machine texts + the 39 corroboration dictionaries; pwg.txt pinned to the H7463 Stage-1 sha (`430c910f…`, shared with `data/pwg_dcs/pwg_substrate_pins.json`) |

Builder: `scripts/mw_vs_pw_missing_build.py` (stdlib, deterministic, ~5 min;
refuses to run if pwg.txt drifts off the H7463 pin). Machine texts live
off-git in csl-orig and are never committed.

_Dr. Mārcis Gasūns_
