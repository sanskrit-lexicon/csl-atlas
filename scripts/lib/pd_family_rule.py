#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7110 — the PD family-composition rule (compound / derivative / simplex).

The rule, the source readers and the shared constants, extracted from
``scripts/pd_family_composition.py`` so the CLI and the rule each fit the repo's
per-file token budget. Re-deriving a class needs nothing outside this module.

Rule (full derivation: reports/PD_FAMILY_COMPOSITION_2026.md):

1. POPULATION — every unique ``<k1>`` for which at least one entry prints
   ``<k1>`` == ``<k2>`` and carries an analysis parenthesis (103,127 headwords,
   of which 380 carry a CORRECTIONS block rather than an analysis).
2. ANALYSIS — the first ``( … )`` after the ``¦`` separator on the entry's first
   body line.
3. MEMBERS — Unicode NFD, strip U+0301/U+0300, ``°`` and apostrophes, NFC again;
   split on hyphen / en-dash / em-dash / whitespace.
4. CLASS — one member => SIMPLEX; last member in ``SUFFIXES`` => DERIVATIVE;
   otherwise => COMPOUND.

Stdlib only; no network; deterministic.
"""

from __future__ import annotations

import hashlib
import os
import re
import unicodedata
from collections import Counter, OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))      # scripts/lib
ROOT = os.path.dirname(os.path.dirname(HERE))          # repo root
# A session worktree lives under <estate>/worktrees/<name>, one level deeper than
# the repos it reads as siblings; fall back to the estate root when the sibling
# clone is not where the worktree expects it.
GH = os.path.dirname(ROOT)
if not os.path.isdir(os.path.join(GH, "csl-orig")):
    _alt = os.path.expanduser(os.path.join("~", "Documents", "GitHub"))
    if os.path.isdir(os.path.join(_alt, "csl-orig")):
        GH = _alt
HEADWORD_LISTS = os.path.join(GH, "SanskritLexicography", "HeadwordLists", "now-2026")

# Pinned source identity (H6942 / H6949 lineage; reproduced 19-10-2026 for H7110).
PD_SHA256 = "4ee75e6619ee2bd86a331586bb922101e0ae090f9edd981752cfac36ed724442"
PD_BYTES = 55122076
PD_ENTRIES = 107620
PWG_SHA256 = "f2c8bcc9d1c1f3d3c1e0d0a3b7f9ff13b0b1d5a4cbdbe2c0df73d7fb1c2e9a0d"
PWG_ENTRIES_MIN = 120000

# Pins the A68 draft quoted; --check refuses when the rebuild leaves the ±band.
POPULATION_PIN = 103127          # unique headwords with a printed analysis
POPULATION_BAND = 6              # parser-level tolerance (draft vs re-derivation)
PRIVATIVE_PIN = 8900             # draft: 4,420 a- + 4,480 an-
PRIVATIVE_BAND = 0.02            # ±2 % of the pinned value
THRESHOLD_PP = 15.0

# Frequent kṛt / taddhita suffixes in IAST, the published derivative test.
SUFFIXES = OrderedDict(
    (s, 1)
    for s in (
        "ka", "tva", "tā", "tara", "tama", "maya", "aka", "ana", "ita",
        "in", "mat", "vat", "tṛ", "tas", "ya",
    )
)

# Family specifications. kind: string (prefix string) | morph (analysis-based).
RE_SHA = re.compile(r"^[0-9a-f]{64}$")
RE_HDR = re.compile(r"^<L>(\d+)<pc>([^<]*)<k1>([^<\s]*)<k2>([^<\s]*)")
RE_ANALYSIS = re.compile(r"¦\s*\(([^)]{0,200})\)")
RE_BLOCK = re.compile(r"(?m)^(?=<L>)")
RE_PWG = re.compile(r"^<L>(\d+)<pc>([^<]*)<k1>([^<\s]*)", re.M)
ACCENTS = {"\u0301": "", "\u0300": "", "°": "", "'": "", "’": ""}


# --------------------------------------------------------------- source reading
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def first_line_paren(block):
    """Return (paren-content, is_correction_block) for the entry's first body line.

    PD prints one parenthesis right after the ``¦`` separator. It is normally the
    compound analysis (``(anna-ka)``). A minority of entries carry a CORRECTIONS
    block there instead — ``({{old->new|date|editor|url}})`` — which is an errata
    insertion, not an analysis, and is reported separately rather than classified.
    """
    lines = block.split("\n", 2)
    seg = lines[1].split("<div", 1)[0] if len(lines) > 1 else ""
    m = RE_ANALYSIS.search(seg)
    if not m:
        return None, False
    a = m.group(1).strip()
    if not a:
        return None, False
    if a.startswith("{{") or "->" in a:
        return None, True
    return a, False


def parse_pd(path):
    """Return (headwords, entries, unique_k1, correction_blocks).

    headwords         — unique k1 → analysis, for k1 that print k1 == k2 somewhere
    entries           — every <L> entry as (k1, k2, analysis-or-None)
    correction_blocks — unique k1 whose only first-line parenthesis is a CORRECTIONS block
    """
    text = open(path, encoding="utf-8", errors="replace").read()
    blocks = RE_BLOCK.split(text)
    headwords = {}
    entries = []
    unique_k1 = set()
    corrections = set()
    for b in blocks:
        m = RE_HDR.match(b)
        if not m:
            continue
        k1, k2 = m.group(3), m.group(4)
        unique_k1.add(k1)
        a, is_corr = first_line_paren(b)
        entries.append((k1, k2, a))
        if k1 in headwords:
            continue
        if k1 == k2 and a:
            headwords[k1] = a
        elif k1 == k2 and is_corr:
            corrections.add(k1)
    # a headword that yields an analysis somewhere is not a correction-only row
    corrections -= set(headwords)
    return headwords, entries, unique_k1, corrections


def parse_pwg(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    return {m.group(3) for m in RE_PWG.finditer(text)}


def headword_list(name):
    path = os.path.join(HEADWORD_LISTS, name)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return [ln.strip() for ln in fh if ln.strip()]


# ------------------------------------------------------------------- the rule
def members(analysis):
    # PD prints Vedic accents either precomposed or as combining marks; NFD+strip
    # handles both, so the class never depends on how the source encodes "á".
    a = unicodedata.normalize("NFD", analysis)
    for src, dst in ACCENTS.items():
        a = a.replace(src, dst)
    # recompose macrons/dots so the suffix comparison sees "tā", not "ta"+U+0304
    a = unicodedata.normalize("NFC", a)
    return [x for x in re.split(r"[-–—\s]+", a.strip()) if x]


def members_literal(analysis):
    """Split without accent normalisation — the A68 draft's literal prefix test."""
    for src, dst in ACCENTS.items():
        analysis = analysis.replace(src, dst)
    return [x for x in re.split(r"[-–—\s]+", analysis.strip()) if x]


def classify(analysis):
    """compound | derivative | simplex | None."""
    ms = members(analysis)
    if not ms:
        return None
    if len(ms) == 1:
        return "simplex"
    return "derivative" if ms[-1].lower() in SUFFIXES else "compound"


def family_keys(kind, token, headwords):
    if kind == "string":
        return sorted(k for k in headwords if k.startswith(token))
    # morphological: first analysis member is the token (a- / an-)
    out = []
    for k in sorted(headwords):
        ms = members(headwords[k])
        if ms and ms[0].lower() == token:
            out.append(k)
    return out


def family_row(name, kind, token, role, headwords, pwg_set, all_k1):
    keys = family_keys(kind, token, headwords)
    if kind == "string":
        # reported n is the whole string family (A68's convention); the shares
        # below are computed over the classified subset only
        n_all = sum(1 for k in all_k1 if k.startswith(token))
    else:
        n_all = len(keys)
    classes = Counter()
    examples = {"compound": [], "derivative": [], "simplex": []}
    unclassified = 0
    for k in keys:
        c = classify(headwords[k])
        if c is None:
            unclassified += 1
            continue
        classes[c] += 1
        if len(examples[c]) < 5:
            examples[c].append(k)
    n = sum(classes.values())
    shares = OrderedDict(
        (c, round(100.0 * classes[c] / n, 1) if n else 0.0)
        for c in ("compound", "derivative", "simplex")
    )
    if kind == "string":
        pwg_n = sum(1 for w in pwg_set if w.startswith(token))
    else:
        pwg_n = "n/a"  # PWG prints no analysis parenthesis: not computable
    return OrderedDict(
        family=name,
        kind=kind,
        role=role,
        token=token,
        pd_headwords=n_all,
        pwg_headwords=pwg_n,
        classified=n,
        compound_n=classes["compound"],
        derivative_n=classes["derivative"],
        simplex_n=classes["simplex"],
        compound_pct=shares["compound"],
        derivative_pct=shares["derivative"],
        simplex_pct=shares["simplex"],
        unclassified=unclassified,
        examples=examples,
    )


def privative_recount(entries, unique_k1):
    """Entry-level count of analyses beginning a- / an-, strict and loose.

    STRICT counts an entry only when the analysis has a second member — a
    privative/negative formation is ``a-``/``an-`` PLUS a base; a single-member
    ``(a)`` or ``(an)`` is the letter itself, not a privative.
    LOOSE counts every entry whose analysis begins with the prefix.
    """
    strict = {"a": 0, "an": 0}
    loose = {"a": 0, "an": 0}
    literal = {"a": 0, "an": 0}
    uniq = {"a": set(), "an": set()}
    for k1, _k2, a in entries:
        if not a:
            continue
        ms = members(a)
        if not ms:
            continue
        first = ms[0].lower()
        if first not in strict:
            continue
        loose[first] += 1
        if len(ms) >= 2:
            strict[first] += 1
            uniq[first].add(k1)
        lms = members_literal(a)
        if lms and lms[0].lower() == first and len(lms) >= 2:
            literal[first] += 1
    return {
        "entries_a": strict["a"],
        "entries_an": strict["an"],
        "entries_total": strict["a"] + strict["an"],
        "loose_a": loose["a"],
        "loose_an": loose["an"],
        "loose_total": loose["a"] + loose["an"],
        "literal_a": literal["a"],
        "literal_an": literal["an"],
        "literal_total": literal["a"] + literal["an"],
        "unique_a": len(uniq["a"]),
        "unique_an": len(uniq["an"]),
        "unique_total": len(uniq["a"] | uniq["an"]),
        "share_of_population_pct": None,  # filled by caller
    }


def density(priv_total, priv_literal):
    """23.2× and the without-privatives multiple, recomputed from committed lists."""
    pd_list = headword_list("PD-unique-key1-104959.txt")
    pwg_list = headword_list("PWG-unique-key1-106082.txt")
    if not pd_list or not pwg_list:
        return None
    try:
        frontier = pwg_list.index("apaca") + 1   # Sanskrit-collated line number
    except ValueError:
        return None
    pd_lemmas = len(pd_list)
    with_p = round(pd_lemmas / frontier, 1)
    without = round((pd_lemmas - priv_total) / frontier, 1)
    without_literal = round((pd_lemmas - priv_literal) / frontier, 1)
    return {
        "pd_lemmas": pd_lemmas,
        "pwg_in_span": frontier,
        "pwg_total": len(pwg_list),
        "multiple": with_p,
        "multiple_without_privatives": without,
        "multiple_without_privatives_literal": without_literal,
        "privatives_subtracted": priv_total,
        "privatives_subtracted_literal": priv_literal,
        "span_frontier": "apaca",
    }


def overall_composition(headwords):
    """The whole-alphabet split the A68 draft quotes (70.4 / 12.7 / 16.9)."""
    c = Counter(classify(a) for a in headwords.values())
    n = c["compound"] + c["derivative"] + c["simplex"]
    return OrderedDict(
        classified=n,
        compound_n=c["compound"],
        derivative_n=c["derivative"],
        simplex_n=c["simplex"],
        compound_pct=round(100.0 * c["compound"] / n, 1),
        derivative_pct=round(100.0 * c["derivative"] / n, 1),
        simplex_pct=round(100.0 * c["simplex"] / n, 1),
    )


def ledger(rows):
    """Apply the >15 pp rule against both references, mechanically."""
    refs = {r["family"]: r for r in rows if r["role"] == "reference"}
    out = []
    for r in rows:
        if r["role"] == "reference":
            continue
        worst = None
        for cat in ("compound_pct", "derivative_pct", "simplex_pct"):
            ds = []
            for ref in ("anna", "agni"):
                d = round(r[cat] - refs[ref][cat], 1)
                ds.append(d)
            row = {
                "category": cat.replace("_pct", ""),
                "vs_anna_pp": ds[0],
                "vs_agni_pp": ds[1],
                "exceeds_both": all(abs(d) > THRESHOLD_PP for d in ds),
            }
            if worst is None or max(abs(row["vs_anna_pp"]), abs(row["vs_agni_pp"])) > max(
                abs(worst["vs_anna_pp"]), abs(worst["vs_agni_pp"])
            ):
                worst = row
        qualifies = any(
            all(
                abs(round(r[cat] - refs[ref][cat], 1)) > THRESHOLD_PP
                for ref in ("anna", "agni")
            )
            for cat in ("compound_pct", "derivative_pct", "simplex_pct")
        )
        out.append(
            OrderedDict(
                family=r["family"],
                kind=r["kind"],
                pd_headwords=r["pd_headwords"],
                pwg_headwords=r["pwg_headwords"],
                worst_category=worst["category"],
                worst_delta_pp=max(abs(worst["vs_anna_pp"]), abs(worst["vs_agni_pp"])),
                qualifies_15pp=qualifies,
                pwg_counterpart=r["pwg_headwords"] != "n/a",
            )
        )
    return out


