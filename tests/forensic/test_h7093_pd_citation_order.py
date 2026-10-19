"""Pins for H7093: full-population PD citation order and its null model.

The 20 gold rows in ``h7093_gold_rows.tsv`` were drawn deterministically from the
committed TSV (10 mixed, 10 monotone, at least three dated citations each) so a
parser or verdict change cannot pass silently.  The summary is recomputed from
the TSV and compared with the committed JSON; the 10,000-permutation null is not
re-run here (the costly check belongs to ``--check``), but its stored observed
counts must agree with the summary.
"""

import csv
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
FORENSIC = pathlib.Path(__file__).resolve().parent
for p in (str(ROOT / "scripts"), str(FORENSIC)):
    if p not in sys.path:
        sys.path.insert(0, p)

import pd_citation_order_full as h7093


def load_tsv(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def test_population_funnel_reconciles_with_h6943_and_has_gold_rows():
    summary = json.loads((ROOT / "data" / "pd" / "pd_citation_order_full_summary.json").read_text(encoding="utf-8"))
    pop = summary["population"]
    rows = load_tsv(ROOT / "data" / "pd" / "pd_citation_order_full.tsv")
    gold = load_tsv(FORENSIC / "h7093_gold_rows.tsv")

    assert pop["entries"] == 107620
    assert pop["entries_with_sense_markers"] == 12770
    assert pop["divisions_total"] == 36449
    assert pop["divisions_ge2_citations"] == 13358
    assert pop["h6943_eligible_entries"] == 2118
    assert pop["eligible_divisions_3clock"] == 4148
    assert pop["eligible_divisions_4clock"] == 9689
    assert len(rows) == pop["eligible_divisions_4clock"]
    assert len(gold) == 20
    assert sum(1 for r in gold if r["verdict"] == "inverted") == 10
    assert sum(1 for r in gold if r["verdict"] == "monotone") == 10


def test_gold_rows_match_the_committed_tsv():
    rows = {(r["L"], r["division"]): r for r in load_tsv(ROOT / "data" / "pd" / "pd_citation_order_full.tsv")}
    gold = load_tsv(FORENSIC / "h7093_gold_rows.tsv")
    fields = ("verdict", "direction", "decidable_clocks", "tau", "adjacent_rate", "n_for_tau", "citation_sequence")
    for g in gold:
        live = rows[(g["L"], g["division"])]
        for field in fields:
            assert live[field] == g[field], f"{g['L']}/{g['division']} {field}: {live[field]!r} != {g[field]!r}"


def test_summary_recomputed_from_tsv_matches_json():
    rows = load_tsv(ROOT / "data" / "pd" / "pd_citation_order_full.tsv")
    committed = json.loads((ROOT / "data" / "pd" / "pd_citation_order_full_summary.json").read_text(encoding="utf-8"))
    assert h7093.summarize(rows) == committed["summary"]
    assert committed["null"]["reps"] == 10000
    for clock in ("pd_swc", "dcs", "dm", "imprint", "any"):
        n = committed["summary"][clock]["n_decidable"]
        k = committed["summary"][clock]["n_inverted"]
        o = committed["null"]["clocks"][clock]
        assert o["n_decidable"] == n
        assert o["observed_mixed"] == k
        assert o["observed_rate"] == committed["summary"][clock]["mixed_rate"]


def test_clopper_pearson_bounds_are_rounded_to_a_portable_precision():
    """The published CI must not carry platform-dependent last bits.

    ``math.lgamma`` differs between libm builds in its last bit and the
    80-step bisection amplifies that into a ~1e-14 spread of the bound, so the
    committed summary JSON could not be reproduced byte-for-byte off the
    machine that built it.  The bound is therefore rounded to 1e-10 -- seven
    orders below the 0.1 % reporting precision.
    """
    assert h7093.CI_DP == 10
    for k, n, lo, hi in (
        (428, 1047, 0.3788236665, 0.4392645766),
        (1027, 2989, 0.3265606234, 0.3609324109),
        (1840, 3877, 0.4587705357, 0.4904553106),
        (5614, 9501, 0.5809195323, 0.600795053),
        (5676, 9689, 0.5759346628, 0.595651656),
    ):
        assert h7093.clopper_pearson(k, n) == (lo, hi)
    committed = json.loads(
        (ROOT / "data" / "pd" / "pd_citation_order_full_summary.json").read_text(encoding="utf-8")
    )
    for clock in ("pd_swc", "dcs", "dm", "imprint", "any"):
        for bound in committed["summary"][clock]["ci95_mixed"]:
            assert bound == round(bound, h7093.CI_DP)


def test_summary_means_use_exact_summation_not_the_builtin_sum():
    """The means must not depend on the interpreter's float ``sum``.

    CPython 3.12 changed the builtin ``sum`` for floats to Neumaier
    compensation, so a 3.11 runner (the CI matrix) and a 3.12+ box produce
    different last bits for the same 9,689-term sum -- which is what made
    ``forensic-pins`` red.  ``math.fsum`` is correctly rounded and therefore
    identical on every interpreter and platform, and it is the value the
    committed artefact already carries.
    """
    rows = load_tsv(ROOT / "data" / "pd" / "pd_citation_order_full.tsv")
    dec = [r for r in rows if r["verdict"] != "undecidable"]
    tau = [float(r["tau"]) for r in dec]
    n = len(dec)
    naive = 0.0
    for v in tau:
        naive += v
    naive /= n
    exact = math.fsum(tau) / n
    summary = h7093.summarize(rows)
    committed = json.loads(
        (ROOT / "data" / "pd" / "pd_citation_order_full_summary.json").read_text(encoding="utf-8")
    )
    assert summary["any"]["mean_tau"] == exact
    assert committed["summary"]["any"]["mean_tau"] == exact
    # the naive sum is a different number on this frozen population -- that
    # difference is exactly what the pin exists to catch
    assert naive != exact


def test_verdict_sentence_is_clock_specific_and_adjudication_is_open():
    report = (ROOT / "reports" / "PD_CITATION_ORDER_FULL_2026.md").read_text(encoding="utf-8")
    assert "Strong form (strict ascending in every division):** refuted" in report
    assert "survives for the work-date clocks DCS" in report
    assert "does **not** survive for PD's own SWC clock" in report
    assert "human annotation outstanding" in report
    assert "H6943 reconciliation anchor:** entries" in report
