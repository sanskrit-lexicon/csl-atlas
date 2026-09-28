"""Emit data/megastructure/wil.json - Wilson Sanskrit-English Dictionary (H5325).

Evidence: csl-doc csldoc pages wilpref01-06 (captions + embedded scan images
wilson_Page_001-006.jpg). Page images were not viewed in this pass; component
boundaries follow the csldoc page captions verbatim.
"""
from _fill_common import comp, ext, t, locus, write

SET = "wil-csldoc"
IMG = [f"wilson_Page_{n:03d}.jpg" for n in range(1, 7)]
L = lambda n: locus(SET, f"{n:02d}", IMG[n - 1])

components = [
    comp("wil.fm.title", 1, "front", "title-page", "identify",
         t("Title", "Title page of the scanned edition (csldoc caption 'Title')"),
         ext(1), [L(1)], "not-digitized",
         "csldoc wilpref01 caption 'Title', scan image wilson_Page_001.jpg; page not viewed in this pass.", langs=("eng", "san")),
    comp("wil.fm.dedication", 2, "front", "dedication", "commemorate",
         t("Dedication", "Dedication page (csldoc caption 'Dedication')"),
         ext(1), [L(2)], "not-digitized",
         "csldoc wilpref02 caption 'Dedication', scan image wilson_Page_002.jpg; page not viewed in this pass.", langs=("eng",)),
    comp("wil.fm.preface", 3, "front", "preface", "frame",
         t("Preface", "Author's preface, four pages (csldoc captions 'Preface, 1'-'Preface, 4')"),
         ext(4, items=4, unit="csldoc pages"), [L(3), L(4), L(5), L(6)], "not-digitized",
         "csldoc wilpref03-06 captions 'Preface, 1'-'Preface, 4', scan images wilson_Page_003-006.jpg; not viewed in this pass.", langs=("eng",)),
]

write({
    "schemaVersion": "1.0.0", "dict": "wil",
    "dictName": "Wilson Sanskrit-English Dictionary",
    "edition": {"label": "Wilson Sanskrit-English Dictionary (scanned edition; printing not verified in this pass)",
                "year": None, "imprint": None, "evidenceLevel": "inferred",
                "evidence": "csl-doc csldoc sidebar names the dictionary 'Wilson Sanskrit-English Dictionary'; the title-page image was not viewed, so year and imprint stay null."},
    "scanSets": [{"id": SET, "kind": "cologne-csldoc",
                  "description": "Cologne csldoc front-matter pages for WIL (6 pages: title, dedication, preface 1-4), one scan image each.",
                  "baseUrl": "https://sanskrit-lexicon.uni-koeln.de/scans/csldev/csldoc/build/dictionaries/prefaces/wilpref/",
                  "inventory": "data/megastructure/scan_inventory.tsv"}],
    "components": components, "excludedScans": [],
    "knownGaps": [{"label": "Back matter (if any) is not scanned",
                   "detail": "csl-doc carries no wilpref pages beyond the preface and the Cologne WIL scan set lists the six tit-001..006 images matching these six pages; nothing later than the preface is catalogued."}],
    "misfits": [],
})
