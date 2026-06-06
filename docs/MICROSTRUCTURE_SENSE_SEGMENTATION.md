# Microstructure Sense Segmentation

Date: 2026-06-06

Audience: scholars who need to know when dictionary "sense counts" are
trustworthy, when they are only structural proxies, and when the R2 rebuild
must intervene before a claim is broadened.

## Trust Block

- Evidence: `src/data/dicts/sense-depth.json`,
  `scripts/build-sense-depth.mjs`, `data/lexico/r2_parser_diagnostics.json`,
  `data/lexico/r2_review_packets.json`, `R2_FINDINGS.md`,
  `R2_REBUILD_CONTRACT.md`, `R2_PARSER_DIAGNOSTICS.md`, and
  `R2_REVIEW_PACKETS.md`.
- Limitations: sense segmentation here means recoverable dictionary structure,
  not a curated semantic inventory. A low structural count can mean prose
  lumping, edition policy, parser scope, or detector blindness.
- Validation: `npm run build-sense-depth`, `npm run build-r2-source-anchors`,
  `npm run build-r2-parser-diagnostics`,
  `npm run build-r2-review-packets`, `npm test`, and `npm run build`.
- Owner repo: `csl-atlas`.
- Next use: use this page before citing sense-depth charts, R2 H1/H2/H3
  findings, or cross-dictionary sense disagreement.

## Why Sense Segmentation Comes Second

Headword/subentry structure asks whether material is promoted to a headword or
nested inside another entry. Sense segmentation is harder: it asks whether a
visible division is a meaning division, a sub-sense, a derived form, a preverb
block, a citation cluster, or just prose punctuation.

The safe reading order is therefore:

1. Identify headword/subentry layout.
2. Ask which sense divisions are explicitly marked.
3. Separate structural divisions from semantic claims.
4. Use R2 diagnostics before broadening sense-alignment hypotheses.

## Three Evidence Zones

| Zone | Dictionaries / artifacts | What can be said | What must not be said |
|---|---|---|---|
| Explicit structural proxy | AP, PWG, PWK in `sense-depth.json` | These dictionaries expose countable sense-division markers. | That the counts are curated meanings or directly comparable across all dictionaries. |
| Source-backed R2 rebuild | `r2_source_anchor_*`, parser diagnostics, review packets | The rebuild has local source rows and parser-work labels for five anchor lemmas across 14 dictionaries. | That the final broad R2 sense corpus is restored. |
| Prose or convention-limited | MW, WIL, VCP, SKD, and other prose-heavy dictionaries | Low or absent structural markers are convention evidence. | That the dictionary is sense-poor. |

## Current Sense-Depth Chart

`src/data/dicts/sense-depth.json` is deliberately narrow. It compares only AP,
PWG, and PWK because those dictionaries expose structural markers that can be
counted deterministically:

| Dictionary | Marker family | Mean divisions / entry | Multi-division entries |
|---|---|---:|---:|
| AP | bullet-style divisions | 1.738 | 28.1% |
| PWG | `<div>` divisions | 1.660 | 17.0% |
| PWK | `<div>` divisions | 1.619 | 14.9% |

The chart reports 10,375 cross-dictionary disparities and 84,897 ties among
lemmas present in at least two countable dictionaries. PWK is deepest for 12,689
lemmas, AP for 4,374, and PWG for 3,108.

Read those numbers as **division richness**, not semantic truth. The largest
gaps are mostly large verbal roots such as `sTA`, `i`, `DA`, and `gam`, where
Petersburg-style `<div>` structure can be much finer than AP bullet divisions.

## Why MW, WIL, VCP, And SKD Are Excluded

MW often separates meanings in prose rather than with frequent structural
`<div>` markers. Counting only explicit divisions would falsely make MW look
sense-poor. WIL, VCP, and SKD are also prose- or convention-heavy: they can
carry real meaning structure, citation structure, or indigenous grammatical
structure without exposing the same marker counted by AP/PWG/PWK.

This is the same zero-reading rule used elsewhere in the microstructure docs:

```text
absence of the counted marker != absence of the phenomenon
```

## R2 Rebuild Gate

R2 is the route from structural division proxies to cross-dictionary sense
alignment. The current branch preserves archived R2 findings and a source-backed
anchor rebuild, but not the final broad generator package.

Current parser diagnostics cover 70 rows: 5 anchor lemmas across 14 dictionaries.
They classify drift before any row count becomes a new sense claim.

| Work package | Why it matters for sense segmentation |
|---|---|
| PWG/PWK `<div>` scope | Decide which source records and labels are the target sense series versus derivative, prefixed, or separately keyed material. |
| Numbered-marker run scope | BEN, AP90, BHS, WIL, and AP-style markers can reset; prefix matches identify main runs without discarding later material. |
| AE reverse filtering | English-to-Sanskrit equivalents need rank-band review before they can support alignment. |
| Indigenous `iti` review | SKD/VCP authority quotations are useful but too coarse to treat as sense boundaries without review. |
| Source-record scope | Same-headword records may include separate keyed blocks; record-level evidence must be reviewed before aggregation. |

## What This Means For H1R, H2, And H3R

- H1R remains a negative finding for pure time inflation, but broadening it
  requires the R2 rebuild gate.
- H2 remains supported in the archived R2 slice: citation-supported ancestor
  senses survive better than uncited senses.
- H3R remains a negative finding for systematic net-addition, but more edges
  should wait until parser drift is resolved.

Do not cite the AP/PWG/PWK sense-depth chart as proof for H1R/H2/H3R by itself.
Use it as structural evidence and use R2 for sense-alignment claims.

## Review Questions

| Question | Evidence to inspect | Decision label |
|---|---|---|
| Is an explicit division a meaning sense or a structural subunit? | AP/PWG/PWK source links and marker labels. | `semantic-sense`, `sub-sense`, `derived-form`, `preverb-block`, `citation-cluster` |
| Does a low count reflect prose lumping? | MW/WIL/VCP/SKD source record and R2 diagnostics. | `prose-lumping`, `detector-blindness` |
| Is a marker run safe as the main sense series? | `markerRunIndex`, prefix matches, source-record clues. | `main-run`, `later-run`, `needs-source-read` |
| Can an indigenous `iti` span be split? | authority hints and direct source text. | `authority-boundary`, `coarse-prose`, `blocked` |

## Acceptance

This layer is complete enough for scholar-facing documentation when a reader can
tell:

- which sense counts are structural and currently reliable;
- why MW/WIL/VCP/SKD are excluded from raw structural comparison;
- which R2 rebuild work packages must be resolved before broader sense claims;
- why sense-depth charts and R2 sense-alignment claims are related but not
  interchangeable.

## Related

- [`MICROSTRUCTURE_HEADWORD_SUBENTRY.md`](MICROSTRUCTURE_HEADWORD_SUBENTRY.md)
- [`MICROSTRUCTURE_PROFILE.md`](MICROSTRUCTURE_PROFILE.md)
- [`MICROSTRUCTURE_METHODS.md`](MICROSTRUCTURE_METHODS.md)
- [`MICROSTRUCTURE_FINDINGS.md`](MICROSTRUCTURE_FINDINGS.md)
- [`R2_REBUILD_CONTRACT.md`](R2_REBUILD_CONTRACT.md)
- [`R2_PARSER_DIAGNOSTICS.md`](R2_PARSER_DIAGNOSTICS.md)
- [`R2_REVIEW_PACKETS.md`](R2_REVIEW_PACKETS.md)
- [`R2_FINDINGS.md`](R2_FINDINGS.md)
