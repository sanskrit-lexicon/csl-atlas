# A01 — author-pass sim sign-off memo

_Created: 08-07-2026 · Last updated: 06-09-2026_

**Paper:** [paper_measurement_framework.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_measurement_framework.md) (P1, *Measuring the Dictionary Family*)
**Pass:** author-voice sim per [AUTHOR_PASS_SIM_PROTOCOL.md](https://github.com/gasyoun/Uprava/blob/main/docs/AUTHOR_PASS_SIM_PROTOCOL.md), executed 08-07-2026 by Fable 5 (`claude-fable-5`), handoff [H368](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H368-Fable_Uprava_author_pass_sim_protocol_batch1_08.07.26.md).

## What changed

- **Byline added** under the title: Mārcis Gasūns · ORCID 0000-0003-4513-884X · gasyoun@ya.ru
  (academic form, no "Dr."); the "final byline to be added" footer note removed.
- **Abstract** rewritten in first-person singular: "We describe / We work / We are explicit"
  → "I describe / I walk / The scope is explicit"; opening clause sharpened ("…yet a
  published result rarely lets the reader walk the number back to the dictionary line that
  produced it"); **"40+ dictionaries" harmonized to "44"** to match §1's committed 2026-07
  measurement envelope (no other number touched).
- **Conclusion** voice: "We have described" → "I have described".
- **Status line** updated to "submit-ready draft pending author sign-off", with this memo linked.
- Body §§1–8 left untouched — the referee-pass prose already reads as one arc; no seams found
  that needed smoothing. No claim, number, table, or citation was added or altered.

## What you must verify (~15 min)

1. **The voice call**: sole-authored "I" throughout abstract + conclusion. If you prefer the
   authorial "we", revert those three sentences — nothing else depends on them.
2. **Abstract "44"**: confirm you want the abstract pinned to the envelope count (44) rather
   than the looser "40+".
3. Read abstract + §1 + §9 once — the only sections touched.

## Flagged suggestions (NOT applied — unverifiable or author's call)

- None. No citation gaps found; the reference list was already verified in the 02-07 pass.

## Venue recommendation

**DSH (Oxford) primary — keep.** The paper's contribution is transferable DH methodology
(traceability discipline, evidence grading), which is DSH's center; IJL would read it as a
methods note and compress it. No change proposed, so no `@DECIDE` needed.

## Pass 2 — 06-09-2026 (Fable 5.1 `claude-fable-5-1`)

**Scope.** Second author-voice pass over [paper_measurement_framework.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_measurement_framework.md) under handoff [H3857](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3857-Fable_Uprava_all-articles-author-voice-pass-workflow_01.09.26.md), executed 06-09-2026 by Fable 5.1 (`claude-fable-5-1`). Voice, register and framing only; no number, claim or citation altered; mechanical drift gate (`tools/voice_drift_check.py --git origin/main`) CLEAN. Pass 1 (above, 08-07-2026) touched abstract, status and conclusion; this pass reads the body for what pass 1 left and finds eight seams, all in §1, §3.2, §5, §6 and §9. Nothing above this heading was rewritten.

### 1. Voice calls made — each may be vetoed

| # | Location | Call | Rationale |
|---|---|---|---|
| 1 | Abstract | Three bold spans dropped ("three layers that any comparable project can reuse", the `Claim → Evidence → Source` commitment, "dictionaries" — the last now italic) | Journal abstracts are plain-text fields; three bold spans in one paragraph read as emphasis by markup rather than by sentence. The governing rule keeps its bold in §1, where it is stated for the record. |
| 2 | §1 para 1 | The Atkins–Rundell aside moved out of the sentence it interrupted; "The toolkit is the real instrument of the work, yet it is usually left implicit …" followed by "Dictionary *production* has long had a codified counterpart …; dictionary *measurement* has not." | The em-dash parenthesis sat between the subject and its "but" clause, so "it" in "but it is usually left implicit" had two candidate referents. Citation and claim unchanged, order only. |
| 3 | §1 para 2 | "It describes … and presents it" → "I describe … and present it"; "44 digitised dictionaries … whose digitised print editions" → "44 dictionaries … whose digitised print editions" | Abstract and §9 already speak in the first person singular (pass 1); the introduction was the one section still in the impersonal "this paper … it". The doubled "digitised" was a leftover of the m3 basis fix. |
| 4 | §3.2 Output | "general dictionaries mutually derivative, specialised and indigenous lexica novel" → "the general dictionaries are mutually derivative, while the specialised and indigenous lexica are novel" | Telegram syntax with both verbs dropped; the finding is unchanged. |
| 5 | §5 | "These are not editorial niceties — they are the difference …" → "They are the difference …" | The "not X — they are Y" figure; the sentence is stronger as the direct claim. |
| 6 | §6 step 2 | "Crucially, this is independent of headword overlap" → "This signal is independent of headword overlap" | Filler intensifier; the independence is the argument, it needs no adverb. |
| 7 | §9 | "falsifiable and in its lane" → "falsifiable and inside its bounds" | Colloquial idiom replaced by the paper's own §1/§5 term for the same thing. |
| 8 | §9 | "the move the empirical companions … each rely on, and which this paper states once" → "the move each empirical companion … relies on, and the one this paper states once" | Number agreement and a mixed relative chain in the closing sentence. |

Header `Last updated` bumped and the status line extended with this pass; no other note added.

### 2. Substance flags carried (not fixed)

1. **§6 step 3 and abstract, "a −3 revision".** The committed value is a mean of −3.07 (Apte 1890 → 1957, P2 table, confirmed in the 03-07 review); P1 never says what the unit is (mean change in sense count per shared lemma along the edge?). A referee will ask "−3 what". Owner of the figure is P2; a half-sentence of unit here is the author's call.
2. **Abstract vs §1 corpus-span basis.** §1 now states the basis (digitised editions 1832–1993; first publications back to 1822); the abstract still says "print sources 1832–1993" with no basis. Consistent with §1 as written, but the m3 cross-reading trap remains open at the abstract level.
3. **§1 para 3, the unnamed rival programme.** "sometimes called a 'measurement framework for digital lexicography'" quotes a phrase without citing whose it is. Naming the programme is a citation addition and therefore out of scope for this pass; without it a referee may read the paragraph as a straw man.
4. **Abstract and §1, "44 dictionaries".** Pinned to the committed 2026-07 envelope. If the envelope is regenerated before submission (csl-orig gained nmmb in 2026-06; further additions are plausible), the count and the "as of" date need re-pinning together.
5. **§3.3 Output.** "0.762 vs 0.705" are given without their denominators (64/84 and 510/723 per the review memo); P2 owns them, but P1's own traceability rule (§4) would be better served by stating them or linking the P2 table row directly.

### 3. Read-and-sign (~30 minutes)

1. Read §1 once for the first-person switch (call 3) — this is the only change that alters the paper's register rather than a single sentence; revert to "It describes … presents" if the journal's house style or your own preference is the impersonal introduction. Nothing else depends on it.
2. Read the abstract once for the de-bolding (call 1) — a pure formatting call; restore if you want the emphasis kept in the Markdown master.
3. Rule on flag 1 (the unit of "−3") and flag 3 (name or not name the rival programme); both are one-sentence edits that a future pass may not make on its own.
4. **Proposed readiness: 4/5** (propose only). The remaining gate is authorial: the two rulings above plus the venue pick.
5. **Venue:** DSH (Oxford) primary, unchanged from pass 1; the paper is still method-first and reads as DH methodology, not as an IJL methods note. No `@DECIDE` needed.

_Dr. Mārcis Gasūns_
