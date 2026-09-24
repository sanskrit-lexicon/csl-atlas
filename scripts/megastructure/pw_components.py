"""Emit data/megastructure/pw.json - the 'pw' (Böhtlingk, Sanskrit-Wörterbuch in
kürzerer Fassung) megastructure record (H5325).

Run once to regenerate the committed JSON:  python scripts/megastructure/pw_components.py

Evidence: all 5 csldoc pages (pwpref01-05 images pw1-000-1..5.png) viewed
24-09-2026; end-matter practice cross-checked against csl-orig/v02/pw/pw.txt
(final entries at pc 7-390-c/d carry <info n="sup_7"/>).
NOTE: the Cologne code 'pw' is the KÜRZERE FASSUNG (Böhtlingk alone, 1879-1889);
'pwg' is the great Böhtlingk & Roth dictionary - per both TEI headers.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "data" / "megastructure" / "pw.json"

CSLDOC = [
    ("01", "pw1-000-1.png", "Title"),
    ("02", "pw1-000-2.png", "Foreword"),
    ("03", "pw1-000-3.png", "Abbreviations of Works, 1"),
    ("04", "pw1-000-4.png", "Abbreviations of Works, 2"),
    ("05", "pw1-000-5.png", "Abbreviations of Works, 3"),
]


def loc(ref, printed=None):
    image = dict((r, i) for r, i, _ in CSLDOC)[ref]
    return {"scanSet": "pw-csldoc", "ref": ref, "image": image, "printedPage": printed}


def comp(cid, seq, ctype, fn, title, extent, scan, disposition, evidence, level="observed",
         langs=("deu",), decodes=(), transcriptions=(), notes=None, secondary=()):
    return {"id": cid, "sequence": seq, "position": "front", "componentType": ctype,
            "componentTypeNote": None, "function": fn, "secondaryFunctions": list(secondary),
            "title": title, "languages": list(langs), "extent": extent, "decodes": list(decodes),
            "scanLocus": scan, "digitalDisposition": disposition, "transcriptions": list(transcriptions),
            "parent": None, "evidenceLevel": level, "evidence": evidence, "notes": notes}


def ext(pages, printed=None, items=None, unit=None):
    return {"pages": pages, "printedRange": printed, "items": items, "itemsUnit": unit}


def t(deu, english):
    return {"asPrinted": deu, "iast": None, "english": english}


components = [
    comp("pw.fm.title", 1, "title-page", "identify",
         t("SANSKRIT-WÖRTERBUCH IN KÜRZERER FASSUNG ... ERSTER THEIL. DIE VOCALE.",
           "Title page of Part 1, 'Die Vocale', St. Petersburg 1879"),
         ext(1), [loc("01")], "not-digitized",
         "csldoc pwpref01 scan viewed 24-09-2026: 'Sanskrit-Wörterbuch in kürzerer Fassung bearbeitet von Otto Böhtlingck. Erster Theil. Die Vocale. St. Petersburg. Buchdruckerei der Kaiserlichen Akademie der Wissenschaften. 1879', plus acquisition lines (Eggers & Comp., Leopold Voss) and the price '3 Rbl 50 Cop. Silb. = 11 Mark 70 Pf.'; handwritten shelf mark 'Ke 1/879' top right.",
         notes="The Cologne code 'pw' is Böhtlingk's shorter redaction of the Petersburg dictionary, published in parts from 1879; the great Böhtlingk & Roth dictionary is Cologne's 'pwg'."),
    comp("pw.fm.vorwort", 2, "preface", "frame", t("VORWORT.", "Preface (Vorwort) of Otto Böhtlingk"),
         ext(2, "III-IV"), [loc("02"), loc("03", "IV")], "not-digitized",
         "csldoc pwpref02-03 scans viewed 24-09-2026: first page unnumbered (III by sequence, IV follows), text runs to mid-p. IV and ends 'Zum Schluss lasse ich das Verzeichniss der in diesem ersten Theile citirten Werke folgen'; signed 'Jena, den 1sten Mai 1879. O. Böhtlingk.' at the end of the abbreviation list on p. VI.",
         secondary=["decode", "source"],
         decodes=[
             {"target": "words attested only by grammarians or lexicographers",
              "markup": None,
              "mechanism": "such words, meanings, constructions and genders carry a star (*); a word invented ad hoc by a grammarian is marked as literary usage via the Bhāṭṭikāvya note.",
              "atlasRef": None},
             {"target": "two-number citations without a work siglum",
              "markup": "<ls> numeric-only citations in pw.txt",
              "mechanism": "they refer to the second edition of Böhtlingk's Chrestomathie.",
              "atlasRef": None},
             {"target": "relation to the great Petersburg dictionary",
              "markup": None,
              "mechanism": "the shorter work improves and adds where possible, drops the apparatus, and refers the reader back to the great dictionary as the store of citations; its corrections ('Nachträge') of the parent work are incorporated.",
              "atlasRef": None}],
         notes="Thanks Roth, Kern, Stenzler and Weber first, then Cappeller, Delbrück, Gārbe, Geldner, Jolly, Leskien, Muir, Pischel, Schiefner, Leopold Schröder and W. O. E. Windisch."),
    comp("pw.fm.abbreviations", 3, "abbreviation-list", "decode",
         t(None, "Verzeichniss der in diesem ersten Theile citirten Werke (key to cited works)"),
         ext(3, "IV-VI"), [loc("03", "IV"), loc("04", "V"), loc("05", "VI")], "not-digitized",
         "csldoc pwpref03-05 scans viewed 24-09-2026: starts under the Vorwort on p. IV, two columns run V-VI and close with the signature 'Jena, den 1sten Mai 1879. O. Böhtlingk.'; a Universität zu Köln 'Seminar für Indologie' stamp sits below the signature.",
         secondary=["source"],
         decodes=[
             {"target": "literary source abbreviations in entries", "markup": "<ls> in pw.txt",
              "mechanism": "siglum = title with the edition used, e.g. 'AK. = Amarakoça, Ausg. von Loiseleur Deslongchamps', 'H. = Hemâçandra's Abhidhânacintâmani, Ausg. von Böhtlingk und Rieu'.",
              "atlasRef": None},
             {"target": "contributor attribution carried inside a siglum",
              "markup": "<ls> entries with a parenthesised name",
              "mechanism": "p. IV: 'Der am Ende eines Titels in Klammern stehende Name bezeichnet den Gelehrten, der die Beiträge für dieses Wörterbuch aus dem angegebenen Bücher ganz oder zum grössten Theile geliefert hat', e.g. '(Roth)', '(Kern)', '(Pischel)'.",
              "atlasRef": None}],
         notes="The list mixes editions, manuscripts ('Hdschr.'), catalogues of manuscripts and journals; p. IV opens by explaining why the Nachträge grew so large (late contributions, an under-exploited press advantage)."),
]

catalogue = {
    "schemaVersion": "1.0.0",
    "dict": "pw",
    "dictName": "Böhtlingk, Sanskrit-Wörterbuch in kürzerer Fassung",
    "edition": {"label": "St. Petersburg 1879 ff., published in parts (Part 1 'Die Vocale' 1879), as scanned by Cologne",
                "year": "1879", "imprint": "Buchdruckerei der Kaiserlichen Akademie der Wissenschaften, St. Petersburg",
                "evidenceLevel": "observed",
                "evidence": "Title page scan viewed 24-09-2026; Vorwort signed 'Jena, den 1sten Mai 1879'."},
    "scanSets": [
        {"id": "pw-csldoc", "kind": "cologne-csldoc",
         "description": "Cologne csldoc front-matter pages for PW (5 pages: Part-1 title, Vorwort, and the key to cited works).",
         "baseUrl": "https://sanskrit-lexicon.uni-koeln.de/scans/csldev/csldoc/build/_images/",
         "inventory": "data/megastructure/scan_inventory.tsv"}
    ],
    "components": components,
    "excludedScans": [],
    "knownGaps": [
        {"label": "Front matter of Parts 2-7 of the kürzeren Fassung (if any was printed beyond the Part-1 preliminaries)",
         "evidenceLevel": "inferred",
         "evidence": "Only Part 1 has csldoc pages; the body scan map starts at ref 1-001 with no captions and cannot show whether later parts carried their own Vorworte."},
        {"label": "Title verso / printer's imprint of Part 1, if printed",
         "evidenceLevel": "inferred",
         "evidence": "The single scanned title leaf is unnumbered; a verso was not scanned and cannot be confirmed from the body map."},
    ],
    "notes": ("Per-volume additions are printed inside the alphabetical sequence (csl-orig pw.txt marks them <info n=\"sup_7\"/> in the final "
              "Part-7 entries at pc 7-390-c/d), so there is no separately paginated back-matter section to catalogue. "
              "The scans carry Cologne caption strips (header 'O. Boehtlingk, Sanskrit-Wörterbuch, Erster Theil, St. Petersburg 1879', "
              "footer 'Institute of Indology & Tamil Studies Cologne University Germany 10/1/07') - see misfits."),
    "misfits": [
        {"label": "Scan-era caption strip printed onto every csldoc page image", "componentId": None,
         "why": "Header and footer naming the work, the Cologne scanning institute and the scan date (10/1/07) overlay the edition's pages; the schema has no scan-overlay layer."},
        {"label": "Universität zu Köln 'Seminar für Indologie' library stamp on p. VI, and the handwritten shelf mark 'Ke 1/879' on the title page", "componentId": None,
         "why": "Marks of the scanned copy and its holding library, not of the edition; the schema has no copy-level layer (same class as the MW pilot's stamp-leaf misfit)."},
    ],
}

OUT.write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {OUT} ({len(components)} components)")
