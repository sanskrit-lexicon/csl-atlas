"""Emit data/megastructure/pw.json - Boehtlingk, Sanskrit-Woerterbuch in kuerzerer Fassung (H5325).

Evidence: csl-doc csldoc pages pwpref01-05 (captions + embedded images
pw1-000-1..5.png). Page images were not viewed in this pass.
"""
from _fill_common import comp, ext, t, locus, write

SET = "pw-csldoc"
IMG = [f"pw1-000-{n}.png" for n in range(1, 6)]
L = lambda n: locus(SET, f"{n:02d}", IMG[n - 1])

components = [
    comp("pw.fm.title", 1, "front", "title-page", "identify",
         t("Title", "Title page of volume 1 (csldoc caption 'Title')"),
         ext(1), [L(1)], "not-digitized",
         "csldoc pwpref01 caption 'Title', scan image pw1-000-1.png; page not viewed in this pass.", langs=("deu", "san")),
    comp("pw.fm.foreword", 2, "front", "preface", "frame",
         t("Foreword", "Editor's foreword (csldoc caption 'Foreword'; Boehtlingk's prefaces are printed in German - inferred)"),
         ext(1), [L(2)], "not-digitized",
         "csldoc pwpref02 caption 'Foreword', scan image pw1-000-2.png; page not viewed, language inferred from the work's German imprint.", langs=("deu",), level="inferred"),
    comp("pw.fm.works-abbrev", 3, "front", "source-list", "source",
         t("Abbreviations of Works", "List of abbreviations of works and authors cited, three pages (csldoc captions 'Abbreviations of Works, 1-3')"),
         ext(3, items=3, unit="csldoc pages"), [L(3), L(4), L(5)], "not-digitized",
         "csldoc pwpref03-05 captions 'Abbreviations of Works, 1-3', scan images pw1-000-3..5.png; not viewed in this pass.",
         secondary=["decode"], langs=("deu",)),
]

write({
    "schemaVersion": "1.0.0", "dict": "pw",
    "dictName": "Sanskrit-Wörterbuch in kürzerer Fassung (Böhtlingk)",
    "edition": {"label": "Sanskrit-Wörterbuch in kürzerer Fassung (scanned edition; printing not verified in this pass)",
                "year": None, "imprint": None, "evidenceLevel": "inferred",
                "evidence": "csl-doc csldoc sidebar: 'PW Böhtlingk Sanskrit-Wörterbuch in kürzerer Fassung'; the title-page image was not viewed."},
    "scanSets": [{"id": SET, "kind": "cologne-csldoc",
                  "description": "Cologne csldoc front-matter pages for PW (5 pages: title, foreword, abbreviations of works 1-3), one scan image each.",
                  "baseUrl": "https://sanskrit-lexicon.uni-koeln.de/scans/csldev/csldoc/build/dictionaries/prefaces/pwpref/",
                  "inventory": "data/megastructure/scan_inventory.tsv"}],
    "components": components, "excludedScans": [],
    "knownGaps": [{"label": "Later volumes' front matter and back matter are not scanned in csldoc",
                   "detail": "pwpref carries only the five volume-1 pages; forewords or addenda of vols. 2-7 are not in csldoc and not catalogued."}],
    "misfits": [{"label": "Foreword language inferred, not verified",
                 "componentId": "pw.fm.foreword",
                 "why": "csldoc exposes only the caption 'Foreword'; the schema has no place for 'language unverified', so the inference is recorded here and in the evidence text."}],
})
