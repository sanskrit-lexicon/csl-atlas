# SIGNOFF — A05 author-voice pass

_Created: 11-07-2026 · Last updated: 11-07-2026_

Author-voice pass over [`docs/articles/paper_xref_lineage.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_xref_lineage.md)
("Pointing Inward", P5), executed under handoff
[H680](https://github.com/gasyoun/Uprava/blob/main/handoffs/H680-Fable_csl-atlas_a04-a05-author-pass_11.07.26.md)
by Fable 5 (`claude-fable-5`) via the [`/paper-author-pass`](https://github.com/gasyoun/claude-config/blob/main/commands/paper-author-pass.md) skill,
paired with the A04 pass ([SIGNOFF_A04_author_pass.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/SIGNOFF_A04_author_pass.md)).

**No number, claim, or citation was changed** except the two items in §1 — both
completions of rulings the referee pass already made, applied loudly here rather than
silently. Verified mechanically against `origin/main`: the numeral/citation multiset
diff shows exactly one `300,000` removed (§1.2, a duplicated phrase) and only the pass
date, signoff link, and ORCID digits added.

---

## 1. Two referee-fix completions — read these first

The [H119 referee pass](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/A05_review_fable5.md)
ruled and merged two corrections ([PR #200](https://github.com/sanskrit-lexicon/csl-atlas/pull/200))
whose application missed one instance each. This pass completed both — they are edits
to *claim text*, so they are flagged here for explicit confirmation, not buried among
the voice calls:

### 1.1 §3.2 still carried the AP/AP90 edition-label swap

Review finding M1 established the CDSL codes (**AP90 = the 1890 edition, AP = the 1957
revision**) and corrected the abstract and Table 1 — but §3.2 still read "Apte 1890
(AP) and the revised Apte (AP90)", contradicting the paper's own Table 1 note two
sections earlier. Now: "Apte 1890 (AP90) and the revised Apte (AP)". The sentence's
claim (same dictionary, two editions) is unchanged; only the code attributions swap.
**Confirm against Table 1 on read-through** — this was the exact defect class M1 called
"corrupts the paper's central calibration narrative".

### 1.2 §4.2 carried both the pre-fix and post-fix wording of the m2 correction

Review finding m2 replaced "in a lexicon of some 300,000 headwords" with "in the
≈300,000-headword union of the two dictionaries' key spaces" — but the merged text
contained **both** phrases spliced into one garbled sentence ("…is not what independent
networks produce — here in the ≈300,000-headword union…"). The duplicate pre-fix phrase
is removed; the sentence now reads with the post-fix wording only. No figure changed
(the ≈300,000 stays, stated once).

---

## 2. Voice calls made in this pass — each may be vetoed

| # | Location | Change | Rationale |
|---|---|---|---|
| V1 | Preamble | Canonical byline installed (name, independent scholar, ORCID, gasyoun@ya.ru) + pass-provenance sentence | Same discharge as A37/A03/A04; the References tail note trimmed accordingly (V4). |
| V2 | Preamble | Inert `` `/tools/xref-lineage` `` code-span → clickable link to [the public chart](https://sanskrit-lexicon.github.io/csl-atlas/tools/xref-lineage) | A real, openable URL must be a link (A03's preamble already links its `/tools/descent-axes` chart this way). |
| V3 | Abstract | "…are *not* independent, but nowhere near the edition-continuity ceiling" → "…are *not* independent, yet the overlap sits nowhere near the edition-continuity ceiling" | The original zeugma made "the networks" the subject of "nowhere near the ceiling"; it is the overlap that sits below the ceiling. Figures verbatim. |
| V4 | References tail | "*Bibliographic details and the final byline…*" → "*Bibliographic details…*" | Byline half discharged (V1). |

**Considered and declined:**

- **Editorial "we"** — same call as every pass in this series.
- **§5.1's paired spin-quotes** ("21.8 % shared, the networks are related!" / "78 %
  divergent…") and the §7 closer ("…they point, faintly but measurably, back along the
  line of descent") — vivid, load-bearing, authorial; preserved.
- **"the project roadmap" (§1)** — series-wide convention; see the A04 signoff's note.

---

## 3. Standing flags carried over (not raised by this pass)

- **Venue** — DH/lex methods journal, WSC 2027 alternate; still the author's pick.
- **"References (draft — author to finalise)"** heading marker — strip at submission.
- **Second edition-continuity control** (§6) — honest future work, no action owed.

---

## 4. Read-and-sign

1. Confirm the two referee-fix completions (**§1.1, §1.2**) against Table 1 and the
   review memo — the only substance-adjacent items in this pass.
2. Skim **§2** and veto any voice call you dislike.
3. Read the manuscript once end-to-end for the target register (~30 min).
4. On sign-off, bump A05 to **5/5** in
   [`Uprava/ARTICLES.md`](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md); the
   venue pick remains its own item.

Step 1 is the one item that needs real attention; 2–3 are register.

_Dr. Mārcis Gasūns_
