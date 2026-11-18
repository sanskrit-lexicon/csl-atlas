"""Agreement primitives for the review-pool alpha report.

Split out of scripts/lexico/review_pool_kappa.py to stay inside the repo's
5 000-token file budget (Uprava tools/token_size_gate). Pure functions over
labels: no I/O, no repo paths.
"""
from __future__ import annotations

from collections import Counter, defaultdict

BOOTSTRAP_RESAMPLES = 2000


def landis_koch(alpha):
    if alpha is None:
        return None
    if alpha < 0:
        return "poor"
    if alpha < 0.20:
        return "slight"
    if alpha < 0.40:
        return "fair"
    if alpha < 0.60:
        return "moderate"
    if alpha < 0.80:
        return "substantial"
    return "almost-perfect"


def krippendorff_alpha_nominal(units):
    """units: list of list-of-labels, one list per row (>=1 keys per row).

    Standard nominal Krippendorff's alpha via the coincidence-matrix method
    (Hayes & Krippendorff 2007). Rows with fewer than 2 keys contribute no
    pairs and are silently excluded (they carry no disagreement information).
    Returns None when there is not enough pairable data, or when the expected
    disagreement is zero (every key falls in a single category -- alpha is
    undefined by the formula, not zero).
    """
    o = defaultdict(float)
    n_total = 0
    for labels in units:
        m = len(labels)
        if m < 2:
            continue
        counts = Counter(labels)
        denom = m - 1
        for c, n_c in counts.items():
            for k, n_k in counts.items():
                if c == k:
                    o[(c, k)] += n_c * (n_c - 1) / denom
                else:
                    o[(c, k)] += n_c * n_k / denom
        n_total += m
    if n_total < 2:
        return None
    categories = sorted({c for c, _ in o} | {k for _, k in o})
    n_c = {c: sum(o.get((c, k), 0.0) for k in categories) for c in categories}
    n = sum(n_c.values())
    if n < 2:
        return None
    diag = sum(o.get((c, c), 0.0) for c in categories)
    do_ = (n - diag) / n
    de_num = n * (n - 1) - sum(v * (v - 1) for v in n_c.values())
    de_ = de_num / (n * (n - 1))
    if de_ == 0:
        return None
    return 1.0 - do_ / de_


def bootstrap_ci(units, rng, resamples=BOOTSTRAP_RESAMPLES):
    """95% CI over rows for Krippendorff's alpha; None if the point estimate
    itself is undefined or too few rows carry >=2 keys to resample."""
    pairable = [u for u in units if len(u) >= 2]
    if len(pairable) < 2:
        return None
    samples = []
    n = len(pairable)
    for _ in range(resamples):
        draw = [pairable[rng.randrange(n)] for _ in range(n)]
        alpha = krippendorff_alpha_nominal(draw)
        if alpha is not None:
            samples.append(alpha)
    if len(samples) < resamples // 2:
        return None
    samples.sort()
    lo = samples[int(0.025 * len(samples))]
    hi = samples[min(len(samples) - 1, int(0.975 * len(samples)))]
    return [round(lo, 4), round(hi, 4)]
