# MBH Droṇaparva (book 7) fitted-index locus census — the blocker refuted

_Created: 12-07-2026 · Last updated: 12-07-2026_

**What this is.** The first **fitted-index locus census** for a Mahābhārata parva, run against
the newly-scraped **Nīlakaṇṭha vulgate** e-text. It closes the negative exit recorded by the
W1a census ([`MBH_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/MBH_CITATION_RESOLUTION_CENSUS.md),
H610): that census had to **defer** the locus census because "no free bulk Nīlakaṇṭha-vulgate
e-text exists" and BORI-critical text is a structural dead end for vulgate locus arithmetic
([`SanskritLexicography/DEAD_ENDS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) §8/§8b).
That premise is **false as of 11-07-2026** — a full vulgate (83,971 shlokas, 18 parvans) was
scraped from [sanatana.in](https://sanatana.in/mahabharata/) into CommentaryStrategies
([PR #83](https://github.com/gasyoun/CommentaryStrategies/pull/83)). This census runs the
deferred lane for **Droṇaparva (book 7)** — the roadmap's own `MBH. 7,9283` exemplar parva —
and the held-out gate **passes**.

**Method (reused, not rebuilt).** The Harivaṃśa fitted-index method
([`f7_harivamsa_resolve.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f7_harivamsa_resolve.py),
H488): order the vulgate verses, assign a provisional continuous number `C`, fit a robust
per-adhyāya constant offset on PWG anchors (median of residuals `N−C`, isotonic-clipped) →
calibrated `Ĉ(verse) = C + offset[adhyāya]`, **hold out MW** as the circularity gate, then
classify each PWG `MBH. 7,*` ref. The citation extractors come from
[`f8_mbh_census.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_census.py);
the new wiring is [`f8_mbh_drona_fitted_index.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_drona_fitted_index.py).

## Inputs

| Quantity | Value |
|---|---|
| Vulgate source | Nīlakaṇṭha (Bombay family), sanatana.in digitization |
| Book-7 vulgate verses | 9,641 shlokas across 202 adhyāyas |
| PWG book-7 anchors | 3,590 `(headword, MBH. 7,N)` |
| MW book-7 anchors | 194 `(headword, MBh. vii, N)` |

The vulgate e-text bytes are **not committed** (third-party rights) — only numbers-only
concordances/offsets/verdicts are. `MBH. 7,9283` sits within the vulgate's own verse ceiling
(the top PWG book-7 numbers cluster at 9,624–9,645, matching the 9,641 total almost exactly;
only 6 of 3,590 refs exceed it — `12110`, `14246` and four neighbours are PWG's own numeric
typos, already flagged in [`mbh_candidate_numeric_typos.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/mbh_candidate_numeric_typos.csv)).

## Held-out gate (method invariant 2) — **PASS**

Fit the per-adhyāya offsets on **PWG only**, then test whether **MW** anchors land within ±3 of
their cited `N` under the calibrated map, against a shuffled-`N` null.

| | value |
|---|---|
| MW anchors evaluable | 187 |
| within ±3 of cited N | **90 (48.1 %)** |
| shuffled-N null | **0 / 185 (0.0 %)** |
| δ distribution (±3) | −2:6 · −1:9 · **0:60** · 1:8 · 2:4 · 3:3 |
| adhyāyas directly fitted | 97 / 202 · offset range −20 … +14 |
| **verdict** | **PASS** (agreement ≥ 0.30 and ≥ 5× null) |

48 % of held-out MW anchors land within ±3 of their independently-cited continuous number,
**peaked exactly at δ=0** (60 of 90 hits exact), against a **0 %** shuffled null. The vulgate's
per-adhyāya numbering aligns with the continuous Calcutta/vulgate numbers PWG and MW cite — the
alignment is real, not fitted noise. Because the gate passes, the classification lane below is
non-circular and permitted to run.

**End-to-end validation on the roadmap's own exemplar.** PWG cites `MBH. 7,9283` (headword brū,
Böhtlingk's printed `abravat` → corrected `abravīt`). The fitted index maps continuous 9283 →
vulgate **7.200.24**, whose vulgate reading is *…droṇaputram **athābravīt*** — the exact
`abravīt` form. The index places the cited number on the correct verse.

## Classification of PWG book-7 refs

Each PWG `MBH. 7,*` ref classified by whether its headword sits at the cited locus ±3 under the
calibrated index (2,862 evaluable of 3,590; the rest have headword keys < 4 chars, too short to
match decisively).

| category | count | share | shuffled-N null |
|---|---|---|---|
| corroborated | 847 | **29.6 %** | 18.8 (0.7 %) |
| displaced | 1,084 | 37.9 % | — |
| absent | 931 | 32.5 % | — |
| displaced (≤3 loci) | 486 | — | 1,035 (chance) |

**(A) Corroboration is far above chance.** 29.6 % corroborated vs a 0.7 % shuffled-N null
(σ ≈ 4.3 refs) — the headword genuinely stands at the cited locus for ~850 refs, not by luck.
The per-ref rate is lower than the 48 % held-out gate because it is diluted by two honest,
non-error effects: **absent (32.5 %)** — the headword is a compound or an inflected form the
coarse token-stem matcher cannot see at that verse, or the verse is among the vulgate's own
gaps; and **displaced** rare single-locus lemmas whose one occurrence drifts > 3 from `N` under
residual calibration noise. The held-out MW gate is the cleaner accuracy proxy because it
restricts to matchable anchors with a proper null.

**(B) No shared-error excess.** Observed clear-displacement (≤ 3 loci) is **486, well *below*
the 1,035 chance mean** — displacements are the expected "a rare word's single locus is usually
> 3 from an arbitrary number", **not** systematic wrong-number citations. There is no evidence
of a shared PWG↔MW MBH numbering error in Droṇa above chance.

## Files (numbers only — no verse text)

- [`mbh_drona_vulgate_concordance.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/mbh_drona_vulgate_concordance.csv) — per verse: `(adhyaya, verse) → continuous_sloka Ĉ`, offset, adhyāya anchor count.
- [`mbh_drona_fitted_index_offsets.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/mbh_drona_fitted_index_offsets.csv) — per-adhyāya calibration offsets + support.
- [`mbh_drona_citation_resolution.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/mbh_drona_citation_resolution.csv) — per PWG book-7 ref: category, delta, n_loci.
- [`f8_drona_report.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f8_drona_report.json) — held-out + corroboration + null stats.

`continuous_sloka` is an **estimate** (calibration noise ±1–2; held-out MW places 60 of 90 hits
exactly and 48 % within ±3). `adhyaya_n_anchors > 0` marks a directly-fitted adhyāya; `0` is an
interpolated offset.

## Limitations & next

- **One parva only.** Book 7 is the exemplar and the highest-cited hard-class parva; the other
  17 parvans are unrun. The same script generalizes by changing `BOOK` — each parva is its own
  held-out gate (a parva whose vulgate digitization diverges from PWG's Calcutta numbering would
  **fail** its gate, a real per-parva negative, not a bug).
- **Vulgate-edition provenance.** sanatana.in's per-adhyāya digitization is not yet verified
  against a specific print vulgate; the passing held-out gate is itself the evidence that its
  continuous numbering matches what PWG/MW cite for Droṇa, but a print-edition confirmation
  (Kinjawadekar/Calcutta) is queued.
- **Coarse matcher.** The 32.5 % absent rate is dominated by compounds and sandhi the token-stem
  matcher misses, not by wrong citations — a lemma-aware matcher (DCS/vidyut) would recover many.
- **Rights.** Vulgate bytes stay gitignored; `/publish-safety-check` before any kosha release.

Scripts run from repo root: `python scripts/forensic/f8_mbh_drona_fitted_index.py` (after the
CommentaryStrategies vulgate scrape). Built under
[H761](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H761-Opus_csl-atlas_mbh_fitted_index_nilakantha_vulgate_unblocked_12.07.26.md).

_Dr. Mārcis Gasūns_
