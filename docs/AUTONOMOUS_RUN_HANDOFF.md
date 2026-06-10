# Autonomous Run Handoff Prompt

The self-pacing prompt the `/loop` carries forward each iteration. Also usable to
**resume in a fresh session** or to seed a **cloud `/schedule`** if this terminal closes
(a self-paced `/loop` only lives as long as the session). Paste the block below verbatim.

> A self-paced `/loop` stops when the session closes. If you need it to survive a week
> unattended, re-seed it as a cloud routine: `/schedule every 2 hours <the prompt below>`.

## The prompt

```
/loop [Autonomous run · csl-atlas 3-week roadmap · self-paced · M.G. away]

You are mid-run, continuing unattended work. Each iteration:

1. ORIENT. `git fetch origin`. Never trust the local checkout or HEAD — an external
   bot moves it. Read docs/AUTONOMOUS_RUN_CHARTER.md, docs/AUTONOMOUS_RUN_ROADMAP.md,
   docs/AUTONOMOUS_RUN_HANDOFF.md (on origin/main). These three repo docs are
   self-contained and authoritative — follow them exactly. (No external memory or
   prior chat context is required; everything you need is in this repo.)

2. PICK NEXT. From .ai_state.md + merged/open PRs, find the next incomplete roadmap
   cell — do not assume a fixed starting item; the run is already in progress and a
   parallel automation may have shipped some cells. Keep the four streams balanced
   across the week (atlas viz · Cologne tooling · decision-support · research).

3. DO IT in a fresh worktree off origin/main, production-ready (generator + JSON with
   empty human fields + page/tests + docs, idempotent — rerun must give no git diff).
   STAY OUT OF THE BOT'S LANE: a parallel automation also commits to this repo (it
   recently merged PR #55 siglum-aliases and PR #58 dcs-summary-adapter). Before
   editing any file, `git fetch` and check it isn't being worked on another open
   branch/PR; on collision risk, switch to a different queue item.

4. SHIP. Feature branch; open the PR with `gh api -X POST repos/.../pulls` (REST —
   GraphQL / `gh pr create` has been TLS-timing-out). Auto-merge on green CI ONLY for
   mechanical tooling batches and own-repo (csl-atlas) changes; HOLD feature/content
   PRs on other maintainer-watched org repos for M.G.'s review.

5. BLOCKED with no safe default → take the documented default, record the open decision
   in DECISIONS_NEEDED.md, and move to the next item. Never stall the loop on one gate.

6. JOURNAL every increment to .ai_state.md (ai-wip: commits). At each week boundary
   write docs/WEEK_N_REVIEW.md as a PR.

7. NOTIFY M.G. only on a no-default blocker or unfixable red CI. Otherwise silent.

Scholar line: for human-gated packets, write a machine SUGGESTION + confidence in a
separate field; leave every human-decision field at needs-review. No final scholarly
or maker calls. Intensity: no ceiling. Continue draining the queue.
```

## Status pointers (updated by the run)
- Shipped pre-Week-1: R2 page regeneration → PR #56.
- Setup PR (charter + roadmap + this handoff): PR #57; handoff made portable in PR #62.
- Run is in progress: Week 1 viz items began landing via PR #61 (incl. the
  sense-divergence map). **Derive the current position from .ai_state.md + PRs** — do
  not trust a hardcoded position here.
