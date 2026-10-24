#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H5303 — backfill the matrix licence into every data JSON envelope.

The one-time sweep behind the H5303 PR. Rules:

  * the licence values come from ``scripts/lib/dataset_meta.py`` — the same
    canonical source the builders import — never typed by hand;
  * ``data/schema/**`` gets the clean-family value (matrix row 12,
    ``CC-BY-4.0``), everything else the repo default ``CC-BY-SA-4.0``;
  * pretty-printed files are edited by pure text insertion: two lines after
    the first-level ``schemaVersion`` key (or right after the opening brace
    when there is none), so every existing byte of the file is preserved —
    no re-serialization, no diff churn;
  * minified files (single line) are re-serialized compact with the licence
    pair inserted at the front, preserving key order;
  * ``*.source.json`` sidecars and files whose root is not an object are
    skipped (not envelopes);
  * idempotent: a file already carrying the expected licence is left
    untouched.

Run after wiring a generator, never instead of it:
  python3 scripts/backfill_dataset_licences.py

Exit codes: 0 ok / 1 something could not be stamped.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
from dataset_meta import (  # noqa: E402
    DATASET_LICENSE, DATASET_LICENSE_URL,
    SCHEMA_LICENSE, SCHEMA_LICENSE_URL,
)

DATA = ROOT / "data"
KEYS = ("license", "licence")


def expected_fields(path: Path) -> dict:
    parts = path.resolve().parts
    if "data" in parts:
        rel = Path(*parts[parts.index("data") + 1:])
        if rel.parts and rel.parts[0] == "schema":
            return {"license": SCHEMA_LICENSE, "licenseUrl": SCHEMA_LICENSE_URL}
    return {"license": DATASET_LICENSE, "licenseUrl": DATASET_LICENSE_URL}


def has_licence(obj) -> str | None:
    if not isinstance(obj, dict):
        return None
    for key in KEYS:
        value = obj.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return None


def stamp_pretty(text: str, fields: dict) -> str | None:
    """Insert two lines into a pretty-printed JSON object. None = not applicable."""
    lines = text.splitlines(keepends=True)
    if not lines or not lines[0].strip() == "{":
        return None
    # first-level indent = the indent of line 1 (first key line)
    m = re.match(r"([ \t]*)", lines[1]) if len(lines) > 1 else None
    indent = m.group(1) if m else "  "
    pair = [f'{indent}"license": {json.dumps(fields["license"], ensure_ascii=False)},\n',
            f'{indent}"licenseUrl": {json.dumps(fields["licenseUrl"], ensure_ascii=False)},\n']
    # find the first-level "schemaVersion": line, else insert right after "{"
    target = 0
    for i in range(1, len(lines)):
        if re.match(rf"^{re.escape(indent)}\"", lines[i]):
            if lines[i].startswith(f'{indent}"schemaVersion"'):
                target = i
            break
    lines[target + 1:target + 1] = pair
    return "".join(lines)


def stamp_minified(text: str, obj: dict, fields: dict) -> str:
    ensure_ascii = all(
        ord(c) < 128 or f"\\u{ord(c):04x}" in text or f"\\U{ord(c):08x}" in text
        for c in set(text) if ord(c) > 127)
    out = {}
    out.update(fields)
    out.update(obj)
    trailing = "\n" if text.endswith("\n") else ""
    return json.dumps(out, ensure_ascii=ensure_ascii,
                      separators=(",", ":")) + trailing


def main() -> int:
    stamped = already = skipped = 0
    failures = []
    for path in sorted(DATA.rglob("*.json")):
        if path.name.endswith(".source.json"):
            continue
        text = path.read_text(encoding="utf-8")
        try:
            obj = json.loads(text)
        except ValueError as exc:
            failures.append(f"{path.relative_to(ROOT)}: unparseable ({exc})")
            continue
        if not isinstance(obj, dict):
            skipped += 1
            continue
        current = has_licence(obj)
        fields = expected_fields(path)
        if current == fields["license"]:
            already += 1
            continue
        if current is not None and current != fields["license"]:
            failures.append(f"{path.relative_to(ROOT)}: declares {current!r}, "
                            f"matrix says {fields['license']!r} — fix the source, "
                            f"not this sweep")
            continue
        if "\n" in text.strip():
            new_text = stamp_pretty(text, fields)
            if new_text is None:
                failures.append(f"{path.relative_to(ROOT)}: unexpected pretty shape")
                continue
        else:
            new_text = stamp_minified(text, obj, fields)
        if json.loads(new_text) != {**fields, **obj} and json.loads(new_text) != obj:
            failures.append(f"{path.relative_to(ROOT)}: post-stamp parse mismatch")
            continue
        path.write_text(new_text, encoding="utf-8")
        stamped += 1
    print(f"licence backfill: {stamped} stamped, {already} already licensed, "
          f"{skipped} non-envelope file(s) skipped")
    for failure in failures:
        print(f"[FAIL] {failure}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
