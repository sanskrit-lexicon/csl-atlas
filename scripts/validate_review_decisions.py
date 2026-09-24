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
# H5308: pool sheets are keyed under pseudonyms (design §4); the roster's known
# pseudonyms come from the pool assignment manifest, never a hard-coded list.
POOL_ID = re.compile(r"^pool-a\d{2,}$")
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
    r2 = read_json("data/lexico/r2_checkpoint_review_packet.json")
    with (ROOT / "data/citations/tradition_tags.tsv").open(encoding="utf-8", newline="") as handle:
        tradition_rows = list(csv.DictReader(handle, delimiter="\t"))

    # B1 (H5308, design §3.1): the H4 sheet shows open rows if any, else the
    # reviewed-ok set — mirroring h4_items() in build-review-sheets.py. The old
    # needs-review-only filter broke after H1621 flipped all 105 rows: the
    # validator expected 0 rows while the builder emitted 89 cards, so every
    # returned H4 export failed on `decided must equal the full sheet count`.
    h4_open = [r for r in h4["sampleRows"] if r["reviewStatus"] == "needs-review"]
    h4_rows = h4_open or [r for r in h4["sampleRows"] if r["reviewStatus"] == "reviewed-ok"]

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
            for row in h4_rows
        },
        "csl-atlas-xref-shared-core_40edges": {
            row["sampleId"]: (
                "lexical-shared-core",
                {"prefix-convention", "normalization-risk", "too-sparse"},
            )
            for row in xref["sharedCoreRows"]
        },
        # B5 (H5308, design §7): R2 never had a sheet or a validator entry. There is
        # no single machine-proposed label — the packet proposes a closed vocabulary
        # per row (proposedParserLabels), so proposed is "" and the annotator names
        # their label via the reject-note contract (`label: rationale`); approve
        # confirms the diagnostic framing itself. MG's recorded reviewedValue is
        # deliberately NOT consulted here — it is the withheld expert baseline.
        "csl-atlas-r2-checkpoint_10rows": {
            row["checkpointId"]: ("", set(row["proposedParserLabels"]))
            for row in r2["checkpointRows"]
        },
    }


def load_pool(path: str | Path):
    """Load the pool assignment manifest (H5308, design §5)."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    annotators = payload.get("annotators")
    packets = payload.get("packets")
    require(isinstance(annotators, list) and len(annotators) >= 2,
            "pool manifest: annotators must list >= 2 pseudonyms")
    require(all(POOL_ID.match(a) for a in annotators),
            "pool manifest: annotator IDs must be pool-aNN pseudonyms")
    require(isinstance(packets, dict) and packets,
            "pool manifest: packets object missing")
    for packet_id, packet in packets.items():
        require(isinstance(packet.get("rows"), dict),
                f"pool manifest: {packet_id} rows missing")
    return payload


def pool_expected(pool, sheet_id: str, reviewer: str):
    """The annotator's assigned row IDs for one sheet, as an expected_sheets-style
    dict (proposed/vocabulary pairs inherited from the full sheet). The manifest
    maps rowId -> [key A, key B]; the slice inverts it."""
    require(reviewer in pool["annotators"],
            f"pool mode: reviewer {reviewer!r} is not a known pool pseudonym")
    packet = pool["packets"].get(sheet_id)
    require(packet is not None, f"pool manifest has no packet {sheet_id!r}")
    rows = [row_id for row_id, keys in packet["rows"].items() if reviewer in keys]
    require(bool(rows), f"pool manifest: {reviewer} has no assigned rows for {sheet_id!r}")
    full = expected_sheets()[sheet_id]
    unknown = [row_id for row_id in rows if row_id not in full]
    require(not unknown, f"pool manifest assigns unknown rows for {sheet_id!r}: {unknown}")
    return {row_id: full[row_id] for row_id in rows}


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


def validate_export(payload, sheets=None, pool=None):
    sheets = sheets or expected_sheets()
    sheet_id = payload.get("sheet_id")
    require(sheet_id in sheets, f"unknown sheet_id: {sheet_id!r}")
    expected = sheets[sheet_id]

    reviewer = payload.get("reviewer")
    require(isinstance(reviewer, str) and reviewer.strip(), "reviewer must be present")
    if pool is not None:
        # B2 (H5308, design §5/§7): a pool export is a per-annotator slice. The
        # reviewer must be a known pseudonym and the item set must equal THAT
        # annotator's assigned rows, not the whole sheet.
        expected = pool_expected(pool, sheet_id, reviewer)
    else:
        require(reviewer == REVIEWER, f"reviewer must be {REVIEWER!r}")
    validate_reviewed_at(payload.get("reviewedAt"))
    require(payload.get("complete") is True, "export must have complete:true")

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
        if pool is not None and decision == "defer":
            # B2 (design §7): in pool mode a defer must say what blocked it, or the
            # adjudication queue has nothing to read.
            note = item.get("note")
            require(isinstance(note, str) and note.strip(),
                    f"{item_id}: pool defer requires a note")
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
    parser.add_argument(
        "--pool", type=Path, default=None,
        help="pool assignment manifest (H5308): validate a per-annotator slice "
             "against that annotator's assigned rows instead of the whole sheet")
    args = parser.parse_args()
    try:
        payload = json.loads(args.export.read_text(encoding="utf-8"))
        pool = load_pool(args.pool) if args.pool else None
        count = validate_export(payload, pool=pool)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"valid: {args.export} ({count} decisions, reviewer={payload['reviewer']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
