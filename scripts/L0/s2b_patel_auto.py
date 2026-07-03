"""Stage 2b — mechanical pre-fill of the two *parseable* Patel conventions.

Per L0_DESIGN §12.2 ("Claude pre-fills ... auto-extracted dimensions where
parseable"), two of Patel's 7 canonical conventions are recoverable directly
from the headword stream without linguistic judgement:

  dim 2  Duplication after r  — old orthography geminates the consonant after a
         consonant-`r` (SLP1 `akarkkaSa`, `akarRRa`) where modern editions keep
         it single (`akarkaSa`, `akarRa`). A pure character-level test.
  dim 4  Inflected vs uninflected headword — citation form carries the nominative
         (visarga `-H`, neuter `-M`: `aMSaH`, `aMSakaM`) vs the bare stem
         (`aMSa`). A suffix test on k1.

The remaining five Patel dims (1 anusvāra-spelling, 3 -at sub-conventions,
5 verb-anusvāra, 6 ṛkārānta, 7 vas/yas) require the Patel-2016 schema or a
philological call and stay `unknown` for the M.G. co-annotation gate (§12.3).

This patches data/L0/convention_fingerprint.csv in place: it sets dim_2 / dim_4
(source = `auto-patel`) for every dict with a local source, then regenerates
annotation_todo.csv. Idempotent — safe to re-run after s2_fingerprint.py.
"""

import os
import sys
import re
import csv
import json
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_ROOT = os.path.normpath(os.path.join(REPO, "..", "csl-orig", "v02"))
FP = "data/L0/convention_fingerprint.csv"
CAP = 8000  # headwords are cheap; sample more for stable cluster-rate estimates

# SLP1 consonants (single chars; capitals = aspirate/retroflex/sibilant).
CONS = set("kKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzsh")
GEMINABLE = CONS - {"r"}  # we never count "rr" itself
HASH = re.compile(r"\{#(.*?)#\}", re.S)
STAG = re.compile(r"<s1?>(.*?)</s1?>", re.S)


def iter_k1(path, cap):
    """Yield k1 headwords (and inline Sanskrit tokens) up to cap entries."""
    n = 0
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("<L>") or line.startswith("<L "):
                m = re.search(r"<k1>([^<]*)", line)
                if m:
                    yield m.group(1)
                n += 1
                if n >= cap:
                    return


def measure(path):
    """Return (r_gemination_rate, n_rC, inflect_rate, n_k1)."""
    n_rC = gem = 0
    n_k1 = infl = 0
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        count = 0
        for line in f:
            if not (line.startswith("<L>") or line.startswith("<L ")):
                continue
            m = re.search(r"<k1>([^<]*)", line)
            if not m:
                continue
            hw = m.group(1).strip()
            if not hw:
                continue
            n_k1 += 1
            # dim 4 — inflected citation form: trailing visarga / neuter anusvara
            if hw.endswith("H") or hw.endswith("M"):
                infl += 1
            # dim 2 — gemination after consonant-r, scanned over the headword
            for i in range(len(hw) - 2):
                if hw[i] == "r" and hw[i + 1] in GEMINABLE:
                    n_rC += 1
                    if hw[i + 2] == hw[i + 1]:
                        gem += 1
            count += 1
            if count >= CAP:
                break
    r_gem = gem / n_rC if n_rC else None
    infl_rate = infl / n_k1 if n_k1 else None
    return r_gem, n_rC, infl_rate, n_k1


def classify_dim2(rate, n):
    if rate is None or n < 20:
        return None, None
    if rate >= 0.40:
        return "duplicated", round(min(0.85, 0.55 + rate / 2), 2)
    if rate <= 0.08:
        return "single", round(min(0.85, 0.55 + (1 - rate) / 2.5), 2)
    return "mixed", 0.55


def classify_dim4(rate, n):
    if rate is None or n < 20:
        return None, None
    if rate >= 0.15:
        return "inflected", round(min(0.85, 0.5 + rate), 2)
    if rate <= 0.05:
        return "uninflected", round(min(0.85, 0.55 + (1 - rate) / 2.5), 2)
    return "uninflected", 0.6  # low but non-zero visarga share → still stem-cited


def main():
    rows = []
    with open(FP, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    report = {}
    patched2 = patched4 = 0
    for r in rows:
        code = r["dict"]
        path = os.path.join(SRC_ROOT, code.lower(), code.lower() + ".txt")
        if not os.path.isfile(path):
            report[code] = "no-source"
            continue
        r_gem, n_rC, infl, n_k1 = measure(path)
        v2, c2 = classify_dim2(r_gem, n_rC)
        v4, c4 = classify_dim4(infl, n_k1)
        if v2:
            r["dim_2_value"], r["dim_2_source"], r["dim_2_confidence"] = v2, "auto-patel", c2
            patched2 += 1
        if v4:
            r["dim_4_value"], r["dim_4_source"], r["dim_4_confidence"] = v4, "auto-patel", c4
            patched4 += 1
        report[code] = {
            "r_gemination_rate": round(r_gem, 3) if r_gem is not None else None,
            "n_rC": n_rC, "dim2": v2,
            "inflect_rate": round(infl, 3) if infl is not None else None,
            "n_k1": n_k1, "dim4": v4,
        }

    with open(FP, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    # regenerate annotation_todo.csv from the patched matrix
    with open("data/L0/dim_schema.json", "r", encoding="utf-8") as f:
        dims = json.load(f)
    name_by_id = {d["dim_id"]: d["name"] for d in dims}
    opts_by_id = {d["dim_id"]: "|".join(d["options"]) for d in dims}
    todos = []
    for r in rows:
        for d in range(1, 31):
            if r[f"dim_{d}_source"] == "unknown":
                todos.append({"dict": r["dict"], "dim_id": d,
                              "dim_name": name_by_id[d],
                              "options_available": opts_by_id[d]})
    with open("data/L0/annotation_todo.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["dict", "dim_id", "dim_name", "options_available"])
        w.writeheader()
        w.writerows(todos)

    with open("data/L0/patel_auto_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # console: dim 2 / dim 4 calls, sorted, so the lineage signal is eyeballable
    print(f"dim 2 (r-duplication) patched: {patched2} dicts")
    print(f"dim 4 (inflected headword) patched: {patched4} dicts")
    print(f"annotation_todo rows now: {len(todos)}\n")
    print(f"{'dict':6s} {'r_gem':>6s} {'n_rC':>6s} {'dim2':>11s}   {'infl':>6s} {'n_k1':>6s} {'dim4':>11s}")
    for code, v in report.items():
        if v == "no-source":
            print(f"{code:6s}  (no local source)")
            continue
        print(f"{code:6s} {str(v['r_gemination_rate']):>6s} {v['n_rC']:>6d} {str(v['dim2']):>11s}   "
              f"{str(v['inflect_rate']):>6s} {v['n_k1']:>6d} {str(v['dim4']):>11s}")

    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from _provenance import write_source
        write_source(FP, "s2b_patel_auto.py", 2)
    except Exception as e:
        print(f"Provenance error: {e}")


if __name__ == "__main__":
    main()
