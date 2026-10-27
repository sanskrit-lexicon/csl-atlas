#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7300 part 01 — inputs, markup-capability panel, dated-coverage panel.

See scripts/pd_koshashri_staleness_audit.py (thin wrapper) for the contract.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))  # package dir -> scripts -> repo root
DATA = os.path.join(ROOT, "data", "pd")

SNAPSHOT = os.path.join(DATA, "pd_koshashri_volume_snapshot_2026-10-27.json")
CENSUS = os.path.join(DATA, "pd_cologne_tag_census_2026-10-27.json")
LEDGER = os.path.join(DATA, "pd_two_layer_fascicle.tsv")
CONTROL = os.path.join(DATA, "pd_v78_bracket_mark_control.tsv")

OUT_MARKUP = os.path.join(DATA, "pd_koshashri_markup_comparison.tsv")
OUT_COVERAGE = os.path.join(DATA, "pd_koshashri_content_coverage.tsv")
OUT_VERDICTS = os.path.join(DATA, "pd_koshashri_staleness_verdicts.json")
OUT_CANARIES = os.path.join(DATA, "pd_koshashri_canaries.tsv")

AUDIT_25_10 = ("Uprava papers/A68/sweeps/2026-10-25-PD-two-digitisations-html-markup.md")
AUDIT_C7 = ("Uprava papers/A68/sweeps/2026-10-14-C7-koshashri-cologne-audit.md")

# ---------------------------------------------------------------- inputs


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_ledger(path=LEDGER):
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    for r in rows:
        r["pp_lo"] = int(r["pp_lo"])
        r["pp_hi"] = int(r["pp_hi"])
        r["year"] = int(r["year"])
    return rows


def load_control(path=CONTROL):
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


# ---------------------------------------------------------------- panel A

# Curated axis table.  Each row carries its evidence and the date the axis was
# last verified live.  Rows marked 27-10-2026 were re-probed this audit; rows
# marked 25-10-2026 are carried from the two-digitisations audit (same estate,
# one day old) and are re-verifiable with --fetch.
def build_markup_panel(snapshot, census):
    tc = census["tag_counts"]
    fresh = "27-10-2026 live probe"
    carried = "25-10-2026 audit (%s)" % AUDIT_25_10
    rows = [
        ("per-entry public URL",
         "yes — getword.php?key=<SLP1>, HTTP 200 (re-probed %s: 927 B)" % fresh,
         "no — /search/preview/<id> answers the sign-in page (re-probed %s)" % fresh,
         "C1/K3 re-probed " + fresh),
        ("stable record id in the artefact",
         "<L>510 in text, ID=510 in entry HTML",
         "numeric vocable.id in doT templates only, not publicly exposed",
         carried),
        ("citation markup",
         "none — <%s> %d, <ab> %d, <info> %d in pd.txt (sigla are plain text)"
         % ("ls", tc["<ls>"], tc["<ab>"], tc["<info>"]),
         "unobservable — no public entry artefact",
         "census %s; gating " % census["probe_date"] + fresh),
        ("printed-page anchor",
         "<pc> anchor on every record (%d) + scan deep link (servepdf)" % tc["<pc>"],
         "not in the public surface (page ranges only, per volume)",
         "census " + census["probe_date"]),
        ("headword keys",
         "<k1>/<k2> SLP1 on every record (%d)" % tc["<k1>"],
         "JSON carries per-volume opening/closing entries only",
         "census + snapshot " + snapshot["probe_date"]),
        ("volume metadata",
         "derivable from <pc> ranges; no official machine metadata",
         "public JSON per volume: year, editor, pages, opening/closing entry "
         "(%d/%d ids answer)" % (snapshot["ok"], snapshot["ok"] + snapshot["error"]),
         "snapshot " + snapshot["probe_date"]),
        ("bulk machine text",
         "yes — one zip, %d <L> records, %d bytes text"
         % (tc["<L>"], census["txt_bytes"]),
         "none observed; no export offered",
         "census " + census["probe_date"] + "; C7 " + AUDIT_C7),
        ("public API",
         "none found (JSON guesses 404)",
         "fetchVolumeInfo/<n> only; POST data paths redirect to /403",
         "snapshot " + snapshot["probe_date"] + "; " + carried),
        ("rendering",
         "static HTML per entry, machine-generated",
         "JS shell + SockJS/STOMP, client-side render; search term absent "
         "from served HTML",
         carried),
        ("crawl surface",
         "direct downloads",
         "robots.txt 404, sitemap.xml 404 (re-probed %s)" % fresh,
         fresh),
        ("licence",
         "CC BY-NC-SA 3.0",
         "all rights reserved (permission by email)",
         "C7 " + AUDIT_C7),
        ("entry schema observability",
         "full — record text and entry HTML both public",
         "none public — entry schema behind sign-in is UNKNOWN, not absent",
         "K3 re-probed " + fresh),
    ]
    return rows


MARKUP_HEADER = ["axis", "cologne_pdscan_2020", "koshashri_portal", "evidence"]


# ---------------------------------------------------------------- panel B


def page_overlap(a_lo, a_hi, b_lo, b_hi):
    return max(0, min(a_hi, b_hi) - max(a_lo, b_lo) + 1)


def build_coverage_panel(snapshot, ledger):
    """Join the 35 portal volume slots to the H7275 ledger by page overlap."""
    vols = {v["id"]: v for v in snapshot["volumes"]}
    rows = []
    anomalies = []
    # ledger-internal duplication check
    seen_ranges = {}
    for r in ledger:
        key = (r["pp_lo"], r["pp_hi"])
        if key in seen_ranges:
            anomalies.append(
                "ledger rows %s and %s share the identical page range %d-%d "
                "(years %s and %s) — 100 pages double-listed"
                % (seen_ranges[key], r["ledger_id"], r["pp_lo"], r["pp_hi"],
                   ledger[[x["ledger_id"] for x in ledger].index(seen_ranges[key])]["year"],
                   r["year"]))
        else:
            seen_ranges[key] = r["ledger_id"]
    for vid in range(1, 36):
        v = vols[vid]
        if v["status"] == "ok":
            lo, hi = v["start_page"], v["end_page"]
            year = v["year_of_publish"]
            editor = v["name_of_ge"]
            opening = v["eng_opening_entry"]
            closing = v["eng_closing_entry"]
            src = "koshashri-json"
        else:
            # portal gap (ids 12, 14): fall back to the committed print ledger,
            # marked as such — never silently filled
            cand = None
            prev_ok = next((vols[i] for i in range(vid - 1, 0, -1)
                            if vols[i]["status"] == "ok"), None)
            next_ok = next((vols[i] for i in range(vid + 1, 36)
                            if vols[i]["status"] == "ok"), None)
            if prev_ok and next_ok:
                gap_lo, gap_hi = prev_ok["end_page"] + 1, next_ok["start_page"] - 1
                cand = [r for r in ledger
                        if page_overlap(gap_lo, gap_hi, r["pp_lo"], r["pp_hi"]) > 0]
            if cand:
                lo, hi = cand[0]["pp_lo"], cand[-1]["pp_hi"]
                year = cand[0]["year"]
                editor = ""
                opening = closing = ""
                src = "ledger-fallback (portal error %s)" % snapshot["probe_date"]
                anomalies.append(
                    "volume id %d: portal JSON answers an error page; pages %d-%d "
                    "and year %d taken from the committed H7275 ledger, "
                    "unverified against the portal" % (vid, lo, hi, year))
            else:
                lo = hi = year = None
                editor = opening = closing = ""
                src = "portal error, no ledger bridge"
        covered = [r for r in ledger
                   if lo is not None and page_overlap(lo, hi, r["pp_lo"], r["pp_hi"]) > 0]
        ledger_ids = ",".join(r["ledger_id"] for r in covered)
        in_digital = ("yes" if covered and all(r["in_digital_text"] == "yes"
                                               for r in covered)
                      else "no" if covered and all(r["in_digital_text"] == "no"
                                                   for r in covered)
                      else "partial/unknown")
        notes = []
        if src.startswith("ledger-fallback"):
            notes.append("portal metadata missing")
        # primary ledger row = maximal page overlap; secondary overlaps are
        # listed in ledger_rows but only the primary row drives notes, so a
        # boundary-straddling row does not spawn phantom disagreements
        primary = None
        if covered:
            primary = max(covered, key=lambda r: page_overlap(lo, hi,
                                                              r["pp_lo"],
                                                              r["pp_hi"]))
        if primary is not None and src == "koshashri-json":
            if primary["year"] != year:
                notes.append("year disagreement: portal %d vs ledger %d (%s)"
                             % (year, primary["year"], primary["ledger_id"]))
                anomalies.append("volume %d: portal year %d vs ledger year %d "
                                 "(row %s)"
                                 % (vid, year, primary["year"],
                                    primary["ledger_id"]))
            if (primary["pp_lo"], primary["pp_hi"]) != (lo, hi):
                notes.append("page-boundary disagreement: portal %d-%d vs "
                             "ledger %s %d-%d"
                             % (lo, hi, primary["ledger_id"],
                                primary["pp_lo"], primary["pp_hi"]))
                anomalies.append(
                    "volume %d: portal range %d-%d vs ledger row %s %d-%d"
                    % (vid, lo, hi, primary["ledger_id"],
                       primary["pp_lo"], primary["pp_hi"]))
        if len(covered) > 1:
            notes.append("also straddles ledger row(s) %s"
                         % ",".join(r["ledger_id"] for r in covered
                                    if r is not primary))
        rows.append({
            "koshashri_vol": vid,
            "portal_status": v["status"],
            "year": year if year is not None else "",
            "pages": ("%d-%d" % (lo, hi)) if lo is not None else "",
            "n_pages": (hi - lo + 1) if lo is not None else "",
            "editor": editor,
            "opening_entry": opening,
            "closing_entry": closing,
            "ledger_rows": ledger_ids,
            "in_cologne_digital_text": in_digital,
            "source": src,
            "notes": "; ".join(notes),
        })
    return rows, anomalies


COVERAGE_HEADER = ["koshashri_vol", "portal_status", "year", "pages", "n_pages",
                   "editor", "opening_entry", "closing_entry", "ledger_rows",
                   "in_cologne_digital_text", "source", "notes"]

