_Created: 31-05-2026 · Last updated: 08-09-2026_

# Changelog

All notable changes to csl-atlas are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/). Dates are ISO.

## [Unreleased]
<!-- entries land in changelog_queue/ -- appended via tools/changelog_queue_consume.py, consumed by cut_release.py at release-cut (H3355); direct bullets here are hook-blocked -->

## [0.21.4] - 2026-10-30

# PD M1/M2 annotation packets — 29-10-2026
- **M2 complete:** frozen stratified 50-row blank-siglum packet, all rows checked against 26 printed page images: 46 dependent commentaries, 2 cross-references, 2 unmarked works, 0 uncertain. Frame and per-record decisions are separate artifacts.
- **M1 annotator B complete:** frozen 200-row siglum→work frame (100 ordinary, 40 shared-siglum, 40 `vision-low`, 20 AOB-join) and an independent printed-page reading pass: 194 confirmed, 5 `wrong_work`, 1 `wrong_siglum`, 0 ambiguous. These are B decisions, not gold and not registry edits.
- **Reliability fence:** annotator A is absent, so `kappa: null` and `adjudicated_rows: 0`; no agent-coded-twice κ is claimed. The κ calculator refuses missing, partial, or ID-mismatched passes.
- **Checks:** `python3 scripts/pd_blank_siglum_adjudication.py --check --complete` and `python3 scripts/pd_siglum_work_m1.py --check --complete` green; `python3 scripts/pd_shared_work_registry.py --check` green (registry unchanged); `/opt/homebrew/bin/python3.13 -m pytest tests/forensic/test_pd_method_ladder_annotations.py -q -p no:cacheprovider` → 4 passed.
# PD locus fields verified and extended (H7458/C2)
- Materialized **391,444** well-formed `(siglum, locus)` pairs (356,478 direct + 34,966
  continuations) across **105,177 / 107,630 entries = 97.72 %**. Added
  `pd_locus_fields.tsv`, `pd_locus_coverage_by_entry.tsv`, `pd_locus_rejections.tsv`,
  `pd_locus_fields_summary.json`, builder/checker, 14 hand-derived controls, C2 report and
  dataset/agent registration. All 28,446 remaining H6949 markers reconcile to named diagnostic classes;
  53 continuations stay unassigned. H6949/C1 artifacts and aggregates are unchanged.
  Independent Codex Sol (`gpt-5.6-sol`) verification: PASS; PR #666.
## [0.21.3] - 2026-10-29

# PD KoshaSHRI fixture dataset registration (H7316)
- **PD KoshaSHRI fixture dataset registration (H7316).** Registered the exact H7316 dataset
  paths `data/pd/pd_koshashri_entries.tsv` and `data/pd/pd_koshashri_citations.tsv` across
  the repository and estate surfaces. Added per-file metadocs with schemas, rights, provenance
  and regeneration commands; linked the fixture from the root README and agent orientation;
  recorded the sync rule that adapter or exporter changes regenerate both TSVs and rerun
  `--check` plus offline tests in the same PR. The all-rights-reserved full source response
  remains local and uncommitted. Dataset bytes and canaries are unchanged from v0.21.2 / PR #653.

## [0.21.2] - 2026-10-29

# PD KoshaSHRI fixture TSV exports (H7316)
- Recovered the public single-entry `agni` response and the 27-10 adapter from
  local evidence, then added the deterministic fixture exporter and two TSVs:
  one entry and 1,400 citation-reference rows. The export preserves all 29
  meanings, the first meaning's 242 citation texts → 248 reference rows,
  hierarchical sense paths, one nested vocable, the volume object and the
  `<s<small>` source defect. Exact `ṚV.` resolves through H7296 to
  `PDW-ecd09ac913`; all other works stay unresolved. Added five offline tests,
  a changed-canary refusal, generation report, data/pd README row and a rights
  addendum. The restricted full JSON is not committed; there is no bulk import,
  new work ID, independent-witness claim or csl-orig edit.

## [0.21.1] - 2026-10-29

- **PD licence-envelope parity in two generators.**
`pd_canon_ledger.py` and `pd_aob_sigla_reconciliation.py` now emit the shared
`license` / `licenseUrl` fields through `scripts/lib/dataset_meta.py`, so their
`--check` modes no longer erase the licence stamp added by the dataset-wide
licence backfill. The canon ledger's input hashes are regenerated against the
current licensed inputs. Both PD parity checks, the AOB selftest and the full
dataset licence validator pass.

## [0.21.0] - 2026-10-24

- **H5302 (Opus 5 `claude-opus-5[1m]`) — per-dataset licence matrix: every `data/` family gets a source, a rights basis, a proposed licence and an exception flag.** New [docs/DATASET_LICENCE_MATRIX.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/DATASET_LICENCE_MATRIX.md) covers all 14 families (13 directories + the `data/` root group). Upstream licences probed live in the local clones, not quoted from memory: `csl-orig`, `csl-guides` and DCS are all **CC BY-SA 4.0**, so ShareAlike propagates through every dictionary-derived family and **CC BY 4.0 is clean for exactly two things** — [data/schema/](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/schema) and [data/dictionary_inventory.csv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/dictionary_inventory.csv) (bibliographic facts). Two 🔴 exceptions: **E4** — AMAR's licence is stated three different ways across four surfaces (`AMAR/LICENSE` is GPLv2, its README and CITATION.cff say CC-BY-SA-4.0, and the atlas's own [kosa_model_measures.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/kosa_model_measures.json) records a fourth reading, GPL-3.0, which has propagated into `paper_kosha_macrostructure.md`, `src/paper/kosa-macrostructure.md` and `EMBEDDING_RETRIEVAL_LANE_PLAN.md`); **E7** — the Poona Dictionary source (`PD_TXT`, never committed) has no verified rights statement, and `pd_siglum_raw.tsv`'s three sample contexts per siglum are the only committed excerpts of a rights-unverified work. Four 🟠 conditions recorded (e-texts measured-not-redistributed in `data/forensic/`, Argos MT provenance, Patel 2016 label attribution, scan-metadata-vs-scan-images, MUDIDI schema shape) plus three metadata defects (DCS recorded as "CC BY" where upstream is CC BY-SA 4.0; wrong AMAR upstream repo name; 109 of 130 data JSON files and all 57 CSV/TSV/Newick files licence-silent). CONTRADICTIONS §17's Zenodo ruling is applied with its condition stated: a repo-level deposit stays safe only while the tracked tree redistributes no source dictionary text — true today. Coverage numbers are reproducible via new [scripts/audit_dataset_licence_keys.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/audit_dataset_licence_keys.py). **Proposal only** — no data file, `LICENSE`, `CITATION.cff` or `.zenodo.json` was edited. Part of epic E014.
- **Zenodo first-DOI release prep: release v1.0.0 notes + cold-readable checklist + metadata creator fix (H5304, 24-09-2026, OxAlpha `opencode/z-ai/glm-5.3-flash`, [#472](https://github.com/sanskrit-lexicon/csl-atlas/pull/472)).** Everything up to the Zenodo button, nothing published. [`.zenodo.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/.zenodo.json) creator `Gasūns, Mikhail` → `Gasūns, Mārcis` (CITATION.cff and every repo byline say Mārcis; `Mikhail` appeared nowhere else) plus Gasūns' ORCID `0000-0003-4513-884X` mirrored from CITATION.cff — the official Zenodo legacy creator schema supports `orcid`. New release notes [`docs/releases/v1.0.0.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/releases/v1.0.0.md) (house format of the v0.2.0 notes, which reserved the `v1.0.0` tag): what ships with record counts verified live from the committed data — 43-dictionary coverage layer over 1,495,459 CDSL v02 records (~384 MB), 43-dictionary headword census of 1,495,422 `<L>` entries (the citation-register census's 44 includes the later-snapshot `nmmb`), citation registers over 44 dictionaries (1,517,609 `<ls>` citations, 66.8% locator, 113,113 inline-iti, citation graph 912 nodes / 1,701 edges), 10-dictionary etymology oracle (67,172 rows, 64,896 rooted headwords), the F1–F8 forensic suite at its pinned `csl-orig` revision — plus build commit `bbca791` with a stamp-at-tagging instruction, and the drafted `v1.0.0` annotated-tag text. New [`docs/ZENODO_FIRST_DOI_CHECKLIST.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/ZENODO_FIRST_DOI_CHECKLIST.md): ten cold-readable copy-pasteable steps (sync `package.json`/`CITATION.cff`/`.zenodo.json` to `1.0.0` → re-validate → stamp build commit → commit/tag/push → connect Zenodo (account-holder-only OAuth) → create the release → watch the mint → publish → backfill the DOI → caveats), each with its skip-consequence stated. Validation evidence: `CITATION.cff` VALID against the official CFF 1.2.0 schema (schema's own YAML-date cast rule), `.zenodo.json` VALID against the official Zenodo legacy deposit schema `zenodo/zenodo zenodo/modules/deposit/jsonschemas/deposits/records/legacyrecord.json` with the single tolerated deviation of `version` (documented Zenodo deposit field, missing from that upstream schema file); `upload_type: software`, `isSupplementTo`/`isDerivedFrom` relations and `scheme: url` all in schema enums. `publication_date` deliberately not added: the GitHub–Zenodo integration stamps the release date and `.zenodo.json` values override defaults (zenodo/zenodo `modules/github/api.py`), so a hardcoded date would mask the real one. No version bump in the metadata, no release/tag created, no data regenerated, no `csl-orig` content.
- **H5306: ORCID gap census across the four ATLAS repos (24-09-2026, OxAlpha `glm-5.3-flash`).** New `docs/ORCID_GAP_CENSUS.md` plus the reproducible `scripts/orcid_gap_census.py` list every author/contributor entry without an ORCID iD in `CITATION.cff`/`.zenodo.json` of csl-atlas, csl-standards, VisualDCS and csl-observatory at pinned revs (all == live origin/main at census time): 7 person entries missing an iD — csl-atlas CITATION.cff L20 (Funderburk, commented-out TODO) and L21 (Andhrabharati), csl-atlas .zenodo.json L9–11 (all three creators, incl. a pre-existing Mikhail-vs-Mārcis name discrepancy flagged not fixed), csl-standards CITATION.cff L6 (sole author; iD cross-attested in 3 sibling repos), VisualDCS references[] L41 (Hellwig, third-party, optional) — csl-observatory zero gaps. No iDs invented or looked up; each row names the exact file and line to fix.
- **H5309: review-pool kappa report tool — Cohen's κ between two double-keyed decisions files (24-09-2026, OxAlpha `zai-coding-plan/glm-5.3-flash`).** New
  [scripts/review_pool_kappa.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/review_pool_kappa.py)
  joins two review-sheet decisions.json exports (shared emitter payload: `{sheet_id, items:[{id, decision, note}]}`,
  decision ∈ approve/reject/defer or null) of the same packet on item id and reports raw agreement, Cohen's κ with a
  95% asymptotic-normal CI (Fleiss SE, clipped to [-1, 1]), the confusion table (A rows × B columns) and the
  disagreement rows with both notes for adjudication. Degenerate inputs are reported honestly, never fudged: the
  single-class case (pe = 1) carries `cohenKappa: null` with an explanatory note while raw agreement stands; items
  seen by only one annotator or unvoted by either are excluded from κ and listed under coverage warnings; unknown
  decision values and duplicate ids fail loud (exit 2). 15 stdlib-unittest fixture tests in
  [scripts/test_review_pool_kappa.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/test_review_pool_kappa.py)
  cover the handoff's three required fixtures — perfect agreement (κ = 1, CI [1, 1]), chance level (κ = 0 on a
  balanced 2×2), degenerate single class — plus join/coverage semantics, schema rejection and a CLI end-to-end smoke.
  Run via `npm run review-pool-kappa -- A.json B.json` / `npm run test-review-pool-kappa`. Prior art consumed:
  scripts/lexico/root_agreement_kappa.py (marginal pe, Landis-Koch bands) and csl-observatory obs_t_gold.py (paired
  κ + confusion Counter); schema aligned with scripts/validate_review_decisions.py. Companion to the E014
  review-pool double-keying chain (H5307/H5308) and the H5312/H5313 obs-t second-annotator units.
- **Recruitment post draft RU for the review pool (H5311, 24-09-2026,
  OxAlpha opencode `z-ai/glm-5.3-flash`,
  [#475](https://github.com/sanskrit-lexicon/csl-atlas/pull/475)).** New
  [docs/REVIEW_POOL_RECRUITMENT_DRAFT.ru.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_POOL_RECRUITMENT_DRAFT.ru.md) —
  draft call for 5–10 student reviewers over the three human-gated packets;
  draft only, nothing sent or posted. Time-per-packet derived from live
  packet sizes probed 24-09-2026 (R2 5 packets / 70 rows, H4 105, xref 50;
  rows × 1–2 min); credit wording parked behind the H2545 human gate; the
  R2 «×10 vs 70 rows» wording delta vs H5307/H5308 documented.
- **H5332 (Opus 5 `claude-opus-5`) — lemmatisation policy census: what counts as a lemma in each of the seven narrative dictionaries.** M1/M2 measured headword *promotion* but never the prior question — which form of a paradigm carries the entry. New [scripts/lexico/m12_lemmatisation_policy.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/m12_lemmatisation_policy.py) (`npm run build-lemmatisation-policy`, stdlib only, ~20 s, deterministic) states a thresholded policy per dictionary × word class for MW, PWG, PW (PWK), AP, WIL, SKD, VCP, over `csl-orig@f4c08c57`, Whitney's 853 testable roots and the 83,239-lemma DCS spine, and writes [data/lexico/lemmatisation_policy.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/lemmatisation_policy.json) + a 28-row [verdict table](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/lemmatisation_policy_classes.csv) + an [exceptions CSV](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/lemmatisation_policy_exceptions.csv) (off-policy key shapes, roots with no headword, the minority side of each nesting verdict, absent DCS lemmas sampled per frequency band). Findings in [docs/LEMMATISATION_POLICY_CENSUS_24-09-2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/LEMMATISATION_POLICY_CENSUS_24-09-2026.md): **three families that are not the collation families** of H5331 — the Petersburg pair (PWG/PW: stem keys, root-form verbs, every compound and derivative its own head), MW and AP (nested macrostructure: MW nests 91.7 % of compound-like and 95.7 % of derivative-like headwords; AP nests 54.9 % of compounds but only 3.9 % of derivatives), and SKD/VCP/WIL (no root layer — 14.9–18.6 % of Whitney's roots are exact headwords against 83.5–94.0 % in the other four; their root material sits in `derived_only`, 577–632 roots, because the key carries anubandhas or a preverb). **SKD keys citation forms** (67.2 % of level-1 keys end in ḥ or ṃ, the gender split of the nominative), AP too at 28.3 %, while VCP is a stem dictionary at 0.15 % — the two indigenous dictionaries agree on the alphabet and disagree on the lemma. The **DCS spine is read stratified by frequency band**, and the band-1 (hapax) spread — MW 52.7 % down to WIL 10.6 % — is five-fold where band 5 agrees within 71–97 %, so a flat coverage claim about a dictionary is a claim about bands 4–5 only. Limits stated in §6 and carried in the JSON: the finite-form test is thematic-only (no guṇa/vṛddhi), nesting is measured on `<e>` records and five dictionaries carry none, and the self-referential compound/derivative tests go blind in a citation-form dictionary (SKD's 41 derivative hits are an artefact, not low productivity). 12 hand-derived pins in [tests/forensic/test_m12_lemmatisation_policy.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_m12_lemmatisation_policy.py). Part of epic E014.
- **H5333: usage and register labels — comparative census across the nine narrative dictionaries (24-09-2026, OxAlpha `opencode/z-ai/glm-5.3-flash`).** New `scripts/lexico/m12_usage_register_labels.py` (`npm run build-usage-register-labels`) extracts every usage/register label from the tagged markup (`<ab>`, `<lang>`) of MW, PWG, PW, AP, WIL, SKD, VCP, ARMH and ABCH at `csl-orig@f4c08c57`, normalises the raw strings to one 12-label vocabulary with the mapping table published as `data/lexico/usage_register_labels_map.csv`, and reports per-dictionary counts and per-1,000-records rates in `data/lexico/usage_register_labels.json` + `usage_register_labels_counts.csv`. Headlines: 5,223 tagged occurrences, all in the five European-medium dicts (the four Sanskrit-medium kośas tag none); VEDIC is 59.8 % of the stock but filed in `<lang>` by MW/PWG/PW and in `<ab>` by AP, whose Vedic rate (21.09/1k records) is ten times MW's (2.14/1k); LEXICOGRAPHERS_ONLY exists as a tagged label in PWG alone (41× `Lexicogrr.`/`Lexicogr.`/`Lexicc.`); PWG alone tags chronological fine-grain (`klass.`, `nachved.`, `liturg.`); the net-untagged residue is 87 occurrences estate-wide, so the tag layer captures ≈98 %. Methods page `docs/USAGE_REGISTER_LABELS_CENSUS_24-09-2026.md`, hypothesis row USAGE-LABEL, hand-derived pins in `tests/forensic/test_m12_usage_register_labels.py`.
- **H5338: maintainer runbook for atlas data builds — `docs/MAINTAINER_RUNBOOK_DATA_BUILDS.md` (24-09-2026, OxAlpha `opencode/z-ai/glm-5.3-flash`).** Bus-factor-one fix written by actually performing a clean-clone build at `78fb3b2` (v0.19.5): prerequisites (Node engines 20.x vs v26.7.0 verified green, the macOS bare-`python` gap and the venv fix, hardcoded sibling checkouts `../csl-orig/v02` + `../SanskritLexicography`, npm install-scripts gate), the measured core chain (`sync-site-data` 0.19 s / 54 files; **`npm run verify` 1 m 45.6 s PASS** = 369 JS tests 0.61 s + 7 python tests + 12 validators + double deterministic regen + `observable build` with 21 links validated + prod-dep audit + clean-tree gates), the rebuild-commit cycle with representative measured pairs (heap-sat 0.98 s build / 0.93 s validate; mw-depth 1.24 s / 0.10 s), a validator failure-mode table with the two Heaps failures induced live (stale site copy → `sync-site-data`; rebuild cross-check disagreement → rerun build), provenance-pin semantics of `*.source.json` sidecars, the release flow (changelog_queue → cut_release.py → CHANGELOG/CITATION.cff/.zenodo.json, v0.19.5 as the worked example; `stardict-dist/` as a release artifact, never committed). No build scripts or data changed — docs only.
# H5318 — Learner reading layer v1: the joined dataset incl. survival-ranked senses (25-09-2026)
- **H5318 (OxAlpha, opencode/z-ai/glm-5.3-flash) — learner reading layer v1: the four-layer joined dataset, validator, tests and page.** [scripts/build-learner-index.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-learner-index.mjs) now closes its own v0 honest-scope sentence: `learner-index.json` (schema 2.0.0, 52,957 cards) joins the v0 frequency + dictionary-coverage base with the three missing layers of [docs/LEARNER_LAYER_V1_SPEC.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/LEARNER_LAYER_V1_SPEC.md) — the **survival-ranked senses** from the P2 panel (28 lemmas, threshold ≥ 0.15; each sense carries `t`/`sv`/`ov`/`e`/`pos`/`ci` with the edge always attached and the sense **text re-harvested from the ancestor articles by re-running the P2 extraction**, a single shared implementation now that `extractSenses`/`loadDictByStem` are exported from `build-r2-h2h3.mjs`), **Whitney root(s) + gaṇa** (`roots.csv` + `root_class.csv`, all homonym roots shown together never picked, gaṇa only from `whitney_no` or absent — never inferred), and the **VisualDCS paradigm link** pinned fail-closed at release `vdcs-learner-v1-20260809` (commit 6d19eed1, per-payload lf-canonical sha256 verified in [scripts/lib/learner-join.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/learner-join.mjs); digest mismatch or unknown `contractVersion` aborts the build — spec §9.2/§9.3). Cross-file paradigm collisions (nominal lemma AND verb root on one IAST string) resolve to the highest-tokens contract with the loser disclosed in `alt` (§7.3 generalized), homonym-split warnings carry the advisory-and-incomplete label (333 cards, 400 of 9,839 candidates shipped), every card gains a first-class **completeness tier A–D** and every missing layer a **reason code from the closed §9.1 vocabulary** rendered on the page. New fail-closed [scripts/validate-learner-index.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/validate-learner-index.mjs) (`npm run validate-learner-index`, wired into `verify`): pins the §8 tier distribution within tolerance, recomputes `counts.coverage` from the entries, and **fails if any survival rank lacks its edge** or the honest-null caveat goes missing (§9.4/§11.2). Page [src/tools/learner-reading-layer.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/learner-reading-layer.md) renders the tier chips, the evidence disclosures, the survival caveat verbatim and the named-absence list — the band-0 tier-D majority card (`ABAti`, 23,243 cards) is the designed worst case, legible with its absences, not the showcase. Measured coverage vs the spec estimate (spec §8, 24-09 measured → this build, 25-09, after the H5423 lemma-set refresh +23 lemmas): A 28 = 28 ✓, B 541 = 541 ✓, C 16,510 ≈ 16,508, D 35,878 ≈ 35,857, nominal 16,452 ≈ 16,450, verb **778 = 778** ✓, Whitney root 690 = 690 ✓ (gaṇa 586 = 586 ✓, homonyms 61 = 61 ✓), survival 28 = 28 ✓ (0.053%), homonym warnings 333 ≈ 332, **all-four 0 = 0 — the spec's headline survives**; ~32.2% of cards (A+B+C 17,079/52,957) gain ≥ 1 layer over v0, against the spec's ~32% estimate. [test/learner-index.test.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/test/learner-index.test.mjs) 16/16 (rank order, homonym show-all, tokens resolution, digest fail-closed, threshold rejection, spec-shaped 52,934-card validator pass + 6 mutations); the 3 pre-existing H4/H5 packet failures on clean main (local csl-orig drift, cf. 0.19.8) are unchanged by this PR. VisualDCS payloads consumed, never re-derived; nothing under `csl-orig` read beyond the same P2 article bodies, nothing committed from it. Part of epic E014.
# H5319 — Learner reading layer v1: the public page smoked + CSV export (25-09-2026)
- **H5319 (OxAlpha, opencode/z-ai/glm-5.3-flash) — the learner reading layer v1 page is browser-smoked at desktop and mobile widths and gains the spec §9.5 card-table CSV.** [docs/LEARNER_LAYER_V1_SMOKE_25-09-2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/LEARNER_LAYER_V1_SMOKE_25-09-2026.md) records the Playwright pass over [src/tools/learner-reading-layer.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/learner-reading-layer.md) on the v1 payload (52,957 cards, pin `vdcs-learner-v1-20260809`): the stop condition is met — the page renders cards for a **high** lemma (`agni`, band 5, tier C), a **mid** lemma (`ābhāsvara`, band 3 via the band filter, sample "120/8,096", tier mix C 93 / D 27) and a **rare** lemma (`ābhāsura`, band 1 hapax, tier D), the trust block is filled with the v1 text (band-0 wording, 28-lemma P2 panel at threshold ≥ 0.15, the not-significant within-edge test, gaṇa-never-inferred, the VisualDCS pin), and the spec §11.3 worst case renders legible — band-0 tier-D `ābhāti` with coverage 5/7, its MW source link and 5 named absences led by `not-in-dcs` ("uncorroborated by this corpus, NOT 'unused'"); the tier-A canary `āśraya` shows 5 of 40 survival-ranked senses all ✓ with the threshold and the per-sense-only caveat. Mobile 390×844: 0 px horizontal overflow, trust block single-column, cards full-width. New: the page's **CSV export** ([src/lib/csv-download.js](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/lib/csv-download.js) house helper) — exports the **currently shown** lookup/band-filter view at click time (18 fixed columns incl. paradigm stable id, senses/survived, threshold, absences; BOM'd UTF-8 for IAST in Excel; filename reflects the active filter, e.g. `learner-cards-band3.csv`), click-captured in-browser and value-verified on the tier-A row. Checks: `npm run validate-learner-index` PASS (tiers A 28 / B 541 / C 16,510 / D 35,878 within tolerance), `node --test` 401 pass / 3 known pre-existing H4/H5 packet failures (unchanged), 16/16 learner-index tests. **Stacked delivery:** at execution the dataset was green on `origin/h5318-drain` (PR #521, verifier PASS) but not yet merged — `sanskrit-lexicon/*` is foreign-owner PR-only for drains — so this PR stacks on #521 and merges after it. Part of epic E014.
- **H5792: duplicate test basename unblock — `scripts/lexico/test_review_pool_kappa.py` renamed so `pytest` collects all 178 tests again (03-10-2026, OxAlpha `zai-individual-coding-plan/glm-5.3`).**
  [scripts/lexico/test_lexico_review_pool_kappa.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/test_lexico_review_pool_kappa.py)
  is the renamed file (was `scripts/lexico/test_review_pool_kappa.py`, H5483, 25-09-2026): it had introduced a
  second `test_review_pool_kappa.py` basename into a repo with no test
  packaging (`__init__.py` exists only under `scripts/L0/`), so bare `python3 -m pytest` from the root hit
  pytest's import-file-mismatch after 162 collected tests and aborted — CI never noticed because
  [test.yml](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/.github/workflows/test.yml) scopes pytest
  to `tests/forensic`. The newcomer yields to the H5309 incumbent
  ([scripts/test_review_pool_kappa.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/test_review_pool_kappa.py),
  24-09-2026); the new name's `lexico` prefix follows the directory's `validate_lexico.py` naming. Test content
  unchanged — both
  kappa test files load their sibling module via location-relative `importlib`, so no import edits were needed.
  References updated: [scripts/verify.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/verify.mjs)
  (`scripts.lexico.test_lexico_review_pool_kappa`) and
  [package.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/package.json) — the rename also fixed a
  latent duplicate JSON key: `test-review-pool-kappa` was declared twice (npm's last-wins parsing silently ran
  only the top-level module); the lexico entry now lives as its own `test-review-pool-kappa-lexico` key.
  Receipts: `python3 -m pytest --collect-only -q` → 178 tests collected, 0 errors (before: 162 collected,
  1 collection error, interrupted); `find -name 'test_*.py' -exec basename {} \; | sort | uniq -d` → empty;
  full suite `python3 -m pytest -q` → 178 passed (0 pre-existing reds: pristine origin/main baseline was green
  with the collision file ignored, 163 passed, plus 15 lexico tests via unittest). Closes H5792.
- **Nightly bug hunt csl-atlas 07-10-2026 (OpenCode GLM `zai-coding-plan/glm-5.3-flash`, MG ruling 26-09-2026).** [BUGHUNT-FINDINGS-csl-atlas-07.10.2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/BUGHUNT-FINDINGS-csl-atlas-07.10.2026.md) — 1 HIGH (vendored `sanskrit-util.js` a month stale vs canonical v0.12.0, missing the H3975 medial-anusvāra `form_key` fold; load-bearing in the H4 crosswalk joins — auto-fixed in the same pass), 2 MEDIUM (drift guard skips in CI so drift ships green; known environment-coupled H5/H4 packet tests vs a stale local `csl-orig`), 1 LOW (ALL-CAPS lookup input gets no lower-case candidate). Suite at hunt time: 409 tests / 405 pass / 4 fail (the 4 = the HIGH + the 3 known-coupling). No secrets, no dead package.json refs; reseed lock, git_ops, cologne-links and sw.js verified clean.
- **Nightly bughunt fix: re-vendor `sanskrit-util.js` v0.12.0 — the H3975 medial-anusvāra `form_key` fold reaches the atlas (07-10-2026, OpenCode GLM `zai-coding-plan/glm-5.3-flash`).** Found by the 07-10 nightly hunt ([BUGHUNT-FINDINGS-csl-atlas-07.10.2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/BUGHUNT-FINDINGS-csl-atlas-07.10.2026.md)): the vendored copy still carried the v0.11.0 `form_key` from `790d3dd0` (re-vendor 04-09-2026, PR #438), while canonical [sanskrit-lexicon/sanskrit-util](https://github.com/sanskrit-lexicon/sanskrit-util) `48052f3` (v0.12.0, 06-09-2026) added `s = s.replace(/[ṃṁ](?=[pbm])/g, 'm')` — medial anusvāra before a labial folds to `m`, so `saṃbhavaḥ`/`sambhavaḥ`-class pairs collide; the atlas's copy sent them to `n` and left the literal `m` alone, so those joins never matched. `slp1_form_key` is load-bearing here ([build-h4-review-packet.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-h4-review-packet.mjs) crosswalk joins, [adjudicate-h4-agent.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/adjudicate-h4-agent.mjs) matching), so the month-long drift made H4 evidence joins diverge from every estate consumer on canonical. Fix is the guard's own documented repair — [src/lib/sanskrit-util.js](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/lib/sanskrit-util.js) re-copied byte-identical from `../sanskrit-util/js/index.mjs` (CRLF-normalized `diff` = 0; exports unchanged; `slp1_norm` untouched, so committed normalized keys are unaffected; no repo test pins the old fold). Verified: `node --test test/lib.test.mjs` 72/72 (drift guard green), consumer suites citation-truncation + cologne-links + learner-index + kosa-model 81/81. Companion finding (report-only): the drift guard skips in CI without the sibling checkout, so a digest-pin is the follow-up that makes CI see this class.
- **ACL-uplift execution agenda §8 adopted + U1 executed: A04 gets chance-corrected κ, reviewed-claim markers and its build commit (10-10-2026, ZCode GLM `account:zai-individual-coding-plan/GLM-5.3`).** MG ruling 10-10-2026 («да» to the acl-uplift proposal) turns the paper queue into a discipline lane: [ATLAS_RESEARCH_AGENDA.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/ATLAS_RESEARCH_AGENDA.md) gains §8 — the ranked U1–U7 table (metrics markers, A02/A03/A05/A06 build commits, review-pool annotator validity, benchmark-fit reporting, data statements, A68 venue @DECIDE) with the two-gates principle, live-verified-citations rule and an explicit no-lint-gaming non-goal (the DOI column means **dataset** DOIs; literature cites use anthology URLs). Item U1 landed the same pass in [Uprava PR (H6386)](https://github.com/gasyoun/Uprava/pull/4659): `papers/A04/paper_indigenous_microstructure.md` §4.4 now reports the chance-corrected agreement that [ROOT_AGREEMENT_KAPPA.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/ROOT_AGREEMENT_KAPPA.md) already computed (mean pairwise Cohen's κ = 0.807 gaṇa / 0.551 pada / 0.533 transitivity, build commit [`f29e06a2`](https://github.com/sanskrit-lexicon/csl-atlas/commit/f29e06a2)), with `[reviewed]` markers naming the machine-reviewed channel and the Artstein & Poesio 2008 norm citation. Scoreboard: the [H5339 lint](https://github.com/gasyoun/Uprava/blob/main/tools/lint_atlas_papers_standing_rules.py) A04 row flips from vacuous (0 markers) to real — κ 2/2 covered, 1 build-commit link, DOI honestly 0 until the v1.0.0 gates clear. Handoff: [H6386](https://github.com/gasyoun/Uprava/blob/main/handoffs/H6386-GLM_Uprava_acl-uplift-a04-kappa_10.10.26.md).
# H6409 — A72 census v1: computed grammatical-abbreviation polysemy across the CSDL canon (10-10-2026)
_Created: 10-10-2026 · Last updated: 10-10-2026_
- **H6409 (OxAlpha-named; executed by GLM-5.3-Flash `zai-coding-plan/glm-5.3-flash` via ZCode, tier-token provenance per H3688) — the hand-collected homograph tables of Gasūns 2006 (EURALEX XII Torino, pp. 773–778) re-founded as a computed census over the full digitized CSDL corpus.** New [scripts/build_abbrev_census.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build_abbrev_census.py) (`npm run build-abbrev-census`) emits [data/abbrev/abbrev_census.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/abbrev/abbrev_census.json) (inventories, unified label table, collision matrix, polysemy, denominators) and the human report [reports/ABBREV_CENSUS_V1_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/ABBREV_CENSUS_V1_2026.md), byte-identical on re-run (stable-`generatedAt` discipline, `CSL_ORIG`/`CSL_GUIDES` env-overridable). Denominators per the H800 lesson: **45 corpus dictionaries parsed, 1,506,391 entries scanned**, 1,037,648 `<ab>` + 776,143 `<lex>` + 55,704 `<lang>` labels counted, 34,765 distinct raw labels; the `<ls>` source-siglum layer (1,517,609 citations) is **reused, not recomputed** — loaded from the committed [data/obs/ls_abbreviation_frequency.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/obs/ls_abbreviation_frequency.json) (H1826, csl-observatory#222) with its sum-equals-register invariant re-run (0 violations). The legend layer is the csl-guides per-dictionary abbreviation dataset (18 of 44 catalogued dictionaries carry machine-readable legends) loaded verbatim with git provenance — prefaces are not re-parsed. **The 2006 class computes**: `M.` is polysemous in 11 senses (Manusmṛiti PWG/LRV, Masculine SHS, Middle CAE, Marut INM…), `P.` in 11 (Parasmaipada AP/AP90/MD/MW, Participium GRA, Passive CAE…), `N.` in 10 (Name AP/AP90/CAE/MW72, Neuter SHS, Naiṣadhacarita AP90, Nalus BOP…), `V.` in 7 (Vocativ GRA, Veda/Vedic MD, Verb SHS, Vikramorvaśīyam AP90…), `c.` carries causal (AE/BUR/GRA) vs case (MW) — and `f.` computes 2006's «and for (Mc)» as MD's «feminine; also = for»; the Petersburg-Wörterbuch synonymy note computes as three competing sigla (`B. R.` MW72, `BR` BHS, `pw` BHS). Comparisons stay on RAW strings (case-sensitive, trailing punctuation kept — the H1076 lesson); expansion equality is casefold+NFC+trailing-period-insensitive. Prior art honoured, nothing rebuilt: corpus read via `parse_cslorig.iter_entries` + `citation_register_gaps.discover_dicts` (the H1826 line, same roster glob as the sibling register artifacts), csl_pyutil.anatomy / H5325 megastructure / H5335 lexicographic-types register cross-linked as different layers; github-first read done (TEI Lex-0 official repo DARIAH-ERIC/lexicalresources `TEILex0.odd` — grammatical info in `gramGrp`/`gram`, typed `usg` labels, values left open; SKOS has no normative GitHub repo, official surface is the W3C SKOS Reference; estate precedent csl-standards pins Lex-0 0.9.5). 11 unittest cases on synthetic fixtures (`npm run test-abbrev-census`); `npm run verify` untouched (two-gates principle). Limits stated in the report: 26 of 44 catalogued dictionaries have no machine-readable legend so the collision matrix is a lower bound, and BOP's mojibake legend source can inflate its sense counts (kept raw, not silently folded). E3 (the 2006 «small classes» normative scheme as controlled vocabulary) is deliberately not touched — this census measures only. Part of paper A72; closes H6409.
_Dr. Mārcis Gasūns_
# H6411 — ABCH f-series rework after verifier round 2 (H5325 FAIL)
H5325's ABCH record mis-mapped the f-series. Verifier round 2 (session 0G4, DeepSeek,
25-09-2026) read all 14 f-pages and found the front matter belonged to other pages; H6411
(10-10-2026) re-read the key pages live and corrected the record:
- `abch.fm.title-sa` moves f02 -> f03 (f02 is the registration notice, read live:
  "Registered according to act XXV of 1867"; "All rights reserved by the publisher.").
- The four-page `prastavana` preface never existed: f03 is the Devanagari title, f04 a
  blank leaf (now `excludedScans`), f05-f06 the introduction's pages 1-2. The component is
  deleted.
- `abch.fm.introduction` moves f07-f11 (5 pp., "unnumbered") -> f05-f10, six pages: the
  first unnumbered, then printed 2-6 (number bands read on f06 = 2, f10 = 6, f12 = 2);
  f10 carries the works list (8. Abhidhanacintamanisilonchhah, 9. Linganusasanam) and
  closes with the editors' signature "Pandit-Sivadatta-Kasinathah".
- f11 re-homed as printed page 1 of the kosa (division title + opening verses 1-3) in
  `excludedScans`; the false `knownGaps` entry "printed page 1 in neither series" is
  removed - printed pages 1-4 sit in the f series (f11-f14), the numbered series runs
  pg05-pg58 = printed 5-58.
- Colophon notes re-checked on the scans: pg57's head reads "6 Samanyakandah" (the kanda
  OPENS at printed 57) and pg58's foot closes the work ("...samaptah || 6 ||") with the
  final verses to 9542 - H5325's "5 Samanyakandah", "colophon closes the kanda at printed
  page 57" and "verses to 1542" were all misreadings (the 1542 drops the leading 9).
- New component `abch.fm.registration` (f02); inventory captions f02-f11 and the guide's
  ABCH row rewritten; the guide's "15 scan sets" count corrected to 13 (3 pilot + 10 new).
Validation unchanged: `validate-megastructure` -> OK - 9 dictionaries, 91 components
(5 ABCH parts: title-en, registration, title-sa, introduction, colophon);
`node --test test/megastructure.test.mjs` -> 9/9.
# ARMH colophon re-read (H5325 record, adversarial pass 11-10-2026)
The H5325 ARMH record mistranscribed two akṣaras of the closing colophon on
printed page 101 (`ARMH_0101.pdf`). A fresh 400 dpi render of a newly fetched
byte-identical PDF shows:
- `भट्ट` for `भद्र` — the author is styled Bhaṭṭa ("Śrī Bhaṭṭa Halāyudha");
- `[अ]नेकार्थ` for `मनोहरा` — e-kāra not o-kāra, क not ह: the kośa-final
  homonym section, not a proper name. The initial अ is faint on the scan;
  the reading is fixed by the unambiguous `नेकार्थ` and the genre.
`armh.bm.colophon` now reads
"इति श्रीभट्टहलायुधकृतायामभिधानरत्नमालायां [अ]नेकार्थकाण्डे पञ्चमं समाप्तम् ॥ ५ ॥"
("Thus ends the fifth, the Anekārtha-kāṇḍa, in the Abhidhānaratnamālā composed
by Śrī Bhaṭṭa Halāyudha"), and the catalogue notes' "fifth, manohara-kāṇḍa"
becomes "fifth, anekārtha-kāṇḍa". Same pass re-derived the ABCH f12-f14 =
printed 2-4 mapping from verse continuity (4-9, 10-15, 16-23, then 24+ on
printed 5) and re-confirmed AP90 `tit_0012` as a blank leaf — all consistent
with the H6411 rework; no ABCH/AP90 record changes.
Validation unchanged: `validate-megastructure` -> OK - 9 dictionaries,
91 components; `node --test test/megastructure.test.mjs` -> 9/9.
# H6459 — A72 validation table: every 2006 claim × computed verdict (11-10-2026)
_Created: 11-10-2026 · Last updated: 11-10-2026_
- **H6459 (OxAlpha-named; executed by GLM-5.3-Flash `zai-coding-plan/glm-5.3-flash` via ZCode, tier-token provenance per H3688; MG 11-10 grill R1.2 Build verdict) — the Gasūns 2006 claim tables validated claim-by-claim against the A72 census, every verdict computed, none hand-tuned.** New [scripts/build_abbrev_validation_2006.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build_abbrev_validation_2006.py) (`npm run build-validation-2006`) transcribes all **111 claims** verbatim from the §2 preamble + §2.1 + §2.2 of the 2006 fulltext (Uprava `research/notes/latin-terms-2006-fulltext.md`; published PDF authoritative) and computes each row's verdict from the committed census payload [data/abbrev/abbrev_census.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/abbrev/abbrev_census.json) (H6409) — emitting the machine table [data/abbrev/validation_2006_claims.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/abbrev/validation_2006_claims.tsv) and the report with the unmappable appendix [data/abbrev/validation_2006_claims.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/abbrev/validation_2006_claims.md), byte-stable (no clock). Denominator line: **12 confirmed / 27 extended / 4 corrected / 68 unmappable**. The computed headline: MW — digitized with legends — carries only `case` for `c.`, so 2006's «conjugation, class (MW)» is **corrected**, while «nom. c[ase] (MW)» confirms at dict level; `int.` is **corrected** (digitized legends carry intensiv/intransitive/intensif, the interjection sense lives on `interj.` in 4 dicts); dict-level confirmations on mapped witnesses: Aṣṭādhyāyī AP90, Ātmanepada AP90, Naiṣadhacarita AP90, `Comp.` = Compound BEN (Bf→BEN), `irreg.` MW — and the Petersburg synonymy note computes: `BR` and `pw` attested with Böhtlingk–Roth legends (BHS), the other seven sigla unmappable with the corpus note (the work itself is digitized as pw/pwg/pwkvn). The **extended** class is the census's polysemy surplus over 2006 (M. 11 senses vs 2, P. 11 vs 9, N. 10 vs 8, `lit.` 6 vs 3, `f.` 6 vs 3, `sc.` 3 vs 1, `red.` 2 vs 1, `pass.` 4 vs 1). Honesty classes per the fail-clause: **U1** label absent from payload (ij, fm., Nm., Ä., the rare §2.2 acronyms), **U2** label attested only as inline ab/lex/lang tokens with no machine-readable legend (`vulg.` 248 tokens pwg/wil, `colloq.` 10 lan, `V`/`S`/`s`/`m`/`litt.`), **U3** sense unattested + witnesses outside the digitized legend set (the long tail of 2006's grammar witnesses — Th, St, Bt, Kn, Hn, Ko… — none digitized), **U4** 2006 states no sense (the «…» row, OCH., AK/EK, aA/aE) — recorded in the appendix, never silently dropped. Witness join encodes only certain code→dict mappings (MW→MW/MW72, Ap→AP/AP90, Bf→BEN, Ln→LAN) and states the rest as outside the legend set rather than guessing; sense matching is a deterministic per-claim regex over NFC-casefolded expansions covering the Latin/German/French surface forms (Aktivum→active, littauisch→Lithuanian, red.→redoubl-/reduplic-); verdict precedence corrected > extended > confirmed, extension = census senses > distinct 2006 senses for the label (computed from the claim table itself). 9 unittest cases (`npm run test-validation-2006`) lock the vocabulary, the spot-check class (V./c./M./P./N. + Petersburg), the corrected flagships, and byte-stable regen; `npm run verify` untouched (two-gates principle, H6409 precedent). Part of paper A72; closes H6459.
_Dr. Mārcis Gasūns_
# H6494 — A68 figure generator: ASCII hyphens + wider fig4 canvas (11-10-2026)
_Created: 11-10-2026 · Last updated: 11-10-2026_
- **H6494 (GLM 5.3 `opencode/zai-coding-plan/glm-5.3`) — upstreams the two figure fixes the A68 ISCLS-9 pack applied privately (H6476, Uprava PR #4781) into [scripts/build_a68_figures.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build_a68_figures.py).** (a) The fig1 title («PD a-volume citation occurrences…») and fig3 subtitle («letter a- volumes») emitted U+2011 non-breaking hyphens, which draw .notdef boxes under rsvg-convert (browsers substitute silently, so every rsvg consumer of the committed SVGs/PDFs was affected) — both label strings now use the ASCII hyphen. (b) fig4's first bar label `144,139 (+140,421)` (x≈686, ~108 px wide) clipped at canvas width 760 — the fig4 canvas is now 830 wide (svg `width` + `viewBox` + bg rect all derive from W, so the fix is self-consistent; the interim hand-patch in the Uprava store had left `viewBox` at 760, horizontally stretching by 830/760 — regen now also corrects that). Values untouched: the re-derivation canary stays 12/12 green (`python scripts/build_a68_figures.py` re-derives every plotted number from `data/pd/*.tsv` before drawing and aborts on drift). Regenerated fig1/fig2/fig3 are byte-identical to the already referee-judged private-store copies; fig4 differs only in the corrected viewBox. Regenerated SVGs stay uncommitted in this repo (paper-priv standing policy, #537) — the published copies live in the Uprava private store, regenerated from this script. Provenance: papers/A68/sweeps/2026-10-iscls9-referee.md gate 3.
_Dr. Mārcis Gasūns_
# H6465 — A72 pedagogy: student label-reading guide as a register usability test (13-10-2026)
_Created: 13-10-2026 · Last updated: 13-10-2026_
- **H6465 (OxAlpha `opencode/z-ai/glm-5.3-flash`, MG verdict 11-10 round-3 card O3: NOW as a register usability test) — the A72 census turned into a student-facing label-reading guide, every row a computed census row.** New [scripts/build_abbrev_label_guide.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build_abbrev_label_guide.py) (`npm run build-abbrev-label-guide`) generates [docs/A72_LABEL_READING_GUIDE.ru.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/A72_LABEL_READING_GUIDE.ru.md) (RU-primary) plus the machine-readable twin [data/abbrev/label_guide_rows.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/abbrev/label_guide_rows.tsv) from the committed census payload [data/abbrev/abbrev_census.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/abbrev/abbrev_census.json) (H6409, snapshot 2026-10-10T19:00:00.879Z): 21 teaching labels across six sections — gender (`m./f./n./mfn.` — mfn. attested in MW as «masculine, feminine and neuter; or = adjective»), pada (`P./A./U.`), verb class (`c./D./med.`), participles (`p./pp.`), the single-letter title class (`V./P./N./M./S./R./K./H.` — the misread trap, `M.` carries 11 census senses from Manu to Middle), and the not-in-census class (`inj.` flagged «Нет в цензе», never glossed — matching the E3 register's declared-unresolved list). Sense counts come from the census's own `polysemy[*].nExpansions` casefold semantics (448 of 4752 legend-carrying strings polysemous — the headline reuses payload values, not a re-derivation; `c.` = 4 senses, `P.` = 11, `M.` = 11, `f.` = 6), legend rows are quoted verbatim with their dictionaries. **Review-pool wiring (H5307 precedent):** the guide joins [docs/REVIEW_POOL_V1_DESIGN.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_POOL_V1_DESIGN.md) §2 as an **optional onboarding packet** (offered before a first sheet, not a gate) with a README link row. **Usability signal:** new [data/schema/label-misread-feedback.schema.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/schema/label-misread-feedback.schema.json) — one lightweight row per misread label (pool pseudonym `pool-aNN` only, UTC date, contact-scrub note rule per §4.5), raw rows gitignored in `review/`, aggregate routed back as register feedback to the E3 small-class register follow-up (csl-standards v1.5.0, SMALL_CLASS_ABBREV_REGISTER_NOTE). **Traceability evidence:** seeded-RNG spot-check log [data/abbrev/label_guide_traceability_spotcheck_2026-10-13.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/abbrev/label_guide_traceability_spotcheck_2026-10-13.md) (8/8 PASS: expansion + dict verbatim + census sense count equal, `inj.` absence verified), plus 9 unittest cases (`npm run test-abbrev-label-guide`) locking verbatim row membership, census sense-count provenance, the pinned `c.` row, the not-in-census flag path, headline numbers, and byte-stable `--check` regen. `npm run verify` untouched (two-gates principle, H6459 precedent). Part of paper A72; closes H6465.
_Dr. Mārcis Gasūns_
- **Correction-loci packet re-baselined to the sibling feed (61571 records, 14-10-2026).** `validate-correction-feed` flagged the packet at 61430 vs the csl-corrections sibling feed at 61571 (plus a pw 18≠159 leg); regenerated with `npm run build-correction-feed` per the validator's own instruction — pointer/date class only, sibling cross-check green. (DeepSeek V4.1 Flash (openrouter/deepseek-v4.1-flash) via OpenCode)
- **H4/H5 review artifacts re-baselined to the current csl-orig (G15 weather repair, 14-10-2026).** The ap.txt correction on csl-orig origin/main shifted AP entry lines (+32 below the correction point); the H4/H5 review artifacts still carried pre-shift source pointers, so the generator-parity tests failed against a live `../csl-orig` sibling. Regenerated with `npm run regen-review-artifacts` — source pointers + stamps only; preserved human review fields byte-equivalent (script-asserted). `node --test` 409/409. (DeepSeek V4.1 Flash (openrouter/deepseek-v4.1-flash) via OpenCode)
- **H6707: AOB declared canon + metric-2 rebase landed machine-readable.** New `data/pd/pd_aob_declared_works.tsv` (1,112 work groups, official-PDF ground truth, 6 confirmed edition pairs collapsed), `data/pd/pd_aob_siglum_title.tsv` (5,106-row census join: 14 print-verified ground-truth joins incl. the recovered Viṣṇupurāṇa row and the ṚV./AV. siglum corrections — all 120 covered sigla join; 78.0 % of occurrence mass), `data/pd/pd_aob_fuzzy_short_adjudication.tsv` (150 low-confidence fuzzy joins adjudicated: 24 confirmed, 126 demoted to unmatched). `pd_dcs_metrics.json` gains the declared-canon keys (`n_declared_aob_rows_edition_level` 1419, `metric_title_level_declared_pct` 8.32, join-rate keys); coverage report §Metric 2 carries the declared-canon denominator alongside the exercised letter-a band; `build_a68_figures.py` fig2 bar rebased to the declared canon (8.3 %) and `papers/figures/*.svg` landed at the script's declared output path. A68 canary 12/12 + rowlevel ALL PASS after the rebase. (GLM 5.3 (zai-coding-plan/glm-5.3-flash) via ZCode)
- **H6939: the long-dictionary league table gets a speed column and Eastern peers (17-10-2026, DeepSeek Flash `deepseek-v4.1-flash`).** 8.8 now derives `entries/yr` on **compilation** span (not publication) for the seven Sanskrit/Indo-Aryan rows and states PD on both bases — 2,099/yr over 50 printing years, 1,346/yr over 78 from Katre's 1948 conception — so the rate column reads as a ceiling for the finished dictionaries and a floor for PD. New **third peer group**: Hanyu Da Cidian (1979-1994, 370,000 words, 24,667/yr) and Nikkoku 1st ed. (~40 yr compilation, 450,000 entries, 11,250/yr), both [secondary] and both flagged for upgrade before citation, with Nikkoku's cloud-native 3rd edition marked **scheduled 2032, not realized**. New derivation: PD's own density implies ~2.59 M entries, i.e. ~1,235 yr at its own rate, ~361 at MW's and ~171 at PWK's — only the last fits the ~180-year ceiling every finished dictionary has kept — and the ~37-volume plan (647 k entries) silently assumes a ~4x terser rest-of-alphabet. 8.10's TamiLex caveat is replaced by a dated re-probe: the site answers HTTP 200 and publishes a Hamburg Academy long-term grant but no start year and no entry count. Non-Sanskrit monuments keep spans only, with the absent rates named as a gap rather than guessed. Frozen values untouched.
- **H6939 fix: the scope projection now divides the REMAINING 2.49 M entries, not the whole 2.59 M** (17-10-2026, DeepSeek Flash `deepseek-v4.1-flash`) — the earlier table double-counted the 104,959 entries already printed and so disagreed with the density-held horizon by ~50 years; the three lines are now ~1,185 / ~346 / ~164 years to completion years ~3211 / ~2372 / ~2190, and the first reconciles with 8.6's ~3211. Also corrected the plan-side wording: the ~37-volume plan covers only ~25 % of the 2.59 M that `a`-density implies, so it assumes ~4x the entries per page (~69.5 vs 17.3, articles ~4x shorter) — the earlier 'terser per page' inverted which quantity is terser. Caught by the independent codex verifier, not by the author.
- **H6939 fix 2: the span basis is stated honestly and the plan multiplier is 4.6x, not 4x** (17-10-2026, DeepSeek Flash `deepseek-v4.1-flash`). The section claimed rates on compilation years while the table actually carries publication spans — now it says so, with PD (50 printing / 78 from conception) and Nikkoku (4 publication / ~40 compilation) as the two cases where the bases diverge. And the plan-side multiplier over the alphabet still to come is ~4.6x the entries per page (17.3 to ~79.5 over the 31,277 plan pages left), not the 4.0x whole-work ratio. Both raised by the independent verifier.
- **H6720: printed AOB authority vs the harvested PD sigla reconciled (17-10-2026, DeepSeek v4.1 Flash `deepseek-flash`, via DSH).** The 5,106-signum harvest (PDScan letter `a-`) and the printed *Abbreviations of Books Quoted* (`PD/AOB.md`, 42 pp OCR) are now measured against each other in both directions. New [scripts/pd_aob_sigla_reconciliation.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_aob_sigla_reconciliation.py) (stdlib, deterministic, `--check` + `--selftest`) parses **1,430 printed entries** — one per printed row, the bibliographic tail reassembled across OCR wraps, 623 merged `Siglum Title` cells split, 15 rows whose siglum the OCR mangled into Devanagari recovered, 61 wrap fragments/garble reported rather than counted — and matches them to the harvest on two independent routes: siglum identity (diacritic-free skeleton, ≥3 letters, edition-suffixed groups like `RajTa,(Ka.)` answering the bare `RājTa.`, one-letter sigla refused unless the printed cell is a clean short form with a title tail) and title identity (H6707's adjudicated title against entry tails). Results, all committed as [pd_aob_entries.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_aob_entries.tsv), [pd_aob_sigla_reconciliation.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_aob_sigla_reconciliation.tsv) (2,954 discrepancy rows in five classes) and [pd_aob_sigla_reconciliation.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_aob_sigla_reconciliation.json): the frozen join claim reproduces exactly (**3,233 families = 63.32 %**, **78.04 % of the 398,359 occurrences**); **80 harvested sigla the join left `census_unmatched` equal a printed entry** and lift presence to **64.88 % / 80.08 %** (`Yādavā.` 928, `Hastyāyur.` 925, `TattvSaṃ.` 703, `RāghPāṇ.` 641 …); the entry-located lower bound is 51.55 %, the gap being **681 joined sigla that cannot be re-located at entry level from this OCR alone** (H6707 also drew on the official-PDF ground truth and a second OCR pass) — listed, never dropped. Reverse direction: **1,003 of 1,362 well-formed printed entries were exercised under `a-` (73.64 %)**, **359 were not (26.36 %)**, of which 223 are hard gaps and 136 exist only as OCR variants (ratio ≥ 0.85) — minor works (`Mandāv.`, `DevīPañ.`, `Nṛtya.`, `Apastambáśulbasūtra`), not famous texts. The `MahāBhā.`/`MahāBh.` trap is asserted in the selftest and lands on two different printed entries (`MahaBha,` / `MahaBh,`, both p. 18). Frozen headline values 25.2 % / 77.9 % and `pd_dcs_metrics.json` untouched. Write-up: [reports/PD_AOB_SIGLA_RECONCILIATION_2026-10-17.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_AOB_SIGLA_RECONCILIATION_2026-10-17.md). `--check` gates the JSON aggregates **and** both row-level TSVs byte for byte (a one-cell tamper exits 1 naming the file; verified as a negative control), so a truncated or hand-edited table cannot pass the reproduction gate.
- **H6923: PD declared-canon denominator audited — 1,419 is an entry count, 1,118 is a clean-subset floor.** New `scripts/pd_aob_declared_canon_audit.py` + `data/pd/pd_aob_declared_canon_audit.json` reconcile the three numbers in circulation for the AOB canon of PD: the 1,419 "edition-level rows" behind metric 2 have no committed parser (the committed re-parse of the same OCR yields 1,517 raw entries; the printed OCR supports 1,476 entry-like lines; the printed census is 1,464), so the denominator is stated as the band **1,419–1,517** and metric 2 as **7.78–8.32 %** instead of the point 8.32 %. The published `pd_aob_declared_works.tsv` (1,112 works / 1,118 edition rows) is shown to be a *clean-subset floor*: the pass-2 clean filter dropped 556 OCR-merged `Siglum Title` entry lines, so 118 / 1,118 = 10.55 % overstates coverage and is explicitly banned as a denominator. `pd_dcs_metrics.json` gains `n_declared_aob_entries_reparse_raw`, `n_declared_aob_entry_lines_structural_r1`, `n_declared_aob_edition_rows_published_tsv`, `declared_canon_denominator_band`, `declared_canon_rows_reproducible` and a per-denominator metric map; the `declared_canon_note` and coverage-report §Metric 2 stop claiming the TSV carries the 1,419 rows. A68 headline values untouched (canary 12/12 + rowlevel re-run green). Denominator *choice* for the manuscript (§5/§7, fig2) stays a recorded judgment fork for the post-submission pass. (DeepSeek Flash, deepseek-flash)
- **H6933: PD declared-canon denominator ruled to the central estimate — metric 2 is now 8.0 %, not 8.3 %.** MG ruled the H6923 fork on 17-10-2026: the quoted denominator is the central estimate (≈1,476 AOB entry rows → 118/1,476 = 7.99 %, one in twelve and a half), with the pass-1 point 8.32 % surviving only as the band's upper bound. `pd_dcs_metrics.json` re-keys `metric_title_level_declared_pct` to 7.99 with `…_denominator` 1,476, `…_ruled_display` 8.0, `…_pass1_point` 8.32 and a written `declared_canon_ruling`; the coverage report (headline table + §Metric 2) and `data/pd/README.md` state 8.0 % with the 7.8–8.3 % band and keep the published TSV named as a clean-subset floor (118/1,118 = 10.6 % still banned); `scripts/build_a68_figures.py` fig2 bar and label move to 8.0 % / "118 of ≈1,476 AOB entries". Manuscript §5/§7, `iscls.tex`, the figure pair and `iscls.pdf` were re-stated in the same pass (Uprava), canary **12/12 PASS**, audit `--check` and prose-drift `--check` green. (DeepSeek Flash, deepseek-flash)
- **H6982: the CDPL vowel claim is corrected and its contradiction registered (17-10-2026, DeepSeek Flash `deepseek-v4.1-flash`).** 8.8 said the three volumes cover 'all the vowels and into the consonants'; by the printed range (a through ujjhittu, ending inside u) two vowels, e and o, are still ahead — while MG was told orally at BORI in 2019 that the vowels were finished in Indian order completely. Both accounts now sit in the text as [computed] vs [testimony], with the settling evidence named (vol. 3's last printed entry against the vols 1-3 title-page ranges). No rate, no frozen value, no other row touched.
- H6982 fix: the SECOND vowel-series assertion is gone too (DeepSeek Flash `deepseek-v4.1-flash`) — 8.8's controlled-experiment paragraph still said BORI 'in 38 years cleared the entire vowel series' while the corrected passage above it records the printed range ending inside u; it now says 'carried its alphabet from a into u, the end of the vowel series being exactly what the two accounts disagree about'. Caught by the verifier.
- H6982 fix 2: the remaining-vowel count is right (DeepSeek Flash `deepseek-v4.1-flash`) — 'two vowels short' counted only e/o; after u the Indian order still has u-long, r, rr, l, e, ai, o, au = eight symbols, and 8.8 now says so. Verifier catch.
- H7006: bughunt 07-10 findings closed — the vendored `sanskrit-util.js` drift guard is now CI-visible: a committed `src/lib/sanskrit-util.pin.json` sha256 is checked unconditionally by `test/lib.test.mjs` (the sibling-checkout comparison still runs when `../sanskrit-util` exists, but no longer gates the guard), and `normalizeLookupQuery` returns a lower-case candidate for ALL-CAPS input (`DEVA` → `DEVA`, `deva`). (DeepSeek Flash (deepseek-flash))
- **Compound-depth evidence — corrected distribution 3–8, p2 interval and censoring bounds, deterministic headword join, full loose frame, GRA convention audit (18-10-2026, DeepSeek Flash `deepseek-flash`).** Under the 18-10-2026 rulings this adds: (Q6) a corrected depth distribution 3–8 from the committed snapshot (markup-3 p2 **47.3 %**, Wilson CI **45.8–48.7 %**; markup-4 22.7 %, markup-5 8.6 %; model-read IC-3+ **2,349 of 5,489** valid, 42.8 %, CI 41.5–44.1 %); (Q10) a censoring bounds table that turns the same cell into **30.5–52.3 %** over all rows, using the rule that truncation drops the first member; (Q11) a deterministic MW/PWG headword join of the 2,121 markup-3 rows the model reads as 2 — **2,101 (99.1 %, CI 98.6–99.4 %)**, 20 residuals, byte-identical on re-run; (Q7) the full loose frame **30,703 records / 28,977 surfaces** with a recorded API cross-check (64.0 % valid, 3+ read **33.4 %**, CI 32.8–34.1 %, vs 1.5 % for privatives); (Q8) a marker-convention audit *before* the number — GRA `<k2>` has **4,360 hyphens and zero em dashes** — then a 500-row pilot (2+ read 43.8 %, CI 38.3–49.4 %). New `scripts/build-compound-depth-evidence.py`, `scripts/build-compound-depth-loose-frame.py`, `scripts/pilot-gra-compound-depth.py`; artefacts under `data/compound-depth/*-2026-10-18.*`; report `reports/COMPOUND_DEPTH_EVIDENCE_2026-10-18.md`. The loose frame and GRA pilot are remote cross-checks, explicitly not canonical: Q9's pinned local run needs a GPU/multi-core host.
- **Compound-depth metric honesty — public surfaces now say joints and publish both depth series (18-10-2026, DeepSeek v4.1 Flash `deepseek-flash`, H6962).** The atlas had been publishing the **loose** 3+ count (30,703) as if it were member depth, with no label. Following the Dharmamitra typography probe and the 18-10-2026 rulings (Q4–Q5), the `compoundSegmentCount` **id is unchanged**; only the display labels and `FAMILY_ASSUMPTIONS` now say **joints** (a joint is an internal division, not an immediate constituent). `src/data/mw/mw-depth-distribution.json` now carries two visibly labelled series — **strict** (em dash only, **8,638** at 3+) and **loose** (em dash, hyphen, plus, **30,703** at 3+) — with the historical key kept as a loose alias. `/tools/mw-depth` plots both series and `/tools/mw-family-depth` relabels its axis, tooltip and table to joints; families are **not re-ranked**. Both tables keep a CSV download (`mw-depth-joint-series.csv`, `mw-family-depth.csv`, etc.). `validate-mw-depth` pins the 8,638 / 30,703 sums. The never-triaged June queue is **retired with a dated tombstone** citing **1,439 of 2,173** resolved rows (66.2 %) as `model-splits-fewer` and pointing at the probe; its builder refuses to regenerate over the tombstone.
- **Compound-depth typography probe — the strict em-dash bracket stands; the loose privative bracket is not licensed (18-10-2026, DeepSeek Flash `deepseek-flash`).** Dharmamitra ByT5 `unsandhied` over all **8,638** MW em-dash 3+ records and all **6,096** single-hyphen privatives (1,000-row stratified sample, then the full frame): the privatives parse as 3+ members in **1.5 %** of 2,713 valid API rows (95 % CI 1.1–2.0) and **6.2 %** on a 160-row local-HF replication (2.7–13.8, 80/80 valid) — the 50 % loose trigger fails either way. The strict numerator is nevertheless a **joint** count, not a constituency count: **47.3 %** of valid markup-3 rows parse as 2 members (`agni—zwoma—yAjin` → `agniṣṭoma_yājin`), so 8,638 is an upper bound on immediate-constituent depth. The remote API truncates or empties ~33 % of bare compounds; the pinned local model does not. New `scripts/probe-compound-depth-privative.py` + `scripts/verify-compound-probe-local.py`, snapshots `data/compound-depth/typography-probe-2026-10-17.json` and `data/compound-depth/local-replication-2026-10-17.json`, report `reports/COMPOUND_DEPTH_TYPOGRAPHY_PROBE_2026-10-17.md`.
- **H6932: the AOB declared-canon denominator is now reproducible to a point — 1,437 usable entries, 118/1,437 = 8.21 %.** The H6720/H6960 inventory (`data/pd/pd_aob_entries.tsv`, after H6960's 29 restored entries and 15 folds: 1,444 parsed / 1,437 usable / 7 junk) is projected **without re-parsing the OCR** into `data/pd/pd_aob_declared_entries.tsv` — one row per usable printed entry with siglum, title, year, page and the merged/garbled/well-formed/exercised flags. `scripts/pd_aob_declared_entries.py` writes it plus `pd_aob_declared_entries.json` (input hashes, counts, the published 1,112-work / 1,118-edition collapse beside it, and every candidate 118/N: 1,437 = 8.21 %, ruled 1,476 = 7.99 %, header-corrected 1,469 = 8.03 %, census 1,464 = 8.06 %, re-parse 1,517 = 7.78 %) with `--check` and `--selftest` green. `pd_dcs_metrics.json` now sets `n_declared_aob_rows_edition_level` to the landed **1,437**, keeps `…_pass1` 1,419 and `declared_canon_denominator_band` [1,419, 1,517] as provenance, flips `declared_canon_rows_reproducible` to **true**, and records the point at `metric_title_level_declared_pct_landed_inventory_point` 8.21. The MG ruling of 17-10-2026 (central estimate 1,476 → 8.0 %, band 7.8–8.3 %) is untouched as the quoted display: both the landed point and the ruled estimate are reproducible and the 7.8–8.3 % band brackets them, so the denominator **choice stays open for MG** and no A68 manuscript, figure or canary value moved (canary 12/12 PASS). The H6923 audit still measures the pass-1 1,419 band low end via the preserved `…_pass1` key. (DeepSeek v4.1 Flash, deepseek/deepseek-flash)
- **H6941: 269 of H6720's 681 unconfirmed AOB joins recovered from the printed book's own text witnesses (18-10-2026, DeepSeek v4.1 Flash `deepseek-flash`, via DSH).** H6720 left 681 rows as `join_unconfirmed_at_entry` — the H6707 adjudicated title could not be re-located in the `AOB.md` tesseract entry inventory. The same printed PDF carries two further machine witnesses: its **PDF/A text layer** (poppler `pdftotext`, 162,027 chars, both columns legible) and the **second OCR** `PD/AOB_ocr.md` (166,348 chars). [scripts/pd_aob_sigla_reconciliation.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_aob_sigla_reconciliation.py) now takes `--witness <pdf|txt>` (repeatable; defaults to `../PD/AOB.pdf` + `../PD/AOB_ocr.md`) and re-checks every unconfirmed row by skeleton coverage (longest common substring in a window anchored on the title or its longest words, ≥0.85 of the title, short titles only on exact containment). **269 rows** reclassify as `join_confirmed_printed_text` (153 from the PDF text layer, 116 from the second OCR): the join's **confirmation coverage rises 78.94 % → 87.26 %** (2,552 → 2,821 of 3,233), and 412 residuals stay listed — every one has an OCR-broken *adjudicated title* (`Jainend lravyikarana`, `Nyayava irttika`), so no witness contains the string; repairing H6707's titles is a separate job and the 0.85 bar is not lowered to inflate the count. Presence does not move (63.32 % / 78.04 %; 64.88 % / 80.08 % corrected); what moves is how much of the join the repository can re-verify independently. Witness files are hashed (file + extracted text) into [pd_aob_sigla_reconciliation.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_aob_sigla_reconciliation.json); the script is deterministic (byte-identical on re-run), `--check` reproduces the JSON plus both TSVs, and the write-up gains a §H6941.
- **H6947: PD volume-level homogeneity — median 3 lines in every fascicle, and the marking fall is editorial/content, not a conversion artefact (18-10-2026, DeepSeek v4.1 Flash `deepseek-flash`).** The 18-10-2026 three-volume spot check is extended to the Deccan College ledger's **35 fascicle-volumes** (24 measured, 11 print-only), joining every entry to its printed page range, year and general editor. **Median printed lines = 3.00 in all 24 measured fascicles and all 8 bound volumes**; the mean is not the spot-check's 4.4–5.7 (a three-volume sample) but **4.36–6.21 by bound volume** and **4.22–7.56 by fascicle**. The H6942 dictionary-source marking share falls **2.06 % → 0.39 %** (vol. 1 → vol. 8), but the pre-v7 average is **1.94 %**, v7 is **0.88 %**, v8 is **0.39 %**, and the fascicle series is non-monotonic (7.2 = 1.88 %, 8.3 = 0.99 % against 8.2 = 0.17 %). The fall is **editorial/content, not a conversion artefact** on the machine-text evidence: general bracket use is stable at 11–17 % of entries, source-leading brackets longer than 40 chars total **29** (1 in v7, 0 in v8), the DBHS gloss exclusion fires twice, OCR near-misses of the seven sigla total **3** (none in v7/v8), and marks per 1,000 printed lines fall even faster (5.27 → 0.70). The named confound is **source-specific acknowledgement practice vs the later alphabet's source mix**; a print check of **v7 p. 3,525** and **v8 p. 3,989** (both zero-mark in the machine text, both carrying grammatical brackets) would settle the residual conversion hypothesis. Artifacts: [pd_publication_ledger.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_publication_ledger.tsv) (35 rows, PDF SHA-256 pinned), [pd_volume_homogeneity.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_volume_homogeneity.tsv), [pd_volume_homogeneity_bound.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_volume_homogeneity_bound.tsv), [pd_volume_homogeneity.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_volume_homogeneity.json); write-up [reports/PD_VOLUME_HOMOGENEITY_2026-10-18.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_VOLUME_HOMOGENEITY_2026-10-18.md). `python3 scripts/pd_volume_homogeneity.py --check` → PASS; H6942 canary (107,630 entries / 1,801 marked / 1,956 marks / exact source split) and H6949 canary (621,100 blocks) reproduce.
- **H6948 (DeepSeek `deepseek-flash`) — PD silent inheritance probed: the citation proxy fails, the gloss proxy survives, and the 1.67 % is a floor of acknowledged *gloss* borrowing (18-10-2026).** The bracket mark is PD's only machine-visible trace of inheritance, so [H6942](https://github.com/gasyoun/Uprava/blob/main/PD_PREFACE_MEASUREMENTS_2026-10-18.md)'s 1.67 % had no ceiling. New [scripts/pd_inheritance_probe.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_inheritance_probe.py) measures the full population (107,630 entries) on three axes and writes [data/pd/pd_inheritance_distributions.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_inheritance_distributions.json) + [data/pd/pd_inheritance_metrics.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_inheritance_metrics.tsv). **Macro:** of PD's 104,773 distinct letter-*a* headwords, **92.5 % (96,954) are absent from both PWG and MW**, and only **1.67 %** of that PD-only residue is a DCS-2021 lemma against **40.3 %** of the shared headwords (the control that makes the join interpretable) — PD's distinctive inventory is its own compositional/technical apparatus, not copied stock. **Micro (shared headwords, stratified sample 3,050 PD–PWG + 3,816 PD–MW rows, seeded shuffled null):** every instrument clears its null 8–12×, but the *calibration* splits — entries PD marks are **less** subsumed by the target's citations (−7.9 pp against PWG, −13.4 pp against MW, CIs exclude 0; target-coverage fails the same way), while entries marked `[MW]` overlap **MW's gloss vocabulary 0.262 vs 0.198 unmarked** (+0.064, 95 % CI 0.043–0.085; size-weighted +0.019) and `[PW]`-marked overlap PWG 0.039 vs 0.017. **Crosswalk-free check, PD against itself:** a marked entry is gloss-only (zero citations) **30.8 %** of the time — 37.2 % on the strict mark — against **1.29 %** unmarked, at the same median length. Marks census reconciles with H6942: strict **1,729 entries = 1.61 %** / 2,007 marks (H6942: 1,801 / 1.67 % / 1,956), broad 2,269 = 2.11 %. **Pre-registered verdict: the bracket is not an inheritance proxy** (D1 fails, sign reversed) — what survives is gloss overlap against the dictionary the bracket names, so the percentage must be read as *marked* gloss attribution and never as a ranking of derived entries. Two limits travel: the abbreviation crosswalk reaches only **3.1–4.0 %** of PD's citation mass (PD prints mixed SLP1/IAST sigla — `AbhinBhā.`, `ArthSaṃ.`, `AnekaTi.` — against PWG/MW's own stock), and DCS absence means "not a DCS lemma", nothing stronger. Write-up: [reports/PD_SILENT_INHERITANCE_PROBE_2026-10-18.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_SILENT_INHERITANCE_PROBE_2026-10-18.md). No dictionary source, page or review packet touched.
- **H6949: PD quotation-level unit — the first count of PD's quotations, and the twelvefold basis tested (18-10-2026, DeepSeek v4.1 Flash `deepseek-flash`).** PD's published numbers count *sigla*; none counted *quotations*, because the machine text carries no quotation tag and its obvious proxy — the `{#...#}` SLP1 block — is not one. It counts the headword (107,620 entries open with one; 107,479 literally `<k1>`), the morphemes of an etymology (`({#a#} + {#kAmatas#})`), and the two halves of a single printed quotation split at a line wrap; the worst entry (`anya`, `L=97714`) holds **3,904 blocks**. The unit is defined instead on PD's own typography: a **quotation** is a maximal run of consecutive blocks separated only by whitespace, immediately followed by a siglum-plus-locus; an **attestation** is one siglum locus plus each further reference inheriting it after a `;` (Reader's Guide X.v). Rule in [scripts/lib/quotation_units.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/quotation_units.py), parser in [scripts/pd_quotation_units.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_quotation_units.py), comparison in [scripts/pd_quotations_vs_pwg.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_quotations_vs_pwg.py), 10 hand-derived pins in [tests/forensic/test_quotation_units.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_quotation_units.py). Over the letter-*a* canon (107,630 entries, 554,243 printed lines): **302,442 quotations and 419,890 attestations** (384,217 siglum loci + 35,673 further references), 2.05 blocks per quotation, median 1 quotation per entry, max 2,329 (`anya`). The 384,217 siglum loci independently corroborate H1336's 398,359 citation occurrences to 96.5 %. PWG measured with the same rule (whole alphabet: 123,366 entries, 801,788 `<ls>`, 329,623 quotations) makes PD's first letter **52.4 % of PWG's entire-alphabet attestation mass and 91.8 % of its quotations**; over the 4,093 lemmas both dictionaries carry, PD holds **8.55 ×** the attestations in aggregate (median **4.0 ×**, p75 9.75 ×, 19.7 % of lemmas ≥12 ×, 8.3 % below parity). **Verdict on Wright 1978's "twelvefold increase in bulk": confirmed as an order of magnitude and best measured on attestations, not as a typical per-headword ratio** — at his own entry `akāmataḥ` PD carries 31 quotations and 75 attestations against PW's 2 and 6 (**12.5 ×**, 15.5 × on quotations, 15.7 × on the 47-vs-3 printed lines he counted). The omission he flagged is still there in the machine text: PWG cites Manu `11,127`, PD's five Manu loci omit it. Artifacts: [data/pd/pd_quotations_by_entry.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_quotations_by_entry.tsv), [data/pd/pd_quotations_vs_pwg.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_quotations_vs_pwg.tsv), [data/pd/pd_quotations_summary.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_quotations_summary.json); write-up [reports/PD_QUOTATION_UNIT_2026-10-18.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_QUOTATION_UNIT_2026-10-18.md). Same pass fixed the dataset README's dead PD source link — `drdhaval2785/SanskritSpellCheck/external_src/pd/pd.txt` no longer exists upstream; the Cologne PDScan 2020 archive is canonical.
- **H6960: the AOB entry parser's wrap-fragment rule repaired — 29 dated edition entries are back as rows, 15 part-word "recoveries" are folded, usable inventory 1,437.** H6720 folded every dotless backticked token into the previous row; that caught OCR wraps but swallowed real printed entries whose siglum lost its terminal dot (`AnyaS( Ni)`, `AtmaU.1`, `PranU.1/2`, `AVP.)`, the seven `Linganu` editions, `Kad. Kadam` = Kādambarī, `P. Astadhy` = Aṣṭādhyāyī). The rule now reads the tail: a capital-initial bibliographic tail (title/author + publisher+number or year), or a first word that already carries the siglum's terminal punctuation, makes the token an entry; a lowercase/part-word tail folds it. The reverse direction is repaired too: 10 part-word rows H6932 counted as recoveries (`N.`, `Pt.`, `Siv:` ×3, `K:`, `Sh:`, `Par:`, `Av:`, `Ram`) plus five that R1 also counts (`Bh:` ×2, `Ny:` ×2, `Ra,`) are folded. `scripts/pd_aob_sigla_reconciliation.py --selftest` re-derives both directions on the real AOB and checks that Kādambarī and Aṣṭhādhyāyī each own a dated row and Linganu matches the witness's seven variants; `--check` gates the regenerated `pd_aob_entries.tsv`, the discrepancy TSV and the new `h6960` block in `pd_aob_sigla_reconciliation.json` (`1423 + 29 − 15 = 1437`). Report numbers re-derived (entry-located 51.65 %, never-cited 26.61 %, H6941 266 of 678); A68's ruled 8.0 % band is left untouched for the next MG ruling (118/1,437 = 8.21 %). (DeepSeek v4.1 Flash, deepseek/deepseek-flash)
- **H6964: Wave A un-stalled — all 74 splitter rows filled from the pinned local ByT5 model, and A3's calibration published as a 2×2 against both dash truths (18-10-2026, DeepSeek v4.1 Flash `deepseek-flash`).** The 74 `n/a (model unavailable)` cells in [data/pd/compound_share_by_letter.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/compound_share_by_letter.tsv) are gone: 42 MW + 32 GRA rows now carry `splitter_pct`, a Wilson 95 % CI, and their n, read from the import-once snapshot [data/dharmamitra/compound_segmentation_sample.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/dharmamitra/compound_segmentation_sample.json) — `chronbmm/sanskrit5-multitask` at pinned revision `c0d2ada54f3d`, dated 2026-10-18, 1,637 headwords (25/letter, equal-letter stratified; CPU int8 on encoder+decoder only, `lm_head` fp32, recorded in the snapshot). [scripts/compound_share.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/compound_share.py) makes **no network call at build time** (verified with `unshare -n`) and two rebuilds are byte-identical. The calibration now scores the same splitter verdict (`n_segments ≥ 2`) against **both** truths: **loose** (any dash joint, MW n=941, tp/fp/fn/tn = 273/74/243/351, P 0.787, R 0.529, **F1 0.633**) and **strict** (em-dash 3+ joints, MW n=440, 21/229/5/185, P 0.084, R 0.808, **F1 0.152**); GRA loose n=696, F1 0.483. The anchor letter reproduces the population (MW `a` 84.0 % vs 83.1 %) and the strict sample base is 5.9 % vs the population's 6.8 %. The loose F1 flatters and the strict F1 damns because they ask different questions — "is a compound" vs "is a 3+ joint"; [reports/LETTER_ANATOMY_AND_ENTRY_SIZE_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/LETTER_ANATOMY_AND_ENTRY_SIZE_2026.md) §7.1 now states which truth each F1 belongs to and what the two disagree about (the splitter absorbs prefixed/privative forms as single words, as the typography probe found).
- **H6969: the printed AOB carries 1,469 entry rows, not 1,476 — and the 2003 "1,473 texts" line is not an independent witness for the denominator.** The row test counts the 42 printed AOB pages and finds the class H6923's R1 rule missed: the AOB repeats its own column header (`Abbreviation. Name of the Book, Author, Edition and Editor — Mode of Reference`) at the top of pages, the OCR catches it **7 times** (pp. 2, 13, 30, 37, 40, 41, 42), and every one passes R1 as though it were a book — so **1,476 entry-like lines = 1,469 entry rows + 7 header rows**. `118 / 1,469 = 8.03 %`, which still displays as the ruled **8.0 %**, so no manuscript, figure or canary value moves. The corrected count is the reference point for the 2003 *Outlook* figure of **1,473 texts**: 4 rows above the recovered floor and inside the OCR-loss ceiling (R2 = 99 un-recovered garbled lines), so it is *consistent* with the printed list but **not an independent witness** — same producer (Deccan College), different time slice (a 1975-vintage corpus count against a list printed 1976–2019) and a different object (texts excerpted, not books quoted); it is corroboration of magnitude, and it must not be counted as a second witness. New `data/pd/pd_aob_row_test_1473.json` + `scripts/pd_aob_row_test_1473.py` (imports the R1 rule from the H6923 audit with a rule-parity guard, per-page census, `--check` green); `pd_dcs_metrics.json` gains `n_declared_aob_entry_rows_header_corrected` 1,469, `n_declared_aob_repeated_column_header_rows` 7, `metric_title_level_declared_pct_header_corrected` 8.03 and a written `declared_canon_header_correction` that explicitly leaves the denominator **choice** to H6932. Only one AOB printing exists in the estate (`PD/AOB.pdf`; `AOB_ocr.md` is a second OCR pass of the same PDF), so no 2003-vintage list was available to test — recorded as a limitation, not inferred around. (DeepSeek Flash, deepseek-flash)
- **H6983: §8.8 gains an inline plan-vs-delivered dimension, per axis and never averaged.** The league table now prints, for each dictionary whose plan is documented, the plan declared at the start and what was delivered: OED 4 vols / 6,400 pp / 10 yr (1879 OUP–Philological Society contract) against 10 bound vols in April 1928 (12 in 1933), 71 years from the 1857 conception — **2.50× volumes, 2.42× pages (OED1 ~15,500 pp, not re-verified) or 3.40× on OED2's fully sourced 21,730 pp / 291,500 entries / 20 vols, and 7.10× years from 1857 (4.90× from the contract)**; Grimm 4.92× volumes / 12.30× years; TLL 8.80× years (floor, still at N/R); CAD 9.00× years; PD 37 vols / 37,333 pp planned against 6,056 pp delivered (16%), with ~149,615 pp required at its own `a`-density = **4.0× the plan**. WIL, GST, PWG, PWK, MW, KEWA, EWA and CDPL say **no documented plan** rather than inventing one (CDPL's ~90,000-entry cap is an entry-axis progress denominator only), as do KOW, WNT, SAOB, HDC and Nikkoku. Existing `Years` and `Entries/yr` columns are untouched; no value is frozen and no rate is changed. OED sources are the OUP record (`public.oed.com/history/` and `/history/oed-editions/`, accessed 18-10-2026). `validate-plan-deviation` now pins the §8.8 cells and recomputes every factor. (DeepSeek Flash, deepseek-flash)
- **H6984: the "~3× over plan" rule is true of size and false of time — size median 2.50× (n=3) against duration median 8.90× (n=4).** The claim was tested on the §8.8 corpus across three separate axes (volumes/pages, entries, elapsed years), requiring a plan *documented at the start* with its source. Only **6 of 17** dictionaries have one: OED (4 vols · 6,400 pp · 10 yr), Grimm (6–7 vols · 10 yr), TLL (15 yr, the only `[literature]` plan), CAD (10 yr), PD (37 vols · 37,333 pp · 200 pp/yr) and CDPL (~90,000 entries). The other **41 of 52** dictionary-axis cells are `NO-DOCUMENTED-PLAN` — including every completed Sanskrit dictionary, whose plans are not in the record. Completed outcomes: OED 2.50×/2.42×/4.90× (volumes/pages/years), Grimm 4.92×/12.30×, TLL 8.80× (floor, still at N/R after 132 yr), CAD 9.00× — **5 of 7 are PLAN-BROKEN (>4×) and none is PLAN-KEPT**. PD's projected duration ratio is 1.65× (not a deviation of scope: its binding constraint is scope, which no plan ratio captures). Verdict: "~3×" is an artefact of *axis mixing* (size ≈2.5×, time ≈8.9×) and of *denominator selection* (the documented-plan set is the notorious set, so 8.9× is an upper bound). New `data/plan_deviation.tsv` (52 rows, 18 columns, every row carrying `plan_source`/`outcome_source`/source class), `reports/DICTIONARY_PLAN_DEVIATION_2026-10-18.md`, `scripts/validate-plan-deviation.mjs` (recomputes every ratio, re-bands every class, refuses an undocumented plan carrying a value, and pins the aggregates the report quotes — `npm run verify` green), a §8.8 cross-reference, and the `validate-plan-deviation` npm script wired into `verify.mjs`. (DeepSeek Flash, deepseek-flash)
- **A68: PWG's 801,788 `<ls>` tags split into 729,719 quotation-linked attestations and 72,069 references; the 2021 DCS baseline has two ends — 74.1 % like-for-like, 74.0 % raw — over the six texts DCS-2026 dropped (892 tokens).** Two denominators the A68 manuscript had begun to use without a committed source are now measured, pinned and published. (1) *PWG quotation-linked attestations*: the unit (`scripts/lib/quotation_units.py`) counts an `<ls>` tag only when it closes a run of `{#...#}` blocks; over PWG's whole alphabet that is **729,719** of the **801,788** raw tags in `pwg.txt`, the other 72,069 (8.99 %, in 33,577 entries) being references that close no quotation. PD's 419,890 letter-*a* attestations are therefore **52.4 %** of PWG's raw tag mass and **57.5 %** of its quotation-linked mass — the report (`reports/PD_QUOTATION_UNIT_2026-10-18.md` §4) had used one word for both objects and now names them. (2) *The 2021 baseline*: DCS-2021 carried six texts DCS-2026 dropped — *Cakra* on Suśr (165 tok), *Comm. on the Kāvyālaṃkāravṛtti* (393), *Hārāṇacandara* on Suśr (162), *Khādiragṛhyasūtrarudraskandavyākhyā* (172) and the zero-token stubs *Ekākṣarakoṣa*, *Nāḍīvijñāna* — **892 tokens** in all; the metric's 2021 denominator (4,577,021) already excludes them, so the published **74.06 % (74.1 %)** is the like-for-like baseline and **74.04 % (74.0 %)** the raw one, and both deltas to 2026 round to +3.8 pp. New `scripts/pwg_quotation_linked_tags.py` + `data/pd/pwg_quotation_linked_tags.json` and `scripts/pd_dcs_2021_baseline.py` + `data/pd/pd_dcs_2021_baseline.json`; five forensic pins in `tests/forensic/test_pwg_quotation_linked.py` (two hand-derived on the rule, three on the artifacts); the two reports and `data/pd/README.md` carry the new rows. Every committed spine value reproduces (4,577,021 / 5,688,416 / 3,389,516 / 4,430,111 / 74.06 / 77.88 — all ok). (opencode/minimax-m3.1-flash-free, 19-10-2026, for the A68 §6.2 four-ledger table)
- **H7093: PD's Preface chronology claim tested on the whole letter-*a* population — the strong form is refuted (58.6 % of 9,689 decidable divisions carry an inversion, exact 95 % CI 57.6–59.6), the weak form survives for the DCS and Dharmamitra clocks (τ = 0.610 and 0.483) but not for PD's own SWC clock (τ = −0.253).** H6943 drew 100 divisions from 2,118 eligible ones and reported 49 % mixed (CI 38.9–59.2) — an interval that admitted both "worse than random" and "better than random", so the claim stayed unfalsifiable in either direction. The population run parses all 107,620 `<L>` entries of PDScan 2020 into 36,449 real numbered divisions (preamble and marker-less whole entries excluded), of which 13,358 carry ≥2 citation sigla, 4,148 are datable by ≥1 of the three H6943 work-date clocks and **9,689** by ≥1 of the four clocks (the new AOB imprint clock, which dates the editor's printed copy, not the work, and is reported separately and never merged into a work-date clock). H6943's 2,118 **entry** anchor reconciles exactly against this run's 9,689 **division** unit — the two counts differ by construction, the entry count is the anchor. A pooled within-division permutation null (10,000 replicates, seed 20261019) settles the direction: under the H6943 `any` rule the observed 58.6 % sits against a null mean of 59.0 % (2.5–97.5 %: 58.6–59.4 %), P(null ≥ observed) = 97.4 %, P(null ≤ observed) = 0.0297 — a marginal difference carried by the imprint clock (9,501 of 9,689 decidable divisions), which is structurally unable to speak about work chronology and must not be cited as a work-date result. Read clock by clock, the work-date clocks pull in opposite directions: PD's own SWC clock is *more* mixed than random (40.9 % vs a 36.6 % null mean, τ = −0.253 — leaning descending), while DCS (34.4 % vs 47.8 %, τ = 0.610) and Dharmamitra (47.5 % vs 52.9 %, τ = 0.483) are well below their nulls. The strong form (strict ascending order in every division) is refuted: 7,615 of 9,689 decidable divisions are not ascending (78.6 %). **What does not follow:** a mixed sequence is not by itself an editorial error — the seeded 200-row adjudication frame (100 flagged + 100 monotone controls, stratified by deciding clock, DCS genre, citation-count bucket and position in *a-*; `data/pd/pd_citation_order_adjudication.tsv`) is committed **unannotated**, so no κ and no adjudicated precision of "inversion" are reported, and the pre-registered withdrawal condition (adjudicated precision < 50 % ⇒ the negative result is withdrawn) is still live. New `scripts/pd_citation_order_full.py` (four clocks — PD/SWC, DCS, Dharmamitra, AOB imprint — never blended; per-division Kendall τ-a and adjacent-forward rate; Clopper–Pearson CIs; pooled permutation null; seeded adjudication draw; hash-pinned inputs), `data/pd/pd_citation_order_full.tsv` (9,689 division rows), `data/pd/pd_citation_order_adjudication.tsv` (200 rows), `data/pd/pd_citation_order_full_summary.json` (population funnel, summary, null, input hashes) and `reports/PD_CITATION_ORDER_FULL_2026.md`. `--check` recomputes the summary, the 10,000-permutation null, the row count, the 2,118 anchor and three report needles from the committed TSV; `--refresh` re-derives the summary JSON and the report from that TSV without the 55 MB PDScan text, so the derived blocks can be regenerated off the build machine. **CI determinism fix shipped with it:** the Clopper–Pearson bound is now rounded to 1e-10, because `_binom_cdf` evaluates the binomial CDF through `math.lgamma` — libm-dependent in its last bit — and the 80-step bisection amplified that one-ULP difference into a ~1e-14 spread of the bound, so the committed summary JSON was not byte-reproducible off the machine that built it; the bound is reported at 0.1 %, seven orders above the rounding. 20 pinned gold rows (`tests/forensic/h7093_gold_rows.tsv`, 10 mixed + 10 monotone) plus `tests/forensic/test_h7093_pd_citation_order.py` keep the parser and the verdict from drifting. A68 verdict memo delivered in `Uprava/papers/A68/PD_CITATION_ORDER_VERDICT_2026.md`: the limitation stands in kind, its numbers are superseded (the footnote's 49 % / 38.9–59.2 must not be quoted), and **no A68 result, table, figure or canary value moves** — the paper uses the citations as canon evidence, not as a chronology. (DeepSeek v4.1 Flash, deepseek/deepseek-flash)
- **H7093 follow-up: PD's senses are chronologically ordered as a tendency, not a rule.** The title claims the OED model — senses in chronological development — which H7093 did not measure (it measured citation order inside a sense). New `scripts/pd_sense_order.py` tests it from the committed per-division TSV: each sense contributes its earliest datable quotation, and the sequence is tested against a 5,000-replicate permutation null. Under Dharmamitra, 60.1 % of two-sense entries put the later quotation in the later sense, entries with ≥3 senses give τ = +0.323 (null band ±0.041), and the median first→last drift is +265 years; DCS gives 49.5 % (150 ties) and τ = +0.322 (+150 y); the imprint clock is flat (τ = +0.134), and PD/SWC — 15 works only — is not evidence either way. **What this does not establish:** a rising sequence is not proof of editorial chronology, because senses carry a partly-forced canonical order (literal → figurative → technical); the estate's cross-dictionary floor is MW-vs-PWG 0.767 against an independent Apte control 0.751 with a 0.50 shuffle floor (`data/forensic/SENSE_ORDER_TEST.md`). Until PWG and MW are put through the same dated test, the +0.32 cannot be attributed to PD's historical principle rather than to semantic structure — that comparative run is the stated refutation condition. The same pass records the clock provenance in the H7093 report: PD/SWC covers 15 works, DCS 70, Dharmamitra 93, imprint 1,459, and DCS/Dharmamitra are related chronologies (ρ = 0.94 on 56 shared works, one joint publication), not independent instruments.
- **H7099: benchmark v2 retires the self-graded `overallPrecision` and reports gold insufficiency honestly (19-10-2026, DeepSeek Flash).** The v1 report called the machine-verdict accept rate over 147 self-reviewed rows "precision" and printed `overallPrecision: 1.0`. v2 removes that field, freezes 100-row stratified held-out samples for encoding/OCR, gender-conflict and citation-link tasks (`src/data/benchmark/split-manifest.json`, seed 20261019, 0 train rows), defines gold as two independent `pool-aNN` keys or an explicit expert row, and reports macro precision/recall/F1, Cohen's κ, Krippendorff's α and seeded bootstrap 95% CIs only when that gold exists. Today it does not: 0/300 held-out rows are double-keyed, coverage 0% against a 10% floor, so every task score is null and the report names the blocking rows plus the 100–200 keys still needed. Adds a rule/parser baseline, a trivial-baseline slot, an inverted-oracle synthetic canary that must fail (and does), `npm run score-benchmark`, task cards/datasheet/licence, and `/tools/benchmark`.
- **H7100 (DeepSeek v4.1 Flash `deepseek/deepseek-flash`) — MW citation graph gains a passage-level index and a verified Ṛgveda link pilot.** New [`data/citations/source-to-entries.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/source-to-entries.json) parses all 286,560 MW `<L>` records and maps **209 canonical source labels to 213,906 of 320,828 citations** (their `<L>` records and source lines), resolving MW sigla through the vendored MWS `mwauthorities/tooltip.txt` table ([`mw-source-abbreviations.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/mw-source-abbreviations.tsv)) because `csl-guides` carries no MW works key; editorial markers (`L.` 40,213, `ib.` 10,100, `W.`, `MW.`, `Cat.`, …) are reported separately under `nontext`, never as texts. New [`citation-passage-links.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/citation-passage-links.json) links the 100 most-cited distinct explicit RV verse loci to GRETIL's Aufrecht edition at per-verse anchors `RV_<maṇḍala>.<hymn:3>.<verse:2>`; all 100 returned **HTTP 200 with the anchor present** (snapshot in `citation-passage-link-verification.json`). DCS is link-out only and deliberately not the verified target: its interactive browser challenge means a machine check cannot establish a stable passage URL. [`/tools/citation-tracer`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/citation-tracer.md) is no longer a placeholder; `/tools/source` and `/tools/dictionary-dossier` gain a "Cited at" panel. Builders `npm run build-citation-passage-index` / `npm run verify-citation-passage-links`; tests in [`test/citation-passage-index.test.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/test/citation-passage-index.test.mjs). A verified anchor proves the passage exists, not that MW's quotation is accurate.
- **H7107: the ZWNJ rule belongs to the generator — the PD AOB parity gates are green again, and a hand edit to a generated `data/pd` file now goes RED in CI.** PR #598 stripped two U+200C OCR artifacts out of two AOB title strings **by hand**, in `data/pd/pd_aob_entries.tsv` and `data/pd/pd_aob_declared_entries.tsv`; the generator re-derives the tail from the KoshaSHRI scan and re-emitted the ZWNJ, so both `--check` parity gates went red — `pd_aob_sigla_reconciliation.py --check` on "committed artifacts drifted in: pd_aob_entries.tsv", and `pd_aob_declared_entries.py --check` on "committed artifacts drifted in: pd_aob_declared_entries.json", whose recorded input hash still pointed at the pre-#598 file. **No figure moved**: the pass-2 spine is unchanged at **1,437 usable entries** (1,444 parsed / 7 junk / 1,379 well-formed) and **118/1,437 = 8.21 %** landed point against the **1,476 = 7.99 %** ruled central estimate — the drift was two invisible characters in two title strings, not a measurement. [scripts/pd_aob_sigla_reconciliation.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_aob_sigla_reconciliation.py) now owns the rule: the scan's invisibles (U+200C ZWNJ, U+200B, U+FEFF) are removed from the printed tail at the source — U+200D ZWJ is kept, it can be orthographically meaningful — so every emitted artifact regenerates byte-for-byte; the rule is pinned by a new selftest block and by a real-data assertion that no entry tail carries an invisible. [data/pd/pd_aob_sigla_reconciliation.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_aob_sigla_reconciliation.json) is regenerated to carry the rule in its own `method` block, and its `--check` now compares the **whole** artifact byte-for-byte instead of a hand-picked list of six blocks — that partial comparison is precisely what let the rule's own `method` edit drift away from the committed JSON unnoticed, so the gate compares every top-level key and names the ones that differ. [data/pd/pd_aob_declared_entries.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_aob_declared_entries.json) carries the refreshed input hash. New [scripts/pd_regen_gate.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_regen_gate.py) runs the three PD `--check` gates — skipping a gate whose source is not vendored here (the sibling `PD` checkout; PDScan's `pd.txt`), the rule the review-artifact regeneration already follows for a missing `csl-orig` — and is wired into `npm run verify`; new [scripts/pd_regen_gate_selftest.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_regen_gate_selftest.py) is the negative control that re-introduces the #598 edit and requires the gate to go RED, and a new `pd-regeneration-negative-control` job runs it in CI. The H7095 attestation gate stays unrunnable on this box (PDScan's `pd.txt` is absent) and is recorded as a residual. (OxAlpha, opencode/minimax-m3.1-flash-free)
- **H7109: PD vs PWG vs OED page economics — a page is ~20–28 decisions in all three, and the difference is entry length, not page packing (19-10-2026, DeepSeek Flash `deepseek-flash`).** Measures what one printed page contains in three dictionaries and what one entry costs in pages. **PD** (Cologne PDScan 2020 `txt/pd.txt`): 107,630 entries over the **4,327** pages the text spans, **440,003** `<div n="lb">` line-divisions plus 107,630 entry-opening lines = **547,633 printed lines** — which is what the text's own header asserts (`547634Lines`), so "line-divisions" is not "printed lines" and the two are reported separately; 42,247,645 characters; 2 columns to the page, **64 lines per column** (median, from the text's `[Page1-0001a+ 54]` markers), median **28 entries per page**. **PWG** (`csl-orig/v02/pwg/pwg.txt`): 123,366 entries, 223,497 body lines, 46,661,479 characters, **8,171** page-col codes (odd = left column, even = right, per `pwg-meta2.txt`), so **≈4,750 printed pages** reconstructed from the per-volume highest column — median **28 entries per page** and 9,823 characters per page, within 0.6 % of PD's 9,764. **OED** (measured on page images of the **1933 corrected re-issue of OED1 1928, vol. IV F–G**, read from the scan's own title page): the re-issue is a **three-column** page, 96 lines a column, **17,231 characters a page** — 1.76 × PD's — with a median **20 entries per page** over a seeded 3-page random sample (pp. 78, 362, 154) drawn with seed 7109; the **fire** anchor page 242 carries both running heads `FIRE.` and is 292 lines of a single entry. Headline: entries-per-page is a near-constant of dictionary typography across a century and three formats, while characters per entry separates them (PD 393, PWG 378, OED ≈1,034) — which corroborates A68 §6.2's per-headword density claim from the page side, so **§6.2 was deliberately left unchanged**. Deliverables: [data/pd/page_economics.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/page_economics.tsv), [data/pd/oed_page_sample.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/oed_page_sample.json), [reports/PD_PAGE_ECONOMICS_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_PAGE_ECONOMICS_2026.md), 10 pins in [tests/forensic/h7109_page_economics_pins.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/h7109_page_economics_pins.tsv) with [tests/forensic/test_pd_page_economics.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_pd_page_economics.py). `python3 scripts/pd_page_economics.py --check` → PASS (9 canaries + 10 pins). The Cologne host refused TLS from this machine (`SSL_ERROR_SYSCALL` on 443, empty reply on 80), so `pdtxt.zip` was taken from the Wayback Machine — member `txt/pd.txt` at **55,122,076 B**, the size the dataset README documents, which is the check that it is the same artefact. Read-only on all three sources; no csl-orig commit.
# H7116 — the sense-order control: PD's chronological sense order is not distinctive (19-10-2026)
- **H7116 (DeepSeek V4.1 Flash, `deepseek-v4.1-flash`) — the missing control for PD's chronological sense ordering, and it withdraws the claim.** [scripts/pd_sense_order_compare.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_sense_order_compare.py) runs H7093's statistic unchanged — earliest datable citation per sense division, two-sense forward rate, Kendall τ(position, earliest date) with a 5,000-replicate within-entry permutation null, exact Clopper–Pearson CIs — on **PWG, PW, MW and AP**, resolving each dictionary's own `<ls>` abbreviation key (csl-guides, longest-prefix; AP borrows the documented AP90 key; MW through the vendored `mw-source-abbreviations.tsv`, 96.8 % of its 320,828 citations resolved) and joining those titles to the same DCS (Dice ≥ 0.90) and Dharmamitra (≥ 0.82) clocks at fixed, never-relaxed thresholds. The PD row is recomputed from the committed TSV before any control is read and must reproduce `pd_sense_order_summary.json` exactly or the run refuses (canary: τ = +0.322 dcs / +0.323 dm). Result on the pre-registered dm clock: **PWG τ = +0.406** (3,343 entries) — a **significant reversal**, Δτ = −0.082 against PD, bootstrap CI −0.125 … −0.040, one-sided permutation P = 1.00 — **MW τ = +0.227** (Δτ = +0.096, 0.004 under the +0.10 floor), **PW τ = −0.041** and **AP τ = −0.042**. Verdict **WITHDRAWN**: PD's chronological sense ordering is shared with dictionaries that do not carry the OED's historical remit, so the *historical principles* reading of its sense order is not evidenced; the A68 footnote `[^chronology]` is amended accordingly in the same push. Numbers carry their denominators (entries, `<ls>`-resolved and dated citations per dictionary: PWG 67.1 %, PW 51.5 %, MW 96.8 %, AP 83.5 %) and a τ-by-entry-size split (PWG 0.421 on 3–7-sense entries, 0.258 on ≥8, so the giant root entries do not carry the result). Sub-senses (`a〉`, `— β〉`) fold into their numbered parent Bedeutung, matching PD's numbered `{@n@}` division unit; the fold *raises* PWG's τ (0.372 → 0.406), so the verdict does not rest on the segmentation. Committed: [summary JSON](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_sense_order_compare_summary.json), [report](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_SENSE_ORDER_COMPARE_2026.md), nine pinned forensic tests in [tests/forensic/test_pd_sense_order_compare.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_pd_sense_order_compare.py) (the verdict is re-derived from its own rows, so a silent flip fails), and the `data/pd/README.md` row. Read-only on `csl-orig`; no paid model calls.
- **PD knowledge index — parity programme: canon ledger, public page, atlas chapter, parity report (24-10-2026, DeepSeek Flash `deepseek-flash`, DSH).** The Poona Dictionary's knowledge surface becomes citable and auditable end to end. [`data/pd/pd_canon_ledger.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_canon_ledger.tsv) derives every canon base that has been quoted for the same 118 covered works (1,118 / 1,419 / 1,437 / 1,464 / 1,469 / 1,476 / 1,517 / 1,622 / 2,031), computes 118/N for each, and **aborts if a computed percentage disagrees with the percentage recorded in the source JSON**; it records the 562-row divergence between the two printed counts (AOB 1,469 entry rows vs Index 2,031) and the Index→AOB join at 981 of 1,622 sigla (60.5 %). [`src/dicts/pd.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/dicts/pd.md) is the atlas's first **unfinished** dictionary chapter, in two registers: comparative (23.2× denser than PWG on the covered span, 13.4× MW, 19.4× AP; median 4.0× attestations on the 4,093 shared lemmas) and fragment (median entry 3 printed lines in all 24 measured volumes; source marking falls 2.06 % → 0.39 % non-monotonically, editorial not conversion; ≈69 attestations per printed page). [`reports/PD_KNOWLEDGE_INDEX_PARITY_2026-10-24.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_KNOWLEDGE_INDEX_PARITY_2026-10-24.md) records the programme at **7/10** on its own checklist, with the DOI, human κ and edition availability left open on purpose. Sibling: a public knowledge page in the PD repository (13/13 sections evidence-labelled, zero private links).
## [0.19.11] - 2026-09-27

- **H5325: megastructure catalogue — the remaining seven dictionaries filled (24-09-2026, OxAlpha OpenCode GLM `zai-coding-plan/glm-5.3-flash`).** The H5324 schema is unchanged; the seven narrative dictionaries now carry their megastructure records, so `npm run validate-megastructure` reports **9 dictionaries, 91 parts over 15 scan sets**, and `node --test test/megastructure.test.mjs` holds the nine-dictionary stop condition (the pilot-only assertion is retired). New records: PWG 19 parts (seven volume titles, the per-part Vorworte and abbreviation supplements, two corrigenda, and the last leaf `7-1821` as a double-page spread), PW 3 (the 1879 *kürzere Fassung*, which is a different dictionary from the atlas `pwg` entry), WIL 3 (Wilson 1832), VCP 8 (Chiltern reprint front matter plus a 34-page *Liṅgānuśāsana* block that sits outside `pdffiles.txt` and had to be declared as a hand-built inventory), AP90 9 (title, imprint, preface pp. (1)-(4) signed Poona 28-12-1890, directions, terminations key, abbreviations, and the three numbered appendices - Prosody pp. 1179-1189, Writers 1190-1192, Geographical names 1193-1196 - all three transcribed in csldoc), ARMH 2 (a 101-page volume in which scan number equals printed page number, title over the opening page and the closing colophon on page 101) and ABCH 5 (English and Devanagari title pages, the *prastāvanā*, the introduction on Hemacandra, and the closing colophon). Findings the fill recorded rather than papered over: ARMH prints an English index in the margins of every page and no schema slot exists for a recurring in-page apparatus; ABCH's `f` series is Cologne's front-matter set but its last three pages are printed body pages 2-4, and the kośa's printed page 1 is in neither series (`pg01`-`pg04` return HTTP 404); AP90's scan `tit_0012` is a blank leaf. Two corrections to the H5324 guide: the Read tool does render scan images (the fill read every cited page that way), and the Google-digitized ABCH scans carry no text layer at all. New inventory rows: 251 pages across the nine dictionaries. Independent mechanical verification corrected one real defect afterwards: the `baseUrl` of all six csldoc scan sets pointed at `.../csldoc/build/dictionaries/prefaces/<dict>pref/`, which serves nothing (403 on the directory, 404 on `baseUrl` + image); csldoc serves the images from `.../csldoc/build/_images/`, where a probed image in every dictionary returns 200, and the two pilot records carried the same error. The same pass matched every declared page to its source - the csldoc inventories against the local `csl-doc/source/images` tree file for file, and every PDF-set ref against `csl-websanlexicon` `pdffiles.txt` - and confirmed by probe that the VCP treatise pages exist on the scan server although `pdffiles.txt` does not map them.

- **H5483 (Claude Sonnet 5 `claude-sonnet-5`) — community review pool v1: merge/adjudication (B7) and the κ report (B8) built and exercised end to end against the H5308 dry-run canary.** New [scripts/merge-review-pool-decisions.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/merge-review-pool-decisions.py) (`npm run merge-review-pool-decisions`) joins two pool exports per packet on item id and applies the design's five-case truth table (docs/REVIEW_POOL_V1_DESIGN.md §8) — resolved label looked up against `validate_review_decisions.expected_sheets()` so merge and validation can never disagree about a row's machine proposal: A1 same-label both-approve → `reviewed-ok`; A2 same-corrected-label both-reject → `reviewed-corrected`; A3 both-defer → `deferred`; A4 anything else → `needs-review` (adjudication queue, resolvable only via `--adjudications` with an explicit `adjudicatedBy` pseudonym and non-empty rationale — a tie never silently defaults to the machine label); A5 one key missing → `needs-review`, flagged `single-key`, never promoted. A note matching an e-mail, `@handle`, `t.me/` link or bare URL (§4.5) refuses the whole file. 14 unittest cases cover all five cases plus the note-scrub refusal, the tie-never-defaults rule, and the real H5308 R2 dry-run canary (10/10 rows merge to `reviewed-ok`, degenerate as expected for an all-approve synthetic canary). New [scripts/lexico/review_pool_kappa.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/review_pool_kappa.py) (`npm run build-review-pool-kappa`) reads one or more B7 merge reports and writes `data/review/pool_kappa_report.json` + generated [docs/REVIEW_POOL_KAPPA_REPORT.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_POOL_KAPPA_REPORT.md) under the house Chart Trust Block: Krippendorff's alpha (nominal, coincidence-matrix method) as the headline statistic since raters rotate (§5), Cohen's kappa per dyad only at n ≥ 30 (else n printed, point estimate suppressed), raw/chance/modal-label agreement, button-level 3-way agreement, a seeded 2000-resample bootstrap 95% CI, Landis–Koch bands reused from `root_agreement_kappa.py`, and an `expertBaseline` slot kept separate from the pool-internal alpha (§9 honesty rule 3). 15 unittest cases include a hand-computed 10-row fixture (α = 13/32 = 0.40625, worked in the test docstring) and the real R2 canary, which correctly reports `krippendorffAlpha: null` — the all-approve synthetic canary is a single-category degenerate case, labelled in the report's limitations as machinery verification, not a measurement (§10 P4/P5 gate). Both scripts wired into `npm run verify`. No recruitment, no real student data, no kappa number claimed — both explicitly out of scope per the handoff. Closes H5483; part of epic E014.

## [0.19.10] - 2026-09-25

- **H5301 (Opus 5 `claude-opus-5`) — the four evidence labels get a citable crosswalk to W3C PROV-O and TEI `@cert` / `@resp` (atlas side).** New [docs/EVIDENCE_LABELS_PROVO_CROSSWALK.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/EVIDENCE_LABELS_PROVO_CROSSWALK.md) maps `observed` / `derived` / `inferred` / `reviewed` with **one worked JSON envelope per label taken from committed review reports** (`h5-anomaly`, `citation-link-pilot`, `compound-depth-crosscheck`, `low-confidence-alignment`), each paired with its PROV-O Turtle and TEI fragment, and states seven explicit **no-equivalent verdicts**: `derived` vs `inferred` has no core PROV relation (the uncertainty lives only in `@cert` / `evidenceLevel`); `needs-review` / `blocked` / `deferred` are annotations, not relations; `assumptions[]` / `warnings[]` / `recordCount` / `schemaVersion` go to SKOS/VoID/DCMI, not PROV; chart trust blocks do not travel with data; the `csl:` namespace does not resolve yet. Two findings came out of a census of the 19,368 items in the 14 committed reports under `src/data/review/`: **`reviewed` is never emitted as an `evidenceLevel`** (0 items — a reviewed row keeps its production label and records the human layer in `reviewStatus` + `reviewer` + `reviewedAt`, so a consumer filtering `evidenceLevel == "reviewed"` matches nothing), and **a `reviewer` is not necessarily a person** (137 of 147 reviewed rows are signed by software agents `codex`/`Antigravity`, 10 by `gasyoun`) — so an exporter must emit `prov:Agent`, not `prov:Person`. Prior art honoured rather than duplicated: the **normative** mapping stays in [csl-standards/docs/EVIDENCE_LABEL_CROSSWALK.md](https://github.com/sanskrit-lexicon/csl-standards/blob/main/docs/EVIDENCE_LABEL_CROSSWALK.md) per [docs/BOUNDARY_RULES.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/BOUNDARY_RULES.md), and the new page carries a two-repo sync rule. Linked from [README.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/README.md) (documentation list + "How to cite") and [docs/EVIDENCE_LABELS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/EVIDENCE_LABELS.md). Documentation only — no builder, schema or generated data changed. Closes atlas review gap G3 on the atlas side; part of epic E014.
- **H5307 (Opus 5 `claude-opus-5`) — community review pool v1 designed: double-keying, pseudonymous annotators, adjudication and the κ report (gap G4).** New [docs/REVIEW_POOL_V1_DESIGN.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_POOL_V1_DESIGN.md) (+ [metadoc](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_POOL_V1_DESIGN.meta.md)) turns the roadmap's «R2 ×10, H4 ×105, xref ×50 blocked on one person» into a buildable mechanism, reusing the existing stack rather than growing a second review system: the [sheet emitter](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-review-sheets.py) and its `decisions.json` export, the [export validator](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/validate_review_decisions.py), the three committed packets, the [review-report overlay contract](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_REPORTS.md), the κ method and Landis–Koch bands of [ROOT_AGREEMENT_KAPPA.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/ROOT_AGREEMENT_KAPPA.md), and the [student guide](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_POOL_STUDENT_GUIDE.ru.md) (H5310). Four rules are fixed before any data exists: **identity** — pseudonyms `pool-aNN` only, roster held off-repo under the 152-ФЗ regime, raw exports never committed (`review/` gitignored), `reviewedAt` coarsened to UTC date, free-text notes scrubbed of contact-bearing tokens, credit opt-in and separate, withdrawal mechanical; **assignment** — rotating-offset blocks `keys(i) = [A[i%n], A[(i%n + 1 + (i//n)%(n−1))%n]]`, deterministic, two distinct keys per row, load `2R/n` ±2, partners rotating over all `n−1` colleagues (fixed-offset round-robin rejected: it freezes the pool into `n` dyads), n ≥ 4, deal committed as `data/review/pool_assignment.json`; **adjudication** — agreement judged on the *resolved label* not the button, five-case truth table, disagreements read against the source line (never a third blind key, never majority vote, never defaulting to the machine's proposed label), `blocked` allowed as a finding; **κ** — Krippendorff's α as headline (raters vary by design), Cohen's κ per dyad only at n ≥ 30, observed/chance/modal-share beside it, bootstrap CI, computed pre-adjudication, no pooled α across packets, R2's n = 10 reported as a machinery pilot not a measurement, MG's 10 recorded R2 decisions held out as a separate expert baseline. Submission is file-return over the recruitment channel (no backend, per [BOUNDARY_RULES.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/BOUNDARY_RULES.md)); student-PR, third-party form and submission-backend alternatives are recorded as rejected with reasons. **Two live defects surfaced by probing** and carried as build items B1/B3: `expected_sheets()` selects H4 rows by `reviewStatus == "needs-review"`, which H1621 emptied — the validator expects **0** rows against 89 emitted cards (probed 24-09-2026: 102 / 114 / 0 / 40), so every H4 export would fail; and the H4 card renders `Agent decision: <label>`, which contaminates the very independence a κ measures. Documentation only — no builder, schema, packet or generated data changed. Part of epic E014.
- **H5317 (Opus 5 `claude-opus-5`) — the learner reading layer v1 has a card spec and a measured join contract.** New [docs/LEARNER_LAYER_V1_SPEC.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/LEARNER_LAYER_V1_SPEC.md) names all eleven inputs (atlas lemma-lookup/dossier, DCS summary, the VisualDCS `learner-contracts-v1` payloads at envelope `vdcs-learner-v1-20260809`, WhitneyRoots `roots.csv` + `root_class.csv`, the P2 survival panel, homonym-split), fixes the join key as the normalised SLP1 lemma with a one-directional `slp1ToIast` hop for the two IAST-keyed VisualDCS payloads, and gives three homonym rules (dictionary homonyms warn and never merge; Whitney root homonyms show all matches; VisualDCS `lemmaId` collisions resolve to highest-`tokens` and disclose the alternatives). Frequency, paradigms and attestation stay consumed, never re-derived. New read-only [scripts/measure-learner-layer-coverage.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/measure-learner-layer-coverage.mjs) produces the coverage table: over 52,934 lemmas, frequency reaches 53.9%, nominal paradigms 31.1%, Whitney roots 1.3% (586 with a gaṇa), sense survival **28 lemmas (0.053%)** — and **zero lemmas carry all four layers**, since no P2 panel lemma is a Whitney root. v1 is therefore specified as a sparse card with named absences (`not-in-dcs`, `not-a-root`, `outside-survival-panel`, …) rather than a full card with gaps, with five audience personas as hard design constraints. Part of [E014](https://github.com/gasyoun/Uprava/blob/main/handoffs/epics).
- **H5423 (Opus 5.5 `claude-opus-5-5`) — Comparative Dictionary Lab outputs get a live monthly refresh.** New [.github/workflows/lemma-dossier-refresh.yml](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/.github/workflows/lemma-dossier-refresh.yml) fetches a shallow v02-only `csl-orig`, reruns `scripts/build-dictionary-comparison.mjs` + `validate-dictionary-comparison.mjs`, re-runs `regen-review-artifacts.mjs` with csl-orig hidden (as `npm run verify` does), and opens a bot PR with auto-merge, dispatching `test.yml` on the branch so the required checks report. Monthly (3rd, 04:41 UTC) + manual dispatch; PRs touching the workflow or builder get a dry run. `src/data/dicts/lemma-dossier.json` had been rebuilt only by hand (`generatedAt` 14-06-2026). Registered in [Uprava data/derived_surfaces.json](https://github.com/gasyoun/Uprava/blob/main/data/derived_surfaces.json) as `csl-atlas-lemma-dossier`. Part of [E016](https://github.com/gasyoun/Uprava/blob/main/handoffs/epics/E016-Uprava_stale-snapshot-autoregen_24.09.26.md) wave 5.
- **H5308/B1 (Claude Sonnet 5 `claude-sonnet-5`) — review-pool κ prerequisite: the H4 export validator no longer expects zero rows.** [`scripts/validate_review_decisions.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/validate_review_decisions.py) `expected_sheets()` selected H4 rows by `reviewStatus == "needs-review"`; H1621's agent adjudication flipped all 105 sample rows to `reviewed-ok`/`auto-resolved`, so the H4 expected set was silently empty and **every** H4 decisions export — including the double-keyed pool exports the community review pool needs — failed on `decided must equal the full sheet count`, as named in [docs/REVIEW_POOL_V1_DESIGN.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_POOL_V1_DESIGN.md) §3.1 item 1 (build item B1). Fix: a new `h4_expected_rows()` helper mirroring `build-review-sheets.py`'s `h4_items()` fallback — open (`needs-review`) rows if any, else the 89 `reviewed-ok` rows — so the validator and the sheet builder select the identical row set. `scripts/test_validate_review_decisions.py`'s pinned count for `csl-atlas-h4-semantic-field_89rows` moves from the stale `0` to `89`, plus two new tests: a synthetic full 89-row export now validates (the design doc's P1 rollout gate), and a `needs-review`-present case proves the fallback still prefers open rows over `reviewed-ok`. `npm run test-review-decisions` (`python3 -m unittest scripts.test_validate_review_decisions`): 9/9 OK. B1 only — pool mode (`--pool`/`--annotator`, B2/B4), blind rendering (B3), the R2 sheet (B5), the assignment builder (B6), merge/adjudication (B7) and the κ report (B8) are unbuilt; tracked at [H5308](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5308-OxAlpha_csl-atlas_review-pool-packets-to-double-keyed-sheets_23.09.26.md). Part of epic E014.
- **H5308 (OxAlpha `opencode/z-ai/glm-5.3-flash`) — review pool v1 machinery: the three blocked packets become double-keyed, blind, per-annotator review sheets with a validated two-annotator dry run.** Implements build items B1–B6 (+B9 tests) of [docs/REVIEW_POOL_V1_DESIGN.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_POOL_V1_DESIGN.md) (H5307, epic E014). B1 landed independently in [#516](https://github.com/sanskrit-lexicon/csl-atlas/pull/516) (`h4_expected_rows()` helper) while this branch was in flight; the merge folds the same fallback into the pool-mode `expected_sheets()`, keeps the count pin at 89, and retains the open-rows-preferred test. **B5** — R2's first sheet: `r2_items()` renders the 10 checkpoint rows (diagnosis, review question, the row's closed `proposedParserLabels` vocabulary, archive-comparison details block, csl-orig source-record links), stem `csl-atlas-r2-checkpoint_10rows`; MG's recorded `reviewedValue` is deliberately never rendered (§9 honesty rule 3 — held-out expert baseline). **B3/B4** — pool mode in [build-review-sheets.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-review-sheets.py): `--pool data/review/pool_assignment.json --annotator pool-aNN` emits that annotator's slice to `review/pool/<id>/` with the pseudonym in the export's `reviewer` field (sheet_id stem unchanged — the filename/localStorage/validator contract), blind: the `Agent decision:` line is suppressed on H4 and no prior decision is rendered on any pool card (§3.1 item 2 — independence is the measurement); honest per-packet screening blocks (R2 0/0/0/10, H4 0/0/0/89, xref 10 auto-resolved/0/0/40) satisfy the H1649 `extras=True` gate that already blocked the three non-xref sheets. **B2** — validator `--pool` mode: the reviewer must be a manifest pseudonym (the hard-pinned `gasyoun` check retires in pool mode only), the item set must equal that annotator's assigned rows (1:1 slice check), and pool `defer` requires a note. **B6** — [build-review-pool-assignment.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-review-pool-assignment.mjs) (`npm run build-review-pool-assignment`) deals all three packets by the design's rotating-offset rule and commits the manifest [data/review/pool_assignment.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/review/pool_assignment.json) with schema [pool-assignment.schema.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/schema/pool-assignment.schema.json); the unanchored `.gitignore` `review/` pattern is root-anchored so `data/review/` is committable while the personal-artifacts `review/` dir stays local. **B9** — property tests: [test/review-pool-assignment.test.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/test/review-pool-assignment.test.mjs) (two distinct keys per row, load ±2, partner rotation, determinism; 4/4) and six pool-mode validator tests (13/13 unittest). **Two-annotator dry run** ([dry_run_review_pool.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/dry_run_review_pool.py), `npm run dry-run-review-pool`): n=2 pool (pool-a01/a02), R2 10/10, H4 89/89, xref 40/40 keyable rows dealt (packet coverage 10/105/50; 16 H4 + 10 xref auto-resolved rows excluded per design §3); both R2 pilot decisions files validate in pool mode and are committed as canary evidence under `data/review/pool_dry_run/` (synthetic approves, marked DRY-RUN — never promoted); H4/xref slices validate transiently and are not persisted. All six per-annotator sheets render (2 × {10, 89, 40}); blindness spot-checked (0 `Agent decision` lines, 0 prior-decision leaks). Publish-safety: pseudonyms only in committed artifacts, no contact-bearing strings, raw exports stay gitignored.
- **H5409 (Opus 5 `claude-opus-5`) — Apte's sort-order disorder is *not* mostly vowel-grade root nesting, and the access-structures census is now browsable on the site.** The M11 census ([scripts/lexico/m11_access_structures.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/m11_access_structures.py)) gains a nest-aware view `heads_nest`: a root and the following headwords whose stem carries the root's guṇa, vṛddhi or zero grade (√kṛ `kf` → *kf, kar, kār*, so *kāra* and *karaṇa* fall into √kṛ's nest) collapse into one sort unit keyed on the root, via the new `grade_variants()` mapping on the root's last vowel. Measured on AP: **8.19 %** within-run violations against the `heads` view's 9.36 %, with the roots-only floor at 0.50 % — the filter removes 1,519 further headwords and closes only **13.1 %** of the gap, far below the pre-registered 75 % bar. **Refutation condition 3 of the methods page fired: the vowel-grade explanation is REFUTED** ([docs/ACCESS_STRUCTURES_SORT_ORDER_CENSUS_24-09-2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/ACCESS_STRUCTURES_SORT_ORDER_CENSUS_24-09-2026.md) §5a, §6). Vowel-grade nesting explains about one violation in eight; the residue is largely prefix-family grouping that never touches a root record (*atikrāntiḥ* → *atikramaṇam*, *aticchedaḥ* → *aticchandaḥ*), plus the grade mapping's named blind spots — samprasāraṇa, nasal-infix loss (√añj → *akta*), set/anit ā-roots. New site page [`/tools/access-structures`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/access-structures.md) carries the per-dictionary best-fit table, the factor-status grid (what the order can and cannot decide about ṃ, ḥ and geminates), the AP root-nest verdict, a counterexample browser filterable by dictionary/kind/policy-sensitivity/headword, and the full dict × view × rule rate table — IAST throughout via `slp1ToIast`, SLP1 kept only as a muted secondary column, CSV download on every table. Eleven hand-derived pins added in [tests/forensic/test_m11_access_structures.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_m11_access_structures.py) for the grade mapping and the nest-aware filter. Part of E014.
## [0.19.9] - 2026-09-24

- **H5 maker proposal draft — divaratha → diviratha evidence packet ready for transmission ([#478](https://github.com/sanskrit-lexicon/csl-atlas/pull/478)).** `docs/H5_MAKER_PROPOSAL_DIVIRATA.md` (H5315) assembles the Cologne-maintainer-actionable form of the one `source-declared-correction-candidate` row from the H5 maker-QA packet: the two wrong-reading entries (MW L92243 "w.r. for divi-", PWG L32945 "falsche Form für diviraTa"), the full witness table (divaraTa exists only in MW+PWG; PW, Vācaspatyam, Sørensen's INM, and DCS-2021 carry only diviraTa), printed-edition scan loci with live-verified scan links, DCS corpus attestation (diviraTa rare-band attested, divaraTa 0 occurrences), the exact two-part ask (data-quality confirmation + optional index redirect; no entry-text change proposed), and a verification appendix — all pinned to csl-orig@f4c08c57 with the June packet's shifted MW line anchors corrected (#L309835, #L310249). Draft only: nothing was filed in csl-orig or any Cologne surface; sending is the human step tracked in the Atlas FAIR roadmap Q3 2026 row.
- **H5329 (OxAlpha, GLM 5.3 flash `zai-coding-plan/glm-5.3-flash`) — ARMH and ABCH chapter stubs → real data chapters on the kośa macrostructure model.** [src/dicts/abch.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/dicts/abch.md) and [src/dicts/armh.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/dicts/armh.md) replaced as data chapters rendering from the generated packet [src/data/kosa-chapters/kosa_chapters.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/kosa-chapters/kosa_chapters.json): counts (ABCH 1,965 verse-groups / 4,606 sets / 13,663 members / 1,518 full verses across 7 kāṇḍas and the tenfold *tiryak* upavarga tier; ARMH 7,907 exploded records / 860 `<vn>` verse-groups / 883 full verses across 5 locator-only kāṇḍas), structure charts with per-page Chart Trust Blocks, the ARMH absent-devices honesty table (varga, synonym-set, gender — measured absences, not gaps), and one shared 13-row AMAR/ABCH/ARMH ordering-device comparison. Builder [scripts/build-kosa-chapters.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-kosa-chapters.mjs) reshapes the committed H5328 instances + measures and [parse-rules](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/parse-rules/abch.json) deterministically offline (no corpus reads; provenance sidecar); fail-closed [scripts/validate-kosa-chapters.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/validate-kosa-chapters.mjs) reconciles instance totals against parse-rules `record_count` (1,965 / 7,907) and enforces model honesty (ARMH keeps no grouped measures) — wired into `verify`; [test/kosa-chapters.test.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/test/kosa-chapters.test.mjs) carries 9 tests incl. 4 mutations. Gate H5328 surfaces untouched (`validate-kosa-model` PASS, 30/30). Part of epic E014.
- **H5453 (Claude Code Fable 5.1 `claude-fable-5-1`) — xref shared-edge pool re-intersected: 641 → 694, review sheet re-dealt to the fresh pool.** [`data/lexico/xref_shared_edges.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/xref_shared_edges.csv) was the m6 run of 04-06-2026 and was never re-run after [`xref_edges.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/xref_edges.csv) gained PWG's `<ab>s.</ab>` redirect edges on 20-07-2026 (H1350). A fresh [`m6_xref_lineage.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/m6_xref_lineage.py) over the committed edges gives 694 shared MW∩PWG edges: 641 retained, 53 added, 0 lost (PWG 22,937 → 25,766 edges, 11,857 → 14,016 sources; shared source lemmas 2,538 → 2,750; MW-side inheritance rate 21.8% → 21.8% unchanged, PWG-side 9.1% → 9.2%; Jaccard 0.069 → 0.069). Re-dealt rather than frozen (the H5453 fork; MG rules by merging this PR): `npm run regen-review-artifacts` rebuilt [`xref_lineage.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/xref_lineage.json), `xref_hub_review.json`, the source-check packet and both worksheets, so the deterministic first-40 slice that is the MW/PWG shared-core review sheet changed: cards `:01`–`:13` keep their edges, `:14`–`:40` shift, 5 B-initial edges enter (`BAvyaraTa→BAvya`, `BImagava→BEmagava`, `BaNgAsura→BANgAsuri`, `BadrasAman→BAdrasAma`, `Badravarman→BAdravarmaRa`) and the 5 D/G-initial ones leave (`Darmya→DArmyAyaRa`, `DraR→Dvan`, `GAwarI→apaGAwilA`, `Ga→pariGa`, `GaRqa→GuRqa`); no human vote was recorded on the old sheet (40 needs-source-check, 10 auto-resolved), so nothing is orphaned. Pool figure, slice initials (Ā/B/C/D, no G) and every sample-specific example re-pointed in both [taxonomy companions](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/XREF_SHARED_CORE_LABEL_TAXONOMY.md) (`test/xref-taxonomy-docs.test.mjs` pins the pool to the CSV), and the same figures refreshed in [MICROSTRUCTURE_XREF_LINEAGE.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_XREF_LINEAGE.md), `MICROSTRUCTURE_XREF_HUB_REVIEW.md`, `MICROSTRUCTURE_DECISIONS.md`, the student guide and [paper_xref_lineage.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_xref_lineage.md) (CAE×PWG 7 → 11, AP90×PWG 11 → 12, AP×PWG rate 34.3% → 31.1%). Unrelated H4/H5 packet churn from local `csl-orig` drift reverted, not landed. Count pins in `test/orchestrators.test.mjs` (40/10/50/110/80/0/30) hold unchanged. Residual of H5408.
## [0.19.8] - 2026-09-24

- **H5407 (Fable 5.1 `claude-fable-5-1`) — A50 citation graph re-frozen at a recorded `csl-orig`/`csl-guides` revision pair; 37-pair transliteration fold in the builder; ledger §P `narrows` → `survives`.** [data/citations/build_ls_citation_graph.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/build_ls_citation_graph.py) `CANON_ALIAS` +37 eye-checked variant pairs (H5295 fold table) with a chain guard; TSVs rebuilt twice, byte-identical, against `csl-orig@f4c08c57` + `csl-guides@64c967d` (both clean) and the first [ls_citation_graph.source.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_graph.source.json) committed beside them (828,505 / 912 / 1,701 → 826,752 citations / 874 nodes / 1,699 edges). The `ben` drift is attributed to three dated `csl-orig` `ben.txt` edits after the 06-07-2026 freeze (`056acf4` BEN #19 `Chr.` 3,017 → 1,602, `d1d0a18` BEN #21, `45d6907` BEN #27), not to the key. `citation_canon.json` (Q 0.4757 vs null 0.4094, 8 modules), `tradition_tags` (119 → 114 rows, five duplicate variants dropped), f12 report + topology arms + [pins](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_f12_a50_claim_ledger.py) regenerated; [A50](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/A50_ls_citation_frequency_graph.md) Abstract, Tables 1–3, §3–§6 and Data availability recomputed; [citations README](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/README.md) v3 change log; [claim ledger](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/A50_CLAIM_FALSIFICATION_LEDGER.md) §P rewritten with the recorded pair. The §4 tradition-map caveat (0 of 114 rows human-reviewed) stays open — separate human sheet; the review sheet keeps its `_119texts` id stem (filename/localStorage contract, as `skd-iti_100units` does) with the visible count corrected to 114.
## [0.19.7] - 2026-09-24

- **A06 kośa macrostructure paper: Amarakośa data-status wording corrected (24-09-2026, Claude Code Opus 5.5 `claude-opus-5-5`).** §2.1 now says the *Amarakośa* is not in the CDSL `csl-orig` corpus (still true), not that it is absent as data. §6 no longer says that "adding a digitized Amara would anchor the model" as if no such data existed: since H5328 the atlas models the *sanskrit-kosha* Amara markup (`amar.txt`, GPL-3.0) on the [kośa macrostructure methods page](https://sanskrit-lexicon.github.io/csl-atlas/paper/kosa-macrostructure). §6 now links that page and names folding its measures into A06's tables as the next-revision step. No numbers or findings changed.
- **H5408: xref source-check packet — 4 shared-core rows falsely flagged 'exact edge missing in MW' (24-09-2026, Claude Code Fable 5.1 `claude-fable-5-1`).** The m3 extractor and the m6 intersection were sound; the packet builder's exact-edge lookup compared MW's raw target (`a/nAkzit`, `Are/`, `Basa/d`, `-DArmyAyaRa` — SLP1 accent or compound hyphen still on it) with the accent-free sample key and never found the row. New [`scripts/lib/xref-normalize.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/xref-normalize.mjs) mirrors `m6_xref_lineage.py normalize()`; `edgeKey()` in [`build-xref-source-check-packet.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-xref-source-check-packet.mjs) folds both ends with it. `sharedCoreRowsWithMissingExactEdge` 4 → 0, exact shared-core pointers 76 → 80 (`mw-pwg-shared:03`, `:07`, `:16`, `:36` now carry both MW and PWG records). Regression test [`test/xref-normalize.test.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/test/xref-normalize.test.mjs); generator-owned packet/worksheet docs regenerated; the `too-sparse` examples in both taxonomy companions rewritten (they named `:03`/`:07` as PWG-only). Intersection unchanged by the fix: re-running m6 over the July-20 `xref_edges.csv` yields 694 shared edges (641 + 53 PWG `<ab>s.</ab>` redirect edges, none lost) — NOT landed here because it re-deals 5 of the 40 review cards; left as a residual.
- **H5421 (Sonnet 5 `claude-sonnet-5`) — union headword count 323,417/323,425 -> 323,422 in living docs; drift checker wired.** New [scripts/check_prose_number_drift.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/check_prose_number_drift.py) + [scripts/prose_number_drift_claims.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/prose_number_drift_claims.json) refuse a new stale copy of the pinned union headword count (`.githooks/pre-commit` on staged `.md`/`.txt`/`.tex`, [.github/workflows/prose-number-drift.yml](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/.github/workflows/prose-number-drift.yml) on PR/push). Corrected `.ai_state.md` + 4 docs (kosha's H4075 04-09-2026 refresh was never carried into prose); `CHANGELOG.md`'s historical entries are untouched by design (MG Q2 ruling, 24-09-2026: changelogs are frozen narrative, drift only logged). Central fix/log engine + estate log: [Uprava tools/prose_number_drift.py](https://github.com/gasyoun/Uprava/blob/main/tools/prose_number_drift.py) + `data/prose_drift_log.tsv`. Part of [E016](https://github.com/gasyoun/Uprava/blob/main/handoffs/epics/E016-Uprava_stale-snapshot-autoregen_24.09.26.md) wave 3.
## [0.19.6] - 2026-09-24

- **H5324: megastructure catalogue — schema plus the SKD and MW pilot (24-09-2026, Claude Code Opus 5.5 `claude-opus-5-5`).** New `data/schema/megastructure-component.schema.json` (1.0.0) records every front- and back-matter part of a dictionary: type, extent, function, what body notation it decodes, scan locus, evidence label, and what Cologne's digital edition did with it. The pilot fills it for SKD (27 parts, including the 19 records of the *mukhabandhana*: sigla key, anubandha key, source lists, genealogy) and MW (15 parts). MW adds pp. xxxiii–xxxvi, which csldoc never OCR'd, and the Additions and Corrections pp. 1308–1333; Cologne merged the latter into `mw.txt` (7,096 `n="sup"` records, 279 `<info n="rev">` markers). `npm run build-megastructure` writes the enveloped catalogue, and `npm run validate-megastructure` proves schema conformance and that every page of every scan inventory (121 pages) is covered or explicitly excluded. When sibling checkouts are present, it also re-measures the MW counts against csl-orig and csl-pywork. Guide and traps for the seven-dictionary follow-on H5325: `docs/MEGASTRUCTURE_CATALOGUE.md`.
## [0.19.5] - 2026-09-24

- **H5295: A50 claim-falsification ledger — one claim withdrawn, seven narrowed, provenance sidecar added (24-09-2026, Claude Code Fable 5.1 `claude-fable-5-1`).** `data/forensic/A50_CLAIM_FALSIFICATION_LEDGER.md` takes nine decision-bearing claims of the citation-canon paper through source sentence → measurement → inferential step → strongest alternative → counterexample → verdict, with an independent logic-critic pass (2 blockers, 11 majors, 12 minors — 24 fixed, 1 deferred to merge; key unification forwarded to H5407) and a delta pass over the fixes (22 findings, all fixed) adjudicated in §5. "No text is cited by all 11 dictionaries" withdraws: `Rigveda` (ben, bhs, lrv, md) is the paper's own §5.5-listed variant of *Ṛgveda* (the other seven), union 11; four texts reach all nine usable rows. "Partly disjoint citation communities" narrows: the optimiser's partition is `ap+ap90 | pwkvn+sch` plus seven singletons — exactly the two key-borrow pairs, so shared resolver key and citation community are not distinguishable in this graph; the margin over the null (Q − null 0.070, z 84) is unchanged under the §5.5 fold and far beyond a 14-run label-privacy control. "Folding would only sharpen modularity" narrows (margin flat under the four-name fold, −0.0035 under all 37 pairs; raw Q falls only because the null falls). "Shared canon predicts nested / the arrangement runs the other way" narrows: a one-canon draw with the same breadths sits on the fixed-fixed null, so NODF below the null means less nested than such a draw. Concentration, the private tail and the kośa sentence narrow (pool is 64.7% PWG; 31 private labels are variants + 9 private→private merges; 89–99.5% of kośa citations are PWG's). Provenance: the TSVs were frozen 06-07-2026 with no sibling revision; a bound rebuild at `csl-orig@f4c08c57` moves six percentage figures by ≤ 0.2 points (top-50 71.0 → 71.2) and four counts (−1,753 citations, −2 edges, −1 node, −1 private label); the builder now writes `ls_citation_graph.source.json`. Stale copies in `HYPOTHESIS_INDEX.md`, the `citation_canon.json` verdict strings and `/tools/citation-canon` rewritten. New `scripts/forensic/f12_a50_claim_ledger.py` (with drift block), `f12_a50_topology_arms.mjs` (8 arms + seed×fraction sweep, hashed inputs), pins in `tests/forensic/test_f12_a50_claim_ledger.py`; `modularity()` in `build-citation-canon.mjs` returns row labels. TSVs unchanged; `citation_canon.json` and `tradition_tags.json` regenerated (verdict/claim strings only, statistics identical); re-freeze + alias extension + key unification minted as H5407.
## [0.19.4] - 2026-09-24

- **H5310 follow-up: student guide corrections from the independent verifier (24-09-2026, Claude Code Fable 5.1 `claude-fable-5-1`).** `^` is svarita and `\` anudātta (not svarita); the two missing R2 labels `candidate-sense-marker` / `supplement-marker` added to the div-source-scope table and the `gam:pwg` worked example now confirms all six recorded labels (L21815 = separate homonym, `<div n="p">` = prefixed series); the 40-edge sample initials read ā-, bh-, ch-, dh-, gh- (SLP1 capitals); PWG Nachträge described as sections at the end of volumes 5 and 7 with corrections inside, not opening words; H5309 link repointed to `handoffs/archive/`; `puṇyavat` added as a live variant-headword vs prose-present disagreement example.
- **H5328: kośa macrostructure model — the versified synonymic dictionary as a macrostructural type (24-09-2026, Claude Code Opus 5.5 `claude-opus-5-5`).** New schema [`kosa-macrostructure.schema.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/schema/kosa-macrostructure.schema.json) models a kośa as kāṇḍa → varga → (upavarga) → verse-group → set (synonym-set, homonym-sense, indeclinable-set, unsegmented-verse) → member with a parsed liṅga tag. Each instance carries an `orderingDevices` table that labels every device observed (source text or digitization markup), inferred (measurement) or absent. [`m10_kosa_macrostructure_model.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/m10_kosa_macrostructure_model.py) (`npm run build-kosa-model`) builds validated instances for the Amarakośa (sanskrit-kosha `amar.txt`; 40 verse-groups across all three kāṇḍas and section types), ABCH and ARMH, plus whole-text measures. Alphabetical adjacency is 0.49–0.50 in the kośas against 0.94 in MW. The nānārtha-varga is sorted by final sound (0.991 against 0.536 for the initial letter) in two series, 802 nominal headwords then 59 mostly indeclinable ones, and 4 of the first series' 5 exceptions follow the ḍ=l / b=v equivalences. Amara keeps each gender in one run in 0.90 of multi-gender sets against 0.68 by chance. [`validate-kosa-model.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/validate-kosa-model.mjs) (`npm run validate-kosa-model`) checks schema and semantic rules; [`kosa-model.test.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/test/kosa-model.test.mjs) proves it rejects nine mutation classes. Methods page: [`/paper/kosa-macrostructure`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/paper/kosa-macrostructure.md).
- **H5328 verifier round 1: kośa model notes and validator corrected (24-09-2026, Claude Code Opus 5.5 `claude-opus-5-5`).** Device notes are now computed from the measures instead of written by hand. The Amarakośa varga note gives the colophon counts (22 of 24 vargas open with *atha … vargaḥ*, 23 close with *iti … vargaḥ*). The indeclinable-section note says the *avyaya-varga* is the last varga of the digitization, because kāṇḍa 3 v. 1 names a *liṅgādisaṅgraha-varga* after it. The ABCH verse note says the numbering runs on continuously; the old note claimed it restarted per section. ARMH verse-groups keep their whole verse block (locator 1.1.1.6 now carries verses 6 and 7), and their `counts.fullVerses` counts distinct verse numbers. [`validate-kosa-model.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/validate-kosa-model.mjs) now derives the whole gender object from its tag. It also checks kāṇḍa labels, set and member counts, and the ARMH locator, set and eid constraints. [`kosa-model.test.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/test/kosa-model.test.mjs) grows from 14 to 26 tests.
- **H5328 verifier round 2: sandhi-aware colophon count and four more validator rules (24-09-2026, Claude Code Opus 5.5 `claude-opus-5-5`).** The Amarakośa colophon count now reads *aTAvyayavargaH* as *atha* + *avyaya-* in sandhi, so 23 of 24 vargas open with *atha … vargaḥ*; only the *bhūmi-varga* lacks one. [`validate-kosa-model.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/validate-kosa-model.mjs) now also checks `counts.fullVerses`, `sectionType` against its section label, upavarga/IAST pairing and ARMH locator-to-kāṇḍa agreement. It deliberately does not order half-verse marks, which are no monotone counter in the source: *(258)* opens the avyaya-varga before *.. 1 ..*. Tests: 30.
- **H5331: access-structures census — sort order of the seven narrative dictionaries (24-09-2026, Claude Code Opus 5.5 `claude-opus-5-5`).** New `scripts/lexico/m11_access_structures.py` (`npm run build-access-structures`) recovers the printed headword order of MW, PWG, PW, AP, WIL, SKD and VCP from `csl-orig@f4c08c57`. It tests that order against 72 varṇamālā collation rules (ṃ, internal ḥ, final ḥ, r+geminate) plus two controls, and writes `data/lexico/access_structures.json` together with a rule-rate CSV and a CSV of all 6,217 best-fit counterexamples. Best-fit within-run violation rates: PW 0.16 %, PWG 0.31 %, SKD 1.15 %, VCP 1.58 %, WIL 1.65 %, MW 2.84 %, AP 9.36 %. The Petersburg family files ṃ as the class nasal; SKD, VCP and WIL keep ṃ at its own slot and degeminate after r. Methods page `docs/ACCESS_STRUCTURES_SORT_ORDER_CENSUS_24-09-2026.md`, hypothesis row ACCESS-SORT, and hand-derived pins in `tests/forensic/test_m11_access_structures.py`.
## [0.19.3] - 2026-09-24

- **CI `test` job green again — generator-owned review docs regenerated, generators hardened (08-09-2026, Fable 5.1 `claude-fable-5-1`, [#454](https://github.com/sanskrit-lexicon/csl-atlas/pull/454)).** `node --test` had 10 red subtests since 05-09 because three direct-to-main doc-hygiene commits (91d6ad0 header/byline + link upgrade, 3fdacf8 and 4307c17 judgment-link rewrites) hand-edited nine generated docs and the machine-only fixture that the tests diff byte-for-byte against their generators; `build-and-deploy` was red for the same reason, so no deploy since 04-09. Fix: every generated doc now carries a `_Generated by … do not hand-edit_` second line (skipped by the Uprava byline/header tool), the two R2 builders emit full blob URLs for vocabulary docs, all ten files regenerated from the committed packet JSON, and [CLAUDE.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/CLAUDE.md) lists the generator-owned docs. Not done: the source-repo `blob/master` → `blob/main` flip (lives in `scripts/lib/source-links.mjs` + ~70k committed links; separate change).
- **CI: test job covers direct-to-main pushes + generator-owned gate proven by negative control (H4613, 12-09-2026, OxAlpha `opencode/z-ai/glm-5.3-flash`, [#456](https://github.com/sanskrit-lexicon/csl-atlas/pull/456)).** The `test` workflow was `pull_request`-only, so the 05-09 direct-to-main hand edits never ran it; it now also runs on `push` to `main`. A new `generator-owned-negative-control` job (overlay-tripwire pattern) simulates a committed hand edit to a generated doc and requires RED on both enforcement nets — the `node --test` byte-compare must fail, and deterministic regeneration must erase the edit — with a clean-baseline environment gate in front. Verified locally before landing: sentinel → `ERR_ASSERTION` (RED); regen → canonical bytes restored (self-heal).
- **Article 21 §3.5 gains the MW-unabsorbed census number + `data/forensic/MW_UNABSORBED_CENSUS.md` companion (H5050, 17-09-2026, OxAlpha `opencode/z-ai/glm-5.3-flash`).** The Nachträge complement of the shared-omission test, folded into the existing §3.5 per the 17-09-2026 routing ruling — one number, no new subsection: **571 volume-7 homonym-extensions** (words MW already heads, for which the Nachträge record a further `<hom>` MW's main body never reaches), with the *kārin*³ canary (`pw.txt` L620966; the MW-annexure *kārin*³ is a different derivation — numbering coincidence, not absorption), the 498–626 numbering-comparability band and the Cologne-digitization provenance clause. New companion
  [`data/forensic/MW_UNABSORBED_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/MW_UNABSORBED_CENSUS.md)
  (SHARED_OMISSION_TEST pattern) holds the full census — method, headline classes (8,406 new · 4,112 never-seen · 27 dropped · 610 variant/fold-twin · 2,743 starred residue), all-layer and POS tables verbatim, caveats, reproduction — indexed in the `data/forensic/README.md` topic-doc table; §7 Reproducibility points at the external builder `mw_unabsorbed_census.py`. Numbers frozen + verifier-PASSed 16-09-2026 in `gasyoun/SanskritLexicography` (PRs #2253/#2255/#2256; posted upstream as [csl-corrections#119 comment 5704062630](https://github.com/sanskrit-lexicon/csl-corrections/issues/119#issuecomment-5704062630)); no census re-run. Book-form twin: SanskritLexicography ch12 §3.5 + BOOK Appendix A (separate PR #2264).
- **Evidence-dependence audit of A10's three strongest descent claims — the combination, not the arithmetic (H5073, 20-09-2026, Claude Code Opus 5 `claude-opus-5`).** H4352 pinned that each forensic *number* is computed correctly; this asks whether the numbers are *independent evidence*. New deterministic, offline, seeded tool [`scripts/forensic/f11_evidence_dependence.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f11_evidence_dependence.py) traces §3.2 (F1 apparatus), §3.4 (F5 citation order) and §3.5 (F9 shared omission) from their published figures down to their loci, then runs six controls; report [`data/forensic/EVIDENCE_DEPENDENCE_AUDIT.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/EVIDENCE_DEPENDENCE_AUDIT.md) + `f11_report.json` + two locus CSVs; 13 hand-derived pins with a null fixture in [`tests/forensic/test_f11_evidence_dependence.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_f11_evidence_dependence.py) (suite now 61 passed). **Dependence found:** all 3,583 of §3.4's order-bearing entries are by construction §3.2 shared-cited lemmas (100% nested) — one evidence base asked two questions, not two corroborations; the rare-reference pool is **94.5% Harivaṃśa** and is the same source-event set §6 resolves against the vulgate; a naive sum of the three locus sets double-counts **7,280**; PW is a partial duplicate witness of PWG (33.8% of its rare events are already PWG's). **Controls all pass:** a seeded verbatim duplicate witness inflates the naive count 88% (598 → 1,125) and independent support by exactly **0**; ablating the 25 commonest texts *widens* §3.2's lineage-over-null separation 9.7× → 16.3×; and a new global-convention control puts §3.4 on firmer ground than its 8-entry Apte null — on 4,685 sigil pairs where MW's and PWG's global ordering habits *disagree*, MW still follows PWG's particular article **75.2%** of the time against a 200-replicate permutation floor of 0.5004. No published figure was refuted; §3.5 is the only claim contributing loci (46.7% of its anchor) that neither citation signal touches. **Provenance gap measured:** `.source.json` sidecars pin the csl-atlas commit, not the `csl-orig` revision — F9 (frozen `key1` exports) reproduces to the digit while F1/F5 drift with upstream corrections (587 → 598 rare refs, 3,593 → 3,583 entries, concordance 0.8107 → 0.8108) against `csl-orig` [`30b2ae7b`](https://github.com/sanskrit-lexicon/csl-orig/commit/30b2ae7b3c6619b1ac6a417a02e4af907c1dd9d4); `f11_report.json` is the first forensic report to record its corpus revision and per-input SHA-256 hashes. [`article_21_apparatus_not_errors.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md) §3.2, §3.4 and §7 updated with the three findings; no A10 number revised, because none changed for a reason other than upstream corpus drift and re-freezing the suite against a newer `csl-orig` is a separate job.
- **Evidence-dependence audit, post-review revision — a determinism defect fixed and three findings softened (H5073, 20-09-2026, Claude Code Opus 5 `claude-opus-5`).** An adversarial pre-review of the audit landed hours earlier in #462 returned four findings, all acted on. **(1) The "deterministic, seeded" claim was false cross-process:** [`f11_evidence_dependence.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f11_evidence_dependence.py) iterated a Python `set` of headwords while drawing from the shared RNG, and because `str` hashing is randomised per process the `CTRL-PERM` band moved under a fixed seed — three runs gave three blocks, and the committed `f11_report.json` did not match the prose citing it. Fixed by sorting the entry set and tie-breaking the `Counter` orderings; two fresh processes now write a **byte-identical** report, and a new pin asserts the permutation block is invariant under container order. Canonical band: `0.5004 / 0.4885–0.5123 / 10.13`. **(2) `CTRL-DUP`'s Δ = 0 is structural, not empirical** — `independent_support()` projects onto `(lemma, ref)`, so a verbatim duplicate cannot move it; the report now says so, and a falsifiable twin **`CTRL-NOVEL`** was added (100 injected novel triples = 91 distinct new keys → independent support +91, expected +91, PASS — an accounting keyed on the witness would have risen by 100, one discarding the ref by 0). **(3) `CTRL-CONV`'s permutation floor was the wrong baseline for the margin:** the control now runs on every reachable comparand, and against the best usable non-lineage reference (Benfey 0.6337 on 101 discordant pairs) MW's excess is **+0.118**, not the +0.251 the 0.5004 floor implies — monotone in claimed lineage distance (PWG 0.752 > PW 0.628 ≈ BEN 0.634 ≫ 0.500). A10 §3.4's unhedged "only ≈0.05 of the 0.811 is convention, and the rest is the article" is replaced by the measured margin plus its caveats (Benfey's own Petersburg exposure, 101 clustered pairs, conditional-convention blindness). **(4) `CTRL-ABL-S`'s "widens 9.7× → 16.3×" is specific to the frozen depth of 25:** a depth sweep (5/10/25/50/100) shows the separation dipping to 8.60× before climbing to 18.31×, so A10 §3.2 and the report now claim *never collapses* rather than *widens*. Also cross-references A10's 96% Harivaṃśa share (565/587, frozen frame) against the audit's 94.5% (565/598) so the two cannot read as a discrepancy, and labels the `C2 ⊂ C1` result as true-by-construction in the graph CSV and §1 table. Forensic pin suite 61 → 62.
- **H5073 independent-review fixes: §3.4's copying margin downgraded to descriptive, cache provenance made honest (22-09-2026, Claude Code Opus 5 `claude-opus-5`).** The named Codex Astra (`gpt-6-astra`) logic critic returned FAIL on the evidence-dependence audit. It reproduced every number, and challenged the wording and provenance behind five points; all five were acted on. (1) "Independent leg/bases" is now "locus-disjoint". Disjoint loci are not statistical independence, and 7,280 is set accounting, not measured inferential double-counting. (2) `CTRL-CONV` gains a matched-population comparison, `arm_comparison()` → `pwg_vs_best_reference` in [`f11_report.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f11_report.json). The PWG and Benfey arms share only 24 discordant loci (2,168 vs 64 contributing entries), and on those Benfey agrees *more*, 0.750 vs 0.667. The unmatched +0.118 has an entry-clustered bootstrap 95% interval of [+0.023, +0.210]. The A10-C2 verdict moves from "survives" to **"weakens: agreement survives, attribution to copying unidentified"**, and A10 §3.4's "real and monotone" and "strongest single copying signal" are withdrawn. (3) "0.752 is an upper bound on article-level copying" is withdrawn. A pinned counterexample scores 1.0 with no copying. (4) `corpus_revision` no longer presents the sibling `csl-orig` checkout HEAD as the cache's generating revision. [`parse_cslorig.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/parse_cslorig.py) now writes `parsed/_parse_provenance.json`, and `source_hashes` is named the binding pin. (5) `CTRL-NOVEL`'s pin now injects onto a duplicated key (3 triples → 2 keys), so triple-counting would fail it. Pins 62 → 64. No A10 number changed; only wording and provenance claims did.
- **H5073 independent review round 2 follow-ups (22-09-2026, Claude Code Opus 5 `claude-opus-5`).** The Codex Astra (`gpt-6-astra`) re-review resolved findings 2, 3 and 5 and flagged two defects that the round-1 fixes had introduced. Both are fixed here. (1) "Locus-disjoint" was false: the omission anchor overlaps the citation loci on 3,697 of its 6,941 words (53.3%) and adds 3,244 of its own. The audit report, its metadoc and A10 §3.4 now say "partially overlapping / adds loci of its own". (2) A partial cache rebuild could relabel the whole cache. `parse_cslorig.py` now writes provenance per cache, bound to each TSV's SHA-256. `f11`'s `corpus_revision` verifies every cache it reads and reports `per_cache`, and `MIXED` / `None` instead of guessing. Also: the entry-bootstrap interval is described as conditional resampling uncertainty, the `convention_split` docstring no longer says discordant agreement is what *only* copying predicts, and the counterexample pin now uses one genuinely shared fixed ordering (X<A<B<Y<C). Pins 64 → 65. No A10 number changed.
- **H5248 F1/F5 forensic figures re-frozen against one recorded `csl-orig` revision (22-09-2026, Claude Code Opus 5 `claude-opus-5`).** Every F1 and F5 figure is now computed at `csl-orig@f4c08c57` (2026-09-20). A new `scripts/forensic/_corpus_pin.py` refuses to write a figure whose corpus revision is None, `MIXED`, dirty or moved mid-run. It takes the revision from hash-verified `_parse_provenance.json` for cache readers (F1) and from the clean checkout HEAD before and after the run for live readers (F5, F10). The four F1/F5 `.source.json` sidecars and `f1_report.json` / `f5_report.json` carry `csl_orig_revision`. A second run from a deleted and rebuilt cache reproduced every figure to the digit. Two example/row CSVs followed Python set order; both now sort, and runs under two `PYTHONHASHSEED`s give byte-identical outputs. A10 figures updated, with the June values listed in §7 and kept under `superseded_2026_06_03` in `f11_report.json`: 587 → 598 rare refs (corpus-unique 203 → 169; Harivaṃśa 565 unchanged, now 94.5%), 3,593 → 3,583 order entries (47.8% → 47.7% identical), 41,552 → 41,571 truncations, Jaccard band 0.16–0.19 → 0.16–0.18 (separation 9.5–49× → 9.7–47×), Benfey order arm 0.68/154 → 0.70/116. No verdict changed, and every F11 audit figure is identical at the new pin. Pins 65 → 74. F8 and F10 were not re-run.
- **H5260 csl-orig revision pin extended to F2, F3, F4, F4b and F8; §6 DCS arm re-run on the 598-row pool (22-09-2026, Claude Code Opus 5 `claude-opus-5`).** `scripts/forensic/_corpus_pin.py` gains `inherited_revision` (derived-table readers take the upstream sidecar's pin; unpinned → None, several → `MIXED`), `assert_same`, and `input_revisions`. F4 reads no `csl-orig` file, so its sidecar records `csl_orig.read = false` and pins `PWG/pwgissues` + `csl-corrections` under `inputs` instead of claiming a corpus revision. The dirty probe now ignores mode-only flips: a hook installer had `chmod`ed `.githooks/pre-push` in `csl-corrections` and the refusal fired. Wired: F2 over all 45 caches, F4b (cache pin plus its correction inputs), F3, F8 census, resolve, quote lane and Droṇa (live pin), F8 presence and verify (inherited pin), and F7 resolve (live pin plus the pool's pin). F2, F3, F4, F4b and the F8 census were re-run at `f4c08c57` and are byte-identical under `PYTHONHASHSEED=1` and `=2`. What moved: A10 §4.2 null 256 vs 102.8 (lift 2.49, p ≈ 4×10⁻⁴¹) → 260 vs 103.3 (lift 2.52, p ≈ 1.5×10⁻⁴²). The 2/123 direct test, §3.3 and §4.3 are unchanged at the precision printed. The §6 DCS arm on 598 candidates resolves 1, the same `CAURAP. (A.) 49` (567 have a DCS text, 293 Harivaṃśa numbers exceed DCS). **A correction:** the 565 Harivaṃśa rows are *not* identical to June. 49 left the pool and 49 others entered it, so A10 now marks the §6 vulgate arm (206/565) as June-membership. The F7 vulgate arm and the F8 witness stages were not re-run, because their rights-restricted verse witnesses are absent on this Mac. Pins 83 → 95 tests.
- **H5264 F7 vulgate arm and the F8 witness stages re-run at `csl-orig@f4c08c57` (22-09-2026, Claude Code Opus 5.5 `claude-opus-5-5`).** The rights-restricted witnesses were re-staged locally (gitignored, never committed): the Harivaṃśa vulgate by re-harvest, which reproduces the June 15,364 verses exactly, and the MBh vulgate + BORI critical text from the CommentaryStrategies local-only branch. `f7_harivamsa_resolve.py`, `f8_mbh_resolve.py`, `f8_mbh_presence.py`, `f8_mbh_quote_lane.py` and `f8_mbh_drona_fitted_index.py` are byte-identical under `PYTHONHASHSEED=1` and `=2`. The F8 outputs are also content-identical between the Windows box and the Mac. The §6 vulgate arm on the pinned 598-row pool: **207/565 corroborated (37.9 % of 546 evaluable, ≈ 74× null)**, up from June's 206 (37.7 %). Index validation is unchanged (68.4 % vs 2.1 %). F8 moved slightly: held-out 0.552 → 0.526, note loci 409/787/1,270 → 391/790/1,285. Droṇa is unchanged. No verdict changes. Article 21 §1/§4/§6/§7 dropped the June-membership caveat on the vulgate arm. A10 "Re-pinned 22-09-2026" item 3 and the three witness census docs carry the pinned figures. Still unpinned: F8 verify (its GRETIL `mbh_*_u.htm` witness is absent on both boxes) and F10 (offline-MT engine and cache absent).
- **H5264 follow-up: F8 verify pinned at `csl-orig@f4c08c57` (23-09-2026, Claude Code Opus 5.5 `claude-opus-5-5`).** The 18 public GRETIL `mbh_*_u.htm` BORI files were re-downloaded into SamudraManthanam's gitignored mirror (72,771 verses). `mbh_note_verdicts.csv` now inherits the pin. The run exposed a `PYTHONHASHSEED` dependence in `f8_mbh_verify.py`: a fuzzy-coverage tie between verses went to whichever verse set-iteration order met first. Ties now resolve to the earliest verse, and the output is byte-identical under `=1` and `=2` and from a cold cache. 32 `bori_locus` values moved; every evidence tier and verdict across the 2,466 notes is unchanged, and so is `f8_verify_report.json` apart from its new revision field. Article 21 §7 and A10 item 3 updated; F10 is now the only unpinned `csl-orig` stage.
- **Student guide for the community review pool, in Russian (H5310, 24-09-2026, Claude Code Fable 5.1 `claude-fable-5-1`).** New [docs/REVIEW_POOL_STUDENT_GUIDE.ru.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_POOL_STUDENT_GUIDE.ru.md) (+ `.meta.md`, README link): for each of the three pool packets — R2 checkpoint ×10, H4 semantic field ×105, xref shared-core ×40 — what the card shows, what the question asks and does not ask, the label vocabulary in plain Russian, a step procedure, worked examples from real rows with recorded answers, and the when-unsure rule; shared preamble on the sheet UI, blind double-keying, Cologne markup and SLP1→IAST. Source-reading for the xref examples found the MW edge present in all four rows the packet flags as «missing in MW» (`Akzit` L22386 «cf. a/nAkzit», `ArAt` L26162 «cf. Are/», `BaMsas` L147529 «cf. Basa/d» — accented targets; `Darmya` L100511 «cf. -DArmyAyaRa» in a continuation sub-record); recorded in the metadoc, extractor unchanged.
## [0.19.2] - 2026-09-08
### Changed

- **Correction-loci packet rebuilt against the current sibling feed (H4178
  flip 1, 06-09-2026).** `npm run build-correction-feed` re-run green against
  the pinned csl-corrections feed
  ([correction_loci.source.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/corrections/correction_loci.source.json)):
  61,430 records · 16 dicts · human 31,377 / bulk 30,053 · pc-resolved 39,531 —
  packet refresh only (date-span advance to 2026-08-04; structure unchanged).
  Confirms the csl-corrections → csl-atlas `correction_loci.tsv` feed live
  end-to-end (consumer shipped in #294, rebuilt #331).

### Added

- **Arithmetic and null-test pins for the nine highest-claim forensic scripts
  (H4352, 08-09-2026).** New offline pytest suite
  [`tests/forensic/`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic)
  (`npm run test-forensic-pins`, CI job `forensic-pins` in
  [test.yml](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/.github/workflows/test.yml)):
  f0 · f4 · f4b · f9 · f1 · f10 · f3 · f2 · f5 plus the `parse_cslorig` foundation,
  each with a hand-computed miniature csl-orig-shaped fixture, a null fixture that
  must report zero shared items, and off-by-one pins on every population count the
  script prints — 48 tests, every expected value hand-derived in the test docstring,
  an autouse socket guard proving no network, no live `../csl-orig` read. Coverage
  table, the 14 scripts left unpinned and why, and three script quirks surfaced
  (f4b crashes without scipy, f5 drops a 0.0 Petersburg row from its mean, f1
  hard-codes a `pw` cache) in
  [FORENSIC_CLAIM_PINS_COVERAGE_08-09-2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/FORENSIC_CLAIM_PINS_COVERAGE_08-09-2026.md).
- **First real consumer of the IndologyScholars
  [meso_discipline_crosswalk.csv](https://github.com/gasyoun/IndologyScholars/blob/main/curation/meso_discipline_crosswalk.csv)
  — atlas discipline-coverage packet + page (H4178 flip 3, ruling F5c slot
  discharged, 06-09-2026).** `npm run build-discipline-coverage` joins the
  atlas's 43-dict inventory through a reviewed dict→meso assignment layer
  ([`dict_meso_assignments.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/disciplines/dict_meso_assignments.json))
  to the ratified discipline taxonomy
  ([`disciplines.csv`](https://github.com/gasyoun/IndologyScholars/blob/main/curation/disciplines.csv),
  D1 10-07-2026) — taxonomy never re-derived, sha-pinned in
  [`discipline_coverage.source.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/disciplines/discipline_coverage.source.json);
  38 dicts assigned (sanskritology 33, buddhology 1, vedic→sanskritology 2,
  epic→sanskritology/literature 1, epigraphy→history_archaeology 2,
  plants→religious_studies 2), 5 honestly unassigned; 8 NOT-MAPPED sentinel
  rows surfaced. Validator `npm run validate-discipline-coverage` (CI-safe,
  sibling cross-check when present). Page:
  [/tools/discipline-coverage](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/discipline-coverage.md).
  `git grep meso_discipline_crosswalk` now returns the consuming call.

### Changed

- **METALEX L8 checkbox ticked: every entry linked to scan page — atlas side
  complete at 99.97% (A07 roadmap-drain re-pass, 04-09-2026).** Re-measured at
  the current sibling-csl-orig `origin/main` snapshot: 1,506,391 entries ·
  1,505,884 atlas-resolvable (**99.97%**) — totals identical to H3725's
  03-09-2026 run, stable with no upstream drift. `test/cologne-links.test.mjs`
  22/22 green. Honest split: the residual 0.03% is not an atlas gap — `nmmb`
  (506 entries) waits on upstream scan-image upload (every embedded pdf 404s;
  the atlas rule is ready the day the images land), 2 entries repo-wide lack
  `<pc>` in csl-orig itself. Census re-confirmed:
  [data/metalex/L8_SCAN_LINK_CENSUS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/metalex/L8_SCAN_LINK_CENSUS.md) ·
  roadmap: [docs/METALEXICOGRAPHY_ROADMAP.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/METALEXICOGRAPHY_ROADMAP.md)
  (L8 box ticked; §7.2 32-dict/63.96% snapshot refreshed to 44 dicts/99.97%).

- **L8 scan-link coverage 92.42% → 99.97%: `COLOGNE_SCAN_DIR` extended 40 → 44
  dicts with the `pui`/`vei`/`acc`/`skd` multi-volume rules (H3725, Atlas L8
  next multivolume slice, 03-09-2026).** `pui` (17,512 entries), `vei` (3,834),
  `acc` (49,833) and `skd` (42,531) now resolve to live Cologne scan pages at
  100% — 113,710 of the 114,216-entry 5-dict gap closed; the four all join
  `MULTI_VOLUME_DICTS` (H839). `<pc>` is shape-pure per dict: pui/vei are
  PWG's verbatim `{vol}-{page}` contract (vol 1..3 / 1..2); acc is
  `{vol}-{page},{col}` (vol 1..3) — a new multi-volume comma-column
  alternative strips the trailing chunk (`1-618,1` → `1-618`); note the H839
  trap acc would have hit under the single-volume rule, whose page-column
  matcher returns `1` — volume-as-page for every entry — the `MULTI_VOLUME`
  gate is what makes acc resolvable at all; skd is pw/pwkvn's three-part
  vol-page-col family (vol 1..5) with 30 letter-break stragglers
  `2-486-a1`..`-c1` whose tail is letters-then-digit (the A08-follow-up
  ap/md letterThenDigit class on the MV tail, `2-486-a1` → `2-486`).
  `redo_cologne_all.sh` maps all four to `{DICT}Scan/2020` (`dictparms.py`
  dictyear 2020 — no `COLOGNE_SCAN_YEAR` entry). Live evidence 03-09-2026,
  one sequential `servepdf.php` probe per dict, each embedded pdf also
  HEAD-checked 200, plus one residual-shape probe: pui `page=2-444` →
  `pg2_444.pdf`, vei `page=2-015` → `pg2_015.pdf`, acc `page=1-618` →
  `pg1_618.pdf`, skd `page=3-122` → `pg3_122.pdf` (straggler page `2-486` →
  `pg2_486.pdf`). **Guarded exclusion remains**: `nmmb` (506 entries) —
  re-tried this pass; the `NMMBScan/2026` servepdf.php viewer shell now
  answers 200 (A11's flat failure has healed) but every embedded pdf it
  names 404s (`pdfpages/pg0001/0020/0100.pdf` and the `NMMBScanpdf/`
  variant) — the scan images behind the tree are absent, so it stays out
  rather than link to dead targets; upstream-scan-images gap, not an atlas
  rule. Census regenerated (1,505,884 / 1,506,391 = 99.97%):
  [data/metalex/L8_SCAN_LINK_CENSUS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/metalex/L8_SCAN_LINK_CENSUS.md) ·
  map: [scripts/lib/cologne-links.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/cologne-links.mjs) ·
  roadmap: [docs/METALEXICOGRAPHY_ROADMAP.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/METALEXICOGRAPHY_ROADMAP.md) ·
  typology packet regenerated with the new L8 flags:
  [src/data/dicts/richness-typology.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dicts/richness-typology.json).

## [0.19.1] - 2026-08-30
### Changed

- **L8 scan-link coverage 79.30% → 92.42%: `COLOGNE_SCAN_DIR` extended 38 → 40
  dicts with the `pw`/`pwkvn` three-part vol-page-col rule (H3695, Atlas L8
  bounded slice, 29-08-2026).** `pw` (170,556 entries) and `pwkvn` (24,976)
  now resolve to live Cologne scan pages at 100%. Their `<pc>` is PWG's
  vol-Spalte (H839) plus a trailing column marker on the same page —
  `N-N-a/b/c/d` dominant, plus per dict 19 letter-break stragglers
  `7-384-1a`..`-1d` (the A08 bop digit-then-letters class) and 1 digit-only
  marker `7-366-1` (the ap90 digit-marker class); vol ∈ 1..7, and 100% of both
  dicts' `<pc>` values are that one shape family. servepdf.php still has no
  vol= parameter, so `scanPageFromPc`'s multi-volume branch now strips the
  trailing marker and returns `{vol}-{page}` verbatim — the H839 bare-page
  refusal is untouched, and a bare page still never silently resolves to
  volume 1. `redo_cologne_all.sh` maps pw → `PWScan/2020` and pwkvn →
  `PWKVNScan/2020` (`dictparms.py` dictyear 2020 for both). Cologne was
  source-health-probed up (200 GO) before the fetches; live evidence, one
  sequential `servepdf.php` probe per dict plus one residual-marker probe:
  pw `page=7-385` → working scan-viewer shell embedding `pw7-385.pdf`
  (marker page `7-384` → `pw7-384.pdf`), pwkvn `page=2-288` → working shell
  embedding `pw2-288N.png`. **Guarded exclusions now**: `pui`/`vei`/`acc`
  (volume first-field), `skd` (same vol-page-col family — kept for a later
  pass with its own spot-check), `nmmb` (broken probe, A11). Census
  regenerated at this pass's snapshot (1,392,174 / 1,506,391 = 92.42%; the
  remaining 5 outside dicts — acc, nmmb, pui, skd, vei — hold 114,216 entries
  and are the dominant gap):
  [data/metalex/L8_SCAN_LINK_CENSUS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/metalex/L8_SCAN_LINK_CENSUS.md) ·
  map: [scripts/lib/cologne-links.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/cologne-links.mjs) ·
  roadmap: [docs/METALEXICOGRAPHY_ROADMAP.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/METALEXICOGRAPHY_ROADMAP.md) ·
  typology packet regenerated with the new L8 flags:
  [src/data/dicts/richness-typology.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dicts/richness-typology.json).

## [0.19.0] - 2026-08-29
### Changed

- **U7 typology chip on the xref shared-core sheet; population share ruled
  genuinely unknown (H3091, 29-08-2026).** `csl-atlas-xref-shared-core_40edges`
  pre-classifies — the card opens with `Предложение: lexical-shared-core` and
  asks the reviewer to confirm that class — so U7 (H2846) applies, even though
  the card's plain `badges` are provenance tags, not a class chip. The share is
  `share_unknown` **by ruling, not by omission**: the population is the 641-edge
  MW∩PWG intersection, no label distribution over it exists (the vote is what
  produces the label), and the 40 rows are `sharedEdges.slice(0, 40)` in headword
  order, so no rate from them generalises. Every card now carries
  `lexical-shared-core (n=40, share unknown)` plus a Russian note naming both
  denominators (641 population / 601 unlabelled) and the sampling bias. Two
  defects found while regenerating: the script had been **unbuildable on `main`**
  against csl-pyutil >= 0.16.0 (`render_review_sheet` requires an H1649
  `screening=` block; `xref_screening()` now supplies it from the packet's own
  counters — the three ✅ closed sheets are deliberately left unbuilt rather than
  given invented counts), and the blurb's "642 общих рёбер" was
  `xref_shared_edges.csv`'s line count *including the header* — the intersection
  is **641**, now counted rather than hardcoded. Emitter floor 0.6.0 → 0.16.0.
  Evidence: 40 `badge-typology` spans == 40 cards, zero `n=None`.
  Generator: [scripts/build-review-sheets.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-review-sheets.py) ·
  standard: [Uprava docs/REVIEW_SHEET_CONTENT_STANDARD_2026.md](https://github.com/gasyoun/Uprava/blob/main/docs/REVIEW_SHEET_CONTENT_STANDARD_2026.md) §8

- **L8 scan-link coverage 64.31% → 79.30%: `COLOGNE_SCAN_DIR` extended 33 → 38
  dicts + three `scanPageFromPc` alternatives (A08 follow-up, H2368 roadmap
  follow-on, 29-08-2026).** `ap`, `ccs`, `lrv`, `md`, `sch` (~224k entries)
  now resolve to live Cologne scan pages at 100%. Verification per the
  A11/A12/A07 bar: `redo_cologne_all.sh` maps ap/ccs/md/sch to `{DIR}Scan/2020`
  and lrv to `LRVScan/2022` (`dictparms.py` still says 2020 for lrv — same
  year-mismatch class as nybj; the live 2022 path answers), per-dict `<pc>`
  first-fields grow like real continuous page numbers with no volume
  component, and one sequential `servepdf.php` live probe per dict plus one
  residual-shape probe for each new rule answered with the working
  scan-viewer shell. New alternatives: ap/md letter-then-digit (`0379-a1` →
  page `0379`), sch unseparated-page-then-column (`104a-1` → page `104`),
  lrv dotted-column (`120-12.1` → page `120`); ccs's `038-1a` already matched
  the A08 bop letter-break rule. `lrv` added to `COLOGNE_SCAN_YEAR` as 2022.
  **Guarded exclusions unchanged**: `pui`/`vei`/`acc` (volume first-field) and
  `pw`/`pwkvn`/`skd` (three-part vol-page-col, first-field ∈ 1..7) — H839;
  `nmmb` stays out (broken probe, A11). Census regenerated
  (1,186,408 / 1,496,157 = 79.30%; 309,748 entries in the remaining 7
  outside dicts are the dominant gap):
  [data/metalex/L8_SCAN_LINK_CENSUS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/metalex/L8_SCAN_LINK_CENSUS.md) ·
  map: [scripts/lib/cologne-links.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/cologne-links.mjs) ·
  roadmap: [docs/METALEXICOGRAPHY_ROADMAP.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/METALEXICOGRAPHY_ROADMAP.md) ·
  typology packet regenerated with the new L8 flags:
  [src/data/dicts/richness-typology.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dicts/richness-typology.json).

- **L8 scan-link coverage 48.11% → 63.96%: `COLOGNE_SCAN_DIR` extended 21 → 32
  dicts + gra's unseparated page-column rule (A07, H2368 roadmap follow-on,
  28-08-2026).** `ben`, `gst`, `inm`, `lan`, `mci`, `mw72`, `mwe`, `nybj`,
  `pe`, `shs`, `yat` (~244k entries) now resolve to live Cologne scan pages,
  and gra's 23 unseparated `NNNa` `<pc>` stragglers resolve too (gra now
  100%). Verification per the A11/A12 bar: `redo_cologne_all.sh` maps all
  eleven to `{DIR}Scan/2020`, per-dict `<pc>` first comma-fields grow like
  real continuous page numbers, and one sequential `servepdf.php` live probe
  per dict answered with the working scan-viewer shell. `nybj` deploys at
  year 2026 per `csl-websanlexicon/v02/dictparms.py` (its redo-script 2020
  path 404s live) — added to `COLOGNE_SCAN_YEAR`. The unseparated rule
  (`0307a` → page `0307`) exists in no other local dict per a full census.
  **Guarded exclusions**: `pui`/`vei`/`acc` lead their `<pc>` with a
  volume-like field (structurally PWG's vol-Spalte, H839) — left out rather
  than emit `?page=1..3` for every entry; each needs its own multi-volume
  rule + spot-check. `nmmb` stays out (broken probe, A11). Census
  regenerated (963,510 / 1,506,391 = 63.96%; local csl-orig grew to
  1,506,391 entries since A12's 1,496,157 — acc/ap/ben landed in between;
  542,880 entries in the remaining 13 outside dicts are the dominant gap):
  [data/metalex/L8_SCAN_LINK_CENSUS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/metalex/L8_SCAN_LINK_CENSUS.md) ·
  map: [scripts/lib/cologne-links.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/cologne-links.mjs) ·
  roadmap: [docs/METALEXICOGRAPHY_ROADMAP.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/METALEXICOGRAPHY_ROADMAP.md) ·
  typology packet regenerated with the new L8 flags:
  [src/data/dicts/richness-typology.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dicts/richness-typology.json).

- **L8 scan-link coverage 38.99% → 48.11%: `COLOGNE_SCAN_DIR` extended 15 → 21
  dicts (A12, H2368 roadmap follow-on, 28-08-2026).** `bur`, `stc`, `vcp`,
  `ae`, `bhs`, `gra` (~136k entries) now resolve to live Cologne scan pages.
  Verification follows the A11 two-step bar: `redo_cologne_all.sh` maps all
  six to `{DICT}Scan/2020`, and each dict's own `-meta2.txt` documents `<pc>`
  as a page-col reference with continuous numbering and no volume component
  (only PWG carries vol-Spalte, H839) — so the existing single-volume
  `scanPageFromPc` paths apply verbatim. One sequential `servepdf.php` live
  probe per dict (ae/gra passed on retry after transient transport errors).
  Residuals recorded in the roadmap: gra 99.82% (23 unseparated `NNNa`
  entries = named next increment), ae 99.99% (its one missing-`<pc>` entry).
  Census regenerated:
  [data/metalex/L8_SCAN_LINK_CENSUS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/metalex/L8_SCAN_LINK_CENSUS.md) ·
  map: [scripts/lib/cologne-links.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/cologne-links.mjs) ·
  roadmap: [docs/METALEXICOGRAPHY_ROADMAP.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/METALEXICOGRAPHY_ROADMAP.md).

## [0.18.0] - 2026-08-28
### Changed

- **One authoritative version surface, and Wave 3's researcher-first navigation
  (H3604, Opus 5 `claude-opus-5`, 28-08-2026).** Two long-standing public
  defects that [H3002](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3002-Opus_multi_stale-roadmap-s4-cologne-ask-replan_17.08.26.md)
  measured but deliberately did not execute, because each needed a build rather
  than a documentation edit.
  - The site footer in
    [`observablehq.config.js`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/observablehq.config.js)
    carried a hardcoded version literal, public on every page since 17-07-2026,
    while the newest release tag and `package.json` each said something
    different - three surfaces, three answers, and the one the public reads was
    the most wrong. `package.json` is now the single source (set to the newest
    existing tag, not an invented number) and the footer interpolates it; no
    version literal is left in the config. Live-Pages footer verified after
    deploy. ([PR #422](https://github.com/sanskrit-lexicon/csl-atlas/pull/422))
  - Navigation re-grouped from 10 build-phase sections into the seven
    researcher-task sections Wave 3 of
    [`docs/ROADMAP_2026_2027.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/ROADMAP_2026_2027.md)
    prescribes by name, and the two routes listed twice
    (`/tools/reader-lookup`, `/tools/dictionary-dossier`) are now listed once
    each. Route-preserving: 71 entries / 69 distinct before, 69 / 69 after,
    zero routes lost or added.
    ([PR #423](https://github.com/sanskrit-lexicon/csl-atlas/pull/423))

## [0.17.4] - 2026-08-24
### Fixed

- **METALEX L8 — ap90 reaches 100% atlas-resolvable scan links, closing the
  digit-marker residual A10 left open (H2368-A11 follow-up, Sonnet 5
  `claude-sonnet-5`, 24-08-2026).** A10's L8 fix taught `scanPageFromPc` to
  strip ap90's page-column-letter `<pc>` shape (`NNNN-a/b/c`) but left 246
  entries unresolved, whose `<pc>` uses a digit instead of a letter
  (`NNNN-N`, e.g. `0220-1`, `0351-2`). Tracing those entries in
  `csl-orig/v02/ap90/ap90.txt` shows the digit shows up exactly at
  new-letter section breaks — page 0220 runs `-a,-b,-c` then restarts as
  `-1` where headwords starting with `A` begin — the same "trailing chunk
  is a column marker, not a volume" shape as the letter case.
  [`scripts/lib/cologne-links.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/cologne-links.mjs)
  now accepts an all-digit trailing marker alongside the all-letter one (a
  mixed chunk like `x0` still stays unresolved — no shape invented beyond
  what's observed), mirrored in
  [`scripts/metalex/l8_scan_link_census.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/metalex/l8_scan_link_census.py).
  L8 census re-measured on top of A11's 12-dict extension: atlas-resolvable
  Cologne scan URLs **583,143 → 583,389** (38.98% → 38.99%); ap90 **99.29% →
  100%**. L8 minimum stays unchecked — the dominant gap (912,767 entries
  across the 29 dicts still outside `COLOGNE_SCAN_DIR`) is unaffected and
  needs per-dict Cologne scan-directory verification, still out of scope
  for this pass. Report:
  [`data/metalex/L8_SCAN_LINK_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/metalex/L8_SCAN_LINK_CENSUS.md).

## [0.17.3] - 2026-08-24
### Added

- **METALEX L8 — 12-dict `COLOGNE_SCAN_DIR` extension (H2368-A11, Sonnet 5
  `claude-sonnet-5`, 24-08-2026).** The L8 census's dominant gap was 41 dicts
  outside the atlas's verified Cologne scan-directory map — A10 scoped
  further extension out as needing "per-dict Cologne scan-directory
  verification." That verification source turned out to already exist:
  `csl-websanlexicon/v02/redo_cologne_all.sh`, the production script that
  deploys the live Cologne site, names the exact `{DICT}Scan/{year}` folder
  for every dict. Of the 41 gap dicts, 13 have a `<pc>` that is always a bare
  integer (no volume/column suffix, so none of the H839 "silently defaults to
  volume 1" risk that blocks a naive PWG-style extension) — `wil, cae, bor,
  fri, ieg, armh, krm, abch, pgn, snp, acsj, acph, nmmb`. Each was spot-checked
  live, one sequential `servepdf.php` fetch per dict (not a burst — this host
  429s, Uprava `SERVER_OUTAGES.md`): 12 resolved a real scanned page; `nmmb`
  (`NMMBScan/2026`, per `SanskritLexicography/FINDINGS.md` §50) returned a
  broken response and was left **out** of `COLOGNE_SCAN_DIR` rather than
  guessed at. New `COLOGNE_SCAN_YEAR` map in
  [`scripts/lib/cologne-links.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/cologne-links.mjs)
  carries the non-2020 deploy years (`fri` 2025; `abch`/`acsj`/`acph` 2023)
  that `redo_cologne_all.sh` records for those dicts; `entryUrl`/`scanUrl` now
  build both link shapes from it instead of hardcoding `/2020/`. Re-running
  [`scripts/metalex/l8_scan_link_census.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/metalex/l8_scan_link_census.py)
  moves the overall L8 figure from 29.71% → **38.98%** (444,527 → **583,143**
  atlas-resolvable entries; the `pc_present_no_cologne_scan_dir` gap shrinks
  from 1,051,383 to **912,767** across 29 remaining dicts).
  [`scripts/build-richness-typology.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-richness-typology.mjs)
  regenerated: the 12 dicts now show `l8.met = true` at dict level. New
  `COLOGNE_SCAN_DIR`/`scanUrl` cases in
  [`test/cologne-links.test.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/test/cologne-links.test.mjs).
  Roadmap L8 checkbox and
  [`data/metalex/L8_SCAN_LINK_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/metalex/L8_SCAN_LINK_CENSUS.md)
  updated — **still not** L8-complete; the remaining 29 dicts have non-trivial
  `<pc>` shapes (page-column-letter, page-comma-column-letter, multi-part) that
  each need their own `scanPageFromPc` rule plus a live spot-check, out of
  scope for this pass.

## [0.17.2] - 2026-08-24
### Added

- **H2891 — the human review overlays now carry a committed digest, and CI goes
  red when one is wiped** (Opus 5 `claude-opus-5`, 17-08-2026). The H2890 census
  measured something worth stating plainly: of the **19,368** records in
  `src/data/review/`, **147** carry a human review *status*, and only **10** are
  attributed to a human — 130 to `codex`, 7 to `Antigravity`. A predicate using
  the status half alone would over-claim human review **14.7×**, which is
  [H1684](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/CHANGELOG.md)
  in numbers. More pointedly: **all 10 of the real human rulings live in one
  file**, `r2-checkpoint-review.json` — precisely the file whose builder carries
  the registered destructive path, since
  [`build-r2-checkpoint-review.mjs --reseed`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-checkpoint-review.mjs)
  sets the preserved map to empty and overwrites every decision with the machine
  seed. The other 13 generators call `loadPreserved` and are overlay-preserving.
  This repo's entire human review corpus therefore sat behind exactly one
  unguarded flag, with nothing watching it. New
  [`data/integrity/csl_atlas_review.pin.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/integrity/csl_atlas_review.pin.json)
  pins two SHA-256 digests over the reviewed projection — content and key-set,
  because a `--reseed` moves both while an in-place edit moves only the first —
  with a per-file digest so a red run names the report that changed rather than
  printing one hash for fourteen. The predicate rides in the pin as data, not
  code, and the hasher is the shared
  [`csl_pyutil.integrity_tripwire`](https://github.com/sanskrit-lexicon/csl-pyutil/pull/28)
  rather than a local copy. New
  [`overlay-tripwire.yml`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/.github/workflows/overlay-tripwire.yml)
  runs it per PR, weekly, and on dispatch, and carries a **negative control**
  that reproduces the `--reseed` outcome in a scratch copy (10 → 0 reviewed
  records) and fails the job if the gate stays green — the real seeder is never
  invoked, because "never `--reseed`" is this repo's own danger fact and CI is
  not the place to make an exception to it. Detection only; the refuse-by-default
  hatch on `--reseed` itself is H2892.

### Fixed

- **METALEX L8 — ap90 scan-page pc-shape gap (H2368-A10, Sonnet 5
  `claude-sonnet-5`, 24-08-2026).** `scanPageFromPc` in
  [`scripts/lib/cologne-links.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/cologne-links.mjs)
  only trusted a bare-digit or `page,column` `<pc>` shape, so every ap90 entry
  — whose `<pc>` is `NNNN-a`/`NNNN-b`/`NNNN-c` (page-column-letter) — silently
  failed to resolve despite ap90 being in `COLOGNE_SCAN_DIR`. Now strips the
  trailing column letter(s) and keeps the page digits verbatim; mw and pwg
  parsing is untouched. Re-running
  [`scripts/metalex/l8_scan_link_census.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/metalex/l8_scan_link_census.py)
  moves ap90 from 0% → **99.29%** atlas-resolvable (34,636 more entries) and the
  overall L8 figure from 27.40% → **29.71%**; a residual 246 ap90 entries use a
  distinct `NNNN-N` numeric-suffix `<pc>` shape not yet understood, left
  unresolved rather than guessed at. New
  [`test/cologne-links.test.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/test/cologne-links.test.mjs)
  covers mw/pwg/ap90 `scanPageFromPc`/`scanUrl` contracts. Roadmap L8 checkbox
  and
  [`data/metalex/L8_SCAN_LINK_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/metalex/L8_SCAN_LINK_CENSUS.md)
  updated with the new measurement — **still not** L8-complete; the dominant
  gap (1,051,383 entries, 41 dicts outside `COLOGNE_SCAN_DIR`) is unchanged and
  needs per-dict Cologne scan-directory verification, out of scope here.

### Changed

- **H2820 — CLAUDE.md truth-pass** (Grok 4.6 `grok-4.6`, 16-08-2026). Dated
  header, what/run/don't, primer + DANGER_FACTS pointers; AGENTS.md twin
  regenerated from the new TOC. Taxonomy tables not recopied.

### Added

- **H2892 — `--reseed` now refuses instead of asking to be trusted** (Opus 5
  `claude-opus-5`, 17-08-2026). `npm run build-r2-checkpoint-review -- --reseed`
  skips `loadPreserved` and blanks the human review overlay back to the machine
  seed. That has been a registered do-not-run danger fact in prose since it was
  written; it is now a gate. The flag exits **2** and writes nothing unless
  `ALLOW_OVERLAY_WIPE=1` is set, and the hatch is an exact match on `1` —
  `true`, `yes`, an empty value all still refuse, because a half-set hatch must
  not read as consent. The stakes the H2890 census measured: of 19,368 review
  rows, 147 carry a `reviewed-*` status and only **10** are human-attributed
  (130 codex, 7 Antigravity), so a careless reseed loses ten irreplaceable
  rulings while looking like a routine rebuild. The lock lives in
  [`scripts/lib/review-report.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/review-report.mjs)
  (`refuseReseedWithoutHatch`), not in the one generator, so a future queue that
  grows a `--reseed` inherits it. The **overlay-preserving rebuild is
  unchanged** and stays the normal path — a guard that refused everything would
  just move the damage from the data to the pipeline, so
  [`test/reseed-lock.test.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/test/reseed-lock.test.mjs)
  asserts all three directions: refusal exits 2 with the committed report
  SHA-256-identical, a plain rebuild carries every human ruling forward verbatim,
  and a *hatched* reseed still does what it says on the tin. The two end-to-end
  cases run in a temporary tree, never against `src/data/review/`.

- **METALEX L8 entry-level scan-page link census (H2368, Grok 4.5 `grok-4.5`,
  07-08-2026).** Stdlib script
  [`scripts/metalex/l8_scan_link_census.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/metalex/l8_scan_link_census.py)
  measures local csl-orig: **1,496,157** entries · **99.9999%** with non-empty
  `<pc>` · **27.40%** atlas-resolvable Cologne scan URLs (mw+pwg at 100%; ap90 in
  `COLOGNE_SCAN_DIR` but 0% under digit-only page extract). Report:
  [`data/metalex/L8_SCAN_LINK_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/metalex/L8_SCAN_LINK_CENSUS.md)
  (+ JSON). Roadmap L8 checkbox annotated with measured % — **not** claimed complete.
  No mass link invention.

## [0.17.1] - 2026-08-06
### Fixed

- **Re-green `main`: R2 drift-explanation golden fixture regenerated (H2292, Sonnet 5
  `claude-sonnet-5`, 06-08-2026).** `test/fixtures/R2_DRIFT_EXPLANATION.machine-only.md`
  drifted against `scripts/build-r2-drift-explanation.mjs` when
  [PR #335](https://github.com/sanskrit-lexicon/csl-atlas/pull/335)'s org-wide link
  auto-fix rewrote the fixture's 5 vocabulary links to a `docs/`-prefixed form, as if the
  fixture file lived at its own path (`test/fixtures/`). The generator's
  `docsRelativeHref()` strips the `docs/` prefix on purpose — the real committed doc,
  `docs/R2_DRIFT_EXPLANATION.md`, sits *inside* `docs/`, so a sibling link to
  `docs/R2_*_LABELS.md` is correctly bare-filename relative from there (confirmed against
  the live committed doc's own links). Regenerated the fixture with the one-liner already
  documented in the test file's own comment; no code change. Closes
  [csl-atlas#337](https://github.com/sanskrit-lexicon/csl-atlas/issues/337).

## [0.17.0] - 2026-08-05
### Added

- **A68 paper draft: "How representative is DCS of the Sanskrit lexicographic canon?"
  (H1867, Fable 5 `claude-fable-5`, 05-08-2026).** The H1336 PD–DCS crosswalk measurement
  is now a venue-shaped paper draft —
  [`papers/A68_DCS_REPRESENTATIVENESS_PD_CANON.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/papers/A68_DCS_REPRESENTATIVENESS_PD_CANON.md)
  — with abstract, explicit canon-membership criteria (§4.1: the frequency-weighted set of
  works PD's published a-volumes cite as `primary`), methods, results (25.2 %
  citation-weighted vs 77.9 % token-weighted; 118 of ~2,445 works; +3.8 pp Vedic-led
  2021→2026 closure), discussion, and limitations. Four figures are committed under
  [`papers/figures/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/papers/figures)
  and regenerate deterministically via
  [`scripts/build_a68_figures.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build_a68_figures.py),
  which re-derives all 12 headline values from the row-level TSVs in
  [`data/pd/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/pd) and aborts
  on any drift from `pd_dcs_metrics.json` (cross-paper figure drift guard).

## [0.16.3] - 2026-08-05
### Added

- **Hostile referee of all nine July 2026 hypothesis promotions — zero demotions, one
  structural row repair (H1866, Fable 5 `claude-fable-5`, 05-08-2026).** Every figure
  asserted by the July-promoted rows (THREE-AXIS-INDEP, CANON-CORE, CITE-4AXIS,
  GHOST-STOCK, HERITAGE-WIT, HEAP-SAT, FREQ-STRAT, ORTHO-CLOCK, L0-GQD) in
  [`docs/HYPOTHESIS_INDEX.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/HYPOTHESIS_INDEX.md)
  was re-read from its committed JSON artifact under a default-REFUTED posture — 102
  figures checked, all match; a staleness sweep confirmed no promotion rests on an input
  regenerated after its promotion date (the 17-07 MW `<ls>` +28.6% fix touched only
  `data/obs/citation_registers.json`). Findings: the CANON-CORE index row had 7 cells
  against 8 columns (its Evidence cell was missing — restored), and it now carries the
  MW-lane caveat its own artifact already recorded (MW resolves to 5 texts in the
  ls-graph, so "none cited by all 11" is partly mechanical); the CANON-CORE-trusts /
  CITE-4AXIS-rejects split over the same ls-graph MW lane is registered as a
  cross-promotion methods contradiction in SanskritLexicography/CONTRADICTIONS.md. Full
  verdicts:
  [`docs/HYPOTHESIS_PROMOTIONS_JULY_2026_REFEREE.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/HYPOTHESIS_PROMOTIONS_JULY_2026_REFEREE.md).

## [0.16.2] - 2026-08-04
### Changed

- **`.gitattributes` LF policy widened from 38 files to the whole repo — and the org deploy
  could never have done it (Opus 5 `claude-opus-5`, 04-08-2026).** The existing attributes
  pinned `eol=lf` on **seven globs** under `data/lexico/` and `src/data/review/`, covering
  **38 of 1 078** tracked files; the other ~96 % of the repo had no line-ending policy at
  all. The gap was self-concealing in two independent ways. First, the standard detector
  (`git ls-files --eol | grep -E 'i/(crlf|mixed)' | grep 'eol=lf'`) only inspects files that
  *carry* an `eol=lf` attribute, so an unpoliced file cannot appear in it — a clean census
  result meant "no violations among the 38", not "no violations". Second, and more
  consequentially, the org-wide deploy in
  [`Uprava/tools/cologne_batch_deploy.py`](https://github.com/gasyoun/Uprava/blob/main/tools/cologne_batch_deploy.py)
  decides coverage with `gitattributes_satisfied()`, which returns `True` when the string
  `eol=lf` appears **anywhere** in the file. Those seven narrow globs therefore marked this
  repo *satisfied*, and every future run of the deploy would have skipped it — a repo can be
  96 % unpoliced and invisible to the tool built to police it. Fixed by appending the
  canonical org block (`GITATTRIBUTES_TEMPLATE`, H2004) beneath the existing rules, which
  are preserved verbatim. **`git add --renormalize` ran in the same commit and changed
  nothing**, confirming every blob was already LF: policy widened with zero content churn
  and no binary file touched. The pairing is deliberate — `.gitattributes` alone governs
  only *future* writes and leaves existing blobs contradicting the new rule, exactly how
  [csl-devanagari#52](https://github.com/sanskrit-lexicon/csl-devanagari/pull/52) was left
  behind by its own policy commit.

## [0.16.1] - 2026-08-04
### Fixed

- **Correction-loci packet resynced with the csl-corrections sibling feed (H2036, csl-atlas#331):** `validate-correction-feed` had gone red (ap90 154!=157, mw72 24!=78, `pwg` missing from the packet) after the sibling feed regenerated 01-08-2026 to 61,430 rows. Rebuilt via `npm run build-correction-feed` -- no code change, packet counts now match the sibling feed exactly for every dict.

### Added

- **ls abbreviation frequency pipeline (H1826, csl-atlas#222):** \scripts/obs/ls_abbreviation_frequency.py\ emits \data/obs/ls_abbreviation_frequency.json\ as \{dict: {token: count}}\ with provenance block; per-dict token sums match \citation_registers.json\ \ls\ totals. npm scripts \uild-ls-abbreviation-frequency\ / \	est-ls-abbreviation-frequency\; node invariant test \	est/ls-abbreviation-frequency.test.mjs\.


## [0.16.0] - 2026-07-31

### Added — citation truncation & hapax overlap (PET-MW-CITE, H1827)

- [`scripts/build-citation-truncation.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-citation-truncation.mjs)
  + [`scripts/validate-citation-truncation.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/validate-citation-truncation.mjs)
  — the roadmap's asymmetric descent test. `citation_truncation_evidence(A→B)`
  counts A's citations, on the sources both dictionaries cite ≥5 times each,
  whose locator depth exceeds B's mean depth for that source; a dictionary can
  shorten an ancestor's `Rv. 1.22.16` to `RV.` but cannot invent precision it
  never had. Paired with a hapax-overlap test on rare headwords (all headwords,
  and the shared-source headwords the roadmap names).
- [`data/lexico/citation_truncation_hapax.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/citation_truncation_hapax.json)
  + `.source.json` provenance envelope (csl-orig commit pinned), with the site
  copy wired through `scripts/sync-site-data.mjs`.
- [`src/tools/citation-truncation.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/citation-truncation.md)
  — new page under *Dictionary structure*: locator-depth composition per
  dictionary, the pairwise asymmetry chart with **within-lane control pairs**,
  a per-shared-source table and depth scatter, and the hapax table with an
  all-headwords / shared-source-headwords toggle. Trust Block, CSV download on
  every table, `Inputs.table` fallback throughout.
- Measured (29-07-2026, 5 dictionaries, 916,370 usable citations):
  `evidence(PWG→MW)` = 277,279 of 291,553 (95.1%) against 25,380 of 154,865
  (16.4%) the other way — asymmetry 0.787; all 3 testable cross-lane pairs put
  the Petersburg side deeper (0.747–0.856) against a within-Petersburg control
  band of 0.141–0.353. MW leaves 78.9% of its citations at a bare siglum, PWG
  16.4%.
- Honest shrinkage recorded in the packet, not silently absorbed: **MW72 carries
  zero `<ls>` tags** and so cannot enter the citation half at all (hapax only);
  the Petersburg lane's elliptical bare-numeral citations (`<ls>112,24</ls>`)
  have no siglum to share and are excluded and counted separately; "PW" and
  "PWK" are one digitisation in csl-orig (code `pw`), so PWKVN joins as the
  third Petersburg witness.
- `docs/HYPOTHESIS_INDEX.md` PET-MW-CITE flipped from "route" to
  direction-consistent-but-not-confirmatory, with the numbers and the standing
  caveat that locator depth reads apparatus formatting, not scholarship.

### Changed

- **`scripts/lib/cdsl_anatomy.py` is now a re-export shim over `csl_pyutil.anatomy`
  (H1808).** The entry-anatomy colouring was written here for the xref sheet (H1646)
  and could be reached from no other generator; when SanskritLexicography's G5
  print-readiness sheet needed the same treatment, MG's note on it was «why entry
  anatomy is missing again? It must be a hook». The implementation moved into the
  shared emitter package ([csl-pyutil v0.6.0](https://github.com/sanskrit-lexicon/csl-pyutil/releases/tag/v0.6.0))
  rather than being copied a second time — two hand-synced copies of one highlighter
  is the fork-drift `SHARED_CODE.md` exists to prevent. This repo keeps its own
  semantics in the shim: `<ab>` stays the bright `crossref` class (in PWG it wraps
  *every* abbreviation, so the shared default is the quieter `abbreviation`), and the
  legend keeps its original ten classes. Regenerating
  `csl-atlas-xref-shared-core_40edges_review.html` reproduces the previous sheet
  byte-for-byte apart from the emitter's new type scale and a `class="anatomy"` hook
  on the block. `requirements-review.txt` and `MIN_EMITTER_VERSION` move to 0.6.0.
- Review sheets now render at the emitter's new default type scale (+150%, MG's
  ruling while voting the G5 sheet), with an A−/A+ control in the toolbar.

## [0.15.0] - 2026-07-27

### Added — entry-anatomy radar chart (H1510)

- [`src/tools/entry-anatomy.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/entry-anatomy.md)
  — new page rendering a per-dictionary radar overlay of the `build-micro-entry`
  10-feature microstructure matrix (entry size, tagged/inline citations, grammar,
  etymology, cross-reference, homonym, division, subentry, root), selectable
  across the R2 anchor lemmas `gam`/`dharma` (SLP1 `Darma`)/`rāma` (SLP1 `rAma`)/`iti`,
  with a Trust Block and a per-lemma CSV download.
- `data/lexico/micro-Darma.json`, `data/lexico/micro-rAma.json`, `data/lexico/micro-iti.json`
  generated by `npm run build-micro-entry -- <lemma>` (previously only `gam` was committed).
- `scripts/sync-site-data.mjs` now also copies the four `micro-<lemma>.json` files into
  `src/data/lexico/` so the new page's `FileAttachment`s resolve.
- `docs/RESEARCH_LAYER_ROADMAP.md` §3 micro-viz checkbox ticked; the roadmap's "24-dim"
  figure noted as aspirational against the 10 features the generator actually implements.

## [0.14.0] - 2026-07-27

### Added — В2 agent adjudication of both remaining review sheets (H1684)

- [`docs/H1684_B2_ADJUDICATION.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/H1684_B2_ADJUDICATION.md)
  — method, results and traps for the В2 pass over `csl-atlas-skd-iti_100units` (102 units) and
  `csl-atlas-tradition-tags_119texts` (119 texts). **221 rows owed to a human → 61.**
- [`scripts/adjudicate-h1684-skd-iti.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/adjudicate-h1684-skd-iti.mjs)
  re-derives every sampled *iti*-unit from local `csl-orig/v02/skd` (29 of 102 are longer than
  the packet's 200-char excerpt, so the sample alone cannot settle them) and rules
  citational-vs-grammatical: **77 confirm · 16 corrected · 9 uncertain**.
- [`scripts/adjudicate-h1684-tradition-tags.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/adjudicate-h1684-tradition-tags.mjs)
  rules all 119 tradition tags against **both** ACC and NCC, joined through the H1657 crosswalk
  at Tier A/B only: **114 confirm · 0 corrected · 5 policy forks**.
- [`scripts/build_h1684_spotcheck_sheet.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build_h1684_spotcheck_sheet.py)
  + [`scripts/apply_h1684_spotcheck.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/apply_h1684_spotcheck.py)
  — stratified **blind** spot-check (the agent verdict is hidden from sampled cards) whose
  per-stratum sample sizes are *derived* from a Wilson-95% / 0.80 promotion floor under a
  finite-population correction, not chosen. Strata gate independently; nothing is stamped
  `reviewed=yes` without the human arm.

### Fixed — the shipped *iti*-classifier mislabels in two directions (H1684)

- **False negatives:** `SKD_AUTHORITY_HINTS` is 17 entries dominated by *text* citations, so bare
  kośa authorities opening a tail unit (halāyudhaḥ, trikāṇḍaśeṣaḥ, rājanighaṇṭuḥ ×3, durgādāsaḥ,
  sāyaṇaḥ, saṃkṣiptasāra-uṇādivṛttiḥ, medinīkara-hemacandrau) fell into `other-no-authority`.
- **False positives:** `ity[a-zA-Z]{3,}` also fires on the grammatical formulae (`ityarthaḥ`,
  `ityādi`, `ityuktāni`, `ityabhidhīyate`, `ityantam`, `ityavyayaṃ`) — explanatory, not
  citational, boundaries.
- Net effect on A02/A08: `other-no-authority` is inflated and `separable` under-counted in the
  shipped fused/separable shares.

### Changed — `tradition_tags.tsv` records review PROVENANCE, not just review (H1684)

- New `reviewed_by` column (`human` | `agent-h1684`). The old
  `allReviewed ? "human-reviewed" : …` derivation would have let promoted agent verdicts make the
  packet claim `human-reviewed` for rows no human ever read. `reviewStatus` is now three-valued
  (`inferred-pending-review` / `human-reviewed` / `agent-adjudicated-human-gated`) with a matching
  `evidenceLabel`, and
  [`validate-tradition-tags.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/validate-tradition-tags.mjs)
  fails the build on a reviewed row with no provenance, a provenance with no review, or any packet
  claiming `human-reviewed` while carrying agent-attributed rows.

## [0.13.0] - 2026-07-26

### Added — Russian companion for the xref taxonomy + a docs-vs-data drift guard (H1648)

- [`docs/XREF_SHARED_CORE_LABEL_TAXONOMY.ru.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/XREF_SHARED_CORE_LABEL_TAXONOMY.ru.md)
  — full Russian companion to the English taxonomy doc, so the reviewer-facing reference
  matches the (already Russian) review sheet. Org filename convention `.ru.md`.
- [`test/xref-taxonomy-docs.test.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/test/xref-taxonomy-docs.test.mjs)
  (5 tests) pins **both** companions to the committed data: every load-bearing figure must
  match `xref_marker_agreement.json` / `xref_source_check_packet.json` / the shared-edge CSV,
  every sheet-applicable label must be covered, neither file may re-assert the retracted
  independence justification outside its retraction section, and the `.ru.md` must actually
  be Cyrillic. Two prose companions in two languages are exactly what goes stale silently;
  now that fails CI instead.

### Fixed — the shared-edge candidate pool is 641, not 642

The drift guard caught it on first run. The figure was a `wc -l` that counted
`xref_shared_edges.csv`'s header as a data row, and it had propagated into the packet's
`selectionPolicy`/`limitations`, both prose companions, the review sheet, FINDINGS §466 and
several PR bodies. `build-xref-source-check-packet.mjs` now **computes** the pool size
(`sharedEdgePoolSize()`) rather than carrying a literal, so it cannot drift again. Also
removed a leftover "Two independent editors recorded the same by-form link" line in the
English doc that had survived the H1648 retraction.


## [0.12.0] - 2026-07-26

### Added — GQD validation of the L0 convention stemma (H1578)

- **`npm run build-l0-gqd` + `validate-l0-gqd`**
  ([`scripts/L0/s7_gqd.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/L0/s7_gqd.py),
  [`scripts/validate-l0-gqd.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/validate-l0-gqd.mjs)):
  Generalized Quartet Distance (Pompei, Loreto & Tria 2011 eq. 8, the tree-evaluation
  metric of Rama, List, Wahle & Jäger 2018) scored over the committed L0 trees against
  two expert references, neither built from convention characters. Re-implemented from
  the published definition — four-point condition on unit-weight topological distances,
  no phylogenetics dependency — with a 999-permutation leaf-shuffle null, deterministic
  seed, and a 21-check `--selftest`. Outputs
  [`data/L0/gqd_report.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/L0/gqd_report.json),
  `gqd_validation.csv`, `gqd_clade_recovery.csv`, `gqd_tree_matrix.csv` and the gold trees
  under [`data/L0/gold/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/L0/gold)
  (with a per-group documentary-warrant CSV). Re-running reproduces all four outputs
  byte-for-byte.
- **[`docs/L0_GQD_VALIDATION.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/L0_GQD_VALIDATION.md)**
  (+ `.meta.md`): the published convention stemma agrees with **85.4% of the
  documented-descent quartets** (GQD 0.1456 vs a null of 0.666 ± 0.068, z=−7.67,
  p=0.001); all ten gated trees span 0.110–0.172, so the agreement survives every
  encoding/metric/algorithm choice. Convention ≠ content is now a topology-level result:
  against the same gold the lemma-overlap tree scores 0.4302, and the two axes recover
  *different* documented families (Petersburg 1.000 convention / 0.395 content; Wilson
  0.442 / 1.000). The gated pipeline beats the preview one by ≈0.28 GQD — a joint effect
  of Patel's seven gold conventions and the weighted-Hamming distance, not separable into
  the two with the trees the repo committed. Registered as
  `L0-GQD` in
  [`docs/HYPOTHESIS_INDEX.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/HYPOTHESIS_INDEX.md);
  agenda backlog #8 ticked.
- **Honest limits carried in the doc, the report JSON and the registry**: the gold is a
  tree while dictionary descent is reticulate, so five documented edges (including
  PWG→MW) are unrepresentable and 0.1456 is a floor; two gold groups cite lemma
  containment, which advantages the content tree and never the convention tree;
  `A_jaccard_upgma` scores better (0.1102) than the pre-registered canonical and was
  deliberately **not** promoted.

### Fixed — `canonical_consensus.newick` was described as something it is not (H1578)

- Chasing why two L0 trees scored identically under GQD surfaced a mislabel:
  `data/L0/trees/canonical_consensus.newick` is **not a consensus tree**. The 1000×
  dimension-bootstrap loop in
  [`scripts/L0/s3_cladogram.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/L0/s3_cladogram.py)
  accumulates per-edge support counts and never builds a topology from the replicates, so
  the canonical file is the single-run UPGMA on the full `B_whamming` matrix and is
  byte-identical to `B_whamming_upgma.newick`. Corrected the prose that asserted otherwise
  — the public `/tools/lexicographic-conventions` page, `docs/L0_RESULTS.md` §1/§4/§6, and
  the script's own docstring and section comment. **No data, tree or number changed**; the
  bootstrap support values are genuinely resampled and remain valid. Whether to rename the
  file or to actually publish a majority-rule consensus (which would change the published
  topology and every GQD number) is filed as
  [csl-atlas#313](https://github.com/sanskrit-lexicon/csl-atlas/issues/313) for a human.

## [0.11.0] - 2026-07-26

### Changed — xref sheet: the "independent witnesses" claim retracted, instructions in Russian (H1648)

Reviewer feedback on the [H1646](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1646-Opus_csl-atlas_xref-sheet-reviewability-40edges_25.07.26.md)
rebuild. Three points, one of them a correction to a claim this repo was making.

- **Retracted: "both dictionaries, independently, print a cross-reference".** MG: *"wrong —
  MW depends on PWG and PW."* MW 1899 was built on Böhtlingk–Roth, so a shared reference may
  be one tradition copied rather than two agreeing. New
  [`scripts/lexico/m9_xref_marker_agreement.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/m9_xref_marker_agreement.py)
  measures it instead of assuming either way: on the **2,750** headwords cross-referenced in
  both dictionaries, MW's `cf.` target is also a PWG `Vgl.`/`s.` target **21.8%** of the time
  versus **0.007%** expected under a degree-preserving null — **≈2,953× enrichment, 0/200
  null draws at or above observed (p < 0.005)**. Committed to
  [`data/lexico/xref_marker_agreement.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/xref_marker_agreement.json).
  `lexical-shared-core` now asserts only that the edge is **real and lexical**; the raw
  containment asymmetry (~3.2×) is flagged as a set-size artifact (~3.4× edge-count ratio),
  not directional evidence.
- **`normalization-risk` grounded in Patel 2016.** MG: *"to check for artifacts you first
  have to check how artifacts could be made."*
  [`docs/refs/Patel_2016_Normalizing_headwords.pdf`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/refs/Patel_2016_Normalizing_headwords.pdf)
  yields four documented conventions where MW and PWG take **opposite** sides and which this
  pipeline does not reconcile: śatṛ `-at`/`-a` (3.1/3.2), vatup/matup `-vat`/`-v` (3.4/3.5),
  ṛ-stems `-ṛ`/`-ar` (6.1/6.2), vas/yas `-vas`/`-vaṃs` (7.1/7.4). Consequence now stated: the
  risk runs both ways, and **the 642-edge intersection is an undercount** — a ṛ-stem edge
  cannot intersect at all while the two dictionaries key it differently.
- **The sheet is in Russian.** Question, label definitions, worked examples, sampling method
  and markup legend are translated, and the emitter's own chrome (toolbar button, keyboard
  hint, save banner, vote legend) with it, via
  [`csl-pyutil` 0.4.0's new `ui_strings`](https://github.com/sanskrit-lexicon/csl-pyutil/pull/9)
  rather than by post-processing HTML here (pin bumped, `MIN_EMITTER_VERSION` 0.3.1 → 0.4.0).
  The only non-Russian prose left on a card is the quoted dictionary text itself.

## [0.10.0] - 2026-07-26

### Added — PH5 ORTHO-CLOCK gloss-orthography census + V5 explorer (H1577)

- **`npm run build-ortho-drift` + `validate-ortho-drift`**
  ([`scripts/build-ortho-drift.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-ortho-drift.mjs),
  [`scripts/validate-ortho-drift.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/validate-ortho-drift.mjs)):
  deterministic census of pre-reform German/Russian spellings in dictionary gloss
  text against the frozen SanskritSpellCheck reform maps (15,685 DE / 7,709 RU
  pairs, consumed read-only from the sibling checkout) →
  [`data/lexico/ortho_drift.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/ortho_drift.json)
  (+ `.source.json`), with entry-bootstrap CIs, exhaustive-permutation Spearman,
  and directional entry-level pair tests. 11 unit tests in
  [`test/ortho-drift.test.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/test/ortho-drift.test.mjs).
- **V5 page [`/tools/ortho-drift`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/ortho-drift.md)**:
  drift-vs-year scatter with lineage lanes and CIs, era-composition clock,
  descent pair-test table, searchable top-drifted-forms table (a learner
  search-normalisation aid), Russian Kossovich section, CSVs + Trust Block.
- **Measured verdicts** (registered in
  [`docs/HYPOTHESIS_INDEX.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/HYPOTHESIS_INDEX.md)
  as ORTHO-CLOCK, Type 1; agenda backlog #6 ticked): the density clock is
  direction-consistent but inconclusive at n=6 (ρ=−0.52, exhaustive p=0.30) and
  is really a **house-style clock** — the Böhtlingk lane stays uniformly fossil
  (PWG 14.8 → PW 17.5/1k) while non-Böhtlingk dictionaries modernise with date
  (GRA 10.4, CCS 6.5, SCH 4.8); the **descent sub-claim is refuted** (CCS 1887,
  a declared Petersburg descendant, is LESS pre-reform than the independent
  GRA 1873 — Cappeller re-spelled); the **era-composition clock is robust**
  (SCH-1928 flips to 69% 1996-ß, reproducing the upstream control at the atlas
  layer); Russian Kossovich (1854) runs at 358/1k, a single dated point.

## [0.9.0] - 2026-07-25

### Changed — xref shared-core review sheet made answerable (H1646)

Reviewer feedback on
[`csl-atlas-xref-shared-core_40edges_review.html`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-review-sheets.py)
was that the 40 cards could not be voted as built: no way to read the entries, raw
markup dumped verbatim, three reject labels named but none defined, and no disclosed
sampling method. Four fixes, all in the generators — the sheet itself stays gitignored
and is regenerated with `npm run build-review-sheets`.

- **Cologne links on both ends of every edge.** New
  [`scripts/lib/cologne-links.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/cologne-links.mjs)
  builds the CDSL entry-display URL (`indexcaller.php`, which auto-searches on load —
  param contract read from the `csl-websanlexicon` template, live-verified for MW and
  PWG) and the printed-scan URL (`servepdf.php`), reusing kosha
  [`app/scan_resolver.py`](https://github.com/gasyoun/kosha/blob/main/app/scan_resolver.py)
  semantics including the PWG `{vol}-{page:04d}` trap. Each source pointer gains
  `pc` / `cologneEntryHref` / `cologneScanHref`; each row gains `targetLinks` for the
  *target* headword, which was never shown. `iterateDict()` now yields `pc`.
- **Entry anatomy colour-coding.** New
  [`scripts/lib/cdsl_anatomy.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/cdsl_anatomy.py)
  keeps the CDSL markup visible but dims delimiters and colours the payload by part
  class (Sanskrit · gloss · citation · grammar · cross-reference marker · etymology ·
  language · taxon · homonym), and outlines every occurrence of the cross-reference
  target — the exact span the edge is claimed from. Part taxonomy from the
  `/entry-anatomy` skill, dark palette from
  [`SanskritLexicography/EntryAnatomy/build_entry_anatomy.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/build_entry_anatomy.py);
  inline styles throughout, since `render_review_sheet` exposes no caller-CSS hook.
- **Label vocabulary with worked examples.** `XREF_LABEL_VOCABULARY` now carries
  `asserts` / `doesNotAssert` / two `examples` per label, rendered on every card.
  States explicitly that `lexical-shared-core` is *not* a synonymy claim. Prose
  companion:
  [`docs/XREF_SHARED_CORE_LABEL_TAXONOMY.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/XREF_SHARED_CORE_LABEL_TAXONOMY.md)
  (+ metadoc).
- **Sampling method disclosed.** `selectionPolicy` now states the real three-stage
  mechanism and the bias it carries: the 40 rows are the **first 40 of 642 shared edges
  in headword order, not a random sample**, so every card is an Ā-/B-/C-/D-/G-initial
  headword. Rendered on each card alongside counts and limitations.
- Cards additionally show IAST titles (SLP1 kept as a badge, per the H1621 display
  rule), and the 4 single-dictionary rows now say on the card that `too-sparse` is a
  legitimate answer. Record excerpts raised 260 → 900 chars.

## [0.8.0] - 2026-07-25

### Added — PH8 Heaps saturation + PH3 era signatures + V4 panels (H1576)

- New builder [`scripts/build-heap-sat.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-heap-sat.mjs)
  (+ `validate-heap-sat`, 8 tests): accumulates the 323,417-lemma
  [union headword backbone](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/union_headwords.tsv)
  in publication order (15 dictionaries, PWG 1855 → AP 1957) via exact
  15-bit-mask novelty arithmetic. Committed packet
  [`data/lexico/heap_sat.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/heap_sat.json):
  **PH8 supported** — Heaps V(n)=K·n^0.538, log–log R²=0.989; largest
  above-curve breaks SKD (+170%, 78.9% novel) and BHS (+178%, 59.0% novel);
  the specialised-break trio statistic (+0.50) stays **descriptive only**
  (seeded order-permutation p=0.070, exhaustive label-permutation p=0.165,
  n=3); the "<5% post-1890 general novelty" sub-claim is refuted (MW 26.9%,
  SCH 31.7%, AP 40.3%).
- New builder [`scripts/build-period-signatures.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-period-signatures.mjs)
  (+ `validate-period-signatures`, 5 tests): joins union provenance × the
  frozen kosha
  [`lemma_frequency.tsv`](https://github.com/gasyoun/kosha/blob/main/data/frequency/lemma_frequency.tsv)
  DCS-period vectors on normalized SLP1 (61,338 lemmas matched, 19.0%;
  boundary-clean — no VisualDCS ingestion). Committed packet
  [`data/lexico/period_signatures.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/period_signatures.json):
  **PH3 supported per-dictionary** — type-weighted era profiles with disjoint
  bootstrap CIs (GRA −423 CE / TVD 0.49; VEI −115; SKD +956, VCP +655;
  Petersburg line 516–574) — while the family-predicts-weighting sub-claim is
  **not supported** (Kruskal–Wallis H=5.42, p≈0.14, descriptive at n=14):
  canon, not language-pair family, drives the signature.
- [`/tools/dictionary-coverage`](https://sanskrit-lexicon.github.io/csl-atlas/tools/dictionary-coverage)
  gains V4 panels i (union growth curve + Heaps fit + step annotations) and
  ii (period-share small multiples + chronological centre-of-mass dot plot),
  each with CSV download and Trust Block; both packets wired into
  `sync-site-data`, the verify validator roster, and
  [`docs/HYPOTHESIS_INDEX.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/HYPOTHESIS_INDEX.md)
  Type 1 (HEAP-SAT, FREQ-STRAT); agenda backlog #5 closed.

### Fixed — deploy gate scoped to production dependencies (advisory churn)

- [`scripts/verify.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/verify.mjs):
  the audit gate is now `npm audit --omit=dev --audit-level=high` — the
  25-07-2026 `brace-expansion` advisory (`GHSA-mh99-v99m-4gvg`, no backport to
  the majors `minimatch` pins) made the unscoped gate unpassable without a
  breaking framework downgrade, blocking every deploy; nothing from the
  devDependency toolchain ships in the static Pages artifact. Posture +
  accepted-advisory list documented in
  [`docs/DEPENDENCY_SECURITY.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/DEPENDENCY_SECURITY.md).
  Lockfile refreshed (`brace-expansion` top-level, `tar`) without `--force`;
  `validate-ghost-stock` added to the verify validator roster.

## [0.7.0] - 2026-07-25

### Added — PH4 ghost stock + PH6 Heritage triangulation (H1575)

- New builder [`scripts/build-ghost-stock.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-ghost-stock.mjs)
  (+ `validate-ghost-stock`, 7 tests): joins the 323,417-lemma
  [union headword backbone](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/union_headwords.tsv)
  × DCS attestation × the
  [MW↔Heritage crosswalk](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw_heritage_crosswalk.tsv)
  on normalized SLP1. Committed packet
  [`src/data/ghost-stock/ghost_stock.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/ghost-stock/ghost_stock.json):
  attestation-by-multiplicity strata with Wilson CIs (4.7% at `n_dicts`=1 →
  100% at 13+), per-dict unique-attested shares, deterministic IRLS logistic
  (`n_dicts` +0.626 log-odds/dict, McFadden R² 0.27, independently reproduced
  in NumPy), the 2×2×2 Heritage witness cube with Woolf-CI odds ratios
  (uncovered→unattested OR 5.45), and a 37,931-row triple-filter
  ghost-candidate queue graded `inferred`.
- New page [`/tools/ghost-stock`](https://sanskrit-lexicon.github.io/csl-atlas/tools/ghost-stock)
  + V4 attestation strip on
  [`/tools/dictionary-coverage`](https://sanskrit-lexicon.github.io/csl-atlas/tools/dictionary-coverage);
  PH4/PH6 promoted Proposed → Type 1 in
  [`docs/HYPOTHESIS_INDEX.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/HYPOTHESIS_INDEX.md)
  (PH4 main claim supported, specialised-concentration sub-claim reversed —
  MW/MD lead unique-attested share, not BHS; PH6 supported); agenda backlog #3
  ticked.

### Fixed — deploy-blocking stale H4 queue count in CI (H1621 residue)

- [`scripts/test_validate_review_decisions.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/test_validate_review_decisions.py):
  `test_expected_queue_counts_are_stable` still expected 89 open
  `csl-atlas-h4-semantic-field` rows after the H1621 agent adjudication
  (PR #297) legitimately drained the sheet to 0, failing the Production
  verification step and **blocking every site deploy since v0.6.0**.
  Expected count updated to 0 with an H1621 provenance comment.

### Fixed — vendored sanskrit-util re-synced (H1394 residue)

- [`src/lib/sanskrit-util.js`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/lib/sanskrit-util.js)
  re-vendored from the canonical `sanskrit-util` checkout: the vendored copy
  still carried the pre-H1394 naive `iast_to_devanagari` and failed the
  sync selftest against the fixed canonical source. No `slp1_norm` change —
  committed normalized keys unaffected.

## [0.6.0] - 2026-07-25

### Fixed — A02 H2 figures re-synced to committed data (H001 residue)

- [`docs/articles/paper_sense_inheritance.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_sense_inheritance.md):
  the pooled H2 citation-survival figures had gone stale against the regenerated
  [`data/lexico/r2_h2h3.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_h2h3.json)
  — the draft asserted 84 cited ancestor senses (0.762 = 64/84 pooled, one cited
  sense on each Wilson edge), while the committed data has **82** cited senses
  (0.768 = 63/82, **zero** on both Wilson edges), making the draft's pooled 0.762
  vs within-edge 0.768 internally impossible. Abstract, §5, §8 and Conclusion now
  quote 0.768 (63/82) / 0.705 (511/725), naive pooled *z* ≈ 1.2, and "all 82 on
  Apte 1890 → 1957". Reference footer narrowed to the two genuinely unverified
  refs (Pagel/Atkinson/Meade 2007; Petersen et al. 2012). H2 verdict unchanged:
  within-edge gap still not significant (*z* = 1.80, *p* = 0.07).

### Added — H4 semantic-field agent adjudication (H1621)

- Close the H4 human vote stage: all **89** `needs-review` rows in
  [`data/lexico/h4_semantic_field_review_packet.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/h4_semantic_field_review_packet.json)
  now carry agent `reviewed-ok` decisions (closed vocab per sample type) with
  evidence notes from local csl-orig probes + packet pointers. Reviewer:
  `grok-4.5` (H1621).
- New runner [`scripts/adjudicate-h4-agent.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/adjudicate-h4-agent.mjs)
  writes the packet overlay and gitignored
  `review/csl-atlas-h4-semantic-field_89rows_decisions.json`.
- `build-h4-review-packet.mjs` preserves agent/human review overlays on rebuild
  (`preservedReviewsMap` / `applyPreservedReviews`); top-level status becomes
  `agent-reviewed` when no open rows remain.
- Human-facing H4 surfaces (review sheet + worksheet) show **IAST** for lemmas
  and field labels; SLP1 remains the machine key. Human vote is no longer required.

## [0.5.0] - 2026-07-24

### Added — Correction-lane overlays (H1579 / DH memo remainders)

- Close the three H271/DH_IMPROVEMENT_MEMO §3 remainders after H306's loci heatmap:
  1. **Shared-error Sankey overlay** on
     [`src/tools/lineage-sankey.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/lineage-sankey.md)
     (PWG/PW→MW co-corrected headwords + F4b Ahlborn direct test / null lift).
  2. **Correction-front strip** page
     [`src/tools/correction-front.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/correction-front.md)
     (OBS-T month×component + 2014–2018 / 2019–2026 era small multiples; data owner csl-observatory).
  3. **Maker-QA correction-pressure column** on
     [`src/tools/correction-loci.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/correction-loci.md)
     (human-process form-key join of H5 candidates + nearestReal against correction_loci.tsv).
- Builder `npm run build-correction-lane-overlays` → committed packets under
  [`src/data/corrections/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/src/data/corrections)
  (`shared_error_overlay`, `correction_front`, `qa_pressure` + `.source.json` sidecars).
- Tests: `test/correction-lane-overlays.test.mjs`.

### Added — Etymology-style witness page (H1525)

- New tools page
  [`src/tools/etymology-style.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/etymology-style.md):
  four Plot charts (Nirukta `.E.` share, `cf.` counts, year×share slope, WIL
  token bars) over frozen observatory probes vendored to
  [`src/data/witness/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/src/data/witness)
  with provenance headers. Trust Block marks the witness as an exploratory
  spike (n=5 dicts). Nav under Dictionary structure; cross-links from the
  homepage and the WIL chapter. Render-only — no new etymology extractor.

### Changed - Data-driven lexicographic timeline (H1484 / agenda V2)

- Upgrade [`src/tools/timeline.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/timeline.md)
  from static Mermaid-only to a Plot spine driven by
  [`data/dictionary_inventory.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/dictionary_inventory.csv):
  per-dictionary lifespan bars (deprecation fade/hatch), family-lane aggregate,
  volume-width encoding, sanhw1 lemma size at start year, and a cumulative
  coverage-ribbon step strip. Mermaid retained below the fold as the teaching
  narrative. Cross-links from [`lexicography`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/lexicography.md)
  and the tools index. Trust Block stresses orientation dates ≠ usage dating.

## [0.4.0] - 2026-07-21

### Added — Evidence-grading deep manual (H1408)

- **[docs/EVIDENCE_GRADING_DEEP_MANUAL.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/EVIDENCE_GRADING_DEEP_MANUAL.md)**
  — the end-to-end operator/scholar manual for the evidence-grading methodology and
  human-review workflow: the four-label evidence ladder (and the `evidenceLevel` vs
  `evidenceLabel` enforcement split), provenance envelopes, Chart Trust Blocks (with a
  61/64-page coverage + 8-item drift census), the review-queue/packet/auto-triage
  machinery, human-decision persistence across rebuilds (`reviewId`/`checkpointId`
  overlays; preservation invariant re-proved live: plain `build-r2-checkpoint-review`
  → 10/10 decisions preserved, byte-identical output), the hypothesis registry, the
  P1–P6/A-paper pipeline, the from-scratch statistics engines (IRLS+CR1,
  degree-preserving permutation nulls, exact small-n permutation), a design-rationale
  chapter, the consolidated incident corpus (A10 uncommitted-generator, YAT
  retraction→un-retraction, H2 pseudoreplication, overlay-wipe class, R2 archive
  loss, extraction under-counts), a failure-mode table, and the 93-script operator
  appendix. Sibling metadoc
  [docs/EVIDENCE_GRADING_DEEP_MANUAL.meta.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/EVIDENCE_GRADING_DEEP_MANUAL.meta.md)
  carries the `LAST_VERIFIED` block (joins the org `manual_staleness.py` estate) and a
  9-item improvement backlog. Closes deep-manual gap-census rows 11+12. Authored by
  Fable 5 (`claude-fable-5`), H1408.

### Added — Macrostructure anatomy waves B & D + Wave-A dash-truth (H1423 executed)

- **Wave B — entry-size decay in real time.** PWG's `<pc>`→volume→year mapping lets all 123,366
  entries carry a publication year: **PWG entries shrank −14.3 %/decade** (CI [−15.0, −13.7]),
  and the compression counter-test shows it is a **smooth fade** (vols 2–7 still −15.3 %/decade
  after dropping the over-detailed vol-1), not a one-time policy break — settling the cause
  question H1416 left open. Feed
  [data/pd/entry_size_by_year.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/entry_size_by_year.tsv);
  PWK/SKD/VCP flagged `date_quality` (no per-fascicule dates).
- **Wave D — density fingerprint.** New page
  [`/tools/dictionary-density`](https://sanskrit-lexicon.github.io/csl-atlas/tools/dictionary-density)
  + feed [data/pd/density_fingerprint.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/density_fingerprint.tsv):
  chars/Sanskrit-spans/markup-tags per entry across MW/AP/PWG/PWK/SKD/VCP. PWG carries the richest
  apparatus (20 tags/entry), PWK the tersest (43 chars), SKD/VCP the longest articles (median
  169/112) but ~0 Cologne markup (plain Skt→Skt).
- **Wave A — dash-truth generalization.** Feed
  [data/pd/compound_share_by_letter.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/compound_share_by_letter.tsv)
  with the MW/GRA dash-truth per-letter compound share. The DharmaMitra ByT5 splitter (for the
  non-dash dicts) was unreachable in the build env, so splitter columns ship *model unavailable*
  (the planned graceful degradation); re-run
  [scripts/import_compound_segmentation.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/import_compound_segmentation.py)
  where the model is reachable to fill them. Report §7.

### Changed — §8.11 sourced (Delbrück) + 74-years conflation fixed (H1336; re-applied after clobber)

- **Sourced the "9/10":** it is **Delbrück's estimate** (B. Delbrück, *Ber. Sächs. Ges. Wiss.* 56,
  1904, 253–258) of Böhtlingk's share of PWG — Roth did the Ṛgveda + Suśruta, Whitney the AV, Weber
  the Śatapatha, Stenzler Manu, Kern Varāhamihira, Schiefner Buddhist Sanskrit; Böhtlingk everything
  else, whole done in ~22 yr (1853–1875), then the *kürzere Fassung* alone (1879–1889). Karttunen's
  entry (source) also cites **A. A. Vigasin** — his Petersburg-dictionary articles to be folded in.
- **Corrected the "74" conflation:** it is the **years since PD's 1948 conception**, not a planned
  lexicographer count; PD's staffing point restated as the real *severe shortage* (~a
  dozen-to-two-dozen active). Report §8.11 + page + sources footer. (This content was lost to a
  concurrent merge — PR #288 never landed — and is re-applied here.)

### Added — Phase-2 execution plan: cross-dictionary macrostructure anatomy (H1423, via /ask)

- Layered plan (index + roadmap + architecture + implementation + verification + metadoc) under
  [docs/](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/docs) for the H1416 follow-up:
  generalise the compound/preverb law across MW/AP/PWG/PWK (+ SKD/VCP contrast) via the
  DharmaMitra splitter calibrated on MW dash-truth (Wave A), regress PWG entry-size on real
  publication year via the `<pc>`→volume→year mapping and test the compression counter-explanation
  (Wave B), and a multi-signal cross-dictionary density fingerprint page (Wave D). Execution
  handoff [H1423](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1423-Opus_csl-atlas_dict-macrostructure-anatomy-exec_21.07.26.md);
  authored via `/ask`, autonomy-readiness gate passed.

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

_Dr. Mārcis Gasūns_
