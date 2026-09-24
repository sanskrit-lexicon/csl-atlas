_Created: 24-09-2026 · Last updated: 24-09-2026_

# Megastructure catalogue — schema and all nine dictionaries

H5324 (E014) piloted the schema on SKD and MW; H5325 filled the other seven (PWG, PW, AP90, WIL, VCP, ARMH, ABCH) without changing it. This catalogue records the **megastructure** of the narrative dictionaries: the front and back matter around the entry list. That means title pages, prefaces, keys, source lists, supplements and genealogies. Each part is one record, and each record points to the scan page it came from. As of 24-09-2026 all nine dictionaries validate against `schemaVersion` 1.0.0: 91 parts over 15 scan sets.

## Files

1. **Schema:** [data/schema/megastructure-component.schema.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/schema/megastructure-component.schema.json) — JSON Schema draft 2020-12, `schemaVersion` 1.0.0.
2. **Per-dictionary records:** [data/megastructure/skd.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/megastructure/skd.json) and [data/megastructure/mw.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/megastructure/mw.json). They are written by the fill scripts [scripts/megastructure/skd_components.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/megastructure/skd_components.py) and [scripts/megastructure/mw_components.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/megastructure/mw_components.py). Edit the script and re-run it; do not hand-edit the JSON.
3. **Scan inventory:** [data/megastructure/scan_inventory.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/megastructure/scan_inventory.tsv). It has one row per declared scan page of every dictionary, 251 rows today. The validator uses it to prove coverage. A scan set declares the pages that bear on the megastructure, not every page of the dictionary: MW declares 62 of its hundreds of pages, and ARMH declares 2 of its 101.
4. **Envelope:** `npm run build-megastructure` runs [scripts/build-megastructure.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-megastructure.mjs). It writes `src/data/megastructure/megastructure_catalogue.json` and its `.source.json` envelope, which carries the CC-BY-SA-4.0 licence fields and the sibling source pins.
5. **Validator:** `npm run validate-megastructure` runs [scripts/validate-megastructure.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/validate-megastructure.mjs). Tests are in [test/megastructure.test.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/test/megastructure.test.mjs), and `npm test` runs them.

## What one record holds

| Field | Meaning |
|---|---|
| `componentType` | One of 25 kinds: title page, preface, sigla key, abbreviation list, source list, supplement, genealogy, and so on. A part that fits none gets `other` plus a `componentTypeNote`. |
| `extent` | Printed pages (fractions allowed when parts share a page), the printed range verbatim, and an optional item count with its unit. |
| `function` | What the part does for the reader: identify, frame, instruct, decode, source, supplement, attest, commemorate. Extra roles go in `secondaryFunctions`. |
| `decodes` | Which body notation the part explains. Each entry gives the target, the csl-orig markup the notation sits in, how the part explains it, and the csl-atlas file that already applies it, if one exists. |
| `scanLocus` | One or more scan pages. Each names a declared scan set, a page ref or a range `first..last`, the image file and the printed page number. |
| `evidenceLevel` + `evidence` | observed / derived / inferred / reviewed, following the [csl-standards crosswalk](https://github.com/sanskrit-lexicon/csl-standards/blob/main/docs/EVIDENCE_LABEL_CROSSWALK.md), plus a concrete note on what was looked at. |
| `digitalDisposition` | What Cologne's digital edition did with the part: not digitized, transcribed (OCR or docx), structured data (a display table), or merged into the entry file. |
| `parent`, `sequence`, `position` | Parts can nest, such as introduction sections. `sequence` is print order, not scan-file order. `position` is front, back or inset. |

Three catalogue-level lists keep the records honest:

1. `excludedScans` — scan pages that deliberately belong to no part, such as a copy's library-stamp leaf.
2. `knownGaps` — parts known to exist in print that no scan shows.
3. `misfits` — facts the schema could not hold without bending. H5325 reads this list to decide whether schema 1.1 is owed.

## What the validator enforces

1. **Schema:** checked by a built-in checker. The repo has no JSON Schema library, so the checker covers exactly the keywords the schema uses. Any other keyword is an error, so a later schema edit cannot be skipped silently.
2. **Ids:** unique, of the form `<dict>.<fm|bm|in>.<slug>`. The prefix must match the file's dict code, and the section must match `position`.
3. **Order and nesting:** sequences are unique; parents exist and never loop; an `other` type carries its note; every `atlasRef` path exists.
4. **Coverage:** every page of every declared scan set is either covered by some part's `scanLocus` or listed in `excludedScans`. This proves the stop condition: "every front and back matter component recorded with a scan locus".
5. **Freshness:** the committed build output must match a fresh build.
6. **Evidence re-measurement:** when `../csl-orig` and `../csl-pywork` are checked out, the MW counts quoted in the evidence strings are measured again. When the siblings are absent, this is logged as a note, not an error, so CI stays green.

## Pilot results (24-09-2026)

| Dict | Parts | Top-level | Front / back | Decode body notation | Scan pages covered | Known gaps | Misfits |
|---|---|---|---|---|---|---|---|
| SKD | 27 | 8 | 27 / 0 | 6 | 30 / 30 csldoc | 3 | 2 |
| MW | 15 | 9 | 14 / 1 | 7 | 29 / 29 csldoc · 62 / 62 PDFs (1 excluded) | 0 | 2 |

### SKD — Śabdakalpadruma (Chowkhamba third edition, 1961, of the Vasu Devanāgarī edition of Śaka 1808)

1. **Order of the front matter:**
   1. two Chowkhamba reprint title pages and the publisher's note
   2. the 1886 title page
   3. a four-page verse preface (*bhūmikā*)
   4. eight pages of testimonials
   5. the *mukhabandhana*: 13 pages, 17 headed sub-sections, recorded as 19 child records. The genealogy (*vaṃśavarṇana*, scans 28–33) closes it and is one of the children.
   6. a *varṇamālā* table
2. **The *mukhabandhana* is the key the body depends on.** Its *sāṅketika* sub-section decodes the gender abbreviations (puṃ/strī/klī/tri), the daṇḍa conventions and the synonym numbering. Its *anubandha* list (46 letters) is the key [docs/MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md) already applies. The *paripāṭī* sub-section explains the va/ba ordering and the empty-anubandha mark; [docs/MICROSTRUCTURE_ZERO_MEANING.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_ZERO_MEANING.md) applies that one.
3. **The source lists are countable:** 29 dictionaries the author obtained (*prāpta*), 32 he did not (*aprāpta*, 10 + 22), and 35 Amara commentaries. The *Vedanighaṇṭu* sub-section is an embedded text of 1,769 words.
4. **No back matter was scanned.** The scan map ends at vol. 5 p. 555. The title pages of parts 2–5 are also unscanned, and so is the first (Bengali-script) edition's seventh-kāṇḍa preface with its index and sigla. All three are recorded in `knownGaps`.

### MW — Monier-Williams 1899 (scanned from an Oxford University Press reprint)

1. **Front matter in print order:**
   1. title page, half-title, OUP imprint
   2. Preface v–x, ending in the Postscript of 4 May 1899
   3. Introduction xi–xxxii, sections I–V
   4. List of Works and Authors xxxiii–xxxiv
   5. Abbreviations xxxv
   6. an ordering note on xxxvi
2. **The last four pages are not in csldoc and were never OCR'd.** They exist only in the Cologne page PDFs t03–t06. Two of them survive as display tables:
   1. the source list as `mwauth/tooltip.txt`: 871 rows, of which 604 are printed rows and 267 are Cologne additions
   2. the abbreviations as `mwab_input.txt`: 424 rows
3. **Back matter:** the Additions and Corrections, pp. 1308–1333. Cologne did not keep it as a separate part; its content is merged into `mw.txt`:
   1. 7,096 records carry `<info n="sup"/>`. 6,220 of them are new entries with a decimal L number, placed after the entry they follow; 876 are existing entries with an integer L.
   2. 279 `<info n="rev">` markers flag corrected entries. 269 point back to a supplement page and column, 5 are marked `pc="cdsl"` (Cologne's own revisions), and 5 have no page.
   3. There are also 15 `<listinfo n="rev"/>` markers.
4. **Section II of the introduction decodes:**
   1. the root-and-derivative arrangement, which the csl-orig `<e>` level codes encode
   2. the homonym figures, encoded as `<hom>`
   3. the reference policy, encoded as `<ls>`
5. **Section IV of the introduction** decodes the transliteration.

## Fill results (H5325, 24-09-2026)

One commit per dictionary, in the handoff's order except that AP90 was filled after VCP. Every scan page that a record cites was viewed, and the edition facts were read off the title pages where they exist.

| Dict | Parts | Front / back | Scan sets (pages declared) | Known gaps | Misfits |
|---|---|---|---|---|---|
| PWG | 19 | 18 / 1 | pwg-csldoc (27) · pwg-scan-pdf (1) | 2 | 2 |
| PW | 3 | 3 / 0 | pw-csldoc (5) | 2 | 2 |
| WIL | 3 | 3 / 0 | wil-csldoc (6) | 1 | 2 |
| VCP | 8 | 8 / 0 | vcp-csldoc (7) · vcp-scan-pdf (34) | 2 | 2 |
| AP90 | 9 | 6 / 3 | ap90-scan-pdf-tit (15, 1 excluded) · ap90-scan-pdf (18) | 0 | 1 |
| ARMH | 2 | 1 / 1 | armh-scan-pdf (2) | 1 | 2 |
| ABCH | 5 | 4 / 1 | abch-scan-pdf (15, 3 excluded) | 1 | 3 |

### PWG — Böhtlingk & Roth, Sanskrit-Wörterbuch (the great Petersburg dictionary)

1. **Seven volume titles, not one.** Each of the seven parts opens with its own title page; the Vorworte and the abbreviation supplements of parts II-VII are inside the volumes, not at the front of the set.
2. **`pwg-scan-pdf` is a single leaf.** The published scan set declares only the last leaf (`7-1821`), a double-page spread of printed pages 1821-1822; the body scan files (1-1821) are the dictionary itself and are not declared.
3. **The csldoc image order swaps at 06/07**, so the title of the second volume is not adjacent to the first.

### PW — Böhtlingk, kürzere Fassung (1879)

1. **PW is its own dictionary, not an abridgement of the atlas `pwg` entry.** It is the 1879 one-volume *kürzere Fassung*, and its title page says so; the fill records it as a separate edition.
2. The csldoc pages `pw1-000-1` to `pw1-000-5` are the whole front matter; there is no back matter in the scan set.

### WIL — Wilson, Sanskrit-English Dictionary (2nd edition, 1832)

1. The front matter is the title, the Colebrooke dedication and the preface (vii-x). The `tit-001.jpg` page in the t-series duplicates the csldoc title image, so only one scan set is declared.

### VCP — Vācaspatyam (Chowkhamba 1962 reprint)

1. **The treatise comes first.** The scan set opens with a 34-page *Liṅgānuśāsana* block (`pg0001`-`pg0034`) that sits outside `pdffiles.txt` entirely and had to be declared as a hand-built inventory - the schema's misfit list carries it.
2. The csldoc pages (7) cover the title and the prefatory matter of each volume.

### AP90 — Apte, The Practical Sanskrit-English Dictionary (first edition, Poona 1890)

1. **Front matter:** title, printer's imprint (Arya Vijaya Press), preface pp. (1)-(4) signed "Poona, 28th December 1890", directions (5)-(6), explanation of terminations (7)-(9), abbreviations (unnumbered start, (12), (13)). Scan `tit_0012` is a **blank leaf** and is the one excluded page.
2. **Back matter is a numbered appendix, not a supplement:** Appendix I Sanskrit Prosody pp. 1179-1189, II dates of Sanskrit writers pp. 1190-1192, III geographical names pp. 1193-1196, closing the volume's own pagination (body ends p. 1178). All three are transcribed in csldoc (`ap90app1-3.rst`), so their `digitalDisposition` is `transcribed`.
3. The preface promises a separate *Dhātus* volume; it is not in the scans and is recorded as a note, not a gap.

### ARMH — Halāyudha, Abhidhānaratnamālā

1. **Scan number equals printed page number** across the 101-page volume: page 1 (unnumbered) carries the title block *over the opening of the kośa*, and page 101 carries the closing colophon of the fifth kāṇḍa. Only those two pages are inventoried; pages 2-100 are kośa body.
2. **The edition prints an English index in the margins of every page.** It is digitized as `armh_hwextra.txt`, but a recurring in-page apparatus has no schema slot - recorded in the notes and as a misfit.
3. The scanned copy carries no imprint, so the edition is identified from `csl-orig/v02/armh/armhheader.xml` and the Cologne bibliographic entry; Cologne's own "Front Matter" link for ARMH returns HTTP 404, which is the known gap.

### ABCH — Hemacandra, Abhidhānacintāmaṇi (Nirṇaya-sāgara Press, Bombay 1896)

1. **The f-series mixes matter and body.** `f01`-`f11` are the English and Devanagari title pages, the four-page *prastāvanā* and the five-page introduction on Hemacandra; `f12`, `f13` and `f14` are printed pages 2, 3 and 4 of the kośa itself, excluded as body. The numbered series `pg05`-`pg58` is printed pages 5-58.
2. **Printed page 1 is in neither series.** `pg01`-`pg04` return HTTP 404 and `f15`/`f16` do not exist, so the kośa's opening verses are unscanned: the known gap.
3. The volume is item **No. 6** of the six-work *Abhidhānasaṃgraha* collection named on both title pages, but it carries only the Abhidhānacintāmaṇi; the collection relation is a misfit because the schema has no series field.

## Traps for H5325 (read before filling)

1. **csl-orig `*_front.txt`, `*_middle.txt` and `*_back.txt` are page-marker scaffolding, not front matter.** SKD's `skd_back.txt` is empty. Use the csldoc preface pages and the scan maps.
2. **The scan map is the only complete page list.** Its path is `csl-websanlexicon/v02/distinctfiles/<dict>/web/webtc/pdffiles.txt`. For MW, csldoc stops at p. xxxii, and pp. xxxiii–xxxvi only exist as scans.
3. **Cologne scan captions can be wrong.** MW t02, captioned "Copyright", is a blank leaf with a library stamp. MW t07, captioned "Title", is the half-title. Look at the page before trusting its caption.
4. **Scan order is not print order.** MW scans pp. xxxvi–xxxiii before the half-title, and swaps xxix/xxx (files mw010033 and mw010034). `sequence` follows print.
5. **A supplement can live in the body.** Look for decimal L numbers and `<info n="sup">` / `n="rev"` markers before recording a supplement as not digitized.
6. **A copy-specific mark belongs in `excludedScans`, not in a part.** The schema has no copy-level layer, which is a recorded misfit.
7. **The scans must be read as images, and the Read tool does render them.** Convert each PDF to PNG with `pymupdf` (`fitz`) and read the PNG; build a PIL contact sheet to triage a run of pages, then read the promising pages one at a time. Do not assume a text layer: the ABCH scans are Google-digitized and carry none (`get_text()` returns 0 characters on all 14 f-pages), and Tesseract is not installed, so macOS Vision OCR is the only OCR fallback. The `read` tool rendering an image is the fastest path - the H5325 fill used it for every page cited.
8. **Page numbers hide in the header band, and the band side alternates.** On ABCH, odd pages carry the number at the right and even pages at the left; a 7%-height corner crop often misses them. Crop the top 12-14% at 200-350 dpi to read them. The same band confirms which kāṇḍa or section a page opens, which is how the fill found that ABCH's printed page 1 is missing from both scan series.

## Filling a new dictionary (H5325 recipe)

1. Append the dictionary's scan pages to `scan_inventory.tsv`, one row per page per scan set, taken from its csldoc prefaces and its `pdffiles.txt` rows that are not body pages.
2. Copy one of the fill scripts to `scripts/megastructure/<dict>_components.py`. Fill in the parts, run the script, then run `npm run build-megastructure` and `npm run validate-megastructure`.
3. Coverage errors list every page that no part claims. Resolve each one with a part, or with an `excludedScans` entry that gives a reason.
4. Put anything the schema cannot hold into `misfits`. Never change the schema for one dictionary. A schema change is a separate handoff, decided on the pooled misfit list.

## Misfits from the pilot

1. **SKD:** the *mukhabandhana* page numbers are not legible on the scans, so `printedPage` is null. Several sub-sections share pages, so their `pages` values are fractions.
2. **MW:** a library-stamp leaf belongs to the scanned copy, not the edition, and the schema has no copy-level layer. In the works list, `extent.items` holds one count, so the printed/added split (604 printed, 267 Cologne additions) is carried in the evidence text.
3. **Neither pilot needed `other`.** The componentType list held all 42 parts.

## Misfits from the fill (H5325)

1. **A recurring in-page apparatus has no slot.** ARMH prints an English index in the margins of every page; it runs across the whole body, so the component vocabulary (title-page, preface, index, ...) cannot express it, and there is no way to declare its per-page extent once.
2. **A scan set can mix kinds of matter.** ABCH's `f` series is Cologne's front-matter set but its last three pages (f12-f14) are printed body pages 2-4; the schema can only record them individually in `excludedScans`, not as "this set is front matter except its tail".
3. **A title printed on a body page.** ARMH's only title is set at the head of the volume's first body page, so `armh.fm.title-page` points at page 1 while `position` forces the front/back/inset choice.
4. **Series membership and volume-in-series.** ABCH is No. 6 of the six-work *Abhidhānasaṃgraha* named on its title pages, and the volume carries only that one item; the `edition` block has no series, volume or "items absent from this volume" field.
5. **One count per extent.** MW's printed/added split and PW's two-title-page structure both exceed what `extent.items` can hold, so the numbers live in the evidence text.
6. **Scan artefacts still have no layer.** The MW pilot's library-stamp leaf is joined by the 'Digitized by Google' watermark on every ABCH page and AP90's handwritten accession marks: marks of the copy or the digitizer, not of the edition.
7. **Only ARMH, VCP and ABCH needed `excludedScans`; the csldoc-based fills needed none.** The csldoc scan sets are already pure front matter.

_Гасунс_
