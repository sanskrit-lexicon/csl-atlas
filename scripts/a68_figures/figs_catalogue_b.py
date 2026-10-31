"""Figs 10-15 — catalogue figures (H7545): DCS-276 layer bar, layer skew,
availability pyramid, coverage slope, corpus-vs-attention, class forest."""
import math

from .helpers import (C4_LAYERS, C_BAR, C_BAR2, C_COVERED, C_RESIDUE,
                      C_SECOND, FONT, esc, svg_header)


def fig10(m):
    """Cat #24 — DCS-276 token mass by Renou layer, all vs covered-118.

    Encodes the committed C4 sweep table; Vedic+epic 44.0 % (all) vs 53.0 %
    (covered, exact 53.05 — the sweep prose rounds it to 53.1), classical
    52.0 % annotated. Layer tags are sweep literals — the per-text tag map
    is not committed; nothing here re-tags texts.
    """
    layers = C4_LAYERS
    tot26 = sum(r[2] for r in layers)
    cov26 = sum(r[5] for r in layers)
    vedic_epic = sum(r[2] for r in layers if r[0] in ("Vedic", "epic"))
    vedic_epic_cov = sum(r[5] for r in layers if r[0] in ("Vedic", "epic"))
    classical = sum(r[2] for r in layers
                    if r[0] in ("śāstra", "kāvya", "purāṇic"))
    colors = {"Vedic": "#d73027", "epic": "#f46d43", "śāstra": "#2166ac",
              "kāvya": "#92c5de", "purāṇic": "#54278f", "other": "#999999"}
    W, H = 860, 340
    bx, bw = 190, 540
    rowy = (86, 196)
    rowh = 46
    s = svg_header(W, H, "DCS-276 token mass by Renou layer")
    s += (f"<text x='30' y='30' {FONT} font-size='15' font-weight='bold'>"
          f"Vedic+epic layers carry {100 * vedic_epic / tot26:.1f} % of DCS "
          f"tokens — {100 * vedic_epic_cov / cov26:.1f} % inside the "
          f"PD-covered set</text>\n")
    for ri, (label, tot) in enumerate((("All DCS-276 (2026 snapshot)", tot26),
                                       ("PD-covered 118", cov26))):
        x = bx
        y = rowy[ri]
        s += (f"<text x='{bx - 10}' y='{y + rowh / 2 + 4:.1f}' {FONT} "
              f"font-size='12' text-anchor='end'>{label}</text>\n")
        for lname, _, tok26, _, _, ctok, _ in layers:
            v = tok26 if ri == 0 else ctok
            w = bw * v / tot
            s += (f"<rect x='{x:.1f}' y='{y}' width='{w:.1f}' height='{rowh}' "
                  f"fill='{colors[lname]}'/>\n")
            if w > 52:
                s += (f"<text x='{x + w / 2:.1f}' y='{y + rowh / 2 + 4:.1f}' "
                      f"{FONT} font-size='11' fill='white' text-anchor='middle'>"
                      f"{100 * v / tot:.1f} %</text>\n")
            x += w
    ve_end = bx + bw * vedic_epic / tot26
    ve_cov_end = bx + bw * vedic_epic_cov / cov26
    cl_end = bx + bw * classical / tot26
    s += (f"<line x1='{bx}' y1='74' x2='{ve_end:.1f}' y2='74' stroke='#444444' "
          f"stroke-width='1.2'/>\n")
    s += (f"<text x='{(bx + ve_end) / 2:.1f}' y='68' {FONT} font-size='12' "
          f"font-weight='bold' text-anchor='middle'>Vedic+epic "
          f"{100 * vedic_epic / tot26:.1f} %</text>\n")
    s += (f"<line x1='{ve_end:.1f}' y1='74' x2='{cl_end:.1f}' y2='74' "
          f"stroke='#888888'/>\n")
    s += (f"<text x='{(ve_end + cl_end) / 2:.1f}' y='68' {FONT} font-size='12' "
          f"fill='#555555' text-anchor='middle'>classical "
          f"{100 * classical / tot26:.1f} %</text>\n")
    s += (f"<line x1='{bx}' y1='{rowy[1] - 12}' x2='{ve_cov_end:.1f}' "
          f"y2='{rowy[1] - 12}' stroke='#444444' stroke-width='1.2'/>\n")
    s += (f"<text x='{(bx + ve_cov_end) / 2:.1f}' y='{rowy[1] - 17}' {FONT} "
          f"font-size='12' font-weight='bold' text-anchor='middle'>"
          f"{100 * vedic_epic_cov / cov26:.1f} %</text>\n")
    lx, ly = bx, 272
    for lname, _, tok26, _, _, _, _ in layers:
        s += (f"<rect x='{lx}' y='{ly - 11}' width='13' height='13' "
              f"fill='{colors[lname]}'/>\n")
        s += (f"<text x='{lx + 18}' y='{ly}' {FONT} font-size='12'>"
              f"{esc(lname)} — {tok26:,} tok</text>\n")
        lx += 30 + 7 * len(lname) + 78
        if lx > W - 170:
            lx = bx
            ly += 24
    s += (f"<text x='30' y='{H - 10}' {FONT} font-size='11' fill='#555555'>"
          f"layer tags: committed C4 sweep (H6698, 14-10-2026) · the documented "
          f"sūtra-cycle call lifts Vedic+epic to 50.5 %</text>\n")
    s += "</svg>\n"
    return s


def fig11(m):
    """Cat #25 — citation-vs-token skew inside the covered-118.

    Per layer: % of covered tokens (blue) vs % of PD citations (red).
    Vedic cited over-weight (19.3 → 24.2), śāstra under (24.2 → 39.1).
    """
    layers = C4_LAYERS
    cov26 = sum(r[5] for r in layers)
    cit = sum(r[6] for r in layers)
    rows = [(r[0], 100 * r[5] / cov26, 100 * r[6] / cit) for r in layers]
    vedic = next(r for r in rows if r[0] == "Vedic")
    sastra = next(r for r in rows if r[0] == "śāstra")
    W, H = 760, 370
    x0, x1 = 190, 600
    rh = 36
    y0 = 90
    maxv = 45.0

    def xx(v):
        return x0 + (x1 - x0) * v / maxv

    s = svg_header(W, H, "Citation-vs-token skew inside the covered 118")
    s += (f"<text x='30' y='30' {FONT} font-size='15' font-weight='bold'>"
          f"PD cites the Vedic layers far above their token weight</text>\n")
    s += (f"<text x='30' y='50' {FONT} font-size='12' fill='#555555'>"
          f"blue dot = share of covered tokens · red dot = share of PD citations</text>\n")
    for gv in (0, 10, 20, 30, 40):
        x = xx(gv)
        s += (f"<line x1='{x:.1f}' y1='{y0 - 14}' x2='{x:.1f}' "
              f"y2='{y0 + rh * len(rows)}' stroke='#dddddd'/>\n")
        s += (f"<text x='{x:.1f}' y='{y0 + rh * len(rows) + 16}' {FONT} "
              f"font-size='11' text-anchor='middle'>{gv} %</text>\n")
    y = y0
    for lname, tokpct, citpct in rows:
        ym = y + rh / 2
        s += (f"<text x='{x0 - 12}' y='{ym + 4:.1f}' {FONT} font-size='12' "
              f"text-anchor='end'>{esc(lname)}</text>\n")
        x1p, x2p = xx(tokpct), xx(citpct)
        s += (f"<line x1='{x1p:.1f}' y1='{ym:.1f}' x2='{x2p:.1f}' y2='{ym:.1f}' "
              f"stroke='#bbbbbb' stroke-width='2'/>\n")
        s += f"<circle cx='{x2p:.1f}' cy='{ym:.1f}' r='5' fill='{C_RESIDUE}'/>\n"
        s += (f"<circle cx='{x1p:.1f}' cy='{ym:.1f}' r='5' fill='{C_BAR}' "
              f"stroke='white' stroke-width='1.5'/>\n")
        lx = max(x1p, x2p) + 14
        s += (f"<text x='{lx:.1f}' y='{ym + 4:.1f}' "
              f"{FONT} font-size='11' fill='#333333' text-anchor='start'>"
              f"{tokpct:.1f} → {citpct:.1f}</text>\n")
        y += rh
    s += (f"<text x='30' y='{H - 12}' {FONT} font-size='11' fill='#555555'>"
          f"Vedic +{vedic[2] - vedic[1]:.1f} pp cited over its token weight · "
          f"śāstra {sastra[2] - sastra[1]:.1f} pp under · per-layer residue "
          f"composition stays blocked (C2/C8)</text>\n")
    s += "</svg>\n"
    return s


def fig12(avail_sig, avail_summary):
    """Cat #29 — edition-availability pyramid: attestation mass by class.

    available_full 144,615 / partial 44,030 / embedded 755 / unresolved
    230,490 of 419,890 attestations; AOB-row annotation from the summary.
    """
    order = ["available_full", "available_partial", "available_embedded",
             "unresolved"]
    labels = {"available_full": "Full e-text available",
              "available_partial": "Partial edition available",
              "available_embedded": "Embedded witness only",
              "unresolved": "Unresolved (not absence)"}
    colors = {"available_full": C_COVERED, "available_partial": C_BAR2,
              "available_embedded": C_SECOND, "unresolved": "#b8b8b8"}
    agg = {c: 0 for c in order}
    for r in avail_sig:
        a = r["availability"].strip() or "unresolved"
        agg[a if a in agg else "unresolved"] += int(r["attestations"])
    total = sum(agg.values())
    avail = agg["available_full"] + agg["available_partial"] + agg["available_embedded"]
    aob = avail_summary["aob_entries"]["by_availability"]
    W, H = 760, 400
    cx = 380
    bw_max = 640
    rh = 52
    y0 = 96
    s = svg_header(W, H, "Edition availability of PD's cited sources")
    s += (f"<text x='30' y='30' {FONT} font-size='15' font-weight='bold'>"
          f"What DCS could legitimately absorb next: availability of cited editions</text>\n")
    s += (f"<text x='30' y='50' {FONT} font-size='12' fill='#555555'>"
          f"bar width = attestation mass (n = {total:,}) · work-level e-text "
          f"presence, not edition identity</text>\n")
    y = y0
    for c in order:
        v = agg[c]
        w = bw_max * v / total
        ym = y + rh / 2
        s += (f"<rect x='{cx - w / 2:.1f}' y='{y:.1f}' width='{w:.1f}' "
              f"height='{rh - 10}' fill='{colors[c]}'/>\n")
        if w >= 150:
            s += (f"<text x='{cx}' y='{ym - 2:.1f}' {FONT} font-size='12' "
                  f"font-weight='bold' text-anchor='middle' fill='white'>"
                  f"{v:,} ({100 * v / total:.1f} %)</text>\n")
        else:
            s += (f"<text x='{cx + w / 2 + 10:.1f}' y='{ym + 4:.1f}' {FONT} "
                  f"font-size='12' font-weight='bold' fill='#333333'>"
                  f"{v:,} ({100 * v / total:.1f} %)</text>\n")
        if c == "available_full":
            s += (f"<text x='{cx - w / 2 - 12:.1f}' y='{ym + 4:.1f}' {FONT} "
                  f"font-size='12' text-anchor='end' "
                  f"fill='#333333'>{labels[c]}</text>\n")
        elif w >= 150:
            s += (f"<text x='{cx + w / 2 + 12:.1f}' y='{ym + 4:.1f}' {FONT} "
                  f"font-size='12' fill='#333333'>{labels[c]}</text>\n")
        else:
            val_w = 7.4 * len(f"{v:,} ({100 * v / total:.1f} %)")
            s += (f"<text x='{cx + w / 2 + 14 + val_w:.1f}' y='{ym + 4:.1f}' "
                  f"{FONT} font-size='12' fill='#333333'>{labels[c]}</text>\n")
        y += rh
    s += (f"<text x='30' y='{H - 42}' {FONT} font-size='12'>"
          f"available at work level: {avail:,} attestations = "
          f"{100 * avail / total:.1f} %</text>\n")
    s += (f"<text x='30' y='{H - 26}' {FONT} font-size='12'>"
          f"AOB edition rows (1,437): {aob['available_full']} full · "
          f"{aob['available_partial']} partial · "
          f"{aob.get('ambiguous_shared_siglum', 0)} ambiguous · "
          f"{aob['unresolved']} unresolved</text>\n")
    s += (f"<text x='30' y='{H - 10}' {FONT} font-size='11' fill='#555555'>"
          f"unresolved mass is not evidence of absence · source: "
          f"pd_edition_availability_by_siglum.tsv (C1 protocol)</text>\n")
    s += "</svg>\n"
    return s


def fig13(crosswalk, m):
    """Cat #8 — coverage slope 2021→2026 for the covered 118.

    Thin lines = per-title share of total DCS tokens (each year against its
    own denominator); bold line = pooled covered share 74.06 → 77.88 (pins).
    The three largest gains and losses are labeled.
    """
    t21 = m["total_dcs_tok_2021"]
    t26 = m["total_dcs_tok_2026"]
    shares = []
    for r in crosswalk:
        s21 = 100 * int(r["dcs_tok_2021"]) / t21
        s26 = 100 * int(r["dcs_tok_2026"]) / t26
        shares.append((r["dcs_title"], s21, s26))
    pooled = (m["metric_dcs_token_weighted_2021_pct"],
              m["metric_dcs_token_weighted_2026_pct"])
    W, H = 760, 460
    x0, x1 = 70, 500
    y0, y1 = 80, 390
    maxv = 80.0

    def yy(v):
        return y1 - (y1 - y0) * v / maxv

    s = svg_header(W, H, "Coverage slope 2021 to 2026, per covered title")
    s += (f"<text x='30' y='30' {FONT} font-size='15' font-weight='bold'>"
          f"The moving target: covered share of DCS climbs "
          f"{pooled[0]:.2f} % → {pooled[1]:.2f} %</text>\n")
    s += (f"<text x='30' y='50' {FONT} font-size='12' fill='#555555'>"
          f"thin lines = individual titles (share of each year's total DCS "
          f"tokens) · bold = pooled covered-118</text>\n")
    for gv in (0, 20, 40, 60, 80):
        y = yy(gv)
        s += (f"<line x1='{x0 - 10}' y1='{y:.1f}' x2='{x1 + 10}' y2='{y:.1f}' "
              f"stroke='#dddddd'/>\n")
        s += (f"<text x='{x0 - 16}' y='{y + 4:.1f}' {FONT} font-size='11' "
              f"text-anchor='end'>{gv} %</text>\n")
    for xv, yr in ((x0, "2021"), (x1, "2026")):
        s += (f"<text x='{xv}' y='{y0 - 18}' {FONT} font-size='13' "
              f"font-weight='bold' text-anchor='middle'>{yr}</text>\n")
    for _, s21, s26 in shares:
        s += (f"<line x1='{x0}' y1='{yy(s21):.1f}' x2='{x1}' y2='{yy(s26):.1f}' "
              f"stroke='#a8bbcc' stroke-width='0.8' opacity='0.5'/>\n")
    s += (f"<line x1='{x0}' y1='{yy(pooled[0]):.1f}' x2='{x1}' "
          f"y2='{yy(pooled[1]):.1f}' stroke='#b2182b' stroke-width='3'/>\n")
    for i, v in enumerate(pooled):
        xv = x0 if i == 0 else x1
        s += f"<circle cx='{xv}' cy='{yy(v):.1f}' r='5' fill='#b2182b'/>\n"
        s += (f"<text x='{xv + 14:.1f}' y='{yy(v) - 8:.1f}' "
              f"{FONT} font-size='13' font-weight='bold' "
              f"text-anchor='start'>{v:.2f} %</text>\n")
    deltas = sorted(shares, key=lambda t: t[2] - t[1])
    picks = deltas[:3] + deltas[-3:]
    # Dedicated label column right of the plot; leaders from the 2026 end;
    # >= 14 px vertical separation enforced.
    order_desc = sorted(picks, key=lambda t: -yy(t[2]))
    slots = {}
    prev = y1 + 4
    for title, s21, s26 in order_desc:
        ly = min(yy(s26), prev - 14)
        slots[title] = ly
        prev = ly
    for title, s21, s26 in picks:
        ly = slots[title]
        lbl = title if len(title) <= 24 else title[:23] + "…"
        s += (f"<circle cx='{x1}' cy='{yy(s26):.1f}' r='2.6' "
              f"fill='#2166ac'/>\n")
        s += (f"<line x1='{x1 + 4:.1f}' y1='{yy(s26):.1f}' "
              f"x2='{x1 + 22:.1f}' y2='{ly:.1f}' stroke='#2166ac' "
              f"stroke-width='0.7'/>\n")
        s += (f"<text x='{x1 + 26:.1f}' y='{ly + 3:.1f}' {FONT} "
              f"font-size='10' fill='#2166ac' text-anchor='start'>"
              f"{esc(lbl)}</text>\n")
    s += (f"<text x='30' y='{H - 8}' {FONT} font-size='11' fill='#555555'>"
          f"labels mark the three largest gains and three largest losses in "
          f"share of total DCS tokens</text>\n")
    s += "</svg>\n"
    return s


def fig14(crosswalk, m):
    """Cat #9 — corpus size vs dictionary attention (log-log scatter).

    x = DCS tokens 2026, y = PD citations, 118 covered titles; median
    crosshairs and quadrant readings.
    """
    pts = [(r["dcs_title"], int(r["dcs_tok_2026"]), int(r["pd_citations"]))
           for r in crosswalk]
    xs = sorted(p[1] for p in pts)
    ys = sorted(p[2] for p in pts)
    n = len(pts)
    medx = (xs[n // 2 - 1] + xs[n // 2]) / 2
    medy = (ys[n // 2 - 1] + ys[n // 2]) / 2
    W, H = 760, 470
    x0, x1 = 80, 700
    y0, y1 = 70, 400
    lx = (2.0, 7.0)
    ly = (0.0, 4.2)

    def xx(v):
        return x0 + (x1 - x0) * (math.log10(v) - lx[0]) / (lx[1] - lx[0])

    def yy(v):
        return y1 - (y1 - y0) * (math.log10(v) - ly[0]) / (ly[1] - ly[0])

    def tickfmt(e):
        return {0: "1", 1: "10", 2: "100", 3: "1k", 4: "10k", 5: "100k",
                6: "1M", 7: "10M"}.get(e, f"1e{e}")

    s = svg_header(W, H, "Corpus size vs dictionary attention, covered 118")
    s += (f"<text x='30' y='30' {FONT} font-size='15' font-weight='bold'>"
          f"Big corpora are not the cited ones: tokens vs PD citations</text>\n")
    s += (f"<text x='30' y='50' {FONT} font-size='12' fill='#555555'>"
          f"log-log · crosshairs = medians ({medx:,.0f} tok, {medy:,.0f} cites)</text>\n")
    for e in range(2, 8):
        x = xx(10 ** e)
        s += (f"<line x1='{x:.1f}' y1='{y0 - 6}' x2='{x:.1f}' y2='{y1}' "
              f"stroke='#eeeeee'/>\n")
        s += (f"<text x='{x:.1f}' y='{y1 + 18}' {FONT} font-size='11' "
              f"text-anchor='middle'>{tickfmt(e)}</text>\n")
    s += (f"<text x='{(x0 + x1) / 2:.0f}' y='{y1 + 38}' {FONT} font-size='12' "
          f"text-anchor='middle'>DCS tokens 2026</text>\n")
    for e in range(0, 5):
        y = yy(10 ** e)
        s += (f"<line x1='{x0}' y1='{y:.1f}' x2='{x1 + 6}' y2='{y:.1f}' "
              f"stroke='#eeeeee'/>\n")
        s += (f"<text x='{x0 - 8}' y='{y + 4:.1f}' {FONT} font-size='11' "
              f"text-anchor='end'>{tickfmt(e)}</text>\n")
    s += (f"<text x='{x0 - 46}' y='{(y0 + y1) / 2:.0f}' {FONT} font-size='12' "
          f"transform='rotate(-90 {x0 - 46} {(y0 + y1) / 2:.0f})' "
          f"text-anchor='middle'>PD citations</text>\n")
    s += (f"<line x1='{xx(medx):.1f}' y1='{y0}' x2='{xx(medx):.1f}' y2='{y1}' "
          f"stroke='#999999' stroke-dasharray='5 4'/>\n")
    s += (f"<line x1='{x0}' y1='{yy(medy):.1f}' x2='{x1}' y2='{yy(medy):.1f}' "
          f"stroke='#999999' stroke-dasharray='5 4'/>\n")
    for title, tok, cit in pts:
        s += (f"<circle cx='{xx(tok):.1f}' cy='{yy(cit):.1f}' r='3.4' "
              f"fill='#2166ac' opacity='0.65'/>\n")
    notable = [("Mahābhārata", 0, -12), ("Ṛgveda", 8, -10),
               ("Śatapathabrāhmaṇa", 8, 14), ("Rāmāyaṇa", 8, -4),
               ("Atharvaveda (Śaunaka)", 8, 6)]
    for title, dx, dy in notable:
        for t, tok, cit in pts:
            if t == title:
                s += (f"<text x='{xx(tok) + dx:.1f}' y='{yy(cit) + dy:.1f}' "
                      f"{FONT} font-size='10' fill='#333333'>"
                      f"{esc(title)}</text>\n")
                break
    s += (f"<text x='{x0 + 10}' y='{y0 + 10}' {FONT} font-size='11' "
          f"text-anchor='start' fill='#555555'>small corpus, heavy attention ↑</text>\n")
    s += (f"<text x='{x1 - 8}' y='{y1 - 8}' {FONT} font-size='11' "
          f"text-anchor='end' fill='#555555'>big corpus, light attention →</text>\n")
    s += (f"<text x='30' y='{H - 8}' {FONT} font-size='11' fill='#555555'>"
          f"n = {n} covered titles · log scales · the median crosshair splits "
          f"the covered canon four ways</text>\n")
    s += "</svg>\n"
    return s
