"""Emit data/megastructure/pwg.json - Boehtlingk & Roth, Grosses Petersburger Woerterbuch (H5325).

Evidence: csl-doc csldoc pages pwgpref01-27 (captions + embedded images
pwg<vol>-0000--NN.png). Page images were not viewed in this pass. csldoc
pages 06/07 carry images --07/--06 respectively: the scanned files for
'Foreword, 5' and 'Abbreviations, 1' are swapped in the scan set itself.
"""
from _fill_common import comp, ext, t, locus, write

SET = "pwg-csldoc"
IMG = ["pwg1-0000--01.png", "pwg1-0000--02.png", "pwg1-0000--03.png", "pwg1-0000--04.png",
       "pwg1-0000--05.png", "pwg1-0000--07.png", "pwg1-0000--06.png", "pwg1-0000--08.png",
       "pwg1-0000--09.png", "pwg1-0000--10.png", "pwg1-0000--11.png", "pwg2-0000--01.png",
       "pwg2-0000--02.png", "pwg2-0000--03.png", "pwg2-0000--04.png", "pwg2-0000--05.png",
       "pwg3-0000--01.png", "pwg3-0000--02.png", "pwg3-0000--03.png", "pwg4-0000--01.png",
       "pwg4-0000--02.png", "pwg5-0000--01.png", "pwg5-0000--02.png", "pwg5-0000--03.png",
       "pwg6-0000--01.png", "pwg7-0000--01.png", "pwg7-0000--02.png"]
L = lambda n: locus(SET, f"{n:02d}", IMG[n - 1])
DEU = ("deu", "san")

components = [
    comp("pwg.fm.title-v1", 1, "front", "title-page", "identify", t("Title, vol. 1", "Title page of volume 1"), ext(1), [L(1)], "not-digitized", "csldoc pwgpref01 caption 'Title, vol. 1'; not viewed in this pass.", langs=DEU),
    comp("pwg.fm.foreword-v1", 2, "front", "preface", "frame", t("Foreword, 1-5", "Editors' foreword of volume 1, five pages (Böhtlingk & Roth's Vorrede; German inferred)"), ext(5, items=5, unit="csldoc pages"), [L(2), L(3), L(4), L(5), L(6)], "not-digitized", "csldoc pwgpref02-06 captions 'Foreword, 1'-'Foreword, 5'; not viewed in this pass. The scan file for 'Foreword, 5' is pwg1-0000--07.png (swapped with --06, see misfits).", langs=DEU, level="inferred"),
    comp("pwg.fm.abbrev-v1", 3, "front", "source-list", "source", t("Abbreviations, 1-5", "List of abbreviations of works and authors, five pages"), ext(5, items=5, unit="csldoc pages"), [L(7), L(8), L(9), L(10), L(11)], "not-digitized", "csldoc pwgpref07-11 captions 'Abbreviations, 1'-'Abbreviations, 5'; not viewed in this pass. First page's scan file is pwg1-0000--06.png (swap).", secondary=["decode"], langs=DEU, level="inferred"),
    comp("pwg.fm.title-v2", 4, "front", "title-page", "identify", t("Title, vol. 2", "Title page of volume 2"), ext(1), [L(12)], "not-digitized", "csldoc pwgpref12 caption 'Title, vol. 2'; not viewed in this pass.", langs=DEU),
    comp("pwg.fm.addenda", 5, "front", "supplement", "supplement", t("Addenda to vol. 1 / vol. 2", "Two addenda leaves grouped at the front of volume 2"), ext(2, items=2, unit="leaves"), [L(13), L(14)], "not-digitized", "csldoc pwgpref13-14 captions 'Addenda to vol. 1' and 'Addenda to vol. 2'; not viewed in this pass.", langs=DEU, level="inferred", notes="Which volume each addendum supplements is in its caption; the schema's extent cannot carry a per-leaf split (see misfits)."),
    comp("pwg.fm.foreword-v2", 6, "front", "preface", "frame", t("Foreword, 2-1", "Volume 2 foreword page"), ext(1), [L(15)], "not-digitized", "csldoc pwgpref15 caption 'Foreword, 2-1'; not viewed in this pass.", langs=DEU, level="inferred"),
    comp("pwg.fm.abbrev-v2", 7, "front", "source-list", "source", t("Abbreviations, 2-1", "Volume 2 abbreviations page"), ext(1), [L(16)], "not-digitized", "csldoc pwgpref16 caption 'Abbreviations, 2-1'; not viewed in this pass.", langs=DEU, level="inferred"),
    comp("pwg.fm.title-v3", 8, "front", "title-page", "identify", t("Title, vol. 3", "Title page of volume 3"), ext(1), [L(17)], "not-digitized", "csldoc pwgpref17 caption 'Title, vol. 3'; not viewed in this pass.", langs=DEU),
    comp("pwg.fm.foreword-v3", 9, "front", "preface", "frame", t("Foreword, 3-1 / 3-2", "Volume 3 foreword, two pages"), ext(2), [L(18), L(19)], "not-digitized", "csldoc pwgpref18-19 captions 'Foreword, 3-1' and 'Foreword, 3-2'; not viewed in this pass.", langs=DEU, level="inferred"),
    comp("pwg.fm.title-v4", 10, "front", "title-page", "identify", t("Title, vol. 4", "Title page of volume 4"), ext(1), [L(20)], "not-digitized", "csldoc pwgpref20 caption 'Title, vol. 4'; not viewed in this pass.", langs=DEU),
    comp("pwg.fm.foreword-v4", 11, "front", "preface", "frame", t("Foreword, 4-1", "Volume 4 foreword page"), ext(1), [L(21)], "not-digitized", "csldoc pwgpref21 caption 'Foreword, 4-1'; not viewed in this pass.", langs=DEU, level="inferred"),
    comp("pwg.fm.title-v5", 12, "front", "title-page", "identify", t("Title, vol. 5", "Title page of volume 5"), ext(1), [L(22)], "not-digitized", "csldoc pwgpref22 caption 'Title, vol. 5'; not viewed in this pass.", langs=DEU),
    comp("pwg.fm.foreword-v5", 13, "front", "preface", "frame", t("Foreword, 5-1 / 5-2", "Volume 5 foreword, two pages"), ext(2), [L(23), L(24)], "not-digitized", "csldoc pwgpref23-24 captions 'Foreword, 5-1' and 'Foreword, 5-2'; not viewed in this pass.", langs=DEU, level="inferred"),
    comp("pwg.fm.title-v6", 14, "front", "title-page", "identify", t("Title, vol. 6", "Title page of volume 6"), ext(1), [L(25)], "not-digitized", "csldoc pwgpref25 caption 'Title, vol. 6'; not viewed in this pass.", langs=DEU),
    comp("pwg.fm.title-v7", 15, "front", "title-page", "identify", t("Title, vol. 7", "Title page of volume 7"), ext(1), [L(26)], "not-digitized", "csldoc pwgpref26 caption 'Title, vol. 7'; not viewed in this pass.", langs=DEU),
    comp("pwg.fm.foreword-v7", 16, "front", "preface", "frame", t("Foreword, 7-1", "Volume 7 foreword page"), ext(1), [L(27)], "not-digitized", "csldoc pwgpref27 caption 'Foreword, 7-1'; not viewed in this pass.", langs=DEU, level="inferred"),
]

write({
    "schemaVersion": "1.0.0", "dict": "pwg",
    "dictName": "Großes Petersburger Wörterbuch (Böhtlingk & Roth)",
    "edition": {"label": "Sanskrit-Wörterbuch herausgegeben von Böhtlingk und Roth (scanned edition; printing not verified in this pass)",
                "year": None, "imprint": None, "evidenceLevel": "inferred",
                "evidence": "csl-doc csldoc sidebar: 'PWG Böhtlingk and Roth Grosses Petersburger Wörterbuch'; seven volume title pages match the 7-volume 1852-1875 work. Images not viewed."},
    "scanSets": [{"id": SET, "kind": "cologne-csldoc",
                  "description": "Cologne csldoc front-matter pages for PWG (27 pages over 7 volumes: title pages, forewords, abbreviation lists, addenda), one scan image each.",
                  "baseUrl": "https://sanskrit-lexicon.uni-koeln.de/scans/csldev/csldoc/build/dictionaries/prefaces/pwgpref/",
                  "inventory": "data/megastructure/scan_inventory.tsv"}],
    "components": components, "excludedScans": [],
    "knownGaps": [{"label": "Volume 6 has no foreword or abbreviations in csldoc",
                   "detail": "pwgpref carries only 'Title, vol. 6' between vol. 5's foreword and vol. 7's title; whether vol. 6 printed front matter beyond the title is not recorded here."}],
    "misfits": [{"label": "Per-leaf addenda split (vol. 1 vs vol. 2)",
                 "componentId": "pwg.fm.addenda",
                 "why": "The two addenda leaves belong to different volumes (their captions say so) but share one component; extent.items holds one count and there is no per-leaf volume field."},
                {"label": "Scan-file swap inside the vol. 1 front block",
                 "componentId": "pwg.fm.foreword-v1",
                 "why": "csldoc page 06 ('Foreword, 5') carries image pwg1-0000--07 and page 07 ('Abbreviations, 1') carries --06: the scan set's file order disagrees with the print order. sequence follows print; the schema has no file-order field, so the note lives here and in evidence."}],
})
