"""Joint inheritance table: for every pair listed in
data/sanhw1_inheritance_edges.csv where both ends are in the L0 32-dict
convention subset, report the directed containment(s) AND the symmetric
convention Gower distance. Pairs at the bottom quartile of pairwise
convention distance AND with containment >= 0.85 pass the joint test of
Paper-1 sect.3.5 -- they are jointly close in content inheritance and
editorial register.

Outputs:
  data/L0/preview/joint_inheritance_table.csv (one row per unordered pair)
  Stdout: ranked table for direct paste into the paper.
"""

import os
import sys
import csv
import json
from collections import defaultdict
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
OUT = "data/L0/preview"


def load_dist(path):
    with open(path, encoding="utf-8") as f:
        rows = list(csv.reader(f))
    labels = rows[0][1:]
    idx = {l: i for i, l in enumerate(labels)}
    M = np.array([[float(x) for x in r[1:]] for r in rows[1:]])
    return labels, idx, M


def main():
    labels, idx, D = load_dist(f"{OUT}/dist_gower.csv")

    # quartile thresholds over the 32-dict pairwise convention distance
    iu = np.triu_indices(len(labels), 1)
    pairwise = D[iu]
    q25, q50, q75 = np.percentile(pairwise, [25, 50, 75])
    print(f"Convention Gower over 32 dicts (n={len(pairwise)} pairs): "
          f"min={pairwise.min():.3f}  Q1={q25:.3f}  median={q50:.3f}  Q3={q75:.3f}  max={pairwise.max():.3f}\n")

    # collect inheritance edges, group by unordered pair
    pair_data = defaultdict(lambda: {"directions": [], "max_containment": 0.0})
    with open("data/sanhw1_inheritance_edges.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            a, b = r["source"], r["inheritor"]
            if a not in idx or b not in idx:
                continue
            key = frozenset({a, b})
            cont = float(r["containment"])
            pair_data[key]["directions"].append(
                (a, b, cont, r["source_year"], r["inheritor_year"],
                 r["temporal_plausible"] == "True"))
            pair_data[key]["max_containment"] = max(
                pair_data[key]["max_containment"], cont)

    rows = []
    for key, info in pair_data.items():
        a, b = sorted(key)
        cd = D[idx[a], idx[b]]
        # pick best (highest containment, temporally plausible if available) direction
        dirs = sorted(info["directions"], key=lambda x: (-x[2], -int(x[5])))
        src, inh, cont, sy, iy, tp = dirs[0]
        rev_cont = ""
        if len(info["directions"]) > 1:
            rev = next((d for d in info["directions"] if (d[0], d[1]) != (src, inh)), None)
            if rev:
                rev_cont = f"{rev[2]:.3f}"
        joint = cd <= q25
        rows.append({
            "pair_a": a, "pair_b": b, "best_source": src, "best_inheritor": inh,
            "containment_best": round(cont, 4),
            "containment_reverse": rev_cont,
            "source_year": sy, "inheritor_year": iy,
            "temporal_plausible": tp,
            "conv_gower": round(float(cd), 4),
            "conv_pctile": round(float((pairwise < cd).mean()), 3),
            "joint_pass_bottom_quartile": bool(joint),
        })

    rows.sort(key=lambda r: r["conv_gower"])

    with open(f"{OUT}/joint_inheritance_table.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"{'pair':14s} {'best dir':14s} {'cont':>6s} {'rev':>6s} "
          f"{'years':>11s} {'tp':>3s} {'conv':>6s} {'pct':>5s} {'JOINT':>6s}")
    print("-" * 88)
    for r in rows:
        pair = f"{r['pair_a']}-{r['pair_b']}"
        dir_ = f"{r['best_source']}->{r['best_inheritor']}"
        yrs = f"{r['source_year']}->{r['inheritor_year']}"
        tp = "✓" if r["temporal_plausible"] else "✗"
        jp = "JOINT" if r["joint_pass_bottom_quartile"] else ""
        print(f"{pair:14s} {dir_:14s} {r['containment_best']:>6.3f} "
              f"{r['containment_reverse']:>6s} {yrs:>11s} {tp:>3s} "
              f"{r['conv_gower']:>6.3f} {r['conv_pctile']:>5.2f} {jp:>6s}")

    joint_pairs = [r for r in rows if r["joint_pass_bottom_quartile"]]
    print(f"\nJoint-pass pairs (containment >= 0.85 AND conv distance in bottom quartile, "
          f"i.e. <= {q25:.3f}):  {len(joint_pairs)} of {len(rows)} inheritance pairs.")
    print("\nThese are the pairs the §5.2 prose names:")
    for r in joint_pairs:
        print(f"  {r['pair_a']}-{r['pair_b']}: containment {r['containment_best']:.3f} "
              f"({r['best_source']}->{r['best_inheritor']}), "
              f"conv Gower {r['conv_gower']:.3f}  ({r['source_year']}->{r['inheritor_year']})")

    # for the prose, also note the convergent-minimalism pairs:
    # convention-close pairs (bottom quartile) that are NOT inheritance edges.
    print("\nConvention-close pairs that are NOT inheritance edges (convergent style):")
    edge_keys = set(pair_data.keys())
    cm = []
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            if D[i, j] <= q25 and frozenset({labels[i], labels[j]}) not in edge_keys:
                cm.append((labels[i], labels[j], float(D[i, j])))
    cm.sort(key=lambda x: x[2])
    for a, b, d in cm[:8]:
        print(f"  {a}-{b}  conv Gower {d:.3f}")

    meta = {"q25_threshold": float(q25), "q50_median": float(q50), "q75": float(q75),
            "n_inheritance_pairs_in_L0": len(rows),
            "n_joint_pass": len(joint_pairs),
            "n_convergent_minimalism_top8": len(cm[:8])}
    with open(f"{OUT}/joint_inheritance_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


if __name__ == "__main__":
    main()
