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

| ID | Finding | Strength | Why it matters |
|---|---|---|---|
| MF-1 | MW and the Petersburg dictionaries differ by macro/micro trade-off. | supported | MW promotes many forms to headwords; Petersburg dictionaries nest more inside entries. |
| MF-2 | A zero can mean detector blindness rather than absence. | supported | SKD/VCP score zero under European markup detectors while carrying rich indigenous verbal structure. |
| MF-3 | Indigenous verbal-root evidence is recoverable. | supported prototype | M4 recovers SKD/VCP/KRM/YAT/SHS root layers by using their own grammatical conventions. |
| MF-4 | Cross-reference edges form a lineage-ready graph signal. | supported prototype | PWG `Vgl.`, MW `cf.`, and Apte-family `cf.{#...#}` produce comparable Sanskrit target edges. |
| MF-5 | Structural register can predict dictionary family. | supported/prototype-backed | Citation style plus grammar-marking separates Western-tagged, indigenous, and index traditions. |
| MF-6 | Content, convention, and microstructure inheritance are separate axes. | strong testable | CAE/CCS and MW/PWG show that headword convention and entry structure can diverge. |
| MF-7 | Amarakosa-native semantic-field bias is measurable. | supported prototype | M8 maps AMAR vargas to dictionary headword coverage without using corpus frequency. |

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
| R2 rebuild | [`R2_REBUILD_CONTRACT.md`](R2_REBUILD_CONTRACT.md) | Restore reproducible generator outputs before broadening H1R/H2/H3R. |
| H6 structural register | [`H6_STRUCTURAL_REGISTER_SCATTER.md`](H6_STRUCTURAL_REGISTER_SCATTER.md) | Review the positive control, genealogy-structure tensions, and structural-convergence prompts in `data/lexico/structural_register_h6_review.json`. |
| H4 interpretation | [`H4_SEMANTIC_FIELD_INTERPRETATION.md`](H4_SEMANTIC_FIELD_INTERPRETATION.md) | Use `data/lexico/semantic_field_family_profiles.json` to review SKD false lows, AP/AP90 deltas, VCP high coverage, and specialized baselines. |
| Xref hubs | [`MICROSTRUCTURE_XREF_HUB_REVIEW.md`](MICROSTRUCTURE_XREF_HUB_REVIEW.md) | Use `data/lexico/xref_hub_review.json` to label shared-core, prefix-convention, and edition-continuity samples. |
| H5 anomaly review | [`H5_GHOST_ANOMALY_SCOPE.md`](H5_GHOST_ANOMALY_SCOPE.md) | Review the 130-item proof-first queue and write the anomaly taxonomy. |

## What The Review Queues Prove

Before writing review procedure, each queue should state its proof value:

| Queue | What it proves |
|---|---|
| SKD/YAT/SHS root-format checks | Whether dictionary-specific verbal-root coding can be decoded reliably enough to emit grammatical columns without forcing all dictionaries into one convention. |
| Xref target overlap | Whether cross-reference graphs preserve lineage beyond headword overlap; see [`MICROSTRUCTURE_XREF_HUB_REVIEW.md`](MICROSTRUCTURE_XREF_HUB_REVIEW.md) and `data/lexico/xref_hub_review.json`. |
| Source-siglum aliases | Whether source citation normalization can improve dictionary evidence without hiding uncertainty. |
| POS/gender conflicts | Which disagreements are dictionary disagreement, parser error, or convention mismatch. |
| H5 anomaly review | Whether rare near-core and raw-headword forensic signals are lineage evidence, correction targets, parser artifacts, or legitimate morphology. |

## H4 Semantic Fields

H4 is now built as M8. Its field scheme is Amarakosa-native and
dictionary-first; corpus fields belong outside the atlas unless a compact
external contract exists. The family-profile artifact is
`data/lexico/semantic_field_family_profiles.json`, and the interpretation
package is
[`H4_SEMANTIC_FIELD_INTERPRETATION.md`](H4_SEMANTIC_FIELD_INTERPRETATION.md).
