#!/usr/bin/env python3
"""Helpers for the PD Index of Works transcription (H6992, shards S1-S5).

Source: PD vol. 1 (Ghatage 1976), "Index of Works Used in the Dictionary",
printed pp. LXXXIX-CXXVII = DjVu leaves 98-136 (39 pages).

The committed table is vision-transcribed. The --draft mode is only a
column-OCR scaffold for the next shard: its Devanagari output must be
checked against the page image before any row reaches the committed TSV.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
import unicodedata
import urllib.request
from collections import Counter
from pathlib import Path

IA_ID = "mAAY_an-encyclopaedic-dictionary-of-sanskrit-vol-1-critically-edited-by-a-m-ghatage-1"
LEAF_FIRST, LEAF_LAST = 98, 136
FIELDS = [
    "page", "row", "title_deva", "title_iast", "author_deva", "author_iast",
    "nature_deva", "subject_code", "subject_class_no", "subject_label",
    "abbreviation_siglum", "abbreviation_qualifier", "confidence",
]
ROOT = Path(__file__).resolve().parents[1]
TSV = ROOT / "data" / "pd" / "pd_index_works.tsv"
DELTA = ROOT / "data" / "pd" / "pd_index_works_siglum_delta.tsv"


def roman(n: int) -> str:
    vals = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"),
            (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"),
            (5, "V"), (4, "IV"), (1, "I")]
    out = ""
    for value, sym in vals:
        while n >= value:
            out += sym
            n -= value
    return out


def printed_page(leaf: int) -> str:
    return roman(leaf - 9)


def image_url(leaf: int) -> str:
    return f"https://archive.org/download/{IA_ID}/page/n{leaf}.jpg"


def fetch(dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for leaf in range(LEAF_FIRST, LEAF_LAST + 1):
        target = dest / f"n{leaf}.jpg"
        if target.exists():
            continue
        with urllib.request.urlopen(image_url(leaf), timeout=120) as r, \
                open(target, "wb") as f:
            f.write(r.read())
        print(f"{leaf}\t{target.stat().st_size}", file=sys.stderr)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]", "", s)


def check() -> int:
    rows = list(csv.DictReader(open(TSV, encoding="utf-8"), delimiter="\t"))
    assert list(rows[0].keys()) == FIELDS, "schema drift"
    seen = set()
    for r in rows:
        key = (r["page"], r["row"])
        assert key not in seen, f"duplicate row {key}"
        seen.add(key)
    pages = sorted({r["page"] for r in rows})
    by_page = Counter(r["page"] for r in rows)
    blank = sum(1 for r in rows if not r["abbreviation_siglum"])
    delta = list(csv.DictReader(open(DELTA, encoding="utf-8"), delimiter="\t"))
    idx = [r for r in delta if r["status"] != "aob_only"]
    assert len(idx) == len(rows), "delta does not cover every Index row"
    print(json.dumps({
        "rows": len(rows),
        "pages": pages,
        "rows_by_page": dict(by_page),
        "blank_siglum": blank,
        "delta_status": dict(Counter(r["status"] for r in idx)),
        "delta_rows": len(delta),
    }, ensure_ascii=False, indent=1))
    return 0


def _ocr_words(path: Path, lang: str) -> list[dict]:
    base = path.with_suffix(path.suffix + "." + lang)
    subprocess.run(["tesseract", str(path), str(base), "-l", lang, "--psm", "6", "tsv"],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    words = []
    for r in csv.DictReader(open(str(base) + ".tsv", encoding="utf-8"), delimiter="\t"):
        if r["level"] == "5" and r["text"].strip():
            left, top = int(r["left"]), int(r["top"])
            words.append({"text": r["text"].strip(), "x": left,
                          "y": top + int(r["height"]) / 2})
    return words


def _lines(words: list[dict], tol: int = 12) -> list[dict]:
    lines: list[dict] = []
    for w in sorted(words, key=lambda w: (w["y"], w["x"])):
        for line in lines:
            if abs(line["y"] - w["y"]) <= tol:
                line["words"].append(w)
                line["y"] = sum(x["y"] for x in line["words"]) / len(line["words"])
                break
        else:
            lines.append({"y": w["y"], "words": [w]})
    for line in lines:
        line["words"].sort(key=lambda w: w["x"])
        line["text"] = " ".join(w["text"] for w in line["words"])
    return sorted(lines, key=lambda line: line["y"])


def draft(image: Path, out: Path) -> int:
    from PIL import Image

    im = Image.open(image)
    width, height = im.size
    left = image.with_name("_left.png")
    right = image.with_name("_right.png")
    im.crop((100, 520, 1180, height - 90)).save(left)
    im.crop((1160, 520, width, height - 90)).save(right)
    llines = _lines(_ocr_words(left, "san"))
    rlines = _lines(_ocr_words(right, "eng"))
    titles = [ln for ln in llines if any(w["x"] < 370 for w in ln["words"])]
    rights = []
    for ln in rlines:
        subj = [w for w in ln["words"] if w["x"] < 385]
        abbr = [w for w in ln["words"] if w["x"] >= 385]
        rights.append({"y": ln["y"], "subject": " ".join(w["text"] for w in subj),
                       "abbr": " ".join(w["text"] for w in abbr)})
    merged: list[dict] = []
    for r in rights:
        code = re.match(r"^\s*(\d+(?:[.,]\s*\d+)?)", r["subject"])
        if merged and not r["abbr"] and not code and r["subject"]:
            merged[-1]["subject"] = (merged[-1]["subject"] + " " + r["subject"]).strip()
        else:
            merged.append(dict(r))
    rows = []
    used: set[int] = set()
    for r in merged:
        best, dist = None, 1e9
        for i, t in enumerate(titles):
            if i in used:
                continue
            d = abs(t["y"] - r["y"])
            if d < dist:
                best, dist = i, d
        title = ""
        if best is not None and dist <= 32:
            used.add(best)
            title = " ".join(w["text"] for w in titles[best]["words"] if w["x"] < 370)
        rows.append({"y": r["y"], "title": title, "subject": r["subject"], "abbr": r["abbr"]})
    for i, t in enumerate(titles):
        if i not in used:
            rows.append({"y": t["y"], "title": t["text"], "subject": "", "abbr": ""})
    rows.sort(key=lambda r: r["y"])
    ys = [r["y"] for r in rows]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        for i, row in enumerate(rows, 1):
            lo = (ys[i - 2] + row["y"]) / 2 if i > 1 else row["y"] - 24
            hi = (row["y"] + ys[i]) / 2 if i < len(ys) else row["y"] + 24
            author, nature = [], []
            for ln in llines:
                if not lo < ln["y"] < hi:
                    continue
                aw = [x for x in ln["words"] if 370 <= x["x"] < 700]
                nw = [x for x in ln["words"] if x["x"] >= 700]
                if aw and ln["y"] > row["y"] - 6:
                    author.append(" ".join(x["text"] for x in aw))
                if nw:
                    nature.append(" ".join(x["text"] for x in nw))
            code = re.match(r"^\s*(\d+(?:[.,]\s*\d+)?)\s*(.*)", row["subject"])
            w.writerow({
                "page": printed_page(int(image.stem[1:])), "row": i,
                "title_deva": row["title"], "title_iast": "",
                "author_deva": " ".join(author), "author_iast": "",
                "nature_deva": " ".join(nature),
                "subject_code": code.group(1) if code else "",
                "subject_class_no": (code.group(1).split(".")[0].split(",")[0] if code else ""),
                "subject_label": code.group(2) if code else row["subject"],
                "abbreviation_siglum": row["abbr"], "abbreviation_qualifier": "",
                "confidence": "ocr-draft",
            })
    print(f"wrote {out} ({len(rows)} draft rows)", file=sys.stderr)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_fetch = sub.add_parser("fetch")
    p_fetch.add_argument("dest", type=Path)
    p_draft = sub.add_parser("draft")
    p_draft.add_argument("image", type=Path)
    p_draft.add_argument("out", type=Path)
    sub.add_parser("check")
    args = ap.parse_args()
    if args.cmd == "fetch":
        fetch(args.dest)
        return 0
    if args.cmd == "draft":
        return draft(args.image, args.out)
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
