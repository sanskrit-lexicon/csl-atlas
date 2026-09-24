"""Emit data/megastructure/skd.json - the SKD megastructure pilot (H5324).

Hand-curated records kept as Python so each record stays one readable call;
run once to regenerate the committed JSON:  python scripts/megastructure/skd_components.py
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "data" / "megastructure" / "skd.json"
DOCX = "sanskrit-lexicon/csl-atlas:docs/refs/SKD_Front pages.docx"
DOCX_NOTE = "Unpaginated Word transcription of the Sanskrit front matter (1886 title + mukhabandhana + genealogy)."


def loc(page, image_no, printed=None):
    return {"scanSet": "skd-csldoc", "ref": f"{page:02d}",
            "image": f"skd_Page_{image_no:02d}_Image_0002.png", "printedPage": printed}


def locs(first_page, first_image, n, printed=None):
    return [loc(first_page + i, first_image + i, (printed[i] if printed else None)) for i in range(n)]


def comp(slug, seq, ctype, fn, title, langs, extent, scan, disposition, evidence,
         level="observed", decodes=(), transcriptions=(), parent=None, notes=None,
         secondary=(), ctype_note=None):
    rec = {
        "id": f"skd.fm.{slug}", "sequence": seq, "position": "front",
        "componentType": ctype, "componentTypeNote": ctype_note,
        "function": fn, "secondaryFunctions": list(secondary),
        "title": title, "languages": langs, "extent": extent,
        "decodes": list(decodes), "scanLocus": scan,
        "digitalDisposition": disposition, "transcriptions": list(transcriptions),
        "parent": parent, "evidenceLevel": level, "evidence": evidence, "notes": notes,
    }
    return rec


def ext(pages, printed=None, items=None, unit=None):
    return {"pages": pages, "printedRange": printed, "items": items, "itemsUnit": unit}


def t(as_printed, iast, english):
    return {"asPrinted": as_printed, "iast": iast, "english": english}


DOCX_T = [{"kind": "docx", "location": DOCX, "note": DOCX_NOTE}]
MUKHA = "skd.fm.mukhabandhana"

components = [
    comp("reprint-title-sanskrit", 1, "title-page", "identify",
         t("शब्दकल्पद्रुमः", "śabdakalpadrumaḥ", "Chowkhamba reprint title page, Devanāgarī (part one)"),
         ["san"], ext(1), [loc(1, 1)], "not-digitized",
         "csldoc skdpref01 scan viewed 24-09-2026: Chowkhamba Sanskrit Granthamālā series line, author, Vasu brothers, 'prathamo bhāgaḥ', Chowkhamba Sanskrit Series Office, Vārāṇasī."),
    comp("reprint-title-english", 2, "title-page", "identify",
         t("SHABDA-KALPADRUM", None, "Chowkhamba reprint title page, English (Chowkhamba Sanskrit Series Work No. 93, Part One)"),
         ["eng"], ext(1), [loc(2, 3)], "not-digitized",
         "csldoc skdpref02 scan viewed 24-09-2026: 'The Chowkhamba Sanskrit Series Work No. 93 ... by Raja Radha Kanta Deva, Part One'."),
    comp("publisher-note", 3, "publisher-note", "frame",
         t("PUBLISHER'S NOTE.", None, "Publisher's note to the third (Chowkhamba) edition"),
         ["eng"], ext(1), [loc(3, 5)], "not-digitized",
         "csldoc skdpref03 scan read 24-09-2026: states a 1961 photo-offset reprint sold out and presents this as the third edition.",
         notes="Dates the scanned copy: a post-1961 Chowkhamba photo-offset of the Vasu Devanāgarī edition."),
    comp("title-1886", 4, "title-page", "identify",
         t("शब्दकल्पद्रुमः", "śabdakalpadrumaḥ", "Title page of the Vasu Devanāgarī edition, part one (Calcutta, Śaka 1808)"),
         ["san"], ext(1), [loc(4, 7)], "transcribed",
         "csldoc skdpref04 scan viewed 24-09-2026; docx lines 5-25 transcribe it (imprint: kalikātā-rājadhānyām ... śakābdāḥ 1808).",
         transcriptions=DOCX_T,
         notes="csldoc captions this page '1888 Title'; the imprint reads Śaka 1808, i.e. 1886/87 CE. The long subtitle is itself a programme of the microstructure (liṅga, nānārtha, paryāya, pramāṇa, prayoga, dhātu with anubandha)."),
    comp("bhumika", 5, "preface", "frame", t("भूमिका", "bhūmikā", "Verse preface of the Vasu edition"),
         ["san"], ext(4, "(1)-(4)", None, None), locs(5, 9, 4, ["(१)", None, None, "(४)"]),
         "not-digitized",
         "csldoc skdpref05-08 scans viewed 24-09-2026: heading bhūmikā after 'śrījagadīśo jayati', numbered ślokas in two columns, signed at the end by Varadāprasāda Vasu and Haricaraṇa Vasu, Calcutta, 71 Pāthuriyāghāṭa, Śaka 1808.",
         secondary=["commemorate"],
         notes="Absent from the docx transcription; only the scan exists."),
    comp("testimonials", 6, "testimonials", "attest",
         t("OPINIONS OF LITERARY MEN ABOUT THE CELEBRATED SANSKRIT ENCYCLOPAEDIC LEXICON THE ŚABDAKALPADRUMA ...", None,
           "Opinions of scholars and learned societies on the Śabdakalpadruma"),
         ["eng", "san", "deu"], ext(8, "(1)-(8)", None, None), locs(9, 13, 8, [None] * 7 + ["(८)"]),
         "not-digitized",
         "csldoc skdpref09-16 scans viewed 24-09-2026: extracts of letters and society minutes (Asiatic Society, Royal Asiatic Society, European academies, Indian scholars); Sanskrit and German letters carry English translations.",
         notes="Reception layer that neither the docx nor csl-orig carries."),
    comp("mukhabandhana", 7, "introduction", "frame", t("मुखबन्धनं।", "mukhabandhanaṃ", "Introduction (mukhabandhana) of Rādhākāntadeva"),
         ["san"], ext(13, None, 17, "headed sub-sections"), locs(17, 21, 13), "transcribed",
         "csldoc skdpref17-29 scans viewed 24-09-2026 and aligned to docx headings (docx lines 27-920).",
         transcriptions=DOCX_T, secondary=["instruct", "decode", "source"],
         notes="Printed page numbers of scans 21-33 not legible at screen resolution; left null. Sub-sections are records with parent = this id."),
    comp("mangalacarana-slokah", 8, "benediction", "commemorate",
         t("तत्रादौ मङ्गलाचरणश्लोकाः।", "tatrādau maṅgalācaraṇaślokāḥ", "Opening benedictory verses"),
         ["san"], ext(0.1, None, 4, "verses"), [loc(17, 21)], "transcribed",
         "scan 21 top; docx lines 29-37.", transcriptions=DOCX_T, parent=MUKHA),
    comp("mangala-bija", 9, "introduction-section", "frame",
         t("ग्रन्थसमाप्तौ मङ्गलाचरणबीजं।", "granthasamāptau maṅgalācaraṇabījaṃ", "Why the benediction is printed at the completion of the work"),
         ["san"], ext(0.2), [loc(17, 21)], "transcribed",
         "scan 21; docx lines 39-41: the first kāṇḍa sold out before the benediction was written, so it heads the later kāṇḍa.",
         transcriptions=DOCX_T, parent=MUKHA),
    comp("prayojana", 10, "introduction-section", "frame",
         t("ग्रन्थरचनप्रयोजनं।", "grantharacanaprayojanaṃ", "Purpose of composing the work"),
         ["san"], ext(0.2), [loc(17, 21)], "transcribed", "scan 21; docx lines 43-45.",
         transcriptions=DOCX_T, parent=MUKHA),
    comp("namakarana", 11, "introduction-section", "frame",
         t("ग्रन्थस्य नामकारणं।", "granthasya nāmakāraṇaṃ", "Reason for the title Śabdakalpadruma"),
         ["san"], ext(0.1), [loc(17, 21)], "transcribed", "scan 21; docx lines 47-48.",
         transcriptions=DOCX_T, parent=MUKHA),
    comp("paripati", 12, "user-guide", "instruct",
         t("अथ ग्रन्थपरिपाटी।", "atha granthaparipāṭī", "Plan and conventions of the work"),
         ["san"], ext(1.3), [loc(17, 21), loc(18, 22)], "transcribed",
         "scans 21-22; docx lines 50-58: alphabetic order and the va/ba distinction, inclusion of Vopadeva's 1754 roots via Durgādāsa's Dhātudīpikā, gaṇa list, and 'roots without anubandha get a dot or a zero'.",
         decodes=[
             {"target": "headword order, including the separate places of vargya ba and antaḥstha va",
              "markup": None, "mechanism": "States the varṇakrama the whole alphabet follows and why the two va letters were separated through root derivation.", "atlasRef": None},
             {"target": "empty anubandha slot of a root entry",
              "markup": "slot after ¦ in root entries (e.g. 'aka¦, i ka ...')",
              "mechanism": "'yeṣāṃ dhātūnām anubandho nāsti tatsthānaṃ binduyuktam athavā śūnyam āste': a dot or 0 means no anubandha, never no verb.",
              "atlasRef": "docs/MICROSTRUCTURE_ZERO_MEANING.md"}],
         transcriptions=DOCX_T, parent=MUKHA, secondary=["decode"]),
    comp("sanketika", 13, "sigla-key", "decode",
         t("साङ्केतिकवर्णचिह्नादीनां विवरणं।", "sāṅketikavarṇacihnādīnāṃ vivaraṇaṃ", "Key to the conventional letters and signs"),
         ["san"], ext(0.4), [loc(18, 22)], "transcribed",
         "scan 22 (heading mid-page); docx lines 60-68.",
         decodes=[
             {"target": "gender labels", "markup": "puṃ / strī / klī / tri after the headword",
              "mechanism": "puṃ = masculine, strī = feminine, klī = neuter, tri = vācyaliṅga (adjective, all three genders).", "atlasRef": None},
             {"target": "sense and synonym separators", "markup": "daṇḍa । and double daṇḍa ॥",
              "mechanism": "one daṇḍa after a same-meaning word and before its authority; two after a different-meaning word and after the authority (irregular in the first kāṇḍa).", "atlasRef": None},
             {"target": "synonym numbering", "markup": "numerals after paryāya words",
              "mechanism": "the principal word counts as 1, its synonyms are numbered 2, 3, ...", "atlasRef": None},
             {"target": "grouped synonyms, section breaks and line-split words", "markup": "brace }, flower mark (*), short hyphen",
              "mechanism": "} closes a set of co-referential words; * separates a special account from the next sense or sub-topic; - marks a word broken across two lines.", "atlasRef": None},
             {"target": "page layout", "markup": None,
              "mechanism": "each page is split in two by a double rule; catchwords of the last word are given (column layout of the print).", "atlasRef": None}],
         transcriptions=DOCX_T, parent=MUKHA),
    comp("anubandha-key", 14, "grammatical-key", "decode",
         t("... षट्चत्वारिंशदनुबन्धवर्णानां फलानि लिख्यन्ते॥", None, "Effects of the 46 anubandha letters (from Durgādāsa's Dhātudīpikā)"),
         ["san"], ext(2.0, None, 46, "anubandha letters"), [loc(18, 22), loc(19, 23), loc(20, 24)], "transcribed",
         "scans 22 (foot) - 24 (top); docx lines 69-110, closing 'iti dhātudīpikāyāṃ anubandhaphalanirūpaṇaṃ'.",
         decodes=[{"target": "gaṇa, pada and operation of every root",
                   "markup": "anubandha slot right after ¦ in SKD root entries",
                   "mechanism": "each it-letter maps to a gaṇa (ka=curādi, ya=divādi, ...), a pada (ṅ=ātmane, ñ=ubhaya) or a morphophonemic operation.",
                   "atlasRef": "docs/MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md"}],
         transcriptions=DOCX_T, parent=MUKHA,
         notes="An embedded extract of another work (Dhātudīpikā on Vopadeva's Kavikalpadruma) serving as the dictionary's key; already applied by scripts/lexico/m4_indigenous.py (SKD gaṇa resolved 1,117 -> 1,737)."),
    comp("adikosa", 15, "introduction-section", "frame",
         t("आदिकोषविवरणं।", "ādikoṣavivaraṇaṃ", "Account of the earliest lexicons"),
         ["san"], ext(0.2), [loc(20, 24)], "transcribed", "scan 24; docx lines 120-121 (from the Agnipurāṇa lexicon onward).",
         transcriptions=DOCX_T, parent=MUKHA, secondary=["source"]),
    comp("prapta-kosa", 16, "source-list", "source",
         t("प्राप्तकोषादिनामानि।", "prāptakoṣādināmāni", "Lexicons obtained and excerpted"),
         ["san"], ext(0.4, None, 29, "numbered sources"), [loc(20, 24)], "transcribed",
         "scan 24 table; docx lines 122-152 numbered 1-29 (26 and 27 share one line).",
         transcriptions=DOCX_T, parent=MUKHA,
         decodes=[{"target": "authority citations in entries", "markup": "iti <source> at the end of a sense",
                   "mechanism": "lists the kośas SKD excerpts, so a body citation 'iti medinī' etc. resolves to a named work and author.", "atlasRef": None}]),
    comp("aprapta-kosa", 17, "source-list", "source",
         t("अप्राप्तकोषनामानि।", "aprāptakoṣanāmāni", "Lexicons known only through citation (Viśva- and Medinī-cited)"),
         ["san"], ext(0.5, None, 32, "numbered sources"), [loc(20, 24), loc(21, 25)], "transcribed",
         "scans 24 foot - 25; docx lines 154-192: viśvadhṛta 10 + medinīdhṛta 22.",
         transcriptions=DOCX_T, parent=MUKHA),
    comp("amara-tika", 18, "source-list", "source",
         t("लब्धालब्धामरकोषटीकानामानि।", "labdhālabdhāmarakoṣaṭīkānāmāni", "Commentaries on the Amarakośa, obtained and not obtained"),
         ["san"], ext(0.3, None, 35, "numbered commentaries"), [loc(21, 25)], "transcribed",
         "scan 25 table; docx lines 195-233.", transcriptions=DOCX_T, parent=MUKHA),
    comp("ahrta-visaya", 19, "scope-statement", "frame",
         t("अत्राहृतविषयबृन्दं शब्दसिन्धुदुस्तरत्वञ्च विज्ञापयामि।", None, "Subjects brought into the work, and the unfathomable ocean of words"),
         ["san"], ext(0.3), [loc(21, 25)], "transcribed",
         "scan 25 foot; docx lines 235-237.", transcriptions=DOCX_T, parent=MUKHA,
         notes="The docx footnotes this heading '[*] Splitted as per the original first edition'."),
    comp("parisista-karana", 20, "introduction-section", "frame",
         t("परिशिष्टकरणकारणम्।", "pariśiṣṭakaraṇakāraṇam", "Why the appendix (pariśiṣṭa) was made"),
         ["san"], ext(0.3), [loc(22, 26)], "transcribed",
         "scan 26 top; docx lines 239-242, closing with the dated completion verse of the seven-kāṇḍa work.",
         transcriptions=DOCX_T, parent=MUKHA),
    comp("mangala-19", 21, "benediction", "commemorate",
         t("अथ सर्व्वोपासकसम्मतमङ्गलाचरणोनविंशतिपद्यानि।", None, "Nineteen benedictory verses acceptable to every sect"),
         ["san"], ext(0.5, None, 19, "verses"), [loc(22, 26)], "transcribed",
         "scan 26; docx lines 244-282.", transcriptions=DOCX_T, parent=MUKHA),
    comp("pratijna", 22, "scope-statement", "frame",
         t("अथ ग्रन्थप्रतिज्ञानवश्लोकाः।", None, "Nine verses announcing the additions (the Vedanighaṇṭu)"),
         ["san"], ext(0.3, None, 9, "verses"), [loc(22, 26), loc(23, 27)], "transcribed",
         "scans 26 foot - 27 top; docx lines 284-303.", transcriptions=DOCX_T, parent=MUKHA),
    comp("vedanighantu", 23, "embedded-text", "source",
         t("तत्र प्रथमाध्याये ४१४ नामानि यथा।", None, "Synopsis of the Vedanighaṇṭu: five adhyāyas, varga by varga, with word counts"),
         ["san"], ext(0.5, None, 1769, "words counted in the tables (414+516+410+278+151)"),
         [loc(23, 27)], "transcribed", "scan 27 tables; docx lines 304-407.",
         transcriptions=DOCX_T, parent=MUKHA),
    comp("anukramanika-abhava", 24, "introduction-section", "frame",
         t("अथ ग्रन्थस्यानुक्रमणिकादिलेखनाभावकारणं वृत्तद्वयम्।", None, "Two verses on why no index or sigla list is repeated here"),
         ["san"], ext(0.1, None, 2, "verses"), [loc(23, 27)], "transcribed",
         "scan 27; docx lines 409-414: index, sigla and the appendix rationale were given in the seventh-kāṇḍa preface of the earlier edition.",
         transcriptions=DOCX_T, parent=MUKHA),
    comp("valmika", 25, "introduction-section", "frame",
         t("अथादर्शपत्राणां वल्मीकभक्षणजन्यमनस्तापतन्निवारणहेतुपञ्चपद्यानि।", None,
           "Five verses on the appendix copy eaten by termites and its remedy"),
         ["san"], ext(0.2, None, 5, "verses"), [loc(23, 27)], "transcribed",
         "scan 27 foot; docx lines 416-425.",
         decodes=[{"target": "absence of a separate appendix in this edition", "markup": None,
                   "mechanism": "termites destroyed much of the appendix printer's copy; the family reprinted SKD in Devanāgarī with the surviving appendix words and others merged into the work.",
                   "atlasRef": None}],
         transcriptions=DOCX_T, parent=MUKHA, secondary=["decode"]),
    comp("vamsa", 26, "genealogy", "commemorate",
         t("अथ ग्रन्थकर्तुर्व्वंशवर्णश्लोकाः।", None, "Verses on the author's lineage"),
         ["san"], ext(6), locs(24, 28, 6), "transcribed",
         "scans 28-33; docx lines 427-920 (verses numbered in groups up to 26).",
         transcriptions=DOCX_T, parent=MUKHA),
    comp("varnamala", 27, "transliteration-table", "decode", t("वर्णमाला।", "varṇamālā", "Table of letters"),
         ["san", "eng"], ext(1), [loc(30, 34)], "not-digitized",
         "csldoc skdpref30 scan viewed 24-09-2026: heading varṇamālā, a two-block table of Devanāgarī letters against an 'English' column and further script columns.",
         level="inferred",
         decodes=[{"target": "letters of the Devanāgarī print", "markup": None,
                   "mechanism": "maps each letter to an English (Roman) value and other script forms for readers unused to Devanāgarī.", "atlasRef": None}],
         notes="Not in the docx. csldoc files it as 'Introduction, 14' but it has its own heading and no sub-section 'atha' formula, so it is recorded outside mukhabandhana (parent null is the inferred part). Column headers beyond 'English' not legible at screen resolution."),
]

catalogue = {
    "schemaVersion": "1.0.0",
    "dict": "skd",
    "dictName": "Śabdakalpadruma (Rādhākāntadeva)",
    "edition": {
        "label": "Chowkhamba third edition (photo-offset) of the Vasu Devanāgarī edition, part one front matter",
        "year": "Vasu edition Śaka 1808 (1886/87 CE); Chowkhamba reprint after 1961",
        "imprint": "Calcutta, 71 Pāthuriyāghāṭa (Vasu); Chowkhamba Sanskrit Series Office, Vārāṇasī (reprint)",
        "evidenceLevel": "observed",
        "evidence": "Title pages csldoc skdpref01, 02, 04 and publisher's note skdpref03 viewed 24-09-2026.",
    },
    "scanSets": [{
        "id": "skd-csldoc", "kind": "cologne-csldoc",
        "description": "Cologne csldoc front-matter pages for SKD (30 pages, one scan image each, taken from a PDF whose even pages 2/4/6/8 are skipped).",
        "baseUrl": "https://sanskrit-lexicon.uni-koeln.de/scans/csldev/csldoc/build/dictionaries/prefaces/skdpref/",
        "inventory": "data/megastructure/scan_inventory.tsv",
    }],
    "components": components,
    "excludedScans": [],
    "knownGaps": [
        {"label": "Title pages of parts 2-5", "evidenceLevel": "inferred",
         "evidence": "Part one is 'prathamo bhāgaḥ'; the Cologne SKD body scans (csl-websanlexicon pdffiles.txt) begin each volume at its page 1 (1-001 ... 5-001) and csldoc shows part one only."},
        {"label": "Anything printed after body page 5-555 (errata, colophon)", "evidenceLevel": "inferred",
         "evidence": "The SKD scan-pdf map ends at 5-555 (pg5_555.pdf, headword hrIkA ... La) and csl-orig skd.txt ends on the same page; no back matter is scanned, so its existence cannot be observed from Cologne material."},
        {"label": "Seventh-kāṇḍa preface of the first (Bengali-script) edition with index and sigla", "evidenceLevel": "observed",
         "evidence": "Referred to in skd.fm.anukramanika-abhava (docx lines 409-414); belongs to the earlier edition, not the one scanned."},
    ],
    "notes": ("Trap: csl-orig v02/skd/skd_front.txt, skd_middle.txt and skd_back.txt are digitisation scaffolding "
              "(page markers such as '[Page1-002-b+ 52]'; skd_back.txt is empty) - not front or back matter. "
              "No back matter is visible in any Cologne SKD scan set; the appendix of the first edition is merged into the body "
              "(skd.fm.valmika). Body: 5 volumes, pages 315/937/792/565/555, one alphabet (L=42139 'asvaH' is a typo for hrasvaH, "
              "not an alphabet restart)."),
    "misfits": [
        {"label": "Printed page numbers of the mukhabandhana", "componentId": MUKHA,
         "why": "Devanāgarī folio numerals on scans 21-33 are not legible at the resolution viewed; printedPage left null rather than guessed."},
        {"label": "Fractional extents of sub-sections sharing a page", "componentId": None,
         "why": "extent.pages accepts fractions (0.1-0.5) estimated from the share of the page; they are estimates, and the record-level evidenceLevel cannot grade one field separately."},
    ],
}

OUT.write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {OUT} ({len(components)} components)")
