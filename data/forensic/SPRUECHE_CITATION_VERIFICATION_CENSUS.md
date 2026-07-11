# Indische Sprüche citation-verification census (Wave 1b)

_Created: 11-07-2026 · Last updated: 11-07-2026_

**What this is.** Verification of every PWG `<ls>Spr.</ls>` / `<ls>Spr. (II)</ls>` citation of
Böhtlingk's *Indische Sprüche* against the typed digitizations in
[sanskrit-lexicon-scans/boesp1](https://github.com/sanskrit-lexicon-scans/boesp1) (1st ed.,
1863–65) and [sanskrit-lexicon-scans/boesp2](https://github.com/sanskrit-lexicon-scans/boesp2)
(2nd ed., 1870–73). Wave 1b of the
[Citation Verification Roadmap 2026–2027](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/CITATION_VERIFICATION_ROADMAP_2026_2027.md)
§4, run per [H611](https://github.com/gasyoun/Uprava/blob/main/handoffs/H611-Sonnet_csl-atlas_spruche_citation_verify_11.07.26.md).

Deliverable pair: this census + [`SPRUECHE_CITATION_VERIFICATION_VERDICT.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/SPRUECHE_CITATION_VERIFICATION_VERDICT.csv)
(15,877 rows, R3 schema per H602/H661).

## 1. Scope-defining finding — boesp1 has NO typed text

The mission brief describes both `boesp1` and `boesp2` as "typed editions." **Only `boesp2` is.**
`boesp1`'s `app1/` is a scan-navigation viewer over `pdfpages/*.pdf` with a verse→page **index**
(`app1/pywork/Indische_Spr_v1_Index.txt`) — no per-verse Sanskrit or German text exists anywhere
in the repo. `boesp2/step0/boesp_deva.xml` (and the `web1/json/section*.json` derived from it) is
the real typed digitization (Thomas Malten, per `boesp2/readme.txt`).

**Consequence for scope:** the 1st-edition sigil `Spr.` (9,557 refs extracted here, lsextract
count 9,360) can only get a **range check** (is the verse number inside 1–5,419?) — never a
quote/headword text match, because there is no text to match against. Only the 2nd-edition sigil
`Spr. (II)` (6,320 refs extracted, lsextract count 7,309) gets full text-level verification. This
was not knowable before opening both repos; the roadmap's "cheapest full-text lane" framing holds
for `Spr. (II)` only.

## 2. Validation case — Spr. 2790 under `brū` does NOT resolve as described

The roadmap's own validation instruction: *"`Spr. 2790` = `tān havyakavyayor viprān anarhān manur
abravīt` (cited under `brū`, PWG); verify presence + reading at boesp2 verse 2790."*

Reading the actual `brū` entry ([`pwg.txt` L=53686](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwg/pwg.txt)),
the two citations are **separate, adjacent examples**, not one:

```
{#na cApriyaM prARizu yo bravIti#} <ls>Spr. 2790</ls>. — {#tāṃ havyakavyayor
viprān anarhān manur abravīt#} {%diese hat er für unwürdig erklärt%} <ls>M. 3,150</ls>.
```

The `tān havyakavyayor…` quote belongs to **`M. 3,150`** (Manu), not `Spr. 2790`. `Spr. 2790`'s
actual quoted pratīka is `na cApriyaM prāṇiṣu yo bravīti`. Also: the citation is tagged plain
`Spr.` (no `(II)`), so per the org's own siglum convention it addresses the **1st** edition —
boesp2 verse 2790 (`dikṣu bhūmau tathākāśe sarvatra ca vibhāvyate…`) is the wrong edition to check
in the first place, and (independently) its text does not match `na cāpriyaṃ prāṇiṣu yo bravīti`
either. Filed as a genuine census finding, not silently "resolved": **`Spr. 2790` verifies as
`range-only-unverifiable`** (edition I, no e-text available); the roadmap's validation-case prose
should be corrected at its source.

## 3. Method

- **Extraction (P1).** Parsed `<ls>Spr. N</ls>` / `<ls n="Spr.">N</ls>` / `<ls>Spr. (II) N</ls>`
  tags directly out of `csl-orig/v02/pwg/pwg.txt` (593,596 lines), keeping only tags whose full
  resolved siglum text is exactly `Spr.` or `Spr. (II)` — this excludes the two false-positive
  strings that also contain "Spr." (`Z. f. vgl. Spr.` = *Zeitschrift für vergleichende
  Sprachwissenschaft*, and the botanical author abbreviation in `Croton polyandrum Spr.`).
  15,877 refs extracted (9,557 ed. I + 6,320 ed. II) against lsextract's raw siglum-frequency
  count of 9,360 + 7,309 = 16,669 — **~95% recall**; the gap is mainly bare `<ls>Spr.</ls>`
  bibliography mentions with no attached number (correctly excluded) and a residual of
  continuation-tag edge cases not yet chased down.
- **Quoted-pratīka capture.** For each `<ls>` tag, the nearest preceding `{#…#}` SLP1 span is
  taken as the quote **only if no other `<ls>` tag intervenes** (dense entries stack many
  citations back-to-back — see the `brū` example above — so a naive "150 chars back" window
  attaches the wrong quote to the wrong citation; this was caught and fixed mid-run, see
  [`extract_spr_refs.py`](https://github.com/gasyoun/Uprava/tree/main/scratchpad) provenance
  below) and only if the gap is ≤220 chars.
- **boesp2 text.** All 79 `web1/json/section*.json` files fetched (12 MB, 9,284 verse entries,
  integer-keyed range 1–7,878), Devanagari `sdeva` spans extracted and transliterated to SLP1
  via `indic_transliteration` (same convention PWG's own SLP1 uses, verified byte-for-byte
  compatible on spot checks).
- **Matching tiers** (R3 schema `evidence_tier`): `quote-exact` (full quote is a literal substring
  of the verse) → `quote-fuzzy` (case/vowel-length-folded substring, or ≥0.5 word-level Jaccard —
  covers the very common case where PWG cites a compound in dictionary/stem form while the verse
  has it sandhi-inflected) → `lemma` (a ≥6-char folded prefix of any quote word matches inside the
  verse — covers single-word compound-fragment citations like `˚raśmi` or `vidyārthin`) → `none`.
- **Don'ts honored.** No OCR attempted (boesp1 has nothing to OCR *from* without leaving this
  mission's scope; flagged as a gap, not worked around). No `csl-orig` edits. `Spr.` inventory
  taken as authoritative from `lsextract_pwg_06.txt`, not rebuilt.

## 4. Results

| Edition | Refs | Verdict | Count | Share |
|---|--:|---|--:|--:|
| I (`Spr.`) | 9,557 | `range-only-unverifiable` | 9,545 | 99.9% |
| I (`Spr.`) | 9,557 | `out-of-range` (verse # > 5,419) | 12 | 0.1% |
| II (`Spr. (II)`) | 6,320 | `corroborated` | 2,621 | 41.5% |
| II (`Spr. (II)`) | 6,320 | `mismatch` | 443 | 7.0% |
| II (`Spr. (II)`) | 6,320 | `unverified-no-quote` (no adjacent quote captured) | 3,255 | 51.5% |
| II (`Spr. (II)`) | 6,320 | `out-of-range` (verse # > 7,878) | 1 | 0.0% |

**Corroborated-tier breakdown (2,621 total):** `quote-exact` 1,332 · `quote-fuzzy` 771 · `lemma` 518.

**`unverified-no-quote` (3,255, 51.5% of ed. II) is the largest bucket** — most `Spr. (II)` refs
in `pwg.txt` are bare page/reference citations with no Sanskrit pratīka quoted alongside them
(PWG frequently cites `Spr.` purely to attest a sense, e.g. after a German gloss with no `{#…#}`
span at all). These are **verse-existence-confirmed** (the number resolves inside boesp2's range)
but carry no text-level evidence either way — a distinct, weaker-but-not-negative bucket from
`mismatch`. Don't conflate the two: `mismatch` means we have a quote and it does NOT match;
`unverified-no-quote` means we never had anything to check.

**Cascade tier (roadmap §5):** every `Spr. (II)` verdict lands at *curated edition e-texts*
(the boesp2 digitization) — the mission's own Don'ts rule out consulting DCS/GRETIL for a text
neither corpus contains. Every `Spr.` (ed. I) row is `unresolved` at this tier — the next tier
that could resolve it is `boesp1`'s own PDF scans (`boesp1/pdfpages/*.pdf`), which is out of
scope here (no OCR) and is the natural W1b follow-up if 1st-edition verification is wanted.

## 5. Edition-siglum-error candidates (P3 cross-edition probe)

For every plain `Spr. N` (ed. I) ref that carries a captured quote, checked whether boesp2's own
verse **at the same number N** (2nd-edition numbering) contains matching text — i.e., whether the
citation might actually belong to the 2nd edition but was tagged without `(II)`. **38 candidates**
found (24 `yes-exact`, 14 `yes-fuzzy`) — see `edition_swap_candidate` column in the CSV. This is a
coincidence check, not a confirmed error: both editions cover overlapping low-to-mid verse-number
ranges, so *some* overlap is expected by chance at this rate (38 / 9,557 ≈ 0.4%). Flagged for a
human read-through, not asserted as citation errors — none routed to
`/cologne-correction-queue` (per Don'ts: apparatus/annotation-layer mismatches are not
digitization typos).

## 6. What this does NOT establish

- **No verdict on whether a `mismatch` is Böhtlingk's error, a PWG transcription slip, or this
  pipeline's matching noise.** 443 `mismatch` rows (7.0% of ed. II) need a human pass before any
  is treated as a real citation defect; spot-checks during this run found several early
  "mismatches" were actually matching-algorithm gaps (fixed iteratively — see §3) rather than
  real defects, so the residual 443 should be read as "flagged for review," not "confirmed wrong."
- **1st-edition (`Spr.`) citations remain entirely unverified at the text level** — 9,545 of them.
  This is the single largest open item from this wave.
- **No PW/PWK `Spr.` sigla extension attempted** (handoff's "extend if trivially parallel, else
  queue as follow-up" — queued, not done: `pw/pwbib.txt` was not read this pass).

## 7. Follow-ups

1. **W1b-2 (queued, not this pass):** PW/PWK `Spr.` siglum extraction, using this pipeline as a
   template.
2. **1st-edition resolution path:** OCR `boesp1/pdfpages/*.pdf` (5,419 verses, 3 volumes) or
   locate an existing typed transcription elsewhere before attempting further ed.-I verification —
   without one, ed. I stays permanently at `range-only-unverifiable`.
3. **Human review queue:** the 443 `mismatch` + 38 `edition_swap_candidate` rows are the
   highest-value review targets; consider a `/review-sheet` pass before the roadmap treats any of
   them as citation-quality signal.
4. Roadmap §4 W1b marked done for the `Spr. (II)` lane below; §2 validation-case prose needs a
   correction per §2 above.

## Provenance

Extracted 11-07-2026 by Sonnet 5 (`claude-sonnet-5`) from
[`csl-orig/v02/pwg/pwg.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwg/pwg.txt) +
[`literarysource/pwg/lsextract_pwg_06.txt`](https://github.com/sanskrit-lexicon/literarysource/blob/main/pwg/lsextract_pwg_06.txt) +
[`sanskrit-lexicon-scans/boesp2`](https://github.com/sanskrit-lexicon-scans/boesp2) `web1/json/*`.
Minted under [H602](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H602-Fable_csl-atlas_citation-verification-roadmap_11.07.26.md),
Wave 1b of [H611](https://github.com/gasyoun/Uprava/blob/main/handoffs/H611-Sonnet_csl-atlas_spruche_citation_verify_11.07.26.md).

_Dr. Mārcis Gasūns_
