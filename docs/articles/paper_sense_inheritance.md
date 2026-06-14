# Condensation, Not Inflation: Sense Inheritance in the Sanskrit Dictionary Family, 1822–1957

*Draft manuscript for submission to a metalexicography venue (target: Lexicographica,
with International Journal of Lexicography as alternate). Empirical basis: the
restored R2 sense-alignment layer — granularity trend
([`data/lexico/r2_h1.json`](../../data/lexico/r2_h1.json), deconfounded panel
[`data/lexico/r2_h1_panel.json`](../../data/lexico/r2_h1_panel.json)), survival and
inheritance edges ([`data/lexico/r2_h2h3.json`](../../data/lexico/r2_h2h3.json)),
reviewed parser checkpoint
([`src/data/review/r2-checkpoint-review.json`](../../src/data/review/r2-checkpoint-review.json))
and the promotion experiment
([`data/lexico/r2_promotion_experiment.json`](../../data/lexico/r2_promotion_experiment.json)).
Companion to *Redundancy and Descent*
([`paper_redundancy_and_descent.md`](paper_redundancy_and_descent.md)) and *Two
Citation Registers* ([`paper_citation_registers.md`](paper_citation_registers.md)).
All counts are reproducible from committed data and the local `csl-orig` sources;
numbers herein are the 2026-06 snapshot. Author: M. Gasūns (byline to finalise).*

---

## Abstract

When one dictionary descends from another, what happens to its senses? The Sanskrit
lexicographic record is uniquely suited to the question: between 1822 and 1957 it
produced two indigenous Sanskrit–Sanskrit encyclopaedic lexica and a dense family
tree of European dictionaries with documented lines of descent — Wilson copied into
Śabda-Sāgara and condensed into Yates, the Petersburg lexicon absorbed into
Monier-Williams, Apte revised across editions. We measure sense behaviour across
eleven general dictionaries (1822–1957) and three documented inheritance edges,
using each dictionary's own sense-marking conventions and aligning senses across
languages through the Sanskrit material they share rather than through translation.
Three results follow. First, **sense granularity does not inflate over time**: the
year-trend across the corpus is flat (Pearson *r* = 0.036; *r* = 0.093 on a fixed
28–30-noun panel that removes the headword-splitting confound). Granularity is a
**family trait** — Benfey enumerates 2.42 sense-units per entry, the Petersburg line
packs 1.13, the indigenous lexica 1.00 by construction — so any diachronic claim
about "richer" later dictionaries must control for lexicographic school. Second,
**citation predicts survival**: on a 28-noun panel of Wilson-line descent, ancestor
senses carrying at least one source citation survive into the descendant at **0.762**
(n = 84) against **0.591** for uncited senses (n = 723), a significant 17-point
advantage (*p* ≈ 0.002) — the apparatus is not decoration but a predictor of
lexicographic persistence. Third,
descendants **copy or condense; they do not expand**: gloss overlap of 0.906 on the
Wilson → Śabda-Sāgara edge (near-verbatim copy, drift 0), drastic condensation on
Wilson → Yates (9 → 1 senses per lemma), contraction on Apte 1890 → 1957 (drift
−3.07) — no measured edge adds senses systematically. A reviewed ten-row parser
checkpoint and a promotion experiment ground the method: some reviewed windows
reproduce the legacy static sense counts exactly without being tuned to them, while
in every case where a window and the legacy count diverge sharply, inspection of the
printed dictionary shows the **legacy count to be the artifact** — Petersburg's
`<div>` nesting counted as senses, Benfey's root truncated mid-derivative — and the
source-faithful window verifiable against the page. The same experiment shows that in
the indigenous *Śabdakalpadruma* the sense list and the authority citation are
**structurally inseparable** — the synonym run *ends in* the citation (*ity Amaraḥ*) —
so the European sense/apparatus distinction cannot be imposed on the *kośa* tradition
without loss.

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
sense rather than entry by entry.

The Cologne Digital Sanskrit Lexicon (CDSL) supplies all three. Its forty-three
dictionaries include eleven general lexica spanning 1822–1957 whose genealogy is
documented both philologically and, in companion work, by headword-containment
measurement: Wilson (1832) is the ancestor of Śabda-Sāgara (1900) and Yates (1846);
Apte's 1890 dictionary was revised into the 1957 edition; the Petersburg lexicon
stands behind Monier-Williams. Alongside the European line stand two indigenous
Sanskrit–Sanskrit encyclopaedic lexica — *Śabdakalpadruma* (1822–58) and
*Vācaspatya* (1873–84) — whose microstructure descends from the *kośa* and
commentarial traditions rather than from the European critical apparatus.

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

*Source: [`r2_h1.json`](../../data/lexico/r2_h1.json), regenerated from csl-orig by
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
Petersburg sense with a *Śabdakalpadruma* unit, with no translation step.

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
construction. We return to this in §7.

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
([`r2_h1_panel.json`](../../data/lexico/r2_h1_panel.json)) — the conclusion stands.
Neither correlation is significant (corpus *r* = 0.036, *t* = 0.11, df = 9; panel
*r* = 0.093, *t* = 0.49, df = 28; both *p* ≫ 0.05), which is the point: there is no
year trend to detect once family is allowed for.
Within a single family the revision edge shows the same: Apte 1957 does not enumerate
more finely than Apte 1890.

The corrective matters for practice. Any cross-dictionary measure normalised "per
sense" — definition length, citation density, equivalence counts — silently encodes
the school of the dictionary unless family is controlled. "Later = finer" is, on
this corpus, false.

## 5. H2: cited senses survive

On the 28-noun Wilson-line panel, each ancestor sense was traced into the descendant
by gloss-text overlap (threshold 0.15). Ancestor senses carrying at least one `<ls>`
source citation survived at **0.762** (64 of 84; Wilson 95 % CI [0.661, 0.840]);
uncited senses at **0.591** (427 of 723; CI [0.554, 0.626]) — a 17-point gap whose
confidence intervals do not overlap and which is significant on a two-proportion
test (*z* = 3.0, *p* ≈ 0.002; χ² = 9.3, df = 1). The direction is stable against the
archived baseline (0.70 vs 0.54). The citation apparatus, whose register-dependence
is the subject of the companion paper, here acquires a diachronic function:
**a citation is a survival predictor**. Senses on textual authority are the ones successor lexicographers keep;
unattested senses are where condensation cuts first. We know of no comparable
quantitative result for any dictionary family.

## 6. H3: descendants copy or condense — none expand

**Table 3. Inheritance edges (28-noun panel).**

| Edge | Mean senses (anc → desc) | Drift | Gloss overlap | Pattern |
|---|---|---:|---:|---|
| Wilson 1832 → Śabda-Sāgara 1900 | 9 → 9 | 0 | **0.906** | near-verbatim copy |
| Wilson 1832 → Yates 1846 | 9 → 1 | −8 | 0.075 | drastic condensation |
| Apte 1890 → Apte 1957 | 10.8 → 7.8 | −3.07 | 0.565 | revision, no expansion |

*Source: [`r2_h2h3.json`](../../data/lexico/r2_h2h3.json), regenerated by
`npm run build-r2-h2h3`.*

The Śabda-Sāgara row is forensic: its glosses are 90.6 % word-identical to Wilson's,
sense by sense — microstructural confirmation of the lemma-level containment edge
(WIL ⊆ SHS ≈ 0.95) reported in the companion redundancy study. Yates is the
opposite strategy, an abridgement that keeps roughly one sense in nine. The Apte
revision contracts. **No measured edge adds senses.** Combined with H1, the result
inverts the inflation intuition twice over: later dictionaries are not finer-grained
in general, and on the edges where inheritance is directly measurable, the movement
is toward condensation — with the citation apparatus steering what survives.

## 7. The indigenous register: where sense and citation are one unit

The indigenous lexica sit at 1.00 units per entry in table 1 — a floor that earlier
phases of this project have repeatedly warned against misreading: zero or floor
values under European detectors measure the **absence of European conventions**, not
absence of content. The promotion experiment sharpens this from a warning into a
structural finding. The *Vācaspatya*, whose articles wrap a Mīmāṃsā definition in
sigla-marked authority quotations and extended commentarial discussion, **does**
separate cleanly: a definition-unit window reproduces the archived sense count
exactly (9 = 9 for *dharma*). The *Śabdakalpadruma* does not: its *kośa*-style
synonym runs terminate in the authority citation itself (*ity Amaraḥ*), so
definition and attestation occupy a single *iti*-unit. Sense segmentation in SKD
therefore requires a unit grammar of its own — enumeration-internal citation — and
any future sense inventory for the indigenous register must treat the authority
formula as a *boundary* of the sense unit, not as extraneous apparatus to be
filtered. The evidence here is an exemplar — *dharma* in SKD versus VCP — not yet a
count; a source *kośa* parser that segments SKD records on their closing authorities
now exists, so scaling this contrast to the indigenous corpus is the immediate next
step. On that exemplar basis it is, to our knowledge, the first explicit
demonstration that the two Sanskrit lexicographic civilisations differ not merely in
citation style (the companion paper's result) but in whether *sense* and *citation*
are separable categories at all.

## 8. Limitations

- Sense-units for the lumped dictionaries are a calibrated proxy (semicolon-delimited
  meaning-clauses), not editorial senses; per-dictionary values sit within 13 % of
  the archived baseline with family ordering preserved.
- The survival metric uses gloss-text overlap within the Wilson line, where glosses
  are English on both sides; it is not yet defined across description languages.
- Verbs remain coarser than nominals throughout: preverb sub-entries, marker-run
  resets and reverse-index collocation noise are documented and review-gated, and the
  reviewed verb/noun asymmetry (reverse-equivalent evidence counts for nominals only)
  is enforced rather than solved.
- The three measurable inheritance edges are few; the Petersburg → Monier-Williams
  edge, philologically certain, is not yet sense-countable because MW marks no
  senses. Extending survival measurement to lumped descendants is the next slice.
- The §7 sense/citation-fusion contrast rests on a single lemma (*dharma*) in two
  indigenous lexica; it is an exemplar, not a frequency. A corpus-scale count over
  SKD/VCP is needed before the "two civilisations" claim is quantitative rather than
  demonstrative.
- The H2 survival panel (84 cited vs 723 uncited ancestor senses) is significant but
  drawn from 28 hand-chosen nouns on the Wilson line; replication on an independent,
  larger panel — and on a non-Wilson edge — would harden the citation-survival result.
- Ten checkpoint rows were reviewed by a single reviewer against the sources; the
  review packets are designed for multi-reviewer adjudication with agreement
  statistics, which is planned but not yet done.

## 9. Conclusion

On the corpus where the history of dictionaries can actually be measured edge by
edge, the received intuition fails twice. Sense granularity is a signature of
lexicographic school, flat in time; and inheritance condenses rather than expands,
with the citation apparatus acting as the selection pressure — cited senses survive
at 0.762, uncited at 0.591. Beneath both results lies a register boundary deeper
than citation style: the European tradition separates sense from authority; the
*kośa* tradition fuses them into one construction. Digital lexicography that aims
to align these traditions must model the fusion, not filter it out.

## References

*[TODO: secondary references — Wiegand on microstructure; Atkins & Rundell;
Hausmann; Zgusta; Vogel's* Indian Lexicography*; CDSL project literature;
companion drafts cited inline.]*
