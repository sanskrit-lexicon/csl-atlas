# A10 "Apparatus, not errors" — reproducibility audit

_Created: 03-07-2026 · Last updated: 22-09-2026_

Data-verification pass over [`docs/articles/article_21_apparatus_not_errors.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md)
(A10), checking every headline figure against the committed forensic artifacts and,
where an artifact was absent, against a faithful reconstruction from the same inputs.
**Verdict (updated 2026-07-03): all six signals — including both decisive ones (F4b
shared-error, F5 citation-order) — reproduce to the digit. §3.1's size-corrected
rare-lemma containment ratios were unreproducible at first pass (their generator was not
yet in the repo), but the generator + output have since been migrated in from
`csl-observatory` (commit `0b73b97`) and now regenerate byte-identically and match the
published ratios exactly — see the §3.1 section below.**

## Reproduces exactly (committed artifact → paper)

Values below are the committed artifacts at the `csl-orig@f4c08c57` pin (H5248 for F1/F5,
H5260 for F2–F4b/F8, 22-09-2026); the first-pass (03-07-2026) values are kept in
brackets where the pin moved them. The article was updated to the pinned values the same pass.

| Paper § | Signal | Paper claim | Committed value | Source |
|---|---|---|---|---|
| §3.1 | MW∩PW-only headwords | 17,007 | **17,007** | `csl-observatory/observatory/snapshots/sanhw1.txt` (df=2, {MW,PW}) |
| §3.2 | F1 citation source-Jaccard | PWG/PW 0.16–0.18; nulls 0.004–0.016 | PWG→MW **0.1579** [0.1594], PW→MW **0.1791** [0.1875]; BHS **0.0038**, AP **0.0163** [0.0168] | [`f1_report.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f1_report.json) |
| §3.4 | F5 citation-order concordance | PWG 0.811 / 47.7% identical; PW 0.73; BEN 0.70; AP 0.42 | PWG **0.8108** / **47.7%** (n=3,583) [0.8107 / 47.8%, n=3,593]; PW **0.7303**; BEN **0.7045** on 116 [0.677 on 154]; AP **0.4167** | [`f5_report.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f5_report.json) |
| §4.1–4.2 | F4b decisive shared-error | 2/123 (1.6%); null 260 vs 103.3, lift 2.52, p≈1.5×10⁻⁴² | **2/123**, 90 correct, 31 absent; null **260** vs **103.31**, lift **2.517**, p **1.49×10⁻⁴²** [256 vs 102.79, 2.491, 4.01×10⁻⁴¹] | [`f4b_report.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f4b_report.json) |
| §4.3 | F3 gloss-length tracking | PWG 0.564 vs AP 0.576 (Δ −0.01) | PWG→MW **0.5641** [0.5636], AP→MW **0.5763** [0.5757] | [`f3_report.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f3_report.json) |
| §4.3 | F6 gloss DE→EN overlap | ALL .104/.129, VERB .044/.098, PHIL .086/.086 | ALL **.1042/.1289**, VERB **.0445/.0979**, PHIL **.086/.0858** | [`f6_report.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f6_report.json) |

The paper's two **decisive** claims — that MW shares ≈0 % of Böhtlingk's mechanical
errors (F4b) and that it reproduced Böhtlingk's citation *order* (F5) — are the ones
that reproduce most cleanly. The forensic case for "heir of the scholarship, author of
the prose" stands on committed, reproducing data.

## RESOLVED (2026-07-03) — §3.1 now reproduces exactly

The paper's §3.1 reports **size-corrected** rare-lemma containment: PWG→MW 0.70 (df≤3) /
0.82 (df≤5), PW→MW 0.71, MW72→MW 0.57, against unrelated BOP→MW 0.35.

When this audit first ran, the generator `scripts/L0/s6_content_lift.py` and its output
`data/L0/content_lift.csv` were **both absent** from `csl-atlas`, so §3.1 could not be
independently checked. Commit `0b73b97` ("L0: migrate the convention-genealogy stream
from csl-observatory") has since **restored both** — the script had lived in
`csl-observatory` all along. The gap is closed:

- `data/L0/content_lift.csv` is committed, and its `rare_cont_3` / `rare_cont_5` columns
  give the paper's ratios **to the digit**: PWG→MW **0.6966 / 0.8153** (paper 0.70 / 0.82),
  PW→MW **0.7125** (0.71, df≤3), MW72→MW **0.5666** (0.57, df≤3), BOP→MW **0.3524** (0.35,
  df≤3). The `excl_pair` column reproduces the 17,007 MW∩PW-only count on the PW→MW row.
- Re-running `python scripts/L0/s6_content_lift.py` regenerates `content_lift.csv`
  **byte-identically** (verified 2026-07-03).
- The method (from the script's own docstring) is the two-instrument L0.8 ladder: a size
  **lift** `|A∩B|·N/(|A|·|B|)` plus **rare-lemma containment** — restrict to A's lemmas with
  corpus document-frequency df ≤ k and ask what fraction recur in B. My earlier
  reconstruction landed 0.75–0.85 (not 0.70–0.82) because it approximated the df universe;
  the committed script's exact dict set reproduces the published gradient, including the
  discriminating BOP→MW 0.35.

The one residual dependency is the **input snapshot** `observatory/snapshots/sanhw1.txt`,
which is owned by `csl-observatory` (a sibling repo), not duplicated into `csl-atlas` — the
same cross-repo-input pattern as the `../csl-orig` forensic readers. The committed
`content_lift.csv` is the walkable artifact; regeneration needs the sibling snapshot.

**All six A10 signals now reproduce.** No paper change is required for the numbers
(they were always correct); §7 correctly names `scripts/L0/s6_content_lift.py`, which is
now present. Optional polish: add a one-line data-pointer in §3.1 to
`data/L0/content_lift.csv` for the same Claim→Evidence→Source walkability the other
signals have.

## Re-pinned 22-09-2026 — F2, F3, F4, F4b and F8 (H5260)

The H5248 pin (`scripts/forensic/_corpus_pin.py`) now covers every forensic writer that reads
`csl-orig`. Cache readers (F2 over all 45 caches, F4b) verify `_parse_provenance.json`; live
readers (F3, F8 census/resolve/quote lane/Droṇa, F7 resolve) pin the clean checkout before and
after; derived-table readers (F8 presence, F8 verify, F7's pool) inherit the upstream sidecar's pin
and refuse an unpinned or mixed one. F4 reads no `csl-orig` file, so its sidecar records
`csl_orig.read = false` and pins `PWG/pwgissues` + `csl-corrections` under `inputs`. A mode-only
flip on a tracked file (a hook installer's `chmod`) is not counted as dirt; a content edit is.

1. Re-run here at `f4c08c57`, byte-identical under `PYTHONHASHSEED=1` and `=2`: F2, F3, F4, F4b,
   F8 census. Moved: the F4b null (above), F4 corrected-in-both headwords 268 → 272 (still ≈ chance),
   F2 raw MW+Petersburg pool 18,025 → 17,918, F3 BEN→MW 0.259 → 0.134 on 15,947 → 22,699 lemmas
   (BEN is not cited by the article). No A10 verdict changes.
2. §6 DCS arm, re-run against the 598-row pool (`F4_CAND=data/forensic/shared_rare_citations.csv
   F4_REPORTS=<tmp> python3 ../VisualDCS/src/DCS-data-2026/dcs_shared_citation_errors.py`):
   598 candidates, 567 with a DCS text (570 in June), **1** locus-resolved — the same
   `CAURAP. (A.) 49`; 293 Harivaṃśa numbers exceed DCS's 6,073 verses (298 in June).
3. **Correction to §7's earlier "Harivaṃśa unchanged at 565".** The count is unchanged but the
   membership is not: 49 of the June 565 `HARIV.` rows left the pool and 49 others entered it
   (upstream corrections to the citation text or to its corpus frequency; not itemised here). The §6 vulgate arm (F7: 206/565 corroborated) is therefore a June-membership
   figure; it was not re-run because its verse witness (`_harivamsa_verses.jsonl`, rights-restricted,
   gitignored) is absent on the box that ran this pass. Same for the F8 stages that read the MBh
   vulgate/critical witnesses — their committed sidecars stay unpinned until that re-run.

## External-evidence gate (unchanged, out of scope)

§6's "one remaining decisive test" — a shared *erroneous* citation verified against the
DCS/VisualDCS corpus — remains outside `csl-atlas` per the boundary rules, and is not
part of this audit.

_Dr. Mārcis Gasūns_
