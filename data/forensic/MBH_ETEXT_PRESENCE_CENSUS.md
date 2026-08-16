# Mahābhārata e-text link layer + the vulgate/critical presence verdict

_Created: 16-08-2026 · Last updated: 16-08-2026_

**What this is.** The text half of the MBh citation programme. Its sibling
[`MBH_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/MBH_CITATION_RESOLUTION_CENSUS.md)
delivered the **numbering** — a fitted per-parvan continuous index over 83,971 Nīlakaṇṭha
vulgate verses. This document delivers the **text**: an e-text link beside every scan link, and
a four-state presence verdict saying, for each citation, whether the verse stands in the
vulgate, in the BORI critical edition, in both, or was never checked.

Executed under
[H2845](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2845-Opus_csl-atlas_citation-etext-layer-mbh-nilakantha-critical-presence_15.08.26.md),
16-08-2026, Opus 5 (`claude-opus-5`).

## 0. The question this answers

> *"Good that MBH. 12,8081 finally at least links to the Cologne scan. But can it link ALSO to
> the etext? We have a concordance, the Nīlakaṇṭha one, right? Is `yadā ca pṛthivīṃ sarvāṃ
> yajamāno 'nuparyagāḥ` in Nīlakaṇṭha's edition that we have full etext of? Is it in the
> Critical edition as well, where? Its absence, if so, is of value as well."*

Absence is only *of value* when it is **proven**. So the whole design rests on one distinction:
`unchecked` is never written as `absent`.

## 1. The witnesses — where the text came from, and why it is not committed

The premise "we have full etext of" needed checking, and was **half true**: this repo held the
numbering and no verse bytes at all
(`data/forensic/_mbh_vulgate_cache/` and `_mbh_vulgate_verses.jsonl` were both absent on disk).
Both witnesses did exist, in the sibling repo, on a branch that never leaves the machine:

| Witness | Verses | Where it was found | Rights |
|---|---:|---|---|
| Nīlakaṇṭha (Bhāvadīpa) vulgate | 83,971 | [CommentaryStrategies](https://github.com/gasyoun/CommentaryStrategies), branch `mahabharata-nilakantha-local-only-do-not-push`, scraped from [sanatana.in/mahabharata](https://sanatana.in/mahabharata) (H921) | third-party volunteer transcription — measurements only |
| BORI critical edition (Tokunaga/Smith "UR" text) | 158,501 half-verse lines | same branch, `mahabharata-nilakantha/bori-critical/MBh01–18.txt` (H784) | © BORI 1999; Smith's stated terms: *"please do not provide copies of the text to others"* |

Both are staged into **gitignored** caches by
[`scripts/forensic/f8_mbh_witnesses.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_witnesses.py),
read straight out of the sibling's git object store — no re-scrape, no network, no checkout of
that branch. Nothing in this document or in any committed CSV carries verse bytes; the single
half-verse quoted in §5 is a de-minimis quotation as evidence, of the kind the dictionaries
themselves print, not a copy of either text.

**Rights verdict (publish-safety, 16-08-2026):** committed artefacts are **numbers, addresses
and URLs only**. The staged text stays local and gitignored. The one exception is the specimen
half-verse in §5, quoted because the question cannot be answered without it.

### Two traps worth keeping

1. **The old harvester no longer works.** `f8_mbh_harvest.py` fetches
   `sanatana.in/mahabharata/listing/getParvaByPage/<slug>?page=<n>`. Probed 16-08-2026: the host
   is up, the parva pages render, and that endpoint returns a **one-byte body**. The site was
   rebuilt around `listing/parva/<slug>?id=P..._U..._A..._S...`. Re-harvesting therefore needs a
   rewritten parser; staging from the sibling branch is what unblocked this pass.
2. **The BORI text is ISO-15919, not IAST.** `r̥`/`l̥` survive `indic_transliteration`'s
   IAST→SLP1 conversion, but anusvāra **`ṁ` (U+1E41) does not** — it passes through as a literal
   `ṁ`, and every folded key carrying an anusvāra then fails to match. Measured, not assumed:
   before the normalisation was added, the §5 specimen came back "absent from the critical
   edition", which would have been a **false finding published as a discovery**. Normalising
   ISO-15919 → IAST first is load-bearing.

## 2. The etext link, beside the scan link

A citation now has two targets. The scan link already shipped
([`ls_links.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_links.py)
→ `mbhcalc`); the etext link is new and is built from the vulgate address the fitted index
resolves to:

| Layer | Template | Example for `MBH. 12,8081` |
|---|---|---|
| scan | `https://sanskrit-lexicon-scans.github.io/mbhcalc?<parvan>.<verse>` | [mbhcalc?12.8081](https://sanskrit-lexicon-scans.github.io/mbhcalc?12.8081) |
| etext | `https://sanatana.in/mahabharata/listing/parva/<slug>?id=P<pp>_U<uu>_A<aaa>_S<sss>` | [shantiparva?id=P12_U03_A226_S006](https://sanatana.in/mahabharata/listing/parva/shantiparva?id=P12_U03_A226_S006) |

The `id` is exactly the `div.shloka` id the harvest recorded, so every link is verifiable
against our own data rather than guessed. Both are emitted as **functions**
(`scan_url` / `etext_url` in
[`f8_mbh_presence.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_presence.py)),
not as stored columns: baking 90-character URLs into 154k rows would add ~14 MB of derivable
text, and a link belongs in the citation renderer. Thirty rendered pairs — scan and etext side
by side — are committed as
[`mbh_presence_spotcheck.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/mbh_presence_spotcheck.csv)
so the join is demonstrable rather than asserted.

**Not yet done, and named plainly:** MG's *"All voting forms have the same functionality now?"*
requires the etext branch to land inside the shared renderer
`RussianTranslation/src/ls_links.py` in the sibling repo
[SanskritLexicography](https://github.com/gasyoun/SanskritLexicography), so that every sheet
built from it gains the link at once. That file is in a different repository from this one and
was **not** touched by this pass. What remains there is one function returning the template
above plus a selftest case; until it lands, cards still render the scan link only.

## 3. Method — how presence is decided

Alignment is **by content, never by number**. The vulgate carries exactly the passages the
critical edition banished to its apparatus, so śloka numbers diverge structurally; comparing
`12.226.6` against `12,226.6` would measure the numbering, not the text.

1. Every vulgate verse is split into half-verses on the daṇḍa (the unit the critical edition is
   addressed by), transliterated to SLP1, and folded (length/retroflex/sibilant-neutral, letters
   only).
2. Each half is retrieved against the **whole** 158,501-line critical corpus by a 12-gram
   shingle index (indexed at step 4, queried at step 1, so any shared substring of ≥ 15 folded
   characters surfaces a candidate). Shingles shared by more than 40 half-verses are dropped as
   formulaic (`bharatarṣabha`, `mahābāho`) — they identify nothing.
3. The best four candidates get an exact 4-gram coverage score, measured **on the critical
   side** (`|shared| / |critical grams|`), so a critical half wholly contained in a longer
   vulgate reading scores 1.0 and a vulgate expansion cannot inflate the score.

| coverage | verdict | evidence label |
|---|---|---|
| ≥ 0.85 | `present` | `quote-exact` |
| ≥ 0.60 | `present` | `quote-fuzzy` — same verse, recension variant |
| below | `absent` | `none` |

A half shorter than 16 folded characters is too formulaic to adjudicate (`X uvāca`) and is
skipped; **a verse whose every half is skipped is `unchecked`, not `absent`.**

## 4. The four-state verdict

### 4.1 Verse level — 83,971 vulgate verses, unconditional

This table compares two texts and depends on no numbering at all.

| vulgate | critical | verses | share | reading |
|---|---|---:|---:|---|
| present | present | 77,246 | 92.0 % | ordinary — the verse stands in both recensions |
| present | **absent** | 6,494 | 7.7 % | **vulgate-only** — the critical edition relegated it to the apparatus |
| absent | unchecked | 231 | 0.3 % | service records with an empty mūla; nothing to check against |
| unchecked | — | 0 | — | both witnesses were staged, so nothing is unexamined |

Per parvan the vulgate-only share ranges from 0.9 % (sauptika) to 29.1 % (svargārohaṇa,
92 of 316) — the epic's late and appended stretches are exactly where the vulgate expands, which
is the expected shape and a sanity check on the method.

### 4.2 Citation level — 70,423 PWG/MW MBh citations

Joined onto PWG's and MW's own extractable loci
([`mbh_citation_inventory.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/mbh_citation_inventory.csv)),
not a toy sample.

| verdict | citations | share |
|---|---:|---:|
| `present/present` | 60,101 | 85.3 % |
| `present/absent` | 5,950 | 8.4 % |
| `unresolved-locus` (`unchecked/unchecked`) | 3,880 | 5.5 % |
| `absent/unchecked` | 492 | 0.7 % |

**What this table is conditional on, stated before it is quoted anywhere.** The verse-level
table is unconditional; this one is only as good as the fitted locus. §6 measures that
directly: the fitted index puts a citation on the exactly right verse about **half** the time.
So `present/absent` here means *"the verse the fitted index points at is vulgate-only"* — not
yet *"PWG cited a verse BORI rejects"*. The quote lane is what upgrades one claim to the other,
and it is not yet applied to the whole citation mass.

Outputs:
[`mbh_vulgate_critical_presence.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/mbh_vulgate_critical_presence.csv)
· [`mbh_citation_presence.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/mbh_citation_presence.csv)
· [`f8_presence_report.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f8_presence_report.json).

## 5. The specimen — `MBH. 12,8081`, answered

The citation is PWG L22170 s.v. `{#gA#}`, sense `{#anupari#}` "durchgehen, durchwandern"
([`csl-orig/v02/pwg/pwg.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt),
line 109787):

    {#yadA ca pfTivIM sarvAM yajamAno 'nuparyagAH#} <ls>MBH. 12,8081</ls>.

Three lanes, and they disagree — which is the result
([`f8_specimen_mbh_12_8081.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f8_specimen_mbh_12_8081.json)):

| lane | answer |
|---|---|
| **A · locus** — where the fitted index sends `12,8081` | Śānti **226.6** (continuous_C 8077). The verse standing there is `santāpādbhraśyate cāyurdharmaścaiva sureśvara…` — **not** the quoted one. |
| **B · quote, vulgate** | The pratīka stands at Śānti **223.24** (`id=P12_U03_A223_S024`, continuous_C 7967, calibrated_N **7971**). Cited 8081 − fitted 7971 = **Δ 110 ślokas**. |
| **C · quote, critical** | BORI **12,216.22a**, 4-gram coverage 0.794 — present, with a variant reading. |

**Answer to MG, in order.**

- *Is it in Nīlakaṇṭha's edition?* **Yes** — Śāntiparvan 223.24, linkable:
  [shantiparva?id=P12_U03_A223_S024](https://sanatana.in/mahabharata/listing/parva/shantiparva?id=P12_U03_A223_S024).
- *Is it in the Critical edition as well, where?* **Yes** — BORI 12,216.22ab. But the two
  witnesses do not read the same words:

  | witness | half-verse |
  |---|---|
  | Nīlakaṇṭha vulgate 12.223.24a | *yadā **ca** pṛthivīṃ sarvāṃ yajamāno **'nuparyagāḥ*** |
  | BORI critical 12,216.22a | *yadā **tu** pṛthivīṁ sarvāṁ yajamāno **'nuparyayāḥ*** |

- *Is its absence of value?* **The verse is not absent — the reading is.** PWG files this
  citation under `√gā` because the vulgate reads `anupari-agāḥ` (aorist of √gā). The critical
  edition reads `anupari-ayāḥ` (√i). At the four-state verse level the verdict is
  `present/present`; at the level of the word the entry is built on, the evidence is
  **vulgate-only**. That is a finer and more useful finding than a missing verse would have
  been: the PWG sense survives or falls with the Bombay recension, and a card showing both
  links lets a reader see that in one glance.
- The Δ 110 in lane B is not a defect of the quote lane but a measurement of the locus lane
  (§6). Where PWG prints the verse, the text — not the number — is the better address.

## 6. How far the fitted locus can be trusted — a free labelled set

PWG prints its quotation immediately before the locus in **12,541** places
(`{#…#} <ls>MBH. p,v</ls>`). Each pair is a labelled example that PWG wrote long before this
index existed, so no held-out split is needed. Retrieving each pratīka in the vulgate and
comparing the calibrated_N of the verse it lands in against the number PWG printed
([`f8_mbh_quote_lane.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_quote_lane.py)
→ [`mbh_quote_lane_check.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/mbh_quote_lane_check.csv)):

All 12,541 pairs were swept. **6,912** carried a pratīka long enough to identify a verse
(≥ 24 folded characters) and were retrieved at ≥ 0.60 coverage; 5,342 probes were too short to
adjudicate and 287 were not retrieved — both are reported, not silently dropped.

| agreement between PWG's printed number and the verse its own quotation stands in | share of the 6,912 |
|---|---:|
| exact (Δ = 0) | **49.4 %** |
| within ±2 ślokas | 68.0 % |
| within ±10 | 72.5 % |
| within ±50 | 85.6 % |
| within ±200 | 98.6 % |

Median Δ = 0, mean Δ = +0.68 — the index is **unbiased but noisy**: it does not drift
systematically, it scatters. The §5 specimen's Δ 110 sits in the 14 % tail beyond ±50.

This is the accuracy the §4.2 citation-level verdict inherits, and it agrees with the fitted
index's own held-out figure (0.552) in
[`MBH_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/MBH_CITATION_RESOLUTION_CENSUS.md).
The §4.1 verse-level table does not depend on it at all.

## 7. Held-out spot check — 30 random resolved loci

[`mbh_presence_spotcheck.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/mbh_presence_spotcheck.csv),
sampled with seed 2845 from the resolved citations:

- **30/30** address round-trip: the calibrated_N read back from the resolved
  (parvan, adhyāya, śloka) equals the cited number.
- **30/30** carry vulgate text at that address, so none is a phantom locus.
- **30/30** render both a scan URL and an etext URL.

Read this for what it is: a check that the join, the addressing, and the link builders are
sound end to end. It is **not** a check that the fitted index put the citation on the right
verse — §6 is, and says roughly half.

## 8. What is still open

1. **`ls_links.py` etext branch** (§2) — the shared renderer in the sibling repo; until it
   lands, only this repo's data carries the etext address.
2. **Quote-lane upgrade of the citation table.** The 12,541 PWG pairs can replace a fitted
   guess with an exact address wherever PWG quotes the verse, turning a conditional
   `present/absent` into an unconditional one. The machinery exists; the join to
   `mbh_citation_presence.csv` does not.
3. **MW's quoted citations** are not mined the way PWG's are — the same free labelled set
   almost certainly exists in `mw.txt`.
4. **Re-harvest path.** If the sibling local-only branch is ever lost, the vulgate cannot
   currently be re-fetched: `f8_mbh_harvest.py` needs rewriting for the rebuilt sanatana.in
   (§1, trap 1). Fixing it before it is needed is cheaper than after.
5. **Repeated calibrated numbers.** 83,971 addressed verses carry only 80,376 distinct
   calibrated_N values; the locus→address lookup keeps the first. Some 3,595 addresses are
   therefore unreachable from a number alone — small, but it belongs in the error budget.

_Dr. Mārcis Gasūns_
