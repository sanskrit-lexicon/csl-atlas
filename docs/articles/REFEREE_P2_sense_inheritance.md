# Pre-submission referee report — P2 (*Condensation, Not Inflation*)

Date: 2026-06-13

Status: internal adversarial review of
[`paper_sense_inheritance.md`](paper_sense_inheritance.md), written in the
voice of a *Lexicographica* / *IJL* referee, to surface the objections a real
reviewer will raise before submission. Points marked **[fixed]** were applied to
the manuscript in the same change; **[author]** points need the author's decision
or new analysis. This report is not part of the manuscript.

## Recommendation

**Major revision.** The three findings (granularity is a family trait, citation
predicts survival, descendants condense) are genuine, well-motivated, and now
statistically supported. Two classes of objection stand between the draft and
acceptance: (a) the **citation-vs-centrality confound** behind the headline H2
claim, and (b) the **thin evidential base** for the most striking claims (the
indigenous-fusion exemplar; the three inheritance edges; the 28-noun panel). None
is fatal; all are addressable.

## Summary of contribution

A genuinely novel use of a digitised dictionary family to measure sense behaviour
across documented lines of descent, with a method (Sanskrit-anchored, convention-
respecting sense counting) that is itself a contribution. The corrective to the
"later = finer" intuition is clean and useful. The paper is honest about its
machinery to an unusual degree.

## Major points

**M1. The headline survival gap had no significance test. [fixed]**
0.762 vs 0.591 was reported as "a 17-point gap" with no inference. Added: Wilson
95 % CIs ([0.661, 0.840] vs [0.554, 0.626], non-overlapping) and a two-proportion
test (*z* = 3.0, *p* ≈ 0.002; χ² = 9.3). H1's *absence* of a trend is now also
quantified as non-significant (*r* = 0.036, *t* = 0.11, df = 9), which is the
correct framing for a null result.

**M2. "Citation predicts survival" is stated causally over a correlational design. [author]**
The sharpest objection. Cited senses may survive more *because they are also the
central, high-frequency senses* — citation could be a proxy for centrality, not an
independent cause. The claim "a citation is a survival predictor" should either be
softened to association, or — better — defended by controlling for sense centrality
(e.g. does the cited-vs-uncited gap persist *within* first-listed senses, or within
a frequency stratum?). This is the revision most likely to be demanded.

**M3. The §7 sense/citation-fusion claim rested on one lemma. [fixed, partially]**
"First corpus-scale demonstration" over a single exemplar (*dharma*) was an
over-claim; softened to "first explicit demonstration" on an exemplar basis, with
the kośa parser flagged as the route to a real count. **[author]** A count over
SKD/VCP (now mechanisable) would convert the boldest claim from demonstrative to
quantitative and is worth doing before submission.

**M4. The survival metric is gloss-overlap at a single, unjustified threshold. [author]**
Survival = gloss-text overlap ≥ 0.15 on the English Wilson line. Two exposures: the
threshold is arbitrary (show the result is stable across 0.10–0.25), and the metric
is English-only, so it measures *gloss persistence*, not sense survival across the
German/Sanskrit material. State this scope explicitly in §3 and add a
threshold-sensitivity line.

**M5. "No measured edge expands" rests on n = 3 edges. [author]**
And one of the three (Apte 1890→1957) the paper itself flags as possibly a
marker-parsing artifact. The general claim is defensible but should be stated as
"on the three edges where senses are countable on both sides," not as a law.

**M6. H1's family means depend on the lumped-sense proxy, whose ground truth is a
machine baseline. [author]**
The semicolon-clause proxy is validated only against the archived counts (±13 %),
which are themselves regex output, not editorial senses — the very gap the MW
**gold-standard validation** ([`analysis/GOLD_STANDARD.md` in MWS docs-pass]) was
built to close. Cross-reference that instrument and state that the family ordering
is robust to proxy error of the documented magnitude.

**M7. The "two civilisations" framing outruns its indigenous evidence. [author]**
The European side is rich (11 dictionaries, 3 edges); the indigenous side is SKD +
VCP on *dharma*. The framing is the paper's most quotable claim and its thinnest
support. Either narrow the framing to what the exemplar shows, or add the SKD/VCP
count from M3.

## Minor points

- **[author]** References: the `[TODO]` block needs Wiegand (microstructure),
  Atkins & Rundell, Zgusta, and Vogel's *Indian Lexicography*; the survival/decay
  literature; and the companion drafts cited inline.
- **[fixed]** Abstract now reports the survival result as significant.
- **[author]** State the 0.15 survival threshold in §3 (Method), not only in §5.
- **[author]** "We know of no comparable quantitative result for any dictionary
  family" — soften to a scoped novelty claim; an over-strong claim invites a
  counter-example hunt.
- **[author]** The abstract is dense (~280 words of results); consider trimming the
  method sentence now that §3 carries it.

## Editorial response (applied vs pending)

| Point | Action |
|---|---|
| M1 significance | **applied** — CIs + *p* in §5; non-significance in §4; abstract |
| M2 confound | pending — author: control for centrality or soften to association |
| M3 fusion exemplar | **applied** (softened) + pending (SKD/VCP count via the kośa parser) |
| M4 threshold/scope | pending — add sensitivity line + state English-gloss scope |
| M5 n = 3 edges | pending — scope the "none expand" claim |
| M6 proxy ground truth | pending — cross-reference the MW gold standard |
| M7 framing vs evidence | pending — narrow framing or add the count |
| References, abstract, threshold-in-§3 | pending — author |

The applied fixes harden the empirical core; the pending items are a coherent
single revision pass (centrality control + an SKD/VCP fusion count + a
threshold-sensitivity line + references) that would carry the paper to acceptance.
