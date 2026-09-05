_Created: 06-06-2026 · Last updated: 05-09-2026_

# R2 Marker Run Scope Label Proposals

Date: 2026-06-06

Status: source-inspected proposal layer for the `marker-run-scope` R2 parser
packet. These labels are not scholar-reviewed sense decisions and must not be
treated as `reviewedValue`.

## Trust Block

- Claim: marker-run diagnostics can be given concrete parser-scope labels by
  inspecting source records, explicit marker runs, and archive-count matches.
- Evidence label: `derived`.
- Source files: `data/lexico/r2_review_packets.json`,
  `data/lexico/r2_parser_diagnostics.json`,
  `data/lexico/r2_source_anchor_senses.jsonl`, and local `csl-orig` records
  for BEN, WIL, AP, AP90, BHS, MW72, CAE, and SCH.
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
| `archive-prefix-runs` | The archived count equals the first one or more explicit marker runs. | Candidate main parser window; later rows stay in retained side tables. |
| `reset-run-expansion` | Later numeric marker sequences restart after a completed run. | Preserve as derived/later expansion until dictionary-specific rules are reviewed. |
| `preface-proxy-extra` | A source-backed row carries headword/POS/header text, not an explicit sense marker. | Exclude from sense counts by default unless a reviewed dictionary rule keeps it. |
| `lookup-bundle-split` | The anchor lookup aggregates raw headwords such as `rama` and `rAma`. | Split by raw headword or homonym before marker-run comparison. |
| `source-record-exact-target` | One source record's row count equals the archive count. | Candidate target record, not proof that sibling records are irrelevant. |
| `single-run-parity-control` | One explicit marker run matches the archive after dropping the preface row. | Positive parser control, not a blocking decision. |
| `preface-retained-control` | The exact archive/source count includes a preface/header proxy. | Low-priority review cue; decide whether the header carries content. |
| `lumped-parity-control` | Source and archive both have one unsplit row. | Useful coverage control, not evidence for marker-run logic. |
| `no-anchor-control` | Neither source-backed nor archived row exists. | Keep as a control; no parser decision now. |

## Source-Inspected Proposals

### High-Priority Rows

| Diagnostic | Source cue | Proposed labels | Parser consequence |
|---|---|---|---|
| `r2-drift:gam:ben` | [`ben.txt#L29576`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ben/ben.txt#L29576), `L=4326`; runs 0-1 have 9 + 14 rows = archived 23. Later reset runs include examples beginning "Gone", "Accessible", causative, prefixed, and other derived subseries. | `archive-prefix-runs`, `reset-run-expansion` | Use runs 0-1 as the first candidate BEN `gam` window; retain runs 2+ as source evidence, not deleted rows. |
| `r2-drift:rama:ben` | [`ben.txt#L87379`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ben/ben.txt#L87379), raw `rama`, has exactly 7 rows, matching the archive. [`ben.txt#L88260`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ben/ben.txt#L88260), raw `rAma`, adds 8 rows. | `source-record-exact-target`, `lookup-bundle-split` | Treat short `rama` as the archive target candidate; keep long `rAma` separate unless the reviewed target is changed. |

### Medium-Priority Rows

| Diagnostic | Source cue | Proposed labels | Parser consequence |
|---|---|---|---|
| `r2-drift:rama:wil` | [`wil.txt#L249272`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/wil/wil.txt#L249272), short `rama`, plus [`wil.txt#L251860`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/wil/wil.txt#L251860), long `rAma`; runs 0-1 total 12 and match the archive. [`wil.txt#L249261`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/wil/wil.txt#L249261) is a verbal-root bundle. | `archive-prefix-runs`, `lookup-bundle-split`, `preface-proxy-extra` | Split root/short/long records before comparison; runs 0-1 are a candidate archive window, later long-`rAma` runs stay retained. |
| `r2-drift:rama:ap90` | [`ap90.txt#L209370`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ap90/ap90.txt#L209370), short `rama`, and [`ap90.txt#L210666`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ap90/ap90.txt#L210666), long `rAma`; no clean prefix match, but the overrun follows the same lookup-bundle pattern. | `lookup-bundle-split`, `reset-run-expansion` | Do not promote a count rule yet; first split raw headwords, then review which `rAma` runs belong to the target. |
| `r2-drift:dharma:bhs` | BHS has separate records: [`bhs.txt#L30930`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/bhs/bhs.txt#L30930) proper-name `Dharma`, [`bhs.txt#L30934`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/bhs/bhs.txt#L30934) semantic `dharma`, [`bhs.txt#L30938`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/bhs/bhs.txt#L30938) adjective, and [`bhs.txt#L31478`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/bhs/bhs.txt#L31478) verse form `DharmaH`. | `lookup-bundle-split`, `preface-proxy-extra` | This is record-scope more than marker-run scope; keep BHS rows split by record family before count comparison. |

### Prefix And Single-Run Controls

| Diagnostic | Source cue | Proposed labels | Parser consequence |
|---|---|---|---|
| `r2-drift:bodhisattva:ap` | [`ap.txt#L325199`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ap/ap.txt#L325199) has two explicit bullet senses plus a headword proxy. | `single-run-parity-control`, `preface-proxy-extra` | Archive count matches the two explicit senses; drop the preface proxy for sense count. |
| `r2-drift:dharma:ap` | [`ap.txt#L232784`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ap/ap.txt#L232784) has one run of 23 bullet senses plus a preface row. | `single-run-parity-control`, `preface-proxy-extra` | Positive AP control: explicit bullets match archive. |
| `r2-drift:dharma:ap90` | [`ap90.txt#L137647`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ap90/ap90.txt#L137647) has one run of 22 numbered senses plus a preface row. | `single-run-parity-control`, `preface-proxy-extra` | Positive AP90 control: explicit markers match archive. |
| `r2-drift:dharma:ben` | [`ben.txt#L49805`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ben/ben.txt#L49805) has one run of 11 numbered senses plus a preface row. | `single-run-parity-control`, `preface-proxy-extra` | Positive BEN noun control. |
| `r2-drift:dharma:wil` | [`wil.txt#L158204`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/wil/wil.txt#L158204) has runs 0-1 totaling 20 and one preface row. | `archive-prefix-runs`, `preface-proxy-extra` | Treat the first two Wilson dot-squared runs as the archive window; keep later material retained. |
| `r2-drift:gam:ap90` | [`ap90.txt#L105357`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ap90/ap90.txt#L105357) has runs 0-1 totaling 14 plus a preface row. | `archive-prefix-runs`, `reset-run-expansion`, `preface-proxy-extra` | Candidate AP90 `gam` rule: count prefix runs, retain later causative/send/bring material. |
| `r2-drift:iti:ben` | [`ben.txt#L11919`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ben/ben.txt#L11919) has five explicit uses plus a preface row. | `single-run-parity-control`, `preface-proxy-extra` | Archive count matches explicit uses. |
| `r2-drift:iti:wil` | [`wil.txt#L48403`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/wil/wil.txt#L48403) has nine explicit particle meanings plus a preface row. | `single-run-parity-control`, `preface-proxy-extra` | Archive count matches explicit meanings. |
| `r2-drift:iti:ap90` | [`ap90.txt#L64140`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ap90/ap90.txt#L64140) has a short header plus two explicit spans and exactly matches the archive. | `preface-retained-control` | Low-priority cue: decide whether AP90 `iti` keeps the header as a content-bearing general use row. |

### Lumped And No-Anchor Controls

| Diagnostics | Source cue | Proposed labels | Parser consequence |
|---|---|---|---|
| `r2-drift:rama:mw72` | [`mw72.txt#L311802`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw72/mw72.txt#L311802) short `rama` and [`mw72.txt#L314666`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw72/mw72.txt#L314666) long `rAma`, both lumped proxies. | `lookup-bundle-split`, `lumped-parity-control` | Split raw headwords; do not infer marker-run logic from MW72. |
| `r2-drift:bodhisattva:bhs`, `r2-drift:bodhisattva:cae`, `r2-drift:bodhisattva:wil`, `r2-drift:dharma:cae`, `r2-drift:dharma:sch`, `r2-drift:gam:cae`, `r2-drift:gam:sch`, `r2-drift:rama:bhs` | Each has one source-backed row and one archived row, with no explicit marker series. | `lumped-parity-control` | Keep as coverage controls only. |
| `r2-drift:bodhisattva:ap90`, `r2-drift:bodhisattva:ben`, `r2-drift:gam:bhs`, `r2-drift:gam:wil`, `r2-drift:iti:bhs` | No source-backed row and no archived row in this anchor prototype. | `no-anchor-control` | No parser promotion; revisit only after headword coverage broadens. |

## First Parser Rule To Test

For the next non-final R2 rebuild experiment:

1. Emit `preface-proxy-extra` rows separately from explicit marker rows.
2. Split lookup bundles by raw headword before comparing marker counts.
3. For rows with `archive-prefix-runs`, count only the matched prefix as the
   candidate main window and retain later reset runs with `reset-run-expansion`.
4. Treat `single-run-parity-control` rows as positive controls for preface
   exclusion.
5. Do not use `lumped-parity-control` or `no-anchor-control` rows to define
   marker-run behavior.

This should explain BEN/AP90/WIL archive parity without silently discarding
later runs, sibling raw headwords, or source-only rows.

_Dr. Mārcis Gasūns_
