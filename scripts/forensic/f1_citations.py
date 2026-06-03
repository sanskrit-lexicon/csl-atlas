"""Phase L3 / F1 — citation forensics (the handoff flagship).

Both Böhtlingk-Roth (PWG/PW, German) and Monier-Williams (MW, English) tag their
references with <ls>. Citations are language-NEUTRAL, so if MW cites the *same
sources for the same lemma* as PWG, MW used Böhtlingk's apparatus — strong copy
evidence that the German→English barrier can't explain.

Signals per dict pair (over lemmas both cite):
  source_jaccard   — do they cite the same TEXTS? (ref stripped to its sigil, e.g.
                     "P. 1,1,14" -> "P", "CHĀND. UP. 4,4,5" -> "CHĀND. UP")
  shared_exact     — same lemma, same FULL ref incl. verse ("P. 1,1,14"). MW often
                     truncates the number, so this is a strict subset of the signal.
  rare smoking-gun — a (lemma, full-ref) shared by two dicts where that ref is cited
                     for very few lemmas corpus-wide = idiosyncratic shared apparatus.
  truncation       — share of shared-lemma refs where B keeps only the sigil while A
                     has the full verse: directional flow (PWG full -> MW abbreviated).

Lemma alignment = exact raw <k1>. Coverage is reported (k1 encodings mostly agree).
Reads data/forensic/parsed/<code>.tsv (build via parse_cslorig.py --all).

Output : data/forensic/citation_pair_overlap.csv  (all citation-bearing pairs, ranked),
         data/forensic/shared_rare_citations.csv    (smoking-gun list, PWG/PW -> MW),
         data/forensic/f1_report.json.
Run from repo root:  python scripts/forensic/f1_citations.py
"""

import os
import re
import sys
import csv
import json
import collections
import itertools

sys.path.insert(0, os.path.abspath("scripts/forensic"))
from parse_cslorig import load_entries, PARSED_DIR

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

MIN_CIT = 500          # only dicts with >= this many citations join F1
LINEAGE = [("PWG", "MW"), ("PW", "MW"), ("PWKVN", "MW"), ("PWG", "PW")]
NULLS = [("BHS", "MW"), ("AP", "MW"), ("BEN", "MW")]
_WS = re.compile(r"\s+")
_DIGIT = re.compile(r"\d")


def norm_ref(ref):
    """Full citation, normalized: uppercase, collapsed spaces, no trailing punctuation."""
    return _WS.sub(" ", ref).strip().upper().rstrip(". ,;")


def source_of(full):
    """The textual sigil: everything before the first digit (the volume/verse number)."""
    m = _DIGIT.search(full)
    return (full[:m.start()] if m else full).strip(" .,;")


def build(code):
    """k1 -> {full refs}, k1 -> {sources}, restricted to entries that cite."""
    full = collections.defaultdict(set)
    src = collections.defaultdict(set)
    for e in load_entries(code):
        k1 = e["k1"]
        if not k1 or not e["citations"]:
            continue
        for c in e["citations"]:
            nf = norm_ref(c)
            if nf:
                full[k1].add(nf)
                src[k1].add(source_of(nf))
    return full, src


def main():
    print("=" * 64)
    print("F1 — citation forensics (shared apparatus PWG/PW -> MW)")
    print("=" * 64)

    stats = json.load(open(os.path.join(PARSED_DIR, "_parse_stats.json"), encoding="utf-8"))
    codes = sorted((s["code"].upper() for s in stats if s["citations"] >= MIN_CIT))
    # NB "citations" here = <ls>-tagged only. SKD/VCP/INM cite densely in the indigenous
    # style (iti+authority, quotes) with no <ls> -> excluded for lack of the tag, NOT
    # citation-free. F1 compares the Western <ls> apparatus. See CITATION_TAGGING.md.
    print(f"\n<ls>-tagging dicts (>= {MIN_CIT} <ls> cites): {', '.join(codes)}")
    print("  (SKD/VCP/INM cite densely in the indigenous style with no <ls> -> see CITATION_TAGGING.md)")

    full = {}
    src = {}
    ref_lemmas = collections.defaultdict(set)     # full ref -> {(code,k1)} for corpus rarity
    for code in codes:
        f, s = build(code.lower())
        full[code], src[code] = f, s
        for k1, refs in f.items():
            for r in refs:
                ref_lemmas[r].add((code, k1))
    print("cited-lemma counts: " + " · ".join(f"{c}={len(full[c]):,}" for c in codes))

    # ---- pairwise overlap ----
    rows = []
    for a, b in itertools.combinations(codes, 2):
        fa, fb = full[a], full[b]
        shared = set(fa) & set(fb)
        if not shared:
            continue
        sj_sum = exact = atrunc = btrunc = comparable = 0
        for k1 in shared:
            sa, sb = src[a][k1], src[b][k1]
            inter = sa & sb
            uni = sa | sb
            if uni:
                sj_sum += len(inter) / len(uni)
            ex = fa[k1] & fb[k1]
            exact += len(ex)
            # truncation: a source cited by both, where one side keeps only the sigil
            for s0 in inter:
                a_full = any(r != s0 and source_of(r) == s0 for r in fa[k1])
                b_full = any(r != s0 and source_of(r) == s0 for r in fb[k1])
                a_bare = s0 in fa[k1]
                b_bare = s0 in fb[k1]
                if a_full and b_bare and not b_full:
                    btrunc += 1
                if b_full and a_bare and not a_full:
                    atrunc += 1
                comparable += 1
        n = len(shared)
        rows.append({
            "dict_a": a, "dict_b": b, "shared_cited_lemmas": n,
            "mean_source_jaccard": round(sj_sum / n, 4),
            "shared_exact_refs": exact,
            "b_truncates_a": btrunc, "a_truncates_b": atrunc,
            "comparable_sources": comparable,
        })
    rows.sort(key=lambda r: -r["mean_source_jaccard"])
    with open("data/forensic/citation_pair_overlap.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["dict_a", "dict_b", "shared_cited_lemmas",
                                          "mean_source_jaccard", "shared_exact_refs",
                                          "b_truncates_a", "a_truncates_b", "comparable_sources"])
        w.writeheader()
        w.writerows(rows)

    # ---- smoking guns: rare shared exact (lemma, ref) for PWG/PW -> MW ----
    def smoking(a, b, max_corpus_lemmas=4):
        out = []
        shared = set(full[a]) & set(full[b])
        for k1 in shared:
            for r in full[a][k1] & full[b][k1]:
                ncorp = len({lm for (_, lm) in ref_lemmas[r]})   # distinct lemmas citing r anywhere
                if ncorp <= max_corpus_lemmas:
                    out.append((ncorp, k1, r, a, b))
        out.sort(key=lambda t: (t[0], t[1]))
        return out

    gun_rows = []
    for a, b in [("PWG", "MW"), ("PW", "MW")]:
        for ncorp, k1, r, da, db in smoking(a, b):
            gun_rows.append({"lemma": k1, "shared_ref": r, "source_dict": da,
                             "inheritor": db, "corpus_lemmas_with_ref": ncorp})
    with open("data/forensic/shared_rare_citations.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["lemma", "shared_ref", "source_dict",
                                          "inheritor", "corpus_lemmas_with_ref"])
        w.writeheader()
        w.writerows(gun_rows)

    # ---- console ----
    rowmap = {(r["dict_a"], r["dict_b"]): r for r in rows}

    def get(a, b):
        return rowmap.get((a, b)) or rowmap.get((b, a))

    print("\n" + "=" * 64)
    print("Lineage vs null — do they cite the same sources for the same lemma?")
    print("=" * 64)
    print(f"  {'pair':12s} {'shared_lem':>10s} {'src_jacc':>9s} {'exact_ref':>10s} {'MW_trunc':>9s}")
    for a, b in LINEAGE + NULLS:
        r = get(a, b)
        if not r:
            print(f"  {a + '/' + b:12s}  (no shared cited lemmas)")
            continue
        mwt = r["b_truncates_a"] if r["dict_b"] == "MW" else r["a_truncates_b"]
        print(f"  {r['dict_a'] + '/' + r['dict_b']:12s} {r['shared_cited_lemmas']:>10,} "
              f"{r['mean_source_jaccard']:>9.3f} {r['shared_exact_refs']:>10,} {mwt:>9,}")

    print("\nTop citation-overlap pairs (mean source Jaccard, >=500 shared lemmas):")
    for r in [x for x in rows if x["shared_cited_lemmas"] >= 500][:12]:
        print(f"  {r['dict_a'] + '/' + r['dict_b']:12s} jac={r['mean_source_jaccard']:.3f} "
              f"shared={r['shared_cited_lemmas']:,} exact={r['shared_exact_refs']:,}")

    print("\nSmoking guns — rare refs shared by PWG&MW for the SAME lemma (eyeball):")
    for g in gun_rows[:15]:
        print(f"  {g['lemma']:18s} cites {g['shared_ref']:22s} "
              f"(only {g['corpus_lemmas_with_ref']} lemma(s) cite it corpus-wide)")

    gun_sources = collections.Counter(source_of(g["shared_ref"]) for g in gun_rows)
    report = {
        "min_cit": MIN_CIT, "citation_dicts": codes,
        "citation_tagging_note": ("'citation_dicts' = <ls>-TAGGED dicts only. SKD (84,616 iti) "
                                  "and VCP (30,928 iti) are the corpus's MOST citation-dense dicts "
                                  "but use the indigenous style (iti+authority, quotes) with no "
                                  "<ls>, so they are absent here -- NOT citation-free. F1 compares "
                                  "the Western <ls> apparatus. See data/forensic/CITATION_TAGGING.md."),
        "n_pairs": len(rows), "n_smoking_guns": len(gun_rows),
        "smoking_gun_sources": dict(gun_sources.most_common(15)),
        "lineage": {f"{a}/{b}": get(a, b) for a, b in LINEAGE if get(a, b)},
        "nulls": {f"{a}/{b}": get(a, b) for a, b in NULLS if get(a, b)},
        "top_pairs": [r for r in rows if r["shared_cited_lemmas"] >= 500][:20],
        "interpretation": ("Citations are language-neutral. MW shares source-Jaccard 0.16-0.19 "
                           "with PWG/PW vs 0.004-0.017 with unrelated dicts (BHS/AP) = 10-40x the "
                           "null; 587 RARE exact refs (e.g. HARIV. <line>, SAH. 545) shared for the "
                           "SAME lemma; MW truncates PWG's full verse to a bare sigil 41,552x "
                           "(directional PWG->MW). Together: MW worked from Bohtlingk's apparatus / "
                           "editions. CAVEAT: a shared citation is a shared FACT (the word's locus), "
                           "not yet a shared ERROR -- independent use of the SAME edition could also "
                           "match. Airtight copy proof needs shared ERRONEOUS refs (verse numbers "
                           "that are WRONG), which requires the source texts as ground truth (F-next)."),
    }
    with open("data/forensic/f1_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nWrote citation_pair_overlap.csv ({len(rows)} pairs), "
          f"shared_rare_citations.csv ({len(gun_rows)} guns), f1_report.json")
    try:
        sys.path.insert(0, os.path.abspath("scripts/L0"))
        from _provenance import write_source
        write_source("data/forensic/citation_pair_overlap.csv", "f1_citations.py", 1)
    except Exception as e:
        print(f"Provenance error: {e}")


if __name__ == "__main__":
    main()
