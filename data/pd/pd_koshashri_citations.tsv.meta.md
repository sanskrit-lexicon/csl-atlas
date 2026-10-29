# Metadoc — pd_koshashri_citations.tsv

_Created: 29-10-2026 · Last updated: 29-10-2026_

Companion to [`pd_koshashri_citations.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_koshashri_citations.tsv), the citation-reference half of the H7316 KoshaSHRI fixture.

## Purpose and scope

One row per citation reference: 1,400 data rows across all 29 senses of the single `agni` entry. The first sense preserves 242 quotation texts as 248 reference rows (237 single-reference, four two-reference and one three-reference citations). Stable entry, sense and citation IDs keep the join to `pd_koshashri_entries.tsv` explicit.

## Schema

Tab-separated UTF-8 with a header and 1,400 data rows. Columns, in order:

`source`, `source_entry_id`, `sense_id`, `source_citation_id`, `quotation_text`, `source_siglum`, `work_title_candidate`, `work_id`, `work_resolution_status`, `locus`, `locus_scheme`, `work_date_raw`, `reference_author`, `validation_state`, `provenance`.

`locus` remains an array and `locus_scheme` retains values such as `Maṇḍala.Sūkta.Ṛc.`; `work_date_raw` retains source strings such as `1400BCE`. The malformed `<s<small>` source prefix is preserved. Only exact `ṚV.` resolves through H7296, to `PDW-ecd09ac913`; other sigla remain unresolved rather than guessed.

## Provenance and rights

Created 29-10-2026 by Kimi (`kimi-code-plan-global/k3.1-pro`) under H7316, merged in [csl-atlas#653](https://github.com/sanskrit-lexicon/csl-atlas/pull/653). The restricted local response is parsed by `scripts/pd_koshashri_vocable.py`; H7296's `pd_work_edition_map.tsv` is consumed read-only. See [the export report](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_KOSHASHRI_FIXTURE_EXPORT_2026.md).

KoshaSHRI is all rights reserved. Never commit the full `data/pd/koshashri_vocable.json` response or use this fixture as permission for bulk publication. The detailed boundary lives in [the rights note](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_koshashri_rights_provenance.md).

## Regeneration and checks

From the repository root, with the restricted input staged locally:

```bash
python3 scripts/pd_koshashri_fixture_export.py
python3 scripts/pd_koshashri_fixture_export.py --check
python3.13 -m pytest tests/forensic/test_pd_koshashri_fixture_export.py -q
```

Regenerate `pd_koshashri_entries.tsv` in the same pass. Expected citations SHA-256: `e325dad1369f61ed7e16c7a293ea9d8ac1c04813bd214424e2a4bd6812f67257`. A changed canary must stop the export; do not weaken the pins to make a changed input pass.

## Limitations

Rows are `unvalidated_pending_double_annotation`. Work coverage is not implied by the single `ṚV.` resolution, and the fixture is not an independent witness to the cited texts.

## Revision history

| Date | Change |
|---|---|
| 29-10-2026 | Created with the H7316 fixture export and document sweep. |

_Dr. Mārcis Gasūns_
