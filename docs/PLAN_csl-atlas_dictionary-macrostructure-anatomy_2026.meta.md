# PLAN_csl-atlas_dictionary-macrostructure-anatomy_2026 — metadoc

_Created: 21-07-2026 · Last updated: 21-07-2026_

**Purpose.** Companion record for the phase-2 execution plan
([PLAN](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/PLAN_csl-atlas_dictionary-macrostructure-anatomy_2026.md))
that generalises the H1416 letter-anatomy study across dictionaries.

**Audience.** The autonomous execution agent (fresh session, Opus tier) that runs the plan
unattended, and any human reviewing what was decided and why.

**Provenance.** Authored via `/ask` (heavy up-front interview: 3 rounds × 4 questions, all
rulings in the PLAN decisions table) on 21-07-2026, Opus 4.8 (`claude-opus-4-8`). Follows H1416
([PR #282](https://github.com/sanskrit-lexicon/csl-atlas/pull/282)/[#284](https://github.com/sanskrit-lexicon/csl-atlas/pull/284)).
The interview resolved every blocking fork; the autonomy-readiness gate passed (VERIFICATION
Phase-4 self-check).

**Improvement backlog (ranked).**
1. If Wave A's ByT5 calibration F1 turns out high (>0.9), promote splitter compound-share from
   "estimate + error" to a near-ground-truth claim in a follow-up — currently held at estimate.
2. Source real per-fascicule dates for PWK/SKD/VCP (currently best-effort/absent) to make Wave B
   cross-dictionary rather than PWG-only for the clean signal.
3. The write-up toward book Ch.7 (macrostructure) / article A68 is deliberately out of span —
   schedule after the three data waves land.

**Limitations.** Splitter output is model evidence, not truth (house rule); Wave B's calendar-
year signal is clean only for PWG; density block-markers differ per dict and are documented, not
uniform. SKD/VCP heavy tails force median-alongside-mean throughout.

**Related.** [[h1416-letter-anatomy]] · [[csl-atlas-observable-offline-build]] (build cache
trick) · H1336 PD×DCS study (the parent lineage).

**Revision history.**
- 21-07-2026 — created alongside the PLAN (Opus 4.8, `/ask`).

_Dr. Mārcis Gasūns_
