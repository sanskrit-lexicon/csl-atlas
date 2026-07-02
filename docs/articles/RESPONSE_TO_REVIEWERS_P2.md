# Response to Reviewers — P2 (A02, *Condensation, Not Inflation*)

_Created: 02-07-2026 · Last updated: 02-07-2026_

Response to
[REFEREE_P2_sense_inheritance.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/REFEREE_P2_sense_inheritance.md)
(2026-06-13), addressing the revised draft of
[paper_sense_inheritance.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_sense_inheritance.md).
Built from the concede/defend table in
[REVISION_BRIEF_P2_OBS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/REVISION_BRIEF_P2_OBS.md)
§1.4 (judgment pass: Fable 5, `claude-fable-5`, 2026-07-02), executed by a Sonnet-tier
session (2026-07-02).

---

## M1 — Significance testing

**Done — point to §4/§5.** The revised draft reports Pearson correlations with
sample sizes and *t*-statistics for H1 (§4: corpus *r* = 0.036, *t* = 0.11, df = 9;
panel *r* = 0.093, *t* = 0.49, df = 28), and two-proportion *z*-tests plus a
cluster-robust logistic regression with confidence intervals for H2 (§5). No claim in
the paper now rests on an unqualified correlation or proportion difference.

## M2 — Citation-vs-centrality confound

**Conceded and exceeded.** The confound analysis found a deeper flaw than the referee
named: not merely that citation correlates with sense centrality, but that 82 of the
84 cited ancestor senses sit on a single inheritance edge (Apte 1890 → 1957), so any
pooled estimate is dominated by that edge's composition. The within-edge test on that
one edge is not significant (0.768 vs 0.661, *z* = 1.80, *p* = 0.07), and the pooled
multi-edge odds ratio (≈ 3, *p* ≈ 0.01) is shown to be an artifact: it shifts from
≈ 1.75 to ≈ 3.0 when an *unrelated* edge's parser is corrected (the Yates semicolon
promotion, §3), without a single cited sense changing. The paper now reports H2 as an
**honest null with a methodological moral** (§5, §9): the pooled estimate fails in the
same way §3 shows legacy sense counts fail — it measures edge composition, not the
citation effect it names. The originally submitted positive claim is withdrawn.

## M3 — Fusion count resting on one lemma

**Conceded — delivered.** A new, read-only corpus-scale build
([`build-r2-kosa-fusion.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-kosa-fusion.mjs),
`data/lexico/r2_kosa_fusion.json`) walks every SKD and VCP record and classifies each
*iti*-unit as authority-terminal (fused), separable, or carrying no authority marker,
replacing the single-lemma *dharma* exemplar with a corpus count (§7). Verified
against the two exemplar records before trusting the aggregate: SKD *dharma*'s
synonym run does close in its own citation (*ity Amaraḥ*, authority-terminal), and the
classifier's output on the stratified sample is legible unit-by-unit (see the sample
rows in
[`r2_kosa_fusion_sample.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_kosa_fusion_sample.json)).
The corpus-scale result does **not** reproduce the exemplar's simple dictionary-level
contrast — SKD splits close to evenly (53.3 % fused / 46.7 % separable) while VCP
skews toward fusion (77.6 %), the opposite direction — so, exactly as the brief's
contingency instructed, §7's claim is re-scoped from a dictionary-level law to a
**record-type-dependent** finding (short encyclopaedic entry vs discursive
commentary). We report this honestly rather than tuning the classifier to recover the
exemplar's direction; §8 now carries the classifier's own limitations (pattern-based,
a documented but uncalibrated fusion threshold) and flags the outstanding human
adjudication sample
([`REVIEW_SKD_ITI_ADJUDICATION.html`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/REVIEW_SKD_ITI_ADJUDICATION.html))
as the next check on the classifier.

## M4 — Threshold and metric scope

**Conceded — delivered.** The committed threshold sweep (`h2ThresholdSensitivity` in
`data/lexico/r2_h2h3.json`, cutoffs 0.10–0.25) is now reported in §5: the naive gap
persists at roughly 3–6 points and the pooled estimate stays edge-composition-driven
at every cutoff, so the H2 null is not an artifact of the 0.15 threshold choice. The
metric-scope half of M4 (the survival metric's English-gloss scope) has moved from §8
into §3.1, where the Sanskrit-fingerprint alignment method is introduced, as a scope
sentence rather than a limitations after-thought.

## M5 — Three inheritance edges (n = 3)

**Defended as scoped.** The H3 claim was already stated as holding "on the three
edges where senses are countable on both sides" (§6); no general law across all
descent relationships is asserted. No change beyond the existing scoping language.

## M6 — Proxy ground truth

**Defended with cross-reference.** §8 now cites the independent MW gold-standard
instrument
([`GOLD_STANDARD.md`](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/GOLD_STANDARD.md),
MWS `docs-pass`) and states that the family ordering (§4) is robust to proxy error of
the documented ±13 % magnitude everywhere except the adjacent Cappeller–Petersburg
pair, on which no conclusion in the paper rests.

## M7 — Two-civilisations framing

**Conceded via the R1 corpus count**, with a correction to the framing itself. The
count promotes the claim from a single-lemma exemplar to a corpus measurement (M3
above), but the corpus measurement shows the phenomenon tracking **record type**
(short entry vs discursive commentary) rather than dictionary identity — so §7 no
longer asserts a dictionary-level "two civilisations" law. It instead reports that
sense/citation fusion occurs on a majority of authority-marked units in *both*
indigenous dictionaries (53–78 %), which is the more defensible and, we think, more
interesting structural claim: the European sense/apparatus distinction cannot be
imposed on the *kośa* register wherever a citation lands inside a unit's own
definitional run, and that happens often in both SKD and VCP, not as a fixed property
of either.

## Minor — References

Added two survival/decay citations to the lexical-obsolescence literature (Pagel,
Atkinson, and Meade 2007; Petersen et al. 2012), cited in §5 alongside the H2 null, and
flagged inline in the reference list for author verification of page ranges/DOIs
before submission, per the brief's instruction not to fabricate bibliographic detail.
Companion-paper cross-references (to *Redundancy and Descent* and *Two Citation
Registers*) were already present and are unchanged.

## Minor — Abstract density

**Done.** The abstract is rewritten to ≤ 250 words (from ~550), per §1.3 of the
revision brief: it keeps the corpus, the three questions, the H1 verdict with
family-trait numbers, the H3 verdict, one sentence for the H2 null, and one sentence
for the fusion count; it cuts the Yates 9→1-vs-5.7 narrative, the legacy-count
vindication detail, and the H1 regression internals, all of which remain in §3–§5.

---

_Dr. Mārcis Gasūns_
