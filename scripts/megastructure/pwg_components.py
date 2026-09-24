"""Emit data/megastructure/pwg.json - the PWG megastructure record (H5325).

Hand-curated records kept as Python so each record stays one readable call;
run once to regenerate the committed JSON:  python scripts/megastructure/pwg_components.py

Evidence: all 27 csldoc pages (pwgpref01-27 images in csl-doc/source/images)
viewed 24-09-2026; vol-7 back-matter tail cross-checked against the Cologne
scan leaf pwg7-1821.pdf (printed pp. 1821-1822) and csl-orig/v02/pwg/pwg.txt
(L=122695..122732).
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "data" / "megastructure" / "pwg.json"

# csldoc reading order (pwgpref01-27) -> scan image in csl-doc/source/images.
# csldoc pages 06/07 show the images in swapped file order (rst06 -> --07.png,
# rst07 -> --06.png); the rst assigns them correctly.
CSLDOC = [
    ("01", "pwg1-0000--01.png", "Title, vol. 1"),
    ("02", "pwg1-0000--02.png", "Foreword, 1"),
    ("03", "pwg1-0000--03.png", "Foreword, 2"),
    ("04", "pwg1-0000--04.png", "Foreword, 3"),
    ("05", "pwg1-0000--05.png", "Foreword, 4"),
    ("06", "pwg1-0000--07.png", "Foreword, 5"),
    ("07", "pwg1-0000--06.png", "Abbreviations, 1"),
    ("08", "pwg1-0000--08.png", "Abbreviations, 2"),
    ("09", "pwg1-0000--09.png", "Abbreviations, 3"),
    ("10", "pwg1-0000--10.png", "Abbreviations, 4"),
    ("11", "pwg1-0000--11.png", "Abbreviations, 5"),
    ("12", "pwg2-0000--01.png", "Title, vol. 2"),
    ("13", "pwg2-0000--02.png", "Addenda to vol. 1"),
    ("14", "pwg2-0000--03.png", "Addenda to vol. 2"),
    ("15", "pwg2-0000--04.png", "Foreword, 2-1"),
    ("16", "pwg2-0000--05.png", "Abbreviations, 2-1"),
    ("17", "pwg3-0000--01.png", "Title, vol. 3"),
    ("18", "pwg3-0000--02.png", "Foreword, 3-1"),
    ("19", "pwg3-0000--03.png", "Foreword, 3-2"),
    ("20", "pwg4-0000--01.png", "Title, vol. 4"),
    ("21", "pwg4-0000--02.png", "Foreword, 4-1"),
    ("22", "pwg5-0000--01.png", "Title, vol. 5"),
    ("23", "pwg5-0000--02.png", "Foreword, 5-1"),
    ("24", "pwg5-0000--03.png", "Foreword, 5-2"),
    ("25", "pwg6-0000--01.png", "Title, vol. 6"),
    ("26", "pwg7-0000--01.png", "Title, vol. 7"),
    ("27", "pwg7-0000--02.png", "Foreword, 7-1"),
]


def loc(ref, printed=None):
    image = dict((r, i) for r, i, _ in CSLDOC)[ref]
    return {"scanSet": "pwg-csldoc", "ref": ref, "image": image, "printedPage": printed}


def locs(first, last, printed=None):
    a = int(first); b = int(last)
    return [loc(f"{n:02d}", (printed[n - a] if printed else None)) for n in range(a, b + 1)]


def comp(cid, seq, ctype, fn, title, extent, scan, disposition, evidence, level="observed",
         langs=("deu",), decodes=(), transcriptions=(), parent=None, notes=None,
         secondary=(), ctype_note=None, position="front"):
    return {"id": cid, "sequence": seq, "position": position, "componentType": ctype,
            "componentTypeNote": ctype_note, "function": fn, "secondaryFunctions": list(secondary),
            "title": title, "languages": list(langs), "extent": extent, "decodes": list(decodes),
            "scanLocus": scan, "digitalDisposition": disposition, "transcriptions": list(transcriptions),
            "parent": parent, "evidenceLevel": level, "evidence": evidence, "notes": notes}


def ext(pages, printed=None, items=None, unit=None):
    return {"pages": pages, "printedRange": printed, "items": items, "itemsUnit": unit}


def t(deu, english):
    return {"asPrinted": deu, "iast": None, "english": english}


ABBR1 = "pwg.fm.abbreviations"
VORW1 = "pwg.fm.vorwort"

components = [
    comp("pwg.fm.title-v1", 1, "title-page", "identify",
         t("SANSKRIT-WÖRTERBUCH ... ERSTER THEIL. DIE VOCALE.", "Title page of volume 1, 'Die Vocale' (vowels), St. Petersburg 1855"),
         ext(1), [loc("01")], "not-digitized",
         "csldoc pwgpref01 scan viewed 24-09-2026: 'Sanskrit-Wörterbuch, herausgegeben von der Kaiserlichen Akademie der Wissenschaften, bearbeitet von Otto Böhtlingk und Rudolph Roth. Erster Theil. Die Vocale. St. Petersburg 1855'; Bodleian library stamps top and bottom.",
         notes="Volume 1 covers the vowel-initial alphabet; the copy carries Oxford (Bodleian) provenance stamps."),
    comp(VORW1, 2, "preface", "frame", t("VORWORT.", "Preface (Vorwort) of Böhtlingk and Roth to volume 1"),
         ext(5, "III-VII"), locs("02", "06", [None, "IV", "V", "VI", "VII"]), "not-digitized",
         "csldoc pwgpref02-06 scans viewed 24-09-2026: pp. IV-VII carry printed numbers; p. III inferred for the first page (unnumbered strip obscured by the scan caption; IV follows).",
         secondary=["decode", "source"],
         decodes=[
             {"target": "root citation form: the vocalic ṛ-ending vowels banned from verbal roots",
              "markup": "root entries cited with √ and the ¦ separator in pwg.txt (e.g. '√{#sparh#}¦')",
              "mechanism": "p. VII: 'Wir haben aus den Verbalwurzeln die Vocale ऋ, ङृ und ङॄ verbannt' and replaced final ऋ of nominal stems with अर्; root vowels are normalised in the headwords.",
              "atlasRef": None},
             {"target": "accent marking in vedic quotations",
              "markup": None,
              "mechanism": "p. VII: accents marked 'auf die einfachste, bei den Indern aber nicht gangbare Weise'; in Veda quotations the manuscript notation is kept.",
              "atlasRef": None},
             {"target": "division of labour behind the entries",
              "markup": None,
              "mechanism": "p. VII: Roth worked the Vedic literature and Suśruta Saṃhitā plus botany, Böhtlingk the rest and the ordering.",
              "atlasRef": None}],
         notes="p. IV announces the 'besonderes Verzeichniss am Ende des Vorworts' of printed and manuscript sources used - realised as the following abbreviation list. p. VII carries a footnote quoting Rādhākānta Deva's letter of 17 May 1855 on the second SKD edition."),
    comp(ABBR1, 3, "abbreviation-list", "decode",
         t("ERKLÄRUNG DER ABKÜRZUNGEN.", "Explanation of the abbreviations (key to the works and authors cited)"),
         ext(5, "VIII-XII"), locs("07", "11", [None, "IX", "X", "XI", "XII"]), "not-digitized",
         "csldoc pwgpref07-11 scans viewed 24-2026: p. IX = 'IX', pp. X-XII printed; first page unnumbered in the caption strip (VIII by sequence, IX follows). Two-column list over pp. VIII-XII ending with the ornament after 'Zur L. u. G. d. W. (Roth)'.",
         secondary=["source"],
         decodes=[
             {"target": "literary source abbreviations in entries", "markup": "<ls> in pwg.txt",
              "mechanism": "siglum = full title with editor and edition, e.g. 'CKDr. = ÇABDAKALPADRUMA (Gild. Bibl. 371)', 'H. = Hemacandra's Abhidhānakintāmaṇi ... St. Petersburg 1847', 'HALĀ. = HALĀYUDHA, ein Lexicograph'; a star marks works only occasionally cited.",
              "atlasRef": None},
             {"target": "page-and-line citation convention (simple number = çloka, double = page and line)",
              "markup": "<ls> numeric suffixes in pwg.txt",
              "mechanism": "head-note on p. VIII and repeated per entry, e.g. under ÇAK.: 'Eine einfache Zahl bezeichnet den Çloka, eine doppelte Seite und Zeile.'",
              "atlasRef": None}],
         notes="The list interleaves printed works and manuscripts ('Hdschr.'), and names the dictionaries of the Indian tradition (CKDr., H., HALĀ., NĀNĀRTHAK., RĀJĀN., RATNAM.) alongside Vedic, philosophical and literary editions."),
    comp("pwg.fm.title-v2", 4, "title-page", "identify",
         t("SANSKRIT-WÖRTERBUCH ... ZWEITER THEIL. क—ह.", "Title page of volume 2, क to ह, St. Petersburg 1858"),
         ext(1), [loc("12")], "not-digitized",
         "csldoc pwgpref12 scan viewed 24-09-2026: 'Zweiter Theil. क - ह. St. Petersburg 1858'."),
    comp("pwg.fm.corrigenda-v1", 5, "corrigenda", "supplement",
         t("Nachträgliche Verbesserungen zum 1. Theile.", "Corrections to Part 1, printed at the front of Part 2"),
         ext(3, None, None, "corrections"), locs("13", "14", [None, "11"]), "not-digitized",
         "csldoc pwgpref13-14 scans viewed 24-09-2026: p. 11 (numbered) shows the tail of the Part-1 corrections; its first page unnumbered. The verso between the two scanned pages is not in the scan set.",
         secondary=["decode"],
         notes="One-line corrections by article number ('S. 8, Art. ... lies: ...'). Part-1 page 10 (verso) is not scanned - the two csldoc pages are not consecutive printed leaves."),
    comp("pwg.fm.corrigenda-v2", 6, "corrigenda", "supplement",
         t("Verbesserungen zum 2. Theile.", "Corrections to Part 2 itself, printed under the Part-1 list"),
         ext(0.9, "11", None, "corrections"), [loc("14", "11")], "not-digitized",
         "csldoc pwgpref14 scan viewed 24-09-2026: heading 'Verbesserungen zum 2. Theile' on p. 11, list complete on the page, closing ornament.",
         parent="pwg.fm.corrigenda-v1",
         notes="Recorded as a child of the corrigenda block so the shared page 11 is held once."),
    comp("pwg.fm.vorwort-v2", 7, "preface", "frame", t("VORWORT.", "Preface to Part 2 (1858)"),
         ext(1), [loc("15")], "not-digitized",
         "csldoc pwgpref15 scan viewed 24-09-2026: single page, complete, signed 'St. Petersburg, Tübingen, den 14/26 October 1858'; states Part 2 closes with the cerebral ष and anticipates Part 3 finishing the dentals.",
         notes="Acknowledges Dr. Kern's contributions from the letter प onwards."),
    comp("pwg.fm.abbreviations-v2", 8, "abbreviation-list", "decode",
         t("Erklärung der im 2. Theile neu hinzugekommenen Abkürzungen.", "Abbreviations newly added in Part 2"),
         ext(1), [loc("16")], "not-digitized",
         "csldoc pwgpref16 scan viewed 24-09-2026: single two-column page ending with the ornament; adds e.g. 'MOLSW. = A Dictionary Murathee and English by James T. Molesworth. Bombay 1831', 'KAP. = Kapila (The Aphorisms of the Sankhya Philosophy ...)'",
         secondary=["source"],
         decodes=[{"target": "source abbreviations first used from the letter क onwards", "markup": "<ls>",
                   "mechanism": "siglum = full title with edition, same convention as the volume-1 list.", "atlasRef": None}]),
    comp("pwg.fm.title-v3", 9, "title-page", "identify",
         t("SANSKRIT-WÖRTERBUCH ... DRITTER THEIL. त—भ.", "Title page of volume 3, त to भ, St. Petersburg 1861"),
         ext(1), [loc("17")], "not-digitized",
         "csldoc pwgpref17 scan viewed 24-09-2026: 'Dritter Theil. त - भ. St. Petersburg 1861'."),
    comp("pwg.fm.vorwort-v3", 10, "preface", "frame", t("VORWORT.", "Preface to Part 3 (1861)"),
         ext(1), [loc("18")], "not-digitized",
         "csldoc pwgpref18 scan viewed 24-09-2026: single page signed 'Otto Böhtlingk. Rudolph Roth.', 'St. Petersburg, Tübingen, den 1/13 Juli 1861'; announces the Bhartṛhari text collated for the dictionary and refers new abbreviations to the following list.",
         notes="p. 1861 footnote corrects three Benfrey readings (Pañcatantra)."),
    comp("pwg.fm.abbreviations-v3", 11, "abbreviation-list", "decode",
         t("Erklärung der im dritten Theile neu hinzugekommenen Abkürzungen.", "Abbreviations newly added in Part 3"),
         ext(1), [loc("19")], "not-digitized",
         "csldoc pwgpref19 scan viewed 24-09-2026: single page; adds the Paris-manuscript and Buddhist sigla communicated by A. Schiefner (Buddhoc., Dççabh., Kālçav., Kathināv. ...) and Goldstücker's Manava-kalpa-sutra.",
         secondary=["source"],
         decodes=[{"target": "source abbreviations first used in Part 3", "markup": "<ls>",
                   "mechanism": "siglum = full title; manuscript sources marked 'handschriftlich in der Pariser Bibliothek, nach Mittheilungen von A. Schiefner'.", "atlasRef": None}],
         notes="csldoc files this page as 'Foreword, 3-2'; the scan shows the abbreviation list, not a second foreword page."),
    comp("pwg.fm.title-v4", 12, "title-page", "identify",
         t("SANSKRIT-WÖRTERBUCH ... VIERTER THEIL. न—फ.", "Title page of volume 4, न to फ, St. Petersburg 1865"),
         ext(1), [loc("20")], "not-digitized",
         "csldoc pwgpref20 scan viewed 24-09-2026: 'Vierter Theil. न - फ. St. Petersburg 1865'."),
    comp("pwg.fm.vorwort-v4", 13, "preface", "frame", t("VORWORT.", "Preface to Part 4 (1865)"),
         ext(1), [loc("21")], "not-digitized",
         "csldoc pwgpref21 scan viewed 24-09-2026: single page signed 'O. Böhtlingk. R. Roth.', 'Den 17/29. November 1864'; measures progress against Wilson's second edition (3/8 done in 12.5 years) and thanks Whitney for the American Oriental Society inscription index.",
         notes="Regrets Dr. Kern's move to Benares reducing contributions for the letter प."),
    comp("pwg.fm.title-v5", 14, "title-page", "identify",
         t("SANSKRIT-WÖRTERBUCH ... FÜNFTER THEIL. फ—य nebst Nachträgen und Verbesserungen von फ—य.", "Title page of volume 5, फ to य with additions and corrections for फ-य, St. Petersburg 1868"),
         ext(1), [loc("22")], "not-digitized",
         "csldoc pwgpref22 scan viewed 24-09-2026: subtitle 'फ - य nebst Nachträgen und Verbesserungen von फ - य. St. Petersburg 1868'."),
    comp("pwg.fm.vorwort-v5", 15, "preface", "frame", t("VORWORT.", "Preface to Part 5 (1868)"),
         ext(2), locs("23", "24"), "not-digitized",
         "csldoc pwgpref23-24 scans viewed 24-09-2026: two pages, complete, signed 'Otto Böhtlingk. Rudolph Roth.', 'St. Petersburg, Tübingen, den 1. (13.) Mai 1868'; discusses the Bombay vs Calcutta व/ब evidence, the relation of a Handwörterbuch to a large dictionary, and transliteration policy.",
         secondary=["decode"],
         notes="Footnote: 'Whitney's Nachträge, die zu spät eintrafen, werden am Schluss des Werkes mitgetheilt werden.'"),
    comp("pwg.fm.title-v6", 16, "title-page", "identify",
         t("SANSKRIT-WÖRTERBUCH ... SECHSTER THEIL. य—व.", "Title page of volume 6, य to व, St. Petersburg 1871"),
         ext(1), [loc("25")], "not-digitized",
         "csldoc pwgpref25 scan viewed 24-09-2026: 'Sechster Theil. य - व. St. Petersburg 1871'."),
    comp("pwg.fm.title-v7", 17, "title-page", "identify",
         t("SANSKRIT-WÖRTERBUCH ... SIEBENTER THEIL. व—ह nebst den Verbesserungen und Nachträgen zum ganzen Werke.", "Title page of volume 7, व to ह with the corrections and additions to the whole work, St. Petersburg 1875"),
         ext(1), [loc("26")], "not-digitized",
         "csldoc pwgpref26 scan viewed 24-09-2026: subtitle 'व - ह nebst den Verbesserungen und Nachträgen zum ganzen Werke. St. Petersburg 1875'."),
    comp("pwg.fm.vorwort-v7", 18, "preface", "commemorate",
         t("VORWORT.", "Preface to Part 7, closing the work (1875)"),
         ext(1), [loc("27")], "not-digitized",
         "csldoc pwgpref27 scan viewed 24-09-2026: single page signed 'O. Böhtlingk. R. Roth.', 'Jena und Tübingen, den 4. August 1875'; closes a nearly 25-year undertaking, thanks Weber, Kern, Stenzler, Whitney and (posthumously) Schiefner, and the Imperial Academy as patron.",
         secondary=["source"],
         notes="Footnote answers Müller's RV-edition preface complaint ('Why are not such technical terms ... given in the Petersburg Dictionary?'): both cited words stand in the body, not in the Nachträge."),
]

catalogue = {
    "schemaVersion": "1.0.0",
    "dict": "pwg",
    "dictName": "Böhtlingk & Roth, Sanskrit-Wörterbuch (the great Petersburg dictionary)",
    "edition": {"label": "St. Petersburg 1855-1875, 7 volumes, as scanned by Cologne (Part 1 'Die Vocale' 1855, Part 2 क-ह 1858, Part 3 त-भ 1861, Part 4 न-फ 1865, Part 5 फ-य 1868, Part 6 य-व 1871, Part 7 व-ह 1875)",
                "year": "1855-1875", "imprint": "Kaiserliche Akademie der Wissenschaften, St. Petersburg",
                "evidenceLevel": "observed",
                "evidence": "All seven volume title pages viewed 24-09-2026 in the csldoc scans; volume years and letter ranges read off them."},
    "scanSets": [
        {"id": "pwg-csldoc", "kind": "cologne-csldoc",
         "description": "Cologne csldoc front-matter pages for PWG (27 pages: 7 volume titles, the Part-1 Vorwort and abbreviation key, per-part corrigenda, Vorworte and abbreviation supplements of Parts 2-3, Vorworte of Parts 4-7).",
         "baseUrl": "https://sanskrit-lexicon.uni-koeln.de/scans/csldev/csldoc/build/dictionaries/prefaces/pwgpref/",
         "inventory": "data/megastructure/scan_inventory.tsv"},
        {"id": "pwg-scan-pdf", "kind": "cologne-scan-pdf",
         "description": "Cologne PWG page PDFs (body map, odd leaf refs each carrying printed pages ref and ref+1); declared here only for the final back-matter leaf pwg7-1821 = printed pp. 1821-1822.",
         "baseUrl": "https://www.sanskrit-lexicon.uni-koeln.de/scans/PWGScan/PWGScanpdf/",
         "inventory": "data/megastructure/scan_inventory.tsv"}
    ],
    "components": components + [
        comp("pwg.bm.last-leaf", 19, "other", "supplement",
             t(None, "Final printed leaf of the work: body tail plus the last corrections and additions, closing with the ornament"),
             ext(2, "1821-1822"),
             [{"scanSet": "pwg-scan-pdf", "ref": "7-1821", "image": "pwg7-1821.pdf", "printedPage": "1821-1822"}],
             "merged-into-body",
             "Scan leaf pwg7-1821.pdf viewed 24-09-2026: double-page spread '1821 सोन - 1822 स्वोतक', right page ends with the closing ornament after hevAkin. csl-orig pwg.txt carries both pages as entries L=122695..122732 (pc 7-1821/7-1822), interleaving short articles with one-line corrections ('Z. 2 lies 8,368', 'füge RV. 1,41,9 hinzu').",
             level="observed", langs=("deu", "san"), position="back",
             ctype_note="A leaf that is neither title nor preface: the printed end of the dictionary, whose addenda-style entries share the page with the last body articles.",
             decodes=[{"target": "corrections woven into the letter sequence of each volume",
                       "markup": "entries in pwg.txt whose text is a correction ('lies', 'füge ... hinzu', 'streiche')",
                       "mechanism": "Böhtlingk printed the per-volume 'Nachträgen und Verbesserungen' inside the alphabetical sequence (see the Part 5 and Part 7 title subtitles), not as a separately paginated supplement; the transcription keeps them as entries.",
                       "atlasRef": None}],
             notes="The pdffiles.txt body map ends at ref 7-1821 with caption 'sOna' (left page); pwg7-1822.pdf does not exist because each scanned leaf carries two printed pages (ref and ref+1)."),
    ],
    "excludedScans": [],
    "knownGaps": [
        {"label": "Verso between the two scanned corrigenda pages of Part 2 (between printed p. 11 and the unnumbered first corrigenda page)",
         "evidenceLevel": "inferred",
         "evidence": "csldoc pwgpref13 (unnumbered first corrigenda page) and pwgpref14 (p. 11, tail of the same list) are not consecutive printed pages; the intervening verso carries no csldoc page and no pdffiles row (front matter is outside the body map)."},
        {"label": "Imprint/verso pages of the seven volume titles, if printed",
         "evidenceLevel": "inferred",
         "evidence": "Only one title page per volume is scanned; title versos (printer's imprints) are absent from csldoc and, front matter being outside the body map, from pdffiles.txt; whether they exist in print was not verified."},
    ],
    "notes": ("csldoc page order is the order of publication (vol. 1 1855 ... vol. 7 1875); csldoc captions are mostly accurate, two exceptions: "
              "pwgpref19 is captioned 'Foreword, 3-2' but shows the Part-3 abbreviation list, and the image files pwg1-0000--06/--07.png are "
              "swapped against reading order (rst06 Foreword 5 shows --07.png, rst07 Abbreviations 1 shows --06.png; the rst assigns them correctly). "
              "Every csldoc scan carries a scan-era caption strip (header 'Otto Böhtlingk & Rudolph Roth: Sanskrit-Wörterbuch, Part N, Petersburg YYYY', "
              "footer 'Institute of Indology & Tamil Studies, Cologne University, Germany 9.2.2007') - see misfits. "
              "The pdffiles.txt body map lists odd leaf refs only; each scanned leaf is a double-page spread carrying printed pages ref and ref+1 "
              "(verified on leaf 7-1821 = printed pp. 1821-1822), so 'missing' even refs are the right-hand printed pages, not absent scans."),
    "misfits": [
        {"label": "Scan-era caption strip printed onto every csldoc page image", "componentId": None,
         "why": "Header and footer naming the work, the Cologne scanning institute and the scan date (9.2.2007) overlay the edition's pages; the schema has no scan-overlay layer, so the strip is documented here instead of per record."},
        {"label": "Back-matter corrections printed inside the alphabetical body", "componentId": "pwg.bm.last-leaf",
         "why": "The Part 5/7 title subtitles promise 'Nachträgen und Verbesserungen', but they are distributed through the letter sequence of each volume rather than bound as a separate paginated supplement; only the shared final leaf can be located as a component, so the inline corrections have no scanLocus of their own."},
    ],
}

OUT.write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {OUT} ({len(components) + 1} components)")
