"""Style studies (MG review 31-10): fig7 denominator ladder and fig10
DCS-276 layer bar, each in four non-Office render styles.

MG pass-3 pick (31-10): style B (Economist) chosen as MAIN for both fig7
and fig10 — folded into the canonical figs_catalogue_a.fig7 /
figs_catalogue_b.fig10 (headline of fig7 rewritten there to state the
claim's fraction outright). fig7_economist / fig10_economist below now
alias the canonical renders, so the style_studies/ set stays complete as
the review record; A/C/D remain unchosen proposals.

Styles:
  A tufte      — minimal ink, no fills, direct numerals, no frame
  B economist  — red accent rule, sans-serif, horizontal bars, source line
                 (CANONICAL since MG pass 3, 31-10)
  C ft         — salmon field, kicker, rounded bars, inline numerals
  D engraving  — monochrome plate, hatched fills, double-rule frame
"""
from .helpers import C4_LAYERS, FONT, SANS, esc, ladder

SERIF = FONT


# ---------------------------------------------------------------- fig7 A
def fig7_tufte(m):
    steps = ladder(m)
    total = steps[0][1]
    W, H = 820, 330
    x0, x1 = 250, 640
    y0, dy = 100, 52

    def xx(v):
        return x0 + (x1 - x0) * v / total

    s = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' "
         f"viewBox='0 0 {W} {H}'>\n<title>Denominator ladder — Tufte "
         f"style</title>\n<rect width='{W}' height='{H}' fill='white'/>\n")
    s += (f"<text x='30' y='40' {SERIF} font-size='16'>One claim, four "
          f"denominators — what 25.2 % is a fraction of</text>\n")
    s += (f"<text x='30' y='60' {SERIF} font-size='12' font-style='italic' "
          f"fill='#444444'>drop of the series: each rung keeps "
          f"{100 * steps[3][1] / total:.1f} % of the first</text>\n")
    # Baseline ticks only — the axis is implied by the dots.
    s += (f"<line x1='{x0}' y1='{y0 - 22}' x2='{x0}' y2='{y0 - 14}' "
          f"stroke='#444444'/>\n")
    s += (f"<line x1='{xx(total)}' y1='{y0 - 22}' x2='{xx(total)}' "
          f"y2='{y0 - 14}' stroke='#444444'/>\n")
    s += (f"<text x='{x0}' y='{y0 - 28}' {SERIF} font-size='11' "
          f"text-anchor='middle'>0</text>\n")
    s += (f"<text x='{xx(total)}' y='{y0 - 28}' {SERIF} font-size='11' "
          f"text-anchor='middle'>398k</text>\n")
    prev = None
    for i, (label, v, tag) in enumerate(steps):
        y = y0 + i * dy
        if prev is not None:
            s += (f"<line x1='{xx(prev):.1f}' y1='{y - dy + 4:.1f}' "
                  f"x2='{xx(v):.1f}' y2='{y + 4:.1f}' stroke='#999999' "
                  f"stroke-width='1' stroke-dasharray='2 3'/>\n")
        prev = v
        s += f"<circle cx='{xx(v):.1f}' cy='{y + 4:.1f}' r='4' fill='#333333'/>\n"
        s += (f"<text x='30' y='{y + 8:.1f}' {SERIF} font-size='13'>"
              f"{esc(label)}</text>\n")
        tail = " (pin)" if tag else ""
        s += (f"<text x='{xx(v) + 10:.1f}' y='{y:.1f}' {SERIF} font-size='15' "
              f"font-weight='bold'>{v:,}{tail}</text>\n")
        s += (f"<text x='{xx(v) + 10:.1f}' y='{y + 15:.1f}' {SERIF} "
              f"font-size='11' fill='#666666'>{100 * v / total:.1f} % of "
              f"all</text>\n")
    s += (f"<text x='30' y='{H - 18}' {SERIF} font-size='11' fill='#666666'>"
          f"25.16 % = 88,929 / 353,512 · third rung = claim-ledger pin "
          f"P-adjudicated, 164 titles</text>\n")
    s += "</svg>\n"
    return s


# ---------------------------------------------------------------- fig7 B
def fig7_economist(m):
    """CANONICAL since MG pass 3 (31-10) — aliases figs_catalogue_a.fig7."""
    from .figs_catalogue_a import fig7 as _canonical_fig7
    return _canonical_fig7(m)


# ---------------------------------------------------------------- fig7 C
def fig7_ft(m):
    steps = ladder(m)
    total = steps[0][1]
    W, H = 780, 420
    bg, ink, teal, claret, grey = "#FFF1E5", "#33302E", "#0D7680", "#990F3D", \
        "#BDB2A5"
    x0 = 220
    bw_max = 480
    y0, dy = 130, 58
    s = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' "
         f"viewBox='0 0 {W} {H}'>\n<title>Denominator ladder — FT "
         f"style</title>\n<rect width='{W}' height='{H}' fill='{bg}'/>\n")
    s += (f"<text x='30' y='44' {SERIF} font-size='11' fill='{claret}' "
          f"letter-spacing='2'>POONA DICTIONARY × DCS</text>\n")
    s += (f"<text x='30' y='74' {SERIF} font-size='19' font-weight='bold' "
          f"fill='{ink}'>One claim, four denominators</text>\n")
    s += (f"<text x='30' y='96' {SERIF} font-size='13' fill='{ink}'>"
          f"What the 25.2 % coverage headline is a fraction of</text>\n")
    for gv in (0, 100000, 200000, 300000, 400000):
        x = x0 + bw_max * gv / total
        s += (f"<line x1='{x:.1f}' y1='116' x2='{x:.1f}' y2='{y0 + dy * 4 - 20}'"
              f" stroke='{bg}' stroke-width='2'/>\n")
        lbl = "0" if gv == 0 else f"{gv // 1000}k"
        s += (f"<text x='{x:.1f}' y='112' {SANS} font-size='10.5' "
              f"fill='{grey}' text-anchor='middle'>{lbl}</text>\n")
    for i, (label, v, tag) in enumerate(steps):
        y = y0 + i * dy
        w = bw_max * v / total
        color = claret if i == 3 else teal
        s += (f"<text x='30' y='{y + 15:.1f}' {SERIF} font-size='13' "
              f"fill='{ink}'>{esc(label)}</text>\n")
        s += (f"<rect x='{x0}' y='{y:.1f}' width='{w:.1f}' height='24' "
              f"fill='{color}' rx='2'/>\n")
        s += (f"<text x='{x0 + w - 8:.1f}' y='{y + 17:.1f}' {SERIF} "
              f"font-size='12' font-weight='bold' fill='white' "
              f"text-anchor='end'>{v:,}</text>\n")
        s += (f"<text x='{x0 + w + 10:.1f}' y='{y + 17:.1f}' {SERIF} "
              f"font-size='11.5' fill='{grey}'>{100 * v / total:.1f} %"
              f"{' · pin' if tag else ''}</text>\n")
    s += (f"<text x='30' y='{H - 44}' {SERIF} font-size='12' fill='{ink}'>"
          f"Every rung is a legitimate denominator — the headline uses the "
          f"second</text>\n")
    s += (f"<text x='30' y='{H - 24}' {SANS} font-size='10' fill='{grey}'>"
          f"Source: committed PD↔DCS metrics · style study, FT chart "
          f"idiom</text>\n")
    s += "</svg>\n"
    return s


# ---------------------------------------------------------------- fig7 D
def fig7_engraving(m):
    steps = ladder(m)
    total = steps[0][1]
    W, H = 780, 450
    x0, y0 = 80, 88
    bw, gap = 130, 34
    plot_h = 220
    # Two-line category labels keep neighbouring columns from touching.
    two_line = {
        "All siglum occurrences": ("All siglum", "occurrences"),
        "Primary work occurrences": ("Primary work", "occurrences"),
        "Hand-adjudicated primary": ("Hand-adjudicated", "primary"),
        "Covered by DCS (118 works)": ("Covered by DCS", "(118 works)"),
    }
    s = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' "
         f"viewBox='0 0 {W} {H}'>\n<title>Denominator ladder — engraved "
         f"plate</title>\n<rect width='{W}' height='{H}' fill='white'/>\n"
         f"<defs><pattern id='hatchA' width='7' height='7' "
         f"patternTransform='rotate(45)' patternUnits='userSpaceOnUse'>"
         f"<line x1='0' y1='0' x2='0' y2='7' stroke='#222222' "
         f"stroke-width='1.1'/></pattern></defs>\n")
    # Double-rule plate frame.
    s += (f"<rect x='14' y='14' width='{W - 28}' height='{H - 28}' "
          f"fill='none' stroke='#222222' stroke-width='1.6'/>\n")
    s += (f"<rect x='20' y='20' width='{W - 40}' height='{H - 40}' "
          f"fill='none' stroke='#222222' stroke-width='0.5'/>\n")
    s += (f"<text x='{W / 2}' y='48' {SERIF} font-size='13' "
          f"text-anchor='middle' letter-spacing='3'>THE DENOMINATOR LADDER"
          f"</text>\n")
    s += (f"<line x1='250' y1='58' x2='{W - 250}' y2='58' "
          f"stroke='#222222' stroke-width='0.6'/>\n")
    # Y axis with ticks every 100k.
    for gv in (0, 100000, 200000, 300000, 400000):
        y = y0 + plot_h - plot_h * gv / total
        s += (f"<line x1='{x0 - 24}' y1='{y:.1f}' x2='{x0 - 18}' y2='{y:.1f}' "
              f"stroke='#222222'/>\n")
        s += (f"<text x='{x0 - 30}' y='{y + 4:.1f}' {SERIF} font-size='11' "
              f"text-anchor='end'>{'0' if gv == 0 else f'{gv // 1000}k'}</text>\n")
    prev_top = None
    for i, (label, v, tag) in enumerate(steps):
        x = x0 + i * (bw + gap)
        h = plot_h * v / total
        y = y0 + plot_h - h
        s += (f"<rect x='{x}' y='{y:.1f}' width='{bw}' height='{h:.1f}' "
              f"fill='url(#hatchA)' stroke='#222222' stroke-width='0.9'/>\n")
        s += (f"<text x='{x + bw / 2}' y='{y - 12:.1f}' {SERIF} font-size='13' "
              f"text-anchor='middle'>{v:,}</text>\n")
        if prev_top is not None:
            delta = v - steps[i - 1][1]
            mid = (y + prev_top) / 2
            s += (f"<text x='{x - gap / 2}' y='{mid - 6:.1f}' "
                  f"{SERIF} font-size='10' text-anchor='middle' "
                  f"fill='#444444'>{delta:+,}</text>\n")
        prev_top = y
        l1, l2 = two_line[label]
        s += (f"<text x='{x + bw / 2}' y='{y0 + plot_h + 24}' {SERIF} "
              f"font-size='11.5' font-weight='bold' text-anchor='middle'>"
              f"{esc(l1)}</text>\n")
        s += (f"<text x='{x + bw / 2}' y='{y0 + plot_h + 38}' {SERIF} "
              f"font-size='11.5' font-weight='bold' text-anchor='middle'>"
              f"{esc(l2)}</text>\n")
        s += (f"<text x='{x + bw / 2}' y='{y0 + plot_h + 54}' {SERIF} "
              f"font-size='10' text-anchor='middle' fill='#444444'>"
              f"{100 * v / total:.1f} % of all{' · pin' if tag else ''}</text>\n")
    s += (f"<text x='{W / 2}' y='{H - 32}' {SERIF} font-size='11' "
          f"font-style='italic' text-anchor='middle'>Fig. — each rung is a "
          f"denominator of the coverage claim; the headline rests on the "
          f"second.</text>\n")
    s += "</svg>\n"
    return s


