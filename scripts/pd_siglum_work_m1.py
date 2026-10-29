#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M1: blind 200-row siglum→work annotation frame and Cohen's κ.

The registry supplies candidate links, never an annotator label. Annotator A and
B files are separate per-record reading passes with the same sample IDs and the
schema: confirmed / wrong_work / wrong_siglum / ambiguous. No κ is emitted for
missing, mismatched, or partially annotated passes.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import os
import random
import sys

from pd_blank_siglum_adjudication import ARCHIVE, LEAVES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = "PD-M1-siglum-work-v1|29-10-2026"
FRAME = os.path.join(ROOT, "data", "pd", "pd_siglum_work_m1_frame.tsv")
PASS_B = os.path.join(ROOT, "data", "pd", "pd_siglum_work_m1_annotator_b.tsv")
LABELS = ("confirmed", "wrong_work", "wrong_siglum", "ambiguous")
QUOTAS = {
    "ordinary": 100,
    "shared_siglum": 40,
    "vision_low": 40,
    "aob_join": 20,
}
FIELDS = [
    "sample_id", "record_id", "work_id", "candidate_label", "page", "row", "title_deva",
    "title_iast", "author_deva", "nature_deva", "abbreviation_siglum", "abbreviation_qualifier",
    "confidence", "sample_stratum", "page_image", "provenance",
]


def read_tsv(name: str) -> list[dict[str, str]]:
    with open(os.path.join(ROOT, "data", "pd", name), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def stratum(row: dict[str, str], work: dict[str, str]) -> str:
    classes = ";".join((row["unresolved_class"], work["unresolved_class"]))
    if "shared_siglum" in classes:
        return "shared_siglum"
    if row["sample_role"] == "vision_low":
        return "vision_low"
    if "aob_join" in classes:
        return "aob_join"
    if int(row["edition_ordinal"] or "1") > 1:
        return "repeat_edition"
    return "ordinary"


def build_frame() -> list[dict[str, str]]:
    index = {(r["page"], r["row"]): r for r in read_tsv("pd_index_works.tsv")}
    registry = {r["work_id"]: r for r in read_tsv("pd_work_registry.tsv") if r["work_id"]}
    candidates = []
    seen_claims = set()
    for row in read_tsv("pd_work_edition_map.tsv"):
        if row["source"] != "pd_index_works" or not row["work_id"] or not row["dictionary_siglum"]:
            continue
        claim_key = (row["source_locator"], row["work_id"], row["dictionary_siglum"])
        if claim_key in seen_claims:
            continue
        seen_claims.add(claim_key)
        page, number = row["source_locator"].split(":")
        printed = index[(page, number)]
        work = registry[row["work_id"]]
        candidates.append((stratum(row, work), row, printed, work))
    if len(candidates) < 200:
        raise SystemExit(f"only {len(candidates)} eligible siglum→work candidates")
    chosen = []
    for name, quota in QUOTAS.items():
        pool = [item for item in candidates if item[0] == name]
        if len(pool) < quota:
            raise SystemExit(f"stratum {name}: {len(pool)} available, {quota} requested")
        pool.sort(key=lambda item: hashlib.sha256(
            f"{SEED}|{item[1]['record_id']}".encode("utf-8")).hexdigest())
        chosen.extend(pool[:quota])
    chosen.sort(key=lambda item: (LEAVES[item[2]["page"]], int(item[2]["row"]), item[1]["record_id"]))
    frame = []
    for i, (name, row, printed, work) in enumerate(chosen, 1):
        frame.append({
            "sample_id": f"M1-{i:03d}",
            "record_id": row["record_id"],
            "work_id": row["work_id"],
            "candidate_label": work["label"],
            "page": printed["page"],
            "row": printed["row"],
            "title_deva": printed["title_deva"],
            "title_iast": printed["title_iast"],
            "author_deva": printed["author_deva"],
            "nature_deva": printed["nature_deva"],
            "abbreviation_siglum": printed["abbreviation_siglum"],
            "abbreviation_qualifier": printed["abbreviation_qualifier"],
            "confidence": printed["confidence"],
            "sample_stratum": name,
            "page_image": ARCHIVE.format(LEAVES[printed["page"]]),
            "provenance": row["provenance"],
        })
    claim_keys = {(r["page"], r["row"], r["work_id"], r["abbreviation_siglum"]) for r in frame}
    if len(frame) != 200 or len({r["record_id"] for r in frame}) != 200 or len(claim_keys) != 200:
        raise SystemExit("M1 frame must contain 200 unique record IDs and siglum→work claims")
    return frame


def write_frame() -> None:
    frame = build_frame()
    with open(FRAME, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(frame)
    with open(PASS_B, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["sample_id", "label", "note"], delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows({"sample_id": r["sample_id"], "label": "", "note": ""} for r in frame)
    print(f"wrote M1 frame and blank annotator-B pass: {len(frame)} rows")


def read_pass(path: str) -> dict[str, dict[str, str]]:
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    result = {r["sample_id"]: r for r in rows}
    if len(result) != len(rows):
        raise SystemExit(f"duplicate sample_id in {path}")
    return result


def check(complete: bool) -> int:
    expected = build_frame()
    if not os.path.exists(FRAME) or not os.path.exists(PASS_B):
        print("MISSING M1 frame or annotator-B file", file=sys.stderr)
        return 2
    actual = read_pass(FRAME)
    pass_b = read_pass(PASS_B)
    errors = []
    ids = {r["sample_id"] for r in expected}
    if len(actual) != 200 or set(actual) != ids:
        errors.append("frame IDs differ from the deterministic 200-row sample")
    if set(pass_b) != ids:
        errors.append("annotator-B IDs differ from the frame")
    for row in expected:
        got = actual.get(row["sample_id"], {})
        for key in FIELDS:
            if got.get(key) != row[key]:
                errors.append(f"{row['sample_id']}: frame drift in {key}")
        label = pass_b.get(row["sample_id"], {}).get("label", "")
        if label and label not in LABELS:
            errors.append(f"{row['sample_id']}: unknown B label {label!r}")
        if complete and (not label or not pass_b[row["sample_id"]].get("note", "").strip()):
            errors.append(f"{row['sample_id']}: B annotation incomplete")
    if errors:
        print("\n".join(errors[:30]), file=sys.stderr)
        return 2
    counts = collections.Counter(r["label"] for r in pass_b.values() if r["label"])
    print(f"OK M1 frame: 200 rows; B annotated={sum(counts.values())}; B labels={dict(counts)}")
    return 0


def kappa(path_a: str, path_b: str) -> int:
    a, b = read_pass(path_a), read_pass(path_b)
    ids = set(a) & set(b)
    if len(ids) != 200 or set(a) != set(b):
        print("κ refused: passes must share exactly the 200 sample IDs", file=sys.stderr)
        return 2
    for sample_id in ids:
        for name, row in (("A", a[sample_id]), ("B", b[sample_id])):
            if row.get("label") not in LABELS or not row.get("note", "").strip():
                print(f"κ refused: {sample_id} lacks a genuine {name} label/note", file=sys.stderr)
                return 2
    ordered = sorted(ids)
    matrix = {x: {y: 0 for y in LABELS} for x in LABELS}
    for sample_id in ordered:
        matrix[a[sample_id]["label"]][b[sample_id]["label"]] += 1
    observed = sum(matrix[x][x] for x in LABELS) / 200
    pa = collections.Counter(a[i]["label"] for i in ordered)
    pb = collections.Counter(b[i]["label"] for i in ordered)
    expected = sum(pa[x] * pb[x] for x in LABELS) / (200 * 200)
    score = (observed - expected) / (1 - expected) if expected < 1 else 1.0
    rng = random.Random(20261029)
    pairs = [(a[i]["label"], b[i]["label"]) for i in ordered]
    boots = []
    for _ in range(5000):
        sample = [pairs[rng.randrange(200)] for _ in range(200)]
        po = sum(x == y for x, y in sample) / 200
        ca = collections.Counter(x for x, _ in sample)
        cb = collections.Counter(y for _, y in sample)
        pe = sum(ca[x] * cb[x] for x in LABELS) / 40000
        boots.append((po - pe) / (1 - pe) if pe < 1 else 1.0)
    boots.sort()
    print(f"Cohen κ={score:.6f}; raw agreement={observed:.4f}; bootstrap95=[{boots[124]:.6f},{boots[4874]:.6f}]")
    print("A\\B\t" + "\t".join(LABELS))
    for x in LABELS:
        print(x + "\t" + "\t".join(str(matrix[x][y]) for y in LABELS))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-frame", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--complete", action="store_true")
    parser.add_argument("--kappa", nargs=2, metavar=("PASS_A", "PASS_B"))
    args = parser.parse_args(argv)
    if args.write_frame:
        write_frame()
        return 0
    if args.check:
        return check(args.complete)
    if args.kappa:
        return kappa(*args.kappa)
    parser.error("use --write-frame, --check [--complete], or --kappa A B")


if __name__ == "__main__":
    sys.exit(main())
