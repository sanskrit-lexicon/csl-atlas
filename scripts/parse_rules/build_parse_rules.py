#!/usr/bin/env python3
"""Build MUDIDI Pass-1-shaped parse-rules JSON per CDSL dictionary.

A deterministic by-product of csl-orig source markup. For each dictionary it emits
the three components MUDIDI infers per dictionary in its Stage-2 "Pass 1":

  1. field_inventory  - observed CDSL tags -> MDF fields (the MDF field map)
  2. abbreviations    - distinct <ab> and <ls> sigla keys (the abbreviation key)
  3. entry_structure  - record / headword / homonym / sense / continuation markers

Inputs : ../csl-orig/v02/<src>/<src>.txt              (source of truth)
         data/lexico/microstructure_fingerprint.json  (optional enrichment)
Outputs: data/parse-rules/<dict>.json, index.json, _validation.json

No LLM inference. Counts are `observed`; the MDF column is `derived` from the
csl-standards MDF_EXPORT_MAPPING.md table. Run: python scripts/parse_rules/build_parse_rules.py
"""
import sys
import json
import re
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[2]
CSL_ORIG = REPO.parent / "csl-orig" / "v02"
OUT = REPO / "data" / "parse-rules"

# dict code -> (csl-orig source code, title, target language)
DICTS = [
    ("mw",   "mw",   "Monier-Williams Sanskrit-English (1899)", "English"),
    ("pwg",  "pwg",  "Petersburg Woerterbuch, grosse Fassung (1855-75)", "German"),
    ("pwk",  "pw",   "Petersburg Woerterbuch, kuerzere Fassung (1879-89)", "German"),
    ("ap",   "ap",   "Apte Practical Sanskrit-English (1957)", "English"),
    ("wil",  "wil",  "Wilson Sanskrit-English (1832)", "English"),
    ("ben",  "ben",  "Benfey Sanskrit-English (1866)", "English"),
    ("cae",  "cae",  "Cappeller Sanskrit-English (1891)", "English"),
    ("skd",  "skd",  "Sabdakalpadruma (1822-58)", "Sanskrit"),
    ("vcp",  "vcp",  "Vacaspatya (1873-84)", "Sanskrit"),
    ("armh", "armh", "Halayudha Abhidhanaratnamala", "Sanskrit"),
    ("abch", "abch", "Hemacandra Abhidhanacintamani", "Sanskrit"),
]

# CDSL tag -> (MDF field, adequacy, role). Mirrors csl-standards/docs/MDF_EXPORT_MAPPING.md.
MDF_MAP = {
    "k1":   ("\\lx",  "clean",   "headword"),
    "k2":   ("\\lc",  "partial", "segmented/sort key"),
    "h":    ("\\hm",  "clean",   "homonym number"),
    "hom":  ("\\hm",  "clean",   "homonym display"),
    "lex":  ("\\ps",  "clean",   "grammar/gender"),
    "div":  ("\\sn",  "clean",   "sense division"),
    "ls":   ("\\bb",  "lossy",   "literary source / L. hedge"),
    "ab":   ("\\cf",  "partial", "abbreviation (q.v. -> cross-ref)"),
    "etym": ("\\et",  "partial", "etymology"),
    "lang": ("\\es",  "partial", "source language"),
    "gk":   ("\\et",  "partial", "Greek inline (etymology)"),
    "bio":  ("\\nt",  "review",  "biographical/bibliographic"),
    "s":    (None,    "partial", "inline Sanskrit (context-dependent)"),
    "s1":   (None,    "partial", "inline Sanskrit (proper/variant)"),
    "e":    (None,    "n/a",     "entry-structure code (structural)"),
    "info": (None,    "n/a",     "machine annotation (infrastructure)"),
    "pc":   (None,    "n/a",     "page-column coordinate (archival)"),
    "pcol": (None,    "n/a",     "page-column coordinate (archival)"),
    "pb":   (None,    "n/a",     "page break (archival)"),
    "i":    (None,    "n/a",     "italic (typography, stripped by MDF)"),
    "b":    (None,    "n/a",     "bold (typography, stripped by MDF)"),
}

TOPK = 40
TAG_RE = re.compile(r"<([a-zA-Z][a-zA-Z0-9]*)\b[^>]*>")  # opening tags only


def load_fingerprint():
    fp = REPO / "data" / "lexico" / "microstructure_fingerprint.json"
    try:
        return json.load(open(fp, encoding="utf-8")).get("dicts", {})
    except Exception:
        return {}


def top_contents(text, pat):
    c = Counter(m.strip() for m in re.findall(pat, text, re.S) if m.strip())
    return [{"value": v, "count": n} for v, n in c.most_common(TOPK)], len(c)


def build(dictcode, src, title, target, fingerprint):
    path = CSL_ORIG / src / f"{src}.txt"
    if not path.exists():
        return None, f"missing source {path}"
    text = path.read_text(encoding="utf-8", errors="replace")

    tags = Counter(TAG_RE.findall(text))
    records = text.count("<L>")

    field_inventory, unmapped = [], []
    for tag, count in sorted(tags.items(), key=lambda kv: (-kv[1], kv[0])):
        if tag.upper() in ("L", "LEND"):
            continue
        if tag in MDF_MAP:
            mdf, adq, role = MDF_MAP[tag]
            field_inventory.append(
                {"tag": tag, "count": count, "mdf": mdf, "adequacy": adq, "role": role}
            )
        else:
            unmapped.append({"tag": tag, "count": count})

    ab_top, ab_n = top_contents(text, r"<ab>(.*?)</ab>")
    ls_top, ls_n = top_contents(text, r"<ls>(.*?)</ls>")

    e_codes = re.findall(r"<e>\s*([0-9]+[A-Za-z]*)", text)
    continuation = sum(1 for c in e_codes if re.search(r"[A-Za-z]$", c))

    fp = fingerprint.get(src) or fingerprint.get(dictcode) or {}
    entry_structure = {
        "record_open": "<L>",
        "record_close": "<LEND>",
        "field_separator": "¦",
        "headword_marker": "k1" if tags.get("k1") else None,
        "homonym_marker": "h" if tags.get("h") else None,
        "sense_division_marker": "div" if tags.get("div") else None,
        "entry_code_marker": "e" if tags.get("e") else None,
        "continuation_entries": continuation,
        "dominant_microstructure_layer": fp.get("dominant_layer") or None,
        "microstructure_layers_present": fp.get("layers_present", []),
    }

    western = sum(tags.get(t, 0) for t in ("ab", "ls", "div", "lex"))
    caveats = []
    if western == 0:
        caveats.append(
            "Western-markup field inventory is ~empty by construction: this dictionary "
            "encodes citations / verbs / senses in indigenous prose (iti+authority, "
            "quotes, dhatuh / preraNe / conjugation-class names), not European tags. A "
            "zero here is detector blindness, NOT absence of content. See "
            "docs/MICROSTRUCTURE_ZERO_MEANING.md."
        )

    obj = {
        "schema": "mudidi-parse-rules/0.1",
        "dict": dictcode,
        "title": title,
        "source_file": f"csl-orig/v02/{src}/{src}.txt",
        "target_language": target,
        "record_count": records,
        "field_inventory": field_inventory,
        "unmapped_tags": unmapped,
        "abbreviations": {
            "ab_distinct": ab_n,
            "ab_top": ab_top,
            "ls_siglum_distinct": ls_n,
            "ls_siglum_top": ls_top,
            "expansions": "not linked; see MWS/mwabbreviations/abbr.html and per-dict intro pages",
        },
        "entry_structure": entry_structure,
        "caveats": caveats,
        "evidence": {
            "field_inventory.count": "observed",
            "field_inventory.mdf": "derived (csl-standards MDF_EXPORT_MAPPING.md)",
            "abbreviations": "observed",
            "dominant_microstructure_layer": "derived",
        },
        "generated_by": "scripts/parse_rules/build_parse_rules.py",
    }
    return obj, None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fingerprint = load_fingerprint()
    index, validation = [], []
    print(f"{'dict':6} {'records':>9} {'fields':>6} {'ls_sig':>7} {'ab':>5} {'cont':>6}  caveat")
    for dictcode, src, title, target in DICTS:
        obj, err = build(dictcode, src, title, target, fingerprint)
        if err:
            validation.append({"dict": dictcode, "status": "skipped", "reason": err})
            print(f"{dictcode:6} SKIPPED: {err}", file=sys.stderr)
            continue
        (OUT / f"{dictcode}.json").write_text(
            json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        ls_n = obj["abbreviations"]["ls_siglum_distinct"]
        ab_n = obj["abbreviations"]["ab_distinct"]
        cont = obj["entry_structure"]["continuation_entries"]
        nf = len(obj["field_inventory"])
        has_cav = "yes" if obj["caveats"] else ""
        print(f"{dictcode:6} {obj['record_count']:>9} {nf:>6} {ls_n:>7} {ab_n:>5} {cont:>6}  {has_cav}")
        index.append({
            "dict": dictcode, "title": title, "record_count": obj["record_count"],
            "field_count": nf, "ls_siglum_distinct": ls_n, "ab_distinct": ab_n,
            "continuation_entries": cont,
            "dominant_microstructure_layer": obj["entry_structure"]["dominant_microstructure_layer"],
            "has_caveats": bool(obj["caveats"]),
        })
        ok = obj["record_count"] > 0 and (nf > 0 or bool(obj["caveats"]))
        validation.append({"dict": dictcode, "status": "ok" if ok else "warn",
                           "record_count": obj["record_count"], "field_count": nf})

    (OUT / "index.json").write_text(
        json.dumps({"schema": "mudidi-parse-rules/0.1", "dicts": index},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "_validation.json").write_text(
        json.dumps({"results": validation}, ensure_ascii=False, indent=2), encoding="utf-8")

    # smoke test: MW must parse sanely, or the run is broken
    mw = next((v for v in validation if v["dict"] == "mw"), None)
    if not mw or mw.get("status") != "ok" or mw.get("record_count", 0) < 100000:
        print("VALIDATION FAILED: MW smoke test did not pass", file=sys.stderr)
        sys.exit(1)
    warns = [v for v in validation if v["status"] != "ok"]
    print(f"\nWrote {len(index)} dicts to {OUT.relative_to(REPO)} "
          f"({len(warns)} warn/skip).")


if __name__ == "__main__":
    main()
