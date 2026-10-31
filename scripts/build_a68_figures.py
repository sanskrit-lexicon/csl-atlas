#!/usr/bin/env python3
"""Build the A68 paper figures from the committed PD-DCS crosswalk data.

Reads only committed inputs under data/pd/ and re-derives every headline
metric from the row-level TSVs, cross-checking against the committed
pd_dcs_metrics.json before drawing anything — a mismatch aborts the run
(cross-paper figure drift is a tracked defect class; every figure must be
regenerable AND re-derived, never restated).

Outputs deterministic SVG (no timestamps, no randomness, stdlib only) into
papers/figures/:

  a68_fig1_mass_breakdown.svg     — the 398,359 siglum occurrences by class
  a68_fig2_two_lenses.svg         — the three coverage metrics side by side
  a68_fig3_residue_top20.svg      — top-20 PD-cited works absent from DCS
  a68_fig4_dcs_growth.svg         — top 2021→2026 DCS token gainers (PD-core)
  a68_fig5_citation_flow.svg      — cat #1: two-stage citation-mass flow
  a68_fig6_fascicle_ci_strip.svg  — cat #2: fascicle coverage dots + Wilson CIs
  a68_fig7_denominator_ladder.svg — cat #12: 398,359→353,512→123,453→88,929
  a68_fig8_fascicle_timeline.svg  — cat #13: fifty-year fascicle gantt 1976-2019
  a68_fig9_pdwg_two_layer.svg     — cat #20: PD vs PWG attestations per stratum
  a68_fig10_dcs276_layers.svg     — cat #24: DCS-276 token mass by Renou layer
  a68_fig11_layer_skew.svg        — cat #25: citation-vs-token skew per layer
  a68_fig12_availability_pyramid.svg — cat #29: attestation mass by availability
  a68_fig13_coverage_slope.svg    — cat #8: coverage slope 2021→2026 (118 titles)
  a68_fig14_corpus_attention.svg  — cat #9: corpus size vs dictionary attention
  a68_fig15_class_forest.svg      — cat #19: class coverage forest with CIs
  a68_fig14b_corpus_attention_zoom.svg — cat #9 zoom: 4 median quadrants,
                                   every title labelled (MG review 31-10)
  a68_fig16_pwg_vs_pd_forest.svg  — PWG vs PD per stratum, companion forest
                                   to fig15 (MG review 31-10)

plus papers/figures/style_studies/ — fig7 and fig10 each in four review
style proposals (Tufte / Economist / FT / engraved plate), same committed
numbers, not paper figures until MG picks. python -m a68_figures.gallery
wraps everything into a single review HTML.

Figures 5-15 (H7545, MG-voted 11-figure set, verdict PR Uprava#6407) follow
the same contract. The C4 layer figures 10-11 encode the committed sweep
table (Uprava papers/A68/sweeps/2026-10-14-C4-renou-layers-dcs276.md); the
per-text layer tag map is NOT committed anywhere, so layers are literals
cross-checked against metrics totals, never re-tagged. Per-layer residue
composition stays blocked (C2/C8) and appears in no figure.

Usage:  python scripts/build_a68_figures.py
"""

"""Shim entry point — the implementation lives in scripts/a68_figures/
(split for the per-file token-size gate; the canonical invocation
python scripts/build_a68_figures.py is unchanged)."""

import sys

from a68_figures.runner import main

if __name__ == "__main__":
    sys.exit(main())
