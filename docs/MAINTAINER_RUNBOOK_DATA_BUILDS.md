_Created: 24-09-2026 · Last updated: 24-09-2026_

# MAINTAINER RUNBOOK — Atlas data builds (H5338)

Written for a co-maintainer following it **cold**. Every command below was run in
this pass on a **clean clone** of `csl-atlas@78fb3b2` (v0.19.5) on macOS
(darwin, arm64), and the durations are wall-clock measurements from that pass,
not estimates. Box details: Node v26.7.0 / npm 11.x, Python 3.13 (Homebrew),
warm npm cache.

The one-sentence mental model: **canonical data lives in `data/` (committed);
`npm run sync-site-data` copies site-facing slices into `src/data/` (some
committed, some gitignored); `npm run verify` is the single production gate
that proves tests, validators, deterministic regeneration, site build, audit
and tree cleanliness all hold at once.**

## 1. Prerequisites

| Requirement | Detail | Check |
|---|---|---|
| Node + npm | engines pin `node 20.x`, `npm 10.x` (CI). Node v26.7.0 also verified green in this pass — mismatch warns, does not block. | `node --version` |
| Python 3 with a bare `python` | `npm run verify` shells out to `python -m unittest`. macOS ships only `python3`, **no `python`** — the cleanest fix is a venv, which always provides `python` on PATH (§2). | `which python` |
| Sibling `csl-orig` checkout | Data builders read the Cologne sources read-only from a **hardcoded sibling path**: `../csl-orig/v02` (see `scripts/lib/dict-parser.mjs`, `scripts/lib/mw-parser.mjs`; forensic scripts allow an env override). | `ls ../csl-orig/v02` |
| Sibling `SanskritLexicography` checkout | Lexico-layer builds (e.g. Heaps-sat) read `../SanskritLexicography/HeadwordLists/union/union_headwords.tsv`. Without it the build **exits fast with an explanatory message** and the committed JSON stays the CI-safe artifact — you can skip these builds entirely. | `ls ../SanskritLexicography` |
| npm install-scripts gate (npm ≥ 11.5) | `npm ci` may print `npm warn install-scripts` and skip postinstalls (esbuild, fsevents). Harmless here — esbuild ships its binary via optionalDependencies — but confirm: `node -e "require('esbuild').version"` prints `0.27.7` (or similar) and `ls node_modules/.bin/observable` exists. | both commands |

If your clones live elsewhere, symlink the siblings next to the atlas clone:

```bash
ln -sfn /path/to/csl-orig ../csl-orig
ln -sfn /path/to/SanskritLexicography ../SanskritLexicography
```

## 2. Clean-clone bootstrap (measured)

```bash
git clone https://github.com/sanskrit-lexicon/csl-atlas.git   # 31.6 s this pass
cd csl-atlas
npm ci --no-audit --no-fund                                   # ~1 s warm cache; allow minutes cold
python3 -m venv .venv && source .venv/bin/activate            # 1.2 s — also fixes the `python` shim
pip install -r requirements-review.txt                        # pinned csl-pyutil zip; seconds
python -m pip show csl_pyutil > /dev/null && echo py-deps-ok   # sanity
```

`requirements-review.txt` pins `csl-pyutil` to an immutable commit archive —
the review-sheet emitter that several generators import. Do not "upgrade" it;
the pin is deliberate.

## 3. The core chain

```bash
npm run sync-site-data   # 0.19 s, "Synced site data (54 files changed)" on fresh clone
npm run verify           # 1 m 45.6 s end-to-end this pass — THE production gate
```

What `npm run verify` (`scripts/verify.mjs`) actually runs, in order:

1. **clean-tree gate** — `git diff` (unstaged + staged) must be empty *before* starting;
2. `node --test` — 369 tests, 363 pass / 6 skipped, **0.61 s**;
3. `python -m unittest scripts.test_validate_review_decisions` — 7 tests, **0.06 s**;
4. **12 validators** (§5);
5. `regen-review-artifacts.mjs` **twice**, then the clean-tree gate again — this is the
   **deterministic-regeneration check**: review artifacts must regenerate byte-identically;
6. `npm run build` = prebuild `sync-site-data` → `observable build` (site, ~21 pages,
   21 links validated) → postbuild copies `manifest.json`, `sw.js`, `favicon.svg`,
   `robots.txt`, `sitemap.xml`, `atlas-card.png` into `dist/`;
7. `npm audit --omit=dev --audit-level=high` — this pass: `found 0 vulnerabilities`;
8. final clean-tree gate.

**PASS line to expect:** `verify: all tests, validators, deterministic regeneration,
build, audit, and clean-tree checks passed.`

For a quick smoke without the site build: `npm test` (0.6 s) and, before any CI
build, `npm run validate-review-reports` (CLAUDE.md contract).

## 4. Rebuilding a data layer

~70 layers, one npm script each: `npm run build-<layer>` plus a paired
`npm run validate-<layer>` where a validator exists (grep `package.json`
`scripts` — never guess). Two representative pairs, measured this pass on the
clean clone:

| Pair | Build | Validate | Outputs |
|---|---|---|---|
| Heaps saturation | `npm run build-heap-sat` — **0.98 s** | `npm run validate-heap-sat` — **0.93 s** | `data/lexico/heap_sat.json` + `heap_sat.source.json`, then site copy |
| MW quantitative depth | `npm run build-mw-depth` — **1.24 s** | `npm run validate-mw-depth` — **0.10 s** | `data/mw-depth.json` + `src/data/mw/*` slices |

What a rebuild legitimately changes even with no upstream data movement:

- **Provenance pins.** Every `*.source.json` sidecar records the atlas commit
  and the sibling-checkout commit it built from (`siblingCommit`). If a sibling
  moved since the artifact was frozen, a rebuild refreshes the pin — a small
  expected diff, not drift in the measurements.
- **Site copies.** A rebuild changes `data/…`; `src/data/…` copies go stale
  until `npm run sync-site-data` re-runs.

The maintainer cycle is therefore always:

```bash
npm run build-<layer>        # rebuild from siblings
npm run validate-<layer>     # layer's own validator
npm run sync-site-data       # refresh site copies
npm run verify               # full gate; its clean-tree gate forces you to commit refreshed artifacts
git checkout -b data/<layer>-rebuild && git add -A && git commit && git push -u origin data/<layer>-rebuild  # PR
```

If you do not intend to ship a refresh, `git checkout -- <files>` restores the
frozen artifacts.

## 5. Validators — what each failure means

Universal failure, all validators:

- `Missing required output: <path>` → the artifact was never built (fresh clone,
  or you deleted it). Run the paired `npm run build-<layer>` first. Note most
  validators check the **site copy** under `src/data/`, so after building run
  `npm run sync-site-data` too.

Layer-specific checks (all verified against real validator code, the Heaps
two induced live in this pass by mutating `data/lexico/heap_sat.json` and
watching both fire):

- `validate-heap-sat`:
  - `src/data/lexico/heap_sat.json (site copy) differs from data/lexico/heap_sat.json — run npm run sync-site-data` (induced);
  - `rebuild cross-check: heapsFit disagrees with the committed packet — rerun npm run build-heap-sat` (induced) — the validator **re-runs the build** when the sibling union is present and compares fitted statistics;
  - `step <code>: noveltyShare mismatch` — per-step union arithmetic broken.
- `validate-mw-depth`: `Record count <n> is far from expected <count>` — record-count drift guard; `Validation report present with 0 warning(s)` on pass.
- `validate-dictionary-comparison`: `missing includedDictionaries` — packet must declare its input dictionaries.
- `validate-correction-feed`: `<dict>: per1k <x> != records/entries*1000 (<y>)` — the per-1000 rate must equal the arithmetic of the counts it ships with.
- `validate-heritage-witness`: `witnessed <headword>: anchored row missing heritageAnchor` — every witnessed row needs its heritage anchor.
- `validate-period-signatures`: `period vocabulary drifted from kosha period_order: <declared>` — period labels must match the kosha registry vocabulary.
- `validate-ghost-stock`: `perDict <code>: missing family` — every dictionary section must carry its family classification.
- `validate-l0-gqd`: positional grammar-drill checks (`unexpected <token> at <pos>`).
- `validate-review-reports`: `<file>: missing required "items" array` / `missing required field "<f>"` — review-report schema; also what CI runs pre-build.
- `validate-citation-canon` / `validate-tradition-tags` / `validate-four-axis-independence`: presence + declared-stats coherence on their packets.

If a validator fails after a *sibling moved* (not your edit), decide: rebuild
and ship the refresh (§4 cycle), or leave frozen and note the drift. Never
hand-edit a committed artifact.

## 6. Cutting a data / site release

Releases flow through the changelog queue (repo convention — direct
`[Unreleased]` bullets are hook-blocked): a dated
`changelog_queue/<date>-<slug>.md` entry is consumed by the org-side
`cut_release.py`, which moves it into `CHANGELOG.md` as a version section and
bumps `CITATION.cff` + `.zenodo.json`. Real example, v0.19.5 (commit `78fb3b2`,
24-09-2026): touched exactly `CHANGELOG.md`, `CITATION.cff`, `.zenodo.json`,
and deleted the consumed queue entry — 4 files, 5 insertions, 3 deletions.

For **data exports shipped as release artifacts** (not committed): e.g.
`npm run build-stardict-export` writes `stardict-dist/` (MW .dict ≈ 46 MB) —
gitignored by policy; attach to a GitHub release
(`gh release create v<ver> stardict-dist/*`) rather than committing the blob.

## 7. Failure triage — quick table

| Symptom | Meaning | Fix |
|---|---|---|
| `python: command not found` inside `npm run verify` | no bare `python` on PATH (macOS) | use the venv from §2 |
| `Required input missing: …/SanskritLexicography/…` (build exits < 1 s) | lexico-layer sibling absent | symlink it (§1) or skip — committed JSON is CI-safe |
| Validator: `Missing required output` | layer not built in this clone | run paired `build-<layer>` + `sync-site-data` |
| Validator: `site copy … differs` | rebuilt canonical, stale site copy | `npm run sync-site-data` |
| Validator: `rebuild cross-check … disagrees` | committed packet ≠ fresh build from siblings | rerun the build, ship the refresh or restore |
| verify: `tracked files are not clean` (before) | uncommitted changes present | commit/stash first — the gate is deliberate |
| verify: `tracked files are not clean` (after regen) | review artifacts not byte-stable | regenerate committed artifacts; investigate non-determinism before shipping |
| `npm audit` exits nonzero | high/critical prod-dep advisory | treat as release blocker (docs/DEPENDENCY_SECURITY.md scopes dev-only advisories as non-blocking) |

## 8. Provenance of this runbook

Every command and duration above was executed 24-09-2026 (H5338) on a clean
clone at `78fb3b2` (v0.19.5): clone 31.6 s; `npm ci` ~1 s warm; venv+pip
seconds; `sync-site-data` 0.19 s / 54 files; `node --test` 0.61 s (369 tests);
python unittest 0.06 s (7 tests); **`npm run verify` 1 m 45.6 s, PASS**;
`build-heap-sat` 0.98 s + `validate-heap-sat` 0.93 s PASS (after sync);
`build-mw-depth` 1.24 s + `validate-mw-depth` 0.10 s PASS; both heap-sat
validator failure modes induced by controlled mutation and reverted. Cold-cache
`npm ci` and `observable build` vary with network/CPU — the 1 m 46 s verify
figure was measured with a warm package cache on an M-series Mac.

_Гасунс_
