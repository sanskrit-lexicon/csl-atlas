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

| Method | Script | Counts | Blind to | Main output |
|---|---|---|---|---|
| M1 | `scripts/lexico/m1_subentries.py` | `<ab>` derivative markers such as causative, passive, desiderative, intensive, denominative, periphrastic, compound. | Equivalent information not wrapped in `<ab>`. | `microstructure_subentries.csv` |
| M2 | `scripts/lexico/m2_preverbs.py` | `<div n="p">` preverb subentry blocks. | Preverb evidence expressed without this division marker. | `preverb_subentries.csv` |
| M3 | `scripts/lexico/m3_xrefs.py` | PWG `Vgl.`, MW `cf.`, and Apte-family `cf.{#...#}` Sanskrit target edges. | Cross-references expressed in other markup or mixed with cognates/citations. | `xref_edges.csv` |
| M4 | `scripts/lexico/m4_indigenous.py` | Verbal-root evidence from dhatupatha citations, SKD anubandha slots, KRM clusters, VCP annotation, and YAT conjugation blocks. | Dictionary-specific verbal formats not explicitly modeled yet. | `indigenous_roots.csv` |
| M5 | `scripts/lexico/m5_profile.py` | Lossless join of M1-M4 on `(dict, L)`, with M3 folded to `xref_out`. | Corpus-level in-degree and hub analysis. | `microstructure_profile.csv` |
| M6 | `scripts/lexico/m6_xref_lineage.py` | Shared cross-reference edges across parsed dictionaries. | Unparsed xref conventions and non-lemma citation targets. | `xref_lineage.json` |

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

This rule is central to the SKD/VCP/YAT correction: they are rich in verbal
apparatus despite scoring low or zero under European `<ab>` and `<div>`
detectors.

## Review Status

Current outputs are deterministic and machine-checked. Human review is still
needed for:

- YAT raw it/anubandha interpretation;
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
python scripts/lexico/validate_lexico.py
```
