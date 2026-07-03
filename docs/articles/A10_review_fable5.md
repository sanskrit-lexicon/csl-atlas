# A10 (Apparatus, not errors) — Hostile Pre-Submission Review

_Created: 03-07-2026 · Last updated: 03-07-2026_

**Paper:** [docs/articles/article_21_apparatus_not_errors.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md)
**Reviewer:** Fable 5 (`claude-fable-5`), adversarial referee pass in the A01/A03–A06 mold; four parallel `fact-check-against-source` verification agents (also Fable 5, `claude-fable-5`), one per claim family (§3.1 inventory / §3.2 citations / §3.3–3.4 structure / §4 errors + §5).
**Prior audit:** [A10_REPRODUCIBILITY_AUDIT.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/A10_REPRODUCIBILITY_AUDIT.md) (all six signals reproduce; §3.1 resolved via [PR #202](https://github.com/sanskrit-lexicon/csl-atlas/pull/202)).
**Verdict: MINOR-to-MAJOR REVISION → all agent-doable findings fixed same pass.** The paper's two decisive results (F4b shared-error ≈0%, F5 citation-order 0.811) verify exactly and the core argument survives hostile scrutiny intact. But the abstract overstated its corpus and its headline percentage, §3.2's "nowhere else in the corpus" was false for 65% of the 587 rows, §5 quoted stale bootstrap figures contradicted by the committed CSV, and the paper had **no References section and zero external citations** — each independently a desk-reject trigger at DSH/JCA.

---

## 1. Figure re-verification

Four fact-check agents recomputed every table figure and in-text number against the committed artifacts ([content_lift_report.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/L0/content_lift_report.json), [f1](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f1_report.json)/[f2](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f2_report.json)/[f3](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f3_report.json)/[f4b](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f4b_report.json)/[f5](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f5_report.json)/[f6](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f6_report.json) reports, [shared_rare_citations.csv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/shared_rare_citations.csv), [homonym_concordance.csv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/homonym_concordance.csv), [ahlborn_mw_comparison.csv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/ahlborn_mw_comparison.csv), [bootstrap_support.csv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/L0/bootstrap_support.csv)).

**Confirmed exact:** rare-lemma containments 0.70/0.82/0.71/0.57/0.35; BOP raw containment 0.94 (corpus maximum); MW 194,084 lemmas; 17,007 MW∩PW-only; F1 lineage Jaccards 0.1594/0.1875 and null endpoints 0.0038/0.0168; 587 shared rare refs; 565 HARIV rows incl. `HARIV. 9529`; all three worked examples (`ullApya`, `dAsatA`, `granTakAra` — each corpus-unique); 41,552 truncations (direction correct); homonym 65/64/77% vs nulls 32–36%, ceiling 81.5%; F5 n=3,593, 0.8107, 47.8%, gradient 0.81/0.73/0.68/0.42; F4b 2/123 (`asUya/asUy`, `vara/var`), 90 correct / 31 absent, null 256 vs 102.79, lift 2.491, p 4.01×10⁻⁴¹; zero shared print errors (24/122 records); F3 Spearman 0.5636/0.5757; F6 all six stratum values.

**Failed verification (fixed):** see M2–M5 below.

## 2. Major findings

**M1 — No References section, zero external citations.** The paper invoked the Lachmann common-error principle, Buddhist Hybrid Sanskrit, a scholar-curated error list, and four named dictionaries with no bibliography of any kind. Instant desk-reject at DSH or *Cultural Analytics*. *Fix (applied):* References section added with only **verified** canonical works — Maas 1958 + West 1973 (common-error principle), Andrews & Macé 2013 (digital stemmatology, the series' settled anchor from A03/A05), Edgerton 1953 (BHS), the five dictionary editions (PWG, PW, MW72, MW, Apte, Benfey), the CDSL portal, the Ahlborn dataset, and the companion redundancy study; in-text citations wired at the Lachmann, BHS, and 89–94% anchors. Per the A33/A37 discipline, nothing was cited that could not be verified as real and on-topic.

**M2 — §3.2's "occur nowhere else in the corpus" was false for 65% of the 587 rows.** The dataset's criterion is rarity (`corpus_lemmas_with_ref` ≤ 4), not uniqueness: distribution {1: 203, 2: 181, 3: 118, 4: 85} in [shared_rare_citations.csv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/shared_rare_citations.csv). A referee who opens the CSV catches it immediately, and it sits on the paper's second-strongest signal. The three worked examples happen to all be uniqueness-1 — cherry-consistent while the blanket claim was not. *Fix (applied):* "each attested at ≤4 lemmas corpus-wide, 203 of them occurring nowhere else in the corpus at all"; examples marked as corpus-unique.

**M3 — Abstract's corpus and signal count were unsupported.** "Five language-neutral signals across 43 digitised dictionaries": no committed dataset uses 43 dicts (inventory ladder n_dicts = 41; citation analysis 13 tagged dicts; fingerprints 35), contradicting the paper's own §3.1 ("41 dicts"); and the method table lists six signals plus the error list, not five. *Fix (applied):* "six language-neutral signals calibrated across 41 digitised dictionaries plus a scholar-curated error list".

**M4 — §5 quoted stale bootstrap figures contradicted by the committed CSV.** "Convention bootstrap 0.02 vs formatting-lineage edges 0.70–0.81" vs [bootstrap_support.csv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/L0/bootstrap_support.csv): PWG→MW consensus support **0.013**, and the formatting-lineage edges span **0.58–0.81** (PWG→SCH 0.676 sits *below* the claimed 0.70 floor). The same stale pair also sits in [paper_H_convention_vs_content_lineage.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_H_convention_vs_content_lineage.md) and [L0_RESULTS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/L0_RESULTS.md) — left untouched here deliberately: Paper H is A11's manuscript and its own review pass (S13 per the Fable index) must re-verify its full figure set coherently, not receive one patched number from a different run. Queued as an explicit A11 review item. *Fix (applied in A10):* 0.013 / 0.58–0.81, with the CSV named in-line.

**M5 — Abstract's "~98% of curated cases" hid the denominator.** 98% holds only over the 92 cases where MW enters the word (90/92 = 97.8%); over all 123 curated cases it is 73.2% (MW lacks the word in 31). The §4.1 body was phrased correctly; the abstract was not. *Fix (applied):* "where MW enters the word at all … (90/92; it lacks the word in the remaining 31 of 123)".

## 3. Minor findings

**m1 — Favorable-rounding pattern in §3.2.** SCH/PW 0.6249 printed as "0.63", AP/AP90 0.7648 as "0.77", and "10–40×" where the quoted endpoint values yield 9.5–49×. Each small; together they read as motivated rounding. *Fix (applied):* 0.62, 0.76, "9.5–49×".

**m2 — Null range silently dropped inconvenient middle values.** BEN/MW 0.1012 is bucketed under `nulls` in [f1_report.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f1_report.json) yet fell outside the quoted "0.004–0.017"; GRA 0.043 and LRV 0.023 also exceed it. *Fix (applied):* nulls named explicitly (BHS, Apte), and the intermediates turned into corroboration — Benfey's intermediate Jaccard is consistent with its Petersburg exposure, which §3.4's order gradient independently shows.

**m3 — Thin nulls uncaveated.** The PE homonym null rests on 3 deep splits; the Apte order null on 8 order-bearing entries (Benfey 154) — the f5 report itself flags this, the paper didn't. *Fix (applied):* both caveats added in-line.

**m4 — Ahlborn attribution incomplete.** The file header credits Ahlborn **with P. Scharf and J. Funderburk** (2011), extracted by Funderburk in October 2014 — not "M. Ahlborn, 2011" alone. *Fix (applied):* full credit in §4.1 + References.

**m5 — F6 floor and stratum size imprecise.** Random-pair floor is 0.0005–0.0007, not "~0.001"; "1,500/stratum" is nominal — VERB achieved n = 1,014 (all extant verb roots). *Fix (applied).*

**m6 — Phantom companions in the preamble.** "Article 17" and "Article 16" exist as no file; "Paper H §5 / Article 20" was unlinked. *Fix (applied):* preamble now links the two real companions ([paper_H_convention_vs_content_lineage.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_H_convention_vs_content_lineage.md), [paper_redundancy_and_descent.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_redundancy_and_descent.md)) and marks 16/17 as planned, not yet drafted.

**m7 — §3.1 lacked its data pointer** (the reproducibility audit's own recommended polish). *Fix (applied):* `data/L0/content_lift.csv` named in-line.

## 4. Data-side notes (no paper change)

- [ahlborn_mw_comparison.csv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/ahlborn_mw_comparison.csv) row `u → utpulaka` has `mw_has_error=True` but status `mw_correct` — an internal CSV inconsistency that does not affect any cited count (status column is what F4b tallies). Worth a look next time the forensic suite reruns.
- The F5 random baselines (0.50 concordance, ~5–17% chance-identical) are asserted in the report's `finding` field, not recomputable from the shipped CSVs — acceptable, but a simulation artifact would make §3.4 fully walkable.

## 5. Checked and sound (no action)

- The central decomposition (inventory / apparatus / error descent) and both decisive signals verify exactly; "heir of the scholarship, author of the prose" stands on committed, reproducing data.
- §4.2's null-test trap is a genuinely good methodological point and the f4b figures behind it are exact.
- §6's limits are honest, and the "one remaining decisive test" (shared erroneous citation vs DCS) is correctly scoped out of csl-atlas.
- Title matches the finding. Venue fit (DSH / *Journal of Cultural Analytics*) is sound for a computational-forensic study of dictionary descent; no HOLD.

## 6. Remaining gates

- **Author:** byline + venue pick (DSH vs JCA); the manuscript carries no byline block yet.
- **A11 (queued):** re-verify Paper H / L0_RESULTS bootstrap prose against the current [bootstrap_support.csv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/L0/bootstrap_support.csv) run in its own review pass (see M4).
- **External (out of scope):** the DCS shared-erroneous-citation test (§6 of the paper).

_Dr. Mārcis Gasūns_
