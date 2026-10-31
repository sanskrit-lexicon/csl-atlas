"""Figs 5-9 — catalogue figures (H7545): flow, fascicle CI strip,
denominator ladder, fifty-year timeline, PD-vs-PWG paired bars."""
from .helpers import (C_BAR, C_BAR2, C_COVERED, C_RESIDUE, C_SECOND,
                      C_STRUCT, FONT, PIN_ADJUDICATED, esc, svg_header)


def fig5(m):
    """Cat #1 — two-stage citation-mass flow (Sankey-like).

    Stage 1: all siglum mass -> primary / structural / secondary.
    Stage 2: primary -> covered-118 (88,929) vs residue (264,583).
    """
    total = m["total_siglum_mass"]
    primary = m["primary_work_mass"]
    W, H = 860, 500
    lx, lw = 40, 16
    mx, mw = 340, 16
    rx, rw = 640, 16
    top, bot = 86, 400
    s = svg_header(W, H, "PD citation-mass flow into the DCS crosswalk")
    s += (f"<text x='30' y='30' {FONT} font-size='15' font-weight='bold'>"
          f"Where PD's citation mass goes — {total:,} siglum occurrences</text>\n")
    s += (f"<text x='{lx - 10}' y='{top - 14}' {FONT} font-size='12'>"
          f"All siglum occurrences — </text>\n")
    s += (f"<text x='{lx - 10 + 178}' y='{top - 14}' {FONT} font-size='12' "
          f"font-weight='bold'>{total:,}</text>\n")

    mid_lbl = [("Primary works", primary, C_COVERED),
               ("Structural", m["structural_mass"], C_STRUCT),
               ("Secondary scholarship", m["secondary_mass"], C_SECOND)]
    # Mid nodes stacked top-down, heights proportional to mass.
    ys = []
    y = top
    for _, v, _ in mid_lbl:
        h = (bot - top) * v / total
        ys.append((y, y + h))
        y += h
    prim_y0, prim_y1 = ys[0]
    r_lbl = [("Covered by DCS (118 works)", m["covered_mass"], C_COVERED),
             ("Residue (outside DCS)", m["residue_mass"], C_RESIDUE)]
    rights = []
    y = prim_y0
    for _, v, _ in r_lbl:
        h = (prim_y1 - prim_y0) * v / primary
        rights.append((y, y + h))
        y += h

    def ribbon(x0, y0a, y0b, x1, y1a, y1b, color):
        cx = (x0 + x1) / 2
        return (f"<path d='M {x0} {y0a:.1f} C {cx} {y0a:.1f}, {cx} {y1a:.1f}, "
                f"{x1} {y1a:.1f} L {x1} {y1b:.1f} C {cx} {y1b:.1f}, "
                f"{cx} {y0b:.1f}, {x0} {y0b:.1f} Z' fill='{color}' "
                f"opacity='0.5'/>\n")

    for (ya, yb), (_, v, color) in zip(ys, mid_lbl):
        s += ribbon(lx + lw, top, bot, mx, ya, yb, color)
    for (ya, yb), (_, v, color) in zip(rights, r_lbl):
        s += ribbon(mx + mw, prim_y0, prim_y1, rx, ya, yb, color)

    s += f"<rect x='{lx}' y='{top}' width='{lw}' height='{bot - top}' fill='#444444'/>\n"
    for (ya, yb), (_, v, color) in zip(ys, mid_lbl):
        s += (f"<rect x='{mx}' y='{ya:.1f}' width='{mw}' "
              f"height='{yb - ya:.1f}' fill='{color}'/>\n")
    for (ya, yb), (_, v, color) in zip(rights, r_lbl):
        s += (f"<rect x='{rx}' y='{ya:.1f}' width='{rw}' "
              f"height='{yb - ya:.1f}' fill='{color}'/>\n")

    for (ya, yb), (label, v, color) in zip(ys, mid_lbl):
        yc = (ya + yb) / 2
        if yb - ya < 30:
            yc = min(yb + 18, bot + 34)
        s += (f"<text x='{mx + 26}' y='{yc - 2:.1f}' {FONT} font-size='12'>"
              f"{label}</text>\n")
        s += (f"<text x='{mx + 26}' y='{yc + 14:.1f}' {FONT} font-size='12' "
              f"font-weight='bold'>{v:,} ({100 * v / total:.1f} %)</text>\n")
    for (ya, yb), (label, v, color) in zip(rights, r_lbl):
        yc = (ya + yb) / 2
        s += (f"<text x='{rx + 26}' y='{yc - 2:.1f}' {FONT} font-size='12'>"
              f"{label}</text>\n")
        s += (f"<text x='{rx + 26}' y='{yc + 14:.1f}' {FONT} font-size='12' "
              f"font-weight='bold'>{v:,} ({100 * v / primary:.1f} % of primary)</text>\n")
    s += (f"<text x='30' y='{H - 12}' {FONT} font-size='11' fill='#555555'>"
          f"ribbon height = occurrence mass · classes re-derived from "
          f"pd_siglum_families.tsv</text>\n")
    s += "</svg>\n"
    return s


def fig6(fasc, m):
    """Cat #2 — fascicle coverage strip with Wilson CIs (24 measured fascicles).

    Dots = per-fascicle coverage; whiskers = committed Wilson CIs; dashed line
    = pooled 25.16 %; shaded band = 16.91-36.90 % (layer-1 min/max, H7275);
    red dots = the 12 fascicles outside pooled ±2 pp.
    """
    pooled = m["metric_pd_citation_weighted_pct"]
    rows = [r for r in fasc if r["coverage_pct"].strip()]
    n = len(rows)
    lo = min(float(r["coverage_pct"]) for r in rows)
    hi = max(float(r["coverage_pct"]) for r in rows)
    outside = sum(1 for r in rows
                  if abs(float(r["coverage_pct"]) - pooled) > 2.0)
    W = 760
    rh = 25
    ptop, pbot_pad = 92, 64
    H = ptop + rh * n + pbot_pad
    x0, x1 = 130, 560
    xmin, xmax = 0.0, 45.0
    pbot = H - pbot_pad

    def xv(v):
        return x0 + (x1 - x0) * (v - xmin) / (xmax - xmin)

    s = svg_header(W, H, "Per-fascicle PD coverage with Wilson 95% CIs")
    s += (f"<text x='30' y='28' {FONT} font-size='15' font-weight='bold'>"
          f"Internal stability: coverage holds near 25 % across fascicles</text>\n")
    s += (f"<text x='30' y='48' {FONT} font-size='12' fill='#555555'>"
          f"{n} measured fascicles · whisker = Wilson 95 % CI · "
          f"red = outside pooled ±2 pp ({outside}/{n}) · band = min-max "
          f"{lo:.2f}-{hi:.2f} %</text>\n")
    s += (f"<rect x='{xv(lo):.1f}' y='{ptop}' width='{xv(hi) - xv(lo):.1f}' "
          f"height='{pbot - ptop}' fill='#f0f0f0'/>\n")
    for gv in (0, 10, 20, 30, 40):
        x = xv(gv)
        s += (f"<line x1='{x:.1f}' y1='{ptop}' x2='{x:.1f}' y2='{pbot}' "
              f"stroke='#dddddd'/>\n")
        s += (f"<text x='{x:.1f}' y='{pbot + 16}' {FONT} font-size='11' "
              f"text-anchor='middle'>{gv} %</text>\n")
    xp = xv(pooled)
    s += (f"<line x1='{xp:.1f}' y1='{ptop}' x2='{xp:.1f}' y2='{pbot}' "
          f"stroke='#444444' stroke-dasharray='6 4' stroke-width='1.5'/>\n")
    yy = ptop + rh / 2
    for r in rows:
        cov = float(r["coverage_pct"])
        wlo = float(r["wilson_lo"])
        whi = float(r["wilson_hi"])
        out = abs(cov - pooled) > 2.0
        color = C_RESIDUE if out else C_BAR
        ym = yy + rh / 2
        s += (f"<text x='{x0 - 12}' y='{ym + 4:.1f}' {FONT} font-size='11' "
              f"text-anchor='end'>{esc(r['ledger_id'])}</text>\n")
        s += (f"<line x1='{xv(wlo):.1f}' y1='{ym:.1f}' x2='{xv(whi):.1f}' "
              f"y2='{ym:.1f}' stroke='{color}' stroke-width='1.6'/>\n")
        for wv in (wlo, whi):
            s += (f"<line x1='{xv(wv):.1f}' y1='{ym - 5:.1f}' x2='{xv(wv):.1f}' "
                  f"y2='{ym + 5:.1f}' stroke='{color}' stroke-width='1.6'/>\n")
        s += f"<circle cx='{xv(cov):.1f}' cy='{ym:.1f}' r='4' fill='{color}'/>\n"
        s += (f"<text x='{x1 + 10}' y='{ym + 4:.1f}' {FONT} "
              f"font-size='10' fill='{color}'>{cov:.2f}</text>\n")
        yy += rh
    s += (f"<text x='{x1 + 10}' y='88' {FONT} font-size='10' fill='#555555' "
          f"text-anchor='start'>coverage</text>\n")
    s += (f"<line x1='{xp:.1f}' y1='{ptop - 6}' x2='{xp:.1f}' y2='{ptop}' "
          f"stroke='#444444' stroke-width='1.5'/>\n")
    s += (f"<text x='30' y='{H - 14}' {FONT} font-size='11' fill='#555555'>"
          f"pooled {pooled:.2f} % (dashed) · fascicles 9.1-35 (2009-2019) lie "
          f"outside the digital text and carry no coverage row</text>\n")
    s += "</svg>\n"
    return s
    s += (f"<text x='30' y='{H - 12}' {FONT} font-size='11' fill='#555555'>"
          f"fascicles 9.1-35 (2009-2019) lie outside the digital text and carry "
          f"no coverage row</text>\n")
    s += "</svg>\n"
    return s


def fig7(m):
    """Cat #12 — the denominator ladder of §5.2.1.

    398,359 all-siglum -> 353,512 primary -> 123,453 hand-adjudicated (pin)
    -> 88,929 covered. Step bars, every denominator in one look.
    """
    total = m["total_siglum_mass"]
    steps = [
        ("All siglum occurrences", total, C_STRUCT,
         ("letters a-: case labels,", "loci, scholarship, works")),
        ("Primary work occurrences", m["primary_work_mass"], C_SECOND,
         ("siglum adjudicated", "class = primary")),
        ("Hand-adjudicated primary", PIN_ADJUDICATED, "#d6604d",
         ("164 hand-adjudicated", "titles (pin)")),
        ("Covered by DCS (118 works)", m["covered_mass"], C_COVERED,
         ("matched in the crosswalk",)),
    ]
    W, H = 780, 410
    x0, y0 = 70, 80
    bw, gap = 140, 30
    plot_h = 220
    s = svg_header(W, H, "The denominator ladder of the coverage headline")
    s += (f"<text x='30' y='30' {FONT} font-size='15' font-weight='bold'>"
          f"One claim, four denominators — what 25.2 % is a fraction of</text>\n")
    x = x0
    for label, v, color, note_lines in steps:
        h = plot_h * v / total
        y = y0 + plot_h - h
        s += f"<rect x='{x}' y='{y:.1f}' width='{bw}' height='{h:.1f}' fill='{color}'/>\n"
        s += (f"<text x='{x + bw / 2}' y='{y - 10:.1f}' {FONT} font-size='13' "
              f"font-weight='bold' text-anchor='middle'>{v:,}</text>\n")
        s += (f"<text x='{x + bw / 2}' y='{y - 26:.1f}' {FONT} font-size='11' "
              f"fill='#555555' text-anchor='middle'>"
              f"{100 * v / total:.1f} % of all</text>\n")
        s += (f"<text x='{x + bw / 2}' y='{y0 + plot_h + 20}' {FONT} "
              f"font-size='11' font-weight='bold' text-anchor='middle'>"
              f"{label}</text>\n")
        for j, line in enumerate(note_lines):
            s += (f"<text x='{x + bw / 2}' y='{y0 + plot_h + 36 + j * 12}' "
                  f"{FONT} font-size='10' fill='#555555' text-anchor='middle'>"
                  f"{esc(line)}</text>\n")
        x += bw + gap
    s += (f"<text x='30' y='{H - 16}' {FONT} font-size='11' fill='#555555'>"
          f"25.16 % = 88,929 / 353,512 (PD-citation-weighted) · third rung is "
          f"the claim-ledger pin P-adjudicated (164 titles)</text>\n")
    s += "</svg>\n"
    return s


def fig8(ledger):
    """Cat #13 — fifty-year fascicle timeline (gantt ribbon, 1976-2019).

    Each fascicle occupies the interval from its publication year to the
    next fascicle's year (the last runs to 2019); colour = in_digital_text.
    """
    rows = ledger
    n = len(rows)
    W = 860
    rh = 20
    H = 110 + rh * n
    ax0, ax1 = 250, 560

    def xx(yr):
        return ax0 + (ax1 - ax0) * (yr - 1976) / (2019 - 1976)

    s = svg_header(W, H, "Fifty years of the Poona Dictionary, fascicle by fascicle")
    s += (f"<text x='30' y='28' {FONT} font-size='15' font-weight='bold'>"
          f"1976-2019: {n} fascicles, one dictionary</text>\n")
    s += (f"<text x='30' y='48' {FONT} font-size='12' fill='#555555'>"
          f"ribbon = interval until the next fascicle · blue = in digital text, "
          f"grey = print-only · pp. = printed extent</text>\n")
    for yr in list(range(1976, 2016, 4)) + [2019]:
        x = xx(yr)
        s += (f"<line x1='{x:.1f}' y1='74' x2='{x:.1f}' y2='{H - 36}' "
              f"stroke='#eeeeee'/>\n")
        s += (f"<text x='{x:.1f}' y='{H - 22}' {FONT} font-size='10' "
              f"text-anchor='middle'>{yr}</text>\n")
    yy = 82
    ndig = 0
    for i, r in enumerate(rows):
        yr = int(r["year"])
        yr_end = int(rows[i + 1]["year"]) if i + 1 < n else 2019
        if yr_end <= yr:
            yr_end = yr + 1
        indig = r["in_digital_text"].strip().lower() == "yes"
        ndig += indig
        color = C_BAR if indig else "#b8b8b8"
        ym = yy + rh / 2
        s += (f"<text x='140' y='{ym + 3:.1f}' {FONT} font-size='10' "
              f"text-anchor='end'>{esc(r['ledger_id'])}</text>\n")
        pair = f"{r['open_entry']} → {r['close_entry']}"
        if len(pair) > 20:
            pair = pair[:19] + "…"
        s += (f"<text x='246' y='{ym + 3:.1f}' {FONT} font-size='8' "
              f"fill='#555555' text-anchor='end'>{esc(pair)}</text>\n")
        s += (f"<rect x='{xx(yr):.1f}' y='{ym - 6:.1f}' "
              f"width='{xx(yr_end) - xx(yr):.1f}' height='12' fill='{color}'/>\n")
        s += (f"<text x='{W - 24}' y='{ym + 3:.1f}' {FONT} font-size='9' "
              f"fill='#555555' text-anchor='end'>pp. {r['pp_lo']}-{r['pp_hi']}</text>\n")
        yy += rh
    s += (f"<text x='30' y='{H - 8}' {FONT} font-size='11' fill='#555555'>"
          f"digital text covers fascicles 1.1-8.4 ({ndig} of {n}); pp. extents "
          f"from pd_publication_ledger.tsv</text>\n")
    s += "</svg>\n"
    return s


def fig9(dens):
    """Cat #20 — two-layer paired bars: PD vs PWG attestations per stratum.

    What PWG gave PD: attestation counts per policy-matched stratum
    (simplex 46,236 vs 6,144, ratio 7.5x).
    """
    strata = [r for r in dens if r["row_kind"] == "stratum"]
    pooled = next(r for r in dens
                  if r["stratum"] == "pooled_standardised_equal_weight")
    groups = strata + [pooled]
    W, H = 880, 400
    x0 = 215
    plot_h = 240
    y0 = 70
    maxv = max(int(r["pd_attestations"]) for r in groups)
    bw = 56

    s = svg_header(W, H, "PD vs PWG attestations per morphological stratum")
    s += (f"<text x='30' y='30' {FONT} font-size='15' font-weight='bold'>"
          f"What PWG gave PD: attestations per stratum, policy-matched key-1s</text>\n")
    s += (f"<text x='30' y='50' {FONT} font-size='12' fill='#555555'>"
          f"dark = PD attestations · light = PWG attestations · label = ratio PD/PWG</text>\n")
    for gv in (0, 25000, 50000, 75000, 100000):
        y = y0 + plot_h - plot_h * gv / maxv
        s += (f"<line x1='{x0 - 10}' y1='{y:.1f}' x2='{W - 20}' y2='{y:.1f}' "
              f"stroke='#dddddd'/>\n")
        lbl = f"{gv // 1000}k" if gv else "0"
        s += (f"<text x='{x0 - 16}' y='{y + 4:.1f}' {FONT} font-size='11' "
              f"text-anchor='end'>{lbl}</text>\n")
    x = x0
    for r in groups:
        pdv = int(r["pd_attestations"])
        pwv = int(r["pwg_attestations"])
        ratio = pdv / pwv
        name = r["stratum"]
        if name.startswith("pooled"):
            name = "pooled (std.)"
        fw = "font-weight='bold' " if r["stratum"].startswith("pooled") else ""
        s += (f"<text x='{x - 10}' y='{y0 + plot_h / 2:.1f}' {FONT} "
              f"font-size='11' {fw}text-anchor='end'>{esc(name)}</text>\n")
        h1 = plot_h * pdv / maxv
        s += (f"<rect x='{x}' y='{y0 + plot_h - h1:.1f}' width='{bw}' "
              f"height='{h1:.1f}' fill='{C_BAR}'/>\n")
        s += (f"<text x='{x + bw / 2}' y='{y0 + plot_h - h1 - 6:.1f}' {FONT} "
              f"font-size='10' text-anchor='middle'>{pdv:,}</text>\n")
        h2 = plot_h * pwv / maxv
        s += (f"<rect x='{x + bw + 6}' y='{y0 + plot_h - h2:.1f}' width='{bw}' "
              f"height='{h2:.1f}' fill='{C_BAR2}'/>\n")
        s += (f"<text x='{x + bw + 6 + bw / 2}' y='{y0 + plot_h - h2 - 6:.1f}' "
              f"{FONT} font-size='10' text-anchor='middle'>{pwv:,}</text>\n")
        s += (f"<text x='{x + bw + 3}' y='{y0 + plot_h + 18}' {FONT} "
              f"font-size='12' font-weight='bold' text-anchor='middle'>"
              f"{ratio:.1f}×</text>\n")
        x += 2 * bw + 24
    s += (f"<text x='30' y='{H - 12}' {FONT} font-size='11' fill='#555555'>"
          f"policy-matched density sample (4,093 key-1 headwords, equal stratum "
          f"weights) · pooled standardised ratio 8.41×</text>\n")
    s += "</svg>\n"
    return s


def fig15(cls, m):
    """Cat #19 — class-coverage forest with Wilson CIs (six classes).

    Coverage = covered_loci / primary_loci per morphological class; pooled
    25.16 % line; policy-matched annotation.
    """
    pooled = m["metric_pd_citation_weighted_pct"]
    rows = sorted(cls, key=lambda r: -float(r["coverage_pct"]))
    W, H = 760, 130 + 44 * len(rows)
    x0, x1 = 200, 580
    xmax = 40.0

    def xx(v):
        return x0 + (x1 - x0) * v / xmax

    s = svg_header(W, H, "Coverage by morphological class, with 95% CIs")
    s += (f"<text x='30' y='30' {FONT} font-size='15' font-weight='bold'>"
          f"Preverbs and simplexes lead; derivatives lag</text>\n")
    s += (f"<text x='30' y='50' {FONT} font-size='12' fill='#555555'>"
          f"dot = covered/primary loci · whisker = Wilson 95 % CI · "
          f"policy-matched simplex ratio vs PWG: 7.5× (see fig. 9)</text>\n")
    for gv in (0, 10, 20, 30, 40):
        x = xx(gv)
        s += (f"<line x1='{x:.1f}' y1='76' x2='{x:.1f}' y2='{H - 58}' "
              f"stroke='#dddddd'/>\n")
        s += (f"<text x='{x:.1f}' y='{H - 42}' {FONT} font-size='11' "
              f"text-anchor='middle'>{gv} %</text>\n")
    px = xx(pooled)
    s += (f"<line x1='{px:.1f}' y1='76' x2='{px:.1f}' y2='{H - 58}' "
          f"stroke='#444444' stroke-dasharray='6 4' stroke-width='1.5'/>\n")
    s += (f"<text x='{px:.1f}' y='70' {FONT} font-size='11' "
          f"text-anchor='middle'>pooled {pooled:.2f} %</text>\n")
    y = 96
    for r in rows:
        cov = float(r["coverage_pct"])
        wlo = float(r["wilson_lo"])
        whi = float(r["wilson_hi"])
        n = int(r["primary_loci"])
        ym = y + 22
        s += (f"<text x='{x0 - 12}' y='{ym + 4:.1f}' {FONT} font-size='12' "
              f"text-anchor='end'>{esc(r['class'])}</text>\n")
        s += (f"<line x1='{xx(wlo):.1f}' y1='{ym:.1f}' x2='{xx(whi):.1f}' "
              f"y2='{ym:.1f}' stroke='#2166ac' stroke-width='2'/>\n")
        for wv in (wlo, whi):
            s += (f"<line x1='{xx(wv):.1f}' y1='{ym - 5:.1f}' x2='{xx(wv):.1f}' "
                  f"y2='{ym + 5:.1f}' stroke='#2166ac' stroke-width='2'/>\n")
        s += f"<circle cx='{xx(cov):.1f}' cy='{ym:.1f}' r='4.5' fill='#2166ac'/>\n"
        s += (f"<text x='{x1 + 14}' y='{ym + 4:.1f}' {FONT} font-size='11'>"
              f"{cov:.2f} [{wlo:.2f}, {whi:.2f}] · n={n:,}</text>\n")
        y += 44
    s += "</svg>\n"
    return s
