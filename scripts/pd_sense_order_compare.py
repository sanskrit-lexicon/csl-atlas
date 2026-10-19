#!/usr/bin/env python3
"""The sense-order control: PD vs PWG, PW, MW and AP (H7116).

Thin CLI over `scripts/pd_compare/` (the package was split out to satisfy the
repo's token-size gate; the measurement lives there).  Usage and the full
pre-registered verdict rule are in the package docstring:

    python scripts/pd_sense_order_compare.py --build
    python scripts/pd_sense_order_compare.py --check
    python scripts/pd_sense_order_compare.py --render
"""
from __future__ import annotations

import argparse
import json
import sys

from pd_compare.core import *            # noqa: F401,F403 - paths + constants + sha256
from pd_compare.measure import *         # noqa: F401,F403 - pd_series_and_taus / control_series / evaluate
from pd_compare.report import *          # noqa: F401,F403 - render_report
from pd_compare.stats import sense       # REPS / SEED, the canonical permutation budget

# ------------------------------------------------------------------ main
def build(reps: int) -> dict:
    print("loading date instruments and abbreviation keys…", file=sys.stderr)
    date_tables = {"dcs": load_dcs(), "dm": load_dm()}
    tables = load_abbrev_tables()
    print(f"  DCS texts {len(date_tables['dcs'])}, Dharmamitra works {len(date_tables['dm'])}; "
          f"abbreviation keys: " + ", ".join(f"{c}:{len(tables.get(c, {}))}" for c in DICTS), file=sys.stderr)

    print("PD side (canary against the committed summary)…", file=sys.stderr)
    pd_clocks, pd_taus = pd_series_and_taus(reps)
    print(f"  PD τ dm {pd_clocks['dm']['mean_tau_position_vs_earliest']:+.3f} "
          f"(n={pd_clocks['dm']['entries_three_plus_senses']:,}), "
          f"dcs {pd_clocks['dcs']['mean_tau_position_vs_earliest']:+.3f} "
          f"(n={pd_clocks['dcs']['entries_three_plus_senses']:,}) — canary OK", file=sys.stderr)

    print("control side (parsing csl-orig)…", file=sys.stderr)
    controls = {}
    for code in DICTS:
        controls[code] = control_series(code, make_resolver(tables.get(code, {})), date_tables, reps)

    verdict = evaluate({"taus": pd_taus}, controls, reps)
    summary = {
        "handoff": HANDOFF,
        "generated": REPORT_DATE,
        "unit": "earliest datable citation per sense division, in sense order",
        "clocks": list(CLOCKS),
        "primary_clock": PRIMARY_CLOCK,
        "rule": {"effect_floor": EFFECT_FLOOR, "alpha": ALPHA, "min_power": MIN_POWER,
                 "reps": reps, "seed": sense.SEED, "holm": True,
                 "source": "pre-registered in scripts/pd_sense_order_compare.py header"},
        "pd_clocks": pd_clocks,
        "controls": controls,
        "verdict": {"status": verdict["status"], "text": verdict["text"], "rows": verdict["rows"],
                    "scored": verdict["scored"]},
        "inputs": {
            "csl_orig": str(CSL_ORIG),
            "guides_abbreviations_sha256": sha256(GUIDES_ABBR),
            "mw_abbreviations_sha256": sha256(MW_ABBR),
            "dcs_texts_sha256": sha256(DCS_JSON),
            "dharmamitra_sha256": sha256(DM_JSON),
            "pd_tsv_sha256": sha256(PD_TSV),
        },
    }
    return summary


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--build", action="store_true", help="write the summary JSON and report")
    ap.add_argument("--check", action="store_true", help="recompute and compare with the committed summary")
    ap.add_argument("--reps", type=int, default=sense.REPS, help=f"permutation reps (default {sense.REPS})")
    ap.add_argument("--render", action="store_true", help="re-render the report from the committed summary")
    args = ap.parse_args(argv)
    if args.render:
        summary = json.loads(OUT_JSON.read_text(encoding="utf-8"))
        REPORT.write_text(render_report(summary), encoding="utf-8")
        print(f"re-rendered {REPORT.relative_to(ROOT)} from the committed summary", file=sys.stderr)
        return 0
    if not (args.build or args.check):
        ap.error("choose --build, --check or --render")
    if args.reps != sense.REPS:
        print(f"! NON-CANONICAL --reps {args.reps}: smoke run, never commit", file=sys.stderr)
    summary = build(args.reps)
    text = json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
    if args.build:
        OUT_JSON.write_text(text, encoding="utf-8")
        REPORT.write_text(render_report(summary), encoding="utf-8")
        print(f"wrote {OUT_JSON.relative_to(ROOT)} and {REPORT.relative_to(ROOT)}", file=sys.stderr)
        print(summary["verdict"]["text"], file=sys.stderr)
        return 0
    if not OUT_JSON.exists():
        print("FAIL: no committed compare summary to check against", file=sys.stderr)
        return 1
    committed = OUT_JSON.read_text(encoding="utf-8")
    if committed != text:
        got, want = json.loads(text), json.loads(committed)
        for code in ("verdict", "pd_clocks", "controls"):
            if got[code] != want[code]:
                print(f"FAIL: {code} does not reproduce", file=sys.stderr)
                return 1
        print("FAIL: committed summary does not reproduce byte-for-byte", file=sys.stderr)
        return 1
    print("OK: compare summary reproduces", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
