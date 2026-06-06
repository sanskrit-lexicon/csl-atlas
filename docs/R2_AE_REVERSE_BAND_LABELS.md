# R2 AE Reverse Band Label Proposals

Date: 2026-06-06

Status: source-inspected proposal layer for the `ae-reverse-bands` R2 parser
packet. These labels are not scholar-reviewed alignment decisions and must not
be treated as `reviewedValue`.

## Trust Block

- Claim: AE reverse-equivalent diagnostics can be separated into review bands
  and source-role labels before any reverse dictionary row is used as alignment
  evidence.
- Evidence label: `derived`.
- Source files: `data/lexico/r2_review_packets.json`,
  `data/lexico/r2_parser_diagnostics.json`,
  `data/lexico/r2_source_anchor_senses.jsonl`, and local
  `../csl-orig/v02/ae/ae.txt` records.
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
| `reverse-high-candidate` | The first matching Sanskrit equivalent is in AE equivalent group 0-2. | Keep in the first AE review band; do not count as final alignment without source-role review. |
| `reverse-medium-review` | The first matching Sanskrit equivalent is in group 3-4. | Keep as a secondary review band; useful for distinctive lemmas, risky for common roots. |
| `reverse-low-context` | The first matching Sanskrit equivalent is in group 5-9. | Retain as context, but exclude from default cross-dictionary alignment counts. |
| `reverse-tail-overmatch` | The first matching Sanskrit equivalent is in group 10 or later. | Retain only as overmatch evidence unless a reviewer promotes the row. |
| `direct-equivalent-candidate` | The queried Sanskrit form is a direct equivalent for the English headword. | Eligible for AE alignment review within its rank band. |
| `phrase-or-collocation-match` | The queried form appears inside a phrase, compound, quoted example, or idiom. | Preserve as dictionary evidence, but do not treat as headword-level equivalence by default. |
| `broad-headword-overmatch` | The English headword has many equivalent groups and the queried form appears deep in a broad list. | Use as a noise-control row; exclude from default alignment counts. |
| `reverse-no-anchor-control` | AE has no source-backed reverse row for the anchor lemma. | Keep as a coverage control; no parser decision now. |

The mechanical rank bands come from `reverseMatchProfile`: high = first
matching group <= 2, medium = <= 4, low = <= 9, tail = >= 10.

## Source-Inspected Proposals

### High-Priority Rows

| Diagnostic | Rank counts | Source cues | Proposed labels | Parser consequence |
|---|---:|---|---|---|
| `r2-drift:gam:ae` | high 37, medium 54, low 72, tail 80 | [`ae.txt#L54747`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ae/ae.txt#L54747), `L=9251`, `scud`, puts `ativegena-sahasA-gam` in group 1 of 3. [`ae.txt#L19724`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ae/ae.txt#L19724), `L=3366`, `elapse`, puts `gam` in group 3 of 5. [`ae.txt#L44175`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ae/ae.txt#L44175), `L=7549`, `pad`, first matches at group 10 of 12. | `reverse-high-candidate`, `reverse-medium-review`, `reverse-low-context`, `reverse-tail-overmatch`, `phrase-or-collocation-match`, `broad-headword-overmatch` | AE `gam` is useful as a ranked motion-root worklist, but even the high band has 37 rows against 30 archived rows. Do not use AE row count parity; review high/medium rows first and retain low/tail as noise controls. |
| `r2-drift:iti:ae` | high 9, medium 7, low 23, tail 37 | [`ae.txt#L61759`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ae/ae.txt#L61759), `L=10400`, `thus`, directly gives `evaM, itTaM, iti`. [`ae.txt#L1484`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ae/ae.txt#L1484), `L=253`, `alias`, has `iti aparanAmaDeya`. [`ae.txt#L30061`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ae/ae.txt#L30061), `L=5103`, `identical`, first matches at group 10 of 22 in a broad pronominal/example row. | `reverse-high-candidate`, `direct-equivalent-candidate`, `reverse-medium-review`, `phrase-or-collocation-match`, `reverse-tail-overmatch`, `broad-headword-overmatch` | Treat high `thus`/`because`-type rows as AE particle candidates; keep formula/example rows as source evidence for `iti` behavior, not automatic alignment rows. |
| `r2-drift:dharma:ae` | high 18, medium 12, low 11, tail 25 | [`ae.txt#L13813`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ae/ae.txt#L13813), `L=2393`, `creed`, gives `DarmaH` in group 1 of 3. [`ae.txt#L32318`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ae/ae.txt#L32318), `L=5521`, `injunction`, gives `Darma-sUtraM` in group 3 of 4. [`ae.txt#L41217`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ae/ae.txt#L41217), `L=7031`, `nature`, first matches at group 5 of 66. [`ae.txt#L44849`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ae/ae.txt#L44849), `L=7680`, `part`, first matches at group 5 of 122. | `reverse-high-candidate`, `direct-equivalent-candidate`, `reverse-medium-review`, `phrase-or-collocation-match`, `reverse-low-context`, `broad-headword-overmatch` | High/medium `dharma` rows are strong review candidates when the English headword is religion/law/duty/attribute-like. Broad rows such as `nature` and `part` should stay out of default alignment counts. |

### Medium And Control Rows

| Diagnostic | Rank counts | Source cues | Proposed labels | Parser consequence |
|---|---:|---|---|---|
| `r2-drift:rama:ae` | high 1, low 1, tail 4 | [`ae.txt#L26241`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ae/ae.txt#L26241), `L=4462`, `genial`, has `ramya`, `ramaRIya`, and `manohara-rama` early in the equivalent list. [`ae.txt#L14897`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ae/ae.txt#L14897), `L=2578`, `dear`, first matches later in an endearment row. [`ae.txt#L46926`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ae/ae.txt#L46926), `L=8021`, `please`, first matches at group 35 of 68. | `reverse-high-candidate`, `phrase-or-collocation-match`, `reverse-low-context`, `reverse-tail-overmatch`, `broad-headword-overmatch` | AE `rama` is a small review queue, not a row-count problem. Keep `genial` as a candidate semantic-neighbor row; treat low/tail rows as contextual evidence only. |
| `r2-drift:bodhisattva:ae` | none | The current AE anchor prototype has no source-backed rows for `bodhisattva`. | `reverse-no-anchor-control` | Keep as an AE coverage control; do not infer absence beyond this anchor lookup. |

## First Parser Rule To Test

For the next non-final R2 rebuild experiment:

1. Preserve `reverseMatch.rank`, `firstGroupIndex`, `matchGroupCount`, and
   `equivalentGroupCount` on every AE row.
2. Route high rows to `reverse-high-candidate`, medium rows to
   `reverse-medium-review`, low rows to `reverse-low-context`, and tail rows to
   `reverse-tail-overmatch`.
3. Add source-role labels during review: `direct-equivalent-candidate` for
   direct headword equivalents, `phrase-or-collocation-match` for examples,
   compounds, and idioms, and `broad-headword-overmatch` for large English
   entries where the match is late or incidental.
4. Exclude `reverse-low-context`, `reverse-tail-overmatch`, and
   `broad-headword-overmatch` from default alignment counts.
5. Never compare AE reverse row counts directly to Sanskrit headword sense
   counts; AE is English-to-Sanskrit evidence and needs rank/source-role review
   before alignment use.

This keeps AE useful for distinctive cross-language hints while preventing
common-root rows such as `gam`, formula rows such as `iti`, and broad entries
such as `part` or `please` from inflating R2 alignment evidence.
