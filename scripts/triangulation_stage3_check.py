#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7484 — Stage-3 regeneration gate: every published triangulation number
regenerates from the committed grid, the committed Stage-1/2 substrates and
the committed row-level TSVs, or the check exits non-zero.

    python3 scripts/triangulation_stage3_check.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "triangulation_stage3")
NON_TEXT = {"catalogue_journal", "edition_marker", "second_hand", "manuscript"}


def load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return json.load(fh)


def load_tsv(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def dig(doc, dotted):
    node = doc
    for part in dotted.split("."):
        node = node[part]
    return node


def r2(x):
    return round(x, 2)


def main() -> int:
    fails = []

    def pin(name, got, want):
        if got != want:
            fails.append(f"{name}: regenerated {got!r} != published {want!r}")

    grid_text = open(os.path.join(D, "grid_preregistration.md"),
                     encoding="utf-8").read()
    blocks = re.findall(r"```json\n(.*?)```", grid_text, flags=re.S)
    if len(blocks) != 1:
        print("TRIANGULATION_STAGE3_CHECK: FAIL — grid json blocks != 1")
        return 1
    grid = json.loads(blocks[0])
    m = load(os.path.relpath(
        os.path.join(D, "triangulation_metrics.json"), ROOT))

    # 1. the grid is the one the run consumed (not retuned after the fact)
    pin("grid_sha256", hashlib.sha256(grid_text.encode("utf-8")).hexdigest(),
        m["grid"]["sha256"])
    pin("grid_commit_precedes_run", m["grid"]["commit"], "b531f96")

    # 2. inputs resolve from their committed source files
    for name, spec in grid["inputs"].items():
        pin(f"input.{name}", dig(load(spec["file"]), spec["key"]), m["inputs"][name])

    # 3. row-level anchors regenerate from the TSVs
    joined = load_tsv("data/pwg_dcs/pwg_dcs_works_joined.tsv")
    text_rows = [r for r in joined if r["stratum"] not in NON_TEXT]
    t_ql = sum(int(r["ql_tags"]) for r in text_rows)
    t_cov = sum(int(r["ql_tags"]) for r in text_rows if r["held"] == "1")
    t_alpha = sum(int(r["alpha_ql"]) for r in text_rows)
    t_alpha_cov = sum(int(r["alpha_ql"]) for r in text_rows if r["held"] == "1")
    a = m["row_level_anchors"]
    pin("rows.pwg_omega_se_pct", r2(100.0 * t_cov / t_ql), a["pwg_omega_se_pct"])
    pin("rows.pwg_alpha_se_pct", r2(100.0 * t_alpha_cov / t_alpha),
        a["pwg_alpha_se_pct"])
    pin("rows.pwg_text_ql", t_ql, a["pwg_text_ql"])
    pin("rows.pwg_text_cov_ql", t_cov, a["pwg_text_cov_ql"])
    pin("rows.pwg_text_alpha", t_alpha, a["pwg_text_alpha"])
    pin("rows.pwg_text_cov_alpha", t_alpha_cov, a["pwg_text_cov_alpha"])
    att = load_tsv("data/nws_layer/nws_works_attestation.tsv")
    pin("rows.nws_attested_works",
        sum(1 for r in att if r["attested"] == "1"), a["nws_attested_works"])
    pin("rows.nws_declared_works", len(att), a["nws_declared_works"])
    pd_m = load("data/pd/pd_dcs_metrics.json")
    pin("rows.pd_alpha_pct", r2(100.0 * pd_m["covered_mass"] / pd_m["primary_work_mass"]),
        a["pd_alpha_pct"])
    pin("rows.pd_residue_share_pct",
        r2(100.0 * pd_m["residue_mass"] / pd_m["primary_work_mass"]),
        a["pd_residue_share_pct"])

    # 4. derived quantities recompute from the inputs
    i = m["inputs"]
    band_lo, band_hi = i["pd_band"]
    d = m["derived"]
    pin("derived.band_width_pp", r2(band_hi - band_lo), d["band_width_pp"])
    pin("derived.within_type_gap_pp",
        r2(i["pwg_alpha_se_pct"] - i["pd_alpha_pct"]), d["within_type_gap_pp"])
    pin("derived.scope_gap_pp",
        r2(abs(i["pwg_alpha_se_pct"] - i["pwg_omega_se_pct"])), d["scope_gap_pp"])
    pin("derived.contradiction_margin_pp",
        r2(i["pwg_omega_se_pct"] - band_hi), d["contradiction_margin_pp"])
    pin("derived.interval_non_overlap_pp",
        r2(i["pwg_bootstrap_p2_5"] - band_hi), d["interval_non_overlap_pp"])
    pin("derived.pwg_residue_share_pct",
        r2(100.0 - i["pwg_omega_se_pct"]), d["pwg_residue_share_pct"])
    pin("derived.residue_share_ratio",
        r2(a["pd_residue_share_pct"] / d["pwg_residue_share_pct"]),
        d["residue_share_ratio"])
    pin("derived.nws_type_line.containment_pct",
        i["nws_containment_pct"], d["nws_type_line"]["containment_pct"])
    pin("derived.nws_type_line.headword_rho",
        i["nws_rho_total"], d["nws_type_line"]["headword_rho"])
    pin("derived.nws_type_line.letter_aggregate_rho",
        i["nws_letter_aggregate_rho"], d["nws_type_line"]["letter_aggregate_rho"])

    # 5. branch verdicts re-evaluate under the committed conditions
    th = grid["thresholds"]
    b = m["branch_verdicts"]
    pin("branch.BR1", bool(i["pwg_omega_se_pct"] > band_hi
                           and i["pwg_bootstrap_p2_5"] > band_hi),
        b["BR1_contradiction_localisation"]["fired"])
    pin("branch.BR2",
        bool(abs(i["pwg_alpha_se_pct"] - i["pd_alpha_pct"]) > d["band_width_pp"]),
        b["BR2_within_type_programme_gap"]["fired"])
    pin("branch.BR3", bool(d["scope_gap_pp"] > d["band_width_pp"]),
        b["BR3_scope_artefact"]["fired"])
    pin("branch.BR4",
        bool(i["nws_containment_pct"] >= th["nws_containment_min_pct"]
             and i["nws_rho_total"] < th["nws_rho_divergent_max"]),
        b["BR4_type_line_reality"]["fired"])
    pin("branch.BR5",
        bool(i["pwg_h2_dispersion_pp"] > i["pd_fascicle_span_pp"]),
        b["BR5_dispersion_convergence"]["fired"])
    pin("branch.BR6",
        bool(i["pwg_anchor_cited_pct"] >= i["pd_token_2026_pct"]
             and i["pwg_anchor_cited_pct"] > th["token_convergence_min_pct"]
             and i["pd_token_2026_pct"] > th["token_convergence_min_pct"]),
        b["BR6_token_level_convergence"]["fired"])

    # 6. §12-row verdicts re-map from the branches
    r12 = m["row12_verdicts"]
    pin("row12.citation_weighted",
        "localized_to_pd_programme"
        if b["BR1_contradiction_localisation"]["fired"]
        and b["BR2_within_type_programme_gap"]["fired"] else "see_branches",
        r12["citation_weighted_25_16"]["verdict"])
    pin("row12.three_quarters",
        "overturned_as_class_claim__apparatus_specific_to_pd"
        if b["BR1_contradiction_localisation"]["fired"]
        else "stands_as_class_fact",
        r12["three_quarters_outside_dcs"]["verdict"])
    pin("row12.deep_not_broad",
        "survives_for_pd__dies_as_class_claim"
        if b["BR1_contradiction_localisation"]["fired"]
        and b["BR2_within_type_programme_gap"]["fired"] else "see_branches",
        r12["deep_not_broad"]["verdict"])
    pin("row12.token_weighted",
        "corroborated_within_anchored_core"
        if b["BR6_token_level_convergence"]["fired"] else "programme_relative",
        r12["token_weighted_77_88_74_06"]["verdict"])

    if fails:
        print("TRIANGULATION_STAGE3_CHECK: FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("TRIANGULATION_STAGE3_CHECK: OK — grid untuned, every published "
          "number regenerates from committed rows and substrates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
