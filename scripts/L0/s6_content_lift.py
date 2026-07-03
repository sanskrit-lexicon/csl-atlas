"""Stage 6 (Phase L0, handoff §3/§4 item A) — de-confounding the MW
"content-absorption" claim.

L0_RESULTS / Paper-H reported MW "absorbed 89-94% of PWG/MW72 content" using
raw headword containment  ca(A->B) = |A & B| / |A|.  L0_HANDOFF §3 shows that
number is SIZE-CONFOUNDED: containment falls monotonically with source size and
is *highest* for the unrelated, tiny BOP (0.94). MW (194k lemmas) contains almost
any older dict's mostly-common-core vocabulary regardless of descent, so raw
containment measures MW's coverage x the source's rarity profile, not inheritance.

This stage replaces raw containment with two size-aware instruments (the
handoff "ladder", steps 1-2):

  step 1  LIFT   = observed_overlap / expected_overlap_given_sizes
                 = |A & B| * N / (|A| * |B|)          (PMI = log2 lift)
          Corrects for "B is huge so overlap is expected". >1 = more than chance.

  step 2  RARE-LEMMA CONTAINMENT  (the single highest-value computation, §3):
          drop the common core, keep only A's *rare* lemmas (document-frequency
          df <= k across all dicts), and ask what fraction recur in B.
          A true content heir contains the source's idiosyncratic/rare lemmas at
          a high rate; a big dict coincidentally covering the common core does not.

  bonus   EXCLUSIVE-PAIR lemmas (df == 2, the two dicts being exactly {A,B}):
          maximally idiosyncratic shared headwords — a cheap forensic copy signal.

Document-frequency comes free: each sanhw1 line lists ALL dicts holding the lemma,
so df(lemma) = len(that list).

Input  : observatory/snapshots/sanhw1.txt  (lemma:DICT,DICT,... ; ~470k lemmas),
         data/dictionary_inventory.csv      (years),
         data/L0/distances/B_whamming.csv   (the 32-dict L0 convention set),
         data/sanhw1_inheritance_edges.csv  (raw-containment baseline + validation).
Output : data/L0/content_lift.csv           (every ordered pair: all instruments),
         data/L0/exclusive_pair_lemmas.csv   (top df==2 exclusive pairs + examples),
         data/L0/content_lift_report.json    (validation + into-MW re-ranking + lineages).

Run from repo root:  python scripts/L0/s6_content_lift.py
"""

import os
import sys
import csv
import json
import math
import collections

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

SNAPSHOT = "observatory/snapshots/sanhw1.txt"
RARE_K = (2, 3, 5)            # document-frequency thresholds for "rare"
MIN_RARE_DENOM = 30          # ignore rare-containment ratios on tiny denominators in headline tables

# Established numbers from the committed raw-containment edges (lex_l2_cladogram.py
# read THIS snapshot); the loader must reproduce them or something has drifted.
EXPECT_SIZE = {"MW": 194084, "PW": 151349, "PWG": 106083, "BOP": 8505}
EXPECT_INTER = {("BOP", "MW"): 7995}


def load_snapshot(path):
    """lemma:DICT,DICT,... -> (dict_lemmas {code: set[int]}, df list, N, excl_pairs).

    Lemmas are interned to int ids for fast set intersection. df[id] is the lemma's
    document frequency (how many dicts hold it). Duplicate lemma lines are unioned.
    """
    lemma_codes = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if ":" not in line:
                continue
            lemma, dictstr = line.split(":", 1)
            lemma = lemma.strip()
            codes = {c.strip() for c in dictstr.strip().split(",") if c.strip()}
            if not lemma or not codes:
                continue
            if lemma in lemma_codes:
                lemma_codes[lemma] |= codes
            else:
                lemma_codes[lemma] = codes

    n = len(lemma_codes)
    dict_lemmas = collections.defaultdict(set)
    df = [0] * n
    excl_pairs = collections.Counter()   # df==2 -> the exact {A,B} pair
    excl_examples = collections.defaultdict(list)
    for i, (lemma, codes) in enumerate(lemma_codes.items()):
        df[i] = len(codes)
        for c in codes:
            dict_lemmas[c].add(i)
        if len(codes) == 2:
            pair = tuple(sorted(codes))
            excl_pairs[pair] += 1
            if len(excl_examples[pair]) < 5:
                excl_examples[pair].append(lemma)
    return dict_lemmas, df, n, excl_pairs, excl_examples


def main():
    print("=" * 64)
    print("L0 stage 6 — size-corrected lift + rare-lemma containment")
    print("=" * 64)

    dict_lemmas, df, N, excl_pairs, excl_examples = load_snapshot(SNAPSHOT)
    dicts = sorted(dict_lemmas.keys())
    print(f"\nLoaded {N:,} distinct lemmas across {len(dicts)} dicts "
          f"({sum(len(s) for s in dict_lemmas.values()):,} lemma-dict pairs)")

    # document-frequency distribution (context for "rare")
    df_hist = collections.Counter(df)
    print("df distribution (lemmas in exactly k dicts):")
    for k in range(1, 9):
        print(f"  df={k}: {df_hist.get(k, 0):>8,}", end="")
    print(f"  df>=9: {sum(v for k, v in df_hist.items() if k >= 9):>8,}")

    # ---- self-validation against the committed baseline (the §5 lesson) ----
    checks, ok = [], True
    for code, exp in EXPECT_SIZE.items():
        got = len(dict_lemmas.get(code, set()))
        passed = got == exp
        ok &= passed
        checks.append({"check": f"|{code}|", "expected": exp, "got": got, "pass": passed})
    for (a, b), exp in EXPECT_INTER.items():
        got = len(dict_lemmas[a] & dict_lemmas[b])
        passed = got == exp
        ok &= passed
        checks.append({"check": f"|{a}&{b}|", "expected": exp, "got": got, "pass": passed})
    print(f"\nLoader validation vs committed edges: {'PASS' if ok else 'FAIL'}")
    for c in checks:
        print(f"  {'ok ' if c['pass'] else 'XX '} {c['check']:12s} expected {c['expected']:>7,}  got {c['got']:>7,}")
    if not ok:
        print("  WARNING: snapshot differs from the numbers behind sanhw1_inheritance_edges.csv",
              file=sys.stderr)

    # ---- supporting metadata ----
    years = {}
    with open("data/dictionary_inventory.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            years[r["code"]] = r.get("year", "n/a")

    with open("data/L0/distances/B_whamming.csv", encoding="utf-8") as f:
        l0_set = set(next(csv.reader(f))[1:])

    # precompute per-dict rare-lemma sets at each threshold
    rare = {k: {c: {i for i in s if df[i] <= k} for c, s in dict_lemmas.items()} for k in RARE_K}

    def yr(code):
        return years.get(code, "n/a")

    def temporal_ok(a, b):
        ya, yb = yr(a), yr(b)
        try:
            return ya == "n/a" or yb == "n/a" or int(ya) <= int(yb)
        except ValueError:
            return True

    # ---- all ordered pairs: full instrument panel ----
    rows = []
    for a in dicts:
        sa = dict_lemmas[a]
        na = len(sa)
        if na == 0:
            continue
        for b in dicts:
            if a == b:
                continue
            sb = dict_lemmas[b]
            nb = len(sb)
            if nb == 0:
                continue
            inter = len(sa & sb)
            containment = inter / na
            expected = na * nb / N
            lift = inter / expected if expected else 0.0
            row = {
                "source": a, "inheritor": b,
                "source_size": na, "inheritor_size": nb, "intersection": inter,
                "containment": round(containment, 4),
                "lift": round(lift, 3),
                "pmi": round(math.log2(lift), 3) if lift > 0 else "",
            }
            for k in RARE_K:
                ra = rare[k][a]
                denom = len(ra)
                rc = len(ra & sb) / denom if denom else 0.0
                row[f"rare_cont_{k}"] = round(rc, 4)
                row[f"src_rare_{k}"] = denom
            row["excl_pair"] = excl_pairs.get(tuple(sorted((a, b))), 0)
            row["source_year"] = yr(a)
            row["inheritor_year"] = yr(b)
            row["temporal_plausible"] = temporal_ok(a, b)
            row["both_in_L0"] = a in l0_set and b in l0_set
            rows.append(row)

    rows.sort(key=lambda r: -r["rare_cont_3"])
    fieldnames = (["source", "inheritor", "source_size", "inheritor_size", "intersection",
                   "containment", "lift", "pmi"]
                  + [f"{m}_{k}" for k in RARE_K for m in ("rare_cont", "src_rare")]
                  + ["excl_pair", "source_year", "inheritor_year", "temporal_plausible", "both_in_L0"])
    os.makedirs("data/L0", exist_ok=True)
    with open("data/L0/content_lift.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    # ---- exclusive-pair table ----
    excl_sorted = sorted(excl_pairs.items(), key=lambda kv: -kv[1])
    with open("data/L0/exclusive_pair_lemmas.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dict_a", "dict_b", "n_exclusive_lemmas", "examples"])
        for (a, b), n in excl_sorted:
            w.writerow([a, b, n, " ".join(excl_examples[(a, b)])])

    # ---- the into-MW re-ranking: the §3 correction in one table ----
    into_mw = sorted((r for r in rows if r["inheritor"] == "MW" and r["src_rare_3"] >= MIN_RARE_DENOM),
                     key=lambda r: -r["rare_cont_3"])
    print("\n" + "=" * 64)
    print("Edges INTO MW — raw containment vs size-aware instruments")
    print("(raw ranks the unrelated BOP top; rare-lemma containment re-ranks)")
    print("=" * 64)
    print(f"  {'source':7s} {'size':>7s} {'raw_cont':>8s} {'lift':>6s} "
          f"{'rare@3':>7s} {'excl':>6s}  lineage")
    note = {"BOP": "unrelated (Latin etym.)", "MW72": "direct (same author)",
            "PWG": "direct", "PW": "direct", "BEN": "weak", "CCS": "German", "MD": "-"}
    for r in into_mw:
        print(f"  {r['source']:7s} {r['source_size']:>7,} {r['containment']:>8.3f} "
              f"{r['lift']:>6.2f} {r['rare_cont_3']:>7.3f} {r['excl_pair']:>6,}  "
              f"{note.get(r['source'], '')}")

    # ---- canonical lineage pairs ----
    canon = [("PWG", "PW"), ("WIL", "SHS"), ("WIL", "YAT"), ("PWKVN", "PW"),
             ("PWG", "MW"), ("MW72", "MW"), ("BOP", "MW")]
    rowmap = {(r["source"], r["inheritor"]): r for r in rows}
    print("\nCanonical lineage pairs:")
    print(f"  {'edge':14s} {'raw_cont':>8s} {'lift':>6s} {'rare@2':>7s} {'rare@3':>7s} {'rare@5':>7s} {'excl':>6s}")
    canon_report = []
    for a, b in canon:
        r = rowmap.get((a, b))
        if not r:
            continue
        print(f"  {a + '->' + b:14s} {r['containment']:>8.3f} {r['lift']:>6.2f} "
              f"{r['rare_cont_2']:>7.3f} {r['rare_cont_3']:>7.3f} {r['rare_cont_5']:>7.3f} {r['excl_pair']:>6,}")
        canon_report.append({"edge": f"{a}->{b}", "raw_containment": r["containment"],
                             "lift": r["lift"], "rare_cont_2": r["rare_cont_2"],
                             "rare_cont_3": r["rare_cont_3"], "rare_cont_5": r["rare_cont_5"],
                             "excl_pair": r["excl_pair"]})

    print("\nTop exclusive-pair lineages (lemmas shared by exactly two dicts):")
    for (a, b), n in excl_sorted[:10]:
        print(f"  {a + '/' + b:14s} {n:>6,}   e.g. {' '.join(excl_examples[(a, b)][:4])}")

    # ---- report ----
    report = {
        "n_lemmas": N, "n_dicts": len(dicts),
        "rare_thresholds": list(RARE_K),
        "loader_validation": {"pass": ok, "checks": checks},
        "df_distribution": {str(k): df_hist.get(k, 0) for k in range(1, 9)},
        "into_MW_reranked": [
            {"source": r["source"], "source_size": r["source_size"],
             "raw_containment": r["containment"], "lift": r["lift"],
             "rare_cont_3": r["rare_cont_3"], "excl_pair": r["excl_pair"]}
            for r in into_mw],
        "canonical_lineages": canon_report,
        "top_exclusive_pairs": [
            {"pair": f"{a}/{b}", "n": n, "examples": excl_examples[(a, b)]}
            for (a, b), n in excl_sorted[:15]],
        "interpretation": (
            "Raw containment is size-confounded (highest for the unrelated BOP). "
            "Rare-lemma containment (rare_cont_k: fraction of the source's df<=k lemmas "
            "recurring in the inheritor) drops the common core and isolates idiosyncratic "
            "overlap -- true content heirs (PWG->MW, MW72->MW) score high, coincidental "
            "coverage (BOP->MW) scores low. Report content claims as rare-lemma containment "
            "or lift, never raw containment."),
    }
    with open("data/L0/content_lift_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nWrote data/L0/content_lift.csv ({len(rows)} ordered pairs), "
          f"exclusive_pair_lemmas.csv ({len(excl_sorted)} pairs), content_lift_report.json")

    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from _provenance import write_source
        write_source("data/L0/content_lift.csv", "s6_content_lift.py", 6)
    except Exception as e:
        print(f"Provenance error: {e}")


if __name__ == "__main__":
    main()
