# Atlas Publication Scope

Date: 2026-06-04

Status: active boundary-safe publication note for `csl-atlas`.

The former cross-repo publication program is preserved as:

- `docs/PUBLICATIONS_LEGACY_CROSS_REPO_PROGRAM.md`

That legacy file includes corpus-based dictionary plans, standards work,
observatory metrics, trend tracking, and long-range publication schedules. It
is preserved for historical continuity, but it is not an atlas implementation
scope document.

## What csl-atlas Owns

`csl-atlas` may support publications that start from dictionary evidence:

- lemma overlap and dictionary inheritance;
- lexicographic genealogy and convention fingerprints;
- Patel headword-convention analysis;
- dictionary microstructure and macrostructure;
- source-citation apparatus and abbreviation behavior;
- sense granularity, homonym handling, and entry structure;
- review queues for dictionary alignments, source sigla, gender/POS conflicts,
  and deterministic dictionary evidence.

## What csl-atlas Does Not Own

- GitHub/org activity, contributor, issue, PR, workflow, and repository-health
  measurement. Use `csl-observatory`.
- TEI, OntoLex, FrAC, SHACL, RDF, and external standards validation. Use
  `csl-standards`.
- DCS/corpus ingestion, passage dashboards, corpus frequency, and grammar
  outside dictionary entries. Use VisualDCS or a future grammar repo.
- Broad publication scheduling, career planning, and quarterly trend tracking
  unless rewritten as dictionary-atlas evidence notes.

## Rule For New Publication Files

Before adding a publication draft to `csl-atlas`, check its first research
object. If it starts from a dictionary, entry, headword, citation, source
siglum, sense, homonym, dictionary comparison, or review item, it can live here.
If it starts from a repository, corpus, standard, workflow, publication venue,
or career program, it needs a different home or an explicit legacy pointer.
