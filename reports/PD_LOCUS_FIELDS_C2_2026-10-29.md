# PD locus fields — C2, 29-10-2026

_Created: 29-10-2026 · Scope: all 107,630 entries and all 419,890 H6949 attestations in the published letter-`a` PD machine text · Status: **landed, full-population extraction with structural review flags** · Evidence: extraction and flags **derived**, no human `reviewed` claim._

## 1. Result

**105,890 of 107,630 PD entries — 98.3834 % — contain at least one assigned `(siglum, locus)`
pair with a non-empty locator.** A stricter structural view finds at least one clean pair in
**102,576 entries = 95.3043 %**.

The two numbers answer different questions. The first is the C2 field-coverage measure. The
second prevents a non-empty but visibly problematic field from being mistaken for a clean one.

| Entry status | Entries | Share of 107,630 |
|---|---:|---:|
| At least one clean pair | 102,576 | 95.3043 % |
| Only pairs needing structural review | 3,314 | 3.0791 % |
| Attestations, but no non-empty assigned pair | 54 | 0.0502 % |
| No attestation under H6949 | 1,686 | 1.5665 % |
| **Total** | **107,630** | **100.0000 %** |

H6949 finds an attestation in 105,944 entries (98.4335 %). The difference between that base
and C2 is exactly **54 entries**: they carry a siglum or an unassigned continuation, but no
non-empty assigned `(siglum, locus)` pair. Their sigla are preserved in
`pd_locus_summary.json`; examples include `cf.`, `PW.`, `MW.`, `comm.`, and bare work
references. They are a review class, not automatically extraction failures.

## 2. Field-level verification

The extraction retains all **419,890** attestation records: 384,217 siglum loci and 35,673
continuations, exactly matching H6949. Of these, **399,403** are non-empty assigned pairs and
**383,638** pass the structural `clean` flag.

| Review flag | Records | Meaning |
|---|---:|---|
| `clean` | 383,638 | non-empty, balanced, not prose-tail or unassigned |
| `empty` | 20,383 | siglum present, locator empty |
| `unbalanced_parentheses` | 10,454 | field ends with an unmatched `(` or `)` |
| `textual` | 5,088 | no numeric or roman locator shape; manual review required |
| `prose_tail` | 223 | locator continues into long prose |
| `unassigned` | 104 | continuation has no safely assignable preceding siglum |
| **Total** | **419,890** | — |

The shape split is `numeric` 207,525, `alphanumeric` 185,998, `roman` 792, `textual` 5,088,
`empty` 20,383, and `unassigned` 104. These flags describe the extracted field, not the
underlying printed edition and not its OCR fidelity.

A `clean` flag is deliberately narrow. It does not assert that the locator resolves to a real
chapter or page, that the cited work is correctly identified, or that the reading at the locus
matches the quotation. Those belong to C3 and to locus-alignment work, not to this field
census.

## 3. Method

1. Reused `quotation_units.count_units` and the H6949 PD siglum rule unchanged. No new
   quotation or attestation definition was introduced.
2. Retained source spans for each siglum and assigned the text up to the next siglum or
   semicolon as its locus. A bare continuation inherits the immediately preceding siglum,
   matching H6949 and C1; 104 continuations without a safe antecedent remain unassigned.
3. Trimmed only delimiters. No prose was silently deleted, no parenthesis was repaired, and no
   uncertain textual locus was promoted to numeric.
4. Classified every record by shape and review flag. Entries receive `clean`,
   `nonempty_only`, `empty_only`, or `no_attestation` independently of their total attestation
   count.
5. Reconciled every entry against committed `pd_quotations_by_entry.tsv`: attestation count,
   siglum-locus count, and continuation count all match exactly. Corpus totals match H6949
   independently as well.

The parser input is the canonical PDScan 2020 `txt/pd.txt`, 55,122,076 bytes, SHA-256
`4ee75e6619ee2bd86a331586bb922101e0ae090f9edd981752cfac36ed724442`.

## 4. What remains open

- The 20,383 empty fields need source-level inspection before they can be called bare
  references, OCR losses, or genuinely missing locators.
- The 10,454 unbalanced fields include both genuine OCR damage and fields cut at a following
  siglum; the flag deliberately does not choose between them.
- The 5,088 textual fields are not automatically invalid. Named sections and prose references
  need a separate typology.
- The 223 prose-tail fields show why non-empty alone is not a sufficient quality gate.
- No human review, inter-annotator κ, locus resolution, or edition-level validation is claimed.

## 5. Reproduce

```sh
python3.13 scripts/pd_locus_fields.py --pd /path/to/pd.txt
python3.13 scripts/pd_locus_fields.py --check --pd /path/to/pd.txt
python3.13 -m pytest tests/forensic/test_pd_locus_fields.py -q
```

Expected check: `PASS C2 105,890/107,630 = 98.3834% nonempty; 95.3043% clean`.

Artifacts:

- [`pd_locus_fields.tsv`](../data/pd/pd_locus_fields.tsv) — 419,890 rows, one per attestation, with siglum, locus, attestation type, shape and review flag.
- [`pd_locus_entries.tsv`](../data/pd/pd_locus_entries.tsv) — 107,630 rows with attestation, non-empty-pair, clean-pair and review counts plus entry status.
- [`pd_locus_summary.json`](../data/pd/pd_locus_summary.json) — headline metrics, all distributions, the 54 empty-only entries, 100 review examples, evidence labels and input hashes.
- [`scripts/pd_locus_fields.py`](../scripts/pd_locus_fields.py) and [`tests/forensic/test_pd_locus_fields.py`](../tests/forensic/test_pd_locus_fields.py) — deterministic extraction and hand-derived controls.

_29-10-2026 — Kimi Work; H6949 reused unchanged, full-population extraction, structural residue made explicit._
