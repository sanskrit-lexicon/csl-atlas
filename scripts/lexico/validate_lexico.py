"""Phase L0.6 — validator for the lexico microstructure outputs (m1, m2).

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


def main():
    print("Validating data/lexico/ …")
    m1_rows, m1_dicts = validate_m1()
    m2_rows, m2_dicts = validate_m2()
    m3_rows, m3_dicts = validate_m3()
    print(f"  m1: {m1_rows:,} rows / {m1_dicts} dicts")
    print(f"  m2: {m2_rows:,} rows / {m2_dicts} preverb dicts")
    print(f"  m3: {m3_rows:,} rows / {m3_dicts} xref dicts")
    if _fail:
        print(f"\nFAIL — {len(_fail)} check(s):", file=sys.stderr)
        for m in _fail[:25]:
            print(f"  - {m}", file=sys.stderr)
        sys.exit(1)
    print("OK — all consistency checks pass.")


if __name__ == "__main__":
    main()
