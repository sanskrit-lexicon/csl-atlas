# Use-Case Page Roadmap

Date: 2026-06-04

Status: maintainer decisions captured for the next documentation and analysis
layer. This roadmap turns the active use cases into page-sized documentation
targets before adding new analysis-method prose.

## Decisions

- Build use-case pages before analysis method notes.
- Make "Which dictionary should I use?" the first reader-facing page and a
  top-level public route: `/dictionary-chooser`.
- Every public tool, chart, or page gets a compact trust block: Evidence,
  Limitations, Validation, Owner repo, Next use.
- Use a GTD-style next action in every major dashboard trust block: after the
  reader sees the evidence and caveats, the page should say what to do next.
- H6 structural-register scatter and H4 semantic-field chart are implemented;
  both now have generated review-prompt artifacts, and next candidates can build
  on those chart-trust examples without mixing in corpus or standards evidence.
- Treat the microstructure work as a scholar-facing doc family:
  `MICROSTRUCTURE_PROFILE.md`, `MICROSTRUCTURE_METHODS.md`, and
  `MICROSTRUCTURE_FINDINGS.md`, starting with
  `MICROSTRUCTURE_HEADWORD_SUBENTRY.md`.
- For review queues, first document what each queue proves; write procedural
  "how to review" notes only after that.
- H4 semantic-field analysis now has a data package, chart, interpretation note,
  family-profile artifact, and scholar review packet.
- Xref hub review and H5 anomaly scope now have proof-first documentation
  packages; the xref hub review also has a generated review-prompt artifact.
- R2 parser diagnostics now classify source/archive drift before any new
  sense-divergence or sense-alignment claims are broadened.
- The dictionary-comparison tool family now carries compact trust blocks for
  generated evidence, limitations, validation, and owner repo.
- The remaining MW, typology, lexicographic-structure, timeline, and archived
  R2 tools now carry compact trust blocks.
- The public Observable page set now has trust blocks across the landing page,
  dictionary chapters, paper tour pages, audit page, and tool pages.

## Page Order

| Order | Page | Primary use cases | Audience | Purpose | Status |
|---|---|---|---|---|---|
| 1 | [`UC_RD_02_DICTIONARY_CHOOSER.md`](UC_RD_02_DICTIONARY_CHOOSER.md) and `/dictionary-chooser` | UC-RD-02 | public readers | Answer which dictionary to start with and why; MW is the default public route. | active first page; public top-level page |
| 1a | [`DICTIONARY_USER_GUIDE.md`](DICTIONARY_USER_GUIDE.md) | UC-RD-02, UC-RD-07 | public readers | Explain the chooser in broader reader-guide context. | active companion |
| 2 | [`READER_LOOKUP_EXPLAINER.md`](READER_LOOKUP_EXPLAINER.md) | UC-RD-01, UC-RD-03, UC-RD-04, UC-RD-05 | public readers | Explain what a lookup result means, including no-result and ambiguous-result cases. | active second page |
| 3 | [`REVIEW_QUEUE_PROOFS.md`](REVIEW_QUEUE_PROOFS.md) | UC-CD-04, UC-CD-05, UC-LX-05, UC-RV-02, UC-RV-03 | reviewers, scholars | Explain what each queue proves before explaining how to review it. | proof doc active; four public queue pages carry proof/trust blocks |
| 4 | [`H6_STRUCTURAL_REGISTER_SCATTER.md`](H6_STRUCTURAL_REGISTER_SCATTER.md), [`H6_STRUCTURAL_REGISTER_REVIEW.md`](H6_STRUCTURAL_REGISTER_REVIEW.md), and `/tools/structural-register` | UC-LX-03, UC-DEV-04 | scholars | Turn the supported H6 claim into a traceable chart/page. | edge and family labels done |
| 5 | [`MICROSTRUCTURE_HEADWORD_SUBENTRY.md`](MICROSTRUCTURE_HEADWORD_SUBENTRY.md) plus the microstructure doc family | UC-LX-01, UC-LX-02, UC-LX-03 | scholars | Start with the easiest parsed structure: headwords vs nested subentries. | active first microstructure page |
| 6 | H4 semantic-field package and `/tools/semantic-fields` | UC-CD-06, UC-LX-04 | scholars, students | Use AMAR-native fields as the active dictionary-first semantic review package. | interpretation and review packet active |
| 7 | Xref hub review package | UC-LX-03, UC-LX-05 | scholars, reviewers | Label cross-reference hub families before paper use. | active labels documented |
| 8 | H5 anomaly scope package | UC-CD-05, UC-RV-03 | makers, reviewers | Turn forensic anomaly signals into a proof-first review queue. | taxonomy active; human review pending |

## GTD Documentation Board

| Bucket | Package | Next action | Done when |
|---|---|---|---|
| Next | R2 parser decision packet | Use `R2_REVIEW_PACKETS.md` to start with `div-source-scope`, then marker runs, AE reverse bands, indigenous `iti`, and source-gap controls. | R2 has source-reviewed parser decisions before broader sense-divergence pages. |
| Waiting | H5 sample review | Classify known corrections and null controls first, then raw-headword-exclusive and shared-doublet rows. | The 130-item queue has human `reviewedValue` labels and a summarized taxonomy. |
| Done | H5 anomaly taxonomy | Keep the review order and expected label set in `H5_GHOST_ANOMALY_SCOPE.md`. | Reviewers can start without treating F0/F2 rows as automatic error claims. |
| Done | H4 semantic fields | Keep H4 active with `false-low-risk`, `high-coverage-check`, `edition-delta-check`, `scope-baseline-check`, and `direction-index-control` starting labels. | H4 review samples can be interpreted without outrunning the structural/microstructure docs. |
| Done | Xref hub review | Keep `prefix-convention`, `lexical-target`, `edition-continuity`, `normalization-risk`, `too-sparse`, and `lexical-shared-core` visible in the xref review docs. | Xref hub labels reuse the same review-label discipline after H4 activation. |
| Done | Public trust blocks | Keep `Evidence`, `Limitations`, `Validation`, `Owner repo`, and `Next use` visible on public pages. | Trust-block audit finds no public Markdown page missing the required fields. |
| Done | MW public default | MW remains the public first stop in chooser, landing, reader guide, and lookup caveats. | Search finds no public-reader route that tells newcomers to start elsewhere for ordinary lookup. |
| Done | Public dictionary chooser polish | Keep MW as the public default, maintain the decision-card route, and test `/dictionary-chooser` after public wording changes. | A reader can choose MW first and understand the second dictionary without learning lexicographic history first. |
| Done | H6 review labels | Keep the 13 edge-comparison labels in `H6_STRUCTURAL_REGISTER_REVIEW.md` as the reviewed interpretation layer. | Each H6 edge has a reviewed interpretation such as `format-shift`, `citation-truncation`, `structural-convergence`, or `positive-control-confirmed`. |
| Done | H6 family outlier labels | Keep the family-outlier labels in `H6_STRUCTURAL_REGISTER_REVIEW.md` as the reviewed interpretation layer. | Each outlier family has an interpretation such as `genre-outlier`, `detector-blindness`, `indigenous-prose-register`, or `lookup-direction-split`. |
| Done | First microstructure layer | Use `MICROSTRUCTURE_HEADWORD_SUBENTRY.md` as the first scholar-facing microstructure page. | The next layer is explicitly sense segmentation. |
| Done | Microstructure sense segmentation | Keep `MICROSTRUCTURE_SENSE_SEGMENTATION.md` linked from the microstructure doc family. | A scholar can tell where sense counts are reliable, where prose segmentation blocks counting, and which dictionaries need R2 rebuild work. |
| Blocked | Corpus frequency joins | Keep out of atlas until VisualDCS supplies a compact dictionary-facing contract. | A VisualDCS output contract exists and can be consumed without importing passage dashboards. |

## Public Page Contract

Every public atlas page or tool must include the short form of
[`CHART_TRUST_TEMPLATE.md`](CHART_TRUST_TEMPLATE.md):

- Evidence
- Limitations
- Validation
- Owner repo
- Next use

For charts and research pages, include the extended block as well: source files,
generation command, evidence labels, known false positives, known false
negatives, review status, and the next action.

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
2. Write the scholar-facing microstructure profile, methods, and findings docs,
   beginning with headword/subentry structure.
3. Use the implemented H6 structural-register scatter as the first full
   chart-trust/method example.
4. Use H4 semantic fields as the active AMAR-native semantic review package,
   beginning with SKD false-low checks.
5. Document review queues by proof value.
6. Use `data/lexico/r2_parser_diagnostics.json` to tighten the R2 splitter
   before building sense-divergence pages.
7. Review the first H5 anomaly sample and summarize the taxonomy.

## Boundary Links

The atlas may link outward, but it must not absorb external work:

- DCS and corpus comparison: [VisualDCS](https://github.com/gasyoun/VisualDCS)
- Standards/export work: [csl-standards](https://github.com/sanskrit-lexicon/csl-standards)
- GitHub/org observatory work: [csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory)
