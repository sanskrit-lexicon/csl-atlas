# Cross-Reference Hub Review

Date: 2026-06-05

Status: scholar-facing review note for the M6 xref lineage package and
`/tools/xref-lineage`.

## Trust Block

- Evidence: `data/lexico/xref_edges.csv`, `data/lexico/xref_by_dict.json`,
  `data/lexico/xref_lineage.json`, `data/lexico/xref_shared_edges.csv`,
  `src/data/dicts/xref-lineage.json`, `scripts/lexico/m3_xrefs.py`,
  `scripts/lexico/m6_xref_lineage.py`, and
  `scripts/build-xref-lineage.mjs`.
- Limitations: normalized source-target overlap is a floor; raw target strings
  are messy, and shared xrefs are lineage signals rather than proof of direct
  copying by themselves.
- Validation: `python scripts/lexico/validate_lexico.py`,
  `npm run build-xref-lineage`, and `npm run build`.
- Owner repo: `csl-atlas`.

## Current Reading

M6 already supports the cautious finding: cross-reference graphs preserve a
shared core but do not prove wholesale descent. The strongest positive control
is AP/AP90: 182 overlapping edges on 211 shared source lemmas, with about 85%
matched edges on both sides. MW/PWG is different: 641 overlapping edges on
2,538 shared source lemmas, with a 21.8% MW-side and 9.1% PWG-side rate.

That means MW/PWG has a real shared core, but each tradition also expands its
xref graph independently.

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
| MW/PWG shared core | 40 edges | `data/lexico/xref_shared_edges.csv` | Classify true shared lexical xrefs vs normalization artifacts. |
| MW prefix hubs | 20 targets | `data/lexico/xref_by_dict.json` | Separate prefix/convention hubs from content inheritance. |
| PWG `Vgl.` hubs | 20 targets | `data/lexico/xref_by_dict.json` | Identify whether PWG hub behavior is mostly compound-marker style. |
| AP/AP90 control | 20 edges | `src/data/dicts/xref-lineage.json` | Confirm the positive-control interpretation. |

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

The next concrete analysis package is a hub-family table: top targets by
dictionary, grouped as prefix/convention hubs vs lexical targets, with the
MW/PWG shared-core sample annotated by the review labels above.
