#!/usr/bin/env python3
"""OBS-C (A08) referee gaps: C-M2 (Table 1 <ls> totals for BEN/BHS/AP) and
C-M5 (the SKD rank-swap number: <ls>-rank vs iti-density-rank).

Trivial counts over csl-orig/v02, per REVISION_BRIEF_P2_OBS.md Part 3.
Reuses the <ls>-extraction convention documented in
scripts/forensic/parse_cslorig.py (iter_entries) rather than re-deriving it.

Usage: python scripts/obs/citation_register_gaps.py
"""
import glob
import os
import re
import sys

sys.path.insert(0, os.path.abspath("scripts/forensic"))
from parse_cslorig import iter_entries, CSL_ORIG  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# iti/ity count per paper_citation_registers.md §3.3: preceded by whitespace
# or a quotation mark (not any non-letter), which is what excludes in-word
# substrings like prIti/nIti while still requiring a genuine word boundary.
ITI_RE = re.compile(r'(?:(?<=\s)|(?<=["“”]))(?:iti|ity)(?![A-Za-z])')


def discover_dicts():
    return sorted(
        os.path.basename(os.path.dirname(p))
        for p in glob.glob(os.path.join(CSL_ORIG, "*", "*.txt"))
        if os.path.basename(p)[:-4] == os.path.basename(os.path.dirname(p))
    )


def counts_for(code):
    path = os.path.join(CSL_ORIG, code, f"{code}.txt")
    if not os.path.exists(path):
        return None
    entries = 0
    ls_total = 0
    iti_total = 0
    for e in iter_entries(path):
        entries += 1
        ls_total += len(e.get("citations") or [])
        iti_total += len(ITI_RE.findall(e.get("body") or ""))
    return {"entries": entries, "ls": ls_total, "iti": iti_total}


def main():
    codes = discover_dicts()
    per_dict = {}
    for code in codes:
        c = counts_for(code)
        if c:
            per_dict[code] = c

    print("=== C-M2: <ls> totals for BEN/BHS/AP (Table 1 gap) ===")
    for code in ("ben", "bhs", "ap"):
        c = per_dict.get(code)
        if not c:
            print(f"  {code}: source not found")
            continue
        per_entry = c["ls"] / c["entries"] if c["entries"] else 0
        print(f"  {code.upper()}: <ls>={c['ls']:,}  entries={c['entries']:,}  per-entry={per_entry:.2f}")

    print("\n=== C-M5: SKD rank-swap (<ls>-rank vs iti-density-rank, all discovered dicts) ===")
    by_ls = sorted(per_dict.items(), key=lambda kv: -kv[1]["ls"])
    by_iti_density = sorted(
        per_dict.items(),
        key=lambda kv: -(kv[1]["iti"] / kv[1]["entries"] if kv[1]["entries"] else 0)
    )
    ls_rank = {code: i + 1 for i, (code, _c) in enumerate(by_ls)}
    iti_rank = {code: i + 1 for i, (code, _c) in enumerate(by_iti_density)}
    n = len(per_dict)
    skd = per_dict.get("skd")
    if skd:
        skd_iti_density = skd["iti"] / skd["entries"] if skd["entries"] else 0
        print(f"  N dictionaries: {n}")
        print(f"  SKD <ls> total: {skd['ls']}  ->  <ls>-density rank {ls_rank['skd']} of {n} (tied last, {skd['ls']} <ls> tags)")
        print(f"  SKD iti-density: {skd_iti_density:.2f} per entry  ->  iti-density rank {iti_rank['skd']} of {n}")
        print(f"  Rank swap: {ls_rank['skd']} (of {n}, by <ls>) -> {iti_rank['skd']} (of {n}, by iti-density)")


if __name__ == "__main__":
    main()
