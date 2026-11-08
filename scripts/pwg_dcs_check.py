#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7463 — regeneration gate: every published PWG↔DCS number regenerates from
the committed row-level TSVs or the check exits non-zero.

    python scripts/pwg_dcs_check.py
"""
from __future__ import annotations

import csv
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "pwg_dcs")
NON_TEXT = {"catalogue_journal", "edition_marker", "second_hand", "manuscript"}


def load(path):
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> int:
    rows = load(os.path.join(D, "pwg_dcs_works_joined.tsv"))
    m = json.load(open(os.path.join(D, "pwg_dcs_join_metrics.json"), encoding="utf-8"))
    fails = []

    def pin(name, got, want):
        if got != want:
            fails.append(f"{name}: regenerated {got!r} != published {want!r}")

    reg = load(os.path.join(D, "pwg_work_register.tsv"))
    pin("register_rows", len(reg), m["register_sigla"])
    pin("raw_ls_tags", sum(int(r["raw_tags"]) for r in reg), 801788)
    pin("quotation_linked", sum(int(r["ql_tags"]) for r in reg), 729719)
    pin("alpha_ql", sum(int(r["alpha_ql"]) for r in reg), 132483)

    total = sum(int(r["ql_tags"]) for r in rows)
    cov = sum(int(r["ql_tags"]) for r in rows if r["held"] == "1")
    text = [r for r in rows if r["stratum"] not in NON_TEXT]
    t_ql = sum(int(r["ql_tags"]) for r in text)
    t_cov = sum(int(r["ql_tags"]) for r in text if r["held"] == "1")
    t_alpha = sum(int(r["alpha_ql"]) for r in text)
    t_alpha_cov = sum(int(r["alpha_ql"]) for r in text if r["held"] == "1")
    d = m["coverage"]["denominators"]
    pin("total_ql", total, d["total_ql"])
    pin("cov_ql", cov, d["cov_ql"])
    pin("text_ql", t_ql, d["text_ql"])
    pin("text_cov_ql", t_cov, d["text_cov_ql"])
    pin("text_alpha", t_alpha, d["text_alpha"])
    pin("text_cov_alpha", t_alpha_cov, d["text_cov_alpha"])

    def pct(x, y):
        return round(100.0 * x / y, 2) if y else None

    pin("pooled_omega", pct(cov, total), m["coverage"]["pooled_omega"])
    pin("stratum_excluded_omega", pct(t_cov, t_ql),
        m["coverage"]["stratum_excluded_omega"])
    pin("stratum_excluded_alpha", pct(t_alpha_cov, t_alpha),
        m["coverage"]["stratum_excluded_alpha"])
    pin("held_works", sum(1 for r in rows if r["held"] == "1" and
                          r["resolution"] != "unresolved"),
        m["work_level"]["held_works"])

    for s, pub in m["strata"].items():
        srows = [r for r in rows if r["stratum"] == s]
        pin(f"strata.{s}.ql", sum(int(r["ql_tags"]) for r in srows), pub["ql"])
        pin(f"strata.{s}.held_works",
            sum(1 for r in srows if r["held"] == "1"), pub["held_works"])

    if fails:
        print("PWG_DCS_CHECK: FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("PWG_DCS_CHECK: OK — every published number regenerates from rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
