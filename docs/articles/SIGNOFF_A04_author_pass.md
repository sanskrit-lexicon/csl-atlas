# SIGNOFF — A04 author-voice pass

_Created: 11-07-2026 · Last updated: 06-09-2026_

Author-voice pass over [`docs/articles/paper_indigenous_microstructure.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_indigenous_microstructure.md)
("Grammar Without Tags", P4), executed under handoff
[H680](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H680-Fable_csl-atlas_a04-a05-author-pass_11.07.26.md)
by Fable 5 (`claude-fable-5`) via the [`/paper-author-pass`](https://github.com/gasyoun/claude-config/blob/main/commands/paper-author-pass.md) skill,
paired with the A05 pass ([SIGNOFF_A05_author_pass.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/SIGNOFF_A05_author_pass.md))
per the handoff — the two papers shared referee [PR #200](https://github.com/sanskrit-lexicon/csl-atlas/pull/200).

**No number, claim, or citation was changed in this pass** — verified mechanically
against `origin/main` (numeral and citation-token multiset diff; the only additions are
the pass date, the signoff link, and the ORCID digits). **This manuscript needed the
least intervention of any paper in the series so far**: after the
[H119 referee pass](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/A04_review_fable5.md)
(every count verified exact), the voice was already consistently authorial — the pass
made exactly one call.

---

## 1. The byline gate — discharged, confirm on read-through

"Author: M. Gasūns (byline to finalise)" → the canonical author identity verbatim
(Mārcis Gasūns, independent scholar,
[ORCID 0000-0003-4513-884X](https://orcid.org/0000-0003-4513-884X), gasyoun@ya.ru),
plus the author-voice-pass provenance sentence beside the referee-pass one. Same block
as the A25 submission and the A37/A03 passes. Confirm it stands when you sign.

## 2. Voice calls made in this pass

| # | Location | Change | Rationale |
|---|---|---|---|
| V1 | Preamble | Canonical byline installed + pass-provenance sentence added | §1 above. |

**Considered and declined:**

- **§2 "The project has recorded this hazard…"** — "the project" as an actor recurs
  across the P-series (A03 §2 "the project's Phase-L0 known edge set", A05 §1 "the
  project roadmap") and reads as the research programme behind the series; changing it
  in one paper would *break* the terminology consistency the handoff asks for. Flag it
  series-wide at submission time if a referee-facing gloss is wanted.
- **Editorial "we"** — same call as every pass in this series.
- **The authorial cadences** ("Five dictionaries, four conventions, one grammatical
  tradition, measured."; "a zero is a question about the instrument before it is a fact
  about the dictionary") — exactly the voice a voice pass should preserve; untouched.

## 3. Standing flags carried over (not raised by this pass)

- **The A35↔A04↔A30 lead-paper `@DECIDE`** — the standing gate from the referee pass
  (which paper leads the shared derivational-apparatus cluster); must be ruled before
  submission, already tracked in GTD. This pass changed nothing about it.
- **Venue** — IJL primary, WSC 2027 alternate; still the author's pick.
- **"References (draft — author to finalise)"** heading marker — strip at submission
  after the primary-source details (Kṛdantarūpamālā edition, Yates 1846 tables,
  Śabda-Sāgara 1900) are checked; these are the least-standardised entries in the list.
- **Homonym-aware root key + second *Dhātudīpikā* witness** — honest future work (§6),
  no action owed.

## 4. Read-and-sign

1. Confirm the byline (§1) stands; V1 is the only voice call to veto.
2. Read the manuscript once end-to-end for IJL register (~30 min).
3. On sign-off, bump A04 to **5/5** in
   [`Uprava/ARTICLES.md`](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md); the
   A35↔A04↔A30 lead-paper `@DECIDE` and the venue pick remain their own items.

## Pass 2 — 06-09-2026 (Fable 5.1 `claude-fable-5-1`)

**Scope.** Second author-voice pass over [paper_indigenous_microstructure.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_indigenous_microstructure.md) under handoff [H3857](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3857-Fable_Uprava_all-articles-author-voice-pass-workflow_01.09.26.md), executed 06-09-2026 by Fable 5.1 (`claude-fable-5-1`). Voice, register and framing only; no number, claim or citation altered; mechanical drift gate (`tools/voice_drift_check.py --git origin/main`) CLEAN (141 numbers, 13 URLs, 107 IAST tokens, 15 headings, 17 table rows identical before and after). Pass 1 (above, 11-07-2026) installed the byline and made one call; this pass reads the body for what pass 1 declined or did not see and finds two classes of seam, the editorial "we" and emphasis-by-bold, plus a handful of single sentences. Nothing above this heading was rewritten.

### 1. Voice calls made — each may be vetoed

| # | Location | Call | Rationale |
|---|---|---|---|
| 1 | Abstract, §1, §3 (eight tokens) | Editorial "we" → first-person singular: "We show" → "I show"; "whose key we recover" → "whose key I recover"; "one we can decode" → "one I can decode"; "We extract" → "I extract"; "we measure … we ask" → "I measure … I ask"; "so we report" → "so I report" | Single-author paper; the H3857 brief and the sibling A01 pass 2 set the series on first-person singular, which reverses pass 1's "editorial we" declination. This is the one change that alters the paper's register; revert wholesale if IJL house style or your preference is the plural. |
| 2 | §1 para 2 | "This paper makes the opposite case with three measurements" → "I make the opposite case with three measurements" | The contribution statement, made singular with call 1; the three-measurement structure is unchanged. |
| 3 | Abstract, first sentence | "over the … *kośa*s of the … CDSL and they score close to zero" → "and every one of them scores close to zero" | **Reverted after adversarial verify:** "every one of them" is a stronger universal claim than the original "they" (meaning drift); original wording restored. |
| 4 | Abstract (three spans), §1 "zero", §2 "position and convention" and "absence of a European convention", §3 "cross-dictionary agreement", §4.1 "eight or fewer", §4.2 "1,737" and "1,498", §4.4 "85.5 %", "75.3 %", "81.4 %" | Emphasis bold removed; the figures and phrases stand as plain text | Journal abstracts and body prose are plain-text fields; twelve bold spans read as emphasis by markup rather than by sentence. Structural bold kept: **Keywords**, **Table 1/2** captions, the §5 run-in paragraph heads, the reference-block labels. |
| 5 | Abstract | "a tag-keyed measure simply cannot see" → "a tag-keyed measure cannot see" | Filler intensifier; the claim is the same without it. |
| 6 | §1 para 1 | "produces a striking and recurring result — the two great …" → "produces one recurring result: the two great …" | **Reverted after adversarial verify:** "striking" is the author's magnitude word, not filler — dropping it changed the claim's strength; noun phrase restored, only the dash → colon kept. |
| 7 | §2 para 1 | "conveyed by position and convention — the company a root keeps, …" → "conveyed by position and convention: the company a root keeps, …" | Em-dash introducing an enumeration; a colon does that job. |
| 8 | §3 para 2 | "reassigned the gaṇa markers" → "reassigned the *gaṇa* markers" | Italic consistency: *gaṇa* is italic in every other occurrence. |
| 9 | §4.2 | "recoverable from surface markers alone — a gain of 55 % and 28 %" → "…alone, a gain of 55 % and 28 %" | Em-dash as an appositive comma. |
| 10 | §4.3 | "agree in shape — *bhvādi* is the modal class in every one (…), exactly as the grammatical tradition predicts" → "agree in shape: *bhvādi* is … (…), as the grammatical tradition predicts" | Colon for the dash; "exactly" was the first of three "exactly"s in the paper and adds nothing to "as the tradition predicts". |
| 11 | §4.4 | "agree even more tightly — *Śabdakalpadruma*–*Vācaspatya* 92.8 % …" → "agree even more tightly: *Śabdakalpadruma*–*Vācaspatya* 92.8 % …" | Colon before the list of pairwise figures; the en-dashes inside the pair names are untouched. |
| 12 | §5 "For digital standards" | "exactly the kind of microstructural specificity the metalexicographic survey tradition anticipates" → "the kind of microstructural specificity …" | Second "exactly" trimmed; the third ("exactly as they must be for the citation apparatus", §5 para 1) is kept because there it carries the parallel. |

Header `Last updated` bumped and the status line extended with this pass and its signoff link; no other note added.

**Considered and declined (again):** §2 "The project has recorded this hazard qualitatively as the *zero-meaning* rule" — pass 1's series-consistency reasoning stands ("the project" is the research programme behind the P-series, used the same way in A03 and A05); switching it to "I have recorded" in one paper alone would break that. The authorial cadences pass 1 protected ("Five dictionaries, four conventions, one grammatical tradition, measured."; "a zero is a question about the instrument before it is a fact about the dictionary") are untouched. The em-dash parentheses that are genuine parentheses (abstract "— for part of speech, gender, or a tagged source apparatus —"; §1 "Third — and this is the validation —"; §6 "— same SLP1 spelling, different roots —") are kept; only dashes doing a colon's or a comma's work were changed.

### 2. Substance flags carried (not fixed)

1. **Abstract vs Table 1 footnote, "eight or fewer in every European dictionary".** The claim holds only with the ACC exclusion the Table 1 footnote states (Aufrecht's *Catalogus Catalogorum*, 10 root-entry hits, a catalogue not a lexicon). The abstract and §4.1 restate the claim without the carve-out; a referee who opens [`indigenous_by_dict.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/indigenous_by_dict.json) before reaching the footnote hits it. Whether the abstract needs "every European dictionary proper" or similar is the author's call (it is a claim-wording change).
2. **§6, "from 86.0 % to 81.2 %" vs the committed SKD–YAT pair rate.** The 03-07 memo verified that 86.0 % is the normalisation-experiment baseline in [MICROSTRUCTURE_ROOT_AGREEMENT.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_ROOT_AGREEMENT.md) (side-finding), distinct from the committed SKD–YAT pair rate of 0.8912. The manuscript never says the two are different measurements; a reader who computes the pair rate from `root_agreement.json` will ask why 86.0 ≠ 89.1. A half-sentence of provenance is a number-adjacent edit and therefore left to the author.
3. **§3, "forty-six *anubandha* letters".** The only count in the paper the 03-07 memo did not list as re-verified; it should be checked once against [MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md) before submission.
4. **§1, "forty-four dictionaries (43 at the 2026-06 measurement snapshot …)".** Pinned correctly per memo M3, but the same "as of" discipline the A01 pass flags applies: if the corpus grows again before submission, the prose count and the snapshot date need re-pinning together.
5. **Standing from pass 1, unchanged:** the A35↔A04↔A30 lead-paper `@DECIDE`; "References (draft — author to finalise)" with the three least-standardised primary entries (*Kṛdantarūpamālā* edition, Yates 1846, *Śabda-Sāgara* 1900); §6's homonym-aware root key and second *Dhātudīpikā* witness as honest future work.

### 3. Read-and-sign (~30 minutes)

1. Read the abstract, §1 and §3 once for the first-person switch (calls 1–2). It is the only register change in this pass; revert to the plural if that is the house style you want for the series (a find-and-replace of eight tokens).
2. Skim the abstract and §4.4 for the de-bolding (call 4), a formatting-only call; restore in the Markdown master if you want the emphasis kept there.
3. Rule on flag 1 (abstract wording of "eight or fewer") and flag 2 (a provenance half-sentence for 86.0 %); both are one-sentence edits that a voice pass may not make on its own.
4. **Proposed readiness: 4/5** (propose only). The remaining gates are authorial: the two rulings above, the A35↔A04↔A30 lead-paper decision, and the venue pick.
5. **Venue:** IJL primary with WSC 2027 as indological alternate, unchanged from the manuscript's own preamble; the paper is metalexicographic first (the zero-meaning rule as a measurement discipline) and IJL is the right first reader. No `@DECIDE` needed beyond the standing lead-paper one.

_Dr. Mārcis Gasūns_
