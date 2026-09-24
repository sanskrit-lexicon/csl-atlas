"""Emit data/megastructure/wil.json - Wilson megastructure (H5325)."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "data" / "megastructure" / "wil.json"
SET = "wil-scan-pdf"


def loc(n):
    return {"scanSet": SET, "ref": f"t{n:03d}", "image": f"tit-{n:03d}.jpg", "printedPage": None}


def comp(cid, seq, ctype, fn, english, pages, loci, level, evidence, note=None, ctype_note=None, langs=("eng",)):
    return {"id": cid, "sequence": seq, "position": "front", "componentType": ctype,
            "componentTypeNote": ctype_note, "function": fn, "secondaryFunctions": [],
            "title": {"asPrinted": None, "iast": None, "english": english}, "languages": list(langs),
            "extent": {"pages": pages, "printedRange": None, "items": None, "itemsUnit": None},
            "decodes": [], "scanLocus": loci, "digitalDisposition": "not-digitized", "transcriptions": [],
            "parent": None, "evidenceLevel": level, "evidence": evidence, "notes": note}


components = [
    comp("wil.fm.title", 1, "title-page", "identify", "Title page of Wilson's Sanskrit-English Dictionary (second edition)", 1,
         [loc(1)], "inferred",
         "Scan map row t001 (tit-001.jpg, caption empty in pdffiles.txt); first of the 6 tit-* pages preceding body page 001. Page content awaits scan reading."),
    comp("wil.fm.front-sequence", 2, "other", "frame", "Unidentified front-matter sequence (5 pages between the title page and body page 1)", 5,
         [loc(n) for n in range(2, 7)], "inferred",
         "Scan map rows t002-t006 (tit-002.jpg-tit-006.jpg, captions empty).",
         note="The second edition (1832) traditionally carries a dedication and preface; the per-page split awaits scan reading.",
         ctype_note="Unidentified block: per-page parts are not yet attributed to scan pages."),
]

catalogue = {
    "schemaVersion": "1.0.0",
    "dict": "wil",
    "dictName": "Wilson, A Sanskrit-English Dictionary",
    "edition": {"label": "The second edition (1832), as scanned by Cologne", "year": "1832", "imprint": None,
                "evidenceLevel": "inferred",
                "evidence": "Dictionary identity from the csl-orig wil digitization (Wilson 2nd ed. is the Cologne source); the scanned title page awaits reading to confirm the print statement."},
    "scanSets": [{"id": SET, "kind": "cologne-scan-pdf",
                  "description": "Cologne WIL front-matter page images: the tit-* series (6 pages) listed in csl-websanlexicon pdffiles.txt ahead of body page 001. Body pages 001-982 are out of scope (entry list).",
                  "baseUrl": "https://www.sanskrit-lexicon.uni-koeln.de/scans/WILScan/WILScanpdf/",
                  "inventory": "data/megastructure/scan_inventory.tsv"}],
    "components": components,
    "excludedScans": [],
    "knownGaps": [],
    "notes": "Scan-set URL probe 25-09-2026 returned 404 for tit-001.jpg under the canonical WILScan/WILScanpdf/ path; the images are named in the Cologne scan map and served through the dictionary pages. The inventory rows come from the map, not from a verified direct URL.",
    "misfits": [{"label": "The 5-page front block cannot be decomposed without reading the scans",
                 "why": "The schema has no 'unidentified block' component type, so the sequence is one 'other' record; per-page parts are owed a follow-up scan reading.", "componentId": "wil.fm.front-sequence"}],
}
OUT.write_text(json.dumps(catalogue, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {OUT}")
