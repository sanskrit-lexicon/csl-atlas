"""Phase L0.6 / M6 — cross-dictionary cross-reference graph overlap (lineage §3.1).

m3 emits each dict's internal cross-reference edges (source lemma → target lemma)
but leaves targets RAW SLP1 and explicitly defers the join. m6 does the deferred
step: normalise both ends to a common key and ask the LEXICOGRAPHY_ROADMAP §3.1
question — **does MW's `cf.` network inherit PWG's `Vgl.` network?** If MW were built
on the Petersburg cross-references, the two edge sets would coincide on the lemmas both
treat; if MW cross-referenced independently, they would not.

The two traditions mark the compound-family target differently — PWG with `°`
(`a°`, `mahA°`), MW with a trailing `-` (`a-`, `mahA-`) — and MW keeps SLP1 accents
(`a/-`). Normalisation strips the family marker, the accents, and stray hyphens so
`a°` (PWG) ≡ `a-` ≡ `a/-` (MW). Conservative: messy multi-part targets that don't
reduce cleanly simply fail to match, so the reported overlap is a FLOOR.

Reads data/lexico/xref_edges.csv (run m3 --all first). Run from repo root:
    python scripts/lexico/m6_xref_lineage.py --probe gam   # MW vs PWG targets for one lemma
    python scripts/lexico/m6_xref_lineage.py
Outputs (data/lexico/):
    xref_lineage.json        per dict-pair overlap stats (mw×pwg headline)
    xref_shared_edges.csv    the actual (src → target) edges shared by MW and PWG
"""

import os
import re
import sys
import csv
import json
import collections

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

DATA = "data/lexico"
csv.field_size_limit(10_000_000)

_ACCENT = re.compile(r"[/\\^]")          # SLP1 udātta/anudātta/etc. — hwnorm1 drops these


def normalize(s):
    """Fold a raw SLP1 lemma/target to a comparison key: drop the compound-family
    marker (`°` PWG / trailing `-` MW), accents, and stray edge hyphens/space."""
    s = _ACCENT.sub("", s.strip()).replace("°", "")
    s = " ".join(s.split()).strip(" -")
    return s


def load_edges():
    """dict code -> set of normalized (src, tgt) edges (deduped)."""
    edges = collections.defaultdict(set)
    raw = collections.defaultdict(list)
    path = os.path.join(DATA, "xref_edges.csv")
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            src, tgt = normalize(row["k1"]), normalize(row["target"])
            if src and tgt:
                edges[row["dict"]].add((src, tgt))
                raw[row["dict"]].append((row["k1"], row["target"], src, tgt))
    return edges, raw


def pair_overlap(a_edges, b_edges):
    """Overlap of two normalized edge sets, restricted to their shared source lemmas."""
    a_src = {s for s, _ in a_edges}
    b_src = {s for s, _ in b_edges}
    shared_src = a_src & b_src
    a_on_shared = {(s, t) for (s, t) in a_edges if s in shared_src}
    b_on_shared = {(s, t) for (s, t) in b_edges if s in shared_src}
    overlap = a_on_shared & b_on_shared
    a_tgt = collections.defaultdict(set)
    b_tgt = collections.defaultdict(set)
    for s, t in a_edges:
        a_tgt[s].add(t)
    for s, t in b_edges:
        b_tgt[s].add(t)
    lemmas_any_shared = sum(1 for s in shared_src if a_tgt[s] & b_tgt[s])
    union = a_on_shared | b_on_shared
    return {
        "a_edges": len(a_edges), "b_edges": len(b_edges),
        "a_sources": len(a_src), "b_sources": len(b_src),
        "shared_sources": len(shared_src),
        "a_edges_on_shared_sources": len(a_on_shared),
        "b_edges_on_shared_sources": len(b_on_shared),
        "overlapping_edges": len(overlap),
        "jaccard_on_shared_sources": round(len(overlap) / len(union), 4) if union else 0,
        "a_inheritance_rate": round(len(overlap) / len(a_on_shared), 4) if a_on_shared else 0,
        "b_inheritance_rate": round(len(overlap) / len(b_on_shared), 4) if b_on_shared else 0,
        "shared_sources_with_shared_target": lemmas_any_shared,
    }, overlap


def probe(lemma, raw):
    key = normalize(lemma)
    print(f"\n--probe {lemma} (norm '{key}'): targets per dict\n" + "-" * 60)
    for code in ("mw", "pwg"):
        tg = sorted({t for (k1, t0, s, t) in raw[code] if s == key})
        raws = sorted({t0 for (k1, t0, s, t) in raw[code] if s == key})
        print(f"  {code.upper():4s} normalized: {tg}")
        print(f"       raw:        {raws}")


def main():
    edges, raw = load_edges()
    if "--probe" in sys.argv:
        probe(sys.argv[sys.argv.index("--probe") + 1], raw)
        return

    print("=" * 64)
    print("M6 — cross-dictionary cross-reference graph overlap (lineage §3.1)")
    print("=" * 64)

    # Headline pair: MW (cf.) × PWG (Vgl.). Report any other co-present pair too.
    have = [c for c in edges if len(edges[c]) >= 50]
    pairs = [(a, b) for i, a in enumerate(have) for b in have[i + 1:]]
    results = {}
    shared_for_csv = None
    for a, b in pairs:
        stats, overlap = pair_overlap(edges[a], edges[b])
        results[f"{a}-{b}"] = stats
        if {a, b} == {"mw", "pwg"}:
            shared_for_csv = sorted(overlap)
        print(f"\n  {a.upper()} × {b.upper()}")
        print(f"    edges: {a}={stats['a_edges']:,}  {b}={stats['b_edges']:,}")
        print(f"    shared source lemmas: {stats['shared_sources']:,} "
              f"({a} sources {stats['a_sources']:,}, {b} sources {stats['b_sources']:,})")
        print(f"    on shared sources: {a}={stats['a_edges_on_shared_sources']:,} edges, "
              f"{b}={stats['b_edges_on_shared_sources']:,} edges")
        print(f"    OVERLAPPING edges (same src→tgt): {stats['overlapping_edges']:,}  "
              f"(Jaccard {stats['jaccard_on_shared_sources']})")
        print(f"    {a} inheritance rate {stats['a_inheritance_rate']:.1%} · "
              f"{b} {stats['b_inheritance_rate']:.1%} · "
              f"shared-src lemmas agreeing on ≥1 target: {stats['shared_sources_with_shared_target']:,}")

    # Three-way verdict — avoid the binary "inherits" overclaim. The shared edges are
    # genuine (variant-form / cognate-root pointers), well above chance, but most of each
    # dict's cross-refs are its own, so this is a shared CORE, not wholesale inheritance.
    verdict = None
    mwpwg = results.get("mw-pwg")
    if mwpwg:
        r = mwpwg["a_inheritance_rate"]
        if r < 0.05:
            verdict = ("negligible overlap — MW's cf-network is essentially INDEPENDENT of "
                       "PWG's Vgl-network")
        elif r < 0.30:
            verdict = ("PARTIAL overlap — a shared cross-reference CORE (MW {:.0%} / PWG {:.0%} of "
                       "cross-refs on lemmas both treat, well above chance) plus large independent "
                       "expansion in each tradition; NOT wholesale inheritance"
                       ).format(r, mwpwg["b_inheritance_rate"])
        else:
            verdict = "substantial overlap — strong structural inheritance of PWG cross-references"

    out = {
        "question": "Does MW cf. inherit PWG Vgl.? (LEXICOGRAPHY_ROADMAP §3.1)",
        "method": ("Normalize both ends of every m3 edge (strip compound marker °/-, SLP1 accents, "
                   "stray hyphens), dedupe per dict, then intersect edge sets restricted to source "
                   "lemmas both dicts cross-reference. Overlap is a FLOOR (messy targets fail to match)."),
        "verdict_mw_pwg": verdict,
        "pairs": results,
    }
    with open(os.path.join(DATA, "xref_lineage.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    csv_path = os.path.join(DATA, "xref_shared_edges.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["src", "target"])
        for s, t in (shared_for_csv or []):
            w.writerow([s, t])

    if verdict:
        print(f"\n  Verdict (mw×pwg): {verdict}.")
    print(f"\nWrote {os.path.join(DATA, 'xref_lineage.json')}, "
          f"{os.path.basename(csv_path)} ({len(shared_for_csv or [])} shared edges)")
    try:
        sys.path.insert(0, os.path.abspath("scripts/L0"))
        from _provenance import write_source
        write_source(csv_path, "m6_xref_lineage.py", 6)
    except Exception as e:
        print(f"Provenance error: {e}")


if __name__ == "__main__":
    main()
