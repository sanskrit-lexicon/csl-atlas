"""Phase L0.6 / M7 — cross-dictionary verbal-feature agreement (Article 9).

m4 recovers each indigenous/root dictionary's per-root grammar — gaṇa (conjugation
class), pada (parasmai/ātmane/ubhaya), transitivity — from five DIFFERENT in-dict
conventions (SKD's Vopadeva anubandha slot, VCP's `0`-marked forms, KRM's parenthesised
cluster, YAT's class-digit block, SHS's prose). m7 asks the cross-dict question that
validates all five at once and feeds the Article-9 verb matrix:

    **When two dictionaries both classify the same root, do they AGREE on its gaṇa / pada
    / transitivity?**

High agreement is strong end-to-end evidence the parses are real (five independent
extractors, five independent source traditions, converging on the same grammar). The
disagreements are themselves the research artifact — places where the dhātupāṭha
traditions genuinely differ, OR where the same SLP1 spelling hides homonymous roots
in different classes (Sanskrit `vid` is cl.2 "know" / cl.6 "find" / cl.4 "be" / cl.7
"discuss"). m7 therefore reports BOTH a strict measure (all dicts give one label) and a
compatible measure (every dict's label set shares a value — tolerant of multi-class
roots), and is framed as ANALYSIS, not a review queue (cf. the homonym-split decision:
differing classification is usually legitimate lexicography, not an error).

Within a dict a root may appear in several entries / classes; m7 collects the SET of
labels that dict gives the root (union over its rows), so a dict that lists `vid` as both
cl.2 and cl.6 is not spuriously "self-inconsistent".

Reads data/lexico/indigenous_roots.csv (run m4 --all first). Run from repo root:
    python scripts/lexico/m7_root_agreement.py --probe vid   # per-dict labels for one root
    python scripts/lexico/m7_root_agreement.py
Outputs (data/lexico/):
    root_agreement.json      per-feature agreement rates + per-dict-pair concordance
    root_feature_conflicts.csv   roots where >=2 dicts give incompatible labels (with the labels)
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

# The dicts whose roots carry parsed grammar (m4 root dicts with feature columns).
ROOT_DICTS = ("skd", "vcp", "krm", "yat", "shs")
FEATURES = ("gana", "pada", "transitivity")


def load_root_features():
    """root (SLP1 k1) -> dict code -> {feature -> set(labels)}; only non-empty labels."""
    byroot = collections.defaultdict(lambda: collections.defaultdict(
        lambda: collections.defaultdict(set)))
    path = os.path.join(DATA, "indigenous_roots.csv")
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["dict"] not in ROOT_DICTS or not r["k1"]:
                continue
            for feat in FEATURES:
                if r[feat]:
                    byroot[r["k1"]][r["dict"]][feat].add(r[feat])
    return byroot


def feature_agreement(byroot, feat):
    """Agreement stats for one feature over roots ≥2 dicts give a label.
    unanimous = the union of all dicts' label sets is a single label.
    compatible = every PAIR of dicts shares ≥1 label (tolerant of multi-class roots)."""
    n_op = n_unanimous = n_compatible = n_conflict = 0
    conflicts = []
    for root, dicts in byroot.items():
        sets = {d: s[feat] for d, s in dicts.items() if s.get(feat)}
        if len(sets) < 2:
            continue
        n_op += 1
        union = set().union(*sets.values())
        if len(union) == 1:
            n_unanimous += 1
            n_compatible += 1
            continue
        # compatible iff a single label is shared by every dict
        compatible = bool(set.intersection(*sets.values()))
        if compatible:
            n_compatible += 1
        else:
            n_conflict += 1
            conflicts.append((root, {d: "|".join(sorted(v)) for d, v in sets.items()}))
    return {
        "roots_with_2plus_opinions": n_op,
        "unanimous": n_unanimous,
        "compatible": n_compatible,
        "conflict": n_conflict,
        "unanimous_rate": round(n_unanimous / n_op, 4) if n_op else 0,
        "compatible_rate": round(n_compatible / n_op, 4) if n_op else 0,
    }, conflicts


def pair_concordance(byroot, feat):
    """Per dict-pair: of roots both give a label, fraction whose label sets intersect."""
    pair_tot = collections.Counter()
    pair_agree = collections.Counter()
    for root, dicts in byroot.items():
        present = [d for d in ROOT_DICTS if dicts.get(d, {}).get(feat)]
        for i, a in enumerate(present):
            for b in present[i + 1:]:
                key = f"{a}-{b}"
                pair_tot[key] += 1
                if dicts[a][feat] & dicts[b][feat]:
                    pair_agree[key] += 1
    return {k: {"shared_roots": pair_tot[k], "agree": pair_agree[k],
                "rate": round(pair_agree[k] / pair_tot[k], 4) if pair_tot[k] else 0}
            for k in sorted(pair_tot, key=lambda k: -pair_tot[k])}


def yat_citation_convention(byroot):
    """Observation (NOT folded into the agreement measure): YAT cites bare verbal stems
    (`BAj`, `Bram`) where the Sanskrit kośa tradition (SKD/VCP/KRM) keeps Vopadeva's
    uccāraṇārtha -a (`BAja`, `Brama`). Count YAT roots that match a Sanskrit-dict root only
    after restoring a trailing -a. A uniform -a strip WOULD add these to the agreement set
    but also collides homographs (gaṇa compatibility 86.0%→81.2% in testing), so the
    normalization is left as a maintainer-gated decision, not applied."""
    sv = set()
    for root, dicts in byroot.items():
        for d in ("skd", "vcp", "krm"):
            if d in dicts:
                sv.add(root)
                break
    yat = {r for r, dd in byroot.items() if "yat" in dd}
    exact = len(yat & sv)
    restorable = sum(1 for y in yat if y not in sv and (y + "a") in sv)
    return {
        "note": ("YAT cites bare stems; SKD/VCP/KRM keep the uccāraṇārtha -a. YAT cross-dict "
                 "agreement is therefore CONSERVATIVE (undercounts). A -a normalization is "
                 "maintainer-gated (it collides homographs: gaṇa 86.0%→81.2%)."),
        "yat_roots": len(yat),
        "match_sanskrit_dict_exact": exact,
        "match_only_after_restoring_trailing_a": restorable,
    }


def probe(root, byroot):
    print(f"\n--probe {root}: per-dict grammar labels\n" + "-" * 60)
    dicts = byroot.get(root)
    if not dicts:
        print("  (not a parsed root in any of " + ", ".join(ROOT_DICTS) + ")")
        return
    for d in ROOT_DICTS:
        if d in dicts:
            feats = {f: "|".join(sorted(dicts[d][f])) for f in FEATURES if dicts[d].get(f)}
            print(f"  {d.upper():4s} {feats}")


def main():
    byroot = load_root_features()
    if "--probe" in sys.argv:
        probe(sys.argv[sys.argv.index("--probe") + 1], byroot)
        return

    print("=" * 64)
    print("M7 — cross-dictionary verbal-feature agreement (Article 9)")
    print("=" * 64)
    print(f"  {len(byroot):,} distinct roots across {len(ROOT_DICTS)} root dicts "
          f"({', '.join(d.upper() for d in ROOT_DICTS)})")

    per_feature = {}
    all_conflicts = {}
    for feat in FEATURES:
        stats, conflicts = feature_agreement(byroot, feat)
        per_feature[feat] = {"agreement": stats, "pairs": pair_concordance(byroot, feat)}
        all_conflicts[feat] = conflicts
        print(f"\n  {feat.upper()}")
        print(f"    roots with ≥2 opinions: {stats['roots_with_2plus_opinions']:,}")
        print(f"    unanimous (one label): {stats['unanimous']:,} ({stats['unanimous_rate']:.1%})")
        print(f"    compatible (sets intersect, multi-class-tolerant): "
              f"{stats['compatible']:,} ({stats['compatible_rate']:.1%})")
        print(f"    conflict (incompatible): {stats['conflict']:,}")

    out = {
        "question": ("When two root dicts classify the same root, do they agree on "
                     "gaṇa / pada / transitivity? (Article 9)"),
        "root_dicts": list(ROOT_DICTS),
        "distinct_roots": len(byroot),
        "method": ("Group m4 rows by SLP1 root; per (dict, root) collect the SET of labels "
                   "(union over the dict's entries, so multi-class roots are not self-conflicts). "
                   "unanimous = all dicts give one label; compatible = a single label is shared by "
                   "every dict (tolerant of homonymous multi-class roots); conflict = otherwise."),
        "caveat": ("Conflicts conflate genuine cross-tradition disagreement with legitimate "
                   "homonymy (same SLP1 spelling, different roots/classes). ANALYSIS, not a review "
                   "queue. SKD/SHS feature coverage is lower than VCP/KRM/YAT, so they contribute "
                   "fewer opinions."),
        "features": per_feature,
        "yat_citation_convention": yat_citation_convention(byroot),
    }
    cc = out["yat_citation_convention"]
    print(f"\n  YAT citation convention: {cc['match_sanskrit_dict_exact']:,} YAT roots match a "
          f"Sanskrit-dict root exactly; +{cc['match_only_after_restoring_trailing_a']:,} more only "
          f"after restoring the uccāraṇārtha -a (maintainer-gated, not applied).")
    with open(os.path.join(DATA, "root_agreement.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    csv_path = os.path.join(DATA, "root_feature_conflicts.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["feature", "root"] + [d for d in ROOT_DICTS])
        for feat in FEATURES:
            for root, labels in sorted(all_conflicts[feat]):
                w.writerow([feat, root] + [labels.get(d, "") for d in ROOT_DICTS])

    n_conf = sum(len(all_conflicts[f]) for f in FEATURES)
    print(f"\nWrote root_agreement.json, {os.path.basename(csv_path)} ({n_conf:,} conflict rows)")
    try:
        sys.path.insert(0, os.path.abspath("scripts/L0"))
        from _provenance import write_source
        write_source(csv_path, "m7_root_agreement.py", 6)
    except Exception as e:
        print(f"Provenance error: {e}")


if __name__ == "__main__":
    main()
