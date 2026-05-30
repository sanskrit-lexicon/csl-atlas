# csl-atlas

An interactive companion to the [CDSL](https://www.sanskrit-lexicon.uni-koeln.de/) — comparative microstructural analysis of nine narrative Sanskrit-dictionary chapters, plus an all-dictionary coverage layer for every local CDSL v02 source dictionary.

**Status:** active public-atlas implementation. The main atlas chapters and interoperability pilot are reproducible from committed JSON plus local `csl-orig` source dictionaries.

---

## What this is

Companion microsite to the [MW microanalysis paper(s)](https://github.com/sanskrit-lexicon/MWS/tree/docs-pass/papers/microanalysis). Static + interactive. Two reader paths:

- **Paper tour:** read the current atlas argument pages ([Grounded](src/paper/grounded.md) · [Triangulation](src/paper/triangulation.md) · [Appendices](src/paper/appendices.md)).
- **Tools:** explore standalone visualisations — [Cross-Dictionary Comparison](src/tools/cross-dict.md), [All-Dictionary Coverage](src/tools/dictionary-coverage.md), [Matrix Explorer](src/tools/matrix-explorer.md), [Lineage Sankey](src/tools/lineage-sankey.md), [Typology Treemap](src/tools/typology-treemap.md), [Lexicographic Timeline](src/tools/timeline.md), [Type Comparator](src/tools/type-comparator.md), [Citation Tracer](src/tools/citation-tracer.md), and [MW-PWG-PWK interoperability hard cases](src/tools/interoperability-hard-cases.md).
- **MW Quantitative Depth (Phase 1):** [Depth dashboard](src/tools/mw-depth-dashboard.md), [Diachronic layers](src/tools/mw-diachronic-layers.md), [Family depth](src/tools/mw-family-depth.md).
- **Comparative Dictionary Lab (Phase 2):** [Coverage matrix](src/tools/dictionary-coverage-matrix.md), [Pairwise overlap](src/tools/dictionary-overlap.md), [Gender conflicts](src/tools/dictionary-conflicts.md), [Homonym splits](src/tools/dictionary-homonyms.md), [Citation apparatus](src/tools/dictionary-citations.md), [Lemma dossier](src/tools/dictionary-dossier.md).
- **Review queues:** [Gender conflicts](src/tools/review-gender-conflicts.md), [Source-layer](src/tools/review-source-layers.md), [Alignment confidence](src/tools/review-alignment.md), [Source-siglum aliases](src/tools/review-source-siglum.md).

Current URL structure:

```
/                        landing (EN)
/tools/dictionary-coverage
/tools/matrix-explorer   18×8 block/type matrix explorer
/tools/lineage-sankey    kosha → WIL/PWG/PWK/MW lineage Sankey
/tools/interoperability-hard-cases
/paper/grounded
/paper/triangulation
/dicts/mw
```

---

## Coverage (Phase 4 atlas — 9 narrative dicts + all-dictionary inventory)

| Repo | Title | Date | Vols | Status |
|---|---|---|---:|---|
| [MW](https://github.com/sanskrit-lexicon/MWS) | Monier-Williams Sanskrit-English Dictionary | 1899 | 1 | chapter ready |
| [PWG](https://github.com/sanskrit-lexicon/PWG) | Petersburg Sanskrit-Wörterbuch | 1855–75 | 7 | chapter ready |
| [PWK](https://github.com/sanskrit-lexicon/PWK) | Petersburg *Kürzerer Fassung* | 1879–89 | 7 | chapter ready |
| [AP](https://github.com/sanskrit-lexicon/AP) | Apte *Practical* Sanskrit-English | 1957 | 3 | chapter ready |
| [WIL](https://github.com/sanskrit-lexicon/WIL) | Wilson Sanskrit-English | 1832 | 1 | chapter ready |
| [SKD](https://github.com/sanskrit-lexicon/SKD) | *Śabdakalpadruma* (Sanskrit-Sanskrit) | 1822–58 | 7 | chapter ready |
| [VCP](https://github.com/sanskrit-lexicon/vcp) | *Vācaspatya* (Sanskrit-Sanskrit) | 1873–84 | 7 | chapter ready |
| [ARMH](https://github.com/sanskrit-lexicon/armh) | Halāyudha's *Abhidhānaratnamālā* | ~10th c. | 1 | chapter stub |
| [ABCH](https://github.com/sanskrit-lexicon/abch) | Hemacandra's *Abhidhānacintāmaṇi* | ~12th c. | 1 | chapter stub |

Each narrative dictionary gets a chapter; each Tier-1 figure has a per-dictionary variant and a cross-dictionary comparative variant. The separate all-dictionary inventory is generated from local `../csl-orig/v02` and currently covers 43 dictionaries with main source files.

---

## MW-PWG-PWK interoperability track

The interoperability track tests how difficult Sanskrit lexicographic cases move across CDSL source records, TEI archival encoding, and OntoLex semantic modeling.

- [Implementation handoff](HANDOFF.md)
- [Project specification](docs/PROJECT_SPEC.md)
- [All-dictionary coverage and size layer](docs/ALL_DICTIONARY_COVERAGE.md)
- [Interoperability model](docs/INTEROPERABILITY_MODEL.md)
- [Validated TEI and OntoLex/FrAC profile](docs/VALIDATED_INTEROPERABILITY_PROFILE.md)
- [Sampling strategy](docs/SAMPLING_STRATEGY.md)
- [Loss-report schema](docs/LOSS_REPORT_SCHEMA.md)

Regenerate and validate the full pilot with:

```bash
npm run build-pilot
```

Run the optional external validation harness with locally installed TEI/SHACL tools:

```bash
npm run validate-external-profiles
npm run validate-external-profiles:strict
```

The external harness records TEI ODD/RELAX NG and SHACL-engine status in `data/pilot/external-validation-review.json`. It uses `teitorelaxng` from the TEI Stylesheets when available, validates TEI XML with `jing` or `xmllint`, and validates RDF/Turtle with `pyshacl`. Set `CSL_ATLAS_TEI_RNG` to reuse a precompiled TEI RELAX NG schema.

---

## MW Quantitative Depth (Phase 1)

Deterministic synchronic + conservative diachronic metrics for Monier-Williams, generated from `../csl-orig/v02/mw/mw.txt`. No LLM inference.

```bash
npm run build-mw-depth      # parse mw.txt → src/data/mw/*.json
npm run validate-mw-depth   # check counts, links, required outputs
```

- **Counted (observed/derived):** article types (overlapping membership counts, validated against `src/data/article-type-counts.json`), citation density, compound segment depth, type overlaps.
- **Inferred (flagged):** lexical families (grouped by shared `<k2>` base — no explicit MW derivation link) and diachronic source layers (from the reviewable seed map `src/data/mw-source-layers.json`).
- **Approximate:** source layers are coarse comparison buckets, **not dates**; unmapped sources fall to `unknown` and surface as a review queue.

Pipeline: `scripts/lib/mw-{parser,classifiers,source-layers,depth-graph}.mjs` → `scripts/build-mw-quantitative-depth.mjs`. See [`docs/MW_QUANTITATIVE_DEPTH_HANDOFF.md`](docs/MW_QUANTITATIVE_DEPTH_HANDOFF.md).

---

## Comparative Dictionary Lab (Phase 2)

Deterministic cross-dictionary comparison of MW, AP, PWG, PWK (`pw`), WIL, VCP, SKD, grouped by normalized SLP1 headword. First slice.

```bash
npm run build-dict-comparison      # index 7 dicts → src/data/dicts/*.json
npm run validate-dict-comparison
```

- **Coverage / overlap / intersection / unique (all 7):** distinct-lemma presence, UpSet-style combinations, pairwise Jaccard, all-dictionary core, per-dictionary unique vocabulary.
- **POS/gender disagreement (5 tagged dicts):** lemmas where MW/AP/PWG/PWK/WIL assert disjoint genders, with source links and an alignment-confidence queue.
- **Per-lemma dossier:** interactive lookup of the ~28.5k lemmas attested in ≥5 dictionaries — per-dictionary record counts, gender, and source links.
- **Homonym splits (MW/PWG/PWK):** lemmas where the homonym-marking dictionaries disagree on homonym count (`<h>` index) — one splits what another merges.
- **Citation apparatus (MW/AP/PWG/PWK):** per-dictionary citation density (PWG is far the densest at ~6.3/entry), apparatus breadth, most-cited sources, and a **cross-dictionary source matrix** aligned by canonical siglum (fold + reviewed alias table `src/data/dict-source-aliases.json`).
- **Deferred:** sense-depth comparison, VCP/SKD prose gender, and full-corpus lemma lookup (search backend). No `LexemeHub` yet — per plan.

Pipeline: `scripts/lib/dict-{normalize,manifest,parser,align}.mjs` → `scripts/build-dictionary-comparison.mjs`. See [`docs/DICTIONARY_COMPARISON_PLAN.md`](docs/DICTIONARY_COMPARISON_PLAN.md).

---

## Documentation

Reader-facing:

- [Dictionary user guide](docs/DICTIONARY_USER_GUIDE.md) — which dictionary to use and how to read an entry
- [Evidence labels](docs/EVIDENCE_LABELS.md) — what the certainty labels mean

Architecture and planning:

- [Architecture](ARCHITECTURE.md) · [Use cases](docs/USE_CASES.md) · [Reader/developer critique](docs/READER_DEVELOPER_CRITIQUE.md)
- [MW Quantitative Depth handoff](docs/MW_QUANTITATIVE_DEPTH_HANDOFF.md) (Phase 1)
- [Dictionary comparison plan](docs/DICTIONARY_COMPARISON_PLAN.md) (Phase 2)
- [DCS corpus ingestion plan](docs/DCS_CORPUS_INGESTION_PLAN.md) (Phase 3)
- [Review reports](docs/REVIEW_REPORTS.md) — shared review shape and status vocabulary

---

## Tech stack

- [**Observable Framework**](https://observablehq.com/framework) (per [Decision 10](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/VISUALISATIONS.md#decision-10--microsite-stack-observable-framework))
- Data: committed JSON exports in `src/data/`, plus generated pilot artifacts in `data/pilot/` and mirrored app JSON in `src/data/pilot/`.
- Palette: committed `src/palette.css` and `src/data/palette-tokens.json`.
- i18n: English/Russian strings in `src/locales-en.json` and `src/locales-ru.json`; the interoperability page exposes a language toggle.
- Deployment: GitHub Pages on push to `main` (workflow in `.github/workflows/build-and-deploy.yml`)

---

## Local development

```bash
npm install
npm run build-coverage
npm run build-pilot
npm run build-mw-depth         # MW quantitative depth (Phase 1)
npm run build-dict-comparison  # comparative dictionary lab (Phase 2)
npm run build-citation-apparatus   # citation density / apparatus comparison
npm run build-gender-review        # gender-conflict review queue
npm run build-source-layer-review  # unknown source-layer review queue
npm run build-alignment-review     # low-confidence alignment review queue
npm run dev      # starts dev server on http://localhost:3000
npm run build    # produces dist/ for GitHub Pages
```

(See [Observable Framework docs](https://observablehq.com/framework/getting-started) for full reference.)

---

## Status checklist

- [x] Observable Framework atlas
- [x] Landing page and dictionary chapters
- [x] Interactive tools: matrix explorer, lineage Sankey, typology treemap, timeline, type comparator, citation tracer
- [x] All-dictionary coverage and size inventory for local CDSL v02 source files
- [x] MW-PWG-PWK hard-case interoperability page
- [x] Pilot generators for hard cases, neutral model, loss reports, TEI profile XML, and OntoLex/FrAC JSON-LD
- [x] 15-case validated TEI archival profile slice beyond stubs
- [x] 15-case validated OntoLex/FrAC JSON-LD plus RDF/Turtle profile slice
- [x] Full 50-case archival TEI machine review and project ODD/profile validation
- [x] Full 50-case OntoLex/RDF machine review and project SHACL/profile validation
- [x] Optional external TEI/SHACL validation harness with strict mode
- [x] MW Quantitative Depth Phase 1: parser, classifiers, source-layer + family-depth metrics, 3 dashboards
- [x] Comparative Dictionary Lab Phase 2 (first slice): 7-dictionary coverage/overlap/intersection/unique + tagged-dict gender disagreement, 4 pages
- [x] Per-lemma dossier: interactive lookup over ~28.5k lemmas in ≥5 dictionaries
- [x] Review layer (`scripts/lib/review-report.mjs`): gender-conflict (3,671) + unknown-source-layer (449) + low-confidence-alignment (7) + source-siglum-alias (151) queues, schema-conforming, human decisions preserved across rebuilds, 4 review pages
- [x] Cross-dictionary source-siglum alignment: fold + reviewed alias table → working source × dictionary citation matrix
- [ ] Phase 2 follow-ups: sense-depth & citation-apparatus comparison, VCP/SKD prose gender, homonym-split, full-corpus lemma lookup (search backend)
- [x] Build and link validation
- [ ] Human review of MW source-layer seed map (unmapped sources → `unknown`)
- [ ] Human philological review of all 50 TEI/OntoLex cases

---

## Issues Overview

Snapshot 2026-05-29: **0** open, **0** closed.

### By Milestone

| Milestone | Open | Closed | Total |
|---|---:|---:|---:|
| API Stability | 0 | 0 | 0 |
| User Experience | 0 | 0 | 0 |
| Data Quality | 0 | 0 | 0 |
| Developer Experience | 0 | 0 | 0 |
| Community | 0 | 0 | 0 |

## GitHub Issue Conventions

Follows the [Cologne tooling-repo taxonomy](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/runbook/cologne-tooling-runbook.md):

- **17 type labels** across 5 categories
- **4 severity levels**: trivial, minor, major, critical
- **5 milestones**: API Stability, User Experience, Data Quality, Developer Experience, Community
- **Domain labels** scoped to web-frontend: `domain:ui`, `domain:routing`, `domain:i18n`, `domain:rendering`
- **Org Project**: [Tooling Roadmap](https://github.com/orgs/sanskrit-lexicon/projects/9)

---

## License

CC-BY-SA-4.0, matching [MWS](https://github.com/sanskrit-lexicon/MWS).

Source data: [CDSL csl-orig](https://github.com/sanskrit-lexicon/csl-orig), `mw.txt` 2026-05-23 and sibling dict files. All figures regenerate from JSON data via Python scripts in [MWS papers/microanalysis/figures/scripts/](https://github.com/sanskrit-lexicon/MWS/tree/docs-pass/papers/microanalysis/figures/scripts).
