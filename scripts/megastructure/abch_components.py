"""Emit data/megastructure/abch.json - Hemacandra's Abhidhānacintāmaṇi (H5325).

Run once to regenerate the committed JSON:  python scripts/megastructure/abch_components.py

Evidence: all 14 f-pages (f01-f14) and pg05, pg06, pg07, pg56, pg57, pg58
fetched from the Cologne scan PDFs and viewed 24-09-2026; the page numbers of
f12 (2), f13 (3), f14 (4), pg05 (5), pg06 (6), pg07 (7), pg56 (56), pg57 (57)
and pg58 (58) were read off the page headers at 350 dpi. Edition facts are from
csl-orig/v02/abch/abchheader.xml and the catalogue's own metadata block
(abch.txt), because the scanned copy's title page gives the 1896 imprint itself.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "data" / "megastructure" / "abch.json"

BASE = "https://www.sanskrit-lexicon.uni-koeln.de/scans/ABCHScan/pdfpages/"


def fref(ref, printed=None):
    return {"scanSet": "abch-scan-pdf", "ref": ref, "image": f"{ref}.pdf", "printedPage": printed}


def pref(n, printed=None):
    return {"scanSet": "abch-scan-pdf", "ref": f"{n:02d}", "image": f"pg{n:02d}.pdf",
            "printedPage": printed or str(n)}


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
    comp("abch.fm.title-en", 1, "front", "title-page", "identify",
         t("THE ABHIDHĀNA-SAṂGRAHA or A Collection of Sanskrit Ancient Lexicons. Nos. 6, 7, 8, 9, 10. "
           "THE ABHIDHĀNA-CHINTĀMAṆI, THE ABHIDHĀNA-CHINTĀMAṆI-PARIŚIṢṬA, THE ANEKĀRTHA-SAṂGRAHA, "
           "THE NIGHANṬU-ŚESHA AND THE LINGĀNUŚĀSANA of HEMACHANDRA. AND No. 11. "
           "THE ABHIDHĀNA-CHINTĀMAṆI-ŚILONCHCHHA of JINADEVA MUNIŚVARA. Edited by Paṇḍit Śivadatta and "
           "Kāśīnāth Pāṇḍuraṅg Parab. Printed and published by the proprietor, the Nirṇaya-sāgara Press. "
           "Bombay. 1896. [Price 11, Rs. 2]",
           "English title page of the volume, giving the collection's six works, its editors, the press and the year 1896"),
         ext(1), [fref("f01")], "not-digitized",
         "Scan f01 viewed 24-09-2026: the English title page, with the filing line 'Registered according to Act XXV of 1867' and '(All rights reserved by the publishers)' set in the middle of the page, and a 'Digitized by Google' watermark at the foot.",
         langs=("eng",), secondary=["frame"]),
    comp("abch.fm.title-sa", 2, "front", "title-page", "identify",
         t("॥ श्रीः ॥ अभिधानसंग्रहः नाम संस्कृतप्राचीनकोशग्रन्थसमुच्चयः । तत्र (६, ७, ८, ९, १०) श्रीमदाचार्यहेमचन्द्रविरचिताः "
           "अभिधानचिन्तामणि-अभिधानचिन्तामणिपरिशिष्ट-अनेकार्थसंग्रह-निघण्टुशेष-लिङ्गानुशासनकोशाः । (११) जिनदेवमुनिवरविरचितः "
           "अभिधानचिन्तामणिशीलोञ्छः ।",
           "Devanagari title page of the collection, naming its six kośas (Nos. 6-11) and its editors"),
         ext(1), [fref("f02")], "not-digitized",
         "Scan f02 viewed 24-09-2026: the Devanagari title page, 'Abhidhānasaṃgraha, a collection of ancient Sanskrit lexicons', with the six works listed by number, the editors' names, and a 'Digitized by Google' watermark.",
         secondary=["frame"]),
    comp("abch.fm.preface", 3, "front", "preface", "frame",
         t("प्रस्तावना", "The editors' preface (प्रस्तावना), in Devanagari prose with English bibliographic citations"),
         ext(4), [fref("f03"), fref("f04"), fref("f05"), fref("f06")], "not-digitized",
         "Scans f03-f06 viewed 24-09-2026: the preface, opening 'अभिधानसंग्रह हा संस्कृत भाषेतील जुने कोश या ग्रन्थांमधील कोश ... हेमचन्द्राचार्य' (the collection's scope and the editors' account of the manuscripts used), citing Dr. P. Peterson's 'A Third Report', W. Wright, Bühler, Zachariae, Weber, Th. Aufrecht, G. Bühler and others, and closing with the enumeration of the six kośas of the volume (1. अभिधानचिन्तामणि: - व्यवहारकोशः; 2. अभिधानचिन्तामणिपरिशिष्ट; 3. अनेकार्थसंग्रहः; 4. निघण्टुशेषः; 5. लिङ्गानुशासनम्; 6. अभिधानचिन्तामणिशीलोञ्छः).",
         langs=("san", "eng"),
         decodes=[{"target": "the provenance of the printed text",
                   "markup": None,
                   "mechanism": "the preface names the manuscripts and the earlier reports from which the editors established the text of each kośa, so the edition's stemma is recoverable from it.",
                   "atlasRef": None}],
         secondary=["source"],
         notes="The volume is No. 6-11 of the 'Abhidhāna-saṃgraha' series; the scanned volume carries only No. 6, the Abhidhānacintāmaṇi (58 printed pages), so the preface's other five kośas are not in this scan set."),
    comp("abch.fm.introduction", 4, "front", "introduction", "frame",
         t("हेमचन्द्रः ।", "Introduction on Hemacandra's date and the Chaulukya kings, running head 'हेमचन्द्रः'"),
         ext(5), [fref("f07"), fref("f08"), fref("f09"), fref("f10"), fref("f11")], "not-digitized",
         "Scans f07-f11 viewed 24-09-2026: an unpaginated Sanskrit introduction under the running head 'हेमचन्द्रः', establishing Hemacandra's date from the Hemakumāracarita and the Prabandhakośa ('इति हेमकुमारचरित्रकाव्ये हेमचन्द्राचार्याणां देवलोकगमनस्योक्तेश्च कुमारपालराज्यसमय एवाचार्यो हेमचन्द्रसमयः ...'), with the genealogy verses of the Chaulukya kings (Mūlarāja, Cāmuṇḍarāja, Durlabharāja, Bhīmadeva, Karṇadeva, Siddharāja Jayasiṃha) and their Vaṃśa dates given in footnotes ('मूलराजराज्यम् — विo संo ९६३-१०५३' etc.), closing with the list of the works of the collection headed '९. लिङ्गानुशासनम्'.",
         langs=("san",),
         decodes=[{"target": "the chronology behind the author's floruit",
                   "markup": None,
                   "mechanism": "the introduction fixes Hemacandra's date by synchronising the Hemakumāracarita's account of his death with Kumārapāla's reign, and gives each Chaulukya king's reign in Vaṃśa-saṃvat years in the footnotes.",
                   "atlasRef": None}],
         notes="The five introduction pages carry no printed page number; the volume's printed pagination starts with the kośa itself."),
    comp("abch.bm.colophon", 5, "back", "colophon", "attest",
         t("इति श्रीहेमचन्द्राचार्यविरचितोऽभिधानचिन्तामणिः समाप्तः ॥",
           "Closing colophon: 'Thus ends the Abhidhānacintāmaṇi composed by Śrī Hemacandrācārya'"),
         ext(1, "58"), [pref(58)], "not-digitized",
         "Scan pg58 viewed 24-09-2026: the volume's last page (printed 58), head 'अभिधानसंग्रहः—६ अभिधानचिन्तामणिः', carrying the final verses (to 1542) and the closing colophon at the foot of the right column. The same colophon closes the kāṇḍa at printed page 57.",
         secondary=["commemorate"],
         notes="The colophon is printed at the foot of the last text page, not on a separate leaf."),
]

catalogue = {
    "schemaVersion": "1.0.0",
    "dict": "abch",
    "dictName": "Hemacandra, Abhidhānacintāmaṇi (No. 6 of the Abhidhānasaṃgraha collection)",
    "edition": {
        "label": "Abhidhānasaṃgraha: a collection of Sanskrit ancient lexicons, No. 6-11, edited by Paṇḍit Śivadatta and Kāśīnāth Pāṇḍuraṅg Parab; the scanned volume carries No. 6, Hemacandra's Abhidhānacintāmaṇi",
        "year": "1896",
        "imprint": "The Nirṇaya-sāgara Press, Bombay",
        "evidenceLevel": "observed",
        "evidence": ("The English title page (scan f01) and the Devanagari title page (scan f02) both give the editors, the Nirṇaya-sāgara Press and the year 1896, matching "
                     "csl-orig/v02/abch/abchheader.xml (Hemacandra, Abhidhānacintāmaṇi, Bombay, The Nirṇaya-sāgara press, 1896, 58 p.) and the abch.txt metadata block "
                     "(editors Paṇdit Śivadatta and Kāśīnāth Pāṇḍuraṅg Parab, publisher The Nirṇaya-sāgara press, Bombay, 1896 A.D.). The abch.txt credits record that the "
                     "scanned book came from Acharya Shri Kailasasagarasuri Gyanamandir (kobatirth.org) and that Google OCR supplied the raw data, which is why every scan "
                     "carries a 'Digitized by Google' watermark."),
    },
    "scanSets": [
        {"id": "abch-scan-pdf", "kind": "cologne-scan-pdf",
         "description": ("Cologne ABCH page PDFs: the f series f01-f14 (English and Devanagari title pages, the four-page preface, and the five-page introduction on "
                         "Hemacandra, followed by printed pages 2, 3 and 4 of the kośa) and the numbered series pg05-pg58 (printed pages 5-58, the body of the "
                         "Abhidhānacintāmaṇi). Printed page 1 of the kośa is in neither series. The volume is a Google-digitized copy and every page carries a "
                         "'Digitized by Google' watermark."),
         "baseUrl": BASE,
         "inventory": "data/megastructure/scan_inventory.tsv"}
    ],
    "components": components,
    "excludedScans": [
        {"scanSet": "abch-scan-pdf", "ref": "f12",
         "reason": "Printed page 2 of the kośa (head 'अभिधानसंग्रहः—६ अभिधानचिन्तामणिः', verses 4-9 with the commentary). Body text, scanned in the f series because the dictionary's own page refs begin at printed page 5."},
        {"scanSet": "abch-scan-pdf", "ref": "f13",
         "reason": "Printed page 3 of the kośa (head '१ देवाधिदेवकाण्डः', verses 10-15 with the commentary). Body text, same reason."},
        {"scanSet": "abch-scan-pdf", "ref": "f14",
         "reason": "Printed page 4 of the kośa (head 'अभिधानसंग्रहः—६ अभिधानचिन्तामणिः', verses 16-23 with the commentary). Body text, same reason."},
    ],
    "knownGaps": [
        {"label": "Printed page 1 of the Abhidhānacintāmaṇi (the kośa's opening verses)",
         "evidenceLevel": "observed",
         "evidence": ("The f series ends at f14 (printed page 4, verses 16-23) and the numbered series begins at pg05 (printed page 5, kāṇḍa 1); pg01-pg04 were probed "
                      "on the scan server 24-09-2026 and all return HTTP 404, and f15/f16 do not exist. The page carrying the kośa's invocatory and first verses is "
                      "therefore in neither series of the scan set.")},
    ],
    "notes": ("The scan set is a Google-digitized copy from Acharya Shri Kailasasagari Gyanamandir (kobatirth.org): every page carries a 'Digitized by Google' watermark, "
              "and the f-series mixes true front matter with the kośa's printed pages 2-4. The volume is item No. 6 of the six-work 'Abhidhānasaṃgraha' collection named on "
              "both title pages, but it carries only the Abhidhānacintāmaṇi: the kośa's own pagination runs 1-58 and its kāṇḍas are 1 देवाधिदेवकाण्ड (printed page 1), "
              "2 देवकाण्ड (opens printed page 7), and, at the end, 5 सामान्यकाण्ड (closing at printed page 57), after which the colophon closes the work. The dictionary's "
              "digitized text in csl-orig/v02/abch/abch.txt covers printed pages 5-58."),
    "misfits": [
        {"label": "One scan set whose pages are two different kinds of matter", "componentId": None,
         "why": ("The f series is Cologne's front-matter scan set for this dictionary, but f12-f14 are printed pages 2-4 of the kośa body. The schema can declare a scan "
                 "set only as a whole and each page either belongs to a component or is excluded; there is no way to say 'this set is front matter except for its last "
                 "three pages, which are body'. Those three pages are recorded in excludedScans.")},
        {"label": "The volume is one item of a numbered collection", "componentId": None,
         "why": ("Both title pages announce the 'Abhidhānasaṃgraha' series and its six kośas, and the volume is No. 6; the schema's edition block has no series, "
                 "volume-in-series or 'items not present in this volume' field, so the series relation is stated in the edition label and the notes.")},
        {"label": "'Digitized by Google' watermark on every page", "componentId": None,
         "why": "A mark of the digitizing contractor, not of the edition; the schema has no scan-artefact layer (same class as the MW pilot's stamp-leaf misfit)."},
    ],
}

OUT.write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {OUT} ({len(components)} components)")
