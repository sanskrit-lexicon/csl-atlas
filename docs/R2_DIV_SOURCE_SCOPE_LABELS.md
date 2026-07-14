# R2 Div Source Scope Label Proposals

Date: 2026-06-06

Status: source-inspected proposal layer for the `div-source-scope` R2 parser
packet. These labels are not scholar-reviewed decisions and must not be treated
as `reviewedValue`.

## Trust Block

- Claim: the `div-source-scope` rows can be split into concrete source-record
  scope classes before any parser rule is promoted.
- Evidence label: `derived`.
- Source files: `data/lexico/r2_review_packets.json`,
  `data/lexico/r2_source_anchor_senses.jsonl`, and local `csl-orig` source
  records under `../csl-orig/v02/pwg/pwg.txt` and `../csl-orig/v02/pw/pw.txt`.
- Validation target: `git diff --check`, `npm test`,
  `npm run validate-review-reports`, `npm run build`.
- Review status: `machine-proposed`.
- Owner repo: `csl-atlas`.
- Boundary note: dictionary source records only; no DCS, corpus frequency,
  TEI/OntoLex, FrAC, backend, database, GitHub/org-process evidence, runtime
  LLM classification, or cross-repo content join.

## Proposed Label Vocabulary

| Label | Meaning | Parser consequence |
|---|---|---|
| `target-primary-series` | Main source record for the requested lookup/homonym. | Candidate for R2 sense splitting after marker-depth rules are reviewed. |
| `same-headword-supplement` | Later addendum or continuation keyed to the same headword/homonym. | Keep as evidence, but do not merge into the main count until a supplement-folding rule is approved. |
| `separate-homonym` | Explicit homonym or distinct raw headword caught by the lookup bundle. | Track separately; do not count as the target series. |
| `prefixed-or-derived-series` | Prefixed verbs, participles, compounds, or derivative subseries under a root/headword. | Keep nested or lower-confidence unless the target is explicitly that subseries. |
| `cross-reference-only` | `Vgl.`/comparison or see-also material without an independent sense series. | Preserve as source evidence; no default sense-count contribution. |
| `source-expansion-control` | Source-backed PW/PWK row with no archived R2 baseline. | Useful for parser design, but not archive parity evidence. |
| `lookup-bundle-split` | The anchor lookup deliberately includes multiple historical spellings or raw headwords. | Split by raw headword/homonym before comparing row counts. |

## Source-Record Proposals

### `gam`

| Diagnostic | Source record | Inspected cue | Proposed label | Parser consequence |
|---|---|---|---|---|
| `r2-drift:gam:pwg` | [`pwg.txt#L203360`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt#L203360), `L=21814`, `<h>1` | Full verbal root record begins with form inventory and main motion senses. | `target-primary-series` | Use as the main `gam` PWG record; split marker depth before count comparison. |
| `r2-drift:gam:pwg` | [`pwg.txt#L671452`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt#L671452), `L=72578`, `<h>1` | Later record resumes numbered senses and then has `gata`, causative, and prefixed sections. | `same-headword-supplement` plus `prefixed-or-derived-series` for `p` sections | Keep as addendum evidence; do not blindly concatenate with `L=21814`. |
| `r2-drift:gam:pwg` | [`pwg.txt#L1112351`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt#L1112351), `L=119742`, `<h>1` | Late addendum starts with `vyati`, `A`, causative, `upA`, `ni`, `vini`, `vinis`, `sam`. | `same-headword-supplement` plus `prefixed-or-derived-series` | Treat as supplement/prefix evidence, not a new primary sense count. |
| `r2-drift:gam:pwg` | [`pwg.txt#L205058`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt#L205058), `L=21815`, `<h>2` | Explicit `2. gam = kzam`, earth sense, only in `gmas`. | `separate-homonym` | Exclude from the motion-root target series; preserve as a distinct homonym. |
| `r2-drift:gam:pw` | [`pw.txt#L138769`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pw/pw.txt#L138769), `L=34676` | Main PW/PWK verbal root record with root mark and numbered motion senses. | `target-primary-series` and `source-expansion-control` | Use for parser design; no archived baseline exists for parity. |
| `r2-drift:gam:pw` | [`pw.txt#L582766`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pw/pw.txt#L582766), `L=204564` | `mit aByud` supplement with one prefixed example. | `same-headword-supplement` plus `prefixed-or-derived-series` | Keep outside the primary count unless supplement folding is approved. |
| `r2-drift:gam:pw` | [`pw.txt#L590772`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pw/pw.txt#L590772), `L=207157` | `mit aBi Caus.` and `mit nis Caus.` supplement. | `same-headword-supplement` plus `prefixed-or-derived-series` | Keep as prefixed/causative addendum evidence. |
| `r2-drift:gam:pw` | [`pw.txt#L623691`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pw/pw.txt#L623691), `L=216783` | Addendum references `aBi`, `A`, `aByud`, `nis`, `upanis`. | `same-headword-supplement` plus `prefixed-or-derived-series` | Preserve as source evidence; do not merge into baseline counts by default. |

### `rama`

The anchor intentionally searches both `rAma` and `rama`. Source counts must be
split by raw headword before any archived comparison.

| Diagnostic | Source record | Inspected cue | Proposed label | Parser consequence |
|---|---|---|---|---|
| `r2-drift:rama:pwg` | [`pwg.txt#L754855`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt#L754855), `L=83557`, raw `rama` | Short-vowel `rama`, from `ram`, with adjective, lover, Kama, Lakshmi, and related senses. | `target-primary-series` within `lookup-bundle-split` | Candidate target if the anchor intends short `rama`; keep separate from `rAma`. |
| `r2-drift:rama:pwg` | [`pwg.txt#L762846`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt#L762846), `L=84468`, raw `rAma`, `<h>1` | Long-vowel `rAma`, dark/black sense and proper-name complex. | `separate-homonym` within `lookup-bundle-split` | Do not mix with short `rama`; compare only if the reviewed target is `rAma`. |
| `r2-drift:rama:pwg` | [`pwg.txt#L762935`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt#L762935), `L=84469`, raw `rAma`, `<h>2` | Long-vowel `rAma`, from `ram`, pleasure/pleasant/lover/feminine subseries. | `separate-homonym` within `lookup-bundle-split` | Track separately from both short `rama` and `rAma` `<h>1`. |
| `r2-drift:rama:pw` | [`pw.txt#L384342`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pw/pw.txt#L384342), `L=92728`, raw `rama` | Short-vowel `rama`, adjective and nominal/feminine derived senses. | `target-primary-series` and `source-expansion-control` | Candidate target for short `rama`; no archived PW/PWK baseline. |
| `r2-drift:rama:pw` | [`pw.txt#L388952`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pw/pw.txt#L388952), `L=93849`, raw `rAma` | Long-vowel `rAma`, black/pleasant/proper-name/feminine plant senses. | `separate-homonym` within `lookup-bundle-split` | Keep separate unless the target anchor is switched to `rAma`. |

### `dharma`

| Diagnostic | Source record | Inspected cue | Proposed label | Parser consequence |
|---|---|---|---|---|
| `r2-drift:dharma:pwg` | [`pwg.txt#L350536`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt#L350536), `L=36241` | Main `Darma` entry with law, duty, virtue, and numbered sense hierarchy. | `target-primary-series` | Candidate primary PWG source record. |
| `r2-drift:dharma:pwg` | [`pwg.txt#L696945`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt#L696945), `L=76490` | Addendum begins with textual corrections and added examples, then appends numbered items. | `same-headword-supplement` | Keep as supplement evidence; fold only under an approved addendum rule. |
| `r2-drift:dharma:pw` | [`pw.txt#L224195`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pw/pw.txt#L224195), `L=54669` | Main `Darma` record with law, duty, nature, ceremony, and proper-name senses. | `target-primary-series` and `source-expansion-control` | Use for PW/PWK parser design; no archived baseline. |
| `r2-drift:dharma:pw` | [`pw.txt#L629601`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pw/pw.txt#L629601), `L=218446` | Late addendum `Darma III. 11` equals bow. | `same-headword-supplement` | Preserve as an addendum to a numbered sense, not a new primary series. |

### `iti`

| Diagnostic | Source record | Inspected cue | Proposed label | Parser consequence |
|---|---|---|---|---|
| `r2-drift:iti:pwg` | [`pwg.txt#L88592`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt#L88592), `L=10029`, `<h>1` | Main adverbial `iti`, deictic/quotative usage with extensive examples. | `target-primary-series` | Candidate primary PWG record for the quotative particle. |
| `r2-drift:iti:pwg` | [`pwg.txt#L635842`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt#L635842), `L=67185`, `<h>1` | Later examples where `iti` is metrically displaced; also `iti hovAca`. | `same-headword-supplement` | Addendum/examples for `<h>1`; keep outside primary counts by default. |
| `r2-drift:iti:pwg` | [`pwg.txt#L88758`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt#L88758), `L=10030`, `<h>2` | `iti` from `i`, feminine "going/moving". | `separate-homonym` | Exclude from quotative-particle target series. |
| `r2-drift:iti:pwg` | [`pwg.txt#L635858`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt#L635858), `L=67186`, `<h>2` | Later h2 note and `Vgl. duriti`. | `same-headword-supplement` plus `cross-reference-only` | Keep with h2 supplement material; no h1 sense-count contribution. |
| `r2-drift:iti:pw` | [`pw.txt#L64269`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pw/pw.txt#L64269), `L=16765`, `<h>1` | Main quotative/deictic adverb. | `target-primary-series` and `source-expansion-control` | Candidate primary PW/PWK record; no archived baseline. |
| `r2-drift:iti:pw` | [`pw.txt#L64272`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pw/pw.txt#L64272), `L=16766`, `<h>2` | Feminine "going, moving" and following after something. | `separate-homonym` | Exclude from quotative-particle target series. |
| `r2-drift:iti:pw` | [`pw.txt#L64277`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pw/pw.txt#L64277), `L=16767`, `<h>3` | Masculine proper name. | `separate-homonym` | Exclude from quotative-particle target series. |
| `r2-drift:iti:pw` | [`pw.txt#L595394`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pw/pw.txt#L595394), `L=208656`, `<h>1` | Later `iti ceti ca` note. | `same-headword-supplement` | Addendum to h1. |
| `r2-drift:iti:pw` | [`pw.txt#L615828`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pw/pw.txt#L615828), `L=214522`, `<h>1` | Later h1 references and `iti - iti` formula. | `same-headword-supplement` | Addendum to h1. |
| `r2-drift:iti:pw` | [`pw.txt#L615831`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pw/pw.txt#L615831), `L=214523`, `<h>2` | Later h2 "Gang" note. | `same-headword-supplement` plus `separate-homonym` | Keep with h2; no h1 count contribution. |

### `bodhisattva`

| Diagnostic | Source record | Inspected cue | Proposed label | Parser consequence |
|---|---|---|---|---|
| `r2-drift:bodhisattva:pw` | [`pw.txt#L320159`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pw/pw.txt#L320159), `L=77744` | Single PW/PWK entry defining the Buddhist term and abstract noun. | `target-primary-series` and `source-expansion-control` | Useful positive source row; no archived PW/PWK baseline. |
| `r2-drift:bodhisattva:pwg` | [`pwg.txt#L515286`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt#L515286), `L=53245` | Main PWG Buddhist term entry; final `Vgl. deva-` is comparison material. | `target-primary-series` plus `cross-reference-only` for `v` | Use as positive control; exclude comparison row from count unless reviewed. |
| `r2-drift:bodhisattva:pwg` | [`pwg.txt#L719134`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt#L719134), `L=79997` | Later compound/abstract-noun examples: `-sattvAMSa`, `-sattvatA`. | `same-headword-supplement` plus `prefixed-or-derived-series` | Preserve as derivative addendum, not the primary two-row archived comparison. |

## Marker-Class Starting Labels

These labels explain why raw `div` counts overrun the archived rows.

| Marker class | Source cue | Proposed label | Parser consequence |
|---|---|---|---|
| `1`, `2`, `3` in a `target-primary-series` record | Explicit nested semantic numbering. | `candidate-sense-marker` | Count only after depth and parent/child rules are chosen. |
| `1`, `2`, `3` in a `same-headword-supplement` record | Addendum continues or corrects earlier numbering. | `supplement-marker` | Keep outside target count until supplement folding is reviewed. |
| `p` | PWG/PW sections for participles, preverbs, causatives, or prefix groups. | `prefixed-or-derived-series` | Do not count as base-sense rows by default. |
| `m` | PW/PWK root record marker associated with modal/grammatical subseries in `gam`. | `prefixed-or-derived-series` | Keep nested until a grammar-subseries rule is reviewed. |
| `o` | PW/PWK residual/other marker in `gam`. | `supplement-marker` | Treat as lower-confidence until examples are source-read. |
| `v` | `Vgl.` comparison rows. | `cross-reference-only` | Preserve evidence, but do not count as an independent sense by default. |

## First Parser Rule To Test

For the first non-final R2 rebuild experiment, test this conservative rule:

1. Select one `target-primary-series` source record per dictionary/lemma/raw
   headword.
2. Keep `separate-homonym` records in separate output groups.
3. Keep `same-headword-supplement`, `prefixed-or-derived-series`, and
   `cross-reference-only` rows in retained side tables.
4. Count candidate senses only from explicit numbered markers in the selected
   primary record, and report depth separately instead of flattening all nested
   `div` markers.

This should reduce false inflation without discarding source evidence.
