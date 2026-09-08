"""Pins for ``f0_shared_headword_typos`` (H4352).

f0 is main()-only past its three helpers, and it resolves the sanhw1 snapshot AT
IMPORT (``SNAPSHOT = _find_sanhw1()``), so the module is imported once behind a
placeholder ``$SANHW1`` and each test then points ``f0.SNAPSHOT`` at its own
fixture. main() is exercised as a dry-run surface: it runs in a tmp cwd against
fixture inventory / L0 files and its ``f0_report.json`` + CSVs are read back.
Limitation: ``MIN_PAIR_SIZE`` (5000) is lowered to 1 so the tiny fixture reaches
``top_doublet_pairs``; every other constant is the script's own.

Hand derivation (REAL_MIN=8 so a lemma needs 8 dict codes to be "real";
rare = 2 <= df <= 5):

    agni  MW,PWG,PW,AP,BOP,SKD,VCP,BEN   df 8  real
    deva  MW,PWG,PW,AP,BOP,SKD,VCP,BEN   df 8  real
    soma  MW,PW,AP,BOP,SKD,VCP,BEN,SCH   df 8  real   (NOT in PWG)
    agnl  MW,PWG                          df 2  rare, ED1 of agni (l<->i)
    agn   MW,PW,PWG                       df 3  rare, ED1 of agni (deletion)
    somx  MW,PWG                          df 2  rare, ED1 of soma (x<->a)
    xyzq  BOP,SKD                         df 2  rare, ED1 of nothing
    devx  AP                              df 1  below the rare floor

Anomalies = agnl, agn, somx (3). Pair tallies (sorted-code keys):
    agnl -> (MW,PWG): shared+1, excl(df2)+1, doublet+1 (both carry agni)
    agn  -> (MW,PW),(MW,PWG),(PW,PWG): shared+1, doublet+1 each
    somx -> (MW,PWG): shared+1, excl+1, doublet+0 (PWG lacks soma)
    => MW/PWG shared 3 · doublet 2 · excl 2 ; MW/PW 1·1·0 ; PW/PWG 1·1·0
sizes: MW holds 6 lemmas, PWG 5 -> per_1k_smaller(MW,PWG) = 1000*3/5 = 600.0
"""

import csv
import json
import os
import sys

import pytest

from conftest import write_text

SNAP = """agni:MW,PWG,PW,AP,BOP,SKD,VCP,BEN
deva:MW,PWG,PW,AP,BOP,SKD,VCP,BEN
soma:MW,PW,AP,BOP,SKD,VCP,BEN,SCH
agnl:MW,PWG
agn:MW,PW,PWG
somx:MW,PWG
xyzq:BOP,SKD
devx:AP
"""

# Null: the two rare lemmas are shared by MW+PWG but sit >= 2 edits from every
# real lemma, so the correct anomaly count is zero.
SNAP_NULL = """agni:MW,PWG,PW,AP,BOP,SKD,VCP,BEN
deva:MW,PWG,PW,AP,BOP,SKD,VCP,BEN
zzzz:MW,PWG
qqq:MW,PWG,PW
"""

INVENTORY = "code,year\nMW,1899\nPWG,1855\nPW,1879\nAP,1890\n"
L0_HEADER = ",MW,PWG\nMW,0,1\nPWG,1,0\n"


@pytest.fixture(scope="module")
def f0(tmp_path_factory):
    placeholder = tmp_path_factory.mktemp("f0") / "placeholder.txt"
    placeholder.write_text("", encoding="utf-8")
    os.environ["SANHW1"] = str(placeholder)
    sys.modules.pop("f0_shared_headword_typos", None)
    import f0_shared_headword_typos as mod
    return mod


def _run(f0, tmp_path, monkeypatch, snapshot_text):
    snap = write_text(tmp_path / "sanhw1.txt", snapshot_text)
    write_text(tmp_path / "data" / "dictionary_inventory.csv", INVENTORY)
    write_text(tmp_path / "data" / "L0" / "distances" / "B_whamming.csv", L0_HEADER)
    monkeypatch.setattr(f0, "SNAPSHOT", str(snap))
    monkeypatch.setattr(f0, "MIN_PAIR_SIZE", 1)
    monkeypatch.chdir(tmp_path)
    f0.main()
    report = json.loads((tmp_path / "data/forensic/f0_report.json").read_text(encoding="utf-8"))
    with open(tmp_path / "data/forensic/pair_shared_typo_counts.csv", encoding="utf-8") as fh:
        pairs = list(csv.DictReader(fh))
    with open(tmp_path / "data/forensic/shared_headword_anomalies.csv", encoding="utf-8") as fh:
        anomalies = list(csv.DictReader(fh))
    return report, pairs, anomalies


def test_helpers_edit_distance_and_deletes(f0):
    assert f0.within_ed1("agni", "agni")
    assert f0.within_ed1("agnl", "agni")      # substitution
    assert f0.within_ed1("agn", "agni")       # deletion / insertion
    assert f0.within_ed1("agni", "agn")
    assert not f0.within_ed1("agxx", "agni")  # two substitutions
    assert not f0.within_ed1("ag", "agni")    # length gap 2
    assert not f0.within_ed1("qqq", "agni")
    assert list(f0.deletes1("abc")) == ["abc", "bc", "ac", "ab"]
    assert len(list(f0.deletes1("agni"))) == 5


def test_load_snapshot_merges_duplicate_lemma_lines(f0, tmp_path, pin):
    snap = write_text(tmp_path / "dup.txt", "agni:MW\nagni:PWG\nbad line\n:MW\n")
    lemma_dicts, df = f0.load_snapshot(str(snap))
    pin("f0", "load_snapshot.lemmas", 1, len(lemma_dicts))
    pin("f0", "load_snapshot.agni_dicts", {"MW", "PWG"}, lemma_dicts["agni"])
    pin("f0", "load_snapshot.agni_df", 2, df["agni"])


def test_positive_fixture_pair_tallies(f0, tmp_path, monkeypatch, pin):
    report, pairs, anomalies = _run(f0, tmp_path, monkeypatch, SNAP)
    pin("f0", "n_lemmas", 8, report["n_lemmas"])
    pin("f0", "n_real", 3, report["n_real"])
    pin("f0", "n_rare", 4, report["n_rare"])
    pin("f0", "n_candidate_anomalies", 3, report["n_candidate_anomalies"])
    pin("f0", "anomalies.csv_rows", 3, len(anomalies))
    pin("f0", "pairs.csv_rows", 3, len(pairs))
    probes = report["probes"]
    pin("f0", "probe.PWG/MW", (3, 2, 2),
        (probes["PWG/MW"]["shared"], probes["PWG/MW"]["doublet"], probes["PWG/MW"]["excl_df2"]))
    pin("f0", "probe.PW/MW", (1, 1, 0),
        (probes["PW/MW"]["shared"], probes["PW/MW"]["doublet"], probes["PW/MW"]["excl_df2"]))
    pin("f0", "probe.PWG/PW", (1, 1, 0),
        (probes["PWG/PW"]["shared"], probes["PWG/PW"]["doublet"], probes["PWG/PW"]["excl_df2"]))
    pin("f0", "probe.BOP/MW", (0, 0, 0),
        (probes["BOP/MW"]["shared"], probes["BOP/MW"]["doublet"], probes["BOP/MW"]["excl_df2"]))
    top = report["top_doublet_pairs"][0]
    pin("f0", "top_doublet_pair", {"pair": "MW/PWG", "doublets": 2, "shared": 3, "per_1k": 600.0}, top)
    pin("f0", "mw_pwg_doublet_examples", ["agnl~agni", "agn~agni"], report["mw_pwg_doublet_examples"])
    by_pair = {(r["dict_a"], r["dict_b"]): r for r in pairs}
    pin("f0", "csv.MW/PWG.sizes", ("6", "5"), (by_pair[("MW", "PWG")]["size_a"], by_pair[("MW", "PWG")]["size_b"]))
    pin("f0", "csv.MW/PWG.both_in_L0", "True", by_pair[("MW", "PWG")]["both_in_L0"])
    pin("f0", "csv.MW/PW.both_in_L0", "False", by_pair[("MW", "PW")]["both_in_L0"])
    # anomaly rows sort df-ascending; the df-3 lemma "agn" must come last
    pin("f0", "anomalies.last_row", ("agn", "agni", "3"),
        (anomalies[-1]["typo_form"], anomalies[-1]["nearest_real"], anomalies[-1]["df_typo"]))


def test_null_fixture_reports_zero_not_noise(f0, tmp_path, monkeypatch, pin):
    report, pairs, anomalies = _run(f0, tmp_path, monkeypatch, SNAP_NULL)
    pin("f0", "null.n_real", 2, report["n_real"])
    pin("f0", "null.n_rare", 2, report["n_rare"])
    pin("f0", "null.n_candidate_anomalies", 0, report["n_candidate_anomalies"])
    pin("f0", "null.anomalies.csv_rows", 0, len(anomalies))
    pin("f0", "null.pairs.csv_rows", 0, len(pairs))
    pin("f0", "null.probe.PWG/MW.shared", 0, report["probes"]["PWG/MW"]["shared"])
    pin("f0", "null.top_doublet_pairs", [], report["top_doublet_pairs"])
    pin("f0", "null.mw_pwg_doublet_examples", [], report["mw_pwg_doublet_examples"])
