#!/usr/bin/env python3
"""H7616 anti-slop gate — WCAG AA conviction arithmetic for fig7/fig10 text.

A contrast Floor verdict requires a computed WCAG ratio, not an eyeball
(A68_ANTI_SLOP_FIGURE_GATE_2026-11-01.md §3). This script is that
calculation: it prints the ratio for every text/background pair the two
canonical figures actually draw and exits non-zero if any pair misses
4.5:1. Run it next to build_a68_figures.py; a fix that fails here has no
business being re-judged.
"""


def _lum(hexcolor):
    r, g, b = (int(hexcolor[i:i + 2], 16) / 255.0 for i in (1, 3, 5))
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
           for c in (r, g, b)]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def ratio(fg, bg="#FFFFFF"):
    l1, l2 = sorted((_lum(fg), _lum(bg)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


# (figure, role, foreground, background) — the pairs the fixed figures draw.
PAIRS = [
    ("fig7", "title #333333 on white", "#333333", "#FFFFFF"),
    ("fig7", "subtitle #555555 on white", "#555555", "#FFFFFF"),
    ("fig7", "ticks/sublabels/source #666666 on white (was #888888 3.55)",
     "#666666", "#FFFFFF"),
    ("fig7", "value digits #333333 on white", "#333333", "#FFFFFF"),
    ("fig10", "row labels/legend #333333 on white", "#333333", "#FFFFFF"),
    ("fig10", "subtitle #555555 on white", "#555555", "#FFFFFF"),
    ("fig10", "source #666666 on white (was #888888 3.55)", "#666666",
     "#FFFFFF"),
    ("fig10", "in-bar % black on Vedic #DB444B (white was 4.25 FAIL)",
     "#000000", "#DB444B"),
    ("fig10", "in-bar % white on śāstra #006BA2", "#FFFFFF", "#006BA2"),
    ("fig10", "in-bar % black on epic #F0AB00", "#000000", "#F0AB00"),
    ("fig10", "in-bar % black on kāvya #3EBCD2", "#000000", "#3EBCD2"),
    ("fig10", "in-bar % black on purāṇic #379A8B", "#000000", "#379A8B"),
    ("fig10", "in-bar % black on other #B4BA39", "#000000", "#B4BA39"),
    # fig10-canon pass (H7641): the pairs the three restyled figures draw.
    ("fig7", "in-bar value white on #006BA2", "#FFFFFF", "#006BA2"),
    ("fig7", "in-bar value black on #DB444B (white would be 4.25 FAIL)",
     "#000000", "#DB444B"),
    ("fig7", "bold row labels #333333 on white", "#333333", "#FFFFFF"),
    ("fig4", "in-bar value white on #2166ac", "#FFFFFF", "#2166ac"),
    ("fig4", "bold row labels #333333 on white", "#333333", "#FFFFFF"),
    ("fig4", "legend/row text #333333 on white", "#333333", "#FFFFFF"),
    ("fig15", "bold row labels #333333 on white", "#333333", "#FFFFFF"),
    ("fig15", "value tspan #333333 on white", "#333333", "#FFFFFF"),
    ("fig15", "pooled label bold #333333 on white", "#333333", "#FFFFFF"),
]


def main():
    worst = 99.0
    for fig, role, fg, bg in PAIRS:
        r = ratio(fg, bg)
        worst = min(worst, r if not role.startswith("cand") else 99.0)
        verdict = "PASS" if r >= 4.5 else "FAIL"
        print(f"{verdict}  {r:6.2f}:1  {fig:5s}  {role}")
    print(f"worst drawn pair: {worst:.2f}:1 (AA floor 4.50:1)")
    return 0 if worst >= 4.5 else 1


if __name__ == "__main__":
    raise SystemExit(main())
