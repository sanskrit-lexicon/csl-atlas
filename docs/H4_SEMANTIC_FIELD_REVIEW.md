# H4 Semantic-Field Review Packet

Date: 2026-06-05

Status: scholar-facing review packet for H4/M8 semantic-field evidence.

## Trust Block

- Evidence: `data/lexico/semantic_field_family_profiles.json`,
  `data/lexico/semantic_field_coverage.csv`,
  `data/lexico/semantic_fields.csv`,
  `src/data/dicts/semantic-fields.json`,
  `scripts/lexico/m8_semantic_fields.py`,
  `scripts/build-semantic-fields.mjs`, and
  `scripts/build-h4-family-profiles.mjs`.
- Limitations: headword coverage only; no corpus frequency, passage evidence,
  sense coverage, or prose-only knowledge is counted.
- Validation: `python scripts/lexico/validate_lexico.py`,
  `npm run build-semantic-fields`, `npm run build-h4-family-profiles`, and
  `npm run build`.
- Owner repo: `csl-atlas`.

## Purpose

This packet turns the H4 family-profile artifact into review work. The current
machine result is already useful: AMAR fields can be mapped to 43 dictionary
headword sets, grouped into 5 family profiles, and summarized as 12 high-spread
field contrasts. The review step asks which of those contrasts are true topical
signals and which are caused by headword convention, genre, or source scope.

## What This Review Proves

| Review packet | Sample size | What it proves | What it does not prove |
|---|---:|---|---|
| H4-R1 SKD false-low | 25 | Whether low SKD headword coverage hides AMAR material in prose, citation, or inflected wording. | That SKD lacks the field. |
| H4-R2 VCP high coverage | 20 | Whether VCP's high AMAR coverage reflects real exposed headwords. | That VCP has richer senses than lower-coverage dictionaries. |
| H4-R3 AP/AP90 delta | 20 | Whether AP > AP90 differences are edition/revision effects, parser effects, or headword normalization effects. | That later dictionaries are automatically broader. |
| H4-R4 specialized baseline | 20 | Whether ARMH, FRI, and BHS matches reflect their own scope rather than general-dictionary breadth. | That specialized works should be ranked against MW. |
| H4-R5 index/reverse controls | 20 | Whether low index and reverse-bilingual coverage is genre or lookup-direction mismatch. | That those works are semantically poor. |

## Review Inputs

Start from `data/lexico/semantic_field_family_profiles.json`:

- `familyProfiles[*].topDictionaries` identifies the dictionaries that drive a
  family signal.
- `familyProfiles[*].topFields` and `lowFields` provide field-level examples
  and missing examples.
- `fieldContrasts` provides the 12 largest family spreads. Treat each spread as
  a prompt, not a finding.

For row-level review, join back to:

- `data/lexico/semantic_field_coverage.csv` for dictionary/field coverage;
- `data/lexico/semantic_fields.csv` for AMAR lemma-to-field rows;
- dictionary source links from the relevant CDSL repo or atlas source-link
  conventions.

## Priority Samples

| ID | How to choose rows | Review question | Expected decision labels |
|---|---|---|---|
| H4-R1 | SKD rows missing from low indigenous-prose fields such as `viSezyaniGnavargaH`, `brahmavargaH`, and `vyomavargaH`. | Is the lemma absent, present under a variant headword, or present only in prose/citation? | `true-low`, `variant-headword`, `prose-present`, `parser-gap` |
| H4-R2 | VCP covered AMAR lemmas across high indigenous-prose fields such as `narakavargaH`, `avyayavargaH`, and `BUmivargaH`. | Does the headword match represent real coverage and a usable dictionary entry? | `true-covered`, `thin-entry`, `normalization-risk` |
| H4-R3 | AMAR lemmas covered by AP but not AP90, across several fields. | Is the delta edition history, parser coverage, or headword normalization? | `edition-delta`, `parser-gap`, `normalization-risk`, `true-delta` |
| H4-R4 | ARMH/FRI/BHS matches from their strongest fields and from one weak field. | Does concentration follow the dictionary's stated scope? | `scope-match`, `incidental-match`, `scope-mismatch` |
| H4-R5 | AE/MWE and index-family exceptions in their top fields. | Are non-zero matches meaningful, or just lookup-direction/index artifacts? | `direction-artifact`, `index-artifact`, `meaningful-exception` |

## Strongest Contrast Prompts

The largest spreads in the current artifact are all western-tagged versus
reverse-bilingual contrasts. Use them as controls before making topical claims:

| Field | High family | Low family | Spread |
|---|---|---|---:|
| `SElavargaH` | western-tagged | reverse-bilingual | 68.8 pts |
| `vyomavargaH` | western-tagged | reverse-bilingual | 67.3 pts |
| `kAlavargaH` | western-tagged | reverse-bilingual | 67.0 pts |
| `DIvargaH` | western-tagged | reverse-bilingual | 65.3 pts |
| `nAwyavargaH` | western-tagged | reverse-bilingual | 62.4 pts |

These are strong evidence that lookup direction matters. They are not yet
evidence that western-tagged dictionaries have a stronger semantic interest in
those fields.

## Review Columns

If this packet becomes a generated review report, keep the canonical
review-report schema and status vocabulary unchanged. Suggested machine fields:

| Field | Meaning |
|---|---|
| `reviewId` | Stable ID such as `h4-skd-false-low:skd:vyomavargaH:AkASa`. |
| `sampleType` | `skd-false-low`, `vcp-high`, `ap-ap90-delta`, `specialized-baseline`, or `index-reverse-control`. |
| `dict` | Dictionary code under review. |
| `fieldKey` | AMAR field key from the generated artifact. |
| `lemma` | AMAR lemma in SLP1. |
| `machineState` | `covered`, `missing`, `delta`, or `exception`. |
| `sourcePointer` | Dictionary source link or entry reference when available. |
| `reviewStatus` | Canonical status, initially `needs-review`. |
| `reviewedValue` | Human label such as `prose-present` or `true-low`. |
| `note` | Short source-facing explanation. |

## Boundary Rules

- Keep H4 dictionary-first. Do not import DCS frequency or passage dashboards.
- Do not use H4 to rank dictionary quality.
- Do not call low coverage absence until a convention check has been sampled.
- Treat reverse-bilingual and index dictionaries as controls, not failures.
- Route future corpus-field hypotheses to VisualDCS first; atlas may later
  consume a compact dictionary-facing summary.

## Acceptance

H4 can move from `machine-reviewed` to `reviewed` interpretation when each
priority packet has a small adjudicated sample and the result is summarized in
`H4_SEMANTIC_FIELD_INTERPRETATION.md`.
