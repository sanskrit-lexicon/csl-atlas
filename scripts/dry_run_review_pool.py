#!/usr/bin/env python3
"""H5308 two-annotator dry run over the R2 pilot (design §10 P3).

Mechanically keys each dry-run annotator's R2 slice (approve = confirm the
diagnostic framing; the machinery under test is sheets → exports → pool-mode
validator, not annotator judgment), writes the two decisions files as canary
evidence under data/review/pool_dry_run/, validates them with
--pool, and prints the packet coverage table. H4/xref slices are validated
transiently and NOT persisted as decision files (never look like real keys).
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import validate_review_decisions as V  # noqa: E402

MANIFEST = "data/review/pool_assignment.json"
OUT = ROOT / "data/review/pool_dry_run"


def export_for(sheet_id: str, reviewer: str, row_ids):
    return {
        "sheet_id": sheet_id,
        "generated": "25-09-2026",
        "decided": len(row_ids),
        "reviewer": reviewer,
        "reviewedAt": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "complete": True,
        "items": [{"id": row_id, "decision": "approve", "note": ""} for row_id in row_ids],
    }


def main() -> int:
    pool = V.load_pool(ROOT / MANIFEST)
    annotators = pool["annotators"]
    print(f"pool manifest: n={len(annotators)} {annotators}")
    print("--- packet coverage (packet rows / keyable / dealt) ---")
    r2 = json.loads((ROOT / "data/lexico/r2_checkpoint_review_packet.json").read_text(encoding="utf-8"))
    h4 = json.loads((ROOT / "data/lexico/h4_semantic_field_review_packet.json").read_text(encoding="utf-8"))
    xref = json.loads((ROOT / "data/lexico/xref_source_check_packet.json").read_text(encoding="utf-8"))
    for name, total, stem in [
        ("R2 checkpoint", len(r2["checkpointRows"]), "csl-atlas-r2-checkpoint_10rows"),
        ("H4 semantic field", len(h4["sampleRows"]), "csl-atlas-h4-semantic-field_89rows"),
        ("xref shared core", len(xref["sharedCoreRows"]) + len(xref["prefixControlRows"]),
         "csl-atlas-xref-shared-core_40edges"),
    ]:
        dealt = len(pool["packets"][stem]["rows"])
        print(f"{name}: packet rows={total} keyable/dealt={dealt}")

    OUT.mkdir(parents=True, exist_ok=True)
    print("--- two-annotator dry run: R2 pilot exports ---")
    r2_stem = "csl-atlas-r2-checkpoint_10rows"
    for reviewer in annotators:
        rows = sorted(row_id for row_id, keys in pool["packets"][r2_stem]["rows"].items() if reviewer in keys)
        payload = export_for(r2_stem, reviewer, rows)
        target = OUT / f"{r2_stem}__{reviewer}__DRY-RUN.json"
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_review_decisions.py"),
             str(target), "--pool", str(ROOT / MANIFEST)],
            capture_output=True, text=True, cwd=ROOT)
        print(f"{reviewer}: {result.stdout.strip() or result.stderr.strip()}")
        if result.returncode != 0:
            return 1
    print("--- transient slice validation: H4 + xref (not persisted) ---")
    for stem in ("csl-atlas-h4-semantic-field_89rows", "csl-atlas-xref-shared-core_40edges"):
        for reviewer in annotators:
            rows = sorted(row_id for row_id, keys in pool["packets"][stem]["rows"].items() if reviewer in keys)
            payload = export_for(stem, reviewer, rows)
            expected = V.pool_expected(pool, stem, reviewer)
            count = V.validate_export(payload, pool=pool)
            assert count == len(expected) == len(rows)
            print(f"{reviewer} × {stem}: pool-mode validation PASS ({count} rows)")
    print("DRY RUN PASS: two decisions files persisted under data/review/pool_dry_run/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
