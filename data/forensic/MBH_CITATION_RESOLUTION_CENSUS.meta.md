# Metadoc — MBH_CITATION_RESOLUTION_CENSUS.md

_Created: 11-07-2026 · Last updated: 11-07-2026_

A document about [`MBH_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/MBH_CITATION_RESOLUTION_CENSUS.md).

## Purpose & audience

The Mahābhārata instalment (W1a) of the citation-verification program — a census of how PWG/MW
cite the MBH, a census of Böhtlingk's own correction notes, the **fitted per-parvan locus index
against the Nīlakaṇṭha vulgate (all 18 parvans, held-out-validated)**, and per-note verification.
Audience: lexicography/philology researchers and the program's later waves (W1b Sprüche, W2
Rāmāyaṇa) that reuse the `f8_mbh_*` engine and the R3 benchmark schema.

## Provenance

Built under [H610](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H610-Opus_csl-atlas_mbh_citation_census_11.07.26.md)
by Opus 4.8 (`claude-opus-4-8`), 11-07-2026. Port of the H488 Harivaṃśa method
([`f7_harivamsa_*`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f7_harivamsa_resolve.py)).
Scripts: [`f8_mbh_census.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_census.py),
[`f8_mbh_harvest.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_harvest.py),
[`f8_mbh_resolve.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_resolve.py),
[`f8_mbh_verify.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_verify.py).
Book-7 companion: [`MBH_DRONA_FITTED_INDEX_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/MBH_DRONA_FITTED_INDEX_CENSUS.md) (H761).

## Key measured facts

- PWG 66,103 MBH `(parvan,verse)` loci (of 67,256 MBH `<ls>` tags); MW 29,178, only 4,320 with roman book.
- 2,466 Böhtlingk correction notes on MBH loci (1,630 high-conf, 752 with an edition cross-ref).
- **Nīlakaṇṭha vulgate harvested from sanatana.in: 83,971 verses, all 18 parvans.** Per-parvan index fitted, **held-out on MW: 55.2 % (2,234/4,048) vs 1.4 % null, ≈ 40×, PASS** — every parvan passes; book 7 = 90/187, reproducing H761's Droṇa census exactly.
- Note-locus resolution vs the vulgate: 409 corroborated / 787 displaced / 1,270 absent.
- BORI retrieval cross-check: 956 confirmed, 422 reading-supported, 1,088 unresolvable (39 %).
- Validation: case 1 (`7,9283` *abravat→abravīt*) **resolved by the vulgate index** — Droṇa adh 200 reads *abravīt* ×7; case 2 (`7,9226` *yenāvibruvatā praśnam*) quote-exact at BORI `07,170.032`.
- 13 candidate PWG numeric typos (worst `13,73001`).

## Ranked improvement backlog

1. ~~Obtain a Nilakantha-vulgate e-text.~~ **DONE** — sanatana.in harvested (`f8_mbh_harvest.py`); the "no free vulgate" premise was wrong. All-18-parvan locus census ran, held-out gate passed.
2. **Full corroborated/displaced/absent census over ALL 66k PWG + 29k MW citations** (not just the 2,466 notes) — the resolver classifies the notes pool + validates on MW anchors; extend to the whole inventory for the headline census. — *status: open, cheap.*
3. **DCS lemma-evidence attach** — for `displaced`/`absent` loci, cite the DCS lemma at the parallel. — *status: open, cheap.*
4. **Cross-edition disagreement lane** — where the vulgate places a citation but BORI's reading differs, flag as an edition-variant candidate (the A10 "shared apparatus" upgrade). — *status: open.*
5. **Extend the notes miner + resolver to pw/PWK/MW** — currently PWG-only. — *status: open, W2+.*

## Known limitations / caveats

- The per-parvan index calibrates the first ~45 Ādiparvan verses to a small **negative** `N` (the vulgate's invocation/anukramaṇikā precedes Calcutta's śloka 1) — an edge artifact, excluded from verdicts.
- `corroborated` (vulgate lane) = headword at the cited śloka ±3; `displaced`/`absent` mix true offsets with unmatchable compounds. Śānti is the weakest fit (held-out 0.28, still 28× null); the tiny end-parvans have small n.
- BORI-lane `confirmed` means *a distinctive reading quoted in the note is attested in BORI*, not strictly *the correction is provably right*.
- `st.` (= *statt*) retains ~5 % residual "Ind. St." false positives even after case-sensitive matching; all medium-confidence.

## Related documents

- Precedent: [`HARIVAMSA_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/HARIVAMSA_CITATION_RESOLUTION_CENSUS.md) (+ its meta).
- Program: [`docs/CITATION_VERIFICATION_ROADMAP_2026_2027.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/CITATION_VERIFICATION_ROADMAP_2026_2027.md) (+ its meta).
- Blocker: [`SanskritLexicography/DEAD_ENDS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md).

## Revision history

| Date | Change | By |
|---|---|---|
| 11-07-2026 | Created with the subject census (H610 W1a). | Opus 4.8 (`claude-opus-4-8`) |
| 12-07-2026 | Locus census unblocked & completed for **all 18 parvans** — Nīlakaṇṭha vulgate harvested from sanatana.in (83,971 verses), per-parvan index fitted + held-out (55.2 % vs 1.4 %), case `7,9283` resolved. Generalizes H761's book-7 census; "blocked" framing + DEAD_ENDS §8b retracted. | Opus 4.8 (`claude-opus-4-8`) |

_Dr. Mārcis Gasūns_
