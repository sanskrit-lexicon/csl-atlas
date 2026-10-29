# PD M2 — 50 blank-siglum rows adjudicated

_Created: 29-10-2026 · Executor: Kimi Work (Kimi; exact model version not exposed in the session) · Separate method-ladder unit M2_

## Frame and codebook

The frozen frame is `data/pd/pd_blank_siglum_adjudication.tsv`, selected from all
409 printed blank abbreviation cells with seed `PD-M2-blank-sigla-v1|29-10-2026`.
Allocation is stratified by the printed relation and transcription confidence:
46 commentary rows (10 `vision`, 36 `vision-low`), 2 cross-references (one per
confidence class), and 2 other/unspecified rows (one per class). The frame and
decisions are separate files, so annotation does not rewrite the frozen sample.

Labels: `dependent_commentary`, `cross_reference`, `unmarked_work`,
`duplicate_or_edition`, `uncertain`. Every selected row was checked against its
printed page image — 26 pages in total. `data/pd/pd_blank_siglum_decisions.tsv`
contains the per-row evidence note.

## Result

| Class | Rows | Share of the M2 sample |
|---|---:|---:|
| `dependent_commentary` | 46 | 92 % |
| `cross_reference` | 2 | 4 % |
| `unmarked_work` | 2 | 4 % |
| `duplicate_or_edition` | 0 | 0 % |
| `uncertain` | 0 | 0 % |
| **Total** | **50** | **100 %** |

The two `unmarked_work` rows are CVI:31 (*padayotanikā*) and CXVIII:15
(*vākyavṛttiṭīkā*): both the Nature and abbreviation cells are empty, so the
printed page supplies no relation that would explain the blank. All 50 blanks
are confirmed as printed blanks, not transcription losses.

## Limits and reproduction

This is a 50-row adjudicated sample, not a population estimate with a confidence
interval and not a double-coded reliability study. No κ is claimed for M2.
The decisions have not been promoted into the work registry.

```bash
python3 scripts/pd_blank_siglum_adjudication.py --check --complete
python3 -m pytest tests/forensic/test_pd_method_ladder_annotations.py -q
```

_Dr. Mārcis Gasūns_
