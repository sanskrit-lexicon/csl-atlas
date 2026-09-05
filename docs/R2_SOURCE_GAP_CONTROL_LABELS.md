_Created: 06-06-2026 · Last updated: 05-09-2026_

# R2 Source Gap Control Label Proposals

Date: 2026-06-06

Status: source-inspected proposal layer for the `source-gap-controls` R2 parser
packet. These labels are not scholar-reviewed sense or alignment decisions and
must not be treated as `reviewedValue`.

## Trust Block

- Claim: source gaps, mild drift rows, source-only rows, and parity rows can be
  labeled as parser controls before they are used to judge future R2 rebuilds.
- Evidence label: `derived`.
- Source files: `data/lexico/r2_review_packets.json`,
  `data/lexico/r2_parser_diagnostics.json`,
  `data/lexico/r2_source_anchor_senses.jsonl`, and local `csl-orig` records
  for MW, MW72, AP, CAE, and SCH controls.
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
| `mild-drift-follow-up` | Drift is visible but lower-risk than the high-priority parser families. | Queue after promoted parser rules; do not block the current R2 slice. |
| `under-split-marker-gap` | Source rows are fewer than archived rows because marker coverage is coarser than the archived fixture. | Review nested marker coverage and lookup variants after high-risk packets. |
| `nested-marker-gap` | Source text contains submarkers or subpoints not yet split as separate rows. | Preserve as a targeted parser follow-up, not a source absence claim. |
| `preface-proxy-extra` | A source-backed row carries headword/POS/header text rather than an explicit sense marker. | Exclude from default sense counts unless a reviewed rule keeps it. |
| `lookup-bundle-split` | The lookup includes multiple raw headwords or homonyms. | Split raw headword/homonym records before count comparison. |
| `archive-parity-control` | Source and archive counts match, or are close enough to be a positive parser control. | Use as a regression check while changing higher-risk parser rules. |
| `homonym-record-control` | Parity depends on preserving separate homonym/source records. | Do not collapse homonyms just to satisfy row-count checks. |
| `continuation-proxy-row` | A source row points at a continuation or body proxy rather than an independent sense. | Preserve as a parser artifact; inspect before counting. |
| `source-only-expansion` | Source-backed row exists where the archived fixture has no baseline. | Keep as rebuild expansion evidence; no archive regression implied. |
| `no-anchor-control` | No source-backed row and no archived row exist for the anchor pair. | Keep as a coverage control; revisit only when lookup coverage broadens. |

## Source-Inspected Proposals

### Medium Follow-Up Rows

| Diagnostic | Source cue | Proposed labels | Parser consequence |
|---|---|---|---|
| `r2-drift:rama:mw` | MW contributes 23 one-row source blocks against 17 archived rows. Early short-`rama` examples include [`mw.txt#L584533`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw/mw.txt#L584533), `L=175086`, "pleasing, delighting", and [`mw.txt#L584539`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw/mw.txt#L584539), `L=175088`, joy. The packet also includes long-`rAma` source rows beginning [`mw.txt#L591557`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw/mw.txt#L591557). | `mild-drift-follow-up`, `lookup-bundle-split`, `homonym-record-control` | Split short `rama` and long `rAma` before deciding whether the six-row excess is a parser issue or target-definition issue. |
| `r2-drift:iti:ap` | [`ap.txt#L92701`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ap/ap.txt#L92701), `L=8130`, has a preface row and two top-level markers. Marker 2 contains nested subpoints such as cause, manifestation, addition, conclusion, reference, and other functions. | `under-split-marker-gap`, `nested-marker-gap`, `preface-proxy-extra` | Do not mark AP `iti` as source-missing. The follow-up is nested marker coverage inside marker 2. |
| `r2-drift:rama:ap` | [`ap.txt#L376348`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ap/ap.txt#L376348), `L=27296`, short `rama`, has preface plus two explicit markers. [`ap.txt#L379737`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ap/ap.txt#L379737), `L=27427`, long `rAma`, contributes five rows. Source rows total 8 against 10 archived rows. | `under-split-marker-gap`, `lookup-bundle-split`, `preface-proxy-extra` | Split raw headwords first, then inspect whether AP submarkers or archive scope explain the two-row deficit. |

### Parity And Source-Only Controls

| Diagnostic | Source cue | Proposed labels | Parser consequence |
|---|---|---|---|
| `r2-drift:dharma:mw` | MW `Darma` rows begin at [`mw.txt#L334919`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw/mw.txt#L334919), `L=99903`, law/statute, and continue through many one-row lumped proxies. Source has 33 rows against 30 archived rows. | `archive-parity-control`, `homonym-record-control` | Treat as near-parity regression control, not proof that every MW source proxy is a reviewed sense. |
| `r2-drift:bodhisattva:mw` | [`mw.txt#L488992`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw/mw.txt#L488992), `L=145897`, term definition; [`mw.txt#L488995`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw/mw.txt#L488995), principal Buddha; [`mw.txt#L488998`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw/mw.txt#L488998), poet. Source and archive both have 3 rows. | `archive-parity-control`, `homonym-record-control` | Positive MW parity control for a compact term/proper-name cluster. |
| `r2-drift:dharma:mw72` | MW72 has three one-row records: [`mw72.txt#L174006`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw72/mw72.txt#L174006), main `dharma`; [`mw72.txt#L174521`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw72/mw72.txt#L174521), denominative verb; [`mw72.txt#L174615`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw72/mw72.txt#L174615), see-reference. | `archive-parity-control`, `homonym-record-control`, `continuation-proxy-row` | Use as MW72 record-scope parity control; do not fold see-reference rows into semantic counts without review. |
| `r2-drift:gam:ap` | AP exact parity: source and archive both have 16 rows. [`ap.txt#L165154`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ap/ap.txt#L165154), `L=13731.006`, is a body proxy; [`ap.txt#L167512`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ap/ap.txt#L167512), `L=13831`, carries explicit marker runs. | `archive-parity-control`, `continuation-proxy-row`, `nested-marker-gap` | Positive AP `gam` regression control; keep the body proxy visible while changing marker-run logic. |
| `r2-drift:gam:mw`, `r2-drift:gam:mw72` | MW has main Vedic `gam`, etymology, and `2. gam = gmas` records at [`mw.txt#L215707`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw/mw.txt#L215707), [`mw.txt#L215756`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw/mw.txt#L215756), and [`mw.txt#L216557`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw/mw.txt#L216557). MW72 has corresponding `gam` h1/h2 records at [`mw72.txt#L116404`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw72/mw72.txt#L116404) and [`mw72.txt#L116665`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw72/mw72.txt#L116665). | `archive-parity-control`, `homonym-record-control` | Positive root/homonym controls; preserve h1/h2 separation. |
| `r2-drift:iti:cae`, `r2-drift:iti:mw`, `r2-drift:iti:mw72` | CAE has three `iti` records at [`cae.txt#L16108`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/cae/cae.txt#L16108), [`cae.txt#L16117`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/cae/cae.txt#L16117), and [`cae.txt#L16120`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/cae/cae.txt#L16120). MW/MW72 likewise keep feminine "going" rows separate from the adverbial particle rows. | `archive-parity-control`, `homonym-record-control` | Positive `iti` homonym controls; parity depends on preserving feminine noun and adverbial particle records separately. |
| `r2-drift:rama:cae` | [`cae.txt#L90073`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/cae/cae.txt#L90073), `L=26601`, short `rama`, is source-backed but has no archived baseline in this fixture. | `source-only-expansion` | Preserve as rebuild expansion evidence; no archive regression or absence claim. |

### No-Anchor Controls

| Diagnostics | Source cue | Proposed labels | Parser consequence |
|---|---|---|---|
| `r2-drift:bodhisattva:mw72`, `r2-drift:bodhisattva:sch`, `r2-drift:iti:sch`, `r2-drift:rama:sch` | The current anchor prototype has no source-backed row and no archived row for these dictionary/lemma pairs. | `no-anchor-control` | Keep apart from source-only expansion and under-split rows; revisit only after lookup coverage broadens. |

## First Parser Rule To Test

For the next non-final R2 rebuild experiment:

1. Use `archive-parity-control` rows as regression checks while changing
   `div`, marker-run, AE, or indigenous parser logic.
2. Route `mild-drift-follow-up`, `under-split-marker-gap`, and
   `nested-marker-gap` to later review queues instead of treating them as
   current blockers.
3. Preserve `lookup-bundle-split`, `homonym-record-control`, and
   `continuation-proxy-row` metadata so parity rows do not hide record-scope
   assumptions.
4. Keep `source-only-expansion` rows as source-backed future coverage, not as
   failed archived parity.
5. Keep `no-anchor-control` rows separate from both source-only and source-gap
   rows.

This gives the R2 rebuild a control layer: rows that should remain stable while
the higher-risk parser decisions change, and rows that should wait for later
coverage or nested-marker review.

_Dr. Mārcis Gasūns_
