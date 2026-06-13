# Import a Dharmamitra ByT5 `lemma` snapshot for the lemma-normalization
# cross-check.
#
# Networked/model refresh step. It lemmatizes the candidate headwords collected
# by build-lemma-normalization-crosscheck.mjs (src/data/external/
# lemma-normalization-candidates.json) and writes a snapshot the deterministic
# build joins back in. Normal atlas builds never call the model.
#
# First consumer of scripts/lib/dharmamitra_infer.py — no duplicated SLP1->IAST
# table or HF skeleton here.
#
# Usage:
#   python scripts/import-dharmamitra-lemma.py --source pypi --limit 50
#   python scripts/import-dharmamitra-lemma.py --source local --revision <sha>
#   npm run import-dharmamitra-lemma -- --limit 50

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
CANDIDATES = ROOT / "src" / "data" / "external" / "lemma-normalization-candidates.json"
OUT = ROOT / "src" / "data" / "external" / "dharmamitra-lemma.json"

PYPI_MODE = "lemma"
LOCAL_PREFIX = "L "


def model_lemma(raw):
    """The `lemma` task returns space/underscore-joined lemmas; a single
    headword yields one. Take the first token as its lemma."""
    tokens = [t for t in (raw or "").replace("_", " ").split() if t]
    return tokens[0] if tokens else None


def load_candidates(limit):
    doc = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    rows = [(c["key"], c["lemmaSlp1"]) for c in doc.get("candidates", [])]
    return rows[:limit] if limit else rows


def main():
    ap = dm.add_common_args(argparse.ArgumentParser(
        description="Snapshot Dharmamitra `lemma` output for the normalization cross-check."))
    args = ap.parse_args()

    if not CANDIDATES.exists():
        sys.exit(f"No candidates file at {CANDIDATES}. Run `npm run build-lemma-normalization-crosscheck` first.")

    rows = load_candidates(args.limit)
    print(f"Lemmatizing {len(rows)} headwords via Dharmamitra ({args.source}, mode=lemma)...")
    raw_by_key, extra_source = dm.run(rows, pypi_mode=PYPI_MODE, local_prefix=LOCAL_PREFIX, args=args)

    by_lemma = {}
    for key, rec in raw_by_key.items():
        by_lemma[key] = {"input": rec["input"], "modelLemmaIast": model_lemma(rec["raw"]), "raw": rec["raw"]}
    resolved = sum(1 for v in by_lemma.values() if v["modelLemmaIast"])

    payload = {
        "schemaVersion": "1.0.0",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "generatedBy": f"python scripts/import-dharmamitra-lemma.py --source {args.source}",
        "source": {
            "name": "Dharmamitra ByT5-Sanskrit analyzer (lemma)",
            "package": "dharmamitra-sanskrit-grammar (PyPI)" if args.source == "pypi" else "byt5-sanskrit-analyzers (local HF)",
            "models": ["chronbmm/sanskrit5-multitask"],
            "repository": "https://github.com/dharmamitra/byt5-sanskrit-analyzers",
            "paper": "arXiv:2409.13920 (Nehrdich, Hellwig & Keutzer, EMNLP Findings 2024)",
            "mode": "lemma",
            "license": {
                "label": "MIT (wrapper); model cards on HuggingFace; DCS-trained",
                "note": "Predictions consumed as review evidence only — not redistributed as atlas data."
            },
            **extra_source,
        },
        "assumptions": [
            "Inputs are atlas lemma keys (SLP1 -> IAST) from lemma-normalization-candidates.json.",
            "modelLemmaIast is the first token of the `lemma` output; the SLP1 comparison happens in the deterministic build via lookup-normalize.js.",
            "The 'pypi' source calls the remote API and is not reproducible; pin a local revision for committed snapshots.",
        ],
        "warnings": [
            "ByT5 lemma is a probabilistic output; disagreement with the atlas key is a review signal, not ground truth.",
            "Do not rewrite the normalizer or any dictionary headword from this snapshot.",
        ],
        "mode": "lemma",
        "lemmaCount": len(by_lemma),
        "resolvedCount": resolved,
        "byLemma": dict(sorted(by_lemma.items())),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(by_lemma)} lemma rows ({resolved} resolved) to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
