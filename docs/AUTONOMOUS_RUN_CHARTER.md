# Autonomous Run Charter

Operating rules for the week-long unattended run set up **2026-06-10** (M.G. away;
"work for a week without me"). The next session / loop iteration should read this
before acting. Supersedes ad-hoc assumptions; M.G. may override any line on return.

## Operating rules

| Rule | Value | Source |
|---|---|---|
| **Streams in scope** | csl-atlas viz · Cologne org runbooks/tooling · other research repos · decision-support prep | M.G. chose all four |
| **Lead priority** | 1) csl-atlas viz → 2) Cologne tooling → 3) decision-support prep → 4) other research repos | adopted (own-repo first, lowest coordination risk) |
| **When blocked** | Take the documented default, record the open decision in `DECISIONS_NEEDED.md`, keep moving. Never stall the week on one gate. | M.G. chose |
| **Git** | Feature branches + **auto-merge on green CI** — *scoped* (see below) | M.G. chose; scope adopted |
| **Auto-merge scope** | Auto-merge on green CI for **mechanical/tooling batches** and **changes in csl-atlas (own repo)**. **Hold feature/content PRs on other maintainer-watched org repos** for M.G.'s review. | adopted — pending confirm |
| **Notify M.G.** | Only on a blocker with no safe default, or red CI I cannot fix. Otherwise silent; journal to `.ai_state.md`. | adopted — pending confirm |
| **Cadence** | Self-paced (work + re-wake until queue drained or blocked). | adopted — pending confirm |

*"Pending confirm"* = my recommended default for a question M.G. left unanswered; safe to override.

## Branch-hygiene protocol (MANDATORY)

An external actor / parallel automation mutates this local checkout mid-session:
during setup it switched `HEAD` to another branch and advanced `origin/main` (PR #55)
underneath the session. Therefore:

1. **Never trust the local checkout's current branch or HEAD.** Always `git fetch` first.
2. **Do every work item in a fresh worktree off `origin/main`:**
   `git worktree add ../csl-atlas-<task> -b <branch> origin/main`.
3. **Open/merge PRs via `gh` against remote refs**, not the local branch.
4. Clean up worktrees when done (`git worktree remove`).

See memory `csl-atlas-branch-hygiene` and `feedback-autonomous-task-prefs`.

## Queue

### Stream 1 — csl-atlas viz engineering (lead)
- [ ] **R2 page-regen PR** (`feature/r2-page-regen`, `b72d068`): push done; open PR → main. *(blocked 2026-06-10 on api.github.com TLS timeouts; retry.)* Hold for review (feature change, but own repo — eligible for auto-merge on green CI).
- [ ] **Sense-divergence map** (maker worklist) — where dictionaries disagree on a lemma's senses; surface as a reviewable list. Generator + JSON (empty human fields) + page + tests.
- [ ] **Sense-alignment micro view** — per-lemma drill-down of the cross-dict alignments already in `r2_align_<lemma>.json`.
- [ ] **H1 panel viz refresh** — render `r2_h1_panel.json` (fixed-lemma, MW-artifact-removed) as its own page.

### Stream 2 — Cologne org runbooks + tooling
- Mechanical batch skills across sanskrit-lexicon repos (CodeQL, dependabot, pre-commit, CoC, branch-protect, CONTRIBUTING, issue-taxonomy runbook). Auto-merge eligible on green CI. Keep bot noise minimal (see `project-maintainer-comment-noise`).

### Stream 3 — Decision-support prep
- Deepen the four human-gated packets (R2 checkpoint · H4 · H5 maker · xref) with analysis + recommendations; keep `DECISIONS_NEEDED.md` current. **Make no final scholarly/maker call.**

### Stream 4 — Other research repos (some blocked)
- VisualDCS (blocked: must emit `dcs_lemma_summary.json` first), IndologyScholars scrapers, Afanasiy Nikitin atlas.

## Definition of done (per item)
Tests green (`npm test`), idempotent generators (rerun → no git diff), docs/journal updated,
PR opened (auto-merged only within the scope above). Presentation-only for viz: no parser/JSON-schema changes.
