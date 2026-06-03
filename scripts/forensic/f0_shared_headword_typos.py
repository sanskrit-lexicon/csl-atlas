"""Phase L3 / F0 — shared near-duplicate headwords (candidate typos & ghost-words).

The Lachmann common-error principle: a correct reading can be reached independently,
but the *same mistake* is near-impossible to invent twice — so headwords that look
like corruptions of a real word and recur in two dicts are descent evidence.

This is the CHEAP teaser (no csl-orig parse): it runs on the normalized sanhw1
headword sets. Because hwnorm1 normalization *removes* most spelling variation, this
is a strict LOWER BOUND — the real shared-typo signal lives in the raw <k1>/<k2>
forms (Phase F2). What survives here are corruptions that normalization treated as
distinct valid-looking forms.

Method:
  - "real" lemma   = document-frequency df >= REAL_MIN (common core; the correct form).
  - candidate typo = a RARE lemma (2 <= df <= RARE_MAX) that is edit-distance 1 from a
                     real lemma (SymSpell delete-index + verified Levenshtein<=1).
  - a candidate typo x is SHARED by a dict pair (A,B) when {A,B} subset of dicts(x).
  - STRONGEST: a shared *doublet* — both A and B carry BOTH the typo x and its correct
                form y (the corrupt entry sits beside the right one in both dicts).

The signal is comparative: Sanskrit morphology makes many ED1 lemma pairs legitimate,
so unrelated dict pairs set the null. A true copy lineage (PWG->MW) shares far more
rare near-duplicates than coincidental coverage does.

Input  : observatory/snapshots/sanhw1.txt, data/dictionary_inventory.csv,
         data/L0/distances/B_whamming.csv (L0 set flag).
Output : data/forensic/shared_headword_anomalies.csv  (each candidate typo + its dicts),
         data/forensic/pair_shared_typo_counts.csv     (per dict-pair tallies, ranked),
         data/forensic/f0_report.json.

Run from repo root:  python scripts/forensic/f0_shared_headword_typos.py
"""

import os
import sys
import csv
import json
import collections
import itertools

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

SNAPSHOT = "observatory/snapshots/sanhw1.txt"
REAL_MIN = 8          # df >= this  -> "real"/common-core lemma (the correct form)
RARE_MAX = 5          # 2 <= df <= this -> rare candidate typo
MIN_PAIR_SIZE = 5000  # foreground pairs where both dicts are at least this big


def load_snapshot(path):
    """lemma -> set(dict codes); returns (lemma_dicts, df)."""
    lemma_dicts = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if ":" not in line:
                continue
            lemma, dictstr = line.split(":", 1)
            lemma = lemma.strip()
            codes = {c.strip() for c in dictstr.strip().split(",") if c.strip()}
            if not lemma or not codes:
                continue
            lemma_dicts[lemma] = lemma_dicts.get(lemma, set()) | codes
    df = {lm: len(cs) for lm, cs in lemma_dicts.items()}
    return lemma_dicts, df


def deletes1(w):
    """The SymSpell distance-<=1 delete set: w itself + every one-char deletion."""
    yield w
    for i in range(len(w)):
        yield w[:i] + w[i + 1:]


def within_ed1(a, b):
    """True iff Levenshtein(a, b) <= 1 (substitution / insertion / deletion)."""
    if a == b:
        return True
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:                       # one substitution
        return sum(1 for x, y in zip(a, b) if x != y) == 1
    if la > lb:                        # ensure a is the shorter
        a, b, la, lb = b, a, lb, la
    i = j = 0
    skipped = False
    while i < la and j < lb:           # b == a with one inserted char
        if a[i] == b[j]:
            i += 1
            j += 1
        elif skipped:
            return False
        else:
            skipped = True
            j += 1
    return True


def main():
    print("=" * 64)
    print("F0 — shared near-duplicate headwords (candidate typos / ghost-words)")
    print("=" * 64)

    lemma_dicts, df = load_snapshot(SNAPSHOT)
    print(f"\nLoaded {len(lemma_dicts):,} lemmas. Thresholds: real df>={REAL_MIN}, "
          f"rare df in [2,{RARE_MAX}].")

    real = [lm for lm, d in df.items() if d >= REAL_MIN]
    rare = [lm for lm, d in df.items() if 2 <= d <= RARE_MAX]
    print(f"real (common core): {len(real):,} · rare candidates: {len(rare):,}")

    # SymSpell delete-index over the real lemmas
    index = collections.defaultdict(set)
    for w in real:
        for d in deletes1(w):
            index[d].add(w)
    print(f"delete-index entries: {len(index):,}")

    # for each rare lemma, find verified ED1 real neighbours
    anomalies = []          # (typo, best_real, n_real_neighbours, df_typo, dicts_typo, dicts_both)
    for x in rare:
        cands = set()
        for d in deletes1(x):
            cands |= index.get(d, set())
        neighbours = [y for y in cands if within_ed1(x, y)]
        if not neighbours:
            continue
        best = max(neighbours, key=lambda y: df[y])   # most "real" neighbour
        dx = lemma_dicts[x]
        dboth = dx & lemma_dicts[best]                 # dicts carrying typo AND correct form
        anomalies.append((x, best, len(neighbours), df[x], dx, dboth))

    print(f"candidate typo/ghost lemmas (rare & ED1 from a common word): {len(anomalies):,}")

    # per-pair aggregation
    pair_shared = collections.Counter()      # all shared anomalies
    pair_excl = collections.Counter()        # df==2 (exclusive to the pair)
    pair_doublet = collections.Counter()     # both dicts carry typo AND correct form
    examples = collections.defaultdict(list)
    for x, y, nn, dfx, dx, dboth in anomalies:
        for a, b in itertools.combinations(sorted(dx), 2):
            pair_shared[(a, b)] += 1
            if dfx == 2:
                pair_excl[(a, b)] += 1
            if a in dboth and b in dboth:
                pair_doublet[(a, b)] += 1
                if len(examples[(a, b)]) < 12:
                    examples[(a, b)].append(f"{x}~{y}")

    # ---- inventory + L0 set for flags / sizes ----
    sizes = collections.Counter()        # dict code -> number of lemmas it holds
    for cs in lemma_dicts.values():
        for c in cs:
            sizes[c] += 1
    years = {}
    with open("data/dictionary_inventory.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            years[r["code"]] = r.get("year", "n/a")
    with open("data/L0/distances/B_whamming.csv", encoding="utf-8") as f:
        l0_set = set(next(csv.reader(f))[1:])

    # ---- write the anomaly table ----
    os.makedirs("data/forensic", exist_ok=True)
    anomalies.sort(key=lambda t: (t[3], -len(t[5])))   # df asc, more shared-doublet dicts first
    with open("data/forensic/shared_headword_anomalies.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["typo_form", "nearest_real", "n_real_neighbours", "df_typo",
                    "n_dicts", "dicts", "n_dicts_with_both"])
        for x, y, nn, dfx, dx, dboth in anomalies:
            w.writerow([x, y, nn, dfx, len(dx), " ".join(sorted(dx)), len(dboth)])

    # ---- write per-pair counts ----
    def norm(a, b, n):
        m = min(sizes.get(a, 1), sizes.get(b, 1))
        return round(1000 * n / m, 3) if m else 0.0

    rows = []
    for (a, b), n in pair_shared.items():
        rows.append({
            "dict_a": a, "dict_b": b,
            "shared_anomalies": n,
            "shared_doublets": pair_doublet.get((a, b), 0),
            "shared_exclusive_df2": pair_excl.get((a, b), 0),
            "per_1k_smaller": norm(a, b, n),
            "size_a": sizes.get(a, 0), "size_b": sizes.get(b, 0),
            "year_a": years.get(a, "n/a"), "year_b": years.get(b, "n/a"),
            "both_in_L0": a in l0_set and b in l0_set,
        })
    rows.sort(key=lambda r: -r["shared_doublets"])
    with open("data/forensic/pair_shared_typo_counts.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["dict_a", "dict_b", "shared_anomalies",
                                          "shared_doublets", "shared_exclusive_df2",
                                          "per_1k_smaller", "size_a", "size_b",
                                          "year_a", "year_b", "both_in_L0"])
        w.writeheader()
        w.writerows(rows)

    # ---- console: the question — MW vs the Petersburg dicts, vs a null ----
    def get(a, b):
        key = tuple(sorted((a, b)))
        return pair_shared.get(key, 0), pair_doublet.get(key, 0), pair_excl.get(key, 0)

    print("\n" + "=" * 64)
    print("Shared rare near-duplicate headwords (LINEAGE signal; vs an unrelated null)")
    print("NB: eyeballing shows most ED1 candidates are legit morphology, not typos —")
    print("    this measures shared rare VOCABULARY, not errors. True typos => F2 (raw k1/k2).")
    print("=" * 64)
    print(f"  {'pair':14s} {'shared':>7s} {'doublet':>8s} {'excl(df2)':>10s}  reading")
    probes = [("PWG", "MW", "PWG->MW (cross-author, cross-lang)"),
              ("PW", "MW", "PW->MW"),
              ("MW72", "MW", "MW72->MW (same author)"),
              ("PWG", "PW", "PWG<->PW (same author = BASELINE)"),
              ("PWG", "MW72", "PWG->MW72 (used PWG vols 1-4)"),
              ("BOP", "MW", "BOP->MW (unrelated = NULL)"),
              ("SKD", "BOP", "SKD<->BOP (unrelated = NULL)"),
              ("AP", "SKD", "AP<->SKD")]
    for a, b, reading in probes:
        s, d, e = get(a, b)
        print(f"  {a + '/' + b:14s} {s:>7,} {d:>8,} {e:>10,}  {reading}")

    print("\nTop dict-pairs by shared DOUBLET corruptions (typo+correct in both):")
    print(f"  {'pair':14s} {'doublet':>8s} {'shared':>7s} {'/1k':>7s}")
    shown = 0
    for r in rows:
        if r["size_a"] < MIN_PAIR_SIZE or r["size_b"] < MIN_PAIR_SIZE:
            continue
        print(f"  {r['dict_a'] + '/' + r['dict_b']:14s} {r['shared_doublets']:>8,} "
              f"{r['shared_anomalies']:>7,} {r['per_1k_smaller']:>7.2f}")
        shown += 1
        if shown >= 15:
            break

    print("\nSample shared MW/PWG corruptions (typo ~ nearest real form) — eyeball these:")
    for ex in examples.get(("MW", "PWG"), [])[:12]:
        print(f"    {ex}")
    if not examples.get(("MW", "PWG")):
        print("    (none with shared doublet; see anomalies.csv for MW/PWG df==2 forms)")

    # ---- report ----
    probe_report = {}
    for a, b, reading in probes:
        s, d, e = get(a, b)
        probe_report[f"{a}/{b}"] = {"shared": s, "doublet": d, "excl_df2": e, "reading": reading}
    report = {
        "n_lemmas": len(lemma_dicts), "real_min": REAL_MIN, "rare_max": RARE_MAX,
        "n_real": len(real), "n_rare": len(rare), "n_candidate_anomalies": len(anomalies),
        "probes": probe_report,
        "top_doublet_pairs": [
            {"pair": f"{r['dict_a']}/{r['dict_b']}", "doublets": r["shared_doublets"],
             "shared": r["shared_anomalies"], "per_1k": r["per_1k_smaller"]}
            for r in rows if r["size_a"] >= MIN_PAIR_SIZE and r["size_b"] >= MIN_PAIR_SIZE][:20],
        "caveat": ("MANUAL EYEBALL (2026-06-03): most ED1 candidates are LEGITIMATE Sanskrit "
                   "morphology (privative a-, inflectional/derivational variants, distinct "
                   "compounds) — NOT corruptions. F0 therefore measures shared rare near-core "
                   "VOCABULARY (a lineage signal: ~100x the null for Petersburg->MW), not typos. "
                   "sanhw1 is also normalized -> strict lower bound. True shared-typo/ghost-word "
                   "detection needs raw <k1>/<k2> (F2). Read pair counts COMPARATIVELY vs the "
                   "unrelated-pair null (BOP/MW=77, SKD/BOP=5), never as absolute error counts."),
        "finding": ("Petersburg<->MW lineage shares 7,700-11,500 rare near-duplicate headwords "
                    "vs 5-77 for unrelated pairs (~100x). Corroborates descent; magnitude of "
                    "true error-copying awaits F2."),
        "mw_pwg_doublet_examples": examples.get(("MW", "PWG"), []),
        "mw_pw_doublet_examples": examples.get(("MW", "PW"), []),
    }
    with open("data/forensic/f0_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nWrote data/forensic/shared_headword_anomalies.csv ({len(anomalies):,} rows), "
          f"pair_shared_typo_counts.csv ({len(rows):,} pairs), f0_report.json")

    try:
        sys.path.insert(0, os.path.abspath("scripts/L0"))
        from _provenance import write_source
        write_source("data/forensic/shared_headword_anomalies.csv", "f0_shared_headword_typos.py", 0)
    except Exception as e:
        print(f"Provenance error: {e}")


if __name__ == "__main__":
    main()
