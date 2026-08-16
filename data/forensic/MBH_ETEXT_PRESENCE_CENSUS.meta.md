# Metadoc — MBH_ETEXT_PRESENCE_CENSUS.md

_Created: 16-08-2026 · Last updated: 16-08-2026_

Companion to
[`MBH_ETEXT_PRESENCE_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/MBH_ETEXT_PRESENCE_CENSUS.md).
Everything a fresh session would otherwise rediscover by trial and error.

## Purpose

Answer, with evidence a reader can click, whether a Mahābhārata citation's verse stands in the
Nīlakaṇṭha vulgate, in the BORI critical edition, in both, or was never checked — and give the
citation an e-text link beside its Cologne scan link. Sibling of
[`MBH_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/MBH_CITATION_RESOLUTION_CENSUS.md),
which owns the numbering; this doc owns the text.

## Provenance

Written 16-08-2026 by Opus 5 (`claude-opus-5`) under
[H2845](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2845-Opus_csl-atlas_citation-etext-layer-mbh-nilakantha-critical-presence_15.08.26.md),
covering point P2 of the MG crosswalk-review umbrella
[H2843](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2843-Opus_Uprava_mg-crosswalk-review-8-point-vote-contour-umbrella_15.08.26.md).

## Pipeline — run in this order, from the repo root

| Step | Script | Produces |
|---|---|---|
| 1 | [`f8_mbh_witnesses.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_witnesses.py) | the two **gitignored** text caches |
| 2 | [`f8_mbh_presence.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_presence.py) | verse-level + citation-level presence CSVs, spot check, report |
| 3 | [`f8_mbh_specimen.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_specimen.py) | the `MBH. 12,8081` three-lane answer |
| 4 | [`f8_mbh_quote_lane.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_quote_lane.py) | the fitted-index accuracy measurement |

Steps 2–4 each take a few minutes; step 1 is seconds. Only step 4 needs
[`csl-orig`](https://github.com/sanskrit-lexicon/csl-orig) cloned next to this repo.

## Things that will bite you

1. **The text is not in this repo and must never be.** Both witnesses are rights-gated and
   gitignored. If `_mbh_vulgate_verses.jsonl` or `_mbh_bori_halfverse.jsonl` is missing, run
   step 1 — do not "fix" a script to work without them, and do not commit them.
2. **The witnesses live on a local-only branch of a sibling repo**
   (`CommentaryStrategies`, `mahabharata-nilakantha-local-only-do-not-push`). It is never
   pushed. If that clone is lost, the vulgate is **not currently re-fetchable**: the sanatana.in
   endpoint the old harvester uses now returns an empty body.
3. **BORI is ISO-15919, not IAST.** `ṁ` does not survive IAST→SLP1 and silently poisons every
   anusvāra-bearing match. This produced a false "absent from the critical edition" during the
   build; the normaliser in step 1 is what fixes it. Any new consumer of that text must
   normalise too.
4. **Never number-align the two editions.** The vulgate carries what the critical edition
   relegated to its apparatus; content alignment is the only valid join.
5. **The citation-level table is conditional, the verse-level table is not.** Quoting the
   `present/absent` citation count as "PWG cites what BORI rejects" without §6's caveat
   overstates it by roughly a factor of two.

## Ranked improvement backlog

1. Land the etext branch in the shared renderer
   [`ls_links.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_links.py)
   — until then only this repo's data knows the etext address.
2. Join the 12,541 quote-lane pairs onto `mbh_citation_presence.csv` so a quoted citation gets
   its exact address instead of a fitted guess, and its verdict becomes unconditional.
3. Mine MW's quoted citations the same way PWG's were.
4. Rewrite `f8_mbh_harvest.py` for the rebuilt sanatana.in before the local witness is needed.
5. Handle the 3,595 addresses unreachable from a calibrated number alone (repeated `calibrated_N`).

## Limitations

- Coverage thresholds (0.85 / 0.60) are argued, not tuned against a gold set — no adjudicated
  vulgate↔critical alignment exists to tune against.
- `MAX_POSTING = 40` trades a little recall on heavily formulaic half-verses for tractability.
- Half-verses under 16 folded characters are deliberately `unchecked`, never `absent`.

## Related

[`MBH_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/MBH_CITATION_RESOLUTION_CENSUS.md)
· [`MBH_DRONA_FITTED_INDEX_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/MBH_DRONA_FITTED_INDEX_CENSUS.md)
· [`docs/CITATION_VERIFICATION_ROADMAP_2026_2027.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/CITATION_VERIFICATION_ROADMAP_2026_2027.md)
· [`BORI_CRITICAL_SOURCE.md`](https://github.com/gasyoun/CommentaryStrategies/blob/main/mahabharata-nilakantha/BORI_CRITICAL_SOURCE.md)
· [`NILAKANTHA_VULGATE_CENSUS.md`](https://github.com/gasyoun/CommentaryStrategies/blob/main/mahabharata-nilakantha/NILAKANTHA_VULGATE_CENSUS.md)

## Revision history

| Date | Change |
|---|---|
| 16-08-2026 | Created with the document (H2845, Opus 5 `claude-opus-5`). |

_Dr. Mārcis Gasūns_
