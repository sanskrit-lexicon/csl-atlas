"""Emit data/megastructure/vcp.json - the Vacaspatyam megastructure record (H5325).

Run once to regenerate the committed JSON:  python scripts/megastructure/vcp_components.py

Evidence: all 7 csldoc pages (vcppref01-07, images vac1_Page_007/008/009/010/
013/015/016) viewed 24-09-2026; the unmapped front block VCPScan pg0001-0034
fetched and viewed as labelled contact sheets plus full-resolution key pages
(pg0001, 0013-0018, 0025-0030, 0031-0034) the same day.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "data" / "megastructure" / "vcp.json"

CSLDOC = [
    ("01", "vac1_Page_007_Image_0002.png", "Title Page"),
    ("02", "vac1_Page_008_Image_0002.png", "Publisher"),
    ("03", "vac1_Page_009_Image_0002.png", "Title Page, vol. 1"),
    ("04", "vac1_Page_010_Image_0002.png", "Publisher's Note"),
    ("05", "vac1_Page_013_Image_0002.png", "Dedication"),
    ("06", "vac1_Page_015_Image_0002.png", "Preface"),
    ("07", "vac1_Page_016_Image_0002.png", "Contents"),
]


def loc(ref, printed=None):
    image = dict((r, i) for r, i, _ in CSLDOC)[ref]
    return {"scanSet": "vcp-csldoc", "ref": ref, "image": image, "printedPage": printed}


def comp(cid, seq, ctype, fn, title, extent, scan, disposition, evidence, level="observed",
         langs=("san",), decodes=(), notes=None, secondary=(), ctype_note=None):
    return {"id": cid, "sequence": seq, "position": "front", "componentType": ctype,
            "componentTypeNote": ctype_note, "function": fn, "secondaryFunctions": list(secondary),
            "title": title, "languages": list(langs), "extent": extent, "decodes": list(decodes),
            "scanLocus": scan, "digitalDisposition": disposition, "transcriptions": [],
            "parent": None, "evidenceLevel": level, "evidence": evidence, "notes": notes}


def ext(pages, printed=None, items=None, unit=None):
    return {"pages": pages, "printedRange": printed, "items": items, "itemsUnit": unit}


def t(as_printed, english, iast=None):
    return {"asPrinted": as_printed, "iast": iast, "english": english}


def pdf(ref, printed=None, image=None):
    return {"scanSet": "vcp-scan-pdf", "ref": ref, "image": image or f"pg{ref}.pdf", "printedPage": printed}


components = [
    comp("vcp.fm.series-title", 1, "title-page", "identify",
         t("वाचस्पत्यम् (बृहत् संस्कृताभिधानम्)", "Sanskrit series title page: Vacaspatyam, the great Sanskrit dictionary, part one (Chowkhamba Sanskrit Granthamala)"),
         ext(1), [loc("01")], "not-digitized",
         "csldoc vcppref01 scan viewed 24-09-2026: Chowkhamba Sanskrit Granthamala heading, 'वाचस्पत्यम् (बृहत् संस्कृताभिधानम्)', 'गणपतिदेवशास्त्रीविरचितव्याख्या-द्वितीय-आवृत्तिसमन्वितम्' (with Ganapati Sastri's second-recension commentary), 'श्रीतारानाथतर्कवाचस्पतिमहोदयेन सङ्कलितम्', 'प्रथमो भागः', Chowkhamba Sanskrit Series Office, Baranasi-1.",
         notes="The work's own series title names the commentary of Ganapati Sastri incorporated in this edition."),
    comp("vcp.fm.publisher-imprint", 2, "imprint", "identify",
         t("प्रकाशक: चौखम्बा संस्कृत पीठिज आफिस / The Chowkhamba Sanskrit Series Office",
           "Printer and publisher imprint of the scanned reprint (Varanasi, 1962)"),
         ext(1), [loc("02")], "not-digitized",
         "csldoc vcppref02 scan viewed 24-09-2026: Devanagari printer/publisher lines plus 'The Chowkhamba Sanskrit Series Office, P.O. Box 8, Varanasi-1 (INDIA) 1962, Phone: 3145'; handwritten shelf marks 'PK 925 T37 v.1' and '920660'.",
         notes="Dates the scanned copy to the 1962 Chowkhamba reprint of the 1873 Calcutta original."),
    comp("vcp.fm.title-english", 3, "title-page", "identify",
         t("VACHASPATYAM", "English title page: Vachaspatyam, a comprehensive Sanskrit dictionary, compiled by Sri Taranatha Tarkavachaspati, vol. I (Chowkhamba Sanskrit Series Work No. 94)"),
         ext(1), [loc("03")], "not-digitized",
         "csldoc vcppref03 scan viewed 24-09-2026: 'The Chowkhamba Sanskrit Series Work No. 94, VACHASPATYAM (A Comprehensive Sanskrit Dictionary), compiled by Sri Taranatha Tarkavachaspati, Professor of Grammar and Philosophy, Govt. Sanskrit College, Calcutta. Vol. I', Chowkhamba imprint 1962."),
    comp("vcp.fm.publisher-note", 4, "publisher-note", "frame",
         t("PUBLISHER'S NOTE.", "Publisher's note to the Chowkhamba reprint"),
         ext(1), [loc("04")], "not-digitized",
         "csldoc vcppref04 scan viewed 24-09-2026: English note praising the encyclopaedic scope (Vedas to Vastushastra; sixteen philosophy systems), claiming additions beyond Wilson's Dictionary, Radhakanta's Shabdakalpadruma and Böhtlingk's St. Petersburg dictionary, and explaining the reprint motive; carries a University of Toronto library stamp (AUG 17 1964) and accession number 920660.",
         secondary=["commemorate"]),
    comp("vcp.fm.dedication", 5, "dedication", "commemorate",
         t("THIS WORK IS DEDICATED TO HIS HIGHNESS SREE MAHARAJAH MEERZA ANANDA GAJAPATTI RAJ MUNEERA SULTAN BAHADOOR OF VIZIANAGARAM",
           "Dedication to the Maharaja of Vizianagaram, patron of Sanskrit learning"),
         ext(1), [loc("05")], "not-digitized",
         "csldoc vcppref05 scan viewed 24-09-2026: dedication 'in acknowledgement of the deep interest shewn by His Highness for the advancement of Sanskrit learning, and of the liberal patronage afforded to the cause of Sanskrit language by the ancestors of His Highness', signed 'Taranatha Tarkavachaspati, the Author'."),
    comp("vcp.fm.preface-woodrow", 6, "preface", "frame",
         t("PREFACE.", "Preface by H. Woodrow on the making and patronage of the dictionary"),
         ext(1), [loc("06")], "not-digitized",
         "csldoc vcppref06 scan viewed 24-09-2026: signed 'H. Woodrow, M.A., Inspector of Schools, Lower provinces of Bengal'; records Taranatha's Panini edition of 1863, the Government of Bengal patronage (letter No. 507, Fort William, 25th January 1866: 200 copies at Rs 50), the five-year extension (letter No. 3480, 12th December 1870), and the aim to exceed Wilson's Dictionary and the Shabdakalpadruma with Sanskrit explanations.",
         langs=("eng", "san"), secondary=["attest"],
         notes="A sponsor's preface, not the author's; names the bilingual purpose 'for the use of both Hindu and European scholars'."),
    comp("vcp.fm.contents", 7, "scope-statement", "instruct",
         t("CONTENTS.", "Contents: the seventeen subjects the dictionary undertakes to cover"),
         ext(1, None, 17, "numbered items"), [loc("07")], "not-digitized",
         "csldoc vcppref07 scan viewed 24-09-2026: seventeen numbered items, from 'Panini on genders', 'On the suffixes', 'On the primitive and derivative words' and the derivations drawn from Wilson's Dictionary and Radhakanta's Shabdakalpadruma, through Vaidik words, Śrauta and Gṛihya sūtra terms, philosophy systems, Hindu law, Puranas, Ramayana, ancient kings, geography, medicine, astronomy, astrology, and the technical words of the Tantras, politics, rhetoric, prosody, music, military science, cookery, Siksha, Kalpa, horses, Hatyoga and Vastushastra, to the classification of the Vedas.",
         secondary=["frame"],
         decodes=[{"target": "the dictionary's grammatical apparatus",
                   "markup": "gender marks (m./f./n.) and derivations inside vcp.txt entries",
                   "mechanism": "items 1-3 announce the Paninian apparatus: genders, suffixes, primitive and derivative words.",
                   "atlasRef": None}]),
    comp("vcp.fm.linganusasana", 8, "embedded-text", "decode",
         t("लिङ्गानुशासनम्", "Taranatha's own Sanskrit grammatical introduction: the Liṅgānuśāsana with its verse paricchiṣṭa (printed pp. 1-34 of vol. 1)"),
         ext(34, "1-34 (printed Devanagari १-३४)"),
         [pdf("0001..0034", "1-34 (printed Devanagari १-३४)")], "not-digitized",
         "All 34 VCPScan pages fetched and viewed 24-09-2026 (contact sheets; key pages at full resolution): opens 'प्रतिग्रह्यं लिङ्गविशेषणानामेव ... पाणिनीयमतम् सुदृढम्' with numbered rule-discussions (स्त्री 1, क्लिबं 5, स्त्रीप्रत्ययान्ताः षट् 7, ...), continues through gender-word lists and the 'शब्दविभागविचार' prose, and closes with the colophon naming the Liṅgānuśāsana of the Śabdārthacintāmaṇi ('इति श्रीमच्छब्दार्थचिन्तामणौ ... लिङ्गानुशासनम्') followed by the verse paricchiṣṭa ('परिशिष्ट इत्येष प्रबन्धः') and benediction verses; printed Devanagari page numbers १-३४ seen on the viewed leaves.",
         langs=("san",),
         decodes=[{"target": "gender assignment and suffix derivation behind the entries",
                   "markup": "gender marks and derivational explanations in vcp.txt entries (Contents items 1-3)",
                   "mechanism": "the treatise argues the Paninian doctrine of genders ( prati-grahya linga-visesanani ) and of primitive and derivative words that the entries apply; Taranatha cites sutra-by-sutra.",
                   "atlasRef": None}],
         secondary=["instruct"],
         ctype_note="An authorial treatise printed ahead of the letter A, not a display key: recorded as an embedded text that decodes the dictionary's grammatical notation.",
         notes="Internal section boundaries (liṅga rules, word lists, vibhaga-vicara, paricchiṣṭa) were classified from the viewed pages but not itemised page by page."),
]

catalogue = {
    "schemaVersion": "1.0.0",
    "dict": "vcp",
    "dictName": "Tarkavachaspati, Vachaspatyam (A Comprehensive Sanskrit Dictionary)",
    "edition": {"label": "Chowkhamba reprint (Varanasi, 1962) of the 1873 Calcutta edition, vol. I as scanned",
                "year": "1962 (reprint of 1873)", "imprint": "The Chowkhamba Sanskrit Series Office, Post Box 8, Varanasi-1",
                "evidenceLevel": "observed",
                "evidence": "Series title, English title page and imprint scans viewed 24-09-2026 ('1962'); Woodrow's preface records the 1866-1870 Bengali Government patronage of the original."},
    "scanSets": [
        {"id": "vcp-csldoc", "kind": "cologne-csldoc",
         "description": "Cologne csldoc front-matter pages for VCP (7 pages: two title pages, imprint, publisher's note, dedication, Woodrow's preface, contents), sampled from the volume's preliminary batch.",
         "baseUrl": "https://sanskrit-lexicon.uni-koeln.de/scans/csldev/csldoc/build/dictionaries/prefaces/vcppref/",
         "inventory": "data/megastructure/scan_inventory.tsv"},
        {"id": "vcp-scan-pdf", "kind": "cologne-scan-pdf",
         "description": "Cologne VCP page PDFs before the letter A: the author's Liṅgānuśāsana treatise, printed pp. 1-34 (pg0001-pg0034). These pages are served by the scan server but absent from csl-websanlexicon pdffiles.txt, which starts at pg0035 (first body page, 'a').",
         "baseUrl": "https://www.sanskrit-lexicon.uni-koeln.de/scans/VCPScan/VCPScanpdf/",
         "inventory": "data/megastructure/scan_inventory.tsv"}
    ],
    "components": components,
    "excludedScans": [],
    "knownGaps": [
        {"label": "Preliminary leaves between the contents and the treatise (blank or otherwise) that neither csldoc sampled nor the scan map lists",
         "evidenceLevel": "inferred",
         "evidence": "csldoc holds seven preliminary pages (csldoc refs 01-07, source-PDF pages 7-16); the server's unmapped front block pg0001-0034 is the printed treatise pp. 1-34; whether further unnumbered prelim leaves exist between them was not verifiable from the available surfaces."},
        {"label": "Front matter of volumes II-VI of the Vacaspatyam, if printed",
         "evidenceLevel": "inferred",
         "evidence": "Only volume I is scanned; the Cologne body map covers vol. I pages onward (pg0035 'a' to pg5441 'hruqa') and shows no later volume preliminaries."},
    ],
    "notes": ("The Cologne pdffiles.txt for vcp starts at ref 0035 with the first headword 'a'; the 34 preceding server pages (pg0001-0034) "
              "are the printed Liṅgānuśāsana and are not mapped anywhere - they were fetched and viewed directly. The csldoc pages come from "
              "the same volume's preliminary batch (csldoc image names carry their source-PDF page numbers 7-16)."),
    "misfits": [
        {"label": "University of Toronto library stamp and accession number on the publisher's note; handwritten shelf marks on the imprint page", "componentId": None,
         "why": "Marks of the scanned copy and its holding library, not of the edition; the schema has no copy-level layer (same class as the MW pilot's stamp-leaf misfit)."},
        {"label": "The author's grammatical treatise precedes the letter A without its own entry in any Cologne page map", "componentId": "vcp.fm.linganusasana",
         "why": "The 34 treatise pages exist only on the scan server, outside pdffiles.txt, so the schema's inventory-backed scan sets had to declare them as a hand-built inventory; a server-side page map that includes unmapped pre-body pages is not expressible."},
    ],
}

OUT.write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {OUT} ({len(components)} components)")
