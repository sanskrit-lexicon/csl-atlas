"""Pins for the H7109 page-economics table.

Every expectation below is hand-derived from the miniature machine texts written
in the test, not produced by the parser and copied back.  The point of the pins
is the *unit grammar*, which is where this measurement can silently go wrong:

* an entry header's ``<L>`` number may carry a sub-entry suffix (``14148.004``),
  so a digits-only pattern drops 636 PWG entries;
* a printed line break is ``<div n="lb">``, and the line that opens an entry has
  none, so "line-divisions" is not "printed lines";
* PD numbers a column (``volume-page`` + a/b), PWG numbers a page-col whose two
  columns are the odd (left) and even (right) numbers of one page.
"""

import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
for p in (str(ROOT / "scripts"), str(ROOT / "scripts" / "lib")):
    if p not in sys.path:
        sys.path.insert(0, p)

import pd_page_economics as econ

PINS_TSV = ROOT / "tests" / "forensic" / "h7109_page_economics_pins.tsv"
TSV = ROOT / "data" / "pd" / "page_economics.tsv"
OED_JSON = ROOT / "data" / "pd" / "oed_page_sample.json"

PD_FIXTURE = (
    "<L>1<pc>1-0001a<k1>a<k2>a\n"
    "first line\n"
    '<div n="lb">second\n'
    "<LEND>\n"
    "<L>2<pc>1-0001a<k1>b<k2>b\n"
    "[Page1-0001a+ 64]\n"
    "x\n"
    "<LEND>\n"
)

PWG_FIXTURE = (
    "<L>1<pc>1-0001<k1>a<k2>a\n"
    "x\n"
    "<LEND>\n"
    "<L>2<pc>1-0002<k1>b<k2>b\n"
    "y\n"
    "<LEND>\n"
    "<L>14148.004<pc>1-0003<k1>c<k2>c\n"
    "z\n"
    "<LEND>\n"
)


def _write(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return str(path)


def test_pd_line_divisions_are_not_printed_lines(tmp_path):
    m = econ.measure_text(_write(tmp_path, "pd.txt", PD_FIXTURE), "pd")
    assert m["entries"] == 2
    # one <div n="lb"> in the whole fixture
    assert m["lb_divs"] == 1
    # printed lines = the break + the two entry-opening lines
    assert m["printed_lines"] == 3 == m["lb_divs"] + m["entries"]


def test_pd_characters_keep_the_h6947_body_definition(tmp_path):
    m = econ.measure_text(_write(tmp_path, "pd.txt", PD_FIXTURE), "pd")
    # entry 1: "first line" + " " + lb-tag-as-space + "second" = 18
    # entry 2: "[Page1-0001a+ 64]" + " " + "x"             = 19
    assert m["chars"] == 37
    # page markers and every body line stay in the line count, as in H6947
    assert m["text_lines"] == 4


def test_pd_numbers_a_column_and_the_page_is_recovered(tmp_path):
    m = econ.measure_text(_write(tmp_path, "pd.txt", PD_FIXTURE), "pd")
    assert m["column_codes"] == 1           # both entries sit in column 1-0001a
    assert m["page_numbers"] == 1           # ... which is one printed page
    assert m["max_page"] == 1
    assert m["entries_per_column_dist"]["n"] == 1
    assert m["entries_per_page_dist"]["n"] == 1


def test_pwg_odd_and_even_columns_are_one_page(tmp_path):
    m = econ.measure_text(_write(tmp_path, "pwg.txt", PWG_FIXTURE), "pwg")
    assert m["column_codes"] == 3           # 1-0001, 1-0002, 1-0003
    # pwg-meta2.txt: odd = left column, even = right column of the same page
    assert m["page_numbers"] == 2           # 1-0001/1-0002 -> page 1, 1-0003 -> page 2
    assert m["printed_pages"] == 2          # ceil(3 / 2)
    assert m["entries_per_page_dist"]["max"] == 2


def test_subentry_headers_are_not_dropped(tmp_path):
    """A digits-only <L> pattern silently loses every N.M sub-entry."""
    m = econ.measure_text(_write(tmp_path, "pwg.txt", PWG_FIXTURE), "pwg")
    assert m["entries"] == 3
    assert m["unmatched_headers"] == 0


def test_pwg_has_no_printed_line_markup(tmp_path):
    m = econ.measure_text(_write(tmp_path, "pwg.txt", PWG_FIXTURE), "pwg")
    assert m["lb_divs"] == 0
    # body lines are all PWG offers, and they are machine lines, not printed ones
    assert m["text_lines"] == 3


def test_oed_sample_requires_three_random_pages_and_page_ids():
    oed = json.loads(OED_JSON.read_text(encoding="utf-8"))
    agg = econ.oed_rows(oed)
    assert agg["n_pages"] == 3
    assert agg["pages"] == [78, 362, 154]
    assert agg["cols"] == 3
    for page in oed["pages"]:
        assert page["printed_page"] and page["leaf"]


def test_oed_chars_per_page_is_columns_times_column_chars():
    oed = json.loads(OED_JSON.read_text(encoding="utf-8"))
    agg = econ.oed_rows(oed)
    # (5664 + 5823) / 2 = 5743.5; x 3 columns
    assert agg["chars_per_column"] == 5743.5
    assert agg["chars_per_page"] == 17230.5


def test_oed_anchor_page_is_not_part_of_the_mean():
    oed = json.loads(OED_JSON.read_text(encoding="utf-8"))
    agg = econ.oed_rows(oed)
    # the fire anchor is one 292-line entry; it must not sit in the sample mean
    assert agg["anchor"]["printed_page"] == 242
    assert sum(p["printed_lines"] for p in oed["pages"] if p["role"] == "random") == 867
    assert round(agg["lines_per_page"], 1) == 289.0


def test_committed_tsv_carries_the_pinned_totals():
    with TSV.open(encoding="utf-8", newline="") as fh:
        rows = {r["dictionary"]: r for r in csv.DictReader(fh, delimiter="\t")}
    assert set(rows) == {"PD", "PWG", "OED"}
    assert rows["PD"]["entries"] == "107630"
    assert rows["PD"]["lines"] == "440003"
    assert rows["PD"]["characters"] == "42247645"
    assert rows["PWG"]["entries"] == "123366"
    assert rows["PWG"]["lines"] == "223497"
    assert rows["OED"]["columns"] == "3"


def test_pins_file_is_ten_rows_and_every_key_is_known():
    with PINS_TSV.open(encoding="utf-8", newline="") as fh:
        pins = list(csv.DictReader(fh, delimiter="\t"))
    assert len(pins) == 10
    known = {
        "pd_entries", "pd_line_divisions", "pd_printed_lines", "pd_characters",
        "pd_column_codes", "pd_page_numbers", "pwg_entries", "pwg_machine_lines",
        "pwg_column_codes", "pwg_printed_pages",
    }
    assert {p["key"] for p in pins} == known
    for pin in pins:
        float(pin["expected"])  # every pin is numeric
