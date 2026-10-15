"""Emit data/megastructure/ap90.json - Apte's Practical Sanskrit-English
Dictionary megastructure record (H5325).

Run once to regenerate the committed JSON:  python scripts/megastructure/ap90_components.py

Evidence: all 15 AP90Scan tit_0001-tit_0015 pages fetched and viewed
24-09-2026 (contact sheets plus full-resolution views of tit_0012-tit_0015);
tail pages pg_1171-pg_1196 fetched and viewed to map the appendix boundaries
(body ends p. 1178; Appendix I pp. 1179-1189, II pp. 1190-1192, III
pp. 1193-1196); csl-doc ap90pref.rst and ap90app1-3.rst transcriptions read.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "data" / "megastructure" / "ap90.json"

TIT = {f"t{i:04d}": f"tit_{i:04d}.pdf" for i in range(1, 16)}


def tref(ref, printed=None):
    return {"scanSet": "ap90-scan-pdf-tit", "ref": ref, "image": TIT[ref], "printedPage": printed}


def brefs(a, b, printed=None):
    return [{"scanSet": "ap90-scan-pdf", "ref": f"{n}",
             "image": f"pg_{n}.pdf", "printedPage": str(n)} for n in range(a, b + 1)]


def comp(cid, seq, position, ctype, fn, title, extent, scan, disposition, evidence, level="observed",
         langs=("eng",), decodes=(), transcriptions=(), notes=None, secondary=(), ctype_note=None):
    return {"id": cid, "sequence": seq, "position": position, "componentType": ctype,
            "componentTypeNote": ctype_note, "function": fn, "secondaryFunctions": list(secondary),
            "title": title, "languages": list(langs), "extent": extent, "decodes": list(decodes),
            "scanLocus": scan, "digitalDisposition": disposition, "transcriptions": list(transcriptions),
            "parent": None, "evidenceLevel": level, "evidence": evidence, "notes": notes}


def ext(pages, printed=None, items=None, unit=None):
    return {"pages": pages, "printedRange": printed, "items": items, "itemsUnit": unit}


def t(as_printed, english):
    return {"asPrinted": as_printed, "iast": None, "english": english}


def rst(path, note=None):
    tr = {"kind": "docx", "location": f"sanskrit-lexicon/csl-doc:source/dictionaries/prefaces/{path}",
          "note": note or "Cologne csldoc page transcription."}
    return [tr]


components = [
    comp("ap90.fm.title", 1, "front", "title-page", "identify",
         t("THE PRACTICAL SANSKRIT-ENGLISH DICTIONARY.",
           "Title page of the first edition (Poona, Shiralkar & Co., 1890)"),
         ext(1), [tref("t0001")], "transcribed",
         "Scan tit_0001 viewed 24-09-2026: 'The Practical Sanskrit-English Dictionary. Containing Appendices on Sanskrit Prosody and important Literary & Geographical names in the ancient history of India. (For the use of schools and colleges.) By Vaman Shivram Apte M.A., Principal and Professor of Sanskrit, Fergusson College, Poona. (All Rights Reserved.) Poona: Shiralkar & Co., Booksellers &c. &c. Budhwar Peth. 1890'; handwritten marks top right.",
         transcriptions=rst("ap90pref.rst", "csldoc transcription of the title page and preface.")),
    comp("ap90.fm.imprint", 2, "front", "imprint", "identify",
         t("POONA: PRINTED AT THE 'ARYA VIJAYA' PRESS.",
           "Printer's imprint on the title verso (Arya Vijaya Press, 160 Budhwar Peth, Poona)"),
         ext(1), [tref("t0002")], "transcribed",
         "Scan tit_0002 viewed 24-09-2026: 'POONA: Printed at the \"Arya Vijaya\" Press. 160 Budhwar Peth.' with handwritten accession marks.",
         transcriptions=rst("ap90pref.rst")),
    comp("ap90.fm.preface", 3, "front", "preface", "frame",
         t("PREFACE.", "Apte's preface to the first edition"),
         ext(4, "1-4"), [tref("t0003"), tref("t0004", "(2)"), tref("t0005", "(3)"), tref("t0006", "(4)")], "transcribed",
         "Scans tit_0003-tit_0006 viewed 24-09-2026: printed pages (1)-(4), first page unnumbered, signed 'Poona, 28th December 1890. V. S. APTE.' with a Devanagari closing couplet.",
         transcriptions=rst("ap90pref.rst"),
         secondary=["decode", "source"],
         decodes=[
             {"target": "scope of the headword stock: Vedic vs classical usage",
              "markup": None,
              "mechanism": "p. (2): words are marked as Vedic or Classical or both, and as common or obsolete; the Vedic and the 'Bhashya' (classical) branches are deliberately kept as two distinct branches (Upanishads vs Vedanga class).",
              "atlasRef": None},
             {"target": "the sources behind the entries",
              "markup": "<ls> in ap90.txt",
              "mechanism": "p. (2): built on Böhtlingk-Roth and Wilson with the smaller aid-works, plus (p. 3) the Tarkasamgraha, Bhāṣāparichchheda and other philosophy manuals for the technical vocabularies, and Monier Williams, Goldstücker's Dictionary, the Petersburg Dictionary and Bohlen's Glossary where quotable.",
              "atlasRef": None},
             {"target": "prose-before-verse arrangement of quotations",
              "markup": None,
              "mechanism": "p. (3): 'the plan and arrangement of the work will be best understood by the Directions which follow', and quotations of prose composed before verse are so noted.",
              "atlasRef": None}]),
    comp("ap90.fm.directions", 4, "front", "user-guide", "instruct",
         t("DIRECTIONS TO BE STUDIED BEFORE USING THIS DICTIONARY.",
           "The fourteen numbered directions explaining the entry arrangement"),
         ext(2, "5-6"), [tref("t0007"), tref("t0008", "(6)")], "not-digitized",
         "Scans tit_0007-tit_0008 viewed 24-09-2026: fourteen numbered items; first page unnumbered, second printed (6).",
         secondary=["decode"],
         decodes=[
             {"target": "order of the parts of speech inside an entry",
              "markup": "sense and homonym order in ap90.txt entries",
              "mechanism": "direction 1 fixes the sequence: noun in large type with derivative parts of speech after it; within a noun the order is nom. of trees and plants, inferior animals, male human beings, women, objects common to both sexes, and things neither male nor female (direction 2, numerals by black dashes, etc.).",
              "atlasRef": None},
             {"target": "typographic conventions: synonyms, compounds, accents",
              "markup": "marker and bracket conventions in ap90.txt",
              "mechanism": "directions 5-8: several meanings distinguished by black figures; synonyms of the same meaning under one; compounds grouped under the first word with the black dash; semi-antiquated or Puranic forms marked 'v.r.'",
              "atlasRef": None},
             {"target": "grammar apparatus: conjugation signs and Krit/Taddhita references",
              "markup": "conjugation-class and suffix notations in ap90.txt",
              "mechanism": "directions 10-11: P., Atm. and U. signs with conjugation-class numbers; Krit and Taddhita words referenced to the Explanation of Terminations; direction 13 sends mythology to small type keyed to the Puranas and Kirtya.",
              "atlasRef": None}]),
    comp("ap90.fm.terminations", 5, "front", "grammatical-key", "decode",
         t("EXPLANATION OF TERMINATIONS USED IN THE DERIVATION OF WORDS.",
           "Key to the Krit and Taddhita terminations used in derivations"),
         ext(3, "7-9"), [tref("t0009"), tref("t0010", "(8)"), tref("t0011", "(9)")], "not-digitized",
         "Scans tit_0009-tit_0011 viewed 24-09-2026: two-column key 'N.B. Ter. stands for Termination, and Tad. for Taddhita', running (7)-(9), the last page closing with 'Note.-The Dhatus will be separately published hereafter.'",
         decodes=[{"target": "derivation suffixes quoted in entries",
                   "markup": "Krit/Taddhita termination references in ap90.txt entries",
                   "mechanism": "each termination (a, ka, tra, tana, lyu, u, ti, ktva...) is glossed with its function and examples, e.g. '(s) a Tad. ter. showing possession, as in ...'.",
                   "atlasRef": None}],
         notes="The promised separate publication of the Dhatus never forms part of this volume's scans."),
    comp("ap90.fm.abbreviations", 6, "front", "abbreviation-list", "decode",
         t("A LIST OF ABBREVIATIONS USED IN THE DICTIONARY.",
           "Abbreviations: I. of works and authors, II. grammatical and other symbols"),
         ext(3, "10-13"), [tref("t0013"), tref("t0014", "(12)"), tref("t0015", "(13)")], "not-digitized",
         "Scans tit_0013-tit_0015 viewed 24-09-2026: section I opens unnumbered with the head-note 'Except where otherwise specified, the Editions of works referred to are mostly those printed at Calcutta' and runs Ait. Br.-K. P.; page (12) carries Ks.-V. May.; page (13) closes the works list (Vop.-Yv., Yaj.), adds the note on Arabic figures (canto vs verse vs page) and opens 'II. Grammatical and other Abbreviations, and Symbols' (A./Atm.-lit., loc.-&c. plus the ° symbol).",
         secondary=["decode"],
         decodes=[
             {"target": "literary source abbreviations in entries", "markup": "<ls> in ap90.txt",
              "mechanism": "siglum = title with the edition used; the note fixes how one or two Arabic figures after a siglum are read (canto/chapter vs verse; a single figure = page).",
              "atlasRef": None},
             {"target": "grammatical abbreviations and symbols", "markup": "<ab>-style markers in ap90.txt",
              "mechanism": "part II expands them (a. = adjective, pass. = passive, pot. p. = potential passive participle, s.v. = sub voce, ° = elision supplying the rest of a word, etc.).",
              "atlasRef": None}],
         notes="The first page of the list is unnumbered and the intervening verso (scan tit_0012) is blank, so printed pages (10)-(11) are not identifiable as such on the scans; the numbered run resumes at (12)-(13)."),
    comp("ap90.bm.appendix1-prosody", 7, "back", "embedded-text", "instruct",
         t("APPENDIX I. SANSKRIT PROSODY.", "Appendix I: a compact manual of Sanskrit prosody (Introduction and Sections A-D of metres)"),
         ext(11, "1179-1189"), brefs(1179, 1189), "transcribed",
         "Scans pg_1179-pg_1189 viewed 24-09-2026: 'APPENDIX I. - SANSKRIT PROSODY.' opens printed p. 1179 with the Introduction (Piṅgala's eight-chapter work, Yādava Prakāśa's method, Śebaliṅkara's commentary, mātrā and guru/laghu definitions); pp. 1180-1189 hold Section A (metres with 4-14 syllables per quarter, Gāthā), Section B (Hallegal metres) and Sections C-D (samavṛtta and ardhasamavṛtta classes up to 28 syllables), each metre with definition, gana scheme and examples.",
         langs=("eng", "san"),
         transcriptions=rst("ap90app1.rst", "csldoc transcription of Appendix I.")),
    comp("ap90.bm.appendix2-writers", 8, "back", "source-list", "source",
         t("APPENDIX II.", "Appendix II: dates and notices of important Sanskrit writers"),
         ext(3, "1190-1192", None, "writer notices"), brefs(1190, 1192), "transcribed",
         "Scans pg_1190-pg_1192 viewed 24-09-2026: 'APPENDIX II. - Giving the dates &c. of important Sanskrit writers', Devanagari headwords with English notices in two columns (Aryabhata 'A well-known astronomer. Born A.D. 476' ... Madhavacarya 'flourished in the 14th century A.D.'), ending on p. 1192.",
         transcriptions=rst("ap90app2.rst", "csldoc transcription of Appendix II."),
         secondary=["attest"]),
    comp("ap90.bm.appendix3-geo", 9, "back", "embedded-text", "source",
         t("APPENDIX III.", "Appendix III: important geographical names in ancient India"),
         ext(4, "1193-1196"), brefs(1193, 1196), "transcribed",
         "Scans pg_1193-pg_1196 viewed 24-09-2026: 'APPENDIX III. - On important Geographical names in ancient India', Devanagari headwords with English notices (Aṅga 'N. of an important kingdom situated on the right bank of the Ganges ...' through Videha), ending p. 1196 with the closing ornament.",
         transcriptions=rst("ap90app3.rst", "csldoc transcription of Appendix III.")),
]

catalogue = {
    "schemaVersion": "1.0.0",
    "dict": "ap90",
    "dictName": "Apte, The Practical Sanskrit-English Dictionary",
    "edition": {"label": "First edition (Poona, Shiralkar & Co., 1890), as scanned by Cologne",
                "year": "1890", "imprint": "Printed at the 'Arya Vijaya' Press, 160 Budhwar Peth, Poona; sold by Shiralkar & Co.",
                "evidenceLevel": "observed",
                "evidence": "Title page and imprint scans viewed 24-09-2026; preface signed 'Poona, 28th December 1890.'"},
    "scanSets": [
        {"id": "ap90-scan-pdf-tit", "kind": "cologne-scan-pdf",
         "description": "Cologne AP90Scan preliminary pages tit_0001-tit_0015 (title, imprint, preface pp. 1-4, directions 5-6, terminations 7-9, one blank leaf, abbreviations). Empty captions in csl-websanlexicon pdffiles.txt.",
         "baseUrl": "https://www.sanskrit-lexicon.uni-koeln.de/scans/AP90Scan/AP90Scanpdf/",
         "inventory": "data/megastructure/scan_inventory.tsv"},
        {"id": "ap90-scan-pdf", "kind": "cologne-scan-pdf",
         "description": "Cologne AP90Scan printed back matter pg_1179-pg_1196: the three appendices that close the numbered pagination. The numbered body pages pg_0001-pg_1178 are not part of the megastructure and are not declared.",
         "baseUrl": "https://www.sanskrit-lexicon.uni-koeln.de/scans/AP90Scan/AP90Scanpdf/",
         "inventory": "data/megastructure/scan_inventory.tsv"}
    ],
    "components": components,
    "excludedScans": [
        {"scanSet": "ap90-scan-pdf-tit", "ref": "t0012",
         "reason": "Blank leaf (verso after the terminations key, before the abbreviations list); carries no printed content."}
    ],
    "knownGaps": [],
    "notes": ("The title page, imprint, preface and all three appendices are transcribed in Cologne csldoc (ap90pref.rst, ap90app1-3.rst); "
              "the directions and terminations keys exist only as scans. The appendices sit inside the dictionary's printed pagination "
              "(pp. 1179-1196) rather than being separately paginated; the body's last page is 1178. The preface's 'Directions' pointer "
              "and the small-type mythology keys are described on directions page (6)."),
    "misfits": [
        {"label": "Handwritten accession and shelf marks on the title and imprint scans", "componentId": None,
         "why": "Marks of the scanned copy or an intermediate library, not of the edition; the schema has no copy-level layer (same class as the MW pilot's stamp-leaf misfit)."}
    ],
}

OUT.write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {OUT} ({len(components)} components)")
