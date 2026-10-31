#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7513 pins — the MW-vs-PWG/pwk missing-entries scan artefacts.

Hand-measured pins on scripts/mw_vs_pw_missing_build.py outputs; drift here
is a broken artefact, not news. Pure committed-data pins (no csl-orig needed,
CI-safe); the substrate sha256 verification lives in scripts/mw_vs_pw_check.py
and runs wherever csl-orig is present.
"""
from __future__ import annotations

import csv
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = os.path.join(ROOT, "data", "mw_vs_pw")


def _rows():
    return list(csv.DictReader(open(os.path.join(D, "mw_missing_candidates.tsv"),
                                    encoding="utf-8"), delimiter="\t"))


def test_universe_and_class_partition():
    m = json.load(open(os.path.join(D, "mw_vs_pw_metrics.json"), encoding="utf-8"))
    u = m["comparison_universe"]
    # denominators stated for BOTH classes (the mission requirement)
    assert u["denominator"] == 157994          # |distinct base k1 in PWG ∪ pwk|
    assert u["in_mw_exact"] == 132284
    assert u["candidates_total"] == 25710
    a = m["classes"]["a_missing_by_error"]
    b = m["classes"]["b_expected_absence"]
    assert a["denominator"] == b["denominator"] == u["denominator"]
    assert a["count"] == 19465
    assert b["count"] == 6245
    assert a["count"] + b["count"] == u["candidates_total"]
    # 83.7 % of the PWG/pwk universe resolves verbatim in MW
    assert round(100.0 * u["in_mw_exact"] / u["denominator"], 1) == 83.7


def test_subclass_breakdown():
    m = json.load(open(os.path.join(D, "mw_vs_pw_metrics.json"), encoding="utf-8"))
    sub = m["classes"]["a_missing_by_error"]["subclasses"]
    assert sub["a_missing_by_error.mw_lacks"] == 5021
    assert sub["a_missing_by_error.form_unresolved_nearform"] == 11483
    assert sub["a_missing_by_error.form_unresolved_stem"] == 2961
    bsub = m["classes"]["b_expected_absence"]["subclasses"]
    assert bsub["b_expected_absence.mw_lacks"] == 1943


def test_canary_karitra():
    """The motivating case (csl-corrections #119): PWK Nachträge 7-331-d
    'kAritra' (MAHĀVY. 245, 844) is absent from MW and fuzzy-hits the
    DIFFERENT word kArita at 0.92 — the near-form trap, pinned."""
    rows = [r for r in _rows() if r["slp1"] == "kAritra"]
    assert len(rows) == 1
    r = rows[0]
    assert r["class"] == "a_missing_by_error"
    assert r["subclass"] == "form_unresolved_nearform"
    assert r["mw_fuzzy"] == "kArita"
    assert float(r["fuzzy_ratio"]) == 0.92
    assert set(r["sources"].split("+")) == {"pw", "pwkvn"}
    assert "pwkvn.txt:" in r["evidence"] and "L=16013" in r["evidence"]
    assert "bhs" in r["corroboration_dicts"].split(",")


def test_evidence_contract():
    """Every candidate row is keyed to file, line and headword form."""
    rows = _rows()
    assert len(rows) == 25710
    for r in rows:
        assert ".txt:" in r["evidence"] and "L=" in r["evidence"]
        assert r["slp1"] and r["iast"]
        assert r["class"] in ("a_missing_by_error", "b_expected_absence")


def test_corroboration_pins():
    m = json.load(open(os.path.join(D, "mw_vs_pw_metrics.json"), encoding="utf-8"))
    c = m["corroboration"]
    assert len(c["dictionaries"]) == 39
    assert c["a_with_ge1"] == 9799
    assert c["a_with_ge2"] == 4405
    # the strongest worklist: NO-MATCH + cited + >=2 independent dictionaries
    assert c["a_nomatch_with_ge2"] == 897


def test_substrate_reuse_pin():
    """pwg.txt is pinned to the H7463 Stage-1 substrate sha (data/pwg_dcs)."""
    m = json.load(open(os.path.join(D, "mw_vs_pw_metrics.json"), encoding="utf-8"))
    s = m["substrate_reuse"]
    assert s["pwg_txt_sha256"].startswith("430c910f8b0c")
    assert s["pwg_dcs_pin_sha_matches"] is True
    assert s["pwg_entries_pin"] == 123366
    assert m["sources"]["pwg"]["entries"] == 123366
