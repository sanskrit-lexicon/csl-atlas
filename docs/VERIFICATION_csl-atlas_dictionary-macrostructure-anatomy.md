# Verification — Cross-dictionary macrostructure anatomy

_Created: 21-07-2026 · Last updated: 21-07-2026_

Acceptance criteria per deliverable, the exact command/flow that proves each works, and the
risks & spikes register. Sibling of
[IMPLEMENTATION](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/IMPLEMENTATION_csl-atlas_dictionary-macrostructure-anatomy.md)
and
[PLAN](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/PLAN_csl-atlas_dictionary-macrostructure-anatomy_2026.md).

## Acceptance criteria

### Wave A — compound law
- **A-AC1** `data/pd/compound_share_by_letter.tsv` exists with a row per (in-scope dict × letter),
  `n_sampled` recorded, and a Wilson CI on every `splitter_pct`.
- **A-AC2** The **MW calibration** is reported: splitter-vs-dash-truth precision/recall/F1,
  overall and per-letter. Prove: on MW rows, `dash_truth_pct` and `splitter_pct` are both present
  and the F1 summary row is populated.
- **A-AC3** Every splitter estimate is presented **with the MW error bar attached** in both the
  TSV and the report/page (calibration-gate ruling: ship estimates with error). No splitter %
  appears without its calibration context.
- **A-AC4** The generalised-law verdict is stated explicitly: does high compound-share track
  preverb-family-heading across dicts, or is MW special? Backed by the table.
- **Fallback-AC** If the ByT5 model is unavailable (Step 0 spike fails) and cannot be fetched:
  the wave ships **dash-truth-only** (MW/GRA) with a logged note; A-AC2/3 are marked N/A. This is
  an accepted degraded outcome, not a failure.

### Wave B — entry-size chronology
- **B-AC1** `data/pd/entry_size_by_year.tsv` exists; PWG rows map every entry to a volume/year;
  the 7 PWG volume buckets are all non-empty and sum to the PWG entry count (validation assert).
- **B-AC2** The PWG decay slope is reported in **chars/decade** with a CI, and its **sign agrees
  with the H1416 alphabetical-position slope** (ρ = −0.19). A sign disagreement is a red flag to
  investigate, not silently ship.
- **B-AC3** The compression counter-test (B3) yields an explicit verdict: smooth funding-fade /
  one-time vol-1 break / indistinguishable — with the number behind it.
- **B-AC4** PWK/SKD/VCP rows carry an honest `date_quality` flag; nowhere is a weak/absent date
  presented as if exact.

### Wave D — density fingerprint
- **D-AC1** `data/pd/density_fingerprint.tsv` exists with chars/senses/blocks-per-entry for every
  in-scope dict (dict-level + per-letter).
- **D-AC2** For SKD/VCP, **median is reported beside mean** (heavy-tail rule).
- **D-AC3** The per-dict sense-division and block marker set used is documented in the report
  (formats differ per dict).
- **D-AC4** New page `/tools/dictionary-density` builds and renders (0 error markers), is
  registered in nav + page-title map.

### Cross-cutting
- **X-AC1** `npm run build` is green; both pages render with 0 `observablehq--error` markers;
  broken-link count does not increase beyond the 3 pre-existing `pd-dcs-coverage` warnings.
- **X-AC2** CHANGELOG `[Unreleased]` carries an entry per shipped wave; **no `/cut-release`**
  (csl-atlas batches).
- **X-AC3** Hub sweep done within the fence: SL FINDINGS § added **and the epistemic-integrity
  structural check passes locally** (`python tools/epistemic_integrity_check.py --dir . --structural-only`
  — the H1416 lesson: add the Index entry + bump the next-free marker, or the SL PR's integrity
  gate goes red); Uprava PROJECT_INTERLINKS feed row(s); handoff registry closed.
- **X-AC4** All feeds mirrored to `src/data/pd/`; generators are deterministic (re-run is
  byte-identical — no `Math.random`/`Date.now`).

## Proof commands

```
# generators
python scripts/compound_share.py && python scripts/entry_size_chronology.py && python scripts/density_fingerprint.py
# integrity (before the SL FINDINGS PR)
python tools/epistemic_integrity_check.py --dir . --structural-only
# site (prime _npm cache first)
npm run build   # green; grep -c observablehq--error dist/tools/{letter-anatomy,dictionary-density}.html == 0
```

## Risks & spikes register

| # | Risk | Likelihood | Mitigation / spike |
|---|---|---|---|
| R1 | **ByT5 model unavailable offline** (network flaky/sandboxed; the build env blocks CDN/HF) | High | **Spike Step 0.1.** Fallback = dash-truth-only Wave A (Fallback-AC). Do not let it block B/D. |
| R2 | ByT5 too slow for the full sample in budget | Med | Spike 0.2 timing; shrink per-letter target, log it. |
| R3 | Splitter calibrates poorly on MW (low F1) | Med | Ruling: **ship estimates with error attached** anyway (calibration-gate answer); the poor F1 is itself the reported finding. |
| R4 | PWG `<pc>` has stray/non-numeric leading tokens | Low | Validate B-AC1 (buckets sum to entry count); route unparseable `<pc>` to an `unknown` bucket, count it. |
| R5 | PWK/SKD/VCP dates too weak to regress | High (expected) | Accepted — `date_quality` flag; report "insufficient date granularity" rather than a spurious slope. |
| R6 | Per-dict sense/block markers differ, miscounted | Med | Reuse mw-depth definition; document the marker set per dict (D-AC3); spot-check 3 entries/dict. |
| R7 | SL epistemic-integrity gate red on the FINDINGS PR | Med | X-AC3 runs the structural check locally before pushing (H1416 hit exactly this). |
| R8 | Concurrent session on csl-atlas (H1336 §8.x still active on adjacent files) | Med | Worktree off fresh `origin/main`; touch only the new files + append-only report sections; rebase before push. |

## Autonomy-readiness self-check (Phase-4 gate)

Every wave-1 (Wave A) deliverable has: an architecture spec (ARCHITECTURE §data-model + contracts),
ordered implementation steps (IMPLEMENTATION A1–A5), acceptance criteria (A-AC1–4 + Fallback-AC),
and identified risks (R1–R3). No blocking `@DECIDE` remains — every fork was ruled in the interview
and is captured in the PLAN decisions table with a marked default. Prior-art is recorded (splitter,
parser, block-logic all REUSE with evidence). **Gate: PASS.**

_Dr. Mārcis Gasūns_
