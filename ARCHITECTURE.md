# CSL Atlas Architecture

Date: 2026-06-04

Status: active dictionary-atlas architecture. This file follows
`docs/BOUNDARY_RULES.md` and supersedes the older integrated evidence-atlas
architecture. The preserved legacy version is
`docs/archive/ARCHITECTURE_LEGACY_INTEGRATED_ATLAS.md`.

## Mission

`csl-atlas` is the public dictionary-evidence path for the Cologne Digital
Sanskrit Lexicon.

North star:

```text
reader question -> dictionary evidence -> source link -> evidence/review status
```

The atlas explores dictionaries as books, editions, source records, headword
systems, citation practices, article structures, and dictionary-to-dictionary
relations.

## Boundaries

The admission test is simple: a page, script, dataset, review queue, or plan
belongs here only when it starts from a dictionary, headword, entry, source
citation, or dictionary comparison.

| Area | Home |
|---|---|
| Dictionary evidence, reader lookup, comparison, genealogy, source sigla | `csl-atlas` |
| TEI, OntoLex, FrAC, SHACL, RDF, export validation | `csl-standards` |
| DCS data, corpus dashboards, dictionary-vs-corpus joins | `VisualDCS` |
| Grammar outside dictionary entries | future grammar repo |
| GitHub/org metrics, issues, contributors, workflow observatory | `csl-observatory` |

External links are allowed when they clarify dictionary evidence. They must not
turn this repository into a standards, corpus, grammar, or observatory site.

## Product Shape

The atlas is static-first and Observable Framework-based.

It exposes:

- reader lookup and dictionary user guidance;
- dictionary chapters;
- source-linked dashboards;
- dictionary comparison tools;
- dictionary-structure and genealogy pages;
- review queues for uncertain dictionary evidence.

No backend, database, runtime LLM classification, or full-text search engine is
part of the current architecture.

## Audience And Languages

Primary audiences:

- readers, students, and translators looking up a Sanskrit word;
- Sanskrit lexicographers and dictionary historians;
- digital humanities researchers inspecting CDSL evidence;
- maintainers reviewing machine-derived dictionary claims.

Interface language policy:

- public UI remains bilingual in English and Russian;
- Russian scholarly terminology should be reviewed rather than invented;
- German and Sanskrit terms appear where they are part of the dictionary record
  or scholarly tradition, not as separate UI locales.

## Source Data

Large source dictionaries stay outside the repo:

```text
../csl-orig/v02/<dict>/<dict>.txt
```

Committed outputs stay compact and reproducible:

```text
src/data/                    Observable-facing generated JSON/CSV
src/data/dicts/              dictionary comparison and lookup data
src/data/review/             review-report overlays
src/data/lexicographic-structure/  L0, R2, genealogy, and convention data
data/                        repo-level generated data or research artifacts
data/schema/                 JSON schemas
```

Raw `csl-orig`, raw DCS, and other large external sources are not committed.

## Core Data Shapes

Parsers and generators should converge on a small dictionary-entry shape:

```text
DictionaryEntry
  dictionary          short code, e.g. mw, pwg, skd
  recordId            stable source record id, usually L or dictionary-local id
  lemmaRaw            source headword as printed/encoded
  lemmaNormalized     comparison/lookup key
  homonymId           explicit or derived homonym marker when available
  line                source line number
  href                source link
  raw                 source record snippet or full record when compact enough
  pos                 coarse POS when reliable
  genders[]           extracted genders when reliable
  citations[]         source sigla or inline citation evidence
  sourceLayers[]      broad citation/source-layer labels when available
  evidenceLevel       observed | derived | inferred | reviewed
  warnings[]          caveats needed for this record
```

Generated files use the standard envelope:

```text
schemaVersion
license            SPDX id (CC-BY-SA-4.0); see scripts/lib/dataset-meta.mjs
licenseUrl
generatedAt
sourcePath
recordCount
assumptions[]
warnings[]
items / rows / data
```

Reader-facing lookup data keeps compatibility monoliths and page-load shards:

```text
src/data/dicts/lemma-lookup.json              legacy/core lookup monolith
src/data/dicts/lemma-dossier.json             legacy/core dossier monolith
src/data/dicts/core-lookup/manifest.json      core lookup manifest + samples
src/data/dicts/core-lookup/shards/*.json      exact/prefix lookup shards
src/data/dicts/core-dossier/manifest.json     core dossier manifest + samples
src/data/dicts/core-dossier/shards/*.json     exact/prefix dossier shards
src/data/dicts/broad-headword/manifest.json   broad headword manifest + samples
src/data/dicts/broad-headword/shards/*.json   broad headword shards
src/data/dcs/lemma-summary/manifest.json      DCS chip manifest
src/data/dcs/lemma-summary/shards/*.json      DCS chip shards
```

Observable pages should load manifests/sample entries first and then only the
candidate shards needed for exact/prefix lookup. The monolithic lookup and
dossier files remain generated for validators and compatibility.

## Evidence Labels

All claims carry one of the canonical labels:

| Label | Meaning |
|---|---|
| `observed` | Directly present in a dictionary source record |
| `derived` | Produced by a deterministic rule from observed source data |
| `inferred` | Heuristic and useful, but not yet verified |
| `reviewed` | Human confirmed or corrected the value |

No visualization should hide whether a result is observed, derived, inferred,
or reviewed. See `docs/EVIDENCE_LABELS.md`.

## Review Architecture

Review reports are overlays on generated data. Re-running a generator must not
erase human decisions.

Canonical review status vocabulary:

| Status | Meaning |
|---|---|
| `machine` | Produced by heuristics; no human has looked at it |
| `needs-review` | Flagged because confidence is low or sources conflict |
| `reviewed-ok` | A human confirmed the machine value |
| `reviewed-corrected` | A human supplied a corrected value |
| `blocked` | Cannot be resolved yet because evidence is missing or bad |
| `deferred` | Valid, but postponed to a later phase |

Review reports live in:

```text
src/data/review/
data/schema/review-report.schema.json
```

Shared helpers live in `scripts/lib/review-report.mjs`. New queues should use
that contract instead of inventing local review formats.

## Current Tracks

1. MW quantitative depth and dictionary chapters.
2. Comparative Dictionary Lab: coverage, overlap, gender/POS conflicts,
   homonyms, senses, citation apparatus, and lemma dossiers.
3. Reader Lookup v1: exact/prefix lookup over generated dictionary comparison
   data.
4. Dictionary structure: L0 convention fingerprints, lexicographic genealogy,
   R2 sense alignment, and forensic dictionary-lineage evidence.
5. Light review sprint over high-value dictionary-evidence queues.

## Diachronic And Source-Layer Policy

The atlas may map dictionary source citations to broad period/source layers
when doing so explains dictionary evidence. These layers are conservative and
must be labeled `derived` or `inferred`; they are not exact dating claims.

DCS passage chronology, corpus frequency, and dictionary-vs-corpus claims do
not belong in this repository.

## Verification Gates

Release checks:

```bash
npm test
npm run validate-review-reports
npm run build
```

Boundary checks:

- no package command for TEI/OntoLex/FrAC/RDF export;
- no package command for DCS/corpus generation;
- no Observable route whose primary object is corpus, standards, or
  GitHub/org observability;
- only pointer/archive docs may mention moved-out work as a destination.

## Related Documents

- `docs/BOUNDARY_RULES.md`
- `docs/REVIEW_RELEASE_ROADMAP.md`
- `docs/RELEASE_CHECKLIST.md`
- `docs/DICTIONARY_USER_GUIDE.md`
- `docs/EVIDENCE_LABELS.md`
- `docs/REVIEW_REPORTS.md`
- `docs/DICTIONARY_COMPARISON_PLAN.md`
- `docs/TEI_ONTOLEX_MIGRATION.md`
