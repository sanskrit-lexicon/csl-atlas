#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H1336 Phases 2-4 — normalise, classify, expand and join PD sigla to DCS.

Reads data/pd/pd_siglum_raw.tsv (Phase 1) and the DCS inventories, then:

  * classifies every siglum as one of
        structural   grammatical / editorial / locus markers (not a work)
        secondary    modern scholarship (dictionaries, IE etymology, epigraphy)
        primary      a Sanskrit work
  * for every primary siglum, decides whether the work is in DCS (covered) or
    not (residue), anchoring on DCS's bounded 276-text inventory;
  * emits data/pd/pd_siglum_families.tsv and data/pd/pd_dcs_text_crosswalk.tsv;
  * writes data/pd/pd_dcs_metrics.json with the four coverage numbers against
    DCS 2021 and DCS 2026.

Design note (see H1336 §4): PD cites a very long tail of works, so the top ~300
sigla are only ~74% of citation mass and hand-expanding to 95% is infeasible.
Instead we anchor on DCS — a bounded 276-text set — and map each DCS text to
its PD siglum(s). Covered mass is therefore exact regardless of a work's rank;
everything primary-but-not-in-DCS is the residue, which is the point of the study.

The MahāBhā./MahāBh. trap (§3) is handled explicitly below: MahāBhā. = Mahābhārata
(epic, in DCS), MahāBh. = Mahābhāṣya (Patañjali, grammar, NOT in DCS). They are
never merged.
"""
import sys
import os
import io
import re
import json
import csv

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PD_DIR = os.path.join(ROOT, "data", "pd")
RAW_TSV = os.path.join(PD_DIR, "pd_siglum_raw.tsv")

GH = os.path.dirname(ROOT)  # worktree is GitHub/csl-atlas-h1336, so GH == .../GitHub
VDCS = os.path.join(GH, "VisualDCS")
DELTA = os.path.join(VDCS, "derived-data", "Corpus-Delta-2021-2026", "per_text_token_delta.csv")
FILES2021 = os.path.join(VDCS, "src", "DCS-data-2021", "Files.csv")
CAPTERS = os.path.join(VDCS, "src", "DCS-data-2021", "capters.csv")
DCS_ABBR = os.path.join(GH, "DCS", "DCS-abbreviation-list.txt")

# ---------------------------------------------------------------------------
# 1. COVERED — DCS text (exact delta title) -> PD siglum(s) that denote it.
#    Only works PD actually cites (found in the raw list) are listed; obscure
#    DCS texts PD does not cite under the a- volume simply do not appear here.
# ---------------------------------------------------------------------------
DCS_TO_PD = {
    # --- Veda saṃhitā ---
    "Ṛgveda": ["ṚV."],
    "Atharvaveda (Śaunaka)": ["AV."],
    "Taittirīyasaṃhitā": ["TaiS."],
    "Maitrāyaṇīsaṃhitā": ["MaiS."],
    "Kāṭhakasaṃhitā": ["KāṭhS."],
    "Vājasaneyisaṃhitā (Mādhyandina)": ["VājaS."],
    # Sāmaveda: PD cites as SV.
    # (DCS has no standalone Sāmaveda saṃhitā entry -> handled as residue below)
    # --- Brāhmaṇa ---
    "Śatapathabrāhmaṇa": ["ŚatBr."],
    "Aitareyabrāhmaṇa": ["AitBr."],
    "Jaiminīyabrāhmaṇa": ["JaimiBr."],
    "Taittirīyabrāhmaṇa": ["TaiBr."],
    "Kauṣītakibrāhmaṇa": ["KauṣīBr."],
    "Gopathabrāhmaṇa": ["GopBr."],
    "Pañcaviṃśabrāhmaṇa": ["PañcBr."],
    "Ṣaḍviṃśabrāhmaṇa": ["ṢaḍviBr."],
    "Sāmavidhānabrāhmaṇa": ["SāmaViBr."],
    "Jaiminīya-Upaniṣad-Brāhmaṇa": ["JaimiUBr."],
    # --- Āraṇyaka / Upaniṣad (mūla only; bhāṣyas are separate residue works) ---
    "Aitareya-Āraṇyaka": ["AitĀ."],
    "Taittirīyāraṇyaka": ["TaiĀ."],
    "Śāṅkhāyanāraṇyaka": ["ŚāṅkhāĀ."],
    "Bṛhadāraṇyakopaniṣad": ["BṛĀraU."],
    "Chāndogyopaniṣad": ["ChāndoU."],
    "Śvetāśvataropaniṣad": ["ŚvetāU."],
    # --- Śrautasūtra ---
    "Āpastambaśrautasūtra": ["ĀpaŚS."],
    "Baudhāyanaśrautasūtra": ["BaudhŚS."],
    "Hiraṇyakeśiśrautasūtra": ["HirŚS."],
    "Kātyāyanaśrautasūtra": ["KātyŚS."],
    "Mānavaśrautasūtra": ["MānŚS."],
    "Bhāradvājaśrautasūtra": ["BhārŚS."],
    "Śāṅkhāyanaśrautasūtra": ["ŚāṅkhāŚS."],
    "Āśvālāyanaśrautasūtra": ["ĀśvaŚS."],
    # Lāṭyāyanaśrautasūtra (LāṭyāŚS.) is NOT in DCS -> residue, not covered
    "Drāhyāyaṇaśrautasūtra": ["DrāhyŚS."],
    "Vārāhaśrautasūtra": ["VārāŚS."],
    "Vaikhānasaśrautasūtra": ["VaikhāŚS."],
    "Vaitānasūtra": ["VaitāSū."],
    "Kauśikasūtra": ["KauśiSū."],
    # --- Gṛhyasūtra ---
    "Āśvalāyanagṛhyasūtra": ["ĀśvaGS."],
    "Pāraskaragṛhyasūtra": ["PāraGS."],
    "Gobhilagṛhyasūtra": ["GobhiGS."],
    "Śāṅkhāyanagṛhyasūtra": ["ŚāṅkhāGS."],
    "Kauṣītakagṛhyasūtra": ["KauṣīGS."],
    "Mānavagṛhyasūtra": ["MānGS."],
    "Bhāradvājagṛhyasūtra": ["BhārGS."],
    "Hiraṇyakeśigṛhyasūtra": ["HirGS."],
    "Kāṭhakagṛhyasūtra": ["KāṭhGS."],
    "Jaiminigṛhyasūtra": ["JaimiGS."],
    "Baudhāyanagṛhyasūtra": ["BaudhGS."],
    "Vaikhānasagṛhyasūtra": ["VaikhāGS."],
    # --- Dharma / smṛti ---
    "Manusmṛti": ["ManuSm."],
    "Yājñavalkyasmṛti": ["YājñaSm."],
    "Viṣṇusmṛti": ["ViṣṇuSm."],
    "Nāradasmṛti": ["NāraSm."],
    "Gautamadharmasūtra": ["GautDS."],
    "Āpastambadharmasūtra": ["ĀpaDS."],
    "Baudhāyanadharmasūtra": ["BaudhDS."],
    "Vasiṣṭhadharmasūtra": ["VāsiDS."],
    "Kātyāyanasmṛti": ["KātySm."],
    "Parāśaradharmasaṃhitā": ["ParāSm."],
    # --- Epic / Purāṇa in DCS ---
    "Mahābhārata": ["MahāBhā."],
    "Rāmāyaṇa": ["Rāmā."],
    "Harivaṃśa": ["HariVaṃ."],
    "Bhāgavatapurāṇa": ["BhāgP."],
    "Agnipurāṇa": ["AgniP."],
    "Matsyapurāṇa": ["MatsyaP."],
    "Viṣṇupurāṇa": ["ViṣṇuP."],
    "Skandapurāṇa": ["SkandP."],
    "Kūrmapurāṇa": ["KūrmaP."],
    "Liṅgapurāṇa": ["LiṅgaP."],
    "Varāhapurāṇa": ["VarāP."],
    "Śivapurāṇa": ["ŚivaP."],
    # --- Kāvya / nāṭaka / campū / kathā in DCS ---
    "Kumārasaṃbhava": ["KumāSaṃ."],
    "Meghadūta": ["MeghDū."],
    "Kirātārjunīya": ["Kirātā."],
    "Harṣacarita": ["HarṣaC."],
    "Daśakumāracarita": ["DaśKuC."],
    "Buddhacarita": ["BuddhaC."],
    "Saundarānanda": ["Saund."],
    "Hitopadeśa": ["Hitopa."],
    "Gītagovinda": ["GītGo."],
    "Śatakatraya": ["ŚatTrayī."],
    "Kathāsaritsāgara": ["KathāSaSāg."],
    "Bṛhatkathāślokasaṃgraha": ["BṛKathāŚloSaṃ."],
    "Vetālapañcaviṃśatikā": ["VetāPañ."],
    "Tantrākhyāyikā": ["Tantrākhyā."],
    # --- Alaṃkāra / poetics in DCS ---
    "Nāṭyaśāstra": ["NāṭyaŚā."],
    "Kāvyālaṃkāra": ["Kāvyālaṅ."],
    "Kāvyādarśa": ["Kāvyāda."],
    # --- Darśana / śāstra in DCS ---
    "Aṣṭādhyāyī": ["P."],
    "Kāśikāvṛtti": ["KāśiVṛ.", "Kāśi."],
    "Nirukta": ["Nir."],
    "Nyāyasūtra": ["NyāySu.", "NyāySū."],
    "Nyāyabhāṣya": ["NyāyBh."],
    "Tarkasaṃgraha": ["TarkSaṃ."],
    "Sāṃkhyatattvakaumudī": ["SāṃkhyaTaKau."],
    "Sāṃkhyakārikābhāṣya": ["SāṃkhyaKāBh."],
    "Yogasūtrabhāṣya": ["YogBh."],
    "Tattvavaiśāradī": ["TattvVai."],
    "Sarvadarśanasaṃgraha": ["SarvaDaSaṃ."],
    "Arthaśāstra": ["ArthŚā."],
    "Kāmasūtra": ["KāmSū."],
    "Mīmāṃsāsūtrabhāṣya": ["ŚābaBh."],
    "Nyāyabhāṣya ": ["NyāyBh."],
    # --- Āyurveda / rasa / nighaṇṭu in DCS ---
    "Carakasaṃhitā": ["CaraS."],
    "Suśrutasaṃhitā": ["SuśruS."],
    "Aṣṭāṅgahṛdayasaṃhitā": ["AṣṭāHṛ."],
    "Aṣṭāṅgasaṃgraha": ["AṣṭāSaṃ."],
    "Bhāvaprakāśa": ["BhāvPra."],
    "Rājanighaṇṭu": ["RājNi."],
    "Dhanvantarinighaṇṭu": ["DhanvNi."],
    "Śārṅgadharasaṃhitā": ["ŚārṅgaS."],
    "Rasaratnasamuccaya": ["RasRaSa."],
    # --- Jyotiṣa ---
    "Sūryasiddhānta": ["SūrySi."],
    # --- Buddhist ---
    "Divyāvadāna": ["Divyāva."],
    "Lalitavistara": ["LaliVi."],
    "Saddharmapuṇḍarīkasūtra": ["SaddhaPuṇ."],
    "Abhidharmakośa": ["AbhidhK."],
    "Abhidharmakośabhāṣya": ["AbhidhKoBh."],
    # --- Tantra / āgama ---
    "Mṛgendratantra": ["MṛgendraT."],
    # --- Kośa ---
    "Amarakośa": ["AmaK."],
    "Abhidhānacintāmaṇi": ["AbhidhāCin."],
    "Trikāṇḍaśeṣa": ["TrikāŚe."],
}

# remove the accidental dup key artefact
DCS_TO_PD.pop("Nyāyabhāṣya ", None)

# ---------------------------------------------------------------------------
# 2. SECONDARY — modern scholarship (excluded from the "books in Sanskrit"
#    denominator per §1). Value is the resolved source.
# ---------------------------------------------------------------------------
SECONDARY = {
    "EI.": "Epigraphia Indica (epigraphy journal)",
    "MW.": "Monier-Williams, Skt-Eng Dictionary",
    "PW.": "Böhtlingk-Roth, Petersburger Wörterbuch (grosses)",
    "APTE.": "Apte, Skt-Eng Dictionary",
    "VIŚVA.": "Vishva Bandhu, Vaidika-Padānukrama-Koṣa (Vedic Word Concordance)",
    "DEBRU.": "Debrunner (Altindische Grammatik)",
    "AltGr.": "Wackernagel-Debrunner, Altindische Grammatik",
    "MAYR.": "Mayrhofer, Etymol. Wörterbuch des Altindoarischen",
    "POK.": "Pokorny, Indogermanisches etymol. Wörterbuch",
    "TURN.": "Turner, Comparative Dict. of Indo-Aryan",
    "GRASS.": "Grassmann, Wörterbuch zum Rig-Veda",
    "RENOU.": "Renou (grammar/philology)",
    "DBHS.": "modern reference (secondary)",
    "Cpd.": "Compendium of Philosophy (Buddhist, secondary)",
}

# ---------------------------------------------------------------------------
# 3. STRUCTURAL — grammatical labels, editorial / apparatus markers, locus
#    sub-part letters and Roman-numeral volume/book numbers. Never a work.
# ---------------------------------------------------------------------------
STRUCTURAL_EXACT = {
    # grammatical case / number / compound / gender labels
    "Nom.", "Acc.", "Instr.", "Dat.", "Abl.", "Gen.", "Voc.", "Loc.",
    "Sg.", "Du.", "Pl.", "Dv.", "Cpd.", "Bv.", "Tp.", "Kdh.", "Karmadh.",
    "Gr.", "Comp.", "Compar.", "Superl.", "Caus.", "Pass.", "Desid.",
    # editorial / apparatus
    "Ed.", "App.", "Introd.", "Comm.", "Var.", "Add.", "Corr.", "Suppl.",
    "Fn.", "Fasc.", "Vol.", "Pt.", "Ch.", "Sec.", "No.", "Cf.",
    # single ambiguous heads seen as locus sub-parts / bhāṣya stubs
    "A.", "B.", "C.", "Ā.", "Bh.", "Bhā.", "Saṃ.", "Vā.", "Ka.", "U.",
    "Vi.", "Mā.", "Ma.", "Su.", "Śā.", "He.", "K.", "N.", "F.", "Ja.",
    "Ra.", "Rā.", "Pra.", "Cin.", "Cam.", "Can.", "Sū.", "Sm.", "Vṛ.",
    "Mañ.", "Dha.", "Dī.", "Kā.", "Nāgā.", "Kau.", "Pari.", "Prati.",
    "Bṛha.", "Bṛ.", "Sārā.", "IE.", "Skt.", "Ved.", "Prāk.", "Pr.",
}
ROMAN_RE = re.compile(r"^(?:X{0,3})(?:IX|IV|V?I{0,3})\.$")  # I.–XXXIX.


def is_structural(siglum: str) -> bool:
    if siglum in STRUCTURAL_EXACT:
        return True
    if ROMAN_RE.match(siglum) and siglum not in ("I.",):  # I. is roman here too
        return True
    if siglum == "I.":
        return True
    # a bare single uppercase letter + period (locus column markers A. B. ...)
    core = siglum[:-1]
    if len(core) == 1 and core.isupper():
        return True
    return False


# ---------------------------------------------------------------------------
# 4. RESIDUE_NAMED — high-frequency primary works PD cites that are NOT in DCS.
#    Purely for the residue report (§4); classification-wise they are primary.
# ---------------------------------------------------------------------------
RESIDUE_NAMED = {
    "PadmP.": "Padmapurāṇa",
    "BrahmāṇḍP.": "Brahmāṇḍapurāṇa",
    "RājTa.": "Rājataraṅgiṇī",
    "MahāBh.": "Mahābhāṣya (Patañjali)",
    "BhaviP.": "Bhaviṣyapurāṇa",
    "Vaija.": "Vaijayantī (kośa)",
    "MārkP.": "Mārkaṇḍeyapurāṇa",
    "BrahmP.": "Brahmapurāṇa",
    "VāyuP.": "Vāyupurāṇa",
    "ViṣṇuDhaP.": "Viṣṇudharmottarapurāṇa",
    "GaṇeP.": "Gaṇeśapurāṇa",
    "ŚiśuVa.": "Śiśupālavadha (Māgha)",
    "NānārthāSaṃ.": "Nānārthasaṃgraha (kośa)",
    "SāhiDa.": "Sāhityadarpaṇa",
    "DevīBhāP.": "Devībhāgavatapurāṇa",
    "VāmaP.": "Vāmanapurāṇa",
    "NaiṣC.": "Naiṣadhīyacarita",
    "MediK.": "Medinīkośa",
    "RaghuVa.": "Raghuvaṃśa (Kālidāsa)",
    "BṛSaṃ.": "Bṛhatsaṃhitā (Varāhamihira)",
    "AnekāSaṃ.": "Anekārthasaṃgraha (kośa)",
    "KāvyPra.": "Kāvyaprakāśa (Mammaṭa)",
    "Kād.": "Kādambarī (Bāṇa)",
    "ViśvaPra.": "Viśvaprakāśa (kośa)",
    "BrahmVaiP.": "Brahmavaivartapurāṇa",
    "KāśyaS.": "Kāśyapasaṃhitā",
    "Loc.": "Locana / locative (ambiguous)",
    "Vār.": "Vārttika (Kātyāyana, on Pāṇini)",
    "Prasā.": "Prasāda (grammatical comm.)",
    "PañcT.": "Pañcatantra",
    "Mṛcch.": "Mṛcchakaṭika",
    "MudrāRā.": "Mudrārākṣasa",
    "VeṇīSaṃ.": "Veṇīsaṃhāra",
    "UttaRāC.": "Uttararāmacarita",
    "MahāvīC.": "Mahāvīracarita",
    "SV.": "Sāmaveda(saṃhitā)",
    "BṛParāSm.": "Bṛhatparāśarasmṛti",
    "AbhidhāRaMā.": "Abhidhānaratnamālā (Halāyudha)",
    "Dhvanyā.": "Dhvanyāloka (Ānandavardhana)",
    "DaśRū.": "Daśarūpaka",
    "ChāndoUBh.": "Chāndogyopaniṣadbhāṣya (Śaṅkara)",
    "BṛĀraUBh.": "Bṛhadāraṇyakopaniṣadbhāṣya (Śaṅkara)",
    "Mālavikā.": "Mālavikāgnimitra",
    "Vikramo.": "Vikramorvaśīya",
    "LāṭyāŚS.": "Lāṭyāyanaśrautasūtra",
}

import unicodedata


def skeleton(siglum: str) -> str:
    """Consonant skeleton of a siglum — used to merge spelling variants
    (PadmP./PadmaP., ManuSm./ManuSma.) into one work-family for an
    approximate distinct-work count. Strip the period, decompose and drop
    combining marks, lowercase, then remove all vowels. Coarse but stable."""
    s = siglum.rstrip(".")
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    s = s.lower()
    return re.sub(r"[aeiou]", "", s)


def load_raw():
    rows = []
    with io.open(RAW_TSV, "r", encoding="utf-8") as fh:
        r = csv.reader(fh, delimiter="\t")
        next(r)
        for parts in r:
            if not parts:
                continue
            sig = parts[0]
            cnt = int(parts[1])
            rows.append((sig, cnt))
    return rows


def load_dcs():
    """Return dict title -> {tok21, tok26, chapters, in2021}."""
    delta = {}
    with io.open(DELTA, "r", encoding="utf-8") as fh:
        r = csv.DictReader(fh)
        for d in r:
            title = d["text_2026"].strip()
            if not title:
                continue
            delta[title] = {
                "tok21": int(d["tok_2021"]) if d["tok_2021"] else 0,
                "tok26": int(d["tok_2026"]) if d["tok_2026"] else 0,
            }
    # title -> DCS abbrev (for chapter counts)
    title2abbr = {}
    with io.open(DCS_ABBR, "r", encoding="utf-8") as fh:
        for line in fh:
            if "\t" not in line:
                continue
            title, abbr = line.rstrip("\n").split("\t", 1)
            title2abbr[title.strip()] = abbr.strip()
    # chapters per abbrev
    chapters = {}
    with io.open(CAPTERS, "r", encoding="utf-8") as fh:
        for line in fh:
            if "," not in line:
                continue
            abbr = line.split(",", 1)[0].strip()
            chapters[abbr] = chapters.get(abbr, 0) + 1
    for title, info in delta.items():
        abbr = title2abbr.get(title)
        info["abbr"] = abbr
        info["chapters"] = chapters.get(abbr, 0) if abbr else 0
    return delta


def main():
    raw = load_raw()
    dcs = load_dcs()
    total_mass = sum(c for _, c in raw)

    # invert DCS_TO_PD: siglum -> dcs_title
    sig2dcs = {}
    for title, sigs in DCS_TO_PD.items():
        for s in sigs:
            sig2dcs[s] = title

    # sanity: warn on any mapped siglum absent from the raw data (typo catch)
    raw_set = {s for s, _ in raw}
    missing = [s for s in sig2dcs if s not in raw_set]
    for s in missing:
        print(f"WARN mapped siglum not found in raw: {s} -> {sig2dcs[s]}", file=sys.stderr)
    dcs_title_set = set(dcs)
    bad_titles = [t for t in DCS_TO_PD if t not in dcs_title_set]
    for t in bad_titles:
        print(f"WARN DCS title not in delta inventory: {t!r}", file=sys.stderr)

    families = []          # (siglum, count, klass, subtype, dcs_title, display)
    covered_mass = 0
    secondary_mass = 0
    structural_mass = 0
    primary_mass = 0
    residue_mass = 0
    covered_titles = {}    # dcs_title -> pd_count
    residue_rows = []      # (display, siglum, count)

    for sig, cnt in raw:
        if sig in SECONDARY:
            families.append((sig, cnt, "secondary", "", "", SECONDARY[sig]))
            secondary_mass += cnt
            continue
        if is_structural(sig):
            families.append((sig, cnt, "structural", "", "", ""))
            structural_mass += cnt
            continue
        # primary work
        primary_mass += cnt
        if sig in sig2dcs:
            title = sig2dcs[sig]
            families.append((sig, cnt, "primary", "covered", title, title))
            covered_mass += cnt
            covered_titles[title] = covered_titles.get(title, 0) + cnt
        else:
            display = RESIDUE_NAMED.get(sig, "")
            families.append((sig, cnt, "primary", "residue", "", display))
            residue_mass += cnt
            residue_rows.append((display, sig, cnt))

    # ---- write families tsv ----
    fam_path = os.path.join(PD_DIR, "pd_siglum_families.tsv")
    with io.open(fam_path, "w", encoding="utf-8", newline="\n") as out:
        out.write("siglum\tcount\tclass\tmatch_type\tdcs_title\tdisplay_title\n")
        for sig, cnt, kl, st, dt, disp in families:
            out.write(f"{sig}\t{cnt}\t{kl}\t{st}\t{dt}\t{disp}\n")

    # ---- write crosswalk tsv (one row per DCS text PD cites) ----
    cw_path = os.path.join(PD_DIR, "pd_dcs_text_crosswalk.tsv")
    covered_tok26 = 0
    covered_tok21 = 0
    with io.open(cw_path, "w", encoding="utf-8", newline="\n") as out:
        out.write("dcs_title\tpd_sigla\tpd_citations\tdcs_tok_2021\tdcs_tok_2026\t"
                  "dcs_chapters\tcoverage_grade\n")
        for title in sorted(covered_titles, key=lambda t: -covered_titles[t]):
            info = dcs.get(title, {})
            tok21 = info.get("tok21", 0)
            tok26 = info.get("tok26", 0)
            ch = info.get("chapters", 0)
            covered_tok26 += tok26
            covered_tok21 += tok21
            sigs = "|".join(DCS_TO_PD[title])
            grade = grade_coverage(title, info)
            out.write(f"{title}\t{sigs}\t{covered_titles[title]}\t{tok21}\t{tok26}\t{ch}\t{grade}\n")

    total_dcs_tok26 = sum(v["tok26"] for v in dcs.values())
    total_dcs_tok21 = sum(v["tok21"] for v in dcs.values())

    # distinct primary works: covered titles + named residue + unnamed-tail families.
    # unnamed tail approximated by distinct siglum (over-counts variants, so this
    # is an UPPER bound on the denominator -> a LOWER bound on title-level %).
    n_covered_titles = len(covered_titles)
    named_residue_sigla = {r[1] for r in residue_rows if r[0]}
    unnamed_residue_sigla = {r[1] for r in residue_rows if not r[0]}
    n_residue_named = len(named_residue_sigla)
    n_residue_unnamed = len(unnamed_residue_sigla)
    # UPPER-BOUND denominator: every distinct primary siglum = a distinct work
    # (over-counts because spelling variants of one work stay separate).
    n_primary_works_ub = n_covered_titles + n_residue_named + n_residue_unnamed
    # ESTIMATE denominator: merge residue sigla by consonant skeleton so
    # PadmP./PadmaP. etc. collapse. Covered works are counted by DCS title (119).
    residue_skeletons = {skeleton(r[1]) for r in residue_rows}
    n_primary_works_est = n_covered_titles + len(residue_skeletons)

    metrics = {
        "generated_by": "H1336 pd_dcs_crosswalk.py (Opus 4.8, claude-opus-4-8)",
        "pd_scope_note": "PD published a- to ~apaca- only (6 of 37+ vols); this is "
                         "PD's canon as exercised under letter a-, not its full "
                         "declared canon.",
        "total_siglum_mass": total_mass,
        "structural_mass": structural_mass,
        "secondary_mass": secondary_mass,
        "primary_work_mass": primary_mass,
        "covered_mass": covered_mass,
        "residue_mass": residue_mass,
        "n_covered_dcs_titles": n_covered_titles,
        "n_primary_works_upper_bound": n_primary_works_ub,
        "n_primary_works_skeleton_estimate": n_primary_works_est,
        "n_residue_named": n_residue_named,
        "n_residue_unnamed_sigla": n_residue_unnamed,
        # --- the four headline metrics ---
        "metric_pd_citation_weighted_pct": round(100 * covered_mass / primary_mass, 2),
        "metric_title_level_pct_lower_bound": round(100 * n_covered_titles / n_primary_works_ub, 2),
        "metric_title_level_pct_estimate": round(100 * n_covered_titles / n_primary_works_est, 2),
        "metric_dcs_token_weighted_2026_pct": round(100 * covered_tok26 / total_dcs_tok26, 2),
        "metric_dcs_token_weighted_2021_pct": round(100 * covered_tok21 / total_dcs_tok21, 2),
        "covered_dcs_tok_2021": covered_tok21,
        "covered_dcs_tok_2026": covered_tok26,
        "total_dcs_tok_2021": total_dcs_tok21,
        "total_dcs_tok_2026": total_dcs_tok26,
        "structural_pct": round(100 * structural_mass / total_mass, 2),
        "secondary_pct": round(100 * secondary_mass / total_mass, 2),
    }
    with io.open(os.path.join(PD_DIR, "pd_dcs_metrics.json"), "w", encoding="utf-8", newline="\n") as out:
        json.dump(metrics, out, ensure_ascii=False, indent=2)

    # residue table (top 40 named / by freq)
    residue_named_sorted = sorted([r for r in residue_rows if r[0]], key=lambda r: -r[2])

    # ---- summary ----
    def pct(x):
        return f"{100*x/total_mass:.1f}%"
    print("=== MASS BREAKDOWN (of {:,} total siglum occurrences) ===".format(total_mass), file=sys.stderr)
    print(f"  structural : {structural_mass:7,}  {pct(structural_mass)}", file=sys.stderr)
    print(f"  secondary  : {secondary_mass:7,}  {pct(secondary_mass)}", file=sys.stderr)
    print(f"  primary    : {primary_mass:7,}  {pct(primary_mass)}", file=sys.stderr)
    print(f"    covered  : {covered_mass:7,}  ({100*covered_mass/primary_mass:.1f}% of primary)", file=sys.stderr)
    print(f"    residue  : {residue_mass:7,}  ({100*residue_mass/primary_mass:.1f}% of primary)", file=sys.stderr)
    print("", file=sys.stderr)
    print("=== FOUR HEADLINE METRICS ===", file=sys.stderr)
    print(f"  1. PD-citation-weighted coverage : {metrics['metric_pd_citation_weighted_pct']}%", file=sys.stderr)
    print(f"  2. title-level coverage (LB)     : {metrics['metric_title_level_pct_lower_bound']}%"
          f"  ({n_covered_titles}/{n_primary_works_ub} raw sigla)", file=sys.stderr)
    print(f"     title-level coverage (est)    : {metrics['metric_title_level_pct_estimate']}%"
          f"  ({n_covered_titles}/{n_primary_works_est} skeleton-merged works)", file=sys.stderr)
    print(f"  3. DCS-token-weighted 2026       : {metrics['metric_dcs_token_weighted_2026_pct']}%", file=sys.stderr)
    print(f"     DCS-token-weighted 2021       : {metrics['metric_dcs_token_weighted_2021_pct']}%", file=sys.stderr)
    print("", file=sys.stderr)
    print(f"  covered DCS titles: {n_covered_titles}", file=sys.stderr)
    print(f"  adjudicated mass (struct+sec+covered+named-residue) reaches "
          f"{100*(structural_mass+secondary_mass+covered_mass+sum(r[2] for r in residue_named_sorted))/total_mass:.1f}% "
          "with an explicit status", file=sys.stderr)
    print("", file=sys.stderr)
    print("=== TOP RESIDUE — PD works NOT in DCS (the §4 finding) ===", file=sys.stderr)
    for disp, sig, cnt in residue_named_sorted[:25]:
        print(f"  {cnt:5d}  {sig:14s} {disp}", file=sys.stderr)
    return 0


def grade_coverage(title, info):
    """Rough complete/partial grade for a covered DCS text."""
    # hand-known partial texts (DCS holds only a portion)
    partials = {
        "Skandapurāṇa": "partial (DCS ~ Revākhaṇḍa / fragments only)",
        "Kāśikāvṛtti": "partial (DCS text incomplete)",
    }
    if title in partials:
        return partials[title]
    tok26 = info.get("tok26", 0)
    if tok26 == 0:
        return "absent-tokens"
    # texts with a large 2021->2026 growth were partial in 2021
    return "present"


if __name__ == "__main__":
    raise SystemExit(main())
