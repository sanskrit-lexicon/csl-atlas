"""Emit data/megastructure/abch.json - Hemacandra Abhidhanacintamani megastructure (H5325)."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "data" / "megastructure" / "abch.json"
SET = "abch-scan-pdf"


def loc(n):
    return {"scanSet": SET, "ref": f"f{n:02d}", "image": f"f{n:02d}.pdf", "printedPage": None}


def comp(cid, seq, ctype, fn, english, pages, loci, level, evidence, note=None, ctype_note=None, langs=("san",)):
    return {"id": cid, "sequence": seq, "position": "front", "componentType": ctype,
            "componentTypeNote": ctype_note, "function": fn, "secondaryFunctions": [],
            "title": {"asPrinted": None, "iast": None, "english": english}, "languages": list(langs),
            "extent": {"pages": pages, "printedRange": None, "items": None, "itemsUnit": None},
            "decodes": [], "scanLocus": loci, "digitalDisposition": "not-digitized", "transcriptions": [],
            "parent": None, "evidenceLevel": level, "evidence": evidence, "notes": note}


components = [
    comp("abch.fm.title", 1, "title-page", "identify", "Title page of the scanned Abhidhanacintamani edition", 1,
         [loc(1)], "inferred",
         "Scan map row f01 (f01.pdf, caption empty in pdffiles.txt); first of the 14 f* pages preceding the body page series (which starts at scan pg05). Page content awaits scan reading."),
    comp("abch.fm.front-sequence", 2, "other", "frame", "Unidentified front-matter sequence (13 pages between the title page and the body block)", 13,
         [loc(n) for n in range(2, 15)], "inferred",
         "Scan map rows f02-f14 (f02.pdf-f14.pdf, captions empty); body page series starts at scan pg05 (csl-orig abch.txt first entry <pc>0001...).",
         note="Kosha editions typically open with a mangala and commentarial apparatus; the per-page split awaits scan reading.",
         ctype_note="Unidentified block: per-page parts are not yet attributed to scan pages."),
]

catalogue = {
    "schemaVersion": "1.0.0",
    "dict": "abch",
    "dictName": "Hemacandra, Abhidhanacintamani (Namalinganushasana)",
    "edition": {"label": "The edition Cologne scanned (print statement awaits scan reading)", "year": None, "imprint": None,
                "evidenceLevel": "inferred",
                "evidence": "Dictionary identity from csl-orig abch.txt metadata (;title{aBiDAnacintAmaRi}; author hemacandrAcArya)."},
    "scanSets": [{"id": SET, "kind": "cologne-scan-pdf",
                  "description": "Cologne ABCH front-matter page PDFs: the f* series (14 pages) listed in csl-websanlexicon pdffiles.txt. Body pages pg05-pg58 are out of scope (entry list).",
                  "baseUrl": "https://www.sanskrit-lexicon.uni-koeln.de/scans/ABCHScan/ABCHScanpdf/",
                  "inventory": "data/megastructure/scan_inventory.tsv"}],
    "components": components,
    "excludedScans": [],
    "knownGaps": [{"label": "Body print pages 1-4 (scan map starts at pg05)", "evidenceLevel": "observed",
                   "evidence": "pdffiles.txt for abch lists body pages pg05-pg58 only; no pg01-pg04 rows exist and the direct URL probe for f01.pdf returned 404 (25-09-2026), so the first four body pages are not shown by any declared scan set."}],
    "notes": "Scan-set URL probe 25-09-2026 returned 404 for f01.pdf under the canonical ABCHScan/ABCHScanpdf/ path; the images are named in the Cologne scan map. The inventory rows come from the map, not from a verified direct URL.",
    "misfits": [{"label": "The 13-page front block cannot be decomposed without reading the scans",
                 "why": "The schema has no 'unidentified block' component type, so the sequence is one 'other' record; per-page parts are owed a follow-up scan reading.", "componentId": "abch.fm.front-sequence"}],
}
OUT.write_text(json.dumps(catalogue, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {OUT}")
