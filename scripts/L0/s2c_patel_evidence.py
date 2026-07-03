"""Stage 2c — build the Patel co-annotation fill-in sheet for the five
judgement-bound conventions (dims 1,3,5,6,7).

For each dict with a local source, this extracts *discriminating* evidence per
convention — a computed rate plus real headword examples of each competing form —
so M.G. can assign the Patel value by eye in seconds rather than re-deriving it.

It does NOT assign the value (that is the human gate, design §12.3): the VALUE /
confidence / notes columns are left empty. The candidate option labels are
grounded in the orthographic phenomenon each convention distinguishes; M.G. can
remap them to Patel 2016's exact taxonomy (the PDF is not on this box).

Outputs:
  data/L0/patel_fillin.csv        32 dicts × 5 dims, evidence + empty VALUE col
  data/L0/patel_evidence.json     raw per-(dict,dim) evidence (rates + examples)
"""

import os
import sys
import re
import csv
import json
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

DIM_META = {
    1: ("Anusvāra before consonants",
        "When a nasal precedes a stop inside a word, is it written as anusvāra "
        "(SLP1 M: aMka, saMskAra) or as the homorganic nasal (aNka, saMskAra→saNskAra)?",
        "anusvara | homorganic | mixed"),
    3: ("Words ending with -at (śatṛ / vatup-matup)",
        "How are present participles in -at and possessives in -vat/-mat cited "
        "(bare -at stem, or with further marking)? Patel: 5 options across 3+2 sub-conventions.",
        "see Patel 2016 — assign from -at / -vat / -mat examples"),
    5: ("Anusvāra of verbs",
        "Are nasal verbal roots cited with anusvāra (aMS) or the dental/labial nasal (aMs)?",
        "anusvara | nasal-letter | n.a. (no verb roots)"),
    6: ("ṛkārānta words (ṛ-final agent nouns)",
        "How is an ṛ-stem agent noun (kartṛ) cited — bare stem (SLP1 kartf), "
        "nominative (kartA), or with -ar/-ṛ (kartar/kartR)?",
        "stem-f | nominative-A | ar/R"),
    7: ("vas/yas suffixes (perfect ppl. -vas, comparative -yas)",
        "How are -vas (perfect participle) and -yas (comparative) stems cited / spelled?",
        "see Patel 2016 — assign from -vas / -yas examples"),
}
DIMS = [1, 3, 5, 6, 7]


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


def evidence(path):
    hws = list(iter_k1(path, CAP))
    ev = {}

    # dim 1 — anusvara vs homorganic nasal before a stop
    anu = homo = 0
    anu_ex, homo_ex = [], []
    for hw in hws:
        for i in range(len(hw) - 1):
            if hw[i] == "M" and hw[i + 1] in STOPS:
                anu += 1
                if len(anu_ex) < 8:
                    anu_ex.append(hw)
                break
        for nas, varga in HOMORGANIC:
            if re.search(nas + "[" + varga + "]", hw):
                homo += 1
                if len(homo_ex) < 8:
                    homo_ex.append(hw)
                break
    tot = anu + homo
    ev[1] = {"anusvara_share": round(anu / tot, 3) if tot else None,
             "n_anusvara": anu, "n_homorganic": homo,
             "ex_anusvara": take(set(), anu_ex), "ex_homorganic": take(set(), homo_ex)}

    # dim 3 — -at / -vat / -mat endings
    at = [h for h in hws if h.endswith("at") and not h.endswith("vat") and not h.endswith("mat")]
    vat = [h for h in hws if h.endswith("vat")]
    mat = [h for h in hws if h.endswith("mat")]
    ev[3] = {"n_at": len(at), "n_vat": len(vat), "n_mat": len(mat),
             "ex_at": take(set(), at), "ex_vat": take(set(), vat), "ex_mat": take(set(), mat)}

    # dim 5 — verbal roots with nasal: anusvara (aMS/aMh) vs nasal-letter (aMs)
    # heuristic: short headwords (≤4 chars) containing a nasal+consonant or ending nasal
    roots = [h for h in hws if len(h) <= 4 and re.search(r"[MmnN]", h)]
    anu_r = [h for h in roots if "M" in h]
    nas_r = [h for h in roots if "M" not in h and re.search(r"[mn]", h)]
    ev[5] = {"n_short_nasal_roots": len(roots),
             "ex_anusvara_root": take(set(), anu_r), "ex_nasal_root": take(set(), nas_r)}

    # dim 6 — ṛ-final agent nouns: bare stem (f), nominative (A after consonant), ar/R
    f_stem = [h for h in hws if h.endswith("f")]
    # nominative -tA / consonant+A that looks like an agent noun
    nomA = [h for h in hws if re.search(r"t[AR]$", h)]
    ar_end = [h for h in hws if h.endswith("ar") or h.endswith("tR")]
    ev[6] = {"n_f_stem": len(f_stem), "n_nomA": len(nomA), "n_ar": len(ar_end),
             "ex_stem_f": take(set(), f_stem), "ex_nomA": take(set(), nomA),
             "ex_ar": take(set(), ar_end)}

    # dim 7 — -vas / -yas suffixes
    vas = [h for h in hws if h.endswith("vas")]
    yas = [h for h in hws if h.endswith("yas")]
    ev[7] = {"n_vas": len(vas), "n_yas": len(yas),
             "ex_vas": take(set(), vas), "ex_yas": take(set(), yas)}

    ev["_n_headwords"] = len(hws)
    return ev


def summary_cell(dim, e):
    """One compact human-readable evidence string per (dict, dim)."""
    if dim == 1:
        s = e[1]
        sh = s["anusvara_share"]
        return (f"anusvāra-share={sh} (M+stop {s['n_anusvara']} vs homorganic {s['n_homorganic']})"
                if sh is not None else "no nasal+stop headwords")
    if dim == 3:
        s = e[3]
        return f"-at {s['n_at']}, -vat {s['n_vat']}, -mat {s['n_mat']}"
    if dim == 5:
        s = e[5]
        return f"short nasal roots {s['n_short_nasal_roots']} (M-form {len(s['ex_anusvara_root'])}+, n/m-form {len(s['ex_nasal_root'])}+)"
    if dim == 6:
        s = e[6]
        return f"ṛ-stem(f) {s['n_f_stem']}, nom-A {s['n_nomA']}, -ar/-R {s['n_ar']}"
    if dim == 7:
        s = e[7]
        return f"-vas {s['n_vas']}, -yas {s['n_yas']}"
    return ""


def examples_cell(dim, e):
    if dim == 1:
        return f"M: {' '.join(e[1]['ex_anusvara'][:4])}  ||  homorg: {' '.join(e[1]['ex_homorganic'][:4])}"
    if dim == 3:
        return (f"-at: {' '.join(e[3]['ex_at'][:3])}  |  -vat: {' '.join(e[3]['ex_vat'][:3])}  "
                f"|  -mat: {' '.join(e[3]['ex_mat'][:3])}")
    if dim == 5:
        return f"M-root: {' '.join(e[5]['ex_anusvara_root'][:4])}  ||  n/m-root: {' '.join(e[5]['ex_nasal_root'][:4])}"
    if dim == 6:
        return (f"stem-f: {' '.join(e[6]['ex_stem_f'][:3])}  |  nom-A: {' '.join(e[6]['ex_nomA'][:3])}  "
                f"|  -ar/R: {' '.join(e[6]['ex_ar'][:3])}")
    if dim == 7:
        return f"-vas: {' '.join(e[7]['ex_vas'][:4])}  ||  -yas: {' '.join(e[7]['ex_yas'][:4])}"
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
              f"anu1={all_ev[code][1]['anusvara_share']}  "
              f"-at={e[3]['n_at']}/-vat={e[3]['n_vat']}  f={e[6]['n_f_stem']}  "
              f"vas={e[7]['n_vas']}/yas={e[7]['n_yas']}")

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
    except Exception as e:
        print(f"Provenance error: {e}")


if __name__ == "__main__":
    main()
