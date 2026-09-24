"""Emit data/megastructure/mw.json - the MW (1899) megastructure pilot (H5324).

Run once to regenerate the committed JSON:  python scripts/megastructure/mw_components.py
Counts quoted in `evidence` were measured on csl-orig@f4c08c5 (mw.txt) and
csl-pywork@4943a6d (mwab, mwauth); validate-megastructure re-measures them
when those sibling checkouts are present.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "data" / "megastructure" / "mw.json"
ROMAN = ["v", "vi", "vii", "viii", "ix", "x", "xi", "xii", "xiii", "xiv", "xv", "xvi", "xvii", "xviii", "xix",
         "xx", "xxi", "xxii", "xxiii", "xxiv", "xxv", "xxvi", "xxvii", "xxviii", "xxix", "xxx", "xxxi", "xxxii"]
# csldoc page n (2..29) shows printed page ROMAN[n-2]; scan file per the Cologne map (xxix/xxx swapped)
SCAN_OF = {r: f"mw0100{9 + i:02d}.jpg" for i, r in enumerate(ROMAN)}
SCAN_OF["xxix"], SCAN_OF["xxx"] = "mw010034.jpg", "mw010033.jpg"


def csldoc(printed):
    page = ROMAN.index(printed) + 2
    return {"scanSet": "mw-csldoc", "ref": f"{page:02d}", "image": SCAN_OF[printed], "printedPage": printed}


def scan_pdf(printed):
    image = SCAN_OF[printed]
    return {"scanSet": "mw-scan-pdf", "ref": f"t{image[6:8]}", "image": image.replace(".jpg", ".pdf"), "printedPage": printed}


def both(printed):
    return [csldoc(printed), scan_pdf(printed)]


def csldoc_range(first, last):
    """csldoc page + the matching Cologne page PDF for every printed page in the range."""
    a, b = ROMAN.index(first), ROMAN.index(last)
    return [locus for r in ROMAN[a:b + 1] for locus in both(r)]


def pdf(ref, image, printed=None):
    return {"scanSet": "mw-scan-pdf", "ref": ref, "image": image, "printedPage": printed}


def ocr(first, last):
    return [{"kind": "ocr-markdown",
             "location": f"sanskrit-lexicon/MWS:prefaces/mwpref{first:02d}.md..mwpref{last:02d}.md",
             "note": "Vision OCR with frontmatter source_scan per page; RU translations alongside (*.ru.md)."}]


def comp(cid, seq, position, ctype, fn, title, extent, scan, disposition, evidence, level="observed",
         decodes=(), transcriptions=(), parent=None, notes=None, secondary=(), langs=("eng",)):
    return {"id": cid, "sequence": seq, "position": position, "componentType": ctype, "componentTypeNote": None,
            "function": fn, "secondaryFunctions": list(secondary), "title": title, "languages": list(langs),
            "extent": extent, "decodes": list(decodes), "scanLocus": scan, "digitalDisposition": disposition,
            "transcriptions": list(transcriptions), "parent": parent, "evidenceLevel": level,
            "evidence": evidence, "notes": notes}


def ext(pages, printed=None, items=None, unit=None):
    return {"pages": pages, "printedRange": printed, "items": items, "itemsUnit": unit}


def t(as_printed, english):
    return {"asPrinted": as_printed, "iast": None, "english": english}


INTRO = "mw.fm.introduction"
components = [
    comp("mw.fm.title", 1, "front", "title-page", "identify",
         t("A SANSKRIT-ENGLISH DICTIONARY ETYMOLOGICALLY AND PHILOLOGICALLY ARRANGED", "Title page of the 1899 new edition"),
         ext(1), [{"scanSet": "mw-csldoc", "ref": "01", "image": "mw010001.jpg", "printedPage": None}, pdf("t01", "mw010001.pdf")],
         "transcribed", "csldoc mwpref01 + MWS/prefaces/mwpref01.md (source_scan mw010001.jpg); scan map t01 'Title'.",
         transcriptions=ocr(1, 1),
         notes="Scanned first, although a half-title (t07) and the imprint (t08) follow it in the scan set; see catalogue notes."),
    comp("mw.fm.half-title", 2, "front", "title-page", "identify", t("A SANSKRIT-ENGLISH DICTIONARY", "Half-title"),
         ext(1), [pdf("t07", "mw010007.pdf")], "not-digitized",
         "Scan t07 viewed 24-09-2026: only 'A SANSKṚIT-ENGLISH DICTIONARY'. The Cologne map captions it 'Title'."),
    comp("mw.fm.imprint", 3, "front", "imprint", "identify",
         t("Oxford University Press, Amen House, London E.C.4", "Publisher's imprint of the scanned reprint"),
         ext(1), [pdf("t08", "mw010008.pdf")], "not-digitized",
         "Scan t08 viewed 24-09-2026: OUP Amen House imprint with branch list (Glasgow ... Kuala Lumpur, Hong Kong).",
         notes="Belongs to the OUP reprint that Cologne scanned, not to the 1899 printing; the branch list dates it to the mid-20th century."),
    comp("mw.fm.preface", 4, "front", "preface", "frame", t("PREFACE TO THE NEW EDITION.", "Preface to the new edition"),
         ext(6, "v-x"), csldoc_range("v", "x"), "transcribed",
         "csldoc mwpref02-07 = printed v-x, scans mw010009-mw010014; OCR headings checked 24-09-2026.",
         transcriptions=ocr(2, 7)),
    comp("mw.fm.postscript", 5, "front", "postscript", "frame", t("POSTSCRIPT.", "Postscript (dated May 4, 1899)"),
         ext(0.3, "x"), both("x"), "transcribed",
         "mwpref07.md: '## POSTSCRIPT.' on p. x, signed 'May 4, 1899. M. F. MONIER-WILLIAMS.'",
         transcriptions=ocr(7, 7), parent="mw.fm.preface",
         notes="Signed by the son after the author's death (April 1899)."),
    comp(INTRO, 6, "front", "introduction", "frame", t("INTRODUCTION.", "Introduction, sections I-V"),
         ext(22, "xi-xxxii", 5, "sections"), csldoc_range("xi", "xxxii"), "transcribed",
         "csldoc mwpref08-29 = printed xi-xxxii; section headings grepped from MWS/prefaces 24-09-2026.",
         transcriptions=ocr(8, 29), secondary=["instruct", "decode"],
         notes="Scans mw010033/mw010034 are swapped against print (xxx/xxix) in the Cologne scan map itself; csldoc and the OCR follow the print."),
    comp("mw.fm.intro-sec1", 7, "front", "introduction-section", "frame",
         t("SECTION I. Statement of the circumstances which led to the peculiar System of Sanskrit Lexicography introduced for the first time in the Monier-Williams Sanskrit-English Dictionary of 1872.",
           "Why the root-based arrangement of 1872"),
         ext(3, "xi-xiii"), csldoc_range("xi", "xiii"), "transcribed", "mwpref08.md heading; runs to mwpref10.md.",
         transcriptions=ocr(8, 10), parent=INTRO),
    comp("mw.fm.intro-sec2", 8, "front", "user-guide", "instruct",
         t("SECTION II. Explanation of the Plan and Arrangement of the Work, and of the Improvements introduced into the Present Edition.",
           "Plan and arrangement of the work"),
         ext(6, "xiv-xix"), csldoc_range("xiv", "xix"), "transcribed",
         "mwpref11.md heading; runs to mwpref16.md; homonym figures 'from each other by the figures 1, 2, 3, &c.' on p. xv.",
         decodes=[
             {"target": "root-and-derivative grouping with typographic levels",
              "markup": "<e> level codes (1, 2, 3, 4 and 1A...) and <k2> hyphenation in mw.txt",
              "mechanism": "explains the root-first arrangement: derivatives and compounds follow their leading word, with levels of type size; Cologne encodes the levels in the <e> field.",
              "atlasRef": "scripts/lib/mw-parser.mjs"},
             {"target": "homonym numbering", "markup": "<hom> and <h> in mw.txt",
              "mechanism": "homonyms are distinguished by figures 1, 2, 3 placed before the transliterated forms.", "atlasRef": None},
             {"target": "references and the symbol &c.", "markup": "<ls>",
              "mechanism": "states the reference policy (few quotations; the Petersburg Thesaurus as the store of citations) and the economy symbol &c.", "atlasRef": None}],
         transcriptions=ocr(11, 16), parent=INTRO, secondary=["decode"]),
    comp("mw.fm.intro-sec3", 9, "front", "scope-statement", "frame",
         t("SECTION III. Extent of Sanskṛit Literature comprehended in the Present Edition.", "Extent of the literature covered"),
         ext(2.5, "xx-xxii"), csldoc_range("xx", "xxii"), "transcribed", "mwpref17.md '## SECTION III.' mid-page xx; runs into mwpref19.md.",
         transcriptions=ocr(17, 19), parent=INTRO, secondary=["source"]),
    comp("mw.fm.intro-sec4", 10, "front", "introduction-section", "decode",
         t("SECTION IV. Reasons for applying the Roman Alphabet to the expression of Sanskṛit, with an account of the Method of Transliteration employed in the Present Dictionary.",
           "Roman alphabet and the transliteration method"),
         ext(8.5, "xxii-xxx"), csldoc_range("xxii", "xxx"), "transcribed", "mwpref19.md '## SECTION IV.' on p. xxii; runs to mwpref27.md.",
         decodes=[{"target": "Indo-Romanic transliteration printed after every Nāgarī headword",
                   "markup": "<k2> and the Roman forms Cologne normalises to SLP1",
                   "mechanism": "argues for Roman type and sets out the letter-by-letter transliteration used throughout.", "atlasRef": None}],
         transcriptions=ocr(19, 27), parent=INTRO, secondary=["frame"]),
    comp("mw.fm.intro-sec5", 11, "front", "introduction-section", "commemorate",
         t("SECTION V. Acknowledgment of Assistance Received.", "Acknowledgment of assistance"),
         ext(2.5, "xxx-xxxii"), csldoc_range("xxx", "xxxii"), "transcribed",
         "mwpref27.md '## SECTION V.' on p. xxx; ends mwpref29.md signed 'MONIER MONIER-WILLIAMS. Indian Institute, Oxford.'",
         decodes=[{"target": "the authority mark MW.", "markup": "<ls>MW.</ls>",
                   "mechanism": "words marked MW. rest partly on the Śabdakalpadruma or on the author's own books.", "atlasRef": None}],
         transcriptions=ocr(27, 29), parent=INTRO, secondary=["source"]),
    comp("mw.fm.works-authors", 12, "front", "source-list", "source", t("LIST OF WORKS AND AUTHORS.", "List of works and authors"),
         ext(2, "xxxiii-xxxiv", 604, "rows of the printed list in tooltip.txt (incl. variant rows such as 01:02x)"),
         [pdf("t05", "mw010005.pdf", "xxxiii"), pdf("t06", "mw010006.pdf", "xxxiv")], "structured-data",
         "Scan t05 viewed 24-09-2026 (five columns, head-note); csl-pywork mwauth/tooltip.txt: 871 rows, 267 marked '[Cologne Addition]', 604 from the printed list.",
         decodes=[{"target": "literary source abbreviations in entries", "markup": "<ls>",
                   "mechanism": "'the letters outside the parentheses represent the abbreviated forms used in the references', e.g. Abhinav(a-gupta).",
                   "atlasRef": None}],
         transcriptions=[{"kind": "structured-data", "location": "sanskrit-lexicon/csl-pywork:v02/distinctfiles/mw/pywork/mwauth/tooltip.txt",
                          "note": "Display tooltip table; mwauth.txt (XML) no longer maintained since 25-07-2022."}],
         notes="Not in csldoc and not OCR'd as a page; exists only as the display table."),
    comp("mw.fm.abbreviations", 13, "front", "abbreviation-list", "decode", t("ABBREVIATIONS.", "Abbreviations"),
         ext(1, "xxxv", 424, "rows in mwab_input.txt (Cologne-extended)"), [pdf("t04", "mw010004.pdf", "xxxv")], "structured-data",
         "Scan t04 viewed 24-09-2026: five columns, head-note on inconsistent use; csl-pywork mwab/mwab_input.txt 424 rows with lexicon counts.",
         decodes=[{"target": "grammatical and general abbreviations in entries", "markup": "<ab> and <lex>",
                   "mechanism": "one-line expansions (f. = feminine, ind. = indeclinable ...); the head-note concedes the use is not uniform.",
                   "atlasRef": None}],
         transcriptions=[{"kind": "structured-data", "location": "sanskrit-lexicon/csl-pywork:v02/distinctfiles/mw/pywork/mwab/mwab_input.txt",
                          "note": "Expansion table with Cologne occurrence counts; rows are not flagged printed vs added."}]),
    comp("mw.fm.dict-order", 14, "front", "ordering-note", "decode", t(None, "Order of the dictionary (p. xxxvi)"),
         ext(1, "xxxvi"), [pdf("t03", "mw010003.pdf", "xxxvi")], "not-digitized",
         "Cologne scan map caption only: 't03:mw010003.pdf:Page xxxvi, Dict. Order'; the PDF did not render when viewed 24-09-2026.",
         level="inferred",
         decodes=[{"target": "headword sort order", "markup": None,
                   "mechanism": "caption says the page states the dictionary order; content not yet read.", "atlasRef": None}],
         notes="Re-view the scan and replace this record's inferred parts before H5325 relies on it."),
    comp("mw.bm.additions", 15, "back", "supplement", "supplement", t(None, "Additions and corrections (supplement)"),
         ext(26, "1308-1333"), [pdf("1308..1333", "mw1308-hvala.pdf .. mw1333.pdf", "1308-1333")], "merged-into-body",
         "Cologne scan map: '1308 hvala, Suppl.' then S1309 ... S1333; csl-orig mw.txt: 7,096 records carry n=\"sup\" (6,220 with a decimal L, 876 with an integer L); 279 <info n=\"rev\"> markers - 269 with pc in 1308-1333, 5 with pc=\"cdsl\" (Cologne's own revisions), 5 with no pc - plus 15 <listinfo n=\"rev\"/>.",
         secondary=["decode"],
         decodes=[
             {"target": "headwords added by the supplement", "markup": "decimal L numbers (e.g. L=27.1) with <info n=\"sup\"/>",
              "mechanism": "Cologne interleaved each supplement entry into the main alphabet after the entry it follows, keeping its supplement page in <pc>.",
              "atlasRef": None},
             {"target": "corrections to existing entries", "markup": "<info n=\"rev\" pc=\"1308,1\"/>",
              "mechanism": "a body entry revised by the supplement points back to the supplement page and column.", "atlasRef": None}],
         notes="Printed heading not viewed (the PDF did not render); body ends mid-page 1308 (L=264858 hval at 1307,3)."),
]

catalogue = {
    "schemaVersion": "1.0.0",
    "dict": "mw",
    "dictName": "Monier-Williams, A Sanskrit-English Dictionary",
    "edition": {"label": "New edition 1899 (Oxford, Clarendon Press), as scanned from an OUP reprint",
                "year": "1899", "imprint": "Oxford University Press, Amen House, London (reprint)",
                "evidenceLevel": "observed",
                "evidence": "Title page OCR (mwpref01.md), postscript dated May 4, 1899, imprint scan t08."},
    "scanSets": [
        {"id": "mw-csldoc", "kind": "cologne-csldoc",
         "description": "Cologne csldoc front-matter pages for MW (29 pages, title + v-xxxii), OCR'd in sanskrit-lexicon/MWS prefaces/.",
         "baseUrl": "https://sanskrit-lexicon.uni-koeln.de/scans/csldev/csldoc/build/dictionaries/prefaces/mwpref/",
         "inventory": "data/megastructure/scan_inventory.tsv"},
        {"id": "mw-scan-pdf", "kind": "cologne-scan-pdf",
         "description": "Cologne MW page PDFs: front matter t01-t36 and supplement pages 1308-1333, per csl-websanlexicon pdffiles.txt.",
         "baseUrl": "https://www.sanskrit-lexicon.uni-koeln.de/scans/MWScan/MWScanpdf/",
         "inventory": "data/megastructure/scan_inventory.tsv"}],
    "components": components,
    "excludedScans": [
        {"scanSet": "mw-scan-pdf", "ref": "t02",
         "reason": "Blank leaf with the scanned copy's library stamp (Inventar 5148); Cologne captions it 'Copyright', but it carries no text of the edition."}],
    "knownGaps": [],
    "notes": ("Scan order is not print order: the Cologne MW scan set runs t01 title, t02 blank leaf, t03-t06 = pp. xxxvi, xxxv, xxxiii, xxxiv "
              "(end of the front matter, bound or scanned first and backwards), t07 half-title, t08 imprint, t09-t36 = pp. v-xxxii with "
              "t33/t34 = xxx/xxix. Two Cologne captions are wrong: t02 'Copyright' is a blank leaf with a library stamp, t07 'Title' is the half-title."),
    "misfits": [
        {"label": "Library provenance stamp on scan t02 ('ex libris', Inventar 5148)", "componentId": None,
         "why": "A mark of the scanned copy, not of the edition; the schema has no copy-level layer, so it is not a component."},
        {"label": "Printed list vs Cologne additions inside one structured table", "componentId": "mw.fm.works-authors",
         "why": "extent.items can hold only one count; the 267 Cologne-added rows are reported in evidence text rather than a field."},
    ],
}

OUT.write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {OUT} ({len(components)} components)")
