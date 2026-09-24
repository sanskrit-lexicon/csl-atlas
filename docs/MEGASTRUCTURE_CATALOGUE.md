_Created: 24-09-2026 · Last updated: 25-09-2026_

# Megastructure catalogue — schema and the SKD + MW pilot

H5324 (E014). This catalogue records the **megastructure** of the narrative dictionaries: the front and back matter around the entry list. That means title pages, prefaces, keys, source lists, supplements and genealogies. Each part is one record, and each record points to the scan page it came from. This pilot fills the schema for SKD and MW. H5325 fills it for the other seven dictionaries (PWG, PW, AP90, WIL, VCP, ARMH, ABCH) without changing the schema.

## Files

1. **Schema:** [data/schema/megastructure-component.schema.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/schema/megastructure-component.schema.json) — JSON Schema draft 2020-12, `schemaVersion` 1.0.0.
2. **Per-dictionary records:** [data/megastructure/skd.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/megastructure/skd.json) and [data/megastructure/mw.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/megastructure/mw.json). They are written by the fill scripts [scripts/megastructure/skd_components.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/megastructure/skd_components.py) and [scripts/megastructure/mw_components.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/megastructure/mw_components.py). Edit the script and re-run it; do not hand-edit the JSON.
3. **Scan inventory:** [data/megastructure/scan_inventory.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/megastructure/scan_inventory.tsv). It has one row per scan page of every declared scan set, 121 rows today. The validator uses it to prove coverage.
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

## Fill state after H5325 (25-09-2026)

Four of the seven remaining dictionaries are catalogued at **block level**: every front/back scan page of ap90, wil, abch and vcp is claimed, but the pages are not yet identified one by one, so each front block is one `other`-type component at evidence level `inferred`. The schema stayed at 1.0.0; the pooled `misfits` now carry what a follow-up scan-reading pass must resolve.

| Dict | Scan pages catalogued | Components | Evidence | Finding |
|---|---|---|---|---|
| ap90 | 15 (t0001–t0015 `tit_*.pdf`) | title page + 14-page front block | inferred | Cologne also digitizes two front tables: `ap90ab_input.txt` (91 rows), `ap90auth/tooltip.txt` (330 rows) — placement inside the block unknown (misfit). |
| wil | 6 (t001–t006 `tit-*.jpg`) | title page + 5-page front block | inferred | Direct scan URL probe 404s; images named by the scan map only. |
| abch | 14 (f01–f14 `f*.pdf`) | title page + 13-page front block | inferred | Body print pages 1–4 are absent from the scan map (body starts at pg05) — `knownGap`. |
| vcp | 34 (pg0001–pg0034) | 34-page front block | inferred | The scan map **omits** these pages (`pdffiles.txt` starts at pg0035) while the PDFs are served (HTTP 200 probes 25-09-2026) — misfit. |

Census of the remaining three scan maps (25-09-2026, `csl-websanlexicon pdffiles.txt`): **pwg, pw and armh list no non-body pages at all** (pwg 4,747/4,747 body rows 1-0001–7-1821; pw 2,127/2,127 rows 1-001–7-390; armh 101/101 rows with the first body entry on scan 0001). Their front matter exists in print but no Cologne scan set shows it, so no components can be minted from these maps — full nine-dictionary coverage needs unlisted scans (or external witnesses such as archive.org), which is a separate unit. armh and abch are both the Abhidhānacintāmaṇi of Hemacandra in two Cologne editions.

Validator after this pass: 6 dictionaries, 49 components, every declared scan set 100 % covered.

## Traps for H5325 (read before filling)

1. **csl-orig `*_front.txt`, `*_middle.txt` and `*_back.txt` are page-marker scaffolding, not front matter.** SKD's `skd_back.txt` is empty. Use the csldoc preface pages and the scan maps.
2. **The scan map is the only complete page list.** Its path is `csl-websanlexicon/v02/distinctfiles/<dict>/web/webtc/pdffiles.txt`. For MW, csldoc stops at p. xxxii, and pp. xxxiii–xxxvi only exist as scans.
3. **Cologne scan captions can be wrong.** MW t02, captioned "Copyright", is a blank leaf with a library stamp. MW t07, captioned "Title", is the half-title. Look at the page before trusting its caption.
4. **Scan order is not print order.** MW scans pp. xxxvi–xxxiii before the half-title, and swaps xxix/xxx (files mw010033 and mw010034). `sequence` follows print.
5. **A supplement can live in the body.** Look for decimal L numbers and `<info n="sup">` / `n="rev"` markers before recording a supplement as not digitized.
6. **A copy-specific mark belongs in `excludedScans`, not in a part.** The schema has no copy-level layer, which is a recorded misfit.
7. **The Read tool refuses scan images here.** View the public csldoc and PDF URLs in a browser instead. Tesseract is not installed, and macOS Vision OCR cannot read Devanāgarī.

## Filling a new dictionary (H5325 recipe)

1. Append the dictionary's scan pages to `scan_inventory.tsv`, one row per page per scan set, taken from its csldoc prefaces and its `pdffiles.txt` rows that are not body pages.
2. Copy one of the fill scripts to `scripts/megastructure/<dict>_components.py`. Fill in the parts, run the script, then run `npm run build-megastructure` and `npm run validate-megastructure`.
3. Coverage errors list every page that no part claims. Resolve each one with a part, or with an `excludedScans` entry that gives a reason.
4. Put anything the schema cannot hold into `misfits`. Never change the schema for one dictionary. A schema change is a separate handoff, decided on the pooled misfit list.

## Misfits from the pilot

1. **SKD:** the *mukhabandhana* page numbers are not legible on the scans, so `printedPage` is null. Several sub-sections share pages, so their `pages` values are fractions.
2. **MW:** a library-stamp leaf belongs to the scanned copy, not the edition, and the schema has no copy-level layer. In the works list, `extent.items` holds one count, so the printed/added split (604 printed, 267 Cologne additions) is carried in the evidence text.
3. **Neither pilot needed `other`.** The componentType list held all 42 parts.

_Гасунс_
