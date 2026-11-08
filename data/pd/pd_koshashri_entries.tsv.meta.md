# Metadoc — pd_koshashri_entries.tsv

_Created: 29-10-2026 · Last updated: 29-10-2026_

Companion to [`pd_koshashri_entries.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_koshashri_entries.tsv), the entry-level half of the H7316 KoshaSHRI fixture.

## Purpose and scope

One `agni` entry with stable source identity, Devanagari/IAST/SLP1 headwords, grammar and etymology fields, the source volume object, sandhi, one nested vocable, validation state and provenance. All 29 senses are represented in the sibling citation table; this table intentionally contains one data row, not one row per sense.

## Schema

Tab-separated UTF-8 with a header and one data row. Columns, in order:

`source`, `source_entry_id`, `headword_devanagari`, `headword_iast`, `lemma_slp1`, `normalization_status`, `source_volume`, `grammar_raw`, `grammar_label`, `subcategory`, `grammatical_note_raw_html`, `etymology_raw_html`, `sandhi`, `nested_vocables`, `validation_state`, `provenance`.

JSON-valued source fields preserve their source distinctions. In particular, `source_volume` retains `{volumeNumber: 4, name: "Volume 2"}`; `nested_vocables` retains the single nested vocable; malformed source HTML is evidence, not text to repair silently.

## Provenance and rights

Created 29-10-2026 by Kimi (`kimi-code-plan-global/k3.1-pro`) under H7316, merged in [csl-atlas#653](https://github.com/sanskrit-lexicon/csl-atlas/pull/653). The input is the public single-entry GET recorded in [the export report](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_KOSHASHRI_FIXTURE_EXPORT_2026.md), adapted by `scripts/pd_koshashri_vocable.py` and exported by `scripts/pd_koshashri_fixture_export.py`.

KoshaSHRI is all rights reserved. The complete `data/pd/koshashri_vocable.json` response is a restricted local input and must not be committed or bulk-published. This single fixture does not grant reuse rights beyond the H7316 scope; see [the rights note](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_koshashri_rights_provenance.md).

## Regeneration and checks

From the repository root, with the restricted input staged locally:

```bash
python3 scripts/pd_koshashri_fixture_export.py
python3 scripts/pd_koshashri_fixture_export.py --check
python3.13 -m pytest tests/forensic/test_pd_koshashri_fixture_export.py -q
```

Regenerate `pd_koshashri_citations.tsv` in the same pass. The builder is offline and deterministic; `--check` verifies canaries and byte identity. Expected entries SHA-256: `29f3cbf7654256762d380e279ffd364acf24106d080803f8b760f09f1bf35fdd`.

## Limitations

This is one fixture, not a KoshaSHRI corpus export or an independent textual witness. Source normalization and work resolution remain deliberately conservative; validation is `unvalidated_pending_double_annotation`.

## Revision history

| Date | Change |
|---|---|
| 29-10-2026 | Created with the H7316 fixture export and document sweep. |

_Dr. Mārcis Gasūns_
