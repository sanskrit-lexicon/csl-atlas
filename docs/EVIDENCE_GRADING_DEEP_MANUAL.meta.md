# EVIDENCE_GRADING_DEEP_MANUAL.meta.md

_Created: 21-07-2026 · Last updated: 21-07-2026_

Companion metadoc for
[EVIDENCE_GRADING_DEEP_MANUAL.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/EVIDENCE_GRADING_DEEP_MANUAL.md).

## Purpose

The durable operator/scholar manual for csl-atlas's evidence-grading methodology and
human-review workflow — the evidence ladder, provenance envelopes, trust blocks,
review queues/packets/auto-triage, decision persistence, hypothesis registry, paper
pipeline, statistics machinery, design rationale, and the incident corpus (previously
scattered in `.ai_state.md` prose). Closes row 11 (and its row-12 operator appendix)
of the org deep-manual gap census
[DEEP_MANUAL_GAP_CENSUS_2026H2.md](https://github.com/gasyoun/Uprava/blob/main/DEEP_MANUAL_GAP_CENSUS_2026H2.md).

## Audience

1. Maintainers running/extending the 93-script pipeline estate without wiping review
   overlays.
2. Scholars/reviewers adjudicating queues and packets, and reading the labels/trust
   blocks critically.
3. Paper authors (P1–P6/A-series) consuming atlas evidence.
4. Org agents (Claude Code / Codex sessions) needing the danger facts and failure
   modes before touching builders.

## Provenance

- Handoff: [H1408](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1408-Fable_csl-atlas_deep-manual-evidence-grading-methodology_20.07.26.md)
  (queued 20-07-2026, executed 21-07-2026).
- Authored by Fable 5 (`claude-fable-5`) against repo state `6956469` (21-07-2026),
  in a worktree off `origin/main`, via a 6-agent parallel subsystem-mining pass
  (evidence ladder/provenance, trust blocks, review queues/persistence, hypothesis
  registry/papers, statistics, incidents/operator layer) followed by single-author
  synthesis.
- Template: [ARCHITECTURE_ORG_DEEP_MANUALS_FABLE_WAVES.md](https://github.com/gasyoun/Uprava/blob/main/docs/ARCHITECTURE_ORG_DEEP_MANUALS_FABLE_WAVES.md);
  verification bar: [VERIFICATION_ORG_DEEP_MANUALS_FABLE_WAVES.md](https://github.com/gasyoun/Uprava/blob/main/docs/VERIFICATION_ORG_DEEP_MANUALS_FABLE_WAVES.md).

## Verification block

LAST_VERIFIED: 21-07-2026
VERIFIED_BY: Fable 5 (claude-fable-5), H1408
COMMANDS_SPOT_RUN: 3

Commands executed during authoring (worktree `csl-atlas-h1408` at `6956469`,
21-07-2026), with real outputs:

1. `npm run validate-review-reports` — all 14 review reports valid; decision-bearing
   counts observed: `r2-checkpoint-review.json` 10× `reviewed-ok`,
   `h5-anomaly-review.json` 130× `reviewed-ok`,
   `low-confidence-alignment-review.json` 7× `reviewed-ok`.
2. `npm run build-r2-checkpoint-review` (plain, no `--reseed`) — output: "Wrote 10 R2
   checkpoint review items (10 human reviews preserved)"; `git status --porcelain
   src/data/review/` empty afterwards — **byte-identical rebuild, preservation
   invariant confirmed live** (the spike queued in H1408).
3. `npm test` — 245 tests, 244 pass, 1 fail. The single failure is the local-only
   drift guard "vendored sanskrit-util.js matches the canonical sanskrit-util source"
   (`test/lib.test.mjs`): `src/lib/sanskrit-util.js` is byte-identical to
   `origin/main` (verified by empty `git diff origin/main`), but the canonical sibling
   `../sanskrit-util/js/index.mjs` received the H1394 `iast_to_devanagari` fix that
   csl-atlas has not re-vendored. Pre-existing on `origin/main`, self-skipped on CI
   (sibling absent there), NOT introduced by this work; spun off as a separate
   re-vendoring task.

Point-in-time censuses in the manual (all dated 21-07-2026, grep-derived, method
stated in place): envelope field coverage over 59 `build-*.mjs` (§4.3); trust-block
coverage 61/64 pages + 8 drift classes (§5.3–5.4); 93 npm scripts = 61 build / 9
validate / 6 import / 17 other (§16.1); hypothesis registry 29 rows + 6 proposed
(§9); 101 active + 14 archived docs under `docs/`.

Independent adversarial refutation pass (verification-bar item 4): run 21-07-2026 by
a separate read-only fact-check agent (same Fable 5 `claude-fable-5` session
spawning, independent context; 84 tool calls) against the finished draft + the
worktree. Both executable claims were re-run live by the verifier and CONFIRMED
(validator exit 0 over 14 files; plain checkpoint rebuild byte-identical, 10/10
preserved). The pass REFUTED 10 claims — census arithmetic (65→64 pages, 15→14
`reviewPayload` importers, 14→15 snapshot fields, "six outputs"→2 fixtures + 4
generators), a stale CI-order description (shared with the repo's CLAUDE.md), a
wrong upstream-check example, a queue-page proof-sentence claim false in substance,
and two overstatements — all corrected in the same pass before commit; the
correction list is preserved in the H1408 session record. Everything else, including
all §3/§6–§8 mechanism claims, schema enums, statistics-engine parameters, and
sampled incident numbers, was CONFIRMED against `6956469`.

Not run in this pass (documented as descriptions, not claims): the full
`scripts/verify.mjs` gate (requires clean tree + `../csl-orig`; its regen-×2
idempotency property was spot-proved on the decision-bearing checkpoint queue
instead); `npm run build` (exercised by CI on the delivering PR).

## Ranked improvement backlog

1. **B1** — Fix the `evidenceLevels` (plural) ghost in
   [docs/EVIDENCE_LABELS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/EVIDENCE_LABELS.md):
   the doc promises a per-field map no script emits; align the doc with the
   implemented singular `evidenceLevel`/`evidenceLabel` pair.
2. **B2** — Generic envelope validator: extend validation beyond
   `src/data/review/` so envelope regressions in display-oriented builders fail CI
   (§4.4).
3. **B3** — Trust-block validator: mechanical check for §5's template (presence,
   field set, order) over `src/**/*.md`, covering the JS/i18n variant; would retire
   drift classes 1–6 in §5.4.
4. **B4** — Orphaned-decision report: surface (not silently drop) human decisions
   whose `reviewId` vanishes from a rebuilt candidate set (§8.1).
5. **B5** — Resolve the OBS-R A-ID inconsistency (A07 in
   [docs/PUBLICATIONS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/PUBLICATIONS.md)
   vs "(A01)" in
   [docs/HYPOTHESIS_INDEX.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/HYPOTHESIS_INDEX.md))
   against Uprava ARTICLES.md.
6. **B6** — Unit-test `nodf`/`modularity`/`trySwap` in
   [scripts/build-citation-canon.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-citation-canon.mjs)
   against known fixtures; add a `validate-r2-h2h3` sibling (§11.4).
7. **B7** — One-off cross-validation of the IRLS + CR1 engine against a reference
   implementation (R/statsmodels), recording the comparison as a committed fixture.
8. **B8** — Unify the label vocabulary drift: either enum-lock `evidenceLabel` or
   document the extended vocabulary deliberately (§3.2).
9. **B9** — Fix the stale CI description in the repo's
   [CLAUDE.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/CLAUDE.md)
   (it still lists `npm test` → `validate-review-reports` → build as separate CI
   steps; actual CI is `npm ci` → `npm run verify`, and `test.yml` triggers are
   `pull_request` + `workflow_dispatch` — §16.2). Optionally align the queue pages'
   proof sentences with the template's exact `This queue proves:` colon form
   (§5.4 item 7 — a formatting nit; the substance is already implemented).

## Limitations

- The manual's censuses are dated point-in-time greps, not live queries; refresh by
  re-derivation, not increment.
- GitHub issue/PR *thread* bodies for the YAT arc (#125/#133/#134) were not fetched;
  the incident chapter rests on commits, the archived journal, and
  [docs/R2_SEMICOLON_COUNTER_REVIEW.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/R2_SEMICOLON_COUNTER_REVIEW.md).
- Incidents predating the 2026-06-05 R2 contract survive only as summaries in the
  archived journal's tail; earlier history was itself truncated (§13.7's journal-loss
  incident explains why).
- The MWS-side canonical microanalysis paper (toured by `src/paper/`) is outside this
  repo and was not verified.

## Related documents

[ARCHITECTURE.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/ARCHITECTURE.md) ·
[docs/EVIDENCE_LABELS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/EVIDENCE_LABELS.md) ·
[docs/REVIEW_REPORTS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_REPORTS.md) ·
[docs/REVIEW_QUEUE_PROOFS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_QUEUE_PROOFS.md) ·
[docs/CHART_TRUST_TEMPLATE.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/CHART_TRUST_TEMPLATE.md) ·
[docs/HYPOTHESIS_INDEX.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/HYPOTHESIS_INDEX.md) ·
[docs/R2_REBUILD_CONTRACT.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/R2_REBUILD_CONTRACT.md) ·
[docs/A10_REPRODUCIBILITY_AUDIT.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/A10_REPRODUCIBILITY_AUDIT.md) ·
[docs/PUBLICATIONS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/PUBLICATIONS.md)

## Revision history

| Date | Change | By |
|---|---|---|
| 21-07-2026 | Initial authoring (H1408): full manual + metadoc, preservation spike run, censuses derived; 10 refutations from the independent adversarial pass corrected pre-commit | Fable 5 (`claude-fable-5`) |

_Dr. Mārcis Gasūns_
