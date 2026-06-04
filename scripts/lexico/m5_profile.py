"""Phase L0.6 / M5 — unified per-lemma microstructure profile (the m1–m4 join).

The integrative deliverable the four extractors were building toward (issue #30,
decision round 1). Joins the per-entry outputs of m1 (derivative subentries),
m2 (preverb subentries), m3 (cross-references, folded to out-degree) and m4
(indigenous roots) on the entry key `(dict, L)` into ONE table — a row wherever
ANY layer fires — over all 43 dicts (decision round 2 #6). Also emits an aggregate
per-dict "microstructure fingerprint".

m3 is edge data (one row per cross-ref); it is folded to `xref_out` = the number of
cross-references the entry MAKES (out-degree). In-degree / hub targets are corpus-level
and live in m3's own report, not in a per-lemma row.

Deterministic, no deps. Reads the four CSVs already in data/lexico/ (run m1–m4 first):
    python scripts/lexico/m5_profile.py
Outputs (data/lexico/):
    microstructure_profile.csv       one row per (dict, L) with any microstructure signal
    microstructure_fingerprint.json  per-dict densities + dominant layer
"""

import os
import sys
import csv
import json
import collections

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

DATA = "data/lexico"
csv.field_size_limit(10_000_000)

# m1 columns carried into the profile (the category counts + shape).
M1_CAT = ["n_caus", "n_pass", "n_desid", "n_intens", "n_den", "n_periphr", "n_comp"]
M1_COLS = ["is_verbal", "n_subentries", "subentry_categories", *M1_CAT, "max_depth"]
M4_COLS = ["root_signal", "gana", "pada", "transitivity", "causative", "set", "anit", "vet"]

PROFILE_FIELDS = (
    ["dict", "L", "k1", "layers"]
    + M1_COLS
    + ["n_preverb_sub", "preverbs"]
    + ["xref_out"]
    + ["is_root"] + M4_COLS
)


def load_csv(name):
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        print(f"  (missing {name} — run its extractor first)", file=sys.stderr)
        return []
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    print("=" * 64)
    print("M5 — unified per-lemma microstructure profile (m1–m4 join)")
    print("=" * 64)

    m1 = load_csv("microstructure_subentries.csv")
    m2 = load_csv("preverb_subentries.csv")
    m3 = load_csv("xref_edges.csv")
    m4 = load_csv("indigenous_roots.csv")

    # Merge on (dict, L). Each row is a dict of profile fields; `layers` tracks which
    # extractors fired so the table is filterable (sub | preverb | xref | root).
    prof = {}

    def row(dic, L, k1):
        key = (dic, L)
        r = prof.get(key)
        if r is None:
            r = {f: "" for f in PROFILE_FIELDS}
            r["dict"], r["L"], r["k1"] = dic, L, k1
            r["layers"] = set()
            r["xref_out"] = 0
            r["is_root"] = 0
            prof[key] = r
        elif k1 and not r["k1"]:
            r["k1"] = k1
        return r

    for s in m1:
        r = row(s["dict"], s["L"], s.get("k1", ""))
        r["layers"].add("sub")
        for c in M1_COLS:
            r[c] = s[c]
    for s in m2:
        r = row(s["dict"], s["L"], s.get("k1", ""))
        r["layers"].add("preverb")
        r["n_preverb_sub"] = s["n_preverb_sub"]
        r["preverbs"] = s["preverbs"]
    for s in m3:                               # edges → out-degree
        r = row(s["dict"], s["L"], s.get("k1", ""))
        r["layers"].add("xref")
        r["xref_out"] += 1
    for s in m4:
        r = row(s["dict"], s["L"], s.get("k1", ""))
        r["layers"].add("root")
        r["is_root"] = 1
        for c in M4_COLS:
            r[c] = s[c]

    rows = sorted(prof.values(), key=lambda r: (r["dict"], int(r["L"]) if r["L"].isdigit() else 0))
    for r in rows:
        r["layers"] = "|".join(sorted(r["layers"]))

    csv_path = os.path.join(DATA, "microstructure_profile.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=PROFILE_FIELDS)
        w.writeheader()
        w.writerows(rows)

    # --- per-dict fingerprint -------------------------------------------------
    # Denominator = entries scanned by m1 (it scanned every dict).
    m1_agg = {}
    p = os.path.join(DATA, "microstructure_by_dict.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            m1_agg = json.load(f).get("dicts", {})

    fp = {}
    for r in rows:
        d = fp.setdefault(r["dict"], collections.Counter())
        if "sub" in r["layers"]:
            d["sub_entries"] += 1
            d["sub_markers"] += int(r["n_subentries"] or 0)
        if "preverb" in r["layers"]:
            d["preverb_entries"] += 1
            d["preverb_total"] += int(r["n_preverb_sub"] or 0)
        if "xref" in r["layers"]:
            d["xref_entries"] += 1
            d["xref_edges"] += int(r["xref_out"] or 0)
        if "root" in r["layers"]:
            d["root_entries"] += 1
            for c in ("pada", "gana", "transitivity", "vet"):
                if r[c] not in ("", "0"):
                    d["root_" + c] += 1

    fingerprint = {}
    for code in sorted(set(list(fp) + list(m1_agg))):
        d = fp.get(code, collections.Counter())
        scanned = m1_agg.get(code, {}).get("entries_scanned", 0)
        layers_present = [name for name, key in
                          (("subentry", "sub_entries"), ("preverb", "preverb_entries"),
                           ("xref", "xref_entries"), ("root", "root_entries")) if d[key]]
        dominant = max(layers_present,
                       key=lambda n: d[{"subentry": "sub_entries", "preverb": "preverb_entries",
                                        "xref": "xref_entries", "root": "root_entries"}[n]],
                       default="")
        fingerprint[code] = {
            "entries_scanned": scanned,
            "subentry": {"entries": d["sub_entries"], "markers": d["sub_markers"],
                         "per_1k_entries": round(1000 * d["sub_entries"] / scanned, 2) if scanned else 0},
            "preverb": {"entries": d["preverb_entries"], "total": d["preverb_total"]},
            "xref": {"entries": d["xref_entries"], "edges": d["xref_edges"]},
            "root": {"entries": d["root_entries"], "pada": d["root_pada"], "gana": d["root_gana"],
                     "transitivity": d["root_transitivity"], "vet": d["root_vet"]},
            "layers_present": layers_present,
            "dominant_layer": dominant,
        }

    fp_path = os.path.join(DATA, "microstructure_fingerprint.json")
    with open(fp_path, "w", encoding="utf-8") as f:
        json.dump({"dicts": fingerprint}, f, indent=2, ensure_ascii=False)

    n_dicts = sum(1 for v in fingerprint.values() if v["layers_present"])
    print(f"  profile rows: {len(rows):,}  over {n_dicts} dicts with any microstructure signal")
    print(f"  layer coverage (entries): "
          + ", ".join(f"{name} {sum(1 for r in rows if name in r['layers']):,}"
                      for name in ("sub", "preverb", "xref", "root")))
    print("\n  per-dict fingerprint (dicts with the richest microstructure):")
    top = sorted(fingerprint.items(),
                 key=lambda kv: kv[1]["subentry"]["entries"] + kv[1]["root"]["entries"]
                 + kv[1]["xref"]["entries"] + kv[1]["preverb"]["entries"], reverse=True)[:10]
    for code, v in top:
        print(f"    {code:6s} scanned={v['entries_scanned']:>7,} "
              f"sub={v['subentry']['entries']:>6,} prev={v['preverb']['entries']:>5,} "
              f"xref={v['xref']['entries']:>6,} root={v['root']['entries']:>5,}  "
              f"dominant={v['dominant_layer']}")
    print(f"\nWrote {csv_path} ({len(rows):,} rows), {os.path.basename(fp_path)}")

    try:
        sys.path.insert(0, os.path.abspath("scripts/L0"))
        from _provenance import write_source
        write_source(csv_path, "m5_profile.py", 6)
    except Exception as e:
        print(f"Provenance error: {e}")


if __name__ == "__main__":
    main()
