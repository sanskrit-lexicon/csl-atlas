#!/usr/bin/env python3
"""Build the first source-siglum family review batch from OBS-C candidates."""
import csv
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
IN_CSV = os.path.join(ROOT, "data", "obs", "siglum_family_candidates.csv")
OUT_JSON = os.path.join(ROOT, "src", "data", "review", "source-siglum-family-batch-1.json")


def parse_members(value):
    members = []
    for part in value.split(" | "):
        if not part:
            continue
        key, _, count = part.partition(":")
        members.append({"foldKey": key, "citations": int(count)})
    return members


def main():
    with open(IN_CSV, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))[:50]

    items = []
    for idx, row in enumerate(rows, start=2):
        members = parse_members(row["members"])
        items.append({
            "reviewId": f"source-siglum-family-batch-1:{row['prefix']}",
            "queue": "source-siglum-alias",
            "reviewFamily": "siglum-family-batch-1",
            "subject": {
                "kind": "source-abbreviation",
                "source": row["representative"],
                "canonicalId": row["representative"],
            },
            "sourcePointers": [{
                "dictionary": None,
                "line": idx,
                "sourceLinkMode": "local-only",
                "sourcePath": "data/obs/siglum_family_candidates.csv",
            }],
            "machineValue": {
                "prefix": row["prefix"],
                "representative": row["representative"],
                "nMembers": int(row["n_members"]),
                "totalCitations": int(row["total_freq"]),
                "members": members,
            },
            "evidenceLevel": "derived",
            "reviewStatus": "needs-review",
            "reviewedValue": None,
            "reviewer": None,
            "reviewedAt": None,
            "note": "",
        })

    doc = {
        "schemaVersion": "1.0.0",
        "license": "CC-BY-SA-4.0",
        "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0/",
        "generatedAt": "2026-06-26T00:00:00.000Z",
        "sourcePath": "data/obs/siglum_family_candidates.csv",
        "recordCount": len(items),
        "queue": "source-siglum-alias",
        "reviewFamily": "siglum-family-batch-1",
        "assumptions": [
            "Rows are the first 50 frequency-ranked abbreviation-family candidates from scripts/obs/siglum_families.py.",
            "A row is a review worklist item, not an accepted alias merge.",
            "Only a reviewer may promote a same-work family into src/data/dict-source-aliases.json.",
            "Mixed clusters should be split or left in needs-review rather than merged wholesale.",
        ],
        "warnings": [
            "Prefix families can mix distinct works, authors, editions, or catalogues.",
            "The reviewed seed in src/data/dict-source-aliases.json already covers some high-frequency safe subsets; this packet preserves the remaining batch context.",
        ],
        "items": items,
    }

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"wrote {OUT_JSON} ({len(items)} items)")


if __name__ == "__main__":
    main()
