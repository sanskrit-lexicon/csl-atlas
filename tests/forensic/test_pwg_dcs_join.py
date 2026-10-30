#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7463 pins — the PWG↔DCS Stage 1 join artefacts.

Hand-derived/measured pins on scripts/pwg_work_register.py outputs and the
join metrics; drift here is a broken artefact, not news. Run the generator
scripts first (they are read-only over inputs, deterministic over outputs).
"""
from __future__ import annotations

import csv
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = os.path.join(ROOT, "data", "pwg_dcs")


def test_register_pins():
    rows = list(csv.DictReader(open(os.path.join(D, "pwg_work_register.tsv"),
                                    encoding="utf-8"), delimiter="\t"))
    assert sum(int(r["raw_tags"]) for r in rows) == 801788
    assert sum(int(r["ql_tags"]) for r in rows) == 729719
    assert sum(int(r["alpha_ql"]) for r in rows) == 132483
    by_key = {r["base_siglum"]: r for r in rows}
    # the highest-mass siglum is the Mahābhārata family
    top = max(rows, key=lambda r: int(r["ql_tags"]))
    assert top["base_siglum"] == "MBH"
    # a kośa is high-mass and its base key is stable
    assert int(by_key["ŚKDR"]["ql_tags"]) == 17639


def test_join_pins():
    m = json.load(open(os.path.join(D, "pwg_dcs_join_metrics.json"),
                       encoding="utf-8"))
    c = m["coverage"]
    assert c["denominators"]["total_ql"] == 729719
    assert c["pooled_omega"] == 59.0
    assert c["stratum_excluded_omega"] == 63.53
    assert c["stratum_excluded_alpha"] == 63.59
    # per-stratum holdings: the kośa class is partially held (DCS Kosha genre)
    assert m["strata"]["kosha_lexicon"]["held_works"] >= 4
    # committed-grid verdicts (thresholds pre-registered before the join)
    assert m["grid"]["convergence"] is False
    assert m["grid"]["divergence_branch"] and "above_band" in m["grid"]["divergence_branch"]
    assert m["grid"]["contradiction"] is True
    assert m["h2"]["exceeds"] is True


def test_dcs_catalogue_pins():
    rows = list(csv.DictReader(open(os.path.join(D, "dcs_catalogue_2026-10-30.tsv"),
                                    encoding="utf-8"), delimiter="\t"))
    assert len(rows) == 285
    kosha = [r for r in rows if r["genre"] == "Kosha"]
    assert len(kosha) == 12          # the report's twelve-held-kośas fact
    assert any(r["title"] == "Amarakośa" for r in kosha)
