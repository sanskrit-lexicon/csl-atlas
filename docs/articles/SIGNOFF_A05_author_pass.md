# SIGNOFF — A05 author-voice pass

_Created: 11-07-2026 · Last updated: 06-09-2026_

Author-voice pass over [`docs/articles/paper_xref_lineage.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_xref_lineage.md)
("Pointing Inward", P5), executed under handoff
[H680](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H680-Fable_csl-atlas_a04-a05-author-pass_11.07.26.md)
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

---

## Pass 2 — 06-09-2026 (Fable 5.1 `claude-fable-5-1`)

Second author-voice pass over
[`docs/articles/paper_xref_lineage.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_xref_lineage.md)
("Pointing Inward", P5), executed under handoff
[H3857](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3857-Fable_Uprava_all-articles-author-voice-pass-workflow_01.09.26.md)
by Fable 5.1 (`claude-fable-5-1`) on 06-09-2026. Pass-1 calls (above) were found
applied and are not revisited. Scope: voice, register and framing only; no number,
claim or citation altered; mechanical drift gate
([`voice_drift_check.py`](https://github.com/gasyoun/Uprava/blob/main/tools/voice_drift_check.py)
against `origin/main`) CLEAN on numbers, URLs, citations, IAST tokens, headings and table
rows.

### 1. Voice calls made — each may be vetoed

| # | Location | Call | Rationale |
|---|---|---|---|
| P2-V1 | Abstract (×2), §1 ("Our solution"), §3.1 ("we report"), §1 ("tells us") | Editorial "we/our/us" → first-person singular "I"; "tells us what a descent signal looks like" → "shows what a descent signal looks like" | Single-author paper; the H3857 brief sets first-person singular where the venue allows, and a DH/lexicography methods journal allows it. Pass 1 declined this on series-convention grounds; the series-wide pass now applies it uniformly. Veto restores "we" in five places, nothing else. |
| P2-V2 | Abstract | Four emphasis bolds removed: "**positive control**", "**85 % inheritance rate (Jaccard 0.74)**", "**21.8 % (Jaccard 0.069)**", "**shared core, not wholesale inheritance**", "**prefix-convention hubs**" | Bold in an abstract survives no journal template and reads as bold-every-other-word; figures verbatim. |
| P2-V3 | §3.1, §4.1, §4.2, §4.4 | Emphasis bolds removed on "source lemmas both dictionaries cross-reference", "directed", "floor", "~85 %", "641 are identical", "21.8 %", "related", the §4.2 verdict phrase, "zero" | Bold now marks only the first definition of a term (§1 content coincidence / convention artefact / inheritance; §3.1 inheritance rate; §3.2 edition-continuity ceiling; §3.3 prefix-convention hub; §2 edge). Table bolds and the Table 1 note untouched. |
| P2-V4 | §1 ¶3 | "Our solution is calibration by a positive control (§3)" → "The contribution of this paper is a calibration by positive control (§3)"; italic "*looks like*" dropped; "interpretable — and the answer" → "interpretable, and the answer" | One explicit singular contribution statement, which the paper lacked; §5.1 and the referee memo already name calibration as the contribution, so no new claim. |
| P2-V5 | §5.1 | "This is the general lesson — a structural-overlap measure means nothing…" → "The general lesson follows: a structural-overlap measure means nothing…" | Em-dash-as-copula. |
| P2-V6 | §6 Limitations | Six bold-lead bullets rewritten as two prose paragraphs, same six limitations in the same order, every figure (22,937 vs 7,637; 7–23; 40-edge) verbatim | Bold-label bullet sheet where sentences carry the same content; the section now reads in the paper's own register. Veto restores the bullets. |
| P2-V7 | §7 Conclusion | Inserted after the first sentence: "The question the introduction posed, whether the Monier-Williams `cf.` network and the Petersburg `Vgl.` network are the same graph, gets a qualified no." | The introduction asks the roadmap question in those words and answers it ("a qualified no"); the conclusion did not repeat the question. Same hedge as §1, no new claim. |
| P2-V8 | Preamble | `Last updated` bumped to 06-09-2026; status paragraph gains "author-voice pass 06-09-2026 (SIGNOFF link)" | Provenance per the brief; nothing else in the preamble touched. |

**Considered and declined (pass 2):** §5.1's paired spin-quotes and the §7 closer
(kept per pass 1); "not X but Y" in §4.3 and §4.4 (genuine contrasts, not the cliché);
"the project roadmap" (§1, series convention); the parenthetical P1/Andrews-Macé
sentence in §3.1 (long, but it carries the citations and is the referee's own wiring).

### 2. Substance flags carried (not fixed)

1. **§2 "(round 7)"** — an internal parsing-round label a journal reader cannot resolve;
   consider dropping the parenthesis or naming the rule. Left because it is a numeral.
2. **Two paths for one artifact** — the preamble cites
   [`data/lexico/xref_lineage.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/xref_lineage.json)
   while both table sources cite
   [`src/data/dicts/xref-lineage.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dicts/xref-lineage.json).
   If these are the same graph, cite one; if not, say which is canonical.
3. **AP × MW Jaccard 0.147 exceeds the headline MW × PWG 0.069** (Table 2) and is
   labelled only "sparse". §6 says the sparse pairs are unreadable; a referee may still
   ask why the paper does not comment on the one cross-tradition pair whose Jaccard beats
   the headline pair.
4. **SLP1 tokens presented as italic Sanskrit** — §1 "*Ayu* … *Ayus*", §4.2 "*ARi → aRi*,
   *Ayu → Ayus*, *Bala → bal*" are SLP1 keys (capital A = ā), not IAST. A journal reader
   will read them as misspellings; a transliteration note or IAST rendering is owed at
   camera-ready. Untouched (Sanskrit tokens are frozen for this pass).
5. **§6 "every cross-tradition pair except MW × PWG and the Apte control"** — the Apte
   control is not a cross-tradition pair, so the exception clause is loose. Wording left
   as it stood (it borders on the claim).
6. **§5.2 cross-paper claim** that the P3 packet "scores [AP × AP90] at high content and
   microstructure" — verify against the P3 manuscript before submission.
7. **Table 2 caption "the reading is the machine review label"** and §6 "machine triage
   classes" — a reader has no definition of the label set; one sentence in §3 naming the
   four classes would close it. Not added (a method addition, not voice).
8. **References** still headed "draft — author to finalise"; Wiegand 1989 page span
   409–461 and the Zgusta dual imprint to be verified (standing from pass 1).

### 3. Read-and-sign

1. Skim §1 above and veto any of P2-V1…V8; P2-V1 (first person) and P2-V6 (limitations
   prose) are the two a reader will notice.
2. Rule on flags 1–4; 5–8 can wait for camera-ready.
3. Read once end-to-end for register (~30 min).
4. Proposed readiness after sign-off: **4/5 → 5/5 candidate** (propose only; the bump is
   the author's). Venue recommendation unchanged: DH/lexicography methods journal, WSC
   2027 alternate. Submission frozen until 2026-11-01.

_Dr. Mārcis Gasūns_
