#!/usr/bin/env python3
"""pd_canon_ledger.py — build the PD canon ledger (W1 of the 24-10-2026 grill).

The Poona Dictionary's declared canon has been quoted against five different bases
in five different documents (1,118 / 1,419 / 1,437 / 1,469 / 1,476 / 2,031). Each
number is correct about a different object, and every one of them has, at some
point, been used as "the" denominator. This script stops that: it derives every
candidate base from the committed artifacts, computes 118/N for each, and refuses
to write if a computed percentage disagrees with the percentage recorded in the
source JSON.

Outputs (committed):
    data/pd/pd_canon_ledger.tsv    one row per measure, base and derived percentage
    data/pd/pd_canon_ledger.json   the same numbers + input sha256 + assertions

Usage:
    python3 scripts/pd_canon_ledger.py            # write both artifacts
    python3 scripts/pd_canon_ledger.py --check    # re-derive, compare to committed
    python3 scripts/pd_canon_ledger.py --print    # table to stdout, no write

House rule this encodes: no percentage without its base in the same row, and no
denominator that is a clean-subset floor (1,118 editions) ever quoted as the canon.
"""

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
from dataset_meta import license_fields  # noqa: E402

DATA = ROOT / "data" / "pd"
OUT_TSV = DATA / "pd_canon_ledger.tsv"
OUT_JSON = DATA / "pd_canon_ledger.json"

ROW_TEST = "pd_aob_row_test_1473.json"
CANON_AUDIT = "pd_aob_declared_canon_audit.json"
INDEX_SUMMARY = "pd_index_works_summary.json"
METRICS = "pd_dcs_metrics.json"
INDEX_DELTA = "pd_index_works_siglum_delta.tsv"

COLUMNS = ["measure_id", "label", "value", "unit", "base_id", "covered_works",
           "pct_of_base", "pct_kind", "source_file", "source_field",
           "provenance", "note"]


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pct(n, d):
    return round(n / d * 100, 2)


def build():
    row_test = load(ROW_TEST)
    audit = load(CANON_AUDIT)
    index = load(INDEX_SUMMARY)
    metrics = load(METRICS)

    covered = metrics["n_covered_dcs_titles"]
    census = row_test["printed_row_census"]
    est = audit["entry_estimates"]
    rec = audit["recorded_numbers"]
    effect = row_test["metric_effect"]
    recon = index["siglum_reconciliation"]
    status = recon["status"]

    index_all = index["row_total_full"]
    blank = index["blank_siglum"]
    with_siglum = recon["with_siglum"]

    # Join counts are recomputed from the committed delta, then asserted against
    # the summary's own status dict — two artifacts, one number.
    delta = list(csv.DictReader((DATA / INDEX_DELTA).open(encoding="utf-8"),
                                delimiter="\t"))
    live = Counter(r["status"] for r in delta)
    for key, value in status.items():
        if live.get(key, 0) != value:
            raise SystemExit("delta/summary disagree on %s: %d vs %d"
                             % (key, live.get(key, 0), value))

    in_aob = status["in_both"] + status["in_aob_only"]
    not_in_aob = status["in_families_only"] + status["index_only"]
    if in_aob + not_in_aob != with_siglum:
        raise SystemExit("join classes do not partition the siglum-bearing rows")

    rows = []

    def add(measure_id, label, value, unit, base_id, cov, p, src, field,
            prov, note, recorded=None, kind=""):
        if p is not None and recorded is not None and abs(p - recorded) > 0.011:
            raise SystemExit("%s: computed %s != recorded %s" % (measure_id, p, recorded))
        rows.append({"measure_id": measure_id, "label": label, "value": value,
                     "unit": unit, "base_id": base_id, "covered_works": cov,
                     "pct_of_base": "" if p is None else p,
                     "pct_kind": kind,
                     "source_file": src, "source_field": field,
                     "provenance": prov, "note": note})

    # --- AOB-side bases -----------------------------------------------------
    add("aob_r1_lines", "AOB entry-like printed lines, header rows still counted",
        census["r1_entry_like_lines_uncorrected"], "rows", "", covered,
        pct(covered, census["r1_entry_like_lines_uncorrected"]), ROW_TEST,
        "printed_row_census.r1_entry_like_lines_uncorrected", "observed",
        "structural count; the paper's denominator",
        effect["at_r1_uncorrected"]["pct"], kind="covered_over_value")
    add("aob_header_corrected",
        "AOB entry rows, the 7 repeated column-header rows removed",
        census["entry_rows_header_corrected"], "rows", "", covered,
        pct(covered, census["entry_rows_header_corrected"]), ROW_TEST,
        "printed_row_census.entry_rows_header_corrected", "observed",
        "the printed list's own row count",
        effect["at_header_corrected"]["pct"], kind="covered_over_value")
    add("aob_print_census", "Print census of AOB entry rows (press-attributed)",
        rec["print_census"], "rows", "", covered, pct(covered, rec["print_census"]),
        CANON_AUDIT, "recorded_numbers.print_census", "press",
        "external count; same producer, older snapshot",
        audit["metric_title_level_declared_pct_at"]["print_census"]["pct"],
        kind="covered_over_value")
    add("aob_pass1", "Pass-1 loose entry parse (not reproducible)",
        rec["pass1_loose_entries"], "rows", "", covered,
        pct(covered, rec["pass1_loose_entries"]), CANON_AUDIT,
        "recorded_numbers.pass1_loose_entries", "recorded",
        "kept only so the retracted 1,419 cannot be requoted as current",
        audit["metric_title_level_declared_pct_at"]["pass1_recorded"]["pct"],
        kind="covered_over_value")
    add("aob_reparse", "Committed re-parse, raw entries (upper bound)",
        rec["reparse_raw_entries"], "rows", "", covered,
        pct(covered, rec["reparse_raw_entries"]), CANON_AUDIT,
        "recorded_numbers.reparse_raw_entries", "derived",
        "upper bound of the band; never a headline",
        audit["metric_title_level_declared_pct_at"]["reparse_raw"]["pct"],
        kind="covered_over_value")
    add("aob_usable_inventory", "Usable edition-level inventory rows",
        metrics["n_declared_aob_rows_edition_level"], "rows", "", covered,
        pct(covered, metrics["n_declared_aob_rows_edition_level"]), METRICS,
        "n_declared_aob_rows_edition_level", "observed",
        "the H6932 edition-level inventory; the paper's §5.2.1 imprint dates "
        "are counted on the clean subset, not on this row",
        kind="covered_over_value")
    add("aob_clean_subset_editions",
        "Published clean-subset edition rows — a FLOOR, never a denominator",
        audit["metric_title_level_declared_pct_at"]["published_tsv_edition_rows"]["n"],
        "rows", "", covered,
        audit["metric_title_level_declared_pct_at"]["published_tsv_edition_rows"]["pct"],
        CANON_AUDIT, "metric_title_level_declared_pct_at.published_tsv_edition_rows",
        "derived", "DROPS the Mahābhārata and Rāmāyaṇa: QUOTING THIS IS A DEFECT",
        kind="covered_over_value")

    # --- Index-side bases ---------------------------------------------------
    add("index_all_rows", "Index of Works, every printed row (pp. LXXXIX–CXXVII)",
        index_all, "rows", "", covered, pct(covered, index_all), INDEX_SUMMARY,
        "row_total_full", "observed",
        "vision transcription, 39 pages; the estate's work authority (Q5)",
        kind="covered_over_value")
    add("index_with_siglum", "Index rows that print an AOB siglum",
        with_siglum, "rows", "index_all_rows", covered,
        pct(covered, with_siglum), INDEX_SUMMARY, "siglum_reconciliation.with_siglum",
        "derived", "joinable layer", kind="covered_over_value")
    add("index_blank_siglum", "Index rows with no siglum printed",
        blank, "rows", "index_all_rows", None, pct(blank, index_all), INDEX_SUMMARY,
        "blank_siglum", "observed",
        "20.1 % of the Index; classed, not dropped; 50-row adjudication is ladder unit M2",
        kind="share_of_base")

    # --- The join and the divergence ---------------------------------------
    add("index_in_aob", "Index sigla that find an AOB row (both + AOB-only)",
        in_aob, "sigla", "index_with_siglum", None, pct(in_aob, with_siglum),
        INDEX_DELTA, "status: in_both + in_aob_only", "derived",
        "the direct siglum join the Index pilot predicted; C3's stricter "
        "edition-identity measure is 815/1,622 = 50.25 % "
        "(reports/PD_AOB_SCAN_LINKS_C3_2026-10-30.md)",
        kind="share_of_base")
    add("index_not_in_aob", "Index sigla with no AOB row (families-only + neither)",
        not_in_aob, "sigla", "index_with_siglum", None, pct(not_in_aob, with_siglum),
        INDEX_DELTA, "status: in_families_only + index_only", "derived",
        "AOB inventory gap or OCR break; not yet classed", kind="share_of_base")
    add("aob_only_sigla", "AOB sigla the Index never prints",
        status["aob_only"], "sigla", "", None, None, INDEX_DELTA, "status: aob_only",
        "observed", "a second join gap, in the opposite direction")
    add("canon_divergence", "Index rows minus AOB header-corrected rows",
        index_all - census["entry_rows_header_corrected"], "rows",
        "aob_header_corrected", None,
        pct(index_all - census["entry_rows_header_corrected"],
            census["entry_rows_header_corrected"]), "(derived)", "index_all_rows - aob_header_corrected",
        "derived", "the two printed canon counts differ by this much",
        kind="share_of_base")

    return rows, covered


def render_tsv(rows):
    out = ["\t".join(COLUMNS)]
    for r in rows:
        out.append("\t".join(str(r[c]) for c in COLUMNS))
    return "\n".join(out) + "\n"


def render_json(rows, covered):
    inputs = {}
    for name in [ROW_TEST, CANON_AUDIT, INDEX_SUMMARY, METRICS, INDEX_DELTA]:
        inputs[name] = sha256(DATA / name)
    return json.dumps({
        **license_fields(),
        "generated_by": "scripts/pd_canon_ledger.py",
        "scope": "PD declared canon — every base that has been quoted, with 118/N each",
        "covered_works": covered,
        "row_count": len(rows),
        "inputs_sha256": inputs,
        "rule": "no percentage without its base in the same row and its kind in "
                "pct_kind — covered_over_value (118/N over this row's own value) "
                "vs share_of_base (this row's value over its base); "
                "aob_clean_subset_editions is a floor and must never be quoted",
    }, indent=1, ensure_ascii=False) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build/check the PD canon ledger")
    ap.add_argument("--check", action="store_true",
                    help="re-derive and compare with the committed artifacts")
    ap.add_argument("--print", dest="print_only", action="store_true",
                    help="print the table; write nothing")
    args = ap.parse_args(argv)

    rows, covered = build()
    tsv = render_tsv(rows)
    js = render_json(rows, covered)

    if args.print_only:
        sys.stdout.write(tsv)
        return 0

    if args.check:
        bad = 0
        for path, expected in ((OUT_TSV, tsv), (OUT_JSON, js)):
            if not path.exists():
                print("MISSING %s" % path.relative_to(ROOT))
                bad += 1
            elif path.read_text(encoding="utf-8") != expected:
                print("DRIFT %s" % path.relative_to(ROOT))
                bad += 1
        print("pd_canon_ledger: %d rows, %d drift" % (len(rows), bad))
        return 0 if bad == 0 else 1

    OUT_TSV.write_text(tsv, encoding="utf-8")
    OUT_JSON.write_text(js, encoding="utf-8")
    print("wrote %s (%d rows)" % (OUT_TSV.relative_to(ROOT), len(rows)))
    print("wrote %s" % OUT_JSON.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
