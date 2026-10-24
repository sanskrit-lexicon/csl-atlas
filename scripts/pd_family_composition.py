#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7110 — PD family composition: compound / derivative / simplex per family.

Answers one question: which PD prefix families have a compound-derivative-simplex
mix that differs from the two families already in the A68 §6.2 table (*anna*
77.5 / 8.7 / 13.8 and *agni* 73.7 / 14.9 / 11.4) by more than 15 percentage
points on at least one category?

The rule, the source readers and every shared constant live in
``scripts/lib/pd_family_rule.py`` (token-budget split, same behaviour). This
script is the CLI: it builds the envelope, renders the two artifacts, and fails
closed in ``--check``.

Reads the external, read-only PDScan 2020 machine text (``txt/pd.txt`` inside
``pdtxt.zip``, https://sanskrit-lexicon.uni-koeln.de/scans/PDScan/2020/downloads/pdtxt.zip,
© 2014 The Sanskrit Library / Thomas Malten, CC BY-NC-SA 3.0) and the Cologne
PWG text (``csl-orig/v02/pwg/pwg.txt``). Neither is committed here.

Outputs (data/pd/):
    pd_family_composition.tsv     one row per family
    pd_family_composition.json    envelope: pins, rule, family rows, examples,
                                  privative recount, density recompute, ledger
Run from repo root:
    python scripts/pd_family_composition.py            # write
    python scripts/pd_family_composition.py --check    # verify committed files
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import OrderedDict

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

# the rule lives in the lib module; these imports are also the test surface
from pd_family_rule import (  # noqa: E402,F401
    PD_SHA256,
    POPULATION_BAND,
    POPULATION_PIN,
    PRIVATIVE_BAND,
    PRIVATIVE_PIN,
    ROOT,
    SUFFIXES,
    THRESHOLD_PP,
    classify,
    density,
    family_row,
    first_line_paren,
    ledger,
    members,
    members_literal,
    overall_composition,
    parse_pd,
    parse_pwg,
    privative_recount,
    sha256,
)

OUT_DIR = os.path.join(ROOT, "data", "pd")
OUT_TSV = os.path.join(OUT_DIR, "pd_family_composition.tsv")
OUT_JSON = os.path.join(OUT_DIR, "pd_family_composition.json")

DEFAULT_PD = os.environ.get(
    "PD_TXT",
    os.path.join(os.path.expanduser("~"), "Documents", "pd", "txt", "pd.txt"),
)
DEFAULT_PWG = os.environ.get("PWG_TXT", os.path.join(ROOT, "..", "csl-orig", "v02", "pwg", "pwg.txt"))
try:
    from pd_family_rule import GH as _GH

    DEFAULT_PWG = os.environ.get("PWG_TXT", os.path.join(_GH, "csl-orig", "v02", "pwg", "pwg.txt"))
except Exception:  # pragma: no cover - GH always exists in practice
    pass

FAMILIES = [
    ("anna", "string", "anna", "reference"),
    ("agni", "string", "agni", "reference"),
    ("anya", "string", "anya", "control"),
    ("antar", "string", "antar", "control"),
    ("ati", "string", "ati", "preverb"),
    ("anu", "string", "anu", "preverb"),
    ("apa", "string", "apa", "preverb"),
    ("atra", "string", "atra", "function"),
    ("atha", "string", "aTa", "function"),
    ("privative a-", "morph", "a", "privative"),
    ("negative an-", "morph", "an", "privative"),
]

# ------------------------------------------------------------------- outputs
def build(pd_path, pwg_path):
    headwords, entries, unique_k1, corrections = parse_pd(pd_path)
    pwg_set = parse_pwg(pwg_path)
    rows = [
        family_row(name, kind, token, role, headwords, pwg_set, unique_k1)
        for name, kind, token, role in FAMILIES
    ]
    priv = privative_recount(entries, unique_k1)
    priv["share_of_population_pct"] = round(100.0 * priv["entries_total"] / len(headwords), 1)
    dens = density(priv["entries_total"], priv["literal_total"])
    led = ledger(rows)
    envelope = OrderedDict(
        hid="H7110",
        generated_by="scripts/pd_family_composition.py",
        rule={
            "population": "unique <k1> with at least one entry printing k1==k2 and an analysis parenthesis",
            "population_pin": POPULATION_PIN,
            "analysis": "first ( … ) after the ¦ separator on the entry's first body line",
            "members": "strip U+0301/U+0300, °, apostrophes; split on hyphen/en-dash/em-dash/whitespace",
            "classification": "1 member ⇒ simplex; last member in suffixes ⇒ derivative; else compound",
            "suffixes": list(SUFFIXES),
            "threshold_pp": THRESHOLD_PP,
            "threshold_rule": "qualify when one category differs from BOTH anna and agni by > 15 pp",
        },
        sources={
            "pd": {
                "bytes": os.path.getsize(pd_path),
                "sha256": sha256(pd_path),
                "entries": len(entries),
                "unique_key1": len(unique_k1),
            },
            "pwg": {"sha256": sha256(pwg_path), "unique_key1": len(pwg_set)},
        },
        population=OrderedDict(
            classified_headwords=len(headwords),
            correction_block_headwords=len(corrections),
            reconciled_total=len(headwords) + len(corrections),
            pin=POPULATION_PIN,
            delta_vs_pin=len(headwords) + len(corrections) - POPULATION_PIN,
            within_band=abs(len(headwords) + len(corrections) - POPULATION_PIN)
            <= POPULATION_BAND,
            note=(
                "the A68 draft's 103,127 is this parser's %d analyses plus the %d "
                "headwords whose first-line parenthesis is a CORRECTIONS block "
                "(an errata insertion, not an analysis); the 380 are counted but "
                "not classified"
                % (len(headwords), len(corrections))
            ),
        ),
        composition=overall_composition(headwords),
        families=rows,
        privative=priv,
        density=dens,
        ledger=led,
    )
    return envelope


def render_tsv(envelope):
    cols = [
        "family", "kind", "role", "pd_headwords", "pwg_headwords", "classified",
        "compound_n", "derivative_n", "simplex_n", "compound_pct", "derivative_pct",
        "simplex_pct", "example_compound", "example_derivative", "example_simplex",
    ]
    lines = ["\t".join(cols)]
    for r in envelope["families"]:
        lines.append(
            "\t".join(
                str(x)
                for x in (
                    r["family"], r["kind"], r["role"], r["pd_headwords"],
                    r["pwg_headwords"], r["classified"], r["compound_n"],
                    r["derivative_n"], r["simplex_n"], r["compound_pct"],
                    r["derivative_pct"], r["simplex_pct"],
                    (r["examples"]["compound"] or [""])[0],
                    (r["examples"]["derivative"] or [""])[0],
                    (r["examples"]["simplex"] or [""])[0],
                )
            )
        )
    return "\n".join(lines) + "\n"


def write_tsv(envelope, path):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_tsv(envelope))


def write_json(envelope, path):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(envelope, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


def check(envelope, tsv_before, json_before):
    problems = []
    tsv_now = render_tsv(envelope)
    if tsv_before != tsv_now:
        problems.append("pd_family_composition.tsv is stale — regenerate and commit")
    if json_before != _render_json(envelope):
        problems.append("pd_family_composition.json is stale — regenerate and commit")
    pop = envelope["population"]
    if not pop["within_band"]:
        problems.append(
            "population %d is outside the ±%d band of the pinned %d"
            % (pop["classified_headwords"], POPULATION_BAND, POPULATION_PIN)
        )
    priv_literal = envelope["privative"]["literal_total"]
    if abs(priv_literal - PRIVATIVE_PIN) > PRIVATIVE_BAND * PRIVATIVE_PIN:
        problems.append(
            "literal privative recount %d is outside ±%d%% of the pinned %d"
            % (priv_literal, int(PRIVATIVE_BAND * 100), PRIVATIVE_PIN)
        )
    priv_total = envelope["privative"]["entries_total"]
    if abs(priv_total - PRIVATIVE_PIN) > 0.10 * PRIVATIVE_PIN:
        problems.append(
            "accent-normalised privative recount %d drifts >10%% from the pinned %d"
            % (priv_total, PRIVATIVE_PIN)
        )
    for r in envelope["families"]:
        for cat in ("compound_pct", "derivative_pct", "simplex_pct"):
            if not (0.0 <= r[cat] <= 100.0):
                problems.append("%s: %s out of range" % (r["family"], cat))
    return problems


def _render_json(envelope):
    return json.dumps(envelope, ensure_ascii=False, indent=1) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pd", default=DEFAULT_PD, help="path to PDScan 2020 txt/pd.txt")
    ap.add_argument("--pwg", default=DEFAULT_PWG, help="path to csl-orig v02/pwg/pwg.txt")
    ap.add_argument("--check", action="store_true", help="verify committed artifacts")
    ap.add_argument("--print-suffixes", action="store_true")
    args = ap.parse_args(argv)

    if args.print_suffixes:
        print(", ".join(SUFFIXES))
        return 0
    for p, label in ((args.pd, "PD"), (args.pwg, "PWG")):
        if not os.path.exists(p):
            print(f"FAIL: {label} source not found: {p}", file=sys.stderr)
            return 1

    envelope = build(args.pd, args.pwg)
    tsv_before = json_before = None
    if args.check:
        if not (os.path.exists(OUT_TSV) and os.path.exists(OUT_JSON)):
            print("FAIL: committed artifacts missing", file=sys.stderr)
            return 1
        tsv_before = open(OUT_TSV, encoding="utf-8").read()
        json_before = open(OUT_JSON, encoding="utf-8").read()
        problems = check(envelope, tsv_before, json_before)
        if problems:
            for p in problems:
                print("FAIL: " + p, file=sys.stderr)
            return 1
        print("PASS: artifacts regenerate byte-identical; pins hold")
    else:
        os.makedirs(OUT_DIR, exist_ok=True)
        write_tsv(envelope, OUT_TSV)
        write_json(envelope, OUT_JSON)
        print("wrote %s and %s" % (OUT_TSV, OUT_JSON))

    src = envelope["sources"]["pd"]
    print(
        "PD: %d entries, %d unique k1, sha256 %s%s"
        % (
            src["entries"],
            src["unique_key1"],
            src["sha256"][:12],
            "" if src["sha256"] == PD_SHA256 else "  (UNPINNED)",
        )
    )
    pop = envelope["population"]
    print(
        "population: %d classified headwords (pin %d, delta %+d)"
        % (pop["classified_headwords"], pop["pin"], pop["delta_vs_pin"])
    )
    priv = envelope["privative"]
    print(
        "privative (accent-normalised): a- %d + an- %d = %d entries (%.1f %% of population)"
        % (priv["entries_a"], priv["entries_an"], priv["entries_total"],
           priv["share_of_population_pct"])
    )
    print(
        "privative (literal a-/an-, the A68 draft's rule): %d + %d = %d"
        % (priv["literal_a"], priv["literal_an"], priv["literal_total"])
    )
    dens = envelope["density"]
    if dens:
        print(
            "density: %.1f× (%d/%d); without privatives %.1f× (literal rule %.1f×)"
            % (dens["multiple"], dens["pd_lemmas"], dens["pwg_in_span"],
               dens["multiple_without_privatives"],
               dens["multiple_without_privatives_literal"])
        )
    print("\nfamily            kind    PD      PWG     comp%  der%  simp%   Δmax  >15pp")
    for r in envelope["families"]:
        led = next(x for x in envelope["ledger"] if x["family"] == r["family"]) if r["role"] != "reference" else None
        print(
            "%-17s %-7s %6d %7s  %5.1f  %4.1f  %5.1f   %5s  %s"
            % (
                r["family"], r["kind"], r["pd_headwords"],
                r["pwg_headwords"] if r["pwg_headwords"] != "n/a" else "—",
                r["compound_pct"], r["derivative_pct"], r["simplex_pct"],
                "%.1f" % led["worst_delta_pp"] if led else "—",
                "YES" if led and led["qualifies_15pp"] else "",
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
