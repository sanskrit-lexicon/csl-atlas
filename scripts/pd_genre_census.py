#!/usr/bin/env python3
"""PD genre-composition census (H6930).

Question: does the letter-a citation mass of *An Encyclopaedic Dictionary of
Sanskrit on Historical Principles* (PD, Deccan College) show epigraphy and
traditional grammar as materially exploited genres (Wright 1978), or are they
marginal?

Two independent layers of PD's citation apparatus are classified into nine
genres and both are reported:

  D1  declared works   -- pd_aob_declared_works.tsv, one row per work
                          (1,112 work-level rows; the printed AOB yields 1,419
                          edition-level rows, see pd_dcs_metrics.json)
  D2  exercised        -- pd_siglum_families.tsv: 353,512 primary citation
      occurrences         occurrences over 4,988 primary sigla, the
                          pre-registered denominator.  It does not depend on
                          the 1,419-vs-1,112 declared-work dispute.

Both occurrence denominators in the TSV sum to 100 %:

  pct_of_353512   occurrences of primary-class sigla / 353,512
                  (the pre-registered denominator named by handoff H6930)
  pct_of_361310   the same plus two works the upstream splitter parked outside
                  the primary mass on structural/secondary-bookkeeping grounds,
                  although they are works rather than locators: Panini's sutras
                  (siglum "P.", 4,517) and Epigraphia Indica (siglum "EI.",
                  3,281).  353,512 + 4,517 + 3,281 = 361,310.

CLASSIFIER.  AOB titles are machine-OCR and heavily mangled ("Vyākare
anamahabhāsya" for Vyākaraṇamahābhāṣya, "Siddl hantakaumudi" for
Siddhāntakaumudī), so token matching alone misfires.  Three ordered channels:

  1. SIGLUM_GENRE -- the highest-mass sigla, resolved by hand against the AOB
     title list and pinned here (they carry about two thirds of primary mass).
  2. FUZZY_WORKS -- a canonical-work lexicon matched by Dice coefficient over
     character bigrams (OCR-tolerant, symmetric, no alignment needed).  Accept
     at >= 0.68 with a >= 0.02 margin over the runner-up genre.
  3. RULES -- a small set of anchored stem rules for the long tail.

Anything left is "other"; the residual mass is reported, never hidden.

SUBJECT-CODE CROSSWALK (H6946).  The nine genre classes are crosswalked to the
62 printed subject classes of PD's *Subject-wise Classification and Approximate
Chronology of the Works* (PD/SWC.md, pp. LXXIII-LXXXI,
https://github.com/sanskrit-lexicon/PD/blob/main/SWC.md).  The same numbered
scheme (1-62) is the subject-code apparatus of the printed Index of Works
(pp. LXXXIX-CXXVII); H6945 transcribes that per-work index separately.  The
crosswalk is one-to-many: a genre owns every printed class that its classifier
would draw from.  The residual "other" genre is the explicit unmapped bucket,
and its share is carried in pd_genre_subject_crosswalk.tsv.  The union of the
mapped codes is validated to cover 1-62 exactly once, so no printed class is
silently dropped.  Genre shares are copied from the census table and never
recomputed from the crosswalk.

TWO INDEPENDENT ANCHORS (not derived from the PD data):

  epigraphy -- Sircar, *Indian Epigraphical Glossary* (IEG), Cologne
      digitisation (csl-orig/v02/ieg/ieg.txt: 7,932 <L> entries, headword list
      and entry text).  The handoff assumed the IEG was scan-only; the estate
      actually holds the machine-readable Cologne text, so that limitation is
      lifted and the anchor uses IEG's own bibliographic apparatus -- the
      epigraphic corpora it cites in <ls> tags.  The counts in IEG_SOURCES were
      extracted 17-10-2026 with:
        grep -o '<ls>[^<]*</ls>' ieg.txt | sed 's/<ls>//;s/<\\/ls>//' \\
          | sort | uniq -c | sort -rn
      IEG_EPIGRAPHIC_CORPORA keeps the epigraphic publications and drops the
      literary/philological sources (LP, HD, BL, LL, ASLV, HRS, CITD, HA, ML).

  grammar   -- Abhyankar, *A Dictionary of Sanskrit Grammar* (Gaekwad's
      Oriental Series 134, Baroda 1961), full text on sa.wikisource
      (https://sa.wikisource.org/wiki/A_Dictionary_of_Sanskrit_Grammar, 435
      proofread pages).  The anchor is the dictionary's own "LIST OF WORKS AND
      AUTHORS CONSULTED" (pp. xiv-xv), transcribed verbatim below; it is the
      grammatical bibliography against which PD's coverage is measured.

Usage:
    python scripts/pd_genre_census.py            # (re)write both TSVs
    python scripts/pd_genre_census.py --check    # exit 1 if either committed TSV drifts
    python scripts/pd_genre_census.py --audit    # top sigla per genre (stdout)
    python scripts/pd_genre_census.py --json     # machine-readable table + verdicts
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data" / "pd"

GENRES = [
    "vedic",
    "epic",
    "purana",
    "kavya",
    "grammar",
    "epigraphy",
    "lexicography",
    "medieval",
    "other",
]

# --------------------------------------------------------------------------
# H6946 -- printed subject classes 1-62.
# Transcribed from the v2 OCR of PD/SWC.md, "Subject-wise Classification and
# Approximate Chronology of the Works" (pp. LXXIII-LXXXI), with OCR spellings
# normalised to the printed forms (Linganugasanas -> Linganusasanas,
# Samgita -> Sangita, Nibandha -> Nibandhas).  Sub-codes 4.1/4.2, 27.1-27.9,
# 39.1-39.3 and 54.1-54.5 are divisions of their parent code and are not
# counted as separate classes.
# --------------------------------------------------------------------------
SUBJECT_CLASSES: list[tuple[int, str]] = [
    (1, "Samhitas"),
    (2, "Brahmanas"),
    (3, "Aranyakas"),
    (4, "Upanisads"),
    (5, "Mantrapatha, Anukramanis etc."),
    (6, "Srautasutras"),
    (7, "Sulbasutras"),
    (8, "Pitrmedhasutras"),
    (9, "Grhyasutras"),
    (10, "Nirukta"),
    (11, "Pratigakhyas"),
    (12, "Epics"),
    (13, "Commentaries on the Mahabharata"),
    (14, "Buddhism"),
    (15, "Jainism: Dogmatics"),
    (16, "Jainism: Narrations"),
    (17, "Puranas"),
    (18, "Tantras"),
    (19, "Grammar: Paninian"),
    (20, "Grammar: Non-Paninian"),
    (21, "Linganusasanas"),
    (22, "Siksas"),
    (23, "Lexicons"),
    (24, "Commentaries on the Amarakosa"),
    (25, "Philosophy: General"),
    (26, "Mimamsa"),
    (27, "Vedanta"),
    (28, "Bhakti"),
    (29, "Trika"),
    (30, "Samkhya"),
    (31, "Yoga"),
    (32, "Nyaya"),
    (33, "Vaisesika"),
    (34, "Nyayavaisesika"),
    (35, "Dharmasutras"),
    (36, "Dharma"),
    (37, "Nibandhas"),
    (38, "Arthasastra"),
    (39, "Minor sciences"),
    (40, "Sangita"),
    (41, "Silpa"),
    (42, "Medicine"),
    (43, "Kama"),
    (44, "Mathematics"),
    (45, "Astronomy"),
    (46, "Astrology"),
    (47, "Alchemy"),
    (48, "Poetics"),
    (49, "Dramaturgy"),
    (50, "Nrtya"),
    (51, "Prosody"),
    (52, "Kavyas"),
    (53, "Historical Poems"),
    (54, "Minor Poems"),
    (55, "Anthology"),
    (56, "Brhatkatha and connected Works"),
    (57, "Stories and Romances"),
    (58, "Campu"),
    (59, "Drama"),
    (60, "Farces"),
    (61, "Allegorical plays"),
    (62, "Inscriptions"),
]

# One-to-many genre -> printed class map.  "other" is left without codes: it is
# the unmapped bucket and keeps its own share in the crosswalk TSV.
GENRE_SUBJECT_CODES: dict[str, list[int]] = {
    "vedic": list(range(1, 12)) + [22],
    "epic": [12, 13],
    "purana": [17],
    "kavya": [16] + list(range(48, 62)),
    "grammar": [19, 20, 21],
    "epigraphy": [62],
    "lexicography": [23, 24],
    "medieval": [14, 15, 18] + list(range(25, 48)),
    "other": [],
}

UNMAPPED_LABEL = "unmapped"

GENRE_SUBJECT_NOTES = {
    "vedic": (
        "Includes class 22 Siksas: H6930 treats pratisakhya/siksa/nirukta as "
        "Vedic auxiliary texts, not as grammar."
    ),
    "epic": "Epics and their commentaries.",
    "purana": "Puranas.",
    "kavya": (
        "Includes classes 48-51 (Poetics, Dramaturgy, Nrtya, Prosody) because "
        "H6930's kavya classifier absorbs Kavyaprakasa, Natyasastra, Dasrupaka, "
        "etc.; class 16 Jainism Narrations falls here as narrative kavya."
    ),
    "grammar": (
        "Paninian and non-Paninian grammar plus Linganusasanas; class 24 "
        "Amarakosa commentaries sit under lexicography."
    ),
    "epigraphy": "Epigraphia Indica and the epigraphic corpora.",
    "lexicography": "Lexicons and their commentaries.",
    "medieval": (
        "Post-classical systematic and commentarial corpus: Buddhism, Jain "
        "dogmatics, Tantras, philosophy, dharma, artha, sciences, medicine, "
        "astronomy/astrology, alchemy."
    ),
    "other": (
        "Unmapped bucket: H6930 residual mass whose title/siglum evidence did "
        "not resolve to a genre; no printed subject class is assigned."
    ),
}

# --------------------------------------------------------------------------
# Anchor 1 -- IEG (Sircar 1966), Cologne digitisation.
# Head of the <ls> frequency table (source abbreviations cited inside IEG
# entries), extracted 17-10-2026 from csl-orig/v02/ieg/ieg.txt.
# --------------------------------------------------------------------------
IEG_SOURCES = {
    "EI": 3140, "IE": 1572, "SITI": 1049, "CII": 1048, "Ep. Ind.": 587,
    "IA": 570, "LP": 501, "SII": 409, "HD": 314, "BL": 310, "LL": 267,
    "ASLV": 198, "HRS": 157, "CITD": 155, "HA": 90, "Chamba": 84,
    "Arthasastra": 83, "Ind. Ant.": 75, "Ind. Ep.": 67, "ML": 64, "JNSI": 60,
    "Select Inscriptions": 58, "Rajatarangini": 55, "H. Rev. Syst.": 48,
    "PJS": 31, "Hist. Dharm.": 26, "Ant. Ch. St.": 22, "A. R. Ep.": 18,
    "Yajnavalkyasmrti": 15, "Sel. Ins.": 15,
}

IEG_EPIGRAPHIC_CORPORA = {
    "EI": "Epigraphia Indica",
    "Ep. Ind.": "Epigraphia Indica",
    "IE": "Indian Epigraphy",
    "CII": "Corpus Inscriptionum Indicarum",
    "SII": "South Indian Inscriptions",
    "SITI": "South Indian Temple Inscriptions",
    "IA": "Indian Antiquary",
    "Ind. Ant.": "Indian Antiquary",
    "Ind. Ep.": "Indian Epigraphy",
    "A. R. Ep.": "Annual Report on Epigraphy",
    "Select Inscriptions": "Select Inscriptions",
    "Sel. Ins.": "Select Inscriptions",
    "JNSI": "Journal of the Numismatic Society of India",
}

# --------------------------------------------------------------------------
# Anchor 2 -- Abhyankar (1961), "LIST OF WORKS AND AUTHORS CONSULTED",
# pp. xiv-xv, transcribed verbatim from the wikisource proofread pages of the
# 435-page scan.  Kept in the anchor's own order and spelling so the
# transcription can be diffed against the source.
# --------------------------------------------------------------------------
ABHYANKAR_WORKS = [
    ("A. Pr.", "Atharvaveda Pratisakhya"),
    ("Astadhyayi", "Panini's Astadhyayi"),
    ("Bh. Vr.", "Bhasavrtti of Purusottamadeva"),
    ("Bhar. Siksa", "Bharadvaja Siksa"),
    ("C. Vy., Can. Vy.", "Candra vyakarana"),
    ("Dhatuvrtti", "Madhaviya Dhatuvrtti"),
    ("Durgacarya", "Durgacarya's commentary on the Nirukta"),
    ("Durgasimha", "Durgasimha's Katantra-Sutravrtti"),
    ("Durgh. Vr.", "Durghatavrtti of Saranadeva"),
    ("Hem.", "Hemacandra's Sabdanusasana"),
    ("Hem. Pari.", "Hemacandra's Paribhasapatha"),
    ("Jain., Jain. Vy.", "Jainendra Vyakarana of Pujyapada Devanandin"),
    ("Jain. Pari.", "Jainendra Paribhasavrtti"),
    ("Kaiy., Kaiyata", "Kaiyata's Mahabhasya-pradipa"),
    ("Kalapa", "Kalapa-vyakarana-sutra"),
    ("Kas.", "Kasika of Jayaditya and Vamana"),
    ("Kas. viv.", "Kasikavivaranapanjika (Nyasa)"),
    ("Kat.", "Katantra vyakarana Sutra"),
    ("Kat. Pari. Durg.", "Katantra Paribhasavrtti of Durgasimha"),
    ("Kav. Prak.", "Kavyaprakasa of Mammata"),
    ("Laghumañjusa", "Laghumañjusa of Nagesa"),
    ("M. Bh.", "Mahabhasya of Patanjali"),
    ("Mahabhasyadipika", "Commentary on the Mahabhasya by Bhartrhari"),
    ("Muktavali", "Nyayamuktavali of Visvanathapancanana"),
    ("Nandikesvara", "Nandikesvarakarika"),
    ("Nir.", "Nirukta of Yaska"),
    ("Nyasa", "Kasikavivaranapanjika of Jinendrabuddhi"),
    ("P., Pan", "Panini's Astadhyayi"),
    ("Padamañjari", "Padamañjari, commentary on the Kasikavrtti by Haradatta"),
    ("Pan. Sik.", "Siksa of Panini"),
    ("Par. Bhas.", "Paribhasabhaskara of Haribhaskara Agnihotri"),
    ("Par. Sek.", "Paribhasendusekhara of Nagesa"),
    ("Paramalaghumañjusa", "Paramalaghumañjusa of Nagesabhatta"),
    ("Pari. Sang.", "Paribhasasamgraha by K. V. Abhyankar"),
    ("Phit. Sutra", "Santanu's Phitsutra"),
    ("Pradipa", "Kaiyata's Mahabhasyapradipa"),
    ("Purusottam", "Purusottamadeva's Paribhasavrtti"),
    ("R. Pr.", "Rgvedapratisakhya by Saunaka"),
    ("R. T.", "Rktantra Pratisakhya"),
    ("R. V.", "Rgveda-samhita"),
    ("Sabdakaustubha", "Sabdakaustubha of Bhattoji Diksita"),
    ("Sak.", "Sakatayana's Sabdanusasana"),
    ("Sak. Pari", "Sakatayana Paribhasapatha"),
    ("S. K. Sid.Kau.", "Siddhantakaumudi"),
    ("Siradeva", "Siradeva's Paribhasavrtti"),
    ("Siva Sutra", "Mahesvarasutras"),
    ("Sring-Prak.", "Sringaraprakasa of Bhoja"),
    ("T. Pr.", "Taittiriya Pratisakhya"),
    ("Tait. Samh.", "Taittiriya Samhita"),
    ("Tattvabodh.", "Tattvabodhini by Jinendrasarasvati"),
    ("Tattvacintamani", "Tattvacintamani of Gangesopadhyaya"),
    ("Tribhasyaratna", "Commentary on the Taittiriya Pratisakhya"),
    ("Uddyota", "Mahabhasya-pradipoddyota of Nagesa"),
    ("Un. Sutra", "Unadisutrapancapadi"),
    ("Un. Sutravr.", "Unadisutravrtti by Ujjvaladatta"),
    ("Upamanyu", "Nandikesvarakarikabhasya by Upamanyu"),
    ("Uvvata", "Uvvata's Bhasya on the Pratisakhya works"),
    ("V. Pr.", "Vajasaneyi Pratisakhya"),
    ("Vaidikabharana", "Commentary on the Taittiriya Pratisakhya"),
    ("Vaiyakaranabhusana", "Kondabhatta's Vaiyakaranabhusanasara"),
    ("Vak. Pad.", "Vakyapadiya of Bhartrhari"),
    ("Vak. Pad. tika", "Commentary on Bhartrhari's Vakyapadiya"),
    ("V., Vart.", "Varttikas on the sutras of Panini"),
    ("Vyadi", "Vyadiparibhasasucana"),
]

# Abhyankar works that are Vedic auxiliary texts (pratisakhya, siksa, nirukta,
# Rgveda-samhita).  Counted as vedic here -- the conservative choice for the
# grammar verdict -- and reported as a boundary note.
ABHYANKAR_VEDIC = {
    "A. Pr.", "Bhar. Siksa", "Nir.", "Pan. Sik.", "R. Pr.", "R. T.", "R. V.",
    "T. Pr.", "Tait. Samh.", "V. Pr.", "Uvvata", "Tribhasyaratna",
    "Vaidikabharana",
}


# Crosswalk: anchor entries whose titles never appear verbatim in the PD canon.
# Maps the anchor's own abbreviation/title to the PD sigla that evidence the
# same work.  Used only for anchor-coverage accounting, never for genre calls.
ANCHOR_PD_SIGLA = {
    "P., Pan": ("p",),
    "Astadhyayi": ("p",),
    "M. Bh.": ("mahabh",),
    "Kas.": ("kasi", "kasivr"),
    "Kas. viv.": ("nyas",),
    "Nyasa": ("nyas",),
    "S. K. Sid.Kau.": ("siddhakau",),
    "Pradipa": ("pradi",),
    "Kaiy., Kaiyata": ("pradi",),
    "Kat.": ("katan", "katanvr"),
    "C. Vy., Can. Vy.": ("candravr",),
    "Jain., Jain. Vy.": ("jainevya",),
    "Vak. Pad.": ("vakyapa", "vakyap"),
    "Un. Sutra": ("una",),
    "Dhatuvrtti": ("dhatuvr",),
    "Sabdakaustubha": ("sabdakaustubha",),
    "Par. Sek.": ("paribhasa",),
    "Hem.": ("siddhahe",),
    "Sak.": ("sakatavya",),
    "Nir.": ("nir",),
    "R. V.": ("rv",),
    "Padamañjari": ("padman",),
    "Sring-Prak.": ("srngapra",),
    "Un. Sutravr.": ("una",),
    "Per. Bhas.": ("paribhasa",),
    "Par. Bhas.": ("paribhasa",),
    "Mahabhasyadipika": ("pradi",),
    "Epigraphia Indica": ("ei",),
    "Indian Antiquary": ("ia",),
}

# --------------------------------------------------------------------------
# Normalisation
# --------------------------------------------------------------------------
_NONALNUM = re.compile(r"[^a-z0-9]+")


def flat(text: str) -> str:
    """Fold diacritics, lowercase, keep ASCII letters/digits only."""
    if not text:
        return ""
    s = unicodedata.normalize("NFD", str(text))
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return _NONALNUM.sub("", s.lower())


def bigrams(s: str) -> set[str]:
    return {s[i : i + 2] for i in range(len(s) - 1)}


# --------------------------------------------------------------------------
# Channel 1 -- hand-resolved high-mass sigla.
# Keyed on the bare siglum string (trailing period stripped, diacritics
# folded).  Each entry was read off its AOB title and its primary mass at
# census time is in pd_siglum_families.tsv, so the concentration is auditable.
# --------------------------------------------------------------------------
SIGLUM_GENRE = {
    # epigraphy
    "EI": "epigraphy",
    # grammar
    "MahāBh": "grammar", "KāśiVṛ": "grammar", "Kāśi": "grammar",
    "Prasā": "grammar", "Pradī": "grammar", "ŚabdaRa": "grammar",
    "SiddhāKau": "grammar", "Nyās": "grammar", "PrakriKau": "grammar",
    "CāndraVṛ": "grammar", "KātanVṛ": "grammar", "Kātan": "grammar",
    "DhātuPra": "grammar", "LaŚabdeŚe": "grammar", "Uṇā": "grammar",
    "VaiyāBhū": "grammar", "Paribhāṣā": "grammar", "MugdhaBo": "grammar",
    "JaineVyā": "grammar", "Śabdakaustubha": "grammar", "Vār": "grammar",
    "VākyaPa": "grammar", "VākyaP": "grammar", "Pradīp": "grammar",
    "P": "grammar",  # Panini's sutras, restored in the genre-safe column
    # lexicography
    "AmaK": "lexicography", "AbhidhāCin": "lexicography",
    "MediK": "lexicography", "NānārthāSaṃ": "lexicography",
    "AnekāSaṃ": "lexicography", "Vaija": "lexicography",
    "ŚabdaRaSaK": "lexicography", "ViśvaLoK": "lexicography",
    "TrikāŚe": "lexicography", "AbhidhāRaMā": "lexicography",
    "NānārthSaṃ": "lexicography", "AnekāK": "lexicography",
    "NighŚe": "lexicography",
    # vedic
    "ṚV": "vedic", "AV": "vedic", "SV": "vedic", "TaiS": "vedic",
    "KāṭhS": "vedic", "MaiS": "vedic", "VājaS": "vedic", "ŚatBr": "vedic",
    "TaiBr": "vedic", "AitBr": "vedic", "JaimiBr": "vedic", "PañcBr": "vedic",
    "KauṣīBr": "vedic", "GopBr": "vedic", "TaiĀ": "vedic", "AitĀ": "vedic",
    "ChāndoU": "vedic", "BṛĀraU": "vedic", "TaiU": "vedic", "ĀpaŚS": "vedic",
    "BaudhŚS": "vedic", "ĀśvaŚS": "vedic", "KātyŚS": "vedic",
    "MānŚS": "vedic", "HirŚS": "vedic", "BhārŚS": "vedic",
    "VaikhāŚS": "vedic", "ĀpaGS": "vedic", "ĀśvaGS": "vedic",
    "GobhiGS": "vedic", "HirGS": "vedic", "KauṣīGS": "vedic",
    "MānGS": "vedic", "PāraGS": "vedic", "ŚāṅkhāGS": "vedic",
    "BaudhGS": "vedic", "TaiPrāti": "vedic", "ṚPrāti": "vedic",
    "VājaPrāti": "vedic", "CaturA": "vedic", "Nir": "vedic",
    "BṛDe": "vedic", "ŚikṣāSa": "vedic", "PāṇiŚi": "vedic",
    "MāṇḍūŚi": "vedic", "KātyŚi": "vedic", "BhārŚi": "vedic",
    # epic
    "MahāBhā": "epic", "Rāmā": "epic", "HariVaṃ": "epic",
    "AdhyāRā": "epic", "RāmāCam": "epic",
    # purana
    "PadmP": "purana", "SkandP": "purana", "BhāgP": "purana",
    "BrahmāṇḍP": "purana", "BhaviP": "purana", "BrahmP": "purana",
    "ViṣṇuP": "purana", "ŚivaP": "purana", "LiṅgaP": "purana",
    "MatsyaP": "purana", "VāyuP": "purana", "KūrmaP": "purana",
    "AgniP": "purana", "MārkP": "purana", "VarāP": "purana",
    "VāmaP": "purana", "DevīBhāP": "purana", "BrahmVaiP": "purana",
    "GaṇeP": "purana", "SaurP": "purana", "ĀdiP": "purana",
    "MahāP": "purana", "BṛDharmaP": "purana", "BṛNāraP": "purana",
    "KalkiP": "purana", "NaraP": "purana", "PadmPrā": "purana",
    # kavya
    "KathāSaSāg": "kavya", "HarVi": "kavya", "PāṇḍaC": "kavya",
    "RaghuVa": "kavya", "KumāSaṃ": "kavya", "MeghDū": "kavya",
    "ŚiśuVa": "kavya", "Kirātā": "kavya", "NaiṣC": "kavya",
    "Bhaṭṭi": "kavya", "DvyāśraKā": "kavya", "HarṣaC": "kavya",
    "Kād": "kavya", "DaśKuC": "kavya", "AvantiKa": "kavya",
    "UdaySuKa": "kavya", "PañcT": "kavya", "Hitopa": "kavya",
    "VetāPañ": "kavya", "GītGo": "kavya", "NalaCam": "kavya",
    "RāmC": "kavya", "YaśasCam": "kavya", "SāhiDa": "kavya",
    "KāvyPra": "kavya", "Dhvanyā": "kavya", "NāṭyaŚā": "kavya",
    "DaśRū": "kavya", "AbhinBhā": "kavya", "ŚṛṅgāPra": "kavya",
    # medieval (post-classical systematic / commentarial)
    "BrahmSūBh": "medieval", "ŚivārkaMaDī": "medieval", "Bhām": "medieval",
    "TātpaṬ": "medieval", "BṛĀraUBhVā": "medieval", "BṛĀraUBh": "medieval",
    "ManuBh": "medieval", "ManuSm": "medieval", "YājñaSm": "medieval",
    "ViṣṇuSm": "medieval", "NāraSm": "medieval", "BṛhaspaSm": "medieval",
    "KātySm": "medieval", "ParāSm": "medieval", "GautDS": "medieval",
    "BaudhDS": "medieval", "ĀpaDS": "medieval", "VasiDS": "medieval",
    "VasiSm": "medieval", "NyāySu": "medieval", "NyāyMañ": "medieval",
    "NyāyVār": "medieval", "NyāyKa": "medieval", "NyāyKuA": "medieval",
    "NyāySū": "medieval", "NyāyBh": "medieval", "TattvCin": "medieval",
    "TantrVā": "medieval", "ŚlokaVār": "medieval", "ŚābaBh": "medieval",
    "MīmāKau": "medieval", "BhāṭṭDī": "medieval", "BhāṭṭCin": "medieval",
    "MīmāSū": "medieval", "AdvaiSi": "medieval", "LaCandr": "medieval",
    "GuruCandr": "medieval", "VedāntKa": "medieval", "VedāntKau": "medieval",
    "VedāntDī": "medieval", "VedāntPari": "medieval", "VedāntSā": "medieval",
    "VedāSaṃ": "medieval", "SarvaDaSaṃ": "medieval",
    "SarvaDaKau": "medieval", "SarvaSiSaṃ": "medieval", "TarkSaṃ": "medieval",
    "TarkBhā": "medieval", "TarkKau": "medieval", "TattvPrakā": "medieval",
    "TattvPradī": "medieval", "TattvSaṃ": "medieval", "TattvVai": "medieval",
    "TattvMu": "medieval", "TattvBi": "medieval", "SāṃkhyaTaKau": "medieval",
    "SāṃkhyaKāBh": "medieval", "YogBh": "medieval", "YogVā": "medieval",
    "YogSū": "medieval", "CaraS": "medieval", "SuśruS": "medieval",
    "AṣṭāSaṃ": "medieval", "AṣṭāHṛ": "medieval", "BhāvPra": "medieval",
    "SūrySi": "medieval", "BrāhmSphuSi": "medieval", "Līlā": "medieval",
    "BījGa": "medieval", "RasGaṅ": "medieval", "RasRaSa": "medieval",
    "SmṛtiCan": "medieval", "CaturCin": "medieval", "KośaKaTa": "medieval",
    "VīraMi": "medieval", "Aparā": "medieval", "BālamBha": "medieval",
    "Mitā": "medieval", "Subodhi": "medieval", "ManvaVi": "medieval",
    "ManvaMu": "medieval", "GītāBh": "medieval", "ArthŚā": "medieval",
    "KāmSū": "medieval", "AbhidhK": "medieval", "AbhidhāRa": "medieval",
    "AbhinDa": "medieval", "MṛgendraT": "medieval", "LakṣmīT": "medieval",
    "KulārT": "medieval", "ŚāraTi": "medieval", "TantrSā": "medieval",
    "TantrRā": "medieval", "TantrRa": "medieval", "NityāṢoḍa": "medieval",
    "SetuBa": "medieval", "Mānaso": "medieval", "RājTa": "medieval",
    "RājMār": "medieval", "NītiSā": "medieval", "NītiVā": "medieval",
    "ŚukraNī": "medieval",

    # --- added in the audit pass: named works the lexicon does not reach ---
    "ŚrutaPra": "medieval", "TilaMañ": "kavya", "TriṣaŚaPuC": "kavya",
    "ĪśānŚiPa": "medieval", "ŚatDū": "medieval", "Yādavā": "kavya",
    "Hastyāyur": "medieval", "RāghPāṇ": "kavya", "Rāgh": "kavya",
    "PadMañ": "grammar", "TattvSaṃ": "medieval", "Kiraṇā": "medieval",
    "ŚrīKaC": "kavya", "KhaṇḍanKhā": "medieval", "PārśvC": "kavya",
    "SyādvāMañ": "medieval", "ŚākaṭāVyā": "grammar", "KalpaK": "medieval",
    "Kuval": "kavya", "VakroJī": "kavya", "NāmaMāli": "lexicography",
    "SvapnVā": "kavya", "PratāYaBhū": "kavya", "CaitaCa": "kavya",
    "PraboCan": "kavya", "ĀnandRa": "kavya", "NaiṣkaSi": "medieval",
    "JīvanVi": "medieval", "MalliC": "kavya", "Nalābhyu": "kavya",
    "BhāmiVi": "kavya", "RasTa": "medieval", "Rasā": "medieval",

    "SaraKaṇṭhā": "kavya", "Subhāṣi": "kavya", "SaduktiKa": "kavya",
    "ŚaṅkaDigVi": "kavya", "YātrāPra": "kavya", "ViśvaPra": "lexicography",
    "SamarāSaṃ": "kavya", "NīlaVi": "kavya", "ParamāKā": "kavya",
    "ŚivLī": "kavya", "VyaktiVi": "kavya", "NavaSāC": "kavya",
    "PrabhāC": "kavya", "VarāṅgaC": "kavya", "KīcaVa": "kavya",
    "BhallāC": "kavya", "Mṛcch": "kavya", "DaśāvaC": "kavya",
    "NemiC": "kavya", "NemiNir": "kavya", "KumāDeC": "kavya",
    "KumāCaSaṃ": "kavya", "VidaMā": "kavya", "VidaMuMa": "kavya",
    "KandaCū": "kavya", "Ratnā": "kavya", "RatnaCūKa": "kavya",
    "CampaŚreKa": "kavya", "UttaKuC": "kavya", "CitraPaC": "kavya",
    "JānaPa": "kavya", "JānaHa": "kavya", "PārthPa": "kavya",
    "PārvPa": "kavya", "UnmaRā": "kavya", "Mālavikā": "kavya",
    "MudrāRā": "kavya", "HammīMaKā": "kavya", "PṛthvīVi": "kavya",
    "MadhuVi": "kavya", "SāhiSā": "kavya", "Mukundā": "kavya",
    "AuciViCa": "kavya", "KalāVi": "kavya", "DarpDa": "kavya",
    "NarmaMā": "kavya", "Hāsyārṇa": "kavya", "SūktiRa": "kavya",
    "SūktiMu": "kavya", "SubhāRaK": "kavya", "PadyāTa": "kavya",
    "KaviKaṇṭhā": "kavya", "SūryaŚ": "kavya", "BhallaŚ": "kavya",
    "BālaKrī": "medieval", "JayaMa": "medieval", "Upask": "medieval",
    "BṛSaṃ": "medieval", "SiddhāTaVi": "medieval", "KalyāKā": "medieval",
    "NyāyRaMā": "medieval", "NayaVi": "medieval", "SaṃkṣeŚā": "medieval",
    "VidhiRa": "medieval", "Śaṅ": "medieval", "SiddhYo": "medieval",
    "DaṇḍaVi": "medieval", "TārkiRa": "medieval", "RugVi": "medieval",
    "ṬupṬ": "medieval", "ŚaktiVā": "medieval", "SaṃgīRa": "medieval",
    "SiddhaHe": "grammar", "CāndraVyā": "grammar", "GaṇRa": "grammar",
    "VyutpaVā": "grammar", "Sāy": "vedic", "AVPari": "vedic",

    "DharK": "lexicography", "HetuBiṬ": "medieval", "ŚaṅkaVi": "kavya",
    "Ekāva": "kavya", "Nārāy": "kavya", "SthānṬ": "medieval",
    "DīpKa": "kavya", "SiddhāLeSaṃ": "medieval", "RāmāMañ": "medieval",
    "BṛKathāK": "kavya",
}

# --------------------------------------------------------------------------
# Channel 2 -- canonical-work lexicon for the Dice matcher.
# (genre, canonical name).  Names are folded ASCII; PD's mangled AOB title is
# compared by bigram Dice.  Covers the classical canon plus the anchors' works
# that PD is expected to cite.
# --------------------------------------------------------------------------
FUZZY_WORKS: list[tuple[str, str]] = [
    ("epigraphy", "epigraphia indica"),
    ("epigraphy", "corpus inscriptionum indicarum"),
    ("epigraphy", "south indian inscriptions"),
    ("epigraphy", "indian antiquary"),
    ("epigraphy", "indian epigraphy"),
    ("epigraphy", "select inscriptions"),
    ("grammar", "mahabhasya"),
    ("grammar", "vyakaranamahabhasya"),
    ("grammar", "kasikavrtti"),
    ("grammar", "kasika"),
    ("grammar", "kasikavivaranapanjika"),
    ("grammar", "nyasa"),
    ("grammar", "padamanjari"),
    ("grammar", "siddhantakaumudi"),
    ("grammar", "laghusiddhantakaumudi"),
    ("grammar", "madhyasiddhantakaumudi"),
    ("grammar", "praudhamanorama"),
    ("grammar", "sabdendusekhara"),
    ("grammar", "laghusabdendusekhara"),
    ("grammar", "paramalaghumanjusa"),
    ("grammar", "laghumanjusa"),
    ("grammar", "prakriyakaumudi"),
    ("grammar", "prakriyasarvasva"),
    ("grammar", "prasada"),
    ("grammar", "paribhasendusekhara"),
    ("grammar", "paribhasabhaskara"),
    ("grammar", "paribhasavrtti"),
    ("grammar", "sabdakaustubha"),
    ("grammar", "linganusasana"),
    ("grammar", "astadhyayi"),
    ("grammar", "katantra"),
    ("grammar", "katantravrtti"),
    ("grammar", "kalapa"),
    ("grammar", "candra vyakarana"),
    ("grammar", "jainendra vyakarana"),
    ("grammar", "sabdanusasana"),
    ("grammar", "sakatayana"),
    ("grammar", "vakyapadiya"),
    ("grammar", "mahabhasyapradipa"),
    ("grammar", "pradipa"),
    ("grammar", "uddyota"),
    ("grammar", "sabdaratnakara"),
    ("grammar", "dhatupatha"),
    ("grammar", "dhatuvrtti"),
    ("grammar", "dhatupradipa"),
    ("grammar", "dhatukavya"),
    ("grammar", "unadisutra"),
    ("grammar", "unadivrtti"),
    ("grammar", "mugdhabodha"),
    ("grammar", "vaiyakaranabhusana"),
    ("grammar", "vyutpattivada"),
    ("grammar", "sabdabhedaprakasa"),
    ("grammar", "sarasvata vyakarana"),
    ("grammar", "haimalinganusasana"),
    ("lexicography", "amarakosa"),
    ("lexicography", "namalinganusasana"),
    ("lexicography", "abhidhanacintamani"),
    ("lexicography", "abhidhanaratnamala"),
    ("lexicography", "abhidhanamanjari"),
    ("lexicography", "medinikosa"),
    ("lexicography", "trikandasesa"),
    ("lexicography", "visvalocanakosa"),
    ("lexicography", "visvaprakasa"),
    ("lexicography", "nighantusesa"),
    ("lexicography", "nanartharnavasamksepa"),
    ("lexicography", "anekarthasamuccaya"),
    ("lexicography", "ekaksaranamamala"),
    ("lexicography", "sabdaratnasamanvayakosa"),
    ("lexicography", "vaijayanti"),
    ("lexicography", "mahavyutpatti"),
    ("lexicography", "dhanvantarinighantu"),
    ("lexicography", "rajanighantu"),
    ("lexicography", "bhavaprakanighantu"),
    ("lexicography", "madanapalanighantu"),
    ("lexicography", "agastyanighantu"),
    ("lexicography", "sabdakosa"),
    ("lexicography", "namamalika"),
    ("vedic", "rgveda samhita"),
    ("vedic", "samaveda samhita"),
    ("vedic", "yajurveda samhita"),
    ("vedic", "atharvaveda samhita"),
    ("vedic", "taittiriya samhita"),
    ("vedic", "kathaka samhita"),
    ("vedic", "maitrayani samhita"),
    ("vedic", "vajasaneyi samhita"),
    ("vedic", "satapatha brahmana"),
    ("vedic", "taittiriya brahmana"),
    ("vedic", "aitareya brahmana"),
    ("vedic", "jaiminiya brahmana"),
    ("vedic", "pancavimsa brahmana"),
    ("vedic", "kausitaki brahmana"),
    ("vedic", "gopatha brahmana"),
    ("vedic", "sadvimsa brahmana"),
    ("vedic", "samavidhana brahmana"),
    ("vedic", "mantra brahmana"),
    ("vedic", "taittiriya aranyaka"),
    ("vedic", "aitareya aranyaka"),
    ("vedic", "sankhayana aranyaka"),
    ("vedic", "chandogya upanisad"),
    ("vedic", "brhadaranyaka upanisad"),
    ("vedic", "taittiriya upanisad"),
    ("vedic", "maitrayani upanisad"),
    ("vedic", "svetasvatara upanisad"),
    ("vedic", "mundaka upanisad"),
    ("vedic", "kena upanisad"),
    ("vedic", "katha upanisad"),
    ("vedic", "prasna upanisad"),
    ("vedic", "isa upanisad"),
    ("vedic", "aitareya upanisad"),
    ("vedic", "kausitaki upanisad"),
    ("vedic", "apastamba srautasutra"),
    ("vedic", "baudhayana srautasutra"),
    ("vedic", "manava srautasutra"),
    ("vedic", "asvalayana srautasutra"),
    ("vedic", "katyayana srautasutra"),
    ("vedic", "latyayana srautasutra"),
    ("vedic", "vaikhanasa srautasutra"),
    ("vedic", "hiranyakesi srautasutra"),
    ("vedic", "bharadvaja srautasutra"),
    ("vedic", "drahyayana srautasutra"),
    ("vedic", "varaha srautasutra"),
    ("vedic", "sankhayana srautasutra"),
    ("vedic", "jaiminiya srautasutra"),
    ("vedic", "rgveda pratisakhya"),
    ("vedic", "taittiriya pratisakhya"),
    ("vedic", "vajasaneyi pratisakhya"),
    ("vedic", "caturadhyayika"),
    ("vedic", "rktantra pratisakhya"),
    ("vedic", "siksa samuccaya"),
    ("vedic", "paniniya siksa"),
    ("vedic", "bharadvaja siksa"),
    ("vedic", "manduki siksa"),
    ("vedic", "katyayani siksa"),
    ("vedic", "nirukta"),
    ("vedic", "brhaddevata"),
    ("vedic", "sarvanukramani"),
    ("vedic", "vedarthasamgraha"),
    ("epic", "mahabharata"),
    ("epic", "ramayana"),
    ("epic", "harivamsa"),
    ("epic", "adhyatmaramayana"),
    ("epic", "ramacampu"),
    ("epic", "balaramayana"),
    ("purana", "padmapurana"),
    ("purana", "skandapurana"),
    ("purana", "bhagavatapurana"),
    ("purana", "brahmandapurana"),
    ("purana", "bhavisyapurana"),
    ("purana", "brahmapurana"),
    ("purana", "visnupurana"),
    ("purana", "sivapurana"),
    ("purana", "lingapurana"),
    ("purana", "matsyapurana"),
    ("purana", "vayupurana"),
    ("purana", "kurmapurana"),
    ("purana", "agnipurana"),
    ("purana", "markandeyapurana"),
    ("purana", "varahapurana"),
    ("purana", "vamanapurana"),
    ("purana", "naradiyapurana"),
    ("purana", "devibhagavata"),
    ("purana", "ganesapurana"),
    ("purana", "kalikapurana"),
    ("purana", "saurapurana"),
    ("purana", "garudapurana"),
    ("purana", "narasimhapurana"),
    ("purana", "kalkipurana"),
    ("purana", "adipurana"),
    ("purana", "mahapurana"),
    ("purana", "nilamata"),
    ("purana", "brhaddharmapurana"),
    ("purana", "brhannaradiyapurana"),
    ("kavya", "raghuvamsa"),
    ("kavya", "kumarasambhava"),
    ("kavya", "meghaduta"),
    ("kavya", "rtusamhara"),
    ("kavya", "malavikagnimitra"),
    ("kavya", "abhijnanasakuntala"),
    ("kavya", "vikramorvasiya"),
    ("kavya", "kiratarjuniya"),
    ("kavya", "sisupalavadha"),
    ("kavya", "naisadhiyacarita"),
    ("kavya", "bhattikavya"),
    ("kavya", "haravijaya"),
    ("kavya", "kathasaritsagara"),
    ("kavya", "pancatantra"),
    ("kavya", "hitopadesa"),
    ("kavya", "vetalapancavimsati"),
    ("kavya", "kadambari"),
    ("kavya", "harsacarita"),
    ("kavya", "dasakumaracarita"),
    ("kavya", "vasavadatta"),
    ("kavya", "kavyadarsa"),
    ("kavya", "kavyaprakasa"),
    ("kavya", "dhvanyaloka"),
    ("kavya", "alankarasarvasva"),
    ("kavya", "natyasastra"),
    ("kavya", "dasarupaka"),
    ("kavya", "sahityadarpana"),
    ("kavya", "gitagovinda"),
    ("kavya", "mrcchakatika"),
    ("kavya", "mudraraksasa"),
    ("kavya", "uttararamacarita"),
    ("kavya", "malatimadhava"),
    ("kavya", "subhasitaratnakosa"),
    ("kavya", "satakatraya"),
    ("kavya", "nalodaya"),
    ("kavya", "kamsavadha"),
    ("kavya", "samayamatrka"),
    ("kavya", "kuttanimata"),
    ("kavya", "sringaraprakasa"),
    ("kavya", "kavyalankara"),
    ("kavya", "kavyanusasana"),
    ("kavya", "saundarananda"),
    ("kavya", "buddhacarita"),
    ("kavya", "priyadarsika"),
    ("kavya", "ratnavali"),
    ("kavya", "nagananda"),
    ("kavya", "anargharaghava"),
    ("kavya", "prasannaraghava"),
    ("kavya", "janakiparinaya"),
    ("kavya", "pandavacarita"),
    ("kavya", "yasastilakacampu"),
    ("kavya", "vikramankadevacarita"),
    ("kavya", "prabandhacintamani"),
    ("kavya", "prabhavakacarita"),
    ("kavya", "mudritakumudacandra"),
    ("kavya", "saktiratnakara"),
    ("kavya", "sringaratilaka"),
    ("kavya", "kandarpacudamani"),
    ("kavya", "kapphinabhyudaya"),
    ("kavya", "haravilasa"),
    ("kavya", "venisamhara"),
    ("kavya", "balacarita"),
    ("kavya", "pratima"),
    ("kavya", "abhiseka"),
    ("kavya", "svapnavasavadatta"),
    ("kavya", "candakausika"),
    ("kavya", "mattavilasa"),
    ("kavya", "latakamelaka"),
    ("kavya", "bhagavadajjukiya"),
    ("kavya", "kamandaki"),
    ("kavya", "sukasaptati"),
    ("kavya", "kathakosa"),
    ("kavya", "brhatkathamanjari"),
    ("kavya", "brhatkathaslokasamgraha"),
    ("kavya", "brhatkathakosa"),
    ("medieval", "manusmrti"),
    ("medieval", "manubhasya"),
    ("medieval", "yajnavalkyasmrti"),
    ("medieval", "visnusmrti"),
    ("medieval", "naradasmrti"),
    ("medieval", "brhaspatismrti"),
    ("medieval", "katyayanasmrti"),
    ("medieval", "parasarasmrti"),
    ("medieval", "gautamadharmasutra"),
    ("medieval", "baudhayanadharmasutra"),
    ("medieval", "apastambadharmasutra"),
    ("medieval", "vasisthadharmasutra"),
    ("medieval", "smrticandrika"),
    ("medieval", "caturvargacintamani"),
    ("medieval", "krtyakalpataru"),
    ("medieval", "kalpataru"),
    ("medieval", "viramitrodaya"),
    ("medieval", "mitaksara"),
    ("medieval", "balambhatta"),
    ("medieval", "apararka"),
    ("medieval", "nirnayasindhu"),
    ("medieval", "dharmasastra"),
    ("medieval", "nyayasutra"),
    ("medieval", "nyayabhasya"),
    ("medieval", "nyayamanjari"),
    ("medieval", "nyayavarttika"),
    ("medieval", "tattvacintamani"),
    ("medieval", "nyayakandali"),
    ("medieval", "nyayakusumanjali"),
    ("medieval", "nyayasiddhanta"),
    ("medieval", "brahmasutrabhasya"),
    ("medieval", "bhamati"),
    ("medieval", "vivarana"),
    ("medieval", "pancapadika"),
    ("medieval", "advaitasiddhi"),
    ("medieval", "vedantasara"),
    ("medieval", "vedantakalpataru"),
    ("medieval", "nyayamrta"),
    ("medieval", "tattvapradipika"),
    ("medieval", "sarvadarsanasamgraha"),
    ("medieval", "sarvadarsanakaumudi"),
    ("medieval", "tantravarttika"),
    ("medieval", "slokavarttika"),
    ("medieval", "sabarabhasya"),
    ("medieval", "mimamsasutra"),
    ("medieval", "mimamsakaustubha"),
    ("medieval", "bhattadipika"),
    ("medieval", "arthasamgraha"),
    ("medieval", "carakasamhita"),
    ("medieval", "susrutasamhita"),
    ("medieval", "astangahrdaya"),
    ("medieval", "astangasangraha"),
    ("medieval", "rasendracintamani"),
    ("medieval", "siddhantasironmani"),
    ("medieval", "brahmasphutasiddhanta"),
    ("medieval", "suryasiddhanta"),
    ("medieval", "aryabhatiya"),
    ("medieval", "lilavati"),
    ("medieval", "bijaganita"),
    ("medieval", "grahalaghava"),
    ("medieval", "karanakutuhala"),
    ("medieval", "mrgendratantra"),
    ("medieval", "malinivijayottaratantra"),
    ("medieval", "kulacudamani"),
    ("medieval", "tantraraja"),
    ("medieval", "tantraratna"),
    ("medieval", "sivasutra"),
    ("medieval", "sivadrsti"),
    ("medieval", "pratyabhijnahrdaya"),
    ("medieval", "isvarapratyabhijnavimarsini"),
    ("medieval", "sarvamatasamgraha"),
    ("medieval", "sarvasiddhantasangraha"),
    ("medieval", "brahmasiddhi"),
    ("medieval", "istasiddhi"),
    ("medieval", "khandanakhandakhadya"),
    ("medieval", "citsukhi"),
    ("medieval", "tattvabindu"),
    ("medieval", "tattvasangraha"),
    ("medieval", "nyayabindu"),
    ("medieval", "pramanavarttika"),
    ("medieval", "pramanasamuccaya"),
    ("medieval", "abhidharmakosa"),
    ("medieval", "abhidharmasamuccaya"),
    ("medieval", "mahavastu"),
    ("medieval", "lalitavistara"),
    ("medieval", "saddharmapundarikasutra"),
    ("medieval", "lankavatarasutra"),
    ("medieval", "bodhisattvabhumi"),
    ("medieval", "divyavadana"),
    ("medieval", "ganavyuha"),
    ("medieval", "yogavasistha"),
    ("medieval", "rasagangadhara"),
    ("medieval", "rasarnavasudhakara"),
    ("medieval", "rasaratnasamuccaya"),
    ("medieval", "rasatarangini"),
    ("medieval", "kamasutra"),
    ("medieval", "arthasastra"),
    ("medieval", "silparatna"),
    ("medieval", "manasollasa"),
    ("medieval", "rajatarangini"),
    ("medieval", "rajamartanda"),
    ("medieval", "nitivakyamrta"),
    ("medieval", "nitiprakasika"),
    ("medieval", "sukranitisara"),
    ("medieval", "hastyayurveda"),
    ("medieval", "upavanavinoda"),
    ("medieval", "sivatattvaratnakara"),
]

# --------------------------------------------------------------------------
# Channel 3 -- anchored stem rules for the long tail.
# Applied to the folded title; anchored or stem-prefixed to avoid the
# substring traps of a naive engine ("nyasa" inside "ahirbudhnyasamhita").
# --------------------------------------------------------------------------
RULES: list[tuple[str, re.Pattern, str]] = [
    ("epigraphy", re.compile(r"epigraph|corpusinscriptionum|southindianinscription|indianantiquar"), "epigraphy-stem"),
    ("grammar", re.compile(r"^(mahabhas|mahabhasy|vyakaranamahabhas)"), "grammar-stem"),
    ("grammar", re.compile(r"^(kasika|kasikavrtt|kasikavivaran)"), "grammar-stem"),
    ("grammar", re.compile(r"siddhantakaumud|sabdendusekhar|prakriyakaumud|paribhasendusekhar"), "grammar-stem"),
    ("grammar", re.compile(r"^(nyasa|padamanjari|vakyapadiya|sabdakaustubh|linganusasan)"), "grammar-stem"),
    ("grammar", re.compile(r"^(dhatupatha|dhatuvrtti|dhatupradip|dhatukavya|unadisutra)"), "grammar-stem"),
    ("grammar", re.compile(r"^(katantra|kalapa|candravyakarana|jainendra|sabdanusasan|sakatayana)"), "grammar-stem"),
    ("grammar", re.compile(r"^(mugdhabodha|vaiyakaranabhusan|vyutpattivada|sabdabhedaprakas)"), "grammar-stem"),
    ("lexicography", re.compile(r"kos|nighant|abhidhan|namalinganusasan|amarakos|namamala"), "lex-stem"),
    ("vedic", re.compile(r"^(rgveda|samaveda|yajurveda|atharvaveda|taittiriya|kathaka|maitrayani|vajasaneyi)"), "vedic-stem"),
    ("vedic", re.compile(r"(brahmana|aranyaka|srautasutra|grhyasutra|pratisakhya|siksa|nirukta|samhita)$"), "vedic-stem"),
    ("vedic", re.compile(r"upanisad|anukramani|brhaddevata"), "vedic-stem"),
    ("epic", re.compile(r"mahabharat|ramayan|harivams"), "epic-stem"),
    ("purana", re.compile(r"puran"), "purana-stem"),
    ("kavya", re.compile(r"^(raghuvamsa|kumarasambhava|meghaduta|kiratarjuniya|sisupalavadha|naisadhiya|bhattikavya|haravijaya)"), "kavya-stem"),
    ("kavya", re.compile(r"(kavyaprakas|dhvanyalok|alankara|dasarupaka|natyasastra|sahityadarpana)"), "kavya-stem"),
    ("kavya", re.compile(r"^(kathasaritsagar|pancatantra|hitopadesa|vetalapancavimsat|kadambari|harsacarita|dasakumaracarita)"), "kavya-stem"),
    ("kavya", re.compile(r"campu|carita|cintamani|prabandha"), "kavya-stem"),
    ("medieval", re.compile(r"smrti|smriti|dharmasastra|dharmasutra|nibandha"), "medieval-stem"),
    ("medieval", re.compile(r"nyaya|tarka|mimamsa|vedanta|brahmasutra|samkhya|yogasutra"), "medieval-stem"),
    ("medieval", re.compile(r"ayurveda|carakasamhita|susrutasamhita|astanga"), "medieval-stem"),
    ("medieval", re.compile(r"siddhanta|jyotisa|ganita"), "medieval-stem"),
    ("medieval", re.compile(r"tantra|agama|mantra"), "medieval-stem"),
    ("medieval", re.compile(r"bhasya|varttika|vrtti|dipika|vyakhya|vivarana|paddhati"), "medieval-stem"),
]

# Siglum-suffix heuristics, used only when the title channels abstain.
SIGLUM_SUFFIX = [
    (re.compile(r"^.{2,}p$"), "purana", "siglum -*P."),
    (re.compile(r"^.{2,}u$"), "vedic", "siglum -*U. (upanisad)"),
    (re.compile(r"^.{2,}s$"), "vedic", "siglum -*S. (samhita)"),
    (re.compile(r"^.{2,}br$"), "vedic", "siglum -*Br. (brahmana)"),
    (re.compile(r"^.{2,}ss$"), "vedic", "siglum -*SS. (srauta)"),
    (re.compile(r"^.{2,}gs$"), "vedic", "siglum -*GS. (grhya)"),
    (re.compile(r"^.{2,}ds$"), "medieval", "siglum -*DS. (dharmasutra)"),
    (re.compile(r"^.{2,}sm$"), "medieval", "siglum -*Sm. (smrti)"),
    (re.compile(r"^.{2,}bh$"), "medieval", "siglum -*Bh. (bhasya)"),
    (re.compile(r"^.{2,}ti$"), "medieval", "siglum -*Ti. (tika)"),
    (re.compile(r"^.{2,}kau$"), "medieval", "siglum -*Kau. (kaumudi)"),
]

# Ablation switches (sensitivity only; the committed TSV uses both channels on).
USE_SIGLUM_MAP = True
USE_DICE = True

DICE_MIN = 0.72
DICE_MARGIN = 0.02

_SIGLUM_INDEX = {flat(k): v for k, v in SIGLUM_GENRE.items()}
_FUZZY_BIGRAMS = [(g, flat(n), bigrams(flat(n))) for g, n in FUZZY_WORKS]
_BIGRAM_INDEX: dict[str, list[int]] = {}
for _i, (_g, _name, _bg) in enumerate(_FUZZY_BIGRAMS):
    for _b in _bg:
        _BIGRAM_INDEX.setdefault(_b, []).append(_i)


def fuzzy_genre(text: str) -> tuple[str, str, float]:
    """Best (genre, work name, dice) for one evidence string, or ('', '', 0)."""
    f = flat(text)
    if len(f) < 5:
        return "", "", 0.0
    bg = bigrams(f)
    votes: dict[int, int] = {}
    for b in bg:
        for i in _BIGRAM_INDEX.get(b, ()):
            votes[i] = votes.get(i, 0) + 1
    scored: list[tuple[float, str, str]] = []
    for i, shared in votes.items():
        if shared < 6:
            continue
        if len(_FUZZY_BIGRAMS[i][1]) < 7:
            continue
        genre, name, nbg = _FUZZY_BIGRAMS[i]
        scored.append((2.0 * shared / (len(bg) + len(nbg)), genre, name))
    if not scored:
        return "", "", 0.0
    # guard: a work name must be anchored by its first four letters appearing
    # in the title, otherwise short names win on spurious bigram overlap
    scored = [t for t in scored if t[2][:4] in f]
    if not scored:
        return "", "", 0.0
    scored.sort(reverse=True)
    best_score, best_genre, best_name = scored[0]
    if best_score < DICE_MIN:
        return "", "", best_score
    for score, genre, _name in scored[1:]:
        if genre != best_genre and best_score - score < DICE_MARGIN:
            return "", "", best_score
    return best_genre, best_name, best_score


def classify(text: str, siglum: str, strength: str = "strong") -> tuple[str, str]:
    """Return (genre, provenance) for one siglum or one declared work."""
    sg = flat(siglum)
    if USE_SIGLUM_MAP and sg in _SIGLUM_INDEX:
        return _SIGLUM_INDEX[sg], "siglum-map"
    if strength == "structural":
        return "other", "structural-locator"
    f = flat(text)
    for genre, rx, label in RULES:
        if rx.search(f):
            return genre, "rule:" + label
    if USE_DICE and strength != "weak":
        g, name, score = fuzzy_genre(text)
        if g:
            return g, f"dice:{name}@{score:.2f}"
    if strength != "structural":
        for rx, genre, label in SIGLUM_SUFFIX:
            if rx.search(sg):
                return genre, label
    return "other", "unresolved"


# --------------------------------------------------------------------------
# Loaders
# --------------------------------------------------------------------------
def read_tsv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def load_metrics() -> dict:
    return json.loads((DATA / "pd_dcs_metrics.json").read_text(encoding="utf-8"))


def declared_by_siglum(works: list[dict]) -> dict[str, str]:
    """folded siglum -> declared work fold (for sigla the AOB resolves)."""
    out: dict[str, str] = {}
    for w in works:
        for s in re.split(r"[\s,;]+", w.get("sigla", "")):
            s = s.strip()
            if s:
                out.setdefault(flat(s), w["work_fold"])
    return out


def evidence_for(row: dict, aob: dict[str, dict], decl: dict[str, str]) -> tuple[str, str]:
    """Best title evidence for one siglum + a strength label."""
    dcs = (row.get("dcs_title") or "").strip()
    if dcs:
        return dcs, "strong"
    a = aob.get(row["siglum"]) or {}
    aob_title = (a.get("title") or "").strip()
    if aob_title:
        return aob_title, "strong"
    disp = (row.get("display_title") or "").strip()
    if disp:
        return disp, "strong"
    fold = decl.get(flat(row["siglum"]))
    if fold:
        return fold, "strong"
    return row["siglum"], "weak"


# --------------------------------------------------------------------------
# Census
# --------------------------------------------------------------------------
# The two works restored into the genre-safe denominator (see module docstring).
RESTORED = {"P.": 4517, "EI.": 3281}


def census() -> dict:
    fam = read_tsv(DATA / "pd_siglum_families.tsv")
    aob = {r["siglum"]: r for r in read_tsv(DATA / "pd_aob_siglum_title.tsv")}
    works = read_tsv(DATA / "pd_aob_declared_works.tsv")
    metrics = load_metrics()
    decl = declared_by_siglum(works)

    sigla = []
    for r in fam:
        text, strength = evidence_for(r, aob, decl)
        if r["class"] == "structural" and flat(r["siglum"]) not in _SIGLUM_INDEX:
            strength = "structural"
        genre, provenance = classify(text, r["siglum"], strength)
        sigla.append(
            {
                "siglum": r["siglum"],
                "siglum_fold": flat(r["siglum"]),
                "count": int(r["count"]),
                "class": r["class"],
                "match_type": r["match_type"],
                "evidence": text,
                "strength": strength,
                "genre": genre,
                "provenance": provenance,
            }
        )

    declared = []
    for w in works:
        text = (w["work_fold"] + " " + (w.get("sample_title") or "")).strip()
        genre, provenance = "other", "unresolved"
        for tok in re.split(r"[\s,;]+", w.get("sigla", "")):
            tok = tok.strip()
            if tok and flat(tok) in _SIGLUM_INDEX:
                genre, provenance = _SIGLUM_INDEX[flat(tok)], "siglum-map"
                break
        if genre == "other":
            genre, provenance = classify(text, w.get("sigla", ""), "strong")
        declared.append({"work": w["work_fold"], "genre": genre, "provenance": provenance})

    total_primary = sum(s["count"] for s in sigla if s["class"] == "primary")
    total_safe = total_primary + sum(RESTORED.values())

    table = []
    for genre in GENRES:
        rows = [s for s in sigla if s["genre"] == genre]
        prim = [s for s in rows if s["class"] == "primary"]
        worked = [s for s in rows if s["class"] != "structural" and s["count"] > 0]
        occ_primary = sum(s["count"] for s in prim)
        occ_safe = occ_primary + sum(RESTORED.get(s["siglum"], 0) for s in rows)
        n_declared = sum(1 for d in declared if d["genre"] == genre)
        top = sorted(worked, key=lambda s: (-s["count"], s["siglum"]))[:5]
        table.append(
            {
                "genre": genre,
                "n_sigla": len(worked),
                "n_sigla_primary": len(prim),
                "n_declared_works": n_declared,
                "declared_pct": 100.0 * n_declared / len(declared),
                "occurrences_primary": occ_primary,
                "pct_of_353512": 100.0 * occ_primary / total_primary,
                "occurrences_genre_safe": occ_safe,
                "pct_of_361310": 100.0 * occ_safe / total_safe,
                "top5": " | ".join(f"{s['siglum']} ({s['count']})" for s in top),
                "top5_works": " | ".join(s["evidence"].strip()[:70] for s in top),
                "printed_subject_codes": ",".join(
                    str(c) for c in GENRE_SUBJECT_CODES[genre]
                )
                or UNMAPPED_LABEL,
            }
        )

    anchor_entries: dict[str, list[tuple[str, str]]] = {"grammar": [], "epigraphy": [], "vedic": []}
    for ab, t in ABHYANKAR_WORKS:
        g = "vedic" if ab in ABHYANKAR_VEDIC else "grammar"
        if g in anchor_entries:
            anchor_entries[g].append((ab, t))
    for ab, t in IEG_EPIGRAPHIC_CORPORA.items():
        anchor_entries["epigraphy"].append((ab, t))
    # dedupe epigraphic corpora by title (the IEG spells some twice)
    seen: set[str] = set()
    deduped: list[tuple[str, str]] = []
    for ab, t in anchor_entries["epigraphy"]:
        if t not in seen:
            seen.add(t)
            deduped.append((ab, t))
    anchor_entries["epigraphy"] = deduped

    def anchor_names(genre: str) -> list[str]:
        if genre == "vedic":
            return sorted({flat(t) for ab, t in ABHYANKAR_WORKS if ab in ABHYANKAR_VEDIC})
        return sorted({flat(t) for _ab, t in anchor_entries[genre]})

    fold_to_sigla: dict[str, list[str]] = {}
    sigla_genre: dict[str, str] = {}
    for s in sigla:
        fold_to_sigla.setdefault(s["siglum_fold"], []).append(s["genre"])
        sigla_genre[s["siglum_fold"]] = s["genre"]
    canon = [flat(s["evidence"]) for s in sigla] + [flat(s["siglum"]) for s in sigla]
    canon += [flat(d["work"]) for d in declared]
    canon += [flat((aob.get(s["siglum"]) or {}).get("author") or "") for s in sigla if aob.get(s["siglum"])]

    def anchor_hit(abbr: str, title: str, genre: str) -> bool:
        names = [flat(t) for t in ANCHOR_PD_SIGLA.get(abbr, ()) + ANCHOR_PD_SIGLA.get(title, ())]
        if any(n in sigla_genre and sigla_genre[n] == genre for n in names):
            return True
        head = flat(title).split("of")[0][:12]
        if len(head) >= 6 and any(head in c for c in canon):
            return True
        first = flat(title).split("s")[0][:8] if " " in title else flat(title)[:8]
        return len(first) >= 6 and any(first in c for c in canon)

    def covered(names: list[str]) -> list[str]:
        return sorted(set(names))

    return {
        "sigla": sigla,
        "declared": declared,
        "table": table,
        "total_primary": total_primary,
        "total_safe": total_safe,
        "n_declared": len(declared),
        "anchors": {
            "grammar": anchor_names("grammar"),
            "epigraphy": anchor_names("epigraphy"),
            "vedic_from_abhyankar": anchor_names("vedic"),
            "entries": anchor_entries,
            "covered": {
                "grammar": sorted({flat(t) for ab, t in anchor_entries["grammar"] if anchor_hit(ab, t, "grammar")}),
                "epigraphy": sorted({flat(t) for ab, t in anchor_entries["epigraphy"] if anchor_hit(ab, t, "epigraphy")}),
            },
        },
        "metrics": metrics,
    }


# --------------------------------------------------------------------------
# Verdict -- PRE-REGISTERED before the numbers were read (handoff H6930).
#
# A contested genre is "materially exploited" (Wright 1978: "fairly thoroughly
# exploited") iff all three criteria hold:
#   M  mass    >= 2.0 % of the genre-safe denominator (361,310 occurrences)
#   B  breadth >= 10 distinct primary sigla with >= 1 occurrence
#   A  anchor  >= 25 % of the anchor's own bibliography evidenced in PD's
#              canon (declared works or exercised sigla)
# CONFIRMED = 3/3, PARTIAL = 2/3, REFUTED = <= 1/3.
# --------------------------------------------------------------------------
MASS_FLOOR = 2.0
BREADTH_FLOOR = 10
ANCHOR_FLOOR = 25.0


def verdict(table: list[dict], result: dict, genre: str) -> dict:
    row = next(r for r in table if r["genre"] == genre)
    anchor_all = result["anchors"][genre]
    anchor_hit = result["anchors"]["covered"][genre]
    anchor_pct = 100.0 * len(anchor_hit) / len(anchor_all) if anchor_all else 0.0
    criteria = {
        "mass_ge_2pct": row["pct_of_361310"] >= MASS_FLOOR,
        "breadth_ge_10": row["n_sigla"] >= BREADTH_FLOOR,
        "anchor_ge_25pct": anchor_pct >= ANCHOR_FLOOR,
    }
    met = sum(criteria.values())
    return {
        "genre": genre,
        "verdict": {3: "CONFIRMED", 2: "PARTIAL", 1: "REFUTED", 0: "REFUTED"}[met],
        "criteria": criteria,
        "criteria_met": met,
        "mass_pct_genre_safe": round(row["pct_of_361310"], 2),
        "mass_pct_primary": round(row["pct_of_353512"], 2),
        "occurrences_genre_safe": row["occurrences_genre_safe"],
        "n_sigla": row["n_sigla"],
        "n_declared_works": row["n_declared_works"],
        "anchor_total": len(anchor_all),
        "anchor_covered": len(anchor_hit),
        "anchor_pct": round(anchor_pct, 1),
        "anchor_missing": sorted(set(anchor_all) - set(anchor_hit)),
    }


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------
TSV_COLUMNS = [
    "genre",
    "n_sigla",
    "n_sigla_primary",
    "n_declared_works",
    "pct_of_declared_titles",
    "occurrences_primary",
    "pct_of_353512",
    "occurrences_genre_safe",
    "pct_of_361310",
    "top5_sigla",
    "top5_works",
    "printed_subject_codes",
]

CROSSWALK_COLUMNS = [
    "genre",
    "mapping",
    "printed_subject_codes",
    "printed_subject_classes",
    "index_of_works_subject_codes",
    "code_count",
    "share_pct_of_361310",
    "share_pct_of_353512",
    "note",
]


def validate_subject_crosswalk() -> None:
    """Every printed class 1-62 is owned exactly once; 'other' owns none."""
    owners: dict[int, str] = {}
    for genre in GENRES:
        for code in GENRE_SUBJECT_CODES[genre]:
            if not 1 <= code <= 62:
                raise SystemExit(f"crosswalk: {genre} has out-of-range code {code}")
            if code in owners:
                raise SystemExit(
                    f"crosswalk: code {code} mapped twice ({owners[code]}, {genre})"
                )
            owners[code] = genre
    missing = sorted(set(range(1, 63)) - set(owners))
    if missing:
        raise SystemExit(f"crosswalk: printed classes not mapped: {missing}")
    if GENRE_SUBJECT_CODES["other"]:
        raise SystemExit("crosswalk: 'other' must remain the unmapped bucket")


def render_crosswalk(table: list[dict]) -> str:
    validate_subject_crosswalk()
    names = dict(SUBJECT_CLASSES)
    lines = ["\t".join(CROSSWALK_COLUMNS)]
    for r in table:
        genre = r["genre"]
        codes = GENRE_SUBJECT_CODES[genre]
        mapped = "unmapped" if genre == "other" else "mapped"
        lines.append(
            "\t".join(
                [
                    genre,
                    mapped,
                    ",".join(str(c) for c in codes) or UNMAPPED_LABEL,
                    "; ".join(f"{c} {names[c]}" for c in codes)
                    or UNMAPPED_LABEL,
                    ",".join(str(c) for c in codes) or UNMAPPED_LABEL,
                    str(len(codes)),
                    f"{r['pct_of_361310']:.2f}",
                    f"{r['pct_of_353512']:.2f}",
                    GENRE_SUBJECT_NOTES[genre],
                ]
            )
        )
    return "\n".join(lines) + "\n"


def render_tsv(table: list[dict]) -> str:
    lines = ["\t".join(TSV_COLUMNS)]
    for r in table:
        lines.append(
            "\t".join(
                [
                    r["genre"],
                    str(r["n_sigla"]),
                    str(r["n_sigla_primary"]),
                    str(r["n_declared_works"]),
                    f"{r['declared_pct']:.2f}",
                    str(r["occurrences_primary"]),
                    f"{r['pct_of_353512']:.2f}",
                    str(r["occurrences_genre_safe"]),
                    f"{r['pct_of_361310']:.2f}",
                    r["top5"],
                    r["top5_works"],
                    r["printed_subject_codes"],
                ]
            )
        )
    return "\n".join(lines) + "\n"


def fmt_table(table: list[dict]) -> str:
    hdr = f"{'genre':<14}{'sigla':>6}{'prim':>6}{'works':>7}{'occ_prim':>10}{'%353512':>9}{'occ_safe':>10}{'%361310':>9}"
    out = [hdr, "-" * len(hdr)]
    for r in table:
        out.append(
            f"{r['genre']:<14}{r['n_sigla']:>6}{r['n_sigla_primary']:>6}{r['n_declared_works']:>7}"
            f"{r['occurrences_primary']:>10}{r['pct_of_353512']:>8.2f}%"
            f"{r['occurrences_genre_safe']:>10}{r['pct_of_361310']:>8.2f}%"
        )
    return "\n".join(out)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="PD genre-composition census (H6930)")
    ap.add_argument("--check", action="store_true", help="fail if the committed TSV drifts")
    ap.add_argument("--audit", action="store_true", help="print top sigla per genre")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--no-dice", action="store_true", help="ablation: disable the fuzzy channel")
    ap.add_argument("--no-map", action="store_true", help="ablation: disable the hand siglum map")
    args = ap.parse_args(argv)

    global USE_DICE, USE_SIGLUM_MAP
    USE_DICE = not args.no_dice
    USE_SIGLUM_MAP = not args.no_map

    result = census()
    table = result["table"]
    tsv = render_tsv(table)
    crosswalk_tsv = render_crosswalk(table)
    target = DATA / "pd_citation_genre.tsv"
    crosswalk_target = DATA / "pd_genre_subject_crosswalk.tsv"

    if args.check:
        stale = []
        for path, rendered in ((target, tsv), (crosswalk_target, crosswalk_tsv)):
            committed = path.read_text(encoding="utf-8") if path.exists() else ""
            if committed != rendered:
                stale.append(f"data/pd/{path.name}")
        if stale:
            print(
                "FAIL: stale; re-run the script: " + ", ".join(stale),
                file=sys.stderr,
            )
            return 1
        print("PASS: both committed TSVs reproduce")
        return 0

    verdicts = {g: verdict(table, result, g) for g in ("epigraphy", "grammar")}

    if args.json:
        print(
            json.dumps(
                {
                    "total_primary": result["total_primary"],
                    "total_genre_safe": result["total_safe"],
                    "n_declared_works": result["n_declared"],
                    "table": table,
                    "verdicts": verdicts,
                    "anchors": result["anchors"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    print(fmt_table(table))
    print()
    print(f"primary mass       {result['total_primary']:,} (4,988 sigla, pre-registered)")
    print(f"genre-safe mass    {result['total_safe']:,} (+ P. 4,517 + EI. 3,281)")
    print(f"declared works     {result['n_declared']:,} (AOB work-level; 1,419 edition-level)")
    print()
    for g in ("epigraphy", "grammar"):
        v = verdicts[g]
        print(
            f"{g:<12} {v['verdict']:<9} mass {v['mass_pct_genre_safe']:>5.2f}% "
            f"(primary {v['mass_pct_primary']:>5.2f}%)  breadth {v['n_sigla']:>4}  "
            f"anchor {v['anchor_covered']}/{v['anchor_total']} ({v['anchor_pct']}%)  "
            f"criteria {v['criteria_met']}/3"
        )
        print(f"{'':<12} criteria {v['criteria']}")
        if v["anchor_missing"]:
            print(f"{'':<12} anchor absent: {', '.join(v['anchor_missing'])}")

    if args.audit:
        print()
        for genre in GENRES:
            rows = sorted(
                [s for s in result["sigla"] if s["genre"] == genre],
                key=lambda s: (-s["count"], s["siglum"]),
            )[: args.top]
            print(f"### {genre}")
            for s in rows:
                print(
                    f"  {s['count']:>6}  {s['siglum']:<14} {s['class']:<10} "
                    f"{s['provenance']:<30} {(s['evidence'] or '')[:55]}"
                )

    writes = not (args.no_dice or args.no_map or args.audit or args.json)
    if writes:
        target.write_text(tsv, encoding="utf-8")
        crosswalk_target.write_text(crosswalk_tsv, encoding="utf-8")
        print(f"\nwrote {target.relative_to(REPO)}")
        print(f"wrote {crosswalk_target.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
