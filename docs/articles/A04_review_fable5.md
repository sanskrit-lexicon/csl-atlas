# A04 (P4 Grammar Without Tags) — Hostile Pre-Submission Review

_Created: 03-07-2026 · Last updated: 03-07-2026_

**Paper:** [docs/articles/paper_indigenous_microstructure.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_indigenous_microstructure.md)
**Reviewer:** Fable 5 (`claude-fable-5`), adversarial referee pass per H119 (Fable window S13), in the A01/A03/A06 mold.
**Verdict: MINOR REVISION** — every count re-verified exact against the committed artifacts; the argument is the series' most self-contained. The defects are the recurring apparatus ones (TODO references, no in-text citations, one stale corpus count) plus one artifact-vs-claim tension a checking referee would raise. All agent-doable; applied in this pass.

---

## 1. Figure re-verification — all counts CONFIRMED

Against [`indigenous_by_dict.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/indigenous_by_dict.json) and [`root_agreement.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/root_agreement.json):

- Table 1 (root entries / total entries): SKD 2,544/42,531 · VCP 2,230/50,135 · KRM 1,757/2,061 · YAT 1,643/45,206 · SHS 463/47,326 · PWG 8/123,366 · PW 3/170,556 · MW72 1/55,388 — all exact.
- Table 2 (resolved features): SKD 1,737/1,498/1,156 · VCP 1,954/1,897/2,183 · KRM 1,755/1,378/1,735 · YAT 1,643/1,643/— · SHS 456/407/454 — all exact (sums of `by_gana`/`by_pada`/`by_transitivity`).
- §4.2: SKD gaṇa distribution bhvādi 634 / curādi 531 / tudādi 170 exact; 1,925/2,544 slot coverage confirmed in [`MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md) and MICROSTRUCTURE_DECISIONS row 19; the 55 %/28 % gains recompute correctly (1,737/1,117; 1,498/1,167).
- §4.3 modal-class counts: SKD 634 / VCP 1,152 / KRM 944 / YAT 1,009 / SHS 288 — all exact.
- §4.4: 1,526 roots with 2+ opinions; compatible 0.8552 (85.5 %), unanimous 0.6992 (69.9 %), 221 conflicts (14.5 %); pairs SKD–VCP 0.9276 (948/1,022), SKD–KRM 0.9502, VCP–KRM 0.9268; *pada* 0.7526, transitivity 0.814 — all exact.
- §6: the 86.0 % → 81.2 % normalisation experiment is documented in [`MICROSTRUCTURE_ROOT_AGREEMENT.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_ROOT_AGREEMENT.md) (side-finding section) — a testing figure, distinct from the committed SKD–YAT pair rate (0.8912), correctly not conflated.

## 2. Major findings

**M1 — Reference apparatus was a TODO with zero in-text citations.** Same defect as A03/A06 pre-fix; a desk-reject at IJL. *Fix (applied):* Vogel 1979 (genre), Palsule 1961 (*The Sanskrit Dhātupāṭhas* — the standard study, by the same scholar whose *Kavikalpadruma* edition the paper already leans on), Hausmann & Wiegand 1989 (microstructure), and the TEI Lex-0 baseline (Tasovac & Romary et al.) for §5's standards paragraph — each wired at its natural anchor.

**M2 — Anti-salami: P1 §3.9 owns this paper's validation metric, and the A35/A30 cluster is uncoordinated.** §4.4's agreement measure is P1's root-parser-agreement estimator; no pointer existed. Worse, ARTICLES.md flags A35 (Pāṇinian derivation, 10 dicts, csl-orig) ↔ A04 ↔ A30 (ŚKD/VCP indigenous microstructure) as an overlap cluster needing a lead-paper decision *before submission* — the manuscript did not acknowledge the siblings at all. *Fix (applied):* companion block added citing P1 (§3.9) and naming A35/A30 as coordinated satellites with the shared-dataset note; the lead-paper choice itself remains the standing MG `@DECIDE`.

**M3 — "the forty-three dictionaries" is stale.** The corpus has been 44 since 2026-06 (BOR; and a fifth kośa, NMMB). *Fix (applied):* §1 now reads "forty-four (44 at the 2026-07 corpus; 43 at the 2026-06 measurement snapshot the numbers herein reflect)".

## 3. Minor findings

**m1 — The "eight or fewer in every European dictionary" claim survives the artifact cross-check only with a definition.** [`indigenous_by_dict.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/indigenous_by_dict.json) shows `acc` with **10** root-entry hits — but ACC is Aufrecht's *Catalogus Catalogorum*, a bibliographic catalog (its 10 hits are citations to root authorities), not a European dictionary. A referee opening the artifact hits this immediately. *Fix (applied):* footnote added to Table 1 stating the ACC exclusion and why.

**m2 — Relative artifact links** in the preamble and Table 1 source. *Fix (applied):* full blob URLs.

**m3 — Table 1 column header** "of total entries" reads as a fraction; it is the dictionary's total entry count. *Fix (applied):* header renamed "dict. total entries".

## 4. Fixes applied in this pass

All M/m findings above, same branch/PR as this review. Remaining gates: **author** byline + venue; the A35↔A04↔A30 lead-paper `@DECIDE`; the homonym-aware root key and the second *Dhātudīpikā* witness stay honest future-work items (§6).

## 5. Checked and sound (no action)

- The three-step argument (indigenous-only object → decodable convention → cross-validated) is tight, and §4.4's homonymy caveat is stated exactly where a referee would demand it.
- The *anubandha* key's provenance chain (empirical cross-walk → corrected by the primary source → corroborated by Palsule's edition) is honestly told, including the earlier mistake.
- §4.5's *iti*-unit point correctly defers to P2 rather than re-deriving it (good salami discipline in that direction).

_Dr. Mārcis Gasūns_
