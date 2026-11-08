#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H5303 (G6) — backfill the licence stamp into data JSON envelopes.

Adds the matrix licence (``license`` + ``licenseUrl``, docs/DATASET_LICENCE_MATRIX.md)
to every ``data/**.json`` envelope that lacks it. The stamp is spliced into the
existing bytes (inserted as the first key, mirroring the shared envelope order
``schemaVersion, license, licenseUrl, …`` from scripts/lib/dataset-meta.mjs
``licenseFields()``), so nothing else in the file moves: no re-serialisation,
no float re-formatting, no key reordering. Idempotent and deterministic —
re-running it on a stamped tree is a no-op.

This is the generator for the licence stamp, not a hand edit: the committed
script is the reproducible way the stamp was produced, mirroring the
licence contract that ``licenseFields()`` already imposes on every new builder.

Run:
  python3 scripts/backfill_dataset_licences.py           # splice (prints actions)
  python3 scripts/backfill_dataset_licences.py --check   # exit 1 if anything unstamped

Exit codes: 0 ok / 1 would-change or error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
KEYS = ("license", "licence")
FAMILY_LICENCES = {
    "schema": ("CC-BY-4.0", "https://creativecommons.org/licenses/by/4.0/"),
}
DEFAULT_LICENCE = ("CC-BY-SA-4.0", "https://creativecommons.org/licenses/by-sa/4.0/")


def licence_for(rel_parts):
    family = rel_parts[0] if len(rel_parts) > 1 else "(root)"
    return FAMILY_LICENCES.get(family, DEFAULT_LICENCE)


def apply_stamp(text, license_value, license_url):
    """Return text with license/licenseUrl inserted as the first top-level keys."""
    start = text.index("{")
    first_quote = text.find('"', start + 1)
    if first_quote == -1:  # empty object — nothing to stamp before
        raise ValueError("no top-level key found")
    pretty = "\n" in text[start + 1:first_quote]
    stamp = json.dumps(license_value), json.dumps(license_url)
    if not pretty:  # compact, single-line JSON (JS JSON.stringify style)
        return (text[:start + 1]
                + f'"license":{stamp[0]},"licenseUrl":{stamp[1]},'
                + text[start + 1:])
    line_start = text.rfind("\n", 0, first_quote) + 1
    indent = text[line_start:first_quote]
    return (text[:line_start]
            + f'{indent}"license": {stamp[0]},\n'
            + f'{indent}"licenseUrl": {stamp[1]},\n'
            + text[line_start:])


def backfill_tree(check_only=False):
    actions = []
    for path in sorted(DATA.rglob("*.json")):
        if path.name.endswith(".source.json"):
            continue
        raw = path.read_text(encoding="utf-8")
        try:
            obj = json.loads(raw)
        except (OSError, ValueError):
            actions.append((Path(path).relative_to(DATA), "SKIP unparsable"))
            continue
        if not isinstance(obj, dict):  # a bare array is not an envelope
            actions.append((Path(path).relative_to(DATA), "SKIP non-envelope"))
            continue
        if any(isinstance(obj.get(k), str) for k in KEYS):
            continue
        parts = Path(path).relative_to(DATA).parts
        want_license, want_url = licence_for(parts)
        if check_only:
            actions.append((Path(path).relative_to(DATA), "WOULD-STAMP"))
            continue
        rel = Path(path).relative_to(DATA)
        try:
            stamped = apply_stamp(raw, want_license, want_url)
            reparsed = json.loads(stamped)
        except (OSError, ValueError) as exc:
            actions.append((rel, f"SKIP stamp failed ({exc})"))
            continue
        # the splice must be semantically identical apart from the two new keys
        assert _equal_modulo_licence(reparsed, obj), rel
        path.write_text(stamped, encoding="utf-8")
        actions.append((rel, f"STAMPED {want_license}"))
    return actions


def _equal_modulo_licence(new, old):
    stripped = {k: v for k, v in new.items() if k not in ("license", "licence", "licenseUrl")}
    return stripped == old


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="report what would be stamped without writing")
    args = parser.parse_args()
    actions = backfill_tree(check_only=args.check)
    stamped = [a for a in actions if a[1].startswith(("STAMPED", "WOULD-STAMP"))]
    for rel, action in actions:
        print(f"{rel} -> {action}")
    print(f"{'would stamp' if args.check else 'stamped'}: {len(stamped)}")
    return 1 if (stamped and args.check) else 0


if __name__ == "__main__":
    raise SystemExit(main())