"""Validate a strict csl-atlas review export against its committed source packet."""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
VERDICTS = {"approve", "reject", "defer"}
REVIEWER = "gasyoun"
REJECTION_NOTE = re.compile(r"^\s*([a-z0-9-]+)\s*:\s*(\S.*)$")
TRADITIONS = {
    "vedic", "epic", "purana", "classical-kavya", "poetics-sastra",
    "grammar-sastra", "dharma-sastra", "lexical-kosa", "medical",
    "jyotisa", "darsana", "buddhist", "jain", "tantra", "other",
}


class ValidationError(ValueError):
    """An exported decision file is not admissible."""


def read_json(relative: str | Path):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def expected_sheets():
    skd = read_json("data/lexico/r2_kosa_fusion_sample.json")
    h4 = read_json("data/lexico/h4_semantic_field_review_packet.json")
    xref = read_json("data/lexico/xref_source_check_packet.json")
    with (ROOT / "data/citations/tradition_tags.tsv").open(encoding="utf-8", newline="") as handle:
        tradition_rows = list(csv.DictReader(handle, delimiter="\t"))

    return {
        "csl-atlas-skd-iti_100units": {
            f"skd-iti:{row['L']}:{row['unitIndex']}":
                (row["klass"], {"authority-terminal", "separable", "other-no-authority"})
            for row in skd["rows"]
        },
        "csl-atlas-tradition-tags_119texts": {
            row["canonical_text"]: (row["tradition"], TRADITIONS)
            for row in tradition_rows if row.get("reviewed") != "yes"
        },
        "csl-atlas-h4-semantic-field_89rows": {
            row["reviewId"]: (row["proposedLabel"], set(row["expectedDecisionLabels"]))
            for row in h4["sampleRows"] if row["reviewStatus"] == "needs-review"
        },
        "csl-atlas-xref-shared-core_40edges": {
            row["sampleId"]: (
                "lexical-shared-core",
                {"prefix-convention", "normalization-risk", "too-sparse"},
            )
            for row in xref["sharedCoreRows"]
        },
    }


def require(condition: bool, message: str):
    if not condition:
        raise ValidationError(message)


def validate_reviewed_at(value):
    require(isinstance(value, str) and value.strip(), "reviewedAt must be present")
    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError("reviewedAt must be a valid ISO-8601 timestamp") from exc
    require(timestamp.tzinfo is not None, "reviewedAt must include a UTC offset")
    require(timestamp.utcoffset().total_seconds() == 0, "reviewedAt must be UTC")


def validate_export(payload, sheets=None):
    sheets = sheets or expected_sheets()
    sheet_id = payload.get("sheet_id")
    require(sheet_id in sheets, f"unknown sheet_id: {sheet_id!r}")
    expected = sheets[sheet_id]

    require(payload.get("complete") is True, "export must have complete:true")
    require(payload.get("reviewer") == REVIEWER, f"reviewer must be {REVIEWER!r}")
    validate_reviewed_at(payload.get("reviewedAt"))

    items = payload.get("items")
    require(isinstance(items, list), "items must be an array")
    require(payload.get("decided") == len(expected), "decided must equal the full sheet count")
    require(len(items) == len(expected), "items must match the sheet 1:1")

    ids = [item.get("id") for item in items]
    require(all(isinstance(item_id, str) and item_id for item_id in ids), "every item needs a stable ID")
    require(len(ids) == len(set(ids)), "item IDs must be unique")
    actual_ids = set(ids)
    expected_ids = set(expected)
    require(actual_ids == expected_ids,
            f"item IDs differ from source packet (missing={sorted(expected_ids - actual_ids)}, "
            f"unknown={sorted(actual_ids - expected_ids)})")

    for item in items:
        item_id = item["id"]
        decision = item.get("decision")
        require(decision in VERDICTS, f"{item_id}: invalid or missing verdict {decision!r}")
        if decision != "reject":
            continue
        note = item.get("note")
        require(isinstance(note, str) and note.strip(), f"{item_id}: rejection requires a note")
        match = REJECTION_NOTE.match(note)
        require(match is not None,
                f"{item_id}: rejection note must be 'corrected-label: rationale'")
        corrected, rationale = match.groups()
        proposed, allowed = expected[item_id]
        require(corrected in allowed, f"{item_id}: corrected label {corrected!r} is outside the closed vocabulary")
        require(corrected != proposed, f"{item_id}: rejected label must differ from the proposal")
        require(bool(rationale.strip()), f"{item_id}: rejection rationale must be non-empty")

    return len(items)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.export.read_text(encoding="utf-8"))
        count = validate_export(payload)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"valid: {args.export} ({count} decisions, reviewer={payload['reviewer']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
