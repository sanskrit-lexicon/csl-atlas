# A03 (P3 Three Axes of Descent) — Hostile Pre-Submission Review

_Created: 03-07-2026 · Last updated: 03-07-2026_

**Paper:** [docs/articles/paper_three_axes_descent.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_three_axes_descent.md)
**Reviewer:** Fable 5 (`claude-fable-5`), adversarial referee pass per H114 (Fable window S12), in the A01/A16/A35 mold.
**Verdict: MINOR REVISION (data) / MAJOR on apparatus** — every number in Table 1 and the text re-verified exact against the committed packet; but the manuscript had **zero in-text citations**, three listed-but-unused references, two unfilled `[author to add]` slots, and one internal contradiction on the flagship row. All agent-doable; applied in this pass.

---

## 1. Figure re-verification — all 13 edges CONFIRMED

Independently re-derived from [`data/lexico/three_axis_comparison.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/three_axis_comparison.json) (13 `comparisonRows`, 4 `focusRows`):

- All 13 Content values (0.926/0.953/0.894/0.938/0.180/0.940/0.896/0.760/0.330/0.893/0.073/0.940/0.937) match `contentAxis.parentInChild` exactly.
- All 13 Convention values match `conventionAxis.conventionSimilarity`; all 13 Microstructure values match `microstructureAxis.microstructureSimilarity01` (incl. Yates→ŚS 0.9995 and AP90→AP 0.9569).
- §3.1 headline: PWG 106,083 / MW 194,084 / ∩ 94,776 → 0.8934 / 0.4883 / J 0.4614 — exact.
- Bootstrap: PWG→MW 0.013 and PWG→SCH 0.676 (paper's "0.68") — exact.
- §4.3 reading-class counts (3/2/4/4) and the §4 band counts (content 9/3/1; convention 3/7/3; microstructure 8/3/2) match `counts` exactly.

## 2. Major findings

**M1 — Zero in-text citations; the framing claim is unsourced.** The paper asserts "computational stemmatics of dictionaries usually collapses these into a single similarity or containment score" and opens with "Monier-Williams stands on the Petersburg lexicon" with no citation anywhere in the body — while the two directly relevant studies of *this very edge* (Zgusta 1988 on copying in MW; Hanneder 2020 reopening it) are absent even from the reference list, and the three references that ARE listed (Atkins & Rundell, Wiegand, Zgusta 1971) are never cited. A methods paper with an empty citation graph is a desk-reject at any DH or lexicography venue. *Fix (applied):* Zgusta 1988 + Hanneder 2020 added and cited (§1, §5.2); the three listed references wired in (§1, §3.3); see M2 for the two `[author to add]` slots.

**M2 — The two flagged reference slots are canonical and were left unfilled.** The bootstrap-support measure has one standard citation — Felsenstein (1985), the non-parametric bootstrap on phylogenies — and multi-dimensional textual descent has an established digital-stemmatology anchor — Andrews & Macé (2013), graph analysis beyond the tree of texts. *Fix (applied):* both added and cited at §3.2 and §1 respectively (the same move [PR #186](https://github.com/sanskrit-lexicon/csl-atlas/pull/186) made for A01).

**M3 — Internal contradiction on the flagship row.** Table 1 labels PWG → MW (1899) "content carried, convention **+ register** recoded", but the committed row shows the citation-and-grammar register is *not* recoded: `structuralRegisterSimilarity01` = **0.8823**, both dictionaries `tagged`, same dominant layer (`xref`); the low components are **convention** (0.371) and layer overlap (Jaccard 0.5). The machine class name fits its other member (Wilson → Yates, register sim 0.294) but misdescribes the flagship edge — a referee who opens the packet catches this immediately, and it matters because §4.1 is the paper's centrepiece. The double dissociation itself (content 0.89 vs convention 0.37/bootstrap 0.013) is untouched. *Fix (applied):* clarifying note under Table 1 + one sentence in §4.1 stating where the recoding does and does not live on this edge; the machine class label is quoted as machine output, not endorsed.

**M4 — Anti-salami: the series map omits P1 and OBS-R.** P1 (*Measuring the Dictionary Family*) now owns the metric definitions (its §3.1 containment-floor rule is re-stated here nearly verbatim) and OBS-R (*Redundancy and Descent*) owns the headword-containment matrix this paper's content axis reads from. Neither was in the companion list. *Fix (applied):* both added; §3.1 cross-cites P1 as the definition owner.

## 3. Minor findings

**m1 — Inconsistent edge naming.** Table 1 has "Petersburg → Monier-Williams" and "Petersburg → MW 1872" as separate rows; the former is the 1899 edition. *Fix (applied):* row renamed "Petersburg → MW 1899", §4.1 bullet aligned.

**m2 — Bootstrap support absent from Table 1** although §4.1's argument leans on it. *Fix (applied):* Bootstrap column added (13 values from the packet, all verified above).

**m3 — Relative artifact links.** The preamble and Table 1 source note used relative `../../data/…` links, which die when the manuscript is read anywhere but the repo blob view. *Fix (applied):* full blob URLs throughout.

## 4. Fixes applied in this pass

All M/m findings above, same branch/PR as this review. Remaining gates are **author-only**: byline; venue pick; optional larger adjudicated edge set (Limitations §6, already honest about the 13-edge scope).

## 5. Checked and sound (no action)

- The double dissociation (§4.1) is real in the committed data and correctly stated; directional containment vs Jaccard reasoning (§3.1) is exact; the floor discipline matches P1 §3.1 and A07's usage.
- Limitations are honest (size confound, unmodelled conventions invisible, genre/detector confounds, 13-edge European skew, readings are prompts not verdicts).
- No claim exceeds its stated bounds; the "machine interpretation prompt, not adjudicated lineage" framing is consistently maintained.

_Dr. Mārcis Gasūns_
