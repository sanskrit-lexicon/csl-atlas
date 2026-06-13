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

## Current Drafts (`docs/articles/`)

| Draft | Starts from | Evidence | Status |
|---|---|---|---|
| [`paper_redundancy_and_descent.md`](articles/paper_redundancy_and_descent.md) — *Redundancy and Descent* (OBS-R) | headword overlap + dictionary inheritance | `CORPUS_REDUNDANCY_GENEALOGY.md`; `scripts/obs/headword_multiplicity.py`; `data/sanhw1_jaccard.csv` | working draft (IJL target); secondary refs + byline to finalise |
| [`paper_citation_registers.md`](articles/paper_citation_registers.md) — *Two Citation Registers* (OBS-C) | source-citation apparatus + abbreviation behaviour | `CITATION_REGISTERS.md`; `scripts/lib/source-siglum.mjs`; `src/data/dict-source-aliases.json` | working draft (IJL target); secondary refs + byline to finalise |
| [`paper_H_convention_vs_content_lineage.md`](articles/paper_H_convention_vs_content_lineage.md) — Paper H | convention vs content lineage | Phase L0 / `data/L0/` | draft section |
| [`paper_sense_inheritance.md`](articles/paper_sense_inheritance.md) — *Condensation, Not Inflation* (R2/P2) | sense granularity, survival, inheritance edges | `r2_h1.json`, `r2_h1_panel.json`, `r2_h2h3.json`, `r2_promotion_experiment.json`, reviewed checkpoint | working draft (Lexicographica target, IJL alternate); secondary refs + byline to finalise |
| [`paper_indigenous_microstructure.md`](articles/paper_indigenous_microstructure.md) — *Grammar Without Tags* (P4) | verbal-root microstructure + indigenous encoding conventions | `indigenous_by_dict.json`, `root_agreement.json`, `MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md`, `MICROSTRUCTURE_ZERO_MEANING.md`; `scripts/lexico/m4_indigenous.py` | working draft (IJL target, WSC 2027 alternate); secondary refs + byline to finalise |

Both OBS drafts start from a dictionary research object (headword, citation, source
siglum) and are in scope per the rule below; each treats overlap as a *floor* for
relatedness, not proof of copying.

## Rule For New Publication Files

Before adding a publication draft to `csl-atlas`, check its first research
object. If it starts from a dictionary, entry, headword, citation, source
siglum, sense, homonym, dictionary comparison, or review item, it can live here.
If it starts from a repository, corpus, standard, workflow, publication venue,
or career program, it needs a different home or an explicit legacy pointer.
