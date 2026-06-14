# Import a Dharmamitra ByT5 `unsandhied` segmentation snapshot for the
# compound-depth cross-check.
#
# Networked/model refresh step. It segments the deep-compound surfaces collected
# by build-compound-depth-crosscheck.mjs (src/data/external/
# compound-depth-candidates.json) and writes a snapshot the deterministic build
# joins back in. Normal atlas builds never call the model.
#
# Generic inference (SLP1->IAST, pypi/local HF, CLI args) comes from
# scripts/lib/dharmamitra_infer.py; this file only owns the segmentation
# post-processing (token count). Model output is review EVIDENCE only.
#
# Usage:
#   python scripts/import-dharmamitra-segmentation.py --source pypi --limit 50
#   python scripts/import-dharmamitra-segmentation.py --source local --revision <sha>
#   npm run import-dharmamitra-segmentation -- --limit 50

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import dharmamitra_infer as dm  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "src" / "data" / "external" / "compound-depth-candidates.json"
OUT = ROOT / "src" / "data" / "external" / "dharmamitra-segmentation.json"

PYPI_MODE = "unsandhied"
LOCAL_PREFIX = "S "  # segmentation task prefix


def segment_count(seg_string):
    """Tokens of a segmentation output (whitespace- or underscore-joined)."""
    return [t for t in (seg_string or "").replace("_", " ").split() if t]


def load_candidates(limit):
    doc = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    rows = [(c["key"], c["surfaceSlp1"]) for c in doc.get("candidates", [])]
    return rows[:limit] if limit else rows


def main():
    ap = dm.add_common_args(argparse.ArgumentParser(
        description="Snapshot Dharmamitra `unsandhied` segmentation for compound-depth check."))
    args = ap.parse_args()

    if not CANDIDATES.exists():
        sys.exit(f"No candidates file at {CANDIDATES}. Run `npm run build-compound-depth-crosscheck` first.")

    rows = load_candidates(args.limit)
    print(f"Segmenting {len(rows)} compound surfaces via Dharmamitra ({args.source}, mode=unsandhied)...")
    raw_by_key, extra_source = dm.run(rows, pypi_mode=PYPI_MODE, local_prefix=LOCAL_PREFIX, args=args)

    by_surface = {}
    for key, rec in raw_by_key.items():
        segs = segment_count(rec["raw"])
        by_surface[key] = {"input": rec["input"], "modelSegments": len(segs), "segments": segs}

    payload = {
        "schemaVersion": "1.0.0",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "generatedBy": f"python scripts/import-dharmamitra-segmentation.py --source {args.source}",
        "source": {
            "name": "Dharmamitra ByT5-Sanskrit analyzer (unsandhied)",
            "package": "dharmamitra-sanskrit-grammar (PyPI)" if args.source == "pypi" else "byt5-sanskrit-analyzers (local HF)",
            "models": ["chronbmm/sanskrit5-multitask"],
            "repository": "https://github.com/dharmamitra/byt5-sanskrit-analyzers",
            "paper": "arXiv:2409.13920 (Nehrdich, Hellwig & Keutzer, EMNLP Findings 2024)",
            "mode": "unsandhied",
            "license": {
                "label": "MIT (wrapper); model cards on HuggingFace; DCS-trained",
                "note": "Predictions consumed as review evidence only — not redistributed as atlas data."
            },
            **extra_source,
        },
        "assumptions": [
            "Inputs are deep-compound surfaces (SLP1 -> IAST) from compound-depth-candidates.json.",
            "modelSegments is the token count of the `unsandhied` output; compared against the markup's compoundSegmentCount.",
            "The 'pypi' source calls the remote API and is not reproducible; pin a local revision for committed snapshots.",
        ],
        "warnings": [
            "ByT5 segmentation is a probabilistic output; disagreement with markup is a review signal, not ground truth.",
            "Do not rewrite the atlas depth metric or mw.txt from this snapshot.",
        ],
        "mode": "unsandhied",
        "count": len(by_surface),
        "bySurface": dict(sorted(by_surface.items())),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(by_surface)} segmentation rows to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
