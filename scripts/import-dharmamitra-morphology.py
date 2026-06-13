# Import a Dharmamitra ByT5-Sanskrit morphology snapshot for the gender cross-check.
#
# This is a model/networked refresh step by design, mirroring
# import-dharmamitra-chronology.mjs: it runs the Dharmamitra ByT5-Sanskrit
# analyzer over the headwords that already sit in the gender-conflict review
# queue, and writes a compact snapshot under src/data/external/. Normal atlas
# builds NEVER call the model; they consume this committed snapshot only.
#
# The deterministic join (model verdict vs. each dictionary's asserted gender)
# lives in scripts/build-gender-model-crosscheck.mjs, which is happy to run
# before this snapshot exists (every modelGender is simply null / pending).
#
# Two execution paths (see --source):
#   pypi  : `dharmamitra-sanskrit-grammar` PyPI package -> REMOTE dharmamitra.org
#           API. Easiest, but sends data off-box and is not reproducible (the
#           API can change). Fine for a one-off pilot.
#   local : the HuggingFace models from dharmamitra/byt5-sanskrit-analyzers
#           (chronbmm/sanskrit5-multitask), pinned by revision. Reproducible and
#           fully offline once the model is cached and sanskrit_tags.tsv is
#           vendored next to this script. Preferred for committed snapshots.
#
# The model is probabilistic. Its output is review EVIDENCE, never a silent
# input to the figure-building pipeline (per README "no LLM inference" rule).
#
# Usage:
#   python scripts/import-dharmamitra-morphology.py --source pypi --limit 50      # remote pilot
#   python scripts/import-dharmamitra-morphology.py --source local --revision <sha>  # reproducible
#   npm run import-dharmamitra-morphology -- --limit 50

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
CONFLICTS = ROOT / "src" / "data" / "review" / "gender-conflicts-review.json"
OUT = ROOT / "src" / "data" / "external" / "dharmamitra-morphology.json"

MODE = "unsandhied-lemma-morphosyntax"

# Local (reproducible) inference targets, from dharmamitra/byt5-sanskrit-analyzers
# (applications/segmentation-lemma-tagging). The multitask checkpoint does every
# task; "SLM " is its segmentation-lemma-morphosyntax task prefix. Output is a
# space-separated string of `unsandhied_lemma_shortTag` tokens; the short tag is
# a key into sanskrit_tags.tsv that expands to UD features (…|Gender=Masc|…).
HF_MODEL_ID = "chronbmm/sanskrit5-multitask"
HF_TASK_PREFIX = "SLM "
HF_MAX_LENGTH = 512
TAGS_TSV_NAME = "sanskrit_tags.tsv"  # vendored next to this script for offline runs
TAGS_TSV_URL = (
    "https://raw.githubusercontent.com/dharmamitra/byt5-sanskrit-analyzers/"
    "{rev}/applications/segmentation-lemma-tagging/data/sanskrit_tags.tsv"
)
GENDER_FROM_UD = {"Masc": "m", "Fem": "f", "Neut": "n"}
UD_GENDER_RE = re.compile(r"Gender=(Masc|Fem|Neut)")

# SLP1 -> IAST. The atlas stores normalized headwords in SLP1; the analyzer
# expects romanized (IAST) Sanskrit input. Longest-key-first is unnecessary
# here because SLP1 is one char per phoneme.
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


# Gender tokens the morphosyntax tagger may emit, mapped to the atlas {m,f,n}.
# Tolerant by design: scan the stringified analysis for any of these. Also
# matches the UD form (Masc/Fem/Neut) used by the local path's expanded tags.
GENDER_PATTERNS = [
    ("f", re.compile(r"\b(fem(?:inine)?|f\.)\b", re.I)),
    ("n", re.compile(r"\b(neut(?:er)?|n\.)\b", re.I)),
    ("m", re.compile(r"\b(masc(?:uline)?|m\.)\b", re.I)),
]


def extract_gender(analysis):
    """Best-effort gender from one analyzer result (used by the pypi path).

    The remote payload shape is not contractually fixed, so we stringify the
    whole result and look for an unambiguous gender token. If more than one
    distinct gender appears, return None rather than guess."""
    blob = json.dumps(analysis, ensure_ascii=False) if not isinstance(analysis, str) else analysis
    hits = {tag for tag, pat in GENDER_PATTERNS if pat.search(blob)}
    return next(iter(hits)) if len(hits) == 1 else None


def load_tag_map(revision, local_path):
    """Short-tag -> UD feature string, from the vendored copy or the pinned repo.

    Mirrors inf/tags.py:read_skt_tags (tab-separated, col0=short, col1=expansion).
    With the vendored scripts/sanskrit_tags.tsv present this never hits the
    network, so --source local runs fully offline."""
    text = None
    candidate = Path(local_path) if local_path else (Path(__file__).resolve().parent / TAGS_TSV_NAME)
    if candidate.exists():
        text = candidate.read_text(encoding="utf-8")
    else:
        import urllib.request
        url = TAGS_TSV_URL.format(rev=revision)
        print(f"  fetching tag map (no vendored {TAGS_TSV_NAME}): {url}")
        with urllib.request.urlopen(url) as resp:
            text = resp.read().decode("utf-8")
    tags = {}
    for line in text.splitlines():
        if "\t" in line:
            short, full = line.split("\t", 1)
            tags[short] = full.strip()
    return tags


def head_gender(expanded_tokens):
    """Gender of a headword from its expanded SLM tokens (list of UD strings).

    A simple headword yields one nominal token; a compound yields several. The
    LAST gendered token is the grammatical head, which carries the lemma's
    gender — so prefer it, but fall back to a unique gender if only one appears.
    Returns 'm'|'f'|'n'|None."""
    found = [GENDER_FROM_UD[m.group(1)] for tok in expanded_tokens for m in [UD_GENDER_RE.search(tok)] if m]
    if not found:
        return None
    if len(set(found)) == 1:
        return found[0]
    return found[-1]  # compound head


def load_lemmas(limit):
    doc = json.loads(CONFLICTS.read_text(encoding="utf-8"))
    seen, lemmas = set(), []
    for item in doc.get("items", []):
        lemma = (item.get("subject") or {}).get("lemma")
        if lemma and lemma not in seen:
            seen.add(lemma)
            lemmas.append(lemma)
    return lemmas[:limit] if limit else lemmas


def run_pypi(lemmas, args):
    """Remote path: the documented 3-line dharmamitra-sanskrit-grammar API."""
    try:
        from dharmamitra_sanskrit_grammar import DharmamitraSanskritProcessor
    except ImportError:
        sys.exit(
            "dharmamitra-sanskrit-grammar is not installed.\n"
            "  pip install dharmamitra-sanskrit-grammar\n"
            "Note: this routes to the remote dharmamitra.org API (data leaves "
            "this machine; not reproducible). Use --source local for committed runs."
        )
    processor = DharmamitraSanskritProcessor()
    out = {}
    for start in range(0, len(lemmas), args.batch_size):
        chunk = lemmas[start:start + args.batch_size]
        inputs = [slp1_to_iast(l) for l in chunk]
        results = processor.process_batch(inputs, mode=MODE, human_readable_tags=True)
        results = results if isinstance(results, list) else [results]
        for lemma, iast, res in zip(chunk, inputs, results):
            out[lemma] = {"input": iast, "gender": extract_gender(res), "raw": res}
        print(f"  analyzed {min(start + args.batch_size, len(lemmas))}/{len(lemmas)}")
    return out, {"endpoint": "remote dharmamitra.org API (not reproducible)"}


def run_local(lemmas, args):
    """Reproducible path: pinned local HuggingFace model.

    Replicates dharmamitra/byt5-sanskrit-analyzers run_inf.py for one mode:
    load chronbmm/sanskrit5-multitask, prefix each IAST headword with "SLM ",
    greedy-generate, then parse `unsandhied_lemma_shortTag` tokens, expand the
    short tag via the vendored sanskrit_tags.tsv, and read the head gender from
    UD features. Pin --revision to a commit hash for a committable run."""
    try:
        import torch
        from transformers import AutoTokenizer, T5ForConditionalGeneration
    except ImportError:
        sys.exit(
            "Local inference needs torch + transformers (and HF model access):\n"
            "  pip install torch transformers\n"
            "Or use --source pypi for the remote API."
        )

    tag_map = load_tag_map(args.revision, args.tags_tsv)
    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"  loading {HF_MODEL_ID}@{args.revision} on {device} ({len(tag_map)} tags)...")
    tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_ID, revision=args.revision)
    model = T5ForConditionalGeneration.from_pretrained(HF_MODEL_ID, revision=args.revision).to(device)
    model.eval()

    def expand(short_tag):
        return tag_map.get(short_tag, short_tag)

    out = {}
    for start in range(0, len(lemmas), args.batch_size):
        chunk = lemmas[start:start + args.batch_size]
        inputs = [slp1_to_iast(l) for l in chunk]
        enc = tokenizer([HF_TASK_PREFIX + s for s in inputs], return_tensors="pt",
                        padding=True, truncation=True, max_length=HF_MAX_LENGTH).to(device)
        with torch.no_grad():
            gen = model.generate(**enc, max_length=HF_MAX_LENGTH, num_beams=1)
        decoded = tokenizer.batch_decode(gen, skip_special_tokens=True)
        for lemma, iast, raw in zip(chunk, inputs, decoded):
            expanded = [expand(tok.split("_")[2]) for tok in raw.split() if len(tok.split("_")) == 3]
            out[lemma] = {"input": iast, "gender": head_gender(expanded), "raw": raw, "tags": expanded}
        print(f"  analyzed {min(start + args.batch_size, len(lemmas))}/{len(lemmas)}")
    return out, {"revision": args.revision, "device": device}


def main():
    ap = argparse.ArgumentParser(description="Snapshot Dharmamitra ByT5 morphology for gender cross-check.")
    ap.add_argument("--source", choices=["pypi", "local"], default="pypi")
    ap.add_argument("--limit", type=int, default=0, help="cap lemmas for a pilot (0 = all)")
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--revision", default="main",
                    help="HF model/tag-file revision for --source local; pin a commit hash for reproducibility")
    ap.add_argument("--tags-tsv", default=None,
                    help="override sanskrit_tags.tsv path (default: vendored next to script, else fetch)")
    ap.add_argument("--device", default=None, help="torch device for --source local (default: cuda if available)")
    args = ap.parse_args()

    lemmas = load_lemmas(args.limit)
    print(f"Analyzing {len(lemmas)} gender-conflict headwords via Dharmamitra ({args.source}, mode={MODE})...")
    by_lemma, extra_source = (run_local if args.source == "local" else run_pypi)(lemmas, args)

    resolved = sum(1 for v in by_lemma.values() if v["gender"])
    payload = {
        "schemaVersion": "1.0.0",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "generatedBy": f"python scripts/import-dharmamitra-morphology.py --source {args.source}",
        "source": {
            "name": "Dharmamitra ByT5-Sanskrit analyzer",
            "package": "dharmamitra-sanskrit-grammar (PyPI)" if args.source == "pypi" else "byt5-sanskrit-analyzers (local HF)",
            "models": ["buddhist-nlp/byt5-sanskrit", "chronbmm/sanskrit5-multitask"],
            "repository": "https://github.com/dharmamitra/byt5-sanskrit-analyzers",
            "paper": "arXiv:2409.13920 (Nehrdich, Hellwig & Keutzer, EMNLP Findings 2024)",
            "mode": MODE,
            "license": {
                "label": "MIT (wrapper); model cards on HuggingFace; DCS-trained",
                "note": "Predictions consumed as review evidence only — not redistributed as atlas data."
            },
            **extra_source,
        },
        "assumptions": [
            "Input headwords are SLP1 from the gender-conflict queue, transliterated to IAST for the model.",
            "Gender is read from the morphosyntax tags; multiple distinct genders in one analysis -> compound head (last gendered token), or null if none.",
            "The 'pypi' source calls the remote dharmamitra.org API and is not reproducible; pin a local model revision for committed snapshots.",
        ],
        "warnings": [
            "ByT5 gender is a probabilistic posterior, not ground truth; it breaks ties, it does not settle them.",
            "Do not auto-rewrite any dictionary's asserted gender from this snapshot.",
        ],
        "mode": MODE,
        "lemmaCount": len(by_lemma),
        "resolvedGenderCount": resolved,
        "byLemma": dict(sorted(by_lemma.items())),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(by_lemma)} morphology rows ({resolved} with a gender) to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
