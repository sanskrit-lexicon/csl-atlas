#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C2 — extract and validate PD (siglum, locus) fields using H6949 unchanged.

    python3.13 scripts/pd_locus_fields.py --pd /path/to/pd.txt
    python3.13 scripts/pd_locus_fields.py --check --pd /path/to/pd.txt

The quotation and attestation boundaries come from quotation_units.count_units.
This pass only retains the locator text and adds structural review flags.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "scripts", "lib"))
import pd_quotation_units as pqu  # noqa: E402
import quotation_units  # noqa: E402

DATA = os.path.join(ROOT, "data", "pd")
OUT_FIELDS = os.path.join(DATA, "pd_locus_fields.tsv")
OUT_ENTRIES = os.path.join(DATA, "pd_locus_entries.tsv")
OUT_SUMMARY = os.path.join(DATA, "pd_locus_summary.json")
REPORT = os.path.join(ROOT, "reports", "PD_LOCUS_FIELDS_C2_2026-10-29.md")
EXPECTED = {
    "entries": 107630,
    "entries_with_attestation": 105944,
    "entries_with_pair": 105890,
    "entries_with_clean_pair": 102576,
    "attestations": 419890,
    "siglum_loci": 384217,
    "continuation_loci": 35673,
    "nonempty_pairs": 399403,
    "clean_pairs": 383638,
    "empty_loci": 20383,
    "unassigned_continuations": 104,
}
FIELD_COLUMNS = ["lid", "pc", "k1", "attestation_type", "siglum", "locus", "shape", "review_flag"]
ENTRY_COLUMNS = ["lid", "pc", "k1", "attestations", "nonempty_pairs", "clean_pairs",
                 "empty_loci", "review_loci", "entry_status"]


def read_tsv(name):
    with open(os.path.join(DATA, name), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sigla_spans(seg):
    """H6949 siglum rule plus source spans; no second citation definition."""
    out = []
    for match in pqu.RE_SIG.finditer(seg):
        name, sep = match.group(1), match.group(2)
        if sep != "." and not sep.endswith(".)"):
            continue
        token = name + sep
        if pqu.is_siglum(token):
            out.append((token, match.start(), match.end()))
    return out


def citation_records(tail):
    """Return H6949 (n_loci, n_continuations, [(siglum, locus, kind)])."""
    tail = tail.split("{@", 1)[0]
    plain = pqu.RE_ITAL.sub(" ", pqu.RE_TAG.sub(" ", tail))
    records = []
    previous = None
    loci = continuations = 0
    for seg in plain.split(";"):
        spans = sigla_spans(seg)
        if spans:
            for i, (siglum, _start, end) in enumerate(spans):
                next_start = spans[i + 1][1] if i + 1 < len(spans) else len(seg)
                locus = seg[end:next_start].strip(" \t,;—-")
                records.append((siglum, locus, "siglum"))
                previous = siglum
                loci += 1
        elif seg.strip() and re.search(r"\d", seg):
            locus = seg.strip(" \t,;—-")
            records.append((previous or "__UNASSIGNED_CONTINUATION__", locus, "continuation"))
            continuations += 1
    return loci, continuations, records


def classify(siglum, locus):
    if siglum == "__UNASSIGNED_CONTINUATION__":
        return "unassigned", "unassigned"
    if not locus:
        return "empty", "empty"
    has_digit = bool(re.search(r"\d", locus))
    has_letter = bool(re.search(r"[^\W\d_]", locus, re.U))
    if has_digit and not has_letter:
        shape = "numeric"
    elif has_digit:
        shape = "alphanumeric"
    elif (re.fullmatch(r"[ivxlcdmIVXLCDM().\s-]+", locus)
          and re.search(r"[ivxlcdmIVXLCDM]", locus)):
        shape = "roman"
    else:
        shape = "textual"
    if shape == "textual":
        flag = "textual"
    elif len(locus) > 80 or (has_digit and len(locus.split()) > 12):
        flag = "prose_tail"
    elif locus.count("(") != locus.count(")"):
        flag = "unbalanced_parentheses"
    else:
        flag = "clean"
    return shape, flag


def build(pd_path):
    fields = []
    entries = []
    entry_kind_counts = {}
    totals = collections.Counter()
    by_shape = collections.Counter()
    by_flag = collections.Counter()
    by_entry_status = collections.Counter()
    empty_only = []
    review_examples = []
    for hdr, body in pqu.iter_entries(pd_path):
        match = pqu.RE_HDR.match(hdr)
        if not match:
            raise ValueError(f"unmatched entry header: {hdr}")
        lid, pc, k1, _k2 = match.groups()
        text = " ".join(body).replace('<div n="lb">', " ")
        units = quotation_units.count_units(text, citation_records)
        records = units["tokens"]
        if len(records) != units["attestations"]:
            raise AssertionError(f"record count mismatch at L={lid}")
        nonempty_pairs = clean_pairs = empty_loci = 0
        for siglum, locus, kind in records:
            shape, flag = classify(siglum, locus)
            by_shape[shape] += 1
            by_flag[flag] += 1
            nonempty = siglum != "__UNASSIGNED_CONTINUATION__" and bool(locus)
            clean = nonempty and flag == "clean"
            nonempty_pairs += nonempty
            clean_pairs += clean
            empty_loci += not locus
            fields.append({"lid": lid, "pc": pc, "k1": k1, "attestation_type": kind,
                           "siglum": siglum, "locus": locus, "shape": shape,
                           "review_flag": flag})
            if flag != "clean" and len(review_examples) < 100:
                review_examples.append({"lid": lid, "k1": k1, "siglum": siglum,
                                        "locus": locus, "review_flag": flag})
        entry_kind_counts[lid] = (units["loci"], units["continuation_loci"])
        if nonempty_pairs:
            status = "clean" if clean_pairs else "nonempty_only"
        elif records:
            status = "empty_only"
            empty_only.append({"lid": lid, "pc": pc, "k1": k1,
                               "sigla": ";".join(sorted({r[0] for r in records}))})
        else:
            status = "no_attestation"
        by_entry_status[status] += 1
        entries.append({"lid": lid, "pc": pc, "k1": k1, "attestations": len(records),
                        "nonempty_pairs": nonempty_pairs, "clean_pairs": clean_pairs,
                        "empty_loci": empty_loci, "review_loci": len(records) - clean_pairs,
                        "entry_status": status})
        totals["attestations"] += len(records)
        totals["siglum_loci"] += units["loci"]
        totals["continuation_loci"] += units["continuation_loci"]
        totals["nonempty_pairs"] += nonempty_pairs
        totals["clean_pairs"] += clean_pairs
        totals["empty_loci"] += empty_loci

    assert len(entries) == EXPECTED["entries"]
    assert sum(r["attestations"] for r in entries) == EXPECTED["attestations"]
    assert totals["siglum_loci"] == EXPECTED["siglum_loci"]
    assert totals["continuation_loci"] == EXPECTED["continuation_loci"]
    assert totals["nonempty_pairs"] == EXPECTED["nonempty_pairs"]
    assert totals["clean_pairs"] == EXPECTED["clean_pairs"]
    assert totals["empty_loci"] == EXPECTED["empty_loci"]
    assert by_shape["unassigned"] == EXPECTED["unassigned_continuations"]
    assert by_entry_status["clean"] == EXPECTED["entries_with_clean_pair"]
    assert by_entry_status["clean"] + by_entry_status["nonempty_only"] == EXPECTED["entries_with_pair"]
    assert by_entry_status["clean"] + by_entry_status["nonempty_only"] + by_entry_status["empty_only"] == EXPECTED["entries_with_attestation"]

    # Independent H6949 per-entry reconciliation, not just corpus totals.
    committed = {r["lid"]: r for r in read_tsv("pd_quotations_by_entry.tsv")}
    assert set(committed) == {r["lid"] for r in entries}
    for row in entries:
        old = committed[row["lid"]]
        assert int(old["attestations"]) == row["attestations"], row["lid"]
        assert (int(old["siglum_loci"]), int(old["continuation_loci"])) == entry_kind_counts[row["lid"]], row["lid"]

    with_pair = EXPECTED["entries_with_pair"]
    with_clean = EXPECTED["entries_with_clean_pair"]
    summary = {
        "license": "CC-BY-SA-4.0",
        "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0/",
        "dataset": "pd_locus_fields_c2",
        "generated_by": "python3.13 scripts/pd_locus_fields.py",
        "generated_on": "2026-10-29",
        "evidenceLevels": {
            "quotation_boundaries": "derived",
            "locus_extraction": "derived",
            "structural_flags": "derived",
            "human_review": "none",
        },
        "protocol": {
            "unit": "H6949 quotation_units.count_units, unchanged",
            "pair": "assigned siglum plus non-empty locus; unassigned continuations excluded",
            "clean_pair": "non-empty pair whose review_flag is clean",
            "review": "empty, textual, prose_tail, unbalanced_parentheses and unassigned stay visible",
        },
        "totals": {
            **EXPECTED,
            "entries_with_pair_pct": round(100 * with_pair / EXPECTED["entries"], 4),
            "entries_with_clean_pair_pct": round(100 * with_clean / EXPECTED["entries"], 4),
            "entries_empty_only": by_entry_status["empty_only"],
            "entries_no_attestation": by_entry_status["no_attestation"],
            "review_loci": EXPECTED["attestations"] - EXPECTED["clean_pairs"],
        },
        "by_shape": dict(sorted(by_shape.items())),
        "by_review_flag": dict(sorted(by_flag.items())),
        "by_entry_status": dict(sorted(by_entry_status.items())),
        "reconciliation": {
            "h6949_entry_rows": len(committed),
            "per_entry_attestations_and_locus_kinds_exact": True,
            "totals_exact": True,
        },
        "inputs": {
            "pd_txt_sha256": sha256(pd_path),
            "pd_quotations_by_entry.tsv": sha256(os.path.join(DATA, "pd_quotations_by_entry.tsv")),
        },
        "empty_only_entries": empty_only,
        "review_examples": review_examples,
    }
    return fields, entries, summary


def write_tsv(path, columns, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write("\t".join(columns) + "\n")
        for row in rows:
            fh.write("\t".join(str(row[c]) for c in columns).rstrip("\t") + "\n")


def write_outputs(fields, entries, summary):
    write_tsv(OUT_FIELDS, FIELD_COLUMNS, fields)
    write_tsv(OUT_ENTRIES, ENTRY_COLUMNS, entries)
    with open(OUT_SUMMARY, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


def check(fields, entries, summary):
    problems = []
    for path, columns, expected in ((OUT_FIELDS, FIELD_COLUMNS, fields),
                                    (OUT_ENTRIES, ENTRY_COLUMNS, entries)):
        with open(path, encoding="utf-8", newline="") as fh:
            actual = list(csv.DictReader(fh, delimiter="\t"))
        expected_rows = [{c: str(row[c]) for c in columns} for row in expected]
        if actual != expected_rows:
            problems.append(f"{os.path.basename(path)} differs from rebuilt rows")
    with open(OUT_SUMMARY, encoding="utf-8") as fh:
        if json.load(fh) != summary:
            problems.append("summary JSON differs from rebuilt summary")
    if not os.path.exists(REPORT):
        problems.append("report missing")
    else:
        with open(REPORT, encoding="utf-8") as fh:
            report = fh.read()
        t = summary["totals"]
        for needle in (f"{t['entries_with_pair']:,}", f"{t['entries_with_pair_pct']:.4f}",
                       f"{t['entries_with_clean_pair']:,}", f"{t['entries_with_clean_pair_pct']:.4f}"):
            if needle not in report:
                problems.append(f"report missing {needle}")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pd", required=True)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    fields, entries, summary = build(args.pd)
    if args.check:
        problems = check(fields, entries, summary)
        if problems:
            print("FAIL")
            for problem in problems:
                print(" ", problem)
            return 1
        t = summary["totals"]
        print(f"PASS C2 {t['entries_with_pair']:,}/{t['entries']:,} = {t['entries_with_pair_pct']:.4f}% "
              f"nonempty; {t['entries_with_clean_pair_pct']:.4f}% clean")
        return 0
    write_outputs(fields, entries, summary)
    print(f"wrote {OUT_FIELDS}\nwrote {OUT_ENTRIES}\nwrote {OUT_SUMMARY}")
    print(json.dumps(summary["totals"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
