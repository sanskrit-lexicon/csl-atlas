"""Pins for ``f4_shared_corrections`` (H4352).

The parsers (change-file, correctionform, printchange) and the two normalisers
are pure and pinned directly. main() reads ``PWGISSUES`` / ``CSLCORR`` (module
globals, repointed at tmp fixtures) and writes ``f4_report.json`` +
``shared_corrections.csv`` into the cwd — read back as the dry-run surface.

Hand derivation of the positive fixture
---------------------------------------
pwgissues/
  issue001fix  change_pwg_1: agni old <ls>MBh. 1,2</ls> ; deva old <ls>R. 3,4</ls>
               change_mw_1 : agni old <ls>MBh. 1,2</ls> ; soma old <ls>MBh. 5,5</ls>
               -> shared hw {agni}=1 · shared cit {MBH. 1,2}=1
  issue002fix  change_pwg_2 only (no mw file)          -> NOT a cross issue
  issue003fix  change_mw_3 : deva old <ls>R. 3,4</ls>
               change_pw_3 : indra old <ls>R. 3,4</ls>
               change_ap_3 : ignored (neither Petersburg nor MW)
               -> shared hw {}=0 · shared cit {R. 3,4}=1
  cross_issues = 2
  aggregate: PET hw {agni,deva,indra} ∩ MW hw {agni,soma,deva} = {agni,deva}
             PET cit {MBH. 1,2, R. 3,4} ∩ MW cit {MBH. 1,2, MBH. 5,5, R. 3,4}
                                                        = {MBH. 1,2, R. 3,4}
csl-corrections/2024/dictionaries/
  pwg/printchange_pwg.txt     tabular: agni  (print error, PET)
  pwg/correctionform_pwg.txt  deva, vala
  mw/printchange_mw.txt       prose quoting 'agni' and 'vala' (print errors, MW)
  mw/change_mw_9.txt          deva old <ls>R. 3,4</ls>
  -> PET corrected {agni,deva,vala}=3 · MW corrected {agni,vala,deva}=3
     both sides = 3 · print errors PET 1 / MW 2 · shared print {agni}=1
     citations fixed on both sides in this source = 0 (PET olds carry no <ls>)
  rows in shared_corrections.csv = |{agni,deva} ∪ {agni,deva,vala}| = 3,
  with in_pwgissues True,True,False (vala is corrections-only).
"""

import csv
import json

import pytest

import f4_shared_corrections as f4
from conftest import write_text


def _issue(root, name, files):
    for fname, text in files.items():
        write_text(root / "pwgissues" / name / fname, text)


def _fixture(tmp_path):
    _issue(tmp_path, "issue001fix", {
        "change_pwg_1.txt": ("; <L>100<k1>agni\n"
                             "10 old fire <ls>MBh. 1,2</ls> foo\n"
                             "10 new fire <ls>MBh. 1,3</ls> foo\n"
                             "; <L>200<k1>deva\n"
                             "20 old god <ls>R. 3,4</ls>\n"
                             "20 new god <ls>R. 3,5</ls>\n"),
        "change_mw_1.txt": ("; <L>300<k1>agni\n"
                            "5 old x <ls>MBh. 1,2</ls>\n"
                            "5 new x <ls>MBh. 1,3</ls>\n"
                            "; <L>400<k1>soma\n"
                            "7 old <ls>MBh. 5,5</ls>\n"
                            "7 new <ls>MBh. 5,6</ls>\n"),
    })
    _issue(tmp_path, "issue002fix", {
        "change_pwg_2.txt": "; <L>1<k1>indra\n1 old <ls>AV. 1,1</ls>\n1 new <ls>AV. 1,2</ls>\n",
    })
    _issue(tmp_path, "issue003fix", {
        "change_mw_3.txt": "; <L>1<k1>deva\n1 old <ls>R. 3,4</ls>\n1 new <ls>R. 3,6</ls>\n",
        "change_pw_3.txt": "; <L>2<k1>indra\n2 old <ls>R. 3,4</ls>\n2 new <ls>R. 3,7</ls>\n",
        "change_ap_3.txt": "; <L>3<k1>agni\n3 old <ls>R. 3,4</ls>\n3 new <ls>R. 3,8</ls>\n",
    })
    corr = tmp_path / "csl-corrections" / "2024" / "dictionaries"
    write_text(corr / "pwg" / "printchange_pwg.txt", "1,2\tagni\tagnl\tagni\ttypo\n")
    write_text(corr / "pwg" / "correctionform_pwg.txt",
               "Case 1: something hw=deva\nold = alt\nnew = neu\n"
               "Case 2: something hw=vala\nold = alt2\nnew = neu2\n")
    write_text(corr / "mw" / "printchange_mw.txt",
               "The headword 'agni' is misprinted; also 'vala' is wrong.\n")
    write_text(corr / "mw" / "change_mw_9.txt",
               "; <L>1<k1>deva\n3 old <ls>R. 3,4</ls>\n3 new <ls>R. 3,9</ls>\n")


def _fixture_null(tmp_path):
    """One cross issue whose two sides fix different headwords and different
    citations; corrections that never touch the same normalised headword."""
    _issue(tmp_path, "issue001fix", {
        "change_pwg_1.txt": "; <L>1<k1>agni\n1 old <ls>MBh. 1,2</ls>\n1 new <ls>MBh. 1,3</ls>\n",
        "change_mw_1.txt": "; <L>2<k1>soma\n2 old <ls>R. 9,9</ls>\n2 new <ls>R. 9,8</ls>\n",
    })
    corr = tmp_path / "csl-corrections" / "2024" / "dictionaries"
    write_text(corr / "pwg" / "printchange_pwg.txt", "1,2\tagni\tagnl\tagni\ttypo\n")
    write_text(corr / "mw" / "printchange_mw.txt", "The headword 'vala' is wrong.\n")


def _run(tmp_path, monkeypatch, forensic_cwd):
    monkeypatch.setattr(f4, "PWGISSUES", str(tmp_path / "pwgissues"))
    monkeypatch.setattr(f4, "CSLCORR", str(tmp_path / "csl-corrections"))
    f4.main()
    report = json.loads((forensic_cwd / "data/forensic/f4_report.json").read_text(encoding="utf-8"))
    with open(forensic_cwd / "data/forensic/shared_corrections.csv", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return report, rows


def test_normalisers_and_name_helpers():
    assert f4.norm_hw("a/gni-˚") == "agni"
    assert f4.norm_hw("k0a") == "ka"          # documented quirk: the digit 0 is dropped
    assert f4.norm_cit("<i>MBh.</i> 1,2.") == "MBH. 1,2"
    assert f4.norm_cit("  r.  3,4 ; ") == "R. 3,4"
    assert f4.dict_of("change_pwg_12.txt") == "pwg"
    assert f4.dict_of("notes_pwg.txt") is None
    assert f4.side("pwg") == "PET" and f4.side("sch") == "PET"
    assert f4.side("mw") == "MW" and f4.side("ap") is None


def test_parse_change_file_records(tmp_path, pin):
    p = write_text(tmp_path / "change_pwg_1.txt",
                   "; <L>100<k1>agni\n10 old fire\n10 new flame\n"
                   "; <L>200<k1>deva\n20 ins added line\n21 del gone\n")
    recs = f4.parse_change_file(str(p))
    pin("f4", "parse_change_file.records", 3, len(recs))
    pin("f4", "parse_change_file.first", ("agni", "10", "fire", "flame"), recs[0])
    pin("f4", "parse_change_file.ins", ("deva", "20", "", "added line"), recs[1])
    pin("f4", "parse_change_file.del", ("deva", "21", "", "gone"), recs[2])
    assert f4.parse_change_file(str(tmp_path / "missing.txt")) == []


def test_parse_correctionform_and_printchange(tmp_path, pin):
    cf = write_text(tmp_path / "correctionform.txt",
                    "Case 1: hw=deva\nold = alt\nnew = neu\nCase 2: hw=vala\nnew = only\n")
    recs = f4.parse_correctionform(str(cf))
    pin("f4", "parse_correctionform", [("deva", "alt", "neu"), ("vala", "", "only")], recs)
    tab = write_text(tmp_path / "printchange_pwg.txt", "1,2\tagni\tagnl\tagni\ttypo\nnot a row\n")
    pin("f4", "parse_printchange.tabular", [("agni", "agnl", "agni")], f4.parse_printchange(str(tab)))
    prose = write_text(tmp_path / "printchange_mw.txt", "Misprints at 'agni' and 'vala'.\n")
    pin("f4", "parse_printchange.prose", [("agni", "", ""), ("vala", "", "")], f4.parse_printchange(str(prose)))


def test_collect_splits_sides_and_citations(pin):
    records = [("pwg", "agni", "1", "x <ls>MBh. 1,2</ls>", "y"),
               ("mw", "agni", "2", "<ls>MBh. 1,2</ls> <ls>R. 3</ls>", ""),
               ("ap", "agni", "3", "<ls>MBh. 1,2</ls>", "")]   # ignored side
    hw, cit = f4.collect(records)
    pin("f4", "collect.hw", ({"agni"}, {"agni"}), (set(hw["PET"]), set(hw["MW"])))
    pin("f4", "collect.cit", ({"MBH. 1,2"}, {"MBH. 1,2", "R. 3"}), (set(cit["PET"]), set(cit["MW"])))


def test_positive_fixture_report(tmp_path, monkeypatch, forensic_cwd, pin):
    _fixture(tmp_path)
    report, rows = _run(tmp_path, monkeypatch, forensic_cwd)
    pin("f4", "source1_cross_issues", 2, report["source1_cross_issues"])
    pin("f4", "issue_breakdown", [("issue001fix", 1, 1), ("issue003fix", 0, 1)],
        [(r["issue"], r["shared_headwords"], r["shared_citations"]) for r in report["issue_breakdown"]])
    pin("f4", "shared_headwords_issue", ["agni", "deva"], report["shared_headwords_issue"])
    pin("f4", "shared_citations_issue", ["MBH. 1,2", "R. 3,4"], report["shared_citations_issue"])
    pin("f4", "source2_pet_corrected_hw", 3, report["source2_pet_corrected_hw"])
    pin("f4", "source2_mw_corrected_hw", 3, report["source2_mw_corrected_hw"])
    pin("f4", "shared_headwords_corpus", 3, report["shared_headwords_corpus"])
    pin("f4", "shared_citations_corpus", 0, report["shared_citations_corpus"])
    pin("f4", "print_errors", (1, 2), (report["print_errors_pet"], report["print_errors_mw"]))
    pin("f4", "shared_print_error_headwords", ["agni"], report["shared_print_error_headwords"])
    pin("f4", "n_shared_correction_rows", 3, report["n_shared_correction_rows"])
    pin("f4", "csv.rows", 3, len(rows))
    pin("f4", "csv.in_pwgissues", [("agni", "True"), ("deva", "True"), ("vala", "False")],
        [(r["headword"], r["in_pwgissues"]) for r in rows])
    pin("f4", "csv.agni.pet_dict", "pwg", rows[0]["pet_dict"])


def test_null_fixture_reports_zero_shared(tmp_path, monkeypatch, forensic_cwd, pin):
    _fixture_null(tmp_path)
    report, rows = _run(tmp_path, monkeypatch, forensic_cwd)
    pin("f4", "null.source1_cross_issues", 1, report["source1_cross_issues"])
    pin("f4", "null.issue_breakdown", [("issue001fix", 0, 0)],
        [(r["issue"], r["shared_headwords"], r["shared_citations"]) for r in report["issue_breakdown"]])
    pin("f4", "null.shared_headwords_issue", [], report["shared_headwords_issue"])
    pin("f4", "null.shared_citations_issue", [], report["shared_citations_issue"])
    pin("f4", "null.shared_headwords_corpus", 0, report["shared_headwords_corpus"])
    pin("f4", "null.shared_citations_corpus", 0, report["shared_citations_corpus"])
    pin("f4", "null.print_errors", (1, 1), (report["print_errors_pet"], report["print_errors_mw"]))
    pin("f4", "null.shared_print_error_headwords", [], report["shared_print_error_headwords"])
    pin("f4", "null.n_shared_correction_rows", 0, report["n_shared_correction_rows"])
    pin("f4", "null.csv.rows", 0, len(rows))
