#!/usr/bin/env python3
"""H6969 -- PD AOB row test: is 1,473 the printed list count?

The 2003 *Outlook* feature on PD reports that the project mined **1,473 texts**
in its first 25 years, catalogued by 1975 in over nine million hand-written
slips (PD repo, ``PRESS/OUTLOOK_2003-12-01_KABRA_DICTIONARYAHA.md``, claim C4).

A68 metric 2 divides 118 covered works by the declared AOB canon.  Four numbers
circulate for that denominator: 1,419 (pass-1 entry count), 1,464 (printed
census), 1,476 (H6923's R1 structural estimate) and 1,473 (this press line).
This script asks the only question that separates them: **what does the printed
AOB ("Abbreviations of Books Quoted", 42 pp) actually carry as entry rows?**

The load-bearing measurement is a correction H6923 did not make: the R1
entry-like-line rule counts the page's **repeated column header** as an entry.
The AOB repeats ``Abbreviation. *Name* of the *Book,* *Author,* ...`` at the top
of each page, the OCR catches it 7 times (pages 2, 13, 30, 37, 40, 41, 42), and
every one of those lines passes R1.  So R1 = 1,476 is **1,469 entry rows + 7
header rows**, and the structural estimate the paper quotes is 7 rows high.

Rules are imported from the committed H6923 audit (``pd_aob_declared_canon_audit``)
so there is exactly ONE definition of R1 -- this script adds the per-page census
and the header class, it does not re-spell the rule.

Run:
  python3 scripts/pd_aob_row_test_1473.py               # measure + write JSON
  python3 scripts/pd_aob_row_test_1473.py --check       # verify the committed JSON
  python3 scripts/pd_aob_row_test_1473.py --aob /path/to/AOB.md

Exit codes: 0 ok / measured, 1 drift under --check, 2 input missing.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pd_aob_declared_canon_audit import (  # noqa: E402  (single source of the R1 rule)
    ENTRY_MIN_TAIL_LETTERS,
    PAGE_RE,
    SIGLUM_WORD_RE,
    TOKEN_RE,
    UPPER_START_RE,
    YEAR_RE,
    count_lines,
    letters,
)

# --- the press figure under test --------------------------------------------
PRESS_CLAIM_1473 = 1473
COVERED_WORKS = 118          # A68 metric-2 numerator; owned by pd_dcs_metrics.json
N_AOB_PAGES = 42

# a printed column header always opens with this word; it labels the columns,
# it is not an abbreviation of a book
HEADER_PREFIX = "abbreviation"


def is_entry_like(token: str, rest: str) -> tuple[bool, bool]:
    """(counted_by_R1, is_merged_siglum_title) for one backticked line."""
    if not UPPER_START_RE.match(token):
        return False, False
    words = token.split()
    merged = (
        len(words) > 1
        and bool(SIGLUM_WORD_RE.match(words[0]))
        and letters(token) >= 10
    )
    counted = letters(rest) >= ENTRY_MIN_TAIL_LETTERS or bool(YEAR_RE.search(rest)) or merged
    return counted, merged


def measure_pages(lines):
    """Per-page R1 census, split into entry rows and repeated column headers."""
    page = 0
    per_page_r1 = {}
    header_pages = []
    header_tokens = []
    r1 = 0
    dups = 0
    merged = 0
    prev = None

    for line in lines:
        m = PAGE_RE.match(line)
        if m:
            page = int(m.group(1))
            continue
        m = TOKEN_RE.match(line)
        if not m:
            continue
        token = m.group(1).strip()
        rest = m.group(2).strip()
        counted, merged_here = is_entry_like(token, rest)
        if not counted:
            continue
        r1 += 1
        if merged_here:
            merged += 1
        per_page_r1[page] = per_page_r1.get(page, 0) + 1
        if token.lower().startswith(HEADER_PREFIX):
            header_pages.append(page)
            header_tokens.append(token)
        if token == prev:
            dups += 1
        prev = token

    return {
        "r1_entry_like_lines": r1,
        "merged_siglum_title_tokens": merged,
        "consecutive_duplicate_sigla": dups,
        "repeated_column_header_rows": len(header_pages),
        "repeated_column_header_pages": sorted(header_pages),
        "repeated_column_header_tokens": header_tokens,
        "per_page_r1": per_page_r1,
    }


def read_inventory(path: Path):
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    return rows


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def pct(n: int, d: int) -> float:
    return round(100.0 * n / d, 2)


def measure(atlas: Path, aob: Path) -> dict:
    if not aob.exists():
        print(f"[FAIL] AOB OCR not found: {aob}", file=sys.stderr)
        return 2
    inv_path = atlas / "data/pd/pd_aob_entries.tsv"
    if not inv_path.exists():
        print(f"[FAIL] entry inventory not found: {inv_path}", file=sys.stderr)
        return 2

    lines = aob.read_text(encoding="utf-8").splitlines()
    m = measure_pages(lines)

    # rule-parity guard: the per-page census must reproduce H6923's own totals,
    # otherwise this script is measuring a different rule than the audit it corrects
    audit = count_lines(lines)
    if audit["entry_like_lines_r1"] != m["r1_entry_like_lines"]:
        print(
            f"[FAIL] rule drift -- audit R1 {audit['entry_like_lines_r1']} != "
            f"per-page R1 {m['r1_entry_like_lines']}",
            file=sys.stderr,
        )
        return 2
    r2 = audit["garbled_start_dated_r2_upper_bound"]

    r1 = m["r1_entry_like_lines"]
    headers = m["repeated_column_header_rows"]
    dups = m["consecutive_duplicate_sigla"]
    entry_rows = r1 - headers
    entry_rows_nodup = entry_rows - dups

    vector = [m["per_page_r1"].get(p, 0) for p in range(1, N_AOB_PAGES + 1)]

    inv = read_inventory(inv_path)
    n_inv = len(inv)
    n_junk = sum(1 for r in inv if r.get("junk") == "yes")
    n_usable = n_inv - n_junk
    n_wellformed = sum(1 for r in inv if r.get("wellformed") == "yes")
    n_merged = sum(1 for r in inv if r.get("merged_token") == "yes")
    n_garbled = sum(1 for r in inv if r.get("garbled_start") == "yes")

    # every defensible candidate for "rows on the printed list"
    candidates = {
        "inventory_usable": n_usable,
        "inventory_parsed": n_inv,
        "print_census_press": 1464,
        "entry_rows_header_corrected": entry_rows,
        "r1_entry_like_lines_uncorrected": r1,
    }
    band_lo = min(candidates.values())
    band_hi = max(candidates.values())

    distances = {str(k): PRESS_CLAIM_1473 - v for k, v in candidates.items()}

    return {
        "generated_by": "H6969 scripts/pd_aob_row_test_1473.py (DeepSeek Flash, deepseek-flash)",
        "audited_on": "2026-10-18",
        "question": "Is the 2003 press figure 1,473 the printed AOB row count?",
        "source_aob": {
            "path": "PD/AOB.md (sanskrit-lexicon/PD, OCR of the official KoshaSHRI AOB.pdf)",
            "sha256": sha256_of(aob),
            "pages": N_AOB_PAGES,
            "lines_total": len(lines),
            "note": "only one AOB printing exists in the estate (AOB.pdf); AOB_ocr.md is a second OCR pass of the same PDF, so no 2003-vintage AOB list can be tested",
        },
        "source_inventory": {
            "path": "data/pd/pd_aob_entries.tsv",
            "sha256": sha256_of(inv_path),
            "entries_parsed": n_inv,
            "entries_junk": n_junk,
            "entries_usable": n_usable,
            "entries_wellformed": n_wellformed,
            "entries_merged_token": n_merged,
            "entries_garbled_start": n_garbled,
        },
        "printed_row_census": {
            "r1_entry_like_lines_uncorrected": r1,
            "repeated_column_header_rows": headers,
            "repeated_column_header_pages": m["repeated_column_header_pages"],
            "repeated_column_header_tokens": m["repeated_column_header_tokens"],
            "entry_rows_header_corrected": entry_rows,
            "consecutive_duplicate_sigla": dups,
            "entry_rows_header_and_dup_corrected": entry_rows_nodup,
            "merged_siglum_title_tokens": m["merged_siglum_title_tokens"],
            "garbled_start_dated_r2_upper_bound": r2,
            "entry_rows_plus_unrecovered_ceiling": entry_rows + r2,
        },
        "page_density": {
            "pages": N_AOB_PAGES,
            "per_page_r1": vector,
            "mean_per_page": round(statistics.mean(vector), 2),
            "median_per_page": statistics.median(vector),
            "min_per_page": min(vector),
            "max_per_page": max(vector),
        },
        "candidates": candidates,
        "band": {"lo": band_lo, "hi": band_hi, "width": band_hi - band_lo},
        "press_claim": {
            "value": PRESS_CLAIM_1473,
            "distance_to_candidate": distances,
            "nearest_candidate": min(distances, key=lambda k: abs(distances[k])),
            "inside_band": band_lo <= PRESS_CLAIM_1473 <= band_hi,
        },
        "metric_effect": {
            "covered_works": COVERED_WORKS,
            "at_r1_uncorrected": {"n": r1, "pct": pct(COVERED_WORKS, r1)},
            "at_header_corrected": {"n": entry_rows, "pct": pct(COVERED_WORKS, entry_rows)},
            "at_inventory_usable": {"n": n_usable, "pct": pct(COVERED_WORKS, n_usable)},
            "displayed_after_rounding": 8.0,
        },
        "verdict": {
            "is_1473_the_printed_row_count": "no -- not reproducible as the count",
            "why": (
                "The printed AOB carries 1,469 entry rows once the 7 repeated column-header "
                "lines are removed from R1's 1,476; 1,473 is 4 above that and 50 above the "
                "careful parse (1,423 usable). Adding back the OCR-garbled entries R1 misses "
                "(R2, 99 candidate lines, an upper bound) a printed count of 1,473 is well "
                "inside the recoverable range, so the press figure CANNOT be excluded as the "
                "list count -- but no committed rule REPRODUCES it, so it is consistent with "
                "the printed row count rather than equal to it."
            ),
            "independent_witness_for_1476": "no",
            "independence_reason": (
                "Three failures: (1) different measurement channel -- the figure is the project's "
                "own count of texts excerpted, given in a feature sourced to its director and "
                "coordinator, not an external count of the printed list; (2) different time slice "
                "-- 'first 25 years', catalogued by 1975, against a list printed with volumes "
                "1976-2019 and OCR'd from the current PDF; (3) same producer -- the AOB and the "
                "press figure both originate at Deccan College, so relaying it is not an "
                "independent second measurement of that institution's own list."
            ),
            "evidentiary_value": (
                "A dateable corroboration of magnitude: by 2003 the project itself put its source "
                "corpus at ~1.47x, which rules out reading 1,419 or 1,118 as its own intended "
                "canon, and brackets the printed list from below. It must NOT be counted as a "
                "second independent witness."
            ),
            "correction_landed": (
                "H6923's structural estimate 1,476 includes 7 repeated column-header rows; the "
                "header-corrected printed entry-row count is 1,469, so 118/N = 8.03 % -- which "
                "still displays as the ruled 8.0 %, so no manuscript number moves."
            ),
        },
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--aob", default=None, help="path to PD/AOB.md")
    ap.add_argument("--check", action="store_true", help="verify the committed JSON")
    ap.add_argument("--json", default=None, help="output JSON path")
    args = ap.parse_args(argv)

    atlas = Path(__file__).resolve().parent.parent
    aob = Path(args.aob) if args.aob else Path.home() / "Documents/GitHub/PD/AOB.md"
    out = Path(args.json) if args.json else atlas / "data/pd/pd_aob_row_test_1473.json"

    measured = measure(atlas, aob)
    if isinstance(measured, int):      # measure() signals an input/rule failure by code
        return measured

    if args.check:
        if not out.exists():
            print(f"2: committed JSON missing: {out}", file=sys.stderr)
            return 2
        committed = json.loads(out.read_text(encoding="utf-8"))
        if committed != measured:
            print("1: DRIFT -- committed JSON != fresh measurement", file=sys.stderr)
            for k in sorted(set(committed) | set(measured)):
                if committed.get(k) != measured.get(k):
                    print(f"  {k}:\n    committed={committed.get(k)!r}\n    measured ={measured.get(k)!r}",
                          file=sys.stderr)
            return 1
        print(f"ok: {out.name} matches the fresh measurement")
        return 0

    out.write_text(json.dumps(measured, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    rc = measured["printed_row_census"]
    print(f"wrote {out}")
    print(f"  R1 entry-like lines        : {rc['r1_entry_like_lines_uncorrected']}")
    print(f"  repeated column headers    : {rc['repeated_column_header_rows']} "
          f"(pages {rc['repeated_column_header_pages']})")
    print(f"  entry rows (header-corr.)  : {rc['entry_rows_header_corrected']}")
    print(f"  press claim 1,473 distance : {measured['press_claim']['distance_to_candidate']}")
    print(f"  band                       : {measured['band']['lo']}-{measured['band']['hi']}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(main())
