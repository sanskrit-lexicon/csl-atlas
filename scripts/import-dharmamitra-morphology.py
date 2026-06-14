# Import a Dharmamitra ByT5-Sanskrit morphology snapshot for the gender cross-check.
#
# Model/networked refresh step: it runs the ByT5 analyzer over the headwords
# already in the gender-conflict review queue and writes a compact snapshot under
# src/data/external/. Normal atlas builds NEVER call the model.
#
# The deterministic join (model verdict vs. each dictionary's asserted gender)
# lives in scripts/build-gender-model-crosscheck.mjs, which runs before this
# snapshot exists (every modelGender simply null / pending).
#
# Generic inference (SLP1->IAST, pypi/local HF, CLI args) comes from
# scripts/lib/dharmamitra_infer.py. This file owns only the morphosyntax
# post-processing: read the gender from the model's tags. For --source local the
# raw output is `unsandhied_lemma_shortTag` tokens whose short tag expands via
# the vendored sanskrit_tags.tsv to UD features (…|Gender=Masc|…); for --source
# pypi the human-readable tags are scanned directly.
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
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import dharmamitra_infer as dm  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CONFLICTS = ROOT / "src" / "data" / "review" / "gender-conflicts-review.json"
OUT = ROOT / "src" / "data" / "external" / "dharmamitra-morphology.json"

MODE = "unsandhied-lemma-morphosyntax"
LOCAL_PREFIX = "SLM "  # segmentation-lemma-morphosyntax task prefix

TAGS_TSV_NAME = "sanskrit_tags.tsv"  # vendored next to this script for offline runs
TAGS_TSV_URL = (
    "https://raw.githubusercontent.com/dharmamitra/byt5-sanskrit-analyzers/"
    "{rev}/applications/segmentation-lemma-tagging/data/sanskrit_tags.tsv"
)
GENDER_FROM_UD = {"Masc": "m", "Fem": "f", "Neut": "n"}
UD_GENDER_RE = re.compile(r"Gender=(Masc|Fem|Neut)")

# Gender tokens the morphosyntax tagger may emit, mapped to the atlas {m,f,n}.
# Tolerant by design: scan the stringified analysis for any of these. Also
# matches the UD form (Masc/Fem/Neut) used by the local path's expanded tags.
GENDER_PATTERNS = [
    ("f", re.compile(r"\b(fem(?:inine)?|f\.)\b", re.I)),
    ("n", re.compile(r"\b(neut(?:er)?|n\.)\b", re.I)),
    ("m", re.compile(r"\b(masc(?:uline)?|m\.)\b", re.I)),
]


def extract_gender(raw):
    """Best-effort gender from one analyzer result (the pypi path).

    Scan the (already stringified) analysis for an unambiguous gender token; if
    more than one distinct gender appears, return None rather than guess."""
    hits = {tag for tag, pat in GENDER_PATTERNS if pat.search(raw or "")}
    return next(iter(hits)) if len(hits) == 1 else None


def load_tag_map(revision, local_path):
    """Short-tag -> UD feature string, from the vendored copy or the pinned repo.

    Mirrors inf/tags.py:read_skt_tags (tab-separated, col0=short, col1=expansion).
    With the vendored scripts/sanskrit_tags.tsv present this never hits the
    network, so --source local runs fully offline."""
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


def gender_from_local_raw(raw, tag_map):
    """Expand an SLM raw string's short tags and read the head gender."""
    expanded = [tag_map.get(tok.split("_")[2], tok.split("_")[2])
                for tok in raw.split() if len(tok.split("_")) == 3]
    return head_gender(expanded), expanded


def load_lemmas(limit):
    doc = json.loads(CONFLICTS.read_text(encoding="utf-8"))
    seen, lemmas = set(), []
    for item in doc.get("items", []):
        lemma = (item.get("subject") or {}).get("lemma")
        if lemma and lemma not in seen:
            seen.add(lemma)
            lemmas.append(lemma)
    return lemmas[:limit] if limit else lemmas


def main():
    ap = dm.add_common_args(argparse.ArgumentParser(
        description="Snapshot Dharmamitra ByT5 morphology for gender cross-check."))
    ap.add_argument("--tags-tsv", default=None,
                    help="override sanskrit_tags.tsv path (default: vendored next to script, else fetch)")
    args = ap.parse_args()

    lemmas = load_lemmas(args.limit)
    print(f"Analyzing {len(lemmas)} gender-conflict headwords via Dharmamitra ({args.source}, mode={MODE})...")
    raw_by_key, extra_source = dm.run([(l, l) for l in lemmas], pypi_mode=MODE, local_prefix=LOCAL_PREFIX, args=args)

    tag_map = load_tag_map(args.revision, args.tags_tsv) if args.source == "local" else None
    by_lemma = {}
    for lemma, rec in raw_by_key.items():
        if args.source == "local":
            gender, expanded = gender_from_local_raw(rec["raw"], tag_map)
            by_lemma[lemma] = {"input": rec["input"], "gender": gender, "raw": rec["raw"], "tags": expanded}
        else:
            by_lemma[lemma] = {"input": rec["input"], "gender": extract_gender(rec["raw"]), "raw": rec["raw"]}

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
