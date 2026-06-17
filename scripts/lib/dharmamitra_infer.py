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
# Pinned commit of the HF model, for reproducible `--source local` runs
# (chronbmm/sanskrit5-multitask, 2024-05-09). The vendored sanskrit_tags.tsv means
# this pins ONLY the model weights; bump it deliberately, never to a moving `main`.
# import-dharmamitra-morphology.py keeps its own copy of this constant — keep them equal.
PINNED_REVISION = "c0d2ada54f3d19903149425aa888a203601423f8"
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
    ap.add_argument("--revision", default=PINNED_REVISION,
                    help=f"HF model revision for --source local (default: pinned {PINNED_REVISION[:12]}; pass another commit to override)")
    ap.add_argument("--device", default=None, help="torch device for --source local")
    return ap


API_URL = "https://dharmamitra.org/api/tagging/"


def _run_pypi(rows, pypi_mode, args):
    """Remote path: call the live dharmamitra.org tagging API directly.

    The PyPI `dharmamitra-sanskrit-grammar` package (v0.1.7) is stale — the API
    schema moved from a string `input_sentence` to a `texts` list, so the package
    now 422s. We post the current contract ourselves: {texts, mode,
    human_readable_tags} -> {"results": [...]} aligned to inputs. Not
    reproducible; pin a local model revision for committed snapshots."""
    try:
        import requests
    except ImportError:
        sys.exit("requests is not installed.\n  pip install requests")
    out = {}
    for start in range(0, len(rows), args.batch_size):
        chunk = rows[start:start + args.batch_size]
        inputs = [slp1_to_iast(s) for _, s in chunk]
        resp = requests.post(API_URL, json={
            "texts": inputs, "mode": pypi_mode, "human_readable_tags": True,
        }, timeout=180)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        for (key, _), iast, raw in zip(chunk, inputs, results):
            out[key] = {"input": iast, "raw": raw if isinstance(raw, str) else json.dumps(raw, ensure_ascii=False)}
        print(f"  inferred {min(start + args.batch_size, len(rows))}/{len(rows)}")
    return out, {"endpoint": API_URL, "note": "remote, not reproducible"}


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
