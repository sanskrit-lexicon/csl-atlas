# Month 5 — train a German-aware Sanskrit/German classifier (scaffold).
#
# #95 (PWG markup cross-check) was low-precision because dharmamitra/detect-language
# models only English-vs-Sanskrit; German is unmodelled, so German words and
# Sanskrit loanwords/inflected forms misfire. The fix the roadmap anticipated:
# add a German model. The training data is FREE — PWG self-labels it: {#...#} is
# Sanskrit (SLP1), {%...%} is German. This trains a SentencePiece model per
# language (CPU, fast) and classifies by minimum fertility, exactly mirroring
# detect-language's method, then measures the lift vs the eng-vs-skt baseline.
#
# Runnable scaffold: trains real models from PWG and reports accuracy. Models go
# to scripts/.langdetect-models/ (gitignored); the metrics JSON is committed.
# To wire into production, point import-dharmamitra-langdetect.py at san.model +
# deu.model (3-way / san-vs-deu fertility) instead of eng/skt.
#
# Usage: python scripts/train-langdetect-german.py [--cap 80000] [--vocab 4000]

import argparse
import json
import random
import re
import sys
import tempfile
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import dharmamitra_infer as dm  # reuse slp1_to_iast  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PWG = ROOT / ".." / "csl-orig" / "v02" / "pwg" / "pwg.txt"
MODELS = Path(__file__).resolve().parent / ".langdetect-models"
METRICS = ROOT / "src" / "data" / "external" / "langdetect-german-metrics.json"

SAN_RE = re.compile(r"\{#([^#]*)#\}")
DEU_RE = re.compile(r"\{%([^%]*)%\}")
ACCENTS = re.compile(r"[/\\^~]")
BASE_MODELS = "https://raw.githubusercontent.com/dharmamitra/detect-language/main/models/{name}"


def extract_labeled(cap):
    text = PWG.read_text(encoding="utf-8")
    san, deu = set(), set()
    for m in SAN_RE.finditer(text):
        s = dm.slp1_to_iast(ACCENTS.sub("", m.group(1)).strip())
        if len(s) >= 3:
            san.add(s)
    for m in DEU_RE.finditer(text):
        g = m.group(1).strip()
        if len(g) >= 3:
            deu.add(g)
    san, deu = sorted(san), sorted(deu)
    random.shuffle(san); random.shuffle(deu)
    return san[:cap], deu[:cap]


def split(rows, frac=0.9):
    k = int(len(rows) * frac)
    return rows[:k], rows[k:]


def train_spm(lines, prefix, vocab):
    import sentencepiece as spm
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("\n".join(lines))
        tmp = f.name
    spm.SentencePieceTrainer.train(
        input=tmp, model_prefix=str(MODELS / prefix), vocab_size=vocab,
        model_type="unigram", character_coverage=1.0, normalization_rule_name="identity",
        minloglevel=2)
    p = spm.SentencePieceProcessor(); p.load(str(MODELS / f"{prefix}.model"))
    return p


def fetch_base(name):
    dest = MODELS / name
    if not dest.exists():
        urllib.request.urlretrieve(BASE_MODELS.format(name=name), dest)
    import sentencepiece as spm
    p = spm.SentencePieceProcessor(); p.load(str(dest))
    return p


def fert(model, s):
    return len(model.encode_as_pieces(s))


def main():
    ap = argparse.ArgumentParser(description="Train + evaluate a German-aware Sanskrit/German classifier from PWG.")
    ap.add_argument("--cap", type=int, default=80000, help="max examples per language")
    ap.add_argument("--vocab", type=int, default=4000)
    ap.add_argument("--seed", type=int, default=13)
    args = ap.parse_args()
    random.seed(args.seed)
    MODELS.mkdir(parents=True, exist_ok=True)

    try:
        import sentencepiece  # noqa: F401
    except ImportError:
        sys.exit("sentencepiece is not installed.\n  pip install sentencepiece")

    print("Extracting PWG self-labeled data ({#..#}=Sanskrit, {%..%}=German)...")
    san, deu = extract_labeled(args.cap)
    san_tr, san_te = split(san)
    deu_tr, deu_te = split(deu)
    print(f"  Sanskrit {len(san)} ({len(san_te)} test) | German {len(deu)} ({len(deu_te)} test)")

    print("Training SentencePiece models (san, deu)...")
    san_m = train_spm(san_tr, "san", args.vocab)
    deu_m = train_spm(deu_tr, "deu", args.vocab)
    print("Fetching detect-language baseline models (eng, skt)...")
    eng_m, skt_m = fetch_base("eng.model"), fetch_base("skt.model")

    # Evaluate on held-out test: baseline (eng vs skt) and German-aware (san vs deu).
    def evaluate(name, sa_model, de_model):
        # predict "sanskrit" if sanskrit-fertility <= german-fertility, else "german".
        san_ok = sum(1 for s in san_te if fert(sa_model, s) <= fert(de_model, s))
        deu_ok = sum(1 for g in deu_te if fert(de_model, g) < fert(sa_model, g))
        sr = san_ok / len(san_te); dr = deu_ok / len(deu_te)
        acc = (san_ok + deu_ok) / (len(san_te) + len(deu_te))
        print(f"  {name:18} sanskrit-recall {sr:.3f} | german-recall {dr:.3f} | accuracy {acc:.3f}")
        return {"sanskritRecall": round(sr, 4), "germanRecall": round(dr, 4), "accuracy": round(acc, 4)}

    print("Evaluating on held-out test set:")
    baseline = evaluate("baseline eng/skt", skt_m, eng_m)   # detect-language method
    german = evaluate("german-aware san/deu", san_m, deu_m)
    lift = round(german["accuracy"] - baseline["accuracy"], 4)
    print(f"  => accuracy lift from the German model: {lift:+.4f}")

    METRICS.parent.mkdir(parents=True, exist_ok=True)
    METRICS.write_text(json.dumps({
        "schemaVersion": "1.0.0",
        "generatedBy": "python scripts/train-langdetect-german.py",
        "method": "Per-language SentencePiece (unigram); classify by minimum fertility. Mirrors dharmamitra/detect-language, adding a German model trained on PWG {%...%}.",
        "trainingData": {"source": "csl-orig PWG {#..#}=Sanskrit, {%..%}=German (self-labeled)",
                         "sanskritExamples": len(san), "germanExamples": len(deu), "capPerLang": args.cap, "vocab": args.vocab, "seed": args.seed},
        "heldOutTest": {"sanskrit": len(san_te), "german": len(deu_te)},
        "baseline_eng_vs_skt": baseline,
        "germanAware_san_vs_deu": german,
        "accuracyLift": lift,
        "models": {"trained": ["san.model", "deu.model"], "dir": "scripts/.langdetect-models/ (gitignored)"},
        "nextStep": "Wire san.model + deu.model into import-dharmamitra-langdetect.py (replace eng/skt fertility), re-run build-langdetect-crosscheck.mjs, re-measure #95 precision.",
        "warnings": ["Trained on PWG's own markup — evaluates the markup's internal consistency, not an external gold standard.",
                     "SentencePiece models are gitignored (binary); regenerate with this script."]
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote metrics to {METRICS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
