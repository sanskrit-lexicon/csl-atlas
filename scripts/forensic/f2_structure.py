"""Phase L3 / F2 — homonym-split concordance + raw-headword anomaly pool.

Two structural / orthographic copy signals on the RAW csl-orig layer:

(a) HOMONYM-SPLIT CONCORDANCE (the clean structural signal). Splitting a headword
    into numbered homonyms (<h>1, <h>2, …) is an editorial decision. If MW divides a
    headword into the same number of homonyms as Böhtlingk does — especially the rare
    3+ splits — that is structural inheritance. Language-neutral, and it covers MW72
    (which has <h> but no citations, so F1 skipped it). Calibrated against unrelated
    dicts that also carry homonyms (the null).

(b) RAW-HEADWORD anomaly pool. Raw <k1> preserves spelling that hwnorm1 later
    normalizes away, so genuine shared misspellings/ghost-words can survive here. We
    list raw headwords shared by exactly {MW, one Petersburg dict} among all parsed
    dicts — a CANDIDATE pool. Like F0 this can't by itself separate a true corruption
    from a rare real compound (needs philological eyeballing), so it is offered as a
    triage list, not a verdict.

Reads data/forensic/parsed/<code>.tsv (parse_cslorig.py --all).
Output : data/forensic/homonym_concordance.csv  (pairs: split-agreement),
         data/forensic/raw_headword_pool.csv      (MW+Petersburg exclusive raw k1),
         data/forensic/f2_report.json.
Run from repo root:  python scripts/forensic/f2_structure.py
"""

import os
import sys
import csv
import json
import glob
import collections
import itertools

sys.path.insert(0, os.path.abspath("scripts/forensic"))
from parse_cslorig import load_entries, PARSED_DIR

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

MIN_HOM = 1000     # dict joins the homonym scan if it has >= this many <h> entries
LINEAGE = [("PWG", "MW"), ("PW", "MW"), ("MW72", "MW"), ("PWG", "MW72"), ("PWG", "PW")]
# True structural nulls = index-type works. NB CAE/CCS are NOT nulls — they cluster with
# Petersburg (CAE/CCS 63%, CAE/PW 37%), echoing the L0 Petersburg-formatting family.
NULLS = [("INM", "MW"), ("PUI", "MW"), ("PE", "MW"), ("STC", "MW")]


def hcount_map(code):
    """k1 -> number of distinct homonyms (entries with <h>); unsplit headwords = 1."""
    hs = collections.defaultdict(set)
    seen = set()
    for e in load_entries(code):
        k1 = e["k1"]
        if not k1:
            continue
        seen.add(k1)
        if e["h"]:
            hs[k1].add(e["h"])
    return {k1: (len(hs[k1]) if k1 in hs else 1) for k1 in seen}


def main():
    print("=" * 64)
    print("F2 — homonym-split concordance + raw-headword anomaly pool")
    print("=" * 64)

    stats = json.load(open(os.path.join(PARSED_DIR, "_parse_stats.json"), encoding="utf-8"))
    hom_codes = sorted(s["code"].upper() for s in stats if s["with_homonym"] >= MIN_HOM)
    print(f"\nHomonym-bearing dicts (>= {MIN_HOM} <h>): {', '.join(hom_codes)}")

    hc = {c: hcount_map(c.lower()) for c in hom_codes}

    # ---- (a) pairwise homonym concordance ----
    rows = []
    for a, b in itertools.combinations(hom_codes, 2):
        ha, hb = hc[a], hc[b]
        shared = set(ha) & set(hb)
        split = [k for k in shared if ha[k] >= 2 or hb[k] >= 2]   # at least one dict splits
        if len(split) < 20:
            continue
        agree = sum(1 for k in split if ha[k] == hb[k])
        deep = [k for k in split if ha[k] >= 3 and hb[k] >= 3]
        deep_agree = sum(1 for k in deep if ha[k] == hb[k])
        rows.append({
            "dict_a": a, "dict_b": b, "shared_headwords": len(shared),
            "split_in_either": len(split),
            "agree_on_count": agree,
            "agreement_rate": round(agree / len(split), 4),
            "deep_split_both_3plus": len(deep),
            "deep_agree": deep_agree,
            "deep_agreement_rate": round(deep_agree / len(deep), 4) if deep else 0.0,
        })
    rows.sort(key=lambda r: -r["agreement_rate"])
    with open("data/forensic/homonym_concordance.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["dict_a", "dict_b", "shared_headwords",
                                          "split_in_either", "agree_on_count", "agreement_rate",
                                          "deep_split_both_3plus", "deep_agree", "deep_agreement_rate"])
        w.writeheader()
        w.writerows(rows)

    # ---- (b) raw-headword exclusive pool: k1 in exactly {MW, Petersburg} among all parsed ----
    all_codes = sorted(os.path.basename(p)[:-4] for p in glob.glob(os.path.join(PARSED_DIR, "*.tsv")))
    k1_dicts = collections.defaultdict(set)
    for code in all_codes:
        for e in load_entries(code):
            if e["k1"]:
                k1_dicts[e["k1"]].add(code.upper())
    pool = []
    for k1, ds in k1_dicts.items():
        if len(ds) == 2 and "MW" in ds and ds & {"PWG", "PW"}:
            partner = (ds - {"MW"}).pop()
            pool.append({"raw_k1": k1, "shared_with": partner})
    pool.sort(key=lambda r: (r["shared_with"], r["raw_k1"]))
    with open("data/forensic/raw_headword_pool.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["raw_k1", "shared_with"])
        w.writeheader()
        w.writerows(pool)

    # ---- console ----
    rowmap = {(r["dict_a"], r["dict_b"]): r for r in rows}

    def get(a, b):
        return rowmap.get((a, b)) or rowmap.get((b, a))

    print("\n" + "=" * 64)
    print("Homonym-split agreement: lineage vs unrelated null")
    print("=" * 64)
    print(f"  {'pair':12s} {'split':>7s} {'agree%':>7s} {'deep(3+)':>9s} {'deep_agree%':>11s}")
    for a, b in LINEAGE + NULLS:
        r = get(a, b)
        if not r:
            print(f"  {a + '/' + b:12s}  (insufficient shared splits)")
            continue
        print(f"  {r['dict_a'] + '/' + r['dict_b']:12s} {r['split_in_either']:>7,} "
              f"{r['agreement_rate'] * 100:>6.1f}% {r['deep_split_both_3plus']:>9,} "
              f"{r['deep_agreement_rate'] * 100:>10.1f}%")

    print("\nTop homonym-concordance pairs (agreement rate, >=100 shared splits):")
    for r in [x for x in rows if x["split_in_either"] >= 100][:12]:
        print(f"  {r['dict_a'] + '/' + r['dict_b']:12s} agree={r['agreement_rate'] * 100:.1f}% "
              f"splits={r['split_in_either']:,} deep={r['deep_split_both_3plus']:,}")

    pool_pwg = sum(1 for p in pool if p["shared_with"] == "PWG")
    pool_pw = sum(1 for p in pool if p["shared_with"] == "PW")
    print(f"\nRaw-headword exclusive pool (MW + exactly one Petersburg dict): "
          f"{len(pool):,} (PWG {pool_pwg:,}, PW {pool_pw:,}) — triage in raw_headword_pool.csv")

    report = {
        "min_hom": MIN_HOM, "homonym_dicts": hom_codes,
        "n_pairs": len(rows),
        "lineage": {f"{a}/{b}": get(a, b) for a, b in LINEAGE if get(a, b)},
        "nulls": {f"{a}/{b}": get(a, b) for a, b in NULLS if get(a, b)},
        "top_pairs": [r for r in rows if r["split_in_either"] >= 100][:20],
        "raw_pool_total": len(pool), "raw_pool_pwg": pool_pwg, "raw_pool_pw": pool_pw,
        "interpretation": ("(a) Homonym-split agreement: a structural heir matches the source's "
                           "homonym DIVISIONS, esp. the rare 3+ splits. On deep (3+) splits MW agrees "
                           "with Petersburg 64-77% vs ~32-36% for true index-type nulls (INM/PUI) = "
                           "~2x = structural inheritance. BUT splits are partly linguistically forced "
                           "(any Sanskritist splits a-vowel / a-privative / a-pronoun), so this "
                           "CORROBORATES, weaker than F1 citations. NB CAE/CCS are Petersburg-derived, "
                           "not nulls. (b) raw_headword_pool = CANDIDATE triage (raw k1 shared only by "
                           "MW + one Petersburg dict; PW count ~ the s6 sanhw1 exclusive figure) — "
                           "cannot alone separate a corruption from a rare real compound; needs eyeball."),
    }
    with open("data/forensic/f2_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nWrote homonym_concordance.csv ({len(rows)} pairs), "
          f"raw_headword_pool.csv ({len(pool):,}), f2_report.json")
    try:
        sys.path.insert(0, os.path.abspath("scripts/L0"))
        from _provenance import write_source
        write_source("data/forensic/homonym_concordance.csv", "f2_structure.py", 2)
    except Exception as e:
        print(f"Provenance error: {e}")


if __name__ == "__main__":
    main()
