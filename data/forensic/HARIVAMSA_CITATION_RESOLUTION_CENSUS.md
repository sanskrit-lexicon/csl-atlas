# Harivaṃśa citation-form census and resolution options

_Created: 10-07-2026 · Last updated: 10-07-2026_

**What this is.** A measured census of how PWG and MW cite the *Harivaṃśa*, and of which text can
actually adjudicate whether one of those citations is **wrong**. It exists because the A10
shared-erroneous-citation test ([`article_21_apparatus_not_errors.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md) §6)
resolved **1 of 587** refs against DCS, and because the remedy the paper offers in the same
paragraph — "a vulgate↔critical verse concordance" — **cannot work**. See
[§ Why a concordance cannot help](#why-a-concordance-cannot-help).

Companion to [`CITATION_TAGGING.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/CITATION_TAGGING.md)
and [`shared_rare_citations.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/shared_rare_citations.csv).
Executable follow-up: [H488](https://github.com/gasyoun/Uprava/blob/main/handoffs/H488-Opus_csl-atlas_harivamsa_vulgate_citation_resolution_10.07.26.md).
Negative-result record: [`SanskritLexicography/DEAD_ENDS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) §8.

## 1. Citation-form census

Measured 10-07-2026 over [`csl-orig/v02/pwg/pwg.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwg/pwg.txt)
and [`csl-orig/v02/mw/mw.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw.txt).

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
- 🟡 **Band boundaries above are approximate.** P2's upper edge (~12,562) is a cumulative estimate
  from Kinjawadekar's verse counts, not a Calcutta-verified boundary; the exact split shifts once the
  index is fitted. Treat 83.9% as a close estimate, not a settled figure.

## Reproduce

Citation-form census: grep `HARIV\.(">| )[0-9]+` over `csl-orig/v02/pwg/pwg.txt`, and
`<ls>Hariv\.[^<]*</ls>` over `csl-orig/v02/mw/mw.txt`. Vulgate harvest census: walk the index at
`harivamsa-cs-index.html`, follow both `hv_<p>_<c>.html` and `_mpr` series (parvan 2 under
`vishnuparva/`, parvan 3 under `bhavishyaparva/`), count `\|\|\s*(\d+)-(\d+)-\s*(\d+)` markers whose
parvan/adhyāya match their page.

**Provenance:** measured 10-07-2026 by Opus 4.8 (`claude-opus-4-8`) over
[`csl-orig`](https://github.com/sanskrit-lexicon/csl-orig),
[`VisualDCS`](https://github.com/gasyoun/VisualDCS), and the Kinjawadekar e-text. Supersedes the
"recension artifact / needs a concordance" framing recorded in A10 §6 by
[PR #235](https://github.com/sanskrit-lexicon/csl-atlas/pull/235).

_Dr. Mārcis Gasūns_
