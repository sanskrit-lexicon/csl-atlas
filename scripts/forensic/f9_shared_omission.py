#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""f9 — the shared-OMISSION test (Böhtlingk item #1).

Historical claim under test
---------------------------
In the Böhtlingk <-> Max Müller correspondence (Stache-Weiske 2015), Müller's
letter of 11 June 1881 formulates the plagiarism charge against Monier-Williams
as, verbatim:

    "Was in Ihrem Werk ausgelassen u[nd] versehen ist, ist bei ihm ausgelassen
     und versehen"  --  what is OMITTED/erroneous in your work [PW] is omitted
     and erroneous in his [MW].

A10 (``article_21_apparatus_not_errors.md``) has already run the *shared-error*
half of that sentence three ways (F4b Ahlborn misspellings ~0%; F4a print
errors 0; F7 Harivamsa shared-erroneous citations = measured null). It never ran
the *shared-OMISSION* half. This script does.

The idea (the negative-space complement of A10 s3.1 "shared presence")
-----------------------------------------------------------------------
Take REAL Sanskrit words that lie OUTSIDE the European Petersburg lineage
entirely -- headwords attested in BOTH major indigenous kosa/encyclopaedic
dictionaries, Sabdakalpadruma (SKD) and Vacaspatyam (VCP). A word both of those
list is unquestionably a real, established word that a European compiler *could*
have entered. Call this anchor set R.

Among R, partition by whether PWG (Bohtlingk-Roth) contains the word. PWG's
BLIND SPOTS = real indigenous words PWG nonetheless lacks. The question:

    does MW disproportionately share PWG's blind spots -- i.e. lack exactly the
    words PWG lacks -- BEYOND what word-rarity alone would predict?

The commonness confound (identical to A10 s4.2's "same hard words" trap)
------------------------------------------------------------------------
A word rare enough that PWG missed it is rare enough that *anyone* might miss it,
so a raw shared-omission lift is confounded by rarity, not copying. The decisive
control is an INDEPENDENT dictionary: Apte (AP, 1890), the independent
English-tradition dict A10 already uses as its citation null. If MW tracks PWG's
omissions MORE than the independent Apte does -- and especially if MW does so
DESPITE being ~2x larger than Apte (194k vs 89k lemmas), which should make MW
*fill* more gaps, not fewer -- that differential is the copy signal net of rarity.

Estimator (size-normalised, control-anchored)
---------------------------------------------
For each candidate dict D in {MW, AP}:
    gap_sensitivity(D) = P(D lacks w | PWG lacks w, w in R)
                         -------------------------------------
                         P(D lacks w | PWG has  w, w in R)
A dict whose omission rate rises steeply on PWG's blind spots (ratio >> 1) is
tracking PWG's inventory gaps. Compare MW's ratio to the independent Apte's.

Inputs are the canonical CDSL key1 headword exports (normalised SLP1 join keys,
one per line) in ``SanskritLexicography/HeadwordLists/now-2026/``. key1 is the
documented join key ("built for machine comparison ... use for matching, dedup,
joins"); the exports are themselves derived from csl-orig, so the result is
reproducible from the same source the rest of the F-suite parses.

Output: prints a report and writes ``data/forensic/shared_omission_test.csv``
(the per-cell contingency counts) + a provenance sidecar. Stdlib only.
"""

import csv
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ATLAS_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
GH_ROOT = os.path.abspath(os.path.join(ATLAS_ROOT, ".."))
HW_DIR = os.path.join(
    GH_ROOT, "SanskritLexicography", "HeadwordLists", "now-2026"
)

# Canonical key1 exports (now-2026 snapshot). File names carry the line count.
FILES = {
    "MW": "MW-unique-key1-194084.txt",   # Monier-Williams 1899
    "PWG": "PWG-unique-key1-106082.txt",  # Bohtlingk-Roth (Grosses PW)
    "AP": "AP-unique-key1-88867.txt",    # Apte 1890 (independent control)
    "SKD": "SKD-unique-key1-40817.txt",  # Sabdakalpadruma (indigenous)
    "VCP": "VCP-unique-key1-48636.txt",  # Vacaspatyam (indigenous)
}


def load(code):
    path = os.path.join(HW_DIR, FILES[code])
    with open(path, encoding="utf-8") as fh:
        return {ln.strip() for ln in fh if ln.strip()}


def contingency(anchor, target, probe):
    """2x2 of (PWG has/lacks) x (probe has/lacks), restricted to anchor set.

    ``target`` = PWG set; ``probe`` = MW or AP set.
    Returns dict with the four cells + derived rates.
    """
    pwg_has_probe_has = pwg_has_probe_lacks = 0
    pwg_lacks_probe_has = pwg_lacks_probe_lacks = 0
    for w in anchor:
        in_pwg = w in target
        in_probe = w in probe
        if in_pwg and in_probe:
            pwg_has_probe_has += 1
        elif in_pwg and not in_probe:
            pwg_has_probe_lacks += 1
        elif not in_pwg and in_probe:
            pwg_lacks_probe_has += 1
        else:
            pwg_lacks_probe_lacks += 1
    pwg_has = pwg_has_probe_has + pwg_has_probe_lacks
    pwg_lacks = pwg_lacks_probe_has + pwg_lacks_probe_lacks
    lack_given_has = pwg_has_probe_lacks / pwg_has if pwg_has else 0.0
    lack_given_lacks = (
        pwg_lacks_probe_lacks / pwg_lacks if pwg_lacks else 0.0
    )
    gap_sensitivity = (
        lack_given_lacks / lack_given_has if lack_given_has else float("inf")
    )
    return {
        "pwg_has_probe_has": pwg_has_probe_has,
        "pwg_has_probe_lacks": pwg_has_probe_lacks,
        "pwg_lacks_probe_has": pwg_lacks_probe_has,
        "pwg_lacks_probe_lacks": pwg_lacks_probe_lacks,
        "pwg_has": pwg_has,
        "pwg_lacks": pwg_lacks,
        "lack_given_pwg_has": round(lack_given_has, 4),
        "lack_given_pwg_lacks": round(lack_given_lacks, 4),
        "gap_sensitivity": (
            round(gap_sensitivity, 3)
            if gap_sensitivity != float("inf")
            else None
        ),
    }


def main():
    sets = {c: load(c) for c in FILES}
    for c in FILES:
        print(f"  loaded {c}: {len(sets[c]):>7,} key1 headwords")

    # Anchor R: real words attested in BOTH indigenous dicts, wholly outside
    # the European lineage -> a PWG/MW omission of one of these is meaningful.
    anchor = sets["SKD"] & sets["VCP"]
    print(f"\nAnchor R = SKD & VCP (indigenous-attested real words): {len(anchor):,}")

    rows = []
    results = {}
    for probe in ("MW", "AP"):
        c = contingency(anchor, sets["PWG"], sets[probe])
        results[probe] = c
        print(f"\n--- probe = {probe} vs PWG, within R ---")
        print(f"  PWG has   & {probe} has  : {c['pwg_has_probe_has']:>6,}")
        print(f"  PWG has   & {probe} LACKS: {c['pwg_has_probe_lacks']:>6,}")
        print(f"  PWG LACKS & {probe} has  : {c['pwg_lacks_probe_has']:>6,}"
              f"   <- {probe} independently filled PWG's gap")
        print(f"  PWG LACKS & {probe} LACKS: {c['pwg_lacks_probe_lacks']:>6,}"
              f"   <- SHARED OMISSION")
        print(f"  P({probe} lacks | PWG has)   = {c['lack_given_pwg_has']:.4f}")
        print(f"  P({probe} lacks | PWG lacks) = {c['lack_given_pwg_lacks']:.4f}")
        print(f"  gap-sensitivity ratio        = {c['gap_sensitivity']}")
        rows.append({"probe": probe, **c})

    mw_gs = results["MW"]["gap_sensitivity"]
    ap_gs = results["AP"]["gap_sensitivity"]
    print("\n=== VERDICT (item #1, shared omission) ===")
    print(f"  MW gap-sensitivity = {mw_gs}   (bigger dict, 194k lemmas)")
    print(f"  AP gap-sensitivity = {ap_gs}   (independent control, 89k lemmas)")
    if mw_gs and ap_gs:
        print(f"  differential MW/AP = {round(mw_gs / ap_gs, 3)}")
    # Fill rates on PWG's blind spots (size-normalised reading).
    mw_fill = results["MW"]["pwg_lacks_probe_has"] / results["MW"]["pwg_lacks"]
    ap_fill = results["AP"]["pwg_lacks_probe_has"] / results["AP"]["pwg_lacks"]
    print(f"\n  On PWG's blind spots (real indigenous words PWG lacks, n="
          f"{results['MW']['pwg_lacks']:,}):")
    print(f"    MW fills {mw_fill:.1%}   AP fills {ap_fill:.1%}")
    print("  (MW is ~2x larger than AP; if MW were independent it should fill")
    print("   MORE of PWG's gaps than AP, not fewer.)")

    out = os.path.join(ATLAS_ROOT, "data", "forensic", "shared_omission_test.csv")
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {out}")

    sidecar = {
        "script": "scripts/forensic/f9_shared_omission.py",
        "inputs": {c: FILES[c] for c in FILES},
        "input_dir": "SanskritLexicography/HeadwordLists/now-2026/",
        "anchor": "SKD & VCP (indigenous-attested)",
        "anchor_n": len(anchor),
        "control": "AP (Apte 1890, independent English tradition)",
        "results": results,
    }
    with open(out + ".source.json", "w", encoding="utf-8") as fh:
        json.dump(sidecar, fh, ensure_ascii=False, indent=2)
    print(f"wrote {out}.source.json")


if __name__ == "__main__":
    main()
