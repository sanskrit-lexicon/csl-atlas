_Created: 06-06-2026 · Last updated: 05-09-2026_

# R2 Indigenous Iti Authority Label Proposals

Date: 2026-06-06

Status: source-inspected proposal layer for the `indigenous-iti-authority` R2
parser packet. These labels are not scholar-reviewed sense, citation, or
authority decisions and must not be treated as `reviewedValue`.

## Trust Block

- Claim: SKD/VCP `iti-unit` diagnostics can be separated into source-role
  classes before indigenous prose rows are used as sense or authority evidence.
- Evidence label: `derived`.
- Source files: `data/lexico/r2_review_packets.json`,
  `data/lexico/r2_parser_diagnostics.json`,
  `data/lexico/r2_source_anchor_senses.jsonl`, and local
  `../csl-orig/v02/skd/skd.txt` / `../csl-orig/v02/vcp/vcp.txt` records.
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
| `definition-iti-unit` | An `iti` split carries a definition, synonym list, or semantic function list. | Candidate indigenous source unit; not automatically one dictionary sense. |
| `authority-quotation-unit` | The unit carries a quotation or named authority phrase in SKD prose. | Preserve authority evidence separately from sense counting. |
| `authority-siglum-unit` | The unit carries VCP-style abbreviated authority tokens such as `hemaca0` or `vahnipu0`. | Preserve as raw authority hints; do not normalize into `<ls>` without review. |
| `commentarial-discussion-unit` | The unit is a prose discussion of doctrine, lakshana, or commentary rather than a compact meaning. | Keep as explanatory evidence; group before sense-count comparison. |
| `morphology-grammar-unit` | The unit carries derivation, root class, grammatical function, or form inventory. | Keep outside default semantic sense counts. |
| `headword-stub-unit` | The split produces only the headword or a very small preface fragment. | Treat as parser artifact unless reviewed as content-bearing. |
| `same-headword-record-split` | Multiple source records with the same headword contribute rows. | Split records before comparing with archived counts. |
| `raw-headword-split` | Lookup gathers distinct raw headwords such as `rama` and `rAma`. | Keep raw headwords separate unless the reviewed target merges them. |
| `source-record-exact-control` | One source record row count equals the archived count. | Useful parser control, not semantic proof. |
| `lumped-indigenous-proxy` | A source record has no explicit `iti` split and is represented by one proxy row. | Preserve as source evidence; do not infer internal sense boundaries. |
| `no-anchor-control` | No SKD/VCP source-backed row exists for the anchor in this prototype. | Keep as a coverage control; no parser decision now. |

SKD authority hints are canonicalized from a small known phrase map. VCP
authority hints are raw abbreviated tokens ending in `0` after excluding common
grammar/gender abbreviations. Both are review aids, not a normalized citation
apparatus.

## Source-Inspected Proposals

### Dharma Rows

| Diagnostic | Source cue | Proposed labels | Parser consequence |
|---|---|---|---|
| `r2-drift:dharma:vcp` | [`vcp.txt#L352094`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/vcp/vcp.txt#L352094), `L=27030`, raw `Darmma`, yields 27 coarse `iti` units. Unit 1 starts from the Jaimini-style definition `codanAlakzaRo'rToDarmaH`; later units include Mimamsa/SAvara/lakshana discussion and many raw authority sigla. | `definition-iti-unit`, `authority-siglum-unit`, `commentarial-discussion-unit` | Do not count 27 VCP units as 27 senses. Group definition/discussion material and keep authority sigla as raw review hints. |
| `r2-drift:dharma:skd` | [`skd.txt#L206577`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/skd/skd.txt#L206577), `L=17667`, has 4 rows and exactly matches the archive. It includes Hitopadesa, Amara, Medini, Hemacandra, and Yogasara hints. [`skd.txt#L206596`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/skd/skd.txt#L206596), `L=17668`, adds 11 more rows, including Medini, Sribhagavatam, Bhagavata, and Dharmadipika hints. | `source-record-exact-control`, `same-headword-record-split`, `definition-iti-unit`, `authority-quotation-unit` | Treat `L=17667` as the archive-parity control and `L=17668` as same-headword expansion until a record-folding rule is reviewed. |

### Iti Rows

| Diagnostic | Source cue | Proposed labels | Parser consequence |
|---|---|---|---|
| `r2-drift:iti:skd` | [`skd.txt#L40325`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/skd/skd.txt#L40325), `L=4089`, yields 7 units. Unit 1 is only `iti`; unit 2 lists `hetuH` and `prakaraRam` with Manu; units 3-7 carry Amara, Manu, Medini, and Ramayana hints, including quotation continuations. | `headword-stub-unit`, `definition-iti-unit`, `authority-quotation-unit`, `morphology-grammar-unit` | Remove the stub from default counts, then review definition/function units separately from authority quotation tails. |
| `r2-drift:iti:vcp` | [`vcp.txt#L85845`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/vcp/vcp.txt#L85845), `L=8142`, yields 5 units. Unit 1 is a stub; unit 2 is an enumerated function list with raw hints including `barttf`, `kuma`, `mimamsaka`, `neza`, `pura`, and `rama`; units 3-4 are example/source fragments; unit 5 moves into verbal/grammatical material. | `headword-stub-unit`, `definition-iti-unit`, `authority-siglum-unit`, `authority-quotation-unit`, `morphology-grammar-unit` | Preserve VCP's function list and raw sigla, but do not treat the five units as five reviewed senses. |

### Rama Rows

| Diagnostic | Source cue | Proposed labels | Parser consequence |
|---|---|---|---|
| `r2-drift:rama:skd` | [`skd.txt#L390829`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/skd/skd.txt#L390829), `L=29190`, raw `rama`, yields 3 units. The record is a verbal root/form inventory: play, root class and forms, then `durgAdAsaH`. | `morphology-grammar-unit`, `definition-iti-unit`, `authority-quotation-unit` | Treat as root grammar/source evidence, not as a 10-row semantic counterpart to the archived SKD baseline. |
| `r2-drift:rama:vcp` | [`vcp.txt#L452114`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/vcp/vcp.txt#L452114), `L=39359`, raw `rama`, is a lumped root record with `jvalA0` and related hints. [`vcp.txt#L452119`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/vcp/vcp.txt#L452119), `L=39360`, raw `rama`, is a nominal record. [`vcp.txt#L453556`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/vcp/vcp.txt#L453556), `L=39589`, raw `rAma`, is a separate proper-name/etymology record with `vahnipu0` and other hints. | `lumped-indigenous-proxy`, `same-headword-record-split`, `raw-headword-split`, `source-record-exact-control`, `authority-siglum-unit` | Keep root `rama`, nominal `rama`, and proper-name `rAma` separate before any archived comparison. |

### Bodhisattva And No-Anchor Rows

| Diagnostic | Source cue | Proposed labels | Parser consequence |
|---|---|---|---|
| `r2-drift:bodhisattva:skd` | [`skd.txt#L310375`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/skd/skd.txt#L310375), `L=24423`, raw `boDisattvaM`, yields a definition unit and a Hemacandra/Kathasaritsagara quotation unit. | `definition-iti-unit`, `authority-quotation-unit` | Keep the second row as authority evidence for the Buddhist term, not as a separate reviewed meaning by default. |
| `r2-drift:bodhisattva:vcp` | [`vcp.txt#L428571`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/vcp/vcp.txt#L428571), `L=35803`, raw `boDisattva`, is one lumped proxy row with `hemaca0`. | `lumped-indigenous-proxy`, `source-record-exact-control`, `authority-siglum-unit` | Positive VCP coverage control; no internal split rule is available from this row. |
| `r2-drift:gam:skd`, `r2-drift:gam:vcp` | No current source-backed rows in the anchor prototype. | `no-anchor-control` | Do not infer absence from SKD/VCP as dictionaries; revisit only when lookup coverage broadens. |

## First Parser Rule To Test

For the next non-final R2 rebuild experiment:

1. Emit `headword-stub-unit` separately and exclude it from default counts.
2. Split SKD/VCP rows by source record and raw headword before comparing
   archived counts.
3. Preserve `authority-quotation-unit` and `authority-siglum-unit` as source
   evidence beside the semantic unit, not as normalized `<ls>` citations.
4. Keep `commentarial-discussion-unit` and `morphology-grammar-unit` outside
   default semantic sense counts unless reviewed into the target series.
5. Treat `source-record-exact-control`, `lumped-indigenous-proxy`, and
   `no-anchor-control` as parser controls, not proof of semantic alignment or
   absence.

This should let R2 use SKD/VCP indigenous evidence without flattening prose,
authority citations, grammar notes, and same-headword records into a single
false sense count.

_Dr. Mārcis Gasūns_
