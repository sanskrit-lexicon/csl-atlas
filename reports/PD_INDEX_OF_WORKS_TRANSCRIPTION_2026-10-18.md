# PD Index of Works — full transcription (pp. LXXXIX–CXXVII, H6992)

_Created: 18-10-2026 · Executor: DeepSeek v4.1 Flash (`deepseek/deepseek-flash`) · Handoff: H6992 (S1 of H6989) · Source: archive.org `mAAY_an-encyclopaedic-dictionary-of-sanskrit-vol-1-critically-edited-by-a-m-ghatage-1`_

## Method

Vision transcription from the archive.org page images (2030 x 2738–2753, leaves 98–138; leaves 109–110 are duplicate scans). The `_djvu.txt` Devanagari is unusable and no row in this table comes from it, from tesseract or from Apple Vision OCR. One row per printed work; the abbreviation column is split into `abbreviation_siglum` and `abbreviation_qualifier`; the printed subject subcodes (4.2, 27.1, 54.4 ...) are recorded alongside the integer class; IAST is generated deterministically from the Devanagari with `indic_transliteration`.

## Totals

- rows: **2031** across **39** printed pages
- blank abbreviation cells: **409** (mostly commentary rows; a few are cf./blank cells — printed data, not misses)
- rows flagged `vision-low`: **434**

## Per-page counts

| page | leaf | rows | blank siglum |
|---|---:|---:|---:|
| LXXXIX | 98 | 48 | 2 |
| XC | 99 | 53 | 7 |
| XCI | 100 | 56 | 12 |
| XCII | 101 | 55 | 9 |
| XCIII | 102 | 48 | 6 |
| XCIV | 103 | 48 | 10 |
| XCV | 104 | 55 | 8 |
| XCVI | 105 | 54 | 7 |
| XCVII | 106 | 56 | 10 |
| XCVIII | 107 | 49 | 9 |
| XCIX | 108 | 51 | 12 |
| C | 111 | 49 | 21 |
| CI | 112 | 50 | 11 |
| CII | 113 | 52 | 14 |
| CIII | 114 | 50 | 5 |
| CIV | 115 | 57 | 10 |
| CV | 116 | 50 | 11 |
| CVI | 117 | 54 | 28 |
| CVII | 118 | 55 | 7 |
| CVIII | 119 | 50 | 17 |
| CIX | 120 | 52 | 11 |
| CX | 121 | 50 | 3 |
| CXI | 122 | 52 | 10 |
| CXII | 123 | 54 | 12 |
| CXIII | 124 | 50 | 9 |
| CXIV | 125 | 55 | 5 |
| CXV | 126 | 54 | 8 |
| CXVI | 127 | 50 | 6 |
| CXVII | 128 | 53 | 12 |
| CXVIII | 129 | 53 | 14 |
| CXIX | 130 | 48 | 24 |
| CXX | 131 | 49 | 13 |
| CXXI | 132 | 50 | 8 |
| CXXII | 133 | 53 | 6 |
| CXXIII | 134 | 54 | 4 |
| CXXIV | 135 | 56 | 18 |
| CXXV | 136 | 52 | 14 |
| CXXVI | 137 | 53 | 13 |
| CXXVII | 138 | 53 | 3 |

## Siglum delta against the AOB

- Index rows: 2031; with a siglum: 1622
- statuses: `aob_only` 497, `in_aob_only` 45, `in_both` 936, `in_families_only` 554, `index_blank` 409, `index_only` 87
- Index-only sigla: `AkaGraTra.`, `AdbhuRāmā.`, `AnekāRaMañ.`, `ApohaSi.`, `AbhidhāVṛMā.`, `AbhisaAlaṁĀ.`, `AvadāKaLa.`, `AṣṭādU.`, `ĀtmapūU.`, `ĀnandVṛCam.`, `ĀrṣeKa.`, `ĪśāViṃśU.`, `USaṃ.`, `USamucc.`, `KathāRa.`, `KaviRa.`, `KātanPariVṛ.`, `KādKaSā.`, `KālikāKaSaṃ.`, `KāvyaPradi.`

## Spot-check (10 pages, 18-10-2026)

Ten pages were re-read against the page image after the merge; on each, the first, middle and last row were checked for title, author, subject code/label and siglum.

| page | rows checked | result |
|---|---|---|
| XCIII | 1, 25, 48 | match |
| XCVIII | 1, 25, 49 | match |
| CIII | 1, 26, 50 | match (row 50 title kept as printed, नागरसर्वेख) |
| CVII | 1, 28, 55 | match |
| CXII | 1, 28, 54 | match |
| CXVI | 19-27 | **drift found and corrected** — re-paired from a native-resolution composite and the page re-transcribed |
| CXX | 1, 25, 49 | match |
| CXXIII | 1, 28, 54 | match |
| CXXV | 1, 27, 52 | match |
| CXXVII | 1, 27, 53 | match |

**Known limitation.** On several pages the letterpress sets the subject/abbreviation columns on an independent leading, so they drift against the title column (worst on CVI, CXVI, CXIX, CXXIII, CXXIV). Those pages were paired by printed order and by the siglum's own reading against the title; the CXVI block is the one case where the first pass was wrong and was corrected in the spot-check. Rows flagged `vision-low` are the honest residue: blank printed cells and character-level doubts.

## Rights

PD is CC BY-NC-SA 3.0 (grill decision, `PD_ACC_NCC_GRILL_DECISIONS_2026-10-18.md`). This transcription is a derived finding layer published with attribution; no combined dump with the ACC/NCC enrichment columns is published before a rights check.

## Reproduce

```
python3 scripts/build_pd_index_works.py --shards <shard-dir> --write --check
```
