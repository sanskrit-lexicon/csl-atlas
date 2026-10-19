#!/usr/bin/env python3
"""PD sense-order chronology — is a later sense's earliest quotation later?

H7093 measured the order of *citations inside* a sense division.  The
dictionary's title claims the order of the *senses* ("on historical
principles", the OED model), which is a different object and was never
measured.  This script measures it from the committed per-division TSV: for
every entry, each sense division contributes its earliest datable citation
date under one clock; the sequence of those dates, in sense order, is then
tested for a rising tendency.

Units and limits that matter when reading the numbers:

* Only entries with **at least two** divisions that carry a datable citation
  are decidable, so this is a subset of the population (about a quarter).
* The date of a sense is the **earliest quotation** filed under it, not a
  date the editors recorded; a sense can be defensible and still be filed
  under later quotations.
* A rising sequence is **not proof of editorial chronology**: senses carry a
  partly-forced canonical order (literal → figurative → technical) that any
  dictionary shares, and the cross-dictionary control for that is
  `data/forensic/SENSE_ORDER_TEST.md` (MW vs PWG 0.767 against an independent
  Apte control 0.751, shuffle floor 0.50).  Until the same test is run on
  PWG/MW, the tendency below cannot be attributed to PD's editorial principle
  rather than to the semantic structure of meanings.  That control has now been
  run (`scripts/pd_sense_order_compare.py`, H7116): PWG orders its senses at
  least as chronologically (τ = +0.41 against +0.32), so the editorial reading
  is withdrawn — see `reports/PD_SENSE_ORDER_COMPARE_2026.md`.

Usage:
    python scripts/pd_sense_order.py --check     # verify committed numbers
    python scripts/pd_sense_order.py --build     # rewrite the summary JSON
"""
from __future__ import annotations

import csv
import json
import random
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_TSV = ROOT / "data" / "pd" / "pd_citation_order_full.tsv"
OUT_JSON = ROOT / "data" / "pd" / "pd_sense_order_summary.json"

CLOCKS = ("pd_swc", "dcs", "dm", "imprint")
SEED = 20261019
REPS = 5000
PAIR = re.compile(r"(\S+)@(-?\d+)")


def dates(seq: str) -> dict[str, int]:
    return {m.group(1): int(m.group(2)) for m in PAIR.finditer(seq or "")}


def kendall_tau(xs: list[int], ys: list[int]) -> float:
    """Kendall tau-a between two equal-length sequences (no ties expected in xs)."""
    n = len(xs)
    conc = disc = 0
    for i in range(n):
        for j in range(i + 1, n):
            prod = (xs[i] - xs[j]) * (ys[i] - ys[j])
            if prod > 0:
                conc += 1
            elif prod < 0:
                disc += 1
    return (conc - disc) / (conc + disc) if conc + disc else 0.0


def entry_series(rows: list[dict], clock: str) -> dict[str, list[int]]:
    """L -> earliest datable citation date per sense division, in document order."""
    by_entry: dict[str, list[int]] = {}
    for row in rows:  # TSV row order is document order
        ds = dates(row[f"{clock}_seq"])
        if not ds:
            continue
        bucket = by_entry.setdefault(row["L"], [])
        bucket.append(min(ds.values()))
    return by_entry


def summarise(series: dict[str, list[int]]) -> dict:
    pairs = [s for s in series.values() if len(s) == 2]
    multi = [s for s in series.values() if len(s) >= 3]
    later = sum(1 for a, b in pairs if b > a)
    ties = sum(1 for a, b in pairs if b == a)
    backward = sum(1 for a, b in pairs if b < a)
    taus = [kendall_tau(list(range(len(s))), s) for s in multi]
    shifts = [s[-1] - s[0] for s in series.values() if len(s) >= 2]
    return {
        "entries_with_series": len(series),
        "entries_two_senses": len(pairs),
        "two_sense_later_sense_later_date": later,
        "two_sense_ties": ties,
        "two_sense_backward": backward,
        "two_sense_forward_rate": round(later / len(pairs), 10) if pairs else None,
        "entries_three_plus_senses": len(multi),
        "mean_tau_position_vs_earliest": round(sum(taus) / len(taus), 10) if taus else None,
        "median_last_minus_first_years": statistics.median(shifts) if shifts else None,
        "shifts": shifts,
    }


def null_mean(series: dict[str, list[int]], reps: int = REPS, seed: int = SEED) -> dict:
    """Permutation null: shuffle the sense dates within each entry, recompute tau.

    Returns the mean tau under the null and its 2.5-97.5 % band.
    """
    rng = random.Random(seed)
    multi = [list(s) for s in series.values() if len(s) >= 3]
    means = []
    for _ in range(reps):
        vals = []
        for seq in multi:
            rng.shuffle(seq)
            vals.append(kendall_tau(list(range(len(seq))), seq))
        means.append(sum(vals) / len(vals) if vals else 0.0)
    means.sort()
    return {
        "reps": reps,
        "mean_tau_null": round(sum(means) / len(means), 10),
        "p2_5": round(means[int(0.025 * len(means))], 10),
        "p97_5": round(means[int(0.975 * len(means))], 10),
    }


def build_payload(rows: list[dict]) -> dict:
    clocks = {}
    for clock in CLOCKS:
        series = entry_series(rows, clock)
        summary = summarise(series)
        summary.pop("shifts", None)
        summary["null"] = null_mean(series)
        clocks[clock] = summary
    return {
        "handoff": "H7093",
        "generated": "2026-10-19",
        "input": "data/pd/pd_citation_order_full.tsv",
        "unit": "earliest datable citation per sense division, in sense order",
        "clocks": clocks,
    }


def main(argv: list[str]) -> int:
    if "--build" not in argv and "--check" not in argv:
        print("choose --build or --check", file=sys.stderr)
        return 2
    with IN_TSV.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    payload = build_payload(rows)
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if "--build" in argv:
        OUT_JSON.write_text(text, encoding="utf-8")
        print(f"wrote {OUT_JSON.relative_to(ROOT)}")
        return 0
    committed = OUT_JSON.read_text(encoding="utf-8")
    if committed != text:
        print("FAIL: committed summary does not reproduce from the TSV", file=sys.stderr)
        return 1
    print("OK: summary reproduces from the TSV")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
