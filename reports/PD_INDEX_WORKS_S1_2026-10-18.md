# PD Index of Works — S1 transcription and reconciliation

_Created: 18-10-2026 · Last updated: 18-10-2026_

**Handoff:** H6992 (S1 of 5) · **Data:** [`data/pd/pd_index_works.tsv`](../data/pd/pd_index_works.tsv)
· **Delta:** [`pd_index_works_siglum_delta.tsv`](../data/pd/pd_index_works_siglum_delta.tsv)
· **Summary:** [`pd_index_works_summary.json`](../data/pd/pd_index_works_summary.json)
· **Script:** [`scripts/pd_index_works_transcribe.py`](../scripts/pd_index_works_transcribe.py)

## What S1 delivers

The printed *Index of Works Used in the Dictionary* in PD vol. 1 (Ghatage 1976),
pp. LXXXIX–CXXVII, is 39 pages = DjVu leaves 98–136. S1 lands the pilot schema
and the first page:

- **Page LXXXIX (leaf 98) fully vision-transcribed: 48 rows**, columns `page`,
  `row`, `title_deva`, `title_iast`, `author_deva`, `author_iast`,
  `nature_deva`, `subject_code`, `subject_class_no`, `subject_label`,
  `abbreviation_siglum`, `abbreviation_qualifier`, `confidence`.
- The first 19 rows are the pilot block named in the handoff; the page is
  extended to all 48 rows in the same file.
- **Blank sigla: 2** (rows 13 and 36 have a printed blank in the abbreviation
  cell; both are commentary rows whose siglum is the commented work's).
- **Subject subcodes are recorded as printed** (`4.2`, `27.1`, `27.4`, `27.7`,
  `54.4`), separately from the 62 integer classes in `subject_class_no`.
  Page LXXXIX uses 8 × `4.2`, 2 × `27.1`, 2 × `27.7`, 1 × `27.4`, 2 × `54.4`.
- **No full-Index total is published.** 38 of 39 pages are still pending; a
  total from one page would be an extrapolation, which the handoff forbids.
  `row_total_verified = 48`, `row_total_full = null`.

## Siglum reconciliation

`pd_index_works_siglum_delta.tsv` joins every Index siglum to both the printed
AOB inventory (`pd_aob_entries.tsv`, 1,444 rows → 1,403 unique sigla) and the
harvest (`pd_siglum_families.tsv`, 3,569 unique sigla), using diacritic- and
punctuation-insensitive exact matching. A near-match column records AOB/harvest
OCR variants without counting them as membership.

Page LXXXIX result (48 rows):

| Status | Rows | Meaning |
|---|---:|---|
| `in_both` | 26 | exact siglum in AOB and in the harvest |
| `in_families_only` | 15 | cited-family harvest only; AOB has no exact form |
| `in_aob_only` | 2 | `AV.(P.)`, `AdvaiRaRa.` — AOB exact, not in the harvest |
| `index_only` | 3 | `AkaGraTra.`, `AdbhuRāmā.`, `AnekāRaMañ.` — neither source has the exact form |
| `index_blank` | 2 | printed abbreviation cell blank |
| **Index total** | **48** | |

The delta file also carries 1,375 `aob_only` rows for AOB sigla not used on this
page, so both directions of the Index/AOB delta are in one artifact.

## Method and limits

- Images: archive.org item
  `mAAY_an-encyclopaedic-dictionary-of-sanskrit-vol-1-critically-edited-by-a-m-ghatage-1`,
  page API `page/n{leaf}.jpg`, 2030×2738.
- Titles, authors, nature and sigla were read from the page image. The
  `_djvu.txt` Devanagari was not used for titles (as the handoff requires); it
  was only an independent check on the abbreviation column.
- IAST is generated from the transcribed Devanagari with
  `indic_transliteration` (IAST scheme).
- `--draft` mode in the script is a tesseract column-OCR scaffold for S2–S5.
  Its output is deliberately labelled `confidence=ocr-draft` and is **not**
  committed: the Devanagari OCR is not reliable enough to stand as a
  transcription.
- Page mapping uses leaf 98 = LXXXIX, leaf 136 = CXXVII, which matches the
  handoff and the printed numerals.

## S2–S5 backlog

Transcribe leaves 99–136 (`XC`–`CXXVII`), one page at a time, and then publish
the reconciled total and the blank-siglum count over all 39 pages. The page
inventory (`pd_index_works_by_page.tsv`) already lays out all 39 pages so no
shard needs to re-derive the leaf/page map.

## Checks

```text
python scripts/pd_index_works_transcribe.py check
PASS: rows=48, pages=['LXXXIX'], blank_siglum=2, delta_rows=1423
```
