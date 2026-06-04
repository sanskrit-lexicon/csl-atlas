#!/usr/bin/env python3
"""
Phase L2 — Lemma-overlap cladogram from sanhw1.

Produces:
  - data/sanhw1_distance_matrix.csv  (41x41 Jaccard distances)
  - data/sanhw1_cladogram.newick     (UPGMA tree in Newick format)
  - data/sanhw1_inheritance_edges.csv (top inheritance edges with directional containment)

This is one signal of the unified inheritance score. L0 will combine
this with the convention-fingerprint cladogram + L3 forensic signals
to produce the canonical genealogy.
"""

import sys
import csv
import collections
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

REPO_ROOT = Path(__file__).parent.parent
SANHW1 = REPO_ROOT / "observatory" / "snapshots" / "sanhw1.txt"
DATA = REPO_ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)

# Load inventory for year + family
INVENTORY = {}
with open(DATA / "dictionary_inventory.csv", encoding='utf-8') as f:
    for row in csv.DictReader(f):
        INVENTORY[row['code']] = row

def load_lemmas():
    """Build dict_code -> set of lemmas from sanhw1.txt."""
    print(f"Loading {SANHW1}...")
    dict_lemmas = collections.defaultdict(set)
    with open(SANHW1, encoding='utf-8') as f:
        for line in f:
            if ':' not in line:
                continue
            lemma, dictstr = line.split(':', 1)
            for code in dictstr.strip().split(','):
                dict_lemmas[code.strip()].add(lemma.strip())
    print(f"  Loaded {len(dict_lemmas)} dicts, total lemma-dict pairs: {sum(len(s) for s in dict_lemmas.values()):,}")
    return dict_lemmas

def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

def upgma(distance_matrix, labels):
    """Simple UPGMA implementation. Returns Newick string."""
    n = len(labels)
    # Active clusters: dict cluster_id -> (newick_string, size)
    clusters = {i: (labels[i], 1) for i in range(n)}
    # Pairwise distances: dict (i,j) -> dist where i<j
    D = {}
    for i in range(n):
        for j in range(i+1, n):
            D[(i, j)] = distance_matrix[i][j]

    next_id = n
    while len(clusters) > 1:
        # Find min-dist pair
        active_keys = [k for k in D.keys() if k[0] in clusters and k[1] in clusters]
        if not active_keys:
            break
        i, j = min(active_keys, key=lambda k: D[k])
        d_ij = D[(i, j)]

        # Merge i and j into new cluster
        ni = clusters[i][1]
        nj = clusters[j][1]
        new_size = ni + nj
        new_newick = f"({clusters[i][0]}:{d_ij/2:.4f},{clusters[j][0]}:{d_ij/2:.4f})"
        clusters[next_id] = (new_newick, new_size)

        # Update distances: avg-linkage UPGMA
        for k in list(clusters.keys()):
            if k in (i, j, next_id):
                continue
            # New distance from cluster (i+j) to k = weighted avg
            d_ik = D.get((min(i, k), max(i, k)), 0)
            d_jk = D.get((min(j, k), max(j, k)), 0)
            new_d = (d_ik * ni + d_jk * nj) / new_size
            D[(min(next_id, k), max(next_id, k))] = new_d

        # Remove old clusters
        del clusters[i]
        del clusters[j]
        next_id += 1

    if not clusters:
        return ""
    last = list(clusters.values())[0]
    return last[0] + ";"

def main():
    print(f"\n{'='*60}")
    print(f"L2 — Lemma cladogram from sanhw1")
    print(f"{'='*60}\n")

    dict_lemmas = load_lemmas()
    dicts = sorted(dict_lemmas.keys())
    n = len(dicts)
    print(f"\nDicts to compare: {n}")

    # 1. Distance matrix (1 - Jaccard)
    print("\nBuilding 41x41 distance matrix...")
    matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            d = 1.0 - jaccard(dict_lemmas[dicts[i]], dict_lemmas[dicts[j]])
            matrix[i][j] = d
            matrix[j][i] = d

    # Save matrix
    matrix_path = DATA / "sanhw1_distance_matrix.csv"
    with open(matrix_path, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['dict'] + dicts)
        for i, code in enumerate(dicts):
            w.writerow([code] + [f'{matrix[i][j]:.4f}' for j in range(n)])
    print(f"  → {matrix_path}")

    # 2. UPGMA cladogram
    print("\nComputing UPGMA tree...")
    newick = upgma(matrix, dicts)
    newick_path = DATA / "sanhw1_cladogram.newick"
    with open(newick_path, 'w', encoding='utf-8') as f:
        f.write(newick + "\n")
    print(f"  → {newick_path} ({len(newick)} chars)")

    # 3. Inheritance edges (directional containment)
    print("\nComputing inheritance edges (directional containment)...")
    edges = []
    for i, A in enumerate(dicts):
        for j, B in enumerate(dicts):
            if i == j:
                continue
            sa = dict_lemmas[A]
            sb = dict_lemmas[B]
            if not sa or not sb:
                continue
            inter = len(sa & sb)
            ca = inter / len(sa) if sa else 0
            # Year filter: A → B only plausible if year(A) <= year(B)
            year_a_str = INVENTORY.get(A, {}).get('year', 'n/a')
            year_b_str = INVENTORY.get(B, {}).get('year', 'n/a')
            try:
                year_a = int(year_a_str) if year_a_str != 'n/a' else None
                year_b = int(year_b_str) if year_b_str != 'n/a' else None
                temporal_ok = (year_a is None or year_b is None or year_a <= year_b)
            except (ValueError, TypeError):
                temporal_ok = True

            if ca >= 0.85:  # Only strong-containment edges
                # Inheritance reading: A (the subset, older) is SOURCE,
                # B (the superset, younger) is INHERITOR
                edges.append({
                    'source': A,           # older, smaller — the lemmas came FROM here
                    'inheritor': B,        # younger, larger — the lemmas went TO here
                    'containment': round(ca, 4),
                    'intersection': inter,
                    'source_size': len(sa),
                    'inheritor_size': len(sb),
                    'source_year': year_a_str,
                    'inheritor_year': year_b_str,
                    'temporal_plausible': temporal_ok  # source older than inheritor
                })

    edges.sort(key=lambda e: -e['containment'])
    edges_path = DATA / "sanhw1_inheritance_edges.csv"
    with open(edges_path, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['source', 'inheritor', 'containment', 'intersection',
                                          'source_size', 'inheritor_size', 'source_year',
                                          'inheritor_year', 'temporal_plausible'])
        w.writeheader()
        for e in edges:
            w.writerow(e)

    print(f"  → {edges_path} ({len(edges)} edges with ≥85% containment)")
    print()
    print("Top 25 temporally-plausible inheritance edges (source → inheritor):")
    plausible = [e for e in edges if e['temporal_plausible']]
    for e in plausible[:25]:
        print(f"  {e['source']:8s} ({e['source_year']}) → {e['inheritor']:8s} ({e['inheritor_year']}) : {e['containment']:.3f}  ({e['intersection']:>6,} shared lemmas)")

    # 4. Save tree as ASCII for quick visual
    print(f"\n=== UPGMA tree (Newick) ===")
    print(newick)

    print(f"\n{'='*60}")
    print(f"L2 COMPLETE")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
