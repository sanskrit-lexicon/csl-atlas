"""Pins for ``f5_entry_comparison`` (H4352).

``sigil`` / ``dedup`` / ``concordant_fraction`` / ``spearman`` are pure and
pinned directly; ``build`` reads a mini csl-orig (``CSL_ORIG`` repointed). main()
is the dry-run surface: it builds MW + the four Petersburg dicts + the two nulls
from ``CSL_ORIG`` and writes ``f5_report.json`` + two CSVs into the cwd.

Hand derivation, positive corpus (sigil = citation text before its first digit):
  MW    agni  <ls> MBh. 1,2 | R. 3,4 | AV. 5 | P. 1,1 -> [MBH, R, AV, P] ; <s>deva <s1>indra
        soma  [MBH] ; deva none
  PWG   agni  same four in the same order ; {#agni#} {#deva#} {#agnI#}
        soma  [MBH]
  PW    agni  reversed [P, AV, R, MBH] ; {#indra#}
  PWKVN agni  [MBH, R] only (2 shared < MIN_SHARED_SRC=3 -> no order verdict)
  SCH   xyz   nothing shared
  AP    agni  [MBH, AV, R, P] (null) ; BEN zzz nothing shared
  order: PWG  seq [0,1,2,3] -> 6/6 = 1.0 (identical, 4 shared -> 1 example row)
         PW   seq [3,2,1,0] -> 0/6 = 0.0
         AP   seq [0,2,1,3] -> 5/6 = 0.8333
  content: MW {deva,indra} vs PWG {agni,deva,agnI} -> 1/4 = 0.25 ; vs PW {indra} -> 0.5
  Petersburg mean order: the script keeps only TRUTHY per-dict means, so PW's
  0.0 is dropped -> 1.0 (hand mean over scored Petersburg rows would be 0.5).
  Pinned as observed and flagged in the coverage note as a quirk.
"""

import csv
import json

import pytest

import f5_entry_comparison as f5
from conftest import write_text


def _entry(k1, body, L="1"):
    return f"<L>{L}<pc>1-1<k1>{k1}<k2>{k1}\n{body}\n<LEND>\n"


MW_TXT = (_entry("agni", "fire <ls>MBh. 1,2</ls> <ls>R. 3,4</ls> <s>deva</s>", "1")
          + _entry("agni", "also <ls>AV. 5</ls> <ls>P. 1,1</ls> <s1>indra</s1>", "1.1")
          + _entry("soma", "juice <ls>MBh. 9</ls>", "2")
          + _entry("deva", "god", "3"))

POSITIVE = {
    "mw": MW_TXT,
    "pwg": _entry("agni", "{#agni#} {%Feuer%} <ls>MBH. 1,2</ls> <ls>R. 3,4</ls> <ls>AV. 5</ls> "
                          "<ls>P. 1,1</ls> {#deva#} {#agnI#}")
           + _entry("soma", "{%Saft%} <ls>MBH. 9</ls>", "2"),
    "pw": _entry("agni", "<ls>P. 1,1</ls> <ls>AV. 5</ls> <ls>R. 3,4</ls> <ls>MBh. 1,2</ls> {#indra#}"),
    "pwkvn": _entry("agni", "<ls>MBh. 1,2</ls> <ls>R. 3,4</ls>"),
    "sch": _entry("xyz", "nothing"),
    "ap": _entry("agni", "<ls>MBh. 1,2</ls> <ls>AV. 5</ls> <ls>R. 3,4</ls> <ls>P. 1,1</ls>"),
    "ben": _entry("zzz", "nothing"),
}

# Null: every dict shares agni with MW but cites three sources MW never cites
# and carries no Sanskrit cross-references.
_DISJOINT = "<ls>X. 1</ls> <ls>Y. 2</ls> <ls>Z. 3</ls>"
NULL = {
    "mw": MW_TXT,
    "pwg": _entry("agni", _DISJOINT),
    "pw": _entry("agni", _DISJOINT),
    "pwkvn": _entry("agni", _DISJOINT),
    "sch": _entry("agni", _DISJOINT),
    "ap": _entry("agni", _DISJOINT),
    "ben": _entry("agni", _DISJOINT),
}


def _corpus(tmp_path, spec):
    root = tmp_path / "csl-orig"
    for code, text in spec.items():
        write_text(root / code / f"{code}.txt", text)
    return root


def _run(tmp_path, monkeypatch, forensic_cwd, spec):
    monkeypatch.setattr(f5, "CSL_ORIG", str(_corpus(tmp_path, spec)))
    f5.main()
    report = json.loads((forensic_cwd / "data/forensic/f5_report.json").read_text(encoding="utf-8"))
    with open(forensic_cwd / "data/forensic/f5_pair_summary.csv", encoding="utf-8") as fh:
        rows = {r["vs"]: r for r in csv.DictReader(fh)}
    with open(forensic_cwd / "data/forensic/f5_citation_order_examples.csv", encoding="utf-8") as fh:
        examples = list(csv.DictReader(fh))
    return report, rows, examples


def test_pure_helpers(pin):
    assert f5.sigil("<i>MBh.</i> 1,2") == "MBH"
    assert f5.sigil("R. 3,4") == "R"
    assert f5.dedup(["a", "b", "a", "", "c", "b"]) == ["a", "b", "c"]
    cf = f5.concordant_fraction
    pin("f5", "concordant.identity", 1.0, cf(["A", "B", "C"], ["A", "B", "C"]))
    pin("f5", "concordant.reversed", 0.0, cf(["A", "B", "C"], ["C", "B", "A"]))
    pin("f5", "concordant.one_swap_of_4", pytest.approx(5 / 6), cf(["A", "B", "C", "D"], ["A", "C", "B", "D"]))
    pin("f5", "concordant.two_shared_only", None, cf(["A", "B", "Q"], ["A", "B", "Z"]))
    pin("f5", "concordant.repeats_deduped", 1.0, cf(["A", "A", "B", "C", "A"], ["A", "B", "B", "C"]))
    pin("f5", "spearman.too_few", 0.0, f5.spearman([(1, 1), (2, 2), (3, 3), (4, 4)]))
    pin("f5", "spearman.monotone", 1.0, round(f5.spearman([(i, i * 2) for i in range(1, 6)]), 6))
    pin("f5", "spearman.reversed", -1.0, round(f5.spearman([(i, 6 - i) for i in range(1, 6)]), 6))


def test_sigil_pali_style_uses_first_arabic_digit():
    # The sigil cut is at the first ARABIC digit; roman numerals stay in the
    # sigil and the trailing ", " is stripped.
    assert f5.sigil("Pāṇ. vi, 2, 161") == "PĀṆ. VI"


def test_build_hand_counts(tmp_path, monkeypatch, pin):
    monkeypatch.setattr(f5, "CSL_ORIG", str(_corpus(tmp_path, POSITIVE)))
    mw = f5.build("mw")
    pin("f5", "build.mw.headwords", 3, len(mw))
    pin("f5", "build.mw.agni.cites", ["MBH", "R", "AV", "P"], mw["agni"]["cites"])
    pin("f5", "build.mw.agni.ncit", 4, mw["agni"]["ncit"])
    pin("f5", "build.mw.agni.sktoks", {"deva", "indra"}, mw["agni"]["sktoks"])
    pin("f5", "build.mw.agni.nsense(2 records, no {%)", 2, mw["agni"]["nsense"])
    pin("f5", "build.mw.deva", ([], 0, set(), 1),
        (mw["deva"]["cites"], mw["deva"]["ncit"], mw["deva"]["sktoks"], mw["deva"]["nsense"]))
    pwg = f5.build("pwg")
    pin("f5", "build.pwg.agni.sktoks", {"agni", "deva", "agnI"}, pwg["agni"]["sktoks"])
    pin("f5", "build.pwg.agni.nsense(1 {%)", 1, pwg["agni"]["nsense"])


def test_positive_fixture_pair_summary(tmp_path, monkeypatch, forensic_cwd, pin):
    report, rows, examples = _run(tmp_path, monkeypatch, forensic_cwd, POSITIVE)
    pin("f5", "rows", 6, len(rows))
    pin("f5", "row_order", ["PWG", "PW", "PWKVN", "SCH", "AP", "BEN"], [p["vs"] for p in report["pairs"]])
    pin("f5", "PWG.shared_headwords", "2", rows["PWG"]["shared_headwords"])
    pin("f5", "PWG.entries_with_order_signal", "1", rows["PWG"]["entries_with_order_signal"])
    pin("f5", "PWG.order", ("1.0", "100.0"), (rows["PWG"]["mean_citation_order_agreement"], rows["PWG"]["pct_identical_order"]))
    pin("f5", "PWG.content_jaccard", "0.25", rows["PWG"]["mean_content_jaccard"])
    pin("f5", "PWG.apparatus_spearman(n<5)", "0.0", rows["PWG"]["apparatus_size_spearman"])
    pin("f5", "PW.order", ("0.0", "0.0"), (rows["PW"]["mean_citation_order_agreement"], rows["PW"]["pct_identical_order"]))
    pin("f5", "PW.content_jaccard", "0.5", rows["PW"]["mean_content_jaccard"])
    pin("f5", "PWKVN.no_order_verdict", ("0", "", ""),
        (rows["PWKVN"]["entries_with_order_signal"], rows["PWKVN"]["mean_citation_order_agreement"], rows["PWKVN"]["mean_content_jaccard"]))
    pin("f5", "SCH.shared_headwords", "0", rows["SCH"]["shared_headwords"])
    pin("f5", "AP.order", "0.8333", rows["AP"]["mean_citation_order_agreement"])
    pin("f5", "AP.is_null", "True", rows["AP"]["is_null"])
    pin("f5", "null_mean_order", 0.8333, report["null_mean_order"])
    pin("f5", "n_order_examples_identical", 1, report["n_order_examples_identical"])
    pin("f5", "examples", [("PWG", "agni", "MBH R AV P")],
        [(e["dict"], e["headword"], e["shared_sources"]) for e in examples])


def test_petersburg_mean_drops_zero_rows_QUIRK(tmp_path, monkeypatch, forensic_cwd, pin):
    """Observed behaviour, not endorsed: ``pet_ord`` filters on truthiness, so a
    Petersburg dict whose mean order agreement is exactly 0.0 falls out of the
    Petersburg mean. With PWG=1.0 and PW=0.0 scored, the hand mean is 0.5; the
    script reports 1.0. If this pin ever fails because the script changed to
    0.5, that is the fix landing — update the pin, do not revert the fix."""
    report, _, _ = _run(tmp_path, monkeypatch, forensic_cwd, POSITIVE)
    pin("f5", "petersburg_mean_order(QUIRK: 0.0 dropped)", 1.0, report["petersburg_mean_order"])


def test_null_fixture_no_order_signal(tmp_path, monkeypatch, forensic_cwd, pin):
    report, rows, examples = _run(tmp_path, monkeypatch, forensic_cwd, NULL)
    pin("f5", "null.shared_headwords", ["1"] * 6, [rows[c]["shared_headwords"] for c in ("PWG", "PW", "PWKVN", "SCH", "AP", "BEN")])
    pin("f5", "null.entries_with_order_signal", ["0"] * 6, [rows[c]["entries_with_order_signal"] for c in rows])
    pin("f5", "null.mean_order_all_empty", [""] * 6, [rows[c]["mean_citation_order_agreement"] for c in rows])
    pin("f5", "null.content_all_empty", [""] * 6, [rows[c]["mean_content_jaccard"] for c in rows])
    pin("f5", "null.petersburg_mean_order", 0, report["petersburg_mean_order"])
    pin("f5", "null.null_mean_order", 0, report["null_mean_order"])
    pin("f5", "null.n_order_examples_identical", 0, report["n_order_examples_identical"])
    pin("f5", "null.examples_rows", 0, len(examples))
