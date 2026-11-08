"""Pins for the PD-vs-control sense-order comparison (H7116).

The published verdict must not flip silently. This file re-derives the verdict
from the committed summary under the pre-registered rule, then pins the numbers
the verdict rests on — so a changed τ, a changed denominator, a softened floor or
a rewritten verdict line all fail here instead of in a footnote somewhere.

It does not recompute the measurement (that is
``scripts/pd_sense_order_compare.py --check``, minutes of permutation nulls); it
checks the committed artifact against itself and against the PD summary it is
anchored to.
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
SUMMARY = ROOT / "data" / "pd" / "pd_sense_order_compare_summary.json"
PD_SUMMARY = ROOT / "data" / "pd" / "pd_sense_order_summary.json"
REPORT = ROOT / "reports" / "PD_SENSE_ORDER_COMPARE_2026.md"


def load():
    return json.loads(SUMMARY.read_text(encoding="utf-8"))


def test_rule_is_the_pre_registered_one():
    s = load()
    assert s["primary_clock"] == "dm"
    assert s["rule"]["effect_floor"] == 0.10
    assert s["rule"]["alpha"] == 0.05
    assert s["rule"]["min_power"] == 30
    assert s["rule"]["reps"] == 5000
    assert s["rule"]["holm"] is True


def test_verdict_follows_from_the_committed_rows():
    """Re-apply the rule to the committed numbers; a silent flip fails here."""
    s = load()
    rows = s["verdict"]["rows"]
    scored = [d for d, r in rows.items() if r["delta_tau"] is not None]
    assert len(scored) >= 2
    should_stand = all(
        rows[d]["delta_tau"] >= s["rule"]["effect_floor"] and rows[d]["p_holm"] <= s["rule"]["alpha"]
        for d in scored
    )
    expected = "STAND" if should_stand else "WITHDRAWN"
    assert s["verdict"]["status"] == expected, (
        f"committed verdict {s['verdict']['status']!r} does not follow from its own rows "
        f"(expected {expected!r})"
    )


def test_withdrawn_because_pwg_and_mw_fail_the_floor():
    s = load()
    assert s["verdict"]["status"] == "WITHDRAWN"
    rows = s["verdict"]["rows"]
    assert rows["pwg"]["clears_floor"] is False
    assert rows["mw"]["clears_floor"] is False
    # the decisive reversal: a non-historical dictionary is MORE chronological
    assert rows["pwg"]["delta_tau"] < 0
    assert rows["pwg"]["delta_tau_ci95"][1] < 0
    # MW is the close call, not the decisive one
    assert -0.11 < rows["mw"]["delta_tau"] < 0.10


def test_primary_clock_pins():
    """τ and denominators on the primary (dm) clock, 3 dp."""
    s = load()
    expected = {                       # dict: (τ, entries ≥3 senses)
        "pwg": (0.406, 3343),
        "pw": (-0.041, 281),
        "mw": (0.227, 3882),
        "ap": (-0.042, 1622),
    }
    for code, (tau, n) in expected.items():
        clock = s["controls"][code]["clocks"]["dm"]
        assert round(clock["mean_tau_position_vs_earliest"], 3) == tau, code
        assert clock["entries_three_plus_senses"] == n, code
    pd = s["pd_clocks"]["dm"]
    assert round(pd["mean_tau_position_vs_earliest"], 3) == 0.323
    assert pd["entries_three_plus_senses"] == 706


def test_pd_row_matches_the_pd_summary_it_is_anchored_to():
    s, pd = load(), json.loads(PD_SUMMARY.read_text(encoding="utf-8"))
    for clock in s["clocks"]:
        mine, theirs = s["pd_clocks"][clock], pd["clocks"][clock]
        for key in ("entries_with_series", "entries_two_senses", "entries_three_plus_senses",
                    "two_sense_later_sense_later_date", "two_sense_ties", "two_sense_backward"):
            assert mine[key] == theirs[key], f"{clock}.{key}"
        for key in ("mean_tau_position_vs_earliest", "two_sense_forward_rate"):
            assert abs(mine[key] - theirs[key]) < 1e-9, f"{clock}.{key}"
        assert abs(mine["median_last_minus_first_years"]
                   - theirs["median_last_minus_first_years"]) < 1e-9, f"{clock}.median"


def test_delta_tau_and_holm_pins():
    s = load()
    rows = s["verdict"]["rows"]
    assert round(rows["pwg"]["delta_tau"], 3) == -0.082
    assert round(rows["pw"]["delta_tau"], 3) == 0.364
    assert round(rows["mw"]["delta_tau"], 3) == 0.096
    assert round(rows["ap"]["delta_tau"], 3) == 0.365
    assert rows["pwg"]["p_holm"] == 1.0
    assert round(rows["mw"]["p_holm"], 4) == 0.0008


def test_exact_cis_bracket_their_point_estimate():
    s = load()
    for code, ctl in s["controls"].items():
        for clock, c in ctl["clocks"].items():
            lo, hi = c["two_sense_forward_rate_ci95"]
            rate = c["two_sense_forward_rate"]
            assert 0.0 <= lo < rate < hi <= 1.0, f"{code}/{clock} forward CI {lo}..{hi} vs {rate}"
            band = c["null"]
            assert band["p2_5"] < 0 < band["p97_5"], f"{code}/{clock} null band excludes 0"


def test_resolution_denominators_are_recorded():
    """No point estimate without its denominator."""
    s = load()
    expected = {                       # dict: (resolved, total <ls>)
        "pwg": (483_000, 720_203),
        "pw": (50_337, 97_781),
        "mw": (310_664, 320_828),
        "ap": (55_766, 66_809),
    }
    for code, (resolved, total) in expected.items():
        stats = s["controls"][code]["stats"]
        assert stats["ls_resolved"] == resolved, code
        assert stats["ls_instances"] == total, code
        assert stats["sense_divisions"] > 0


def test_report_carries_the_verdict_and_the_amendment():
    text = REPORT.read_text(encoding="utf-8")
    s = load()
    assert s["verdict"]["status"] in text
    assert "no comparative test has yet separated" in text   # the A68 sentence being replaced
    assert "not** distinctive" in text or "not distinctive" in text
