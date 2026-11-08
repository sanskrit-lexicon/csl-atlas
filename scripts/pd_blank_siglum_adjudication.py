#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build and check the separate M2 blank-siglum adjudication packet.

The 50-row frame is frozen before annotation. Allocation is stratified by the
printed relation (commentary / cross-reference / other) and transcription
confidence, with one row in each non-empty confidence cell. Selection inside a
cell is deterministic by sha256(seed|page|row). Annotation itself is a
per-record reading of the printed page, never inferred from this script.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "data", "pd", "pd_index_works.tsv")
OUTPUT = os.path.join(ROOT, "data", "pd", "pd_blank_siglum_adjudication.tsv")
SEED = "PD-M2-blank-sigla-v1|29-10-2026"
ARCHIVE = "https://archive.org/download/mAAY_an-encyclopaedic-dictionary-of-sanskrit-vol-1-critically-edited-by-a-m-ghatage-1/page/n{}.jpg"
LEAVES = dict(zip(
    ["LXXXIX", "XC", "XCI", "XCII", "XCIII", "XCIV", "XCV", "XCVI", "XCVII", "XCVIII", "XCIX",
     "C", "CI", "CII", "CIII", "CIV", "CV", "CVI", "CVII", "CVIII", "CIX", "CX", "CXI", "CXII",
     "CXIII", "CXIV", "CXV", "CXVI", "CXVII", "CXVIII", "CXIX", "CXX", "CXXI", "CXXII", "CXXIII",
     "CXXIV", "CXXV", "CXXVI", "CXXVII"],
    [98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 111, 112, 113, 114, 115, 116, 117, 118,
     119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138],
))
QUOTAS = {
    ("commentary", "vision"): 10,
    ("commentary", "vision-low"): 36,
    ("crossref", "vision"): 1,
    ("crossref", "vision-low"): 1,
    ("other", "vision"): 1,
    ("other", "vision-low"): 1,
}
FIELDS = [
    "sample_id", "page", "row", "title_deva", "title_iast", "author_deva", "author_iast",
    "nature_deva", "subject_code", "subject_label", "confidence", "sample_stratum",
    "page_image", "adjudicated_class", "evidence_note",
]
CLASSES = {
    "dependent_commentary",
    "cross_reference",
    "unmarked_work",
    "duplicate_or_edition",
    "uncertain",
}
SOURCE_FIELDS = [
    "page", "row", "title_deva", "title_iast", "author_deva", "author_iast", "nature_deva",
    "subject_code", "subject_label", "confidence",
]


def relation(row: dict[str, str]) -> str:
    nature = row["nature_deva"].strip().lower()
    if nature.startswith("comm"):
        return "commentary"
    if nature.startswith("cf"):
        return "crossref"
    return "other"


def read_source() -> list[dict[str, str]]:
    with open(SOURCE, encoding="utf-8", newline="") as fh:
        return [r for r in csv.DictReader(fh, delimiter="\t") if not r["abbreviation_siglum"].strip()]


def selected_rows() -> list[dict[str, str]]:
    rows = read_source()
    if len(rows) != 409:
        raise SystemExit(f"expected 409 blank-siglum rows, found {len(rows)}")
    chosen = []
    for stratum, quota in QUOTAS.items():
        rel, confidence = stratum
        pool = [r for r in rows if relation(r) == rel and r["confidence"] == confidence]
        if len(pool) < quota:
            raise SystemExit(f"stratum {stratum} has {len(pool)} rows, needs {quota}")
        pool.sort(key=lambda r: hashlib.sha256(
            f"{SEED}|{r['page']}|{r['row']}".encode("utf-8")).hexdigest())
        for row in pool[:quota]:
            chosen.append((stratum, row))
    chosen.sort(key=lambda item: (LEAVES[item[1]["page"]], int(item[1]["row"])))
    out = []
    for i, (stratum, row) in enumerate(chosen, 1):
        out.append({
            "sample_id": f"M2-{i:02d}",
            **{key: row[key] for key in SOURCE_FIELDS},
            "sample_stratum": f"{stratum[0]}|{stratum[1]}",
            "page_image": ARCHIVE.format(LEAVES[row["page"]]),
            "adjudicated_class": "",
            "evidence_note": "",
        })
    if len(out) != 50:
        raise SystemExit(f"frame must contain 50 rows, found {len(out)}")
    return out


def write_frame() -> None:
    rows = selected_rows()
    with open(OUTPUT, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {os.path.relpath(OUTPUT, ROOT)}: 50 rows")


def check(complete: bool) -> int:
    expected = selected_rows()
    decisions_path = os.path.join(ROOT, "data", "pd", "pd_blank_siglum_decisions.tsv")
    if not os.path.exists(OUTPUT) or not os.path.exists(decisions_path):
        print("MISSING M2 frame or decisions file", file=sys.stderr)
        return 2
    with open(OUTPUT, encoding="utf-8", newline="") as fh:
        actual = list(csv.DictReader(fh, delimiter="\t"))
    with open(decisions_path, encoding="utf-8", newline="") as fh:
        decision_rows = list(csv.DictReader(fh, delimiter="\t"))
    decisions = {r["sample_id"]: r for r in decision_rows}
    errors = []
    if len(actual) != 50:
        errors.append(f"row count {len(actual)} != 50")
    if len(decision_rows) != len(decisions):
        errors.append("duplicate sample_id in decisions")
    if set(decisions) != {r["sample_id"] for r in expected}:
        errors.append("decision IDs differ from the frozen frame")
    for i, (want, got) in enumerate(zip(expected, actual), 1):
        for key in ["sample_id", *SOURCE_FIELDS, "sample_stratum", "page_image"]:
            if want[key] != got.get(key):
                errors.append(f"row {i} {key}: frame drift")
        decision = decisions.get(want["sample_id"], {})
        label = decision.get("adjudicated_class", "")
        if label and label not in CLASSES:
            errors.append(f"row {i}: unknown class {label!r}")
        if complete and (not label or not decision.get("evidence_note", "").strip()):
            errors.append(f"row {i}: annotation incomplete")
    if errors:
        print("\n".join(errors[:30]), file=sys.stderr)
        return 2
    counts = {name: sum(r["adjudicated_class"] == name for r in decision_rows) for name in sorted(CLASSES)}
    print(f"OK M2 frame: 50 rows; annotated={sum(bool(r['adjudicated_class']) for r in decision_rows)}; classes={counts}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-frame", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--complete", action="store_true")
    args = parser.parse_args(argv)
    if args.write_frame:
        write_frame()
        return 0
    if args.check:
        return check(args.complete)
    parser.error("use --write-frame or --check [--complete]")


if __name__ == "__main__":
    sys.exit(main())
