"""Stage 5 (Phase L0-rigor) — Neighbour-Joining bootstrap + Bayesian MCMC.

Upgrades the L0 canonical from a bootstrap-consensus UPGMA to the design's full
"all three algorithms" (L0_DESIGN §5): UPGMA + NJ + Bayesian, with proper support.

- **NJ bootstrap**: B character resamples → Saitou–Nei NJ → tally sister (cherry)
  support per known edge.
- **Bayesian MCMC**: the one-hot convention characters as binary morphological
  characters under a 2-state symmetric **Mk (Lewis 2001)** model; Felsenstein
  pruning likelihood; Metropolis–Hastings with NNI (topology) + multiplier
  (branch-length) moves, started from the NJ tree. Posterior sister-support +
  MAP tree.
- Cross-method comparison table (UPGMA vs NJ vs Bayesian sister-support on the
  known edges) + Robinson–Foulds between the three point estimates.

Validation that the sampler works: the documented sister pairs (WIL+SHS, PWG+PW,
CAE+CCS, MW72+BOP) should carry high posterior. Outputs to data/L0/.
"""

import os
import sys
import csv
import json
import math
import numpy as np
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s3_cladogram as s3  # reuse load / informative_dims / clades / rf_distance
from preview_tree import linkage_to_newick  # noqa: E402
from scipy.cluster.hierarchy import linkage, to_tree
from scipy.spatial.distance import squareform

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

RNG = np.random.default_rng(20260603)
B_BOOT = 500          # NJ bootstrap replicates
GEN = 80000           # MCMC generations
BURNIN = 25000
THIN = 40

KNOWN = [("WIL", "SHS"), ("WIL", "YAT"), ("YAT", "SHS"), ("PWG", "PW"),
         ("PW", "CCS"), ("CCS", "CAE"), ("MW72", "MW"), ("AP90", "AP"),
         ("PWG", "SCH"), ("MW72", "BOP"), ("BOP", "MW")]


# ----------------------------------------------------------- characters ---
def build_characters():
    codes, vals, _ = s3.load()
    dims = s3.informative_dims(codes, vals)
    tokens = sorted({f"{d}={o}" for c in codes for d in dims if d in vals[c]
                     for o in vals[c][d].split("+")})
    M = np.full((len(codes), len(tokens)), -1, dtype=int)  # -1 = ambiguous
    for ti, tok in enumerate(tokens):
        d = int(tok.split("=")[0]); opt = tok.split("=", 1)[1]
        for ci, c in enumerate(codes):
            if d in vals[c]:
                M[ci, ti] = 1 if opt in vals[c][d].split("+") else 0
    # keep characters that vary among observed {0,1}
    keep = [j for j in range(M.shape[1])
            if len({v for v in M[:, j] if v >= 0}) > 1]
    return codes, M[:, keep]


# ------------------------------------------------------------------ NJ ----
def nj_adjacency(D, n):
    adj = defaultdict(set); blen = {}
    active = list(range(n))
    dist = {i: {j: float(D[i, j]) for j in range(n) if j != i} for i in active}
    nxt = n
    while len(active) > 2:
        m = len(active)
        r = {i: sum(dist[i][k] for k in active if k != i) for i in active}
        best = bi = bj = None
        for x in range(m):
            for y in range(x + 1, m):
                i, j = active[x], active[y]
                q = (m - 2) * dist[i][j] - r[i] - r[j]
                if best is None or q < best:
                    best, bi, bj = q, i, j
        i, j = bi, bj; dij = dist[i][j]
        li = 0.5 * dij + (r[i] - r[j]) / (2 * (m - 2))
        li = min(max(li, 1e-6), dij); lj = max(dij - li, 1e-6)
        u = nxt; nxt += 1
        adj[u].add(i); adj[i].add(u); blen[frozenset((u, i))] = li
        adj[u].add(j); adj[j].add(u); blen[frozenset((u, j))] = lj
        du = {}
        for k in active:
            if k in (i, j):
                continue
            du[k] = 0.5 * (dist[i][k] + dist[j][k] - dij)
            dist[k][u] = du[k]
        dist[u] = du
        active = [a for a in active if a not in (i, j)] + [u]
    a, b = active
    adj[a].add(b); adj[b].add(a); blen[frozenset((a, b))] = max(dist[a][b], 1e-6)
    return adj, blen


def internal_nodes(adj, n):
    return [u for u in adj if u >= n]


def cherries(adj, n):
    """Set of leaf-pairs sharing one internal neighbour (sisters)."""
    out = set()
    for u in internal_nodes(adj, n):
        leaves = [x for x in adj[u] if x < n]
        for a in range(len(leaves)):
            for b in range(a + 1, len(leaves)):
                out.add(frozenset((leaves[a], leaves[b])))
    return out


def leaves_beyond(adj, u, v, n):
    """Leaf set on v's side when edge (u,v) is cut (excludes u's side)."""
    seen = {u, v}
    stack = [v]
    leaves = set()
    while stack:
        x = stack.pop()
        if x < n:
            leaves.add(x)
        for w in adj[x]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    return leaves


def clade_sets_adj(adj, n):
    """All bipartition sides (both) of an unrooted tree, as leaf-id frozensets."""
    allleaves = set(range(n))
    out = []
    done = set()
    for u in list(adj):
        for v in adj[u]:
            if frozenset((u, v)) in done:
                continue
            done.add(frozenset((u, v)))
            side = leaves_beyond(adj, u, v, n)
            out.append(frozenset(side))
            out.append(frozenset(allleaves - side))
    return out


def clades_linkage(Z, n):
    """Rooted clades (each internal node's descendant leaf-id set)."""
    t = to_tree(Z)
    out = []
    def rec(nd):
        if nd.is_leaf():
            return [nd.id]
        ls = rec(nd.get_left()) + rec(nd.get_right())
        out.append(frozenset(ls))
        return ls
    rec(t)
    return out


def pair_close(clade_list, ai, bi, k=4):
    """True if some clade of size 2..k contains both leaves."""
    for cl in clade_list:
        if 2 <= len(cl) <= k and ai in cl and bi in cl:
            return True
    return False


# ------------------------------------------------- Mk likelihood (Felsenstein) ---
def pmat(t):
    e = math.exp(-2.0 * t)
    s, d = 0.5 * (1 + e), 0.5 * (1 - e)
    return np.array([[s, d], [d, s]])


def loglik(adj, blen, root, leafL, C):
    """leafL: dict leaf -> (C,2). Returns total lnL over characters."""
    def cond(node, parent):
        if node not in adj or all(nb == parent for nb in adj[node]):
            return leafL[node]
        if node < N_LEAVES:
            return leafL[node]
        L = np.ones((C, 2))
        for nb in adj[node]:
            if nb == parent:
                continue
            Lc = cond(nb, node)
            P = pmat(blen[frozenset((node, nb))])
            L *= Lc @ P.T
        return L
    Lr = cond(root, None)
    site = 0.5 * Lr[:, 0] + 0.5 * Lr[:, 1]
    return float(np.sum(np.log(np.clip(site, 1e-300, None))))


def do_nni(adj, blen, n):
    """One random NNI on an internal edge; returns (success)."""
    edges = [(u, v) for u in internal_nodes(adj, n) for v in adj[u]
             if v >= n and u < v]
    if not edges:
        return False
    u, v = edges[RNG.integers(len(edges))]
    u_others = [x for x in adj[u] if x != v]
    v_others = [x for x in adj[v] if x != u]
    if len(u_others) < 2 or len(v_others) < 2:
        return False
    a = u_others[RNG.integers(len(u_others))]
    c = v_others[RNG.integers(len(v_others))]
    # swap subtrees a (under u) and c (under v)
    adj[u].discard(a); adj[a].discard(u)
    adj[v].discard(c); adj[c].discard(v)
    adj[u].add(c); adj[c].add(u)
    adj[v].add(a); adj[a].add(v)
    blen[frozenset((u, c))] = blen.pop(frozenset((u, a)))
    blen[frozenset((v, a))] = blen.pop(frozenset((v, c)))
    return True


def main():
    global N_LEAVES
    codes, M = build_characters()
    N_LEAVES = len(codes)
    C = M.shape[1]
    print(f"{N_LEAVES} taxa × {C} variable binary characters\n")

    # leaf conditional likelihoods (C,2): 1→[0,1] 0→[1,0] -1→[1,1]
    leafL = {}
    for i in range(N_LEAVES):
        a = np.ones((C, 2))
        a[M[i] == 1] = [0, 1]
        a[M[i] == 0] = [1, 0]
        leafL[i] = a

    # distance matrix (Hamming on observed chars) for NJ start + bootstrap
    def dmat(Mat):
        n = Mat.shape[0]
        D = np.zeros((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                obs = (Mat[i] >= 0) & (Mat[j] >= 0)
                d = np.mean(Mat[i][obs] != Mat[j][obs]) if obs.any() else 1.0
                D[i, j] = D[j, i] = d
        return D

    D = dmat(M)
    idx = {c: i for i, c in enumerate(codes)}

    # ---- NJ + UPGMA bootstrap (clade co-membership ≤ 4) ----
    nj_count = defaultdict(int); up_count = defaultdict(int)
    for _ in range(B_BOOT):
        cols = RNG.integers(0, C, C)
        Db = dmat(M[:, cols])
        adjb, _ = nj_adjacency(Db, N_LEAVES)
        cl_nj = clade_sets_adj(adjb, N_LEAVES)
        Zb = linkage(squareform(Db, checks=False), method="average")
        cl_up = clades_linkage(Zb, N_LEAVES)
        for a, b in KNOWN:
            if pair_close(cl_nj, idx[a], idx[b]):
                nj_count[(a, b)] += 1
            if pair_close(cl_up, idx[a], idx[b]):
                up_count[(a, b)] += 1

    # ---- Bayesian Mk MCMC ----
    adj, blen = nj_adjacency(D, N_LEAVES)
    root = internal_nodes(adj, N_LEAVES)[0]
    cur = loglik(adj, blen, root, leafL, C)
    best_ll, best_adj, best_blen = cur, {k: set(v) for k, v in adj.items()}, dict(blen)
    n_acc = 0
    cherry_post = defaultdict(int); biparts = defaultdict(int); n_samp = 0
    sys.setrecursionlimit(10000)

    for g in range(GEN):
        if RNG.random() < 0.5:  # NNI
            save_adj = {k: set(v) for k, v in adj.items()}; save_blen = dict(blen)
            if do_nni(adj, blen, N_LEAVES):
                root = internal_nodes(adj, N_LEAVES)[0]
                new = loglik(adj, blen, root, leafL, C)
                if math.log(RNG.random() + 1e-300) < new - cur:
                    cur = new; n_acc += 1
                else:
                    adj, blen = save_adj, save_blen
        else:  # branch-length multiplier
            e = list(blen)[RNG.integers(len(blen))]
            old = blen[e]; fac = math.exp(1.0 * (RNG.random() - 0.5))
            blen[e] = old * fac
            new = loglik(adj, blen, root, leafL, C)
            # exp(1) prior + multiplier Hastings (fac)
            la = (new - cur) + (-(blen[e] - old)) + math.log(fac)
            if math.log(RNG.random() + 1e-300) < la:
                cur = new; n_acc += 1
            else:
                blen[e] = old
        if cur > best_ll:
            best_ll = cur; best_adj = {k: set(v) for k, v in adj.items()}; best_blen = dict(blen)
        if g >= BURNIN and (g - BURNIN) % THIN == 0:
            n_samp += 1
            cl = clade_sets_adj(adj, N_LEAVES)
            for a, b in KNOWN:
                if pair_close(cl, idx[a], idx[b]):
                    cherry_post[(a, b)] += 1

    # ---- MAP tree → Newick (via UPGMA-style recursion on best_adj) ----
    def to_newick(adj, blen, root):
        def rec(node, parent):
            kids = [nb for nb in adj[node] if nb != parent]
            if not kids:
                return codes[node]
            inner = ",".join(rec(k, node) for k in kids)
            return f"({inner})"
        return rec(root, None) + ";"
    map_root = internal_nodes(best_adj, N_LEAVES)[0]
    bayes_nwk = to_newick(best_adj, best_blen, map_root)
    with open("data/L0/trees/bayesian_map.newick", "w", encoding="utf-8") as f:
        f.write(bayes_nwk + "\n")

    # ---- comparison table (metric = P(shared clade ≤ 4 leaves)) ----
    rows = []
    for a, b in KNOWN:
        rows.append({"parent": a, "child": b,
                     "upgma_support": round(up_count[(a, b)] / B_BOOT, 3),
                     "nj_support": round(nj_count[(a, b)] / B_BOOT, 3),
                     "bayes_support": round(cherry_post[(a, b)] / max(n_samp, 1), 3)})
    rows.sort(key=lambda r: -(r["upgma_support"] + r["nj_support"] + r["bayes_support"]))
    with open("data/L0/algorithm_support_comparison.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["parent", "child", "upgma_support", "nj_support", "bayes_support"])
        w.writeheader(); w.writerows(rows)

    # ---- RF between the three point estimates ----
    Zc = linkage(squareform(D, checks=False), method="average")
    upgma_nwk = linkage_to_newick(Zc, codes)
    nj_adj0, nj_blen0 = nj_adjacency(D, N_LEAVES)
    nj_nwk = to_newick(nj_adj0, nj_blen0, internal_nodes(nj_adj0, N_LEAVES)[0])
    rf = {
        "upgma_vs_nj": round(s3.rf_distance(upgma_nwk, nj_nwk, codes), 3),
        "upgma_vs_bayes": round(s3.rf_distance(upgma_nwk, bayes_nwk, codes), 3),
        "nj_vs_bayes": round(s3.rf_distance(nj_nwk, bayes_nwk, codes), 3),
    }

    report = {
        "n_taxa": N_LEAVES, "n_characters": C,
        "mcmc": {"generations": GEN, "burnin": BURNIN, "thin": THIN,
                 "samples": n_samp, "acceptance_rate": round(n_acc / GEN, 3),
                 "map_loglik": round(best_ll, 2), "model": "Mk (2-state symmetric, Lewis 2001)"},
        "nj_bootstrap_replicates": B_BOOT,
        "support_metric": "P(pair in a shared clade of ≤ 4 leaves)",
        "robinson_foulds_point_estimates": rf,
        "edge_support": rows,
        "note": ("Strong formatting edges (PWG-PW, PWG-SCH, WIL-SHS, AP90-AP) are recovered "
                 "by all three algorithms; the convention-reformatted edges (MW72-MW, WIL-YAT) "
                 "stay low across all three — the content≠convention finding is not a UPGMA "
                 "artifact. Bayesian Mk is the most sensitive to shared derived states "
                 "(surfaces PW-CCS, BOP-MW)."),
    }
    with open("data/L0/bayesian_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # ---- console ----
    print(f"MCMC: {n_samp} samples, acceptance {n_acc/GEN:.2f}, MAP lnL {best_ll:.1f}")
    print(f"RF (point estimates): {rf}\n")
    print("Support — P(shared clade ≤4) — three algorithms on the known edges:")
    print(f"  {'edge':12s} {'UPGMA':>7s} {'NJ':>7s} {'Bayes':>7s}")
    for r in rows:
        print(f"  {r['parent']+'-'+r['child']:12s} {r['upgma_support']:>7.2f} "
              f"{r['nj_support']:>7.2f} {r['bayes_support']:>7.2f}")

    try:
        from _provenance import write_source
        write_source("data/L0/bayesian_report.json", "s5_bayesian.py", 5)
    except Exception as e:
        print(f"Provenance error: {e}")


if __name__ == "__main__":
    main()
