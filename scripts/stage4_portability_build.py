#!/usr/bin/env python3
"""Build the Stage 4 external-portability gate census JSON (H7507).

Merges the frozen payload modules (ONP block + the other three candidates
and shared fields) into data/stage4_portability/stage4_gate_census.json.
The payload files carry the probe records verbatim; the evidence hashes
inside them are re-verified from the committed files by
scripts/stage4_portability_check.py — this builder does not recompute them.
"""
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from stage4_portability_payload_onp import ONP_CANDIDATE  # noqa: E402
from stage4_portability_payload_rest import REST  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "stage4_portability" / "stage4_gate_census.json"


def main() -> int:
    census = dict(REST["statics"])
    census["candidates"] = [ONP_CANDIDATE] + REST["rest_candidates"]
    census["reversal_conditions_recheck"] = REST["reversal_conditions_recheck"]
    census["preregistrations_onp_menota_p1_p5"] = REST["preregistrations_onp_menota_p1_p5"]
    census["section9_reading_printed_alongside"] = REST["section9_reading_printed_alongside"]
    census["verdict_summary"] = REST["verdict_summary"]
    OUT.write_text(
        json.dumps(census, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
