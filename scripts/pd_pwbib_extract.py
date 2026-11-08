#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract dictionary-specific siglum tables from the PW / PWG bibliographies.

H7296.  The shared PD work registry consumes `pwgbib.txt` and `pwbib.txt` as the
PWG-side and PW-side members of a cross-dictionary siglum map.  Those files live
in the `literarysource` repository, not here, so this extractor turns them into
two small, pinned TSVs:

    data/pd/pd_pwgbib_sigla.tsv
    data/pd/pd_pwbib_sigla.tsv

The reference string is copied verbatim from the bibliography (everything after
the first `=`) — the registry never shortens, translates or invents a title.  The
raw files are not committed; their sha256 is recorded by the registry builder in
`data/pd/pd_work_registry_diagnostics.json` through the derived TSVs' own bytes.

Usage:
  python3 scripts/pd_pwbib_extract.py --pwgbib PATH --pwbib PATH --write
  python3 scripts/pd_pwbib_extract.py --pwgbib PATH --pwbib PATH --check
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = {
    "pwg": os.path.join(ROOT, "data", "pd", "pd_pwgbib_sigla.tsv"),
    "pw": os.path.join(ROOT, "data", "pd", "pd_pwbib_sigla.tsv"),
}
FIELDS = ["siglum", "reference", "source_line"]
ROMAN = {"i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"}


def read_tsv(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def parse_line(line):
    """Return (siglum tokens, verbatim reference) for one <HI ...> line."""
    m = re.search(r'iast="([^"]*)"', line)
    if not m:
        return [], ""
    tokens = []
    for tok in re.split(r"\s+", m.group(1).strip()):
        tok = tok.strip()
        if not tok or tok.lower() in ROMAN:
            continue
        if tok[0] in "(&[{" or not re.search(r"[A-Za-z\u00c0-\u024f]", tok):
            continue
        if len(tok) > 40:
            continue
        tokens.append(tok)
    rest = line[m.end():]
    ref = rest.split("=", 1)[1].strip() if "=" in rest else rest.strip()
    return tokens, ref


def extract(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = fh.read().splitlines()
    rows, seen = [], set()
    for lineno, line in enumerate(lines, 1):
        if "<HI" not in line:
            continue
        tokens, ref = parse_line(line)
        for tok in tokens:
            key = tok
            if key in seen:
                continue
            seen.add(key)
            rows.append({"siglum": tok, "reference": ref, "source_line": str(lineno)})
    return rows


def render(rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pwgbib", required=True)
    ap.add_argument("--pwbib", required=True)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    payload = {
        "pwg": render(extract(args.pwgbib)),
        "pw": render(extract(args.pwbib)),
    }
    rc = 0
    for key, text in payload.items():
        path = OUT[key]
        if args.check:
            with open(path, encoding="utf-8", newline="") as fh:
                on_disk = fh.read()
            if on_disk != text:
                print(f"CHECK FAIL: {path} differs from the bibliography extract", file=sys.stderr)
                rc = 1
            else:
                print(f"OK {os.path.relpath(path, ROOT)}: {len(text.splitlines()) - 1} rows")
        else:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(text)
            print(f"wrote {os.path.relpath(path, ROOT)}: {len(text.splitlines()) - 1} rows")
    return rc


if __name__ == "__main__":
    sys.exit(main())
