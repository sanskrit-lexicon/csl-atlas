"""Style studies (MG review 31-10): fig10 DCS-276 layer bar in four
non-Office render styles — review proposals, not paper figures.

Styles: A tufte, B economist, C ft, D engraving (see figs_style_fig7).
Same committed C4_LAYERS numbers as the canonical fig10.
"""
from .helpers import C4_LAYERS, FONT, esc

SANS = "font-family='Helvetica, Arial, sans-serif'"
SERIF = FONT


# ---------------------------------------------------------------- fig10 A
def fig10_tufte(m):
    layers = C4_LAYERS
    tot26 = sum(r[2] for r in layers)
    cov26 = sum(r[5] for r in layers)
    ve = sum(r[2] for r in layers if r[0] in ("Vedic", "epic"))
    ve_cov = sum(r[5] for r in layers if r[0] in ("Vedic", "epic"))
    W, H = 940, 300
    bx, bw = 150, 560
    rows = (("all DCS-276", tot26, 86), ("PD-covered 118", cov26, 186))
    strip_h = 30
    s = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' "
         f"viewBox='0 0 {W} {H}'>\n<title>DCS-276 token mass by Renou layer "
         f"— Tufte style</title>\n<rect width='{W}' height='{H}' "
         f"fill='white'/>\n")
    s += (f"<text x='30' y='36' {SERIF} font-size='16'>Vedic+epic carry "
          f"{100 * ve / tot26:.1f} % of DCS tokens — {100 * ve_cov / cov26:.1f} %"
          f" of the PD-covered set</text>\n")
    s += (f"<text x='30' y='56' {SERIF} font-size='12' font-style='italic' "
          f"fill='#444444'>100 %-strips; connectors trace each layer's drift "
          f"all → covered</text>\n")
    fills = ["#333333", "#777777", "#222222", "#888888", "#555555", "#aaaaaa"]
    segs = []
    for ri, (label, tot, y) in enumerate(rows):
        x = bx
        s += (f"<text x='30' y='{y + strip_h / 2 + 4:.1f}' {SERIF} "
              f"font-size='12'>{label}</text>\n")
        for li, (lname, _, tok26, _, _, ctok, _) in enumerate(layers):
            v = tok26 if ri == 0 else ctok
            w = bw * v / tot
            s += (f"<rect x='{x:.1f}' y='{y}' width='{w:.1f}' "
                  f"height='{strip_h}' fill='{fills[li]}' "
                  f"stroke='white' stroke-width='1'/>\n")
            pct = 100 * v / tot
            if w > 46:
                s += (f"<text x='{x + w / 2:.1f}' y='{y + strip_h / 2 + 4:.1f}' "
                      f"{SERIF} font-size='10.5' fill='white' "
                      f"text-anchor='middle'>{pct:.1f}</text>\n")
            segs.append((ri, li, x, x + w))
            x += w
    # Connectors between matching segments of the two strips.
    for ri, li, xa0, xa1 in segs:
        if ri == 0:
            xb0, xb1 = next((b0, b1) for r2, l2, b0, b1 in segs
                            if r2 == 1 and l2 == li)
            y1, y2 = 86 + strip_h, 186
            s += (f"<line x1='{(xa0 + xa1) / 2:.1f}' y1='{y1 + 2}' "
                  f"x2='{(xb0 + xb1) / 2:.1f}' y2='{y2 - 2}' stroke='#bbbbbb' "
                  f"stroke-width='0.8'/>\n")
    # Key column at right: all% → cov% per layer.
    kx, ky = 750, 86
    for li, (lname, _, tok26, _, _, ctok, _) in enumerate(layers):
        yy = ky + li * 26
        s += (f"<rect x='{kx}' y='{yy - 8}' width='9' height='9' "
              f"fill='{fills[li]}'/>\n")
        s += (f"<text x='{kx + 14}' y='{yy}' {SERIF} font-size='10.5'>"
              f"{esc(lname)}</text>\n")
        s += (f"<text x='{kx + 14}' y='{yy + 11}' {SERIF} font-size='9.5' "
              f"fill='#666666'>{100 * tok26 / tot26:.1f} → "
              f"{100 * ctok / cov26:.1f} %</text>\n")
    s += (f"<text x='30' y='{H - 18}' {SERIF} font-size='11' fill='#666666'>"
          f"grey tones, no hue · layer tags: committed C4 sweep (H6698) · "
          f"sweep's sūtra call lifts Vedic+epic to 50.5 %</text>\n")
    s += "</svg>\n"
    return s


# ---------------------------------------------------------------- fig10 B
def fig10_economist(m):
    layers = C4_LAYERS
    tot26 = sum(r[2] for r in layers)
    cov26 = sum(r[5] for r in layers)
    ve = sum(r[2] for r in layers if r[0] in ("Vedic", "epic"))
    ve_cov = sum(r[5] for r in layers if r[0] in ("Vedic", "epic"))
    pal = {"Vedic": "#DB444B", "epic": "#F0AB00", "śāstra": "#006BA2",
           "kāvya": "#3EBCD2", "purāṇic": "#379A8B", "other": "#B4BA39"}
    W, H = 860, 360
    bx, bw = 210, 560
    rows = (("All DCS-276", tot26, 118), ("PD-covered 118", cov26, 208))
    strip_h = 44
    s = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' "
         f"viewBox='0 0 {W} {H}'>\n<title>DCS-276 token mass by Renou layer "
         f"— Economist style</title>\n<rect width='{W}' height='{H}' "
         f"fill='white'/>\n")
    s += f"<rect x='30' y='24' width='14' height='42' fill='#E3120B'/>\n"
    s += (f"<text x='56' y='44' {SANS} font-size='17' font-weight='bold'>"
          f"The covered canon leans older than the corpus</text>\n")
    s += (f"<text x='56' y='62' {SANS} font-size='12' fill='#555555'>"
          f"DCS token mass by Renou layer · Vedic+epic "
          f"{100 * ve / tot26:.1f} % of all, {100 * ve_cov / cov26:.1f} % of "
          f"the covered set</text>\n")
    for ri, (label, tot, y) in enumerate(rows):
        x = bx
        s += (f"<text x='30' y='{y + strip_h / 2 + 4:.1f}' {SANS} "
              f"font-size='12.5' font-weight='bold' fill='#333333'>"
              f"{label}</text>\n")
        for lname, _, tok26, _, _, ctok, _ in layers:
            v = tok26 if ri == 0 else ctok
            w = bw * v / tot
            s += (f"<rect x='{x:.1f}' y='{y}' width='{w:.1f}' "
                  f"height='{strip_h}' fill='{pal[lname]}'/>\n")
            if w > 44:
                s += (f"<text x='{x + w / 2:.1f}' y='{y + strip_h / 2 + 4:.1f}'"
                      f" {SANS} font-size='11' fill='white' "
                      f"text-anchor='middle'>{100 * v / tot:.0f} %</text>\n")
            x += w
    lx, ly = 210, 288
    for lname, _, tok26, _, _, _, _ in layers:
        s += (f"<rect x='{lx}' y='{ly - 10}' width='12' height='12' "
              f"fill='{pal[lname]}'/>\n")
        s += (f"<text x='{lx + 17}' y='{ly}' {SANS} font-size='11' "
              f"fill='#333333'>{esc(lname)}</text>\n")
        lx += 20 + int(6.3 * len(lname)) + 22
    s += (f"<line x1='30' y1='{H - 46}' x2='{W - 30}' y2='{H - 46}' "
          f"stroke='#E3120B' stroke-width='1'/>\n")
    s += (f"<text x='30' y='{H - 28}' {SANS} font-size='10.5' "
          f"fill='#888888'>Source: C4 Renou-layer sweep of DCS-276, committed"
          f" 14-10-2026 · style study, Economist chart idiom</text>\n")
    s += "</svg>\n"
    return s


# ---------------------------------------------------------------- fig10 C
def fig10_ft(m):
    layers = C4_LAYERS
    tot26 = sum(r[2] for r in layers)
    cov26 = sum(r[5] for r in layers)
    ve = sum(r[2] for r in layers if r[0] in ("Vedic", "epic"))
    ve_cov = sum(r[5] for r in layers if r[0] in ("Vedic", "epic"))
    bg, ink, grey, claret = "#FFF1E5", "#33302E", "#BDB2A5", "#990F3D"
    pal = {"Vedic": "#990F3D", "epic": "#E8927C", "śāstra": "#0D7680",
           "kāvya": "#7CBF7F", "purāṇic": "#5F87B6", "other": "#D5BE9A"}
    W, H = 860, 380
    bx, bw = 220, 560
    rows = (("All DCS-276", tot26, 132), ("PD-covered 118", cov26, 224))
    strip_h = 44
    s = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' "
         f"viewBox='0 0 {W} {H}'>\n<title>DCS-276 token mass by Renou layer "
         f"— FT style</title>\n<rect width='{W}' height='{H}' fill='{bg}'/>"
         f"\n")
    s += (f"<text x='30' y='44' {SERIF} font-size='11' fill='{claret}' "
          f"letter-spacing='2'>DCS CORPUS COMPOSITION</text>\n")
    s += (f"<text x='30' y='74' {SERIF} font-size='19' font-weight='bold' "
          f"fill='{ink}'>What PD covers is not what DCS holds</text>\n")
    s += (f"<text x='30' y='96' {SERIF} font-size='13' fill='{ink}'>"
          f"Vedic+epic: {100 * ve / tot26:.1f} % of all tokens but "
          f"{100 * ve_cov / cov26:.1f} % of the covered set</text>\n")
    for ri, (label, tot, y) in enumerate(rows):
        x = bx
        s += (f"<text x='30' y='{y + strip_h / 2 + 4:.1f}' {SERIF} "
              f"font-size='13' fill='{ink}'>{label}</text>\n")
        for lname, _, tok26, _, _, ctok, _ in layers:
            v = tok26 if ri == 0 else ctok
            w = bw * v / tot
            s += (f"<rect x='{x:.1f}' y='{y}' width='{w:.1f}' "
                  f"height='{strip_h}' fill='{pal[lname]}' rx='2'/>\n")
            if w > 44:
                s += (f"<text x='{x + w / 2:.1f}' y='{y + strip_h / 2 + 4:.1f}'"
                      f" {SERIF} font-size='11.5' fill='white' "
                      f"text-anchor='middle'>{100 * v / tot:.0f} %</text>\n")
            x += w
    lx, ly = 220, 300
    for lname, _, tok26, _, _, _, _ in layers:
        s += (f"<rect x='{lx}' y='{ly - 10}' width='12' height='12' "
              f"fill='{pal[lname]}' rx='2'/>\n")
        s += (f"<text x='{lx + 17}' y='{ly}' {SERIF} font-size='12' "
              f"fill='{ink}'>{esc(lname)}</text>\n")
        lx += 20 + int(6.6 * len(lname)) + 24
    s += (f"<text x='30' y='{H - 48}' {SERIF} font-size='12' fill='{ink}'>"
          f"The 118 covered works sit in the older layers — coverage "
          f"inherits the canon's centre of gravity</text>\n")
    s += (f"<text x='30' y='{H - 26}' {SANS} font-size='10' fill='{grey}'>"
          f"Source: C4 Renou-layer sweep of DCS-276 · style study, FT chart "
          f"idiom</text>\n")
    s += "</svg>\n"
    return s


# ---------------------------------------------------------------- fig10 D
def fig10_engraving(m):
    layers = C4_LAYERS
    tot26 = sum(r[2] for r in layers)
    cov26 = sum(r[5] for r in layers)
    ve = sum(r[2] for r in layers if r[0] in ("Vedic", "epic"))
    ve_cov = sum(r[5] for r in layers if r[0] in ("Vedic", "epic"))
    pats = ["hV", "hE", "hS", "hK", "hP", "hO"]
    defs = {
        "hV": (45, 6, 1.2), "hE": (-45, 6, 1.2), "hS": (0, 5, 1.1),
        "hK": (90, 5, 1.1), "hP": ((45, -45), 7, 0.9), "hO": (90, 3.2, 0.8),
    }
    W, H = 810, 470
    x0, gap = 150, 120
    colw = 150
    y0, plot_h = 100, 260
    s = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' "
         f"viewBox='0 0 {W} {H}'>\n<title>DCS-276 token mass by Renou layer "
         f"— engraved plate</title>\n<rect width='{W}' height='{H}' "
         f"fill='white'/>\n<defs>")
    for pid in pats[:-1]:
        ang, sp, sw = defs[pid]
        s += (f"<pattern id='{pid}' width='{sp}' height='{sp}' "
              f"patternTransform='rotate({ang})' "
              f"patternUnits='userSpaceOnUse'><line x1='0' y1='0' x2='0' "
              f"y2='{sp}' stroke='#222222' stroke-width='{sw}'/></pattern>")
    s += (f"<pattern id='hP' width='7' height='7' "
          f"patternUnits='userSpaceOnUse'><path d='M0 0 L7 7 M7 0 L0 7' "
          f"stroke='#222222' stroke-width='0.7'/></pattern>")
    s += (f"<pattern id='hO' width='4' height='4' "
          f"patternUnits='userSpaceOnUse'><circle cx='2' cy='2' r='0.8' "
          f"fill='#222222'/></pattern></defs>\n")
    s += (f"<rect x='14' y='14' width='{W - 28}' height='{H - 28}' "
          f"fill='none' stroke='#222222' stroke-width='1.6'/>\n")
    s += (f"<rect x='20' y='20' width='{W - 40}' height='{H - 40}' "
          f"fill='none' stroke='#222222' stroke-width='0.5'/>\n")
    s += (f"<text x='{W / 2}' y='48' {SERIF} font-size='13' "
          f"text-anchor='middle' letter-spacing='3'>TOKEN MASS BY RENOU "
          f"LAYER</text>\n")
    s += (f"<line x1='270' y1='58' x2='{W - 270}' y2='58' stroke='#222222' "
          f"stroke-width='0.6'/>\n")
    s += (f"<text x='{W / 2}' y='76' {SERIF} font-size='11' font-style='italic'"
          f" text-anchor='middle'>Vedic+epic {100 * ve / tot26:.1f} % of all "
          f"tokens; {100 * ve_cov / cov26:.1f} % within the covered set</text>\n")
    # Two stratigraphic columns, absolute scale.
    for ci, (label, tot) in enumerate((("all DCS-276", tot26),
                                       ("covered-118", cov26))):
        x = x0 + ci * (colw + gap)
        scale = plot_h / tot26
        y = y0 + plot_h
        s += (f"<text x='{x + colw / 2}' y='{y + 34}' {SERIF} font-size='11.5'"
              f" font-weight='bold' text-anchor='middle'>{label}</text>\n")
        s += (f"<text x='{x + colw / 2}' y='{y + 48}' {SERIF} font-size='10' "
              f"text-anchor='middle' fill='#444444'>{tot:,} tok</text>\n")
        for li, (lname, _, tok26, _, _, ctok, _) in enumerate(layers):
            v = tok26 if ci == 0 else ctok
            h = v * scale
            y -= h
            s += (f"<rect x='{x}' y='{y:.1f}' width='{colw}' height='{h:.1f}' "
                  f"fill='url(#{pats[li]})' stroke='#222222' "
                  f"stroke-width='0.8'/>\n")
            if h > 26:
                s += (f"<text x='{x + colw / 2}' y='{y + h / 2 + 4:.1f}' "
                      f"{SERIF} font-size='10.5' text-anchor='middle'>"
                      f"{100 * v / tot:.1f} %</text>\n")
    # Hatch key (right of both columns: col2 ends at x0+2*colw+gap=570).
    kx, ky = 620, 118
    for li, (lname, _, _, _, _, _, _) in enumerate(layers):
        yy = ky + li * 27
        s += (f"<rect x='{kx}' y='{yy - 10}' width='16' height='16' "
              f"fill='url(#{pats[li]})' stroke='#222222' "
              f"stroke-width='0.7'/>\n")
        s += (f"<text x='{kx + 24}' y='{yy + 2}' {SERIF} font-size='11.5'>"
              f"{esc(lname)}</text>\n")
    s += (f"<text x='{W / 2}' y='{H - 34}' {SERIF} font-size='11' "
          f"font-style='italic' text-anchor='middle'>Fig. — stratigraphic "
          f"columns to one scale; texture, not hue, separates the layers."
          f"</text>\n")
    s += "</svg>\n"
    return s
