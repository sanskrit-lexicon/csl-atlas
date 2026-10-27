"""Pins for H7297: PD policy-matched density (simplex / derivative / compound).

The class ledger is built from the external PDScan text, so the tests read the
committed artifacts (the ``test_pd_family_composition.py`` / ``test_pd_two_layer_validation.py``
pattern) and check the three things that can silently go wrong:

* the raw H6949/H7095 ledger is read, not replaced — every total is re-derived
  from ``pd_attestation_decomposition.tsv`` and must equal its pin;
* the strata are a partition with explicit denominators, and the standardised
  pool is exactly the equal-weight mean of the three stratum ratios;
* the PD-only inventory result stays separate and keeps its 23.2x contrast
  labelled as a lemmatisation-choice ratio, never as a citation measure.

The 18 gold rows are pinned from the committed H6949/H7095 ledgers and the
frozen class ledger; the family of each is the H7110 rule's output for that
headword, recorded so a re-classification cannot pass unnoticed.
"""

import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
for p in (str(ROOT / "scripts"), str(ROOT / "scripts" / "lib")):
    if p not in sys.path:
        sys.path.insert(0, p)

import pd_policy_matched_density as h7297

DATA = ROOT / "data" / "pd"
GOLD = ROOT / "tests" / "forensic" / "h7297_policy_matched_gold.tsv"
BANNED = ("twelvefold per headword", "per-headword twelvefold")


def _tsv(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def _json():
    with open(DATA / "pd_policy_matched_density.json", encoding="utf-8") as fh:
        return json.load(fh)


def test_check_regenerates_committed_artifacts():
    assert h7297.run_check() == 0


def test_raw_ledger_is_read_not_replaced():
    rows = h7297.load_population()
    assert len(rows) == 4093
    assert sum(r["pd_att"] for r in rows) == 157480
    assert sum(r["pwg_att"] for r in rows) == 18423
    assert sum(r["pd_quotations"] for r in rows) == 97413
    assert sum(r["pwg_quotations"] for r in rows) == 10225
    assert sum(1 for r in rows if r["pd_att"] < r["pwg_att"]) == 340
    payload = _json()
    assert payload["raw_ledger_retained"]["attestation_ratio"] == 8.548
    assert payload["raw_ledger_retained"]["quotation_ratio"] == 9.5269
    assert payload["raw_ledger_retained"]["median_attestation_ratio"] == 4.0


def test_strata_are_a_partition_with_denominators():
    rows = h7297.load_population()
    classes = h7297.load_class()
    groups = h7297.by_stratum(rows, classes)
    total = sum(len(g) for g in groups.values())
    assert total == len(rows) == 4093
    assert len(groups["simplex"]) + len(groups["derivative"]) + len(groups["compound"]) == 4059
    assert len(groups["unclassified"]) == 34
    for name, group in groups.items():
        assert all(r["pwg_att"] >= 0 for r in group), name
    # every stratum row in the TSV carries its own PD and PWG denominator
    for row in _tsv(DATA / "pd_policy_matched_density.tsv"):
        assert int(row["pd_attestations"]) >= 0
        assert int(row["pwg_attestations"]) >= 0
        assert int(row["lemmas"]) >= int(row["lemmas_with_pwg_attestation"])


def test_standardised_pool_is_the_equal_weight_mean():
    payload = _json()
    strata = payload["strata"]
    expected = round(
        sum(strata[s]["attestation_ratio"] for s in ("simplex", "derivative", "compound")) / 3.0,
        4,
    )
    assert payload["pooled"]["standardised_equal_weight"]["value"] == expected
    assert payload["pooled"]["standardised_equal_weight"]["value"] != payload["pooled"]["raw_ratio_of_sums"]["value"]
    lo, hi = payload["pooled"]["standardised_equal_weight"]["bootstrap_95"]
    assert lo < expected < hi
    # the pooled row is present in the table, next to the raw row, not instead of it
    rows = {r["stratum"]: r for r in _tsv(DATA / "pd_policy_matched_density.tsv")}
    assert rows["pooled_standardised_equal_weight"]["attestation_ratio"] == str(expected)
    assert rows["pooled_raw_ratio_of_sums"]["attestation_ratio"] == "8.548"


def test_canaries_akamatas_compound_and_below_parity():
    payload = _json()
    ak = payload["canaries"]["akAmatas"]
    assert ak["family"] == "derivative"
    assert (ak["pd_quotations"], ak["pwg_quotations"]) == (31, 2)
    assert (ak["pd_attestations"], ak["pwg_attestations"]) == (75, 6)
    assert ak["attestation_ratio"] == 12.5
    comp = payload["canaries"]["compound_stratum"]
    assert comp["lemmas"] == 2929
    assert comp["attestation_ratio"] == 9.1293
    bp = payload["below_parity"]
    assert bp["n"] == 340
    assert bp["by_stratum"] == {"simplex": 110, "derivative": 17, "compound": 209, "unclassified": 4}
    assert bp["zero_pd"] == 191
    assert bp["membership_sha256"] == payload["canaries"]["below_parity_sha256"]
    assert len(bp["examples_first"]) == 10 and len(bp["examples_last"]) == 10


def test_gold_rows():
    rows = h7297.load_population()
    by_key = {r["k1"]: r for r in rows}
    for pin in _tsv(GOLD):
        r = by_key[pin["k1"]]
        assert r["pd_entries"] == int(pin["pd_entries"]), pin["k1"]
        assert r["pwg_entries"] == int(pin["pwg_entries"]), pin["k1"]
        assert r["pd_quotations"] == int(pin["pd_quotations"]), pin["k1"]
        assert r["pwg_quotations"] == int(pin["pwg_quotations"]), pin["k1"]
        assert r["pd_att"] == int(pin["pd_attestations"]), pin["k1"]
        assert r["pwg_att"] == int(pin["pwg_attestations"]), pin["k1"]
        status = "below_parity" if r["pd_att"] < r["pwg_att"] else "at_or_above_parity"
        assert status == pin["status"], pin["k1"]


def test_class_ledger_is_frozen_and_complete():
    rows = _tsv(DATA / "pd_policy_matched_class.tsv")
    assert len(rows) == 104950
    assert {r["family"] for r in rows} <= {"simplex", "derivative", "compound", "unclassified"}
    counts = {}
    for r in rows:
        counts[r["family"]] = counts.get(r["family"], 0) + 1
    assert counts == {"simplex": 17445, "derivative": 12670, "compound": 72632, "unclassified": 2203}
    payload = _json()
    assert payload["classification"]["source_sha256"] == h7297.family_rule.PD_SHA256
    assert payload["classification"]["shared_classified"] == 4059


def test_inventory_result_is_separate_and_labelled():
    rows = _tsv(DATA / "pd_policy_matched_inventory.tsv")
    contrast = [r for r in rows if r["row_kind"] == "inventory_contrast"]
    assert len(contrast) == 1
    assert contrast[0]["headwords"] == "104959"
    assert "not a citation measure" in contrast[0]["note"]
    assert "not a per-headword" in contrast[0]["note"]
    share = [r for r in rows if r["row_kind"] == "family_share"]
    assert {r["scope"] for r in share} == {"pd_only", "shared"}
    pd_only = next(r for r in share if r["scope"] == "pd_only" and r["family"] == "all")
    assert pd_only["headwords"] == "100866"
    assert pd_only["headwords_at_most_one"] == "66036"
    assert pd_only["attestation_mass"] == "262410"
    # a share row carries no citation ratio column at all
    assert "attestation_ratio" not in rows[0]
    payload = _json()
    assert payload["inventory_policy"]["inventory_contrast"]["value"] == 23.2
    assert payload["inventory_policy"]["pd_only_headwords"] == 100866
    assert payload["inventory_policy"]["threshold_attestations"] == 1


def test_no_banned_wording():
    for path in (DATA / "pd_policy_matched_density.json",
                 ROOT / "reports" / "PD_POLICY_MATCHED_DENSITY_2026.md",
                 DATA / "pd_policy_matched_inventory.tsv"):
        text = path.read_text(encoding="utf-8")
        for phrase in BANNED:
            assert phrase not in text, (path.name, phrase)
