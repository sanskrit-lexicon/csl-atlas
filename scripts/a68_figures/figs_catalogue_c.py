"""Figs 14b/16 — MG review follow-ups (31-10).

fig14b: corpus size vs dictionary attention, zoomed 2x per axis as four
        median-quadrant panels + small overview; EVERY title labelled.
fig16:  PWG vs PD per morphological stratum — the companion fig15 asked
        for ("another where PWG vs. PD"): fig15 shows PD coverage by
        class with Wilson CIs; fig16 shows what each dictionary gives per
        stratum, with the committed attestation-ratio CIs.
"""
import math

from .helpers import FONT, esc, svg_header


def fig14b(crosswalk, m):
    """Cat #9 zoom — 4 median-quadrant panels at ~2x axis scale each."""
    pts = [(r["dcs_title"], int(r["dcs_tok_2026"]), int(r["pd_citations"]))
           for r in crosswalk]
    xs = sorted(p[1] for p in pts)
    ys = sorted(p[2] for p in pts)
    n = len(pts)
    medx = (xs[n // 2 - 1] + xs[n // 2]) / 2
    medy = (ys[n // 2 - 1] + ys[n // 2]) / 2
    quads = {
        "A": ("small corpus × heavy attention",
              [p for p in pts if p[1] < medx and p[2] >= medy]),
        "B": ("big corpus × heavy attention",
              [p for p in pts if p[1] >= medx and p[2] >= medy]),
        "C": ("small corpus × light attention",
              [p for p in pts if p[1] < medx and p[2] < medy]),
        "D": ("big corpus × light attention",
              [p for p in pts if p[1] >= medx and p[2] < medy]),
    }
    W, H = 1600, 1030

    def rng(vals, pad=0.06):
        lo = math.log10(min(vals))
        hi = math.log10(max(vals))
        d = (hi - lo) * pad
        return (lo - d, hi + d)

    def tickfmt(e):
        return {0: "1", 1: "10", 2: "100", 3: "1k", 4: "10k", 5: "100k",
                6: "1M", 7: "10M"}.get(e, f"1e{e}")

    s = svg_header(W, H, "Corpus size vs dictionary attention — quadrant zoom")
    s += (f"<text x='30' y='34' {FONT} font-size='17' font-weight='bold'>"
          f"Corpus size vs dictionary attention — every covered title, "
          f"readable</text>\n")
    s += (f"<text x='30' y='56' {FONT} font-size='12' fill='#555555'>"
          f"zoom: four median quadrants at ~2× axis scale (≈4× area) · "
          f"crosshairs = medians ({medx:,.0f} tok, {medy:,.0f} cites) · "
          f"n = {n}</text>\n")

    # --- overview, top left ---
    ox0, ox1, oy0, oy1 = 60, 500, 100, 480
    lx, ly = (2.0, 7.0), (0.0, 4.2)

    def oxx(v):
        return ox0 + (ox1 - ox0) * (math.log10(v) - lx[0]) / (lx[1] - lx[0])

    def oyy(v):
        return oy1 - (oy1 - oy0) * (math.log10(v) - ly[0]) / (ly[1] - ly[0])

    s += (f"<text x='{ox0}' y='{oy0 - 12}' {FONT} font-size='12' "
          f"font-weight='bold'>overview</text>\n")
    for _, tok, cit in pts:
        s += (f"<circle cx='{oxx(tok):.1f}' cy='{oyy(cit):.1f}' r='2.6' "
              f"fill='#2166ac' opacity='0.6'/>\n")
    s += (f"<line x1='{oxx(medx):.1f}' y1='{oy0}' x2='{oxx(medx):.1f}' "
          f"y2='{oy1}' stroke='#999999' stroke-dasharray='4 3'/>\n")
    s += (f"<line x1='{ox0}' y1='{oyy(medy):.1f}' x2='{ox1}' "
          f"y2='{oyy(medy):.1f}' stroke='#999999' stroke-dasharray='4 3'/>\n")
    qlab = {"A": (ox0 + 10, oy0 + 16, "start"), "B": (ox1 - 10, oy0 + 16, "end"),
            "C": (ox0 + 10, oy1 - 10, "start"), "D": (ox1 - 10, oy1 - 10, "end")}
    for q, (qx, qy, anch) in qlab.items():
        s += (f"<text x='{qx}' y='{qy}' {FONT} font-size='12' "
              f"font-weight='bold' fill='#b2182b' text-anchor='{anch}'>"
              f"{q} · {len(quads[q])} titles</text>\n")

    # --- four zoom panels ---
    pw, ph = 490, 410
    pos = {"A": (560, 100), "B": (1080, 100), "C": (560, 560), "D": (1080, 560)}
    for q, (px, py) in pos.items():
        reading, qpts = quads[q]
        xr = rng([p[1] for p in qpts])
        yr = rng([p[2] for p in qpts])
        qx0, qy1 = px + 70, py + ph - 44
        qx1, qy0 = px + pw - 130, py + 40

        def qx(v, xr=xr):
            return qx0 + (qx1 - qx0) * (math.log10(v) - xr[0]) / (xr[1] - xr[0])

        def qy(v, yr=yr):
            return qy1 - (qy1 - qy0) * (math.log10(v) - yr[0]) / (yr[1] - yr[0])

        s += (f"<rect x='{px + 4}' y='{py}' width='{pw - 8}' height='{ph}' "
              f"fill='#fbfbfb' stroke='#dddddd'/>\n")
        s += (f"<text x='{px + 16}' y='{py + 24}' {FONT} font-size='13' "
              f"font-weight='bold' fill='#b2182b'>{q}</text>\n")
        s += (f"<text x='{px + 36}' y='{py + 24}' {FONT} font-size='12.5'>"
              f"{reading} · {len(qpts)} titles</text>\n")
        for e in range(math.floor(xr[0]), math.ceil(xr[1]) + 1):
            v = 10 ** e
            if not (xr[0] <= math.log10(v) <= xr[1]):
                continue
            x = qx(v)
            s += (f"<line x1='{x:.1f}' y1='{qy0}' x2='{x:.1f}' y2='{qy1}' "
                  f"stroke='#eeeeee'/>\n")
            s += (f"<text x='{x:.1f}' y='{qy1 + 16}' {FONT} font-size='10.5' "
                  f"text-anchor='middle'>{tickfmt(e)}</text>\n")
        for e in range(math.floor(yr[0]), math.ceil(yr[1]) + 1):
            v = 10 ** e
            if not (yr[0] <= math.log10(v) <= yr[1]):
                continue
            y = qy(v)
            s += (f"<line x1='{qx0}' y1='{y:.1f}' x2='{qx1}' y2='{y:.1f}' "
                  f"stroke='#eeeeee'/>\n")
            s += (f"<text x='{qx0 - 8}' y='{y + 4:.1f}' {FONT} font-size='10.5'"
                  f" text-anchor='end'>{tickfmt(e)}</text>\n")
        # Label placement: preferred side by panel midx, but every label
        # must fit INSIDE its panel box (flip side / truncate to the
        # available room); greedy vertical ladder per side, shifted up as
        # a block if it overruns the bottom.
        midx = (qx0 + qx1) / 2
        CH = 5.6  # px per 10px-font character, conservative
        sides = {"right": [], "left": []}
        for p in qpts:
            title, tok, cit = p
            x, y = qx(tok), qy(cit)
            lbl = title if len(title) <= 26 else title[:25] + "…"
            w = CH * len(lbl)
            pref = "right" if x >= midx else "left"
            room_r = (px + pw - 6) - (x + 6)
            room_l = (x - 6) - (px + 6)
            if (pref == "right" and room_r >= w) or \
               (pref == "left" and room_l >= w):
                side = pref
            elif room_r >= w or room_r > room_l:
                side = "right"
            else:
                side = "left"
            room = room_r if side == "right" else room_l
            if CH * len(lbl) > room:
                keep = max(4, int(room / CH) - 1)
                lbl = lbl[:keep] + "…"
            sides[side].append((x, y, lbl))
        for side in ("right", "left"):
            placed = []
            ladder = -10_000.0
            for x, y, lbl in sorted(sides[side],
                                    key=lambda t: t[1]):
                ly_t = max(y - 3.5, ladder + 11.5, qy0 + 8)
                ladder = ly_t
                placed.append((x, y, ly_t, lbl))
            if placed:
                over = max(0.0, placed[-1][2] - (qy1 - 2))
                if over:
                    placed = [(x, y, ly - over, t)
                              for x, y, ly, t in placed]
            for x, y, ly_t, lbl in placed:
                s += (f"<circle cx='{x:.1f}' cy='{y:.1f}' r='3.4' "
                      f"fill='#2166ac' opacity='0.75'/>\n")
                dx = 6 if side == "right" else -6
                anch = "start" if side == "right" else "end"
                s += (f"<text x='{x + dx:.1f}' y='{ly_t:.1f}' {FONT} "
                      f"font-size='10' fill='#333333' text-anchor='{anch}'>"
                      f"{esc(lbl)}</text>\n")
                if abs(ly_t - 3.5 - y) > 4:
                    s += (f"<line x1='{x + dx * .6:.1f}' y1='{y:.1f}' "
                          f"x2='{x + dx:.1f}' y2='{ly_t - 3:.1f}' "
                          f"stroke='#bbbbbb' stroke-width='0.6'/>\n")
        s += (f"<text x='{(qx0 + qx1) / 2:.0f}' y='{qy1 + 34}' {FONT} "
              f"font-size='10.5' fill='#555555' text-anchor='middle'>"
              f"DCS tokens 2026</text>\n")
        s += (f"<text x='{px + 14}' y='{(qy0 + qy1) / 2:.0f}' {FONT} "
              f"font-size='10.5' fill='#555555' "
              f"transform='rotate(-90 {px + 14} {(qy0 + qy1) / 2:.0f})' "
              f"text-anchor='middle'>PD citations</text>\n")

    # overview panel axis labels
    for e in (2, 4, 6):
        x = oxx(10 ** e)
        s += (f"<text x='{x:.1f}' y='{oy1 + 16}' {FONT} font-size='10.5' "
              f"text-anchor='middle'>{tickfmt(e)}</text>\n")
    for e in (0, 2, 4):
        y = oyy(10 ** e)
        s += (f"<text x='{ox0 - 8}' y='{y + 4:.1f}' {FONT} font-size='10.5' "
              f"text-anchor='end'>{tickfmt(e)}</text>\n")
    s += (f"<text x='30' y='{H - 14}' {FONT} font-size='11' fill='#555555'>"
          f"log scales · labels truncated at 25 chars · quadrant split at the "
          f"medians; panel edges ARE the median crosshair</text>\n")
    s += "</svg>\n"
    return s, {q: len(v[1]) for q, v in quads.items()}


def fig16(dens):
    """PWG vs PD per morphological stratum — companion to fig15.

    Left: paired attestation dots per stratum on a shared log axis
    (open grey = PWG, filled blue = PD). Right: the COMMITTED
    attestation-ratio with its CI columns (attestation_ratio_lo/hi);
    unclassified carries no committed CI and is shown without one.
    """
    strata = [r for r in dens if r["row_kind"] == "stratum"]
    pooled = next(r for r in dens
                  if r["stratum"] == "pooled_standardised_equal_weight")
    rows = strata + [pooled]
    W, H = 780, 130 + 46 * len(rows)
    x0, x1 = 210, 560
    lo, hi = 2.0, math.log10(200000)

    def xx(v):
        return x0 + (x1 - x0) * (math.log10(v) - lo) / (hi - lo)

    s = svg_header(W, H, "PWG vs PD attestations per stratum, forest form")
    s += (f"<text x='30' y='30' {FONT} font-size='15' font-weight='bold'>"
          f"What each dictionary gives: PWG vs PD per stratum</text>\n")
    s += (f"<text x='30' y='50' {FONT} font-size='12' fill='#555555'>"
          f"open grey = PWG attestations · filled blue = PD attestations · "
          f"right: PD/PWG ratio with committed CI</text>\n")
    for gv, gl in ((100, "100"), (1000, "1k"), (10000, "10k"),
                   (100000, "100k")):
        x = xx(gv)
        s += (f"<line x1='{x:.1f}' y1='76' x2='{x:.1f}' y2='{H - 58}' "
              f"stroke='#dddddd'/>\n")
        s += (f"<text x='{x:.1f}' y='{H - 42}' {FONT} font-size='11' "
              f"text-anchor='middle'>{gl}</text>\n")
    y = 96
    for r in rows:
        pdv = int(r["pd_attestations"])
        pwv = int(r["pwg_attestations"])
        ratio = float(r["attestation_ratio"])
        rlo = r["attestation_ratio_lo"].strip()
        rhi = r["attestation_ratio_hi"].strip()
        pooled_row = r["row_kind"] == "pooled"
        name = "pooled (std.)" if pooled_row else r["stratum"]
        fw = "font-weight='bold' " if pooled_row else ""
        ym = y + 24
        s += (f"<text x='{x0 - 12}' y='{ym + 4:.1f}' {FONT} font-size='12' "
              f"{fw}text-anchor='end'>{esc(name)}</text>\n")
        s += (f"<line x1='{xx(pwv):.1f}' y1='{ym:.1f}' x2='{xx(pdv):.1f}' "
              f"y2='{ym:.1f}' stroke='#999999' stroke-width='1.6'/>\n")
        s += (f"<circle cx='{xx(pwv):.1f}' cy='{ym:.1f}' r='4.5' "
              f"fill='white' stroke='#777777' stroke-width='1.6'/>\n")
        s += (f"<circle cx='{xx(pdv):.1f}' cy='{ym:.1f}' r='4.5' "
              f"fill='#2166ac'/>\n")
        # Value rides above the dot when the row is long enough that the
        # inline value would reach the ratio column.
        vw = 6.2 * len(f"{pdv:,}")
        if xx(pdv) + 8 + vw > x1 + 8:
            s += (f"<text x='{xx(pdv):.1f}' y='{ym - 12:.1f}' {FONT} "
                  f"font-size='10' fill='#2166ac' text-anchor='middle'>"
                  f"{pdv:,}</text>\n")
        else:
            s += (f"<text x='{xx(pdv) + 8:.1f}' y='{ym + 4:.1f}' {FONT} "
                  f"font-size='10' fill='#2166ac'>{pdv:,}</text>\n")
        ci = (f" [{float(rlo):.2f}, {float(rhi):.2f}]"
              if rlo and rhi else " [no committed CI]")
        s += (f"<text x='{x1 + 14}' y='{ym + 4:.1f}' {FONT} font-size='11.5' "
              f"{fw}fill='#333333'>{ratio:.2f}×{ci}</text>\n")
        y += 46
    s += (f"<text x='30' y='{H - 14}' {FONT} font-size='11' fill='#555555'>"
          f"ratio CIs as committed in pd_policy_matched_density.tsv · "
          f"companion to fig. 15 (class-coverage forest, PD side)</text>\n")
    s += "</svg>\n"
    return s
