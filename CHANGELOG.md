# Changelog

All notable changes to csl-atlas are documented here. Format loosely follows [Keep a Changelog](https://keepachangelog.com/). Dates are ISO. The atlas is unversioned (static site); entries are grouped by date.

## [1.0.0] - 2026-06-13

### 2026-07-13 — F10 sense-order test: Böhtlingk's fourth clause, measured

#### Added
- **Sense-order forensic test** (`scripts/forensic/f10_sense_order.py`, `+ _f10_pretranslate.py`): measures the last untested clause of Böhtlingk's 1883 plagiarism charge against MW — *"die Reihenfolge der Bedeutungen einfach abgeschrieben"* (the order of the meanings copied out), which A10 had only proxied via F5 citation-order (0.811). Senses segmented by the validated per-dict markers (MW sub-`<L>` records + `<div n="to|P|1">`, PWG `<div>` Bedeutungen, AP `∙` bullets); MW↔PWG senses aligned **cross-lingually by meaning** (offline argos `de→en` gloss + Sanskrit referents; citations excluded → independent of F5); sequence concordance scored as F5 does, with an independent **Apte** control and a **shuffled-sense** null. Outputs `data/forensic/{sense_order_test,sense_order_examples,sense_order_robustness}.csv` + `f10_report.json` + `SENSE_ORDER_TEST.md`.
- **Result — a measured near-null.** Over 2,451 shared headwords (≥3 senses each) MW reproduces PWG's sense order at **0.767** concordance, but barely above the *independent* Apte control (**0.751**; paired n=660 diff **+0.003**, sign-test n.s.) — against F5 citation-order's decisive +0.39 gap over Apte. A similarity-floor sweep isolates a small Petersburg-specific residue (+0.10 at match-sim > 0.20) confined to the most closely-derived entries. Sense order is **predominantly convergent** (the shared literal→figurative→technical convention), not copied: Böhtlingk overreached on this clause. Folded into `docs/articles/article_21_apparatus_not_errors.md` §3.6 + abstract (A10).

### 2026-06-17 - Repo hygiene

#### Changed
- Archived 10 `docs/*_LEGACY_*.md` documents into `docs/archive/` and repointed the in-repo references to them, including a dead link in `docs/L0_HANDOFF.md`.
- Untracked the session-journal working files `HANDOFF.md` and `docs/SESSION_HANDOFF.md` (local-only per the org session-state protocol).
- Deleted merged branches and enabled auto-delete-on-merge for the repository.

### 2026-06-16 — DTB link-target: exact per-hymn verse validation (Dharmamitra Month 2)

#### Added
- **RV per-hymn stanza-count table** (`scripts/import-rv-verse-counts.mjs`, `npm run import-rv-verse-counts`): networked importer that derives the number of stanzas in each (maṇḍala, hymn) of the Ṛgveda from VedaWeb's own curated stanza index ([VedaWebProject/vedaweb-data](https://github.com/VedaWebProject/vedaweb-data), `rigveda/info/rv_locations.tsv`) and snapshots it to `src/data/external/rv-verse-counts.json` (1028 hymns, 10552 stanzas). Cross-checked against the long-known hymns-per-maṇḍala counts.

#### Changed
- **Citation-link pilot** (`scripts/build-citation-link-pilot.mjs`) now validates the verse index **exactly** against each hymn's stanza count instead of the conservative global cap (≤58). This caught **60** MW `<ls>RV…</ls>` citations whose verse exceeds the cited hymn's length (e.g. `RV. iii, 20, 24` — hymn 3.20 has 5 stanzas) — broken VedaWeb stanza links that the cap would have proposed. Distinct proposed loci: 3,996 → 3,942. Falls back to the ≤58 cap if the snapshot is absent. Helpers (`vedawebId`, `parseLocus`, `inRange`, `loadVerseCounts`) exported for testing.

#### Tests
- 8 new tests (`test/citation-link-pilot.test.mjs`): `vedawebId` padding, `parseLocus` citation shapes, exact vs fallback `inRange`, `deriveVerseCounts` reduction + gap detection, and the committed snapshot shape.

### 2026-06-14 — Broad dictionary parity, lookup polish, and Dharmamitra integration

#### Added
- **Broad dictionary headword coverage and overlap:** neutral coverage/overlap analyses now default to the broad set of 40 eligible local Sanskrit/BHS dictionaries, while the Core 7 scope remains available for legacy comparison.
- **Scoped coverage artifacts:** coverage matrix, pairwise overlap, unique lemmas, and all-intersection outputs expose broad and Core 7 payloads, with broad top-level summaries for public-page defaults.
- **Adapter-gated deep analysis:** deep metrics now publish explicit included/unavailable dictionary lists and method notes. Missing feature markup is represented as unavailable, not as zero evidence.
- **Validated feature expansion:** grammar/POS includes 14 supported dictionaries, citations include 13 supported `<ls>` dictionaries plus SKD/VCP/KRM partial `iti` diagnostics and WIL weak `iti` diagnostics, homonyms include 20 supported dictionaries, and senses include 14 supported dictionaries.
- **Reader Lookup and Dictionary Dossier broad mode:** public lookup remains IAST-only, supports `?q=` plus `scope`/`mode` deep links, and lazy-loads broad lookup shards on demand instead of rendering broad data eagerly.
- **Dharmamitra review-evidence layer:** merged the corpus/source adapters, shared inference helper, citation-link pilots, confidence/reporting scaffolds, monthly plan, and static integration docs from PRs #89-#96, #100, #102, and #104.

#### Changed
- **Source links:** dictionary source-link generation is centralized and trailing-slash-safe; local-only dictionaries no longer emit broken GitHub hrefs.
- **Generated data stability:** builders preserve `generatedAt` when regenerated content is otherwise identical, reducing timestamp-only churn.
- **Public copy:** coverage/overlap pages distinguish broad headword evidence from validated deep comparison, and citation pages label prose/`iti` diagnostics separately from `<ls>` source-overlap evidence.

#### Fixed
- **Reader/Dossier polish:** query and mode state now round-trip through deep links, including localized lookup pages.
- **Build pipeline fallback:** source-link and generated-data handling no longer depend on fragile GitHub URL assumptions when local dictionaries are source-link-limited.

#### Tests
- PR #106 was green on `Test` and `CodeQL`, squash-merged to `main` as `3c4646e`, and post-merge `Test`, `CodeQL`, and `Build and deploy csl-atlas` succeeded.
- Local verification before merge covered broad/headword builders, dictionary comparison builders, capability audit, citation/sense builders, dictionary validators, review-report validators, `npm test` (184 tests), and the temp Observable build workaround (51 pages, 130 links).

### 2026-06-10 — R2 page regeneration + deferred engineering

#### Added
- **R2 page regeneration** (`scripts/build-r2-pages.mjs`): data-driven SVG generators for three R2 tool pages from live JSON. Pure helpers exported for testing: `yearToX`, `rateToY`, `patternColor`, `h1Points`, `h2Bars`, `h3rDumbbells`. Marker-based file injection ensures idempotent updates.
  - **H1 scatter** (720×440): sense-granularity vs publication year from `r2_h1.json`, family legend, Pearson-r caption.
  - **H2 bars** (720×300): citation-survival rates from `r2_h2h3.json`, two groups (Cited/Uncited), 4 bars (restored+archived per group), gap annotation.
  - **H3R dumbbell** (720×300): sense-drift per inheritance edge, 3 rows, dumbbell marks with arrowheads, pattern colors, overlap labels, archived ghost circles.
  - **New page** `src/tools/r2-h2h3.md`: H2/H3R analysis with data table and findings paragraph; all numbers live from JSON.
  - Navigation: r2-h2h3 added to `observablehq.config.js`.
- **H1 panel viz refresh**: `r2-h1.md` now shows generated full-corpus scatter + new 30-lemma deconfounded panel scatter (via `h1PanelPoints` in `build-r2-pages.mjs`). Archived static SVG removed; Trust Block updated to live-data language.
- **Sense-divergence map**: `src/tools/sense-divergence.md` Observable Framework page with filterable ranked table of 1,282 lemmas with entry-count range > 0 (out of 6,777 total). Data from `data/lexico/sense_divergence.json`; generator `scripts/lexico/build_divergence_map.py`. Added to Review queues nav.

#### Tests
- 5 new tests for R2 page generators (patternColor, yearToX, rateToY, h1Points, h2Bars, h3rDumbbells). 2 new tests for H1 panel helpers. Total: 140 tests pass.

### 2026-06-11 — OBS corpus-evidence layer and two manuscripts

#### Added
- **OBS-R / OBS-C findings** (corpus-wide, all 43 dicts): `docs/CORPUS_REDUNDANCY_GENEALOGY.md` (1.49M entries → 409,649 distinct lemmas = 3.65:1; 57.9% redundant; MW-absorber stemma) and `docs/CITATION_REGISTERS.md` (two citation registers — European `<ls>` 1.23M / 59% resolvable vs indigenous `iti` SKD 69k/VCP 22k/KRM 6.4k). `OBS-R`/`OBS-C` rows added to `docs/HYPOTHESIS_INDEX.md`. (PRs #53–#55.)
- **Generators**: `scripts/obs/headword_multiplicity.py` (format-aware — reads the abch/acph/acsj `<syns>` kośa markup, so all 43 dicts are counted) and `scripts/obs/siglum_families.py` (abbreviation-family review-candidate generator).
- **Reviewed source-abbreviation table**: `src/data/dict-source-aliases.json` grown from the seed to 27 canonical works (138 aliases); reasoning in `docs/SIGLUM_ALIAS_ADJUDICATION.md`. (PR #55.)
- **Two draft manuscripts** in `docs/articles/` (IJL-targeted): `paper_redundancy_and_descent.md` (OBS-R) and `paper_citation_registers.md` (OBS-C). (PRs #68, #69.)
- `.gitignore`: `src/*.pdf` (scoped; tracked `docs/refs/` PDFs unaffected). (PR #66.)

#### Notes
- OBS-R/OBS-C are corpus-wide quantifications of existing Type-1 hypotheses (`M1-M2-MACRO`, `XREF-CORE`, `INDIG-CITE`), not parallel claims; containment is treated as a floor for overlap, **not** proof of copying.
- Manuscripts are working drafts: secondary-literature citations are flagged `[TODO]` and the byline/venue are the author's to finalise.
- The org-process twin **OBS-Q** (correction sustainability) lives in `csl-observatory`, per the boundary rules.

### 2026-06-03 — Review-release roadmap and Reader Lookup v1

#### Added
- Review-release planning docs: `docs/REVIEW_RELEASE_ROADMAP.md`, `docs/RELEASE_CHECKLIST.md`, and `docs/LIGHT_REVIEW_SPRINT.md`.
- Reader Lookup v1: static dictionary-first headword lookup backed by `src/data/dicts/lemma-lookup.json` for lemmas attested in >=4 target dictionaries.
- Shared lookup normalization module for SLP1 and IAST query candidates, with unit tests.
- Public Reader Mode entry in the sidebar and landing page.
- Dictionary-structure pages moved in from `csl-observatory`: dictionary genealogy, convention fingerprints, and R2 sense-structure pages.

#### Notes
- Reader Lookup v1 is exact/prefix headword lookup only; lower-coverage lemmas remain omitted. It is not full-text dictionary search, corpus lookup, sandhi recovery, Devanagari input, or `LexemeHub`.
- The light review sprint prepares worklists for human review; it does not mark philological decisions as complete.
- TEI/OntoLex/FrAC standards work moved out of `csl-atlas` to `csl-standards`.
- DCS corpus inventory work moved out of `csl-atlas`; migration copies live in `VisualDCS/docs/csl-atlas-migration/`.

### 2026-05-29 → 2026-05-31 — Evidence atlas build-out

A large expansion from the interoperability pilot into a deterministic, source-linked, evidence-labelled research atlas over the CDSL dictionaries and the DCS corpus reference data. Every generated claim is reproducible from `../csl-orig` / `../DCS` and carries `observed` / `derived` / `inferred` labels; no runtime LLM inference.

#### Added — documentation foundation
- `ARCHITECTURE.md`, `docs/USE_CASES.md`, `docs/READER_DEVELOPER_CRITIQUE.md`.
- Reader-facing: `docs/DICTIONARY_USER_GUIDE.md`, `docs/EVIDENCE_LABELS.md`.
- Plans: `docs/DICTIONARY_COMPARISON_PLAN.md` (Phase 2), `docs/REVIEW_REPORTS.md`; DCS planning from this period was later migrated to VisualDCS.

#### Added — Phase 1: MW Quantitative Depth
- Pipeline `scripts/lib/mw-{parser,classifiers,source-layers,depth-graph}.mjs` + `build-mw-quantitative-depth.mjs` → `src/data/mw/*.json`; `validate-mw-depth`.
- Article-type classifier reproduces the committed typology counts exactly (grammar types primary-only + exclusive by priority m>f>n>mfn>ind).
- Conservative source-layer seed map (`src/data/mw-source-layers.json`) with a base-form fallback; unmapped citations cut from 31.9% to ~9%.
- Pages: depth dashboard, diachronic layers, family depth.

#### Added — Phase 2: Comparative Dictionary Lab (MW, AP, PWG, PWK, WIL, VCP, SKD)
- `scripts/lib/dict-{normalize,manifest,parser,align}.mjs` + `build-dictionary-comparison.mjs`.
- Coverage matrix, pairwise overlap, all-dictionary intersection, dictionary-unique vocabulary, **homonym splits** (MW/PWG/PWK `<h>`), **gender disagreement** (all 7 — `<lex>` for tagged dicts, prose markers for VCP/SKD), **sense depth** (AP/PWG/PWK), **citation apparatus**, and an interactive **lemma dossier**.
- Cross-dictionary **source-siglum mapping**: diacritic/case fold + reviewed alias table (`src/data/dict-source-aliases.json`) → working source × dictionary matrix.

#### Added — Phase 3a: DCS corpus (later migrated)
- DCS schema inspection documented the local `../DCS/` export as reference data, not passage-level occurrences.
- The DCS inventory generator and page were later moved out of `csl-atlas`; migration copies live in `VisualDCS/docs/csl-atlas-migration/`.

#### Added — Review layer
- `data/schema/review-report.schema.json` + shared `scripts/lib/review-report.mjs` (overlay preserved across rebuilds by `reviewId`).
- Four queues with pages: gender conflicts (4,556), unknown source layers (449), low-confidence alignment (7), source-siglum aliases (151).

#### Added — site, tests, CI
- Sidebar + landing reorganized into purpose groups (MW depth · comparison · review · figures · paper · dictionaries).
- Unit tests via Node's built-in `node:test` (`npm test`, 39 tests) covering the lib modules and orchestrator decision helpers; build orchestrators made import-safe (guarded `main()`).
- `.github/workflows/test.yml` gates PRs.

### Baseline — Interoperability pilot (≤ 2026-05-29)
- MW-PWG-PWK hard-case interoperability track: 50-case TEI archival + OntoLex/FrAC pilot, loss reports, and validation harnesses. This track now lives in `csl-standards`.
- Nine narrative dictionary chapters and the microanalysis paper pages.
