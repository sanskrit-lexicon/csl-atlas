#!/usr/bin/env python3
"""H6932 -- land a reproducible AOB declared-entry table from the committed inventory.

H6720/H6960 already parsed the printed *Abbreviations of Books* into
``data/pd/pd_aob_entries.tsv`` (one row per printed row, tails reassembled
across OCR wraps). H6923 then showed that the denominator behind A68 metric 2
(1,419 entry rows) had no committed parser behind it, while the published
``pd_aob_declared_works.tsv`` (1,112 works / 1,118 edition rows) is a clean
subset, not the canon.

This script does **not** re-parse the OCR. It projects the landed inventory into
the declared-entry table the denominator needs, and makes every count that is
quoted from it reproducible from a committed file:

  data/pd/pd_aob_declared_entries.tsv  one row per USABLE printed entry
                                       (siglum, title, year, page, flags)
  data/pd/pd_aob_declared_entries.json counts, hashes, the edition-to-work
                                       collapse, and the candidate 118/N values

The denominator remains a recorded MG judgment, not a silent pick. The ruling of
17-10-2026 quotes the central estimate 1,476 (118/1,476 = 7.99 % -> 8.0 %); the
landed inventory makes a *point* available at 1,437 usable entries
(118/1,437 = 8.21 %). Both are recorded, the band stays as provenance, and the
choice is left open for MG to re-rule.

Run:
  python3 scripts/pd_aob_declared_entries.py            # derive + write
  python3 scripts/pd_aob_declared_entries.py --check    # verify committed artifacts
  python3 scripts/pd_aob_declared_entries.py --selftest # invariants + named rows

Exit codes: 0 ok / 1 drift under --check or failed selftest / 2 input missing.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRIES_IN = ROOT / "data/pd/pd_aob_entries.tsv"
WORKS_IN = ROOT / "data/pd/pd_aob_declared_works.tsv"
METRICS = ROOT / "data/pd/pd_dcs_metrics.json"
OUT_TSV = ROOT / "data/pd/pd_aob_declared_entries.tsv"
OUT_JSON = ROOT / "data/pd/pd_aob_declared_entries.json"

YEAR_RE = re.compile(r"\b(1[89]\d\d|20[0-2]\d)\b")
LATIN_RE = re.compile(r"[A-Za-z\u00c0-\u024f]")

COLS = ["entry_id", "page", "siglum", "siglum_skeleton", "title", "year",
        "title_or_year", "merged_token", "garbled_start", "wellformed",
        "exercised", "routes", "harvested_sigla", "title_tail"]


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path):
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        return reader.fieldnames or [], list(reader)


def derive_title(tail: str) -> str:
    """Best committed projection: the first comma-separated segment of the tail.

    ``title_tail`` fuses title, author, publisher, year and locus in one OCR
    field. The printed title always opens the field, so the first comma (or,
    when there is no comma, the whole field) is the reproducible title
    projection. It is never hand-edited.
    """
    head = tail.split(",", 1)[0].strip()
    if not head or not LATIN_RE.search(head):
        return ""
    return head


def project_rows(entries):
    rows = []
    for r in entries:
        if r.get("junk") != "no":
            continue
        tail = r.get("title_tail", "")
        title = derive_title(tail)
        m = YEAR_RE.search(tail)
        year = m.group(1) if m else ""
        rows.append({
            "entry_id": r["entry_id"],
            "page": r["page"],
            "siglum": r["siglum"],
            "siglum_skeleton": r["siglum_skeleton"],
            "title": title,
            "year": year,
            "title_or_year": "yes" if (title or year) else "no",
            "merged_token": r["merged_token"],
            "garbled_start": r["garbled_start"],
            "wellformed": r["wellformed"],
            "exercised": r["exercised"],
            "routes": r["routes"],
            "harvested_sigla": r["harvested_sigla"],
            "title_tail": tail,
        })
    return rows


def render_tsv(rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLS, delimiter="\t",
                       lineterminator="\n", extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


def measure():
    entries_cols, entries = read_tsv(ENTRIES_IN)
    works_cols, works = read_tsv(WORKS_IN)
    metrics = json.loads(METRICS.read_text(encoding="utf-8"))

    for col in ("entry_id", "page", "siglum", "junk", "title_tail"):
        if col not in entries_cols:
            raise SystemExit(f"[FAIL] {ENTRIES_IN} has no {col} column")
    if "n_editions" not in works_cols:
        raise SystemExit(f"[FAIL] {WORKS_IN} has no n_editions column")

    projected = project_rows(entries)
    usable = len(projected)
    parsed = len(entries)
    junk = sum(1 for r in entries if r.get("junk") != "no")
    wellformed = sum(1 for r in projected if r["wellformed"] == "yes")
    no_title_or_year = [r["entry_id"] for r in projected
                        if r["title_or_year"] == "no"]

    works_rows = len(works)
    edition_rows = sum(int(r["n_editions"]) for r in works)
    n_covered = int(metrics["n_covered_dcs_titles"])

    candidates = {
        "1437_landed_usable_entries": usable,
        "1444_landed_parsed_entries": parsed,
        "1464_print_census": int(metrics["n_declared_aob_print_census"]),
        "1469_entry_rows_header_corrected":
            int(metrics["n_declared_aob_entry_rows_header_corrected"]),
        "1476_structural_entry_lines":
            int(metrics["n_declared_aob_entry_lines_structural_r1"]),
        "1517_reparse_raw": int(metrics["n_declared_aob_entries_reparse_raw"]),
    }
    pct = {k: round(100.0 * n_covered / n, 2) for k, n in candidates.items()}

    return projected, {
        "generated_by": "H6932 scripts/pd_aob_declared_entries.py "
                        "(DeepSeek v4.1 Flash, deepseek/deepseek-flash)",
        "method": "projection of the committed H6720/H6960 entry inventory; "
                  "no OCR re-parse. One row per entry with junk=no; title is "
                  "the first comma-separated segment of title_tail; year is the "
                  "first 1830-2029 token.",
        "inputs": {
            "entries": {"path": "data/pd/pd_aob_entries.tsv",
                        "sha256": sha256_of(ENTRIES_IN),
                        "rows": parsed},
            "works": {"path": "data/pd/pd_aob_declared_works.tsv",
                      "sha256": sha256_of(WORKS_IN),
                      "rows": works_rows},
            "metrics": {"path": "data/pd/pd_dcs_metrics.json",
                        "sha256": sha256_of(METRICS)},
        },
        "counts": {
            "entries_parsed": parsed,
            "entries_usable": usable,
            "entries_junk": junk,
            "entries_wellformed_usable": wellformed,
            "entries_without_title_or_year": len(no_title_or_year),
            "entries_without_title_or_year_ids": no_title_or_year,
        },
        "edition_to_work_collapse": {
            "source": "data/pd/pd_aob_declared_works.tsv",
            "works": works_rows,
            "edition_rows": edition_rows,
            "is": "published clean-subset collapse (H6707/H6720), not the "
                  "inventory-derived canon; kept beside the table for comparison",
        },
        "denominator": {
            "n_covered_dcs_titles": n_covered,
            "landed_point": {"n": usable, "pct": pct["1437_landed_usable_entries"]},
            "ruled_central_estimate": {
                "n": int(metrics["metric_title_level_declared_pct_denominator"]),
                "pct": float(metrics["metric_title_level_declared_pct"]),
                "display": float(metrics["metric_title_level_declared_pct_ruled_display"]),
            },
            "band_provenance": metrics["declared_canon_denominator_band"],
            "candidates": {k: {"n": n, "pct": pct[k]} for k, n in candidates.items()},
            "choice": "OPEN -- both the landed point (1437) and the ruled central "
                      "estimate (1476) are reproducible; MG re-rules the quoted "
                      "denominator. The 7.8-8.3 % band brackets both.",
        },
        "artifacts": {
            "entries_tsv": "data/pd/pd_aob_declared_entries.tsv",
            "entries_json": "data/pd/pd_aob_declared_entries.json",
        },
    }


def selftest() -> int:
    rows, summary = measure()
    c = summary["counts"]
    assert c["entries_parsed"] == 1444, c
    assert c["entries_usable"] == 1437, c
    assert c["entries_junk"] == 7, c
    assert c["entries_wellformed_usable"] == 1379, c
    assert len(rows) == c["entries_usable"]
    assert summary["denominator"]["landed_point"]["pct"] == 8.21, summary["denominator"]
    # H6960's named absences must own rows in the projection
    by_siglum = {r["siglum"]: r for r in rows}
    assert "Kad. Kadam" in by_siglum, "Kadambari row missing"
    assert "P. Astadhy" in by_siglum, "Astadhyayi row missing"
    print("ok  selftest: 1,444 parsed / 1,437 usable / 7 junk / 1,379 well-formed")
    print("ok  selftest: 118/1,437 = 8.21 % point; Kad. and P. Astadhy rows present")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="recompute and compare with the committed artifacts")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    rows, summary = measure()
    tsv = render_tsv(rows)
    js = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"

    if args.check:
        diffs = []
        if not OUT_TSV.is_file() or OUT_TSV.read_text(encoding="utf-8") != tsv:
            diffs.append(OUT_TSV.name)
        if not OUT_JSON.is_file() or OUT_JSON.read_text(encoding="utf-8") != js:
            diffs.append(OUT_JSON.name)
        metrics = json.loads(METRICS.read_text(encoding="utf-8"))
        usable = summary["counts"]["entries_usable"]
        pct = summary["denominator"]["landed_point"]["pct"]
        expected = {
            "n_declared_aob_rows_edition_level": usable,
            "metric_title_level_declared_pct_landed_inventory_point": pct,
            "declared_canon_rows_reproducible": True,
            "declared_canon_entries_table": "data/pd/pd_aob_declared_entries.tsv",
        }
        for k, v in expected.items():
            if metrics.get(k) != v:
                diffs.append("metrics:%s" % k)
        if diffs:
            print("[FAIL] committed artifacts drifted in: %s" % ", ".join(diffs),
                  file=sys.stderr)
            return 1
        print("ok  declared-entry table reproduces; metrics spine points at "
              "N=%d (118/N = %.2f %%)" % (usable, pct))
        return 0

    OUT_TSV.write_text(tsv, encoding="utf-8", newline="\n")
    OUT_JSON.write_text(js, encoding="utf-8", newline="\n")
    print("wrote %s (%d rows)" % (OUT_TSV.relative_to(ROOT), len(rows)))
    print("wrote %s" % OUT_JSON.relative_to(ROOT))
    print("118 / %d = %.2f %% (landed point); ruled central %d = %.2f %%"
          % (summary["counts"]["entries_usable"],
             summary["denominator"]["landed_point"]["pct"],
             summary["denominator"]["ruled_central_estimate"]["n"],
             summary["denominator"]["ruled_central_estimate"]["pct"]))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
