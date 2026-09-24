"""Emit data/megastructure/wil.json - the Wilson megastructure record (H5325).

Run once to regenerate the committed JSON:  python scripts/megastructure/wil_components.py

Evidence: all 6 csldoc pages (wilpref01-06, images wilson_Page_001..006.jpg)
viewed 24-09-2026; the wil scan map's trailing tit-001..006.jpg checked as
duplicates of the same six pages (tit-001.jpg fetched and viewed 24-09-2026).
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "data" / "megastructure" / "wil.json"

CSLDOC = [
    ("01", "wilson_Page_001.jpg", "Title"),
    ("02", "wilson_Page_002.jpg", "Dedication"),
    ("03", "wilson_Page_003.jpg", "Preface, 1"),
    ("04", "wilson_Page_004.jpg", "Preface, 2"),
    ("05", "wilson_Page_005.jpg", "Preface, 3"),
    ("06", "wilson_Page_006.jpg", "Preface, 4"),
]


def loc(ref, printed=None):
    image = dict((r, i) for r, i, _ in CSLDOC)[ref]
    return {"scanSet": "wil-csldoc", "ref": ref, "image": image, "printedPage": printed}


def locs(a, b, printed=None):
    return [loc(f"{n:02d}", (printed[n - a] if printed else None)) for n in range(a, b + 1)]


def comp(cid, seq, ctype, fn, title, extent, scan, disposition, evidence, level="observed",
         langs=("eng",), decodes=(), notes=None, secondary=()):
    return {"id": cid, "sequence": seq, "position": "front", "componentType": ctype,
            "componentTypeNote": None, "function": fn, "secondaryFunctions": list(secondary),
            "title": title, "languages": list(langs), "extent": extent, "decodes": list(decodes),
            "scanLocus": scan, "digitalDisposition": disposition, "transcriptions": [],
            "parent": None, "evidenceLevel": level, "evidence": evidence, "notes": notes}


def ext(pages, printed=None, items=None, unit=None):
    return {"pages": pages, "printedRange": printed, "items": items, "itemsUnit": unit}


def t(as_printed, english):
    return {"asPrinted": as_printed, "iast": None, "english": english}


components = [
    comp("wil.fm.title", 1, "title-page", "identify",
         t("A DICTIONARY IN SANSCRIT AND ENGLISH",
           "Title page of the second edition, greatly extended (Calcutta, Education Press, 1832)"),
         ext(1), [loc("01")], "not-digitized",
         "csldoc wilpref01 scan viewed 24-09-2026: 'A Dictionary in Sanscrit and English; Translated, amended, and enlarged from an original compilation, prepared by learned natives for the College of Fort William. By H. H. Wilson. The second edition, greatly extended, and published under the sanction of the General Committee of Public Instruction in Bengal. Calcutta: printed at the Education Press, Circular Road: 1832. Sold by Parbury, Allen & Co. London'; handwritten shelf mark top left.",
         notes="The first edition (1819) is named on the preface's first page; the title itself documents the work's origin in a native compilation for Fort William College."),
    comp("wil.fm.dedication", 2, "dedication", "commemorate",
         t("TO HENRY THOMAS COLEBROOKE, Esq.", "Dedication to Henry Thomas Colebrooke"),
         ext(1), [loc("02")], "not-digitized",
         "csldoc wilpref02 scan viewed 24-09-2026: 'To Henry Thomas Colebrooke, Esq., Director of the Royal Asiatic Society of Great Britain, and for many years President of the Asiatic Society of Bengal, to whose aid and encouragement the Sanscrit Dictionary owed its first publication ... this work is inscribed, as a tribute of acknowledgement, admiration, and esteem, by H. H. Wilson.'"),
    comp("wil.fm.preface", 3, "preface", "frame", t("PREFACE.", "Preface to the second edition"),
         ext(4, "vii-x"), locs(3, 6, ["vii", "viii", "ix", "x"]), "not-digitized",
         "csldoc wilpref03-06 scans viewed 24-09-2026: pp. viii-x carry printed bracketed numbers ([viii], [ix], [x]); the first page is unnumbered (vii inferred, viii follows). Ends on p. x with Wilson 'on the eve of quitting India' and his election by the University of Oxford.",
         langs=("eng", "san"), secondary=["decode", "source"],
         decodes=[
             {"target": "order of senses inside an entry",
              "markup": "sense sequence in wil.txt entries",
              "mechanism": "p. ix: the first edition followed the source vocabularies (Amara-kośa first); the second edition gives precedence to 'the sense that seems most naturally to result from the etymology of the word', the others following by relation to the original purport.",
              "atlasRef": None},
             {"target": "provenance of the headword stock",
              "markup": None,
              "mechanism": "pp. vii-viii: the compilation embodies indigenous lexicography (native vocabularies and commentaries), with exceptions such as the Vaijayantī, Utpalinī, Śāśvat, Keśava and Śiva kośas barely used; verbal indices of printed books (Māgha, Kirātārjunīya, Hitopadeśa, Manu, Bhagavad Gītā, Gīta Govinda, Durgā Pāṭha, Amaru Śataka, Siddhānta Kaumudī, parts of Bhatti and Mitākṣarā) fed the additions, and Rādhākānta Deb's dictionary supplied material as far as the word prātardanda.",
              "atlasRef": None}],
         notes="p. ix: the second edition holds 'between fifty and sixty thousand' words, nearly double the first; per-particular vocabulary references were dropped to save space. pp. ix-x work the case of vas-('to serve') with its āśrita derivatives to show why dictionary senses cannot simply mirror translations."),
]

catalogue = {
    "schemaVersion": "1.0.0",
    "dict": "wil",
    "dictName": "Wilson, A Dictionary in Sanscrit and English",
    "edition": {"label": "Second edition, greatly extended (Calcutta, Education Press, 1832)",
                "year": "1832", "imprint": "Education Press, Circular Road, Calcutta; sold by Parbury, Allen & Co., London",
                "evidenceLevel": "observed",
                "evidence": "Title page scan viewed 24-09-2026; preface names the 1819 first edition."},
    "scanSets": [
        {"id": "wil-csldoc", "kind": "cologne-csldoc",
         "description": "Cologne csldoc front-matter pages for WIL (6 pages: title, dedication, preface pp. vii-x).",
         "baseUrl": "https://sanskrit-lexicon.uni-koeln.de/scans/csldev/csldoc/build/_images/",
         "inventory": "data/megastructure/scan_inventory.tsv"}
    ],
    "components": components,
    "excludedScans": [],
    "knownGaps": [
        {"label": "Any abbreviations key or advertisement leaves between the dedication and the preface, if printed",
         "evidenceLevel": "inferred",
         "evidence": "The preface runs [vii]-[x]; the scans hold no pages before it except title and dedication, and the body map starts at pg-001.jpg with no captions; nothing in the scan universe shows whether such leaves exist."},
    ],
    "notes": ("The WIL scan map's final rows t001-t006 (tit-001..006.jpg) duplicate the six csldoc pages (tit-001.jpg fetched and viewed "
              "24-09-2026: the same title page), so only the csldoc set is declared. No separately printed abbreviation key exists in the "
              "scanned front matter; the preface itself names the source works. Scans carry the Cologne caption strip ('H.H. Wilson, "
              "A Dictionary in Sanskrit and English, 2nd ed., Calcutta 1832' header, 'Institut of Indology & Tamil Studies University of "
              "Cologne Germany 21/10/07' footer) - see misfits."),
    "misfits": [
        {"label": "Scan-era caption strip printed onto every csldoc page image", "componentId": None,
         "why": "Header and footer naming the work, the Cologne scanning institute and the scan date (21/10/07) overlay the edition's pages; the schema has no scan-overlay layer."},
        {"label": "Handwritten shelf mark on the title page", "componentId": "wil.fm.title",
         "why": "A mark of the scanned copy, not of the edition; the schema has no copy-level layer (same class as the MW pilot's stamp-leaf misfit)."},
    ],
}

OUT.write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {OUT} ({len(components)} components)")
