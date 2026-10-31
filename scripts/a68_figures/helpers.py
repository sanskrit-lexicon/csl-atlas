"""Shared constants, cross-check helpers and SVG primitives."""
import csv
import json
import math
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
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
SANS = "font-family='Helvetica, Arial, sans-serif'"

# C4 layer table — verbatim from the committed sweep
# Uprava/papers/A68/sweeps/2026-10-14-C4-renou-layers-dcs276.md (H6698/C4,
# 14-10-2026). tok = tokens at the 2026 snapshot (all-276); cov = covered-118
# subset; cit = PD citations over the covered-118. The sweep publishes NO
# per-layer covered-tok-2021 column — none is invented here. The aggregate
# rows of the sweep (Vedic+epic 44.0 %, classical 52.0 %) are recomputed
# below from these six rows and cross-checked, never trusted as literals.
# The sweep prose quotes the covered Vedic+epic share as 53.1 %; the exact
# value from these committed columns is 53.05 % (rounds to 53.0) — figures
# show the re-derived value.
C4_LAYERS = [
    # layer, texts@2026, tok2026, tok2021, cov texts, cov tok2026, PD cit
    ("Vedic",    38,  920029,  378782, 22,  854611, 21513),
    ("epic",      4, 1581085, 1492450,  3, 1495430, 13145),
    ("śāstra",  174, 1802358, 1436108, 67, 1070077, 34732),
    ("kāvya",    26,  423207,  342285, 14,  361244,  7156),
    ("purāṇic",  16,  733553,  732968,  9,  524083, 11964),
    ("other",    18,  228184,  195320,  3,  124666,   419),
]
# Ladder step 3 is a claim-ledger pin, not a metrics-JSON field:
#   P-adjudicated 123,453 — "primary occurrences in hand-adjudicated primary
#   rows" (Uprava papers/A68/A68_CLAIM_LEDGER.tsv; iscls.tex §5.2.1 table:
#   164 hand-adjudicated primary titles). Pinned, zero tolerance.
PIN_ADJUDICATED = 123453


def ladder(m):
    """The four §5.2.1 denominators, top rung first (pin = claim-ledger).

    Shared by the canonical fig7 and the fig7 style studies.
    """
    return [
        ("All siglum occurrences", m["total_siglum_mass"], ""),
        ("Primary work occurrences", m["primary_work_mass"], ""),
        ("Hand-adjudicated primary", PIN_ADJUDICATED, "pin"),
        ("Covered by DCS (118 works)", m["covered_mass"], ""),
    ]


def read_tsv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def check(name, derived, committed, tol=0.0):
    ok = abs(derived - committed) <= tol
    status = "OK " if ok else "FAIL"
    print(f"  [{status}] {name}: derived={derived} committed={committed}")
    return ok


def wilson(k, n, z=1.96):
    """Wilson score interval for k successes of n, as (lo, hi) in percent."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (100 * max(0.0, centre - half), 100 * min(1.0, centre + half))


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg_header(w, h, title):
    return (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' "
        f"viewBox='0 0 {w} {h}'>\n"
        f"<title>{title}</title>\n"
        f"<rect width='{w}' height='{h}' fill='white'/>\n"
    )



