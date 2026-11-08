#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7476 pins — the NWS-layer Stage 2 artefacts (data/nws_layer/).

Hand-measured pins on the committed row-level TSVs and the join metrics;
drift here is a broken artefact, not news. The extractor
(scripts/nws_layer_extract.py, local-only) is fail-closed on the kosha H6064
pins; the join/check regenerate every number from these rows.
"""
from __future__ import annotations

import csv
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = os.path.join(ROOT, "data", "nws_layer")


def tsv(name):
    return list(csv.DictReader(open(os.path.join(D, name), encoding="utf-8"),
                               delimiter="\t"))


def test_substrate_pins():
    hw = tsv("nws_headword_mass.tsv")
    pwg = tsv("pwg_headword_ql.tsv")
    env = tsv("nws_letter_envelope.tsv")
    census = tsv("nws_x_mw_census.tsv")
    assert len(hw) == 34101                       # prose entries (denominator)
    assert len(pwg) == 123366                     # PWG entries
    assert sum(int(r["ql_tags"]) for r in pwg) == 729719   # pre-reg (a)
    assert sum(int(r["raw_tags"]) for r in pwg) == 801788
    assert sum(int(r["keys_total"]) for r in env) == 167990
    assert sum(int(r["keys_prose"]) for r in env) == 34101
    assert sum(int(r["page_refs"]) for r in hw) == 8440
    assert sum(int(r["lit_refs"]) for r in hw) == 8937
    assert census[0]["marker"] == "Lex(MW)"
    assert int(census[0]["count"]) == 5873        # the dependence tracer head


def test_h5_h6_pins():
    m = json.load(open(os.path.join(D, "nws_layer_metrics.json"), encoding="utf-8"))
    r1 = m["role1_attestation_mass"]
    assert r1["shared_headwords"] == 28158
    assert r1["containment_pct"] == 82.57
    assert r1["spearman_vs_pwg_ql"]["mass_total"] == 0.3414
    assert r1["spearman_vs_pwg_ql"]["n"] == 28158
    assert r1["letter_aggregate_rho"] == 0.9782
    assert r1["decile_inversions"] == 2
    # H5 verdict follows the declared mapping (rho 0.34 < 0.40 -> divergent),
    # and the upgrade conditional stays gated: the Halle print remainder is
    # NOT quantified on this substrate (H5940).
    assert m["h5"]["verdict"] == "divergent"
    assert r1["undigitized_halle_remainder"]["print_remainder_quantified"] is False
    # H6: 82/174 from the dated scrape with its hash, never from stems
    r2 = m["role2_declared_vs_exercised"]
    assert r2["attested_works"] == 82 and r2["declared_works"] == 174
    assert r2["scrape"]["fetched"] == "2026-10-06"
    assert r2["scrape"]["html_sha256"].startswith("86c9495e")


def test_tracer_pins():
    m = json.load(open(os.path.join(D, "nws_layer_metrics.json"), encoding="utf-8"))
    r3 = m["role3_dependence_tracer"]
    assert r3["lex_mw_markers"] == 5873
    assert r3["x_mw_family_total"] == 13738
    assert r3["x_mw_kinds"] == 41
    assert r3["pure_mw_mediated_entries"] == 3356
    assert r3["pure_mw_mediated_share_pct"] == 9.84
    # the inventory join stays pre-registered out
    assert "OUT" in m["pre_registered_out"]["nws_dcs_inventory_join"]
