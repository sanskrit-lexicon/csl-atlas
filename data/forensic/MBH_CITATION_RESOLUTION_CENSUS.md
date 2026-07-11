# Mahābhārata citation census, Böhtlingk correction-notes verification, and why the locus census is blocked

_Created: 11-07-2026 · Last updated: 11-07-2026_

**What this is.** The Mahābhārata port of the executed Harivaṃśa census
([`HARIVAMSA_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/HARIVAMSA_CITATION_RESOLUTION_CENSUS.md),
H488) — the largest citation mass in both Petersburg dictionaries and Monier-Williams. It
delivers three things and records one blocker:

1. a full **citation-form census** of how PWG and MW address the MBH (P0);
2. a context-aware **census of Böhtlingk's own correction notes** on MBH loci — the new
   pilot lane the [citation-verification roadmap](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/CITATION_VERIFICATION_ROADMAP_2026_2027.md)
   §4 W1a prescribes (P1);
3. per-note **verification** against the local BORI critical text via a deterministic
   character-fuzzy **quote-retrieval lane** (roadmap R1), reporting the R3 benchmark schema (P4/P4b);

and it records **why the fitted-index locus census that worked for the Harivaṃśa cannot be run
for the MBH** ([§ Why the locus census is blocked](#why-the-locus-census-is-blocked)) — the
handoff's sanctioned negative exit, written back to
[`SanskritLexicography/DEAD_ENDS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md).

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

## 2. Why the locus census is blocked

The Harivaṃśa census succeeded because a clean, freely downloadable **vulgate** e-text existed
(Kinjawadekar, Chitrashala 1936) against which a continuous index could be fitted and
held-out-validated. **No equivalent exists for the full Mahābhārata.** Every freely
bulk-downloadable full MBH Sanskrit text is the **BORI critical recension**:

| Text | Recension | Bulk-downloadable | Role here |
|---|---|---|---|
| GRETIL (Tokunaga/Smith), local [`SamudraManthanam`](https://github.com/gasyoun/SamudraManthanam/tree/main/GRETIL-1_sanskr) mirror | BORI critical | yes | reading evidence (this doc) |
| DCS, local [`VisualDCS`](https://github.com/gasyoun/VisualDCS) CoNLL-U | BORI critical | yes | lemma evidence |
| [sanskritdocuments.org](https://sanskritdocuments.org/) MBH | BORI critical | yes | (same recension) |
| [bombay.indology.info](https://bombay.indology.info/mahabharata/statement.html) | BORI critical | yes | (same recension) |
| Manipal Sastri-Vavilla (Nilakantha **vulgate**) | vulgate | **no** — SPA, private API (D3) | spot-check tier only |
| Calcutta 1834–39 (the cited edition) | vulgate | **no** — scans, needs OCR | last-tier |

Fitting a continuous index against the **critical** text is the measured
[DEAD_ENDS §8](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md)
structural dead end: BORI systematically removed vulgate passages throughout, so the offset
between a Calcutta continuous `N` and a BORI running count is not a per-parvan constant, and a
concordance cannot separate "wrong number" from "verse cut by the editors" (DCS resolved 1 of
587 shared refs). **The MBH locus census is therefore deferred, not attempted against an
untrusted index** — the handoff's sanctioned exit (b). It unblocks only when a Nilakantha-vulgate
e-text is obtained (Manipal Sastri-Vavilla harvest under a D3 ruling, or OCR of the Calcutta
scans). Until then, the reachable verification is **reading-evidence**, not locus arithmetic.

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

## 4. Verification: reading-evidence + character-fuzzy quote-retrieval (P4/P4b)

Because locus arithmetic is blocked (§2), verification runs the roadmap-R1 **retrieval lane**:
[`f8_mbh_verify.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_verify.py)
folds the local GRETIL BORI text (72,771 verses) to a length/retroflex/sibilant-normalized
SLP1 key and searches each note's quoted pratīka across the **whole corpus, independent of the
cited locus** (exact substring → `quote-exact`; ≥ 0.85 4-gram coverage → `quote-fuzzy`; ≥ 0.50
→ `lemma`). Grammatical paradigm listings (comma-separated `{#abruvam, abravīt#}`) are excluded
— they are not verse quotes and fuzzy-match spuriously. Cascade tier: **local-GRETIL** (§5).
Output: [`mbh_note_verdicts.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/mbh_note_verdicts.csv).

**Validation cases (the worked examples, brū / L=53686):**

| Case | Locus | Note | Evidence | BORI locus | Verdict |
|---|---|---|---|---|---|
| 2 | `MBH. 7,9226` | *yenāvibruvatā praśnam*, "mit der ed. Bomb. … zu lesen" | **quote-exact** | `07,170.32` | **confirmed** |
| 1 | `MBH. 7,9283` | *abravat* "fehlerhaft für" *abravīt*, "wie die ed. Bomb. hat" | none | — | **unresolvable → D3** |
| 3 | `MBH. 7,9283` (valid ref, same entry) | cited as a *valid* locus under `tam … vacanam abravīt` | not flagged | — | (correctly not mined) |

Case 2 is the flagship result: the reading Böhtlingk endorsed "with the Bombay edition" at
Calcutta 7,9226 stands **verbatim** in the critical text — `yenāvibruvatā praśnaṃ tathā kṛṣṇā
sabhāṃ gatā` at `07,170.032` — so his correction is **confirmed** by an independent witness,
locus-free. Case 1 is the honest counter-case: *abravat → abravīt* is a **single-word** Calcutta
print error, and *abravīt* is ubiquitous — corpus retrieval cannot decide it, so it **escalates
to the §5 D3 tier** (a Manipal Sastri-Vavilla / Calcutta-scan spot-check at the actual 7,9283
locus), demonstrating the cascade rather than forcing a verdict. Case 3 confirms the mining is
occurrence-level: the same locus cited validly elsewhere in the entry is **not** flagged.

**Aggregate (2,466 notes; R3 benchmark schema — per-ref ID · evidence tier · verdict · cascade tier):**

| Evidence tier | Notes | | Verdict | Notes |
|---|--:|---|---|--:|
| quote-exact | 648 | | **confirmed** (quote-exact/fuzzy) | **956** |
| quote-fuzzy | 308 | | reading-supported (lemma) | 422 |
| lemma | 422 | | unresolvable (BORI lacks parallel) | 1,088 |
| none | 1,088 | | | |

**956 of 2,466 notes (39 %)** have a quoted reading attested in the critical text — in line
with the Harivaṃśa census's 37.7 % exact-locus corroboration, but reached here **without a
fitted index**, purely by locus-free retrieval. 1,088 are `unresolvable` because BORI (a
different, shorter recension) simply lacks the parallel — expected, and precisely the material
a vulgate e-text would recover. **Baseline (R1):** the fitted-index lane is unavailable for MBH
(§2), so retrieval-only *is* the hybrid here; the fitted-index-vs-retrieval comparison the
roadmap asks for is deferred with the locus census.

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
python scripts/forensic/f8_mbh_census.py      # P0 inventory + P1 notes + QA typos  (csl-orig only)
python scripts/forensic/f8_mbh_verify.py      # P4/P4b BORI reading-evidence retrieval
```

`f8_mbh_verify.py` needs the sibling `../SamudraManthanam` GRETIL mirror, `indic_transliteration`,
and `../sanskrit-util/py`; it caches the folded BORI corpus to a **gitignored**
`data/forensic/_mbh_bori_folded.jsonl` (rights: derived e-text, only measurements are committed).

## 7. Provenance

Census measured and verification executed 11-07-2026 by Opus 4.8 (`claude-opus-4-8`) over
[`csl-orig`](https://github.com/sanskrit-lexicon/csl-orig), the local
[`SamudraManthanam`](https://github.com/gasyoun/SamudraManthanam) GRETIL BORI mirror, and
[`VisualDCS`](https://github.com/gasyoun/VisualDCS) DCS, under
[H610](https://github.com/gasyoun/Uprava/blob/main/handoffs/H610-Opus_csl-atlas_mbh_citation_census_11.07.26.md)
(program [H602](https://github.com/gasyoun/Uprava/blob/main/handoffs/H602-Fable_csl-atlas_citation-verification-roadmap_11.07.26.md);
ACL-lineage uplift [H661](https://github.com/gasyoun/Uprava/blob/main/handoffs/H661-Fable_csl-atlas_citation-roadmap-acl-uplift_11.07.26.md)).
The locus-census blocker is written back to
[`SanskritLexicography/DEAD_ENDS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md).

_Dr. Mārcis Gasūns_
