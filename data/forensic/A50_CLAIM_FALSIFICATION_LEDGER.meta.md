# Metadoc — A50_CLAIM_FALSIFICATION_LEDGER.md

_Created: 24-09-2026 · Last updated: 24-09-2026_

A document about [`A50_CLAIM_FALSIFICATION_LEDGER.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/A50_CLAIM_FALSIFICATION_LEDGER.md).

## Purpose & audience

The pre-merge falsification pass H5295 asked for: not "is each number computed
correctly?" (that is the H4352 pin discipline) but "does the measurement
identify the mechanism the sentence claims?". Audience: the A50 referee, the
author before submission, and any later paper that wants the same pass —
the ledger format (source sentence · evidence · inferential step · alternative ·
counterexample · provenance · verdict · patch) is the reusable part.

## How it was produced

1. Census: `git log --since=2026-09-01 --name-only` over articles and forensic
   docs; five substantive candidates; A50 selected (only unreviewed
   identification claim; §1 of the ledger gives the table and the PR search).
2. `scripts/forensic/f12_a50_claim_ledger.py` re-derives every descriptive
   figure from the committed TSVs and records their SHA-256; it also builds the
   variant-fold map (named tier from A50 §5.5, ASCII tier by diacritic fold).
3. `scripts/forensic/f12_a50_topology_arms.mjs` re-runs the committed test
   (`scripts/build-citation-canon.mjs`, same seed, same null) on eight matrices:
   committed, two foldings, thin rows dropped, a constructed one-canon matrix,
   two private-spelling variants of it, and the regenerated edge list — plus a
   12-run seed × fraction sweep of the control (`--quick` skips it).
4. Pins: `tests/forensic/test_f12_a50_claim_ledger.py` (hand-derived fixture
   expectations + the committed-report and arms-report figures the prose quotes).
5. Paper repaired in the same PR; an independent read-only logic critic reviewed
   the pre-merge head (three FAIL verdicts, 25 findings: 24 fixed, 1 deferred to
   merge), then a delta pass over the fixes (22 findings, all fixed; the key unification
   I4 asks for is forwarded to H5407) and a confirmation pass on the committed
   head (7 residues, all fixed) — all adjudicated in the ledger's §5 / §5.1 and recorded in the PR thread and the
   handoff's `## Verifier`.

## Maintenance

- Regenerate after any change to `data/citations/ls_citation_*.tsv` (H5407 did so on
  24-09-2026): rerun both scripts, re-derive the committed-report pins by hand, update §P and
  the post-re-freeze status paragraph under the header. Rows C1–C7 keep the H5295-pass
  figures as the falsification record; only the status paragraph, §P and §4 track the data.
- The arms script takes ~15 minutes (8 arms + 12 sweep runs × 1,000 nulls; `--quick` skips the sweep). A perfectly nested
  construction hangs the fixed-fixed null — keep the rank-biased sampler.
- The ASCII fold deliberately does not collapse `ṃ`/`n`; extend `NAMED_VARIANTS`
  for such pairs rather than loosening the fold.

## Related

- [`EVIDENCE_DEPENDENCE_AUDIT.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/EVIDENCE_DEPENDENCE_AUDIT.md) — the sibling pass over A10 (H5073).
- [`data/citations/README.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/README.md) — dataset change log, provenance sidecar.
- Handoffs: H5295 (this pass), H5407 (alias extension + re-freeze at a recorded revision,
  executed 24-09-2026: §P `narrows` → `survives`).

_Гасунс_
