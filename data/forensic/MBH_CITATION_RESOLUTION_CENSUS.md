# Mahābhārata citation resolution census — PWG/MW loci against the Nīlakaṇṭha vulgate (all 18 parvans)

_Created: 11-07-2026 · Last updated: 12-07-2026_

**What this is.** The Mahābhārata port of the executed Harivaṃśa census
([`HARIVAMSA_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/HARIVAMSA_CITATION_RESOLUTION_CENSUS.md),
H488) — the largest citation mass in both Petersburg dictionaries and Monier-Williams. It
delivers:

1. a full **citation-form census** of how PWG and MW address the MBH (P0);
2. a context-aware **census of Böhtlingk's own correction notes** on MBH loci — the
   pilot lane the [citation-verification roadmap](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/CITATION_VERIFICATION_ROADMAP_2026_2027.md)
   §4 W1a prescribes (P1);
3. a **fitted per-parvan continuous index against the Nīlakaṇṭha vulgate for all 18 parvans**
   (harvested from sanatana.in), **held-out-validated on MW and PASSED** — the locus census (P2/P3);
4. per-note **verification** — vulgate locus resolution + a deterministic character-fuzzy
   **quote-retrieval lane** against BORI (roadmap R1/R3, P4/P4b).

> **Correction.** An earlier draft concluded the fitted-index locus census was *blocked* ("no free
> bulk Nilakantha-vulgate e-text exists"). **That was wrong.**
> [sanatana.in/mahabharata](https://sanatana.in/mahabharata) serves the complete Nīlakaṇṭha
> (Bhāvadīpa) vulgate — the edition family PWG/MW cite. The book-7 refutation shipped first as
> [`MBH_DRONA_FITTED_INDEX_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/MBH_DRONA_FITTED_INDEX_CENSUS.md)
> (H761); this doc generalizes it to **all 18 parvans** (83,971 verses, pooled held-out MW
> **0.552 vs 0.014 null, ≈ 40×**). The [DEAD_ENDS §8b](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md)
> entry is retracted accordingly.

Program context: [`docs/CITATION_VERIFICATION_ROADMAP_2026_2027.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/CITATION_VERIFICATION_ROADMAP_2026_2027.md)
§2 (method invariants), §5 (cascade). Executable follow-up:
[H610](https://github.com/gasyoun/Uprava/blob/main/handoffs/H610-Opus_csl-atlas_mbh_citation_census_11.07.26.md).

Program context: [`docs/CITATION_VERIFICATION_ROADMAP_2026_2027.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/CITATION_VERIFICATION_ROADMAP_2026_2027.md)
§2 (method invariants), §5 (cascade). Executable follow-up:
[H610](https://github.com/gasyoun/Uprava/blob/main/handoffs/H610-Opus_csl-atlas_mbh_citation_census_11.07.26.md).

## 1. Citation-form census (P0)

Measured over [`csl-orig/v02/pwg/pwg.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwg/pwg.txt)
and [`csl-orig/v02/mw/mw.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw.txt)
by [`scripts/forensic/f8_mbh_census.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_census.py).

| Measure | PWG | MW |
|---|--:|--:|
| MBH-bearing `<ls>` tags | 67,256 | — |
| **Extractable `(parvan, verse)` loci** | **66,103** | **29,178** |
| — with roman/arabic book **and** verse | 66,103 | 4,320 |
| — book-only / bare siglum, no verse | 1,153 (bare) | 24,858 |

**Two grammars, one schema.** PWG cites `MBH. <arabic-book>,<verse>` (e.g. `MBH. 7,9283`) — an
arabic parvan number and a **per-parvan continuous śloka number** — with abbreviated
continuation forms (`<ls n="MBH. 3,">12470</ls>`, `<ls n="MBH.">4,321</ls>`) that the plain
`<ls>` regex misses; the extractor threads the last-seen book so a bare continuation inherits
it. MW cites `MBh. <roman-book>, <verse>` (`MBh. iii, 14189`), but only **4,320 of 29,178**
(14.8 %) carry the roman book — the majority (23,900) are a bare `MBh.` siglum with no
address, censused honestly here rather than silently dropped. The MW total matches the
roadmap's independent `lsextract` figure of 29,181 to within 3; PWG's 66,103 extracted loci
(98.3 % of the 67,256 MBH `<ls>` tags) exceed `lsextract`'s 55,834 because this pass expands
every `n="MBH…"` continuation into its own `(book,verse)` locus.

Per-parvan distribution (PWG; full table
[`mbh_parvan_distribution.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/mbh_parvan_distribution.csv)),
median cited verse — **not** the max, which carries PWG's own typos (see §5):

| # | Parvan | PWG loci | median verse | # | Parvan | PWG loci | median verse |
|--:|---|--:|--:|--:|---|--:|--:|
| 1 | Ādi | 11,831 | 4,015 | 10 | Sauptika | 278 | 344 |
| 2 | Sabhā | 3,724 | 1,146 | 11 | Strī | 248 | 313 |
| 3 | Vana/Āraṇyaka | 15,093 | 9,990 | 12 | Śānti | 5,823 | 6,326 |
| 4 | Virāṭa | 3,260 | 830 | 13 | Anuśāsana | 7,831 | 3,094 |
| 5 | Udyoga | 5,272 | 3,827 | 14 | Āśvamedhika | 2,608 | 1,253 |
| 6 | Bhīṣma | 2,523 | 2,253 | 15 | Āśramavāsika | 655 | 516 |
| 7 | Droṇa | 3,590 | 3,244 | 16 | Mausala | 260 | 120 |
| 8 | Karṇa | 1,585 | 2,069 | 17 | Mahāprasthānika | 51 | 66 |
| 9 | Śalya | 1,347 | 2,558 | 18 | Svargārohaṇa | 124 | 112 |

The Vana- and Ādi-parvans dominate (15,093 + 11,831 = 41 % of PWG's MBH loci). Böhtlingk's
Calcutta numbering runs high within a parvan — real Vana-parvan citations reach `MBH. 3,17472`
— confirming the vulgate's per-parvan continuous count, larger than the BORI critical text.

## 2. The Nīlakaṇṭha vulgate and the fitted per-parvan index (P2/P3)

PWG/MW cite the **Calcutta/Bombay Nīlakaṇṭha vulgate** by per-parvan continuous śloka number.
That text is freely available — [sanatana.in/mahabharata](https://sanatana.in/mahabharata) serves
the complete Nīlakaṇṭha (Bhāvadīpa) mūla.
[`f8_mbh_harvest.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_harvest.py)
harvested it — **83,971 verses, all 18 parvans** — via the site's `listing/getParvaByPage` JSON
endpoint; each verse's `<article id="Ppp_Uuu_Aaaa">` carries its parva/adhyāya directly, transcoded
Devanagari→SLP1 with the canonical `indic_transliteration` library. (Bytes rights-gitignored; only
measurements committed. The same source was independently harvested for the book-7 census
[`MBH_DRONA_FITTED_INDEX_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/MBH_DRONA_FITTED_INDEX_CENSUS.md)
(H761) — the two agree exactly on book 7, 9,641 verses.)

[`f8_mbh_resolve.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_resolve.py)
fits the f7 continuous index **per parvan** (provisional `C` = running verse count, then a robust
per-adhyāya offset fitted on PWG anchors), then **holds out MW** as the circularity gate.

**Held-out gate — PASSED, pooled and per-parvan:**

| Held-out MW check (pooled, 18 parvans) | Value |
|---|--:|
| MW anchors with headword within ±3 of cited `N` | **2,234 / 4,048 = 55.2 %** |
| Shuffled-N null | 1.4 % |
| Enrichment | **≈ 40×** |

Every parvan passes individually — per-parvan agreement 0.20–0.80, each ≥ 10× its own ~0.00–0.03
null (Sabhā 0.80, Śalya/Āśvamedhika 0.76, Anuśāsana 0.69; weakest Śānti 0.28 = 28× and the tiny
Svargārohaṇa 0.20 on n=5). Book 7 (Droṇa) scores **90/187 = 0.48**, reproducing H761's independent
figure exactly. The index is trustworthy — the locus census is real, not the
[DEAD_ENDS §8](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) artifact
that fitting against the *critical* recension would be. Per-parvan vulgate ceilings (verse counts)
and full offsets:
[`mbh_continuous_index_offsets.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/mbh_continuous_index_offsets.csv);
the concordance ([`mbh_vulgate_concordance.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/mbh_vulgate_concordance.csv),
83,971 rows, `parvan·adhyāya·shloka → continuous N`, numbers only). Caveat: the first ~45 Ādi
verses calibrate to a small negative `N` (the vulgate's invocation/anukramaṇikā precedes Calcutta's
śloka 1) — an edge artifact, excluded from verdicts.

**Validation case `MBH. 7,9283` resolved.** Böhtlingk: the Calcutta print reads *abravat*,
"fehlerhaft für *abravīt*", per the Bombay edition. The calibrated locus `N ≈ 9283` lands at
Droṇaparvan **adhyāya 200** (`droṇaputram atha **abravīt**`; `rājānam idam **abravīt**`) — the
vulgate reads **abravīt ×7, abravat ×0** there. The vulgate/Bombay tradition confirms *abravīt*;
the erroneous *abravat* was the Calcutta *print's* alone, so Böhtlingk's correction stands. This
is the exact case that was *unresolvable* against BORI (§4).

## 3. Böhtlingk correction-notes census (P1)

Böhtlingk frequently flags a printing or transmission error at an MBH locus in his own words.
[`f8_mbh_census.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_census.py)
mines these **context-aware** — each German erratum marker is bound to the MBH `<ls>` it
**follows** (Böhtlingk's notes trail their citation), capturing the printed vs corrected form
from the surrounding `{#…#}` braces and any `ed. Bomb.`/`ed. Calc.` cross-reference. Output:
[`mbh_correction_notes.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/mbh_correction_notes.csv).

**2,466 correction notes** on MBH loci, of which **1,630 high-confidence** and **752 carry an
explicit edition cross-reference** (453 high-conf + `ed. Bomb.`):

| Marker | Count | Conf. | Marker | Count | Conf. |
|---|--:|:--|---|--:|:--|
| `zu lesen` | 787 | high | `lies` | 172 | high |
| `fehlerhaft` | 605 | high | `statt` | 60 | med |
| `st.` (= statt) | 579 | med | `falsch` | 38 | med |
| `fälschlich` | 153 | med | `zu schreiben` | 37 | high |
| `Druckfehler` | 29 | high | `unrichtig` | 6 | med |

Marker matching is **case-sensitive** on purpose: a case-insensitive `st.` matched "Ind.
**St.**" (Indische Studien) 696/835 times — Böhtlingk's abbreviation for *statt* is lowercase,
the journal is `St.`. The auto-extracted `printed_slp1`/`corrected_slp1` columns are
best-effort (the `quote` column is authoritative — cf. validation case 2 below, where the
corrected form column mis-grabs a neighbouring lemma while the quote preserves the truth).

## 4. Verification: vulgate locus-resolution + BORI character-fuzzy quote-retrieval (P4/P4b)

Two complementary lanes:

**(a) Vulgate locus-resolution** (§2's fitted index). Each note's headword is located in the
Nīlakaṇṭha vulgate and classified against the cited `N`: `corroborated` (headword at `N ± 3`) /
`displaced` / `absent`. Over the 2,466 notes
([`mbh_citation_resolution.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/mbh_citation_resolution.csv)):
**409 corroborated · 787 displaced · 1,270 absent** — 409 notes whose flagged headword sits at
the cited vulgate śloka ± 3.

**(b) BORI reading-evidence retrieval** (roadmap R1), a locus-free cross-check:
[`f8_mbh_verify.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_verify.py)
folds the local GRETIL BORI text (72,771 verses) to a length/retroflex/sibilant-normalized SLP1
key and searches each note's quoted pratīka across the **whole corpus, independent of the cited
locus** (exact substring → `quote-exact`; ≥ 0.85 4-gram coverage → `quote-fuzzy`; ≥ 0.50 →
`lemma`). Paradigm listings (comma-separated `{#abruvam, abravīt#}`) are excluded. Cascade tier:
**local-GRETIL** (§5). Output:
[`mbh_note_verdicts.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/mbh_note_verdicts.csv).

**Validation cases (the worked examples, brū / L=53686):**

| Case | Locus | Note | Lane | Result | Verdict |
|---|---|---|---|---|---|
| 1 | `MBH. 7,9283` | *abravat* "fehlerhaft für" *abravīt* | **vulgate locus** | Droṇa adh 200: **abravīt ×7, abravat ×0** | **confirmed** |
| 2 | `MBH. 7,9226` | *yenāvibruvatā praśnam*, "ed. Bomb. … zu lesen" | BORI retrieval | quote-exact at `07,170.032` | **confirmed** |
| 3 | `MBH. 7,9283` (valid ref, same entry) | cited as a *valid* locus | note-miner | not flagged | (correctly not mined) |

Case 1 is the flagship: an earlier draft called it *unresolvable* (single-word *abravīt* is too
common for corpus retrieval), but the **fitted vulgate index resolves it directly** — cited
`N = 9283` maps to Droṇaparvan adhyāya 200, whose ślokas read *abravīt* (`droṇaputram atha
abravīt`), never *abravat*; Böhtlingk's correction is confirmed against the very edition family he
cited. Case 2 is corroborated independently by the BORI retrieval lane (the reading stands verbatim
in the critical text too). Case 3 confirms occurrence-level mining.

**BORI-lane aggregate (2,466 notes; R3 benchmark schema — per-ref ID · evidence tier · verdict · cascade tier):**

| Evidence tier | Notes | | Verdict | Notes |
|---|--:|---|---|--:|
| quote-exact | 648 | | **confirmed** (quote-exact/fuzzy) | **956** |
| quote-fuzzy | 308 | | reading-supported (lemma) | 422 |
| lemma | 422 | | unresolvable (BORI lacks parallel) | 1,088 |
| none | 1,088 | | | |

**Baseline (R1) — now measurable.** Two independent lanes exist: the fitted **vulgate index**
(55.2 % held-out) and **BORI retrieval** (39 % confirmed). They agree on the flagship cases and are
complementary — the vulgate places a citation on its *cited* śloka (a correctable locus, the actual
scholarly payoff), while retrieval attests a *reading* independent of any number. The hybrid is
their union.

## 5. QA — candidate PWG numeric typos

The MBH analogue of the Harivaṃśa `HARIV. 19850` outlier. **13** PWG citations name a verse far
beyond their parvan's robust upper fence (Q3 + 3·IQR and past the 99.9th percentile) — almost
certainly PWG's own numeric misprints. Full list:
[`mbh_candidate_numeric_typos.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/mbh_candidate_numeric_typos.csv).
Worst offenders: `MBH. 13,73001` (`han`, L=115989 — a stray digit), `MBH. 2,17286` (`nalina`,
L=37910 — Sabhā-parvan has ~4,500 ślokas), `MBH. 14,16950` (`jīv`, L=27572). These are
**reported QA items, not change files** — the true readings are not yet established; route
through [`/cologne-correction-queue`](https://github.com/gasyoun/claude-config/blob/main/commands/cologne-correction-queue.md)
once known.

## 6. Reproduce

```sh
python scripts/forensic/f8_mbh_census.py       # P0 inventory + P1 notes + QA typos  (csl-orig only)
python scripts/forensic/f8_mbh_harvest.py      # P2 harvest Nīlakaṇṭha vulgate from sanatana.in (all 18 parvans)
python scripts/forensic/f8_mbh_resolve.py      # P3 per-parvan index fit + held-out gate + locus census
python scripts/forensic/f8_mbh_verify.py       # P4b BORI reading-evidence retrieval (cross-check)
```

`f8_mbh_harvest.py` needs `indic_transliteration`; it caches raw pages under a **gitignored**
`data/forensic/_mbh_vulgate_cache/` and writes verses to a gitignored `_mbh_vulgate_verses.jsonl`
(rights: third-party transcription, only measurements committed). `f8_mbh_resolve.py` /
`f8_mbh_verify.py` need `../sanskrit-util/py` (and, for verify, the `../SamudraManthanam` GRETIL
mirror + its own gitignored `_mbh_bori_folded.jsonl`).

## 7. Provenance

Census measured and pipeline (harvest → per-parvan index → held-out gate → resolve → BORI
cross-check) executed 11–12-07-2026 by Opus 4.8 (`claude-opus-4-8`) over
[`csl-orig`](https://github.com/sanskrit-lexicon/csl-orig), the
[sanatana.in](https://sanatana.in/mahabharata) Nīlakaṇṭha vulgate (local sample in
[`CommentaryStrategies/mahabharata-nilakantha`](https://github.com/gasyoun/CommentaryStrategies/tree/main/mahabharata-nilakantha)),
the local [`SamudraManthanam`](https://github.com/gasyoun/SamudraManthanam) GRETIL BORI mirror, and
[`VisualDCS`](https://github.com/gasyoun/VisualDCS) DCS, under
[H610](https://github.com/gasyoun/Uprava/blob/main/handoffs/H610-Opus_csl-atlas_mbh_citation_census_11.07.26.md)
(program [H602](https://github.com/gasyoun/Uprava/blob/main/handoffs/H602-Fable_csl-atlas_citation-verification-roadmap_11.07.26.md);
ACL-lineage uplift [H661](https://github.com/gasyoun/Uprava/blob/main/handoffs/H661-Fable_csl-atlas_citation-roadmap-acl-uplift_11.07.26.md);
book-7 census [H761](https://github.com/gasyoun/Uprava/blob/main/handoffs/H610-Opus_csl-atlas_mbh_citation_census_11.07.26.md)).
The earlier "locus census blocked" verdict (and its
[`SanskritLexicography/DEAD_ENDS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md)
§8b entry) is **retracted** — the vulgate exists and the index validated across all 18 parvans.

_Dr. Mārcis Gasūns_
