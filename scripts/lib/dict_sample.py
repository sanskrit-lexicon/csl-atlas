"""Deterministic stratified per-letter headword sampling (H1423 Wave A).

No RNG — uses a fixed stride per letter so re-runs are byte-identical (the
determinism rule). For a letter with n headwords and target t, takes every
ceil(n/t)-th headword, capped at t.
"""
import math


def stratified_sample(hw_list, base_letter_fn, per_letter=300):
    """Return [(letter, headword), ...] — up to `per_letter` per initial letter,
    evenly strided through that letter's headwords (deterministic)."""
    by_letter = {}
    for hw in hw_list:
        lb = base_letter_fn(hw)
        if lb is None:
            continue
        by_letter.setdefault(lb, []).append(hw)
    out = []
    for lb, words in by_letter.items():
        n = len(words)
        if n <= per_letter:
            picks = words
        else:
            stride = math.ceil(n / per_letter)
            picks = words[::stride][:per_letter]
        for w in picks:
            out.append((lb, w))
    return out
