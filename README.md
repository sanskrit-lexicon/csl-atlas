# csl-atlas

_Created: 23-05-2026 · Last updated: 11-07-2026_

An interactive companion to the [CDSL](https://www.sanskrit-lexicon.uni-koeln.de/) — comparative microstructural analysis of nine narrative Sanskrit-dictionary chapters, plus an all-dictionary coverage layer for every local CDSL v02 source dictionary.

**Status:** active public-atlas implementation. The dictionary-atlas chapters are reproducible from committed JSON plus local `csl-orig` source dictionaries. TEI/OntoLex standards work has moved to [`csl-standards`](https://github.com/sanskrit-lexicon/csl-standards).

---

## What this is

Companion microsite to the [MW microanalysis paper(s)](https://github.com/sanskrit-lexicon/MWS/tree/docs-pass/papers/microanalysis). Static + interactive. Two reader paths:

- **Paper tour:** read the current atlas argument pages ([Grounded](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/paper/grounded.md) · [Triangulation](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/paper/triangulation.md) · [Appendices](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/paper/appendices.md)).
- **Reader mode:** start with [Reader Lookup](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/reader-lookup.md), then use the [Dictionary user guide](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/DICTIONARY_USER_GUIDE.md) and [Evidence labels](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/EVIDENCE_LABELS.md).
- **Tools:** explore standalone visualisations — [Cross-Dictionary Comparison](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/cross-dict.md), [All-Dictionary Coverage](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/dictionary-coverage.md), [Matrix Explorer](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/matrix-explorer.md), [Lineage Sankey](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/lineage-sankey.md), [Typology Treemap](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/typology-treemap.md), [Lexicographic Timeline](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/timeline.md), [Type Comparator](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/type-comparator.md), [Citation Tracer](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/citation-tracer.md).
- **MW Quantitative Depth (Phase 1):** [Depth dashboard](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/mw-depth-dashboard.md), [Diachronic layers](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/mw-diachronic-layers.md), [Family depth](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/mw-family-depth.md).
- **Comparative Dictionary Lab (Phase 2):** [Coverage matrix](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/dictionary-coverage-matrix.md), [Pairwise overlap](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/dictionary-overlap.md), [Gender conflicts](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/dictionary-conflicts.md), [Homonym splits](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/dictionary-homonyms.md), [Citation apparatus](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/dictionary-citations.md), [Sense depth](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/dictionary-senses.md), [Lemma dossier](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/dictionary-dossier.md).
- **Dictionary structure:** [Dictionary genealogy](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/lexicography.md), [Convention fingerprints](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/lexicographic-conventions.md), [Structural register](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/structural-register.md), [R2 sense explorer](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/r2-explorer.md), [R2 sense granularity](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/r2-h1.md).
- **Review queues:** [Gender conflicts](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/review-gender-conflicts.md), [Source-layer](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/review-source-layers.md), [Alignment confidence](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/review-alignment.md), [Source-siglum aliases](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/review-source-siglum.md).

Current URL structure:

```
/                        landing (EN)
/tools/dictionary-coverage
/tools/matrix-explorer   18×8 block/type matrix explorer
/tools/lineage-sankey    kosha → WIL/PWG/PWK/MW lineage Sankey
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

Each narrative dictionary gets a chapter; each Tier-1 figure has a per-dictionary variant and a cross-dictionary comparative variant. The separate all-dictionary inventory is generated from local `../csl-orig/v02` and covers the local CDSL v02 source dictionaries that ship a main source file.

---

## Standards Work

TEI, OntoLex, FrAC, SHACL, RDF, and related export/validation work now belongs in [`csl-standards`](https://github.com/sanskrit-lexicon/csl-standards):

- local path: `C:\Users\user\Documents\GitHub\csl-standards`
- migration note: [TEI/OntoLex migration note](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/TEI_ONTOLEX_MIGRATION.md)

The atlas may link to standards outputs when they clarify dictionary evidence, but it no longer owns those generators, schemas, generated pilot data, or UI routes.

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

Pipeline: `scripts/lib/mw-{parser,classifiers,source-layers,depth-graph}.mjs` → `scripts/build-mw-quantitative-depth.mjs`. See [`docs/MW_QUANTITATIVE_DEPTH_HANDOFF.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MW_QUANTITATIVE_DEPTH_HANDOFF.md).

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
- **Sense depth (AP/PWG/PWK):** sense-division richness per dictionary and the deepest treatment per shared lemma (AP densest at ~1.74/entry; roots show the Petersburg dictionaries' exhaustive sense splitting). MW/WIL/VCP/SKD segment senses in prose and are excluded.
- **Gender (all 7):** the gender comparison and review queue now include VCP/SKD via prose markers (VCP under-marks f/n — documented), alongside the five `<lex>`-tagged dictionaries.
- **Deferred:** full-corpus lemma lookup (search backend). No `LexemeHub` yet — per plan.

Pipeline: `scripts/lib/dict-{normalize,manifest,parser,align}.mjs` → `scripts/build-dictionary-comparison.mjs`. See [`docs/DICTIONARY_COMPARISON_PLAN.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/DICTIONARY_COMPARISON_PLAN.md).

---

## Documentation

Reader-facing:

- [TEI/OntoLex migration note](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/TEI_ONTOLEX_MIGRATION.md) — why the standards pilot moved to [`csl-standards`](https://github.com/sanskrit-lexicon/csl-standards)
- [Boundary rules](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/BOUNDARY_RULES.md) — what belongs in the dictionary atlas, and what must move elsewhere
- [Dictionary user guide](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/DICTIONARY_USER_GUIDE.md) — which dictionary to use and how to read an entry
- [Reader lookup explainer](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/READER_LOOKUP_EXPLAINER.md) — what a lookup result means and what it does not prove
- [Evidence labels](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/EVIDENCE_LABELS.md) — what the certainty labels mean

Architecture and planning:

- [Architecture](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/ARCHITECTURE.md) · [Use cases](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/USE_CASES.md) · [Reader/developer critique](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/READER_DEVELOPER_CRITIQUE.md)
- [Use-case page roadmap](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/USE_CASE_PAGE_ROADMAP.md) — page order, trust block policy, and analysis sequence
- [Chart trust template](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/CHART_TRUST_TEMPLATE.md) — required evidence/limitations/validation/owner block
- [MW Quantitative Depth handoff](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MW_QUANTITATIVE_DEPTH_HANDOFF.md) (Phase 1)
- [Dictionary comparison plan](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/DICTIONARY_COMPARISON_PLAN.md) (Phase 2)
- [H6 structural-register scatter](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/H6_STRUCTURAL_REGISTER_SCATTER.md) — implemented scholar-facing analysis page and chart spec
- [Microstructure profile](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_PROFILE.md) · [methods](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_METHODS.md) · [findings](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_FINDINGS.md)
- DCS migration material now lives in `VisualDCS/docs/csl-atlas-migration/`; active corpus work belongs outside this repo
- [Review reports](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_REPORTS.md) — shared review shape and status vocabulary
- [Review queue proofs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_QUEUE_PROOFS.md) — what each review queue proves before procedure
- [Review release roadmap](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_RELEASE_ROADMAP.md) · [Release checklist](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/RELEASE_CHECKLIST.md) · [Light review sprint](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/LIGHT_REVIEW_SPRINT.md)
- [Changelog](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/CHANGELOG.md) — what changed and when

---

## Tech stack

- [**Observable Framework**](https://observablehq.com/framework) (per [Decision 10](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/VISUALISATIONS.md#decision-10--microsite-stack-observable-framework))
- Data: committed JSON exports in [`src/data/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/src/data).
- Palette: committed [`src/palette.css`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/palette.css) and [`src/data/palette-tokens.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/palette-tokens.json).
- i18n: English/Russian strings in [`src/locales-en.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/locales-en.json) and [`src/locales-ru.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/locales-ru.json).
- Deployment: GitHub Pages on push to `main` (workflow in [`.github/workflows/build-and-deploy.yml`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/.github/workflows/build-and-deploy.yml))

---

## Local development

```bash
npm install
npm run build-coverage
npm run build-mw-depth         # MW quantitative depth (Phase 1)
npm run build-dict-comparison  # comparative dictionary lab (Phase 2)
npm run build-citation-apparatus   # citation density / apparatus comparison
npm run build-sense-depth          # sense-division richness comparison
npm run build-gender-review        # gender-conflict review queue
npm run build-source-layer-review  # unknown source-layer review queue
npm run build-alignment-review     # low-confidence alignment review queue
npm test         # unit tests for the deterministic libs (node --test)
npm run dev      # starts dev server on http://localhost:3000
npm run build    # produces dist/ for GitHub Pages
```

The full script inventory — many additional derived-data builders, importers, and review-packet generators beyond the ones above — lives in [`package.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/package.json). (See [Observable Framework docs](https://observablehq.com/framework/getting-started) for full reference.)

---

## Status checklist

- [x] Observable Framework atlas
- [x] Landing page and dictionary chapters
- [x] Interactive tools: matrix explorer, lineage Sankey, typology treemap, timeline, type comparator, citation tracer
- [x] All-dictionary coverage and size inventory for local CDSL v02 source files
- [x] TEI/OntoLex standards pilot moved to [`csl-standards`](https://github.com/sanskrit-lexicon/csl-standards)
- [x] MW Quantitative Depth Phase 1: parser, classifiers, source-layer + family-depth metrics, 3 dashboards
- [x] Comparative Dictionary Lab Phase 2 (first slice): 7-dictionary coverage/overlap/intersection/unique + tagged-dict gender disagreement, 4 pages
- [x] Per-lemma dossier: interactive lookup over ~28.5k lemmas in ≥5 dictionaries
- [x] Review layer ([`scripts/lib/review-report.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/review-report.mjs)): gender-conflict (4,556) + unknown-source-layer (449) + low-confidence-alignment (7) + source-siglum-alias (151) queues, schema-conforming, human decisions preserved across rebuilds, 4 review pages
- [x] Cross-dictionary source-siglum alignment: fold + reviewed alias table → working source × dictionary citation matrix
- [x] Sense-depth comparison (AP/PWG/PWK): per-dictionary richness, deepest-treatment leaderboard, largest gaps
- [x] DCS corpus slice moved out of the atlas; migration copies are preserved in `VisualDCS/docs/csl-atlas-migration/`
- [x] Reader Lookup v1: static SLP1/IAST headword lookup over lemmas attested in ≥4 of the 7 comparison dictionaries
- [x] Review-release roadmap, release checklist, and light review sprint worklist
- [ ] Future DCS/corpus work belongs in VisualDCS or a future grammar repo, not in this atlas
- [ ] Phase 2 follow-ups: full-text dictionary search backend; cross-dictionary siglum alias-table growth via review
- [x] Build and link validation
- [x] Unit tests (`npm test`, `node --test`) for the deterministic libs + CI test workflow
- [ ] Human review of MW source-layer seed map (unmapped sources → `unknown`)

---

## Issues Overview

Live issues: <https://github.com/sanskrit-lexicon/csl-atlas/issues>. As of 11-07-2026 there are **2** open issues; issue/PR numbering has reached #243.

## GitHub Issue Conventions

Follows the [Cologne tooling-repo taxonomy](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/runbook/cologne-tooling-runbook.md):

- **17 type labels** across 5 categories
- **4 severity levels**: trivial, minor, major, critical
- **5 milestones**: API Stability, User Experience, Data Quality, Developer Experience, Community
- **Domain labels** scoped to web-frontend: `domain:ui`, `domain:routing`, `domain:i18n`, `domain:rendering`
- **Org Project**: [Tooling Roadmap](https://github.com/orgs/sanskrit-lexicon/projects/9)

---

## License

CC-BY-SA-4.0, matching [MWS](https://github.com/sanskrit-lexicon/MWS). See [`LICENSE`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/LICENSE).

Source data: [CDSL csl-orig](https://github.com/sanskrit-lexicon/csl-orig), `mw.txt` 2026-05-23 and sibling dict files. All figures regenerate from JSON data via Python scripts in [MWS papers/microanalysis/figures/scripts/](https://github.com/sanskrit-lexicon/MWS/tree/docs-pass/papers/microanalysis/figures/scripts).

---

## How to cite

Citation metadata lives in [`CITATION.cff`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/CITATION.cff) (Citation File Format 1.2.0); GitHub renders a **"Cite this repository"** button from it. A machine-readable [`.zenodo.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/.zenodo.json) pre-stages a Zenodo software deposit so that, once the repository is connected to [Zenodo](https://zenodo.org), a tagged release mints an archival **DOI** automatically.

Until that first DOI is minted, cite the repository directly:

> Gasūns, M., Funderburk, J., & Andhrabharati. *csl-atlas: an evidence-graded atlas of the Cologne Digital Sanskrit Lexicon* (version 0.1.0). Cologne Digital Sanskrit Dictionaries project. <https://github.com/sanskrit-lexicon/csl-atlas>

When citing a specific dataset rather than the repository, use that dataset's own provenance envelope (`sourcePath`, `generatedBy`, `generatedAt`) so the exact source records and build step are recoverable. The meaning of each per-claim evidence label is defined in [`docs/EVIDENCE_LABELS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/EVIDENCE_LABELS.md).

> **Pending author actions (FAIR):** register [ORCID](https://orcid.org) iDs and add them to [`CITATION.cff`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/CITATION.cff) and [`.zenodo.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/.zenodo.json); confirm the preferred legal name for the `Andhrabharati` contributor; connect the repository to Zenodo and cut a release to mint the first DOI.

---

_Dr. Mārcis Gasūns_
