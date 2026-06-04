# CSL Atlas Session Handoff

Date: 2026-06-04

Read this first when resuming `csl-atlas`.

`csl-atlas` is now the dictionary-evidence path only. The former mixed
observatory handoff is preserved as
`docs/SESSION_HANDOFF_LEGACY_OBSERVATORY.md`.

## Start Here

1. Read `docs/BOUNDARY_RULES.md`.
2. Read `docs/REVIEW_RELEASE_ROADMAP.md`.
3. Read `docs/RELEASE_CHECKLIST.md`.
4. For implementation shape, read `ARCHITECTURE.md`.

## Current Active Work

- Public atlas readiness and release hygiene.
- Reader Lookup v1 over generated dictionary comparison data.
- Light review sprint:
  - 7 low-confidence alignments;
  - top source-layer and source-siglum review samples;
  - representative gender-conflict sample.
- Dictionary-structure pages now hosted here:
  - `src/tools/lexicography.md`;
  - `src/tools/lexicographic-conventions.md`;
  - `src/tools/r2-explorer.md`;
  - `src/tools/r2-h1.md`.

## What Belongs Here

- dictionary chapters;
- reader lookup and dictionary guidance;
- per-entry and per-lemma dictionary dossiers;
- dictionary coverage, overlap, homonym, POS/gender, sense, citation, and
  source-siglum analysis;
- lexicographic genealogy, Patel convention fingerprints, L0/R2, and forensic
  dictionary-lineage work;
- review queues about dictionary evidence.

## What Must Stay Elsewhere

- TEI/OntoLex/FrAC/RDF export and validation: `csl-standards`;
- DCS data, corpus dashboards, dictionary-vs-corpus joins: `VisualDCS`;
- grammar outside dictionary entries: future grammar repo;
- GitHub/org observatory, issues, contributors, workflows: `csl-observatory`.

## Verification Commands

```bash
npm test
npm run validate-review-reports
npm run build
```

`npm run build-pilot`, TEI/OntoLex validators, and FrAC/RDF checks now belong
in `csl-standards`, not here.

## Important Pointers

- `docs/TEI_ONTOLEX_MIGRATION.md` explains the standards split.
- `VisualDCS/docs/csl-atlas-migration/` preserves old DCS migration material.
- `docs/DECISIONS_NEEDED_LEGACY_OBSERVATORY.md` preserves the old mixed
  decision list for reference.
- `docs/ARCHITECTURE_LEGACY_INTEGRATED_ATLAS.md` preserves the old integrated
  architecture for historical context.

## Agent Rule

Before adding or editing an atlas file, ask:

> Does this start from a dictionary, headword, entry, source citation, or
> dictionary comparison?

If not, move the work to the correct repository instead of expanding atlas
scope.
