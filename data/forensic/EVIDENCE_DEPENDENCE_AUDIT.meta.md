# Metadoc — EVIDENCE_DEPENDENCE_AUDIT.md

_Created: 20-09-2026 · Last updated: 22-09-2026_

A document about [`EVIDENCE_DEPENDENCE_AUDIT.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/EVIDENCE_DEPENDENCE_AUDIT.md).

## Purpose & audience

The second-order check on the A10 forensic suite. H4352 asked "is each number
computed correctly?"; this asks "are the numbers independent evidence, and does
the combination overstate the historical case?" Audience: the A10 referee, the
paper's later revisions, and anyone reusing the F1/F5/F9 signals as a template
for separating content-descent from error-descent in another corpus of related
editions — the audit's controls are the reusable part.

## Provenance

Built under [H5073](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5073-Opus_csl-atlas_forensic-combined-evidence-dependence-audit_17.09.26.md)
by Claude Code Opus 5 (`claude-opus-5`), 20-09-2026. Handoff minted by Codex
Astra (`gpt-6-astra`), 16-09-2026. Script:
[`f11_evidence_dependence.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f11_evidence_dependence.py)
(deterministic across processes, stdlib-only, offline, `seed = 20260920`, ~60 s). Pins:
[`test_f11_evidence_dependence.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_f11_evidence_dependence.py).
Predecessor: [`FORENSIC_CLAIM_PINS_COVERAGE_08-09-2026.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/FORENSIC_CLAIM_PINS_COVERAGE_08-09-2026.md)
(H4352, Fable 5.1).

## Key measured facts

- **`A10-C2` is 100% nested inside `A10-C1`** — all 3,583 order-bearing entries are §3.2 shared-cited lemmas. Not a second corroboration.
- **Rare-reference pool is 94.5% Harivaṃśa** (565/598); 33 events over 18 other texts survive ablation. Same source events as §6.
- **Naive sum of the three locus sets double-counts 7,280** (91,124 → 83,844 distinct).
- **`CTRL-DUP` PASS, but structural** — a seeded verbatim PWG duplicate moves naive witness events 598 → 1,125 (+88.1%) and independent source events by **0**; the Δ cannot fail, so the falsifiable twin **`CTRL-NOVEL`** was added (100 novel triples = 91 distinct new keys → support +91, expected +91, PASS).
- **`CTRL-PWDUP`** — 33.8% of PW's rare events are already PWG's; 598 naive → 574 independent.
- **`CTRL-ABL-S`** — separation never collapses across ablation depths 5–100 (8.60×–18.31×; 16.29× at the frozen depth 25, against 9.69× unablated). The *widening* is depth-25-specific; only survival is robust.
- **`CTRL-CONV`** — on 4,685 convention-discordant sigil pairs MW follows PWG's per-entry order at **0.7518**. Against the best non-lineage reference (Benfey 0.6337, 101 pairs) the unmatched excess is **+0.118** (entry-clustered bootstrap 95 % [+0.023, +0.210]) — but the arms score different populations (2,168 vs 64 entries; 24 shared loci, on which BEN agrees *more*, 0.750 vs 0.667), so the margin is descriptive, not an identified copying excess (independent review 22-09-2026). Against the within-entry permutation floor (0.5004, 200 reps) it is +0.251, but that floor represents no signal at all.
- **`A10-C3` is the only locus-disjoint leg** — 3,244 anchor words (46.7%) touch neither citation locus set; disjoint loci, not proven statistical independence.
- **Provenance gap** — F9 reproduces exactly (12.336 / 1.51, frozen `key1` exports); F1/F5 drift (587 → 598, 3,593 → 3,583) — most plausibly upstream drift, not proven exclusive, because no sidecar pins the `csl-orig` revision; the parsed cache's own generating revision is unrecorded too (`parse_cslorig.py` now writes `_parse_provenance.json` for future builds).

## Ranked improvement backlog

1. **Pin `csl-orig` in every `.source.json` sidecar** and re-freeze the F1/F5/F10 figures against one named revision — the cleanest fix for §4's gap, and it moves every `f*_report.json` at once. — *status: open, medium.*
2. **Entry-type covariate for `CTRL-CONV`** — a conditional ordering convention (Veda-first in grammatical entries, epic-first in narrative ones) is scored as convention-defying today, and a pinned counterexample scores 1.0 with no copying — 0.7518 is a pair-agreement rate, not a bound on copying. — *status: open, needs an entry-type signal this repo lacks.*
3. **Extend the audit to §3.1 and §3.3** — headword containment and homonym concordance were out of H5073's three-claim scope; the PW-as-duplicate-witness caution applies to §3.1's PWG 0.70 / PW 0.71 gradient with more force than it does here. — *status: open, cheap.*
4. **A genuinely unexposed reference arm** — Benfey now carries the floor at 101 discordant pairs but has its own Petersburg exposure, and Apte's 13 pairs are unusable. A contemporary with no Petersburg contact, or a lowered `MIN_SHARED_SRC` for the reference arms only with the bias stated, plus a matched-loci comparison with enough shared pairs (today 24), would be needed before any copying margin is defensible. — *status: open, cheap.* (Partially addressed 20-09-2026: the reference floor replaced the 8-entry Apte null.)
5. **Independence at the level of decisions, not loci** — disjoint locus sets do not make MW's decision to enter a word and its decision to cite a text for it statistically independent. — *status: open, research.*

## Known limitations / caveats

- The global-convention estimator is a mean normalised sigil position; it cannot see a conditional convention (backlog 2).
- `CTRL-ABL-S` ablates by corpus document-frequency, a proxy for "texts everyone cites", not the thing itself.
- Sub-`<L>` entries are folded per `k1`, matching F1/F5 — MW's habit of splitting one word across several `<L>` records is invisible here exactly as it is in the audited signals.
- SKD/VCP `key1` exports are absent from the `now-2026` snapshot on some boxes; the raw-`<k1>` fallback reproduces both counts exactly (40,817 / 48,636), and the report records which path ran under `anchor_sources`.
- No claim was refuted and no published figure revised. The audit's output is a constraint on how the signals may be *combined*.

## Related documents

- Under audit: [`article_21_apparatus_not_errors.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md) (A10) §3.2, §3.4, §3.5, §6, §7.
- Arithmetic layer: [`FORENSIC_CLAIM_PINS_COVERAGE_08-09-2026.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/FORENSIC_CLAIM_PINS_COVERAGE_08-09-2026.md).
- The Harivaṃśa stratum: [`HARIVAMSA_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/HARIVAMSA_CITATION_RESOLUTION_CENSUS.md).
- The omission anchor: [`SHARED_OMISSION_TEST.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/SHARED_OMISSION_TEST.md).

## Revision history

| Date | Change | By |
|---|---|---|
| 20-09-2026 | Created with the subject audit (H5073): three claim→signal→locus graphs, deduplicated accounting, six controls, corpus-revision pin. | Claude Code Opus 5 (`claude-opus-5`) |
| 20-09-2026 | Post-review revision (same session, four findings of an OxAlpha GLM 5.3 Flash pre-review): cross-process determinism fixed (sorted entry set, tie-broken counters) and the permutation band re-measured; `CTRL-NOVEL` added as `CTRL-DUP`'s falsifiable twin; `CTRL-CONV` given non-lineage reference arms and the margin restated as +0.118 over Benfey; `CTRL-ABL-S` given a depth sweep and "widens" replaced by "never collapses". Pins 13 → 14. | Claude Code Opus 5 (`claude-opus-5`) |

_Dr. Mārcis Gasūns_
