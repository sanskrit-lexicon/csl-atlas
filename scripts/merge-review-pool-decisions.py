"""Merge two independent review-pool keys per row into a promoted overlay (H5483/B7).

Design: docs/REVIEW_POOL_V1_DESIGN.md §8. Each row of a pool packet is keyed by
two pseudonymous annotators (design §5); this tool joins their two decisions.json
exports on item id and applies the five-case truth table:

  A1  same label, both approve            -> reviewed-ok
  A2  same corrected label, both reject   -> reviewed-corrected
  A3  both defer                          -> deferred
  A4  anything else (incl. reject/reject
      with different corrections)         -> needs-review, adjudication queue
  A5  one key missing (dropout)           -> needs-review, flagged single-key,
                                              never promoted

The "resolved label" a decision maps to is looked up against
validate_review_decisions.expected_sheets() -- the same (proposedLabel,
vocabulary) pairs the pool validator checks exports against, so merge and
validation can never disagree about what a row's machine proposal is. For R2
that proposed label is "" (design §7 B5 / validate_review_decisions.py: R2 has
no single machine-proposed label, so approve confirms the diagnostic framing
itself, not a specific value).

A note matching an e-mail, an @handle, a t.me/ link, or any other bare URL
(design §4.5) makes the whole file refuse to merge -- the coordinator redacts
and re-files before the merge can proceed.

Adjudication (design §8): an A4 row is resolved by supplying
--adjudications FILE, a JSON object {"adjudications": [{"reviewId", "verdict"
(reviewed-ok|reviewed-corrected|blocked), "reviewedValue", "adjudicatedBy",
"note"}]}. A tie never silently defaults to the machine's proposed label --
every adjudicated row requires an explicit adjudicatedBy pseudonym and a
non-empty rationale note, regardless of what verdict is chosen.

Usage:
  python scripts/merge-review-pool-decisions.py SHEET_ID EXPORT_A.json EXPORT_B.json \
      [EXPORT_C.json ...] [--adjudications adjudications.json] [--out report.json]

Exit codes: 0 report produced; 2 input/merge error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from validate_review_decisions import expected_sheets, REJECTION_NOTE, POOL_ID  # noqa: E402

DEFER_LABEL = "__defer__"
VALID_VERDICTS = {"reviewed-ok", "reviewed-corrected", "blocked"}

# design §4.5: e-mail, @handle, t.me/ link, or any other user-bearing URL.
CONTACT_PATTERN = re.compile(
    r"[\w.+-]+@[\w-]+\.[\w.-]+"
    r"|(?<!\w)@\w{3,}"
    r"|t\.me/\S+"
    r"|https?://\S+",
    re.IGNORECASE,
)


class MergeError(ValueError):
    """A pool export, adjudication file, or the merge itself is not admissible."""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def scrub_notes(payload: dict, path: Path) -> None:
    for item in payload.get("items", []):
        note = item.get("note") or ""
        if CONTACT_PATTERN.search(note):
            raise MergeError(
                f"{path}: item {item.get('id')!r} note contains a contact-bearing token "
                "(design §4.5) -- redact before merging"
            )


def load_export(path: Path):
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MergeError(f"{path}: cannot read export ({exc})") from None
    scrub_notes(payload, path)
    reviewer = payload.get("reviewer")
    if not (isinstance(reviewer, str) and POOL_ID.match(reviewer)):
        raise MergeError(f"{path}: reviewer {reviewer!r} is not a pool pseudonym (pool-aNN)")
    items = {}
    for item in payload.get("items", []):
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            raise MergeError(f"{path}: an item is missing a stable id")
        if item_id in items:
            raise MergeError(f"{path}: duplicate item id {item_id!r}")
        items[item_id] = item
    return reviewer, items


def resolve_label(decision, note, proposed):
    if decision == "approve":
        return proposed
    if decision == "defer":
        return DEFER_LABEL
    if decision == "reject":
        match = REJECTION_NOTE.match(note or "")
        if not match:
            raise MergeError(f"reject with unparsable note: {note!r}")
        return match.group(1)
    raise MergeError(f"unknown decision {decision!r}")


def merge_packet(sheet_id: str, exports, adjudications: dict | None = None):
    """exports: [(reviewer, {row_id: item}), ...]. Returns list of merged records,
    one per row of the packet, in the packet's own order."""
    sheets = expected_sheets()
    if sheet_id not in sheets:
        raise MergeError(f"unknown sheet_id: {sheet_id!r}")
    expected = sheets[sheet_id]
    adjudications = adjudications or {}

    reviewers_seen = [reviewer for reviewer, _ in exports]
    if len(reviewers_seen) != len(set(reviewers_seen)):
        raise MergeError(f"{sheet_id}: duplicate reviewer among exports: {reviewers_seen}")

    by_row: dict[str, list[tuple[str, dict]]] = {row_id: [] for row_id in expected}
    for reviewer, items in exports:
        for row_id, item in items.items():
            if row_id not in expected:
                raise MergeError(f"{sheet_id}: {reviewer} keyed unknown row id {row_id!r}")
            by_row[row_id].append((reviewer, item))

    records = []
    for row_id, (proposed, _vocabulary) in expected.items():
        keys_raw = by_row[row_id]
        if len(keys_raw) > 2:
            raise MergeError(
                f"{sheet_id}/{row_id}: more than two keys "
                f"({[r for r, _ in keys_raw]}) -- a row is keyed by exactly two annotators"
            )

        keys = [
            {
                "annotator": reviewer,
                "decision": item.get("decision"),
                "resolvedLabel": resolve_label(item.get("decision"), item.get("note"), proposed),
                "note": item.get("note") or "",
            }
            for reviewer, item in keys_raw
        ]

        record = {"reviewId": row_id, "keys": keys, "singleKey": len(keys) < 2}

        if len(keys) < 2:
            # A5: dropout/withdrawal -- never promoted, never counted in kappa.
            record.update(
                reviewStatus="needs-review", reviewedValue=None,
                adjudicated=False, adjudicatedBy=None, note="single-key: not promoted",
            )
            records.append(record)
            continue

        labels = {k["resolvedLabel"] for k in keys}
        decisions = {k["decision"] for k in keys}

        if decisions == {"defer"}:
            record.update(reviewStatus="deferred", reviewedValue=None,
                          adjudicated=False, adjudicatedBy=None, note="")
        elif decisions == {"approve"} and len(labels) == 1:
            record.update(reviewStatus="reviewed-ok", reviewedValue=proposed,
                          adjudicated=False, adjudicatedBy=None, note="")
        elif decisions == {"reject"} and len(labels) == 1:
            record.update(reviewStatus="reviewed-corrected", reviewedValue=next(iter(labels)),
                          adjudicated=False, adjudicatedBy=None, note="")
        else:
            # A4: anything else -- adjudication queue.
            adjudication = adjudications.get(row_id)
            if adjudication is None:
                record.update(reviewStatus="needs-review", reviewedValue=None,
                              adjudicated=False, adjudicatedBy=None, note="")
            else:
                verdict = adjudication.get("verdict")
                if verdict not in VALID_VERDICTS:
                    raise MergeError(f"{sheet_id}/{row_id}: bad adjudication verdict {verdict!r}")
                adjudicated_by = adjudication.get("adjudicatedBy")
                if not (isinstance(adjudicated_by, str) and adjudicated_by.strip()):
                    raise MergeError(f"{sheet_id}/{row_id}: adjudication missing adjudicatedBy")
                rationale = adjudication.get("note")
                if not (isinstance(rationale, str) and rationale.strip()):
                    raise MergeError(f"{sheet_id}/{row_id}: adjudication missing rationale note")
                record.update(
                    reviewStatus=verdict,
                    reviewedValue=adjudication.get("reviewedValue") if verdict != "blocked" else None,
                    adjudicated=True, adjudicatedBy=adjudicated_by, note=rationale,
                )
        records.append(record)
    return records


def load_adjudications(path: Path | None):
    if path is None:
        return {}
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = payload.get("adjudications")
    if not isinstance(rows, list):
        raise MergeError(f"{path}: 'adjudications' must be a list")
    out = {}
    for row in rows:
        review_id = row.get("reviewId")
        if not isinstance(review_id, str) or not review_id:
            raise MergeError(f"{path}: an adjudication row is missing reviewId")
        if review_id in out:
            raise MergeError(f"{path}: duplicate adjudication for {review_id!r}")
        out[review_id] = row
    return out


def build_report(sheet_id: str, export_paths, adjudication_path: Path | None = None):
    exports = [load_export(Path(p)) for p in export_paths]
    adjudications = load_adjudications(adjudication_path)
    records = merge_packet(sheet_id, exports, adjudications)
    counts = Counter(r["reviewStatus"] for r in records)
    return {
        "schemaVersion": "1.0.0",
        "generatedAt": now_iso(),
        "generatedBy": "npm run merge-review-pool-decisions",
        "poolVersion": "v1",
        "sheetId": sheet_id,
        "rows": len(records),
        "rowsDoubleKeyed": sum(1 for r in records if not r["singleKey"]),
        "rowsSingleKey": sum(1 for r in records if r["singleKey"]),
        "counts": dict(sorted(counts.items())),
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("sheet_id")
    parser.add_argument("exports", nargs="+", type=Path)
    parser.add_argument("--adjudications", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    try:
        report = build_report(args.sheet_id, args.exports, args.adjudications)
    except (MergeError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out} ({report['rows']} rows, {report['rowsDoubleKeyed']} double-keyed, "
              f"counts={report['counts']})")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
