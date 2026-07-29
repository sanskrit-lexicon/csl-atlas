# Autonomous Run Roadmap — 3 weeks, balanced

_Created: 10-06-2026 · Last updated: 29-07-2026_

> **SUPERSEDED (29-07-2026, H1877 roadmap-drift sweep).** This plan's literal 3-week
> window closed ~2026-07-01 with no `WEEK_N_REVIEW.md` filed, and the Week 1-3
> "decision-support" deliverables (adding a `machineSuggestion`/`confidence` field to
> the R2 checkpoint / Xref / H4 review packets, as literally scoped in the matrix
> below) were never built under those names. They are functionally superseded by a
> separate **auto-triage initiative**, completed and recorded "Auto-triage initiative
> COMPLETE" in `.ai_state.md` on 2026-06-17: `build-h4-review-packet.mjs` and
> `build-xref-source-check-packet.mjs` gained an `applyAutoTriage` rule table that
> mechanically auto-resolves the easy rows instead of adding a machine-suggestion
> field to every row. Post auto-triage, the remaining unreviewed rows — **40 in the
> Xref shared-core packet, 89 in the H4 semantic-field packet** — are documented as
> carrying **zero mechanical signal** (pure scholarly judgement calls), so this
> roadmap's literal Week 1-3 matrix below will not be built as scoped — kept for
> historical record only. Live human-review work is tracked in `.ai_state.md`.

Companion to `AUTONOMOUS_RUN_CHARTER.md`. Set 2026-06-10 (M.G. away). Structure:
**three weekly phases**, each ending in a `WEEK_N_REVIEW.md` PR M.G. reads async.
Aim: **balanced progress across all four streams** every week (not one stream per week).
Intensity: **no ceiling**. Quality bar: **production-ready** (generator + JSON + tests +
docs, idempotent). Git/isolation/blocker rules: see charter.

## Locked parameters

| Param | Value |
|---|---|
| Streams | (1) csl-atlas viz · (2) Cologne org tooling · (3) decision-support · (4) other research |
| Weighting | Balanced — touch all four each week |
| Phasing | 3 weeks, weekly re-eval + `WEEK_N_REVIEW.md` PR |
| Git | feature branches + auto-merge on green CI, **scoped**: auto-merge mechanical batches + own-repo (csl-atlas); hold feature PRs on other org repos for review |
| Blocked | default + record in `DECISIONS_NEEDED.md`, keep moving |
| Notify | only on no-default blocker / unfixable red CI; else silent + weekly doc |
| Isolation | worktree off `origin/main` per item; **stay out of the parallel bot's lane** — a parallel automation also commits/merges here; `git fetch` and check before editing any file |
| Scholar line | suggest value + confidence in a **separate** field; human field stays `needs-review` |

## The matrix

### Week 1 — Foundations & smallest-leverage slices
| Stream | Deliverable | Acceptance |
|---|---|---|
| **1 Viz** | **Sense-divergence map** — where dicts disagree on a lemma's senses (senses with no/low cross-dict alignment), as a maker worklist. | generator + JSON (empty human fields) + page + tests; idempotent; PR. |
| **2 Tooling** | **Baseline hygiene sweep, all org repos**: `dependabot`, `code-of-conduct`, `contributing`. Auto-detect ecosystems. | one PR per repo (or batch), green CI, auto-merge eligible; skip-list logged. |
| **3 Decision-support** | **R2 checkpoint** (10 rows) — suggested decision + confidence per row in a new suggestion field. | `r2-checkpoint-review.json` gains `machineSuggestion`/`confidence`; human fields untouched; doc; PR. |
| **4 Research** | **Triage** IndologyScholars + Afanasiy Nikitin: feasibility, rights, smallest tractable increment. (VisualDCS adapter = bot's lane, skip.) | a `TRIAGE.md` per repo + one concrete starter PR on the most tractable. |

### Week 2 — Depth & security
| Stream | Deliverable | Acceptance |
|---|---|---|
| **1 Viz** | **Sense-alignment micro view** — per-lemma drill-down of the cross-dict alignments in `r2_align_<lemma>.json`. | new page + reused/extended generator + tests; idempotent; PR. |
| **2 Tooling** | **Security/CI sweep**: `codeql` (repos with code) + `pre-commit` across all repos. | per-repo PRs, green CI; pure-content repos correctly skipped + logged. |
| **3 Decision-support** | **Xref source-check** (40 shared-core + 10 prefix-control) — suggested adjudication + confidence. | suggestion fields added; human fields untouched; doc; PR. |
| **4 Research** | **Deepen** the Week-1 pick (e.g. IndologyScholars enwiki scraper hardening via `enwiki_bridge.py`, RKN-proof path). | working increment + tests/fixtures where applicable; PR. |

### Week 3 — Breadth-close & the big packet
| Stream | Deliverable | Acceptance |
|---|---|---|
| **1 Viz** | **H1 panel viz refresh** — render `r2_h1_panel.json` (MW-artifact-removed) as its own page; consolidate/polish the R2 viz set. | page + tests; nav wired; idempotent; PR. |
| **2 Tooling** | **Governance sweep**: `branch-protect-all` + `issue-runbook`/`runbook-all` (taxonomy) across remaining repos. | per-repo; taxonomy verified (paginate, exclude PRs); stale default labels deleted. |
| **3 Decision-support** | **H4 semantic-field** (105 rows) — suggested field + confidence; plus confirm H5 `divaraTa→diviraTa` is queued for makers. | suggestion fields on all 105; human fields untouched; doc; PR. |
| **4 Research** | **Second repo or consolidate** — Afanasiy FAIR/LOD spine starter, or harden Week-2 work into a reusable, citable resource. | scoped deliverable + doc; PR. |

## Weekly checkpoint protocol
At each week's close, in a worktree off `origin/main`:
1. Write `docs/WEEK_N_REVIEW.md`: shipped (with PR links), decisions taken + defaults used,
   `DECISIONS_NEEDED.md` additions, blockers, and proposed adjustments for the next week.
2. Open it as a PR (docs-only → auto-merge eligible) so M.G. can read async.
3. Update `.ai_state.md` (Completed / Next Steps / Dev Notes) and the charter queue checkboxes.
4. Re-evaluate: if a stream is blocked or a priority shifted, rebalance the next week's row.

## Standing guards
- **Stay out of the bot's lane.** A parallel automation actively commits/merges to this repo. Before touching any csl-atlas file, `git fetch` and check it isn't being worked on another open branch/PR. On collision risk, switch queue items.
- **Never make a final scholarly/maker call.** Suggestions only; humans decide.
- **No parser/JSON-schema changes for viz** (presentation only) unless a packet's contract explicitly calls for a new suggestion field (Stream 3).
- **Idempotent or it isn't done.** Re-running any generator must produce no git diff.

_Dr. Mārcis Gasūns_
