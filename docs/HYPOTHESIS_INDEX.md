# Cross-Repo Hypothesis Index

Date: 2026-06-04

Status: canonical boundary-aware hypothesis index. This file routes active and
recent hypotheses to the repository that owns the next test. It does not move
scope across repository boundaries.

Types:

- **Type 1: Evidence-Backed Findings** - already supported or refuted by current data.
- **Type 2: Strong Testable Hypotheses** - clear data and method exist; next implementation can test them.
- **Type 3: Exploratory / External Hypotheses** - promising, but blocked by new data, another repo, or a future contract.

## Type 1: Evidence-Backed Findings

| ID | Type | Claim | Current status | Evidence | Owner repo | Next test | Paper/dashboard target |
|---|---|---|---|---|---|---|---|
| H2 | Type 1 | Citation-supported senses survive better than uncited senses. | Supported: cited ancestor senses survive at 70%, uncited at 54%. | [`R2_FINDINGS.md`](R2_FINDINGS.md) | `csl-atlas` | Broaden beyond the 28-noun panel and three inheritance edges. | Sense-alignment methods paper; maker divergence worklist. |
| WIL-SHS-SENSE | Type 1 | WIL to SHS is near-verbatim at sense level. | Supported: SHS sense glosses are 82% word-identical to Wilson sense glosses in the tested panel. | [`R2_FINDINGS.md`](R2_FINDINGS.md) | `csl-atlas` | Expand the Wilson-line panel and add citation-order preservation. | Paper H lineage section; sense-copying figure. |
| H1R | Type 1 | Sense granularity is a family/marking-style trait, not pure temporal inflation. | Replacement finding for H1: pure time trend is not supported. | [`R2_FINDINGS.md`](R2_FINDINGS.md) | `csl-atlas` | Use family as a covariate in later sense-evolution work. | Paper L / sense-evolution section. |
| H3R | Type 1 | Descendants copy or condense senses unless edge-specific evidence proves expansion. | Replacement finding for H3: net-addition is not supported on measured edges. | [`R2_FINDINGS.md`](R2_FINDINGS.md) | `csl-atlas` | Test more directed edges after parser coverage improves. | Paper H; sense-drift dashboard. |
| H6 | Type 1 | Structural register predicts dictionary family. | Prototype-backed: citation style plus grammar-marking separates Western-tagged, indigenous, and index traditions. | [`RESEARCH_LAYER_ROADMAP.md`](RESEARCH_LAYER_ROADMAP.md) | `csl-atlas` | Build the citation-register scatter and compare clusters to L0 genealogy. | Macro profile dashboard; Paper M/H method note. |
| M1-M2-MACRO | Type 1 | MW and the Petersburg dictionaries differ by macro/micro trade-off. | Supported: MW promotes derivatives/preverb forms to headwords; Petersburg dictionaries nest them. | [`MICROSTRUCTURE_M1_M2_RESULTS.md`](MICROSTRUCTURE_M1_M2_RESULTS.md) | `csl-atlas` | Add a normalized lemma-to-depth ratio for shared verb roots. | Article 9; microstructure dashboard. |
| INDIG-CITE | Type 1 | SKD/VCP are citation-dense despite low `<ls>` tagging. | Supported: indigenous quotation and `iti` citation style must be counted separately. | [`RESEARCH_LAYER_ROADMAP.md`](RESEARCH_LAYER_ROADMAP.md), [`MICROSTRUCTURE_ZERO_MEANING.md`](MICROSTRUCTURE_ZERO_MEANING.md) | `csl-atlas` | Add a per-dict citation-format normalizer. | Evidence-label docs; citation-register scatter. |

## Type 2: Strong Testable Hypotheses

| ID | Type | Claim | Current status | Evidence | Owner repo | Next test | Paper/dashboard target |
|---|---|---|---|---|---|---|---|
| SKD-ANU | Type 2 | SKD/VCP crosswalk can recover indigenous grammatical coding. | Strong candidate: M4 proves indigenous root detection; anubandha decoding awaits philological verification. | [`MICROSTRUCTURE_ZERO_MEANING.md`](MICROSTRUCTURE_ZERO_MEANING.md) | `csl-atlas` | Verify `Na`, `Ya`, `i`, `u`; adjudicate `f`, `I`, `o`; then emit SKD `pada` with confidence labels. | Indigenous-root parser; Article 9. |
| KOW-WIL | Type 2 | KOW derives from or translates WIL. | Plausible cross-language lineage hypothesis. | [`LEXICOGRAPHY_ROADMAP.md`](LEXICOGRAPHY_ROADMAP.md) | `csl-atlas` | Combine lemma overlap, citation overlap/order, translation similarity, and preface evidence. | Paper L specialized/cross-language section. |
| PET-MW-CITE | Type 2 | PWG/PW/PWK to MW lineage is visible through citation truncation and rare terms. | Strong route for directed Petersburg-to-MW evidence. | [`LEXICOGRAPHY_ROADMAP.md`](LEXICOGRAPHY_ROADMAP.md) | `csl-atlas` | Build citation-truncation and rare-term/hapax overlap tests. | Paper H; citation truncation dashboard. |
| H5 | Type 2 | Ghost entries and rare anomalies identify both lineage and QA targets. | Proposed; method is clear from forensic/rarity signals. | [`RESEARCH_LAYER_ROADMAP.md`](RESEARCH_LAYER_ROADMAP.md), [`LEXICOGRAPHY_ROADMAP.md`](LEXICOGRAPHY_ROADMAP.md) | `csl-atlas` | Define anomaly classes and run rarity-weighted pair matching. | Maker QA worklist; forensic methods note. |
| H4 | Type 2 | Semantic-field bias is measurable with Amarakosa-native fields. | Scheme decided; implementation not yet built. | [`RESEARCH_LAYER_ROADMAP.md`](RESEARCH_LAYER_ROADMAP.md) | `csl-atlas` | Map AMAR hierarchy to dictionary gloss/headword evidence and produce per-dict field distributions. | Semantic-field treemap; Paper L. |
| XREF-GRAPH | Type 2 | Cross-reference graphs preserve lineage. | Strong candidate from M3: PWG `Vgl.` and MW `cf.` produce comparable Sanskrit target graphs. | [`MICROSTRUCTURE_M1_M2_RESULTS.md`](MICROSTRUCTURE_M1_M2_RESULTS.md) | `csl-atlas` | Compare PWG `Vgl.` targets with MW `cf.` targets and compound-family hubs. | Lineage graph dashboard; Paper H. |
| THREE-AXES | Type 2 | Content, convention, and microstructure inheritance are separate axes. | Strong candidate: CAE/CCS and MW/PWG already show axis divergence. | [`MICROSTRUCTURE_M1_M2_RESULTS.md`](MICROSTRUCTURE_M1_M2_RESULTS.md), [`LEXICOGRAPHY_ROADMAP.md`](LEXICOGRAPHY_ROADMAP.md) | `csl-atlas` | Build a three-axis comparison table for known families. | Two-axis methods note expanded to three axes. |

## Type 3: Exploratory / External Hypotheses

| ID | Type | Claim | Current status | Evidence | Owner repo | Next test | Paper/dashboard target |
|---|---|---|---|---|---|---|---|
| DCS-JOIN | Type 3 | Dictionary-corpus frequency joins can improve reader difficulty and learning paths. | External: belongs to VisualDCS first; atlas may consume a compact dictionary-facing summary later. | [`RESEARCH_LAYER_ROADMAP.md`](RESEARCH_LAYER_ROADMAP.md) | `VisualDCS` | Define a compact SLP1-keyed output contract in VisualDCS. | Student learning paths; Reader Lookup extension. |
| FRAC-CORPUS | Type 3 | FrAC publication from corpus attestations can connect lexical records to corpus evidence. | External and blocked until real corpus evidence exists. | `csl-standards` `docs/FRAC_NOTE.md` | `csl-standards` | Wait for VisualDCS corpus evidence; do not invent FrAC claims from dictionary-only records. | Standards workbench; future RDF publication. |
| TEI-ONTOLEX-EXT | Type 3 | TEI/OntoLex loss reports can become a formal Sanskrit lexicographic extension proposal. | Standards workbench hypothesis, not atlas implementation. | `csl-standards` `docs/PAPER_OUTLINE.md` | `csl-standards` | Turn pilot loss reports into extension requirements. | Standards paper; TEI/OntoLex profile docs. |
| MW-ATTENTION | Type 3 | MW has received disproportionate digital-edition attention. | Boundary-sensitive: dictionary evidence lives in atlas; GitHub/org metrics stay in observatory. | [`METALEXICOGRAPHY_ROADMAP.md`](METALEXICOGRAPHY_ROADMAP.md) | `csl-atlas` | Define an atlas-owned dictionary-richness slice and link, not copy, observatory metrics. | Paper M data-richness section. |
| LEXEMEHUB-FUTURE | Type 3 | A LexemeHub-style integration layer may become useful later. | Future only; not an atlas roadmap item until a real cross-repo integration contract exists. | [`REVIEW_RELEASE_ROADMAP.md`](REVIEW_RELEASE_ROADMAP.md) | `csl-atlas` | Revisit only after dictionary, VisualDCS, and standards outputs expose stable contracts. | Future integration roadmap, not current release. |

## Maintenance Rules

- Every row must have exactly one owner repo.
- `csl-observatory` may own only GitHub/org-process hypotheses; content hypotheses must not be assigned there.
- Refuted hypotheses stay visible as Type 1 findings with replacement IDs, not as active open hypotheses.
- External hypotheses may be linked from the atlas, but their implementation must happen in their owner repository.
