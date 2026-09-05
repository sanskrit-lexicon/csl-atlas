_Created: 06-06-2026 · Last updated: 05-09-2026_

# Microstructure Methods

Date: 2026-06-04

Audience: scholars and maintainers who need to know exactly what each
microstructure extractor counts.

## Trust Block

- Evidence: deterministic extractors in `scripts/lexico/` and generated outputs
  in `data/lexico/`.
- Limitations: the methods are convention detectors; they do not read all prose
  as full lexicographic structure.
- Validation: `python -m py_compile scripts/lexico/*.py` and
  `python scripts/lexico/validate_lexico.py`.
- Owner repo: `csl-atlas`.

## Method Inventory

For scholar-facing reading, start with the easiest visible layer:
[`MICROSTRUCTURE_HEADWORD_SUBENTRY.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_HEADWORD_SUBENTRY.md).
It explains why M1/M2 headword and subentry structure comes first. Then use
[`MICROSTRUCTURE_SENSE_SEGMENTATION.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_SENSE_SEGMENTATION.md)
to decide which sense divisions are structural proxies and which require R2
review before interpretation.

| Method | Script | Counts | Blind to | Main output |
|---|---|---|---|---|
| M1 | `scripts/lexico/m1_subentries.py` | `<ab>` derivative markers such as causative, passive, desiderative, intensive, denominative, periphrastic, compound. | Equivalent information not wrapped in `<ab>`. | `microstructure_subentries.csv` |
| M2 | `scripts/lexico/m2_preverbs.py` | `<div n="p">` preverb subentry blocks. | Preverb evidence expressed without this division marker. | `preverb_subentries.csv` |
| M3 | `scripts/lexico/m3_xrefs.py` | PWG `Vgl.`, MW `cf.`, and Apte-family `cf.{#...#}` Sanskrit target edges. | Cross-references expressed in other markup or mixed with cognates/citations. | `xref_edges.csv` |
| M4 | `scripts/lexico/m4_indigenous.py` | Verbal-root evidence from dhatupatha citations, SKD anubandha slots, KRM clusters, SHS dash clusters, VCP annotation, and YAT conjugation blocks. | Dictionary-specific verbal formats not explicitly modeled yet. | `indigenous_roots.csv` |
| M5 | `scripts/lexico/m5_profile.py` | Lossless join of M1-M4 on `(dict, L)`, with M3 folded to `xref_out`. | Corpus-level in-degree and hub analysis. | `microstructure_profile.csv` |
| M6 | `scripts/lexico/m6_xref_lineage.py` | Shared cross-reference edges across parsed dictionaries. | Unparsed xref conventions and non-lemma citation targets. | `xref_lineage.json` |
| M7 | `scripts/lexico/m7_root_agreement.py` | Cross-dictionary agreement and conflict in root gaṇa, pada, and transitivity. | Root identity normalization across citation conventions. | `root_agreement.json` |
| M8 | `scripts/lexico/m8_semantic_fields.py` | Amarakośa varga/upavarga field coverage by dictionary headwords. | Corpus frequency, sense coverage, and prose-only AMAR knowledge. | `semantic_field_report.json` |

Sense segmentation is documented separately because the current countable chart
is produced by `scripts/build-sense-depth.mjs`, while broader sense-alignment
claims depend on the R2 rebuild contract and review packets.

## Method Rule

Do not compare raw zeros across traditions without first asking whether the
same convention is visible to the detector. The correct claim is often:

```text
This dictionary does not use the convention counted by this method.
```

not:

```text
This dictionary lacks the phenomenon.
```

This rule is central to the SKD/VCP/YAT/SHS correction: they are rich in verbal
apparatus despite scoring low or zero under European `<ab>` and `<div>`
detectors.

## Review Status

Current outputs are deterministic and machine-checked. Human review is still
needed for:

- YAT raw it/anubandha interpretation;
- SHS dash-cluster and English-ordinal sample review;
- ambiguous VCP gana abbreviations;
- cross-reference target classes outside the parsed `Vgl.` / `cf.` seam;
- interpretation of rare or mixed conventions.

## Reproduce

```sh
python scripts/lexico/m1_subentries.py --all
python scripts/lexico/m2_preverbs.py --all
python scripts/lexico/m3_xrefs.py --all
python scripts/lexico/m4_indigenous.py --all
python scripts/lexico/m5_profile.py
python scripts/lexico/m6_xref_lineage.py
python scripts/lexico/m7_root_agreement.py
python scripts/lexico/m8_semantic_fields.py
python scripts/lexico/validate_lexico.py
```

_Dr. Mārcis Gasūns_
