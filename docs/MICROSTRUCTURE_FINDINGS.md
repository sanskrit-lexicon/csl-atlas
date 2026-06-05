# Microstructure Findings

Date: 2026-06-04

Audience: scholars. This page states what the current microstructure layer
already supports, what it refutes, and what it prepares for later analysis.

## Trust Block

- Evidence: `MICROSTRUCTURE_M1_M2_RESULTS.md`,
  `MICROSTRUCTURE_ZERO_MEANING.md`, `microstructure_profile.csv`,
  `microstructure_fingerprint.json`, and the M1-M6 scripts.
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

## Next Analysis Priority

Use the implemented H6 structural-register scatter as the first chart built
under the chart trust template. It remains prototype-backed, but it now has a
generated JSON input and public atlas page.

The SKD anubandha key and cross-reference graph overlap packages are now
implemented. The next scholar-facing analysis package is therefore **H4:
Amarakosa-native semantic fields**, after one pass over current M4/YAT/SHS caveats.

## What The Review Queues Prove

Before writing review procedure, each queue should state its proof value:

| Queue | What it proves |
|---|---|
| SKD/YAT/SHS root-format checks | Whether dictionary-specific verbal-root coding can be decoded reliably enough to emit grammatical columns without forcing all dictionaries into one convention. |
| Xref target overlap | Whether cross-reference graphs preserve lineage beyond headword overlap. |
| Source-siglum aliases | Whether source citation normalization can improve dictionary evidence without hiding uncertainty. |
| POS/gender conflicts | Which disagreements are dictionary disagreement, parser error, or convention mismatch. |

## Later: H4 Semantic Fields

H4 is the next strong testable package. Its field scheme should remain
Amarakosa-native and dictionary-first; corpus fields belong outside the atlas
unless a compact external contract exists.
