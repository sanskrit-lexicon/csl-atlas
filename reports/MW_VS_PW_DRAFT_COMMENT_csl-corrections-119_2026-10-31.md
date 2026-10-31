# DRAFT comment for csl-corrections #119 — for MG's review, NOT posted

_Created: 31-10-2026 · H7513. Executor does not post; MG reviews, edits and
posts at his judgement. Voice: gasyoun reply in the #119 thread, answering
KnbRao's "Can AI be put to try-out this?" (14-09) at full-inventory scope._

---

The full-inventory version of the comparison you proposed is now run: every
headword of PWG and of the kürzerer-Fassung digitization (`pw` + its
Nachträge `pwkvn`) checked against MW's complete headword inventory —
25,710 candidates where MW lacks the verbatim form, split by whether
Böhtlingk actually *cites* the word:

- **19,465 missing-by-error candidates** — PWG/pwk carry ≥1 textual citation
  (`<ls>`) under the headword and MW lacks it or keeps it only under a form
  that no longer resolves (stem / near-form review tiers). 5,021 have no MW
  neighbour at all; **897 of those are corroborated by ≥2 of 39 further
  Cologne dictionaries** — the natural scan-adjudication queue.
- **6,245 expected absences** — MW lacks them *and* PWG/pwk never cite them
  (cross-references, re-spellings, gloss-only stubs): no by-error evidence.

Denominator, stated for both classes: 157,994 distinct base headwords in
PWG ∪ pwk, of which 132,284 (83.7 %) resolve verbatim in MW. Per source:
PWG 11,298 candidates (10,373 cited / 925 uncited), pwk-union 22,338
(16,556 / 5,782 in `pw`; 4,332 / 905 in the Nachträge).

`kāritra` reproduces end-to-end and is pinned as the canary: PW 7-331-d /
Nachträge (Mahāvy. 245, 844, = ceṣṭita), zero occurrences in mw.txt, nearest
MW form `kārita` at 0.92 — which is precisely why near-form rows ship as
review flags, not matches.

Everything regenerates from committed row-level data (each candidate keyed to
file, line, L/pc/k1 and first citation payload) under a drift check that
exits non-zero:

- report: `reports/MW_VS_PW_MISSING_ENTRIES_SCAN_2026-10-31.md` (csl-atlas)
- candidate list: `data/mw_vs_pw/mw_missing_candidates.tsv` (25,710 rows)
- check: `python scripts/mw_vs_pw_check.py` · pins: `tests/forensic/test_mw_vs_pw_missing.py`

Caveats kept on the record: absence from MW is not automatically MW error
(class (a) is an adjudication worklist, not an auto-correction batch);
near-form/stem tiers need human eyes (`kāritra`~`kārita` is the trap the
canary pins); the join is spelling-level SLP1 with homonym numbers collapsed;
"Böhtlingk cites it" means ≥1 `<ls>` tag with payload, an entry-level rule
coarser than quotation-unit linking.

This widens the 14-09 Nachträge trial (`issues/issue119/` here;
SanskritLexicography/HeadwordLists) from the 13 k `sup_7` rows to the whole
PWG/pwk inventory, and cross-pins the PWG machine text to the PWG↔DCS Stage-1
substrate (same sha) so the two corpus jobs stay on one substrate.
