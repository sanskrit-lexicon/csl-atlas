"""Pins for H7110: PD family composition (compound / derivative / simplex).

Two kinds of pin, and they are separate on purpose.

*GOLD ROWS* — ``h7110_gold_rows.tsv`` holds 20 rows read out of PD's own printed
analysis parenthesis and classified BY HAND from the printed form: a two-member
analysis ending in a substantive member is a compound (``anna-bhāṇḍa``), a
two-member analysis ending in one of the published suffixes is a derivative
(``annabhojana-tva``), one member is simplex (``ánna``). Nothing in this file
regenerates them from the script they check.

*CORPUS PINS* — the totals in ``data/pd/pd_family_composition.json`` and its TSV
sibling are pinned to the values the report quotes. They are re-derivable only
with the external PDScan source, so the test reads the committed artifacts (the
same pattern as ``test_h7093_pd_citation_order.py``).

Rationale and the corpus-level discussion: reports/PD_FAMILY_COMPOSITION_2026.md.
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

import pd_family_composition as h7110

JSON = ROOT / "data" / "pd" / "pd_family_composition.json"
TSV = ROOT / "data" / "pd" / "pd_family_composition.tsv"
GOLD = FORENSIC / "h7110_gold_rows.tsv"


def _rows():
    with open(TSV, encoding="utf-8", newline="") as fh:
        return {r["family"]: r for r in csv.DictReader(fh, delimiter="\t")}


def _env():
    return json.loads(JSON.read_text(encoding="utf-8"))


def _gold():
    with open(GOLD, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


# ------------------------------------------------------------------ rule pins
def test_gold_rows_are_twenty_and_cover_every_family():
    gold = _gold()
    assert len(gold) == 20
    assert {r["family"] for r in gold} == {
        "anna", "agni", "atha", "apa", "anya", "antar",
        "privative a-", "negative an-",
    }
    assert {r["class"] for r in gold} == {"compound", "derivative", "simplex"}


def test_gold_rows_classify_as_hand_classified():
    for r in _gold():
        assert h7110.classify(r["analysis_printed"]) == r["class"], r


def test_members_strip_accents_and_split_on_dashes():
    assert h7110.members("ánna") == ["anna"]      # precomposed accent stripped
    assert h7110.members("a\u0301nna") == ["anna"]  # combining accent stripped
    assert h7110.members("a-chandomá") == ["a", "chandoma"]
    assert h7110.members("á-cyuta") == ["a", "cyuta"]        # accented privative prefix
    assert h7110.members("antarā-bhāsa-maya") == ["antarā", "bhāsa", "maya"]
    assert h7110.members("-atha") == ["atha"]


def test_correction_block_is_not_an_analysis():
    block = "<L>1<pc>1-1a<k1>x<k2>x\n{#x#}¦ ({{a-kārya->a-kārya||20160404|JF|u}})"
    analysis, is_corr = h7110.first_line_paren(block)
    assert analysis is None and is_corr is True


def test_analysis_is_read_from_the_first_body_line_only():
    block = "<L>1<pc>1-1a<k1>x<k2>x\n{#x#}¦ (anna-ka) {%n.%}\n<div n=\"lb\">later (not-this)"
    analysis, _ = h7110.first_line_paren(block)
    assert analysis == "anna-ka"


def test_suffix_set_is_the_published_fifteen():
    assert len(h7110.SUFFIXES) == 15
    for s in ("tva", "tā", "tara", "tama", "maya", "aka", "ana", "ita", "in",
              "mat", "vat", "tṛ", "tas", "ya", "ka"):
        assert s in h7110.SUFFIXES


# ------------------------------------------------------------- population pins
def test_population_reconciles_the_a68_draft_exactly():
    pop = _env()["population"]
    assert pop["classified_headwords"] == 102747
    assert pop["correction_block_headwords"] == 380
    assert pop["reconciled_total"] == 103127      # the A68 draft's figure
    assert pop["delta_vs_pin"] == 0
    assert pop["within_band"] is True


def test_whole_alphabet_split_is_pinned():
    comp = _env()["composition"]
    assert comp["classified"] == 102747
    assert (comp["compound_n"], comp["derivative_n"], comp["simplex_n"]) == (
        72632, 12670, 17445)
    assert (comp["compound_pct"], comp["derivative_pct"], comp["simplex_pct"]) == (
        70.7, 12.3, 17.0)
    assert round(sum(comp[k] for k in
                     ("compound_pct", "derivative_pct", "simplex_pct")), 1) == 100.0


def test_reference_families_match_the_a68_table_counts():
    rows = _rows()
    assert (int(rows["anna"]["pd_headwords"]), int(rows["anna"]["pwg_headwords"])) == (877, 33)
    assert (int(rows["agni"]["pd_headwords"]), int(rows["agni"]["pwg_headwords"])) == (2312, 170)
    assert float(rows["anna"]["compound_pct"]) == 78.1
    assert float(rows["agni"]["derivative_pct"]) == 14.0
    assert float(rows["anna"]["simplex_pct"]) == 13.8
    assert float(rows["agni"]["simplex_pct"]) == 11.4


def test_atha_is_the_qualifying_function_word():
    row = _rows()["atha"]
    assert (int(row["pd_headwords"]), int(row["pwg_headwords"])) == (173, 24)
    assert (float(row["compound_pct"]), float(row["derivative_pct"]),
            float(row["simplex_pct"])) == (63.1, 7.5, 29.4)


def test_ledger_qualifies_three_families_and_only_one_has_a_pwg_counterpart():
    led = {x["family"]: x for x in _env()["ledger"]}
    qualified = sorted(f for f, x in led.items() if x["qualifies_15pp"])
    assert qualified == ["atha", "negative an-", "privative a-"]
    assert led["atha"]["pwg_counterpart"] is True
    assert led["privative a-"]["pwg_counterpart"] is False
    assert led["atha"]["worst_delta_pp"] == 18.0
    assert led["anu"]["qualifies_15pp"] is False


def test_family_shares_sum_to_a_hundred():
    for r in _env()["families"]:
        total = r["compound_pct"] + r["derivative_pct"] + r["simplex_pct"]
        assert abs(total - 100.0) <= 0.3, (r["family"], total)
        assert r["compound_n"] + r["derivative_n"] + r["simplex_n"] == r["classified"]


def test_tsv_and_json_agree_row_for_row():
    tsv = _rows()
    for r in _env()["families"]:
        row = tsv[r["family"]]
        assert int(row["pd_headwords"]) == r["pd_headwords"]
        assert int(row["classified"]) == r["classified"]
        assert float(row["compound_pct"]) == r["compound_pct"]


# --------------------------------------------------------------- privative pins
def test_privative_recount_reproduces_the_draft_under_its_own_rule():
    priv = _env()["privative"]
    # the draft's literal a-/an- prefix test
    assert (priv["literal_a"], priv["literal_an"], priv["literal_total"]) == (
        4419, 4475, 8894)
    assert abs(priv["literal_total"] - 8900) <= 0.02 * 8900   # ≈8,900, ±2 %
    # accent-normalised — the class rule this script uses everywhere else
    assert (priv["entries_a"], priv["entries_an"], priv["entries_total"]) == (
        4698, 4754, 9452)
    assert priv["entries_total"] > priv["literal_total"]      # accents hide privatives
    assert (priv["loose_a"], priv["loose_an"], priv["loose_total"]) == (4712, 4768, 9480)


def test_privative_share_of_population():
    assert _env()["privative"]["share_of_population_pct"] == 9.2


# ------------------------------------------------------------------ density pins
def test_density_multiple_recomputes_from_the_committed_headword_lists():
    dens = _env()["density"]
    assert dens is not None, "headword lists not present on this machine"
    assert dens["pd_lemmas"] == 104959
    assert dens["pwg_in_span"] == 4519
    assert dens["multiple"] == 23.2
    assert dens["multiple_without_privatives"] == 21.1
    assert dens["multiple_without_privatives_literal"] == 21.3


# --------------------------------------------------------------------- sources
def test_source_pins_name_the_pdscan_file():
    src = _env()["sources"]["pd"]
    assert src["bytes"] == 55122076
    assert src["entries"] == 107620
    assert src["unique_key1"] == 104950
    assert src["sha256"].startswith("4ee75e66")


def test_pwg_pin_is_a_full_sha256():
    pwg = _env()["sources"]["pwg"]
    assert len(pwg["sha256"]) == 64
    assert pwg["unique_key1"] == 106067
