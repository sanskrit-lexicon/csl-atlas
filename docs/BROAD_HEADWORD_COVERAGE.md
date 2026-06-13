# Broad Headword Coverage

Broad headword coverage is a public lookup layer for Reader lookup and Lemma dossier. It expands visibility beyond the core comparison dictionaries without changing the deeper comparison model.

## Scopes

- `coreComparison`: MW, AP, PWG, PWK, WIL, VCP, SKD. This remains the source for gender conflicts, homonym splits, citation apparatus, sense depth, divergence, and the existing coverage/overlap pages.
- `broadHeadword`: eligible local Sanskrit/BHS headword dictionaries from `../csl-orig/v02`. This is used for broad Reader and Dossier lookup only.

## Inclusion Rules

A dictionary is eligible for broad headword coverage when:

- it appears in `src/data/lexicographic-structure/dictionary_inventory.csv`;
- its local `../csl-orig/v02/<code>/<code>.txt` file exists;
- `language_pair` starts with `Skt-`, or is exactly `BHS-Eng`.

`BHS-Eng` is included as a specialized Sanskrit-family source.

## Exclusions

Reverse English-Sanskrit dictionaries are excluded from Sanskrit-headword lookup because their lookup keys are English headwords. Current exclusions include AE, BOR, and MWE/ApteES.

## Link Modes

The broad manifest exposes `sourceLinkMode` per dictionary:

- `github`: public GitHub source links can be emitted.
- `local-only`: the local source exists, but the inventory does not mark it as GitHub-linkable, so the UI shows coverage without a broken external href.

## Evidence Limit

Broad mode reports headword presence, record count, and first source line where linkable. It does not imply reliable gender extraction, citation tagging, homonym markup, sense segmentation, semantic agreement, or editorial priority.

Full analytical parity for all dictionaries is a later phase and requires dictionary-specific parsing and validation.
