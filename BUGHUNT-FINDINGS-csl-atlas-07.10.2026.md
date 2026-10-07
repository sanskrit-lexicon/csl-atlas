# BUGHUNT-FINDINGS — csl-atlas — nightly 07.10.2026

_Created: 07-10-2026 · Last updated: 07-10-2026_

Nightly one-repo bug hunt (MG ruling 26-09-2026: nightly, one repo, auto-fix HIGH).
Repo: [sanskrit-lexicon/csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas) at `1e2a391fa98f3968f511049381d05356e06d050b` (origin/main).
Runner: OpenCode, GLM `zai-coding-plan/glm-5.3-flash`. Phase 1 read-only; report landed via worktree `csl-atlas-h4068-63566` off `origin/main`.

**Elapsed: ~40 min wall** (hunt ~25 min, land + fix ~15 min).

## Scope

- Scanned: `src/lib/` (all 6 JS files, read in full), `src/sw.js`, `observablehq.config.js`, `package.json` (all 135 script targets checked for dead refs), `.github/workflows/` (9 workflows), `scripts/verify.mjs`, CI-gate scripts ([check_prose_number_drift.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/1e2a391fa98f3968f511049381d05356e06d050b/scripts/check_prose_number_drift.py), [changelog_duplicate_bullets.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/1e2a391fa98f3968f511049381d05356e06d050b/scripts/changelog_duplicate_bullets.py)), [git_ops.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/1e2a391fa98f3968f511049381d05356e06d050b/scripts/git_ops.py), [review-report.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/1e2a391fa98f3968f511049381d05356e06d050b/scripts/lib/review-report.mjs) (reseed lock), [cologne-links.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/1e2a391fa98f3968f511049381d05356e06d050b/scripts/lib/cologne-links.mjs), plus pattern sweeps (swallowed errors, secrets, `shell=True`, `eval`, unguarded `match()[i]`, `parseInt` radix) over `scripts/` (~31k LOC Python) and `src/`.
- Skipped per brief: vendored copies reviewed only at their drift guard, `package-lock.json`, `node_modules/`, `data/` giants, `dist/`.
- Skipped per fence: nothing under any `stenogrammy/` path.

## Findings (ranked)

| # | Rank | One-line | Status |
|---|---|---|---|
| 1 | **HIGH** | Vendored `sanskrit-util.js` a month stale vs canonical v0.12.0 — `form_key` misses the H3975 medial-anusvāra-before-labial fold; live joins in the H4 pipeline diverge from the canonical key | **Auto-fixed this run** (PR linked below) |
| 2 | MEDIUM | The vendor-drift guard skips when the sibling is absent — CI can never run it, so drift ships green | Report only |
| 3 | MEDIUM | H5/H4 orchestrator tests regenerate line-pinned csl-orig links from the local sibling; a stale local `csl-orig` (behind 8) mismatches committed fixtures by +1 line — known coupling, listed for the nightly record | Report only |
| 4 | LOW | `normalizeLookupQuery` gives no lower-case fallback for ALL-CAPS reader input | Report only |

No committed secrets found (regex sweep over `scripts/`, `src/`, `.github/`, configs: zero hits). No `shell=True`, no `eval`/`exec` on input, no unguarded `match()[i]` (all 6 call sites null-guarded), no dead `package.json` script refs (0/135).

### 1. HIGH — vendored sanskrit-util.js drifted from canonical (missing H3975 form_key fix)

- File: [src/lib/sanskrit-util.js:185-196](https://github.com/sanskrit-lexicon/csl-atlas/blob/1e2a391fa98f3968f511049381d05356e06d050b/src/lib/sanskrit-util.js#L185-L196) vs canonical `../sanskrit-util/js/index.mjs` (v0.12.0).
- Live evidence (run in this session): `node --test test/lib.test.mjs` fails with `AssertionError: src/lib/sanskrit-util.js has drifted from ../sanskrit-util/js/index.mjs — re-vendor it` at [test/lib.test.mjs:461](https://github.com/sanskrit-lexicon/csl-atlas/blob/1e2a391fa98f3968f511049381d05356e06d050b/test/lib.test.mjs#L461); `diff` of the two files is exactly 9 lines — the vendored copy lacks the medial-anusvāra block (`s = s.replace(/[ṃṁ](?=[pbm])/g, 'm') // H3975` and its 8-line comment).
- Dating: last re-vendor `790d3dd0` "re-vendor sanskrit-util v0.11.0" (04-09-2026, PR #438); canonical fix `48052f3` "fix(form_key): medial anusvāra before a labial folds to m (0.12.0, H3975)" landed 06-09-2026 in [sanskrit-lexicon/sanskrit-util](https://github.com/sanskrit-lexicon/sanskrit-util) — **three days after the re-vendor, so the drift window is a full month**.
- Impact: `slp1_form_key` is load-bearing in this repo — [build-h4-review-packet.mjs:675,691,697](https://github.com/sanskrit-lexicon/csl-atlas/blob/1e2a391fa98f3968f511049381d05356e06d050b/scripts/build-h4-review-packet.mjs#L675) (H4 crosswalk joins) and [adjudicate-h4-agent.mjs:38,82,148](https://github.com/sanskrit-lexicon/csl-atlas/blob/1e2a391fa98f3968f511049381d05356e06d050b/scripts/adjudicate-h4-agent.mjs#L38) (adjudication matching). With the stale fold, `saṃbhavaḥ`/`sambhavaḥ`-class lemma↔form pairs do **not** collide here while they do in every consumer on canonical v0.12.0 — the H4 evidence joins silently diverge from the estate-wide key. This drift class has hit the repo before (H1394 residue, re-synced in CHANGELOG §0.10-era "Fixed — vendored sanskrit-util re-synced").
- Disposition: **auto-fixed in this run** per the MG 26-09-2026 ruling — re-vendored byte-identical from canonical v0.12.0 (documented repair; the guard's own message). Fix PR: _linked in the changelog queue entry of this merge_.
- Verification of the fix: `node --test test/lib.test.mjs` green after re-vendor; vendored file byte-equal (modulo CRLF) to `../sanskrit-util/js/index.mjs`; no repo test pins the old fold (`grep form_key test/*.mjs` → 0 hits), exports unchanged.

### 2. MEDIUM — the drift guard is blind in CI by construction

- File: [test/lib.test.mjs:456-462](https://github.com/sanskrit-lexicon/csl-atlas/blob/1e2a391fa98f3968f511049381d05356e06d050b/test/lib.test.mjs#L456-L462) — `skip: fs.existsSync(canonicalSanskritUtil) ? false : "requires sibling ../sanskrit-util checkout"`.
- Live evidence: `gh run list` shows `Test: success` on `1e2a391f` (2026-10-06) — the same commit whose vendored copy fails the guard locally; CI has no sibling checkout, so the guard skips and finding 1 shipped green for a month.
- Recommendation (human decision, not auto-fixed): pin the canonical digest at re-vendor time (e.g. a `sha256` line beside the vendored file, checked unconditionally in CI) so CI detects drift without needing the sibling. Same shape already exists in-repo: `data/integrity/*.pin.json` tripwires.

### 3. MEDIUM — environment-coupled H5/H4 packet tests (known; recorded for the nightly ledger)

- Files: [test/orchestrators.test.mjs:768](https://github.com/sanskrit-lexicon/csl-atlas/blob/1e2a391fa98f3968f511049381d05356e06d050b/test/orchestrators.test.mjs#L768), [:837](https://github.com/sanskrit-lexicon/csl-atlas/blob/1e2a391fa98f3968f511049381d05356e06d050b/test/orchestrators.test.mjs#L837), [:991](https://github.com/sanskrit-lexicon/csl-atlas/blob/1e2a391fa98f3968f511049381d05356e06d050b/test/orchestrators.test.mjs#L991).
- Live evidence: full-suite run in this session — 409 tests, 405 pass, **4 fail**; 3 of the 4 are these. Each failure is a uniform +1 delta on pinned `mw.txt` line numbers (e.g. expected `#L246835`, generated `#L246834`); the local `../csl-orig` checkout is `behind 8` of origin/main, while the committed fixtures were frozen against a newer revision. CI is green on the same SHA because source-derived steps skip without the sibling (documented in `test.yml`'s negative-control job comment).
- Not new: the changelog_queue H5318 entry already records "the 3 pre-existing H4/H5 packet failures on clean main (local csl-orig drift, cf. 0.19.8)". Listed here so the nightly ledger is complete and nobody mistakes them for regressions from finding 1's fix. Report only — the cure (pinning csl-orig revisions for fixture-freeze runs, as the citation re-freeze chain already does) is a design decision.

### 4. LOW — ALL-CAPS reader input gets no lower-case lookup candidate

- File: [src/lib/lookup-normalize.js:35-47](https://github.com/sanskrit-lexicon/csl-atlas/blob/1e2a391fa98f3968f511049381d05356e06d050b/src/lib/lookup-normalize.js#L35-L47).
- Live evidence (run in this session): `normalizeLookupQuery("Deva")` → candidates `["Deva","deva"]` (good), but `normalizeLookupQuery("DEVA")` → candidates `["DEVA"]` only — the title-case fallback regex `^[A-Z][a-z][A-Za-z-]*$` requires a lower-case second letter, and the all-lower regex does not match, so an all-caps query carries no indexable candidate. Cosmetic reach (rare input shape), no data risk. Report only.

## What verified green

- `npm test` (node --test, full suite): **409 tests, 405 pass**; the 4 failures are findings 1 (fix verified green post-re-vendor) and 3 (known environment coupling, unchanged by this run).
- `package.json` script census: 135 scripts, 0 dead file references.
- Secrets sweep (API-key/secret/password/token literal patterns over `scripts/`, `src/`, `.github/`, root configs): 0 hits.
- [scripts/lib/review-report.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/1e2a391fa98f3968f511049381d05356e06d050b/scripts/lib/review-report.mjs) reseed lock intact (exact-match `"1"` hatch, distinct refusal exit 2; [test/reseed-lock.test.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/1e2a391fa98f3968f511049381d05356e06d050b/test/reseed-lock.test.mjs) passing).
- [scripts/git_ops.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/1e2a391fa98f3968f511049381d05356e06d050b/scripts/git_ops.py): per-call `GIT_*` env stripping, bounded timeouts raising named `GitTimeout`, explicit `-C <repo>` — no subprocess-git holes found.
- [scripts/lib/cologne-links.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/1e2a391fa98f3968f511049381d05356e06d050b/scripts/lib/cologne-links.mjs): every `page.match(...)` consumer null-guarded (no invented scan links); all `scanPageFromPc` shape tests green.
- [src/sw.js](https://github.com/sanskrit-lexicon/csl-atlas/blob/1e2a391fa98f3968f511049381d05356e06d050b/src/sw.js): network-first with cache fallback and offline navigate fallback — no stale-cache or 5xx-caching hole found.
- [scripts/verify.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/1e2a391fa98f3968f511049381d05356e06d050b/scripts/verify.mjs): validator list matches 14 existing `scripts/validate-*.mjs` files; deterministic double-regen + clean-tree asserts present.

## Process notes

- Phases: hunt (read-only) → this report → HIGH auto-fix. Max-3-attempts fix budget: used 1 of 3 (first attempt verified green).
- No HIGH credential/infra finding, so no GTD `@DO` row was minted; findings 2–4 are report-only per the ruling.

_Dr. Mārcis Gasūns_
