"""Pins for the H6947 PD volume table and the H6942 marking rule it reuses.

The marking expectations are hand-derived from the miniature entries below, not
produced by the parser.  The ledger assertions pin the Deccan College
transcription shipped in data/pd/pd_publication_ledger.tsv.
"""

import csv
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
for p in (str(ROOT / "scripts"), str(ROOT / "scripts" / "lib")):
    if p not in sys.path:
        sys.path.insert(0, p)

import pd_marked_sources as m


def test_leading_source_and_direct_mark():
    assert m.leading_source("DBHS") == "DBHS"
    assert m.leading_source("MW, APTE") == "MW"
    assert m.leading_source("a gloss") is None
    assert m.entry_marks("[DBHS] text [PW]") == ["DBHS", "PW"]
    assert m.marked_entry("[DBHS] text [PW]")


def test_dbhs_gloss_is_not_a_mark_but_pointer_is():
    assert not m.marked_entry("baby [DBHS cloth, garment]")
    assert m.marked_entry("[DBHS. q. under √i]")


def test_long_brackets_are_capped_but_long_mw_survives_uncapped():
    long = "MW " + "x" * 50
    entry = f"[{long}]"
    assert not m.marked_entry(entry)
    assert m.entry_marks(entry) == ["MW"]
    assert m.entry_marks("[" + "PW " + "x" * 50 + "]") == []


def test_vac_in_a_source_list_counts_only_uncapped():
    entry = "[MW., Vācas.]"
    assert m.entry_marks(entry) == ["MW", "VAC"]
    assert m.entry_marks(entry, capped=True) == ["MW"]


def test_ledger_is_complete_and_marks_the_print_only_tail():
    path = ROOT / "data" / "pd" / "pd_publication_ledger.tsv"
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    assert len(rows) == 35
    assert sum(1 for r in rows if r["in_digital_text"] == "yes") == 24
    digital = [r for r in rows if r["in_digital_text"] == "yes"]
    assert min(int(r["pp_lo"]) for r in digital) == 1
    assert max(int(r["pp_hi"]) for r in digital) == 4328
    assert [r["ledger_id"] for r in digital[:3]] == ["1.1", "1.2", "1.3"]
    assert [r["ledger_id"] for r in digital[-3:]] == ["8.1", "8.2", "8.3"]
    assert all(r["in_digital_text"] == "no" for r in rows[24:])
