# Use-Case Page Roadmap

Date: 2026-06-04

Status: maintainer decisions captured for the next documentation and analysis
layer. This roadmap turns the active use cases into page-sized documentation
targets before adding new analysis-method prose.

## Decisions

- Build use-case pages before analysis method notes.
- Make "Which dictionary should I use?" the first reader-facing page.
- Every public tool, chart, or page gets a compact trust block: Evidence,
  Limitations, Validation, Owner repo.
- Prioritize the H6 structural-register scatter before SKD anubandha review.
- Treat the microstructure work as a scholar-facing doc family:
  `MICROSTRUCTURE_PROFILE.md`, `MICROSTRUCTURE_METHODS.md`, and
  `MICROSTRUCTURE_FINDINGS.md`.
- For review queues, first document what each queue proves; write procedural
  "how to review" notes only after that.
- H4 semantic-field analysis comes after the page layer, trust template, H6
  scatter, and microstructure doc family are in place.

## Page Order

| Order | Page | Primary use cases | Audience | Purpose | Status |
|---|---|---|---|---|---|
| 1 | `DICTIONARY_USER_GUIDE.md` | UC-RD-02, UC-RD-07 | public readers | Answer which dictionary to start with and why. | active first page |
| 2 | [`READER_LOOKUP_EXPLAINER.md`](READER_LOOKUP_EXPLAINER.md) | UC-RD-01, UC-RD-03, UC-RD-04, UC-RD-05 | public readers | Explain what a lookup result means, including no-result and ambiguous-result cases. | active second page |
| 3 | Review queue proof pages | UC-CD-04, UC-CD-05, UC-LX-05, UC-RV-02, UC-RV-03 | reviewers, scholars | Explain what each queue proves before explaining how to review it. | planned |
| 4 | H6 structural-register scatter | UC-LX-03, UC-DEV-04 | scholars | Turn the supported H6 claim into a traceable chart/page spec. | planned before H4 |
| 5 | Microstructure doc family | UC-LX-01, UC-LX-02, UC-LX-03 | scholars | Give the M1-M5 profile, methods, and findings one coherent entry point. | active scaffold |
| 6 | H4 semantic-field package | UC-CD-06, UC-LX-04 | scholars, students | Build the Amarakosa-native semantic-field analysis after the above layers settle. | later |

## Public Page Contract

Every public atlas page or tool must include the short form of
[`CHART_TRUST_TEMPLATE.md`](CHART_TRUST_TEMPLATE.md):

- Evidence
- Limitations
- Validation
- Owner repo

For charts and research pages, include the extended block as well: source files,
generation command, evidence labels, known false positives, known false
negatives, and review status.

## Review Queue Documentation Rule

For every queue, write the proof page first:

| Queue family | First documentation question | Later procedure question |
|---|---|---|
| Low-confidence dictionary alignments | What kind of alignment uncertainty does this queue reveal? | How does a reviewer accept, correct, or block a row? |
| Source-siglum unknowns and aliases | What does the frequency-ranked list prove about citation normalization? | How does a reviewer add an alias or source expansion? |
| POS/gender conflicts | What kind of dictionary disagreement does the sample represent? | How does a reviewer preserve a correction across generator reruns? |
| Sense divergence | What does cross-dictionary disagreement prove about inheritance or condensation? | How does a reviewer adjudicate a sense boundary? |

## Analysis Sequence

1. Land the use-case page layer and trust template.
2. Write the scholar-facing microstructure profile, methods, and findings docs.
3. Specify and then build the H6 structural-register scatter.
4. Document review queues by proof value.
5. Start H4 semantic-field analysis after the above items are stable.

## Boundary Links

The atlas may link outward, but it must not absorb external work:

- DCS and corpus comparison: [VisualDCS](https://github.com/gasyoun/VisualDCS)
- Standards/export work: [csl-standards](https://github.com/sanskrit-lexicon/csl-standards)
- GitHub/org observatory work: [csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory)
