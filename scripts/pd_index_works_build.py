#!/usr/bin/env python3
"""Build the PD Index of Works table from hand-transcribed page fragments.

S1 (H6992, PR #591) committed page LXXXIX. This builder ingests the same
fragment shape for the remaining pages, so a later shard only has to supply
rows — never re-derive the schema, the IAST, the page inventory or the delta.

Fragment schema (TAB, header required), one row per printed Index row:
    page row title_deva author_deva nature_deva subject_code subject_label siglum qualifier

Usage:
    python scripts/pd_index_works_build.py rows/XC.tsv rows/XCI.tsv
    python scripts/pd_index_works_build.py --check

The fragments are *inputs* from vision transcription; this script never reads
_djvu.txt. It writes:
    data/pd/pd_index_works.tsv               (all transcribed pages, leaf order)
    data/pd/pd_index_works_by_page.tsv       (39-page inventory)
    data/pd/pd_index_works_siglum_delta.tsv  (Index vs AOB vs harvest)
    data/pd/pd_index_works_summary.json
"""

from __future__ import annotations

import csv
import json
import re
import sys
import unicodedata
from collections import Counter, OrderedDict
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PD = ROOT / "data" / "pd"
TSV = PD / "pd_index_works.tsv"
BY_PAGE = PD / "pd_index_works_by_page.tsv"
DELTA = PD / "pd_index_works_siglum_delta.tsv"
SUMMARY = PD / "pd_index_works_summary.json"
AOB = PD / "pd_aob_entries.tsv"
FAMILIES = PD / "pd_siglum_families.tsv"

FIELDS = [
    "page", "row", "title_deva", "title_iast", "author_deva", "author_iast",
    "nature_deva", "subject_code", "subject_class_no", "subject_label",
    "abbreviation_siglum", "abbreviation_qualifier", "confidence",
]
FRAG_FIELDS = ["page", "row", "title_deva", "author_deva", "nature_deva",
               "subject_code", "subject_label", "siglum", "qualifier"]
LEAF_FIRST, LEAF_LAST = 98, 136
DEV_DIGITS = re.compile(r"[०-९]")


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


PAGE_OF_LEAF = {leaf: roman(leaf - 9) for leaf in range(LEAF_FIRST, LEAF_LAST + 1)}
LEAF_OF_PAGE = {v: k for k, v in PAGE_OF_LEAF.items()}


def iast(deva: str) -> str:
    if not deva:
        return ""
    from indic_transliteration import sanscript
    text = DEV_DIGITS.sub("", deva).strip()
    return sanscript.transliterate(text, sanscript.DEVANAGARI, sanscript.IAST)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]", "", s)


def read_tsv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def existing_rows() -> list[dict]:
    if not TSV.exists():
        return []
    return read_tsv(TSV)


def frag_rows(paths: list[Path]) -> list[dict]:
    out = []
    for p in paths:
        rows = read_tsv(p)
        assert rows and list(rows[0].keys()) == FRAG_FIELDS, f"fragment schema drift: {p}"
        for r in rows:
            page = r["page"].strip()
            assert page in LEAF_OF_PAGE, f"{p}: unknown page {page!r}"
            code = r["subject_code"].strip()
            out.append({
                "page": page,
                "row": int(r["row"]),
                "title_deva": r["title_deva"].strip(),
                "title_iast": iast(r["title_deva"]),
                "author_deva": r["author_deva"].strip(),
                "author_iast": iast(r["author_deva"]),
                "nature_deva": r["nature_deva"].strip(),
                "subject_code": code,
                "subject_class_no": code.split(".")[0] if code else "",
                "subject_label": r["subject_label"].strip(),
                "abbreviation_siglum": r["siglum"].strip(),
                "abbreviation_qualifier": r["qualifier"].strip(),
                "confidence": "vision",
            })
    return out


def merge(rows: list[dict]) -> list[dict]:
    key = lambda r: (LEAF_OF_PAGE[r["page"]], int(r["row"]))
    seen = {}
    for r in rows:
        seen[key(r)] = r
    return [seen[k] for k in sorted(seen)]


def write_tsv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def by_page(rows: list[dict]) -> list[dict]:
    per = defaultdict_rows = {}
    for r in rows:
        per.setdefault(r["page"], []).append(r)
    out = []
    for leaf in range(LEAF_FIRST, LEAF_LAST + 1):
        page = PAGE_OF_LEAF[leaf]
        got = per.get(page, [])
        subcodes = sorted({r["subject_code"] for r in got if r["subject_code"]},
                          key=lambda c: (float(c.split(".")[0]), c))
        out.append({
            "printed_page": page,
            "leaf": leaf,
            "rows": len(got) if got else "",
            "blank_siglum": sum(1 for r in got if not r["abbreviation_siglum"]) if got else "",
            "subject_subcodes": "; ".join(subcodes),
            "status": "vision" if got else "pending",
        })
    return out


def near(target: str, pool: dict[str, str]) -> str:
    """Best OCR-variant candidate for a normalized siglum (not a membership test)."""
    best, score = "", 0.0
    head = target[:2]
    for normed, raw in pool.items():
        if normed[:2] != head or abs(len(normed) - len(target)) > 3:
            continue
        s = SequenceMatcher(None, target, normed).ratio()
        if s > score:
            best, score = raw, s
    return best if score >= 0.85 else ""


def delta(rows: list[dict]) -> list[dict]:
    aob = read_tsv(AOB)
    families = read_tsv(FAMILIES)
    aob_pool = {}
    for r in aob:
        for raw in (r["siglum"].strip(), (r.get("siglum_skeleton") or "").strip()):
            if raw:
                aob_pool.setdefault(norm(raw), raw)
    fam_pool = {norm(r["siglum"]): r["siglum"] for r in families if r["siglum"]}
    # AOB sigla are printed with OCR punctuation noise; strip it for membership.
    out, used_aob = [], set()
    for r in rows:
        sig = r["abbreviation_siglum"].strip()
        n = norm(sig)
        if not sig:
            out.append({"index_siglum": "", "normalized": "", "in_aob": "no",
                        "aob_match": "", "aob_near": "", "in_siglum_families": "no",
                        "families_match": "", "families_near": "",
                        "status": "index_blank", "note": "printed abbreviation cell blank"})
            continue
        in_aob = n in aob_pool
        in_fam = n in fam_pool
        if in_aob:
            used_aob.add(n)
        status = ("in_both" if in_aob and in_fam else
                  "in_aob_only" if in_aob else
                  "in_families_only" if in_fam else "index_only")
        out.append({
            "index_siglum": sig, "normalized": n,
            "in_aob": "yes" if in_aob else "no",
            "aob_match": aob_pool[n] if in_aob else "",
            "aob_near": "" if in_aob else near(n, aob_pool),
            "in_siglum_families": "yes" if in_fam else "no",
            "families_match": fam_pool[n] if in_fam else "",
            "families_near": "" if in_fam else near(n, fam_pool),
            "status": status, "note": "",
        })
    for n, raw in sorted(aob_pool.items()):
        if n in used_aob:
            continue
        out.append({"index_siglum": "", "normalized": n, "in_aob": "yes",
                    "aob_match": raw, "aob_near": "", "in_siglum_families": "",
                    "families_match": "", "families_near": "",
                    "status": "aob_only", "note": "AOB siglum not matched by this Index page set"})
    return out


def summary(rows: list[dict], pages: list[dict], delta_rows: list[dict]) -> dict:
    done = OrderedDict((p["printed_page"], p["rows"]) for p in pages if p["rows"] != "")
    blank = sum(1 for r in rows if not r["abbreviation_siglum"])
    subcodes = Counter(r["subject_code"] for r in rows if r["subject_code"])
    return {
        "handoff": "H6992 (S1 of 5) + residual",
        "source": {
            "title": "An Encyclopaedic Dictionary of Sanskrit on Historical Principles, vol. 1 (A. M. Ghatage, ed., Deccan College, Poona 1976)",
            "section": "Index of Works Used in the Dictionary",
            "printed_pages": "LXXXIX-CXXVII",
            "leaves": [LEAF_FIRST, LEAF_LAST],
            "leaf_count": 39,
            "archive_org_identifier": "mAAY_an-encyclopaedic-dictionary-of-sanskrit-vol-1-critically-edited-by-a-m-ghatage-1",
            "page_image_api": "https://archive.org/download/{id}/page/n{leaf}.jpg",
            "image_size": "2030x2753",
        },
        "schema": FIELDS,
        "pages_total": 39,
        "pages_laid_out": len(pages),
        "pages_transcribed": dict(done),
        "row_total_verified": len(rows),
        "row_total_full": None,
        "row_total_note": "No full-Index total is published until every one of the 39 pages is transcribed; the mission rejects extrapolating a total from a partial layout.",
        "blank_siglum": blank,
        "subject_subcodes": dict(sorted(subcodes.items(), key=lambda kv: (float(kv[0].split('.')[0]), kv[0]))),
        "method": "vision transcription of the archive.org page images; IAST via indic_transliteration; page fragments merged by scripts/pd_index_works_build.py; _djvu.txt used only as a structural skeleton and an OCR cross-check on the Latin columns",
        "subject_integer_classes": dict(sorted(Counter(
            r["subject_class_no"] for r in rows if r["subject_class_no"]).items(),
            key=lambda kv: int(kv[0]))),
        "siglum_reconciliation": {
            "index_rows": len(rows),
            "with_siglum": len(rows) - blank,
            "status": dict(Counter(r["status"] for r in delta_rows)),
            "delta_rows": len(delta_rows),
        },
        "confidence": (f"All {len(rows)} committed rows are vision-transcribed "
                       "(confidence=vision). No OCR-draft row is committed."),
        "backlog": {
            "pages": ", ".join(p["printed_page"] for p in pages if p["rows"] == "")
                     + f" ({sum(1 for p in pages if p['rows'] == '')} pages)",
            "scripts": "scripts/pd_index_works_build.py ingests one page fragment per page "
                       "(page row title_deva author_deva nature_deva subject_code subject_label "
                       "siglum qualifier) and regenerates this table, the page inventory, the "
                       "delta and this summary.",
        },
        "pages_manifest": [{"leaf": p["leaf"], "printed_page": p["printed_page"],
                            "status": p["status"]} for p in pages],
    }


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    frags = [Path(a) for a in argv if not a.startswith("--")]
    rows = merge(existing_rows() + frag_rows(frags)) if not check_only else merge(existing_rows())
    if not rows:
        print("no rows", file=sys.stderr)
        return 1
    pages = by_page(rows)
    if check_only:
        seen = set()
        for r in rows:
            k = (r["page"], r["row"])
            assert k not in seen, f"duplicate {k}"
            seen.add(k)
        print(json.dumps({"rows": len(rows),
                          "pages": [p["printed_page"] for p in pages if p["rows"] != ""],
                          "blank_siglum": sum(1 for r in rows if not r["abbreviation_siglum"])},
                         ensure_ascii=False))
        return 0
    write_tsv(TSV, rows, FIELDS)
    write_tsv(BY_PAGE, pages, ["printed_page", "leaf", "rows", "blank_siglum",
                               "subject_subcodes", "status"])
    delta_rows = delta(rows)
    write_tsv(DELTA, delta_rows, ["index_siglum", "normalized", "in_aob", "aob_match",
                                  "aob_near", "in_siglum_families", "families_match",
                                  "families_near", "status", "note"])
    SUMMARY.write_text(json.dumps(summary(rows, pages, delta_rows), ensure_ascii=False, indent=1) + "\n",
                       encoding="utf-8")
    done = [p for p in pages if p["rows"] != ""]
    print(json.dumps({"rows": len(rows), "pages_done": [p["printed_page"] for p in done],
                      "rows_by_page": {p["printed_page"]: p["rows"] for p in done},
                      "blank_siglum": sum(1 for r in rows if not r["abbreviation_siglum"])},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
