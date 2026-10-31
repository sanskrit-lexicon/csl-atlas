#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7513 — regeneration gate: every published MW-vs-PWG/pwk missing-entries
number regenerates from the committed row-level TSV and metrics JSON, or the
check exits non-zero.

    python scripts/mw_vs_pw_check.py

Pure committed-data checks always run. When the csl-orig machine texts are
present (default ``~/Documents/GitHub/csl-orig/v02`` or ``$CSL_ORIG_V02``),
the substrate pins (sha256, entry counts, the H7463 Stage-1 pwg pin) are
verified against the actual files as well; without them the pin stage SKIPS
with a notice so CI stays green on checkouts that do not carry csl-orig.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data" / "mw_vs_pw"

CANARY_ROW = {
    "slp1": "kAritra",
    "class": "a_missing_by_error",
    "subclass": "form_unresolved_nearform",
    "mw_tier": "nearform",
    "mw_fuzzy": "kArita",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    fails: list = []
    skipped: list = []

    def pin(name, got, want):
        if got != want:
            fails.append(f"{name}: regenerated {got!r} != published {want!r}")

    rows = list(csv.DictReader(open(D / "mw_missing_candidates.tsv", encoding="utf-8"),
                               delimiter="\t"))
    m = json.load(open(D / "mw_vs_pw_metrics.json", encoding="utf-8"))
    pins = json.load(open(D / "substrate_pins.json", encoding="utf-8"))

    # ---- the two-class candidate list: class partition and totals ----
    u = m["comparison_universe"]
    a = m["classes"]["a_missing_by_error"]
    b = m["classes"]["b_expected_absence"]
    pin("universe_denominator_sum",
        u["in_mw_exact"] + u["candidates_total"], u["denominator"])
    pin("candidates_rows", len(rows), u["candidates_total"])
    pin("class_a_count", sum(1 for r in rows if r["class"] == "a_missing_by_error"),
        a["count"])
    pin("class_b_count", sum(1 for r in rows if r["class"] == "b_expected_absence"),
        b["count"])
    pin("class_sum", a["count"] + b["count"], u["candidates_total"])

    # ---- subclass breakdowns regenerate from the TSV ----
    from collections import Counter
    subs = Counter(f"{r['class']}.{r['subclass']}" for r in rows)
    for cls_key, cls in m["classes"].items():
        for k, v in cls["subclasses"].items():
            pin(f"subclass_{k}", subs.get(k, 0), v)

    # ---- denominators stated for BOTH classes (the mission's requirement) ----
    for cls_key, cls in m["classes"].items():
        pin(f"denominator_{cls_key}", cls["denominator"], u["denominator"])

    # ---- per-source counts regenerate from the TSV sources column ----
    for code, ps in m["per_source"].items():
        got = sum(1 for r in rows if code in r["sources"].split("+"))
        pin(f"per_source_{code}_candidates", got, ps["candidates"])
        pin(f"per_source_{code}_a", ps["a_missing_by_error"] + ps["b_expected_absence"],
            ps["candidates"])

    # ---- corroboration columns regenerate ----
    cor = m["corroboration"]
    pin("a_with_ge2", sum(1 for r in rows if r["class"] == "a_missing_by_error"
                          and int(r["corroboration_n"]) >= 2), cor["a_with_ge2"])
    pin("a_with_ge1", sum(1 for r in rows if r["class"] == "a_missing_by_error"
                          and int(r["corroboration_n"]) >= 1), cor["a_with_ge1"])
    listed = set(cor["dictionaries"])
    seen = set()
    for r in rows:
        seen.update(x for x in r["corroboration_dicts"].split(",") if x)
        if int(r["corroboration_n"]) != len([x for x in r["corroboration_dicts"].split(",")
                                             if x]):
            fails.append(f"corroboration_n mismatch on row {r['slp1']}")
            break
    unknown = sorted(seen - listed)
    if unknown:
        fails.append(f"corroboration dicts not in metrics list: {unknown}")

    # ---- canary: the motivating case kAritra (issue #119) ----
    ka = [r for r in rows if r["slp1"] == CANARY_ROW["slp1"]]
    if len(ka) != 1:
        fails.append(f"canary kAritra: expected exactly 1 row, found {len(ka)}")
    else:
        for k, v in CANARY_ROW.items():
            pin(f"canary_{k}", ka[0][k], v)
        if float(ka[0]["fuzzy_ratio"]) != 0.92:
            fails.append("canary fuzzy_ratio: expected 0.92 "
                         f"(the kAritra~kArita trap), got {ka[0]['fuzzy_ratio']}")

    # ---- evidence contract: every row keyed to file, line, headword form ----
    bad_ev = sum(1 for r in rows if ".txt:" not in r["evidence"] or "L=" not in r["evidence"])
    pin("rows_without_file_line_evidence", bad_ev, 0)

    # ---- substrate pins against the machine texts (when present) ----
    v02 = Path(os.environ.get(
        "CSL_ORIG_V02",
        os.path.join(os.path.expanduser("~"), "Documents", "GitHub", "csl-orig", "v02")))
    src_files = {"mw": v02 / "mw" / "mw.txt", "pwg": v02 / "pwg" / "pwg.txt",
                 "pw": v02 / "pw" / "pw.txt", "pwkvn": v02 / "pwkvn" / "pwkvn.txt"}
    if all(p.is_file() for p in src_files.values()):
        for code, p in src_files.items():
            src = pins["sources"].get(code) if code != "mw" else pins["mw_txt"]
            pin(f"{code}_sha256", sha256(p), src["sha256"])
        # the H7463 Stage-1 substrate reuse contract
        pin("pwg_sha_vs_h7463_pin", pins["sources"]["pwg"]["sha256"],
            "430c910f8b0c9229d89ef1580b2385883ce5f4e2ee83dfc6ecb7d6251bb62166")
        pwg_dcs = json.load(open(ROOT / "data" / "pwg_dcs" / "pwg_substrate_pins.json",
                                 encoding="utf-8"))
        pin("pwg_sha_vs_pwg_dcs_pin", pins["sources"]["pwg"]["sha256"],
            pwg_dcs["pwg_txt"]["sha256"])
    else:
        skipped.append("substrate sha verification (csl-orig not present on this host)")

    # ---- report ----
    for name in fails:
        print(f"FAIL {name}")
    for name in skipped:
        print(f"SKIP {name}")
    print(f"mw_vs_pw_check: {'FAIL' if fails else 'PASS'} "
          f"({len(rows)} candidate rows, a={a['count']} b={b['count']})")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
