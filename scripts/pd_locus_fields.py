#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7458 / C2 — materialize and verify PD ``(siglum, locus)`` fields.

H6949 counts citation markers; this pass preserves those frozen counts but does
not mistake every marker for a located citation. A well-formed pair needs a
candidate siglum followed by a numeric or roman-numeral locus. Lowercase
English discourse abbreviations (``cf.``, ``comm.``, ``etc.`` …) are excluded
unless PD's committed siglum census independently knows the token. Semicolon
continuations inherit the preceding candidate siglum, as in C1.

    python3.13 scripts/pd_locus_fields.py --pd /path/to/pd.txt
    python3.13 scripts/pd_locus_fields.py --check --pd /path/to/pd.txt

No network. No H6949/C1 artifact is rewritten.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "scripts", "lib"))
import pd_quotation_units as pqu  # noqa: E402
import quotation_units  # noqa: E402
from pd_locus_parser import candidate_siglum, parse_citation_tail  # noqa: E402,F401

DATA = os.path.join(ROOT, "data", "pd")
BASELINE = os.path.join(DATA, "pd_quotations_by_entry.tsv")
FAMILIES = os.path.join(DATA, "pd_siglum_families.tsv")
OUT_LOCUS = os.path.join(DATA, "pd_locus_fields.tsv")
OUT_ENTRIES = os.path.join(DATA, "pd_locus_coverage_by_entry.tsv")
OUT_REJECTED = os.path.join(DATA, "pd_locus_rejections.tsv")
OUT_JSON = os.path.join(DATA, "pd_locus_fields_summary.json")
REPORT = os.path.join(ROOT, "reports", "PD_LOCUS_FIELDS_C2_2026-10-29.md")
EXPECTED_PD_SHA256 = "4ee75e6619ee2bd86a331586bb922101e0ae090f9edd981752cfac36ed724442"
H6949_TOTALS = {
    "entries": 107630,
    "quotations": 302442,
    "siglum_loci": 384217,
    "continuation_loci": 35673,
    "attestations": 419890,
}
LOCUS_COLUMNS = [
    "locus_id", "lid", "pc", "k1", "quotation_index", "citation_index",
    "siglum", "locus", "kind", "raw_citation",
]
ENTRY_COLUMNS = [
    "lid", "pc", "k1", "h6949_quotations", "h6949_siglum_loci",
    "h6949_continuation_loci", "h6949_attestations", "siglum_pairs",
    "continuation_pairs", "verified_pairs", "coverage_status",
]
REJECTION_COLUMNS = ["siglum", "reason", "occurrences", "entries", "examples"]
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_tsv(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path, columns, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, delimiter="\t", lineterminator="\n",
                                extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def load_known_sigla():
    return {row["siglum"] for row in read_tsv(FAMILIES)}


def build(pd_path):
    baseline = read_tsv(BASELINE)
    if len(baseline) != H6949_TOTALS["entries"]:
        raise ValueError(f"H6949 baseline has {len(baseline)} rows, expected {H6949_TOTALS['entries']}")
    known_sigla = load_known_sigla()
    locus_rows = []
    entry_rows = []
    rejection_examples = collections.defaultdict(list)
    rejection_occurrences = collections.Counter()
    rejection_entries = collections.defaultdict(set)
    quotation_total = 0

    source_entries = pqu.iter_entries(pd_path)
    for baseline_row, (hdr, body) in zip(baseline, source_entries):
        match = pqu.RE_HDR.match(hdr)
        if not match:
            raise ValueError(f"unmatched PD header: {hdr[:120]}")
        lid, pc, k1, _k2 = match.groups()
        if lid != baseline_row["lid"]:
            raise ValueError(f"source/baseline order drift: {lid} != {baseline_row['lid']}")
        text = " ".join(body).replace('<div n="lb">', " ")
        segs, nblocks = quotation_units.split_blocks(text)
        quotation_index = 0
        citation_index = 0
        siglum_pairs = continuation_pairs = 0
        i = 2  # block 1 is the headword, exactly as in H6949
        while i <= nblocks:
            run = 1
            while i + run <= nblocks and segs[2 * (i + run - 1)].strip() == "":
                run += 1
            tail = segs[2 * (i + run - 1)]
            n_loci, _n_cont, _tokens = pqu.citation_tail(tail)
            if n_loci:
                quotation_index += 1
                records, diagnostics = parse_citation_tail(tail, known_sigla)
                for siglum, reason, example in diagnostics:
                    key = (siglum, reason)
                    rejection_occurrences[key] += 1
                    rejection_entries[key].add(lid)
                    if example and len(rejection_examples[key]) < 3:
                        rejection_examples[key].append(example)
                for record in records:
                    citation_index += 1
                    if record["kind"] == "continuation":
                        continuation_pairs += 1
                    else:
                        siglum_pairs += 1
                    locus_rows.append({
                        "locus_id": f"PDL-{len(locus_rows) + 1:07d}",
                        "lid": lid,
                        "pc": pc,
                        "k1": k1,
                        "quotation_index": quotation_index,
                        "citation_index": citation_index,
                        **record,
                    })
            i += run
        quotation_total += quotation_index
        entry_rows.append({
            "lid": lid,
            "pc": pc,
            "k1": k1,
            "h6949_quotations": int(baseline_row["quotations"]),
            "h6949_siglum_loci": int(baseline_row["siglum_loci"]),
            "h6949_continuation_loci": int(baseline_row["continuation_loci"]),
            "h6949_attestations": int(baseline_row["attestations"]),
            "siglum_pairs": siglum_pairs,
            "continuation_pairs": continuation_pairs,
            "verified_pairs": siglum_pairs + continuation_pairs,
            "coverage_status": "has_verified_pair" if siglum_pairs + continuation_pairs else "no_verified_pair",
        })

    try:
        next(source_entries)
        raise ValueError("source has more entries than the H6949 baseline")
    except StopIteration:
        pass

    rejection_rows = []
    for (siglum, reason), occurrences in sorted(rejection_occurrences.items(),
                                                key=lambda item: (-item[1], item[0])):
        rejection_rows.append({
            "siglum": siglum,
            "reason": reason,
            "occurrences": occurrences,
            "entries": len(rejection_entries[(siglum, reason)]),
            "examples": " | ".join(rejection_examples[(siglum, reason)]),
        })

    totals = {key: sum(int(row[key]) for row in baseline) for key in (
        "quotations", "siglum_loci", "continuation_loci", "attestations")}
    for key, expected in H6949_TOTALS.items():
        observed = len(baseline) if key == "entries" else totals[key]
        if observed != expected:
            raise ValueError(f"H6949 {key} drift: {observed} != {expected}")
    if quotation_total != H6949_TOTALS["quotations"]:
        raise ValueError(f"quotation traversal drift: {quotation_total}")

    siglum_pairs = sum(row["kind"] == "siglum" for row in locus_rows)
    continuation_pairs = sum(row["kind"] == "continuation" for row in locus_rows)
    reason_counts = collections.Counter()
    for (siglum, reason), occurrences in rejection_occurrences.items():
        reason_counts[reason] += occurrences
    siglum_accounted = (siglum_pairs + reason_counts["discourse_not_siglum"]
                        + reason_counts["siglum_without_locus"]
                        + reason_counts["marker_consumed_by_locus"]
                        + reason_counts["page_separated_qualifier"]
                        - reason_counts["page_joined_marker"])
    continuation_accounted = (continuation_pairs + reason_counts["continuation_without_locus"]
                              + reason_counts["page_marker_only_continuation"]
                              + reason_counts["unassigned_continuation"])
    if siglum_accounted != H6949_TOTALS["siglum_loci"]:
        raise ValueError(f"unbalanced siglum markers: {siglum_accounted} != {H6949_TOTALS['siglum_loci']}")
    if continuation_accounted != H6949_TOTALS["continuation_loci"]:
        raise ValueError(f"unbalanced continuations: {continuation_accounted} != {H6949_TOTALS['continuation_loci']}")
    entries_with_h6949 = sum(row["h6949_attestations"] > 0 for row in entry_rows)
    entries_with_pairs = sum(row["verified_pairs"] > 0 for row in entry_rows)
    entries = len(entry_rows)
    summary = {
        "license": "CC-BY-SA-4.0",
        "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0/",
        "dataset": "pd_locus_fields_c2",
        "handoff": "H7458",
        "generated_by": "python3.13 scripts/pd_locus_fields.py",
        "generated_on": "2026-10-29",
        "protocol": {
            "population": "all 107,630 PDScan 2020 entries and all H6949 quotation tails",
            "pair_rule": "a candidate siglum immediately followed by a numeric or roman-numeral locus",
            "discourse_rule": "lowercase tokens are excluded unless independently present in pd_siglum_families.tsv",
            "continuation_rule": "a bare numeric semicolon continuation inherits the preceding candidate siglum, as in C1",
            "roman_rule": "roman numerals consumed by a locus are not counted again as sigla",
            "line_wrap_rule": "a hyphenated siglum wrap is joined only when the result exists in pd_siglum_families.tsv",
            "page_rule": "Page markers are metadata, never continuation loci; qualifiers split by them are not new sigla",
            "verification": "deterministic typographic validation and full-population reconciliation; no human review claim",
            "frozen_baseline": "H6949 and C1 artifacts and aggregates are not rewritten",
        },
        "evidenceLevels": {
            "locus_fields": "derived",
            "coverage_aggregates": "derived",
            "human_review": "none",
        },
        "totals": {
            **H6949_TOTALS,
            "entries_with_h6949_attestations": entries_with_h6949,
            "entries_with_h6949_attestations_pct": round(100 * entries_with_h6949 / entries, 4),
            "verified_pairs": len(locus_rows),
            "siglum_pairs": siglum_pairs,
            "continuation_pairs": continuation_pairs,
            "verified_pairs_pct_of_h6949_attestations": round(100 * len(locus_rows) / H6949_TOTALS["attestations"], 4),
            "entries_with_verified_pair": entries_with_pairs,
            "entries_with_verified_pair_pct": round(100 * entries_with_pairs / entries, 4),
            "entries_without_verified_pair": entries - entries_with_pairs,
            "rejected_marker_occurrences": sum(row["occurrences"] for row in rejection_rows),
            "unassigned_continuations": rejection_occurrences[("__UNASSIGNED_CONTINUATION__", "unassigned_continuation")],
        },
        "reconciliation": {
            "siglum_loci_accounted": siglum_accounted,
            "siglum_loci_unaccounted": H6949_TOTALS["siglum_loci"] - siglum_accounted,
            "continuation_loci_accounted": continuation_accounted,
            "continuation_loci_unaccounted": H6949_TOTALS["continuation_loci"] - continuation_accounted,
            "all_markers_accounted": True,
        },
        "rejections_by_reason": {
            reason: sum(row["occurrences"] for row in rejection_rows if row["reason"] == reason)
            for reason in sorted({row["reason"] for row in rejection_rows})
        },
        "top_rejections": rejection_rows[:30],
        "inputs": {
            "pd_txt_sha256": sha256(pd_path),
            "pd_quotations_by_entry_sha256": sha256(BASELINE),
            "pd_siglum_families_sha256": sha256(FAMILIES),
        },
        "scope_caveat": "published letter-a PD machine text only, up to ~apaca- (1976–2008 fascicles)",
    }
    if summary["inputs"]["pd_txt_sha256"] != EXPECTED_PD_SHA256:
        raise ValueError("PDScan source SHA-256 differs from the pinned H6949 input")
    return locus_rows, entry_rows, rejection_rows, summary


def write_outputs(locus_rows, entry_rows, rejection_rows, summary):
    write_tsv(OUT_LOCUS, LOCUS_COLUMNS, locus_rows)
    write_tsv(OUT_ENTRIES, ENTRY_COLUMNS, entry_rows)
    write_tsv(OUT_REJECTED, REJECTION_COLUMNS, rejection_rows)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


def compare_tsv(path, columns, expected):
    committed = read_tsv(path)
    wanted = [{key: str(value) for key, value in row.items()} for row in expected]
    if committed != wanted:
        return [f"{os.path.basename(path)} differs from rebuilt rows"]
    return []


def check(locus_rows, entry_rows, rejection_rows, summary):
    problems = []
    for path, columns, rows in (
        (OUT_LOCUS, LOCUS_COLUMNS, locus_rows),
        (OUT_ENTRIES, ENTRY_COLUMNS, entry_rows),
        (OUT_REJECTED, REJECTION_COLUMNS, rejection_rows),
    ):
        problems.extend(compare_tsv(path, columns, rows))
    with open(OUT_JSON, encoding="utf-8") as fh:
        if json.load(fh) != summary:
            problems.append("JSON summary differs from rebuilt summary")
    if not os.path.exists(REPORT):
        problems.append("C2 report missing")
    else:
        with open(REPORT, encoding="utf-8") as fh:
            report = fh.read()
        totals = summary["totals"]
        for needle in (
            f"{totals['entries_with_verified_pair']:,}",
            f"{totals['entries_with_verified_pair_pct']:.2f}",
            f"{totals['verified_pairs']:,}",
        ):
            if needle not in report:
                problems.append(f"report missing {needle}")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pd", required=True, help="path to the pinned PDScan 2020 txt/pd.txt")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    locus_rows, entry_rows, rejection_rows, summary = build(args.pd)
    if args.check:
        problems = check(locus_rows, entry_rows, rejection_rows, summary)
        if problems:
            print("FAIL")
            for problem in problems:
                print(" ", problem)
            return 1
        totals = summary["totals"]
        print(f"PASS C2 {totals['entries_with_verified_pair']:,}/{H6949_TOTALS['entries']:,} entries "
              f"= {totals['entries_with_verified_pair_pct']:.2f}%; "
              f"{totals['verified_pairs']:,} well-formed pairs")
        return 0
    write_outputs(locus_rows, entry_rows, rejection_rows, summary)
    print(f"wrote {OUT_LOCUS}\nwrote {OUT_ENTRIES}\nwrote {OUT_REJECTED}\nwrote {OUT_JSON}")
    print(json.dumps(summary["totals"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
