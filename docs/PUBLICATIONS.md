# Atlas Publication Scope

Date: 2026-06-04

Status: active boundary-safe publication note for `csl-atlas`.

The former cross-repo publication program is preserved as:

- `docs/archive/PUBLICATIONS_LEGACY_CROSS_REPO_PROGRAM.md`

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
| [`paper_measurement_framework.md`](articles/paper_measurement_framework.md) — *Measuring the Dictionary Family* (P1) | the atlas's dictionary metrics + traceability discipline (methods spine for P2–P6) | `HYPOTHESIS_INDEX.md`; `scripts/lib/review-report.mjs`, `scripts/lib/dataset-meta.mjs`; `data/schema/review-report.schema.json`; `ARCHITECTURE.md`; the per-metric generators | working draft (DSH/Oxford target, IJL methods alternate); atlas-only methods spine for P2–P6 — NOT the legacy project-KPI paper (that is `csl-observatory`'s); full draft with the 10-metric catalog + AP90→AP worked example; author tails: 2 `[author to add]` refs (provenance, reproducibility) + byline/venue |
| [`paper_redundancy_and_descent.md`](articles/paper_redundancy_and_descent.md) — *Redundancy and Descent* (OBS-R / A07) | headword overlap + dictionary inheritance | `CORPUS_REDUNDANCY_GENEALOGY.md`; `scripts/obs/headword_multiplicity.py`; `data/sanhw1_jaccard.csv` | minor revision executed 2026-07-02 (reverse-containment column + denominators in Table 2, anusvāra/visarga fold-sensitivity number, secondary refs filled) — pending author pass |
| [`paper_citation_registers.md`](articles/paper_citation_registers.md) — *Two Citation Registers* (OBS-C / A08) | source-citation apparatus + abbreviation behaviour | `CITATION_REGISTERS.md`; `scripts/lib/source-siglum.mjs`; `src/data/dict-source-aliases.json`; `scripts/obs/citation_register_gaps.py` | minor revision executed 2026-07-02 (Table 1 BEN/BHS/AP `<ls>` totals, SKD `<ls>`-vs-*iti*-density rank swap, pre-digital comparator sentence, secondary refs filled) — pending author pass; ~100-row SKD *iti* adjudication (C-M1, shared with A02) outstanding |
| [`paper_H_convention_vs_content_lineage.md`](articles/paper_H_convention_vs_content_lineage.md) — Paper H | convention vs content lineage | Phase L0 / `data/L0/` | draft section |
| [`paper_sense_inheritance.md`](articles/paper_sense_inheritance.md) — *Condensation, Not Inflation* (R2/P2/A02) | sense granularity, survival, inheritance edges | `r2_h1.json`, `r2_h1_panel.json`, `r2_h2h3.json`, `r2_promotion_experiment.json`, `r2_kosa_fusion.json`, reviewed checkpoint | major revision executed 2026-07-02 per `REVISION_BRIEF_P2_OBS.md` — H2 reframed as an honest null, corpus-scale SKD/VCP fusion count replaces the exemplar (§7 re-scoped to record-type-dependent), abstract cut to ≤250 words, `RESPONSE_TO_REVIEWERS_P2.md` filed — pending author pass; SKD *iti* adjudication sample outstanding |
| [`paper_three_axes_descent.md`](articles/paper_three_axes_descent.md) — *Three Axes of Descent* (P3) | content vs convention vs microstructure inheritance (THREE-AXES) | `three_axis_comparison.json`, `THREE_AXIS_COMPARISON.md`, `L0_RESULTS.md`, `sanhw1_jaccard.csv`, `microstructure_fingerprint.json` | working draft (DH/lexicography methods target, WSC 2027 alternate); methodological companion to P2/P4/P6; stemmatics refs + byline to finalise |
| [`paper_indigenous_microstructure.md`](articles/paper_indigenous_microstructure.md) — *Grammar Without Tags* (P4) | verbal-root microstructure + indigenous encoding conventions | `indigenous_by_dict.json`, `root_agreement.json`, `MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md`, `MICROSTRUCTURE_ZERO_MEANING.md`; `scripts/lexico/m4_indigenous.py` | working draft (IJL target, WSC 2027 alternate); secondary refs + byline to finalise |
| [`paper_xref_lineage.md`](articles/paper_xref_lineage.md) — *Pointing Inward* (P5) | cross-reference graphs as a descent signal (XREF-CORE) | `xref_lineage.json`, `xref_edges.csv`, `xref_shared_edges.csv`, `xref_hub_review.json`; `MICROSTRUCTURE_XREF_LINEAGE.md`, `MICROSTRUCTURE_XREF_HUB_REVIEW.md`; `/tools/xref-lineage` | working draft (DH/lexicography methods target, WSC 2027 alternate); AP×AP90 positive control (85%/J=0.74) vs MW×PWG shared core (21.8%/J=0.069); graph refs + byline to finalise |
| [`paper_kosha_macrostructure.md`](articles/paper_kosha_macrostructure.md) — *Order Is the Dictionary* (P6) | macrostructure of the versified synonymic kośa (kāṇḍa→verse→synonym-set) | `kosha_macrostructure.json`; `scripts/lexico/m6_kosha_macrostructure.py`; `csl-orig` armh/abch/acph/acsj; `MICROSTRUCTURE-MACROSTRUCTURE.md` | working draft (IJL target, WSC 2027 alternate); macrostructural companion to P4; secondary refs + byline to finalise |

Both OBS drafts start from a dictionary research object (headword, citation, source
siglum) and are in scope per the rule below; each treats overlap as a *floor* for
relatedness, not proof of copying.

## Rule For New Publication Files

Before adding a publication draft to `csl-atlas`, check its first research
object. If it starts from a dictionary, entry, headword, citation, source
siglum, sense, homonym, dictionary comparison, or review item, it can live here.
If it starts from a repository, corpus, standard, workflow, publication venue,
or career program, it needs a different home or an explicit legacy pointer.
