# A02 — author-pass sim sign-off memo

_Created: 08-07-2026 · Last updated: 06-09-2026_

**Paper:** [paper_sense_inheritance.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_sense_inheritance.md) (P2, *Condensation, Not Inflation*)
**Pass:** author-voice sim per [AUTHOR_PASS_SIM_PROTOCOL.md](https://github.com/gasyoun/Uprava/blob/main/docs/AUTHOR_PASS_SIM_PROTOCOL.md), executed 08-07-2026 by Fable 5 (`claude-fable-5`), handoff [H368](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H368-Fable_Uprava_author_pass_sim_protocol_batch1_08.07.26.md).

## What changed

- **Byline added** (Mārcis Gasūns · ORCID 0000-0003-4513-884X · gasyoun@ya.ru), replacing
  "Author: M. Gasūns (byline to finalise)"; the footer's "final byline" clause dropped.
- **Voice**: authorial we → first-person singular in four spots (abstract, §3.3, §5 ×2) —
  uniform with A01 ([#228](https://github.com/sanskrit-lexicon/csl-atlas/pull/228)) and A06
  ([#229](https://github.com/sanskrit-lexicon/csl-atlas/pull/229)).
- **Status block** records this pass and links this memo.
- Abstract left structurally as-is — it was already cut to 244 words in the 02-07 revision
  and its honest re-scoping language (the §7 record-type finding) is load-bearing; the arc
  §1→§9 reads clean. No claim, number, table, or citation added or altered.

## What you must verify (~25 min)

1. **The voice call** (same as A01/A06).
2. **"forty-three dictionaries" (§1)** — the paper pins to the 2026-06 snapshot; A01/A04
   now say 44 (post-NMMB 2026-07 envelope). I did NOT change it because the committed R2
   artifacts underlying this paper are the 2026-06 build; confirm the snapshot framing is
   the one you want, or re-pin after the next data refresh.
3. **Two references still flagged in-text for author verification** (left per guardrail):
   Pagel/Atkinson/Meade 2007 and Petersen et al. 2012 — page range + DOI vs the published
   articles.
4. **Outstanding data gate (not prose):** the ~100-row SKD *iti* adjudication
   ([REVIEW_SKD_ITI_ADJUDICATION.html](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/REVIEW_SKD_ITI_ADJUDICATION.html))
   — §7's 53 %/78 % figures may sharpen after your vote. The paper already labels the
   classifier honestly (§8), so submission need not wait on it, but signing before voting
   means accepting that caveat as published text.

## Flagged suggestions (NOT applied)

- None beyond the standing in-text flags above.

## Venue recommendation

**Lexicographica primary — keep.** De Gruyter journal, same publisher family as the locked
monograph series (Lexicographica Series Maior), and this is the chapter the book plan wants
"under review" at proposal time — submitting here strengthens the Brill/De Gruyter proposal.
IJL stays the alternate. No change proposed.

## Pass 2 — 06-09-2026 (Fable 5.1 `claude-fable-5-1`)

**Scope.** Second author-voice pass over [paper_sense_inheritance.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_sense_inheritance.md)
under handoff [H3857](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3857-Fable_Uprava_all-articles-author-voice-pass-workflow_01.09.26.md),
executed 06-09-2026 by Fable 5.1 (`claude-fable-5-1`). Voice, register and framing
only; no number, claim, citation, table cell, heading or Sanskrit token altered;
mechanical drift gate (`tools/voice_drift_check.py --git origin/main`) CLEAN on all
eight categories (310 numbers, 20 URLs, 46 IAST tokens, 15 headings, 24 table rows
identical before and after). Pass 1 (08-07-2026) above is untouched and its calls
stand.

## 1. Voice calls made — each may be vetoed

| # | Location | Call | Rationale |
|---|---|---|---|
| 1 | Abstract, §3.2, §3.3, §4, §5, §6, §7 | Emphasis bold removed from figures and claims (five bold spans in the abstract; `**r = 0.036**`, `**0.768**`, `**not significant**`, `**genuine condensation**`, `**No measured edge adds senses**`, `**opposite**`, the re-scoped §7 finding, and similar). Bold kept only where a term is introduced (*parser families*, *Sanskrit fingerprint*, *review checkpoint*, *additive experiment*), on the three run-in paragraph heads of §3.3, and in table captions. | Bold-every-other-phrase is the slide-deck register; a Lexicographica abstract carries no bold, and the numbers carry their own weight. |
| 2 | Abstract | Reflowed; "Descendants copy or condense, never expand" → "copy or condense and never expand"; "if anything it declines" joined with "and". | Line-wrap residue from the 02-07 cut; the triplet-with-a-twist cadence read as rhetoric. |
| 3 | §1 | "This paper asks three questions of that record" → "I put three questions to that record". | First-person singular is the paper's voice elsewhere (abstract, §3.3, §5); the one impersonal pivot stood out. |
| 4 | §1, end | One contribution sentence added: "The contribution is a sense-level measurement of inheritance, made with an alignment that runs through shared Sanskrit material rather than translation, on a dictionary family whose lines of descent are documented." | The brief asks for one explicit singular contribution statement; the paper had a results summary but no sentence naming what it contributes. Contains no number, comparison or new claim — it restates §1 and §3.1. Veto if you prefer the contribution to stay implicit. |
| 5 | §3.3 | "The European sense/apparatus distinction is not wrong for SKD — it is **inapplicable**" → "For SKD the European sense/apparatus distinction is inapplicable rather than wrong". | The "not X — it is Y" figure with bold on Y is the de-AI checklist's cliché; the contrast survives without the cadence. |
| 6 | §3.3, closing paragraph | "This reframes the experiment's contribution … it is **demonstrably more faithful** … than the counts it is checked against — and" → "This reframes what the experiment shows … the rows above show it to be the more faithful to the printed dictionary, and". | "Demonstrably" is an intensifier standing in for the demonstration Table 2 already makes; "contribution" here collided with the new §1 contribution sentence. Claim strength unchanged (the rows are the demonstration). |
| 7 | §5 | "The honest reading is therefore that citation **co-varies**" → "The reading the data support is that citation co-varies". | "Honest reading" is fake candour; what makes the reading honest is the data, so say that. |
| 8 | §5, last sentence | Reflowed only (a three-line orphan "§3 shows legacy sense / counts fail" left by an earlier edit). | Cosmetic. |
| 9 | §6, last sentence | "The stronger earlier claim that the citation apparatus *steers* what survives is qualified by §5 and is not relied on here" → "The stronger claim that the citation apparatus *steers* what survives is not made here; §5 qualifies it". | **Reverted after adversarial verify:** the rewrite shifted the meaning from "qualified by §5, not relied on" to "not made here" — a stronger disavowal than the original; original wording restored. |
| 10 | §7, opening | "a floor that earlier phases of this project have repeatedly warned against misreading" → "a floor that is easily misread". | **Reverted after adversarial verify:** dropping "earlier phases of this project have repeatedly warned" removed a substantive provenance claim (the warning is a project result, not a generic caution); original wording restored, only the de-bolding of "absence of European conventions" kept. |
| 11 | §7, second paragraph | "A new read-only build (…) walks every SKD and VCP record" → "A build script (…) walks". | **Reverted after adversarial verify:** "new" and "read-only" are substantive method qualifiers (a fresh, non-mutating pass over the corpus), not repository trivia; original wording restored. |
| 12 | §9 | The 90-word sentence split after "(*z* = 1.80, *p* = 0.07)"; "borrows strength across edges to manufacture apparent significance fails in exactly the way §3 shows legacy sense counts fail — it measures edge composition, not the citation effect it names" → "owes its apparent significance to edge composition, not to the citation effect it names — the same failure §3 finds in the legacy sense counts". | §9 repeated §5's closing sentence almost verbatim; "manufacture" was the one rhetorical verb in the conclusion. The §3 parallel and every figure stay. |
| 13 | Byline | ", independent scholar" inserted after the name. | Aligns with the standing EN byline form; ORCID and e-mail unchanged. |
| 14 | Header / status paragraph | `Last updated` bumped to 06-09-2026; this pass appended to the status paragraph's pass list, linking this memo. | Brief's header-note rule. |

Not touched (deliberately): the two term-defining bold spans in §3.1, the three run-in heads of §3.3, all headings, all tables, the `[**Flagged for author verification** …]` notes inside two reference entries (reference entries are off-limits to this pass; see flag 2 below).

## 2. Substance flags carried (not fixed)

1. **"forty-three dictionaries" (§1)** — carried from pass 1: A01/A04 say 44 (post-NMMB 2026-07 envelope); this paper pins to the 2026-06 R2 snapshot. Still unresolved; confirm the snapshot framing or re-pin after the next data refresh.
2. **Pagel, Atkinson & Meade 2007 and Petersen et al. 2012** — still carry the in-text "Flagged for author verification" note (page range + DOI), and the Pagel entry embeds referee-memo residue ("§1.4 M-minor") that will not survive typesetting. Reference entries are outside this pass's remit; a human must verify and strip.
3. **Panel size wording** — §4 says "a fixed panel of 28–30 simple nouns" and reports the panel correlation with df = 28 (n = 30); §5 and Table 3 say "28-noun panel". Both may be correct (per-dictionary availability vs. the edge panel), but a referee will ask; one sentence reconciling them would close it.
4. **Table 3 drift precision** — Apte 1890 → 1957 shows means "10.8 → 7.8" (one decimal) against drift "−3.07" (two decimals); the arithmetic on the rounded means gives −3.0. Presumably the drift is computed on unrounded means; a consistent decimal policy or a footnote would pre-empt the question. Wilson → Yates ("9 → 5.7", −3.3) is consistent.
5. **SKD *iti* adjudication (outstanding data gate)** — carried from pass 1: the ~100-row [REVIEW_SKD_ITI_ADJUDICATION.html](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/REVIEW_SKD_ITI_ADJUDICATION.html) vote is still outstanding; §7's 53 %/78 % and §8's caveat are unchanged.
6. **Abstract vs. §7 percentages** — the abstract's "SKD is 53 % fused, VCP 78 %" are the *among authority-marked units* shares (53.3 % / 77.6 %), while §7 also reports record-level shares (43.3 % / 76.7 %). Correct as written, but the abstract does not say which denominator it uses; a referee may read 53 % as a record-level figure.
7. **§8, first bullet** — "per-dictionary values sit within 13 % of the archived baseline" cites the MWS `docs-pass` branch `GOLD_STANDARD.md`; a branch URL will rot at submission time. Not a prose matter; noted for the camera-ready pass.

## 3. Read-and-sign

- **Time:** ~30 minutes — read §1 (the added contribution sentence), the abstract without its bold, and §9 as split; skim the rest of the diff for the bold removals.
- **Proposed readiness (propose only):** 4/5. Prose is submission-shaped; the block is the two unverified reference entries (flag 2) and the outstanding SKD adjudication (flag 5), neither of which this pass can clear.
- **Venue:** Lexicographica primary, IJL alternate — no change from pass 1. No submission before 2026-11-01.

_Dr. Mārcis Gasūns_
