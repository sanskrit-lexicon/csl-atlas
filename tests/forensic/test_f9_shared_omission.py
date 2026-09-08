"""Pins for ``f9_shared_omission`` (H4352).

``contingency`` is pure and pinned directly. main() reads five key1 headword
exports from ``HW_DIR`` and writes under ``ATLAS_ROOT/data/forensic`` — both
repointed at tmp — so the CSV it writes is the dry-run surface.

f9 replaces ``sys.stdout``/``sys.stderr`` with fresh UTF-8 wrappers at import;
the module fixture restores pytest's capture streams after importing so later
tests keep working.

Hand derivation (anchor R = SKD ∩ VCP):
    SKD = {agni, deva, soma, indra, varuRa, mitra, SabdaX}
    VCP = {agni, deva, soma, indra, varuRa, mitra, vAcaspatiX}
    R   = {agni, deva, soma, indra, varuRa, mitra}                       |R| = 6
    PWG = {agni, deva, soma, indra}         (lacks varuRa, mitra)
    MW  = {agni, deva, soma, mitra}         (lacks indra, varuRa)
    AP  = {agni, varuRa, mitra}
    MW:  has&has {agni,deva,soma}=3 · has&lacks {indra}=1 · lacks&has {mitra}=1
         · lacks&lacks {varuRa}=1 ; P(lack|has)=1/4 ; P(lack|lacks)=1/2 ; ratio 2.0
    AP:  has&has {agni}=1 · has&lacks {deva,soma,indra}=3 · lacks&has {varuRa,mitra}=2
         · lacks&lacks {}=0 ; P(lack|has)=3/4 ; P(lack|lacks)=0 ; ratio 0.0
    MW fills 1/2 of PWG's blind spots, AP fills 2/2.
"""

import csv
import io
import json
import sys

import pytest

from conftest import write_text


@pytest.fixture(scope="module")
def f9():
    """f9 does ``sys.stdout = io.TextIOWrapper(sys.stdout.buffer, ...)`` at
    import. Under pytest that would wrap (and later close) the capture tmpfile,
    so the import runs behind throwaway streams that own their own buffers."""
    saved = sys.stdout, sys.stderr
    sys.stdout = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
    sys.stderr = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
    try:
        import f9_shared_omission as mod
    finally:
        sys.stdout, sys.stderr = saved
    return mod


SETS = {
    "SKD": ["agni", "deva", "soma", "indra", "varuRa", "mitra", "SabdaX"],
    "VCP": ["agni", "deva", "soma", "indra", "varuRa", "mitra", "vAcaspatiX"],
    "PWG": ["agni", "deva", "soma", "indra"],
    "MW": ["agni", "deva", "soma", "mitra"],
    "AP": ["agni", "varuRa", "mitra"],
}

# Null: MW and AP each carry every word PWG lacks -> zero shared omissions.
SETS_NULL = dict(SETS, MW=["agni", "deva", "varuRa", "mitra"], AP=["varuRa", "mitra"])


def _run(f9, tmp_path, monkeypatch, sets):
    hw = tmp_path / "hw"
    for code, words in sets.items():
        write_text(hw / f"{code}.txt", "\n".join(words) + "\n\n")
    (tmp_path / "data" / "forensic").mkdir(parents=True)
    monkeypatch.setattr(f9, "HW_DIR", str(hw))
    monkeypatch.setattr(f9, "FILES", {c: f"{c}.txt" for c in sets})
    monkeypatch.setattr(f9, "ATLAS_ROOT", str(tmp_path))
    f9.main()
    out = tmp_path / "data" / "forensic" / "shared_omission_test.csv"
    with open(out, encoding="utf-8") as fh:
        rows = {r["probe"]: r for r in csv.DictReader(fh)}
    with open(str(out) + ".source.json", encoding="utf-8") as fh:
        sidecar = json.load(fh)
    return rows, sidecar


def test_contingency_hand_counts(f9, pin):
    anchor = set(SETS["SKD"]) & set(SETS["VCP"])
    pin("f9", "anchor", 6, len(anchor))
    c = f9.contingency(anchor, set(SETS["PWG"]), set(SETS["MW"]))
    pin("f9", "MW.cells", (3, 1, 1, 1),
        (c["pwg_has_probe_has"], c["pwg_has_probe_lacks"], c["pwg_lacks_probe_has"], c["pwg_lacks_probe_lacks"]))
    pin("f9", "MW.margins", (4, 2), (c["pwg_has"], c["pwg_lacks"]))
    pin("f9", "MW.rates", (0.25, 0.5), (c["lack_given_pwg_has"], c["lack_given_pwg_lacks"]))
    pin("f9", "MW.gap_sensitivity", 2.0, c["gap_sensitivity"])
    a = f9.contingency(anchor, set(SETS["PWG"]), set(SETS["AP"]))
    pin("f9", "AP.cells", (1, 3, 2, 0),
        (a["pwg_has_probe_has"], a["pwg_has_probe_lacks"], a["pwg_lacks_probe_has"], a["pwg_lacks_probe_lacks"]))
    pin("f9", "AP.rates", (0.75, 0.0), (a["lack_given_pwg_has"], a["lack_given_pwg_lacks"]))
    pin("f9", "AP.gap_sensitivity", 0.0, a["gap_sensitivity"])


def test_contingency_edge_ratios(f9, pin):
    anchor = {"w1", "w2", "w3", "w4"}
    pwg = {"w1", "w2"}
    # probe holds every PWG word -> P(lack|has)=0 -> ratio undefined -> None
    c = f9.contingency(anchor, pwg, {"w1", "w2"})
    pin("f9", "edge.ratio_undefined", None, c["gap_sensitivity"])
    pin("f9", "edge.shared_omission", 2, c["pwg_lacks_probe_lacks"])
    # probe lacks exactly one of each margin -> equal rates -> ratio 1.0 (no coupling)
    c1 = f9.contingency(anchor, pwg, {"w1", "w3"})
    pin("f9", "edge.ratio_one", 1.0, c1["gap_sensitivity"])
    # empty anchor -> all zero, ratio None
    c0 = f9.contingency(set(), pwg, {"w1"})
    pin("f9", "edge.empty_anchor", (0, 0, None), (c0["pwg_has"], c0["pwg_lacks"], c0["gap_sensitivity"]))


def test_main_positive_csv(f9, tmp_path, monkeypatch, pin):
    rows, sidecar = _run(f9, tmp_path, monkeypatch, SETS)
    pin("f9", "main.rows", 2, len(rows))
    pin("f9", "main.anchor_n", 6, sidecar["anchor_n"])
    mw, ap = rows["MW"], rows["AP"]
    pin("f9", "main.MW.cells", ("3", "1", "1", "1"),
        (mw["pwg_has_probe_has"], mw["pwg_has_probe_lacks"], mw["pwg_lacks_probe_has"], mw["pwg_lacks_probe_lacks"]))
    pin("f9", "main.MW.gap_sensitivity", "2.0", mw["gap_sensitivity"])
    pin("f9", "main.AP.cells", ("1", "3", "2", "0"),
        (ap["pwg_has_probe_has"], ap["pwg_has_probe_lacks"], ap["pwg_lacks_probe_has"], ap["pwg_lacks_probe_lacks"]))
    pin("f9", "main.AP.gap_sensitivity", "0.0", ap["gap_sensitivity"])
    pin("f9", "main.sidecar.MW.gap_sensitivity", 2.0, sidecar["results"]["MW"]["gap_sensitivity"])


def test_main_null_zero_shared_omission(f9, tmp_path, monkeypatch, pin):
    rows, sidecar = _run(f9, tmp_path, monkeypatch, SETS_NULL)
    mw, ap = rows["MW"], rows["AP"]
    pin("f9", "null.MW.shared_omission", "0", mw["pwg_lacks_probe_lacks"])
    pin("f9", "null.MW.gap_sensitivity", "0.0", mw["gap_sensitivity"])
    pin("f9", "null.AP.shared_omission", "0", ap["pwg_lacks_probe_lacks"])
    # AP lacks every PWG word: P(lack|has)=1.0, P(lack|lacks)=0 -> ratio 0.0
    pin("f9", "null.AP.rates", ("1.0", "0.0"), (ap["lack_given_pwg_has"], ap["lack_given_pwg_lacks"]))
    pin("f9", "null.sidecar.MW.lacks_lacks", 0, sidecar["results"]["MW"]["pwg_lacks_probe_lacks"])
