#!/usr/bin/env python3
"""Archive.org image probes and conservative scandata labels for PD C3."""
from __future__ import annotations

import csv
import os
import re
import time
import urllib.request
import xml.etree.ElementTree as ET

DEVANAGARI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")


def scan_url(archive_id, leaf):
    return f"https://archive.org/download/{archive_id}/page/n{leaf}.jpg"


def fetch_bytes(url, timeout=90):
    req = urllib.request.Request(url, headers={"User-Agent": "csl-atlas-PD-C3/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read(), response.status, response.headers.get("Content-Type", "")


def probe_image(archive_id, leaf):
    url = scan_url(archive_id, leaf)
    last = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "csl-atlas-PD-C3/1.0", "Range": "bytes=0-31"})
            with urllib.request.urlopen(req, timeout=90) as response:
                payload = response.read(32)
                return {
                    "url": url, "status": response.status,
                    "content_type": response.headers.get("Content-Type", ""),
                    "bytes_read": len(payload), "ok": response.status in {200, 206} and bool(payload),
                }
        except Exception as exc:  # receipts retain the failure; no silent success
            last = repr(exc)
            if "429" not in last:
                break
            time.sleep(2 * (attempt + 1))
    return {"url": url, "status": 0, "content_type": "", "bytes_read": 0,
            "ok": False, "error": last}


def numeric_page(value):
    value = value.strip().translate(DEVANAGARI_DIGITS)
    return int(value) if re.fullmatch(r"\d+", value) else None


def monotonic_page_candidates(scandata):
    """Accept only printed-page labels inside >=3-page +1 runs.

    Isolated OCR labels and non-monotonic tails are rejected. Duplicate labels
    across valid runs remain visible for the caller to mark ambiguous.
    """
    root = ET.fromstring(scandata)
    labelled = []
    for page in root.findall(".//pageData/page"):
        if page.findtext("pageType", "").strip() != "Normal":
            continue
        number = numeric_page(page.findtext("pageNumber", ""))
        if number is not None:
            labelled.append((int(page.attrib["leafNum"]), number))
    accepted = []
    run = []
    for item in labelled:
        if run and item[1] != run[-1][1] + 1:
            if len(run) >= 3:
                accepted.extend(run)
            run = []
        run.append(item)
    if len(run) >= 3:
        accepted.extend(run)
    return accepted, len(labelled)


def visual_range_candidates(ranges):
    """Expand only visually anchored ranges; two-page scans use page_step=2."""
    candidates = []
    for row in ranges:
        first_leaf = int(row["leaf_first"])
        for leaf in range(first_leaf, int(row["leaf_last"]) + 1):
            page = int(row["printed_page_first"]) + (leaf - first_leaf) * int(row["printed_page_step"])
            candidates.append({
                "siglum": row["siglum"], "archive_id": row["archive_id"],
                "volume": row["volume"], "printed_page": page, "leaf": leaf,
                "target_status": "", "scan_url": scan_url(row["archive_id"], leaf),
                "map_basis": row["map_basis"],
            })
    return candidates


def compare_tsv(path, columns, expected):
    with open(path, encoding="utf-8", newline="") as fh:
        actual = list(csv.DictReader(fh, delimiter="\t"))
    normalized = [{c: str(row.get(c, "")) for c in columns} for row in expected]
    return [] if actual == normalized else [os.path.basename(path) + " differs from rebuilt rows"]
