"""Stage 4 (Phase L0.7) — the content↔convention reformatting residual.

Operationalises the L0 finding (L0_RESULTS §3, Paper H §5) as a quantitative
instrument. Two descent axes:

  content     — shared lexicon: sanhw1 headword containment / Jaccard
  convention  — shared house style: the L0 convention-fingerprint distance

For a directed pair A→B,
  reformatting_residual(A→B) = content_containment(A→B) − convention_similarity(A,B)
where convention_similarity = 1 − convention_distance (B_whamming, undirected).

A HIGH positive residual = "absorbed the lexicon, recoded the house style" — the
quantitative signature of an editorial reformatting (predicts PWG→MW, MW72→MW).
A LOW/zero residual = faithful in both content and form (PWG→PW, WIL→SHS).

Inputs : data/sanhw1_inheritance_edges.csv (directed containment),
         data/sanhw1_distance_matrix.csv (Jaccard, for the undirected scatter),
         data/L0/distances/B_whamming.csv (convention distance).
Outputs: data/L0/content_convention_residual.csv (ranked directed edges),
         data/L0/content_convention_scatter.csv (every shared pair: 2 axes),
         data/L0/residual_report.json.
"""

import os
import sys
import csv
import json

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def load_matrix(path):
    """Symmetric distance matrix CSV → {(a,b): dist}, plus the code list."""
    with open(path, encoding="utf-8") as f:
        rows = list(csv.reader(f))
    header = rows[0][1:]
    D = {}
    for r in rows[1:]:
        a = r[0]
        for b, v in zip(header, r[1:]):
            if v not in ("", "n/a"):
                try:
                    D[(a, b)] = float(v)
                except ValueError:
                    pass
    return D, header


def main():
    conv_dist, conv_codes = load_matrix("data/L0/distances/B_whamming.csv")
    cont_dist, cont_codes = load_matrix("data/sanhw1_distance_matrix.csv")
    conv_set = set(conv_codes)
    shared = [c for c in cont_codes if c in conv_set]
    print(f"convention dicts: {len(conv_codes)} · content dicts: {len(cont_codes)} · "
          f"shared: {len(shared)}")

    def conv_sim(a, b):
        d = conv_dist.get((a, b), conv_dist.get((b, a)))
        return None if d is None else 1 - d

    # ---- directed residual on the known containment edges ----
    edges = []
    with open("data/sanhw1_inheritance_edges.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            a, b = r["source"], r["inheritor"]
            if a not in conv_set or b not in conv_set:
                continue
            cs = conv_sim(a, b)
            if cs is None:
                continue
            cont = float(r["containment"])
            edges.append({
                "source": a, "inheritor": b,
                "content_containment": round(cont, 4),
                "convention_similarity": round(cs, 4),
                "convention_distance": round(1 - cs, 4),
                "reformatting_residual": round(cont - cs, 4),
                "source_year": r["source_year"], "inheritor_year": r["inheritor_year"],
                "temporal_plausible": r["temporal_plausible"],
            })
    edges.sort(key=lambda e: -e["reformatting_residual"])

    with open("data/L0/content_convention_residual.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["source", "inheritor", "content_containment",
                                          "convention_similarity", "convention_distance",
                                          "reformatting_residual", "source_year",
                                          "inheritor_year", "temporal_plausible"])
        w.writeheader()
        w.writerows(edges)

    # ---- undirected two-axis scatter over every shared pair ----
    scatter = []
    for i, a in enumerate(shared):
        for b in shared[i + 1:]:
            cd = cont_dist.get((a, b), cont_dist.get((b, a)))
            cv = conv_sim(a, b)
            if cd is None or cv is None:
                continue
            scatter.append({"a": a, "b": b,
                            "content_similarity": round(1 - cd, 4),
                            "convention_similarity": round(cv, 4),
                            "gap": round((1 - cd) - cv, 4)})
    scatter.sort(key=lambda s: -s["gap"])
    with open("data/L0/content_convention_scatter.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["a", "b", "content_similarity",
                                          "convention_similarity", "gap"])
        w.writeheader()
        w.writerows(scatter)

    # ---- report + console ----
    top_reformat = edges[:6]
    faithful = sorted(edges, key=lambda e: e["reformatting_residual"])[:6]
    report = {
        "n_shared_dicts": len(shared), "shared_dicts": shared,
        "n_directed_edges": len(edges), "n_scatter_pairs": len(scatter),
        "top_reformatting_edges": [{"edge": f"{e['source']}→{e['inheritor']}",
                                    "residual": e["reformatting_residual"],
                                    "containment": e["content_containment"],
                                    "conv_sim": e["convention_similarity"]} for e in top_reformat],
        "most_faithful_edges": [{"edge": f"{e['source']}→{e['inheritor']}",
                                 "residual": e["reformatting_residual"],
                                 "containment": e["content_containment"],
                                 "conv_sim": e["convention_similarity"]} for e in faithful],
        "interpretation": ("High residual = absorbed lexicon but recoded house style "
                           "(editorial reformatting); low residual = faithful in content + form."),
    }
    with open("data/L0/residual_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nDirected edges scored: {len(edges)} · scatter pairs: {len(scatter)}\n")
    print("TOP reformatting events (high content, recoded conventions):")
    print(f"  {'edge':16s} {'residual':>9s} {'containmt':>10s} {'conv_sim':>9s}")
    for e in top_reformat:
        print(f"  {e['source']+'→'+e['inheritor']:16s} {e['reformatting_residual']:>9.3f} "
              f"{e['content_containment']:>10.3f} {e['convention_similarity']:>9.3f}")
    print("\nMOST faithful (content + form both inherited):")
    for e in faithful:
        print(f"  {e['source']+'→'+e['inheritor']:16s} {e['reformatting_residual']:>9.3f} "
              f"{e['content_containment']:>10.3f} {e['convention_similarity']:>9.3f}")

    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from _provenance import write_source
        write_source("data/L0/content_convention_residual.csv", "s4_residual.py", 4)
    except Exception as e:
        print(f"Provenance error: {e}")


if __name__ == "__main__":
    main()
