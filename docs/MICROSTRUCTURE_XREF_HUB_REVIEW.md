# Cross-Reference Hub Review

Date: 2026-06-05

Status: scholar-facing review note for the M6 xref lineage package and
`/tools/xref-lineage`.

## Trust Block

- Evidence: `data/lexico/xref_edges.csv`, `data/lexico/xref_by_dict.json`,
  `data/lexico/xref_lineage.json`, `data/lexico/xref_shared_edges.csv`,
  `data/lexico/xref_hub_review.json`,
  `src/data/dicts/xref-lineage.json`, `scripts/lexico/m3_xrefs.py`,
  `scripts/lexico/m6_xref_lineage.py`, and
  `scripts/build-xref-lineage.mjs`, `scripts/build-xref-hub-review.mjs`.
- Limitations: normalized source-target overlap is a floor; raw target strings
  are messy, and shared xrefs are lineage signals rather than proof of direct
  copying by themselves.
- Validation: `python scripts/lexico/validate_lexico.py`,
  `npm run build-xref-lineage`, `npm run build-xref-hub-review`, and
  `npm run build`.
- Owner repo: `csl-atlas`.

## Current Reading

M6 already supports the cautious finding: cross-reference graphs preserve a
shared core but do not prove wholesale descent. The strongest positive control
is AP/AP90: 182 overlapping edges on 211 shared source lemmas, with about 85%
matched edges on both sides. MW/PWG is different: 641 overlapping edges on
2,538 shared source lemmas, with a 21.8% MW-side and 9.1% PWG-side rate.

That means MW/PWG has a real shared core, but each tradition also expands its
xref graph independently.

`data/lexico/xref_hub_review.json` now turns the next review step into a
deterministic artifact: 6 dictionary hub profiles, 10 pair review rows, and a
40-edge MW/PWG shared-core sample. In the current top-target lists, MW and PWG
are dominated by prefix/convention hubs, while AP/AP90/CAE top targets are
lexical-target hubs. AE is kept as a normalization-risk control.

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
| MW/PWG shared core | 40 edges | `data/lexico/xref_hub_review.json` | Classify true shared lexical xrefs vs normalization artifacts. |
| MW prefix hubs | top targets | `data/lexico/xref_hub_review.json` | Separate prefix/convention hubs from content inheritance. |
| PWG `Vgl.` hubs | top targets | `data/lexico/xref_hub_review.json` | Identify whether PWG hub behavior is mostly compound-marker style. |
| AP/AP90 control | pair row | `data/lexico/xref_hub_review.json` | Confirm the positive-control interpretation. |

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

Use `data/lexico/xref_hub_review.json` for scholar review. The next human step
is to confirm whether the MW/PWG shared-core sample is truly lexical, and
whether the MW/PWG top hubs are convention hubs rather than content inheritance.
