#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H5303 — the dataset-licence envelope gate (fail-closed).

Every ``data/**/*.json`` envelope (a JSON file whose root is an object) must
declare a top-level licence key whose value matches the family's row in
``docs/DATASET_LICENCE_MATRIX.md`` (H5302):

  * ``data/schema/**``   -> ``CC-BY-4.0``  (matrix row 12: own JSON Schemas,
        no dictionary content — the one genuinely clean family);
  * everything else      -> ``CC-BY-SA-4.0`` (repo ``LICENSE`` default; the
        csl-orig-derived families inherit ShareAlike).

Excluded from the gate:

  * ``*.source.json`` provenance sidecars — they carry their own licence
    block and are not envelopes;
  * files whose JSON root is not an object (a bare array or primitive is
    not an envelope and cannot carry a top-level key; currently exactly one:
    ``data/L0/dim_schema.json``, an input schema consumed by the ``s2*.py``
    scripts).

The expected values are re-derived from ``scripts/lib/dataset_meta.py`` —
the same single source of truth the builders import — so the gate, the
backfill sweep (``scripts/backfill_dataset_licences.py``) and every
generator emit the same bytes.

Usage:
  python3 scripts/validate_dataset_licences.py            # gate: whole data/
  python3 scripts/validate_dataset_licences.py --file P   # validate one file

Exit codes: 0 every envelope licensed / 1 violation (missing or wrong value).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
from dataset_meta import (  # noqa: E402
    DATASET_LICENSE, DATASET_LICENSE_URL,
    SCHEMA_LICENSE, SCHEMA_LICENSE_URL,
)

KEYS = ("license", "licence")
DATA = ROOT / "data"


def expected_for(path: Path) -> tuple[str, str]:
    """(licence, licenceUrl) a file at ``path`` must declare, per the matrix."""
    parts = path.resolve().parts
    if "data" in parts and "schema" in parts[parts.index("data") + 1:]:
        # only the direct data/schema family, not e.g. a nested 'schemas' dir
        rel = Path(*parts[parts.index("data") + 1:])
        if rel.parts[0] == "schema":
            return SCHEMA_LICENSE, SCHEMA_LICENSE_URL
    return DATASET_LICENSE, DATASET_LICENSE_URL


def declared_licence(obj) -> str | None:
    if not isinstance(obj, dict):
        return None
    for key in KEYS:
        value = obj.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return None


def check_file(path: Path) -> tuple[str, str | None]:
    """Return (status, message); status is "ok", "non-envelope" or "violation"."""
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return "violation", f"unparseable JSON ({exc})"
    if not isinstance(obj, dict):
        return "non-envelope", None  # bare array/primitive; cannot carry a key
    value = declared_licence(obj)
    expected, _ = expected_for(path)
    if value is None:
        return "violation", "missing top-level licence key"
    if value != expected:
        return "violation", f"licence {value!r} != matrix value {expected!r}"
    return "ok", None


def scan():
    violations, non_envelopes = [], []
    for path in sorted(DATA.rglob("*.json")):
        if path.name.endswith(".source.json"):
            continue
        status, message = check_file(path)
        if status == "violation":
            violations.append((path, message))
        elif status == "non-envelope":
            non_envelopes.append(path)
    return violations, non_envelopes


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--file", type=Path, default=None,
                    help="validate a single file instead of the whole data/ tree")
    args = ap.parse_args(argv)

    if args.file is not None:
        status, message = check_file(args.file)
        if status in ("ok", "non-envelope"):
            print(f"licence gate: {args.file} OK"
                  + (" (non-envelope, excluded)" if status == "non-envelope" else ""))
            return 0
        print(f"[FAIL] {args.file}: {message}", file=sys.stderr)
        return 1

    violations, non_envelopes = scan()
    for path, problem in violations:
        print(f"[FAIL] {path.relative_to(ROOT)}: {problem}", file=sys.stderr)
    for path in non_envelopes:
        print(f"[note] {path.relative_to(ROOT)}: root is not an object — "
              f"not an envelope, excluded from the licence gate")
    total = sum(1 for p in DATA.rglob("*.json") if not p.name.endswith(".source.json"))
    licensed = total - len(violations) - len(non_envelopes)
    print(f"licence gate: {licensed}/{total} data JSON envelopes carry the "
          f"matrix licence ({len(non_envelopes)} non-envelope file(s) excluded)")
    if violations:
        print(f"licence gate: {len(violations)} violation(s)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
