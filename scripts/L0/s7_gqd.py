"""Stage 7 — Generalized Quartet Distance (GQD) validation of the L0 stemma.

Applies the phylogenetic-evaluation metric used by Rama, List, Wahle & Jäger
(2018) — the Generalized Quartet Distance of Pompei, Loreto & Tria (2011,
PLOS ONE 6(6):e20109, eq. 8) — to the committed L0 trees, scoring them against
two *expert* reference classifications that were NOT built from the convention
characters:

  gold_stemma     documented bibliographic descent (author identity, prefaces,
                  publication order, sanhw1 containment) — the analogue of the
                  Glottolog/Ethnologue gold tree in the language-phylogeny
                  literature. Deliberately polytomous: only documented groups
                  are resolved.
  gold_tradition  the target-language / tradition families recorded in
                  data/dictionary_inventory.csv (`family` column), a coarser
                  reference derived mechanically from committed metadata.

GQD (Pompei et al. eq. 8)
-------------------------
A quartet (4 leaves) is a *butterfly* in a tree if the tree resolves it into
two pairs (ab|cd), and a *star* if it does not (polytomy). With T_I the
inferred tree and T_E the expert tree:

    GQD(T_I, T_E) = |{butterflies of T_E resolved differently in T_I}|
                    ---------------------------------------------------
                            |{butterflies of T_E}|

Stars of T_E are excluded from both numerator and denominator, so an expert
classification's lack of resolution is never counted as an error — that is the
whole point of the *generalized* form. 0 = the inferred tree agrees with every
resolved expert quartet, 1 = it contradicts all of them.

Two readings are reported because the L0 candidate set contains one
non-binary tree (the bootstrap consensus can leave polytomies):
  gqd            strict: an expert butterfly left *unresolved* by T_I counts
                 as an error (conservative; what a reviewer would assume).
  gqd_pompei     literal eq. 8: only butterflies resolved *differently* count;
                 quartets T_I leaves as stars are dropped from the numerator.
They coincide whenever T_I is fully binary; `n_inferred_star` reports the gap.

Quartet topologies are read off each tree with the four-point condition on the
unit-weight topological distance matrix (branch lengths are ignored — GQD is a
topology metric): for {a,b,c,d} the resolved pairing is the one minimising
d(x,y)+d(z,w); a three-way tie is a star. This is exact for tree metrics and
needs no phylogenetics dependency (no dendropy/scikit-bio import), so the stage
runs anywhere numpy runs.

Significance is a label-permutation randomisation test (N_PERM shuffles of the
inferred tree's leaf labels, fixed seed): it answers "could a tree of this shape
match the expert classification this well by accident?" — it is NOT a model
likelihood-ratio test and is reported as such.

Outputs (data/L0/):
  gold/gold_stemma.newick            hand-specified expert descent tree
  gold/gold_stemma_warrants.csv      per-group documentary warrant + source
  gold/gold_tradition.newick         mechanically built from the inventory
  gqd_validation.csv                 tree x gold -> GQD + permutation null
  gqd_clade_recovery.csv             per expert group, quartet recovery rate
  gqd_tree_matrix.csv                pairwise normalised quartet distance
  gqd_report.json                    everything above + limitations, machine-readable

Run from the repo root:  python scripts/L0/s7_gqd.py
Self-test:               python scripts/L0/s7_gqd.py --selftest
"""

import csv
import itertools
import json
import os
import sys
from collections import deque

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

OUT = "data/L0"
GOLD_DIR = f"{OUT}/gold"
INVENTORY = "data/dictionary_inventory.csv"
SEED = 20260726
N_PERM = 999

# --------------------------------------------------------------- gold ------
# Documented descent only. Every group below is warranted by bibliography or by
# the committed inventory notes -- never by the convention fingerprint that the
# trees under test are built from. Groups left unresolved (root polytomy) are
# dictionaries with no documented parent inside the corpus; under GQD they cost
# nothing, which is exactly why the generalized form is used.
GOLD_STEMMA_GROUPS = [
    ("Wilson", ["WIL", "YAT", "SHS"], "flat",
     "Wilson 1832 is the head of the English-tradition line; YAT (1846) and SHS "
     "(1900) both re-lexicalise it.",
     "dictionary_inventory.csv notes (WIL<->YAT ~91% mutual containment; "
     "WIL subset SHS 0.953); s3_cladogram.py KNOWN_EDGES tier A"),
    ("Cappeller", ["CCS", "CAE"], "flat",
     "Same compiler (Carl Cappeller): CCS 1887 (Skt-German) and CAE 1891 "
     "(Skt-English) are the two faces of one lexicon.",
     "dictionary_inventory.csv notes ('Same author as CCS'/'Same author as CAE'); "
     "KNOWN_EDGES tier A CCS->CAE"),
    ("Petersburg", ["PWG", "PW", "SCH", "CCS", "CAE"], "nest:Cappeller",
     "The Petersburg line: PWG (1855-75) -> PW (1879-89, Boehtlingk's shorter "
     "recension) -> SCH (1928 Nachtraege) with the Cappeller pair descending "
     "from PW.",
     "dictionary_inventory.csv notes ('Continuation of PWG/PWK'; "
     "'CCS subset PW 0.945 confirms PWK->CCS'); KNOWN_EDGES tier A "
     "PWG->PW, PW->CCS, PWG->SCH"),
    ("Monier-Williams", ["MW72", "MW"], "flat",
     "Same compiler, first (1872) and second (1899) editions.",
     "dictionary_inventory.csv notes ('Predecessor to MW (1899)'); "
     "KNOWN_EDGES tier A MW72->MW"),
    ("Apte", ["AP90", "AP"], "flat",
     "Apte 1890 and the 1957-59 Pune revision of it.",
     "dictionary_inventory.csv notes ('Original 1890 Apte; AP90->AP grew 2.6x'); "
     "KNOWN_EDGES tier A AP90->AP"),
]

# Documented descent that a TREE cannot express (reticulation): recorded here so
# the limitation is machine-readable rather than prose-only.
GOLD_STEMMA_UNREPRESENTABLE = [
    ("PWG", "MW72", "A", "MW72's preface credits the early PWG fascicles, but MW72 "
     "already sits in the Monier-Williams group; a tree gives each leaf one parent."),
    ("PWG", "MW", "A", "Same conflict for MW (1899)."),
    ("BOP", "MW", "B", "Bopp-Glossarium hypothesis; MW is already placed."),
    ("BEN", "MW", "B", "Benfey hypothesis; MW is already placed."),
    ("YAT", "SHS", "A", "Collapsed into the flat Wilson group rather than resolved, "
     "to keep the gold conservative."),
]


def gold_stemma_newick(taxa):
    """Assemble the expert descent tree from GOLD_STEMMA_GROUPS.

    Groups are emitted as clades; a group marked ``nest:<name>`` embeds that
    earlier group as a sub-clade. Every taxon in *taxa* not covered by a group
    is attached to the root, i.e. left unresolved.
    """
    present = set(taxa)
    rendered, placed, sub = {}, set(), set()
    for name, members, mode, _why, _src in GOLD_STEMMA_GROUPS:
        mem = [m for m in members if m in present]
        if len(mem) < 2:
            rendered[name] = None
            continue
        if mode.startswith("nest:"):
            inner = mode.split(":", 1)[1]
            inner_members = set(dict((g[0], g[1]) for g in GOLD_STEMMA_GROUPS)[inner])
            outer = [m for m in mem if m not in inner_members]
            parts = sorted(outer)
            if rendered.get(inner):
                parts.append(rendered[inner])
                sub.add(inner)
            rendered[name] = "(" + ",".join(parts) + ")"
        else:
            rendered[name] = "(" + ",".join(sorted(mem)) + ")"
        placed.update(mem)
    top = [rendered[n] for n, _m, _mo, _w, _s in GOLD_STEMMA_GROUPS
           if rendered.get(n) and n not in sub]
    loose = sorted(t for t in taxa if t not in placed)
    return "(" + ",".join(top + loose) + ");"


def gold_tradition_newick(taxa):
    """Tradition families straight from the committed inventory `family` column."""
    fam = {}
    with open(INVENTORY, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["code"] in taxa:
                fam.setdefault(r["family"], []).append(r["code"])
    missing = sorted(set(taxa) - {c for v in fam.values() for c in v})
    if missing:
        raise SystemExit(f"inventory has no family row for: {missing}")
    parts = []
    for name in sorted(fam):
        mem = sorted(fam[name])
        parts.append("(" + ",".join(mem) + ")" if len(mem) > 1 else mem[0])
    return "(" + ",".join(parts) + ");", {k: sorted(v) for k, v in fam.items()}


# ------------------------------------------------------------- newick ------
class Tree:
    """Unrooted topology: leaf names + unit-weight topological distances."""

    def __init__(self, name, newick, grade="", kind="", note=""):
        self.name, self.grade, self.kind, self.note = name, grade, kind, note
        self.leaves, self._adj = _parse_newick(newick)
        self.index = {lf: i for i, lf in enumerate(self.leaves)}
        self.D = _topo_distances(self._adj, self.leaves)

    def __repr__(self):
        return f"<Tree {self.name} n={len(self.leaves)}>"


def _parse_newick(s):
    """Return (leaf_names, adjacency). Branch lengths / support labels ignored."""
    s = s.strip()
    if not s.endswith(";"):
        raise ValueError("newick must end with ';'")
    s = s[:-1]
    adj, leaves = {}, []
    counter = itertools.count()

    def new_node():
        nid = next(counter)
        adj[nid] = []
        return nid

    def link(a, b):
        adj[a].append(b)
        adj[b].append(a)

    pos = 0

    def parse_node():
        nonlocal pos
        if s[pos] == "(":
            pos += 1
            node = new_node()
            while True:
                child = parse_node()
                link(node, child)
                if s[pos] == ",":
                    pos += 1
                    continue
                if s[pos] == ")":
                    pos += 1
                    break
                raise ValueError(f"unexpected {s[pos]!r} at {pos}")
            _skip_label()
            return node
        start = pos
        while pos < len(s) and s[pos] not in "(),:":
            pos += 1
        label = s[start:pos].strip()
        node = new_node()
        if not label:
            raise ValueError(f"unnamed leaf at {start}")
        leaves.append(label)
        adj[node] = adj[node]
        _skip_label()
        _leaf_of[node] = label
        return node

    def _skip_label():
        nonlocal pos
        while pos < len(s) and s[pos] not in "(),":
            pos += 1

    _leaf_of = {}
    root = parse_node()
    if pos != len(s):
        raise ValueError(f"trailing input at {pos}: {s[pos:]!r}")
    if len(set(leaves)) != len(leaves):
        dup = sorted({x for x in leaves if leaves.count(x) > 1})
        raise ValueError(f"duplicate leaf labels: {dup}")
    leaf_nodes = {v: k for k, v in _leaf_of.items()}
    _ = root
    return leaves, (adj, leaf_nodes)


def _topo_distances(adjacency, leaves):
    adj, leaf_nodes = adjacency
    n = len(leaves)
    D = np.zeros((n, n), dtype=np.int32)
    for i, lf in enumerate(leaves):
        src = leaf_nodes[lf]
        dist = {src: 0}
        q = deque([src])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    q.append(v)
        for j, other in enumerate(leaves):
            D[i, j] = dist[leaf_nodes[other]]
    return D


# ------------------------------------------------------------ quartets -----
_QCACHE = {}


def quartet_index(taxa):
    """(qa,qb,qc,qd) index arrays over C(len(taxa),4) quartets, canonical order."""
    key = ("idx", len(taxa))
    if key not in _QCACHE:
        combos = np.array(list(itertools.combinations(range(len(taxa)), 4)),
                          dtype=np.int32)
        _QCACHE[key] = (combos[:, 0], combos[:, 1], combos[:, 2], combos[:, 3])
    return _QCACHE[key]


def quartet_codes(tree, taxa):
    """0 = star (unresolved), 1 = ab|cd, 2 = ac|bd, 3 = ad|bc, per quartet."""
    key = ("codes", tree.name, tuple(taxa))
    if key in _QCACHE:
        return _QCACHE[key]
    idx = np.array([tree.index[t] for t in taxa], dtype=np.int32)
    D = tree.D[np.ix_(idx, idx)].astype(np.int64)
    qa, qb, qc, qd = quartet_index(taxa)
    s1 = D[qa, qb] + D[qc, qd]
    s2 = D[qa, qc] + D[qb, qd]
    s3 = D[qa, qd] + D[qb, qc]
    codes = _codes_from_sums(s1, s2, s3)
    _QCACHE[key] = codes
    return codes


def _codes_from_sums(s1, s2, s3):
    stacked = np.stack([s1, s2, s3])
    mn = stacked.min(axis=0)
    n_min = (stacked == mn).sum(axis=0)
    codes = np.where(stacked[0] == mn, 1, np.where(stacked[1] == mn, 2, 3))
    codes = np.where(n_min == 1, codes, 0).astype(np.int8)
    return codes


def _permuted_codes(tree, taxa, perm, subset):
    """Inferred quartet codes on `subset` after relabelling leaves by `perm`."""
    idx = np.array([tree.index[t] for t in taxa], dtype=np.int32)
    D = tree.D[np.ix_(idx, idx)].astype(np.int64)
    n = len(taxa)
    flat = D.ravel()
    qa, qb, qc, qd = (a[subset] for a in quartet_index(taxa))
    pa, pb, pc, pd = perm[qa], perm[qb], perm[qc], perm[qd]
    s1 = flat[pa * n + pb] + flat[pc * n + pd]
    s2 = flat[pa * n + pc] + flat[pb * n + pd]
    s3 = flat[pa * n + pd] + flat[pb * n + pc]
    return _codes_from_sums(s1, s2, s3)


def gqd(inferred, gold, taxa, n_perm=0, rng=None):
    """Pompei et al. (2011) eq. 8, with the strict/literal pair and a null."""
    ic = quartet_codes(inferred, taxa)
    gc = quartet_codes(gold, taxa)
    butterfly = gc > 0
    n_b = int(butterfly.sum())
    if n_b == 0:
        raise ValueError("gold tree resolves no quartet on this taxon set")
    diff_strict = butterfly & (ic != gc)
    resolved_both = butterfly & (ic > 0)
    diff_pompei = resolved_both & (ic != gc)
    out = {
        "n_taxa": len(taxa),
        "n_quartets": int(butterfly.size),
        "n_gold_butterflies": n_b,
        "n_disagree": int(diff_strict.sum()),
        "n_inferred_star": int((butterfly & (ic == 0)).sum()),
        "gqd": round(float(diff_strict.sum()) / n_b, 4),
        "gqd_pompei": (round(float(diff_pompei.sum()) / int(resolved_both.sum()), 4)
                       if int(resolved_both.sum()) else None),
    }
    if n_perm:
        subset = np.flatnonzero(butterfly)
        gsub = gc[subset]
        n = len(taxa)
        null = np.empty(n_perm)
        for k in range(n_perm):
            perm = rng.permutation(n).astype(np.int32)
            pc = _permuted_codes(inferred, taxa, perm, subset)
            null[k] = float((pc != gsub).sum()) / n_b
        obs = out["gqd"]
        out["null_mean"] = round(float(null.mean()), 4)
        out["null_sd"] = round(float(null.std(ddof=1)), 4)
        out["null_min"] = round(float(null.min()), 4)
        out["z"] = (round(float((obs - null.mean()) / null.std(ddof=1)), 2)
                    if null.std(ddof=1) > 0 else None)
        out["p_perm"] = round((1 + int((null <= obs).sum())) / (1 + n_perm), 4)
        out["n_perm"] = n_perm
    return out


def clade_quartet_recovery(inferred, taxa, members):
    """Fraction of {2-in-group, 2-out} quartets the tree resolves as the group."""
    memb = np.array([t in set(members) for t in taxa])
    qa, qb, qc, qd = quartet_index(taxa)
    ma, mb, mc, md = memb[qa], memb[qb], memb[qc], memb[qd]
    cnt = ma.astype(np.int8) + mb + mc + md
    sel = cnt == 2
    target = np.where((ma & mb) | (mc & md), 1,
                      np.where((ma & mc) | (mb & md), 2, 3))
    ic = quartet_codes(inferred, taxa)
    tested = int(sel.sum())
    hit = int((sel & (ic == target)).sum())
    return tested, hit, (round(hit / tested, 4) if tested else None)


def pairwise_quartet_distance(t1, t2, taxa):
    c1, c2 = quartet_codes(t1, taxa), quartet_codes(t2, taxa)
    return round(float((c1 != c2).sum()) / c1.size, 4)


# ------------------------------------------------------------- selftest ----
def selftest():
    checks = []

    def ok(label, cond):
        checks.append((label, bool(cond)))

    t_ab_cd = Tree("ab|cd", "((a,b),(c,d));")
    t_ac_bd = Tree("ac|bd", "((a,c),(b,d));")
    t_star = Tree("star", "(a,b,c,d);")
    taxa = ["a", "b", "c", "d"]
    ok("binary quartet resolves", quartet_codes(t_ab_cd, taxa)[0] == 1)
    ok("alternative resolution differs", quartet_codes(t_ac_bd, taxa)[0] == 2)
    ok("polytomy is a star", quartet_codes(t_star, taxa)[0] == 0)
    ok("identical trees GQD 0", gqd(t_ab_cd, t_ab_cd, taxa)["gqd"] == 0.0)
    ok("contradicting trees GQD 1", gqd(t_ac_bd, t_ab_cd, taxa)["gqd"] == 1.0)
    ok("star gold has no butterflies",
       int((quartet_codes(t_star, taxa) > 0).sum()) == 0)
    # star in the inferred tree: strict counts it, literal eq. 8 drops it
    r = gqd(t_star, t_ab_cd, taxa)
    ok("strict penalises inferred star", r["gqd"] == 1.0)
    ok("literal eq.8 drops inferred star", r["gqd_pompei"] is None)
    ok("inferred-star count reported", r["n_inferred_star"] == 1)
    # six taxa: gold resolves only the (a,b) group; inferred keeps it
    g6 = Tree("g6", "((a,b),c,d,e,f);")
    i6 = Tree("i6", "((a,b),(c,(d,(e,f))));")
    taxa6 = ["a", "b", "c", "d", "e", "f"]
    r6 = gqd(i6, g6, taxa6)
    ok("polytomous gold scores 0 when group kept", r6["gqd"] == 0.0)
    ok("polytomous gold has C(4,2)=6 butterflies", r6["n_gold_butterflies"] == 6)
    # Hand-counted: g6's butterflies are the 6 quartets {a,b,x,y}. j6 keeps a
    # and b together in 3 of them ({a,b,d,e}, {a,b,d,f}, {a,b,e,f}) and splits
    # them in the 3 containing c -> 3/6.
    j6 = Tree("j6", "((a,c),(b,(d,(e,f))));")
    ok("partial disagreement is counted exactly", gqd(j6, g6, taxa6)["gqd"] == 0.5)
    # k6 splits a from b everywhere except {a,b,e,f}, where the (e,f) clade
    # forces ab|ef -> 5/6.
    k6 = Tree("k6", "((a,c),(b,d),(e,f));")
    ok("near-total disagreement is counted exactly",
       gqd(k6, g6, taxa6)["gqd"] == round(5 / 6, 4))
    tested, hit, rate = clade_quartet_recovery(i6, taxa6, ["a", "b"])
    ok("clade recovery counts C(4,2) quartets", tested == 6 and hit == 6 and rate == 1.0)
    ok("pairwise QD self is 0", pairwise_quartet_distance(i6, i6, taxa6) == 0.0)
    ok("pairwise QD is symmetric",
       pairwise_quartet_distance(i6, j6, taxa6)
       == pairwise_quartet_distance(j6, i6, taxa6))
    # branch lengths and support labels must not change the topology reading
    t_len = Tree("len", "((a:0.1,b:0.2)0.97:0.3,(c:0.4,d:0.5)0.8:0.6);")
    ok("branch lengths ignored", (quartet_codes(t_len, taxa)
                                  == quartet_codes(t_ab_cd, taxa)).all())
    # trifurcating (unrooted) newick reads the same as its rooted twin
    t_tri = Tree("tri", "((a,b),c,d);")
    ok("trifurcating root reads the same", quartet_codes(t_tri, taxa)[0] == 1)
    # gold assembly
    nw = gold_stemma_newick(["WIL", "YAT", "SHS", "PWG", "PW", "SCH", "CCS", "CAE",
                             "MW72", "MW", "AP90", "AP", "BOP"])
    gt = Tree("gold", nw)
    ok("gold parses", len(gt.leaves) == 13)
    ok("Cappeller nests inside Petersburg", "(CAE,CCS)" in nw and "PWG" in nw)
    ok("undocumented dict left at root", nw.count("BOP") == 1)
    bad = [c for c, v in checks if not v]
    for c, v in checks:
        print(f"  {'PASS' if v else 'FAIL'}  {c}")
    print(f"selftest: {len(checks) - len(bad)}/{len(checks)} passed")
    return 1 if bad else 0


# ----------------------------------------------------------------- main ----
TREES = [
    ("canonical_consensus", f"{OUT}/trees/canonical_consensus.newick", "gated",
     "convention", "published point estimate: B_whamming UPGMA, 1000x "
     "dimension-bootstrap consensus"),
    ("B_whamming_upgma", f"{OUT}/trees/B_whamming_upgma.newick", "gated",
     "convention", "canonical config, single UPGMA run"),
    ("B_whamming_nj", f"{OUT}/trees/B_whamming_nj.newick", "gated", "convention", ""),
    ("B_hamming_upgma", f"{OUT}/trees/B_hamming_upgma.newick", "gated", "convention", ""),
    ("B_hamming_nj", f"{OUT}/trees/B_hamming_nj.newick", "gated", "convention", ""),
    ("A_jaccard_upgma", f"{OUT}/trees/A_jaccard_upgma.newick", "gated", "convention", ""),
    ("A_jaccard_nj", f"{OUT}/trees/A_jaccard_nj.newick", "gated", "convention", ""),
    ("C_chamming_upgma", f"{OUT}/trees/C_chamming_upgma.newick", "gated", "convention", ""),
    ("C_chamming_nj", f"{OUT}/trees/C_chamming_nj.newick", "gated", "convention", ""),
    ("bayesian_map", f"{OUT}/trees/bayesian_map.newick", "gated", "convention",
     "Bayesian Mk MCMC maximum-a-posteriori tree (s5_bayesian.py)"),
    ("preview_common_convention", f"{OUT}/preview/common_convention.newick", "preview",
     "convention", "preview-grade (19 dims, Gower), restricted to the tanglegram "
     "leaf set"),
    ("preview_common_lemma", f"{OUT}/preview/common_lemma.newick", "preview",
     "content", "CONTENT baseline: UPGMA on sanhw1 lemma-overlap Jaccard "
     "(tanglegram.py), same leaf set"),
]


def main():
    rng = np.random.default_rng(SEED)
    trees = []
    for name, path, grade, kind, note in TREES:
        if not os.path.exists(path):
            print(f"  ! missing {path} — skipped")
            continue
        with open(path, encoding="utf-8") as f:
            trees.append(Tree(name, f.read().strip(), grade, kind, note))
    if not trees:
        raise SystemExit("no committed L0 trees found — run s3_cladogram.py first")
    by_name = {t.name: t for t in trees}

    full = sorted(by_name["canonical_consensus"].leaves)
    common = sorted(set(full) & set(by_name["preview_common_lemma"].leaves)) \
        if "preview_common_lemma" in by_name else full
    print(f"taxa: full={len(full)}  content-comparable={len(common)}")

    os.makedirs(GOLD_DIR, exist_ok=True)
    stemma_nw = gold_stemma_newick(full)
    trad_nw, families = gold_tradition_newick(full)
    with open(f"{GOLD_DIR}/gold_stemma.newick", "w", encoding="utf-8") as f:
        f.write(stemma_nw + "\n")
    with open(f"{GOLD_DIR}/gold_tradition.newick", "w", encoding="utf-8") as f:
        f.write(trad_nw + "\n")
    with open(f"{GOLD_DIR}/gold_stemma_warrants.csv", "w", encoding="utf-8",
              newline="") as f:
        w = csv.writer(f)
        w.writerow(["group", "members", "structure", "warrant", "source"])
        for name, members, mode, why, src in GOLD_STEMMA_GROUPS:
            w.writerow([name, " ".join(members), mode, why, src])
        for a, b, tier, why in GOLD_STEMMA_UNREPRESENTABLE:
            w.writerow([f"UNREPRESENTABLE:{a}->{b}", f"{a} {b}", f"tier {tier}",
                        why, "s3_cladogram.py KNOWN_EDGES"])

    golds = {
        "stemma": Tree("gold_stemma", stemma_nw, "expert", "gold"),
        "tradition": Tree("gold_tradition", trad_nw, "expert", "gold"),
    }

    # ---- GQD table -------------------------------------------------------
    rows = []
    for t in trees:
        taxa = sorted(set(t.leaves) & set(full))
        for gname, g in golds.items():
            r = gqd(t, g, taxa, n_perm=N_PERM, rng=rng)
            r.update(tree=t.name, gold=gname, grade=t.grade, kind=t.kind)
            rows.append(r)
            print(f"  {t.name:26s} vs {gname:9s} GQD={r['gqd']:.4f} "
                  f"(null {r['null_mean']:.3f}+-{r['null_sd']:.3f}, "
                  f"z={r['z']}, p={r['p_perm']})")

    # Head-to-head on the leaf set both the convention and content trees share.
    head = []
    if "preview_common_lemma" in by_name:
        for tname in ("canonical_consensus", "preview_common_convention",
                      "preview_common_lemma"):
            if tname not in by_name:
                continue
            for gname, g in golds.items():
                r = gqd(by_name[tname], g, common, n_perm=N_PERM, rng=rng)
                r.update(tree=tname, gold=gname, kind=by_name[tname].kind,
                         leaf_set="content-comparable")
                head.append(r)

    fields = ["tree", "gold", "grade", "kind", "n_taxa", "n_quartets",
              "n_gold_butterflies", "n_disagree", "n_inferred_star", "gqd",
              "gqd_pompei", "null_mean", "null_sd", "null_min", "z", "p_perm",
              "n_perm"]
    with open(f"{OUT}/gqd_validation.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # ---- per-group quartet recovery --------------------------------------
    groups = [(f"stemma:{n}", m) for n, m, _mo, _w, _s in GOLD_STEMMA_GROUPS]
    groups += [(f"tradition:{k}", v) for k, v in sorted(families.items())
               if len(v) > 1]
    recov = []
    for gname, members in groups:
        for t in trees:
            taxa = sorted(set(t.leaves) & set(full))
            mem = [m for m in members if m in set(taxa)]
            if len(mem) < 2 or len(mem) > len(taxa) - 2:
                continue
            tested, hit, rate = clade_quartet_recovery(t, taxa, mem)
            recov.append({"group": gname, "members": " ".join(sorted(mem)),
                          "tree": t.name, "kind": t.kind, "n_quartets": tested,
                          "n_recovered": hit, "recovery": rate})
    with open(f"{OUT}/gqd_clade_recovery.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["group", "members", "tree", "kind",
                                          "n_quartets", "n_recovered", "recovery"])
        w.writeheader()
        for r in recov:
            w.writerow(r)

    # ---- pairwise quartet distance among trees ---------------------------
    names = [t.name for t in trees]
    with open(f"{OUT}/gqd_tree_matrix.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([""] + names)
        for a in trees:
            row = [a.name]
            for b in trees:
                taxa = sorted(set(a.leaves) & set(b.leaves))
                row.append(f"{pairwise_quartet_distance(a, b, taxa):.4f}")
            w.writerow(row)

    report = {
        "stage": 7,
        "metric": {
            "name": "Generalized Quartet Distance (GQD)",
            "definition": ("|butterflies of the expert tree resolved differently "
                           "in the inferred tree| / |butterflies of the expert "
                           "tree|; stars of the expert tree are excluded"),
            "source": ("Pompei S, Loreto V, Tria F (2011) On the Accuracy of "
                       "Language Trees. PLOS ONE 6(6):e20109, eq. 8 "
                       "(doi:10.1371/journal.pone.0020109); used for tree "
                       "evaluation by Rama T, List J-M, Wahle J, Jaeger G (2018) "
                       "'Are Automatic Methods for Cognate Detection Good Enough "
                       "for Phylogenetic Reconstruction in Historical "
                       "Linguistics?', NAACL-HLT 2018 (arXiv:1804.05416)"),
            "implementation": ("re-implemented here from the published definition "
                               "(four-point condition on unit-weight topological "
                               "distances); no black-box phylogenetics package"),
            "seed": SEED, "n_perm": N_PERM,
        },
        "inputs": {
            "trees": [{"name": t.name, "path": p, "grade": t.grade, "kind": t.kind,
                       "note": t.note, "n_leaves": len(t.leaves)}
                      for t, (_n, p, _g, _k, _no) in
                      zip(trees, [x for x in TREES if os.path.exists(x[1])])],
            "gold_stemma": f"{GOLD_DIR}/gold_stemma.newick",
            "gold_tradition": f"{GOLD_DIR}/gold_tradition.newick",
            "inventory": INVENTORY,
        },
        "taxa": {"full": full, "content_comparable": common},
        "families": families,
        "gqd": rows,
        "head_to_head": head,
        "clade_recovery": recov,
        "limitations": [
            "The expert stemma is a TREE; documented dictionary descent is "
            "reticulate. Five documented edges (listed in "
            "gold/gold_stemma_warrants.csv as UNREPRESENTABLE) cannot be encoded, "
            "including PWG->MW and PWG->MW72 — the very edges the L0 results "
            "identify as reformatted. GQD therefore cannot reward a tree for "
            "recovering them.",
            "The gold stemma's warrants include sanhw1 lemma containment, which is "
            "the content axis. That gives the CONTENT tree a mild home-field "
            "advantage in the head-to-head and gives the convention tree none; "
            "read a convention-tree win as conservative and a content-tree win as "
            "partly circular.",
            "The permutation test randomises leaf labels only. It bounds accidental "
            "agreement given the tree's shape; it is not a model-comparison test "
            "and yields no likelihood.",
            "n = 32 dictionaries, of which only 14 sit in a documented group; the "
            "remaining 18 are unresolved in the gold and contribute no butterflies "
            "of their own.",
            "Corpus is European-tradition-skewed (see L0_DESIGN limitations); the "
            "gold inherits that skew.",
        ],
    }
    with open(f"{OUT}/gqd_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    try:
        from _provenance import write_source
        write_source(f"{OUT}/gqd_report.json", "s7_gqd.py", 7)
        write_source(f"{OUT}/gqd_validation.csv", "s7_gqd.py", 7)
    except Exception as e:  # provenance is best-effort, as in the other stages
        print(f"Provenance error: {e}")

    print(f"\nwrote {OUT}/gqd_validation.csv, gqd_clade_recovery.csv, "
          f"gqd_tree_matrix.csv, gqd_report.json and {GOLD_DIR}/")


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    main()
