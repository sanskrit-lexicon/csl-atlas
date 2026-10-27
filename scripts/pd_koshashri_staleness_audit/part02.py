#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7300 part 02 — verdicts, canaries, emit, --check, main.

See scripts/pd_koshashri_staleness_audit.py (thin wrapper) for the contract.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys

from part01 import *  # noqa: F401,F403
from part01 import (COVERAGE_HEADER, DATA, LEDGER, MARKUP_HEADER, ROOT,
                    build_coverage_panel, build_markup_panel, load_control,
                    load_json, load_ledger)

# ---------------------------------------------------------------- verdicts


def build_verdicts(snapshot, census, ledger, control, coverage_rows, anomalies):
    digital_pp = sum(r["pp_hi"] - r["pp_lo"] + 1 for r in ledger
                     if r["in_digital_text"] == "yes")
    print_only_rows = [r for r in ledger if r["in_digital_text"] == "no"]
    print_hi = max(r["pp_hi"] for r in ledger)
    portal_years = [v["year_of_publish"] for v in snapshot["volumes"]
                    if v["status"] == "ok"]
    portal_hi = max(v["end_page"] for v in snapshot["volumes"]
                    if v["status"] == "ok")
    digital_vols = [r for r in coverage_rows
                    if r["in_cologne_digital_text"] == "yes"]
    pune_only = [r for r in coverage_rows if r["in_cologne_digital_text"] == "no"]
    # distinct pages of the Pune-only tail: union of the portal ranges, so the
    # portal-internal vol 31/32 overlap (5521-5608 listed twice) is not
    # double-counted; the naive per-volume sum is reported beside it
    def _union_pages(rows):
        spans = []
        for r in rows:
            if r["pages"]:
                lo, hi = r["pages"].split("-")
                spans.append((int(lo), int(hi)))
        spans.sort()
        total, cur = 0, None
        for lo, hi in spans:
            if cur is None:
                cur = [lo, hi]
            elif lo <= cur[1] + 1:
                cur[1] = max(cur[1], hi)
            else:
                total += cur[1] - cur[0] + 1
                cur = [lo, hi]
        if cur is not None:
            total += cur[1] - cur[0] + 1
        return total

    pune_pp_naive = sum(r["n_pages"] for r in pune_only if r["n_pages"] != "")
    punee_pp = _union_pages(pune_only)
    n_ctrl = len(control)
    n_consistent = sum(1 for r in control if r["cell"] == "consistent")
    n_convloss = sum(1 for r in control
                     if r["print_present"] == "yes"
                     and r["machine_present"] == "no")
    n_editorial = sum(1 for r in control
                      if r["print_present"] == "no"
                      and r["machine_present"] == "no")
    tc = census["tag_counts"]
    voc = {v["total_vocables_raw"] for v in snapshot["volumes"]
           if v["status"] == "ok"}
    verdicts = {
        "handoff": "H7300",
        "generated": snapshot["probe_date"],
        "panels": {
            "A_markup_capability": {
                "artifact": "data/pd/pd_koshashri_markup_comparison.tsv",
                "cologne_L_records": tc["<L>"],
                "cologne_absent_tags": {k: tc[k] for k in
                                        ("<ls>", "<ab>", "<info>")},
                "koshashri_volume_json_ok": snapshot["ok"],
                "koshashri_volume_json_error": snapshot["error"],
            },
            "B_dated_content_coverage": {
                "artifact": "data/pd/pd_koshashri_content_coverage.tsv",
                "print_record_volumes": 35,
                "print_record_year_span": [min(portal_years), max(portal_years)],
                "print_record_final_page": portal_hi,
                "cologne_digital_pages": digital_pp,
                "cologne_digital_volumes": len(digital_vols),
                "cologne_digital_ends": "vol 24, 2008, p. 4328",
                "pune_only_volumes": len(pune_only),
                "pune_only_pages": punee_pp,
                "pune_only_pages_naive_sum": pune_pp_naive,
                "pune_only_year_span": "2009-2019",
                "source_anomalies": anomalies,
            },
            "C_print_fidelity_v78_control": {
                "artifact": "data/pd/pd_v78_bracket_mark_control.tsv",
                "pages_sampled": sorted({r["page"] for r in control}),
                "marks_checked": n_ctrl,
                "consistent": n_consistent,
                "print_only_marks_missing_from_machine": n_convloss,
                "absent_from_both": n_editorial,
            },
            "C_print_fidelity_2009_2019": {
                "verdict": "STOP_NO_PRINT_ACCESS",
                "reason": "no page images of ledger rows 9.1-35 (2009-2019) "
                          "are reachable in the estate (H7275 layer-2 "
                          "precedent, 26-10-2026); KoshaSHRI entry preview is "
                          "login-walled and no permission is held",
            },
        },
        "verdicts": {
            "schema_staleness": (
                "COLOGNE_FLAT_RECORD_SCHEMA (no <ls>/<ab>/<info>; sigla plain "
                "text) vs PUNE_STRUCTURED_DB (typed per-volume JSON); Pune's "
                "entry-level schema is UNKNOWN_NOT_PUBLICLY_OBSERVABLE — "
                "login-walled, never probed past the gate"),
            "content_coverage": (
                "COLOGNE_DIGITAL_STALE: ends vol 24 (2008, p. 4328); the "
                "print record reaches vol 35 (2019, p. 6056); Pune-only tail "
                "= %d volumes / %d pages / 2009-2019; KoshaSHRI portal "
                "metadata current through 2019 as of %s"
                % (len(pune_only), punee_pp, snapshot["probe_date"])),
            "conversion_loss": (
                "NOT_DETECTED_IN_V78_SAMPLE: %d/%d bracketed source marks on "
                "4 print pages of vols 7-8 present in both print and machine "
                "text; 0 print-only marks; sample is not the dictionary"
                % (n_consistent, n_ctrl)),
            "editorial_change": (
                "NO_POSITIVE_CLAIM: tags alone prove nothing; in the v7/v8 "
                "print-checked sample no divergence was seen (%d marks, "
                "incl. bare-vs-bracketed DBHS. variation matching print); "
                "for the 2009-2019 tail: STOP_NO_PRINT_ACCESS"
                % n_ctrl),
        },
        "unknowns": [
            "KoshaSHRI entry-level markup/schema (login-walled, unprobed).",
            "KoshaSHRI volume ids 12 and 14 (portal error pages; ledger "
            "fallback used, unverified against the portal).",
            "Whether a KoshaSHRI bulk export exists at all (none observed in "
            "navigation; absence not proven).",
            "Same-print-page fidelity for the 2009-2019 print record "
            "(STOP_NO_PRINT_ACCESS).",
            "Whether the portal's 2009-2019 entry text differs editorially "
            "from the 2009-2019 print fascicles.",
        ],
        "rights": ("KoshaSHRI: all rights reserved — public per-volume JSON "
                   "metadata only, no entry text fetched or committed, no "
                   "circumvention. Cologne PDScan: CC BY-NC-SA 3.0 — derived "
                   "counts only, no bulk text committed. Scan PDFs fetched "
                   "for visual control were not committed."),
        "probes": {
            "volume_snapshot": "data/pd/pd_koshashri_volume_snapshot_2026-10-27.json",
            "cologne_census": "data/pd/pd_cologne_tag_census_2026-10-27.json",
            "prior_audits": [AUDIT_C7, AUDIT_25_10],
        },
    }
    if voc != {100}:
        verdicts["verdicts"]["schema_staleness"] += (
            " — WARNING: total_vocables constant-100 trap broken %s" % sorted(voc))
    return verdicts


# ---------------------------------------------------------------- canaries


def build_canaries(snapshot, census, control):
    vols = {v["id"]: v for v in snapshot["volumes"]}
    tc = census["tag_counts"]
    v1, v35 = vols[1], vols[35]
    rows = [
        ("K1",
         "KoshaSHRI vol 1 opens the print record",
         "year=1976 pages=1-216 editor=A.M. Ghatage",
         "year=%s pages=%s-%s editor=%s"
         % (v1["year_of_publish"], v1["start_page"], v1["end_page"],
            v1["name_of_ge"]),
         "volume snapshot " + snapshot["probe_date"]),
        ("K2",
         "KoshaSHRI vol 35 closes the print record",
         "year=2019 pages=5881-6056 closing=abhigamyamānaparadārādi",
         "year=%s pages=%s-%s closing=%s"
         % (v35["year_of_publish"], v35["start_page"], v35["end_page"],
            v35["eng_closing_entry"]),
         "volume snapshot " + snapshot["probe_date"]),
        ("K3",
         "Cologne PDScan record census and the <ls> correction",
         "<L>=107630 <ls>=0",
         "<L>=%d <ls>=%d" % (tc["<L>"], tc["<ls>"]),
         "cologne census " + census["probe_date"]),
        ("K4",
         "total_vocables is a constant-100 trap, not a per-volume count",
         "distinct total_vocables values across all ok records = {100}",
         "%s" % sorted({v["total_vocables_raw"] for v in snapshot["volumes"]
                        if v["status"] == "ok"}),
         "volume snapshot " + snapshot["probe_date"]),
        ("K5",
         "the portal's known volume-JSON gap persists unchanged",
         "error ids = [12, 14]; ok = 33 of 35",
         "error ids = %s; ok = %d of 35"
         % ([v["id"] for v in snapshot["volumes"] if v["status"] != "ok"],
            snapshot["ok"]),
         "volume snapshot " + snapshot["probe_date"]),
    ]
    return rows


CANARY_HEADER = ["canary_id", "assertion", "expected", "observed", "source"]


# ---------------------------------------------------------------- emit


def render_tsv(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, delimiter="\t", lineterminator="\n")
    w.writerow(header)
    for r in rows:
        w.writerow(list(r.values()) if isinstance(r, dict) else list(r))
    return buf.getvalue()


def build_all():
    snapshot = load_json(SNAPSHOT)
    census = load_json(CENSUS)
    ledger = load_ledger()
    control = load_control()
    markup = build_markup_panel(snapshot, census)
    coverage, anomalies = build_coverage_panel(snapshot, ledger)
    verdicts = build_verdicts(snapshot, census, ledger, control,
                              coverage, anomalies)
    canaries = build_canaries(snapshot, census, control)
    return {
        OUT_MARKUP: render_tsv(MARKUP_HEADER, markup),
        OUT_COVERAGE: render_tsv(COVERAGE_HEADER, coverage),
        OUT_VERDICTS: json.dumps(verdicts, ensure_ascii=False, indent=1,
                                 sort_keys=False) + "\n",
        OUT_CANARIES: render_tsv(CANARY_HEADER, canaries),
    }


def canary_pins_ok():
    """Hard pins: the five canary rows must observe exactly their expected
    values against the committed snapshots."""
    snapshot = load_json(SNAPSHOT)
    census = load_json(CENSUS)
    vols = {v["id"]: v for v in snapshot["volumes"]}
    assert vols[1]["year_of_publish"] == 1976
    assert (vols[1]["start_page"], vols[1]["end_page"]) == (1, 216)
    assert vols[35]["year_of_publish"] == 2019
    assert (vols[35]["start_page"], vols[35]["end_page"]) == (5881, 6056)
    assert vols[35]["eng_closing_entry"] == "abhigamyamānaparadārādi"
    assert census["tag_counts"]["<L>"] == 107630
    assert census["tag_counts"]["<ls>"] == 0
    assert {v["total_vocables_raw"] for v in snapshot["volumes"]
            if v["status"] == "ok"} == {100}
    assert [v["id"] for v in snapshot["volumes"]
            if v["status"] != "ok"] == [12, 14]
    assert snapshot["ok"] == 33
    return True

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="verify committed artifacts, no writes")
    ap.add_argument("--fetch", action="store_true",
                    help="live re-probe (network; writes new dated snapshots)")
    args = ap.parse_args(argv)
    if args.fetch:
        print("--fetch is the live probe mode; see module docstring and "
              "reports/PD_KOSHASHRI_STALENESS_AUDIT_2026.md §Repro for the "
              "exact curl surface. It is intentionally not automated beyond "
              "the documented commands: portal probes need a browser UA and "
              "human-paced requests.", file=sys.stderr)
        return 0
    for needed in (SNAPSHOT, CENSUS, LEDGER, CONTROL):
        if not os.path.exists(needed):
            print("MISSING committed input: %s" % needed, file=sys.stderr)
            return 3
    built = build_all()
    if args.check:
        bad = []
        for path, content in built.items():
            if not os.path.exists(path):
                bad.append("missing: %s" % path)
                continue
            with open(path, encoding="utf-8") as fh:
                if fh.read() != content:
                    bad.append("stale: %s" % path)
        try:
            canary_pins_ok()
        except AssertionError as exc:
            bad.append("canary pin broke: %s" % exc)
        if bad:
            print("\n".join(bad), file=sys.stderr)
            return 2
        print("OK — 4 artifacts byte-identical, 5 canary pins hold")
        return 0
    for path, content in built.items():
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        print("wrote %s" % os.path.relpath(path, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
