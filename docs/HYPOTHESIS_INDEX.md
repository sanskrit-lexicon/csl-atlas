# Cross-Repo Hypothesis Index

Date: 2026-06-05

Status: canonical boundary-aware hypothesis index for active and recent
`csl-atlas` research claims. This file routes each hypothesis to exactly one
owning repository. Refuted hypotheses remain visible as findings, because a
negative result is still evidence.

Types:

- **Type 1: Evidence-Backed Findings** - supported or refuted by current or
  archived atlas evidence.
- **Type 2: Strong Testable Hypotheses** - clear data and method exist; the
  next implementation can test them.
- **Type 3: Exploratory / External Hypotheses** - promising, but blocked by
  new data, another repository, or a future contract.

Boundary rule: `csl-atlas` owns dictionary evidence only. DCS/corpus work
belongs to VisualDCS, standards/export work belongs to `csl-standards`, and
GitHub/org-process evidence belongs to `csl-observatory`.

## Type 1: Evidence-Backed Findings

| ID | Type | Claim | Current status | Evidence | Owner repo | Next test | Paper/dashboard target |
|---|---|---|---|---|---|---|---|
| H2 | Type 1 | Citation-supported senses survive better than uncited senses. | Supported in the R2 sense-alignment findings: cited ancestor senses survive at 70%, uncited senses at 54%. | [`R2_FINDINGS.md`](R2_FINDINGS.md), [`R2_REBUILD_CONTRACT.md`](R2_REBUILD_CONTRACT.md), [`R2_PARSER_DIAGNOSTICS.md`](R2_PARSER_DIAGNOSTICS.md) | `csl-atlas` | Restore or rebuild the R2 generator package; use parser diagnostics to tighten high-drift families before broadening beyond the 28-noun panel and three inheritance edges. | Sense-alignment methods paper; maker divergence worklist. |
| WIL-SHS-SENSE | Type 1 | WIL to SHS is near-verbatim at sense level. | Supported in the measured panel: SHS sense glosses are 82% word-identical to Wilson sense glosses. | [`R2_FINDINGS.md`](R2_FINDINGS.md) | `csl-atlas` | Expand the Wilson-line panel and test citation-order preservation. | Paper H lineage section; sense-copying figure. |
| H1R | Type 1 | Sense granularity is a family/marking-style trait, not pure temporal inflation. | Replacement finding for H1: pure year trend is not supported; the current `/tools/r2-h1` page is a static snapshot of that result. | [`R2_FINDINGS.md`](R2_FINDINGS.md), [`R2_REBUILD_CONTRACT.md`](R2_REBUILD_CONTRACT.md), [`R2_PARSER_DIAGNOSTICS.md`](R2_PARSER_DIAGNOSTICS.md), `/tools/r2-h1` | `csl-atlas` | Restore reproducible R2 artifacts or reimplement them against current `csl-orig`; resolve parser-drift classes before using family as a covariate on broader data. | Paper L / sense-evolution section. |
| H3R | Type 1 | Descendants copy or condense senses unless edge-specific evidence proves expansion. | Replacement finding for H3: net-addition is not supported on measured inheritance edges. | [`R2_FINDINGS.md`](R2_FINDINGS.md), [`R2_REBUILD_CONTRACT.md`](R2_REBUILD_CONTRACT.md), [`R2_PARSER_DIAGNOSTICS.md`](R2_PARSER_DIAGNOSTICS.md) | `csl-atlas` | Test more directed edges after parser coverage improves and high-priority row-count drift is explained. | Paper H; sense-drift dashboard. |
| SKD-ANU | Type 1 | The SKD anubandha key decodes indigenous grammatical coding. | Verified and applied from SKD front matter; no longer only a hypothesis. | [`MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md`](MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md) | `csl-atlas` | Add scholar-reviewed notes for residual edge cases and expose confidence labels where needed. | Indigenous-root parser; Article 9. |
| H6 | Type 1 | Structural register predicts dictionary family. | Prototype-backed, charted, and review-classed: citation style plus grammar-marking separates traditions, and `structural_register_h6_review.json` compares 13 L0 known edges against H6 space. | [`H6_STRUCTURAL_REGISTER_SCATTER.md`](H6_STRUCTURAL_REGISTER_SCATTER.md), `data/lexico/structural_register_h6_review.json`, `/tools/structural-register` | `csl-atlas` | Scholar-review the positive control, genealogy-structure tensions, and structural-convergence prompts before paper use. | Macro profile dashboard; Paper M/H method note. |
| M1-M2-MACRO | Type 1 | MW and the Petersburg dictionaries differ by macro/micro trade-off. | Supported: MW promotes derivatives and preverb forms to headwords; Petersburg dictionaries nest them. | [`MICROSTRUCTURE_M1_M2_RESULTS.md`](MICROSTRUCTURE_M1_M2_RESULTS.md) | `csl-atlas` | Add normalized lemma-to-depth ratios for shared verb roots. | Article 9; microstructure dashboard. |
| XREF-CORE | Type 1 | Cross-reference graphs preserve a shared core but not wholesale descent. | Supported and charted: AP/AP90 is a positive control; MW/PWG has a shared core plus large independent expansion. | [`MICROSTRUCTURE_XREF_LINEAGE.md`](MICROSTRUCTURE_XREF_LINEAGE.md), [`MICROSTRUCTURE_XREF_HUB_REVIEW.md`](MICROSTRUCTURE_XREF_HUB_REVIEW.md), `/tools/xref-lineage` | `csl-atlas` | Review hub families and label shared-core samples before paper use. | Lineage graph dashboard; Paper H. |
| M7-ROOT-AGREE | Type 1 | Independent root-dictionary parsers agree often enough to validate the recovered grammar layer. | Supported: compatible agreement is 85.5% for gana, 75.3% for pada, and 81.4% for transitivity. | [`MICROSTRUCTURE_ROOT_AGREEMENT.md`](MICROSTRUCTURE_ROOT_AGREEMENT.md) | `csl-atlas` | Sample conflicts and classify homonymy vs real disagreement vs parser weakness. | Article 9; indigenous grammar appendix. |
| H4 | Type 1 | Semantic-field bias is measurable with Amarakosa-native fields. | Supported prototype: M8 maps AMAR vargas to dictionary headword coverage, `/tools/semantic-fields` visualizes the result, and the family-profile artifact groups 43 dictionaries into 5 evidence-bearing families. | [`MICROSTRUCTURE_SEMANTIC_FIELDS.md`](MICROSTRUCTURE_SEMANTIC_FIELDS.md), [`H4_SEMANTIC_FIELD_REVIEW.md`](H4_SEMANTIC_FIELD_REVIEW.md), `data/lexico/semantic_field_family_profiles.json`, `/tools/semantic-fields` | `csl-atlas` | Use the H4 review packet to adjudicate samples without importing corpus categories. | Semantic-field dashboard; Paper L. |
| INDIG-CITE | Type 1 | SKD/VCP are citation-dense despite low `<ls>` tagging. | Supported: indigenous quotation and `iti` citation style must be counted separately. | [`MICROSTRUCTURE_ZERO_MEANING.md`](MICROSTRUCTURE_ZERO_MEANING.md), [`H6_STRUCTURAL_REGISTER_SCATTER.md`](H6_STRUCTURAL_REGISTER_SCATTER.md) | `csl-atlas` | Add per-dictionary citation-format normalizers where needed. | Evidence-label docs; citation-register scatter. |

## Type 2: Strong Testable Hypotheses

| ID | Type | Claim | Current status | Evidence | Owner repo | Next test | Paper/dashboard target |
|---|---|---|---|---|---|---|---|
| KOW-WIL | Type 2 | KOW derives from or translates WIL. | Plausible cross-language lineage hypothesis; source acquisition and directed tests still needed. | [`LEXICOGRAPHY_ROADMAP.md`](LEXICOGRAPHY_ROADMAP.md) | `csl-atlas` | Combine lemma overlap, citation overlap/order, translation similarity, and preface evidence. | Paper L specialized/cross-language section. |
| PET-MW-CITE | Type 2 | PWG/PW/PWK to MW lineage is visible through citation truncation and rare terms. | Strong route for directed Petersburg-to-MW evidence. | [`LEXICOGRAPHY_ROADMAP.md`](LEXICOGRAPHY_ROADMAP.md), [`MICROSTRUCTURE_XREF_LINEAGE.md`](MICROSTRUCTURE_XREF_LINEAGE.md) | `csl-atlas` | Build citation-truncation and rare-term/hapax overlap tests. | Paper H; citation truncation dashboard. |
| H5 | Type 2 | Ghost entries and rare anomalies identify both lineage and QA targets. | First proof-first review queue exists: 130 F0/F2/known-correction rows with preserved review fields; no error claims before review. | [`H5_GHOST_ANOMALY_SCOPE.md`](H5_GHOST_ANOMALY_SCOPE.md), `src/data/review/h5-anomaly-review.json`, [`REVIEW_QUEUE_PROOFS.md`](REVIEW_QUEUE_PROOFS.md) | `csl-atlas` | Review the sample and write the taxonomy: legitimate form, variant convention, possible typo, ghost candidate, lineage-only, or parser artifact. | Maker QA worklist; forensic methods note. |
| H4-FIELD-FAMILY | Type 2 | AMAR field profiles differ by dictionary family, not only by gross coverage. | Family-profile artifact exists with top/low fields, distinctive clusters, and 12 high-spread contrast prompts; review packet exists but human adjudication is still pending. | [`MICROSTRUCTURE_SEMANTIC_FIELDS.md`](MICROSTRUCTURE_SEMANTIC_FIELDS.md), [`H4_SEMANTIC_FIELD_INTERPRETATION.md`](H4_SEMANTIC_FIELD_INTERPRETATION.md), [`H4_SEMANTIC_FIELD_REVIEW.md`](H4_SEMANTIC_FIELD_REVIEW.md), `data/lexico/semantic_field_family_profiles.json`, `/tools/semantic-fields` | `csl-atlas` | Review SKD false lows, VCP high coverage, AP/AP90 deltas, specialized baselines, and index/reverse controls. | Semantic-field interpretation note and review packet. |
| XREF-HUBS | Type 2 | Cross-reference hub families preserve lineage and convention differences. | Hub-review artifact exists: top targets are labeled as prefix-convention, lexical-target, or normalization-risk, with a 40-edge MW/PWG shared-core sample. | [`MICROSTRUCTURE_XREF_LINEAGE.md`](MICROSTRUCTURE_XREF_LINEAGE.md), [`MICROSTRUCTURE_XREF_HUB_REVIEW.md`](MICROSTRUCTURE_XREF_HUB_REVIEW.md), `data/lexico/xref_hub_review.json` | `csl-atlas` | Scholar-review the MW/PWG shared-core sample and confirm prefix/convention hubs before paper use. | Cross-reference graph page; Paper H. |
| THREE-AXES | Type 2 | Content, convention, and microstructure inheritance are separate axes. | Strong candidate: CAE/CCS and MW/PWG already show axis divergence. | [`MICROSTRUCTURE_M1_M2_RESULTS.md`](MICROSTRUCTURE_M1_M2_RESULTS.md), [`LEXICOGRAPHY_ROADMAP.md`](LEXICOGRAPHY_ROADMAP.md) | `csl-atlas` | Build a three-axis comparison table for known families. | Two-axis methods note expanded to three axes. |
| REVIEW-PROOF | Type 2 | Review queues can be treated as proof instruments, not only cleanup lists. | Queue proof taxonomy exists; review outcomes still need to be sampled. | [`REVIEW_QUEUE_PROOFS.md`](REVIEW_QUEUE_PROOFS.md) | `csl-atlas` | Review the planned samples and record which uncertainty class each queue resolves. | Release review report; methods appendix. |

## Type 3: Exploratory / External Hypotheses

| ID | Type | Claim | Current status | Evidence | Owner repo | Next test | Paper/dashboard target |
|---|---|---|---|---|---|---|---|
| DCS-JOIN | Type 3 | Dictionary-corpus frequency joins can improve reader difficulty and learning paths. | External: belongs to VisualDCS first; atlas may consume a compact dictionary-facing summary later. | [`RESEARCH_LAYER_ROADMAP.md`](RESEARCH_LAYER_ROADMAP.md) | `VisualDCS` | Define a compact SLP1-keyed output contract in VisualDCS. | Student learning paths; Reader Lookup extension. |
| FRAC-CORPUS | Type 3 | FrAC publication from corpus attestations can connect lexical records to corpus evidence. | External and frozen until real corpus evidence exists. | [`TEI_ONTOLEX_MIGRATION.md`](TEI_ONTOLEX_MIGRATION.md) | `csl-standards` | Wait for VisualDCS corpus evidence; do not invent FrAC claims from dictionary-only records. | Standards workbench; future RDF publication. |
| TEI-ONTOLEX-EXT | Type 3 | TEI/OntoLex loss reports can become a formal Sanskrit lexicographic extension argument. | Standards workbench hypothesis, not atlas implementation. | [`TEI_ONTOLEX_MIGRATION.md`](TEI_ONTOLEX_MIGRATION.md) | `csl-standards` | Turn pilot loss reports into extension requirements in `csl-standards`. | Standards paper; TEI/OntoLex profile docs. |
| MW-ATTENTION | Type 3 | MW receives disproportionate digital-project attention. | Boundary-sensitive: GitHub/org-process evidence belongs to `csl-observatory`; atlas may only provide dictionary evidence for a separate richness comparison. | [`METALEXICOGRAPHY_ROADMAP.md`](METALEXICOGRAPHY_ROADMAP.md) | `csl-observatory` | Define an observatory-owned attention metric and link atlas dictionary-richness evidence without copying it. | Observatory/process dashboard; boundary note. |
| LEXEMEHUB-FUTURE | Type 3 | A LexemeHub-style integration layer may become useful later. | Future only; not a current atlas roadmap item until stable cross-repo contracts exist. | [`REVIEW_RELEASE_ROADMAP.md`](REVIEW_RELEASE_ROADMAP.md) | `csl-atlas` | Revisit only after dictionary, VisualDCS, and standards outputs expose stable contracts. | Future integration roadmap, not current release. |

## Maintenance Rules

- Every row must have exactly one owner repo.
- `csl-observatory` may own only GitHub/org-process hypotheses.
- Refuted hypotheses stay visible as Type 1 findings with replacement IDs.
- External hypotheses may be linked from the atlas, but implementation belongs
  in the owner repository named in the row.
- Do not add DCS passages, TEI/OntoLex/FrAC generators, GitHub metrics, or a
  broad LexemeHub object to the atlas to satisfy a hypothesis row.
