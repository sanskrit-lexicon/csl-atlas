# Shared Dharmamitra ByT5 inference helpers.
#
# Factored out per docs/DHARMAMITRA_INTEGRATION.md so the per-task importers
# (lemma, segmentation, morphosyntax) stop duplicating the SLP1->IAST table and
# the local HF inference skeleton. import-dharmamitra-lemma.py is the first
# consumer; the gender (#89) and compound-depth (#91) importers should be
# refactored onto this module once those PRs land.
#
# Every importer:
#   1. builds rows = [(key, slp1_surface), ...]
#   2. calls run(rows, pypi_mode=..., local_prefix=..., args=...)
#   3. post-processes the returned raw decoded string per task
#      (extract a lemma, count segments, read gender tags, ...).
#
# The model is probabilistic: callers must treat its output as review evidence,
# never a silent build input.

import json
import sys

# ByT5 task prefixes (local HF path) from dharmamitra/byt5-sanskrit-analyzers
# inf/model.py, and the PyPI `mode` strings (remote path). Keep in sync.
LOCAL_PREFIX = {
    "lemma": "L ",
    "unsandhied": "S ",
    "lemma-morphosyntax": "LM ",
    "segmentation-morphosyntax": "SM ",
    "unsandhied-lemma-morphosyntax": "SLM ",
}
HF_MODEL_ID = "chronbmm/sanskrit5-multitask"
HF_MAX_LENGTH = 512

# SLP1 -> IAST (one char per phoneme). Single source of truth.
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


def add_common_args(ap):
    """Register the CLI flags every Dharmamitra importer shares."""
    ap.add_argument("--source", choices=["pypi", "local"], default="pypi")
    ap.add_argument("--limit", type=int, default=0, help="cap rows for a pilot (0 = all)")
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--revision", default="main",
                    help="HF model revision for --source local; pin a commit hash for reproducibility")
    ap.add_argument("--device", default=None, help="torch device for --source local")
    return ap


def _run_pypi(rows, pypi_mode, args):
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
        results = processor.process_batch(inputs, mode=pypi_mode, human_readable_tags=True)
        results = results if isinstance(results, list) else [results]
        for (key, _), iast, res in zip(chunk, inputs, results):
            raw = res if isinstance(res, str) else json.dumps(res, ensure_ascii=False)
            out[key] = {"input": iast, "raw": raw}
        print(f"  inferred {min(start + args.batch_size, len(rows))}/{len(rows)}")
    return out, {"endpoint": "remote dharmamitra.org API (not reproducible)"}


def _run_local(rows, local_prefix, args):
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
    print(f"  loading {HF_MODEL_ID}@{args.revision} on {device} (prefix {local_prefix!r})...")
    tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_ID, revision=args.revision)
    model = T5ForConditionalGeneration.from_pretrained(HF_MODEL_ID, revision=args.revision).to(device)
    model.eval()

    out = {}
    for start in range(0, len(rows), args.batch_size):
        chunk = rows[start:start + args.batch_size]
        inputs = [slp1_to_iast(s) for _, s in chunk]
        enc = tokenizer([local_prefix + s for s in inputs], return_tensors="pt",
                        padding=True, truncation=True, max_length=HF_MAX_LENGTH).to(device)
        with torch.no_grad():
            gen = model.generate(**enc, max_length=HF_MAX_LENGTH, num_beams=1)
        decoded = tokenizer.batch_decode(gen, skip_special_tokens=True)
        for (key, _), iast, raw in zip(chunk, inputs, decoded):
            out[key] = {"input": iast, "raw": raw}
        print(f"  inferred {min(start + args.batch_size, len(rows))}/{len(rows)}")
    return out, {"revision": args.revision, "device": device}


def run(rows, *, pypi_mode, local_prefix, args):
    """Run inference for rows=[(key, slp1_surface)]. Returns ({key: {input, raw}}, extra_source).

    Raw is the decoded model string; the caller post-processes it per task."""
    if local_prefix not in LOCAL_PREFIX.values():
        raise ValueError(f"unknown local_prefix {local_prefix!r}; known: {sorted(LOCAL_PREFIX.values())}")
    if args.source == "local":
        return _run_local(rows, local_prefix, args)
    return _run_pypi(rows, pypi_mode, args)
