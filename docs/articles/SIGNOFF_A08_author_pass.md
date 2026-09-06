# SIGNOFF — A08 author-voice pass

_Created: 11-07-2026 · Last updated: 06-09-2026_

Author-voice pass over [`docs/articles/paper_citation_registers.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_citation_registers.md)
("Two Citation Registers", OBS-C), executed under handoff
[H682](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H682-Fable_Uprava_fable-untouched-next-article_11.07.26.md)
by Fable 5 (`claude-fable-5`) via the [`/paper-author-pass`](https://github.com/gasyoun/claude-config/blob/main/commands/paper-author-pass.md) skill,
following the same-day A03/A04/A05 passes
([SIGNOFF_A04_author_pass.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/SIGNOFF_A04_author_pass.md)).
Substance basis: the 2026-06-13 referee memo
([REFEREE_OBS_RC.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/REFEREE_OBS_RC.md) §B)
whose pending [author] items C-M2 (Table 1 totals), C-M4 (comparator sentence, §4.2)
and C-M5 (rank-swap quantified, §4.4 "2nd of 44") were applied in the 2026-07-02
revision ([PR #184](https://github.com/sanskrit-lexicon/csl-atlas/pull/184)), with all
counts regenerated from the committed artifact in
[PR #187](https://github.com/sanskrit-lexicon/csl-atlas/pull/187).

**No number, claim, or citation was changed in this pass** — verified mechanically
against `origin/main` (numeral-token multiset diff; the only additions are the
referee/revision/pass provenance dates, the PR numbers, and the ORCID digits). Like
A04, this manuscript needed minimal intervention: the voice was already consistently
authorial after two substance rounds — three calls, two of them mechanical.

---

## 1. The byline gate — discharged, confirm on read-through

"Author: M. Gasūns (byline to finalise)" → the canonical author identity verbatim
(Mārcis Gasūns, independent scholar,
[ORCID 0000-0003-4513-884X](https://orcid.org/0000-0003-4513-884X), gasyoun@ya.ru),
plus the referee/revision/author-pass provenance sentences. Same block as the A25
submission and the A03/A04/A05 passes. Confirm it stands when you sign.

## 2. Voice calls made in this pass

| # | Location | Change | Rationale |
|---|---|---|---|
| V1 | Preamble | Canonical byline installed + provenance sentences (referee memo, revision PRs, this pass) | §1 above. |
| V2 | Abstract, final sentence | Re-wrapped "Per-␊dictionary" → "Per-dictionary" on one line | The hyphen sat at a line break and rendered as "Per- dictionary" — a typo in any venue export. |
| V3 | §4.4 | "all forty-four discovered CDSL dictionaries" → "all forty-four CDSL dictionaries" | "Discovered" is pipeline idiom (auto-discovered source files); the count is the same 44 the abstract and §1 already name. Veto if the auto-discovery nuance should stay reader-visible. |

**Considered and declined:**

- **"The project" as actor** (§2.1 "A standing effort within the project…", §2.2 "The
  project has already recorded…") — the same series-wide convention the A04 pass kept;
  changing it in one paper breaks cross-paper terminology. Flag series-wide at
  submission if a referee-facing gloss is wanted.
- **"Committed artifact" repo idiom** (preamble, Table 1 note) — the series' provenance
  convention; at submission the GitHub-blob pointers become archived-dataset citations
  anyway, so the rewording belongs to that pass, not this one.
- **"Critically," in the abstract** — legitimate emphasis introducing the paper's
  principal finding, not filler; kept.
- **Editorial "we"** — same call as every pass in this series.
- **The authorial cadences** ("The mis-ranking is not a rhetorical figure but a
  measured swap."; "different *in kind*"; "two technologies of authority") — exactly
  what a voice pass preserves; untouched.

## 3. Standing flags carried over (not raised by this pass)

- **SKD *iti* hand-validation (referee C-M1, the "SKD adjudication" gate)** — the
  adjudication sheet
  [REVIEW_SKD_ITI_ADJUDICATION.html](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/REVIEW_SKD_ITI_ADJUDICATION.html)
  exists but has **no decisions file yet** — a human classifies ~100 SKD *iti*
  occurrences as citational vs grammatical, converting the §3.3 indicator into
  "≥ X % of *iti* are citations" and letting the two registers be compared on equal
  footing. The manuscript's hedges ("indicator, not an exact citation count", "bounds
  their citation rate from above") are honest without it, but this is the one referee
  item still open between 4/5 and 5/5 alongside the read-and-sign.
- **"References (draft — author to finalise)"** heading marker — strip at submission;
  the Benfey entry still lacks its title and the *Kṛdantarūpamālā* needs edition
  details; these are the least-standardised entries in the list.
- **Venue** — IJL (International Journal of Lexicography), per
  [`ARTICLES.md`](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md); still the
  author's pick.
- **Register unification at the work level** (§6) — honest future work, no action owed.

## 4. Read-and-sign

1. Confirm the byline (§1) stands; V3 is the only judgment call to veto (V1/V2 are
   mechanical).
2. Read the manuscript once end-to-end for IJL register (~30 min).
3. Vote the SKD *iti* adjudication sheet (§3, first flag) — or explicitly defer it to
   the submission pass.
4. On sign-off, bump A08 to **5/5** in
   [`Uprava/ARTICLES.md`](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md);
   the venue confirmation remains its own item.

---

## Pass 2 — 06-09-2026 (Fable 5.1 `claude-fable-5-1`)

Second author-voice pass over
[`docs/articles/paper_citation_registers.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_citation_registers.md) under handoff
[H3857](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3857-Fable_Uprava_all-articles-author-voice-pass-workflow_01.09.26.md) (all-articles author-voice pass), Fable 5.1 (`claude-fable-5-1`),
06-09-2026. Scope: voice, register and framing only; no number, claim or citation
altered; mechanical drift gate ([`voice_drift_check.py`](https://github.com/gasyoun/Uprava/blob/main/tools/voice_drift_check.py) against
`origin/main`) CLEAN — 122 numbers, 14 URLs, 70 IAST tokens, 21 headings, 12 table
rows count-identical before and after. Pass 1 above is untouched; its three calls
stand. This pass reverses two of Pass 1's "considered and declined" items (editorial
*we*; "Critically,") because the H3857 batch brief sets first-person singular and the
de-AI list as the series standard, and the sibling passes of the same day (A01, A02,
A04, A05, A06) made the same switch — series consistency now points the other way.

### 1. Voice calls made — each may be vetoed

| # | Location | Call | Rationale |
|---|---|---|---|
| P2-1 | Preamble | `Last updated` bumped to 06-09-2026; status paragraph gains "second author-voice pass 2026-09-06 (Pass 2 in the same SIGNOFF)" | Brief's header note; ISO date form kept to match the paragraph's other three dates. |
| P2-2 | Abstract, §1, §3.1, §3.3, §4.2, §4.3 (9 places) | Editorial *we* → first-person singular (*I answer*, *I count*, *I conclude*, *I ask*, *I argue*, *I extract*, *I count*, *I am not aware*, *I adjudicated*) | Single-author paper; IJL accepts *I*; brief and same-day sibling passes (A01/A02/A04/A05/A06) use it. Veto restores *we* in nine places, no other text depends on it. |
| P2-3 | Abstract | "Critically, the `<ls>` tally measures only one citation register." → "But the `<ls>` tally …" | "Critically/crucially" is on the filler-intensifier list; the turn is carried by the contrast itself. Pass 1 kept it as emphasis — reversed here, veto if the emphasis is wanted back. |
| P2-4 | Abstract + §3.1, §3.2, §4.1–§4.5, §7 (24 spans) | Inline bold stripped from prose (numbers, headline phrases, "up to"); Table captions, `Keywords:` and the three §5 run-in heads keep bold; the four defined terms in §3.1–§3.2 (*locator-bearing*, *bare*, *diacritic-and-case fold*, *abbreviation-family*) now italic as term definitions | Seven bold spans in one abstract and bolded numbers throughout read as a slide deck; IJL sets no bold in running text. Words unchanged. Veto restores bold wholesale (the diff is mechanical). |
| P2-5 | §4.2, comparator sentence | One 70-word sentence with a nested em-dash pair split at "qualitative, not quantitative." into two; the trailing "— so a ~59 % locator rate" becomes ", so a ~59 % locator rate" | Two stacked parentheses inside one clause; every word of the claim (exception-not-rule, bare authority names, "already exceeds … rather than falling short") kept. |
| P2-6 | §4.2 | "tight, ≈58.6–59.3 %, and robust" → "and stable" | "robust" is on the de-AI list; "stable" says the same thing at the same strength (the preceding clause has just shown a 0.7-point move). Veto if "robust" is preferred in its statistical sense. |
| P2-7 | §7, first sentence | Clause order: "all drawing on a working apparatus of roughly two thousand sources" moved to attach to the 1.2 million citations; "Up to a tight majority of them — 59.3 % …" starts its own sentence | As written, "all drawing on" attached grammatically to the 507,000 bare abbreviations; the apparatus is the source pool of the whole `<ls>` register (§4.3, abstract). Every token kept, including "up to", "at least", "all". See flag F5. |

Considered and left alone: "The mis-ranking is not a rhetorical figure but a measured
swap." and "a finding of comparative metalexicography, not merely a markup detail"
(Pass 1 named these as the author's cadence; "not merely" is a scope qualifier and
untouchable); "the project" as actor (§2.1, §2.2 — series convention); the
"committed artifact" idiom (submission pass); the four italicised questions of §1.

### 2. Substance flags carried (not fixed)

1. **F1 — SKD *iti* hand-validation (referee C-M1) still open.** The sheet
   [REVIEW_SKD_ITI_ADJUDICATION.html](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/REVIEW_SKD_ITI_ADJUDICATION.html) exists on `main`; no decisions file
   sits beside it as of 06-09-2026. Unchanged since Pass 1; still the one referee item
   between 4/5 and 5/5.
2. **F2 — abstract poses two questions, §1 poses three plus a prior fourth.** "I answer
   both questions" (abstract) vs "I ask three questions … A fourth question proves to be
   prior" (§1). Not a contradiction — the abstract folds volume and locator share into
   one — but a referee may ask for the count to match. Voice-neutral; left for the author.
3. **F3 — two snapshots in one paragraph (§4.2).** The 0.7-point siglum penalty and the
   "59.8 % → 59.1 %" pair are the 2026-06 siglum pass; the 59.3 % / 738,173 / 507,000
   headline is the 2026-07 artifact; the band ≈58.6–59.3 % applies the 06 penalty to
   the 07 rate. The preamble declares the two snapshots, but the §4.2 sentence should say
   so in-line before submission, or the band be regenerated from one snapshot.
4. **F4 — §4.3 siglum-inventory figures (~13,000 / ~9,000 / 2,166) are the 2026-06
   pass** while everything else is 2026-07; the preamble notes this, the abstract does
   not. Regenerate or footnote at submission.
5. **F5 — "all drawing on a working apparatus of roughly two thousand sources" (§7).**
   §4.3 says the 2,166 sources cited ten or more times resolve "the great majority" of
   the apparatus, with a long tail of rare sigla behind them; "all … drawing on" the
   two-thousand set is stronger than §4.3 supports. I kept every word (scope word "all"
   is untouchable) and only moved the clause; the author may want "most" or "drawing
   overwhelmingly on" here.
6. **F6 — Table 1 row order has no stated key** (PWG, MW, BEN, BHS, AP is neither by
   total nor by density). Table rows are untouchable in this pass; a one-word caption
   note ("by citation total" would require reordering) or a re-sort at submission.
7. **F7 — §5 "working set of ~2,000 sources" vs §4.3 "2,166" and §7 "roughly two
   thousand"** — three roundings of one figure; harmless, but IJL copy-editors query it.
8. **F8 — References still "draft — author to finalise"**: Benfey lacks a title,
   *Kṛdantarūpamālā* lacks edition details (carried from Pass 1).

### 3. Read-and-sign

1. Read the diff of this pass once (~30 minutes with the manuscript): P2-2 (*I*), P2-3
   ("But"), P2-6 ("stable") and P2-7 (clause order) are the four judgment calls; P2-1,
   P2-4 and P2-5 are mechanical.
2. Rule on F5 (the "all drawing on" strength) and F2 (two vs three questions) — both are
   one-word author decisions this pass may not make.
3. Vote the SKD *iti* sheet (F1) or defer it explicitly to the submission pass.
4. Proposed readiness after sign-off: **4/5 → 5/5 proposed, not set** in
   [`Uprava/ARTICLES.md`](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) — the bump waits on F1 and the read-through. Venue:
   IJL, unchanged. No submission before 2026-11-01.

_Dr. Mārcis Gasūns_
