# Dictionary Comparison Plan

Date: 2026-05-29

Status: planning document for Phase 2 (Comparative Dictionary Lab). This is the second implementation direction, after MW Quantitative Depth. It must not start in the same pass as Phase 1 unless explicitly requested (`docs/READER_DEVELOPER_CRITIQUE.md`).

This plan turns Track 2 of `ARCHITECTURE.md` into a bounded, deterministic implementation slice.

## Goal

Compare MW, AP, PWG, PWK, WIL, VCP, and SKD so that a user can ask, for any lemma or feature, **which dictionaries cover it, where they agree, and where they conflict** — always traceable to source records.

```text
question -> coverage / overlap / conflict view -> aligned entries -> source link -> review status
```

## Prerequisites

- **MW Quantitative Depth (Phase 1) is stable.** The MW parser and classifiers are the reference implementation other dictionary parsers imitate.
- **Coverage layer exists.** `npm run build-coverage` already scans every local `../csl-orig/v02/<code>/<code>.txt` and writes `dictionary-coverage.json` (43 dictionaries, ~1.5M entries; see `docs/ALL_DICTIONARY_COVERAGE.md`). That layer answers "how big / what fit band" per dictionary and is the entry point for comparison.
- **Do not build `LexemeHub` yet.** Comparison must produce real conflicts *before* a universal alignment object is justified (`ARCHITECTURE.md`, AUC-08). The first pass aligns pairwise and by normalized headword only.

## Comparison Levels

From `ARCHITECTURE.md`, in increasing difficulty. Implement top-down; stop where evidence quality drops.

| Level | Question | Difficulty |
|---|---|---|
| lemma coverage | Which dictionaries contain this lemma? | low — needs only normalized headwords |
| homonym split | Does one dictionary split what another merges? | medium — needs record IDs and homonym handling |
| grammar profile | Do POS, gender, or root status disagree? | medium — needs per-dictionary grammar parsing |
| sense inventory | Which dictionary is deeper or broader? | high — needs sense segmentation |
| citation apparatus | Which sources are cited, and where? | medium — `<ls>` for tagged dicts, prose `iti` for VCP/SKD |
| domain tagging | Which technical domains are recognized? | medium-high |
| lexical family | Which derivatives and compounds are covered? | high — reuses MW depth heuristics |

## Alignment Strategy

The hard problem is deciding when two records are "the same lemma." Keep the first pass conservative and confidence-labeled.

1. **Normalize headwords** to a shared key (transliteration → canonical form). Reuse the normalization used for reader lookup.
2. **Group by normalized key** across dictionaries — this gives the coverage matrix directly.
3. **Score alignment confidence** per match: exact normalized match = high; match after stripping accents/homonym index = medium; fuzzy/near match = low → review queue.
4. **Never silently merge homonyms.** If one dictionary has `agni 1` / `agni 2` and another has a single `agni`, that is a *finding* (homonym split), not noise to flatten.
5. **Carry evidence labels.** Coverage is `observed`; grammar conflicts are `derived`; family overlaps are often `inferred`. See [`docs/EVIDENCE_LABELS.md`](EVIDENCE_LABELS.md).

Tagged dictionaries (MW, AP, PWG, PWK, WIL) and prose `iti` dictionaries (VCP, SKD) need different parsers. Comparison must handle the prose lexica as a distinct genre, not force them into the MW tag model (`docs/ALL_DICTIONARY_COVERAGE.md`, fit bands). For VCP/SKD, citation comparison falls back to inline `iti` detection.

## Suggested Pipeline

Mirror the Phase 1 layout under `scripts/lib/` and `scripts/`:

- `scripts/lib/dict-normalize.mjs` — shared headword normalization.
- `scripts/lib/dict-parsers/<code>.mjs` — one parser per dictionary, returning the common `DictionaryEntry` shape from `ARCHITECTURE.md`.
- `scripts/lib/dict-align.mjs` — normalized-key grouping + confidence scoring.
- `scripts/build-dictionary-comparison.mjs` — emits the outputs below.
- `scripts/validate-dictionary-comparison.mjs` — checks counts and source links.

Package scripts: `build-dict-comparison`, `validate-dict-comparison`.

The existing `src/data/cross-dict.json` (keys: `blocks`, `dicts`) is the seed of this layer and should be superseded or extended by the structured outputs, not duplicated.

## Data Outputs

Generate compact JSON under `src/data/dicts/`:

- `coverage-matrix.json` — dictionary × normalized-lemma presence.
- `pairwise-overlap.json` — MW↔AP, MW↔PWG, PWG↔PWK, etc. (UC-CD-02).
- `all-intersection.json` — lemmas present in every target dictionary (UC-CD-03).
- `pos-disagreement.json` — POS/gender conflicts with snippets (UC-CD-04 / UC-CD-05).
- `sense-depth.json` — sense and gloss-depth ranking with caveats (UC-CD-06).
- `citation-apparatus.json` — citation density / source overlap (UC-CD-07).
- `dictionary-unique.json` — per-dictionary unique vocabulary (UC-LX-13).
- `alignment-confidence.json` — confidence distribution and the review queue (UC-CD-09).
- `dictionary-comparison-validation.json` — validation report.

Each file carries the standard envelope: `schemaVersion`, `generatedAt`, `sourcePath`, `recordCount`, `assumptions`, `warnings`, and per-finding `evidenceLevel`.

## Observable Pages

Following the Visualization Series in `ARCHITECTURE.md` and UC-VIZ-02/03:

- `src/tools/dictionary-coverage-matrix.md` — coverage matrix.
- `src/tools/dictionary-overlap.md` — pairwise + UpSet-style overlap.
- `src/tools/dictionary-conflicts.md` — POS/gender disagreement tables with source links.
- `src/tools/dictionary-dossier.md` — per-lemma side-by-side view (UC-RD-03, the reader-facing payoff).

Every table keeps small examples with source links so any number can be debugged back to a record (UC-DEV-14).

## Review Queues

Comparison is the largest producer of review work. Wire these into the shared review-report format ([`docs/REVIEW_REPORTS.md`](REVIEW_REPORTS.md)):

- low-confidence alignment queue (UC-RV-01);
- POS/gender conflict queue (UC-RV-02);
- manual alignment correction (UC-LX-15 / UC-RV-08).

Do not scatter one-off report shapes; reuse `scripts/select-review-cases.mjs` precedent.

## Acceptance Criteria

- One command regenerates all comparison JSON deterministically.
- Validation passes and Observable build passes.
- Coverage matrix counts reconcile with `dictionary-coverage.json`.
- Every conflict and overlap finding includes source-linked examples.
- Homonym splits are reported, never silently merged.
- Low-confidence alignments land in a review queue, not in published tables as if certain.
- No runtime LLM classification.

## Non-Goals (Phase 2)

- No `LexemeHub` universal object yet (AUC-08).
- No corpus comparison — that is Phase 3 (`docs/DCS_CORPUS_INGESTION_PLAN.md`).
- No exact dating from citations (AUC-01).
- No flattening of German or Sanskrit-Sanskrit evidence into English-only summaries (AUC-09).

## Related Documents

- `ARCHITECTURE.md` — Track 2, common data model, Comparative Dictionary Series.
- `docs/ALL_DICTIONARY_COVERAGE.md` — the coverage/size/fit layer this builds on.
- [`docs/EVIDENCE_LABELS.md`](EVIDENCE_LABELS.md) and [`docs/REVIEW_REPORTS.md`](REVIEW_REPORTS.md).
- `docs/USE_CASES.md` — UC-CD-01 through UC-CD-10, UC-LX-09 through UC-LX-15.
