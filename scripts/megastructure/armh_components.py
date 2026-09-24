"""Emit data/megastructure/armh.json - Halāyudha's Abhidhānaratnamālā (H5325).

Run once to regenerate the committed JSON:  python scripts/megastructure/armh_components.py

Evidence: ARMH_0001-ARMH_0008, ARMH_0010, ARMH_0020, ARMH_0050, ARMH_0075,
ARMH_0090, ARMH_0095-ARMH_0101 fetched from the Cologne scan PDFs and viewed
24-09-2026. The edition facts are from the catalogue's own armhheader.xml
(csl-orig/v02/armh) and the Cologne ARMHScan bibliographic entry, because the
scanned copy carries no imprint.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "data" / "megastructure" / "armh.json"

BASE = "https://www.sanskrit-lexicon.uni-koeln.de/scans/ARMHScan/ARMHScanpdf/"


def locus(ref):
    return {"scanSet": "armh-scan-pdf", "ref": ref, "image": f"ARMH_{ref}.pdf",
            "printedPage": str(int(ref))}


def ext(pages, printed=None, items=None, unit=None):
    return {"pages": pages, "printedRange": printed, "items": items, "itemsUnit": unit}


def t(as_printed, english):
    return {"asPrinted": as_printed, "iast": None, "english": english}


def comp(cid, seq, position, ctype, fn, title, extent, scan, disposition, evidence,
         level="observed", langs=("san",), decodes=(), transcriptions=(), notes=None,
         secondary=(), ctype_note=None):
    return {"id": cid, "sequence": seq, "position": position, "componentType": ctype,
            "componentTypeNote": ctype_note, "function": fn, "secondaryFunctions": list(secondary),
            "title": title, "languages": list(langs), "extent": extent, "decodes": list(decodes),
            "scanLocus": scan, "digitalDisposition": disposition, "transcriptions": list(transcriptions),
            "parent": None, "evidenceLevel": level, "evidence": evidence, "notes": notes}


components = [
    comp("armh.fm.title-page", 1, "front", "title-page", "identify",
         t("हलायुधकोशः ( अभिधानरत्नमाला ) प्रथमः स्वर्गकाण्डम्",
           "Title block: 'Halāyudhakośa (Abhidhānaratnamālā), First [kāṇḍa:] Svarga-kāṇḍa', printed at the head of the volume's first page over the opening of the kośa"),
         ext(1), [locus("0001")], "not-digitized",
         "ARMH_0001 viewed 24-09-2026: the volume has no separate title leaf; the title is set in large type at the head of page 1, immediately above the maṅgala verses ('शब्दब्रह्म ...') and the first entry verse ('स्व: स्वर्गः सुरसद्म त्रिदशावासस्त्रिविष्टपं ...'), the page's margins already carrying the English index. The page is unnumbered; page 2 carries the printed number 2.",
         notes="The edition's title is given in Devanagari only; no English title page is present in the scan set.",
         secondary=["frame"]),
    comp("armh.bm.colophon", 2, "back", "colophon", "attest",
         t("इति श्रीभद्रहलायुधकृतायामभिधानरत्नमालायां मनोहराकाण्डे पञ्चमं समाप्तम् ॥ ५ ॥",
           "Closing colophon: 'Thus ends the fifth, the Manohara-kāṇḍa, in the Abhidhānaratnamālā composed by Śrī Bhadra Halāyudha'"),
         ext(1), [locus("0101")], "not-digitized",
         "ARMH_0101 viewed 24-09-2026: the kośa's last verse (1887) is followed by the closing colophon and the kāṇḍa numeral 5, closing the volume. It is printed at the foot of the last text page (printed 101), not on a separate leaf.",
         secondary=["commemorate"]),
]

catalogue = {
    "schemaVersion": "1.0.0",
    "dict": "armh",
    "dictName": "Halāyudha, Abhidhānaratnamālā (the Halāyudhakośa)",
    "edition": {
        "label": "Halāyudhakośa (Abhidhānaratnamālā) of Halāyudha, usually cited from Jośī Jayaśaṅkara's edition; the scanned copy carries no imprint and its front matter is not in the scan set",
        "year": None,
        "imprint": None,
        "evidenceLevel": "inferred",
        "evidence": ("The scanned copy shows only the Devanagari title block, with no imprint leaf or date; the identification is from the "
                     "catalogue's own metadata (csl-orig/v02/armh/armhheader.xml: biblStruct ARMH - Halāyudha, Halāyudhakośaḥ "
                     "(Abhidhānaratnamālā), first edition, Vārāṇasī 1958, Publication Bureau, Department of Information, Government of "
                     "Uttar Pradesh for Sarasvatī Bhavana; 746 pp.) and from the Cologne ARMHScan bibliographic entry "
                     "'HALĀYUDHA & JOSHĪ JAYAŚAṄKARA, Halāyudhakośa (Abhidhānaratnamālā) of Halāyudha'. The header's own note says the "
                     "scanned book came from archive.org. The scanned volume runs to 101 pages, while the header's edition is 746 pp., "
                     "so the scan set covers the kośa text (which ends complete with the fifth kāṇḍa colophon) and not a 746-page apparatus."),
    },
    "scanSets": [
        {"id": "armh-scan-pdf", "kind": "cologne-scan-pdf",
         "description": ("Cologne ARMH page PDFs, ARMH_0001-ARMH_0101: the complete scanned volume, in which the scan number equals the "
                         "printed page number (page 1 unnumbered but carrying the title block over the kośa opening; page 101 the closing "
                         "colophon). Only the two megastructure-bearing pages are inventoried here; pages 2-100 are kośa body text, which "
                         "the schema does not model. The scans were obtained from archive.org."),
         "baseUrl": BASE,
         "inventory": "data/megastructure/scan_inventory.tsv"}
    ],
    "components": components,
    "excludedScans": [],
    "knownGaps": [
        {"label": "Front matter of the printed volume, if any, beyond scan page 1",
         "evidenceLevel": "inferred",
         "evidence": ("The Cologne ARMHScan index links a 'Front Matter' page at "
                      "sanskrit-lexicon.uni-koeln.de/scans/csldev/csldoc/build/dictionaries/armh.html, which returns HTTP 404 (probed "
                      "24-09-2026), and csl-doc carries no armh prefaced directory, so no csldoc front-matter scan set exists for this "
                      "dictionary. Whether the printed volume has a title leaf, preface or publisher's note before the text page that the "
                      "scans number 1 cannot be established from the scan set.")},
    ],
    "notes": ("The edition prints an English index in the margins of every text page (left and right margins of each page carry English "
              "glosses with reference numbers to the entry verses, e.g. page 3: 'Shiva's bow 2.', 'Name of Ganesh 9.', 'Name of Vishnu 55.'). "
              "That apparatus is digitized as the extra headwords in csl-orig/v02/armh/armh_hwextra.txt, but it recurs on every page and is "
              "not bracketed front or back matter, so it is recorded here rather than as a component. The kośa's body divisions are the five "
              "kāṇḍas - svarga (from page 1), bhūmi-kāṇḍa (opens printed page 20), the third kāṇḍa (opens page 75), the fourth, sāmānyakāṇḍa "
              "(ends printed page 90), and the fifth, manohara-kāṇḍa (pages 91-101)."),
    "misfits": [
        {"label": "English index printed in the margins of every text page", "componentId": None,
         "why": ("A recurring in-page apparatus, not bracketed matter. The component vocabulary (title-page, preface, index, ...) assumes "
                 "components that occupy whole pages or page ranges; a parallel apparatus that runs across the body has no slot, and nothing "
                 "in the schema lets its per-page extent be declared once. It is described in catalogue notes and its digitized form "
                 "(armh_hwextra.txt) is named there.")},
        {"label": "Title block printed at the head of the first text page rather than on a separate leaf", "componentId": "armh.fm.title-page",
         "why": ("The schema's position field forces front/back/inset, and this title occupies the upper part of the volume's first body page; "
                 "the record keeps it as a front title-page component with scanLocus page 1 rather than inventing an inset position, but the "
                 "page is simultaneously body text.")},
    ],
}

OUT.write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {OUT} ({len(components)} components)")
