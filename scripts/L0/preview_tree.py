"""L0 preview tree — first REAL convention cladogram (not the gated Stage 3/4).

The gated Stage 3 preflight requires cells_unknown == 0. We are not there yet.
This is a deliberate preview: it keeps only the 19 informative auto dims and the
32 dicts that have real data (drops KNA/KOW/AMAR, which are all-unknown), uses a
missing-aware Gower distance, and builds UPGMA + NJ trees so we can see whether
the convention fingerprint clusters into the lineages we already know.

Outputs -> data/L0/preview/  (kept apart from data/L0/distances|trees).
"""

import os
import sys
import csv
import json
import numpy as np
from scipy.cluster.hierarchy import linkage, to_tree
from scipy.spatial.distance import squareform

sys.stdout.reconfigure(encoding="utf-8")

OUT = "data/L0/preview"
INFORMATIVE = [9, 10, 11, 12, 13, 14, 17, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
DROP = {"KNA", "KOW", "AMAR"}  # all-unknown (no local source)

# Known lineages to look for in the tree (from prior sanhw1 / inventory findings).
KNOWN_GROUPS = {
    "Wilson lineage (WIL→YAT→SHS)": ["WIL", "YAT", "SHS"],
    "Apte siblings (AP90→AP)": ["AP90", "AP"],
    "Cappeller (CAE/CCS)": ["CAE", "CCS"],
    "Monier-Williams self (MW72→MW)": ["MW72", "MW"],
    "Petersburg/German (PWG/PW/SCH/CCS/GRA/BOP)": ["PWG", "PW", "SCH", "CCS", "GRA", "BOP"],
    "Indigenous Skt-Skt (VCP/SKD)": ["VCP", "SKD"],
}


def load():
    rows = {}
    with open("data/L0/convention_fingerprint.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            code = r["dict"]
            if code in DROP:
                continue
            vec = []
            for d in INFORMATIVE:
                v = r[f"dim_{d}_value"]
                src = r[f"dim_{d}_source"]
                vec.append(v if (src == "auto" and v != "unknown") else None)
            rows[code] = vec
    return list(rows.keys()), rows


def gower(codes, rows):
    """Missing-aware categorical distance: fraction of co-known dims that differ."""
    n = len(codes)
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            a, b = rows[codes[i]], rows[codes[j]]
            common = diff = 0
            for x, y in zip(a, b):
                if x is not None and y is not None:
                    common += 1
                    if x != y:
                        diff += 1
            d = diff / common if common else 1.0
            D[i, j] = D[j, i] = round(d, 4)
    return D


def jaccard(codes, rows):
    """Set-membership Jaccard over 'dim=value' tokens (unknown dims contribute none)."""
    n = len(codes)
    sets = {c: {f"{k}={v}" for k, v in zip(INFORMATIVE, rows[c]) if v is not None}
            for c in codes}
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            A, B = sets[codes[i]], sets[codes[j]]
            u = len(A | B)
            d = 1 - (len(A & B) / u) if u else 1.0
            D[i, j] = D[j, i] = round(d, 4)
    return D


# ---- Newick converters --------------------------------------------------
def linkage_to_newick(Z, labels):
    tree = to_tree(Z, rd=False)

    def recurse(node):
        if node.is_leaf():
            return labels[node.id]
        return f"({recurse(node.get_left())},{recurse(node.get_right())})"

    return recurse(tree) + ";"


def neighbor_joining(D, labels):
    """Saitou–Nei NJ. Returns a Newick string (unrooted)."""
    D = D.astype(float).copy()
    nodes = list(labels)
    active = list(range(len(labels)))
    n_orig = len(labels)
    nwk = {i: labels[i] for i in range(n_orig)}
    next_id = n_orig
    # work on a dict-of-dict distance keyed by node id
    dist = {i: {} for i in active}
    for i in active:
        for j in active:
            if i != j:
                dist[i][j] = D[i, j]

    while len(active) > 2:
        m = len(active)
        r = {i: sum(dist[i][k] for k in active if k != i) for i in active}
        # Q-matrix; pick min
        best, bi, bj = None, None, None
        for ii in range(m):
            for jj in range(ii + 1, m):
                i, j = active[ii], active[jj]
                q = (m - 2) * dist[i][j] - r[i] - r[j]
                if best is None or q < best:
                    best, bi, bj = q, i, j
        i, j = bi, bj
        dij = dist[i][j]
        li = 0.5 * dij + (r[i] - r[j]) / (2 * (m - 2)) if m > 2 else 0.5 * dij
        lj = dij - li
        li, lj = max(li, 0.0), max(lj, 0.0)
        u = next_id
        next_id += 1
        nwk[u] = f"({nwk[i]}:{li:.4f},{nwk[j]}:{lj:.4f})"
        dist[u] = {}
        for k in active:
            if k in (i, j):
                continue
            dku = 0.5 * (dist[i][k] + dist[j][k] - dij)
            dist[u][k] = dku
            dist[k][u] = dku
        active = [a for a in active if a not in (i, j)] + [u]

    a, b = active
    return f"({nwk[a]}:{dist[a][b]/2:.4f},{nwk[b]}:{dist[a][b]/2:.4f});"


# ---- ASCII dendrogram ---------------------------------------------------
def ascii_tree(Z, labels):
    tree = to_tree(Z, rd=False)
    lines = []

    def rec(node, prefix, is_last):
        conn = "└─ " if is_last else "├─ "
        if node.is_leaf():
            lines.append(prefix + conn + labels[node.id])
        else:
            lines.append(prefix + conn + f"┐ {node.dist:.3f}")
            child = prefix + ("   " if is_last else "│  ")
            rec(node.get_left(), child, False)
            rec(node.get_right(), child, True)

    rec(tree, "", True)
    return "\n".join(lines)


def png(Z, labels, path, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from scipy.cluster.hierarchy import dendrogram
    fig, ax = plt.subplots(figsize=(7, 9))
    dendrogram(Z, labels=labels, orientation="right", ax=ax, color_threshold=0.6)
    ax.set_title(title)
    ax.set_xlabel("convention distance")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def nearest_neighbours(codes, D):
    nn = {}
    for i, c in enumerate(codes):
        order = np.argsort(D[i])
        for j in order:
            if j != i:
                nn[c] = (codes[j], round(float(D[i, j]), 4))
                break
    return nn


def main():
    os.makedirs(OUT, exist_ok=True)
    codes, rows = load()
    print(f"Preview over {len(codes)} dicts × {len(INFORMATIVE)} informative dims.\n")

    matrices = {"gower": gower(codes, rows), "jaccard": jaccard(codes, rows)}

    for name, D in matrices.items():
        # save matrix
        with open(f"{OUT}/dist_{name}.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow([""] + codes)
            for i, c in enumerate(codes):
                w.writerow([c] + [f"{x:.4f}" for x in D[i]])
        Z = linkage(squareform(D, checks=False), method="average")  # UPGMA
        with open(f"{OUT}/upgma_{name}.newick", "w", encoding="utf-8") as f:
            f.write(linkage_to_newick(Z, codes) + "\n")
        with open(f"{OUT}/nj_{name}.newick", "w", encoding="utf-8") as f:
            f.write(neighbor_joining(D, codes) + "\n")
        png(Z, codes, f"{OUT}/upgma_{name}.png", f"UPGMA · {name} · 19 conv. dims · 32 dicts")

    # headline: print Gower UPGMA ASCII tree
    Zg = linkage(squareform(matrices["gower"], checks=False), method="average")
    print("UPGMA tree (Gower distance over 19 convention dims):\n")
    print(ascii_tree(Zg, codes))

    # nearest-neighbour validation
    nn = nearest_neighbours(codes, matrices["gower"])
    print("\nNearest convention-neighbour per dict (Gower):")
    for c in codes:
        print(f"  {c:5s} -> {nn[c][0]:5s}  d={nn[c][1]}")

    # known-group cohesion check
    print("\nKnown-lineage cohesion (mean within-group Gower vs global mean):")
    idx = {c: i for i, c in enumerate(codes)}
    gmean = matrices["gower"][np.triu_indices(len(codes), 1)].mean()
    group_report = {}
    for label, members in KNOWN_GROUPS.items():
        present = [m for m in members if m in idx]
        if len(present) < 2:
            continue
        ds = [matrices["gower"][idx[a], idx[b]]
              for x, a in enumerate(present) for b in present[x + 1:]]
        mean_in = float(np.mean(ds))
        group_report[label] = {"members_present": present,
                               "mean_within": round(mean_in, 4),
                               "tighter_than_global": bool(mean_in < gmean)}
        flag = "✓ tighter" if mean_in < gmean else "✗ looser"
        print(f"  {flag:10s} {mean_in:.3f}  {label}  {present}")
    print(f"\n  (global mean pairwise Gower = {gmean:.3f})")

    summary = {
        "n_dicts": len(codes), "dims_used": INFORMATIVE, "dropped": sorted(DROP),
        "global_mean_gower": round(float(gmean), 4),
        "nearest_neighbours": {c: nn[c] for c in codes},
        "known_group_cohesion": group_report,
        "note": "PREVIEW only — not gated Stage 3/4; built on 19 informative dims with missing-aware Gower.",
    }
    with open(f"{OUT}/preview_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from _provenance import write_source
        write_source(f"{OUT}/dist_gower.csv", "preview_tree.py", 34)
    except Exception as e:
        print(f"Provenance error: {e}")

    print(f"\nWrote: {OUT}/  (dist_*.csv, upgma_*.newick, nj_*.newick, upgma_*.png, preview_summary.json)")


if __name__ == "__main__":
    main()
