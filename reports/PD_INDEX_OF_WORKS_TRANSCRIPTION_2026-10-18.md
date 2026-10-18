# PD Index of Works — pages XC and XCI (vision transcription)

_Created: 18-10-2026 · Last updated: 18-10-2026_

**Handoff:** H6992 (S1 of 5) — refused by `handoff.py go` because merged PR
[#591](https://github.com/sanskrit-lexicon/csl-atlas/pull/591) names it; that PR
delivered **one page of thirty-nine**. This pass is the residue, executed under
the residual handoff minted for the remainder.
· **Data:** [`data/pd/pd_index_works.tsv`](../data/pd/pd_index_works.tsv)
· **Inventory:** [`pd_index_works_by_page.tsv`](../data/pd/pd_index_works_by_page.tsv)
· **Delta:** [`pd_index_works_siglum_delta.tsv`](../data/pd/pd_index_works_siglum_delta.tsv)
· **Summary:** [`pd_index_works_summary.json`](../data/pd/pd_index_works_summary.json)
· **Builder:** [`scripts/pd_index_works_build.py`](../scripts/pd_index_works_build.py)

## What this pass delivers

| Printed page | Leaf | Rows | Blank siglum | Status |
|---|---:|---:|---:|---|
| LXXXIX | 98 | 48 | 2 | S1, unchanged |
| **XC** | **99** | **52** | **7** | **this pass** |
| **XCI** | **100** | **56** | **12** | **this pass** |

Table total: **156 rows over 3 of 39 pages** (36 pages pending). `row_total_full`
stays `null` — a full-Index total from three pages would be an extrapolation,
which the handoff forbids.

## Method

1. **Images.** archive.org item
   `mAAY_an-encyclopaedic-dictionary-of-sanskrit-vol-1-critically-edited-by-a-m-ghatage-1`,
   `page/n{leaf}.jpg`, 2030 × 2753 px (the S1 summary's `2030x2738` is the
   earlier probe's reading; the two pages fetched here measure 2030 × 2753).
2. **Titles, authors, nature and sigla were read from the page image**, column by
   column at native resolution (title/author crops, then a subject/abbreviation
   crop, then a nature-column strip), never from `_djvu.txt`.
3. **`_djvu.xml` was used as a structural skeleton only** — per-word bounding
   boxes give the row geometry and the Latin columns' position, which is what
   makes nature-column attribution exact on multi-line entries. Its Devanagari
   is not OCR'd at all on p. XC and is badly garbled on p. XCI, so it cannot and
   does not supply a title.
4. **The AOB inventory is the second source.** `pd_aob_entries.tsv` carries PD's
   own printed sigla with their Latin titles, so every doubtful reading was
   settled against it: `AbhidhāMañ.` → *Abhidhānamāñjarī*, **Bhīṣagarya** (the
   image's `भिषगार्य`, not the `मिषगार्य` a fast read suggests); `AlaṅkāMañ.` →
   *Alaṃkāramañjūṣā*, **Devāśaṅkara Purohita**; `AlaṅkāRa.` → *Alaṃkāraratnākara*,
   **Śobhākaramitra**; `SadrasaNi.` → *Ṣaḍrasanighaṇṭu or Abhidhānaratnamālā*;
   `AvadāKaLa.` → *Avadānakalpalatā*; `AnyāŚ.(Nī.)` / `AnyāŚ.(Ma.)` →
   *Anyāpadeśaśataka* of Nīlakaṇṭha Dīkṣita / of Madhusūdana; `AnyoŚ.` →
   *Anyoktiśataka* of **Bhāṭṭavīreśvara**.
5. **IAST is generated** from the transcribed Devanagari with
   `indic_transliteration` (IAST scheme), as S1 did.

## Row reconciliation (layout-aware, not OCR line counts)

- **XC = 52 rows.** The XML skeleton yields 46 Latin-bearing lines; the image
  adds 6 rows whose abbreviation cell is blank or whose line the OCR dropped
  (`अलंकारकौस्तुभमुक्तावली`, `अलंकारचन्द्रिका`, `अलंकारविमर्शिनी`, and the three
  commentary rows at 35/50/51). Every printed title was matched to exactly one
  subject/abbreviation line by order and confirmed by semantics (siglum ↔ title).
- **XCI = 56 rows.** The XML skeleton yields 55 lines; the image shows 56
  (`आत्मोपनिषद्` prints twice, `१` and `२`, with sigla `ĀtmaU.₁`/`ĀtmaU.₂`).
- **Page-break duplication, recorded not doubled.** `अवधूतोपनिषद्` prints at the
  foot of XC *and* at the head of XCI. It is counted **once**, on XCI — where its
  title, subject (`4.2`) and siglum (`AvadhūU.`) all print — and XC therefore
  closes at `अवदानकल्पलता`. The pilot TSV also places it on XCI.

## Canary: the 19 pilot rows

| Result | Rows |
|---|---:|
| siglum found, page + subject identical | 16 |
| page differs: `AṣṭāHṛ.` pilot XC → **XCI** | 1 |
| siglum form differs from S1's own LXXXIX transcription | 2 |

- The `AṣṭāHṛ.` difference is a **pilot page-attribution error**, not a reading
  difference: the pilot sampled five pages with a continuous row counter, and
  `अष्टाङ्गहृदय` is printed on XCI (row 12), between `अष्टाङ्गसंग्रह` and
  `अष्टादश उपनिषदः`. The image is authoritative.
- The two siglum-form differences (`AkṣMaU.` pilot vs `AksMāU.` in the table;
  `AnekāSaṃ.` pilot vs `AnekāSam.`) come from **S1's committed LXXXIX rows**,
  which this pass did not touch — the first 48 data rows are byte-identical to
  `origin/main`. They are listed here so the next pass can adjudicate them
  against p. LXXXIX itself rather than inherit them silently.

## Delta parity

`scripts/pd_index_works_build.py` regenerates the siglum delta from the table.
**Its status set for the 48 LXXXIX rows is identical to the committed delta**
(`in_both 26`, `in_families_only 15`, `index_only 3`, `in_aob_only 2`,
`index_blank 2`) — the generator reproduces S1's reconciliation exactly, which is
what licenses the same generator for the new pages.

Over the 156 transcribed rows: `in_both 83`, `in_families_only 39`, `index_only 9`,
`in_aob_only 4`, `index_blank 21`.

## Where the OCR would have lied (image wins)

| Line | OCR reading | Printed | Note |
|---|---|---|---|
| `अष्टाङ्गनिघण्टु` | subject `43` | `42 Medicine` | digit misread |
| `अष्टाङ्गसंग्रह` | subject `49` | `42 Medicine` | digit misread (`9`↔`2`) |
| `अभिधानमञ्जरी` | subject `49` | `42 Medicine` | digit misread |
| `अन्यापदेशशतक` | siglum `AnyaS` | `AnyāŚ.` | diacritic loss |
| XC row 33/35 | nature lines shifted | `अथर्ववेदपरिशिष्ट` belongs to `अमोघनन्दिनीशिक्षा`; `comm. on सौन्दर्यलहरी` belongs to `अरुणामोदिनी` | resolved from the image at row alignment |

## Printed subject subcodes

New in this pass: `4.3` (2 rows, XCI), `6`, `7`, `9`, `16`, `17.3`, `21`, `24`,
`26`, `32`, `35`, `39.1`, `45`, `56`, `58`, `61`, plus the subcodes already seen
on LXXXIX. **47 distinct subcodes over 156 rows**; the integer part is kept in
`subject_class_no` so H6946's 62 integer classes are unchanged. `4.3` is a
subcode H6946 does not yet carry — flagged for the composition stream (H6994).

## Spot-check (2 pages, image ↔ AOB)

- XC: 46 sigla checked against `pd_aob_entries.tsv`; 4 resolved only through the
  AOB title (`AbhidhāMañ.`, `AlaṅkāMañ.`, `AlaṅkāRa.`, `SadrasaNi.`); 3 confirmed
  blank (`अभिधानचिन्तामणिटीका`, `अरुणामोदिनी`, `अलंकारकौस्तुभमुक्तावली`,
  `अलंकारचन्द्रिका`, `अलंकारविमर्शिनी`, `अवचूरि` ×2).
- XCI: 44 sigla checked; `ĀtmaU.` qualifiers `1`/`2` split from the siglum, not
  merged; `ĀpaManPāṭha.` confirmed as printed (no space).

## Backlog (resume pointer)

**36 pages: XCII–CXXVII (leaves 101–136).** One page = one fragment; run
`python scripts/pd_index_works_build.py rows/<PAGE>.tsv` to append. Leaves
103–107, 116 and 134 failed to fetch in this session (archive.org resets) —
retry `page/n{leaf}.jpg` before starting XCII.

## Checks

```text
python scripts/pd_index_works_build.py --check
{"rows": 156, "pages": ["LXXXIX", "XC", "XCI"], "blank_siglum": 21}

git diff origin/main -- data/pd/pd_index_works.tsv | head   # 48 old rows untouched
LXXXIX delta statuses == committed delta                     # parity, see above
pilot canary: 16/19 identical, 1 page fix, 2 inherited forms  # see above
```
