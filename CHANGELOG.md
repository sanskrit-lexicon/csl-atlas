# Changelog

All notable changes to csl-atlas are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/). Dates are ISO.

## [Unreleased]

### Changed — §8.11 sourced + a conflation fixed (H1336)

- **Sourced the "9/10" figure:** it is **Delbrück's estimate** of Böhtlingk's share of the
  "Böhtlingk–Roth" PWG (Roth = Ṛgveda + Suśruta, Whitney = AV, Weber = Śatapatha, Stenzler = Manu;
  Böhtlingk everything else, whole done in 23 years, 1852–1875). **Corrected a conflation:** the
  "74" is the **years since PD's 1948 conception**, *not* a planned lexicographer count; PD's
  staffing point is now stated as a *severe shortage* (~a dozen-to-two-dozen active), the real
  cause. Report §8.11 + page.

### Changed — §8.11 solo-vs-committee sharpened (H1336)

- **Böhtlingk** wrote ~**9/10 of the "Böhtlingk–Roth" PWG** as well as the *kürzere Fassung* alone
  — one man, two complete Sanskrit dictionaries (strengthens the near-solo point). **PD's committee
  structure is a *cause* of non-completion, not a footnote:** planned for **~74 lexicographers**, it
  has **about a dozen** working regularly now — "may never finish at all". Report §8.11 + page.

### Added — §8.11 "Who finishes a dictionary — and why" (measured note, H1336)

- New report §8.11 + page section answering "are Germans the best dictionary-makers and Indians
  confined to the kośa?" — measured, non-essentialist: it is method/institution/scope, not nation.
  The real German trait is **finishability** (Mayrhofer's rule), not maximalism; **PD is not German**
  (Deccan-College slip-archive project, slips now scanned). The entry-size decay is a **European**
  trait (PWG/PWK/Grassmann/KEWA/EWA + big non-Sanskrit dicts) — **SKD/VCP show none**. The finished
  dictionaries were near-solo: **V. S. Apte** made a complete Skt-Eng dictionary almost alone and
  **died at 34**; Böhtlingk carried the *kürzere Fassung* single-handed. Indians produced *finished*
  encyclopaedias (Apte, SKD, VCP); the struggling ones are the modern *institutional* projects.
  Also softened the BORI claim (still **far from finished**, ~37 % after 38 yr, not "~2090").

### Added — Per-letter anatomy + entry-size decay test (H1416)

- New study
  [reports/LETTER_ANATOMY_AND_ENTRY_SIZE_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/LETTER_ANATOMY_AND_ENTRY_SIZE_2026.md)
  and interactive page [`/tools/letter-anatomy`](https://sanskrit-lexicon.github.io/csl-atlas/tools/letter-anatomy),
  extending the H1336 §8.5–8.9 per-letter observations into a systematic programme
  ([scripts/letter_anatomy.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/letter_anatomy.py)).
- **Q1 samāsa share (MW):** reproduces the H1336 `a`/`ā` figure exactly (83.1 %) and
  generalises it — `u` 79.5 %, `p` 78.0 %, `s` 77.9 %, `v` 75.5 %; `k` (no preverb) 56.4 %.
  `a` is the most compound-dense letter but **not uniquely** so.
- **Q2 upasarga profile:** every large letter heads a preverb family — `v` = *vi-* (38.6 %),
  `u` = *ud-/upa-* (62.3 %), `s` = *sam-/su-*, `p` = *pra-/pari-/prati-*, `a` = five preverbs +
  the privative. The mechanistic reason `a`/`u`/`p`/`s`/`v` balloon.
- **Q4 funding-decay test (the headline):** using an outlier-robust per-letter rank test
  (mandatory — VCP has single articles >310k chars that wreck the parametric FE), the belief
  that entries shrink over serial publication is **refuted for the two dictionaries it named,
  SKD and VCP** (ρ ≈ 0.00). The decay is real and strong instead in **PWG (−0.19), PWK (−0.34),
  GRA (−0.20)** — the German Petersburg/Grassmann tradition with a documented compression history.
- New derived feeds
  [data/pd/letter_anatomy.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/letter_anatomy.tsv)
  (dict × letter),
  [data/pd/entry_size_by_position.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/entry_size_by_position.tsv),
  and [data/pd/upasarga_counts.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/upasarga_counts.tsv)
  (Q2 full breakdown — every one of the 20 preverbs × every dictionary, count + %; report §3.1).
  `vi-` is the largest preverb in every dict; the `sam`/`su` order flips in Vedic (GRA `su` 452 > `sam` 126).
- **Graveyard of `a` — corrected (H1336 tidy):** the reef sinks only the *exhaustive*.
  Goldstücker (1856) died in Sanskrit `a` (6,761 entries). Kossowicz (KOW, 1854) reached 13,488
  entries but is ordered by the **Russian**, not Sanskrit, alphabet and left unfinished — a
  partial work of a different kind; Böhtlingk–Roth's PWG (1855) spent its first volume on `a-`
  yet *completed* the alphabet. Terseness finishes, exhaustiveness drowns — report §8.9 + page.

### Changed — PD × DCS coverage: conclusions + completion-horizon analysis (H1336)

- Added §8 Conclusions to
  [reports/PD_DCS_CORPUS_COVERAGE_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_DCS_CORPUS_COVERAGE_2026.md)
  and a conclusions block to the `/tools/pd-dcs-coverage` page: at its current
  printing rate (~6 volumes / 6,056 pp in 50 years, 1976–2026, still inside the
  letter `a`), the Poona Dictionary completes in **~250 years (≈ 2280)** against a
  ~37-volume plan. Deep comparison — an **arithmetic** dictionary (~121 pp/yr, flat)
  against a **geometric** corpus (DCS +4.45 %/yr, doubling every ~16 yr): the residue
  is a moving front, not a permanent deficit. Recommendation: feed the corpus (digitise
  PD's high-frequency residue) rather than wait centuries for the dictionary.
- Added §8.5 (report) + a benchmark block (page): PD's frontier `apaca-` located inside
  the finished AP/PWG/MW headword lists. PD has reached only **4–6 % of the alphabet**
  (MW 4.1 %, PWG 4.3 %, Apte 6.1 %) yet its `a-`…`apaca-` alone (104,959 lemmas) already
  holds **as many entries as the entire PWG** and 54 % of all MW — PD is **13–23× denser**
  than any completed dictionary. Two-speed horizon: at 121 / 200 pp/yr PD finishes ~2284 /
  ~2182 (37-volume plan) or ~3211 / ~2744 (current density held). Scope dominates rate.
- Added §8.6–8.8 (report) + milestone/league blocks (page): **milestones** — PD clears the
  short vowel `a` only ~2094, all vowels ~2179, mid-dictionary (at `p`) ~2594; **extra metrics**
  to count (per-letter workload, editor-generations ~8.6–40, DCS catch-up date); and the
  **long-dictionary league table** (PWG 23 yr · OED 71 · CAD 90 · Grimm 123 · SAOB 130 · WNT 134
  · TLL ~156 · **PD ~308⁺, still in `a`**) — no dictionary ever finished took >~180 yr; PWG did
  all of Sanskrit in 23. PD is on course to be the longest lexicographic project in history.
- Added §8.9 (report) + `a`-analysis & expanded league (page): **is `a` the hardest letter?**
  By initial-letter count `a` is only 4th in MW/PWG (`s`>`p`>`v`>`a`) but **1st in Apte (14.3 %)**
  — the privative/samāsa intuition holds in the compound-heavy tradition; PD's hardest letters
  (`s`,`p`,`v`) are still ahead. Expanded the peer table into **Sanskrit/Indo-Aryan** (WIL, GST,
  PWG, PW, MW, KEWA, EWA) vs **century-long giants**: seven Sanskrit dicts finished in 10–27 yr
  (PW: 151,349 lemmas in 10), while **Goldstücker's 1856 remake of Wilson died in `a` at 6,761
  entries** — PD is that project reborn at ~16× density. Per-letter chart added.
- Quantified the samāsa question: **83 % of MW's `a`/`ā`-entries (19,601 of 23,590) are
  dash-marked compounds**, only ~17 % simple stems — `a` is a letter of combinations, not roots.
  Added **BORI's Prakrit dictionary** (CDPL) to the comparison: same city (Pune), founding editor
  A. M. Ghatage *also edited PD*, started 1988 (younger than PD) yet already `a`→`ujjhittu` (past
  all vowels, ~33,600 lexemes, bounded ~90k plan, finish ~2090) — a natural experiment showing a
  Sanskrit-family dictionary finishes only if it bounds its scope.
- Added **KOW (Kossowicz 1854)** to the comparison (report + page): a partial Wilson-based
  Sanskrit→Russian dictionary of 13,488 entries **arranged in Russian (not Sanskrit) alphabetical
  order** and left unfinished — so it is neither a death-in-`a` nor comparable on the
  Sanskrit-letter axis (verified against `SanskritLexicography/literature/kos_01.txt`). Only
  Goldstücker (exhaustive) died in Sanskrit `a`; PWG (first vol `a-`) completed. Added
  §8.10 + a page section on **[TamiLex](https://www.tamilex.uni-hamburg.de)** (Hamburg): the
  born-digital, corpus-integrated, non-alphabetical paradigm that *retires* the print-fascicule
  model — differs from PD in kind, not speed; it is for Tamil what §8.4 recommends for Sanskrit
  (DCS + a lexical layer). TamiLex exact figures pending (site returned a transient error).

## [0.3.0] - 2026-07-20

### Added — PD × DCS corpus coverage (H1336)

- First-ever measurement of what share of the **Poona Dictionary**'s source
  canon the **Digital Corpus of Sanskrit** covers, for PD's published letter-`a-`
  volumes (107,630 entries, 398,359 citation occurrences). New page
  **`/tools/pd-dcs-coverage`**, report
  [reports/PD_DCS_CORPUS_COVERAGE_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_DCS_CORPUS_COVERAGE_2026.md),
  and data under [data/pd/](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/pd)
  (`pd_siglum_families.tsv`, `pd_dcs_text_crosswalk.tsv`, `pd_dcs_metrics.json`).
- Headline: DCS is **25 % PD-citation-weighted** but **78 % DCS-token-weighted** —
  it holds the archaic/classical core (Mahābhārata, Rāmāyaṇa, Vedas) PD leans on,
  but only ~118 of ~2,445 distinct works PD cites, missing the purāṇic,
  lexicographic and classical-kāvya breadth (residue is 75 % of PD's primary
  citation mass). DCS's 2021→2026 growth was concentrated in exactly PD's Vedic
  core (+3.8 pp token-weighted coverage). Scripts
  `scripts/pd_extract_sigla.py`, `scripts/pd_dcs_crosswalk.py`. Anchors on DCS's
  bounded 276-text inventory so every siglum carries an adjudicated `match_type`.

### Changed — review sheets on the 19-07-2026 org standard (V1–V8)

- `scripts/build-review-sheets.py` now requires the review-sheet emitter at
  **>= v0.3.1** (the [19-07-2026 standard](https://github.com/sanskrit-lexicon/csl-pyutil/releases/tag/v0.3.0)
  ratified from the h178_da vote, plus its light-mode contrast fix) and turns on **V3** copyable id chips, **V6**
  taller note boxes, and a **V8** save-path banner on all four sheets, plus
  **V4** clickable card headers on the two packets that carry real source URLs
  (xref edges → `csl-orig` lines, SKD units → `skd.txt` lines). All four sheets
  regenerated; `npm run test-review-decisions` and `npm run validate-review-reports`
  stay green.
- **V1/V5 rating and V7 Cyrillic highlighting are deliberately not applied**,
  with the reasoning recorded in the generator's module docstring: every
  csl-atlas sheet is a categorical label decision (no scale to score), and the
  content under judgement is Sanskrit/IAST and Latin class labels — the only
  Cyrillic is identical instruction chrome on every card.

### Fixed

- `requirements-review.txt` pinned the emitter at v0.2.0. The pin now names the
  v0.3.0 commit — specifically v0.3.0 plus [csl-pyutil#5](https://github.com/sanskrit-lexicon/csl-pyutil/pull/5),
  a `__version__`-string fix this port surfaced: the 0.3.0 release still
  reported `0.2.0` from `csl_pyutil/__init__.py`, so the `REQUIRED_EMITTER_VERSION`
  equality guard here could not express "require the standard" at all.
- **Emitter pin bumped to v0.3.1; the version guard is now a minimum, not an
  equality.** The old `REQUIRED_EMITTER_VERSION = "0.3.0"` `!=` check hard-failed
  against any newer emitter — including [csl-pyutil v0.3.1](https://github.com/sanskrit-lexicon/csl-pyutil/releases/tag/v0.3.1),
  which carries the light-mode contrast fix (dark-only sheets rendered the note
  box white-bg/light-text — invisible — in a light-mode browser). `requirements-review.txt`
  now pins the v0.3.1 commit and the guard uses `MIN_EMITTER_VERSION` with a `>=`
  comparison, so future emitter patch releases no longer break generation.

## [0.2.0] - 2026-07-17

### Stabilization release

- Added `npm run regen-review-artifacts` and `npm run verify`; CI and Pages now
  run the same deterministic, clean-tree release contract.
- Regenerated the R2, H5, H4, and xref review evidence, retaining all human
  review fields and canonical `csl-orig/main` source links.
- Pinned Node 20/npm 10 and Observable Framework 1.13.4; refreshed compatible
  transitive dependencies and documented the remaining development-only low
  advisory.
- Established `docs/ROADMAP_2026_2027.md` as the governing roadmap and archived
  completed/superseded roadmap documents.

### Earlier unversioned work included in this baseline

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
