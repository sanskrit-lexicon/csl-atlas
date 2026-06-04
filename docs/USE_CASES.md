# CSL Atlas Use Cases

Date: 2026-06-04

This is the active use-case inventory for `csl-atlas` after the repository
boundary split.

The earlier integrated atlas use cases are preserved for history in
`docs/USE_CASES_LEGACY_INTEGRATED_ATLAS.md`. Do not treat that legacy file as
current product scope.

## Boundary Rule

An active atlas use case must start from at least one of these objects:

- a dictionary;
- a dictionary headword or entry;
- a dictionary source citation;
- a dictionary comparison;
- a dictionary-structure feature;
- a dictionary review item.

Use cases that start from corpus passages, DCS data, grammar analysis, TEI,
OntoLex, FrAC, SHACL, RDF, GitHub issues, contributors, workflows, or org-level
metrics belong in another repository:

- DCS and corpus comparison: `VisualDCS`;
- grammar: future grammar repo;
- standards/export: `csl-standards`;
- GitHub/org observatory: `csl-observatory`.

## Evidence Labels

The atlas must keep uncertainty visible.

| Label | Meaning |
|---|---|
| `observed` | Directly present in a source dictionary record. |
| `derived` | Deterministically computed from dictionary records. |
| `inferred` | Proposed by a heuristic and needs review. |
| `machine-reviewed` | Generated output passed deterministic checks only. |
| `human-reviewed` | A reviewer confirmed or corrected the item. |

## Reader Use Cases

### UC-RD-01 Basic Word Lookup `P0`

- Actor: Sanskrit reader, student, translator.
- Goal: enter a lemma and see available dictionary evidence.
- Evidence: dictionary headwords, normalized lemmas, entry links, coverage count.

### UC-RD-02 Choose Which Dictionary To Use `P0`

- Actor: new dictionary user.
- Goal: understand whether MW, AP, PWG, PWK, WIL, VCP, SKD, or another
  dictionary is the best first stop for a task.
- Evidence: dictionary scope, language, source density, coverage, caveats.

### UC-RD-03 Multi-Dictionary Lemma View `P0`

- Actor: reader comparing dictionaries.
- Goal: see side-by-side coverage for one lemma.
- Evidence: dictionary coverage, POS/gender when reliable, source links, review
  status.

### UC-RD-04 No Result Or Ambiguous Result `P0`

- Actor: reader typing SLP1 or IAST.
- Goal: get clear no-result, prefix-result, or ambiguous-result messaging.
- Evidence: normalized query forms and matching dictionary headwords.

### UC-RD-05 Evidence Explanation `P0`

- Actor: non-specialist reader.
- Goal: understand whether a label means "in the source", "computed", or
  "probable".
- Evidence: the shared evidence-label vocabulary.

### UC-RD-06 Source Citation Follow-Through `P1`

- Actor: reader checking a dictionary claim.
- Goal: follow a dictionary source citation or raw entry link.
- Evidence: source abbreviations, dictionary entry links, citation counts.

### UC-RD-07 German Dictionary Help `P1`

- Actor: reader using PWG, PWK, SCH, CAE, or CCS.
- Goal: understand why German evidence matters and where caveats apply.
- Evidence: dictionary language metadata, lineage notes, glossary links.

## Dictionary Comparison Use Cases

### UC-CD-01 Coverage Matrix `P1`

- Actor: researcher.
- Goal: see which dictionaries cover which lemma sets.
- Evidence: generated coverage matrix under `src/data/dicts/`.

### UC-CD-02 Pairwise Overlap `P1`

- Actor: researcher.
- Goal: compare two dictionaries by shared and unique lemmas.
- Evidence: pairwise overlap output and dictionary source metadata.

### UC-CD-03 All-Dictionary Intersection `P1`

- Actor: researcher or reader.
- Goal: identify high-coverage lemmas attested across many target dictionaries.
- Evidence: all-intersection output and coverage thresholds.

### UC-CD-04 POS And Gender Conflict Review `P1`

- Actor: reviewer.
- Goal: inspect disagreements where dictionary metadata conflicts.
- Evidence: generated conflict queues with preserved review decisions.

### UC-CD-05 Alignment Confidence Review `P1`

- Actor: reviewer.
- Goal: review low-confidence dictionary alignments.
- Evidence: alignment-confidence reports and review status fields.

### UC-CD-06 Dictionary Recommendation For A Task `P2`

- Actor: reader choosing sources.
- Goal: identify dictionaries suited to broad lookup, deep source apparatus,
  German tradition, Sanskrit-Sanskrit evidence, or specialized vocabulary.
- Evidence: coverage, language, source density, and documented caveats.

## Dictionary Structure Use Cases

### UC-LX-01 MW Article Anatomy `P0`

- Actor: reader or researcher.
- Goal: understand the structure of a Monier-Williams entry.
- Evidence: entry-type counts, source links, typology examples.

### UC-LX-02 Lexicographic Conventions `P1`

- Actor: lexicography researcher.
- Goal: compare headword conventions across dictionaries.
- Evidence: L0 convention fingerprints, Patel convention mapping, review notes.

### UC-LX-03 Dictionary Genealogy `P1`

- Actor: historian of lexicography.
- Goal: inspect dictionary lineage hypotheses and evidence.
- Evidence: cladograms, overlap, rare-lemma containment, citation and convention
  signals.

### UC-LX-04 Sense-Splitter Research `P2`

- Actor: researcher.
- Goal: compare deterministic sense segmentation across dictionary families.
- Evidence: R2 sense-splitter outputs and documented parser caveats.

### UC-LX-05 Source-Siglum Review `P1`

- Actor: reviewer.
- Goal: resolve common unknown source-layer sigla and alias candidates.
- Evidence: frequency-ranked source-siglum queues and dictionary citations.

## Review And Quality Use Cases

### UC-RV-01 Record A Human Correction `P0`

- Actor: reviewer.
- Goal: preserve `reviewStatus`, `reviewedValue`, `reviewer`, `reviewedAt`, and
  `note` when generators rerun.
- Evidence: canonical review-report schema and generated reports.

### UC-RV-02 Track Reviewed Vs Machine Status `P0`

- Actor: release manager.
- Goal: measure what was human-reviewed and what remains machine-derived.
- Evidence: review reports, sprint docs, validation commands.

### UC-RV-03 Sample Large Conflict Queues `P1`

- Actor: reviewer with limited time.
- Goal: review representative samples instead of exhausting thousands of items.
- Evidence: ranked queues, 25-item samples, documented conflict types.

## Developer Use Cases

### UC-DEV-01 Regenerate Dictionary Data `P0`

- Actor: developer.
- Goal: rebuild compact generated dictionary JSON without committing raw sources.
- Evidence: package scripts, local `csl-orig`, validation outputs.

### UC-DEV-02 Add Or Improve A Dictionary Parser `P1`

- Actor: developer.
- Goal: improve deterministic extraction from a dictionary source.
- Evidence: source-linked examples, validation reports, review queues.

### UC-DEV-03 Keep The Atlas Static `P0`

- Actor: maintainer.
- Goal: ship a public Observable site with no backend requirement.
- Evidence: committed compact JSON, build output, GitHub Pages readiness.

### UC-DEV-04 Diagnose A Metric From A Source Link `P1`

- Actor: developer or reviewer.
- Goal: trace a dashboard value back to dictionary records.
- Evidence: source pointers, assumptions, warnings, evidence labels.

## Anti-Use Cases

These are explicitly out of scope for active `csl-atlas` work.

### AUC-01 Corpus Or Passage Lookup

DCS passages, corpus dashboards, dictionary-vs-corpus joins, and corpus frequency
claims belong in `VisualDCS` or a future grammar repo.

### AUC-02 Standards Export Work

TEI, OntoLex, FrAC, SHACL, RDF, external validation profiles, and export
pipelines belong in `csl-standards`.

### AUC-03 GitHub Or Organisation Observatory

Issue counts, contributor metrics, workflow dashboards, and org-level refresh
jobs belong in `csl-observatory`.

### AUC-04 Runtime LLM Classification

The public atlas uses deterministic, reproducible data generation. LLMs may help
with offline drafting or review prompts, but runtime classification is out of
scope.

### AUC-05 Backend-First Search

Reader Lookup v1 is static-first. A database, backend search engine, full-text
corpus search, or broad `LexemeHub` object is future cross-repo work, not this
roadmap.

### AUC-06 Hiding Weak Evidence

Unreviewed, inferred, or machine-derived outputs must remain visibly labeled.

## Current Milestones

### Milestone A: Reader Can Start

- Reader Lookup v1 works for exact SLP1 and normalized IAST queries.
- Dictionary-choice guidance is visible.
- Evidence labels and caveats appear near complex tools.

### Milestone B: Reviewer Can Improve Data

- Low-confidence alignments, source-siglum queues, and representative conflict
  samples are measurable.
- Existing review decisions survive generator reruns.

### Milestone C: Researcher Can Trust A Chart

- Every chart has source data, assumptions, warnings, and validation commands.
- Corpus, standards, and observatory claims point outside the atlas.

## Documentation Layer Decisions

- Use-case pages come before analysis method notes.
- The first reader page is the dictionary chooser:
  [`DICTIONARY_USER_GUIDE.md`](DICTIONARY_USER_GUIDE.md).
- Every public tool, chart, or page must carry a compact trust block:
  Evidence, Limitations, Validation, Owner repo.
- Scholar-facing analysis docs come before public-facing analysis explanations.
- Review queues should first document what each queue proves, then how to review
  it.
- H6 structural-register scatter is now the implemented chart-trust example;
  H4 semantic fields come after the use-case page layer and microstructure doc
  family are stable.

## Related Docs

- `docs/BOUNDARY_RULES.md`
- `docs/USE_CASE_PAGE_ROADMAP.md`
- `docs/CHART_TRUST_TEMPLATE.md`
- `docs/REVIEW_RELEASE_ROADMAP.md`
- `docs/RELEASE_CHECKLIST.md`
- `docs/REVIEW_QUEUE_PROOFS.md`
- `docs/DICTIONARY_USER_GUIDE.md`
- `docs/READER_LOOKUP_EXPLAINER.md`
- `docs/EVIDENCE_LABELS.md`
- `docs/H6_STRUCTURAL_REGISTER_SCATTER.md`
- `docs/MICROSTRUCTURE_PROFILE.md`
- `docs/MICROSTRUCTURE_METHODS.md`
- `docs/MICROSTRUCTURE_FINDINGS.md`
- `docs/USE_CASES_LEGACY_INTEGRATED_ATLAS.md`
