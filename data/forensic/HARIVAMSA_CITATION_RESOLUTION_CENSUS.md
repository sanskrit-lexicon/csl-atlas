# Harivaṃśa citation-form census and resolution options

_Created: 10-07-2026 · Last updated: 10-07-2026_

**What this is.** A measured census of how PWG and MW cite the *Harivaṃśa*, and of which text can
actually adjudicate whether one of those citations is **wrong**. It exists because the A10
shared-erroneous-citation test ([`article_21_apparatus_not_errors.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md) §6)
resolved **1 of 587** refs against DCS, and because the remedy the paper offers in the same
paragraph — "a vulgate↔critical verse concordance" — **cannot work**. See
§ Why a concordance cannot help.

Companion to [`CITATION_TAGGING.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/CITATION_TAGGING.md)
and [`shared_rare_citations.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/shared_rare_citations.csv).
Executable follow-up: [H488](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H488-Opus_csl-atlas_harivamsa_vulgate_citation_resolution_10.07.26.md).
Negative-result record: [`SanskritLexicography/DEAD_ENDS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) §8.

## 1. Citation-form census

Measured 10-07-2026 over [`csl-orig/v02/pwg/pwg.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt)
and [`csl-orig/v02/mw/mw.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw/mw.txt).

| Measure | PWG | MW |
|---|--:|--:|
| Total `HARIV.` / `Hariv.` markers | 15,688 | 6,304 |
| **Numbered** citations (`HARIV. 9529`) | **15,415** | **1,053** |
| Bare sigil, no number | — | 5,229 |
| Page-line form (`HARIV. S. 927, Z. 5`) | 9 | 0 |
| Parvan-style (`HARIV. 52,84`) | 2 | 0 |
| Observed numeric range | 1 … 16,369 | within 1 … 16,374 |
| Out-of-range outliers | **1** (`HARIV. 19850`) | 0 |

**Both dictionaries address the same space.** The observed PWG maximum (16,369) sits just under the
Calcutta vulgate's nominal 16,374 ślokas, and MW's numbered refs fall in the same range. The
numbering is a single **continuous running śloka count**, not `parvan.adhyāya.verse`. This is the
Calcutta (Asiatic Society, 1834–39) vulgate — the edition Böhtlingk cited.

Decile distribution of PWG's 15,415 numbers: p10 = 1,075 · p50 = 7,068 · p90 = 13,680.

**QA item — one bad number.** `HARIV. 19850` exceeds the ceiling by ~3,500 and is glossed *"N. pr.
eines Wesens im Gefolge Śiva's"*. Almost certainly a typo in PWG. The correct value is **not yet
established**, so this is a reported issue, not a change file; route through
[`/cologne-correction-queue`](https://github.com/gasyoun/claude-config/blob/main/commands/cologne-correction-queue.md)
once the true reading is known.

## 2. What each candidate text can adjudicate

| Text | Edition | Extent | Addressing | Can it test a wrong `HARIV. N`? |
|---|---|---|---|---|
| DCS / VisualDCS | Vaidya, BORI critical | 118 adhyāyas, ~6,073 ślokas | adhyāya.verse | **No** — wrong recension |
| Vulgate↔critical concordance | derived | n/a | maps addresses | **No** — see §3 |
| GRETIL `sa_harivaMza` | Vaidya critical + star passages | 118 adhyāyas | `HV_nn.nn` | **No** — same recension as DCS |
| Kinjawadekar e-text | Chitrashala 1936, **vulgate** | 291 adhyāyas, 11,646 verses harvested | parvan-adhyāya-verse | **Yes**, after a continuous index is fitted |
| Calcutta 1834–39 scan | the cited edition itself | Vol. IV, pp. 445–1007 | continuous śloka | **Yes** — but needs OCR |

DCS chapter census: exactly **118** files, `HV, 1` … `HV, 118`, in `VisualDCS/src/DCS-data-2026/conllu/files/Harivaṃśa/`.
The critical edition is roughly **one third** of the vulgate (6,073 of 16,374 ślokas), so a
majority of any vulgate citation is expected to be `ABSENT` from it by construction.

## 3. Why a concordance cannot help

A concordance is a function from a vulgate address to a critical address. It maps the address **on
the assumption the address is correct** — which is exactly the proposition the shared-error test
interrogates.

- Feed it an **erroneous** citation → it returns a critical verse that does not contain the headword.
- Feed it a **correct** citation pointing at vulgate-only material → it returns `ABSENT`.

Both branches emit the same observable: *headword not found*. The concordance therefore cannot
distinguish **"Böhtlingk wrote the wrong number"** from **"Vaidya cut this verse"** — and with ⅔ of
the vulgate missing from the critical text, the second branch dominates. This holds even for a
*perfect, verse-level* concordance. It is not a data-quality problem; it is a structural one.

**The error is an error in the vulgate's own numbering, so it must be adjudicated against the
vulgate.** Once a numbered vulgate text exists, no concordance is needed at all.

> A concordance may still be worth building for *other* purposes — reading our citations against
> modern critical-edition scholarship, for instance. It simply does not unblock A10.

## 4. The reachable path

[mahabharata-resources.org/harivamsa](https://mahabharata-resources.org/harivamsa/harivamsa-cs-index.html)
carries the Harivaṃśa of **Pandit Ramachandrashastri Kinjawadekar (Chitrashala Press, 1936)** — a
vulgate text, ITRANS, transcribed by K. S. Ramachandran and Gilles Schaufelberger. Verse markers are
`||1-10-2` (parvan-adhyāya-verse); there is **no** continuous numbering, so the bridge to `HARIV. N`
must be fitted.

Harvest census (both page series; the `_mpr` mūla-pāṭha series is the fuller one):

| Parvan | Adhyāyas with verses | Verses |
|---|--:|--:|
| 1 Harivaṃśa | 55 | 3,036 |
| 2 Viṣṇu | 127 | 7,526 |
| 3 Bhaviṣya | 36 | ~1,062 |
| **Union (distinct triples)** | | **11,646** |

**11,646 of 16,374 = 71.1% of the vulgate.** Kinjawadekar divides chapters as 55/128/108 = **291
adhyāyas**, against Calcutta's 55/81/135 = **271** — the chapter division differs between vulgate
editions even though the verse sequence is broadly shared. Hence fitting an index, not a lookup.

Where the A10 pool lands (565 `HARIV.` refs of the 587 shared rare citations):

| Band | Refs | Share |
|---|--:|--:|
| P1 Harivaṃśa-parvan (1–3036) | 157 | 27.8% |
| P2 Viṣṇu-parvan (3037–~12562) | 317 | 56.1% |
| P3 Bhaviṣya-parvan (>~12562) | 91 | 16.1% — thin coverage |
| **Reachable now (P1+P2)** | **474** | **83.9%** |

**474 of 565, against 1 of 587 via DCS.** The 91 Bhaviṣya refs must be logged as an explicit
exclusion, never silently dropped; closing that gap means OCRing Calcutta Vol. IV.

## 5. Caveats

- 🔴 **Circularity.** Fitting the continuous index on the citations and then calling the residuals
  "errors" is circular unless the offset is fitted with a **robust statistic** (median, dominated by
  correct citations) and validated on **held-out** citations (fit on PWG, hold out MW). If the
  held-out agreement is poor, the index is untrustworthy and the error test must not be run.
- 🟠 **The host's TLS certificate is expired.** `WebFetch` fails; `curl -k` /
  `requests(verify=False)` work. Logged in [`Uprava/FINDINGS.md`](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md).
- 🟠 **Rights.** The Kinjawadekar text is 1936 and the e-text is a volunteer transcription. Deriving
  *measurements* is fine; **republishing the bytes may not be**. Run
  [`/publish-safety-check`](https://github.com/gasyoun/claude-config/blob/main/commands/publish-safety-check.md)
  before any public-tier `kosha` release.
- 🟢 **Superseded by §6 (H488 executed 10-07-2026).** The §4 reachability of 83.9% was a
  *plan-time estimate*; the actual harvest reached **93.8%** of the vulgate and the fitted index
  validated on held-out MW anchors, so the numbers below §6 — not §4's estimates — are the settled
  figures. §4 is retained as the pre-execution scoping record.

## 6. Results (H488, executed 10-07-2026)

The plan in §4 was executed. Outputs:
[`harivamsa_vulgate_concordance.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/harivamsa_vulgate_concordance.csv),
[`harivamsa_continuous_index_offsets.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/harivamsa_continuous_index_offsets.csv),
[`harivamsa_shared_citation_resolution.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/harivamsa_shared_citation_resolution.csv),
[`f7_report.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f7_report.json).
Scripts:
[`f7_harivamsa_harvest.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f7_harivamsa_harvest.py),
[`f7_harivamsa_resolve.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f7_harivamsa_resolve.py).

**The concordance file.** [`harivamsa_vulgate_concordance.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/harivamsa_vulgate_concordance.csv)
is the standalone product of the calibration: **15,364 rows**, one per harvested verse, mapping
Kinjawadekar's `parvan · adhyāya · verse` address to the **continuous Calcutta śloka number `HARIV. N`**
the Petersburg dictionaries cite (`continuous_sloka` = `C + adhyaya_offset`), plus the adhyāya's offset
and anchor count. Numbers only — **no verse text** (rights, per §5). This is the *vulgate-internal*
concordance (Kinjawadekar addressing ↔ Calcutta continuous numbering), **not** a vulgate↔critical
(DCS/BORI) concordance — that one is a separate object and, for the error test, a
[dead end](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) §8. Caveats: the
number is an **estimate** (calibration noise ±1–2; held-out MW 68.4 % land within ±3; `kīrtimant`
`1-2-9` → 63 vs cited 62); the mapping is monotone in verse order but for 31 of 15,363 steps at chapter
seams; and **0.8 %** of verses sit in adhyāyas whose offset was interpolated (`adhyaya_n_anchors = 0`)
rather than directly fitted. Coverage spans continuous **8 … 16,368** of the 16,374-śloka vulgate.

**Harvest beat the §4 estimate.** Fetching *both* page series in full yielded **15,364 distinct
verses = 93.8 %** of the 16,374-śloka vulgate, not the 71.1 % estimated pre-harvest — the
Bhaviṣya-parvan came in at **4,594 verses / 135 adhyāyas** (the `bhavishyaparva/` plain series is far
fuller than the `_mpr` series the estimate sampled), so the "thin P3 / OCR Calcutta Vol. IV" worry in
§4 and the Prerequisites largely dissolves. Kinjawadekar divides the text **55 / 128 / 135 = 318
adhyāyas**; P1 and P3 chapter counts match Calcutta (55, 135), so the continuous-index drift
concentrates in the Viṣṇu-parvan. (A handful of stray out-of-range verse markers — adhyāya 422, 711,
… with 1–2 verses — were dropped.)

**Continuous index — held-out check PASSED.** A per-adhyāya constant offset (median of anchor
residuals `N − C`, clipped to a monotone confident-baseline envelope so a few mismatched anchors
cannot inject garbage) was fitted on **14,471 PWG** anchors and validated on **815 held-out MW**
anchors:

| Held-out MW check | Value |
|---|--:|
| MW anchors with headword within ±3 of cited `N` | **528 / 772 = 68.4 %** |
| Shuffled-N null (same test at a random far `N`) | 2.1 % |
| Enrichment | **≈ 33×** |

The calibrated `δ = Ĉ − N` distribution peaks sharply at 0 (283) and is tight (±2), and corroboration
is flat in the window width (36.7 % at ±2 → 39.7 % at ±10), confirming correct citations sit *at* the
cited verse, not merely near it. The index is trustworthy; the error test was run.

**Shared-citation resolution (565 shared rare `HARIV.` refs, 547 with a matchable ≥4-char key):**

| Category | Count | Share |
|---|--:|--:|
| **corroborated** — headword within ±3 of cited `N` | **206** | 37.7 % |
| displaced — headword present only > ±3 from `N` | 152 | 27.8 % |
| absent — no strict locus (uncovered verse or unmatchable compound) | 189 | 34.6 % |

**(A) Verse-level shared apparatus — confirmed.** 206 of 547 shared rare citations **resolve to the
exact cited vulgate śloka** (e.g. `kīrtimant` `HARIV. 62` → verse 1-2-9, which reads
*…kīrtimantaṃ ca…*), against a shuffled-N null of **2.7 (0.5 %)** — a **≈ 75× enrichment**. This
upgrades A10's citation evidence from *shared sources/editions* (source-Jaccard) to a **shared,
verse-level, verifiably-correct apparatus**, and stands against **1 of 587** resolvable via DCS.

**(B) Shared *erroneous* citation — negative (a valid exit).** No shared error is demonstrable above
chance. The "displaced" cases are **fewer** than expected by chance (79 clean displaced observed vs a
shuffled-N null of **200**), their offsets `δ` neither cluster nor form plausible-typo patterns, and
widening the window does not pull them toward `N` — i.e. they are coincidental occurrences of a rare
word elsewhere while the cited (often uncovered) verse is its true home, **not** copied wrong numbers.
So A10's *airtight* upgrade (a shared **mistake**) is **not** achieved — but now for a measured reason
rather than a data-availability block: against the very edition the dictionaries cite, the shared
citations **verify as correct**, leaving no shared error to find in this pool. A10 stays at "very
strong, not airtight," now with direct verse-level corroboration underneath it.

## Reproduce

Citation-form census: grep `HARIV\.(">| )[0-9]+` over `csl-orig/v02/pwg/pwg.txt`, and
`<ls>Hariv\.[^<]*</ls>` over `csl-orig/v02/mw/mw.txt`. Full resolution pipeline (harvest → transcode →
anchors → calibrate → held-out → shared-error test): `python scripts/forensic/f7_harivamsa_harvest.py`
then `python scripts/forensic/f7_harivamsa_resolve.py` (needs the sibling `../sanskrit-util/py` and
`pip install indic_transliteration`; the harvested e-text is gitignored per the rights caveat and is
regenerated by the harvest script).

**Provenance:** census measured, and §6 resolution executed (H488), 10-07-2026 by Opus 4.8
(`claude-opus-4-8`) over [`csl-orig`](https://github.com/sanskrit-lexicon/csl-orig),
[`VisualDCS`](https://github.com/gasyoun/VisualDCS), and the Kinjawadekar e-text. Supersedes the
"recension artifact / needs a concordance" framing recorded in A10 §6 by
[PR #235](https://github.com/sanskrit-lexicon/csl-atlas/pull/235); the §6 result is written back to
A10 §6.

_Dr. Mārcis Gasūns_
