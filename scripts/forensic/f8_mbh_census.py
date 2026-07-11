"""Phase F8a — Mahābhārata citation-form census + Böhtlingk correction-notes miner (H610).

Ports the H488 Harivaṃśa method (f7_harivamsa_*) to the largest citation mass in the
Petersburg/Monier-Williams dictionaries. Two jobs, no web harvest:

  P0  Extract every MBH citation from PWG (`MBH. <book>,<verse>`, arabic book + continuous
      per-book verse) and MW (`MBh. <roman-book>, <verse>`), handling the abbreviated
      continuation forms (`<ls n="MBH. 3,">12470</ls>`, `<ls n="MBH.">4,321</ls>`) the plain
      <ls> regex misses. Census per parvan; census MW's bare-siglum rest honestly.

  P1  Mine Böhtlingk's *own explicit correction notes* attached to an MBH locus — the new
      pilot lane. German markers (fehlerhaft / Druckfehler / lies / richtig / st. / falsch /
      verderbt), associated with the NEAREST MBH <ls> occurrence, capturing the printed vs
      corrected form from the surrounding `{#…#}` braces and any `ed. Bomb.`/`ed. Calc.`
      cross-reference. Occurrence-level, not ref-level: the same locus can be flagged-wrong in
      one spot and cited valid in another (brū MBH. 7,9283) — only the flagged occurrence is
      captured (validation case 3, context-aware mining).

Why no continuous-index fit here (cf. f7). PWG/MW cite the Calcutta *vulgate* (per-parvan
continuous śloka numbers); every freely bulk-downloadable full MBH Sanskrit e-text is the
BORI *critical* recension (GRETIL/DCS/sanskritdocuments), against which a continuous index is
the measured DEAD_ENDS §8 dead end. No free Nilakantha-vulgate bulk text exists (Manipal
Sastri-Vavilla is D3-gated spot-check only; Calcutta is scans/OCR). So the fitted-index locus
census is deferred (recorded in the census doc + DEAD_ENDS); reading-evidence verification of
the disputed notes runs instead in f8_mbh_verify.py.

Outputs (committed measurements — no verse text):
  data/forensic/mbh_citation_inventory.csv     per citation: dict, book, verse, form, edition, L, headword
  data/forensic/mbh_parvan_distribution.csv    per (dict, parvan): count, min/median/max verse
  data/forensic/mbh_correction_notes.csv       mined notes: L, headword, book, verse, marker, forms, quote
  data/forensic/f8_report.json                 census + notes summary

Run from repo root:  python scripts/forensic/f8_mbh_census.py
Deps: ../sanskrit-util/py on sys.path (for SLP1 folding of the note forms; optional).
"""
import sys, os, re, json, csv, statistics
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath("scripts/forensic"))
sys.path.insert(0, os.path.abspath("scripts/L0"))
from parse_cslorig import iter_entries, CSL_ORIG
from _provenance import write_source

OUT = "data/forensic"
ROMAN = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7, "viii": 8, "ix": 9,
         "x": 10, "xi": 11, "xii": 12, "xiii": 13, "xiv": 14, "xv": 15, "xvi": 16,
         "xvii": 17, "xviii": 18}
# The 18 parvans (Calcutta/vulgate order) — for the distribution table labels.
PARVAN_NAME = {1: "Ādi", 2: "Sabhā", 3: "Vana/Āraṇyaka", 4: "Virāṭa", 5: "Udyoga", 6: "Bhīṣma",
               7: "Droṇa", 8: "Karṇa", 9: "Śalya", 10: "Sauptika", 11: "Strī", 12: "Śānti",
               13: "Anuśāsana", 14: "Āśvamedhika", 15: "Āśramavāsika", 16: "Mausala",
               17: "Mahāprasthānika", 18: "Svargārohaṇa"}

# <ls n="ATTR">PAYLOAD</ls>, tags stripped from payload
LS = re.compile(r'<ls(?:\s+n="([^"]*)")?\s*>(.*?)</ls>', re.DOTALL)
TAG = re.compile(r"<[^>]*>")
WS = re.compile(r"\s+")
# German correction / erratum markers (Böhtlingk's apparatus vocabulary).
# CASE-SENSITIVE on purpose: a case-insensitive `st.` matched "Ind. St." (Indische Studien)
# 696/835 times — the abbreviation "statt" is lowercase, "Studien"/"Stelle" is "St.".
MARKERS = re.compile(
    r"(?<![A-Za-zÄÖÜäöü])("
    r"[Ff]ehlerhaft|Druckfehler|verderbt|verschrieben|[Ff]älschlich|[Ff]alsch|"
    r"unrichtig|zu\s+lesen|zu\s+schreiben|lies|statt|st\.)"
    r"(?![A-Za-zäöü])")
# High-precision markers (Böhtlingk explicitly flags a printing/transmission error).
HIGH_CONF = {"fehlerhaft", "druckfehler", "verderbt", "verschrieben",
             "zu lesen", "zu schreiben", "lies"}


def clean(s):
    return WS.sub(" ", TAG.sub("", s)).strip()


def slp_forms(text):
    """Pull the {#…#} SLP1 tokens out of a note fragment (printed/corrected forms)."""
    return [WS.sub("", t) for t in re.findall(r"\{#([^#]*)#\}", text)]


# ---- P0: citation extraction --------------------------------------------------
def pwg_citations(body):
    """Yield (book, verse, form, edition) for each MBH ref in a PWG entry body.

    Handles: full `MBH. 7,9283`; edition-qualified `MBH. ed. Calc. 3,2729`; continuation
    `<ls n="MBH. 3,">12470</ls>` (book in attr) and `<ls n="MBH.">4,321</ls>` (book,verse in
    payload). Threads the last-seen book so a bare `<ls n="MBH.">9283</ls>` inherits it.
    """
    last_book = None
    for m in LS.finditer(body):
        attr = clean(m.group(1) or "")
        payload = clean(m.group(2) or "")
        A, P = attr.upper(), payload.upper()
        if not (A.startswith("MBH") or P.startswith("MBH") or
                (A.startswith("MBH") is False and P == "" and A == "")):
            pass
        # decide whether this <ls> is an MBH ref
        is_mbh = P.startswith("MBH") or A.startswith("MBH")
        if not is_mbh:
            continue
        edition = None
        blob = (attr + " " + payload).strip()
        if re.search(r"ed\.\s*Calc", blob, re.I):
            edition = "Calc"
        elif re.search(r"ed\.\s*Bomb", blob, re.I):
            edition = "Bomb"
        # strip the siglum + edition words, keep the numeric tail
        num_src = payload if re.search(r"\d", payload) else attr
        num_src = re.sub(r"(?i)MBH\.?|ed\.\s*Calc\.?|ed\.\s*Bomb\.?", " ", num_src)
        mm = re.search(r"(\d+)\s*,\s*(\d+)", num_src)          # book,verse together
        if mm:
            book, verse = int(mm.group(1)), int(mm.group(2))
        else:
            # book may sit in attr ("MBH. 3,"), verse alone in payload
            ab = re.search(r"(\d+)\s*,\s*$", attr)
            pv = re.search(r"^\s*(\d+)\s*$", payload)
            if ab and pv:
                book, verse = int(ab.group(1)), int(pv.group(1))
            elif pv and last_book is not None:
                book, verse = last_book, int(pv.group(1))       # bare verse inherits book
            else:
                continue                                        # bare siglum, no number
        if not (1 <= book <= 18):
            continue
        last_book = book
        yield book, verse, ("full" if re.search(r"\d+\s*,\s*\d+", payload) else "cont"), edition


def mw_citations(body):
    """Yield (book|None, verse|None, form) for MW `MBh.` refs. Roman book optional."""
    # MW cites in running text, not always <ls>; scan the raw body for MBh. tokens.
    for m in re.finditer(r"MBh\.\s*([ivxlc]+)?\s*,?\s*(\d+)?", body):
        roman, verse = m.group(1), m.group(2)
        book = ROMAN.get((roman or "").lower()) if roman else None
        v = int(verse) if verse else None
        if roman and book is None:
            continue                          # a stray non-roman token
        if book is None and v is None:
            yield None, None, "bare"          # bare `MBh.` siglum, no address
        elif book is not None and v is not None:
            yield book, v, "book+verse"
        elif v is not None:
            yield None, v, "verse-only"
        else:
            yield book, None, "book-only"


# ---- P1: correction-note miner ------------------------------------------------
def mine_notes(body, L, k1):
    """Find correction markers adjacent to an MBH <ls>; associate occurrence-level."""
    notes = []
    # locate every MBH <ls> occurrence with char offsets
    occ = []
    lastb = None
    for m in LS.finditer(body):
        attr = clean(m.group(1) or ""); payload = clean(m.group(2) or "")
        if not (attr.upper().startswith("MBH") or payload.upper().startswith("MBH")):
            continue
        ns = re.sub(r"(?i)MBH\.?|ed\.\s*Calc\.?|ed\.\s*Bomb\.?", " ", payload if re.search(r"\d", payload) else attr)
        mm = re.search(r"(\d+)\s*,\s*(\d+)", ns)
        if mm:
            b, v = int(mm.group(1)), int(mm.group(2))
        else:
            ab = re.search(r"(\d+)\s*,\s*$", attr); pv = re.search(r"^\s*(\d+)\s*$", payload)
            if ab and pv: b, v = int(ab.group(1)), int(pv.group(1))
            elif pv and lastb is not None: b, v = lastb, int(pv.group(1))
            else: continue
        if not (1 <= b <= 18): continue
        lastb = b
        occ.append((m.start(), m.end(), b, v))
    if not occ:
        return notes
    for mk in MARKERS.finditer(body):
        mpos = mk.start()
        # A Böhtlingk correction note refers to the citation it FOLLOWS ("MBH. 7,9226 … zu
        # lesen ist", "{#abravat#} MBH. 7,9283 fehlerhaft für …"). Prefer the nearest PRECEDING
        # MBH occurrence; fall back to the nearest following (some notes lead: "fehlerhaft für
        # {#pōṣya#} MBH. 1,312"). 150-char window tolerates an interposed <ls>ed. Bomb.</ls>.
        preceding = [o for o in occ if o[1] <= mpos]
        following = [o for o in occ if o[0] >= mk.end()]
        near, dist = None, 10 ** 9
        if preceding:
            c = max(preceding, key=lambda o: o[1]); near, dist = c, mpos - c[1]
        if (near is None or dist > 150) and following:
            c = min(following, key=lambda o: o[0]); near, dist = c, c[0] - mk.end()
        if near is None or dist > 150:
            continue
        b, v = near[2], near[3]
        marker = re.sub(r"\s+", " ", mk.group(1)).lower().strip()
        # printed = last {#…#} BEFORE the citation; corrected = first {#…#} AFTER the marker,
        # else the {#…#} sitting between citation and marker ("… {#Y#} zu lesen").
        before = re.findall(r"\{#([^#]*)#\}", body[max(0, near[0] - 70): near[0]])
        after = re.findall(r"\{#([^#]*)#\}", body[mk.end(): mk.end() + 70])
        between = re.findall(r"\{#([^#]*)#\}", body[near[1]: mk.start()])
        printed = WS.sub("", before[-1]) if before else ""
        if after:
            corrected = WS.sub("", after[0])
        elif between:
            corrected = WS.sub("", between[-1])
        else:
            corrected = ""
        ctx = clean(body[max(0, near[0] - 70): mk.end() + 90])
        ed = "Bomb" if re.search(r"ed\.\s*Bomb", ctx, re.I) else ("Calc" if re.search(r"ed\.\s*Calc", ctx, re.I) else None)
        notes.append({"L": L, "k1": k1, "book": b, "verse": v, "marker": marker,
                      "confidence": "high" if marker in HIGH_CONF else "medium",
                      "printed": printed, "corrected": corrected,
                      "edition_ref": ed or "", "quote": ctx[:240]})
    return notes


def load(code, fname, extractor):
    src = os.path.join(CSL_ORIG, code.lower(), f"{fname}.txt")
    cites, notes = [], []
    for e in iter_entries(src):
        k1 = (e["k1"] or "").strip()
        for tup in extractor(e["body"]):
            cites.append((k1, e["L"], tup))
        if code == "PWG":
            notes += mine_notes(e["body"], e["L"], k1)
    return cites, notes


def main():
    print("F8a — Mahābhārata citation census + Böhtlingk correction-notes (H610)")
    pwg, pwg_notes = load("PWG", "pwg", pwg_citations)
    mw, _ = load("MW", "mw", mw_citations)
    print(f"PWG MBH citations: {len(pwg)}   MW MBh citations: {len(mw)}   PWG notes: {len(pwg_notes)}")

    os.makedirs(OUT, exist_ok=True)
    # inventory csv
    with open(f"{OUT}/mbh_citation_inventory.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dict", "parvan", "verse", "form", "edition", "L", "headword_slp1"])
        for k1, Lid, (b, v, form, ed) in pwg:
            w.writerow(["PWG", b, v, form, ed or "", Lid, k1])
        for k1, Lid, (b, v, form) in mw:
            w.writerow(["MW", b if b else "", v if v is not None else "", form, "", Lid, k1])

    # parvan distribution
    dist = defaultdict(list)
    for k1, Lid, (b, v, form, ed) in pwg:
        dist[("PWG", b)].append(v)
    for k1, Lid, (b, v, form) in mw:
        if b and v is not None:
            dist[("MW", b)].append(v)
    with open(f"{OUT}/mbh_parvan_distribution.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dict", "parvan", "parvan_name", "n_citations", "min_verse", "median_verse", "max_verse"])
        for (d, b) in sorted(dist):
            vs = dist[(d, b)]
            w.writerow([d, b, PARVAN_NAME.get(b, "?"), len(vs), min(vs),
                        int(statistics.median(vs)), max(vs)])

    # notes csv
    with open(f"{OUT}/mbh_correction_notes.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["L", "headword_slp1", "parvan", "verse", "marker", "confidence",
                    "printed_slp1", "corrected_slp1", "edition_ref", "quote"])
        for n in sorted(pwg_notes, key=lambda n: (n["confidence"] != "high", n["book"], n["verse"])):
            w.writerow([n["L"], n["k1"], n["book"], n["verse"], n["marker"], n["confidence"],
                        n["printed"], n["corrected"], n["edition_ref"], n["quote"]])

    # QA: candidate PWG numeric typos — verse far beyond its parvan's robust upper fence
    # (Q3 + 3·IQR and past the 99.9th pct), the MBH analogue of HARIV. 19850. Reported items,
    # NOT change files — route through /cologne-correction-queue once the true reading is known.
    typos = []
    for b in range(1, 19):
        vs = sorted(dist[("PWG", b)])
        if len(vs) < 20:
            continue
        q1, q3 = vs[len(vs) // 4], vs[len(vs) * 3 // 4]
        fence = max(q3 + 3 * (q3 - q1), vs[int(len(vs) * 0.999)])
        for k1, Lid, (bb, v, form, ed) in pwg:
            if bb == b and v > fence:
                typos.append((b, v, Lid, k1, fence))
    typos.sort(key=lambda t: -t[1])
    with open(f"{OUT}/mbh_candidate_numeric_typos.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["parvan", "cited_verse", "L", "headword_slp1", "parvan_robust_fence"])
        for b, v, Lid, k1, fence in typos:
            w.writerow([b, v, Lid, k1, int(fence)])
    write_source(f"{OUT}/mbh_candidate_numeric_typos.csv", "f8_mbh_census.py", 8)

    # report
    mw_forms = Counter(form for _, _, (_, _, form) in mw)
    pwg_maxv = defaultdict(int)
    for _, _, (b, v, _, _) in pwg:
        pwg_maxv[b] = max(pwg_maxv[b], v)
    report = {
        "pwg_mbh_citations": len(pwg),
        "mw_mbh_citations": len(mw),
        "mw_form_breakdown": dict(mw_forms),
        "mw_with_roman_book": sum(1 for _, _, (b, v, f) in mw if b and v is not None),
        "pwg_correction_notes": len(pwg_notes),
        "pwg_notes_high_conf": sum(1 for n in pwg_notes if n["confidence"] == "high"),
        "pwg_notes_with_edition_ref": sum(1 for n in pwg_notes if n["edition_ref"]),
        "pwg_parvan_counts": {b: len(dist[("PWG", b)]) for b in range(1, 19) if ("PWG", b) in dist},
        "pwg_parvan_max_verse": dict(sorted(pwg_maxv.items())),
        "note_markers": dict(Counter(n["marker"] for n in pwg_notes)),
        "candidate_numeric_typos": len(typos),
    }
    json.dump(report, open(f"{OUT}/f8_report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for p in ("mbh_citation_inventory.csv", "mbh_parvan_distribution.csv", "mbh_correction_notes.csv"):
        write_source(f"{OUT}/{p}", "f8_mbh_census.py", 8)

    print(f"\nMW forms: {dict(mw_forms)}")
    print(f"PWG parvan max cited verse (raw; some are PWG's own typos, e.g. 13,73001): "
          f"{ {b: pwg_maxv[b] for b in sorted(pwg_maxv)} }")
    print(f"notes by marker: {report['note_markers']}")
    print(f"\nwrote mbh_citation_inventory.csv + mbh_parvan_distribution.csv + "
          f"mbh_correction_notes.csv + f8_report.json")


if __name__ == "__main__":
    main()
