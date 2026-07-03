"""Quantify homoplasy: convention-tree (fingerprint) vs lemma-tree (sanhw1 Jaccard
descent signal), over their shared leaves. Produces a tanglegram PNG plus three
congruence metrics:

  1. Mantel r  — Pearson correlation of the two distance matrices + permutation p.
  2. Robinson-Foulds — topological disagreement of the two UPGMA trees, normalised,
     against a label-permutation random baseline.
  3. Tanglegram crossings — Kendall-tau inversions between the two leaf orderings.

Plus per-dict rank displacement: the dictionaries that move most between the two
trees are the homoplasy culprits (expect YAT, STC, ...).

Inputs : data/L0/preview/dist_gower.csv  (convention, 32 dicts)
         data/sanhw1_distance_matrix.csv  (lemma overlap, 41 dicts)
Outputs: data/L0/preview/tanglegram.png + homoplasy_metrics.json + two newicks.
"""

import os
import sys
import csv
import json
import numpy as np
from scipy.cluster.hierarchy import linkage, to_tree, leaves_list
from scipy.spatial.distance import squareform

sys.stdout.reconfigure(encoding="utf-8")
OUT = "data/L0/preview"
RNG = np.random.default_rng(0)


def load_matrix(path):
    with open(path, encoding="utf-8") as f:
        rows = list(csv.reader(f))
    cols = rows[0][1:]
    labels = [r[0] for r in rows[1:]]
    assert cols == labels, f"{path}: header/row labels differ"
    M = np.array([[float(x) for x in r[1:]] for r in rows[1:]])
    return labels, M


def subset(labels, M, keep):
    idx = [labels.index(k) for k in keep]
    return M[np.ix_(idx, idx)]


def upgma(M):
    return linkage(squareform(M, checks=False), method="average")


def newick(Z, labels):
    t = to_tree(Z, rd=False)

    def rec(n):
        if n.is_leaf():
            return labels[n.id]
        return f"({rec(n.get_left())},{rec(n.get_right())})"

    return rec(t) + ";"


def clade_set(Z, labels):
    """Set of non-trivial clades (frozensets of labels) for an UPGMA tree."""
    t = to_tree(Z, rd=False)
    clades = set()

    def rec(n):
        if n.is_leaf():
            return frozenset([labels[n.id]])
        s = rec(n.get_left()) | rec(n.get_right())
        if 1 < len(s) < len(labels):
            clades.add(s)
        return s

    rec(t)
    return clades


def rf(Za, Zb, labels):
    A, B = clade_set(Za, labels), clade_set(Zb, labels)
    return len(A ^ B)


def mantel(Da, Db, perms=999):
    iu = np.triu_indices(len(Da), 1)
    a, b = Da[iu], Db[iu]
    r = float(np.corrcoef(a, b)[0, 1])
    n = len(Da)
    count = 0
    for _ in range(perms):
        p = RNG.permutation(n)
        bp = Db[np.ix_(p, p)][iu]
        if abs(np.corrcoef(a, bp)[0, 1]) >= abs(r):
            count += 1
    return r, (count + 1) / (perms + 1)


def kendall_crossings(rank_a, rank_b, labels):
    order = sorted(labels, key=lambda l: rank_a[l])
    seq = [rank_b[l] for l in order]
    inv = sum(1 for i in range(len(seq)) for j in range(i + 1, len(seq)) if seq[i] > seq[j])
    return inv


# ---- tanglegram drawing -------------------------------------------------
def draw_tree(ax, Z, labels, ypos, x_root, x_tip):
    t = to_tree(Z, rd=False)
    maxd = t.dist or 1.0
    sign = 1 if x_tip > x_root else -1
    span = abs(x_tip - x_root)

    def x_of(dist):
        return x_tip - sign * (dist / maxd) * span

    def rec(n):
        if n.is_leaf():
            return ypos[labels[n.id]], x_tip
        yL, xL = rec(n.get_left())
        yR, xR = rec(n.get_right())
        xn = x_of(n.dist)
        ax.plot([xL, xn], [yL, yL], color="0.35", lw=0.8)
        ax.plot([xR, xn], [yR, yR], color="0.35", lw=0.8)
        ax.plot([xn, xn], [yL, yR], color="0.35", lw=0.8)
        return (yL + yR) / 2, xn

    rec(t)


def tanglegram(labels, Zc, Zl, rank_c, rank_l, disp, path, metrics):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = len(labels)
    fig, ax = plt.subplots(figsize=(9, 0.34 * n + 1.5))
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-1, n)
    ax.axis("off")

    yc = {l: rank_c[l] for l in labels}
    yl = {l: rank_l[l] for l in labels}
    draw_tree(ax, Zc, labels, yc, x_root=0.0, x_tip=4.0)
    draw_tree(ax, Zl, labels, yl, x_root=10.0, x_tip=6.0)

    dmax = max(disp.values()) or 1
    for l in labels:
        d = disp[l]
        col = plt.cm.Reds(0.35 + 0.65 * d / dmax) if d > 0 else "0.7"
        lw = 0.8 + 2.0 * d / dmax
        ax.plot([4.0, 6.0], [yc[l], yl[l]], color=col, lw=lw, alpha=0.8, zorder=1)
    for l in labels:
        ax.text(4.0, yc[l], l, ha="right", va="center", fontsize=7,
                bbox=dict(fc="white", ec="none", pad=0.4), zorder=3)
        ax.text(6.0, yl[l], l, ha="left", va="center", fontsize=7,
                bbox=dict(fc="white", ec="none", pad=0.4), zorder=3)

    ax.text(2.0, n - 0.2, "CONVENTION fingerprint\n(UPGMA · Gower · 19 dims)",
            ha="center", va="bottom", fontsize=8, weight="bold")
    ax.text(8.0, n - 0.2, "LEMMA overlap\n(UPGMA · sanhw1 Jaccard)",
            ha="center", va="bottom", fontsize=8, weight="bold")
    ax.set_title(
        f"Convention vs descent — {n} dicts   |   Mantel r={metrics['mantel_r']:.2f} "
        f"(p={metrics['mantel_p']:.3f})   RF={metrics['rf']}/{metrics['rf_max']} "
        f"(norm {metrics['rf_norm']:.2f}; random {metrics['rf_random_mean']:.0f})   "
        f"crossings={metrics['crossings']}", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def main():
    cl, Mc = load_matrix(f"{OUT}/dist_gower.csv")
    ll, Ml = load_matrix("data/sanhw1_distance_matrix.csv")
    common = [c for c in cl if c in set(ll)]
    print(f"convention dicts={len(cl)}  lemma dicts={len(ll)}  common={len(common)}")
    print(f"common: {common}")

    Dc = subset(cl, Mc, common)
    Dl = subset(ll, Ml, common)
    Zc, Zl = upgma(Dc), upgma(Dl)
    labels = common

    rank_c = {labels[i]: int(p) for p, i in enumerate(leaves_list(Zc))}
    rank_l = {labels[i]: int(p) for p, i in enumerate(leaves_list(Zl))}
    disp = {l: abs(rank_c[l] - rank_l[l]) for l in labels}

    n = len(labels)
    rf_obs = rf(Zc, Zl, labels)
    rf_max = 2 * (n - 2)
    # random baseline: relabel one tree's leaves, recompute RF
    rnd = []
    base_clades = clade_set(Zc, labels)
    for _ in range(300):
        perm = list(RNG.permutation(labels))
        other = clade_set(Zl, perm)
        rnd.append(len(base_clades ^ other))
    r, p = mantel(Dc, Dl)
    crossings = kendall_crossings(rank_c, rank_l, labels)

    conv_clades = clade_set(Zc, labels)
    lemm_clades = clade_set(Zl, labels)
    shared = sorted(conv_clades & lemm_clades, key=len)
    conv_only = sorted(conv_clades - lemm_clades, key=len)
    lemm_only = sorted(lemm_clades - conv_clades, key=len)

    metrics = {
        "n_common": n, "common": labels,
        "mantel_r": round(r, 4), "mantel_p": round(p, 4),
        "rf": rf_obs, "rf_max": rf_max, "rf_norm": round(rf_obs / rf_max, 4),
        "rf_random_mean": round(float(np.mean(rnd)), 1),
        "rf_random_sd": round(float(np.std(rnd)), 1),
        "crossings": crossings, "crossings_max": n * (n - 1) // 2,
        "crossings_norm": round(crossings / (n * (n - 1) / 2), 4),
        "rank_displacement": dict(sorted(disp.items(), key=lambda kv: -kv[1])),
        "shared_clades": [sorted(c) for c in shared],
        "convention_only_clades": [sorted(c) for c in conv_only],
        "lemma_only_clades": [sorted(c) for c in lemm_only],
    }
    with open(f"{OUT}/homoplasy_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    with open(f"{OUT}/common_convention.newick", "w", encoding="utf-8") as f:
        f.write(newick(Zc, labels) + "\n")
    with open(f"{OUT}/common_lemma.newick", "w", encoding="utf-8") as f:
        f.write(newick(Zl, labels) + "\n")

    tanglegram(labels, Zc, Zl, rank_c, rank_l, disp, f"{OUT}/tanglegram.png", metrics)

    print(f"\nMantel r = {r:.3f}  (p = {p:.3f})   "
          f"[1.0 = identical signal, 0 = unrelated]")
    print(f"Robinson-Foulds = {rf_obs} / {rf_max}  (norm {rf_obs/rf_max:.2f})   "
          f"random baseline = {np.mean(rnd):.0f} ± {np.std(rnd):.0f}")
    print(f"Tanglegram crossings = {crossings} / {n*(n-1)//2} "
          f"(norm {crossings/(n*(n-1)/2):.2f})")
    print("\nTop homoplasy culprits (rank displacement between trees):")
    for l, d in list(metrics["rank_displacement"].items())[:10]:
        print(f"  {l:5s} moves {d:2d} ranks")
    print(f"\nShared clades (present in BOTH trees) — {len(shared)} of {n-2} possible:")
    for c in shared:
        print(f"  {sorted(c)}")
    print(f"\nWrote {OUT}/tanglegram.png + homoplasy_metrics.json + 2 newicks")

    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from _provenance import write_source
        write_source(f"{OUT}/homoplasy_metrics.json", "tanglegram.py", 34)
    except Exception as e:
        print(f"Provenance error: {e}")


if __name__ == "__main__":
    main()
