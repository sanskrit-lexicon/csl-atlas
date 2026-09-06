# SIGNOFF A09 — author-voice pass, Sanskrit-anchored sense alignment

_Created: 06-09-2026 · Last updated: 06-09-2026_

**Scope.** Manuscript: [PAPER_SENSE_ALIGNMENT.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/PAPER_SENSE_ALIGNMENT.md) (paper A09, readiness 3/5). Handoff: [H3857 — all-articles author-voice pass workflow](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3857-Fable_Uprava_all-articles-author-voice-pass-workflow_01.09.26.md). Pass by Fable 5.1 (`claude-fable-5-1`) on 06-09-2026. Voice, register and framing only; no number, claim or citation altered; mechanical drift gate CLEAN ([voice_drift_check.py](https://github.com/gasyoun/Uprava/blob/main/tools/voice_drift_check.py) against `origin/main`: numbers 198/198, URLs 14/14, IAST 28/28, headings 21/21, table rows 4/4).

## 1. Voice calls made — each may be vetoed

| # | Location | Call | Rationale |
|---|---|---|---|
| 1 | Working title block | Added the academic byline line (Mārcis Gasūns, independent scholar, ORCID, gasyoun@ya.ru) under the title | Manuscript carried only the internal `Owner: M. Gasūns + Claude` line; no author byline existed |
| 2 | Header / Status | `Last updated` bumped to 06-09-2026; status paragraph gains `author-voice pass 06-09-2026 (SIGNOFF_A09_author_pass.md)` | Brief's header-note rule |
| 3 | Thesis / abstract | De-bolded `**same**`, `**senses**`, `**deterministically, with no translation**` | Three bolds in five sentences is bold-every-other-word; the claims read the same unbolded |
| 4 | §1 para 1 | De-bolded `questions about **senses**, not headwords` | Same as 3; the contrast carries itself |
| 5 | §2 Related work | One 90-word sentence joined by an em-dash split in two: `...unavailable or unreliable. The two approaches could be benchmarked ... (e.g. PWG↔Apte); that benchmark is flagged as an open validation idea for §7/§8 rather than attempted here.` De-bolded `complementary, translation-free alternative` | Em-dash run-on; wording and hedging otherwise verbatim |
| 6 | §2 last sentence | `... method — worth direct comparison in a revision pass, and the paper this one should ...` became `... method. It deserves direct comparison in a revision pass, and it is the paper this one should ...` | Em-dash-as-copula with a dropped verb (telegram syntax) |
| 7 | §4 | Removed the in-prose `⚠️` and the bold on `not yet reproduced by the restored splitter` | Emoji marker inside manuscript prose; the caveat sentence itself is untouched and is repeated in "Open before submission", where the marker stays |
| 8 | §5.1 | De-bolded `**convention**` | Decorative emphasis |
| 9 | §5.2 | `⚠️ The restored pipeline ... and they **downgrade the claim** — this section must be written as *co-varies*, not *predicts*.` became `The restored pipeline ... and they downgrade the claim; this section is therefore written as *co-varies*, not *predicts*.` | Emoji and bold removed; an author-facing instruction turned into the statement the section already obeys (its heading says "co-varies"). Claim strength unchanged. Veto if the instruction form is wanted until §5.2 is final |
| 10 | §5.3 | `(drift −3.07, overlap 0.57 — revision, not expansion)` became `(drift −3.07, overlap 0.57); this is revision, not expansion.` | Em-dash-as-copula; the "revision, not expansion" wording is kept verbatim |
| 11 | §5.3 | Dropped the opener `Most strikingly,` before `the Śabda-Sāgara (1900) reproduces ...`; de-bolded `reproduces Wilson's sense glosses near-verbatim` | Filler intensifier; the 90.6% figure and "near-verbatim" carry the point |
| 12 | §7 opener | `The method's determinism is also its honesty policy: every weakness below ...` became `Because the pipeline is deterministic, every weakness below ...` | Decorative metaphor replaced by the causal statement it stood for |
| 13 | §7 Coverage paragraph | Removed the in-prose `⚠️` after the bold lead-in | As 7 |

Not changed on purpose: the first-person plural (`we`) throughout — the co-author decision is open (see flag 6), so switching to singular now would have to be undone if a co-author is added; `**anchoring on Sanskrit**`, `**Sanskrit fingerprint**`, `**tradition cluster**`, `**threshold-dependent**`, `**edge-concentrated**` and the §7 bold run-in headings, which name terms rather than decorate; the "Technique-adoption assessment (internal note, not manuscript prose)" block, which is labelled as a note and left as found.

## 2. Substance flags carried (not fixed)

1. **Dictionary count is inconsistent across the paper.** Title and abstract say 15 dictionaries; H1 (§5.1) uses "eleven general dictionaries"; §7 says the restored package covers "fourteen dictionaries in the explorer slice plus Yates and Śabda-Sāgara", i.e. sixteen. The abstract's count should be reconciled with the restored corpus before submission.
2. **Stchoupak (French) in the abstract but not in the restored corpus** — already recorded in §7 and "Open before submission"; a scope decision, not a wording fix.
3. **§2 heading conflict.** The Structure list assigns §2 to "Data — the CDSL csl-orig corpus" but the only drafted §2 is "Related work"; §2 Data and §6 Explorer are outline-only and §8 Conclusion is unwritten, so the intro-question / conclusion-answer alignment cannot be checked in this pass.
4. **Author-facing notes still live inside §5.2 prose:** "report the sensitivity table and the within-edge test, not a single star" and "(The companion inheritance manuscript already adopts this framing; keep the two in lockstep.)" These are instructions, not results; they need moving to "Open before submission" or deleting by a human, since removing sentences is outside this pass.
5. **§1 rounds 90.6% to "90% word-identical"** while Contributions and §5.3 give 90.6%. Consistent enough for a draft, but a referee will notice; not touched.
6. **Byline vs ownership.** The added byline names a single author; the header still says `Owner: M. Gasūns + Claude` and "Open before submission" lists a co-author as `MG @DECIDE`. The byline form must follow that decision.
7. **H2 wording lockstep.** §5.2 states the companion inheritance manuscript "already adopts this framing"; nothing in this pass verified that the two manuscripts still match after their respective voice passes.
8. **Contributions item 3 vs §1 para 4.** Contributions call H2 "suggestive, not established"; §1 says "though on evidence concentrated on a single edge". Both hedge, at slightly different strengths; left as found.

## 3. Read-and-sign

About 30 minutes: read the abstract, §1, §2, §5.2–5.3 and the §7 opener against the table above; rule on flags 1, 3, 4 and 6.

- Proposed readiness: 3/5 → stays 3/5 (propose only). §2 Data, §6 and §8 are unwritten and the dictionary count is unreconciled; the voice pass does not move readiness.
- Venue: the manuscript's own §2 points at ISCLS (positioning against Patel & Kulkarni, ISCLS 2024); no change recommended here. Submission frozen until 2026-11-01 per H3857.

_Dr. Mārcis Gasūns_
