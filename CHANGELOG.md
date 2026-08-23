# Changelog

All notable changes to csl-atlas are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/). Dates are ISO.

## [Unreleased]

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
