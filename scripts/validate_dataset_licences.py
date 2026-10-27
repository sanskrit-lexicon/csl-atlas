#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H5303 (G6) — every data JSON envelope must declare its licence.

Per docs/DATASET_LICENCE_MATRIX.md: envelopes under ``data/`` must carry a
top-level ``license`` (or ``licence``) string; ``data/schema/`` is the one
clean family (CC BY 4.0), everything else inherits the repo-wide
CC BY-SA 4.0. Fails (exit 1) on a missing key, a value that contradicts the
matrix, or a ``licenseUrl`` that does not match the license. ``*.source.json``
provenance sidecars and non-envelope (top-level array) files are counted
separately, not gated — an array cannot carry top-level keys.

Run:
  python3 scripts/validate_dataset_licences.py            # gate over data/
  python3 scripts/validate_dataset_licences.py --selftest # fixture check

Exit codes: 0 pass / 1 violation / 2 selftest failure.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
KEYS = ("license", "licence")

#: family (first directory under data/) -> permitted (license, licenseUrl)
FAMILY_LICENCES = {
    "schema": ("CC-BY-4.0", "https://creativecommons.org/licenses/by/4.0/"),
}
DEFAULT_LICENCE = ("CC-BY-SA-4.0", "https://creativecommons.org/licenses/by-sa/4.0/")


def expected_for(rel_parts):
    family = rel_parts[0] if len(rel_parts) > 1 else "(root)"
    return FAMILY_LICENCES.get(family, DEFAULT_LICENCE)


def check_tree(data_dir=DATA):
    """Return (failures, n_envelopes, n_declared, n_sidecars, n_non_envelope)."""
    data_dir = Path(data_dir)
    failures = []
    n_env = declared = n_sidecar = n_other = 0
    for path in sorted(data_dir.rglob("*.json")):
        if path.name.endswith(".source.json"):
            n_sidecar += 1
            continue
        rel = str(path.relative_to(data_dir))
        parts = Path(rel).parts
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            failures.append(f"{rel}: unreadable/invalid JSON ({exc})")
            n_env += 1
            continue
        if not isinstance(obj, dict):
            n_other += 1
            continue
        n_env += 1
        license_value = value_url = None
        for key in KEYS:
            if isinstance(obj.get(key), str):
                license_value = obj[key]
                break
        if not license_value:
            failures.append(f"{rel}: data envelope declares no licence key")
            continue
        declared += 1
        want_license, want_url = expected_for(parts)
        if license_value != want_license:
            failures.append(
                f"{rel}: declares {license_value} but the matrix proposes {want_license}")
        url_value = obj.get("licenseUrl")
        if url_value is not None and url_value != want_url:
            failures.append(f"{rel}: licenseUrl {url_value} does not match {want_url}")
    return failures, n_env, declared, n_sidecar, n_other


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true",
                        help="check gate fixtures (with/without the key) instead of data/")
    args = parser.parse_args()

    if args.selftest:
        ok = _selftest()
        return 0 if ok else 2

    failures, n_env, declared, n_sidecar, n_other = check_tree(DATA)
    print(f"data JSON envelopes: {n_env} (sidecars {n_sidecar}, non-envelope arrays {n_other})")
    print(f"declaring a matrix-valid licence key: {declared}")
    for line in failures:
        print(f"FAIL {line}")
    if failures:
        print(f"validate_dataset_licences: RED — {len(failures)} violation(s)")
        return 1
    print("validate_dataset_licences: PASS")
    return 0


def _selftest() -> bool:
    """The gate must PASS a fixture that declares the key and FAIL one without."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        good = tmp_path / "with-key.json"
        bad = tmp_path / "without-key.json"
        good.write_text(json.dumps({"schemaVersion": "1.0.0", "license": "CC-BY-SA-4.0",
                                    "licenseUrl": DEFAULT_LICENCE[1], "note": "fixture"},
                                   indent=2), encoding="utf-8")
        bad.write_text(json.dumps({"schemaVersion": "1.0.0", "note": "fixture"}, indent=2),
                       encoding="utf-8")
        failures, n_env, declared, _, _ = check_tree(tmp_path)
        ok = (n_env == 2 and declared == 1
              and len(failures) == 1 and "without-key.json" in failures[0]
              and "no licence key" in failures[0])
        print(f"SELFTEST {'PASS' if ok else 'FAIL'} — "
              f"fixture with key declared, fixture without key rejected: {failures}")
        return ok


if __name__ == "__main__":
    raise SystemExit(main())