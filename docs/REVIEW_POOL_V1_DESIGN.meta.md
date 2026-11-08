# REVIEW_POOL_V1_DESIGN.md — metadoc

_Created: 24-09-2026 · Last updated: 24-09-2026_

Companion record for
[`docs/REVIEW_POOL_V1_DESIGN.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_POOL_V1_DESIGN.md).

## Purpose

Design of record for the community review pool v1 — the mechanism that closes roadmap gap
**G4** (single-reviewer bottleneck: R2 ×10, H4 ×105, xref ×50 blocked on one person, so no
inter-annotator agreement exists). It fixes four things that had no written rule: annotator
identity without personal data in a public repo, the assignment rule that gives every row two
independent keys, the adjudication rule for disagreements, and the shape of the κ report.
Eight of its twelve sections are a reuse inventory and a named build list — the document
exists so the pool is implemented as patches to the existing sheet/validator/overlay stack,
not as a second review system.

## Audience

The session that implements B1–B9 (§7); the pool coordinator running intake and adjudication;
any reviewer of P1/P2/P5 asking where the atlas's reliability figure comes from. Not
student-facing — that is
[`REVIEW_POOL_STUDENT_GUIDE.ru.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_POOL_STUDENT_GUIDE.ru.md).

## Provenance

- Handoff: [H5307](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5307-Opus_csl-atlas_review-pool-v1-double-keying-design_23.09.26.md)
  (epic E014, ATLAS fair-pubs wave 1); roadmap item «Community review pool v1» and gap G4 in
  [ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md).
- Model: Claude Code Opus 5 (`claude-opus-5`), 24-09-2026.
- Every count in §3 was probed live on this branch, not copied from the roadmap: packet row
  counts from `data/lexico/*_packet.json`, recorded decisions from
  `src/data/review/r2-checkpoint-review.json`, and the validator's expected-sheet sizes by
  importing `expected_sheets()` directly (102 / 114 / **0** / 40).
- Sibling docs: [REVIEW_REPORTS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/REVIEW_REPORTS.md)
  (the overlay contract the pool lands in), [ROOT_AGREEMENT_KAPPA.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/ROOT_AGREEMENT_KAPPA.md)
  (the κ method and banding reused), [XREF_SHARED_CORE_LABEL_TAXONOMY.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/XREF_SHARED_CORE_LABEL_TAXONOMY.md)
  and [H4_SEMANTIC_FIELD_REVIEW.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/H4_SEMANTIC_FIELD_REVIEW.md)
  (label vocabularies), [BOUNDARY_RULES.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/BOUNDARY_RULES.md)
  (the no-backend constraint §6 obeys).

## Two live defects the design surfaced

Both were found by probing, both block the pool before a student ever sees a sheet, and both
are carried as B1 and B3 in §7:

1. `expected_sheets()` in
   [`scripts/validate_review_decisions.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/validate_review_decisions.py)
   selects H4 rows by `reviewStatus == "needs-review"`, which H1621 emptied — the validator
   expects 0 rows while `build-review-sheets.py` emits 89 cards, so every H4 export fails.
2. The H4 card renders `Agent decision: <label>`. Correct for a QA pass, fatal for a
   double-keyed reliability measurement.

## Sync rules

1. Re-cutting any of the three packets (row counts, label vocabulary) updates §3's table here,
   the student guide's matching tables (the `CLAUDE.md` H5310 rule), and the assignment
   manifest in the same PR.
2. Measured results never land in the design doc — they belong to the generated κ report
   (`data/review/pool_kappa_report.json` → `docs/REVIEW_POOL_KAPPA_REPORT.md`).
3. When B1–B9 land, §7's table becomes a record of what was built; the file names there are
   the contract the implementing PR is checked against.

## Freshness

Re-read when: the pool is actually dealt (the §3 counts and the n of §5 become concrete), any
of B1–B9 lands, the packets are re-cut, or the submission path is revisited against a measured
intake cost (§6, rejected alternative 3).

_Гасунс_
