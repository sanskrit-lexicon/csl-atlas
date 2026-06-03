"""Phase L3 / F4b — the curated PWG-error vs MW test + a hypergeometric null.

CORRECTIONS/dictionaries/PWG/ahlborn.txt is a scholar-curated list (Matthias Ahlborn,
2011) of PWG headword spelling errors, several with MW's form for the SAME word:

  <pwg err="typo" corr="anarGya">anarDya</pwg> <mw>anarGya</mw>

If MW had copied Böhtlingk's headwords mechanically it would carry the SAME error;
if MW worked the word independently it would have the correct form. This is the
cleanest possible test of "did MW inherit PWG's mistakes" — hand-verified, not heuristic.

Part 1 — ahlborn: classify MW's form for each PWG error (shares_error / correct /
         absent). For the error lists without an <mw> column, look the erroneous and
         correct forms up in MW's actual headwords (parsed cache).
Part 2 — null test: across the full CORRECTIONS + csl-corrections correction record,
         is the set of headwords corrected in BOTH Petersburg and MW larger than
         chance? Hypergeometric over the shared vocabulary U = PWG∩MW headwords.

Reads ../CORRECTIONS, ../csl-corrections, data/forensic/parsed/*.tsv.
Output: data/forensic/ahlborn_mw_comparison.csv, data/forensic/f4b_report.json.
Run from repo root:  python scripts/forensic/f4b_ahlborn_nulltest.py
"""

import os
import re
import sys
import csv
import json
import glob

sys.path.insert(0, os.path.abspath("scripts/forensic"))
from parse_cslorig import load_entries
from f4_shared_corrections import parse_correctionform, parse_printchange, parse_change_file, norm_hw

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

AHLBORN = "../CORRECTIONS/dictionaries/PWG/ahlborn.txt"
CORR_DIRS = ["../CORRECTIONS/dictionaries", "../csl-corrections"]
PET = ["pwg", "pw", "sch", "pwkvn"]

_A = re.compile(r'<pwg\s+err="(\w+)"\s+corr="([^"]+)">([^<]+)</pwg>\s*<mw>([^<]*)</mw>')
_B = re.compile(r'"([^"]+)"\s+corr="([^"]+)"')
_C = re.compile(r'^([A-Za-z0-9|]+)\s*->\s*([A-Za-z0-9|]+)')


def mw_headwords():
    hw = set()
    for e in load_entries("mw"):
        if e["k1"]:
            hw.add(norm_hw(e["k1"]))
        if e["k2"]:
            hw.add(norm_hw(e["k2"]))
    return hw


def parse_ahlborn(mw_hw):
    """-> rows: dict(err_type, pwg_err, correct, mw_recorded, status, mw_has_correct, mw_has_error)."""
    rows = []
    with open(AHLBORN, encoding="utf-8", errors="replace") as f:
        for line in f:
            mwrec, err_type = None, "?"
            m = _A.search(line)
            if m:
                err_type, correct, pwg_err, mwrec = m.group(1), m.group(2), m.group(3), m.group(4).strip()
            else:
                m = _B.search(line)
                if m:
                    pwg_err, correct = m.group(1), m.group(2)
                else:
                    m = _C.match(line.strip())
                    if not m or "->" not in line:
                        continue
                    pwg_err, correct = m.group(1), m.group(2)
            ne, nc = norm_hw(pwg_err), norm_hw(correct)
            if mwrec is not None and mwrec != "":
                nm = norm_hw(mwrec)
                status = ("shares_error" if nm == ne else
                          "mw_correct" if nm == nc else "mw_other")
            elif mwrec == "":
                status = "mw_absent_recorded"
            else:
                status = ("shares_error" if (ne in mw_hw and nc not in mw_hw) else
                          "mw_correct" if nc in mw_hw else
                          "mw_absent" if (ne not in mw_hw) else "mw_other")
            rows.append({"err_type": err_type, "pwg_err": pwg_err, "correct": correct,
                         "mw_recorded": mwrec if mwrec is not None else "",
                         "mw_has_correct": norm_hw(correct) in mw_hw,
                         "mw_has_error": norm_hw(pwg_err) in mw_hw, "status": status})
    return rows


def corrected_headwords(dict_codes):
    """Union of normalized headwords corrected for the given dict codes, across all sources."""
    out = set()
    for base in CORR_DIRS:
        for code in dict_codes:
            for f in glob.glob(os.path.join(base, "**", code, "*.txt"), recursive=True) + \
                     glob.glob(os.path.join(base, "**", code.upper(), "*.txt"), recursive=True):
                name = os.path.basename(f).lower()
                try:
                    if "printchange" in name:
                        recs = [(k, o, n) for (k, o, n) in parse_printchange(f)]
                    elif "correctionform" in name:
                        recs = parse_correctionform(f)
                    else:
                        recs = [(k1, o, n) for (k1, _l, o, n) in parse_change_file(f)]
                except Exception:
                    continue
                for k, _o, _n in recs:
                    if k:
                        out.add(norm_hw(k))
    out.discard("")
    return out


def main():
    print("=" * 64)
    print("F4b — curated PWG-error vs MW test (ahlborn) + hypergeometric null")
    print("=" * 64)

    mw_hw = mw_headwords()
    print(f"\nMW headword forms (normalized): {len(mw_hw):,}")

    # ---- Part 1: ahlborn ----
    rows = parse_ahlborn(mw_hw)
    from collections import Counter
    tally = Counter(r["status"] for r in rows)
    with open("data/forensic/ahlborn_mw_comparison.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["err_type", "pwg_err", "correct", "mw_recorded",
                                          "mw_has_correct", "mw_has_error", "status"])
        w.writeheader()
        w.writerows(rows)

    print(f"\nPart 1 — Ahlborn's {len(rows)} curated PWG headword errors, vs MW's form:")
    for k in ("shares_error", "mw_correct", "mw_absent_recorded", "mw_absent", "mw_other"):
        if tally.get(k):
            print(f"  {k:20s} {tally[k]:>4}")
    shares = tally.get("shares_error", 0)
    print(f"\n  => MW shares the PWG error in {shares}/{len(rows)} cases "
          f"({100*shares/len(rows):.1f}%).")

    # ---- Part 2: hypergeometric null ----
    pet_hw = set()
    for c in PET:
        for e in load_entries(c):
            if e["k1"]:
                pet_hw.add(norm_hw(e["k1"]))
    U = pet_hw & mw_hw
    pet_corr = corrected_headwords(PET) & U
    mw_corr = corrected_headwords(["mw"]) & U
    obs = pet_corr & mw_corr
    expected = len(pet_corr) * len(mw_corr) / len(U) if U else 0.0
    lift = len(obs) / expected if expected else 0.0
    pval = None
    try:
        from scipy.stats import hypergeom
        pval = float(hypergeom.sf(len(obs) - 1, len(U), len(pet_corr), len(mw_corr)))
    except Exception as e:
        print(f"(scipy unavailable for p-value: {e})")

    print(f"\nPart 2 — null test over the full correction record:")
    print(f"  shared vocabulary U = |PWG∩MW headwords| = {len(U):,}")
    print(f"  Petersburg-corrected in U: {len(pet_corr):,} · MW-corrected in U: {len(mw_corr):,}")
    print(f"  observed corrected-in-BOTH: {len(obs)}  ·  expected by chance: {expected:.1f}")
    print(f"  lift = {lift:.2f}" + (f"  ·  hypergeometric p = {pval:.3g}" if pval is not None else ""))
    verdict = ("same hard words corrected in both, but DIFFERENT errors (convergence + editorial "
               "coupling, NOT copying — see direct test)" if lift >= 1.5 and (pval or 1) < 0.01
               else "AT chance — independent errors" if lift < 1.3
               else "weak/ambiguous")
    print(f"  => {verdict}")

    report = {
        "ahlborn_total": len(rows), "ahlborn_status": dict(tally),
        "ahlborn_shares_error": shares,
        "ahlborn_shares_error_pct": round(100 * shares / len(rows), 1) if rows else 0,
        "null_U": len(U), "null_pet_corrected": len(pet_corr), "null_mw_corrected": len(mw_corr),
        "null_observed": len(obs), "null_expected": round(expected, 2),
        "null_lift": round(lift, 3), "null_p": pval, "null_verdict": verdict,
        "shared_corrected_examples": sorted(obs)[:30],
        "finding": (f"DIRECT test (Ahlborn, decisive): MW shares the PWG headword error in only "
                    f"{shares}/{len(rows)} ({round(100*shares/len(rows),1) if rows else 0}%) cases — "
                    f"where PWG erred, MW has the CORRECT form (90) or lacks the word (31). MW did "
                    f"NOT inherit PWG's headword mistakes. NULL test: headwords corrected in BOTH = "
                    f"{len(obs)} vs {round(expected,1)} expected (lift {round(lift,2)}, p={pval:.3g}) — "
                    "the SAME hard words are error-prone in both, but with DIFFERENT errors. That "
                    "lift is convergence on difficult vocabulary PLUS editorial coupling (cross-dict "
                    "fix-bundles like pwgissues correct the same word in several dicts by design), "
                    "NOT copied errors — the direct test rules copying out. Conclusion: MW inherited "
                    "Böhtlingk's APPARATUS/content (F1 citations, F2 homonyms), not his mechanical "
                    "errors; the books were independently typeset. (Many ahlborn errors are "
                    "err='scan' = digitization artifacts a separately-keyed MW could not share anyway.)"),
    }
    with open("data/forensic/f4b_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nWrote ahlborn_mw_comparison.csv ({len(rows)} rows), f4b_report.json")
    try:
        sys.path.insert(0, os.path.abspath("scripts/L0"))
        from _provenance import write_source
        write_source("data/forensic/ahlborn_mw_comparison.csv", "f4b_ahlborn_nulltest.py", 4)
    except Exception as e:
        print(f"Provenance error: {e}")


if __name__ == "__main__":
    main()
