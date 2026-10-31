"""Figs 1-4 — the original four A68 figures (unchanged output)."""
from .helpers import (C_BAR, C_BAR2, C_COVERED, C_RESIDUE, C_SECOND,
                      C_STRUCT, FONT, esc, svg_header)


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
          f"PD a-volume citation occurrences (n = {total:,}) by class</text>\n")
    x = bx
    for label, v, color in parts:
        w = bw * v / total
        s += (f"<rect x='{x:.1f}' y='{by}' width='{w:.1f}' height='{bh}' "
              f"fill='{color}'/>\n")
        pct = 100.0 * v / total
        if w > 60:
            s += (f"<text x='{x + w / 2:.1f}' y='{by + bh / 2 + 5}' {FONT} "
                  f"font-size='13' fill='white' text-anchor='middle'>"
                  f"{pct:.1f} %</text>\n")
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
        ("Title-level, declared canon\n(118 of ≈1,476 AOB entries)", m["metric_title_level_declared_pct"], C_BAR2),
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
              f"text-anchor='end'>{gy} %</text>\n")
    x = x0 + 20
    for label, v, color in bars:
        h = plot_h * v / 100
        y = y0 + plot_h - h
        s += f"<rect x='{x}' y='{y:.1f}' width='{bw}' height='{h:.1f}' fill='{color}'/>\n"
        s += (f"<text x='{x + bw / 2}' y='{y - 6:.1f}' {FONT} font-size='14' "
              f"font-weight='bold' text-anchor='middle'>{v:.1f} %</text>\n")
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
          f"bar length = PD citation occurrences (letter a- volumes)</text>\n")
    y = 70
    for title, v in rows:
        w = bw_max * v / maxv
        s += (f"<text x='{x0 - 8}' y='{y + 12}' {FONT} font-size='12' "
              f"text-anchor='end'>{esc(title)}</text>\n")
        s += (f"<rect x='{x0}' y='{y}' width='{w:.1f}' height='16' "
              f"fill='{C_RESIDUE}'/>\n")
        s += (f"<text x='{x0 + w + 6:.1f}' y='{y + 12}' {FONT} "
              f"font-size='11'>{v:,}</text>\n")
        y += rh
    s += "</svg>\n"
    return s


def fig4(gainers):
    """Top 2021→2026 DCS token gainers among PD-covered texts.

    Canvas is 830 wide (not 760): the first bar label '144,139 (+140,421)'
    ends ~794px at x0+420+6 — it clipped at 760.
    """
    rows = gainers[:8]
    W = 830
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
              f"text-anchor='end'>{esc(title)}</text>\n")
        s += f"<rect x='{x0}' y='{y}' width='{w21:.1f}' height='11' fill='{C_BAR2}'/>\n"
        s += f"<rect x='{x0}' y='{y + 13}' width='{w26:.1f}' height='11' fill='{C_BAR}'/>\n"
        s += (f"<text x='{x0 + w26 + 6:.1f}' y='{y + 23}' {FONT} font-size='11'>"
              f"{t26:,} (+{t26 - t21:,})</text>\n")
        y += rh
    s += "</svg>\n"
    return s


