"""The statistics: exact CIs, the permutation null, and the difference tests.

`pd_sense_order` is imported, not copied — its τ and its permutation-null design
are the identity this comparison rests on.
"""
from __future__ import annotations

import math
import random
import statistics
import sys

from .core import ROOT

if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
import pd_sense_order as sense  # noqa: E402

# ------------------------------------------------------------------ statistics
def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Exact (Clopper–Pearson) binomial CI by bisection on the binomial tails.

    lower: p with P[X ≥ k] = α/2 (increasing in p); upper: p with P[X ≤ k] = α/2
    (decreasing in p).  Verified against scipy.stats.beta.ppf in the unit checks.
    """
    if n == 0:
        return (0.0, 1.0)
    if k == 0:
        lo = 0.0
    else:
        lo, hi = 0.0, k / n
        for _ in range(120):
            mid = (lo + hi) / 2
            if 1.0 - _binom_cdf(k - 1, n, mid) < alpha / 2:
                lo = mid
            else:
                hi = mid
        lo = (lo + hi) / 2
    if k == n:
        hi = 1.0
    else:
        lo2, hi2 = k / n, 1.0
        for _ in range(120):
            mid = (lo2 + hi2) / 2
            if _binom_cdf(k, n, mid) > alpha / 2:
                lo2 = mid
            else:
                hi2 = mid
        hi = (lo2 + hi2) / 2
    return (lo, hi)


def _binom_cdf(k: int, n: int, p: float) -> float:
    """P[X ≤ k] for X ~ Binomial(n, p), summed from the largest term in range.

    Starting the recurrence at i = k underflows when k is far above the mean
    (a 6,000-trial CDF evaluated at p = 0.27 while the answer lives near 0.54),
    and the bisection then closes on the wrong bracket.  Summing outward from the
    mode (or from k, when k is below it) keeps every term representable.
    """
    if k < 0:
        return 0.0
    if k >= n or p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 0.0
    lp, lq = math.log(p), math.log1p(-p)

    def lpmf(i: int) -> float:
        return (math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
                + i * lp + (n - i) * lq)

    mode = min(max(int((n + 1) * p), 0), n)
    top = min(k, mode)
    term = math.exp(lpmf(top))
    total = term
    for i in range(top + 1, k + 1):          # up towards k
        term *= (n - i + 1) / i * math.exp(lp - lq)
        total += term
    term = math.exp(lpmf(top))
    for i in range(top - 1, -1, -1):         # down towards 0
        term *= (i + 1) / (n - i) * math.exp(lq - lp)
        total += term
    return min(1.0, total)


def per_entry_taus(series: dict[str, list[int]]) -> list[float]:
    return [sense.kendall_tau(list(range(len(s))), s)
            for s in series.values() if len(s) >= 3]


def fast_null(series: dict[str, list[int]], reps: int, seed: int) -> dict:
    """Within-entry permutation null, vectorised.

    Same design as `pd_sense_order.null_mean` — shuffle the sense dates inside one
    entry, recompute τ per entry, average — and the same quantile convention
    (`means[int(0.025 * len)]`).  The loop is vectorised because PWG root entries
    carry 200+ Bedeutungen: a pair-by-pair Python τ over 5,000 replicates would take
    hours.  τ between positions and dates reduces to counting pairwise comparisons,
    so one replicate is "shuffle within blocks, count a<b and a>b" — milliseconds in
    numpy.  Falls back to the stdlib implementation when numpy is absent (slow, same
    design).
    """
    try:
        import numpy as np
    except ImportError:                     # pragma: no cover - CI installs numpy
        return sense.null_mean(series, reps=reps)
    blocks = [np.asarray(s, dtype=np.int64) for s in series.values() if len(s) >= 3]
    if not blocks:
        return {"reps": reps, "mean_tau_null": 0.0, "p2_5": 0.0, "p97_5": 0.0, "impl": "numpy"}
    lengths = np.array([len(b) for b in blocks])
    block_id = np.repeat(np.arange(len(blocks)), lengths)
    vals = np.concatenate(blocks)
    ri, rj, off = [], [], 0
    for b in blocks:
        iu, ju = np.triu_indices(len(b), 1)
        ri.append(iu + off)
        rj.append(ju + off)
        off += len(b)
    pi, pj = np.concatenate(ri), np.concatenate(rj)
    # reduceat offsets are PAIR-block starts (n(n-1)/2 each), not value-block starts
    pair_lengths = lengths * (lengths - 1) // 2
    starts = np.concatenate(([0], np.cumsum(pair_lengths)[:-1]))
    rng = np.random.RandomState(seed)        # legacy stream: stable across numpy versions
    means = np.empty(reps)
    for r in range(reps):
        flat = vals[np.lexsort((rng.random(vals.size), block_id))]
        a, b = flat[pi], flat[pj]
        gt = np.add.reduceat((a > b).astype(np.int64), starts)
        lt = np.add.reduceat((a < b).astype(np.int64), starts)
        denom = lt + gt
        tau = np.where(denom > 0, (lt - gt) / np.maximum(denom, 1), 0.0)
        means[r] = tau.mean()
    means.sort()
    return {"reps": reps, "mean_tau_null": round(float(means.mean()), 10),
            "p2_5": round(float(means[int(0.025 * len(means))]), 10),
            "p97_5": round(float(means[int(0.975 * len(means))]), 10),
            "impl": "numpy"}


def summarise(series: dict[str, list[int]], reps: int) -> dict:
    pairs = [s for s in series.values() if len(s) == 2]
    later = sum(1 for a, b in pairs if b > a)
    ties = sum(1 for a, b in pairs if a == b)
    backward = sum(1 for a, b in pairs if b < a)
    taus = per_entry_taus(series)
    shifts = [s[-1] - s[0] for s in series.values() if len(s) >= 2]
    lo, hi = clopper_pearson(later, len(pairs)) if pairs else (None, None)
    return {
        "entries_with_series": len(series),
        "entries_two_senses": len(pairs),
        "two_sense_later_sense_later_date": later,
        "two_sense_ties": ties,
        "two_sense_backward": backward,
        "two_sense_forward_rate": round(later / len(pairs), 10) if pairs else None,
        "two_sense_forward_rate_ci95": [round(lo, 6), round(hi, 6)] if pairs else None,
        "entries_three_plus_senses": len(taus),
        "mean_tau_position_vs_earliest": round(sum(taus) / len(taus), 10) if taus else None,
        "median_last_minus_first_years": statistics.median(shifts) if shifts else None,
        "tau_by_size": _tau_by_size(series),
        "null": fast_null(series, reps, sense.SEED),
    }


def _tau_by_size(series: dict[str, list[int]]) -> dict:
    """τ split by entry size — keeps a handful of 100+-sense root entries from
    silently carrying (or hiding) the tendency."""
    small = [sense.kendall_tau(list(range(len(s))), s)
             for s in series.values() if 3 <= len(s) <= 7]
    large = [sense.kendall_tau(list(range(len(s))), s)
             for s in series.values() if len(s) >= 8]
    return {
        "3_to_7": {"entries": len(small),
                   "mean_tau": round(sum(small) / len(small), 10) if small else None},
        "8_plus": {"entries": len(large),
                   "mean_tau": round(sum(large) / len(large), 10) if large else None},
    }


def permutation_diff(pd_taus: list[float], ctl_taus: list[float], reps: int, seed: int) -> dict:
    """One-sided permutation test of mean(PD) − mean(control) > 0 under relabelling."""
    n_pd, n_ctl = len(pd_taus), len(ctl_taus)
    if not n_pd or not n_ctl:
        return {"reps": 0, "observed_diff": None, "p_one_sided": None}
    observed = sum(pd_taus) / n_pd - sum(ctl_taus) / n_ctl
    pooled = list(pd_taus) + list(ctl_taus)
    rng = random.Random(seed)
    hits = 0
    for _ in range(reps):
        rng.shuffle(pooled)
        diff = sum(pooled[:n_pd]) / n_pd - sum(pooled[n_pd:]) / n_ctl
        if diff >= observed - 1e-12:
            hits += 1
    return {"reps": reps, "observed_diff": round(observed, 10),
            "p_one_sided": round((1 + hits) / (reps + 1), 10)}


def bootstrap_diff(pd_taus: list[float], ctl_taus: list[float], reps: int, seed: int) -> list[float] | None:
    if not pd_taus or not ctl_taus:
        return None
    rng = random.Random(seed)
    diffs = []
    for _ in range(reps):
        a = [rng.choice(pd_taus) for _ in pd_taus]
        b = [rng.choice(ctl_taus) for _ in ctl_taus]
        diffs.append(sum(a) / len(a) - sum(b) / len(b))
    diffs.sort()
    return [round(diffs[int(0.025 * (len(diffs) - 1))], 6),
            round(diffs[int(0.975 * (len(diffs) - 1))], 6)]


def holm(pvals: dict[str, float]) -> dict[str, float]:
    """Holm step-down adjusted p-values."""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    out: dict[str, float] = {}
    running = 0.0
    for i, (name, p) in enumerate(items):
        adj = min(1.0, (m - i) * p)
        running = max(running, adj)
        out[name] = round(running, 10)
    return out

