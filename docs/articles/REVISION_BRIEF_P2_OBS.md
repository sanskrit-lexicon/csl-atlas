# Revision brief — P2 (A02) major revision, with OBS-R (A07) / OBS-C (A08) verdicts

_Created: 02-07-2026 · Last updated: 02-07-2026_

Status: the executable revision plan for
[paper_sense_inheritance.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_sense_inheritance.md)
(A02, *Lexicographica*, internal referee verdict "major revision"), plus one-paragraph
revision verdicts for
[paper_redundancy_and_descent.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_redundancy_and_descent.md)
(A07) and
[paper_citation_registers.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_citation_registers.md)
(A08). Written against the referee reports
[REFEREE_P2_sense_inheritance.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/REFEREE_P2_sense_inheritance.md)
and
[REFEREE_OBS_RC.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/REFEREE_OBS_RC.md)
(both 2026-06-13) **and the current drafts**, which have moved past those reports.
Intended executor: a Sonnet-tier session, no further judgment calls required — every
decision below is made here. Judgment pass: Fable 5 (`claude-fable-5`), 2026-07-02.

---

## Part 1 — A02: what the major revision argues

### 1.0 Where the draft actually stands

The referee report's pending table is stale. Since 2026-06-13 the draft has already
absorbed: **M1** (significance — CIs and *z*-tests in §4–§5), **M5** (the "no edge
expands" claim is scoped to "the three edges on which senses are countable on both
sides"), **M7** (the "two civilisations" framing is narrowed to the exemplar, with the
count named as next step), and most of the reference block (Zgusta, Wiegand,
Hausmann, Atkins & Rundell, Vogel are in).

More importantly, **M2 was answered by a deeper analysis that dissolved the H2
positive result**. The report's 0.762-vs-0.591 significant gap (*z* = 3.0) is gone;
the current draft finds 82 of 84 cited senses sit on a single edge (Apte 1890→1957),
the clean within-edge test is not significant (0.768 vs 0.661, *z* = 1.80,
*p* = 0.07), and the pooled logistic OR ≈ 3 is shown to be unstable — it moved from
≈ 1.75 to ≈ 3.0 when an *unrelated* edge's parser changed (the Yates semicolon
promotion). H2 is now an honest null. The revision must be built around that fact,
not around patching the old positive claim.

What genuinely remains: the SKD/VCP fusion **count** (M3/M7), the
threshold-sensitivity **report-out** (M4 — the data is already committed), the MW
gold-standard **cross-reference** (M6), the survival/decay **references**, and an
**abstract rewrite** (currently ~550 words; referees will balk).

### 1.1 The revised thesis

The submitted paper argued three positive findings. The revision argues **two robust
findings, one newly quantified register finding, and one honest null with a
methodological moral** — a stronger paper for a metalexicography venue than the
original, because the null demonstrates the method auditing itself.

1. **Granularity is a school signature, not a function of time** (H1). Flat pooled
   trend, family-fixed slopes flat-to-declining, the per-entry metric school-encoded.
   Unchanged.
2. **Descent copies or condenses; no measured edge expands** (H3). The title claim —
   *Condensation, Not Inflation* — is carried jointly by H1 + H3. Unchanged.
3. **The two Sanskrit lexicographic civilisations differ in whether sense and
   citation are separable categories at all** (§7) — **promoted from exemplar to
   corpus count** (the one new computation, §1.2 R1). With the count in hand, the
   "two civilisations" framing the referee flagged as the paper's thinnest support
   becomes its third quantitative result.
4. **H2 reframed as a cautionary result**: not "citation predicts survival" but "a
   digitised dictionary family can manufacture a spurious predictor." The pooled
   OR ≈ 3 (*p* ≈ 0.01) that shifts 1.75 → 3.0 under an unrelated parser change is the
   same lesson §3 teaches about legacy sense counts: an apparently solid number can
   be an artifact of composition, and the method catches its own would-be headline.
   State this explicitly in §5's closing paragraph and in the conclusion — one
   sentence each, e.g. "the pooled estimate fails in exactly the way §3 shows legacy
   sense counts fail: it measures composition, not the quantity it names."

### 1.2 What gets recomputed

**R1 — the SKD/VCP sense/citation-fusion count (the only new computation).**
Machinery already exists: the R2 indigenous *iti*-unit parser family
([build-r2-h1.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-h1.mjs)),
the SKD closing-authority window built for the promotion experiment
([build-r2-promotion-experiment.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-promotion-experiment.mjs)),
and the authority-citation signal inventory in
[m4_indigenous.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/m4_indigenous.py)
(*ity Amaraḥ* / *iti Medinī* / `…0` sigla patterns). Task: a **new, read-only** build
script (mirror the existing envelope pattern; output
`data/lexico/r2_kosa_fusion.json`) that walks every SKD and VCP record in
`csl-orig/v02` and classifies each *iti*-unit as:

- (a) **authority-terminal** — the synonym/definition run ends *in* the authority
  formula (sense and citation fused, the *dharma*-in-SKD pattern);
- (b) **separable** — definition unit distinct from its authority citation (the
  *dharma*-in-VCP pattern);
- (c) **other/no-authority**.

Report per dictionary: % of records containing ≥ 1 authority-marked unit, and among
authority-marked units the fused (a) vs separable (b) share. Expected shape (from the
exemplar): SKD high-fusion, VCP low-fusion — but report whatever comes out; if the
contrast does NOT hold at corpus scale, §7's claim must be re-scoped to "record-type
dependent" rather than dictionary-level, and the abstract sentence adjusted to match.
Wire into `package.json` beside the other `build-r2-*` scripts. Feeds: §7 (replace
"the evidence here is an exemplar … not yet a count" with the numbers), §8 (drop the
exemplar-limitation bullet, replace with the count's own caveats — the classifier is
pattern-based, borderline units exist), and one abstract sentence.

**R2 — report the committed threshold sweep (no computation).**
`h2ThresholdSensitivity` in
[r2_h2h3.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_h2h3.json)
already sweeps the survival cutoff over 0.10–0.25: the naive cited-vs-uncited gap
persists at roughly 3–6 points at every threshold, and the controlled OR is nominally
significant at every cutoff but — per the block's own summary — edge-concentration-
driven and not to be relied on (it rose with the YAT semicolon promotion, #126/#133,
without any cited sense changing). Add one sentence to §5 ("the pattern is invariant
to the 0.15 threshold: across cutoffs 0.10–0.25 the naive gap persists at 3–6 points
and the pooled estimate stays edge-driven") and one to the §8 threshold bullet. This
closes referee M4's first half; the second half (English-gloss scope) moves from §8
into §3.1 as a scope sentence where the fingerprint/overlap machinery is introduced.

**Nothing else is recomputed.** H1, H3, the checkpoint, and the promotion experiment
stand as committed.

### 1.3 What gets cut or tightened

- **Abstract: ~550 → ≤ 250 words.** Keep: the corpus and the three questions; H1
  verdict with the family-trait numbers (Benfey 2.42 / Petersburg 1.13 / indigenous
  1.00); H3 verdict (copy 0.906 / condense −3.07, −3.3; no expansion); one sentence
  for the H2 null ("cited senses survive somewhat more often, but the signal sits on
  one edge and is not significant there; citation is not established as an
  independent predictor"); one sentence for the fusion count (with R1's number).
  **Cut from the abstract**: the Yates 9→1-vs-5.7 parser-promotion narrative, the
  legacy-count vindication detail (PWG `<div>` nesting, Benfey truncation), and the
  H1 regression internals (partial slope, CI) — all of it already lives in §3–§5.
- **§5: compress the pooled-logistic exposition to one paragraph.** State the model,
  the instability demonstration (1.75 → 3.0), and the verdict; point to
  `h2Controlled` in the committed JSON for the full grid. The current three-paragraph
  treatment buries the reframing under mechanics.
- **Scope the novelty claim** (§5 end): "We know of no comparable quantitative
  treatment, positive or null, for any dictionary family" → "…for any historical
  dictionary family with documented lines of descent." Keeps the claim, shrinks the
  counter-example surface.
- Do **not** cut §3's promotion-experiment material — for this venue the
  method-vindication narrative (legacy counts as artifacts) is a selling point and
  now rhymes with the H2 moral.

### 1.4 Response-to-reviewers: concede vs defend

| Referee point | Line to take |
|---|---|
| M1 significance | Done — point to §4/§5. |
| M2 citation-vs-centrality confound | **Concede and exceed.** Say plainly: the confound analysis found a deeper flaw than the referee named (edge concentration), and the positive claim was withdrawn — H2 is reported as a null with the instability documented. Referees reward a withdrawn headline more than a defended one. |
| M3 fusion count on one lemma | **Concede — delivered.** The corpus-scale SKD/VCP count (R1) replaces the exemplar. |
| M4 threshold / metric scope | **Concede — delivered.** Sweep reported (R2); English-gloss scope stated in §3.1. |
| M5 n = 3 edges | **Defend as scoped.** The claim is already stated as "on the three edges where senses are countable on both sides"; no law is asserted. |
| M6 proxy ground truth | **Defend with cross-reference.** Cite the MW gold-standard instrument ([GOLD_STANDARD.md](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/GOLD_STANDARD.md), MWS `docs-pass`) and state the family ordering is robust to proxy error of the documented ±13 % magnitude (the gap between adjacent families exceeds it except Cappeller–Petersburg, which no conclusion rests on). |
| M7 two-civilisations framing | **Concede via R1.** Framing retained *because* it is now quantitative. |
| Minor: references | Add 2–4 survival/decay citations (lexical obsolescence / word-death literature; candidates: Petersen et al. 2012 *Statistical laws governing fluctuations in word use*, and a historical-lexicology treatment of obsolescence — **flag whatever is chosen for author verification**, do not fabricate page numbers). Fill the companion-paper cross-references. |
| Minor: abstract density | Done via §1.3. |

Deliverable: `docs/articles/RESPONSE_TO_REVIEWERS_P2.md` built from this table, one
numbered reply per referee point, quoting the revised text.

### 1.5 Execution checklist (ordered, for the Sonnet session)

1. Write the R1 fusion-count script + `data/lexico/r2_kosa_fusion.json`; verify
   against the two known exemplars (*dharma* in SKD → fused; in VCP → separable).
2. Rewrite §7 with the count; replace the §8 exemplar bullet.
3. R2: threshold sentence in §5; sweep sentence in §8; gloss-scope sentence in §3.1.
4. M6 cross-reference in §8 bullet 1.
5. Rewrite the abstract (≤ 250 words, per §1.3).
6. Compress §5 pooled-logistic paragraphs; add the H2-moral sentence to §5 and §9.
7. References: survival/decay additions (flagged for author), companion details.
8. Write `RESPONSE_TO_REVIEWERS_P2.md` from §1.4.
9. Update [PUBLICATIONS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/PUBLICATIONS.md)
   and `.ai_state.md`; deliver by PR.

**Guardrails (unchanged, this repo bites):** the R1 script is a *new, read-only*
reader over `csl-orig/v02` — it must NOT re-run or touch the R2
checkpoint/drift/promotion seeders or anything under `src/data/review/`
(human-reviewed; wiping it is unrecoverable). PR-only delivery; full blob URLs in
all authored Markdown; state model tier + exact version in the PR body.

---

## Part 2 — A07 (OBS-R, *Redundancy and Descent*) verdict

**Minor revision in substance; nothing threatens the core result.** All five referee
points were sound; two were applied, and the three that remain are cheap because the
numbers are latent in the committed generator
([headword_multiplicity.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/obs/headword_multiplicity.py)):
(1) **reverse-containment column** `b_in_a` in Table 2 — genuinely required, it is
the single change that converts "MW is a near-total absorber" from asserted to shown
(0.94 one way, small the other); (2) **denominators** — add |A| and |A∩B| beside each
ratio; (3) the **anusvāra/visarga fold-sensitivity number** — §6's "lowers the
independence figure by a few points … reported elsewhere" must become the actual
figure (run the fold, report 42.1 % → X %); a hand-wave where a number belongs is a
free referee hit. The references `[TODO]` block is the only other blocker. Reviewer
noise, safe to skip: the comparator-aggregate suggestion (one sentence *only if* a
published entry-to-lemma ratio for another portal surfaces during the reference pass
— do not go hunting); no further framing work, since R-M2 (value vs independence) and
R-M5 (unique vs attested) are already in the text. The 3.65 : 1 collapse, 57.9 %
redundancy, and the MW-absorber stemma need no re-derivation.

## Part 3 — A08 (OBS-C, *Two Citation Registers*) verdict

**Minor revision; one real task, two mechanical ones.** The referee is right that the
two-registers *symmetry* rests on the unbounded *iti* proxy, and the one substantive
task is C-M1's **hand-validation**: classify ~100 SKD *iti*-occurrences as citational
vs grammatical and report "≥ X % citational" — **do it inside the A02 fusion-count
annotation pass (Part 1 R1), which walks the same units; one effort, two papers**
(see Part 4). Also required: **C-M2**, fill Table 1's missing `<ls>` totals for
BEN/BHS/AP (trivial counts over `csl-orig/v02`; an incomplete headline table is an
easy referee target), and **C-M5**, the rank-swap number — where SKD ranks among the
43 dictionaries by *iti*-density versus dead-last by `<ls>` (one join over counts the
paper already has; it makes the mis-ranking warning land). C-M4's comparator is a
single sentence of context — satisfy it with the pre-digital expectation
(locator-bearing citation was the exception, not the rule, in pre-critical
lexicography) or state that no comparable corpus-level figure is published; do not
build a comparator corpus. C-M1's framing fix and C-M3 (resolvability bound) are
already applied. References `[TODO]` as for A07. The two-registers finding itself is
not at risk.

## Part 4 — Cross-paper synergy (do the SKD annotation once)

A02's R1 fusion count and A08's C-M1 *iti* validation read the **same SKD units**.
Execute as one pass: the R1 classifier emits, alongside the fusion classes, a random
~100-unit sample stratified over (a)/(b)/(c) into a review sheet; the human
citational-vs-grammatical adjudication of that sample is A08's "≥ X %" number, and it
doubles as the manual check on R1's pattern classifier. One annotation session
services both revisions and hardens both papers' proxies.

---

_Judgment pass by Fable 5 (`claude-fable-5`), 2026-07-02, for Dr. Mārcis Gasūns._

_Dr. Mārcis Gasūns_
