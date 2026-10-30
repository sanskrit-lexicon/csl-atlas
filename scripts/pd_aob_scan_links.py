#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C3 PD AOB scan links. Offline build/--check; network only --fetch-archive."""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "pd")
PAGE_MAP = os.path.join(DATA, "pd_aob_scan_page_map.tsv")
PROBES = os.path.join(DATA, "pd_aob_scan_probes_2026-10-30.json")
OUT_TARGETS = os.path.join(DATA, "pd_aob_scan_targets.tsv")
OUT_LOCI = os.path.join(DATA, "pd_aob_locus_scan_resolution.tsv")
OUT_JSON = os.path.join(DATA, "pd_aob_scan_links_summary.json")
REPORT = os.path.join(ROOT, "reports", "PD_AOB_SCAN_LINKS_C3_2026-10-30.md")
INDEX_ARCHIVE_ID = "mAAY_an-encyclopaedic-dictionary-of-sanskrit-vol-1-critically-edited-by-a-m-ghatage-1"
PAGE_SCHEMES = {"page_line", "page_sloka", "volume_page_line"}
TARGET_COLUMNS = [
    "record_id", "work_id", "index_page", "index_row", "siglum", "title_iast",
    "work_identity_status", "n_aob_editions", "aob_edition_ids",
    "aob_edition_status", "exact_siglum", "aob_exact_entry_ids",
    "scan_target_status", "scan_urls", "index_scan_url",
]
MAP_COLUMNS = [
    "siglum", "archive_id", "volume", "printed_page", "leaf", "target_status",
    "scan_url", "map_basis",
]
LOCUS_COLUMNS = [
    "locus_id", "siglum", "principal_siglum", "work_id", "locus", "kind",
    "resolution_status", "archive_id", "printed_page", "scan_url", "reason",
]
ROMAN = set("i ii iii iv v vi vii viii ix x".split())

sys.path.insert(0, os.path.join(ROOT, "scripts", "lib"))
from pd_aob_scan_archive import (  # noqa: E402
    fetch_bytes, monotonic_page_candidates, numeric_page, probe_image, scan_url,
)


def read_tsv(name):
    with open(os.path.join(DATA, name), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path, columns, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write("\t".join(columns) + "\n")
        for row in rows:
            fh.write("\t".join(str(row.get(c, "")) for c in columns).rstrip("\t") + "\n")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_archive():
    editions = read_tsv("pd_aob_scan_editions.tsv")
    candidates = []
    receipts = {"dataset": "pd_aob_scan_c3", "generated_on": "2026-10-30",
                "protocol": "Archive.org metadata + scandata; monotonic printed-page runs only",
                "items": [], "locus_page_samples": []}
    for edition in editions:
        ident = edition["archive_id"]
        meta_url = "https://archive.org/metadata/" + ident
        payload, status, _ = fetch_bytes(meta_url)
        metadata = json.loads(payload)
        files = {f["name"]: f for f in metadata.get("files", [])}
        scan_name = next((name for name in files if name.endswith("_scandata.xml")), None)
        if not scan_name:
            raise RuntimeError(f"no scandata for {ident}")
        scan_url_raw = "https://archive.org/download/" + ident + "/" + urllib.parse.quote(scan_name)
        scan_payload, scan_status, _ = fetch_bytes(scan_url_raw)
        scan_text = scan_payload.decode("utf-8")
        accepted, labelled = monotonic_page_candidates(scan_text) if edition["map_scope"] == "main_pagination" else ([], 0)
        for leaf, page in accepted:
            candidates.append({
                "siglum": edition["siglum"], "archive_id": ident,
                "volume": edition["volume"], "printed_page": page, "leaf": leaf,
                "target_status": "", "scan_url": scan_url(ident, leaf),
                "map_basis": "archive_scandata_monotonic_run_min3",
            })
        receipts["items"].append({
            "siglum": edition["siglum"], "archive_id": ident,
            "metadata_url": meta_url, "metadata_status": status,
            "metadata_sha256": hashlib.sha256(payload).hexdigest(),
            "scandata_url": scan_url_raw, "scandata_status": scan_status,
            "scandata_sha256": hashlib.sha256(scan_payload).hexdigest(),
            "numeric_labels": labelled, "monotonic_labels": len(accepted),
            "title_page_probe": probe_image(ident, 0),
        })
        time.sleep(0.25)
    grouped = collections.defaultdict(list)
    for row in candidates:
        grouped[(row["siglum"], row["volume"], row["printed_page"])].append(row)
    for group in grouped.values():
        status = "unique" if len({r["scan_url"] for r in group}) == 1 else "ambiguous_duplicate"
        for row in group:
            row["target_status"] = status
    candidates.sort(key=lambda r: (r["siglum"], r["volume"], r["printed_page"], r["archive_id"], r["leaf"]))
    write_tsv(PAGE_MAP, MAP_COLUMNS, candidates)
    for ident in sorted({r["archive_id"] for r in candidates if r["target_status"] == "unique"}):
        row = next(r for r in candidates if r["archive_id"] == ident and r["target_status"] == "unique")
        probe = probe_image(ident, row["leaf"])
        probe.update({"siglum": row["siglum"], "printed_page": row["printed_page"]})
        receipts["locus_page_samples"].append(probe)
        time.sleep(0.25)
    with open(PROBES, "w", encoding="utf-8") as fh:
        json.dump(receipts, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(f"Archive refresh: {len(editions)} items, {len(candidates)} mapped page candidates")


def parse_page_locus(locus, scheme):
    """Return (volume, printed_page), or a named syntactic rejection."""
    value = locus.strip().rstrip(".")
    if scheme not in PAGE_SCHEMES:
        return None, None, "non_page_locus_scheme"
    if scheme == "volume_page_line":
        match = re.fullmatch(r"([ivxlcdm]+)(?:\(\d+\))?\.[\s]*(\d+)\.\s*\d+(?:[-–]\d+)?", value)
        if not match:
            if re.fullmatch(r"\d+\.\s*\d+(?:[-–]\d+)?", value):
                return None, None, "missing_volume"
            return None, None, "locus_syntax"
        volume = match.group(1)
        if volume not in ROMAN:
            return None, None, "locus_syntax"
        return volume, int(match.group(2)), "ok"
    match = re.fullmatch(r"(\d+)\.\s*\d+(?:[-–]\d+)?", value)
    if not match:
        return None, None, "locus_syntax"
    return "", int(match.group(1)), "ok"


def live_probe_index():
    with open(PROBES, encoding="utf-8") as fh:
        receipts = json.load(fh)
    return {r["archive_id"]: bool(r["title_page_probe"].get("ok")) for r in receipts["items"]}


def build():
    editions = read_tsv("pd_aob_scan_editions.tsv")
    availability = read_tsv("pd_edition_availability_by_siglum.tsv")
    availability_by_siglum = {r["siglum"]: r for r in availability}
    registry = {r["work_id"]: r for r in read_tsv("pd_work_registry.tsv") if r["work_id"]}
    live_ok = live_probe_index()

    principal_by_work = {}
    for row in editions:
        avail = availability_by_siglum[row["siglum"]]
        work_id = avail["work_id"]
        if not work_id or avail["edition_identity"] != "aob_exact":
            raise ValueError(f"C1 exact-edition identity missing for {row['siglum']}")
        principal_by_work.setdefault(work_id, row["siglum"])
        if principal_by_work[work_id] != row["siglum"]:
            raise ValueError(f"two principal sigla for {work_id}")
    items_by_work = collections.defaultdict(list)
    for row in editions:
        items_by_work[availability_by_siglum[row["siglum"]]["work_id"]].append(row)
    exact_by_siglum = {}
    for row in availability:
        if row["edition_identity"] == "aob_exact" and row["work_id"] in principal_by_work:
            exact_by_siglum[row["siglum"]] = principal_by_work[row["work_id"]]

    edition_map = read_tsv("pd_work_edition_map.tsv")
    index_records = {}
    editions_by_work = collections.defaultdict(list)
    for row in edition_map:
        if row["relation"] == "primary_work" and row["source"] == "pd_index_works":
            index_records[row["source_locator"]] = row
        elif row["relation"] == "edition_of_declared_work":
            editions_by_work[row["work_id"]].append(row["source_locator"])

    page_leaves = {r["printed_page"]: r["leaf"] for r in read_tsv("pd_index_works_by_page.tsv")}
    targets = []
    for index in read_tsv("pd_index_works.tsv"):
        siglum = index["abbreviation_siglum"]
        if not siglum:
            continue
        locator = f"{index['page']}:{index['row']}"
        record = index_records.get(locator, {})
        work_id = record.get("work_id", "")
        aob_ids = sorted(set(editions_by_work.get(work_id, [])))
        principal = principal_by_work.get(work_id, "")
        exact = availability_by_siglum.get(principal, {}) if principal else {}
        urls = [scan_url(r["archive_id"], 0) for r in items_by_work.get(work_id, [])
                if live_ok.get(r["archive_id"])]
        exact_entry_ids = exact.get("aob_entry_ids", "")
        edition_status = "resolved_registry" if aob_ids else ("resolved_c1_exact" if exact_entry_ids else "unresolved")
        targets.append({
            "record_id": record.get("record_id", ""), "work_id": work_id,
            "index_page": index["page"], "index_row": index["row"], "siglum": siglum,
            "title_iast": index["title_iast"],
            "work_identity_status": "resolved" if work_id else "unresolved_structural_siglum",
            "n_aob_editions": len(aob_ids), "aob_edition_ids": ";".join(aob_ids),
            "aob_edition_status": edition_status,
            "exact_siglum": principal, "aob_exact_entry_ids": exact_entry_ids,
            "scan_target_status": "resolved_aob_exact" if urls else "unresolved",
            "scan_urls": " ; ".join(urls),
            "index_scan_url": scan_url(INDEX_ARCHIVE_ID, page_leaves[index["page"]]),
        })
    if len(targets) != 1622:
        raise AssertionError(f"Index siglum population changed: {len(targets)}")

    map_rows = read_tsv("pd_aob_scan_page_map.tsv")
    page_candidates = collections.defaultdict(list)
    for row in map_rows:
        if live_ok.get(row["archive_id"]):
            page_candidates[(row["siglum"], row["volume"], int(row["printed_page"]))].append(row)

    loci = []
    status_counts = collections.Counter()
    for field in read_tsv("pd_locus_fields.tsv"):
        principal = exact_by_siglum.get(field["siglum"])
        if not principal:
            continue
        work_id = availability_by_siglum[field["siglum"]]["work_id"]
        work_items = items_by_work[work_id]
        schemes = {r["locus_scheme"] for r in work_items}
        if len(schemes) != 1:
            raise ValueError(f"conflicting locus schemes for {principal}")
        scheme = next(iter(schemes))
        volume, page, parse_status = parse_page_locus(field["locus"], scheme)
        rec = {key: "" for key in LOCUS_COLUMNS}
        rec.update({key: field[key] for key in ("locus_id", "siglum", "locus", "kind")})
        rec.update({"principal_siglum": principal, "work_id": work_id})
        if parse_status == "non_page_locus_scheme":
            rec.update(resolution_status="unresolved", reason=parse_status)
        elif parse_status == "missing_volume":
            rec.update(resolution_status="unresolved", reason=parse_status)
        elif parse_status != "ok":
            rec.update(resolution_status="unresolved", reason=parse_status)
        elif volume not in {r["volume"] for r in work_items}:
            rec.update(resolution_status="unresolved", reason="volume_not_scanned")
        else:
            candidates = page_candidates.get((principal, volume, page), [])
            unique = [r for r in candidates if r["target_status"] == "unique"]
            if unique:
                chosen = unique[0]
                rec.update(resolution_status="resolved", archive_id=chosen["archive_id"],
                           printed_page=page, scan_url=chosen["scan_url"], reason="printed_page_unique")
            elif candidates:
                rec.update(resolution_status="unresolved", reason="ambiguous_duplicate_page")
            else:
                rec.update(resolution_status="unresolved", reason="printed_page_not_mapped")
        status_counts[rec["reason"]] += 1
        loci.append(rec)

    total_c2 = sum(1 for _ in read_tsv("pd_locus_fields.tsv"))
    resolved_loci = sum(r["resolution_status"] == "resolved" for r in loci)
    work_resolved = sum(r["work_identity_status"] == "resolved" for r in targets)
    edition_resolved = sum(r["aob_edition_status"] != "unresolved" for r in targets)
    scan_resolved = sum(r["scan_target_status"] == "resolved_aob_exact" for r in targets)
    by_siglum = collections.defaultdict(lambda: {"aob_exact": 0, "resolved": 0})
    for row in loci:
        by_siglum[row["principal_siglum"]]["aob_exact"] += 1
        by_siglum[row["principal_siglum"]]["resolved"] += row["resolution_status"] == "resolved"
    summary = {
        "license": "CC-BY-SA-4.0",
        "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0/",
        "dataset": "pd_aob_scan_links_c3",
        "generated_by": "python scripts/pd_aob_scan_links.py",
        "generated_on": "2026-10-30",
        "protocol": {
            "work_identity": "H7296 primary_work record for each printed Index row; structural sigla stay unresolved",
            "edition_identity": "H7296 edition_of_declared_work records, or C1's explicit aob_exact entry where the conservative registry has no edge; never inferred from work-level availability",
            "scan_target": "C1 aob_exact Archive.org witness with a live page/n0.jpg probe; item details URLs are not scan targets",
            "locus_resolution": "C2 pair + AOB page-bearing locus scheme + unique printed-page label in a monotonic Archive.org scandata run",
            "duplicate_rule": "repeated printed-page labels in different parts remain ambiguous",
            "unknown_rule": "missing edition, missing scan, non-page locus and unmapped page are distinct unresolved classes, never absence verdicts",
        },
        "evidenceLevels": {
            "identity_and_aggregates": "derived", "archive_probes": "observed",
            "page_map": "derived_from_archive_scandata", "human_review": "none",
        },
        "index": {
            "siglum_rows": len(targets), "work_identity_resolved": work_resolved,
            "work_identity_pct": round(100 * work_resolved / len(targets), 4),
            "aob_edition_identity_resolved": edition_resolved,
            "aob_edition_identity_pct": round(100 * edition_resolved / len(targets), 4),
            "aob_edition_identity_by_source": dict(sorted(collections.Counter(r["aob_edition_status"] for r in targets).items())),
            "aob_exact_scan_targets": scan_resolved,
            "aob_exact_scan_targets_pct": round(100 * scan_resolved / len(targets), 4),
            "aob_exact_scan_works": len({r["work_id"] for r in targets if r["scan_target_status"] == "resolved_aob_exact"}),
            "index_scan_targets": sum(bool(r["index_scan_url"]) for r in targets),
        },
        "loci": {
            "c2_total": total_c2, "aob_exact": len(loci),
            "aob_exact_pct_of_c2": round(100 * len(loci) / total_c2, 4),
            "resolved_scan_pages": resolved_loci,
            "resolved_pct_of_aob_exact": round(100 * resolved_loci / len(loci), 4) if loci else 0,
            "resolved_pct_of_all_c2": round(100 * resolved_loci / total_c2, 4),
            "by_reason": dict(sorted(status_counts.items())),
            "by_siglum": dict(sorted(by_siglum.items())),
        },
        "archive": {
            "edition_items": len(editions), "live_title_page_targets": sum(live_ok.values()),
            "page_candidates": len(map_rows),
            "unique_page_candidates": sum(r["target_status"] == "unique" for r in map_rows),
            "ambiguous_page_candidates": sum(r["target_status"] == "ambiguous_duplicate" for r in map_rows),
        },
        "inputs": {name: sha256(os.path.join(DATA, name)) for name in (
            "pd_aob_scan_editions.tsv", "pd_aob_scan_page_map.tsv",
            "pd_aob_scan_probes_2026-10-30.json", "pd_edition_availability_by_siglum.tsv",
            "pd_work_registry.tsv", "pd_work_edition_map.tsv", "pd_index_works.tsv",
            "pd_index_works_by_page.tsv", "pd_locus_fields.tsv",
        )},
        "warnings": [
            "Index scan URLs locate the printed siglum row, not the cited AOB edition; they are reported separately",
            "AOB-exact scan coverage is a lower bound bounded by C1's curated exact-edition evidence",
            "A resolved locus is a printed-page image target, not a quotation-fidelity or line-level verification",
            "Work identity and edition identity inherit H7296's unvalidated_pending_double_annotation status",
        ],
    }
    return targets, loci, summary


def compare_tsv(path, columns, expected):
    problems = []
    with open(path, encoding="utf-8", newline="") as fh:
        actual = list(csv.DictReader(fh, delimiter="\t"))
    normalized = [{c: str(row.get(c, "")) for c in columns} for row in expected]
    if actual != normalized:
        problems.append(os.path.basename(path) + " differs from rebuilt rows")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fetch-archive", action="store_true", help="refresh page map and live receipts from Archive.org")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    if args.fetch_archive:
        fetch_archive()
    targets, loci, summary = build()
    if args.check:
        problems = []
        problems += compare_tsv(OUT_TARGETS, TARGET_COLUMNS, targets)
        problems += compare_tsv(OUT_LOCI, LOCUS_COLUMNS, loci)
        with open(OUT_JSON, encoding="utf-8") as fh:
            if json.load(fh) != summary:
                problems.append("JSON summary differs from rebuilt summary")
        if os.path.exists(REPORT):
            with open(REPORT, encoding="utf-8") as fh:
                report = fh.read()
            i = summary["index"]
            l = summary["loci"]
            needles = [
                f"{i['work_identity_resolved']:,} / 1,622", f"{i['aob_edition_identity_resolved']:,} / 1,622",
                f"{i['aob_exact_scan_targets']:,} / 1,622", f"{l['aob_exact']:,}",
                f"{l['resolved_scan_pages']:,}", f"{l['resolved_pct_of_aob_exact']:.2f} %",
            ]
            problems += [f"report missing {needle}" for needle in needles if needle not in report]
        else:
            problems.append("report missing")
        if problems:
            for problem in problems:
                print("FAIL", problem)
            return 1
        i, l = summary["index"], summary["loci"]
        print(f"PASS C3 Index work {i['work_identity_resolved']}/1,622; edition {i['aob_edition_identity_resolved']}/1,622; "
              f"scan {i['aob_exact_scan_targets']}/1,622; loci {l['resolved_scan_pages']}/{l['aob_exact']} "
              f"= {l['resolved_pct_of_aob_exact']:.2f}% AOB-exact")
        return 0
    write_tsv(OUT_TARGETS, TARGET_COLUMNS, targets)
    write_tsv(OUT_LOCI, LOCUS_COLUMNS, loci)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    i, l = summary["index"], summary["loci"]
    print(f"C3 Index work {i['work_identity_resolved']}/1,622; edition {i['aob_edition_identity_resolved']}/1,622; "
          f"scan {i['aob_exact_scan_targets']}/1,622; loci {l['resolved_scan_pages']}/{l['aob_exact']} "
          f"= {l['resolved_pct_of_aob_exact']:.2f}% AOB-exact")
    return 0


if __name__ == "__main__":
    sys.exit(main())
