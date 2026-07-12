# SIGNOFF — A08 author-voice pass

_Created: 11-07-2026 · Last updated: 11-07-2026_

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

_Dr. Mārcis Gasūns_
