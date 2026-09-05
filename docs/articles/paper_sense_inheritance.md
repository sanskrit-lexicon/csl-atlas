_Created: 12-06-2026 · Last updated: 05-09-2026_

# Condensation, Not Inflation: Sense Inheritance in the Sanskrit Dictionary Family, 1822–1957

*Draft manuscript for submission to a metalexicography venue (target: Lexicographica,
with International Journal of Lexicography as alternate). Empirical basis: the
restored R2 sense-alignment layer — granularity trend
([`data/lexico/r2_h1.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_h1.json), deconfounded panel
[`data/lexico/r2_h1_panel.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_h1_panel.json)), survival and
inheritance edges ([`data/lexico/r2_h2h3.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_h2h3.json)),
reviewed parser checkpoint
([`src/data/review/r2-checkpoint-review.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/review/r2-checkpoint-review.json))
the promotion experiment
([`data/lexico/r2_promotion_experiment.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_promotion_experiment.json)),
and the corpus-scale SKD/VCP sense/citation-fusion count
([`data/lexico/r2_kosa_fusion.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_kosa_fusion.json), §7).
Companion to *Redundancy and Descent*
([`paper_redundancy_and_descent.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_redundancy_and_descent.md)) and *Two
Citation Registers* ([`paper_citation_registers.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_citation_registers.md)).
All counts are reproducible from committed data and the local `csl-orig` sources;
numbers herein are the 2026-06 snapshot, including the confound-controlled H1 and H2
analyses (`h1Controlled` with `withinPrimaryEdge`, `h2ThresholdSensitivity`) and the
reviewer-adjudicated YAT semicolon-aware sense counter, which re-counts the
Wilson → Yates edge from the earlier inline-number artifact to a genuine condensation.
Author-voice pass 2026-07-08, Fable 5 `claude-fable-5` — see
[SIGNOFF_A02_author_pass.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/SIGNOFF_A02_author_pass.md).*

**Mārcis Gasūns** · ORCID [0000-0003-4513-884X](https://orcid.org/0000-0003-4513-884X) · gasyoun@ya.ru

---

## Abstract

When one dictionary descends from another, what happens to its senses? Between 1822
and 1957 the record produced two indigenous Sanskrit–Sanskrit encyclopaedic lexica
and a family tree of European dictionaries with documented descent — Wilson into
Śabda-Sāgara and Yates, Petersburg into Monier-Williams, Apte revised across
editions. I ask whether sense
counts inflate over time (H1), whether citation predicts survival (H2), and
whether descendants expand, copy, or condense (H3), across eleven dictionaries and
three inheritance edges, aligning senses through shared Sanskrit material rather
than translation.
**Granularity does not inflate over time — if anything it declines within a
family**: the pooled trend is flat (*r* = 0.036), and granularity is instead a
**family trait** — Benfey 2.42 sense-units/entry, the Petersburg line 1.13, the
indigenous lexica 1.00 by construction. **Citation co-varies with survival but is
not an independent predictor**: cited senses survive somewhat more often (0.768 vs
0.705), but the signal sits on one edge and is not significant there (*z* = 1.80,
*p* = 0.07); a pooled estimate that looks significant is an edge-concentration
artifact. Descendants **copy or condense, never expand**:
gloss overlap 0.906 on Wilson → Śabda-Sāgara, drift −3.07 on Apte 1890 → 1957, −3.3
on Wilson → Yates. A corpus-scale count over
every SKD and VCP record finds that sense/citation fusion — the *dharma* exemplar's
synonym run closing *in* its own citation — tracks **record type, not dictionary
identity**: SKD is 53 % fused, VCP 78 %, by entry length rather than dictionary.

**Keywords:** historical lexicography; Sanskrit; sense granularity; dictionary
inheritance; sense survival; polysemy; citation apparatus; microstructure; digital
lexicography.

---

## 1. Introduction

A persistent intuition in the history of lexicography holds that later dictionaries
are richer: more senses, finer divisions, fuller treatment. The intuition is rarely
tested, because testing it requires (i) a set of dictionaries with documented lines
of descent, (ii) a way of counting senses that respects each dictionary's own
conventions rather than imposing one, and (iii) a way of aligning senses across
dictionaries — and, in the Sanskrit case, across three description languages
(German, English, Sanskrit) — so that survival and drift can be measured sense by
sense rather than entry by entry. The second of these is the classical microstructural
problem — segmenting and comparing senses on each dictionary's own terms rather than a
single editor's (Zgusta 1971; Wiegand 1989; Atkins and Rundell 2008) — here sharpened
by a corpus that mixes four marking regimes across three description languages.

The Cologne Digital Sanskrit Lexicon (CDSL) supplies all three. Its forty-three
dictionaries include eleven general lexica spanning 1822–1957 whose genealogy is
documented both philologically and, in companion work, by headword-containment
measurement: Wilson (1832) is the ancestor of Śabda-Sāgara (1900) and Yates (1846);
Apte's 1890 dictionary was revised into the 1957 edition; the Petersburg lexicon
stands behind Monier-Williams. Alongside the European line stand two indigenous
Sanskrit–Sanskrit encyclopaedic lexica — *Śabdakalpadruma* (1822–58) and
*Vācaspatya* (1873–84) — whose microstructure descends from the *kośa* and
commentarial traditions (Vogel 1979) rather than from the European critical apparatus.

This paper asks three questions of that record. **H1 (inflation):** do sense counts
per entry rise with publication year? **H2 (survival):** when a dictionary inherits
from an ancestor, which ancestor senses survive — and does the source-citation
apparatus predict survival? **H3 (drift):** do descendants expand, copy, or condense
the inherited sense inventory? A methodological question is prior to all three: can
senses be counted and aligned at all across conventions as different as Apte's
numbered bullets, the Petersburg structural divisions, Monier-Williams's run-on
glosses, and the *iti*-closed prose units of the indigenous lexica? Sections 3–4
answer the method question with a reviewed parser checkpoint and a promotion
experiment; sections 5–7 report the three findings.

## 2. Data

Eleven general dictionaries carry the granularity analysis (table 1); the
inheritance edges use the Wilson line (Wilson 1832 → Śabda-Sāgara 1900, Wilson 1832
→ Yates 1846) and the Apte revision edge (1890 → 1957), the three edges on which
senses are countable on both sides. All sources are the CDSL v02 plain-text files;
every count cited here regenerates from them with the committed build scripts.

**Table 1. Corpus for the granularity trend (H1).**

| Year | Dictionary | Family | Entries | Sense-units/entry |
|---:|---|---|---:|---:|
| 1822 | Śabdakalpadruma (SKD) | indigenous | 42,531 | 1.00 |
| 1832 | Wilson (WIL) | Wilson | 44,577 | 1.71 |
| 1855 | Petersburg (PWG) | Petersburg | 123,366 | 1.13 |
| 1866 | Benfey (BEN) | Benfey | 17,310 | 2.42 |
| 1872 | Monier-Williams 1872 (MW72) | Monier-Williams | 55,388 | 2.85 |
| 1873 | Vācaspatya (VCP) | indigenous | 50,135 | 1.00 |
| 1890 | Apte 1890 (AP90) | Apte | 34,882 | 2.52 |
| 1891 | Cappeller (CAE) | Cappeller | 40,069 | 1.36 |
| 1899 | Monier-Williams (MW) | Monier-Williams | 286,560 | 1.15 |
| 1928 | Schmidt (SCH) | Petersburg | 29,125 | 1.14 |
| 1957 | Apte (AP) | Apte | 90,654 | 1.73 |

*Source: [`r2_h1.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_h1.json), regenerated from csl-orig by
`npm run build-r2-h1`.*

## 3. Method

### 3.1 Splitting by each dictionary's own conventions

No single sense-segmentation rule fits this corpus, because the corpus contains four
distinct marking regimes. The splitter therefore implements four **parser families**,
each using the dictionary's own convention:

- **Explicit Western markers.** Apte 1957 numbers senses with a bullet (`∙²N`);
  Apte 1890, Benfey and Edgerton use `{@N@}`; Wilson uses `.²N`; the Petersburg
  dictionaries use structural `<div>` divisions. Marker runs that restart at 1
  (Benfey's per-preverb runs) are tracked as separate runs.
- **Lumped glosses.** Monier-Williams (both editions), Schmidt and Cappeller mark no
  senses; meaning-clauses delimited by semicolons, with citations stripped, serve as
  a calibrated proxy and are flagged as such.
- **Indigenous prose.** SKD and VCP close each unit of discourse with the quotative
  particle *iti*; *iti*-units are the splitting proxy, with authority sigla
  (*ity Amaraḥ*, *iti Medinī*; VCP's `…0` sigla) captured per unit.
- **Reverse index.** Apte's English–Sanskrit volume is reverse-indexed: a Sanskrit
  lemma retrieves the English headwords that gloss it, with the lemma's position
  among the Sanskrit equivalents recorded as a rank band.

Cross-dictionary alignment never compares gloss translations. Each sense carries a
**Sanskrit fingerprint** — the SLP1 tokens it quotes, headword excluded, plus its
citation sigla — and senses align by Jaccard overlap of fingerprints. This is what
permits a German Petersburg sense to align with an English Apte sense, or a
Petersburg sense with a *Śabdakalpadruma* unit, with no translation step. The H2
survival metric (§5) is narrower than this general fingerprint alignment: it traces
senses by gloss-text overlap within the Wilson line, where glosses are English on
both sides, and is not yet defined across description languages.

### 3.2 The reviewed checkpoint

Counting rules of this kind harbour known failure modes: a dictionary's later-volume
supplements can double-count a lemma; a homonym can be merged into the target; a
reverse index over-matches common verbs; *iti*-units conflate definition with
commentary. Rather than tune silently, the pipeline isolates the ten highest-risk
lemma/dictionary pairs as a **review checkpoint**, each row carrying source pointers
into the original files and a machine-proposed label vocabulary. All ten rows were
human-reviewed against the sources (2026-06-12): seven window rules were promoted,
two rows were retained as side evidence, one as a regression control. Among the
reviewed rules: Petersburg supplements (*Nachträge*) and the true homonym ²*gam*
"earth" are excluded from the primary series; Benfey's per-preverb marker runs are
separated from the main run; the reverse index's rank bands count as equivalent
evidence for **nominal lemmas only** — for verbs, reverse rows are collocational
context ("go abroad" → *prakāśatāṃ gam*), not sense equivalents.

### 3.3 The promotion experiment

The promoted rules were then applied to the source-backed anchor rows as an
**additive experiment** — non-window rows retained as labelled side evidence, the
archived sense counts (the first-pass splitter's static output, here called the
*legacy counts*) used only as a comparison signal, never as an optimisation target.
The outcomes fall into three classes.

**Exact reproduction, untuned.** Two windows recover the legacy sense count exactly
without being fitted to it: the Benfey *rama* rule (exact-headword record plus
lookup-bundle split) gives 7 = 7, and the *Vācaspatya dharma* definition-unit window
gives 9 = 9. The positive control — Apte *gam*, where source and legacy count already
agree — held at 16 = 16.

**The legacy count is the artifact.** In the high-drift cases, where the
source-faithful window and the legacy count diverge sharply, inspection of the
printed dictionary vindicates the window, not the count (Table 2). For the Petersburg
*gam* and *dharma*, the `<div n>` attribute that the first-pass splitter counted is a
*depth* marker, not a sense number; Böhtlingk prints his own enumeration in the entry
text ("— 1) … — 7)" for ¹*gam*, "1) … — 11)" for *dharma*), giving seven and eleven
top-level senses — each directly checkable against the page. The legacy 30 and 5 had
counted nesting depth and preverb material, or under-read the enumeration, not the
senses. For the Benfey *gam*, the single record nests forty-two numbered runs: the
bare finite root (nine senses), its primary derivatives — the participles
*gata* / *gamya* and the causative *gamaya* (twenty-four) — and thirty-eight
preverb-combined lexemes, each headed "-- With *preverb*" (one hundred thirty-eight).
The legacy 23 is the root plus the first participle alone, an arbitrary cut stopping
in the middle of the derivative block. In every high-drift row the legacy static
count, not the source window, proves to be the artifact, and the window is faithful
to the printed text in a way the count it "diverges" from is not.

**The register limit.** One high-drift case is not a counting error but a property of
the source. In *Śabdakalpadruma* the experiment under-counts *by design*: the synonym
run for *dharma* (*puṇyam, śreyaḥ, sukṛtam, vṛṣaḥ*) **ends in** *ity Amaraḥ*, so the
unit is simultaneously the sense list and its citation. A classifier that routes
authority-marked units out of the sense window therefore removes the senses
themselves. The European sense/apparatus distinction is not wrong for SKD — it is
**inapplicable**: in the *kośa* register, attestation and enumeration are one
construction. I return to this in §7.

**Table 2. Source-faithful windows versus the legacy static counts on the high-drift
checkpoint rows.**

| Row | Source window | Legacy count | What the legacy count actually was |
|---|---:|---:|---|
| PWG ¹*gam* | 7 | 30 | `<div>` nesting depth + preverb blocks |
| PWG *dharma* | 11 | 5 | under-read enumeration ("3 divisions") |
| BEN *gam* | 9 | 23 | root + first participle (arbitrary cut) |
| SKD *dharma* | 1\* | 4 | register limit: sense and citation are one *iti*-unit (§7) |

*\*The SKD figure is the definition-unit residue once authority-marked units are
removed; it is an under-count by construction, not a legacy-count error.*

This reframes the experiment's contribution. The method does not merely *reproduce*
the legacy sense counts; where the two disagree, it is **demonstrably more faithful to
the printed dictionary** than the counts it is checked against — and the disagreement
is itself diagnostic of how each dictionary marks (or fuses) its senses. That is the
same lesson H1 draws at the corpus scale (§4): a sense count is only meaningful
relative to a dictionary's own marking convention.

## 4. H1: granularity is a family trait, not a function of time

Across the eleven dictionaries the correlation of sense-units per entry with
publication year is **r = 0.036** — no trend. The variance is captured instead by
lexicographic family: Benfey's mean is 2.42 units per entry, the Apte family 2.12,
Monier-Williams 2.00, Wilson 1.71, Cappeller 1.36, the Petersburg line 1.13, the
indigenous lexica 1.00 (by construction of the *iti*-unit proxy; see §7 for why this
floor is a register fact, not emptiness).

Two confounds were controlled. The per-entry metric penalises dictionaries that
split compounds into separate headwords — Monier-Williams 1899's 286,560 entries
dilute its ratio (1.15) far below its own 1872 edition (2.85), a headword-policy
artefact, not a temporal one. A fixed panel of 28–30 simple nouns present across
the corpus removes the artefact; the panel correlation is **r = 0.093**
([`r2_h1_panel.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_h1_panel.json)) — the conclusion stands.
Neither correlation is significant (corpus *r* = 0.036, *t* = 0.11, df = 9; panel
*r* = 0.093, *t* = 0.49, df = 28; both *p* ≫ 0.05) — but with only eleven
dictionaries across seven families, the pooled correlation is *underidentified*, not a
measured null: it cannot separate a year effect from family composition, and a
family-controlled regression (year plus family dummies, n = 11) is near-saturated,
leaving year's partial slope at −0.051 sense-units per year with a wide 95 %
confidence interval, [−0.186, +0.084], centred below zero. The decisive test holds
family fixed. Each of the four families that span more than one edition is
flat-to-*declining* in granularity over time — on the fixed panel, indigenous −0.014,
Apte −0.027, Petersburg −0.049, Monier-Williams −0.349 sense-units per lemma·year
(mean −0.11) — and within the single Western-parsed regime the trend is likewise
negative (*r* = −0.11). Inflation is therefore not merely undetected but contradicted
in direction: where inheritance is measured within a tradition, later editions
enumerate no more finely — and usually less finely — than earlier ones (Apte 1957 does
not enumerate more finely than Apte 1890). These controls are committed as the
`h1Controlled` block of [`r2_h1_panel.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_h1_panel.json).

The corrective matters for practice. Any cross-dictionary measure normalised "per
sense" — definition length, citation density, equivalence counts — silently encodes
the school of the dictionary unless family is controlled. "Later = finer" is, on
this corpus, false.

## 5. H2: cited senses survive more often — but the signal sits on one edge

On the 28-noun panel, each ancestor sense was traced into the descendant by
gloss-text overlap (threshold 0.15). Cited ancestor senses — those carrying at least
one `<ls>` source citation — survived at **0.768** (63 of 82); uncited senses at
**0.705** (511 of 725). The pooled gap is small and, on a naive two-proportion test,
not significant (*z* ≈ 1.2).

The deeper problem is *where* the cited senses are. Citation is not spread across the
panel: Wilson 1832 carries no `<ls>` on these edges, so **all 82 cited ancestor
senses fall on a single edge — Apte 1890 → 1957** (the two Wilson edges contribute
none). The citation-survival question is therefore really a question about
that one edge, and the clean test is *within* it, where the parsing of the others is
irrelevant. On Apte 1890 → 1957, cited senses survive at **0.768** (n = 82) against
**0.661** for uncited senses (n = 221) — a two-proportion *z* = 1.80, *p* = 0.07,
**not significant** (`h2Controlled.withinPrimaryEdge` in
[`r2_h2h3.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_h2h3.json)).

A pooled model that borrows strength across edges does not rescue the result; it
misleads. Fitting survival as a logistic regression (`survived ~ cited + position +
gloss-length + cross-dictionary redundancy + edge fixed effects`, cluster-robust by
lemma) returns a citation odds ratio of ≈ 3 (*p* ≈ 0.01) that *looks* significant, but
the estimate is unstable precisely because cited senses are concentrated on one edge:
changing how an *unrelated* edge is parsed (the Yates semicolon promotion, §3) moved
it from ≈ 1.75 to ≈ 3.0 without touching a single cited sense, so the pooled number is
an artifact of that imbalance, not a citation effect, and I do not rely on it — the
full grid is in `h2Controlled` in
[`r2_h2h3.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_h2h3.json). Two real confounds compound the
point — senses nested within a lemma share a fate, and citation is itself entangled
with sense centrality (early position, longer gloss, cross-family recurrence) — so
even the within-edge gap is an upper bound. The pattern is invariant to the 0.15
survival threshold: across cutoffs 0.10–0.25 the naive cited-vs-uncited gap persists
at roughly 3–6 points at every threshold, and the pooled estimate stays
edge-composition-driven at every cutoff (`h2ThresholdSensitivity` in the same file).

The honest reading is therefore that citation **co-varies** with persistence — cited
senses do survive somewhat more often — but on this corpus the effect rests on a
single edge and is not significant there, so the data do not establish citation as an
*independent* predictor of survival. This sits alongside a broader lexical-survival
literature that ties word-level persistence to usage frequency rather than to any
single textual apparatus (Pagel, Atkinson, and Meade 2007; Petersen et al. 2012); the
present result is at the sense level within one dictionary family rather than the
word level across languages, but the same caution applies — an apparent survival
predictor can be a proxy for something else (frequency there, edge composition here)
unless the confound is controlled. A larger panel with citation-dense ancestors on
more than one edge could confirm or dissolve the citation effect itself. I know of no
comparable quantitative treatment, positive or null, for any historical dictionary
family with documented lines of descent. The pooled estimate fails in exactly the way
§3 shows legacy sense
counts fail: it measures composition, not the quantity it names.

## 6. H3: descendants copy or condense — none expand

**Table 3. Inheritance edges (28-noun panel).**

| Edge | Mean senses (anc → desc) | Drift | Gloss overlap | Pattern |
|---|---|---:|---:|---|
| Wilson 1832 → Śabda-Sāgara 1900 | 9 → 9 | 0 | **0.906** | near-verbatim copy |
| Wilson 1832 → Yates 1846 | 9 → 5.7 | −3.3 | 0.256 | condensation (semicolon-aware count) |
| Apte 1890 → Apte 1957 | 10.8 → 7.8 | −3.07 | 0.565 | revision, condensation, no expansion |

*Source: [`r2_h2h3.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_h2h3.json), regenerated by
`npm run build-r2-h2h3`. The Yates count uses the reviewer-adjudicated semicolon-aware
counter (§3); the earlier 9 → 1 was an inline-number extraction artifact.*

The Śabda-Sāgara row is forensic: its glosses are 90.6 % word-identical to Wilson's,
sense by sense — microstructural confirmation of the lemma-level containment edge
(WIL ⊆ SHS ≈ 0.95) reported in the companion redundancy study. The Apte revision
contracts, dropping from 10.8 to 7.8 sense-units per lemma without adding any. The
Wilson → Yates edge once read as a dramatic 9 → 1 abridgement, but that figure was an
extraction artifact: Yates marks its senses with semicolons rather than the numbered
markers the Western-explicit parser expects, so the inline-number splitter collapsed
every entry to one. A source probe
([`verify-yat-sense-artifact.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/verify-yat-sense-artifact.mjs)) and a
reviewed parser promotion (§3) re-count Yates by semicolon segmentation — about 5.7
distinct meanings per panel lemma, with lone adjectival entries kept whole to avoid
over-splitting synonym lists. Counted correctly, Yates is a **genuine condensation**
(≈ 9 → 5.7, drift −3.3, overlap 0.26), of the same order as the Apte revision — an
abridgement that keeps about three senses in five, not the spurious one in nine.
**No measured edge adds senses**: across all three edges the movement is copy or
condense, never expansion. Combined with H1 the result inverts the inflation intuition
twice over — later dictionaries are not finer-grained in general, and on the edges
where inheritance is directly measurable the movement is toward faithful copying or
contraction. The stronger earlier claim that the citation apparatus *steers* what
survives is qualified by §5 and is not relied on here.

## 7. The indigenous register: where sense and citation are one unit

The indigenous lexica sit at 1.00 units per entry in table 1 — a floor that earlier
phases of this project have repeatedly warned against misreading: zero or floor
values under European detectors measure the **absence of European conventions**, not
absence of content. The promotion experiment sharpens this from a warning into a
structural finding at the level of one lemma. The *Vācaspatya*'s definition-unit
window reproduces the archived sense count exactly for *dharma* (9 = 9); the
*Śabdakalpadruma*'s *dharma* entry instead closes its synonym run *ity Amaraḥ* — the
listed synonyms (*puṇyam, śreyaḥ, sukṛtam, vṛṣaḥ*) and the citation that licenses them
sit in the same *iti*-unit, so definition and attestation are structurally fused.

A corpus-scale count generalises this contrast — and complicates it. A new read-only
build ([`build-r2-kosa-fusion.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-kosa-fusion.mjs),
`data/lexico/r2_kosa_fusion.json`) walks every SKD and VCP record, classifying each
*iti*-unit as authority-terminal (a substantial run of definitional content closes in
its own authority citation, the *dharma*-in-SKD pattern), separable (the unit is
essentially the citation tag alone, its definition sitting in a sibling unit, the
*dharma*-in-VCP pattern), or carrying no authority marker. 43.3 % of SKD records and
76.7 % of VCP records contain at least one authority-marked unit; among those units,
SKD splits close to evenly — 53.3 % authority-terminal, 46.7 % separable — while VCP
skews toward fusion, 77.6 % authority-terminal. That is the **opposite** direction
from the *dharma* exemplar's clean synonym-run-versus-discursive-prose contrast, and
the reason is registral rather than a classifier artifact: VCP's *dharma* entry is not
a short synonym list at all but an extended Mīmāṃsā argument that threads its `…0`
sigla (*bhāṣya*, *sūtra*, and others) through paragraphs of discursive prose, so a
citation's preceding unit is rarely short there. The *dharma* pair illustrates one
real record type — the short encyclopaedic synonym-run SKD favours for an ordinary
nominal — not a dictionary-wide law: SKD carries plenty of short authority-tagged
citation units too (its 46.7 % separable share), and VCP carries plenty of fused ones
where a citation lands inside a longer definitional stretch. The finding is
accordingly re-scoped: **sense/citation fusion tracks record type — short
encyclopaedic entry versus long discursive commentary — rather than a fixed,
dictionary-level rule.** The structural point survives the re-scoping: wherever a
citation lands inside a unit's own definitional run, the European sense/apparatus
distinction cannot be imposed without loss, and that happens on a majority of
authority-marked units in *both* indigenous dictionaries (53–78 %), not on some and
not on others.

## 8. Limitations

- Sense-units for the lumped dictionaries are a calibrated proxy (semicolon-delimited
  meaning-clauses), not editorial senses; per-dictionary values sit within 13 % of the
  archived baseline with family ordering preserved — a magnitude cross-checked against
  the independent MW gold-standard instrument
  ([`GOLD_STANDARD.md`](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/analysis/GOLD_STANDARD.md),
  MWS `docs-pass`); the family ordering (§4) is robust to proxy error of this
  documented magnitude everywhere except the adjacent Cappeller–Petersburg pair, on
  which no conclusion in this paper rests.
- The survival metric (§5) uses gloss-text overlap within the Wilson line, where
  glosses are English on both sides; it is not yet defined across description
  languages (§3.1).
- Verbs remain coarser than nominals throughout: preverb sub-entries, marker-run
  resets and reverse-index collocation noise are documented and review-gated, and the
  reviewed verb/noun asymmetry (reverse-equivalent evidence counts for nominals only)
  is enforced rather than solved.
- The three measurable inheritance edges are few; the Petersburg → Monier-Williams
  edge, philologically certain, is not yet sense-countable because MW marks no
  senses. Extending survival measurement to lumped descendants is the next slice.
- The §7 sense/citation-fusion classifier is pattern-based over a heterogeneous corpus
  of philological Sanskrit prose, not a scholar-reviewed sense/citation boundary;
  borderline units exist, and the fused-vs-separable cut point
  (`FUSION_MIN_CONTENT_CHARS` in `build-r2-kosa-fusion.mjs`) is a documented threshold,
  not a calibrated one. A stratified ~100-unit SKD sample has been drawn for human
  citational-vs-grammatical adjudication
  ([`REVIEW_SKD_ITI_ADJUDICATION.html`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/REVIEW_SKD_ITI_ADJUDICATION.html)); that
  adjudication is outstanding and will sharpen or revise the 53 %/78 % figures in §7.
- The H2 citation-survival signal rests on a single edge: all 82 cited ancestor
  senses are on Apte 1890 → 1957 (Wilson 1832 carries no `<ls>` on these edges), where the
  within-edge test is not significant (0.768 vs 0.661; *z* = 1.80, *p* = 0.07). The
  pooled multi-edge odds ratio is edge-composition-sensitive — it shifted from ≈ 1.75
  to ≈ 3.0 when an unrelated edge's parser was changed — and is not relied on. The
  pattern holds across the committed threshold sweep (0.10–0.25; §5); an independent
  panel with citation-dense ancestors on more than one edge is needed before any
  independent citation effect can be claimed.
- The Wilson → Yates count depends on a reviewer-adjudicated parser promotion (§3):
  Yates is semicolon-packed, not sense-numbered, and the promoted semicolon-aware
  counter (with a lone-adjective refinement to avoid over-splitting synonym lists)
  recovers ≈ 5.7 meanings per lemma. The edge is a genuine condensation under this
  counter; a different segmentation choice would shift the exact drift, though not the
  copy/condense direction.
- The within-family granularity slopes (H1) rest on as few as two editions per family
  (one slope each), and the pooled family-controlled regression is near-saturated
  (eleven dictionaries, seven families); the within-family decline is a robust
  *direction*, not a precisely estimated rate.
- Ten checkpoint rows were reviewed by a single reviewer against the sources; the
  review packets are designed for multi-reviewer adjudication with agreement
  statistics, which is planned but not yet done.

## 9. Conclusion

On the corpus where the history of dictionaries can actually be measured edge by
edge, the received intuition fails twice. Sense granularity is a signature of
lexicographic school, flat — indeed gently declining within families — in time; and
inheritance copies or condenses rather than expands — across all three measurable
edges, including a Yates abridgement that condenses about nine senses to six once its
semicolon-packed entries are counted correctly. Cited senses do survive somewhat more
often (0.768 versus 0.705 overall; 0.768 versus 0.661 on the one citation-bearing
edge — the same cited rate, since every cited sense sits there), but that signal
rests on a single edge and is not significant there
(*z* = 1.80, *p* = 0.07); the pooled estimate that borrows strength across edges to
manufacture apparent significance fails in exactly the way §3 shows legacy sense
counts fail — it measures edge composition, not the citation effect it names — so the
apparatus marks persistence without a demonstrated independent effect on it. A
register boundary underlies the citation question: European dictionaries separate
sense from authority, while the *kośa* tradition fuses them into one construction on a
majority of its authority-marked units — 53 % of SKD's, 78 % of VCP's — a pattern
tied to record type (short encyclopaedic entry versus discursive commentary) rather
than to dictionary identity. Digital lexicography that aims to align these traditions
must model the fusion, not filter it out.

## References

Atkins, B. T. Sue, and Michael Rundell. 2008. *The Oxford Guide to Practical
Lexicography.* Oxford: Oxford University Press.

Hausmann, Franz Josef, Oskar Reichmann, Herbert Ernst Wiegand, and Ladislav Zgusta,
eds. 1989–1991. *Wörterbücher / Dictionaries / Dictionnaires: An International
Encyclopedia of Lexicography.* 3 vols. (Handbücher zur Sprach- und
Kommunikationswissenschaft 5.1–5.3.) Berlin and New York: Walter de Gruyter.

Pagel, Mark, Quentin D. Atkinson, and Andrew Meade. 2007. "Frequency of Word-Use
Predicts Rates of Lexical Evolution Throughout Indo-European History." *Nature*
449: 717–720. [**Flagged for author verification** — added for the survival/decay
literature referee point (§1.4 M-minor); page range and DOI to be confirmed against
the published article before submission.]

Petersen, Alexander M., Joel Tenenbaum, Shlomo Havlin, and H. Eugene Stanley. 2012.
"Statistical Laws Governing Fluctuations in Word Use from Word Birth to Word Death."
*Scientific Reports* 2: 313. [**Flagged for author verification**, as above.]

Vogel, Claus. 1979. *Indian Lexicography.* (A History of Indian Literature, ed. Jan
Gonda, vol. 5, fasc. 4.) Wiesbaden: Otto Harrassowitz.

Wiegand, Herbert Ernst. 1989. "Der Begriff der Mikrostruktur: Geschichte, Probleme,
Perspektiven." In Hausmann et al. (eds.), *Wörterbücher / Dictionaries /
Dictionnaires,* vol. 1 (HSK 5.1), 409–461. Berlin and New York: Walter de Gruyter.

Zgusta, Ladislav. 1971. *Manual of Lexicography.* (Janua Linguarum, Series Maior 39.)
Prague: Academia; The Hague and Paris: Mouton.

**Primary digital source.** Cologne Digital Sanskrit Dictionaries (CDSL). Institute of
Indology and Tamil Studies, University of Cologne.
[`sanskrit-lexicon.uni-koeln.de`](https://www.sanskrit-lexicon.uni-koeln.de/). The
eleven dictionaries and their `csl-orig` plain-text sources are itemised in §2 and
cited inline by file.

**Companion papers (this project).**

Gasūns, M. (in preparation). *Redundancy and Descent in a Digitised Dictionary Family:
A Headword-Level Stemma of the Cologne Digital Sanskrit Lexicon.* (Cited above as the
companion redundancy study.)

Gasūns, M. (in preparation). *Two Citation Registers and the Dictionary-to-Book Gap in
the Cologne Digital Sanskrit Lexicon.* (Cited above as the companion citation-registers
paper.)

*Bibliographic details are verified for the five core secondary references (Atkins &
Rundell; Hausmann et al.; Vogel; Wiegand; Zgusta). Still to confirm before submission:
page range and DOI for Pagel, Atkinson & Meade (2007) and Petersen et al. (2012), as
flagged inline above.*

_Dr. Mārcis Gasūns_
