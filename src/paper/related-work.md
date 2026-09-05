_Created: 11-06-2026 · Last updated: 05-09-2026_

---
title: Paper — related work & positioning
---

# Related work: where the atlas sits in the digitisation pipeline

A short positioning note placing the atlas relative to the current machine
dictionary-digitisation literature. It complements the [grounded body](grounded),
the [triangulation](triangulation) against three lexicographic frameworks, and the
[framework appendices](appendices).

## Trust Block

- Evidence: Setiawan et al., *MUDIDI: A Two-Stage Framework for Multilingual Dictionary Digitization with Language Models* (University of Melbourne + LILT; code: [DavidSamuell/MUDIDI](https://github.com/DavidSamuell/MUDIDI)), read against this repo's convention-fingerprint and microstructure outputs. A local PDF copy is kept with the project sources; it is not redistributed here pending confirmation of its licence.
- Limitations: MUDIDI is an upstream digitisation/benchmark paper, not a test of the atlas's *block-economy* thesis; its support is for the general convention-priors claim, and its exact F1 figures are from a recent preprint and should be re-checked before citation.
- Validation: checked by `npm run build`; claims about MUDIDI should be verified against the source paper.
- Owner repo: `csl-atlas`.
- Next use: read alongside the [parse-rules framing](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/PARSE_RULES_FRAMING.md) and the candidate [MDF export profile](https://github.com/sanskrit-lexicon/csl-standards/blob/main/docs/MDF_EXPORT_MAPPING.md) in `csl-standards`.

## Positioning

Recent vision-language work treats dictionary digitisation as a two-stage problem —
faithful page transcription, then parsing into a lexicographic schema — and the
MUDIDI benchmark (Setiawan et al., 30 public-domain dictionaries across diverse
scripts, **Sanskrit–English among them**) reports that the decisive, low-cost
intervention for the *parsing* stage is not a bigger model but **per-dictionary
prior knowledge**: supplying a dictionary's own introduction (its abbreviation keys
and entry conventions) and a formal field schema each lift entry-field-assignment F1
by roughly 3–6 points, and substituting human-validated *parse-rules* for
machine-inferred ones adds about 6 more. This is independent, quantified corroboration
of the atlas's core methodological bet: that a dictionary's **house-style conventions
are not incidental but are the controlling signal for correct structural
interpretation** — exactly the knowledge the atlas already encodes by hand as the
[convention fingerprints](../tools/lexicographic-conventions) (25 dimensions; Patel's
seven canonical normalisation conventions plus eighteen auto-extracted), the
[structural register](../tools/structural-register), and the eighteen-block
microstructure apparatus. The atlas therefore stands one step *downstream* of MUDIDI
— it analyses CDSL text that Cologne has already keyed, rather than recovering text
from scans — but the two meet at the schema boundary: the atlas's per-dictionary
convention profiles are precisely the validated parse-rules MUDIDI shows are worth the
largest single F1 gain, and the [candidate MDF export](https://github.com/sanskrit-lexicon/csl-standards/blob/main/docs/MDF_EXPORT_MAPPING.md)
adds SIL's Multi-Dictionary Formatter — the flat standard-format-marker schema defined
in Coward & Grimes (2000) — as a third interoperability target beside the
`csl-standards` TEI and OntoLex/FrAC views. (Note that MUDIDI exercises Sanskrit only
in its transcription stage; its ten-dictionary *parsing* subset does not include
Sanskrit — a gap the atlas's source-linked structured CDSL data is uniquely placed to
fill.)

## See also

- 🔗 [Grounded body](grounded) · [Triangulation (§7)](triangulation) · [Framework appendices](appendices)
- 🔗 Parse-rules framing: [`docs/PARSE_RULES_FRAMING.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/PARSE_RULES_FRAMING.md)
- 🔗 Candidate MDF export profile: [`csl-standards/docs/MDF_EXPORT_MAPPING.md`](https://github.com/sanskrit-lexicon/csl-standards/blob/main/docs/MDF_EXPORT_MAPPING.md)

---

*Tour page. The canonical microanalysis paper lives in [MWS `docs-pass`](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md); MUDIDI is external related work, summarised here for positioning.*

_Dr. Mārcis Gasūns_
