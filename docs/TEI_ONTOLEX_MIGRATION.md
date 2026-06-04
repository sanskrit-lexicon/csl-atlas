# TEI/OntoLex Migration Note

Date: 2026-06-03

Status: moved to `csl-standards`.

## Decision

TEI, OntoLex, FrAC, SHACL, RDF, and related standards/export work does not
belong in `csl-atlas`.

Destination:

```text
C:\Users\user\Documents\GitHub\csl-standards
```

## Why It Moved

`csl-atlas` is the dictionary-evidence path. It should start from dictionaries,
headwords, entries, source citations, or dictionary comparisons.

The TEI/OntoLex pilot is different. It asks how CDSL records can be validated,
exported, modeled, and published through external standards. That is important,
but it is standards infrastructure, not dictionary exploration.

## Goals In The New Repo

- TEI: validation of CDSL markup and publication for other lexicographic
  projects.
- OntoLex: stress test for now, real RDF publication later.
- FrAC: frozen until VisualDCS or another corpus-evidence source is ready.

## Atlas Rule After Migration

`csl-atlas` keeps only this pointer. New standards work must happen in
`csl-standards`.

The active migration manifest is:

```text
C:\Users\user\Documents\GitHub\csl-standards\docs\MIGRATION_PLAN.md
```
