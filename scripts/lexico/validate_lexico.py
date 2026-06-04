"""Phase L0.6 — validator for the lexico microstructure outputs (m1–m5).

Data-driven consistency checks (no deps), in the spirit of the project's
validate-*.mjs. Asserts the per-entry CSVs agree with their per-dict aggregates
and that each row's internal invariants hold. Run after m1/m2:

    python scripts/lexico/validate_lexico.py      # exits non-zero on any failure
"""

import os
import sys
import csv
import json
import collections

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

DATA = "data/lexico"
CATS = ["caus", "pass", "desid", "intens", "den", "periphr", "comp"]
_fail = []


def check(cond, msg):
    if not cond:
        _fail.append(msg)


def load_csv(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_json(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


def validate_m1():
    rows = load_csv("microstructure_subentries.csv")
    agg = load_json("microstructure_by_dict.json")["dicts"]
    per_dict_markers = collections.Counter()
    per_dict_rows = collections.Counter()
    for i, r in enumerate(rows):
        n = int(r["n_subentries"])
        catsum = sum(int(r[f"n_{c}"]) for c in CATS)
        present = {c for c in CATS if int(r[f"n_{c}"]) > 0}
        labelled = set(filter(None, r["subentry_categories"].split(",")))
        check(n >= 1, f"m1 row {i} ({r['dict']} L{r['L']}): n_subentries={n} not >=1")
        check(catsum >= n, f"m1 row {i}: sum(per-cat)={catsum} < n_subentries={n}")
        check(present == labelled, f"m1 row {i}: categories {labelled} != per-cat>0 {present}")
        check(r["is_verbal"] in ("0", "1"), f"m1 row {i}: is_verbal={r['is_verbal']}")
        check(int(r["max_depth"]) in (0, 1, 2), f"m1 row {i}: max_depth={r['max_depth']}")
        check(int(r["total_chars_subentries"]) >= 0, f"m1 row {i}: neg total_chars")
        per_dict_markers[r["dict"]] += n
        per_dict_rows[r["dict"]] += 1
    for code, a in agg.items():
        check(per_dict_markers[code] == a["subentry_markers_total"],
              f"m1 {code}: CSV markers {per_dict_markers[code]} != aggregate {a['subentry_markers_total']}")
        check(per_dict_rows[code] == a["entries_with_subentries"],
              f"m1 {code}: CSV rows {per_dict_rows[code]} != aggregate with_sub {a['entries_with_subentries']}")
    return len(rows), len(agg)


def validate_m2():
    rows = load_csv("preverb_subentries.csv")
    agg = load_json("preverb_by_dict.json")["dicts"]
    pd_sub = collections.Counter()
    pd_rows = collections.Counter()
    for i, r in enumerate(rows):
        n = int(r["n_preverb_sub"])
        parts = [p for p in r["preverbs"].split("|") if p]
        check(n >= 1, f"m2 row {i}: n_preverb_sub={n} not >=1")
        check(len(parts) == n, f"m2 row {i}: preverbs count {len(parts)} != n_preverb_sub {n}")
        pd_sub[r["dict"]] += n
        pd_rows[r["dict"]] += 1
    for code, a in agg.items():
        check(pd_sub[code] == a["preverb_subentries_total"],
              f"m2 {code}: CSV {pd_sub[code]} != aggregate {a['preverb_subentries_total']}")
        check(pd_rows[code] == a["entries_with_preverb_sub"],
              f"m2 {code}: CSV rows {pd_rows[code]} != aggregate {a['entries_with_preverb_sub']}")
    return len(rows), len([a for a in agg.values() if a["preverb_subentries_total"]])


def validate_m3():
    rows = load_csv("xref_edges.csv")
    agg = load_json("xref_by_dict.json")["dicts"]
    pd_edges = collections.Counter()
    pd_entries = collections.defaultdict(set)
    for i, r in enumerate(rows):
        check(r["kind"] in ("vgl", "cf"), f"m3 row {i}: kind={r['kind']}")
        check(bool(r["target"]), f"m3 row {i}: empty target")
        pd_edges[r["dict"]] += 1
        pd_entries[r["dict"]].add(r["L"])
    for code, a in agg.items():
        check(pd_edges[code] == a["xref_edges"],
              f"m3 {code}: CSV edges {pd_edges[code]} != aggregate {a['xref_edges']}")
        check(len(pd_entries[code]) == a["entries_with_xref"],
              f"m3 {code}: CSV entries {len(pd_entries[code])} != aggregate {a['entries_with_xref']}")
    return len(rows), len(agg)


def validate_m4():
    if not os.path.exists(os.path.join(DATA, "indigenous_roots.csv")):
        return 0, 0  # prototype output optional
    GANA = {"bhvadi", "adadi", "juhotyadi", "divadi", "svadi", "tudadi", "rudhadi",
            "tanadi", "kryadi", "curadi", ""}
    PADA = {"parasmaipada", "atmanepada", "ubhayapada", ""}
    TRANS = {"sakarmaka", "akarmaka", ""}
    rows = load_csv("indigenous_roots.csv")
    agg = load_json("indigenous_by_dict.json")["dicts"]
    pd_rows = collections.Counter()
    pd_feat = collections.defaultdict(collections.Counter)
    pd_cat = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    for i, r in enumerate(rows):
        check(r["root_signal"] in ("citation", "annotation", "both"),
              f"m4 row {i}: root_signal={r['root_signal']}")
        check(r["dhatupatha_source"] in ("kavikalpadruma", "madhaviya", "durgadasa",
                                         "dhatupatha", "(annotation-only)"),
              f"m4 row {i}: source={r['dhatupatha_source']}")
        check(r["gana"] in GANA, f"m4 row {i}: gana={r['gana']}")
        check(r["pada"] in PADA, f"m4 row {i}: pada={r['pada']}")
        check(r["transitivity"] in TRANS, f"m4 row {i}: transitivity={r['transitivity']}")
        for f in ("causative", "set", "anit", "vet"):
            check(r[f] in ("0", "1"), f"m4 row {i}: {f}={r[f]}")
            pd_feat[r["dict"]][f] += int(r[f])
        for col in ("gana", "pada", "transitivity"):
            if r[col]:
                pd_cat[r["dict"]][col][r[col]] += 1
        pd_rows[r["dict"]] += 1
    for code, a in agg.items():
        check(pd_rows[code] == a["root_entries"],
              f"m4 {code}: CSV rows {pd_rows[code]} != aggregate root_entries {a['root_entries']}")
        for f in ("causative", "set", "anit", "vet"):
            check(pd_feat[code][f] == a[f], f"m4 {code}: CSV {f} {pd_feat[code][f]} != aggregate {a[f]}")
        for col in ("gana", "pada", "transitivity"):
            check(dict(pd_cat[code][col]) == a["by_" + col], f"m4 {code}: by_{col} CSV != aggregate")
    return len(rows), len(agg)


def validate_m5():
    """The m1–m4 join must be LOSSLESS: profile keys == union of source keys, and
    folded xref_out totals == m3 edge counts."""
    if not os.path.exists(os.path.join(DATA, "microstructure_profile.csv")):
        return 0, 0
    rows = load_csv("microstructure_profile.csv")
    union = set()
    for name in ("microstructure_subentries.csv", "preverb_subentries.csv",
                 "xref_edges.csv", "indigenous_roots.csv"):
        for r in load_csv(name):
            union.add((r["dict"], r["L"]))
    keys = set()
    prof_xref = collections.Counter()
    for i, r in enumerate(rows):
        keys.add((r["dict"], r["L"]))
        lyr = r["layers"].split("|")
        check(r["layers"] != "", f"m5 row {i}: empty layers")
        check((r["is_root"] == "1") == ("root" in lyr), f"m5 row {i}: is_root/root-layer mismatch")
        check((int(r["xref_out"] or 0) > 0) == ("xref" in lyr), f"m5 row {i}: xref_out/xref-layer mismatch")
        prof_xref[r["dict"]] += int(r["xref_out"] or 0)
    check(keys == union,
          f"m5: profile keys != union of m1–m4 keys (|profile|={len(keys)} |union|={len(union)})")
    m3_edges = collections.Counter(r["dict"] for r in load_csv("xref_edges.csv"))
    for code in m3_edges:
        check(prof_xref[code] == m3_edges[code],
              f"m5 {code}: profile xref_out {prof_xref[code]} != m3 edges {m3_edges[code]}")
    return len(rows), len({k[0] for k in keys})


def main():
    print("Validating data/lexico/ …")
    m1_rows, m1_dicts = validate_m1()
    m2_rows, m2_dicts = validate_m2()
    m3_rows, m3_dicts = validate_m3()
    m4_rows, m4_dicts = validate_m4()
    m5_rows, m5_dicts = validate_m5()
    print(f"  m1: {m1_rows:,} rows / {m1_dicts} dicts")
    print(f"  m2: {m2_rows:,} rows / {m2_dicts} preverb dicts")
    print(f"  m3: {m3_rows:,} rows / {m3_dicts} xref dicts")
    print(f"  m4: {m4_rows:,} rows / {m4_dicts} indigenous-root dicts (prototype)")
    print(f"  m5: {m5_rows:,} rows / {m5_dicts} dicts (unified profile join)")
    if _fail:
        print(f"\nFAIL — {len(_fail)} check(s):", file=sys.stderr)
        for m in _fail[:25]:
            print(f"  - {m}", file=sys.stderr)
        sys.exit(1)
    print("OK — all consistency checks pass.")


if __name__ == "__main__":
    main()
