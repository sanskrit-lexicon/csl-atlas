"""Emit data/megastructure/vcp.json - Vacaspatyam (H5325).

Evidence: csl-doc csldoc pages vcppref01-07 (captions + embedded images
vac1_Page_007..016_Image_0002.png). Page images were not viewed in this pass.
"""
from _fill_common import comp, ext, t, locus, write

SET = "vcp-csldoc"
IMG = {1: "vac1_Page_007_Image_0002.png", 2: "vac1_Page_008_Image_0002.png",
       3: "vac1_Page_009_Image_0002.png", 4: "vac1_Page_010_Image_0002.png",
       5: "vac1_Page_013_Image_0002.png", 6: "vac1_Page_015_Image_0002.png",
       7: "vac1_Page_016_Image_0002.png"}
L = lambda n: locus(SET, f"{n:02d}", IMG[n])

components = [
    comp("vcp.fm.reprint-title", 1, "front", "title-page", "identify",
         t("Title Page", "Reprint wrapper title page (csldoc caption 'Title Page', before the vol. 1 title)"),
         ext(1), [L(1)], "not-digitized",
         "csldoc vcppref01 caption 'Title Page', scan vac1_Page_007_Image_0002.png; not viewed in this pass.", langs=("san",)),
    comp("vcp.fm.reprint-imprint", 2, "front", "imprint", "identify",
         t("Publisher", "Publisher's page of the reprint wrapper (csldoc caption 'Publisher')"),
         ext(1), [L(2)], "not-digitized",
         "csldoc vcppref02 caption 'Publisher', scan vac1_Page_008_Image_0002.png; not viewed in this pass.", langs=("san",)),
    comp("vcp.fm.vol1-title", 3, "front", "title-page", "identify",
         t("Title Page, vol. 1", "Title page of volume 1 of the work itself"),
         ext(1), [L(3)], "not-digitized",
         "csldoc vcppref03 caption 'Title Page, vol. 1', scan vac1_Page_009_Image_0002.png; not viewed in this pass.", langs=("san",)),
    comp("vcp.fm.publishers-note", 4, "front", "publisher-note", "frame",
         t("Publisher's Note", "Note by the publisher of the scanned edition"),
         ext(1), [L(4)], "not-digitized",
         "csldoc vcppref04 caption 'Publisher's Note', scan vac1_Page_010_Image_0002.png; not viewed in this pass.", langs=("eng",), level="inferred"),
    comp("vcp.fm.dedication", 5, "front", "dedication", "commemorate",
         t("Dedication", "Dedication page"),
         ext(1), [L(5)], "not-digitized",
         "csldoc vcppref05 caption 'Dedication', scan vac1_Page_013_Image_0002.png; not viewed in this pass. Scans 011-012 between the note and the dedication are not in csldoc and not catalogued.", langs=("san",), level="inferred"),
    comp("vcp.fm.preface", 6, "front", "preface", "frame",
         t("Preface", "Preface"),
         ext(1), [L(6)], "not-digitized",
         "csldoc vcppref06 caption 'Preface', scan vac1_Page_015_Image_0002.png; not viewed in this pass. Scan 014 is not in csldoc.", langs=("san", "eng"), level="inferred"),
    comp("vcp.fm.contents", 7, "front", "index", "instruct",
         t("Contents", "Table of contents"),
         ext(1), [L(7)], "not-digitized",
         "csldoc vcppref07 caption 'Contents', scan vac1_Page_016_Image_0002.png; not viewed in this pass.", langs=("san",), level="inferred"),
]

write({
    "schemaVersion": "1.0.0", "dict": "vcp",
    "dictName": "Vācaspatyam",
    "edition": {"label": "Vācaspatyam (scanned edition with a reprint wrapper title/imprint before the vol. 1 title)",
                "year": None, "imprint": None, "evidenceLevel": "inferred",
                "evidence": "csldoc captions pair a 'Title Page' + 'Publisher' wrapper with a separate 'Title Page, vol. 1'; the images were not viewed, so year and imprint stay null."},
    "scanSets": [{"id": SET, "kind": "cologne-csldoc",
                  "description": "Cologne csldoc front-matter pages for VCP (7 pages: wrapper title+publisher, vol. 1 title, publisher's note, dedication, preface, contents), one scan image each.",
                  "baseUrl": "https://sanskrit-lexicon.uni-koeln.de/scans/csldev/csldoc/build/dictionaries/prefaces/vcppref/",
                  "inventory": "data/megastructure/scan_inventory.tsv"}],
    "components": components, "excludedScans": [],
    "knownGaps": [{"label": "Scan leaves 011-012 and 014 are absent from csldoc",
                   "detail": "The vac1_Page numbering jumps 010 -> 013 -> 015; the two leaves between the publisher's note and the dedication, and the leaf between it and the preface, are not catalogued and may be blank or belong to a part csldoc does not caption."}],
    "misfits": [],
})
