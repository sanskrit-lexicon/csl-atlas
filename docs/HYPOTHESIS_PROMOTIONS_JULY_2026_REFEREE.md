# July 2026 hypothesis promotions — hostile referee report (H1866)

_Created: 05-08-2026 · Last updated: 05-08-2026_

Referee: Fable 5 (`claude-fable-5`), handoff [H1866](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1866-Fable_csl-atlas_july-hypothesis-promotions-hostile-referee_29.07.26.md).
Posture: **default REFUTED** — every promotion had to survive on its committed evidence,
not on having been promoted. Method: every figure asserted in the
[HYPOTHESIS_INDEX.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/HYPOTHESIS_INDEX.md)
row was re-read from the committed artifact it cites (JSON re-parse, not prose re-read);
each promotion's source files were checked against every later July commit for
silently-changed inputs.

## Scope — what counts as a July promotion

From `git log --since=2026-07-01 --until=2026-08-01 -- docs/HYPOTHESIS_INDEX.md`, nine
hypotheses entered or moved into the Type 1 (tested) table in July:

| # | ID | Promoted | PR | Recorded verdict |
|---|---|---|---|---|
| 1 | THREE-AXIS-INDEP | 03-07-2026 | [#193](https://github.com/sanskrit-lexicon/csl-atlas/pull/193) | Supported (descriptive, n=13) |
| 2 | CANON-CORE (PH1) | 07-07-2026 | [#225](https://github.com/sanskrit-lexicon/csl-atlas/pull/225) | Refuted — modular, not nested |
| 3 | CITE-4AXIS (PH2) | 08-07-2026 | [#233](https://github.com/sanskrit-lexicon/csl-atlas/pull/233) | Independence not rejected (n=5) |
| 4 | GHOST-STOCK (PH4) | 25-07-2026 | [#300](https://github.com/sanskrit-lexicon/csl-atlas/pull/300) | Main claim supported; sub-claim reversed |
| 5 | HERITAGE-WIT (PH6) | 25-07-2026 | [#300](https://github.com/sanskrit-lexicon/csl-atlas/pull/300) | Supported |
| 6 | HEAP-SAT (PH8) | 25-07-2026 | [#304](https://github.com/sanskrit-lexicon/csl-atlas/pull/304) | Growth law supported; break descriptive; <5% sub-claim refuted |
| 7 | FREQ-STRAT (PH3) | 25-07-2026 | [#304](https://github.com/sanskrit-lexicon/csl-atlas/pull/304) | Signatures supported; family sub-claim not supported |
| 8 | ORTHO-CLOCK (PH5) | 26-07-2026 | [#308](https://github.com/sanskrit-lexicon/csl-atlas/pull/308) | Clock inconclusive/house-style; descent refuted; era-composition robust |
| 9 | L0-GQD | 26-07-2026 | [#312](https://github.com/sanskrit-lexicon/csl-atlas/pull/312) | Both parts supported |

Not in scope: M7-ROOT-AGREE κ re-grade, APPARATUS-NOT-ERRORS reproducibility audit and
the OBS-R/OBS-C regenerations (03–17 July) are *status updates to already-promoted rows*,
not promotions; PET-MW-CITE (measured 29-07, [#325](https://github.com/sanskrit-lexicon/csl-atlas/pull/325))
remains Type 2, unpromoted.

## Verdict table

| ID | Referee verdict | Figures re-checked | Discrepancies |
|---|---|---|---|
| THREE-AXIS-INDEP | **CONFIRMED** | 8/8 match | none (one unreported sign flip, see below) |
| CANON-CORE | **CONFIRMED — with two mandatory row repairs** | 9/9 match | index row structurally defective + MW-lane caveat missing |
| CITE-4AXIS | **CONFIRMED** | 10/10 match | none |
| GHOST-STOCK | **CONFIRMED** | 14/14 match | none |
| HERITAGE-WIT | **CONFIRMED** | 9/9 match | none |
| HEAP-SAT | **CONFIRMED** | 14/14 match | one wording slippage (SKD vs "specialised") |
| FREQ-STRAT | **CONFIRMED** | 13/13 match | none |
| ORTHO-CLOCK | **CONFIRMED** | 13/13 match | one unreported sensitivity (all-map vs dated-map) |
| L0-GQD | **CONFIRMED** | 12/12 match | none |

**Demotions: none.** All nine recorded verdicts survive adversarial re-check against
their committed artifacts. **Promotions resting on since-changed figures: none** (checked
explicitly, §"Staleness sweep" below).

## Per-promotion checks

### 1. THREE-AXIS-INDEP — CONFIRMED

Artifact [`data/lexico/three_axis_independence.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/three_axis_independence.json)
(generated 03-07-2026). Row vs artifact: content~convention 0.15 → 0.146 ✓;
content~micro 0.26 → 0.262 ✓; convention~micro −0.09 → −0.088 ✓; n=13 ✓ (threshold
0.553 correctly stated for n=13, p=0.05); bootstrap~convention r=0.92 → 0.923 ✓;
register~layers r=0.85 → 0.854 ✓. The row's own "descriptive, not confirmatory" framing
is warranted and sufficient.

*Referee note (no action forced):* the Spearman companions flip sign on content~micro
(Pearson +0.262, Spearman −0.415) — rank-vs-linear instability at n=13 that the row does
not mention. It *strengthens* the row's descriptive-only framing rather than undermining
any claim, so it is recorded here, not in the row.

### 2. CANON-CORE — CONFIRMED, with two mandatory row repairs

Artifact [`src/data/citations/citation_canon.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/citations/citation_canon.json)
(generated 07-07-2026). Row vs artifact: NODF 24.4 → 24.441, null mean 29.0 → 28.976,
p=1 ✓; Barber Q 0.50 → 0.4995, null 0.43 → 0.4295, p=0.001 (1,000 fixed-fixed nulls,
Dror et al. protocol) ✓; 11 dicts × 912 texts, 1,701 edges ✓; 608/912 single-dictionary
texts ✓; Rāmāyaṇa in 9 dicts ✓; "best of 6 restarts" label-propagation heuristic ✓. The
refuted-modular *direction* is strongly supported: opposite-tail significance (p=0.001 vs
p=1.0) under a degree-preserving null, with the heuristic-Q caveat already recorded in the
artifact.

**Repair 1 — structural row defect.** The index row had **7 cells against the table's
8 columns**: the Evidence cell was missing entirely, so "Current status" spilled into
Evidence and every later cell sat one column left. The one promotion whose evidence
column was empty was also the only one needing a caveat — fixed in this pass (Evidence
cell now cites the artifact, the builder, and `/tools/citation-canon`).

**Repair 2 — MW-lane degeneracy caveat.** The matrix is built from
[`data/citations/ls_citation_edges.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_edges.tsv),
in which MW resolves to **5 distinct texts** (vs PWG's 475; MW's real tagged apparatus is
320,828 citations per the citation-apparatus matrix) — and two of MW's five "texts" are
category labels ("Buddhist", "Inscriptions"), not works. The artifact's own `limitations`
field says this plainly; the index row did not. Consequences the row must carry:
(a) the sub-claim "**none** [is cited] by all 11" is partly mechanical — a text shared by
all 11 would have to be among MW's 5 resolved entries; (b) MW's community placement is
resolver-shaped. The 10 well-resolved lanes carry the modular verdict on their own, so
the direction stands — but the row now says so explicitly.

### 3. CITE-4AXIS — CONFIRMED

Artifact [`data/lexico/four_axis_citation_independence.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/four_axis_citation_independence.json)
(generated 08-07-2026). Row vs artifact: n=5 testable of 13 documented edges ✓ (8
excluded edges enumerated, nothing imputed); threshold 0.878 for n=5 correctly stated;
citation~content 0.42 → 0.416 (perm p 0.408) ✓; citation~convention 0.16 → 0.160
(p 0.792) ✓; citation~microstructure 0.84 → 0.843, exact p 0.083 over all 120
permutations ✓; "7 of the 14 dictionaries have a validated `<ls>` adapter" ✓; ls-graph
demoted to sensitivity column with rank agreement Spearman 0.7 ✓; BEN~MW cosine-0.0
artifact documented ✓. The honest-shrinkage note (agenda estimated "9 of 13", packet
delivers 5) is a point in the packet's favour.

### 4. GHOST-STOCK — CONFIRMED

Artifact [`src/data/ghost-stock/ghost_stock.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/ghost-stock/ghost_stock.json)
(generated 25-07-2026). Row vs artifact: monotone attestation strata 4.7% (n=1) →
0.0474 ✓, 11.8% → 0.1181 ✓, 35.2% (n=4) → 0.3523 ✓, 74.8% (n=7) → 0.7479 ✓, 100% at
13+ ✓ (Wilson CIs present per stratum ✓); n=323,417 union lemmas, 19.0% attested →
0.1897 ✓; logistic n_dicts coefficient +0.626 (SE 0.005, OR e^0.626≈1.87) ✓, McFadden
R² 0.27 → 0.2657 ✓; reversal sub-finding MW 10.5% → 0.1052 (4,644/44,156 exact) ✓,
MD 10.3% → 0.1028 ✓, BHS 4.4% → 0.0435 vs unique-stratum mean 4.7% ✓. The DCS
Buddhist-undersampling caveat is recorded in the row. The recorded
"main claim supported, specialised-concentration sub-claim REVERSED" verdict is exactly
what the artifact shows.

### 5. HERITAGE-WIT — CONFIRMED

Same artifact, `heritageCube` + `tripleFilter`. Row vs artifact: Heritage-uncovered →
DCS-unattested OR 5.45 → 5.447 (Woolf CI 5.296–5.601 ≈ "5.30–5.60") ✓; MW-unique →
unattested OR 4.58 → 4.579 (CI 4.434–4.729) ✓; within-MW-unique Heritage OR 2.33 →
2.329 (CI 2.08–2.608) ✓; 193,852 MW lemmas ✓; triple filter 37,931 = 35,607 explicit +
2,324 crosswalk-missing ✓ (verified as actual array lengths, not just the stated
totals); evidence grade `inferred`, routed to H5-style review, never asserted as ghost
words ✓.

### 6. HEAP-SAT — CONFIRMED

Artifact [`data/lexico/heap_sat.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/heap_sat.json)
(generated 25-07-2026). Row vs artifact: β=0.538 → 0.53821, log–log R²=0.989 →
0.98874, 15 steps ✓; 323,417 distinct from 806,120 listings, PWG 1855 → AP 1957 ✓;
SKD break +170% → relativeResidual 1.7043, 78.9% novel → 0.7888 ✓; BHS +178% → 1.7775,
59.0% → 0.5898 ✓; trio mean residual +0.50 → 0.4978 ✓; order-permutation p=0.070 →
0.07019 (5,000 seeded) ✓; exhaustive label-permutation p=0.165 → 0.16484 ✓; VEI −44% →
−0.4448 ✓; post-1890 refutation figures CAE 6.3/MD 5.7/MW 26.9/SCH 31.7/AP 40.3 all
exact ✓.

*Wording slippage (recorded, no demotion):* the hypothesis claim says "specialised
lexica arrive as breaks above the curve", and the row's largest-break exhibit is SKD —
which the artifact classifies `specialised: false` (family Sanskrit-Sanskrit; the tested
Specialized trio is INM/VEI/BHS). The row's own test paragraph handles this correctly
(the trio test is what's graded descriptive), but a reader skimming the claim + exhibit
could take SKD as evidence *for* the specialised-break sub-claim. It is evidence for a
break, not for the *specialised* break.

### 7. FREQ-STRAT — CONFIRMED

Artifact [`data/lexico/period_signatures.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/period_signatures.json)
(generated 25-07-2026). Row vs artifact: 61,338 matched union lemmas (19.0%) ✓ (totals:
matchedLemmas 61338, matchRate 0.1897); GRA centre of mass −423 CE → −422.6 (bootstrap
CI −436.8..−408.7 ≈ "−437..−409") ✓, TVD 0.49 → 0.491 ✓; VEI −115 → −115.4 ✓; SKD +956
→ 956.1 ✓; VCP +655 → 654.8 ✓; PWG 516 → 516.4, PWK 533 → 533.4, SCH 574 → 574.3,
MW 523 → 522.7, AP 516 → 515.6 ✓; Kruskal–Wallis H=5.42 → 5.417, p≈0.14 → 0.1437,
across the 4 multi-member families (n=14, Sanskrit-French singleton excluded) ✓;
Cramér's V max 0.44 (GRA) → 0.4435 ✓. The artifact's own KW note (chi-square
approximation unreliable at these group sizes; non-independent samples) matches the
row's descriptive grading.

### 8. ORTHO-CLOCK — CONFIRMED

Artifact [`data/lexico/ortho_drift.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/ortho_drift.json)
(generated 26-07-2026). Row vs artifact: PWG 14.8/1k → 14.8425, PW 17.5 → 17.4714
(1879–89 ✓), PWKVN 17.1 → 17.0562; GRA 10.4 → 10.434, CCS 6.5 → 6.4505, SCH 4.8 →
4.7986; bootstrap CIs disjoint across the Böhtlingk/non-Böhtlingk groups ✓; Spearman
ρ=−0.52 → −0.5218, exact p=0.30 over all 720 orderings (n=6) ✓; descent contrast CCS −
GRA = −3.98/1k → −3.9835, one-sided p=1; opposite pair PWG→GRA p=0.001 ✓; era
composition: all 19th-c. dicts ≥87% 1901-regime (min CCS 0.8725) ✓, SCH flips to 69%
1996-ß → 0.6947 ✓; de_reform_map 15,685 pairs ✓; >1.5M German gloss tokens ✓ (~2.4M
summed); Kossovich 358/1k → 358.1747, map and definitional test agree exactly (31,389 =
31,389) ✓.

*Unreported sensitivity (recorded, no demotion):* on the **all-map** density
(`driftPer1kAllMap`, dated + undated pre-reform forms), the lane contrast largely
disappears — GRA 27.7 vs PWG 27.1 vs PW 28.8. The Böhtlingk-fossil-lane finding lives
specifically in the **dated**-reform subset the study pre-registered. That is a
defensible design (only datable forms can carry a clock), but the row's "uniformly
fossil lane" reading should not be quoted without the dated-subset qualifier.

### 9. L0-GQD — CONFIRMED

Artifact [`data/L0/gqd_report.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/L0/gqd_report.json)
(v0.12.0, 26-07-2026). Row vs artifact: canonical_consensus GQD 0.1456 (= 85.4%
agreement), 5,625 gold butterflies of 35,960 quartets ✓; null 0.666 ± 0.068 → 0.6663 ±
0.0679, z=−7.67, p=0.001 at the 1/1000 floor (999 perms) ✓; all 10 gated trees span
0.110–0.172 → min A_jaccard_upgma 0.1102, max B_hamming_upgma 0.1723 ✓; head-to-head on
30 shared leaves: convention 0.1468 vs content 0.4302 ✓; tradition-gold inversion
content 0.494 → 0.4943 beats convention 0.577 → 0.5773 ✓; preview tree 0.4292 ✓;
clade recovery Wilson 0.442 → 0.4417 convention vs 1.000 content ✓; the
A_jaccard_upgma-scores-better fact is recorded and NOT re-canonicalised ✓. The three
honest limits in the row (tree-vs-reticulate gold floor; sanhw1-containment gold groups
advantaging the content tree; pre-registration kept) match the artifact.

## Staleness sweep — no promotion rests on a since-changed figure

The one July input-regeneration that changed already-published numbers is
[#266](https://github.com/sanskrit-lexicon/csl-atlas/pull/266) (17-07-2026, H1086): the MW
`<ls>` row had undercounted the apparatus by 28.6%, and `data/obs/citation_registers.json`
was regenerated corpus-wide. Checked against every promotion's `sourceFiles`:

- **CANON-CORE** reads `data/citations/ls_citation_edges.tsv` — untouched by #266.
- **CITE-4AXIS** reads `src/data/dicts/citation-apparatus.json` (sourceGeneratedAt
  13-06-2026) — untouched by #266 (and its `whyNotLsGraph` note is the *reason* the fix
  didn't propagate there).
- The remaining seven promotions consume the union headword list, kosha frequency
  release, DCS attestation, Heritage crosswalk, reform maps, or the L0 matrix — none
  regenerated in July after their respective promotion dates.

The known post-H1086 stale surface is the **A08 paper prose** (`OBS-C` row already flags
it), which is not a July promotion.

## Contradiction found → registered

**Two July promotions treat the same source with opposite trust.** CANON-CORE's entire
matrix is built from the ls-citation graph's per-dictionary text resolution — including
its degenerate MW lane (5 texts) — while CITE-4AXIS, one day later, *rejects* that same
graph for citation vectors precisely because MW's lane measures "resolver coverage, not
canon shape" (BEN~MW cosine 0.0 artifact). Both packets are internally honest (CANON-CORE
lists the MW under-representation in `limitations`), but the pair licenses opposite
readings of the same file, and CANON-CORE's headline "none cited by all 11" partly
inherits the artifact CITE-4AXIS refused. Registered in the org Sanskrit-data registry
([SanskritLexicography/CONTRADICTIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md))
in this same pass; resolution path = re-run the canon topology test with MW either
dropped (10-dict matrix) or fed from the citation-apparatus matrix (MW fully resolved:
320,828 tagged citations).

## Actions taken in this pass

1. This report committed as the referee record.
2. [HYPOTHESIS_INDEX.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/HYPOTHESIS_INDEX.md):
   CANON-CORE row repaired (missing Evidence cell restored; MW-lane caveat added to the
   status text); index header date bumped; a referee-pass note added pointing here.
3. CONTRADICTIONS row appended in SanskritLexicography (see above).
4. CHANGELOG entry + release in csl-atlas.

_Dr. Mārcis Gasūns_
