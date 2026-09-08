"""Pins for ``f4b_ahlborn_nulltest`` (H4352).

Part 1 (``parse_ahlborn``) is pinned directly against a hand-classified
fixture. Part 2 (the hypergeometric null) lives inside main(); it is pinned as a
dry-run surface with ``AHLBORN``, ``CORR_DIRS`` and the parsed-cache directory
repointed at tmp fixtures, reading ``f4b_report.json`` back.

Limitation: main() formats the p-value with ``{pval:.3g}`` inside its
``finding`` string, which raises ``TypeError`` when scipy is absent (pval is
None) — so the main()-surface tests ``importorskip`` scipy. That is a latent
defect in the script, recorded in the coverage note, not patched here.

Hand derivation, Part 1 (mw_hw = {pqs, tuv, mno, mnp}):
    <pwg corr=anarGya>anarDya</pwg> <mw>anarGya</mw>  recorded == correct  -> mw_correct
    <pwg corr=abc>abd</pwg> <mw>abd</mw>              recorded == error    -> shares_error
    <pwg corr=xyz>xyw</pwg> <mw></mw>                 recorded empty       -> mw_absent_recorded
    <pwg corr=klm>kln</pwg> <mw>klq</mw>              recorded is neither  -> mw_other
    "pqr" corr="pqs"      lookup: pqs in MW, pqr not                       -> mw_correct
    tuv -> tuw            lookup: tuv in MW, tuw not                       -> shares_error
    ghi -> ghj            lookup: neither                                  -> mw_absent
    (a line with no arrow)                                                 -> skipped
    mno -> mnp            lookup: both present, correct wins               -> mw_correct
    => 8 rows: mw_correct 3 · shares_error 2 · mw_absent_recorded 1 · mw_other 1 · mw_absent 1

Hand derivation, Part 2 (main):
    mw.tsv k1  = a b c d e        pwg.tsv k1 = a b c d x ; pw.tsv = a b ; sch, pwkvn empty
    U = PET ∩ MW = {a,b,c,d}                                   |U| = 4
    PET corrected {a,b,x} ∩ U = {a,b}                          2
    MW  corrected {a,c,e} ∩ U = {a,c}                          2
    observed both = {a}                                        1
    expected = 2*2/4 = 1.0 ; lift = 1.0 ; verdict "AT chance" (lift < 1.3)
    hypergeom p = P(X >= 1 | M=4, n=2, N=2) = 1 - C(2,0)C(2,2)/C(4,2) = 1 - 1/6 = 5/6
"""

import json

import pytest

import f4b_ahlborn_nulltest as f4b
import parse_cslorig
from conftest import write_text, write_tsv

AHLBORN = """<pwg err="typo" corr="anarGya">anarDya</pwg> <mw>anarGya</mw>
<pwg err="typo" corr="abc">abd</pwg> <mw>abd</mw>
<pwg err="scan" corr="xyz">xyw</pwg> <mw></mw>
<pwg err="typo" corr="klm">kln</pwg> <mw>klq</mw>
"pqr" corr="pqs"
tuv -> tuw
ghi -> ghj
a line with no arrow at all
mno -> mnp
"""

# main()-surface ahlborn: judged against mw_hw = {a,b,c,d,e} from mw.tsv
AHLBORN_MAIN = """<pwg err="typo" corr="abc">abd</pwg> <mw>abc</mw>
<pwg err="typo" corr="klm">kln</pwg> <mw>kln</mw>
b -> c
zz -> zy
"""
# null: MW carries the correct form every time
AHLBORN_NULL = """<pwg err="typo" corr="abc">abd</pwg> <mw>abc</mw>
<pwg err="typo" corr="klm">kln</pwg> <mw>klm</mw>
zz -> a
"""


def _change(hws):
    return "".join(f"; <L>{i}<k1>{h}\n{i} old q\n{i} new r\n" for i, h in enumerate(hws, 1))


def _parsed(tmp_path):
    parsed = tmp_path / "parsed"
    write_tsv(parsed / "mw.tsv", [(i, k, "", "", "", 0, "") for i, k in enumerate("abcde", 1)])
    write_tsv(parsed / "pwg.tsv", [(i, k, "", "", "", 0, "") for i, k in enumerate("abcdx", 1)])
    write_tsv(parsed / "pw.tsv", [(1, "a", "", "", "", 0, ""), (2, "b", "", "", "", 0, "")])
    write_tsv(parsed / "sch.tsv", [])
    write_tsv(parsed / "pwkvn.tsv", [])
    return parsed


def _run(tmp_path, monkeypatch, forensic_cwd, ahlborn, pet_corrected, mw_corrected):
    parsed = _parsed(tmp_path)
    corr = tmp_path / "corr" / "dictionaries"
    write_text(corr / "pwg" / "change_pwg_1.txt", _change(pet_corrected))
    write_text(corr / "mw" / "change_mw_1.txt", _change(mw_corrected))
    monkeypatch.setattr(parse_cslorig, "PARSED_DIR", str(parsed))
    monkeypatch.setattr(f4b, "AHLBORN", str(write_text(tmp_path / "ahlborn.txt", ahlborn)))
    monkeypatch.setattr(f4b, "CORR_DIRS", [str(tmp_path / "corr")])
    f4b.main()
    return json.loads((forensic_cwd / "data/forensic/f4b_report.json").read_text(encoding="utf-8"))


def test_parse_ahlborn_hand_classified(tmp_path, monkeypatch, pin):
    monkeypatch.setattr(f4b, "AHLBORN", str(write_text(tmp_path / "ahlborn.txt", AHLBORN)))
    rows = f4b.parse_ahlborn({"pqs", "tuv", "mno", "mnp"})
    pin("f4b", "ahlborn.rows", 8, len(rows))
    statuses = [r["status"] for r in rows]
    pin("f4b", "ahlborn.statuses",
        ["mw_correct", "shares_error", "mw_absent_recorded", "mw_other",
         "mw_correct", "shares_error", "mw_absent", "mw_correct"], statuses)
    pin("f4b", "ahlborn.shares_error", 2, statuses.count("shares_error"))
    pin("f4b", "ahlborn.err_type.first", "typo", rows[0]["err_type"])
    pin("f4b", "ahlborn.err_type.lookup_form", "?", rows[5]["err_type"])
    pin("f4b", "ahlborn.mw_recorded.empty", "", rows[2]["mw_recorded"])
    pin("f4b", "ahlborn.mw_has_error.tuv", True, rows[5]["mw_has_error"])


def test_corrected_headwords_union(tmp_path, monkeypatch, pin):
    corr = tmp_path / "corr" / "dictionaries"
    write_text(corr / "pwg" / "change_pwg_1.txt", _change(["a", "b"]))
    write_text(corr / "pwg" / "printchange_pwg.txt", "1,2\tx\told\tnew\tc\n")
    write_text(corr / "pw" / "correctionform_pw.txt", "Case 1: hw=b\nold = o\nnew = n\n")
    monkeypatch.setattr(f4b, "CORR_DIRS", [str(tmp_path / "corr")])
    pin("f4b", "corrected_headwords.PET", {"a", "b", "x"}, f4b.corrected_headwords(f4b.PET))
    pin("f4b", "corrected_headwords.mw_none", set(), f4b.corrected_headwords(["mw"]))


def test_main_positive_null_test_arithmetic(tmp_path, monkeypatch, forensic_cwd, pin):
    pytest.importorskip("scipy")
    report = _run(tmp_path, monkeypatch, forensic_cwd, AHLBORN_MAIN,
                  pet_corrected=["a", "b", "x"], mw_corrected=["a", "c", "e"])
    pin("f4b", "main.ahlborn_total", 4, report["ahlborn_total"])
    pin("f4b", "main.ahlborn_status",
        {"mw_correct": 2, "shares_error": 1, "mw_absent": 1}, report["ahlborn_status"])
    pin("f4b", "main.ahlborn_shares_error_pct", 25.0, report["ahlborn_shares_error_pct"])
    pin("f4b", "main.null_U", 4, report["null_U"])
    pin("f4b", "main.null_pet_corrected", 2, report["null_pet_corrected"])
    pin("f4b", "main.null_mw_corrected", 2, report["null_mw_corrected"])
    pin("f4b", "main.null_observed", 1, report["null_observed"])
    pin("f4b", "main.null_expected", 1.0, report["null_expected"])
    pin("f4b", "main.null_lift", 1.0, report["null_lift"])
    pin("f4b", "main.null_p", pytest.approx(5 / 6, abs=1e-9), report["null_p"])
    pin("f4b", "main.null_verdict", "AT chance — independent errors", report["null_verdict"])
    pin("f4b", "main.shared_corrected_examples", ["a"], report["shared_corrected_examples"])


def test_main_null_fixture_zero_shared(tmp_path, monkeypatch, forensic_cwd, pin):
    pytest.importorskip("scipy")
    report = _run(tmp_path, monkeypatch, forensic_cwd, AHLBORN_NULL,
                  pet_corrected=["a", "b"], mw_corrected=["c", "d"])
    pin("f4b", "null.ahlborn_total", 3, report["ahlborn_total"])
    pin("f4b", "null.ahlborn_shares_error", 0, report["ahlborn_shares_error"])
    pin("f4b", "null.ahlborn_shares_error_pct", 0.0, report["ahlborn_shares_error_pct"])
    pin("f4b", "null.null_observed", 0, report["null_observed"])
    pin("f4b", "null.null_expected", 1.0, report["null_expected"])
    pin("f4b", "null.null_lift", 0.0, report["null_lift"])
    pin("f4b", "null.null_p", 1.0, report["null_p"])
    pin("f4b", "null.shared_corrected_examples", [], report["shared_corrected_examples"])
