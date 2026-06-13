# Import a Dharmamitra ByT5 `unsandhied` segmentation snapshot for the
# compound-depth cross-check.
#
# Networked/model refresh step (mirrors import-dharmamitra-morphology.py). It
# segments the deep-compound surfaces collected by
# build-compound-depth-crosscheck.mjs (src/data/external/compound-depth-candidates.json)
# and writes a snapshot the deterministic build joins back in. Normal atlas
# builds never call the model.
#
# Why a separate importer rather than reusing import-dharmamitra-morphology.py:
# this slice ships isolated off `main`, where that file is not present. The
# shared helpers (SLP1->IAST, the local HF inference skeleton) are duplicated
# deliberately and kept small; once the Dharmamitra PRs land they should be
# factored into a scripts/lib/ module shared by both importers.
#
# Two paths (see --source):
#   pypi  : `dharmamitra-sanskrit-grammar` -> remote dharmamitra.org API. Easy,
#           not reproducible. mode="unsandhied".
#   local : pinned HF chronbmm/sanskrit5-multitask, task prefix "S " (the
#           segmentation task from byt5-sanskrit-analyzers). Reproducible/offline.
#
# Model output is review EVIDENCE only, never a silent build input.
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

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "src" / "data" / "external" / "compound-depth-candidates.json"
OUT = ROOT / "src" / "data" / "external" / "dharmamitra-segmentation.json"

PYPI_MODE = "unsandhied"
HF_MODEL_ID = "chronbmm/sanskrit5-multitask"
HF_TASK_PREFIX = "S "  # segmentation task prefix
HF_MAX_LENGTH = 512

# SLP1 -> IAST (one char per phoneme; see import-dharmamitra-morphology.py).
SLP1_TO_IAST = {
    "a": "a", "A": "ā", "i": "i", "I": "ī", "u": "u", "U": "ū",
    "f": "ṛ", "F": "ṝ", "x": "ḷ", "X": "ḹ",
    "e": "e", "E": "ai", "o": "o", "O": "au",
    "M": "ṃ", "H": "ḥ", "~": "m̐", "z": "ṣ",
    "k": "k", "K": "kh", "g": "g", "G": "gh", "N": "ṅ",
    "c": "c", "C": "ch", "j": "j", "J": "jh", "Y": "ñ",
    "w": "ṭ", "W": "ṭh", "q": "ḍ", "Q": "ḍh", "R": "ṇ",
    "t": "t", "T": "th", "d": "d", "D": "dh", "n": "n",
    "p": "p", "P": "ph", "b": "b", "B": "bh", "m": "m",
    "y": "y", "r": "r", "l": "l", "v": "v", "L": "ḷ",
    "S": "ś", "s": "s", "h": "h", "'": "'",
}


def slp1_to_iast(text):
    return "".join(SLP1_TO_IAST.get(ch, ch) for ch in text)


def segment_count(seg_string):
    """Token count of a segmentation output (whitespace- or underscore-joined)."""
    tokens = [t for t in seg_string.replace("_", " ").split() if t]
    return tokens


def load_candidates(limit):
    doc = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    rows = [(c["key"], c["surfaceSlp1"]) for c in doc.get("candidates", [])]
    return rows[:limit] if limit else rows


def run_pypi(rows, args):
    try:
        from dharmamitra_sanskrit_grammar import DharmamitraSanskritProcessor
    except ImportError:
        sys.exit(
            "dharmamitra-sanskrit-grammar is not installed.\n"
            "  pip install dharmamitra-sanskrit-grammar\n"
            "Note: routes to the remote dharmamitra.org API (not reproducible). "
            "Use --source local for committed runs."
        )
    processor = DharmamitraSanskritProcessor()
    out = {}
    for start in range(0, len(rows), args.batch_size):
        chunk = rows[start:start + args.batch_size]
        inputs = [slp1_to_iast(s) for _, s in chunk]
        results = processor.process_batch(inputs, mode=PYPI_MODE, human_readable_tags=False)
        results = results if isinstance(results, list) else [results]
        for (key, _), iast, res in zip(chunk, inputs, results):
            text = res if isinstance(res, str) else json.dumps(res, ensure_ascii=False)
            segs = segment_count(text)
            out[key] = {"input": iast, "modelSegments": len(segs), "segments": segs}
        print(f"  segmented {min(start + args.batch_size, len(rows))}/{len(rows)}")
    return out, {"endpoint": "remote dharmamitra.org API (not reproducible)"}


def run_local(rows, args):
    try:
        import torch
        from transformers import AutoTokenizer, T5ForConditionalGeneration
    except ImportError:
        sys.exit(
            "Local inference needs torch + transformers:\n"
            "  pip install torch transformers\n"
            "Or use --source pypi for the remote API."
        )
    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"  loading {HF_MODEL_ID}@{args.revision} on {device}...")
    tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_ID, revision=args.revision)
    model = T5ForConditionalGeneration.from_pretrained(HF_MODEL_ID, revision=args.revision).to(device)
    model.eval()

    out = {}
    for start in range(0, len(rows), args.batch_size):
        chunk = rows[start:start + args.batch_size]
        inputs = [slp1_to_iast(s) for _, s in chunk]
        enc = tokenizer([HF_TASK_PREFIX + s for s in inputs], return_tensors="pt",
                        padding=True, truncation=True, max_length=HF_MAX_LENGTH).to(device)
        with torch.no_grad():
            gen = model.generate(**enc, max_length=HF_MAX_LENGTH, num_beams=1)
        decoded = tokenizer.batch_decode(gen, skip_special_tokens=True)
        for (key, _), iast, raw in zip(chunk, inputs, decoded):
            segs = segment_count(raw)
            out[key] = {"input": iast, "modelSegments": len(segs), "segments": segs}
        print(f"  segmented {min(start + args.batch_size, len(rows))}/{len(rows)}")
    return out, {"revision": args.revision, "device": device}


def main():
    ap = argparse.ArgumentParser(description="Snapshot Dharmamitra `unsandhied` segmentation for compound-depth check.")
    ap.add_argument("--source", choices=["pypi", "local"], default="pypi")
    ap.add_argument("--limit", type=int, default=0, help="cap candidates for a pilot (0 = all)")
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--revision", default="main",
                    help="HF model revision for --source local; pin a commit hash for reproducibility")
    ap.add_argument("--device", default=None, help="torch device for --source local")
    args = ap.parse_args()

    if not CANDIDATES.exists():
        sys.exit(f"No candidates file at {CANDIDATES}. Run `npm run build-compound-depth-crosscheck` first.")

    rows = load_candidates(args.limit)
    print(f"Segmenting {len(rows)} compound surfaces via Dharmamitra ({args.source}, mode=unsandhied)...")
    by_surface, extra_source = (run_local if args.source == "local" else run_pypi)(rows, args)

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
