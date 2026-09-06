# A06 — author-pass sim sign-off memo

_Created: 08-07-2026 · Last updated: 06-09-2026_

**Paper:** [paper_kosha_macrostructure.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_kosha_macrostructure.md) (P6, *Order Is the Dictionary*)
**Pass:** author-voice sim per [AUTHOR_PASS_SIM_PROTOCOL.md](https://github.com/gasyoun/Uprava/blob/main/docs/AUTHOR_PASS_SIM_PROTOCOL.md), executed 08-07-2026 by Fable 5 (`claude-fable-5`), handoff [H368](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H368-Fable_Uprava_author_pass_sim_protocol_batch1_08.07.26.md).

## What changed

- **Byline added** (Mārcis Gasūns · ORCID 0000-0003-4513-884X · gasyoun@ya.ru), replacing
  "Author: M. Gasūns (byline to finalise)".
- **Voice**: authorial we/our → first-person singular in nine spots (abstract ×2, §1
  contribution paragraph, §2.1, §2.2, §3 ×2, §4.2, §6) — matches A01's voice call so the
  series reads uniformly.
- **Status block** updated to record this pass and link this memo.
- Abstract, argument arc, and conclusion otherwise left as-is — the four-finding structure
  already lands, and the conclusion's "a zero is a question about the instrument" close is
  the paper's strongest sentence; I did not touch it. No claim, number, table, or citation
  was added or altered.

## What you must verify (~20 min)

1. **The voice call** (same as A01): "I" as sole author. Revert mechanically if you prefer "we".
2. **Two standing author-verification flags I did NOT fill** (unverifiable without the
   physical source — protocol guardrail):
   - §2.1: *"[author to verify against Wilson's 1819 preface, which documents the
     kosha-based compilation, before submission]"* — the Wilson→MW descent-via-kośa claim.
   - References: Wilson 1819 *"[author to verify page range]"*.
3. The "References (draft — author to finalise)" header stays until (2) is resolved.

## Flagged suggestions (NOT applied)

- Consider Zachariae, *Die indischen Wörterbücher (Kośa)* (1897, Grundriss der
  Indo-Arischen Philologie I.3b) as a secondary reference alongside Vogel 1979 — it is the
  other standard genre survey and a referee may expect it. Not added because I could not
  verify the exact fascicle numbering against a physical/scanned copy in this pass.

## Venue recommendation

**IJL primary — keep.** The paper is metalexicography with a measurement-bias moral, square
IJL territory; WSC 2027 stays the indological alternate for the conference version. No
change proposed.

## Pass 2 — 06-09-2026 (Fable 5.1 `claude-fable-5-1`)

**Scope.** Second author-voice pass over [paper_kosha_macrostructure.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_kosha_macrostructure.md) (P6, *Order Is the Dictionary*) under handoff [H3857](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3857-Fable_Uprava_all-articles-author-voice-pass-workflow_01.09.26.md), executed 06-09-2026 by Fable 5.1 (`claude-fable-5-1`). Voice, register and framing only; no number, claim or citation altered; mechanical drift gate (`voice_drift_check.py --git origin/main`) CLEAN: numbers 169/169, URLs 11/11, IAST tokens 146/146, headings 16/16, table rows 22/22. Pass-1 calls (first person, byline) stand; this pass removes what pass 1 left: journal-incompatible emphasis bold in the abstract and running prose, one fake-candour opener, one "not X; it is Y" close, and the em-dash-as-copula habit (50 em-dashes down to 34; the paired parenthetical dashes and the *kāṇḍa*-order arrows were left alone).

### 1. Voice calls made — each may be vetoed

| # | Location | Call | Rationale |
|---|---|---|---|
| 1 | Header status paragraph | `Last updated` bumped to 06-09-2026; this pass recorded after the 2026-07-08 note with a link to this memo | Brief's header-note rule; only place the pass is mentioned in the manuscript |
| 2 | Abstract, sentence 1 | "no definitional prose — a microstructure detector scores it zero" → "no definitional prose, so a microstructure detector scores it zero" | em-dash carrying a causal link; a conjunction says it |
| 3 | Abstract | bold stripped from "macrostructure", "(1)"–"(4)", "Jain", "9.2 synonyms per verse", "56 names for Viṣṇu", "opposite", "incommensurable", "inherit the six-*kāṇḍa* frame" | IJL abstracts carry no typographic emphasis; bold-every-other-word is on the de-AI list |
| 4 | Abstract, finding (1) | ~~"— a **Jain** signature, with the Arhats placed above … and the mass … in the *human* world" → ", a Jain signature that places the Arhats above … and the mass … in the *human* world"~~ | reverted after adversarial verify: "that places" made the Jain signature the cause of the placement, where the original only lists the two facts side by side; de-bolding of "Jain" kept |
| 5 | Abstract, finding (2) | "peaking at 56 …, 47 …, 45 for Śiva — theonyms carry the largest sets" → "and peaks at 56 …, 47 … and 45 for Śiva: theonyms carry the largest sets" | dash-as-copula → colon; finite verb restores the sentence |
| 6 | Abstract, finding (3) | "digitized by opposite models — ARMH … , ABCH … — so their entry counts are incommensurable" → "digitized by opposite models: ARMH … , ABCH … . Their entry counts are therefore incommensurable" | split a three-dash sentence into two |
| 7 | Abstract, last sentence | ~~"no entry-level measure can see — the same convention-blindness" → "… can see: the same convention-blindness"~~ | reverted after adversarial verify: a colon after the verb "see" reads as introducing a list or a quotation, where the original dash appends an apposition; em-dash restored |
| 8 | §1, para 1 | "is simply to find them" → "is to find them" | filler intensifier |
| 9 | §1, para 2 | "reads as **empty**" → "reads as empty" | emphasis bold in prose |
| 10 | §2.1, NMMB sentence | "i.e. yet a *third* digitization variant …; it is out of scope … §4.3's warning" → "that is, a *third* digitization variant … . It is out of scope … the warning of §4.3" | run-on split; "i.e." and a possessive on a section number out of running prose |
| 11 | §2.1, last sentence | "microstructure — which is one more reason" → "microstructure, which is one more reason" | dash where a relative clause needs a comma |
| 12 | §2.2 | "it is simply *located in the arrangement*" → "it is *located in the arrangement*" | filler intensifier |
| 13 | §3, lead | bold stripped from "opposite digitization models" | emphasis bold in prose |
| 14 | §4.1, para 1 | bold stripped from "differently", "cosmic region", "hierarchy of beings" | emphasis bold in prose |
| 15 | §4.1, para 2 | "First, it is **Jain**" → "First, it is Jain"; "the **martya- (human) *kāṇḍa* holds 811 of ABCH's 1,965 records** — more than gods (271+41) and animals (602) — while the hell-*kāṇḍa* musters only **6**" → same figures, bold removed, dashes → commas | emphasis bold + parenthetical dashes around a comparison that reads as a plain clause |
| 16 | §4.2, para 1 | bold stripped from the counts; "lowest on earth (8.6) — the gods attract the most names" → "…(8.6): the gods attract the most names"; ~~"The peak is emphatic:" → "The largest sets are theonyms:"~~ | dash-as-copula → colon; bold removal kept. The "emphatic" rewrite reverted after adversarial verify: it turned a remark on the size of the peak into a generalisation about theonyms that the sentence does not support |
| 17 | §4.2, para 2 | "One honest qualification: ARMH's fifth *kāṇḍa* is *anekārtha* — **homonymic**, not synonymic." → "One qualification is needed. ARMH's fifth *kāṇḍa* is *anekārtha*, homonymic rather than synonymic." | fake candour ("honest"); bold; dash |
| 18 | §4.2, last sentence | "flag *kāṇḍa* 5 separately — the same convention-awareness" → "… separately: the same convention-awareness" | dash-as-copula → colon |
| 19 | §4.3, lead | "The headline methodological result is that the **same genre is digitized two opposite ways**" → "The main methodological result is that the same genre is digitized in two opposite ways" | "headline" is press register; bold; missing preposition |
| 20 | §4.3 | bold stripped from "7,907 "entries."", "1,965 "entries"", "4,619 lexemes" | emphasis bold on figures that the table already carries |
| 21 | §4.3 | "But it means **a corpus statistic that sums … is summing incommensurable units** — ARMH's record is a lexeme, ABCH's is a synonym-set" → "But it means that a corpus statistic that sums … is summing incommensurable units: ARMH's record is a lexeme, ABCH's a synonym-set" | bold; dash-as-copula → colon. The "It does mean … which sums" rewrite reverted after adversarial verify: "It does mean" is a concessive the author did not write and "which" for a restrictive clause is not the paper's usage |
| 22 | §4.4 | bold stripped from "gender apparatus", "inherited within the Hemacandra corpus"; "alphabetisation is — and just as measurable" → "alphabetisation is, and just as measurable" | emphasis bold; dash |
| 23 | §5, three paragraph lead-ins | ~~"**Order is the lexicographic act.**" / "**Incommensurable counts are a corpus hazard.**" / "**A bridge to the lineage.**" → italic run-in labels~~ | reverted after adversarial verify: §3 and §6 keep bold run-in leads, so italic here broke the paper's own convention; the italic-vs-bold house style is for copy-editing |
| 24 | §5, para 1 | "is **100 % macrostructure**" → "is 100 % macrostructure" | emphasis bold |
| 25 | §5, para 2 | ~~"the companion papers identify — convention must be a controlled variable" → "… identify: convention must be a controlled variable"~~ | reverted after adversarial verify: a colon after the verb "identify" reads as introducing what is identified, where the original dash appends an apposition; em-dash restored |
| 26 | §7, sentence 1 | ~~"The versified synonymic *kośa* is not a dictionary without structure; it is a dictionary that is *only* structure." → "The versified synonymic *kośa*, which every entry-level measure reads as structureless, is a dictionary that is *only* structure."~~ | reverted after adversarial verify: the relative clause added a claim ("every entry-level measure reads as structureless") that the original antithesis does not make; the antithesis is the paper's thesis statement and stays |
| 27 | §7 | "make their entry-counts incommensurable — a warning for any statistic" → "… incommensurable, a warning for any statistic" | dash-as-copula |
| 28 | §2.1 | "A **fifth** kośa" → "A fifth kośa" | emphasis bold |

Left alone on purpose: the bold sigla at first mention in §2.1 (**ARMH**, **ABCH**, **ACPH**, **ACSJ**, **NMMB**); the quoted "**Not applicable**" in §2.2 (it quotes the atlas dictionary pages verbatim); the bullet labels "**ARMH — exploded.**" / "**ABCH / ACPH / ACSJ — grouped.**" in §3 (list labels, not emphasis); the paired parenthetical dashes in §3, §4.3 and §6; the → arrows in the *kāṇḍa* orderings; "word-hoard" in the closing sentence (pass 1 named that close the paper's strongest sentence, and I agree); the five-clause anaphora of §7 (it mirrors the four findings and is the paper's own summary, not rhythm for its own sake).

### 2. Substance flags carried (not fixed)

1. **Gender-tag counting unit, §4.4 vs §6 (new).** §4.4 presents 13,284 as the additive total of distinct tag types (7,015 + 3,110 + 2,524 + 385 + 122 = 13,156, the rarer combinations making up the remainder), i.e. a combined tag such as *puṃklī* is counted once, as its own type. §6 says "The gender figures count combined tags toward each gender admitted", which describes the opposite scheme (a *puṃklī* tag would count once under masculine and once under neuter). Both cannot be true of the same 7,015 / 3,110 / 2,524. The memo re-verified the figures against the JSON but not the sentence in §6. A human must decide which counting scheme the extractor uses and correct the other sentence.
2. **Tags outnumber lexemes, §4.4 (new).** "every lexeme in ABCH is tagged for *liṅga*" sits next to 13,284 gender tags over 4,619 `<eid>` lexemes (Table 3), about 2.9 tags per lexeme. Either the tags are counted per word in the `<syns>` field (not per `<eid>`), or across the whole Hemacandra family, or lexemes carry several tags. The prose should name the unit; I did not touch it.
3. **Abstract density figure (new, minor).** The abstract reports "9.2 synonyms per verse" for ARMH as a whole, while §4.2 argues the synonym density is properly the *kāṇḍa* 1–4 mean (9.18) because *kāṇḍa* 5 is homonymic. Both round to 9.2, so nothing is false, but a referee who reads §4.2 may ask why the abstract uses the unqualified figure.
4. **"Hemacandra's corpus" vs Jinadeva (carried from memo m3).** The abstract calls ACSJ part of "Hemacandra's *Abhidhānacintāmaṇi* corpus" and §4.4 says "Hemacandra's koshas" while Table 1 and the References attribute the *-śiloñcha* to "Jinadeva (attr.)". "Hemacandra corpus" as a textual-tradition label is defensible; a one-word hedge ("the Hemacandra tradition") is the author's choice.
5. **Wilson 1819 verification (carried from pass 1 and memo M1).** §2.1 "[author to verify against Wilson's 1819 preface …]" and the References entry "[author to verify page range]" are still open; the "References (draft — author to finalise)" heading stays until they close. Load-bearing for §5 "A bridge to the lineage".
6. **Zachariae 1897 (carried from pass 1).** Still not added; same reason (fascicle numbering unverified).
7. **Amarakośa absent from the data (acknowledged in §6).** The keywords list "Amarakośa"; it is a comparandum, not data. Fine as is, noted so the keyword is a conscious choice.

### 3. Read-and-sign

About 30 minutes: read the abstract and §7 once against the pass-1 text (the two places where the rewrites are more than bold removal), then rule on flags 1 and 2, which are the only items that could change a sentence of substance. Proposed readiness: **4/5** (propose only; the two counting-unit flags and the Wilson verification stand between this draft and 5/5). Venue: no change, IJL primary with WSC 2027 as the indological alternate, as in pass 1. No submission before 2026-11-01.

_Dr. Mārcis Gasūns_
