"""Emit data/megastructure/ap90.json - Apte 1890 megastructure (H5325)."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "data" / "megastructure" / "ap90.json"
SET = "ap90-scan-pdf"


def loc(n):
    return {"scanSet": SET, "ref": f"t{n:04d}", "image": f"tit_{n:04d}.pdf", "printedPage": None}


def range_locs(first, last):
    return [loc(n) for n in range(first, last + 1)]


def comp(cid, seq, ctype, fn, english, pages, loci, level, evidence, note=None, ctype_note=None, disp="not-digitized"):
    return {"id": cid, "sequence": seq, "position": "front", "componentType": ctype,
            "componentTypeNote": ctype_note, "function": fn, "secondaryFunctions": [],
            "title": {"asPrinted": None, "iast": None, "english": english}, "languages": ["eng"],
            "extent": {"pages": pages, "printedRange": None, "items": None, "itemsUnit": None},
            "decodes": [], "scanLocus": loci, "digitalDisposition": disp, "transcriptions": [],
            "parent": None, "evidenceLevel": level, "evidence": evidence, "notes": note}


components = [
    comp("ap90.fm.title", 1, "title-page", "identify", "Title page of Apte's Practical Sanskrit-English Dictionary (1890)", 1,
         range_locs(1, 1), "inferred",
         "Scan map row t0001 (tit_0001.pdf, caption empty in pdffiles.txt); first of the 15 tit_* pages preceding body page 0001. Page content awaits scan reading."),
    comp("ap90.fm.front-sequence", 2, "other", "frame", "Unidentified front-matter sequence (14 pages between the title page and body page 1)", 14,
         range_locs(2, 15), "inferred",
         "Scan map rows t0002-t0015 (tit_0002.pdf-tit_0015.pdf, captions empty); csl-pywork carries two Cologne display tables for this dictionary (ap90ab_input.txt, 91 rows; ap90auth/tooltip.txt, 330 rows) counted 25-09-2026.",
         note="The composition (preface, abbreviation list, works/authors list) follows the Cologne front-matter pattern; the per-page split awaits scan reading.",
         ctype_note="Unidentified block: per-page parts are not yet attributed to scan pages.",
         disp="structured-data"),
]
components[1]["transcriptions"] = [
    {"kind": "structured-data", "location": "sanskrit-lexicon/csl-pywork:v02/distinctfiles/ap90/pywork/ap90ab/ap90ab_input.txt",
     "note": "Abbreviation display table, 91 rows; printed page placement inside t0002-t0015 awaits scan reading."},
    {"kind": "structured-data", "location": "sanskrit-lexicon/csl-pywork:v02/distinctfiles/ap90/pywork/ap90auth/tooltip.txt",
     "note": "Works/authors display table, 330 rows; printed page placement inside t0002-t0015 awaits scan reading."},
]

catalogue = {
    "schemaVersion": "1.0.0",
    "dict": "ap90",
    "dictName": "Apte, The Practical Sanskrit-English Dictionary (revised and enlarged edition)",
    "edition": {"label": "The revised and enlarged edition of 1890, as scanned by Cologne", "year": "1890",
                "imprint": None, "evidenceLevel": "inferred",
                "evidence": "Dictionary identity from the csl-orig ap90 digitization; the scanned title page awaits reading to confirm the print statement."},
    "scanSets": [{"id": SET, "kind": "cologne-scan-pdf",
                  "description": "Cologne AP90 front-matter page PDFs: the tit_* series (15 pages) listed in csl-websanlexicon pdffiles.txt ahead of body page 0001. Body pages 0001-1196 are out of scope (entry list).",
                  "baseUrl": "https://www.sanskrit-lexicon.uni-koeln.de/scans/AP90Scan/AP90Scanpdf/",
                  "inventory": "data/megastructure/scan_inventory.tsv"}],
    "components": components,
    "excludedScans": [],
    "knownGaps": [{"label": "Back matter (addenda/corrigenda after body page 1196)", "evidenceLevel": "inferred",
                   "evidence": "The trailing pdffiles.txt rows (pg_1194-pg_1196) carry empty captions; whether the print carries a closing addenda section is unresolved without reading the scans."}],
    "notes": None,
    "misfits": [
        {"label": "The 14-page front block cannot be decomposed without reading the scans",
         "why": "The schema has no 'unidentified block' component type, so the sequence is one 'other' record; per-page parts are owed a follow-up scan reading.", "componentId": "ap90.fm.front-sequence"},
        {"label": "Placement of the two digitized tables inside the block is unknown",
         "why": "extent.pages holds the block, but the schema cannot record that ap90ab (91 rows) and ap90auth (330 rows) belong to unnamed pages of the range.", "componentId": "ap90.fm.front-sequence"},
    ],
}
OUT.write_text(json.dumps(catalogue, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {OUT}")
