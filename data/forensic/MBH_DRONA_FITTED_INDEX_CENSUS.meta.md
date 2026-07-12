# Metadoc — MBH_DRONA_FITTED_INDEX_CENSUS.md

_Created: 12-07-2026 · Last updated: 12-07-2026_

A document about [`MBH_DRONA_FITTED_INDEX_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/MBH_DRONA_FITTED_INDEX_CENSUS.md).

## Purpose & audience

The first fitted-index locus census for a Mahābhārata parva (Droṇa, book 7), run against the
Nīlakaṇṭha vulgate scraped 11-07-2026 — closing the negative exit the W1a census
([`MBH_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/MBH_CITATION_RESOLUTION_CENSUS.md),
H610) recorded. Audience: lexicography/philology researchers and the citation-verification
program's later waves (W2 Rāmāyaṇa + the hard class) that reuse the fitted-index engine and the
held-out gate.

## Provenance

Built under [H761](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H761-Opus_csl-atlas_mbh_fitted_index_nilakantha_vulgate_unblocked_12.07.26.md)
by Opus 4.8 (`claude-opus-4-8`), 12-07-2026. Reuses the H488 Harivaṃśa fitted-index method
([`f7_harivamsa_resolve.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f7_harivamsa_resolve.py):
`fit_offsets`, `held_out`, `classify`) and the H610 MBH citation extractors
([`f8_mbh_census.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_census.py):
`pwg_citations`, `mw_citations`) — no method rebuild. New wiring:
[`f8_mbh_drona_fitted_index.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_drona_fitted_index.py).
Vulgate input: `CommentaryStrategies/mahabharata-nilakantha/nilakantha_vulgate_full.jsonl`
(gitignored, [PR #83](https://github.com/gasyoun/CommentaryStrategies/pull/83)).

## Key measured facts

- Book-7 vulgate: 9,641 shlokas / 202 adhyāyas. PWG anchors 3,590; MW anchors 194.
- **Held-out gate PASSES:** MW agreement 48.1 % (90/187) within ±3, δ peaked at 0 (60 exact),
  shuffled null 0.0 % (0/185). Offsets −20…+14, 97/202 adhyāyas directly fitted.
- Classification (2,862 evaluable): corroborated 847 (29.6 % vs 0.7 % null), displaced 1,084,
  absent 931. Clear-displacement 486 **below** the 1,035 chance mean → no shared-error excess.
- Exemplar `MBH. 7,9283` → vulgate 7.200.24 (`…droṇaputram athābravīt`) — the fitted index
  places the cited number on the correct verse end-to-end.

## Improvement backlog (ranked)

1. **Run the other 17 parvans.** Change `BOOK` and re-run; each parva is its own held-out gate.
   A failing gate is a publishable per-parva negative (vulgate digitization ≠ PWG's Calcutta
   numbering for that parva), not a bug. Highest value: the other high-mass parvans (1, 3, 12).
2. **Lemma-aware matcher.** The 32.5 % absent rate is dominated by compounds/sandhi the coarse
   token-stem matcher misses; a DCS/vidyut lemma layer would recover many corroborations and is
   the single biggest accuracy lever.
3. **Print-edition provenance check.** Verify sanatana.in's per-adhyāya digitization against a
   named print vulgate (Kinjawadekar/Calcutta) to firm up the numbering-family claim beyond the
   passing gate.
4. **Retrieval × fitted-index cross-check.** For book-7 refs, compare this fitted-index verdict
   against f8_mbh_verify's BORI character-fuzzy retrieval verdict — the roadmap R1 "free baseline
   comparison (fitted-index-only vs retrieval-only vs hybrid)" is now runnable for Droṇa.

## Limitations

- One parva; coarse (non-lemma-aware) matcher; vulgate provenance not yet print-verified.
- `continuous_sloka` is an estimate (±1–2 calibration noise). Numbers-only outputs; no verse text.

## Related

- [`MBH_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/MBH_CITATION_RESOLUTION_CENSUS.md)
  (W1a, the deferred-blocker census this unblocks) + its metadoc.
- [`HARIVAMSA_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/HARIVAMSA_CITATION_RESOLUTION_CENSUS.md)
  (H488, the method template).
- [`CITATION_VERIFICATION_ROADMAP_2026_2027.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/CITATION_VERIFICATION_ROADMAP_2026_2027.md) §4 W1a.

## Revision history

| Date | Change |
|---|---|
| 12-07-2026 | Created (H761, Opus 4.8 `claude-opus-4-8`) — first parva (Droṇa) fitted-index census; held-out gate PASS. |

_Dr. Mārcis Gasūns_
