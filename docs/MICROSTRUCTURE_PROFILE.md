# Microstructure Profile

Date: 2026-06-04

Audience: scholars of lexicography and maintainers who need a dictionary-level
and entry-level account of how microstructure differs across CDSL dictionaries.

## Trust Block

- Evidence: M1-M6 generated outputs under `data/lexico/`, especially
  `microstructure_profile.csv` and `microstructure_fingerprint.json`.
- Limitations: marker counts measure recoverable conventions, not the full
  content of every dictionary.
- Validation: `python scripts/lexico/validate_lexico.py`.
- Owner repo: `csl-atlas`.

## What This Profile Is

The microstructure profile is a sparse per-entry join over dictionary structure
signals. A row exists when at least one of the current extractors fires for a
dictionary entry:

- M1 derivative subentry markers;
- M2 preverb subentries;
- M3 cross-reference edges, folded to outgoing degree;
- M4 verbal-root evidence from indigenous and dictionary-specific conventions;
- M5 unified join and per-dictionary fingerprint.

Read the doc family in parse order. Start with
[`MICROSTRUCTURE_HEADWORD_SUBENTRY.md`](MICROSTRUCTURE_HEADWORD_SUBENTRY.md),
then move to
[`MICROSTRUCTURE_SENSE_SEGMENTATION.md`](MICROSTRUCTURE_SENSE_SEGMENTATION.md)
before citation practice, grammar/gender marking, and cross-references.

The row key is `(dict, L)`, the dictionary code and CDSL entry number. The
profile is meant to answer scholar-facing questions such as:

- Does a dictionary put grammatical detail inside entries or promote it to
  separate headwords?
- Which dictionaries share a microstructure convention?
- Where does a zero mean absence, and where does it mean detector blindness?
- Which structural signals can support lineage hypotheses?

## Primary Files

| File | Role | Evidence label |
|---|---|---|
| `data/lexico/microstructure_profile.csv` | Per-entry M1-M5 join. | `derived` |
| `data/lexico/microstructure_fingerprint.json` | Per-dictionary layer densities and dominant layer. | `derived` |
| `data/lexico/microstructure_subentries.csv` | M1 derivative-subentry rows. | `derived` |
| `data/lexico/preverb_subentries.csv` | M2 preverb-subentry rows. | `derived` |
| `data/lexico/xref_edges.csv` | M3 cross-reference edges. | `derived` |
| `data/lexico/indigenous_roots.csv` | M4 indigenous root rows. | `derived` |
| `data/lexico/xref_lineage.json` | M6 shared cross-reference overlap. | `derived` |

## Use-Case Mapping

| Use case | How the profile helps |
|---|---|
| UC-LX-01 MW Article Anatomy | Distinguishes MW headword promotion from Petersburg nesting. |
| UC-LX-02 Lexicographic Conventions | Makes convention differences measurable. |
| UC-LX-03 Dictionary Genealogy | Supplies structural evidence independent of headword overlap. |
| UC-DEV-04 Diagnose A Metric From A Source Link | Gives generated rows and scripts behind each metric. |

## Reading The Profile

The safest interpretation is comparative and convention-aware. A high M1 or M2
count means a dictionary exposes a structure in a detectable CDSL markup
convention. A low or zero count does not automatically mean the dictionary lacks
that structure. Indigenous and root-layer dictionaries such as SKD, VCP, KRM,
SHS, and YAT need M4 because their verbal apparatus is written in source-specific
conventions, not European abbreviation tags.

## Companion Docs

- [`MICROSTRUCTURE_METHODS.md`](MICROSTRUCTURE_METHODS.md)
- [`MICROSTRUCTURE_FINDINGS.md`](MICROSTRUCTURE_FINDINGS.md)
- [`MICROSTRUCTURE_HEADWORD_SUBENTRY.md`](MICROSTRUCTURE_HEADWORD_SUBENTRY.md)
- [`MICROSTRUCTURE_SENSE_SEGMENTATION.md`](MICROSTRUCTURE_SENSE_SEGMENTATION.md)
- [`MICROSTRUCTURE_M1_M2_RESULTS.md`](MICROSTRUCTURE_M1_M2_RESULTS.md)
- [`MICROSTRUCTURE_ZERO_MEANING.md`](MICROSTRUCTURE_ZERO_MEANING.md)
- [`MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md`](MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md)
- [`MICROSTRUCTURE_XREF_LINEAGE.md`](MICROSTRUCTURE_XREF_LINEAGE.md)
- [`MICROSTRUCTURE_ROOT_AGREEMENT.md`](MICROSTRUCTURE_ROOT_AGREEMENT.md)
- [`MICROSTRUCTURE_SEMANTIC_FIELDS.md`](MICROSTRUCTURE_SEMANTIC_FIELDS.md)
