"""Pins for PD sense-order chronology (H7093 follow-up).

The published numbers in ``reports/PD_SENSE_ORDER_2026.md`` and
``data/pd/pd_sense_order_summary.json`` are recomputed here from the committed
TSV without the permutation null (that costs minutes and is the job of
``scripts/pd_sense_order.py --check``); the cheap counts and the two τ values
are pinned so a parser change cannot pass silently.
"""

import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
FORENSIC = pathlib.Path(__file__).resolve().parent
for p in (str(ROOT / "scripts"), str(FORENSIC)):
    if p not in sys.path:
        sys.path.insert(0, p)

import pd_sense_order as sense


def load_rows():
    with open(ROOT / "data" / "pd" / "pd_citation_order_full.tsv", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def test_summary_recomputes_from_tsv():
    committed = json.loads(
        (ROOT / "data" / "pd" / "pd_sense_order_summary.json").read_text(encoding="utf-8")
    )
    rows = load_rows()
    for clock in sense.CLOCKS:
        series = sense.entry_series(rows, clock)
        summary = sense.summarise(series)
        summary.pop("shifts")
        published = committed["clocks"][clock]
        for key, value in summary.items():
            assert published[key] == value, f"{clock}.{key}: {value!r} != {published[key]!r}"


def test_work_date_clocks_are_outside_the_null_band():
    committed = json.loads(
        (ROOT / "data" / "pd" / "pd_sense_order_summary.json").read_text(encoding="utf-8")
    )
    for clock in ("dcs", "dm"):
        c = committed["clocks"][clock]
        tau = c["mean_tau_position_vs_earliest"]
        null = c["null"]
        assert tau > null["p97_5"], f"{clock}: tau {tau} inside null band"
        assert tau > 0.30, f"{clock}: tau {tau} below the published tendency"


def test_pd_swc_is_not_used_as_evidence():
    """The SWC clock sees 15 works; its row must not be quoted as a result."""
    committed = json.loads(
        (ROOT / "data" / "pd" / "pd_sense_order_summary.json").read_text(encoding="utf-8")
    )
    swc = committed["clocks"]["pd_swc"]
    assert swc["two_sense_ties"] > 100  # ties dominate: not evidence either way
