# Cross-Reference Hub Review

Date: 2026-06-05

Status: scholar-facing review note for the M6 xref lineage package and
`/tools/xref-lineage`.

## Trust Block

- Evidence: `data/lexico/xref_edges.csv`, `data/lexico/xref_by_dict.json`,
  `data/lexico/xref_lineage.json`, `data/lexico/xref_shared_edges.csv`,
  `data/lexico/xref_hub_review.json`,
  `data/lexico/xref_source_check_packet.json`,
  `src/data/dicts/xref-lineage.json`, `scripts/lexico/m3_xrefs.py`,
  `scripts/lexico/m6_xref_lineage.py`, and
  `scripts/build-xref-lineage.mjs`, `scripts/build-xref-hub-review.mjs`,
  `scripts/build-xref-source-check-packet.mjs`.
- Limitations: normalized source-target overlap is a floor; raw target strings
  are messy, and shared xrefs are lineage signals rather than proof of direct
  copying by themselves.
- Validation: `python scripts/lexico/validate_lexico.py`,
  `npm run build-xref-lineage`, `npm run build-xref-hub-review`,
  `npm run build-xref-source-check-packet`, and `npm run build`.
- Owner repo: `csl-atlas`.
- Next use: use `MICROSTRUCTURE_XREF_SOURCE_CHECK.md` as the active xref
  source-check packet before making paper-level lineage claims.

## Current Reading

M6 already supports the cautious finding: cross-reference graphs preserve a
shared core but do not prove wholesale descent. The strongest positive control
is AP/AP90: 182 overlapping edges on 211 shared source lemmas, with about 85%
matched edges on both sides. MW/PWG is different: 641 overlapping edges on
2,538 shared source lemmas, with a 21.8% MW-side and 9.1% PWG-side rate.

That means MW/PWG has a real shared core, but each tradition also expands its
xref graph independently.

`data/lexico/xref_hub_review.json` turns the review labels into a deterministic
artifact: 6 dictionary hub profiles, 10 pair review rows, and a 40-edge MW/PWG
shared-core sample. `data/lexico/xref_source_check_packet.json` now adds the
source-check layer: the same 40 shared-core rows plus 10 PWG/MW prefix-control
rows, with source pointers and empty human fields. In the current top-target
lists, MW and PWG are dominated by prefix/convention hubs, while AP/AP90/CAE
top targets are lexical-target hubs. AE is kept as a normalization-risk
control.

The artifact now carries the review starting labels. These are not completed
source readings; they say what kind of evidence each row is allowed to become
after source checking.

## Hub Families To Review

| Hub family | Evidence | Review question |
|---|---|---|
| Edition-continuity hubs | AP/AP90 high overlap. | Which targets remain stable across edition revision? |
| Prefix/compound hubs | MW top targets include `a-`, `A-`, `aBi-`, `vi-`, `pra-`; PWG top targets include related compound-marker hubs. | Are these structural convention hubs or meaningful lineage links? |
| Lexical shared-core hubs | MW/PWG shared edges include 641 normalized source-target pairs. | Which shared edges are philologically meaningful rather than normalizing artifacts? |
| Sparse-pair hubs | AP/CAE and AP90/CAE have one or two shared sources. | Keep these visible but do not interpret them as lineage evidence. |

## Review Samples

| Sample | Size | Source | Purpose |
|---|---:|---|---|
| MW/PWG shared core | 40 edges | `data/lexico/xref_source_check_packet.json` | Classify true shared lexical xrefs vs normalization artifacts. |
| MW prefix hubs | 5 controls | `data/lexico/xref_source_check_packet.json` | Separate prefix/convention hubs from content inheritance. |
| PWG `Vgl.` hubs | 5 controls | `data/lexico/xref_source_check_packet.json` | Identify whether PWG hub behavior is mostly compound-marker style. |
| AP/AP90 control | pair row | `data/lexico/xref_hub_review.json` | Confirm the positive-control interpretation. |

## Artifact-Carried Labels

| Evidence slice | Artifact signal | Starting label | Use |
|---|---|---|---|
| PWG top targets | 20/20 top targets are compound or prefix-style hubs (`a˚`, `mahA˚`, `su˚`, `vi˚`, etc.). | `prefix-convention` | Treat PWG hubs as structural convention until a source sample proves rare lexical inheritance. |
| MW top targets | 20/20 top targets are prefix-style hubs (`a-`, `a/-`, `A-`, `aBi-`, `pra-`, `vi-`, etc.). | `prefix-convention` | Keep MW/PWG hub overlap separate from the 40-edge lexical shared-core sample. |
| AP/AP90/CAE top targets | Top targets are lexical targets rather than prefix hubs. | `lexical-target` | Use these as a different xref style, not as evidence that AP-style graphs behave like PWG/MW. |
| AE top targets | Only 2 xref edges, both proverb-like strings. | `normalization-risk` | Keep AE as a control for target extraction risk. |
| AP/AP90 pair | 211 shared sources, 182 overlapping edges, about 85% match on both sides. | `edition-continuity` | Positive-control ceiling for what same-family xref inheritance looks like. |
| MW/PWG pair | 2,538 shared sources, 641 overlapping edges, 21.8% MW-side and 9.1% PWG-side match. | `lexical-shared-core` | Real shared core, not wholesale xref inheritance. |
| AP/CAE and AP90/CAE pairs | 1 or 2 shared source lemmas. | `too-sparse` | Keep visible, but do not use for lineage interpretation. |
| Other AP/MW/PWG/CAE pairs | Modest overlap with normalization and convention exposure. | `normalization-risk` | Review only as controls unless a rare shared target is source-confirmed. |

## Review Labels

Use these labels in notes or a future review queue:

| Label | Meaning |
|---|---|
| `lexical-shared-core` | Same source lemma points to the same meaningful Sanskrit target. |
| `prefix-convention` | Shared target is mainly a prefix/compound-reference convention. |
| `edition-continuity` | Stable edge across editions of the same dictionary family. |
| `normalization-risk` | Edge may be created or lost by target normalization. |
| `too-sparse` | Pair has too few shared sources for lineage interpretation. |

## What Not To Claim Yet

- Do not claim MW copied PWG xrefs wholesale.
- Do not use sparse pair rows as evidence of lineage.
- Do not mix xref hubs with corpus co-occurrence or DCS passage evidence.
- Do not treat a prefix hub as the same kind of evidence as a rare lexical
  shared target.

## Next Test

Use `MICROSTRUCTURE_XREF_SOURCE_CHECK.md` and
`data/lexico/xref_source_check_packet.json` for scholar review. Start with the
MW/PWG 40-edge shared-core sample, then adjudicate the 10 PWG/MW prefix
controls. The package can move from machine labels to reviewed interpretation
only after those source checks confirm which edges are lexical and which are
convention artifacts.
