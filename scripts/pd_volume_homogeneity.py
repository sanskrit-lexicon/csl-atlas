#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H6947 — PD volume-level homogeneity, print-anchored.

Reads the external, read-only PDScan 2020 machine text and the Deccan College
publication ledger, then writes per-fascicle-volume and per-bound-volume entry
size, marking and citation-block tables.

    python scripts/pd_volume_homogeneity.py --pd /path/to/pd.txt
    python scripts/pd_volume_homogeneity.py --check --pd /path/to/pd.txt

The unit is the ``<L>…<LEND>`` entry.  For every entry this script measures
printed lines (body lines, the H6949 definition), characters, ``{#...#}``
blocks, H6949 quotations, and the H6942 bracketed-dictionary-source mark.  Each
entry is assigned to a ledger fascicle by its printed page number; the ledger
is read from ``data/pd/pd_publication_ledger.tsv`` (35 rows, PDF hash pinned in
the adjacent ``.meta.json``).

The digital text covers pp. 1-4327 = ledger fascicles 1.1-8.3 (1976-2008).
Rows 9.1-35 are print-only and carry no measurements; they are kept in the TSV
so the ledger join is complete.

Stdlib only; no network.  Exit 3 when the machine text is missing, exit 2 when
the H6942/H6949 baselines or ``--check`` comparison fail.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import statistics
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "scripts", "lib"))

import pd_marked_sources as marks_rule
import quotation_units
from pd_quotation_units import citation_tail

LEDGER = os.path.join(ROOT, "data", "pd", "pd_publication_ledger.tsv")
OUT_TSV = os.path.join(ROOT, "data", "pd", "pd_volume_homogeneity.tsv")
OUT_BOUND_TSV = os.path.join(ROOT, "data", "pd", "pd_volume_homogeneity_bound.tsv")
OUT_JSON = os.path.join(ROOT, "data", "pd", "pd_volume_homogeneity.json")
DEFAULT_PD = os.environ.get("PD_TXT", "")

RE_HDR = re.compile(r"^<L>([\d.]+)<pc>([^<]*)<k1>([^<\s]*)<k2>([^<\s]*)")
RE_PAGE = re.compile(r"^(\d+)-(\d+)([ab])?")
NEAR_MISS = [re.compile(p, re.I) for p in (
    r"^\s*dbh", r"^\s*p\s*[.]?\s*w", r"^\s*m\s*[.]?\s*w", r"^\s*apt",
    r"^\s*vi[śs]va", r"^\s*n\s*[.]?\s*t", r"^\s*v[āa]c",
)]

TSV_COLUMNS = [
    "ledger_id", "bound_volume", "year", "general_editor", "pp_lo", "pp_hi",
    "in_digital_text", "pages_present", "entries",
    "mean_lines", "median_lines", "mean_chars", "median_chars",
    "mean_blocks", "median_blocks", "mean_quotations", "median_quotations",
    "marked_entries", "marking_share_pct", "marks_total",
    *[f"marks_{name}" for name in marks_rule.SOURCE_NAMES],
    "bracket_entries", "bracket_share_pct", "brackets_total",
    "marks_per_1000_lines", "marks_per_1000_blocks",
]
BOUND_COLUMNS = [
    "bound_volume", "ledger_ids", "year_first", "year_last", "general_editors",
    "pp_lo", "pp_hi", "pages_present", "entries",
    "mean_lines", "median_lines", "mean_chars", "median_chars",
    "mean_blocks", "median_blocks", "mean_quotations", "median_quotations",
    "marked_entries", "marking_share_pct", "marks_total",
    *[f"marks_{name}" for name in marks_rule.SOURCE_NAMES],
    "bracket_entries", "bracket_share_pct", "brackets_total",
    "marks_per_1000_lines", "marks_per_1000_blocks",
]

BASELINE = {
    "entries": 107630,
    "marked_entries": 1801,
    "marks_total": 1956,
    "marks_by_source": {
        "DBHS": 852, "PW": 399, "APTE": 264, "MW": 245,
        "VISVA": 101, "NT": 84, "VAC": 11,
    },
    "blocks": 621100,
}


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_ledger(path: str) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    for row in rows:
        row["pp_lo"] = int(row["pp_lo"])
        row["pp_hi"] = int(row["pp_hi"])
        row["year"] = int(row["year"])
    if len(rows) != 35:
        raise SystemExit(f"ledger must have 35 rows, found {len(rows)}")
    return rows


def iter_entries(lines):
    cur = None
    for line in lines:
        line = line.rstrip("\n")
        if line.startswith("<L>"):
            if cur is not None:
                yield cur[0], cur[1]
            cur = [line, []]
        elif cur is not None:
            if line.startswith("<LEND>"):
                yield cur[0], cur[1]
                cur = None
            else:
                cur[1].append(line)
    if cur is not None:
        yield cur[0], cur[1]


def fmt(value: float) -> str:
    return f"{value:.2f}"


def summary(rows: list[dict]) -> dict:
    n = len(rows)
    if not n:
        return {}
    lines = [r["lines"] for r in rows]
    chars = [r["chars"] for r in rows]
    blocks = [r["blocks"] for r in rows]
    quotes = [r["quotations"] for r in rows]
    marked = sum(1 for r in rows if r["marked"])
    marks_total = sum(len(r["marks"]) for r in rows)
    marks_by_source = Counter(m for r in rows for m in r["marks"])
    bracket_entries = sum(1 for r in rows if r["brackets"])
    brackets_total = sum(len(r["brackets"]) for r in rows)
    total_lines = sum(lines)
    total_blocks = sum(blocks)
    return {
        "entries": n,
        "mean_lines": statistics.mean(lines),
        "median_lines": statistics.median(lines),
        "mean_chars": statistics.mean(chars),
        "median_chars": statistics.median(chars),
        "mean_blocks": statistics.mean(blocks),
        "median_blocks": statistics.median(blocks),
        "mean_quotations": statistics.mean(quotes),
        "median_quotations": statistics.median(quotes),
        "marked_entries": marked,
        "marking_share_pct": 100.0 * marked / n,
        "marks_total": marks_total,
        "marks_by_source": {name: marks_by_source.get(name, 0) for name in marks_rule.SOURCE_NAMES},
        "bracket_entries": bracket_entries,
        "bracket_share_pct": 100.0 * bracket_entries / n,
        "brackets_total": brackets_total,
        "marks_per_1000_lines": 1000.0 * marks_total / total_lines,
        "marks_per_1000_blocks": 1000.0 * marks_total / total_blocks,
    }


def tsv_row(row: dict, agg: dict) -> list[str]:
    out = [
        row["ledger_id"], str(row["bound_volume"]), str(row["year"]),
        row["general_editor"], str(row["pp_lo"]), str(row["pp_hi"]),
        row["in_digital_text"],
    ]
    if not agg:
        return out + [""] * (len(TSV_COLUMNS) - len(out))
    out.extend([
        str(agg["pages_present"]), str(agg["entries"]),
        fmt(agg["mean_lines"]), fmt(agg["median_lines"]),
        fmt(agg["mean_chars"]), fmt(agg["median_chars"]),
        fmt(agg["mean_blocks"]), fmt(agg["median_blocks"]),
        fmt(agg["mean_quotations"]), fmt(agg["median_quotations"]),
        str(agg["marked_entries"]), fmt(agg["marking_share_pct"]),
        str(agg["marks_total"]),
        *[str(agg["marks_by_source"][name]) for name in marks_rule.SOURCE_NAMES],
        str(agg["bracket_entries"]), fmt(agg["bracket_share_pct"]),
        str(agg["brackets_total"]),
        fmt(agg["marks_per_1000_lines"]), fmt(agg["marks_per_1000_blocks"]),
    ])
    return out


def build(text: str, ledger: list[dict]) -> tuple[str, str, dict]:
    ranges = [row for row in ledger if row["in_digital_text"] == "yes"]
    rows = []
    unassigned = []
    diagnostics = {
        "uncapped_marked_entries": 0,
        "uncapped_marks_total": 0,
        "long_source_brackets": 0,
        "long_source_brackets_by_volume": defaultdict(int),
        "gloss_excluded_brackets": 0,
        "near_miss_source_brackets": 0,
        "near_miss_examples": [],
        "all_bracket_entries_by_volume": defaultdict(int),
        "all_brackets_by_volume": defaultdict(int),
        "entries_by_volume": defaultdict(int),
        "zero_mark_pages": defaultdict(list),
        "unassigned_entries": 0,
    }
    for hdr, body in iter_entries(text.splitlines()):
        m = RE_HDR.match(hdr)
        if not m:
            unassigned.append(hdr)
            continue
        lid, pc, _k1, _k2 = m.groups()
        pm = RE_PAGE.match(pc)
        if not pm:
            unassigned.append(hdr)
            continue
        page = int(pm.group(2))
        vol = pm.group(1)
        entry = hdr + "\n" + "\n".join(body)
        flat = " ".join(body).replace('<div n="lb">', " ")
        quotes = quotation_units.count_units(flat, citation_tail)["quotations"]
        marks = marks_rule.entry_marks(entry)
        capped = marks_rule.entry_marks(entry, capped=True)
        brackets = re.findall(r"\[([^\]]*)\]", entry)
        ledger_row = next((r for r in ranges if r["pp_lo"] <= page <= r["pp_hi"]), None)
        if ledger_row is None:
            diagnostics["unassigned_entries"] += 1
            continue
        rec = {
            "ledger_id": ledger_row["ledger_id"],
            "bound_volume": int(vol),
            "page": page,
            "lines": len(body),
            "chars": len(flat),
            "blocks": flat.count("{#"),
            "quotations": quotes,
            "marks": marks,
            "marked": bool(capped),
            "brackets": brackets,
        }
        rows.append(rec)
        diagnostics["entries_by_volume"][vol] += 1
        if marks:
            diagnostics["uncapped_marked_entries"] += 1
            diagnostics["uncapped_marks_total"] += len(marks)
        for token in brackets:
            name = marks_rule.leading_source(token)
            if name is None:
                if any(p.match(token) for p in NEAR_MISS):
                    diagnostics["near_miss_source_brackets"] += 1
                    if len(diagnostics["near_miss_examples"]) < 8:
                        diagnostics["near_miss_examples"].append(token[:80])
                continue
            if len(token) > marks_rule.MAX_BRACKET_CONTENT:
                diagnostics["long_source_brackets"] += 1
                diagnostics["long_source_brackets_by_volume"][vol] += 1
            if name == "DBHS" and marks_rule.DBHS_GLOSS.match(token.lstrip()) \
                    and not marks_rule.DBHS_POINTER.match(token.lstrip()):
                diagnostics["gloss_excluded_brackets"] += 1
        if brackets:
            diagnostics["all_bracket_entries_by_volume"][vol] += 1
            diagnostics["all_brackets_by_volume"][vol] += len(brackets)

    by_ledger = defaultdict(list)
    by_bound = defaultdict(list)
    for rec in rows:
        by_ledger[rec["ledger_id"]].append(rec)
        by_bound[rec["bound_volume"]].append(rec)

    ledger_out = []
    for row in ledger:
        agg = summary(by_ledger.get(row["ledger_id"], []))
        if agg:
            agg["pages_present"] = len({r["page"] for r in by_ledger[row["ledger_id"]]})
        ledger_out.append(tsv_row(row, agg))

    bound_out = []
    for vol in sorted(by_bound):
        recs = by_bound[vol]
        led = [r for r in ranges if int(r["bound_volume"]) == vol]
        agg = summary(recs)
        agg["pages_present"] = len({r["page"] for r in recs})
        led_ids = [r["ledger_id"] for r in led]
        editors = []
        for r in led:
            for name in r["general_editor"].split(";"):
                name = name.strip()
                if name and name not in editors:
                    editors.append(name)
        bound_out.append([
            str(vol),
            led_ids[0] + "-" + led_ids[-1] if led_ids else "",
            str(min(r["year"] for r in led)),
            str(max(r["year"] for r in led)),
            "; ".join(editors),
            str(min(r["pp_lo"] for r in led)),
            str(max(r["pp_hi"] for r in led)),
            str(agg["pages_present"]), str(agg["entries"]),
            fmt(agg["mean_lines"]), fmt(agg["median_lines"]),
            fmt(agg["mean_chars"]), fmt(agg["median_chars"]),
            fmt(agg["mean_blocks"]), fmt(agg["median_blocks"]),
            fmt(agg["mean_quotations"]), fmt(agg["median_quotations"]),
            str(agg["marked_entries"]), fmt(agg["marking_share_pct"]),
            str(agg["marks_total"]),
            *[str(agg["marks_by_source"][name]) for name in marks_rule.SOURCE_NAMES],
            str(agg["bracket_entries"]), fmt(agg["bracket_share_pct"]),
            str(agg["brackets_total"]),
            fmt(agg["marks_per_1000_lines"]), fmt(agg["marks_per_1000_blocks"]),
        ])

    page_stats = defaultdict(lambda: {"entries": 0, "marked": 0, "brackets": 0, "lines": 0})
    for rec in rows:
        if rec["bound_volume"] not in (7, 8):
            continue
        key = (rec["bound_volume"], rec["page"])
        st = page_stats[key]
        st["entries"] += 1
        st["marked"] += 1 if rec["marked"] else 0
        st["brackets"] += len(rec["brackets"])
        st["lines"] += rec["lines"]
    for vol in (7, 8):
        zero = [
            {"page": page, **st}
            for (v, page), st in page_stats.items()
            if v == vol and st["marked"] == 0 and st["entries"] >= 20
        ]
        zero.sort(key=lambda d: (-d["entries"], d["page"]))
        diagnostics["zero_mark_pages"][str(vol)] = zero[:5]

    totals = {
        "entries": len(rows),
        "lines": sum(r["lines"] for r in rows),
        "chars": sum(r["chars"] for r in rows),
        "blocks": sum(r["blocks"] for r in rows),
        "quotations": sum(r["quotations"] for r in rows),
        "marked_entries": sum(1 for r in rows if r["marked"]),
        "marks_total": sum(len(r["marks"]) for r in rows),
        "marks_by_source": dict(Counter(m for r in rows for m in r["marks"])),
    }
    diagnostics["long_source_brackets_by_volume"] = dict(diagnostics["long_source_brackets_by_volume"])
    diagnostics["all_bracket_entries_by_volume"] = dict(diagnostics["all_bracket_entries_by_volume"])
    diagnostics["all_brackets_by_volume"] = dict(diagnostics["all_brackets_by_volume"])
    diagnostics["entries_by_volume"] = dict(diagnostics["entries_by_volume"])
    diagnostics["unassigned_headers"] = len(unassigned)
    diagnostics["all_bracket_share_by_volume_pct"] = {
        vol: round(100.0 * diagnostics["all_bracket_entries_by_volume"].get(vol, 0)
                   / diagnostics["entries_by_volume"][vol], 2)
        for vol in sorted(diagnostics["entries_by_volume"])
    }

    document = {
        "dataset": "pd_volume_homogeneity",
        "handoff": "H6947",
        "generated_by": "python scripts/pd_volume_homogeneity.py",
        "generated_on": "2026-10-18",
        "definitions": {
            "entry": "<L>…<LEND>",
            "printed_lines": "body lines between <L> and <LEND>, H6949 definition",
            "chars": "characters of the body after joining lines and removing <div n=\"lb\"> tags",
            "blocks": "{#...#} SLP1 blocks, H6949 block unit",
            "quotations": "H6949 quotation unit (run of blocks followed by a siglum locus)",
            "marked_entry": "entry with >=1 bracketed dictionary source under the H6942 capped rule",
        },
        "source": {
            "bytes": os.path.getsize(DEFAULT_PD) if DEFAULT_PD and os.path.exists(DEFAULT_PD) else None,
            "sha256": sha256(DEFAULT_PD) if DEFAULT_PD and os.path.exists(DEFAULT_PD) else None,
            "url": "https://sanskrit-lexicon.uni-koeln.de/scans/PDScan/2020/downloads/pdtxt.zip",
            "licence": "© 2014 The Sanskrit Library / Thomas Malten, CC BY-NC-SA 3.0",
        },
        "ledger": {
            "path": "data/pd/pd_publication_ledger.tsv",
            "sha256": sha256(LEDGER),
            "rows": len(ledger),
            "digital_rows": sum(1 for r in ledger if r["in_digital_text"] == "yes"),
            "source_url": "https://dcpune.ac.in/pdf/12.%20Publication%20(Dictionary%20Publication).pdf",
            "source_sha256": "7432bd1bb5ab992c42529fface6409459a3abe732a474f1484a21d190307093d",
        },
        "scope_caveat": "Machine text = pp. 1-4327, ledger fascicles 1.1-8.3 (1976-2008). Rows 9.1-35 are print-only and carry no measurements.",
        "baseline_canaries": {
            "h6942_entries": BASELINE["entries"],
            "h6942_marked_entries": BASELINE["marked_entries"],
            "h6942_marks_total": BASELINE["marks_total"],
            "h6942_marks_by_source": BASELINE["marks_by_source"],
            "h6949_blocks": BASELINE["blocks"],
            "reproduced": None,
        },
        "totals": totals,
        "diagnostics": diagnostics,
    }
    document["baseline_canaries"]["reproduced"] = (
        totals["entries"] == BASELINE["entries"]
        and totals["marked_entries"] == BASELINE["marked_entries"]
        and totals["marks_total"] == BASELINE["marks_total"]
        and {name: totals["marks_by_source"].get(name, 0) for name in marks_rule.SOURCE_NAMES}
        == BASELINE["marks_by_source"]
        and totals["blocks"] == BASELINE["blocks"]
    )

    def render_tsv(columns, rows_):
        lines = ["\t".join(columns)]
        lines.extend("\t".join(r) for r in rows_)
        return "\n".join(lines) + "\n"

    return render_tsv(TSV_COLUMNS, ledger_out), render_tsv(BOUND_COLUMNS, bound_out), document


def main(argv=None) -> int:
    global DEFAULT_PD
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pd", default=DEFAULT_PD, help="path to PDScan 2020 txt/pd.txt")
    ap.add_argument("--ledger", default=LEDGER)
    ap.add_argument("--check", action="store_true", help="compare with committed artifacts")
    args = ap.parse_args(argv)

    if not args.pd or not os.path.exists(args.pd):
        print(f"pd.txt not found: {args.pd!r}; pass --pd or set PD_TXT", file=sys.stderr)
        return 3
    DEFAULT_PD = args.pd

    ledger = read_ledger(args.ledger)
    with open(args.pd, encoding="utf-8") as fh:
        text = fh.read()
    tsv, bound_tsv, document = build(text, ledger)

    if not document["baseline_canaries"]["reproduced"]:
        print("baseline FAIL: H6942/H6949 canaries do not reproduce", file=sys.stderr)
        print(json.dumps(document["baseline_canaries"], indent=2), file=sys.stderr)
        return 2

    if args.check:
        expected = {
            OUT_TSV: tsv,
            OUT_BOUND_TSV: bound_tsv,
            OUT_JSON: json.dumps(document, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
        }
        failures = []
        for path, content in expected.items():
            if not os.path.exists(path):
                failures.append(f"missing {path}")
                continue
            with open(path, encoding="utf-8") as fh:
                if fh.read() != content:
                    failures.append(f"drift {path}")
        if failures:
            print("PASS: false — " + "; ".join(failures), file=sys.stderr)
            return 2
        print("PASS: per-fascicle TSV, per-bound-volume TSV and JSON reproduce; H6942/H6949 canaries green")
        return 0

    for path, content in ((OUT_TSV, tsv), (OUT_BOUND_TSV, bound_tsv)):
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(content)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(document, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")

    t = document["totals"]
    print(f"entries {t['entries']:,}  marked {t['marked_entries']:,} "
          f"({100 * t['marked_entries'] / t['entries']:.2f} %)  marks {t['marks_total']:,}")
    print(f"wrote {OUT_TSV}")
    print(f"wrote {OUT_BOUND_TSV}")
    print(f"wrote {OUT_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
