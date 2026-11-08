#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7484 pins — the PD/PWG/NWS Stage-3 triangulation artefacts.

Drift here is a broken artefact, not news. The grid sha pin is the
"committed before the run, not retuned" guarantee: any edit to the grid
after commit b531f96 fails here and in triangulation_stage3_check.py.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = os.path.join(ROOT, "data", "triangulation_stage3")

GRID_SHA = "b020d966735a3e2b98befb3ccf69339c9e5564c71398633d75244177d59b39c7"


def test_grid_untuned():
    text = open(os.path.join(D, "grid_preregistration.md"), encoding="utf-8").read()
    assert hashlib.sha256(text.encode("utf-8")).hexdigest() == GRID_SHA


def test_triangulation_pins():
    m = json.load(open(os.path.join(D, "triangulation_metrics.json"),
                       encoding="utf-8"))
    # committed inputs the triangulation consumed
    assert m["inputs"]["pd_alpha_pct"] == 25.16
    assert m["inputs"]["pwg_omega_se_pct"] == 63.53
    assert m["inputs"]["pwg_alpha_se_pct"] == 63.59
    assert m["inputs"]["nws_rho_total"] == 0.3414
    assert m["inputs"]["nws_containment_pct"] == 82.57
    assert m["inputs"]["pd_band"] == [19.15, 31.52]
    # derived triangulated quantities
    assert m["derived"]["within_type_gap_pp"] == 38.43
    assert m["derived"]["scope_gap_pp"] == 0.06
    assert m["derived"]["contradiction_margin_pp"] == 32.01
    assert m["derived"]["interval_non_overlap_pp"] == 15.1
    assert m["derived"]["pd_residue_share_pct"] == 74.84
    assert m["derived"]["pwg_residue_share_pct"] == 36.47
    assert m["derived"]["residue_share_ratio"] == 2.05
    # branch verdicts (pre-registered conditions, evaluated)
    assert m["branch_verdicts"]["BR1_contradiction_localisation"]["fired"] is True
    assert m["branch_verdicts"]["BR2_within_type_programme_gap"]["fired"] is True
    assert m["branch_verdicts"]["BR3_scope_artefact"]["fired"] is False
    assert m["branch_verdicts"]["BR4_type_line_reality"]["fired"] is True
    assert m["branch_verdicts"]["BR5_dispersion_convergence"]["fired"] is True
    assert m["branch_verdicts"]["BR6_token_level_convergence"]["fired"] is True
    # §12-row verdicts
    assert m["row12_verdicts"]["citation_weighted_25_16"]["verdict"] \
        == "localized_to_pd_programme"
    assert m["row12_verdicts"]["three_quarters_outside_dcs"]["verdict"] \
        == "overturned_as_class_claim__apparatus_specific_to_pd"
    assert m["row12_verdicts"]["deep_not_broad"]["verdict"] \
        == "survives_for_pd__dies_as_class_claim"
    assert m["row12_verdicts"]["token_weighted_77_88_74_06"]["verdict"] \
        == "corroborated_within_anchored_core"
    assert m["row12_verdicts"]["residue_four_cluster_structure"]["verdict"] \
        == "not_triangulable_row_level"
    assert m["row12_verdicts"]["chronological_order"]["verdict"] \
        == "open__h4_not_executed_in_stages_1_2"
