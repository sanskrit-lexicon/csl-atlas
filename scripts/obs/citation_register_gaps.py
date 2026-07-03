#!/usr/bin/env python3
"""OBS-C citation-register measurement (A02/A08).

Counts, for every discovered csl-orig dictionary, the two citation registers:
Register A (<ls>-tagged, European critical apparatus — with a locator-bearing
split) and Register B (word-boundary iti/ity quotative proxy, indigenous
kośas). Emits the committed artifact data/obs/citation_registers.json — the
reproducible basis for docs/CITATION_REGISTERS.md and the Table 1 / Table 2 /
rank-swap numbers in docs/articles/paper_citation_registers.md — and prints
the C-M2 / C-M5 referee-gap report (Table 1 <ls> totals for BEN/BHS/AP; the
SKD rank swap), per REVISION_BRIEF_P2_OBS.md Part 3.

Reuses the <ls>-extraction convention documented in
scripts/forensic/parse_cslorig.py (iter_entries) rather than re-deriving it.

Usage (from the repo root; CSL_ORIG env overrides the ../csl-orig/v02 default):
    python scripts/obs/citation_register_gaps.py
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.abspath("scripts/forensic"))
sys.path.insert(0, os.path.abspath("scripts/lib"))
from parse_cslorig import iter_entries, CSL_ORIG as _DEFAULT_CSL_ORIG  # noqa: E402
from dataset_meta import (  # noqa: E402
    generated_at_for_payload, license_fields, read_json_if_exists,
)

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

CSL_ORIG = os.environ.get("CSL_ORIG", _DEFAULT_CSL_ORIG)
OUT = os.path.join("data", "obs", "citation_registers.json")
SCHEMA_VERSION = "1.0.0"

# iti/ity count per paper_citation_registers.md §3.3: a Latin-letter word
# boundary on both sides. This excludes in-word substrings like prIti/nIti
# while still counting quotatives that sit directly after markup or
# punctuation — e.g. KRM wraps Sanskrit in <s>…</s>, so the bulk of its
# sUtra-citing iti appears as `<s>iti` and a space-or-quote lookbehind
# (the pre-2026-07 rule) missed ~2/3 of them.
ITI_RE = re.compile(r'(?<![A-Za-z])(?:iti|ity)(?![A-Za-z])')

# Locator-bearing <ls> per paper §3.1: the cleaned citation content contains a
# numeral (book/chapter/verse/page digits); bare otherwise.
DIGIT_RE = re.compile(r"\d")


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
    ls_locator = 0
    iti_total = 0
    for e in iter_entries(path):
        entries += 1
        citations = e.get("citations") or []
        ls_total += len(citations)
        ls_locator += sum(1 for c in citations if DIGIT_RE.search(c))
        iti_total += len(ITI_RE.findall(e.get("body") or ""))
    return {"entries": entries, "ls": ls_total, "lsWithLocator": ls_locator,
            "iti": iti_total}


def competition_ranks(per_dict, density_key):
    """1224-style competition rank by density descending: rank = 1 + number of
    dicts with strictly greater density, so zero-density dicts tie for last."""
    densities = {code: c[density_key] for code, c in per_dict.items()}
    return {
        code: 1 + sum(1 for other in densities.values() if other > d)
        for code, d in densities.items()
    }


def build_payload(per_dict):
    ls_rank = competition_ranks(per_dict, "lsPerEntry")
    iti_rank = competition_ranks(per_dict, "itiPerEntry")
    totals = {
        "entries": sum(c["entries"] for c in per_dict.values()),
        "ls": sum(c["ls"] for c in per_dict.values()),
        "lsWithLocator": sum(c["lsWithLocator"] for c in per_dict.values()),
        "iti": sum(c["iti"] for c in per_dict.values()),
    }
    totals["lsPerEntry"] = round(totals["ls"] / totals["entries"], 4) if totals["entries"] else 0
    totals["lsLocatorShare"] = round(totals["lsWithLocator"] / totals["ls"], 4) if totals["ls"] else 0
    dicts = {}
    for code in sorted(per_dict):
        c = per_dict[code]
        dicts[code] = {
            "entries": c["entries"],
            "ls": c["ls"],
            "lsWithLocator": c["lsWithLocator"],
            "lsPerEntry": c["lsPerEntry"],
            "lsDensityRank": ls_rank[code],
            "iti": c["iti"],
            "itiPerEntry": c["itiPerEntry"],
            "itiDensityRank": iti_rank[code],
        }
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        **license_fields(),
        "generatedBy": "scripts/obs/citation_register_gaps.py",
        "sourceRoot": "../csl-orig/v02",
        "method": {
            "registerA": "every <ls>…</ls> element per parse_cslorig.iter_entries; "
                         "locator-bearing = cleaned citation content contains a digit "
                         "(paper §3.1; an upper bound on resolvability, not verified linkability)",
            "registerB": f"word-boundary iti/ity regex {ITI_RE.pattern!r} over entry bodies — "
                         "not adjacent to a Latin letter, so markup-/punctuation-adjacent "
                         "quotatives count (paper §3.3; a register indicator including some "
                         "grammatical iti, not an exact citation count)",
            "ranks": "competition ranking (ties share the smallest rank) by per-entry density, descending",
        },
        "dictionaryCount": len(per_dict),
        "totals": totals,
        "dicts": dicts,
    }
    return payload


def print_report(per_dict, payload):
    n = payload["dictionaryCount"]
    t = payload["totals"]
    print(f"=== Corpus totals ({n} dicts) ===")
    print(f"  entries={t['entries']:,}  <ls>={t['ls']:,} ({t['lsPerEntry']:.2f}/entry)  "
          f"locator-bearing={t['lsWithLocator']:,} ({t['lsLocatorShare']*100:.1f}%)  "
          f"iti={t['iti']:,}")

    print("\n=== C-M2: <ls> totals for BEN/BHS/AP (Table 1 gap) ===")
    for code in ("ben", "bhs", "ap"):
        c = per_dict.get(code)
        if not c:
            print(f"  {code}: source not found")
            continue
        print(f"  {code.upper()}: <ls>={c['ls']:,}  entries={c['entries']:,}  per-entry={c['lsPerEntry']:.2f}")

    print("\n=== C-M5: SKD rank-swap (<ls>-density rank vs iti-density rank) ===")
    skd = payload["dicts"].get("skd")
    if skd:
        print(f"  N dictionaries: {n}")
        print(f"  SKD <ls> total: {skd['ls']}  ->  <ls>-density rank {skd['lsDensityRank']} of {n} "
              f"(tied last with every zero-<ls> dict)")
        print(f"  SKD iti: {skd['iti']:,} ({skd['itiPerEntry']:.2f}/entry)  ->  "
              f"iti-density rank {skd['itiDensityRank']} of {n}")
        print(f"  Rank swap: {skd['lsDensityRank']} (of {n}, by <ls>-density) -> "
              f"{skd['itiDensityRank']} (of {n}, by iti-density)")

    print("\n=== Register B: densest zero-<ls> iti citers ===")
    zero_ls = [(code, c) for code, c in payload["dicts"].items() if c["ls"] == 0 and c["iti"] > 0]
    for code, c in sorted(zero_ls, key=lambda kv: -kv[1]["itiPerEntry"])[:8]:
        print(f"  {code.upper():6s} iti={c['iti']:>7,}  entries={c['entries']:>7,}  "
              f"iti/entry={c['itiPerEntry']:.2f}")


def main():
    per_dict = {}
    for code in discover_dicts():
        c = counts_for(code)
        if c:
            c["lsPerEntry"] = round(c["ls"] / c["entries"], 4) if c["entries"] else 0
            c["itiPerEntry"] = round(c["iti"] / c["entries"], 4) if c["entries"] else 0
            per_dict[code] = c

    payload = build_payload(per_dict)
    payload["generatedAt"] = generated_at_for_payload(read_json_if_exists(OUT), payload)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print_report(per_dict, payload)
    print(f"\nWrote {OUT} ({payload['dictionaryCount']} dicts)")


if __name__ == "__main__":
    main()
