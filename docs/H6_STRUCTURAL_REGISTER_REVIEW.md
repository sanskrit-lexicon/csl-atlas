# H6 Structural-Register Review Packet

Date: 2026-06-05

Status: scholar-facing review packet with reviewed edge labels for the H6
structural-register artifact.

## Trust Block

- Evidence: `data/lexico/structural_register_h6_review.json`,
  `src/data/dicts/structural-register.json`,
  `data/dictionary-coverage.json`,
  `data/lexico/microstructure_fingerprint.json`,
  `src/data/lexicographic-structure/L0/bootstrap_support.csv`,
  `scripts/build-structural-register.mjs`, and
  `scripts/build-h6-structural-review.mjs`.
- Limitations: structural distance compares citation and grammar-register
  signals; it does not prove descent, copying, or semantic inheritance.
- Validation: `npm run build-structural-register`,
  `npm run build-h6-structural-review`,
  `python scripts/lexico/validate_lexico.py`, `npm test`, and
  `npm run build`.
- Owner repo: `csl-atlas`.
- Next use: use the 13 reviewed edge labels below for H6 interpretation, then
  review family outliers before presenting the full family-level claim.

## Purpose

H6 is already supported as a prototype: citation register plus grammar marking
separate several dictionary traditions. This packet turns the L0 edge-comparison
artifact into review work and records the first reviewed interpretation for all
13 edge-comparison rows. The review question is not "which dictionary descends
from which?" It is: when H6 agrees or disagrees with L0 known-edge evidence,
what kind of structural explanation is visible?

## What This Review Proves

| Review packet | Rows | What it proves | What it does not prove |
|---|---:|---|---|
| H6-R1 positive control | 1 | Whether a known close pair is also structurally close. | That all close points are genealogical. |
| H6-R2 genealogy-structure tensions | 4 | Whether strong L0 edges can be structurally far because of format, edition, or register change. | That L0 support is wrong. |
| H6-R3 structural convergences | 2 | Whether weak L0 edges can look close because of shared convention or genre. | That weak L0 edges are hidden descent. |
| H6-R4 intermediate review cases | 4 | Whether mixed support needs a separate explanation before paper use. | That the class can be resolved automatically. |
| H6-R5 family outliers | 5 families | Whether outlier dictionaries reveal narrow genre, detector blindness, or real structural distinctiveness. | That outliers are errors. |

## Edge Review Rows

Reviewed labels below are interpretive labels over the generated machine fields,
not edits to `data/lexico/structural_register_h6_review.json`. They explain how
to read H6 distance against L0 edge support.

| Class | Edge | Structural distance | L0 consensus | Reviewed label | Reviewed interpretation |
|---|---|---:|---:|---|---|
| positive-control | AP90 -> AP | 0.0861 | 0.581 | `positive-control-confirmed` | Same family and tagged citation mode, tiny citation delta, and only modest grammar delta confirm that H6 recognizes the close Apte edition pair. |
| genealogy-structure-tension | WIL -> SHS | 0.7056 | 0.806 | `grammar-policy-shift` | The edge is strongly supported by L0, but H6 distance is almost entirely grammar delta; SHS exposes root/prose conventions where WIL exposes grammar marking. |
| genealogy-structure-tension | PWG -> PW | 0.3924 | 0.806 | `citation-truncation` | Strong lineage support remains compatible with H6 distance because the citation delta is large while grammar delta is effectively zero. |
| genealogy-structure-tension | CCS -> CAE | 0.6663 | 0.683 | `grammar-policy-shift` | The same-author pair keeps low citation register but changes grammar marking sharply, so H6 reads the editorial policy shift rather than a content break. |
| genealogy-structure-tension | PWG -> SCH | 0.5675 | 0.676 | `detector-blindness` | Citation mode stays tagged and close, but grammar delta is high and SCH has no detected M1-M5 layer; treat this as simplified/detector-limited Petersburg structure. |
| structural-convergence | YAT -> SHS | 0.0009 | 0.045 | `structural-convergence` | Near-zero H6 distance with weak L0 support is low-register convergence, not hidden descent. |
| structural-convergence | PWG -> MW | 0.1177 | 0.013 | `structural-convergence` | MW and PWG are close in tagged citation/grammar register, but low L0 support keeps this as structural resemblance, not a lineage claim. |
| review | PW -> CCS | 0.6304 | 0.294 | `format-shift` | Mixed support plus large citation and grammar deltas mark an editorial-format shift; H6 should not decide inheritance without separate content evidence. |
| review | MW72 -> MW | 0.7615 | 0.310 | `format-shift` | The 1899 MW tagging layer changes both citation and grammar register, explaining why a known edition relation is structurally far in H6. |
| review | BOP -> MW | 0.7601 | 0.319 | `format-shift` | BOP is low-register/minimal while MW is highly tagged; H6 captures the later MW format rather than judging BOP content proximity. |
| review | BEN -> MW | 0.1359 | 0.236 | `structural-convergence` | Both are high tagged-register dictionaries with close H6 coordinates; the support level is too low for a descent claim. |
| expected-separation | WIL -> YAT | 0.7057 | 0.073 | `expected-separation-confirmed` | Weak L0 support and high grammar-policy distance agree; H6 separation is expected even inside the Wilson-line neighborhood. |
| expected-separation | PWG -> MW72 | 0.8739 | 0.018 | `expected-separation-confirmed` | The pre-1899 MW layer lacks the later tagged register and is far from PWG on both citation and grammar axes. |

## Family Outlier Checks

Use `familyProfiles[*].outliers` from the artifact:

| Family | First checks | Review question |
|---|---|---|
| western-tagged | SCH, PWG, BEN | Are outliers caused by citation density, grammar marking, or a missing M1-M5 layer? |
| indigenous-prose | VCP, SKD, KRM | Are prose/iti citation and root layers being counted correctly? |
| reverse-bilingual | AE, MWE | Is lookup direction creating a structural split inside the family? |
| specialized | BHS, PGN, PE | Does narrow scope or small source size explain the outlier? |
| index-catalogue | MCI, ACC, PUI | Is the index/catalogue warning sufficient, or does the family need subtypes? |

## Decision Labels

Use these labels in notes or future review reports:

| Label | Meaning |
|---|---|
| `format-shift` | Strong lineage/content evidence, but structural form changed. |
| `citation-truncation` | Citation density/register explains most of the distance. |
| `grammar-policy-shift` | Grammar marking explains most of the distance. |
| `structural-convergence` | Weak lineage edge looks close due to shared convention or genre. |
| `positive-control-confirmed` | Known close edge is structurally close. |
| `detector-blindness` | Missing M1-M5 layer or convention gap likely distorts the position. |
| `genre-outlier` | Narrow or index genre explains the position. |
| `needs-source-read` | The chart cannot explain the edge without direct chapter/source reading. |
| `expected-separation-confirmed` | Weak L0 support and large structural distance point in the same direction. |

## Review Columns

If H6 becomes a generated review report, keep the canonical review-report schema
and status vocabulary unchanged. Suggested machine fields:

| Field | Meaning |
|---|---|
| `reviewId` | Stable ID such as `h6-edge:pwg:mw:structural-convergence`. |
| `sampleType` | `edge-comparison` or `family-outlier`. |
| `parent` / `child` | Edge endpoints for L0 comparison rows. |
| `dict` | Dictionary code for family outlier rows. |
| `reviewClass` | Existing artifact class. |
| `structuralDistance01` | H6 distance on the normalized chart space. |
| `consensusSupport` | L0 edge support when available. |
| `citationDeltaPct` | Citation-register difference. |
| `grammarDeltaPct` | Grammar-marking difference. |
| `reviewStatus` | Canonical status, initially `needs-review`. |
| `reviewedValue` | Human label such as `format-shift` or `citation-truncation`. |
| `note` | Short explanation with source/chapter references. |

## Boundary Rules

- H6 is dictionary structure only; no corpus, DCS, standards, or GitHub evidence.
- Do not read structural closeness as descent without a separate lineage test.
- Do not read structural distance as non-inheritance without checking format
  change, edition policy, and detector blindness.
- Keep H6 separate from H4: H6 is register/microstructure; H4 is semantic-field
  headword coverage.

## Acceptance

H6 edge comparisons now have reviewed interpretation labels. H6 can move from
edge-reviewed to full reviewed interpretation when the family outliers also have
labels explaining whether the chart shows lineage corroboration, format shift,
convergence, genre outliers, or detector limitation.
