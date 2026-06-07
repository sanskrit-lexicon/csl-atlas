# Microstructure Findings

Date: 2026-06-04

Audience: scholars. This page states what the current microstructure layer
already supports, what it refutes, and what it prepares for later analysis.

## Trust Block

- Evidence: `MICROSTRUCTURE_M1_M2_RESULTS.md`,
  `MICROSTRUCTURE_ZERO_MEANING.md`, `microstructure_profile.csv`,
  `microstructure_fingerprint.json`, and the M1-M8 scripts.
- Limitations: results are recoverable-structure findings, not exhaustive
  claims about all semantic or grammatical content.
- Validation: `python scripts/lexico/validate_lexico.py`.
- Owner repo: `csl-atlas`.

## Findings

The first reading layer is headword/subentry structure:
[`MICROSTRUCTURE_HEADWORD_SUBENTRY.md`](MICROSTRUCTURE_HEADWORD_SUBENTRY.md).
It explains the MW vs Petersburg macro/micro trade-off before the reader moves
to
[`MICROSTRUCTURE_SENSE_SEGMENTATION.md`](MICROSTRUCTURE_SENSE_SEGMENTATION.md),
citation practice, grammar/gender marking, and cross-references.

| ID | Finding | Strength | Why it matters |
|---|---|---|---|
| MF-1 | MW and the Petersburg dictionaries differ by macro/micro trade-off. | supported | MW promotes many forms to headwords; Petersburg dictionaries nest more inside entries. |
| MF-2 | A zero can mean detector blindness rather than absence. | supported | SKD/VCP score zero under European markup detectors while carrying rich indigenous verbal structure. |
| MF-3 | Indigenous verbal-root evidence is recoverable. | supported prototype | M4 recovers SKD/VCP/KRM/YAT/SHS root layers by using their own grammatical conventions. |
| MF-4 | Cross-reference edges form a lineage-ready graph signal. | supported prototype | PWG `Vgl.`, MW `cf.`, and Apte-family `cf.{#...#}` produce comparable Sanskrit target edges. |
| MF-5 | Structural register can predict dictionary family. | supported/prototype-backed | Citation style plus grammar-marking separates Western-tagged, indigenous, and index traditions. |
| MF-6 | Content, convention, and microstructure inheritance are separate axes. | machine comparison packet | [`THREE_AXIS_COMPARISON.md`](THREE_AXIS_COMPARISON.md) keeps content containment, convention similarity, and microstructure/register similarity separate for the 13 L0 known edges, including CAE/CCS and MW/PWG focus rows. |
| MF-7 | Amarakosa-native semantic-field bias is measurable. | supported prototype plus review packet | M8 maps AMAR vargas to dictionary headword coverage without using corpus frequency, and the generated H4 review packet selects 105 rows for source review before paper-level claims. |
| MF-8 | Sense segmentation is reliable only where the division convention is explicit or reviewed. | supported documentation layer | AP/PWG/PWK expose countable structural divisions; MW/WIL/VCP/SKD require prose-aware R2 review before raw sense-count comparison. |

## Next Analysis Priority

Use the implemented H6 structural-register scatter and H4 semantic-field page
as the first chart-trust examples. Both remain prototype-backed, but both now
have generated JSON inputs and public atlas pages. H6 and H4 also have generated
review-prompt artifacts that turn the next questions into scholar review rather
than data assembly.

The SKD anubandha key, cross-reference graph overlap, root-agreement, and H4
semantic-field packages are now implemented as data/docs/chart layers where
applicable. The remaining scholar-facing packages are now explicit:

| Package | Doc | Next proof step |
|---|---|---|
| R2 rebuild | [`R2_REBUILD_CONTRACT.md`](R2_REBUILD_CONTRACT.md), [`R2_PARSER_DIAGNOSTICS.md`](R2_PARSER_DIAGNOSTICS.md), [`R2_REVIEW_PACKETS.md`](R2_REVIEW_PACKETS.md) | Use the packet order to tighten PWG/PWK `div` scope, numbered-marker runs, AE reverse rank bands, SKD/VCP `iti` labels, and source-gap controls before broadening H1R/H2/H3R. |
| Sense segmentation | [`MICROSTRUCTURE_SENSE_SEGMENTATION.md`](MICROSTRUCTURE_SENSE_SEGMENTATION.md) | Use the AP/PWG/PWK sense-depth chart as a structural proxy, then use R2 diagnostics before citing broad sense-alignment claims. |
| H6 structural register | [`H6_STRUCTURAL_REGISTER_SCATTER.md`](H6_STRUCTURAL_REGISTER_SCATTER.md), [`H6_STRUCTURAL_REGISTER_REVIEW.md`](H6_STRUCTURAL_REGISTER_REVIEW.md) | Edge and family-outlier labels are documented; source-read selected examples before paper use. |
| H4 interpretation | [`H4_SEMANTIC_FIELD_INTERPRETATION.md`](H4_SEMANTIC_FIELD_INTERPRETATION.md), [`H4_SEMANTIC_FIELD_REVIEW.md`](H4_SEMANTIC_FIELD_REVIEW.md), [`H4_SEMANTIC_FIELD_REVIEW_SAMPLES.md`](H4_SEMANTIC_FIELD_REVIEW_SAMPLES.md) | Use the generated 105-row H4 worksheet to adjudicate SKD false lows, VCP high coverage, AP/AP90 deltas, specialized baselines, and index/reverse controls. |
| Xref hubs | [`MICROSTRUCTURE_XREF_HUB_REVIEW.md`](MICROSTRUCTURE_XREF_HUB_REVIEW.md), [`MICROSTRUCTURE_XREF_SOURCE_CHECK.md`](MICROSTRUCTURE_XREF_SOURCE_CHECK.md) | Source-check packet exists for 40 MW/PWG shared-core rows and 10 PWG/MW prefix controls; next proof step is human adjudication before paper use. |
| Three-axis comparison | [`THREE_AXIS_COMPARISON.md`](THREE_AXIS_COMPARISON.md) | Source-read the MW/PWG, CCS/CAE, WIL/SHS, and PWG/SCH focus rows before turning the machine packet into a methods-note claim. |
| H5 anomaly review | [`H5_GHOST_ANOMALY_SCOPE.md`](H5_GHOST_ANOMALY_SCOPE.md), [`H5_MAKER_QA_CANDIDATES.md`](H5_MAKER_QA_CANDIDATES.md), [`H5_MAKER_CORRECTION_PROPOSAL.md`](H5_MAKER_CORRECTION_PROPOSAL.md) | The 130-item first sample is classified, the 10-row maker-QA worksheet is source-checked, and the single source-declared correction candidate is now isolated as a maker-facing `divaraTa -> diviraTa` proposal. |

## What The Review Queues Prove

Before writing review procedure, each queue should state its proof value:

| Queue | What it proves |
|---|---|
| SKD/YAT/SHS root-format checks | Whether dictionary-specific verbal-root coding can be decoded reliably enough to emit grammatical columns without forcing all dictionaries into one convention. |
| Xref target overlap | Whether cross-reference graphs preserve lineage beyond headword overlap; see [`MICROSTRUCTURE_XREF_HUB_REVIEW.md`](MICROSTRUCTURE_XREF_HUB_REVIEW.md), [`MICROSTRUCTURE_XREF_SOURCE_CHECK.md`](MICROSTRUCTURE_XREF_SOURCE_CHECK.md), `data/lexico/xref_hub_review.json`, and `data/lexico/xref_source_check_packet.json`. |
| Source-siglum aliases | Whether source citation normalization can improve dictionary evidence without hiding uncertainty. |
| POS/gender conflicts | Which disagreements are dictionary disagreement, parser error, or convention mismatch. |
| H5 anomaly review | Whether rare near-core and raw-headword forensic signals are lineage evidence, correction targets, parser artifacts, or legitimate morphology. |

## H4 Semantic Fields

H4 is now built as M8. Its field scheme is Amarakosa-native and
dictionary-first; corpus fields belong outside the atlas unless a compact
external contract exists. The family-profile artifact is
`data/lexico/semantic_field_family_profiles.json`; the generated review packet
is `data/lexico/h4_semantic_field_review_packet.json`; and the interpretation
package is
[`H4_SEMANTIC_FIELD_INTERPRETATION.md`](H4_SEMANTIC_FIELD_INTERPRETATION.md).
