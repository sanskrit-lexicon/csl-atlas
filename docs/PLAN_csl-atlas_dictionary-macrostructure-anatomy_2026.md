# PLAN — Cross-dictionary macrostructure anatomy (H1416 phase 2)

_Created: 21-07-2026 · Last updated: 21-07-2026_

**Execution index.** This is the cover doc a fresh agent reads first, then executes the four
layer docs below. Authored via `/ask` (heavy up-front interview → layered plan) on 21-07-2026,
Opus 4.8 (`claude-opus-4-8`). Extends H1416
([LETTER_ANATOMY_AND_ENTRY_SIZE_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/LETTER_ANATOMY_AND_ENTRY_SIZE_2026.md)).

## Goal (one paragraph)

Generalise the H1416 letter-anatomy findings from MW to the completed Cologne dictionaries and
deepen the entry-size decay result into real publication time. Three independent waves, each
shipping the H1416 deliverable shape (derived TSV feed + report section + Observable page):
**(A)** a cross-dictionary compound/preverb law — using the DharmaMitra ByT5 splitter on a
stratified per-letter sample, calibrated against MW's dash ground-truth, reporting both the
conservative dash-truth claim and the splitter estimates with their measured error; **(B)** the
funding-decay "why" — regressing PWG entry-size on real calendar year (via the confirmed
`<pc>`→volume→year mapping) and testing the editorial-compression counter-explanation, best-
effort for the other serial dicts; **(D)** a multi-signal cross-dictionary density fingerprint
(chars/senses/blocks per entry) on a new page. Scope: MW/AP/PWG/PWK primary, SKD/VCP as an
explicit contrast, GRA for dash-truth. No paper in this span.

## Layer docs

- **Roadmap** — [ROADMAP_csl-atlas_dictionary-macrostructure-anatomy_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/ROADMAP_csl-atlas_dictionary-macrostructure-anatomy_2026.md) — waves A/B/D, deliverables, non-goals, sequencing.
- **Architecture** — [ARCHITECTURE_csl-atlas_dictionary-macrostructure-anatomy.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/ARCHITECTURE_csl-atlas_dictionary-macrostructure-anatomy.md) — component map, data model, interfaces, build-vs-reuse verdicts.
- **Implementation** — [IMPLEMENTATION_csl-atlas_dictionary-macrostructure-anatomy.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/IMPLEMENTATION_csl-atlas_dictionary-macrostructure-anatomy.md) — file-level ordered steps (0 → A → B → D → F).
- **Verification** — [VERIFICATION_csl-atlas_dictionary-macrostructure-anatomy.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/VERIFICATION_csl-atlas_dictionary-macrostructure-anatomy.md) — acceptance criteria, proof commands, risks/spikes, the passed autonomy gate.

## Decisions taken (every interview ruling + rationale)

| # | Decision | Ruling | Rationale |
|---|---|---|---|
| D1 | Direction | **All three waves** A (compound law) + B (funding-why) + D (density) | User wants the full analytical program, not one slice |
| D2 | Dictionary scope | MW/AP/PWG/PWK primary + **SKD/VCP as explicit contrast** + GRA dash-truth | Skt→Skt encyclopedics behave differently (H1416); don't pool |
| D3 | Output | Data + report + viz page (H1416 shape) | Self-contained csl-atlas deliverable; paper is a later step |
| D4 | Execution | **Autonomous 5–8h build** | Mint handoff, run unattended → autonomy contract below |
| D5 | Compound-law basis | **Both** — calibrated splitter estimates AND dash-truth-only claim, compared | Makes the splitter's reliability itself a finding; most rigorous |
| D6 | Splitter scale | **Stratified per-letter sample** (~300/letter) | Full-corpus ByT5 is GPU-heavy; sample suffices for per-letter share + CI |
| D7 | Funding wave scope | **All serial dicts, best-effort dates** | PWG clean via `<pc>`; PWK/SKD/VCP flagged `date_quality` |
| D8 | Density definition | **Multi-signal** (chars+senses+blocks) on a **new** cross-dict page | Richer than chars-only; reuses mw-depth block logic |
| D9 | Calibration gate | **Ship splitter estimates with measured MW error attached** (do not auto-suppress) | Reader weighs reliability; poor calibration is itself reported |

## Autonomy contract (verbatim — governs the unattended run)

- **On ambiguity:** pick the marked default for the fork, **log the choice in the report, and
  continue.** For anything unforeseen, choose the most conservative option and record it. Never
  stall waiting for a human — none is reachable.
- **Stop conditions (halt only on hard blockers):** halt only if (a) the ByT5 model/network is
  unavailable AND the dash-truth fallback also fails, (b) a required data source is missing, or
  (c) a site build stays red after 6 tries. Otherwise press on and report gaps. Wave-level
  blocks (e.g. ByT5 down ⇒ Wave A degrades to dash-truth-only) do **not** stop the other waves.
- **Commit authority:** commit → PR → merge is **authorized** for this handoff (handoff-scoped
  autonomy rule); csl-atlas via PR, Uprava via direct push to main, SL via PR.
- **The fence — may touch:** csl-atlas `data/pd/`, `data/dharmamitra/`, `reports/`, `scripts/`,
  `src/tools/`, `src/data/pd/`, `CHANGELOG.md`, `observablehq.config.js`; and the standard hub
  sweep — Uprava `handoffs/README.md` + `PROJECT_INTERLINKS.md`, SanskritLexicography
  `FINDINGS.md` + `changelog.md`. **Must NOT touch:** `csl-orig` source, other dictionaries'
  pipelines, any model training/fine-tuning, or any other repo (kosha/VisualDCS are read-only
  consumed, not edited).
- **Calibration gate:** splitter compound-share is always shipped **with the MW-measured error
  bar**; it is labelled an estimate (model evidence), never ground truth.
- **Determinism:** no `Math.random`/`random`/`Date.now`/`new Date()` in the derived-data path
  (stride sampling, passed-in dates) so re-runs are byte-identical.

## Execution

```
Read C:\Users\user\Documents\GitHub\csl-atlas\docs\PLAN_csl-atlas_dictionary-macrostructure-anatomy_2026.md and execute it.
```

Run on Opus 4.8 (`claude-opus-4-8`) — the calibration design, the funding-vs-compression
adjudication, and the evidence-grading are judgment calls. Start at IMPLEMENTATION Step 0 (the
ByT5 spike), then Wave A → B → D → F.

_Dr. Mārcis Gasūns_
