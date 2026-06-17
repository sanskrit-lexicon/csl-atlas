# Import a language classification snapshot for the PWG markup cross-check.
#
# German-aware (Month 5, #115): classifies each PWG {#...#} Sanskrit-marked span
# with two locally-trained SentencePiece models — san.model (Sanskrit) and
# deu.model (German) — by minimum fertility. This replaces the off-the-shelf
# dharmamitra/detect-language eng/skt pair (#95), which modelled only
# English-vs-Sanskrit and so misfired on German + Sanskrit loanwords/inflected
# forms. On a held-out PWG test the German-aware pair lifts accuracy 0.942 ->
# 0.995 and cuts the Sanskrit false-flag rate 5.5% -> 0.3%.
#
# A span that reads as German ("foreign") despite Sanskrit markup is the review
# signal (foreign/OCR content in Sanskrit markup). CPU only (sentencepiece);
# inputs are SLP1 -> IAST. Review EVIDENCE only.
#
# The san/deu models are gitignored binaries — train them first:
#   npm run train-langdetect-german
#
# Usage:
#   python scripts/import-dharmamitra-langdetect.py --limit 500   # pilot
#   python scripts/import-dharmamitra-langdetect.py               # all candidates
#   npm run import-dharmamitra-langdetect

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import dharmamitra_infer as dm  # noqa: E402  (reused only for slp1_to_iast)

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "src" / "data" / "external" / "langdetect-candidates.json"
OUT = ROOT / "src" / "data" / "external" / "dharmamitra-langdetect.json"
MODELS_DIR = Path(__file__).resolve().parent / ".langdetect-models"
MODELS = ("san.model", "deu.model")


def require_models(models_dir):
    paths = {}
    for name in MODELS:
        dest = models_dir / name
        if not dest.exists():
            sys.exit(f"Missing {dest}.\nTrain the German-aware models first:\n  npm run train-langdetect-german")
        paths[name] = dest
    return paths


def load_candidates(limit):
    doc = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    rows = [(c["key"], c["text"]) for c in doc.get("candidates", [])]
    return rows[:limit] if limit else rows


def main():
    ap = argparse.ArgumentParser(description="Classify PWG Sanskrit spans with the German-aware san/deu SentencePiece pair.")
    ap.add_argument("--limit", type=int, default=0, help="cap candidates for a pilot (0 = all)")
    ap.add_argument("--models-dir", default=None, help="dir holding san.model/deu.model (default: cached next to script)")
    args = ap.parse_args()

    try:
        import sentencepiece as spm
    except ImportError:
        sys.exit("sentencepiece is not installed.\n  pip install sentencepiece")

    if not CANDIDATES.exists():
        sys.exit(f"No candidates file at {CANDIDATES}. Run `npm run build-langdetect-crosscheck` first.")

    paths = require_models(Path(args.models_dir) if args.models_dir else MODELS_DIR)
    san = spm.SentencePieceProcessor(); san.load(str(paths["san.model"]))
    deu = spm.SentencePieceProcessor(); deu.load(str(paths["deu.model"]))

    rows = load_candidates(args.limit)
    print(f"Classifying {len(rows)} PWG Sanskrit spans (German-aware san vs deu SentencePiece)...")
    by_key = {}
    foreign = 0
    for i, (key, text) in enumerate(rows, 1):
        iast = dm.slp1_to_iast(text)
        sp = len(san.encode_as_pieces(iast))
        dp = len(deu.encode_as_pieces(iast))
        label = "foreign" if dp < sp else "sanskrit"   # ties -> sanskrit
        if label == "foreign":
            foreign += 1
        by_key[key] = {"iast": iast, "sanPieces": sp, "deuPieces": dp, "label": label}
        if i % 20000 == 0:
            print(f"  classified {i}/{len(rows)}")

    payload = {
        "schemaVersion": "2.0.0",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "generatedBy": "python scripts/import-dharmamitra-langdetect.py",
        "source": {
            "name": "German-aware Sanskrit/German classifier (trained on PWG self-labeled data)",
            "trainer": "scripts/train-langdetect-german.py",
            "method": "san.model vs deu.model SentencePiece fertility; fewer pieces wins (ties -> sanskrit). Mirrors dharmamitra/detect-language with a German model added.",
            "metrics": "src/data/external/langdetect-german-metrics.json (held-out accuracy 0.942 -> 0.995)",
            "license": {
                "label": "Models derived from CDSL PWG markup",
                "note": "Classifications consumed as review evidence only — not redistributed as atlas data."
            },
        },
        "assumptions": [
            "Label 'foreign' means the German SPM tokenized the string more efficiently than the Sanskrit one.",
            "Inputs are PWG {#...#} Sanskrit spans (SLP1 -> IAST); 'foreign' on a Sanskrit-marked span is the review signal (German/Latin/OCR in Sanskrit markup).",
            "Short strings are noisy; the deterministic build applies a fertility margin before flagging.",
        ],
        "warnings": [
            "Models are trained on PWG's own markup, so this measures the markup's internal consistency, not an external gold standard.",
            "Probabilistic signal; do not rewrite PWG markup from this snapshot.",
        ],
        "candidateCount": len(by_key),
        "foreignCount": foreign,
        "byKey": dict(sorted(by_key.items())),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(by_key)} classifications ({foreign} 'foreign') to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
