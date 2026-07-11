# Metadoc — MBH_CITATION_RESOLUTION_CENSUS.md

_Created: 11-07-2026 · Last updated: 11-07-2026_

A document about [`MBH_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/MBH_CITATION_RESOLUTION_CENSUS.md).

## Purpose & audience

The Mahābhārata instalment (W1a) of the citation-verification program — a census of how PWG/MW
cite the MBH, a census of Böhtlingk's own correction notes, their verification against the BORI
critical text, and a record of why the fitted-index locus census is blocked. Audience:
lexicography/philology researchers and the program's later waves (W1b Sprüche, W2 Rāmāyaṇa) that
reuse the `f8_mbh_*` engine and the R3 benchmark schema.

## Provenance

Built under [H610](https://github.com/gasyoun/Uprava/blob/main/handoffs/H610-Opus_csl-atlas_mbh_citation_census_11.07.26.md)
by Opus 4.8 (`claude-opus-4-8`), 11-07-2026. Port of the H488 Harivaṃśa method
([`f7_harivamsa_*`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f7_harivamsa_resolve.py)).
Scripts: [`f8_mbh_census.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_census.py),
[`f8_mbh_verify.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_verify.py).

## Key measured facts

- PWG 66,103 MBH `(parvan,verse)` loci (of 67,256 MBH `<ls>` tags); MW 29,178, only 4,320 with roman book.
- 2,466 Böhtlingk correction notes on MBH loci (1,630 high-conf, 752 with an edition cross-ref).
- Retrieval verdicts: 956 confirmed, 422 reading-supported, 1,088 unresolvable (39 % confirmed, ≈ Harivaṃśa's 37.7 %).
- Validation: case 2 (`7,9226` *yenāvibruvatā praśnam*) quote-exact at BORI `07,170.032` → confirmed; case 1 (`7,9283` *abravat→abravīt*) unresolvable → D3 escalation.
- 13 candidate PWG numeric typos (worst `13,73001`).

## Ranked improvement backlog

1. **Obtain a Nilakantha-vulgate e-text** (Manipal Sastri-Vavilla harvest under a D3 ruling, or Calcutta-scan OCR) → unblocks the fitted-index locus census and the fitted-vs-retrieval baseline. — *status: blocked on D3 / OCR; the single biggest unlock.*
2. **Manipal spot-check lane for the `unresolvable` + case-1-type single-word notes** — reverse-engineer the Manipal private API for individual disputed loci (`curl -k`; D3 spot-check, not bulk). — *status: open.*
3. **DCS lemma-evidence attach** — for `reading-supported` notes, cite the DCS lemma at the retrieved BORI locus (an `abravīt→brū` query is native). — *status: open, cheap.*
4. **Tighten `corrected_slp1` auto-extraction** — case 2 mis-grabs a neighbouring lemma; parse the specific "X fehlerhaft für Y" / "Y zu lesen" templates. — *status: open, low priority (quote column is authoritative).*
5. **Extend the notes miner to pw/PWK/MW** — currently PWG-only. — *status: open, W2+.*

## Known limitations / caveats

- **No locus arithmetic** for MBH (§2 of the subject) — verification is reading-evidence only until a vulgate e-text exists. This is the defining difference from the Harivaṃśa census.
- `confirmed` means *a distinctive reading quoted in the note's context is attested in BORI*, not strictly *the correction is provably right*; for the flagship case 2 it is the corrected reading, but the aggregate mixes printed/corrected forms drawn from the same quote window.
- Short two-word pratīkas (~8–10 folded chars) at `quote-exact` are weaker than long phrases; the min-length gate (8) admits some.
- `st.` (= *statt*) retains ~5 % residual "Ind. St." false positives even after case-sensitive matching; all are medium-confidence.

## Related documents

- Precedent: [`HARIVAMSA_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/HARIVAMSA_CITATION_RESOLUTION_CENSUS.md) (+ its meta).
- Program: [`docs/CITATION_VERIFICATION_ROADMAP_2026_2027.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/CITATION_VERIFICATION_ROADMAP_2026_2027.md) (+ its meta).
- Blocker: [`SanskritLexicography/DEAD_ENDS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md).

## Revision history

| Date | Change | By |
|---|---|---|
| 11-07-2026 | Created with the subject census (H610 W1a). | Opus 4.8 (`claude-opus-4-8`) |

_Dr. Mārcis Gasūns_
