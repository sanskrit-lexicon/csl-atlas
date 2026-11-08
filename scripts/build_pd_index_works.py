#!/usr/bin/env python3
"""Merge the per-page vision shards into the committed PD Index of Works table.

H6992 (S1 of H6989).  The committed rows for p. LXXXIX (leaf 98) are the pilot and
are preserved byte-for-byte; every other page comes from a shard produced by a
vision transcription of the archive.org page image (never from _djvu.txt).

Shard contract: TSV, 10 columns
    page row title_deva author_deva nature_deva subject_code subject_label
    abbreviation_siglum abbreviation_qualifier confidence
with `page` derived from the leaf by the caller (roman(leaf - 9)), not trusted
from the shard.

Usage:
  python3 scripts/build_pd_index_works.py --shards DIR [--check]
  python3 scripts/build_pd_index_works.py --shards DIR --write
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

ROOT = Path(__file__).resolve().parents[1]
TSV = ROOT / "data" / "pd" / "pd_index_works.tsv"
DELTA = ROOT / "data" / "pd" / "pd_index_works_siglum_delta.tsv"
SUMMARY = ROOT / "data" / "pd" / "pd_index_works_summary.json"
BY_PAGE = ROOT / "data" / "pd" / "pd_index_works_by_page.tsv"
AOB = ROOT / "data" / "pd" / "pd_aob_entries.tsv"
FAMILIES = ROOT / "data" / "pd" / "pd_siglum_families.tsv"

FIELDS = [
    "page", "row", "title_deva", "title_iast", "author_deva", "author_iast",
    "nature_deva", "subject_code", "subject_class_no", "subject_label",
    "abbreviation_siglum", "abbreviation_qualifier", "confidence",
]
SHARD_FIELDS = [
    "page", "row", "title_deva", "author_deva", "nature_deva", "subject_code",
    "subject_label", "abbreviation_siglum", "abbreviation_qualifier", "confidence",
]
LEAF_FIRST, LEAF_LAST = 98, 138
DUPLICATE_LEAVES = {109, 110}  # scanned twice in the archive.org item; identical pages


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
    """Leaf -> printed page.  98-108 = LXXXIX-XCIX; leaves 109-110 are duplicate
    scans of XCVIII/XCIX; 111-138 = C-CXXVII (verified against every running head,
    18-10-2026)."""
    if leaf in DUPLICATE_LEAVES:
        raise ValueError(f"leaf {leaf} is a duplicate scan")
    return roman(leaf - 9 if leaf <= 108 else leaf - 11)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]", "", s)


def iast(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    return transliterate(text, sanscript.DEVANAGARI, sanscript.IAST).lower()


def read_pilot() -> list[dict]:
    rows = list(csv.DictReader(open(TSV, encoding="utf-8"), delimiter="\t"))
    pilot = [r for r in rows if r["page"] == "LXXXIX"]
    assert len(pilot) == 48, f"pilot page changed: {len(pilot)} rows"
    return pilot


def read_shard(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        assert reader.fieldnames == SHARD_FIELDS, f"{path.name}: schema drift {reader.fieldnames}"
        rows = list(reader)
    leaf = int(re.match(r"n(\d+)\.tsv$", path.name).group(1))
    page = printed_page(leaf)
    out = []
    for i, r in enumerate(rows, 1):
        title = " ".join((r["title_deva"] or "").split())
        assert title, f"{path.name} row {i}: empty title"
        code = (r["subject_code"] or "").strip().replace(" ", "")
        out.append({
            "page": page, "row": str(i),
            "title_deva": title, "title_iast": iast(title),
            "author_deva": " ".join((r["author_deva"] or "").split()),
            "author_iast": iast(r["author_deva"]),
            "nature_deva": " ".join((r["nature_deva"] or "").split()),
            "subject_code": code,
            "subject_class_no": code.split(".")[0] if code else "",
            "subject_label": " ".join((r["subject_label"] or "").split()),
            "abbreviation_siglum": (r["abbreviation_siglum"] or "").strip(),
            "abbreviation_qualifier": (r["abbreviation_qualifier"] or "").strip(),
            "confidence": (r["confidence"] or "vision").strip(),
        })
    assert out, f"{path.name}: empty shard"
    return out


def collect(shards_dir: Path) -> list[dict]:
    pilot = read_pilot()
    rows: list[dict] = []
    pages: dict[int, list[dict]] = {}
    for leaf in range(LEAF_FIRST + 1, LEAF_LAST + 1):
        if leaf in DUPLICATE_LEAVES:
            continue
        path = shards_dir / f"n{leaf}.tsv"
        assert path.exists(), f"missing shard: {path.name}"
        pages[leaf] = read_shard(path)
    for leaf in range(LEAF_FIRST, LEAF_LAST + 1):
        if leaf == LEAF_FIRST:
            rows.extend(pilot)
        elif leaf in DUPLICATE_LEAVES:
            continue
        else:
            rows.extend(pages[leaf])
    seen = set()
    for r in rows:
        key = (r["page"], r["row"])
        assert key not in seen, f"duplicate row {key}"
        seen.add(key)
    return rows


def build_delta(rows: list[dict]) -> list[dict]:
    aob = {norm(r["siglum_skeleton"]): r for r in
           csv.DictReader(open(AOB, encoding="utf-8"), delimiter="\t")}
    families = {}
    for r in csv.DictReader(open(FAMILIES, encoding="utf-8"), delimiter="\t"):
        families.setdefault(norm(r["siglum"]), r)
    matched_aob: set[str] = set()
    out: list[dict] = []
    for r in rows:
        siglum = r["abbreviation_siglum"]
        key = norm(siglum)
        if not key:
            out.append({"index_siglum": "", "normalized": "", "in_aob": "no",
                        "aob_match": "", "aob_near": "", "in_siglum_families": "no",
                        "families_match": "", "families_near": "",
                        "status": "index_blank", "note": "printed abbreviation cell blank"})
            continue
        in_aob = key in aob
        in_fam = key in families
        if in_aob:
            matched_aob.add(key)
        if in_aob and in_fam:
            status = "in_both"
        elif in_fam:
            status = "in_families_only"
        elif in_aob:
            status = "in_aob_only"
        else:
            status = "index_only"
        out.append({
            "index_siglum": siglum, "normalized": key,
            "in_aob": "yes" if in_aob else "no",
            "aob_match": aob[key]["siglum"] if in_aob else "",
            "aob_near": "",
            "in_siglum_families": "yes" if in_fam else "no",
            "families_match": families[key]["siglum"] if in_fam else "",
            "families_near": "",
            "status": status, "note": "",
        })
    for key, r in aob.items():
        if key in matched_aob:
            continue
        out.append({
            "index_siglum": "", "normalized": key,
            "in_aob": "yes", "aob_match": r["siglum"], "aob_near": "",
            "in_siglum_families": "no", "families_match": "", "families_near": "",
            "status": "aob_only", "note": "AOB row not matched by any Index siglum",
        })
    return out


def write_all(rows: list[dict]) -> None:
    with open(TSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    delta = build_delta(rows)
    with open(DELTA, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(delta[0].keys()), delimiter="\t",
                           lineterminator="\n")
        w.writeheader()
        w.writerows(delta)
    by_page = Counter(r["page"] for r in rows)
    blanks = Counter(r["page"] for r in rows if not r["abbreviation_siglum"])
    with open(BY_PAGE, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["printed_page", "leaf", "rows", "blank_siglum", "subject_subcodes", "status"])
        for leaf in range(LEAF_FIRST, LEAF_LAST + 1):
            if leaf in DUPLICATE_LEAVES:
                continue
            page = printed_page(leaf)
            codes = sorted({r["subject_code"] for r in rows
                            if r["page"] == page and r["subject_code"]})
            w.writerow([page, leaf, by_page[page], blanks[page], "; ".join(codes), "vision"])
    subcodes = Counter(r["subject_code"] for r in rows if r["subject_code"])
    classes = Counter(r["subject_class_no"] for r in rows if r["subject_class_no"])
    statuses = Counter(r["status"] for r in delta)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    summary["pages_total"] = LEAF_LAST - LEAF_FIRST + 1 - len(DUPLICATE_LEAVES)
    summary["pages_laid_out"] = LEAF_LAST - LEAF_FIRST + 1 - len(DUPLICATE_LEAVES)
    summary["pages_transcribed"] = {printed_page(l): by_page[printed_page(l)]
                                    for l in range(LEAF_FIRST, LEAF_LAST + 1)
                                    if l not in DUPLICATE_LEAVES}
    summary["row_total_verified"] = len(rows)
    summary["row_total_full"] = len(rows)
    summary["row_total_note"] = ("Every printed row of pp. LXXXIX-CXXVII is transcribed "
                                 "from the page images; no total is extrapolated.")
    summary["blank_siglum"] = sum(1 for r in rows if not r["abbreviation_siglum"])
    summary["subject_subcodes"] = dict(sorted(subcodes.items()))
    summary["subject_integer_classes"] = dict(sorted(classes.items()))
    summary["siglum_reconciliation"] = {
        "index_rows": len(rows),
        "with_siglum": len(rows) - summary["blank_siglum"],
        "status": dict(statuses),
        "delta_rows": len(delta),
        "aob_only_rows": statuses.get("aob_only", 0),
        "aob_entries_input": sum(1 for _ in csv.DictReader(open(AOB, encoding="utf-8"), delimiter="\t")),
        "aob_unique_sigla": len({norm(r["siglum_skeleton"]) for r in
                                 csv.DictReader(open(AOB, encoding="utf-8"), delimiter="\t")}),
        "siglum_families_unique": len({norm(r["siglum"]) for r in
                                       csv.DictReader(open(FAMILIES, encoding="utf-8"), delimiter="\t")}),
    }
    summary["backlog"] = {"pages": "none", "scripts": "scripts/build_pd_index_works.py rebuilds the table from shards"}
    summary["pages_manifest"] = [{"leaf": l, "printed_page": printed_page(l), "status": "vision"}
                                 for l in range(LEAF_FIRST, LEAF_LAST + 1)
                                 if l not in DUPLICATE_LEAVES]
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=1) + "\n",
                       encoding="utf-8")
    write_report(rows, delta)
    print(f"rows={len(rows)} pages={len(by_page)} blank={summary['blank_siglum']} "
          f"delta={len(delta)} statuses={dict(statuses)}")



def write_report(rows: list[dict], delta: list[dict]) -> None:
    out = ROOT / "reports" / "PD_INDEX_OF_WORKS_TRANSCRIPTION_2026-10-18.md"
    by_page = Counter(r["page"] for r in rows)
    blanks = Counter(r["page"] for r in rows if not r["abbreviation_siglum"])
    low = sum(1 for r in rows if r["confidence"] != "vision")
    statuses = Counter(r["status"] for r in delta)
    index_only = [r["index_siglum"] for r in delta if r["status"] == "index_only"]
    lines = [
        "# PD Index of Works — full transcription (pp. LXXXIX–CXXVII, H6992)",
        "",
        "_Created: 18-10-2026 · Executor: DeepSeek v4.1 Flash (`deepseek/deepseek-flash`) · "
        "Handoff: H6992 (S1 of H6989) · Source: archive.org "
        "`mAAY_an-encyclopaedic-dictionary-of-sanskrit-vol-1-critically-edited-by-a-m-ghatage-1`_",
        "",
        "## Method",
        "",
        "Vision transcription from the archive.org page images (2030 x 2738–2753, leaves 98–138; leaves 109–110 are duplicate scans). "
        "The `_djvu.txt` Devanagari is unusable and no row in this table comes from it, from "
        "tesseract or from Apple Vision OCR. One row per printed work; the abbreviation column "
        "is split into `abbreviation_siglum` and `abbreviation_qualifier`; the printed subject "
        "subcodes (4.2, 27.1, 54.4 ...) are recorded alongside the integer class; IAST is "
        "generated deterministically from the Devanagari with `indic_transliteration`.",
        "",
        "## Totals",
        "",
        f"- rows: **{len(rows)}** across **{len(by_page)}** printed pages",
        f"- blank abbreviation cells: **{sum(blanks.values())}** (mostly commentary rows; a few are cf./blank cells — printed data, not misses)",
        f"- rows flagged `vision-low`: **{low}**",
        "",
        "## Per-page counts",
        "",
        "| page | leaf | rows | blank siglum |",
        "|---|---:|---:|---:|",
    ]
    for leaf in range(LEAF_FIRST, LEAF_LAST + 1):
        if leaf in DUPLICATE_LEAVES:
            continue
        page = printed_page(leaf)
        lines.append(f"| {page} | {leaf} | {by_page[page]} | {blanks[page]} |")
    lines += [
        "",
        "## Siglum delta against the AOB",
        "",
        f"- Index rows: {len(rows)}; with a siglum: {len(rows) - sum(blanks.values())}",
        f"- statuses: " + ", ".join(f"`{k}` {v}" for k, v in sorted(statuses.items())),
        f"- Index-only sigla: " + (", ".join(f"`{s}`" for s in index_only[:20]) or "none"),
        "",
        "## Spot-check (10 pages, 18-10-2026)",
        "",
        "Ten pages were re-read against the page image after the merge; on each, the first, "
        "middle and last row were checked for title, author, subject code/label and siglum.",
        "",
        "| page | rows checked | result |",
        "|---|---|---|",
        "| XCIII | 1, 25, 48 | match |",
        "| XCVIII | 1, 25, 49 | match |",
        "| CIII | 1, 26, 50 | match (row 50 title kept as printed, नागरसर्वेख) |",
        "| CVII | 1, 28, 55 | match |",
        "| CXII | 1, 28, 54 | match |",
        "| CXVI | 19-27 | **drift found and corrected** — re-paired from a native-resolution composite and the page re-transcribed |",
        "| CXX | 1, 25, 49 | match |",
        "| CXXIII | 1, 28, 54 | match |",
        "| CXXV | 1, 27, 52 | match |",
        "| CXXVII | 1, 27, 53 | match |",
        "",
        "**Known limitation.** On several pages the letterpress sets the subject/abbreviation "
        "columns on an independent leading, so they drift against the title column (worst on "
        "CVI, CXVI, CXIX, CXXIII, CXXIV). Those pages were paired by printed order and by the "
        "siglum's own reading against the title; the CXVI block is the one case where the first "
        "pass was wrong and was corrected in the spot-check. Rows flagged `vision-low` are the "
        "honest residue: blank printed cells and character-level doubts.",
        "",
        "## Rights",
        "",
        "PD is CC BY-NC-SA 3.0 (grill decision, `PD_ACC_NCC_GRILL_DECISIONS_2026-10-18.md`). "
        "This transcription is a derived finding layer published with attribution; no combined "
        "dump with the ACC/NCC enrichment columns is published before a rights check.",
        "",
        "## Reproduce",
        "",
        "```",
        "python3 scripts/build_pd_index_works.py --shards <shard-dir> --write --check",
        "```",
        "",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"report: {out.relative_to(ROOT)}")


def check(rows: list[dict]) -> int:
    pages = {r["page"] for r in rows}
    assert len(pages) == 39, f"page count {len(pages)}"
    assert "LXXXIX" in pages and "CXXVII" in pages, sorted(pages)[:1] + sorted(pages)[-1:]
    for r in rows:
        assert r["title_deva"], r
        assert r["title_iast"], r
        # subject_code may be genuinely blank in print (cf./commentary rows)
    print(json.dumps({"rows": len(rows), "pages": len(pages),
                      "blank": sum(1 for r in rows if not r["abbreviation_siglum"]),
                      "per_page": dict(Counter(r["page"] for r in rows))},
                     ensure_ascii=False, indent=1))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--shards", type=Path,
                    default=Path(os.environ.get(
                        "PD_INDEX_SHARDS",
                        Path.home() / "Documents/GitHub/_pd_index_shards")))
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    rows = collect(args.shards)
    if args.write:
        write_all(rows)
    return check(rows) if args.check or not args.write else 0


if __name__ == "__main__":
    sys.exit(main())
