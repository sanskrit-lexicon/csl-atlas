"""Stage 2c — build the Patel co-annotation fill-in sheet for the five
judgement-bound conventions (dims 1,3,5,6,7).

For each dict with a local source, this extracts *discriminating* evidence per
convention — a computed rate plus real headword examples of each competing form —
so M.G. can assign the Patel value by eye in seconds rather than re-deriving it.

It does NOT assign the value (that is the human gate, design §12.3): the VALUE /
confidence / notes columns are left empty. The candidate option labels are
grounded in the orthographic phenomenon each convention distinguishes; M.G. can
remap them to Patel 2016's exact taxonomy (the PDF is not on this box).

R004 recount (21-11-2026, R003a dossier defects a-c fixed):
  (a) dim 1 now splits internal nasal vs compound-final म् (Patel 1.1/1.2 vs
      1.5/1.6): a nasal closes the first compound member when a hyphen precedes
      it or it is the M/N of the prefix saM-/saN-; everything else is internal.
      JSON keys become anu_i/anu_c/homo_i/homo_c.
  (b) dim 5 root buckets require a nasal directly followed by a consonant AND
      a consonant-final headword — kills the noun contaminants (agni, atnu,
      an, anas, prAn; aMsa/aMSu-type vowel-final stems). Full bucket counts
      replace the old example-length "4+ vs 4+" display bug.
  (c) dims 6/7 noun filters: -ar bucket drops the function words
      antar/apunar/punar/kiMpunar; dim 7 gains the counter-form buckets
      (vāṃs/vaṃs/yāṃs, vān/yān) that were previously verified only by eye.

Outputs:
  data/L0/patel_fillin.csv        32 dicts × 5 dims, evidence + empty VALUE col
  data/L0/patel_evidence.json     raw per-(dict,dim) evidence (rates + examples)
"""

import csv
import json
import os
import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_ROOT = os.path.normpath(os.path.join(REPO, "..", "csl-orig", "v02"))
CAP = 12000

DICTS = ["WIL", "YAT", "GST", "BEN", "MW72", "LRV", "AP90", "CAE", "MD", "MW",
         "SHS", "AP", "BOR", "AE", "BUR", "STC", "PWG", "GRA", "PW", "CCS", "SCH",
         "BOP", "VCP", "SKD", "INM", "VEI", "PUI", "BHS", "FRI", "ACC", "KRM", "MCI"]
NO_SOURCE = ["KNA", "KOW", "AMAR"]

# SLP1 stop consonants by varga + the homorganic nasal that precedes each.
STOPS = "kKgGcCjJwWqQtTdDpPbB"
HOMORGANIC = [("N", "kKgG"), ("Y", "cCjJ"), ("R", "wWqQ"), ("n", "tTdD"), ("m", "pPbB")]
# SLP1 consonants (nasals M m n N Y excluded; R = retroflex continuant, kept).
CONSONANTS = "kKgGcCjJwWqQRtTdDpPbBmyrlvLzSsh"

DIM_META = {
    1: ("Anusvāra before consonants",
        ("When a nasal precedes a stop inside a word, is it written as anusvāra "
        "(SLP1 M: aMka, saMskAra) or as the homorganic nasal (aNka, saMskAra→saNskAra)?"),
        "anusvara | homorganic | mixed"),
    3: ("Words ending with -at (śatṛ / vatup-matup)",
        ("How are present participles in -at and possessives in -vat/-mat cited "
        "(bare -at stem, or with further marking)? Patel: 5 options across 3+2 sub-conventions."),
        "see Patel 2016 — assign from -at / -vat / -mat examples"),
    5: ("Anusvāra of verbs",
        "Are nasal verbal roots cited with anusvāra (aMS) or the dental/labial nasal (aMs)?",
        "anusvara | nasal-letter | n.a. (no verb roots)"),
    6: ("ṛkārānta words (ṛ-final agent nouns)",
        ("How is an ṛ-stem agent noun (kartṛ) cited — bare stem (SLP1 kartf), "
        "nominative (kartA), or with -ar/-ṛ (kartar/kartR)?"),
        "stem-f | nominative-A | ar/R"),
    7: ("vas/yas suffixes (perfect ppl. -vas, comparative -yas)",
        "How are -vas (perfect participle) and -yas (comparative) stems cited / spelled?",
        "see Patel 2016 — assign from -vas / -yas examples"),
}
DIMS = [1, 3, 5, 6, 7]

# Function words ending in -ar that the dim-6 bucket wrongly caught (R003a (c)).
AR_STOP = {"antar", "apunar", "punar", "kiMpunar"}


def iter_k1(path, cap):
    n = 0
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("<L>") or line.startswith("<L "):
                m = re.search(r"<k1>([^<]*)", line)
                if m:
                    hw = m.group(1).strip()
                    if hw:
                        yield hw
                n += 1
                if n >= cap:
                    return


def take(seen, pool, k=4):
    out = []
    for x in pool:
        if x not in seen:
            out.append(x)
            seen.add(x)
        if len(out) >= k:
            break
    return out


def compound_final(hw, nas_i):
    """True when the nasal at index nas_i closes the first compound member
    (R003a (a) split): an explicit hyphen precedes it, or it is the M/N of the
    prefix saM-/saN- (the only preverb ending in m; asaM- included)."""
    if nas_i > 0 and hw[nas_i - 1] == "-":
        return True
    return nas_i >= 2 and hw[nas_i - 2: nas_i] == "sa"


def evidence(path):
    hws = list(iter_k1(path, CAP))
    ev = {}

    # dim 1 — anusvara vs homorganic nasal before a stop, split internal vs
    # compound-final म्. A headword counts once per bucket it exhibits.
    anu_i = anu_c = homo_i = homo_c = 0
    ex = {k: [] for k in ("anu_i", "anu_c", "homo_i", "homo_c")}
    for hw in hws:
        for i in range(len(hw) - 1):
            if hw[i] == "M" and hw[i + 1] in STOPS:
                key = "anu_c" if compound_final(hw, i) else "anu_i"
                if key == "anu_c":
                    anu_c += 1
                else:
                    anu_i += 1
                if len(ex[key]) < 8:
                    ex[key].append(hw)
                break
        for i in range(len(hw) - 1):
            if hw[i] in "NYRnm" and hw[i + 1] in STOPS:
                if not any(hw[i] == nas and hw[i + 1] in vg for nas, vg in HOMORGANIC):
                    continue
                key = "homo_c" if compound_final(hw, i) else "homo_i"
                if key == "homo_c":
                    homo_c += 1
                else:
                    homo_i += 1
                if len(ex[key]) < 8:
                    ex[key].append(hw)
                break
    sh_i = round(anu_i / (anu_i + homo_i), 3) if (anu_i + homo_i) else None
    sh_c = round(anu_c / (anu_c + homo_c), 3) if (anu_c + homo_c) else None
    ev[1] = {"anusvara_share_internal": sh_i, "anusvara_share_compound": sh_c,
             "n_anu_i": anu_i, "n_anu_c": anu_c, "n_homo_i": homo_i, "n_homo_c": homo_c,
             "ex_anu_i": take(set(), ex["anu_i"]), "ex_anu_c": take(set(), ex["anu_c"]),
             "ex_homo_i": take(set(), ex["homo_i"]), "ex_homo_c": take(set(), ex["homo_c"])}

    # dim 3 — -at / -vat / -mat endings
    at = [h for h in hws if h.endswith("at") and not h.endswith("vat") and not h.endswith("mat")]
    vat = [h for h in hws if h.endswith("vat")]
    mat = [h for h in hws if h.endswith("mat")]
    ev[3] = {"n_at": len(at), "n_vat": len(vat), "n_mat": len(mat),
             "ex_at": take(set(), at), "ex_vat": take(set(), vat), "ex_mat": take(set(), mat)}

    # dim 5 — nasal roots (R003a (b) fix): root-like = short (≤4), a nasal
    # directly followed by a consonant, and consonant-final — kills the noun
    # contaminants (agni/atnu/an/anas/prAn; vowel-final aMsa/aMSu-type stems).
    roots = [h for h in hws if (len(h) <= 4 and h[-1] in CONSONANTS
                                and re.search("[MmnN][" + CONSONANTS + "]", h))]
    anu_r = [h for h in roots if "M" in h]
    nas_r = [h for h in roots if "M" not in h and re.search(r"[mnN]", h)]
    ev[5] = {"n_roots": len(roots), "n_anusvara_root": len(anu_r),
             "n_nasal_root": len(nas_r),
             "ex_anusvara_root": take(set(), anu_r), "ex_nasal_root": take(set(), nas_r)}

    # dim 6 — ṛ-final agent nouns (R003a (c) filters: -ar stoplist; nom-A mass
    # kept but labelled — kartA-nominative and abstract -tā collide in SLP1).
    f_stem = [h for h in hws if h.endswith("f")]
    nomA = [h for h in hws if re.search(r"t[AR]$", h)]
    ar_end = [h for h in hws if (h.endswith("ar") and h not in AR_STOP) or h.endswith("tR")]
    R_end = [h for h in hws if h.endswith("R") and len(h) > 2]
    ev[6] = {"n_f_stem": len(f_stem), "n_nomA": len(nomA), "n_ar": len(ar_end),
             "n_R": len(R_end),
             "ex_stem_f": take(set(), f_stem), "ex_nomA": take(set(), nomA),
             "ex_ar": take(set(), ar_end), "ex_R": take(set(), R_end)}

    # dim 7 — -vas / -yas suffixes + the counter-forms (R003a (c)): plain
    # vas/yas spellings vs vāṃs/vaṃs/yāṃs and vān/yān, previously eye-checked.
    vas = [h for h in hws if h.endswith("vas")]
    yas = [h for h in hws if h.endswith("yas")]
    vams = [h for h in hws if re.search(r"[vy][Aa]M?s$", h)
            and not (h.endswith("vas") or h.endswith("yas"))]
    van = [h for h in hws if len(h) >= 5 and re.search(r"[vy][Aa]n$", h)
           and not h.endswith(("yan", "van"))]
    ev[7] = {"n_vas": len(vas), "n_yas": len(yas), "n_vams": len(vams), "n_van": len(van),
             "ex_vas": take(set(), vas), "ex_yas": take(set(), yas),
             "ex_vams": take(set(), vams), "ex_van": take(set(), van)}

    ev["_n_headwords"] = len(hws)
    return ev


def summary_cell(dim, e):
    """One compact human-readable evidence string per (dict, dim)."""
    if dim == 1:
        s = e[1]
        si, sc = s["anusvara_share_internal"], s["anusvara_share_compound"]
        parts = []
        if si is not None:
            parts.append(f"internal share={si} (M {s['n_anu_i']} vs homorg {s['n_homo_i']})")
        if sc is not None:
            parts.append(f"compound-final share={sc} (saM {s['n_anu_c']} vs saN {s['n_homo_c']})")
        return " · ".join(parts) if parts else "no nasal+stop headwords"
    if dim == 3:
        s = e[3]
        return f"-at {s['n_at']}, -vat {s['n_vat']}, -mat {s['n_mat']}"
    if dim == 5:
        s = e[5]
        return (f"nasal roots {s['n_roots']} "
                f"(M-form {s['n_anusvara_root']} vs n/m-form {s['n_nasal_root']})")
    if dim == 6:
        s = e[6]
        return f"ṛ-stem(f) {s['n_f_stem']}, nom-A {s['n_nomA']} (-tā mass), -ar/-R {s['n_ar']}"
    if dim == 7:
        s = e[7]
        return (f"-vas {s['n_vas']}, -yas {s['n_yas']} "
                f"· counter vāṃs/vaṃs {s['n_vams']}, vān/yān {s['n_van']}")
    return ""


def examples_cell(dim, e):
    if dim == 1:
        return (f"M-int: {' '.join(e[1]['ex_anu_i'][:3])}  ||  homorg-int: {' '.join(e[1]['ex_homo_i'][:3])}  "
                f"||  M-comp: {' '.join(e[1]['ex_anu_c'][:3])}  ||  homorg-comp: {' '.join(e[1]['ex_homo_c'][:3])}")
    if dim == 3:
        return (f"-at: {' '.join(e[3]['ex_at'][:3])}  |  -vat: {' '.join(e[3]['ex_vat'][:3])}  "
                f"|  -mat: {' '.join(e[3]['ex_mat'][:3])}")
    if dim == 5:
        return f"M-root: {' '.join(e[5]['ex_anusvara_root'][:4])}  ||  n/m-root: {' '.join(e[5]['ex_nasal_root'][:4])}"
    if dim == 6:
        return (f"stem-f: {' '.join(e[6]['ex_stem_f'][:3])}  |  nom-A: {' '.join(e[6]['ex_nomA'][:3])}  "
                f"|  -ar/R: {' '.join(e[6]['ex_ar'][:3])}")
    if dim == 7:
        base = f"-vas: {' '.join(e[7]['ex_vas'][:3])}  ||  -yas: {' '.join(e[7]['ex_yas'][:3])}"
        counter = []
        if e[7]["ex_vams"]:
            counter.append(f"vāṃs-like: {' '.join(e[7]['ex_vams'][:3])}")
        if e[7]["ex_van"]:
            counter.append(f"vān-like: {' '.join(e[7]['ex_van'][:3])}")
        return base + (("  ||  " + "  |  ".join(counter)) if counter else "")
    return ""


def main():
    all_ev = {}
    rows = []
    for code in DICTS:
        path = os.path.join(SRC_ROOT, code.lower(), code.lower() + ".txt")
        if not os.path.isfile(path):
            continue
        e = evidence(path)
        all_ev[code] = e
        for dim in DIMS:
            name, question, opts = DIM_META[dim]
            rows.append({
                "dict": code, "dim_id": dim, "dim_name": name,
                "convention_question": question,
                "candidate_options": opts,
                "evidence": summary_cell(dim, e),
                "examples": examples_cell(dim, e),
                "VALUE": "", "confidence": "", "notes": "",
            })
        print(f"{code:5s} hw={e['_n_headwords']:5d}  "
              f"anu_i={all_ev[code][1]['anusvara_share_internal']}  "
              f"anu_c={all_ev[code][1]['anusvara_share_compound']}  "
              f"-at={e[3]['n_at']}/-vat={e[3]['n_vat']}  f={e[6]['n_f_stem']}  "
              f"vas={e[7]['n_vas']}/yas={e[7]['n_yas']}  vams={e[7]['n_vams']}/van={e[7]['n_van']}")

    for code in NO_SOURCE:
        for dim in DIMS:
            name, question, opts = DIM_META[dim]
            rows.append({
                "dict": code, "dim_id": dim, "dim_name": name,
                "convention_question": question, "candidate_options": opts,
                "evidence": "NO LOCAL SOURCE — annotate from Cologne scans/print",
                "examples": "", "VALUE": "", "confidence": "", "notes": ""})

    fields = ["dict", "dim_id", "dim_name", "convention_question", "candidate_options",
              "evidence", "examples", "VALUE", "confidence", "notes"]
    with open("data/L0/patel_fillin.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    with open("data/L0/patel_evidence.json", "w", encoding="utf-8") as f:
        json.dump(all_ev, f, indent=2, ensure_ascii=False)

    print(f"\nWrote data/L0/patel_fillin.csv ({len(rows)} rows = "
          f"{len(DICTS)}+{len(NO_SOURCE)} dicts × {len(DIMS)} dims)")
    print("Wrote data/L0/patel_evidence.json")

    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from _provenance import write_source
        write_source("data/L0/patel_fillin.csv", "s2c_patel_evidence.py", 2)
        write_source("data/L0/patel_evidence.json", "s2c_patel_evidence.py", 2)
    except Exception as e:
        print(f"Provenance error: {e}")


if __name__ == "__main__":
    main()
