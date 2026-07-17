# Use-Case Page Roadmap

_Created: 06-06-2026 · Last updated: 12-06-2026_

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
  family-profile artifact, scholar review packet, and generated 105-row review
  worksheet with empty human fields.
- Xref hub review and H5 anomaly scope now have proof-first documentation
  packages; H5 also has a first 130-row reviewed taxonomy plus a generated
  maker-QA candidate packet, and xref has a generated source-check packet
  with shared-core rows and prefix controls.
- R2 parser diagnostics now classify source/archive drift before any new
  sense-divergence or sense-alignment claims are broadened.
- All five R2 parser decision packets now have source-inspected proposal
  layers, and the R2 drift explanation/control packet explains all 70 current
  diagnostics while the checkpoint rows remain blocked on human review.
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
| 6 | H4 semantic-field package and `/tools/semantic-fields` | UC-CD-06, UC-LX-04 | scholars, students | Use AMAR-native fields as the active dictionary-first semantic review package. | generated review sample packet active |
| 7 | Xref hub review package | UC-LX-03, UC-LX-05 | scholars, reviewers | Label and source-check cross-reference hub families before paper use. | source-check packet active |
| 8 | H5 anomaly scope package | UC-CD-05, UC-RV-03 | makers, reviewers | Turn forensic anomaly signals into a proof-first review queue. | maker-QA packet active |

## GTD Documentation Board

| Bucket | Package | Next action | Done when |
|---|---|---|---|
| Done (2026-06-12) | R2 checkpoint review | All 10 rows decided in `src/data/review/r2-checkpoint-review.json` (7 promote-parser-candidate, 2 retain-side-evidence, 1 control-only; reviewer gasyoun, source-verified against local csl-orig). | The 10 `r2-checkpoint` rows have human decisions in `src/data/review/r2-checkpoint-review.json`. |
| Waiting | H4 semantic-field source review | Use `H4_SEMANTIC_FIELD_REVIEW_SAMPLES.md` and `data/lexico/h4_semantic_field_review_packet.json` to source-review the 105 SKD/VCP/AP/AP90/specialized/index-control rows. | Decisions separate topical signal from convention, scope, parser, and lookup-direction effects before paper use. |
| Waiting | H5 maker correction review | Submit or track the generated `divaraTa -> diviraTa` proposal with dictionary makers; do not edit dictionary source data automatically. | A maker decision or external issue link is recorded outside the generated proposal packet. |
| Waiting | Xref source-check adjudication | Use `MICROSTRUCTURE_XREF_SOURCE_CHECK.md` and `data/lexico/xref_source_check_packet.json` to review the 40 shared-core rows and 10 prefix controls. | Source-check decisions distinguish lexical evidence, prefix convention, and normalization risk before paper use. |
| Done | Xref source-check packet | Keep `data/lexico/xref_source_check_packet.json` and `MICROSTRUCTURE_XREF_SOURCE_CHECK.md` generated from `xref_hub_review.json` and `xref_edges.csv`. | The packet carries 50 `needs-source-check` rows, 106 source pointers, and empty human fields. |
| Done | H4 semantic-field review sample packet | Keep `data/lexico/h4_semantic_field_review_packet.json` and `H4_SEMANTIC_FIELD_REVIEW_SAMPLES.md` generated from the semantic-field family profiles. | The packet carries 105 `needs-review` rows across five H4 sample groups, with source/coverage pointers and empty human fields. |
| Done | THREE-AXES comparison packet | Keep `data/lexico/three_axis_comparison.json` and `THREE_AXIS_COMPARISON.md` generated from L0 known edges, sanhw1 overlap, convention scatter, and structural-register evidence. | The 13 known-edge rows expose content, convention, and microstructure/register axes separately, with focus rows ready for source-reading before a methods-note claim. |
| Done | H5 maker correction proposal | Keep `data/lexico/h5_maker_correction_proposal.json` and `H5_MAKER_CORRECTION_PROPOSAL.md` generated from the source-checked maker-QA packet. | The proposal cites MW/PWG source pointers for `divaraTa`, `diviraTa`, and rejected neighbor `devaraTa`, while the nine source-supported rows stay out of correction flow. |
| Done | R2 drift explanation/control packet | Keep `data/lexico/r2_drift_explanation.json` and `docs/R2_DRIFT_EXPLANATION.md` generated from the label proposals, checkpoint packet, and empty checkpoint review report. | All 70 diagnostics are explained by machine proposal labels, and all 10 checkpoint rows remain `needs-review`. |
| Done | H5 sample review | Keep the 130 reviewed rows in `src/data/review/h5-anomaly-review.json` and use the summary in `H5_GHOST_ANOMALY_SCOPE.md` before choosing maker QA follow-up rows. | The 130-item queue has `reviewedValue` labels and a summarized taxonomy. |
| Done | H5 maker QA source check | Keep `data/lexico/h5_maker_qa_candidates.json` and `H5_MAKER_QA_CANDIDATES.md` generated from the reviewed H5 report. | The first source-check worksheet has 10 checked candidate rows, 6 calibration rows, 9 source-supported non-correction rows, and 1 source-declared correction candidate. |
| Done | R2 parser decision packets | Keep `R2_REVIEW_PACKETS.md` linked to the five proposal layers: `R2_DIV_SOURCE_SCOPE_LABELS.md`, `R2_MARKER_RUN_SCOPE_LABELS.md`, `R2_AE_REVERSE_BAND_LABELS.md`, `R2_INDIGENOUS_ITI_AUTHORITY_LABELS.md`, and `R2_SOURCE_GAP_CONTROL_LABELS.md`. | The R2 splitter has source-inspected packet labels to guide the next rebuild experiment; the labels are not scholar-reviewed sense decisions. |
| Done | H5 anomaly taxonomy | Keep the review order and expected label set in `H5_GHOST_ANOMALY_SCOPE.md`. | Reviewers can start without treating F0/F2 rows as automatic error claims. |
| Done | H4 semantic fields | Keep H4 active with `false-low-risk`, `high-coverage-check`, `edition-delta-check`, `scope-baseline-check`, and `direction-index-control` starting labels. | H4 review samples are generated without outrunning the structural/microstructure docs. |
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
4. Use the generated H4 semantic-field review samples as the active
   AMAR-native source-review packet.
5. Document review queues by proof value.
6. Use the R2 drift explanation and checkpoint review gate before any
   non-final parser experiment or sense-divergence page.
7. Submit or track the single source-declared H5 maker correction proposal
   before any dictionary source edit.
8. Source-read the THREE-AXES focus rows before expanding the content vs
   convention method note into a three-axis claim.
9. Source-read the xref source-check packet before turning hub labels into
   paper-level lineage evidence.

## Boundary Links

The atlas may link outward, but it must not absorb external work:

- DCS and corpus comparison: [VisualDCS](https://github.com/gasyoun/VisualDCS)
- Standards/export work: [csl-standards](https://github.com/sanskrit-lexicon/csl-standards)
- GitHub/org observatory work: [csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory)

_Dr. Mārcis Gasūns_
