#!/usr/bin/env python3
"""H7109 — PD vs PWG vs OED page economics.

Measures what one printed page of a dictionary contains, and what one entry
costs in pages, in three dictionaries:

* **PD** — the Deccan College *Encyclopaedic Dictionary of Sanskrit on
  Historical Principles*, from the read-only Cologne PDScan 2020 machine text.
* **PWG** — Böhtlingk & Roth's *Sanskrit-Wörterbuch*, from the read-only
  ``csl-orig/v02/pwg/pwg.txt`` machine text.
* **OED** — the Oxford English Dictionary, 1933 corrected re-issue of the 1928
  first edition, volume IV (F-G), measured on **page images** of one scan.

    python scripts/pd_page_economics.py --pd /path/to/pd.txt
    python scripts/pd_page_economics.py --check --pd /path/to/pd.txt

The two machine texts are measured from their own markup; the OED numbers are
read from ``data/pd/oed_page_sample.json``, which records hand measurements
taken on the page images (page IDs, column counts, printed lines counted by
row projection, entries counted visually, characters from the page's own OCR
text layer).  **The three sources are never mixed inside one average**: every
row of the TSV names its own source, and no PD or PWG number is derived from
an OED number or vice versa.

Units, which are the whole difficulty of this comparison:

* **PD** encodes a printed line break as ``<div n="lb">`` (440,003 of them),
  and the line that opens an entry carries no such tag.  Printed lines are
  therefore ``lb`` divisions plus entry-opening lines (547,633), which is what
  the machine text's own header claims (``547634Lines``).  The handoff's
  "line-divisions" figure is the bare ``lb`` count.
* **PWG** encodes **no** printed line break at all: its file lines are wrapped
  at source level (median 115 characters, max 15,234), so they are *machine
  lines*, not printed lines.  PWG printed lines are not recoverable from the
  text and are not reported as if they were.
* **OED** printed lines come from the page images.

Page and column basis: PD and PWG both number a **column**, not a page.
PD's ``<pc>`` is ``volume-page`` plus a column letter ``a``/``b`` (two columns
to the page, ``[Page1-0001a+ 54]`` page markers show 64 lines per column).
PWG's ``<pc>`` is a page-col reference whose two columns are the odd (left) and
even (right) numbers of one page, as ``pwg-meta2.txt`` states.  A PD or PWG
"page" in this report is therefore a **printed page reconstructed from the
column reference**, and the reconstruction is stated in the row's ``basis``.

Stdlib only; no network.  Exit 3 when a machine text is missing, exit 2 when
``--check`` finds a difference or a canary fails.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_TSV = os.path.join(ROOT, "data", "pd", "page_economics.tsv")
OED_JSON = os.path.join(ROOT, "data", "pd", "oed_page_sample.json")
PINS_TSV = os.path.join(ROOT, "tests", "forensic", "h7109_page_economics_pins.tsv")
REPORT = os.path.join(ROOT, "reports", "PD_PAGE_ECONOMICS_2026.md")

RE_HDR = re.compile(r"^<L>([\d.]+)<pc>([^<]*)<k1>")
RE_PD_COL = re.compile(r"^(\d+)-(\d+)([ab])$")
RE_PWG_COL = re.compile(r"^(\d+)-(\d+)$")
RE_PD_PAGEMARK = re.compile(r"^\[Page([0-9]+-[0-9]+[ab]?)\+\s*([0-9]+)\]$")
RE_LB = '<div n="lb">'

DEFAULT_PD = os.environ.get("PD_TXT", "")
DEFAULT_PWG = os.environ.get(
    "PWG_TXT", os.path.join(ROOT, os.pardir, "csl-orig", "v02", "pwg", "pwg.txt"))

TSV_COLUMNS = [
    "dictionary", "edition", "pages", "entries", "lines", "characters",
    "entries_per_page", "lines_per_page", "chars_per_page", "columns",
    "page_size", "source", "basis", "note",
]


def fmt(value: float) -> str:
    return f"{value:.2f}"


def measure_text(path: str, kind: str) -> dict:
    """Measure one Cologne-style dictionary machine text.

    ``kind`` is ``"pd"`` or ``"pwg"`` and selects the page/column grammar.
    """
    entries = 0
    column_codes: set[str] = set()
    page_numbers: set[str] = set()
    vol_max_col: dict[str, int] = {}
    lb_divs = 0
    text_lines = 0
    chars = 0
    entries_per_column: dict[str, int] = {}
    column_lines_marker: list[int] = []
    unmatched = 0
    cur: str | None = None
    body: list[str] = []

    col_re = RE_PD_COL if kind == "pd" else RE_PWG_COL
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            s = line.rstrip("\n")
            if s.startswith("<L>"):
                entries += 1
                m = RE_HDR.match(s)
                if not m:
                    unmatched += 1
                    cur = None
                    body = []
                    continue
                code = m.group(2)
                cur = code
                column_codes.add(code)
                entries_per_column[code] = entries_per_column.get(code, 0) + 1
                cm = col_re.match(code)
                if cm:
                    vol, num = cm.group(1), int(cm.group(2))
                    if kind == "pd":
                        page_numbers.add(f"{vol}-{num}")
                    else:
                        page_numbers.add(f"{vol}-{(num + 1) // 2}")
                    vol_max_col[vol] = max(vol_max_col.get(vol, 0), num)
                body = []
            elif s.startswith("<LEND>"):
                if cur is not None:
                    joined = "\n".join(body)
                    lb_divs += joined.count(RE_LB)
                    flat = " ".join(body).replace(RE_LB, " ")
                    chars += len(flat)
                cur = None
                body = []
            else:
                mk = RE_PD_PAGEMARK.match(s)
                if mk:
                    column_lines_marker.append(int(mk.group(2)))
                if cur is not None:
                    # The H6947/H6949 body definition keeps every line between
                    # <L> and <LEND>, page markers and blank lines included; the
                    # characters are counted after joining and dropping the lb
                    # tags.  Keeping it identical is what makes the two reports
                    # reconcile to the same totals.
                    text_lines += 1
                    body.append(s)

    per_col = sorted(entries_per_column.values())
    per_page_counts: dict[str, int] = {}
    for code, n in entries_per_column.items():
        cm = col_re.match(code)
        if not cm:
            continue
        vol, num = cm.group(1), int(cm.group(2))
        page = f"{vol}-{num}" if kind == "pd" else f"{vol}-{(num + 1) // 2}"
        per_page_counts[page] = per_page_counts.get(page, 0) + n
    per_page = sorted(per_page_counts.values())

    if kind == "pwg":
        printed_pages = sum((mx + 1) // 2 for mx in vol_max_col.values())
        max_page = printed_pages
    else:
        printed_pages = len(page_numbers)
        # PD page numbers run continuously across the eight volumes, so the
        # highest page number is the last page the machine text reaches.
        max_page = max((int(p.split("-", 1)[1]) for p in page_numbers), default=0)

    return {
        "kind": kind,
        "path": path,
        "entries": entries,
        "unmatched_headers": unmatched,
        "column_codes": len(column_codes),
        "page_numbers": len(page_numbers),
        "printed_pages": printed_pages,
        "max_page": max_page,
        "volumes": len(vol_max_col),
        "vol_max_col": dict(sorted(vol_max_col.items(), key=lambda kv: int(kv[0]))),
        "lb_divs": lb_divs,
        "text_lines": text_lines,
        "chars": chars,
        "printed_lines": lb_divs + entries,
        "entries_per_column_dist": dist(per_col),
        "entries_per_page_dist": dist(per_page),
        "marker_lines_per_column_dist": dist(column_lines_marker),
    }


def dist(values: list[float]) -> dict:
    if not values:
        return {}
    ordered = sorted(values)
    return {
        "n": len(ordered),
        "min": ordered[0],
        "median": statistics.median(ordered),
        "mean": round(statistics.mean(ordered), 3),
        "max": ordered[-1],
    }


def load_oed() -> dict:
    with open(OED_JSON, encoding="utf-8") as fh:
        return json.load(fh)


def oed_rows(oed: dict) -> dict:
    """Aggregate the OED sample: random pages only, anchor page held aside."""
    pages = oed["pages"]
    random_pages = [p for p in pages if p["role"] == "random"]
    anchor = next((p for p in pages if p["role"] == "anchor"), None)
    if len(random_pages) != 3:
        raise SystemExit(f"OED sample must carry exactly 3 random pages, found {len(random_pages)}")
    for p in pages:
        if not p.get("printed_page") or not p.get("leaf"):
            raise SystemExit(f"OED page without a page ID: {p}")
    chars_cols = [p["chars_per_column"] for p in random_pages if p.get("chars_per_column")]
    chars_per_column = statistics.mean(chars_cols) if chars_cols else None
    total_lines = sum(p["printed_lines"] for p in random_pages)
    total_entries = sum(p["entries"] for p in random_pages)
    columns = random_pages[0]["columns"]
    chars_per_page = chars_per_column * columns if chars_per_column else None
    scan = oed["edition"]["scan"]
    return {
        "n_pages": len(random_pages),
        "pages": [p["printed_page"] for p in random_pages],
        "entries": total_entries,
        "lines": total_lines,
        "cols": columns,
        "chars_per_column": chars_per_column,
        "chars_per_page": chars_per_page,
        "entries_per_page": total_entries / len(random_pages),
        "lines_per_page": total_lines / len(random_pages),
        "entries_per_page_dist": dist([p["entries"] for p in random_pages]),
        "lines_per_page_dist": dist([p["printed_lines"] for p in random_pages]),
        "lines_per_column_dist": dist([n for p in random_pages for n in p["lines_per_column"]]),
        "anchor": anchor,
        "scan": scan,
        "edition": oed["edition"]["edition_id"],
    }


def build_rows(pd: dict, pwg: dict, oed: dict) -> list[dict]:
    od = oed_rows(oed)
    w, h = od["scan"]["page_cm_from_declared_dpi"]
    rows = [
        {
            "dictionary": "PD",
            "edition": "Deccan College Encyclopaedic Dictionary of Sanskrit on Historical Principles, letter a",
            "pages": pd["max_page"],
            "entries": pd["entries"],
            "lines": pd["lb_divs"],
            "characters": pd["chars"],
            "entries_per_page": fmt(pd["entries"] / pd["max_page"]),
            "lines_per_page": fmt(pd["lb_divs"] / pd["max_page"]),
            "chars_per_page": fmt(pd["chars"] / pd["max_page"]),
            "columns": 2,
            "page_size": "n/a",
            "source": "machine text (Cologne PDScan 2020 txt/pd.txt)",
            "basis": "pages = last page reached by the machine text (4,327); lines = <div n=\"lb\"> divisions only",
            "note": (
                "Printed lines are lb divisions + entry-opening lines = 547,633 "
                "(the text's own header says 547634Lines); using lb alone gives "
                f"{fmt(pd['lb_divs'] / pd['max_page'])} lines/page, using printed lines gives "
                f"{fmt(pd['printed_lines'] / pd['max_page'])}. The catalogue extent is 6,056 printed pages, "
                "but only pp. 1-4,327 are in the machine text, so per-page averages over 6,056 divide "
                "text-derived content by pages that carry no text in this source."
            ),
        },
        {
            "dictionary": "PWG",
            "edition": "Böhtlingk & Roth, Sanskrit-Wörterbuch (Petersburg), 7 vols",
            "pages": pwg["printed_pages"],
            "entries": pwg["entries"],
            "lines": pwg["text_lines"],
            "characters": pwg["chars"],
            "entries_per_page": fmt(pwg["entries"] / pwg["printed_pages"]),
            "lines_per_page": fmt(pwg["text_lines"] / pwg["printed_pages"]),
            "chars_per_page": fmt(pwg["chars"] / pwg["printed_pages"]),
            "columns": 2,
            "page_size": "n/a",
            "source": "machine text (csl-orig/v02/pwg/pwg.txt)",
            "basis": (
                "pages = sum over volumes of ceil(highest <pc> column / 2) = "
                f"{pwg['printed_pages']}; lines = body lines of the machine text, NOT printed lines"
            ),
            "note": (
                f"{pwg['column_codes']} distinct <pc> page-col codes (odd = left column, even = right, "
                "per pwg-meta2.txt). PWG carries no printed-line markup: its body lines are wrapped at "
                "source level (median 115 characters, max 15,234), so lines/entry and lines/page here are "
                "machine-text measures and are not comparable to PD's printed lines."
            ),
        },
        {
            "dictionary": "OED",
            "edition": "Oxford English Dictionary, corrected re-issue 1933 of OED1 1928, vol. IV (F-G)",
            "pages": od["n_pages"],
            "entries": od["entries"],
            "lines": od["lines"],
            "characters": round(od["chars_per_page"] * od["n_pages"]) if od["chars_per_page"] else "n/a",
            "entries_per_page": fmt(od["entries_per_page"]),
            "lines_per_page": fmt(od["lines_per_page"]),
            "chars_per_page": fmt(od["chars_per_page"]) if od["chars_per_page"] else "n/a",
            "columns": od["cols"],
            "page_size": f"{w} x {h} cm",
            "source": "page images (archive.org scan, volume IV)",
            "basis": (
                "random sample of 3 printed pages ("
                + ", ".join(str(p) for p in od["pages"])
                + "); lines counted by row projection on the page image; "
                "chars/column from the page's own OCR text layer between its two running heads"
            ),
            "note": (
                f"Page size derived from the scan's declared {od['scan']['dpi_declared']} dpi and its "
                "original pixel dimensions, not from a caliper. Entries are a visual count on the page "
                "image (+/-1). The fire anchor page (p. "
                f"{od['anchor']['printed_page'] if od['anchor'] else '?'}) is excluded from these means: "
                "both of its running heads read FIRE., so it is one long entry, not an ordinary page."
            ),
        },
    ]
    return rows


def render_tsv(rows: list[dict]) -> str:
    import io
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=TSV_COLUMNS, delimiter="\t",
                            lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buf.getvalue()


CANARIES = {
    "pd_entries": ("PD", "entries", 107630),
    "pd_line_divisions": ("PD", "lines", 440003),
    "pd_characters": ("PD", "characters", 42247645),
    "pwg_entries": ("PWG", "entries", 123366),
}


def check_canaries(rows: list[dict], pd: dict, pwg: dict, oed: dict) -> list[str]:
    failures = []
    by_dict = {r["dictionary"]: r for r in rows}
    for label, (dictionary, column, expected) in CANARIES.items():
        got = by_dict[dictionary][column]
        if got != expected:
            failures.append(f"{label}: expected {expected}, got {got}")
    if pd["printed_lines"] != 547633:
        failures.append(f"pd_printed_lines: expected 547633, got {pd['printed_lines']}")
    if pd["column_codes"] != 7684:
        failures.append(f"pd_column_codes: expected 7684, got {pd['column_codes']}")
    if pwg["text_lines"] != 223497:
        failures.append(f"pwg_machine_lines: expected 223497, got {pwg['text_lines']}")
    if pwg["column_codes"] != 8171:
        failures.append(f"pwg_column_codes: expected 8171, got {pwg['column_codes']}")
    if pwg["printed_pages"] != 4750:
        failures.append(f"pwg_printed_pages: expected 4750, got {pwg['printed_pages']}")
    return failures


def check_pins(pd: dict, pwg: dict, oed: dict) -> list[str]:
    """Every pinned row in the forensic TSV must re-derive."""
    od = oed_rows(oed)
    facts = {
        "pd_entries": pd["entries"],
        "pd_line_divisions": pd["lb_divs"],
        "pd_entry_openers": pd["entries"],
        "pd_printed_lines": pd["printed_lines"],
        "pd_characters": pd["chars"],
        "pd_column_codes": pd["column_codes"],
        "pd_page_numbers": pd["page_numbers"],
        "pd_columns_per_page": 2,
        "pwg_entries": pwg["entries"],
        "pwg_machine_lines": pwg["text_lines"],
        "pwg_column_codes": pwg["column_codes"],
        "pwg_printed_pages": pwg["printed_pages"],
        "oed_sample_pages": od["n_pages"],
        "oed_columns": od["cols"],
        "oed_lines_per_page_mean": round(od["lines_per_page"], 2),
        "oed_entries_per_page_mean": round(od["entries_per_page"], 2),
    }
    failures = []
    with open(PINS_TSV, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            key = row["key"]
            if key not in facts:
                failures.append(f"pin {key}: no such fact")
                continue
            expected = float(row["expected"])
            got = float(facts[key])
            if abs(got - expected) > 0.005:
                failures.append(f"pin {key}: expected {expected}, got {facts[key]}")
    return failures


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pd", default=DEFAULT_PD, help="path to PDScan 2020 txt/pd.txt")
    ap.add_argument("--pwg", default=DEFAULT_PWG, help="path to csl-orig/v02/pwg/pwg.txt")
    ap.add_argument("--check", action="store_true",
                    help="re-derive everything and diff against the committed files")
    args = ap.parse_args(argv)

    if not args.pd or not os.path.exists(args.pd):
        print(f"pd.txt not found: {args.pd!r}; pass --pd or set PD_TXT", file=sys.stderr)
        return 3
    if not os.path.exists(args.pwg):
        print(f"pwg.txt not found: {args.pwg!r}; pass --pwg or set PWG_TXT", file=sys.stderr)
        return 3

    pd = measure_text(args.pd, "pd")
    pwg = measure_text(args.pwg, "pwg")
    oed = load_oed()
    rows = build_rows(pd, pwg, oed)
    tsv = render_tsv(rows)

    canary_failures = check_canaries(rows, pd, pwg, oed)
    pin_failures = check_pins(pd, pwg, oed)
    with open(PINS_TSV, encoding="utf-8", newline="") as _fh:
        n_pins = sum(1 for _ in csv.DictReader(_fh, delimiter="\t"))

    if args.check:
        failures = list(canary_failures) + list(pin_failures)
        try:
            with open(OUT_TSV, encoding="utf-8", newline="") as fh:
                committed = fh.read()
        except FileNotFoundError:
            committed = None
        if committed != tsv:
            failures.append(f"{os.path.relpath(OUT_TSV, ROOT)} is stale; re-run without --check")
        if failures:
            for f in failures:
                print(f"FAIL {f}", file=sys.stderr)
            return 2
        print(f"PASS {os.path.relpath(OUT_TSV, ROOT)}: 3 rows, "
              f"{len(CANARIES) + 5} canaries, {n_pins} pins")
        return 0

    with open(OUT_TSV, "w", encoding="utf-8", newline="") as fh:
        fh.write(tsv)
    print(f"wrote {os.path.relpath(OUT_TSV, ROOT)}")
    for row in rows:
        print(f"  {row['dictionary']}: pages={row['pages']} entries={row['entries']} "
              f"lines={row['lines']} chars={row['characters']} "
              f"entries/page={row['entries_per_page']} lines/page={row['lines_per_page']} "
              f"chars/page={row['chars_per_page']}")
    if canary_failures:
        for f in canary_failures:
            print(f"CANARY FAIL {f}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
