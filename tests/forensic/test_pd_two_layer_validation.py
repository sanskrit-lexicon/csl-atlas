"""Pins for H7275: two-layer PD validation.

Layer 1 is re-derivable only with the external PDScan text, so the test reads
the committed artifacts (the ``test_pd_family_composition.py`` pattern) and
checks the arithmetic that does not need the source: the entry partition sums
to the H6949 population, every numerator is inside its denominator, and the
H6949 pins are exact.

Layer 2 is generated from the ledger alone, so the whole manifest is checked
byte-for-byte against a fresh build: 300 slots, 100 per period, every page
inside its own ledger row, and the same seed from the frozen seed text.
"""

import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
for p in (str(ROOT / "scripts"), str(ROOT / "scripts" / "lib")):
    if p not in sys.path:
        sys.path.insert(0, p)

import pd_two_layer_validation as h7275

DATA = ROOT / "data" / "pd"


def _json(name):
    with open(DATA / name, encoding="utf-8") as fh:
        return json.load(fh)


def _tsv(name):
    with open(DATA / name, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def test_frozen_manifest_rebuilds_byte_identically():
    ledger = h7275.read_ledger()
    manifest = h7275.build_manifest(ledger)
    committed = _json("pd_print_only_sample_manifest.json")
    assert h7275.render_json(manifest) == h7275.render_json(committed)
    assert h7275.render_slots(manifest) == (
        DATA / "pd_print_only_sample_slots.tsv"
    ).read_text(encoding="utf-8")


def test_manifest_quota_and_frames():
    manifest = _json("pd_print_only_sample_manifest.json")
    slots = manifest["slots"]
    assert len(slots) == 300
    for period in manifest["periods"]:
        n = sum(r["slots"] for r in period["rows"])
        assert n == period["quota"] == 100
        for row in period["rows"]:
            assert row["pp_lo"] <= min(
                s["page"] for s in slots if s["ledger_id"] == row["ledger_id"]
            )
            assert max(
                s["page"] for s in slots if s["ledger_id"] == row["ledger_id"]
            ) <= row["pp_hi"]
    # a row never repeats a page: one slot per selected page
    for row in manifest["periods"]:
        for r in row["rows"]:
            pages = [s["page"] for s in slots if s["ledger_id"] == r["ledger_id"]]
            assert len(pages) == len(set(pages))
    assert manifest["status"] == "STOP_NO_PRINT_ACCESS"
    assert manifest["frozen_before_measurement"] is True


def test_layer1_pins_and_partition():
    env = _json("pd_two_layer_stability.json")
    rec = env["recount"]
    assert rec["loci"] == 384217
    assert rec["continuation_loci"] == 35673
    assert rec["attestations"] == 419890
    assert abs(rec["coverage_pct"] - 25.16) <= 0.5
    assert all(env["canaries"].values())
    assert rec["covered_loci"] <= rec["primary_loci"] <= rec["loci"]

    rows = _tsv("pd_two_layer_class.tsv")
    assert sum(int(r["entries"]) for r in rows) == 107630
    for r in rows:
        assert int(r["covered_loci"]) <= int(r["primary_loci"])


def test_stability_verdict_is_evidence_bounded():
    env = _json("pd_two_layer_stability.json")
    st = env["stability"]
    assert st["measured_fascicles"] == 24
    assert st["pooled_pct"] == rec_round(env, st)
    assert st["min_fascicle_pct"] <= st["pooled_pct"] <= st["max_fascicle_pct"]
    assert st["verdict"] in {"stable", "partially stable", "not stable"}
    assert env["layer2"]["verdict"].startswith("not assessed")


def rec_round(env, st):
    rec = env["recount"]
    return round(100.0 * rec["covered_loci"] / rec["primary_loci"], 2)


def test_frozen_classes():
    assert {"ati", "anu", "apa"} <= h7275.UPASARGAS
    assert "a" not in h7275.UPASARGAS and "an" not in h7275.UPASARGAS
    assert h7275.family_rule.classify("anna-BARqa") == "compound"
    assert h7275.family_rule.classify("anna-tva") == "derivative"
    assert h7275.family_rule.classify("anna") == "simplex"
