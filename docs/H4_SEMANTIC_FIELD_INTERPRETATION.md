# H4 Semantic-Field Interpretation

Date: 2026-06-05

Status: scholar-facing interpretation note for the implemented M8 data layer
and `/tools/semantic-fields`.

## Trust Block

- Evidence: `data/lexico/semantic_fields.csv`,
  `data/lexico/semantic_field_coverage.csv`,
  `data/lexico/semantic_field_report.json`,
  `data/lexico/semantic_field_family_profiles.json`,
  `src/data/dicts/semantic-fields.json`,
  `scripts/lexico/m8_semantic_fields.py`, and
  `scripts/build-semantic-fields.mjs`,
  `scripts/build-h4-family-profiles.mjs`.
- Limitations: headword coverage only; no corpus frequency, passage
  attestation, sense coverage, or non-headword mentions.
- Validation: `python scripts/lexico/validate_lexico.py`,
  `npm run build-semantic-fields`, `npm run build-h4-family-profiles`,
  and `npm run build`.
- Owner repo: `csl-atlas`.

## Current Reading

H4 is now stronger than "can we measure fields?" The answer is yes: AMAR vargas
produce a stable dictionary-first coverage layer. The family-profile artifact
now shows that coverage profiles can be compared by dictionary family rather
than only by gross size.

## Family Profile Artifact

`data/lexico/semantic_field_family_profiles.json` groups the 43 compared
dictionaries into 5 evidence-bearing family profiles across 24 AMAR fields. It
emits top fields, low fields, distinctive high/low fields, and 12 high-spread
field contrasts as review prompts. Each family cluster includes a convention
explanation so low coverage is not mistaken for absence of knowledge.

The strongest current aggregate contrast is still a convention contrast:
Western-tagged dictionaries average 52.5% AMAR headword coverage across the
family, while reverse-bilingual works average 0.2% under this strict Sanskrit
headword test. That spread is not a quality ranking; it tells us which lookup
and headword conventions the review samples must control for.

## Family-Level Signals

| Family | Current signal | Interpretation |
|---|---|---|
| Western-tagged | 21 dictionaries with non-zero coverage; average non-zero coverage about 52.5%. | General Western dictionaries dominate the high-coverage band, but family members still differ sharply by headword policy and scope. |
| Indigenous-prose | VCP is high at 79.2%; SKD is low at 20.8%; KRM is tiny at 2.4%. | Indigenous works cannot be read through one coverage number; exposed `<k1>` headwords and prose/citation conventions diverge. |
| Specialized | ARMH is high at 45.5%, while many specialized dictionaries are narrow or zero. | A specialized work can be field-rich when its topic overlaps AMAR; low coverage often means scope mismatch, not poor quality. |
| Index-catalogue | Average non-zero coverage about 10.1%. | Indexes are reference tools, not general dictionaries; H4 should not rank them as deficient general dictionaries. |
| Reverse-bilingual | AE/MWE are near zero in this strict test. | English-to-Sanskrit direction is a lookup convention mismatch for AMAR headword coverage. |

## Strongest Data Points

| Claim | Evidence | Reading |
|---|---|---|
| MW is the broadest AMAR headword coverer. | MW covers 8,955 AMAR lemmas, 91.8%. | This is a high-coverage dictionary signal, not a corpus-frequency claim. |
| A broad 78-80% band exists. | PW/PWK 79.8%, YAT 79.7%, WIL 79.4%, VCP 79.2%, SHS 79.2%, PWG 78.4%. | Several lineages converge on broad AMAR headword coverage. |
| Apte is not simply "late therefore broader." | AP 47.5%, AP90 32.4%. | H4 joins H1R in warning against simple temporal richness claims. |
| SKD's low value is convention-sensitive. | SKD covers 20.8%, but often embeds kosha material in prose/citations rather than `<k1>` headwords. | SKD needs a false-low review sample before any topical conclusion. |
| Specialized dictionaries need separate baselines. | ARMH 45.5%, FRI 24.8%, BHS 13.5%. | Compare them to their own scope, not to MW. |

## Review Samples

Use small scholar-reviewed samples before making paper-level claims:

| Sample | Size | Purpose |
|---|---:|---|
| SKD false-low sample | 25 AMAR lemmas missing as SKD `<k1>` but likely present in prose/citations. | Estimate convention loss. |
| VCP high-coverage sample | 20 covered AMAR lemmas across high fields. | Check whether high coverage reflects true headword exposure. |
| AP/AP90 delta sample | 20 AMAR lemmas covered by AP but not AP90. | Separate edition/revision differences from parser effects. |
| Specialized baseline sample | 20 ARMH/FRI/BHS matches. | Confirm that field concentration reflects scope. |

The review packet is now documented in
[`H4_SEMANTIC_FIELD_REVIEW.md`](H4_SEMANTIC_FIELD_REVIEW.md). It adds sample
selection rules, decision labels, review columns, and boundary rules for SKD
false lows, VCP high coverage, AP/AP90 deltas, specialized baselines, and
index/reverse controls.

## What Not To Claim Yet

- Do not claim AMAR fields measure dictionary quality.
- Do not rank dictionaries by semantic exhaustiveness.
- Do not import corpus frequency or DCS passage evidence into H4.
- Do not treat low SKD/index/reverse coverage as absence of knowledge.

## Next Test

Use the review packet to choose rows from the family-profile artifact, then
record which high/low clusters are true topical signals and which are convention
or scope effects. This can become a paper figure only after those samples are
checked.
