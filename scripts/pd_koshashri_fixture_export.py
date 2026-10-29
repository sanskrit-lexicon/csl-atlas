#!/usr/bin/env python3
"""H7316 — deterministic one-entry KoshaSHRI fixture TSV export.

The restricted source response is local-only (default:
``data/pd/koshashri_vocable.json``) and is never fetched or emitted by this
script. Only the two fixture TSVs are built. Tests and --check use no network.

Usage:
    python3 scripts/pd_koshashri_fixture_export.py [--input PATH]
    python3 scripts/pd_koshashri_fixture_export.py --check [--input PATH]

Exit codes: 0 ok, 2 STOP_CANARY_MISMATCH or stale TSV, 3 missing input.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
from collections import Counter
from pathlib import Path
import sys

HERE = Path(__file__).resolve()
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from pd_koshashri_vocable import citation_records, entry_record, parse_response

DATA = ROOT / "data" / "pd"
DEFAULT_INPUT = DATA / "koshashri_vocable.json"
EDITION_MAP = DATA / "pd_work_edition_map.tsv"
ENTRY_PATH = DATA / "pd_koshashri_entries.tsv"
CITATION_PATH = DATA / "pd_koshashri_citations.tsv"
RV_WORK_ID = "PDW-ecd09ac913"
VALIDATION = "unvalidated_pending_double_annotation"

ENTRY_FIELDS = [
    "source", "source_entry_id", "headword_devanagari", "headword_iast",
    "lemma_slp1", "normalization_status", "source_volume", "grammar_raw",
    "grammar_label", "subcategory", "grammatical_note_raw_html",
    "etymology_raw_html", "sandhi", "nested_vocables", "validation_state",
    "provenance",
]
CITATION_FIELDS = [
    "source", "source_entry_id", "sense_id", "source_citation_id",
    "quotation_text", "source_siglum", "work_title_candidate", "work_id",
    "work_resolution_status", "locus", "locus_scheme", "work_date_raw",
    "reference_author", "validation_state", "provenance",
]


class CanaryMismatch(RuntimeError):
    pass


def _json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _tsv(fields, rows) -> str:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def _rv_resolver(siglum: str):
    """Resolve only the contract's ṚV. pin; every other siglum stays unresolved."""
    if siglum != "ṚV.":
        return None
    with EDITION_MAP.open(encoding="utf-8", newline="") as fh:
        matches = [row for row in csv.DictReader(fh, delimiter="\t")
                   if row["dictionary_siglum"] == siglum]
    work_ids = {row["work_id"] for row in matches}
    if work_ids != {RV_WORK_ID}:
        raise CanaryMismatch(f"STOP_CANARY_MISMATCH: ṚV. registry ids={sorted(work_ids)}")
    return RV_WORK_ID


def build(input_path: Path = DEFAULT_INPUT):
    outer, vocable, nested = parse_response(input_path.read_text(encoding="utf-8"))
    entry = entry_record(outer, vocable, nested)
    provenance = f"koshashri:/search/vocable/{outer['id']}"
    entry["source_volume"] = _json(entry["source_volume"])
    entry["sandhi"] = _json(entry["sandhi"])
    entry["nested_vocables"] = _json(entry["nested_vocables"])
    entry["provenance"] = provenance
    citations = citation_records(outer, vocable, work_resolver=_rv_resolver)
    for row in citations:
        row["locus"] = _json(row["locus"])
        row["provenance"] = provenance
        if row["work_id"]:
            row["provenance"] += ";data/pd/pd_work_edition_map.tsv:ṚV."
    check_canaries(outer, vocable, nested, entry, citations)
    return {
        ENTRY_PATH: _tsv(ENTRY_FIELDS, [entry]),
        CITATION_PATH: _tsv(CITATION_FIELDS, citations),
    }


def check_canaries(outer, vocable, nested, entry, citations):
    first_citations = vocable["meaning"][0]["citations"]
    first_rows = [row for row in citations if row["sense_id"].endswith(":1")]
    multiplicities = Counter(len(row["references"]) for row in first_citations)
    paths = {row["sense_id"] for row in citations}
    other_work = [row for row in citations if row["source_siglum"] != "ṚV."]
    checks = [
        (outer["id"] == "3b892686-9184-4bce-a2cc-aaa78551e517", "entry id"),
        (len(vocable["meaning"]) == 29, "29 meanings"),
        (len(first_citations) == 242, "242 first-meaning citation texts"),
        (len(first_rows) == 248, "248 first-meaning reference rows"),
        (multiplicities == Counter({1: 237, 2: 4, 3: 1}), "multi-reference split"),
        (citations[0]["source_siglum"] == "ṚV.", "ṚV. siglum"),
        (citations[0]["work_id"] == RV_WORK_ID, "ṚV. work id"),
        (citations[0]["locus"] == '["i.12.6;"]', "ṚV. locus"),
        (citations[0]["locus_scheme"] == "Maṇḍala.Sūkta.Ṛc.", "locus scheme"),
        (citations[0]["work_date_raw"] == "1400BCE", "work date"),
        (entry["source_volume"] == '{"name":"Volume 2","volumeNumber":4}', "volume object"),
        (len(nested) == 1, "one nested vocable"),
        (entry["grammatical_note_raw_html"].startswith("<s<small>"), "source defect"),
        (any(path.endswith(":2i") for path in paths), "2i sense path"),
        (any(path.endswith(":2ii") for path in paths), "2ii sense path"),
        (all(row["work_id"] is None and row["work_resolution_status"] == "unresolved"
              for row in other_work), "other works unresolved"),
        (all(row["validation_state"] == VALIDATION for row in citations), "validation state"),
        (len({row["source_citation_id"] for row in citations}) == len(citations),
         "unique citation ids"),
    ]
    failed = [name for name, ok in checks if not ok]
    if failed:
        raise CanaryMismatch("STOP_CANARY_MISMATCH: " + ", ".join(failed))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not args.input.is_file():
        print(f"restricted fixture input missing: {args.input}", file=sys.stderr)
        return 3
    try:
        built = build(args.input)
        if args.check:
            stale = [str(path) for path, text in built.items()
                     if not path.is_file() or path.read_text(encoding="utf-8") != text]
            if stale:
                print("STOP_CANARY_MISMATCH: stale TSV: " + ", ".join(stale), file=sys.stderr)
                return 2
            print(f"OK: 1 entry, {sum(1 for _ in CITATION_PATH.open(encoding='utf-8')) - 1} "
                  "citation-reference rows; canaries and byte identity green")
            return 0
        for path, text in built.items():
            with path.open("w", encoding="utf-8", newline="") as fh:
                fh.write(text)
        print(f"wrote {ENTRY_PATH} and {CITATION_PATH}")
        return 0
    except (CanaryMismatch, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
