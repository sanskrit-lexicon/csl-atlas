# Boundary Rules

Date: 2026-06-03
Last updated: 2026-06-04

Status: human decision. These rules define the direction of `csl-atlas` and
supersede older broad "Sanskrit evidence atlas" language wherever it conflicts.

## Mission

`csl-atlas` is the dictionary-evidence path.

It explores Sanskrit dictionaries as books, editions, source records,
headword systems, citation practices, article structures, and
dictionary-to-dictionary relations.

## Admission Test

A page, script, dataset, review queue, or plan belongs in `csl-atlas` only if
its primary object is one of:

- a dictionary;
- a dictionary edition or original printed book;
- a dictionary headword or entry;
- a dictionary source record from `csl-orig`;
- a dictionary source citation or source siglum;
- a dictionary microstructure or macrostructure feature;
- a dictionary-to-dictionary comparison;
- a reader path that starts from dictionary evidence.

If it does not start from dictionary evidence, it does not belong here.

## Belongs Here

- Dictionary chapters and reader-facing dictionary guidance.
- Reader lookup over dictionary headwords.
- Per-entry and per-lemma dictionary dossiers.
- MW, PWG, PWK, AP, WIL, SKD, VCP, ARMH, ABCH, and other dictionary-specific
  analysis.
- Cross-dictionary coverage, overlap, gender/POS, homonym, citation, sense,
  source-siglum, and lineage analysis.
- Lexicographic genealogy, headword-convention, Patel-style normalization, and
  cladogram work, because these compare the structure of dictionaries.
- Review queues whose uncertainty is about dictionary evidence.

## Does Not Belong Here

- DCS corpus data, corpus dashboards, corpus grammar, passage evidence, and
  dictionary-vs-corpus joins. DCS data belongs at
  `https://github.com/gasyoun/VisualDCS`; grammar needs a separate future repo.
- GitHub organization analytics, repo metrics, issues, PRs, contributors,
  tooling runbooks, workflow health, and ecosystem observability.
- Publication planning unless it is directly tied to dictionary-atlas pages or
  dictionary-evidence interpretation.
- General technical standards/export work such as TEI, OntoLex, FrAC, SHACL,
  or RDF pipeline maintenance. This belongs in `csl-standards`, not in the
  atlas. These formats may be mentioned here only when they clarify what a
  dictionary record contains; they should not define the atlas direction.

## External Links Are Allowed

`csl-atlas` may link to external corpus, observatory, standards, or publication
repositories, but it must not import their scope. A link is acceptable when it
helps explain dictionary evidence without turning the atlas into a corpus,
workflow, or standards site.

## Boundary Cleanup Completed

Completed on 2026-06-04 and merged in
[`csl-atlas` PR #32](https://github.com/sanskrit-lexicon/csl-atlas/pull/32):

- TEI/OntoLex/FrAC pilot exports and validation moved to `csl-standards`.
  TEI is for CDSL-markup validation and publication for other lexicographic
  projects; OntoLex is a stress test for now and real RDF publication later;
  FrAC is frozen until VisualDCS/corpus evidence is ready.
- Public standards home:
  `https://github.com/sanskrit-lexicon/csl-standards`.
- DCS inventory page, generated manifest, and build script moved out of the
  active atlas. Migration copies live in
  `https://github.com/gasyoun/VisualDCS/tree/main/docs/csl-atlas-migration`.
- Lexicographic genealogy, Patel convention fingerprints, L0 cladogram,
  Paper H convention/content lineage, and R2 sense-structure material moved
  into `csl-atlas` from `csl-observatory`.
  The observatory-side cleanup merged in
  [`csl-observatory` PR #14](https://github.com/sanskrit-lexicon/csl-observatory/pull/14).

## Current Relocation Candidates

These are present or planned items that need review before future cleanup:

- Broad `LexemeHub`, `CorpusOccurrence`, and corpus-grammar architecture in
  older planning docs: remove from atlas direction or archive as superseded
  planning.

## Future Work Rule

Before adding a new file, page, generated dataset, or package command, ask:

> Does this start from a dictionary, headword, entry, source citation, or
> dictionary comparison?

If the answer is no, open or use a different repository.
