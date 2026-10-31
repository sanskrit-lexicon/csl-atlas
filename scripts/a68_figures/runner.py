"""main() — loads committed inputs, runs the cross-check gate, writes SVGs."""
from .helpers import (C4_LAYERS, DATA, OUT, PIN_ADJUDICATED, check,
                      read_tsv, wilson)
from .figs_core import fig1, fig2, fig3, fig4
from .figs_catalogue_a import fig5, fig6, fig7, fig8, fig9, fig15
from .figs_catalogue_b import fig10, fig11, fig12, fig13, fig14
from .figs_catalogue_c import fig14b, fig16
from . import figs_style_fig10 as ss10
from . import figs_style_fig7 as ss7
import json
import sys


def main():
    m = json.loads((DATA / "pd_dcs_metrics.json").read_text(encoding="utf-8"))
    families = read_tsv(DATA / "pd_siglum_families.tsv")
    crosswalk = read_tsv(DATA / "pd_dcs_text_crosswalk.tsv")

    # --- Re-derive every plotted number from the row-level TSVs ---
    print("Cross-checking derived metrics against pd_dcs_metrics.json:")
    total = sum(int(r["count"]) for r in families)
    by_class = {}
    for r in families:
        by_class[r["class"]] = by_class.get(r["class"], 0) + int(r["count"])
    covered = sum(int(r["count"]) for r in families if r["match_type"] == "covered")
    primary = by_class.get("primary", 0)
    residue = primary - covered
    cov_tok_21 = sum(int(r["dcs_tok_2021"]) for r in crosswalk)
    cov_tok_26 = sum(int(r["dcs_tok_2026"]) for r in crosswalk)

    ok = True
    ok &= check("total_siglum_mass", total, m["total_siglum_mass"])
    ok &= check("structural_mass", by_class.get("structural", 0), m["structural_mass"])
    ok &= check("secondary_mass", by_class.get("secondary", 0), m["secondary_mass"])
    ok &= check("primary_work_mass", primary, m["primary_work_mass"])
    ok &= check("covered_mass", covered, m["covered_mass"])
    ok &= check("residue_mass", residue, m["residue_mass"])
    ok &= check("n_covered_dcs_titles", len(crosswalk), m["n_covered_dcs_titles"])
    ok &= check("metric_pd_citation_weighted_pct",
                round(100.0 * covered / primary, 2),
                m["metric_pd_citation_weighted_pct"], tol=0.01)
    ok &= check("covered_dcs_tok_2021", cov_tok_21, m["covered_dcs_tok_2021"])
    ok &= check("covered_dcs_tok_2026", cov_tok_26, m["covered_dcs_tok_2026"])
    ok &= check("metric_dcs_token_weighted_2026_pct",
                round(100.0 * cov_tok_26 / m["total_dcs_tok_2026"], 2),
                m["metric_dcs_token_weighted_2026_pct"], tol=0.01)
    ok &= check("metric_dcs_token_weighted_2021_pct",
                round(100.0 * cov_tok_21 / m["total_dcs_tok_2021"], 2),
                m["metric_dcs_token_weighted_2021_pct"], tol=0.01)
    if not ok:
        print("DRIFT DETECTED — refusing to draw figures from stale metrics.")
        return 2

    # --- H7545 gate: figures 5-15 inputs (same abort-on-mismatch rule) ---
    print("Cross-checking fig5-15 inputs:")
    fasc = read_tsv(DATA / "pd_two_layer_fascicle.tsv")
    ledger = read_tsv(DATA / "pd_publication_ledger.tsv")
    dens = read_tsv(DATA / "pd_policy_matched_density.tsv")
    cls = read_tsv(DATA / "pd_two_layer_class.tsv")
    avail_sig = read_tsv(DATA / "pd_edition_availability_by_siglum.tsv")
    avail_summary = json.loads(
        (DATA / "pd_edition_availability_summary.json").read_text(encoding="utf-8"))

    # fig6 fascicle strip: measured fascicles only; pins 16.91-36.90, 12/24
    meas = [r for r in fasc if r["coverage_pct"].strip()]
    fmin = min(float(r["coverage_pct"]) for r in meas)
    fmax = max(float(r["coverage_pct"]) for r in meas)
    fout = sum(1 for r in meas
               if abs(float(r["coverage_pct"]) - 25.16) > 2.0)
    ok &= check("fascicle_measured_n", len(meas), 24)
    ok &= check("fascicle_band_min", fmin, 16.91, tol=0.005)
    ok &= check("fascicle_band_max", fmax, 36.90, tol=0.005)
    ok &= check("fascicle_outside_2pp", fout, 12)
    for r in meas:
        k = int(r["covered_loci"])
        n = int(r["primary_loci"])
        cov = 100.0 * k / n
        wlo, whi = wilson(k, n)
        tag = f"fascicle {r['ledger_id']}"
        ok &= check(f"{tag} coverage_pct", round(cov, 2),
                    float(r["coverage_pct"]), tol=0.01)
        ok &= check(f"{tag} wilson_lo", round(wlo, 2), float(r["wilson_lo"]),
                    tol=0.02)
        ok &= check(f"{tag} wilson_hi", round(whi, 2), float(r["wilson_hi"]),
                    tol=0.02)

    # fig7 ladder: metrics rungs already gated above; pin rung is a literal
    print(f"  [PIN ] P-adjudicated = {PIN_ADJUDICATED:,} "
          f"(A68_CLAIM_LEDGER.tsv / iscls.tex §5.2.1, 164 titles)")

    # fig8 timeline: 35 fascicles 1976-2019, monotonic years
    years = [int(r["year"]) for r in ledger]
    ok &= check("ledger_rows", len(ledger), 35)
    ok &= check("ledger_year_min", min(years), 1976)
    ok &= check("ledger_year_max", max(years), 2019)
    ok &= check("ledger_years_monotonic",
                1 if all(a <= b for a, b in zip(years, years[1:])) else 0, 1)

    # fig9 paired bars: stratum ratios re-derive; pooled 157,480 / 18,423
    for r in dens:
        if r["row_kind"] != "stratum":
            continue
        ratio = int(r["pd_attestations"]) / int(r["pwg_attestations"])
        ok &= check(f"density {r['stratum']} ratio", round(ratio, 4),
                    float(r["attestation_ratio"]), tol=0.01)
    pooled_row = next(r for r in dens
                      if r["stratum"] == "pooled_standardised_equal_weight")
    ok &= check("density pooled pd", int(pooled_row["pd_attestations"]), 157480)
    ok &= check("density pooled pwg", int(pooled_row["pwg_attestations"]), 18423)

    # fig10/11 C4 layer table: sums vs metrics; texts sum = 118
    c4_tot26 = sum(r[2] for r in C4_LAYERS)
    c4_tot21 = sum(r[3] for r in C4_LAYERS)
    c4_cov26 = sum(r[5] for r in C4_LAYERS)
    c4_cit = sum(r[6] for r in C4_LAYERS)
    c4_texts = sum(r[4] for r in C4_LAYERS)
    ok &= check("c4 tok2026 sum", c4_tot26, m["total_dcs_tok_2026"])
    ok &= check("c4 tok2021 sum (metrics + 892 dropped stubs)", c4_tot21,
                m["total_dcs_tok_2021"] + 892)
    ok &= check("c4 cov118 tok2026", c4_cov26, m["covered_dcs_tok_2026"])
    ok &= check("c4 PD citations = covered_mass", c4_cit, m["covered_mass"])
    ok &= check("c4 cov118 texts", c4_texts, m["n_covered_dcs_titles"])
    ve = sum(r[2] for r in C4_LAYERS if r[0] in ("Vedic", "epic"))
    cl = sum(r[2] for r in C4_LAYERS if r[0] in ("śāstra", "kāvya", "purāṇic"))
    ve_cov = sum(r[5] for r in C4_LAYERS if r[0] in ("Vedic", "epic"))
    ok &= check("c4 Vedic+epic % 2026", round(100 * ve / c4_tot26, 1), 44.0,
                tol=0.05)
    ok &= check("c4 classical % 2026", round(100 * cl / c4_tot26, 1), 52.0,
                tol=0.05)
    ok &= check("c4 cov Vedic+epic % (exact 53.05, sweep prose says 53.1)",
                round(100 * ve_cov / c4_cov26, 1), 53.0, tol=0.0)

    # fig12 availability: per-status group-by vs committed summary
    order = ("available_full", "available_partial", "available_embedded",
             "unresolved")
    agg = {c: 0 for c in order}
    for r in avail_sig:
        a = r["availability"].strip() or "unresolved"
        agg[a if a in agg else "unresolved"] += int(r["attestations"])
    atot = sum(agg.values())
    ok &= check("availability attestations total", atot,
                avail_summary["totals"]["attestations"])
    for c in order:
        ok &= check(f"availability {c}", agg[c],
                    avail_summary["by_status"][c]["attestations"])
    ok &= check("availability available_work_level",
                agg["available_full"] + agg["available_partial"]
                + agg["available_embedded"],
                avail_summary["totals"]["available_work_level"])
    ok &= check("availability aob rows", avail_summary["aob_entries"]["rows"],
                1437)

    # fig15 class forest: coverage + Wilson re-derivation per class
    for r in cls:
        k = int(r["covered_loci"])
        n = int(r["primary_loci"])
        cov = 100.0 * k / n
        wlo, whi = wilson(k, n)
        tag = r["class"]
        ok &= check(f"class {tag} coverage_pct", round(cov, 2),
                    float(r["coverage_pct"]), tol=0.01)
        ok &= check(f"class {tag} wilson_lo", round(wlo, 2),
                    float(r["wilson_lo"]), tol=0.02)
        ok &= check(f"class {tag} wilson_hi", round(whi, 2),
                    float(r["wilson_hi"]), tol=0.02)
    simplex = next(r for r in cls if r["class"] == "simplex")
    ok &= check("class simplex coverage pin", 29.06,
                float(simplex["coverage_pct"]), tol=0.005)

    # --- MG review follow-ups (31-10): fig14b quadrant census + fig16 gates ---
    pooled_dens = next(r for r in dens
                       if r["stratum"] == "pooled_standardised_equal_weight")
    ok &= check("fig16 pooled std ratio committed",
                float(pooled_dens["attestation_ratio"]), 8.4051, tol=0.001)
    for r in dens:
        if r["row_kind"] not in ("stratum", "pooled"):
            continue
        ratio = float(r["attestation_ratio"])
        lo_c = r["attestation_ratio_lo"].strip()
        hi_c = r["attestation_ratio_hi"].strip()
        if lo_c and hi_c:
            ok &= check(f"fig16 {r['stratum']} ratio within CI",
                        1 if float(lo_c) <= ratio <= float(hi_c) else 0, 1)

    if not ok:
        print("DRIFT DETECTED — refusing to draw figures from stale metrics.")
        return 2

    residue_rows = sorted(
        ((r["display_title"], int(r["count"]))
         for r in families
         if r["class"] == "primary" and r["match_type"] == "residue"
         and r["display_title"].strip()),
        key=lambda t: -t[1])
    gainers = sorted(
        ((r["dcs_title"], int(r["dcs_tok_2021"]), int(r["dcs_tok_2026"]))
         for r in crosswalk),
        key=lambda t: -(t[2] - t[1]))

    OUT.mkdir(parents=True, exist_ok=True)
    figs = {
        "a68_fig1_mass_breakdown.svg": fig1(m),
        "a68_fig2_two_lenses.svg": fig2(m),
        "a68_fig3_residue_top20.svg": fig3(residue_rows),
        "a68_fig4_dcs_growth.svg": fig4(gainers),
        "a68_fig5_citation_flow.svg": fig5(m),
        "a68_fig6_fascicle_ci_strip.svg": fig6(fasc, m),
        "a68_fig7_denominator_ladder.svg": fig7(m),
        "a68_fig8_fascicle_timeline.svg": fig8(ledger),
        "a68_fig9_pdwg_two_layer.svg": fig9(dens),
        "a68_fig10_dcs276_layers.svg": fig10(m),
        "a68_fig11_layer_skew.svg": fig11(m),
        "a68_fig12_availability_pyramid.svg": fig12(avail_sig, avail_summary),
        "a68_fig13_coverage_slope.svg": fig13(crosswalk, m),
        "a68_fig14_corpus_attention.svg": fig14(crosswalk, m),
        "a68_fig15_class_forest.svg": fig15(cls, m),
    }
    # MG review follow-ups (31-10): zoomed fig14 + PWG-vs-PD forest.
    fig14b_svg, quad_n = fig14b(crosswalk, m)
    ok_q = sum(quad_n.values()) == len(crosswalk)
    print(f"  [{'OK ' if ok_q else 'FAIL'}] fig14b quadrant census: "
          f"{quad_n} sums to {sum(quad_n.values())} of {len(crosswalk)}")
    if not ok_q:
        print("DRIFT DETECTED — fig14b quadrants do not partition the 118.")
        return 2
    figs["a68_fig14b_corpus_attention_zoom.svg"] = fig14b_svg
    figs["a68_fig16_pwg_vs_pd_forest.svg"] = fig16(dens)
    for name, content in figs.items():
        (OUT / name).write_text(content, encoding="utf-8", newline="\n")
        print(f"  wrote papers/figures/{name}")

    # Style studies (review proposals, not paper figures yet).
    ss_out = OUT / "style_studies"
    ss_out.mkdir(parents=True, exist_ok=True)
    studies = {
        "a68_fig7_styleA_tufte.svg": ss7.fig7_tufte(m),
        "a68_fig7_styleB_economist.svg": ss7.fig7_economist(m),
        "a68_fig7_styleC_ft.svg": ss7.fig7_ft(m),
        "a68_fig7_styleD_engraving.svg": ss7.fig7_engraving(m),
        "a68_fig10_styleA_tufte.svg": ss10.fig10_tufte(m),
        "a68_fig10_styleB_economist.svg": ss10.fig10_economist(m),
        "a68_fig10_styleC_ft.svg": ss10.fig10_ft(m),
        "a68_fig10_styleD_engraving.svg": ss10.fig10_engraving(m),
    }
    for name, content in studies.items():
        (ss_out / name).write_text(content, encoding="utf-8", newline="\n")
        print(f"  wrote papers/figures/style_studies/{name}")
    print(f"All checks passed; {len(figs)} figures + {len(studies)} style "
          f"studies written.")
    return 0


