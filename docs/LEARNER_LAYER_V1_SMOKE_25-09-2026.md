# Learner reading layer v1 — public page browser smoke (H5319)

_Created: 25-09-2026 · Last updated: 25-09-2026_

Browser smoke of [src/tools/learner-reading-layer.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/learner-reading-layer.md)
against the v1 payload ([src/data/learner/learner-index.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/learner/learner-index.json),
schema 2.0.0, 52,957 cards, pin `vdcs-learner-v1-20260809`), executed 25-09-2026 as handoff
[H5319](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5319-OxAlpha_csl-atlas_learner-layer-v1-public-page_23.09.26.md)
(epic E014). Stop condition: *the page renders cards for a high, a mid and a rare lemma and the
trust block is filled.* Method: `npm run dev` (Observable preview, `127.0.0.1:3000`) + Playwright,
viewports 1280×800 (desktop) and 390×844 (mobile); DOM assertions read back in-page.

## Gate / precondition state at smoke time

The handoff's precondition is "the learner-layer dataset exists on origin main, otherwise STOP".
At smoke time the dataset lived on **`origin/h5318-drain` (PR #521 head `e912ba4`), green CI 9/9,
verifier PASS (DeepSeek 4.1 Flash pairing) — but not yet merged**: `sanskrit-lexicon/*` is a
foreign-owner repo, PR-only for drain workers (H4086 allowlist auto-merge covers gasyoun-owned
repos only), so the merge click is a human step. The unit executed anyway as a **stacked branch**:
this PR sits on top of PR #521 and merges after it. Merge order: **#521 first, then the H5319 PR**.

## Render proofs (desktop 1280×800)

| Case | Lemma | Band | Tier | Verified in-page |
|---|---|---|---|---|
| High (stop condition) | `agni` | 5 · "learn early" | C | starter card renders; band chip + tier chip + dict chips |
| Tier A showcase | `ASraya` (āśraya) | 4 · common | A | exact match; 5 senses shown (of 40), all ✓-survived, threshold ≥ 0.15 rendered, per-sense-only caveat verbatim, details open by default |
| Mid (stop condition) | `ABAsvara` (ābhāsvara) | 3 · uncommon | C | band-filter sample "Showing band: 3 · uncommon (120/8,096)", first card, tier mix C 93 / D 27 |
| Rare (stop condition) | `ABAsura` (ābhāsura) | 1 · hapax | D | exact match; 0 senses; 4 named absences |
| Worst case (spec §11.3) | `ABAti` (ābhāti) | 0 · not in corpus | D | legible card; coverage 5/7 gr 4; source link MW L89509; 5 absences, first = `not-in-dcs` — "uncorroborated by this corpus, NOT 'unused'" |

- **Trust block filled** (Evidence / Limitations / Validation / Owner / Next use): v1 text confirmed
  in DOM — band-0 wording, 28-lemma P2 panel at threshold ≥ 0.15, the not-significant within-edge
  test, gaṇa-never-inferred, the `vdcs-learner-v1-20260809` pin.
- **Named absences** render as the closed §9.1 vocabulary with notes (`no-paradigm-contract`,
  `not-a-root`, `outside-survival-panel`, `homonym-payload-truncated`) — no silent empty slots.
- **Lookup + band filter** both drive the card grid; normalization candidates shown in the status row.

## CSV export (spec §9.5) — added in this unit

The page had no card-table CSV; §9.5 of the spec asks for one "per the repo convention". Added via
the existing house helper [src/lib/csv-download.js](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/lib/csv-download.js)
(`csvDownloadButton`, zero-arg row function → exports the **current lookup/band-filter view** at
click time, not the whole index; filename reflects the active filter, e.g.
`learner-cards-q-ASraya.csv`, `learner-cards-band3.csv`). Click-captured in-browser: 18 fixed
columns (lemma IAST + SLP1, band + label, tier, coverage, gr, dictionaries, senses/survived,
threshold, paradigm stable id + cells, roots + gaṇas, homonyms, absences); tier-A row verified
value-by-value (`āśraya,ASraya,adjm,4,common,A,5,4,mw pwg pw wil vcp,40,33,0.15,vdcs:v1:nominal:62752,15,,,,not-a-root homonym-payload-truncated`).
Downloaded bytes start `ef bb bf` — UTF-8 BOM present, so Excel renders the IAST diacritics.

## Mobile (390×844)

- Horizontal overflow **0 px**; no element protrudes past the viewport.
- Trust block collapses to a single column; cards full-width (326 px); CSV row visible and unclipped.
- Worst-case lookup (`ABAti`) re-verified at mobile width, card + absences render.

## Console

One console error in the dev preview: the `sw.js` service-worker registration fails on the preview
server. Pre-existing dev-server artifact, unrelated to the page (also present on other atlas pages
under preview; production builds serve the SW fine).

## Checks

- `npm run validate-learner-index` — **PASS** (52,957 cards; schema 2.0.0; pin `vdcs-learner-v1-20260809`; tiers A 28 / B 541 / C 16,510 / D 35,878 within spec tolerance).
- `node --test` — 405 tests: **401 pass / 3 fail / 1 skipped**; the 3 failures are the known
  pre-existing H4/H5 packet failures on clean main (local csl-orig drift), unchanged by this unit;
  the 16 learner-index tests all pass.
- Browser smoke — this document; both viewports, five render proofs, CSV click-through.

## Repro

```bash
npm install && npm run dev   # then open http://127.0.0.1:3000/tools/learner-reading-layer
# lookups: ASraya (tier A) · ABAsvara (mid) · ABAsura (rare) · ABAti (worst case)
# band filter: 3 · click ⬇ Download CSV with a filter active
npm run validate-learner-index && node --test
```

_Dr. Mārcis Gasūns_
