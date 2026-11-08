"""The two measured sides: the PD canary and the per-dictionary control series."""
from __future__ import annotations

import json
import sys
import time

from .core import *                     # noqa: F401,F403 - constants + helpers
from .corpus import *                   # noqa: F401,F403 - record/sense segmentation
from .stats import *                    # noqa: F401,F403 - CI / null / difference tests
from .stats import _tau_by_size        # private name: star-import skips it
from .stats import sense                # the PD statistic, imported not copied
from .core import CLOCKS, DICTS, PD_JSON, PD_TSV

# ------------------------------------------------------------------ PD side (canary)
def pd_series_and_taus(reps: int) -> tuple[dict, dict]:
    """Recompute the PD row with pd_sense_order and refuse on any drift.

    The counts and both τ values are compared on every run; the null band is the
    committed published band under the canonical 5,000 reps (a smoke run with
    `--reps 200` computes its own cheap band and is never committed).
    """
    import csv
    with PD_TSV.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    committed = json.loads(PD_JSON.read_text(encoding="utf-8"))
    clocks, series = {}, {}
    for clock in CLOCKS:
        series[clock] = sense.entry_series(rows, clock)
        got = sense.summarise(series[clock])
        got.pop("shifts", None)
        want = committed["clocks"][clock]
        for key in ("entries_with_series", "entries_two_senses", "two_sense_later_sense_later_date",
                    "two_sense_ties", "two_sense_backward", "entries_three_plus_senses"):
            if got[key] != want[key]:
                raise SystemExit(f"CANARY FAIL {clock}.{key}: {got[key]} != {want[key]}")
        for key in ("two_sense_forward_rate", "mean_tau_position_vs_earliest",
                    "median_last_minus_first_years"):
            if got[key] is None or want[key] is None:
                if got[key] != want[key]:
                    raise SystemExit(f"CANARY FAIL {clock}.{key}: {got[key]} != {want[key]}")
            elif abs(got[key] - want[key]) > 1e-9:
                raise SystemExit(f"CANARY FAIL {clock}.{key}: {got[key]} != {want[key]}")
        if reps == sense.REPS:
            # PD's published null band is the committed one (same design, stdlib
            # stream).  Its own 5,000-replicate recomputation costs minutes and has
            # already been verified by `pd_sense_order.py --check`; a band is a
            # sanity interval, not a verdict input, so the published band is quoted.
            got["null"] = dict(want["null"])
        else:
            got["null"] = fast_null(series[clock], reps, sense.SEED)
        got["tau_by_size"] = _tau_by_size(series[clock])
        clocks[clock] = got
    taus = {clock: per_entry_taus(series[clock]) for clock in CLOCKS}
    return clocks, taus


# ------------------------------------------------------------------ control side
def control_series(code: str, resolve, date_tables: dict[str, dict[str, int]],
                   reps: int) -> dict:
    path = CSL_ORIG / code / f"{code}.txt"
    if not path.exists():
        raise SystemExit(f"missing corpus: {path}")
    years: dict[str, tuple] = {}

    def dated(node: str):
        if node not in years:
            years[node] = tuple(
                (best_match(node, date_tables[c], DICE[c]) or (None, 0.0))[0] for c in CLOCKS)
        return years[node]

    series: dict[str, dict[str, list[int]]] = {c: {} for c in CLOCKS}
    stats = {"records": 0, "entries": 0, "sense_divisions": 0,
             "ls_instances": 0, "ls_resolved": 0,
             "dated_instances": {c: 0 for c in CLOCKS},
             "resolved_texts": set()}
    t0 = time.time()
    for header, body in iter_records(path):
        stats["records"] += 1
        key = entry_key(code, header)
        stats["entries"] += 1 if key else 0
        for chunk in sense_chunks(code, body):
            keys = LS.findall(chunk)
            if not keys:
                continue
            stats["sense_divisions"] += 1
            by_clock: dict[str, list[int]] = {c: [] for c in CLOCKS}
            for raw in keys:
                stats["ls_instances"] += 1
                node = resolve(raw)
                if not node:
                    continue
                stats["ls_resolved"] += 1
                stats["resolved_texts"].add(node)
                y_dcs, y_dm = dated(node)
                if y_dcs is not None:
                    by_clock["dcs"].append(y_dcs)
                    stats["dated_instances"]["dcs"] += 1
                if y_dm is not None:
                    by_clock["dm"].append(y_dm)
                    stats["dated_instances"]["dm"] += 1
            for clock in CLOCKS:
                if by_clock[clock]:
                    series[clock].setdefault(key, []).append(min(by_clock[clock]))
    stats["resolved_texts"] = len(stats["resolved_texts"])
    print(f"  {code}: {stats['records']:,} records, {stats['sense_divisions']:,} sense divisions "
          f"with citations, {stats['ls_resolved']:,}/{stats['ls_instances']:,} <ls> resolved "
          f"({100 * stats['ls_resolved'] / max(stats['ls_instances'], 1):.1f}%), "
          f"{stats['resolved_texts']} distinct texts ({time.time() - t0:.1f}s)", file=sys.stderr)
    return {"stats": stats,
            "clocks": {c: summarise(series[c], reps) for c in CLOCKS},
            "taus": {c: per_entry_taus(series[c]) for c in CLOCKS}}


# ------------------------------------------------------------------ verdict
def evaluate(pd: dict, controls: dict, reps: int) -> dict:
    rows = {}
    pvals = {}
    for code in DICTS:
        ctl = controls[code]
        row = {"entries_three_plus_senses": ctl["clocks"][PRIMARY_CLOCK]["entries_three_plus_senses"]}
        if row["entries_three_plus_senses"] >= MIN_POWER:
            test = permutation_diff(pd["taus"][PRIMARY_CLOCK], ctl["taus"][PRIMARY_CLOCK], reps, sense.SEED)
            row["delta_tau"] = test["observed_diff"]
            row["p_one_sided"] = test["p_one_sided"]
            row["delta_tau_ci95"] = bootstrap_diff(pd["taus"][PRIMARY_CLOCK],
                                                   ctl["taus"][PRIMARY_CLOCK], reps, sense.SEED)
            pvals[code] = test["p_one_sided"]
        else:
            row.update({"delta_tau": None, "p_one_sided": None, "delta_tau_ci95": None})
        rows[code] = row
    adj = holm(pvals)
    for code, p in adj.items():
        rows[code]["p_holm"] = p
    for code in DICTS:
        rows[code].setdefault("p_holm", None)
        r = rows[code]
        r["clears_floor"] = bool(r["delta_tau"] is not None and r["delta_tau"] >= EFFECT_FLOOR)
        r["clears_alpha"] = bool(r["p_holm"] is not None and r["p_holm"] <= ALPHA)
    scored = [c for c in DICTS if rows[c]["delta_tau"] is not None]
    if len(scored) < 2:
        status = "INCONCLUSIVE"
        text = (f"INCONCLUSIVE — {len(scored)} dictionary(ies) carry ≥{MIN_POWER} entries with "
                f"≥3 datable senses, fewer than the pre-registered two; the instrument cannot "
                f"see the control, so the A68 footnote is unchanged and no trend is claimed.")
    elif all(rows[c]["clears_floor"] and rows[c]["clears_alpha"] for c in scored):
        status = "STAND"
        worst = min(scored, key=lambda c: rows[c]["delta_tau"])
        text = (f"STAND — PD keeps a chronological sense-order tendency no tested non-historical "
                f"dictionary matches: the smallest gap is Δτ = {rows[worst]['delta_tau']:+.3f} "
                f"against {worst.upper()} (Holm p = {rows[worst]['p_holm']:.4f}, floor +{EFFECT_FLOOR:.2f}).")
    else:
        status = "WITHDRAWN"
        fails = [c for c in scored if not (rows[c]["clears_floor"] and rows[c]["clears_alpha"])]
        f = fails[0]
        text = (f"WITHDRAWN — the claim that PD's chronological sense ordering is distinctive is "
                f"withdrawn: {', '.join(c.upper() for c in fails)} fail(s) the pre-registered floor "
                f"(worst Δτ = {rows[f]['delta_tau']:+.3f}, Holm p = {rows[f]['p_holm']:.4f} against "
                f"a floor of +{EFFECT_FLOOR:.2f}); the tendency is shared with non-historical "
                f"dictionaries and the A68 footnote must say so.")
    return {"status": status, "text": text, "rows": rows, "scored": scored}

