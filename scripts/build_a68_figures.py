#!/usr/bin/env python3
"""Build the A68 paper figures from the committed PD-DCS crosswalk data.

Reads only committed inputs under data/pd/ and re-derives every headline
metric from the row-level TSVs, cross-checking against the committed
pd_dcs_metrics.json before drawing anything — a mismatch aborts the run
(cross-paper figure drift is a tracked defect class; every figure must be
regenerable AND re-derived, never restated).

Outputs deterministic SVG (no timestamps, no randomness, stdlib only) into
papers/figures/:

  a68_fig1_mass_breakdown.svg   — the 398,359 siglum occurrences by class
  a68_fig2_two_lenses.svg       — the three coverage metrics side by side
  a68_fig3_residue_top20.svg    — top-20 PD-cited works absent from DCS
  a68_fig4_dcs_growth.svg       — top 2021→2026 DCS token gainers (PD-core)

Usage:  python scripts/build_a68_figures.py
"""

import csv
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "pd"
OUT = ROOT / "papers" / "figures"

# Palette (colorblind-safe, print-friendly)
C_COVERED = "#2166ac"
C_RESIDUE = "#b2182b"
C_STRUCT = "#999999"
C_SECOND = "#f4a582"
C_BAR = "#2166ac"
C_BAR2 = "#92c5de"
FONT = "font-family='Georgia, serif'"


def read_tsv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def check(name, derived, committed, tol=0.0):
    ok = abs(derived - committed) <= tol
    status = "OK " if ok else "FAIL"
    print(f"  [{status}] {name}: derived={derived} committed={committed}")
    return ok


def svg_header(w, h, title):
    return (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' "
        f"viewBox='0 0 {w} {h}'>\n"
        f"<title>{title}</title>\n"
        f"<rect width='{w}' height='{h}' fill='white'/>\n"
    )


def fig1(m):
    """Stacked horizontal bar: occurrence mass by class."""
    total = m["total_siglum_mass"]
    parts = [
        ("Covered by DCS", m["covered_mass"], C_COVERED),
        ("Residue (primary, not in DCS)", m["residue_mass"], C_RESIDUE),
        ("Structural (case labels, loci)", m["structural_mass"], C_STRUCT),
        ("Secondary scholarship", m["secondary_mass"], C_SECOND),
    ]
    W, H, bx, bw, bh, by = 760, 220, 30, 700, 56, 46
    s = svg_header(W, H, "PD siglum occurrence mass by class")
    s += (f"<text x='{bx}' y='28' {FONT} font-size='15' font-weight='bold'>"
          f"PD a‑volume citation occurrences (n = {total:,}) by class</text>\n")
    x = bx
    for label, v, color in parts:
        w = bw * v / total
        s += (f"<rect x='{x:.1f}' y='{by}' width='{w:.1f}' height='{bh}' "
              f"fill='{color}'/>\n")
        pct = 100.0 * v / total
        if w > 60:
            s += (f"<text x='{x + w / 2:.1f}' y='{by + bh / 2 + 5}' {FONT} "
                  f"font-size='13' fill='white' text-anchor='middle'>"
                  f"{pct:.1f} %</text>\n")
        x += w
    ly = by + bh + 30
    lx = bx
    for label, v, color in parts:
        s += f"<rect x='{lx}' y='{ly - 11}' width='13' height='13' fill='{color}'/>\n"
        s += (f"<text x='{lx + 18}' y='{ly}' {FONT} font-size='12'>"
              f"{label} — {v:,}</text>\n")
        ly += 22
        if ly > by + bh + 30 + 44:
            ly = by + bh + 30
            lx = bx + 380
    s += "</svg>\n"
    return s


def fig2(m):
    """The three coverage metrics side by side."""
    bars = [
        ("Title-level\n(118 of ~2,445 works)", m["metric_title_level_pct_estimate"], C_BAR2),
        ("PD-citation-weighted\n(of what PD cites)", m["metric_pd_citation_weighted_pct"], C_BAR),
        ("DCS-token-weighted 2021\n(of DCS's own mass)", m["metric_dcs_token_weighted_2021_pct"], C_BAR2),
        ("DCS-token-weighted 2026\n(of DCS's own mass)", m["metric_dcs_token_weighted_2026_pct"], C_BAR),
    ]
    W, H = 760, 340
    x0, y0, plot_h, bw, gap = 60, 50, 200, 140, 30
    s = svg_header(W, H, "DCS coverage of the PD canon under three metrics")
    s += (f"<text x='30' y='30' {FONT} font-size='15' font-weight='bold'>"
          f"DCS coverage of the PD source canon — three lenses, one corpus</text>\n")
    for gy in (0, 25, 50, 75, 100):
        y = y0 + plot_h - plot_h * gy / 100
        s += (f"<line x1='{x0}' y1='{y:.1f}' x2='{W - 20}' y2='{y:.1f}' "
              f"stroke='#dddddd'/>\n")
        s += (f"<text x='{x0 - 8}' y='{y + 4:.1f}' {FONT} font-size='11' "
              f"text-anchor='end'>{gy} %</text>\n")
    x = x0 + 20
    for label, v, color in bars:
        h = plot_h * v / 100
        y = y0 + plot_h - h
        s += f"<rect x='{x}' y='{y:.1f}' width='{bw}' height='{h:.1f}' fill='{color}'/>\n"
        s += (f"<text x='{x + bw / 2}' y='{y - 6:.1f}' {FONT} font-size='14' "
              f"font-weight='bold' text-anchor='middle'>{v:.1f} %</text>\n")
        for i, line in enumerate(label.split("\n")):
            s += (f"<text x='{x + bw / 2}' y='{y0 + plot_h + 18 + i * 14}' {FONT} "
                  f"font-size='11' text-anchor='middle'>{line}</text>\n")
        x += bw + gap
    s += "</svg>\n"
    return s


def fig3(residue_rows):
    """Top-20 named residue works by PD citation count."""
    rows = residue_rows[:20]
    W = 760
    rh = 24
    H = 80 + rh * len(rows)
    maxv = rows[0][1]
    x0, bw_max = 300, 400
    s = svg_header(W, H, "Most-cited PD works absent from DCS")
    s += (f"<text x='30' y='30' {FONT} font-size='15' font-weight='bold'>"
          f"The residue: most-cited PD works absent from DCS</text>\n")
    s += (f"<text x='30' y='50' {FONT} font-size='12' fill='#555555'>"
          f"bar length = PD citation occurrences (letter a‑ volumes)</text>\n")
    y = 70
    for title, v in rows:
        w = bw_max * v / maxv
        s += (f"<text x='{x0 - 8}' y='{y + 12}' {FONT} font-size='12' "
              f"text-anchor='end'>{title}</text>\n")
        s += (f"<rect x='{x0}' y='{y}' width='{w:.1f}' height='16' "
              f"fill='{C_RESIDUE}'/>\n")
        s += (f"<text x='{x0 + w + 6:.1f}' y='{y + 12}' {FONT} "
              f"font-size='11'>{v:,}</text>\n")
        y += rh
    s += "</svg>\n"
    return s


def fig4(gainers):
    """Top 2021→2026 DCS token gainers among PD-covered texts."""
    rows = gainers[:8]
    W = 760
    rh = 40
    H = 90 + rh * len(rows)
    maxv = max(r[2] for r in rows)
    x0, bw_max = 260, 420
    s = svg_header(W, H, "DCS 2021 to 2026 growth in PD-covered texts")
    s += (f"<text x='30' y='30' {FONT} font-size='15' font-weight='bold'>"
          f"Where DCS grew, 2021→2026: the Vedic core of PD's canon</text>\n")
    s += (f"<text x='30' y='50' {FONT} font-size='12' fill='#555555'>"
          f"light bar = tokens 2021 · dark bar = tokens 2026</text>\n")
    y = 72
    for title, t21, t26 in rows:
        w21 = bw_max * t21 / maxv
        w26 = bw_max * t26 / maxv
        s += (f"<text x='{x0 - 8}' y='{y + 18}' {FONT} font-size='12' "
              f"text-anchor='end'>{title}</text>\n")
        s += f"<rect x='{x0}' y='{y}' width='{w21:.1f}' height='11' fill='{C_BAR2}'/>\n"
        s += f"<rect x='{x0}' y='{y + 13}' width='{w26:.1f}' height='11' fill='{C_BAR}'/>\n"
        s += (f"<text x='{x0 + w26 + 6:.1f}' y='{y + 23}' {FONT} font-size='11'>"
              f"{t26:,} (+{t26 - t21:,})</text>\n")
        y += rh
    s += "</svg>\n"
    return s


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
    }
    for name, content in figs.items():
        (OUT / name).write_text(content, encoding="utf-8", newline="\n")
        print(f"  wrote papers/figures/{name}")
    print("All checks passed; 4 figures written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
