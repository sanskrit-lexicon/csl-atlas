#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7484 — Stage 3: the PD/PWG/NWS triangulation under the pre-registered grid.

Reads the grid committed BEFORE this run
(data/triangulation_stage3/grid_preregistration.md, fenced JSON block),
resolves every input from the committed Stage-1/Stage-2 substrates,
regenerates the row-level anchors, evaluates branches BR1-BR6, maps the
§12 rows to their pre-declared outcome space, and writes
data/triangulation_stage3/triangulation_metrics.json.

No new measurement: quantities already committed at Stages 1-2 are consumed
as inputs (their own check scripts gate them); Stage-3-derived quantities
(gaps, margins, ratios, verdicts) are computed here and gated by
scripts/triangulation_stage3_check.py.

    python3 scripts/triangulation_stage3_join.py
"""
from __future__ import annotations

import csv
import datetime
import hashlib
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRID = os.path.join(ROOT, "data", "triangulation_stage3", "grid_preregistration.md")
OUT = os.path.join(ROOT, "data", "triangulation_stage3", "triangulation_metrics.json")

NON_TEXT = {"catalogue_journal", "edition_marker", "second_hand", "manuscript"}


def load_metrics(rel):
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


def parse_grid(path):
    text = open(path, encoding="utf-8").read()
    blocks = re.findall(r"```json\n(.*?)```", text, flags=re.S)
    if len(blocks) != 1:
        raise SystemExit(f"grid must carry exactly one json block, found {len(blocks)}")
    return json.loads(blocks[0]), hashlib.sha256(
        text.encode("utf-8")).hexdigest()


def r2(x):
    return round(x, 2)


def main() -> int:
    grid, grid_sha = parse_grid(GRID)
    inputs = {}
    for name, spec in grid["inputs"].items():
        inputs[name] = dig(load_metrics(spec["file"]), spec["key"])

    # ---- row-level regeneration anchors (same rules as the stage gates) ----
    joined = load_tsv("data/pwg_dcs/pwg_dcs_works_joined.tsv")
    text_rows = [r for r in joined if r["stratum"] not in NON_TEXT]
    t_ql = sum(int(r["ql_tags"]) for r in text_rows)
    t_cov = sum(int(r["ql_tags"]) for r in text_rows if r["held"] == "1")
    t_alpha = sum(int(r["alpha_ql"]) for r in text_rows)
    t_alpha_cov = sum(int(r["alpha_ql"]) for r in text_rows if r["held"] == "1")
    regen = {
        "pwg_omega_se_pct": r2(100.0 * t_cov / t_ql),
        "pwg_alpha_se_pct": r2(100.0 * t_alpha_cov / t_alpha),
        "pwg_text_ql": t_ql,
        "pwg_text_cov_ql": t_cov,
        "pwg_text_alpha": t_alpha,
        "pwg_text_cov_alpha": t_alpha_cov,
    }
    att = load_tsv("data/nws_layer/nws_works_attestation.tsv")
    regen["nws_attested_works"] = sum(1 for r in att if r["attested"] == "1")
    regen["nws_declared_works"] = len(att)
    pd_m = load_metrics("data/pd/pd_dcs_metrics.json")
    regen["pd_alpha_pct"] = r2(100.0 * pd_m["covered_mass"] / pd_m["primary_work_mass"])
    regen["pd_residue_share_pct"] = r2(
        100.0 * pd_m["residue_mass"] / pd_m["primary_work_mass"])

    # every grid input that has a row-level regeneration must agree
    mismatches = [
        f"{k}: rows say {regen[k]!r}, committed input says {inputs[k]!r}"
        for k in ("pwg_omega_se_pct", "pwg_alpha_se_pct", "nws_attested_works",
                  "nws_declared_works", "pd_alpha_pct")
        if regen[k] != inputs[k]
    ]
    if mismatches:
        for m in mismatches:
            print("ROW-ANCHOR MISMATCH:", m, file=sys.stderr)
        return 1

    # ---- derived triangulated quantities ----
    band_lo, band_hi = inputs["pd_band"]
    band_width = r2(band_hi - band_lo)
    pwg_residue_share = r2(100.0 - inputs["pwg_omega_se_pct"])
    derived = {
        "band_width_pp": band_width,
        "within_type_gap_pp": r2(inputs["pwg_alpha_se_pct"] - inputs["pd_alpha_pct"]),
        "scope_gap_pp": r2(abs(inputs["pwg_alpha_se_pct"] - inputs["pwg_omega_se_pct"])),
        "contradiction_margin_pp": r2(inputs["pwg_omega_se_pct"] - band_hi),
        "interval_non_overlap_pp": r2(inputs["pwg_bootstrap_p2_5"] - band_hi),
        "pd_residue_share_pct": regen["pd_residue_share_pct"],
        "pwg_residue_share_pct": pwg_residue_share,
        "residue_share_ratio": r2(regen["pd_residue_share_pct"] / pwg_residue_share),
        "nws_type_line": {
            "containment_pct": inputs["nws_containment_pct"],
            "headword_rho": inputs["nws_rho_total"],
            "letter_aggregate_rho": inputs["nws_letter_aggregate_rho"],
            "reading": "inventory contained, allocation divergent — the type "
                       "line carries information (envelope tracks at letter "
                       "level, within-letter allocation does not)",
        },
        "token_level_pair": {
            "pd_token_weighted_2026_pct": inputs["pd_token_2026_pct"],
            "pd_token_weighted_2021_pct": inputs["pd_token_2021_pct"],
            "pwg_anchor_cited_pct": inputs["pwg_anchor_cited_pct"],
            "construction_note": "PWG's share is within the 118-text DCS "
                "anchor (PD-covered-by-construction); PD's 77.88 is against "
                "the whole corpus. Same-side reading: within the anchored "
                "core, PWG independently cites 93.98% of token mass.",
        },
    }

    # ---- branch evaluation (conditions fixed by the committed grid) ----
    th = grid["thresholds"]
    br = {
        "BR1_contradiction_localisation": {
            "fired": inputs["pwg_omega_se_pct"] > band_hi
                     and inputs["pwg_bootstrap_p2_5"] > band_hi,
            "evidence": {
                "pwg_omega_se_pct": inputs["pwg_omega_se_pct"],
                "bootstrap_p2_5": inputs["pwg_bootstrap_p2_5"],
                "band_top": band_hi,
            },
        },
        "BR2_within_type_programme_gap": {
            "fired": abs(inputs["pwg_alpha_se_pct"] - inputs["pd_alpha_pct"]) > band_width,
            "evidence": {
                "gap_pp": derived["within_type_gap_pp"],
                "band_width_pp": band_width,
            },
        },
        "BR3_scope_artefact": {
            "fired": derived["scope_gap_pp"] > band_width,
            "evidence": {
                "scope_gap_pp": derived["scope_gap_pp"],
                "band_width_pp": band_width,
            },
        },
        "BR4_type_line_reality": {
            "fired": inputs["nws_containment_pct"] >= th["nws_containment_min_pct"]
                     and inputs["nws_rho_total"] < th["nws_rho_divergent_max"],
            "evidence": {
                "containment_pct": inputs["nws_containment_pct"],
                "headword_rho": inputs["nws_rho_total"],
            },
        },
        "BR5_dispersion_convergence": {
            "fired": inputs["pwg_h2_dispersion_pp"] > inputs["pd_fascicle_span_pp"],
            "evidence": {
                "pwg_dispersion_pp": inputs["pwg_h2_dispersion_pp"],
                "pd_fascicle_span_pp": inputs["pd_fascicle_span_pp"],
            },
        },
        "BR6_token_level_convergence": {
            "fired": inputs["pwg_anchor_cited_pct"] >= inputs["pd_token_2026_pct"]
                     and inputs["pwg_anchor_cited_pct"] > th["token_convergence_min_pct"]
                     and inputs["pd_token_2026_pct"] > th["token_convergence_min_pct"],
            "evidence": {
                "pwg_anchor_cited_pct": inputs["pwg_anchor_cited_pct"],
                "pd_token_weighted_2026_pct": inputs["pd_token_2026_pct"],
            },
        },
    }

    # ---- §12-row verdicts (outcome space fixed by the committed grid) ----
    row12 = {
        "citation_weighted_25_16": {
            "verdict": "localized_to_pd_programme"
                       if br["BR1_contradiction_localisation"]["fired"]
                       and br["BR2_within_type_programme_gap"]["fired"]
                       else "see_branches",
            "basis": "BR1+BR2",
        },
        "three_quarters_outside_dcs": {
            "verdict": "overturned_as_class_claim__apparatus_specific_to_pd"
                       if br["BR1_contradiction_localisation"]["fired"]
                       else "stands_as_class_fact",
            "basis": "BR1",
        },
        "residue_four_cluster_structure": {
            "verdict": "not_triangulable_row_level",
            "basis": "no genre-level rows for the PWG residue in the committed "
                     "substrates; Stage-1 report §4 carries the qualitative "
                     "cluster remark only",
        },
        "declared_canon_8pct": {
            "verdict": "declared_vs_exercised_distinction_corroborated_by_nws_h6",
            "basis": f"NWS {inputs['nws_attested_works']}/"
                     f"{inputs['nws_declared_works']} exercised; the PWG "
                     "527/2,665 analogue is report-level, not row-committed",
        },
        "token_weighted_77_88_74_06": {
            "verdict": "corroborated_within_anchored_core"
                       if br["BR6_token_level_convergence"]["fired"]
                       else "programme_relative",
            "basis": "BR6 + construction note",
        },
        "density_multiple": {
            "verdict": "already_corroborated_and_bounded_stage1",
            "basis": "PWG 6.50 vs MW 1.12 <ls>/entry; not re-measured",
        },
        "chronological_order": {
            "verdict": "open__h4_not_executed_in_stages_1_2",
            "basis": "no committed work-date join rows; no Stage-3 claim",
        },
        "deep_not_broad": {
            "verdict": "survives_for_pd__dies_as_class_claim"
                       if br["BR1_contradiction_localisation"]["fired"]
                       and br["BR2_within_type_programme_gap"]["fired"]
                       else "see_branches",
            "basis": "BR1+BR2",
        },
    }

    out = {
        "created": datetime.date.today().isoformat(),
        "dataset": "triangulation_stage3/triangulation_metrics",
        "license": "CC-BY-SA-4.0",
        "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0/",
        "generated_by": "scripts/triangulation_stage3_join.py",
        "handoff": "H7484",
        "protocol": grid["protocol"],
        "grid": {
            "path": "data/triangulation_stage3/grid_preregistration.md",
            "sha256": grid_sha,
            "committed_before_run": True,
            "commit": "b531f96",
        },
        "inputs": inputs,
        "row_level_anchors": regen,
        "derived": derived,
        "branch_verdicts": br,
        "row12_verdicts": row12,
        "kill_exits_respected": grid["kill_exits_respected"],
        "unconditional": [
            "kosha reframing stands regardless (12 held koshas are a catalogue fact)",
            "no stage-3 verdict upgrades genre-level certification into task adequacy",
        ],
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False, sort_keys=True)
        fh.write("\n")
    print("TRIANGULATION_STAGE3_JOIN: wrote", os.path.relpath(OUT, ROOT))
    for name, verdict in br.items():
        print(f"  {name}: {'FIRED' if verdict['fired'] else 'not fired'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
