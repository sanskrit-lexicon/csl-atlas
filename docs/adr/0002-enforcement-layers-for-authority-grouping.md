# 0002 — Enforcement layers for the dictionary authority grouping

ADR-0001 ruled the grouping but left it unenforced — a future sheet could silently
reintroduce the flat anonymous census badge. Decided MG 21-11-2026 (grilling round,
four rulings): three complementary layers, strongest-first. (1) **Deterministic gate**:
`scripts/validate-dict-authority-tiers.mjs` in verify.mjs VALIDATORS (CI + `npm run
verify`) — census coverage, Grundlagen invariant (PWG+PW in Tier A), generator
consumption of the tiers CSV, flat-badge literal banned from scripts/src/tools;
fail-closed, with the `DICT_TIERS_CSV` test seam for negative testing. (2) **Org
convention**: standing rule in the review-sheet skill (`~/.zcode/skills/review-sheet/
SKILL.md`, census-badge rule next to the naming rule), so every sheet-authoring session
in any repo loads the rule at authorship time. (3) **Reminder hook**: global PostToolUse
hook `~/.claude/hooks/check_flat_dict_badge.py` (narrow flat-badge literal match,
emits via `hookSpecificOutput.additionalContext` per H1817) for sessions outside
csl-atlas; reminder only, never blocks. A periodic estate sweep was rejected as noise —
the three layers cover the commit, authorship, and edit moments respectively.
