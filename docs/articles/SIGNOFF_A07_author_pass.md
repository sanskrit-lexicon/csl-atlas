# A07 — author-voice pass sign-off memo

_Created: 06-09-2026 · Last updated: 06-09-2026_

**Paper:** [paper_redundancy_and_descent.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_redundancy_and_descent.md) (*Redundancy and Descent in a Digitised Dictionary Family: A Headword-Level Stemma of the Cologne Digital Sanskrit Lexicon*).
**Pass:** author-voice pass, executed 06-09-2026 by Fable 5.1 (`claude-fable-5-1`), handoff [H3857](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3857-Fable_Uprava_all-articles-author-voice-pass-workflow_01.09.26.md).
**Scope:** voice, register and framing only; no number, claim or citation altered; mechanical drift gate ([voice_drift_check.py](https://github.com/gasyoun/Uprava/blob/main/tools/voice_drift_check.py) against `origin/main`) CLEAN — 243 numbers, 5 URLs, 39 IAST tokens, 20 headings, 23 table rows count-identical before and after.

## 1. Voice calls made — each may be vetoed

| # | Location | Call | Rationale |
|---|---|---|---|
| 1 | Under the H1 title | Byline block added: Mārcis Gasūns, independent scholar, ORCID 0000-0003-4513-884X, gasyoun@ya.ru. The status paragraph's "Author: M. Gasūns." is left in place. | The paper carried only the abbreviated name inside the italic status note; the academic byline form with ORCID was absent. |
| 2 | Abstract ×3, §1 ×2, §3.1 ×4, §3.2 ×2, §4.3 ×1 | Authorial "we / our" → first-person singular in twelve spots ("I measure", "I reduce", "I argue", "My claim", "I therefore treat", "I work", "I extract", "I take", "I also report", "I compute", "I apply", "I expect"). | Single-author paper; matches the voice call already made in A01 and A06 so the series reads uniformly. IJL accepts the singular. Revert mechanically if "we" is preferred. |
| 3 | Abstract | "Crucially, redundancy is not uniform but *structured*" → "Redundancy is not uniform but *structured*". | Filler intensifier from the de-AI list; the contrast itself (not uniform / structured) and every figure that follows are untouched. |
| 4 | Table 2 caption (§4.4) | "— the pair that turns "MW is a near-total absorber" from asserted into shown:" → ", so that the claim "MW is a near-total absorber" can be checked row by row:". | The old wording addressed a reviewer of an earlier draft ("asserted before"), not the reader of the finished paper. The caption's own claim (`a_in_b` large, `b_in_a` small in every row) is unchanged. |
| 5 | §4.4, paragraph after Table 2 | "the asymmetry that "absorption" only asserted before is now visible directly" → "the asymmetry behind the word "absorption" is visible directly". | Same drafting-history register removed; the 88–94 % / 9.6 % claim that follows is untouched. |
| 6 | §4.4, same paragraph | "The WIL ⊂ SHS edge is the exception that proves the rule:" → "The WIL ⊂ SHS edge is the instructive exception:". | Stock phrase; the sentence that follows already explains in what sense the edge is the exception (near-mutual supersets, gloss overlap 0.906). |
| 7 | §4.5 opening | "A striking corollary emerges once …" → "A corollary follows once …". | "Striking" is a decorative epithet on the corollary, not a magnitude word attached to a measurement; the figures (3.3 %, 14.1 %, 7.6 %, 23.0 %, 2,265) are untouched. |
| 8 | §5, first paragraph | "into an actionable map:" → "into a map an editor can act on:". | "Actionable" is management register; the three-part list that follows is unchanged. |
| 9 | §1 | Line-wrap join of "Sanskrit-to- / English" (trivial, no wording change). | A hard line break split a hyphenated compound. |
| 10 | Header line | `Last updated` bumped to 06-09-2026. | Standing header rule. No pass note added to the status paragraph because it lists no prior passes. |

Not touched on purpose: "not merely *a* large dictionary but the documentary sink" (§4.4) — "merely" is a qualifier and stays; "the great compiler-hub" (Table 1, a cell); "which is a service, not a defect" (§4.3); the bold-lead paragraph structure of §5 ("For digital lexicography." etc.), which is conventional for the venue.

## 2. Substance flags carried (not fixed)

1. **"Nine other dictionaries" vs six shown.** Abstract and §4.4 say MW contains 88–94 % of the headword stock of *nine* other dictionaries, and that those nine contain "at most 9.6 %" of MW's. Table 2 shows six MW rows (BOP, BEN, MD, ARMH, ABCH, GRA; min 0.878, max reverse 0.096). The other three rows are not in the paper, so a referee cannot check the "nine" or the 9.6 % ceiling from the table. Either add the three rows or say "the six strongest of nine" in the caption.
2. **Intro date range "1822–1993".** §1 says the printed editions span 1822–1993, but no 1993 dictionary is named anywhere in the paper (latest named: Edgerton 1953, Apte revision 1957–59). Checked against [data/dictionary_inventory.csv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/dictionary_inventory.csv): the 1993 member is MCI, the *Mahabharata Cultural Index* (Pusalker, partial publication 1976–1993). The date is correct; §2.1's "and others" is where it hides. Consider naming it, since the range's upper bound otherwise looks unanchored.
3. **Cross-references to unpublished companions.** §4.1 "Paper on microstructure, M1–M2"; §4.4 "Paper P2 §6" (gloss overlap 0.906); §1, §5, §6 "Paper H"; §5 "companion OBS-Q study"; §6 "sense-alignment work (R2)". Internal project labels, not citable references; a submission version needs either a citation or a "(in preparation)" form for each.
4. **Bracketed editorial note inside the References.** The paragraph "[Same core metalexicography set as the companion sense-inheritance paper (P2); a dictionary-aggregation-specific comparator … is not pursued here …]" is a note to self inside the reference list. Left untouched (reference entries are out of scope for this pass); a human should decide whether it moves to §6 or is dropped before submission.
5. **Table 2 caption "direction by year + size" vs the CCS ⊂ PW row.** Years read "1887 / 1879" (A later than B) while WIL ⊂ SHS reads "1832 / 1900" (A earlier than B). Both are consistent with §3.2's rule (the earlier superset is the ancestor), but the "A ⊂ B" arrow is a containment relation, not the descent direction, and a reader may take it as the latter. Consider one sentence in the caption saying so.
6. **Apte year — checked, consistent.** §2.1 gives "Apte (1890; revised three-volume edition 1957–59)"; Table 1 labels the row "AP — Apte 1957". The inventory carries `AP` = 1957–59 Pune revision (88,667 entries) and `AP90` = 1890 original (34,277) as separate members, so the table label is right. No action.
7. **Abstract "for the first time at the level of the whole corpus".** A priority claim; left at full strength. If a prior whole-corpus overlap census exists anywhere (e.g. the CDSL's own *sanhw1* documentation), soften before submission.
8. **Closer `_Dr. Mārcis Gasūns_`.** Repo file convention, left in place; the submission export should drop it (the academic byline above carries no "Dr.").

## 3. Read-and-sign

- Estimated read: ~30 minutes (manuscript ≈ 370 lines; the ten calls above are the only diffs, all in prose).
- Proposed readiness: **4/5** (propose only; the 5/5 bump is a human ruling after flags 1–3 are settled).
- Venue recommendation: keep the *International Journal of Lexicography* as primary — the paper is metalexicography with a reproducible-audit moral; no change proposed. No submission before the 2026-11-01 freeze lifts.

_Dr. Mārcis Gasūns_
