#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7463 — parse the DCS corpus catalogue snapshot into a TSV.

Input : data/pwg_dcs/dcs_corpus_catalogue_<date>.html (the live page
        https://www.sanskrit-linguistics.org/dcs/index.php?contents=corpus,
        fetched and committed verbatim for sha-pinning).
Output: data/pwg_dcs/dcs_catalogue_<date>.tsv — one row per text:
        title, author, period, genre, text_id.

    python scripts/dcs_catalogue_parse.py [--html PATH] [--out PATH]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN_DIR = os.path.join(ROOT, "data", "pwg_dcs")

RE_ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
RE_TD = re.compile(r"<td[^>]*>(.*?)</td>", re.S)
RE_ID = re.compile(r"IDTextDisplay=(\d+)")


def clean(td: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", td)).replace("&nbsp;", " ").strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--html", default=os.path.join(
        IN_DIR, "dcs_corpus_catalogue_2026-10-30.html"))
    ap.add_argument("--out", default=os.path.join(
        IN_DIR, "dcs_catalogue_2026-10-30.tsv"))
    args = ap.parse_args()

    html = open(args.html, encoding="utf-8").read()
    rows = []
    for row in RE_ROW.findall(html):
        if "IDTextDisplay" not in row:
            continue
        tds = [clean(td) for td in RE_TD.findall(row)]
        mid = RE_ID.search(row)
        if len(tds) >= 4 and mid:
            title, author, period, genre = tds[0], tds[1], tds[2], tds[3]
            rows.append((title, author, period, genre, mid.group(1)))

    with open(args.out, "w", encoding="utf-8") as out:
        out.write("title\tauthor\tperiod\tgenre\ttext_id\n")
        for r in rows:
            out.write("\t".join(r) + "\n")

    sha = hashlib.sha256(open(args.html, "rb").read()).hexdigest()
    json.dump({"html_sha256": sha, "rows": len(rows), "html_bytes": os.path.getsize(args.html)},
              open(os.path.join(IN_DIR, "dcs_catalogue_pins.json"), "w", encoding="utf-8"),
              indent=2, sort_keys=True)
    print(f"rows={len(rows)} sha={sha[:16]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
