"""Emit data/megastructure/vcp.json - Vacaspatyam megastructure (H5325)."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "data" / "megastructure" / "vcp.json"
SET = "vcp-scan-pdf"


def loc(n):
    return {"scanSet": SET, "ref": f"{n:04d}", "image": f"pg{n:04d}.pdf", "printedPage": None}


components = [
    {"id": "vcp.fm.front-sequence", "sequence": 1, "position": "front", "componentType": "other",
     "componentTypeNote": "Unidentified block: 34 pre-body pages, per-page parts not yet attributed to scan pages.",
     "function": "frame", "secondaryFunctions": [],
     "title": {"asPrinted": None, "iast": None,
               "english": "Unidentified front-matter sequence (34 pre-body pages of the Vacaspatyam scan)"},
     "languages": ["san"],
     "extent": {"pages": 34, "printedRange": None, "items": None, "itemsUnit": None},
     "decodes": [], "scanLocus": [loc(n) for n in range(1, 35)],
     "digitalDisposition": "not-digitized", "transcriptions": [], "parent": None,
     "evidenceLevel": "inferred",
     "evidence": "pdffiles.txt for vcp begins at ref 0035 (caption 'a', the first body headword); HTTP probe 25-09-2026: pg0001.pdf, pg0034.pdf and pg0035.pdf all return 200 under VCPScan/VCPScanpdf/, so pages 1-34 are served but unmapped.",
     "notes": "The Vacaspatyam is known to open with a long Sanskrit preface; the per-page split awaits scan reading."},
]

catalogue = {
    "schemaVersion": "1.0.0",
    "dict": "vcp",
    "dictName": "Taranatha Tarkavacaspati, Vacaspatyam",
    "edition": {"label": "The edition Cologne scanned (print statement awaits scan reading)", "year": None, "imprint": None,
                "evidenceLevel": "inferred",
                "evidence": "Dictionary identity from the csl-orig vcp digitization (Vacaspatyam)."},
    "scanSets": [{"id": SET, "kind": "cologne-scan-pdf",
                  "description": "Cologne VCP page PDFs pg0001-pg0034: the pre-body block served under VCPScan/VCPScanpdf/ but ABSENT from the csl-websanlexicon pdffiles.txt scan map (which begins at pg0035, the first body page). Body pages are out of scope (entry list).",
                  "baseUrl": "https://www.sanskrit-lexicon.uni-koeln.de/scans/VCPScan/VCPScanpdf/",
                  "inventory": "data/megastructure/scan_inventory.tsv"}],
    "components": components,
    "excludedScans": [],
    "knownGaps": [],
    "notes": None,
    "misfits": [{"label": "Cologne's scan map omits pg0001-pg0034 although the PDFs are served",
                 "why": "The scan map is the declared page list, but 34 pre-body pages exist outside it (HTTP 200); the catalogue inventories them from the server, not from the map.", "componentId": "vcp.fm.front-sequence"},
                {"label": "The 34-page front block cannot be decomposed without reading the scans",
                 "why": "The schema has no 'unidentified block' component type; per-page parts are owed a follow-up scan reading.", "componentId": "vcp.fm.front-sequence"}],
}
OUT.write_text(json.dumps(catalogue, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {OUT}")
