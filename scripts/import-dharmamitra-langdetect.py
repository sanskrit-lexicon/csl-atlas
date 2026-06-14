# Import a Dharmamitra detect-language classification snapshot for the
# PWG markup cross-check.
#
# Unlike the ByT5 importers, this uses dharmamitra/detect-language: two
# SentencePiece models (eng.model, skt.model). A string is classified by
# whichever model tokenizes it into FEWER pieces (lower fertility) — so it is
# effectively a Sanskrit / not-Sanskrit separator. Inputs are PWG {#...#}
# Sanskrit spans (SLP1), transliterated to IAST here; a span that lands on the
# not-Sanskrit ("en") side is the review signal (foreign content in Sanskrit
# markup). SLP1/IAST is distinctive, so genuine Sanskrit reliably reads "sa".
#
# It runs on CPU (sentencepiece only, no GPU/torch), so unlike the ByT5 steps
# this produces REAL data, not model-pending scaffolding. The models (~0.5 MB
# each) are fetched from the pinned repo on first run and cached.
#
# Consumes the candidate spans written by build-langdetect-crosscheck.mjs and
# writes a classification snapshot the deterministic build joins back in.
# SLP1->IAST reuses scripts/lib/dharmamitra_infer.py. Model output is review
# EVIDENCE only.
#
# Usage:
#   python scripts/import-dharmamitra-langdetect.py --limit 500   # pilot
#   python scripts/import-dharmamitra-langdetect.py               # all candidates
#   npm run import-dharmamitra-langdetect

import argparse
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import dharmamitra_infer as dm  # noqa: E402  (reused only for slp1_to_iast)

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "src" / "data" / "external" / "langdetect-candidates.json"
OUT = ROOT / "src" / "data" / "external" / "dharmamitra-langdetect.json"
CACHE = Path(__file__).resolve().parent / ".langdetect-models"

REPO = "https://github.com/dharmamitra/detect-language"
RAW = "https://raw.githubusercontent.com/dharmamitra/detect-language/{rev}/models/{name}"
MODELS = ("eng.model", "skt.model")


def ensure_models(revision, models_dir):
    models_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name in MODELS:
        dest = models_dir / name
        if not dest.exists():
            url = RAW.format(rev=revision, name=name)
            print(f"  fetching {name}: {url}")
            urllib.request.urlretrieve(url, dest)
        paths[name] = dest
    return paths


def load_candidates(limit):
    doc = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    rows = [(c["key"], c["text"]) for c in doc.get("candidates", [])]
    return rows[:limit] if limit else rows


def main():
    ap = argparse.ArgumentParser(description="Classify PWG glosses with Dharmamitra detect-language (eng vs skt SPM).")
    ap.add_argument("--limit", type=int, default=0, help="cap candidates for a pilot (0 = all)")
    ap.add_argument("--revision", default="main", help="detect-language repo revision (pin a commit for reproducibility)")
    ap.add_argument("--models-dir", default=None, help="dir holding eng.model/skt.model (default: cached next to script)")
    args = ap.parse_args()

    try:
        import sentencepiece as spm
    except ImportError:
        sys.exit("sentencepiece is not installed.\n  pip install sentencepiece")

    if not CANDIDATES.exists():
        sys.exit(f"No candidates file at {CANDIDATES}. Run `npm run build-langdetect-crosscheck` first.")

    models_dir = Path(args.models_dir) if args.models_dir else CACHE
    paths = ensure_models(args.revision, models_dir)
    eng = spm.SentencePieceProcessor(); eng.load(str(paths["eng.model"]))
    skt = spm.SentencePieceProcessor(); skt.load(str(paths["skt.model"]))

    rows = load_candidates(args.limit)
    print(f"Classifying {len(rows)} PWG Sanskrit spans via detect-language (eng vs skt SentencePiece)...")
    by_key = {}
    not_sanskrit = 0
    for i, (key, text) in enumerate(rows, 1):
        iast = dm.slp1_to_iast(text)  # skt.model expects romanized Sanskrit
        e = len(eng.encode_as_pieces(iast))
        s = len(skt.encode_as_pieces(iast))
        # detect.py: "en" if eng strictly shorter, else "sa" (ties -> sa).
        label = "en" if e < s else "sa"
        if label == "en":
            not_sanskrit += 1
        by_key[key] = {"iast": iast, "engPieces": e, "sktPieces": s, "label": label}
        if i % 20000 == 0:
            print(f"  classified {i}/{len(rows)}")

    payload = {
        "schemaVersion": "1.0.0",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "generatedBy": "python scripts/import-dharmamitra-langdetect.py",
        "source": {
            "name": "Dharmamitra detect-language",
            "repository": REPO,
            "revision": args.revision,
            "method": "eng.model vs skt.model SentencePiece fertility; fewer pieces wins (ties -> sa).",
            "license": {
                "label": "Dharmamitra GitHub organization license",
                "note": "Classifications consumed as review evidence only — not redistributed as atlas data."
            },
        },
        "assumptions": [
            "Label 'en' means the English SPM tokenized the string more efficiently than the Sanskrit one (does not read as Sanskrit).",
            "Inputs are PWG {#...#} Sanskrit spans (SLP1 -> IAST); 'en' on a Sanskrit-marked span is the review signal.",
            "Short strings are noisy; the deterministic build applies a fertility margin before flagging.",
        ],
        "warnings": [
            "detect-language separates Sanskrit from English; SLP1/IAST Sanskrit is distinctive, so 'en' on a Sanskrit-marked span flags genuine non-Sanskrit content (German, Latin, OCR).",
            "Probabilistic signal; do not rewrite PWG markup from this snapshot.",
        ],
        "candidateCount": len(by_key),
        "notSanskritCount": not_sanskrit,
        "byKey": dict(sorted(by_key.items())),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(by_key)} classifications ({not_sanskrit} 'en'/not-sanskrit) to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
