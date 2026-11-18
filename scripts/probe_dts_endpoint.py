#!/usr/bin/env python3
# coding: utf-8
"""Probe a Distributed Text Services (DTS) endpoint / Collection document.

H8428 — the estate has no live DTS endpoint (H8426 scorecard). This probe is
the conformance check the adoption move owes: it validates the DTS Collection
shape offline against our generated manifest, and can probe a live endpoint
with --url. It never writes to a remote service and makes no network call in
the default (offline) mode.

Usage:
  python scripts/probe_dts_endpoint.py --selftest
  python scripts/probe_dts_endpoint.py --offline
  python scripts/probe_dts_endpoint.py --url https://example.org/dts/api/collection
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "data/tei_dts/ap-dts-manifest.json"
RECEIPT = ROOT / "data/tei_dts/dts_probe_receipt.json"
SCHEMA_VERSION = "1.0.0"
DTS_NS = "distributed-text-services"


def validate_collection(doc: object) -> tuple[bool, list[str]]:
    """Return (ok, errors) for a DTS Collection document."""
    errors: list[str] = []
    if not isinstance(doc, dict):
        return False, ["document is not a JSON object"]
    ctx = doc.get("@context")
    if not isinstance(ctx, (str, list)) or DTS_NS not in json.dumps(ctx):
        errors.append("missing DTS @context")
    structure = doc.get("citeStructure")
    if not isinstance(structure, list) or not structure:
        errors.append("missing citeStructure")
    else:
        stack = list(structure)
        seen = 0
        while stack:
            node = stack.pop()
            seen += 1
            if not isinstance(node, dict):
                errors.append("citeStructure node is not an object")
                continue
            if not node.get("citeType") or not node.get("use"):
                errors.append("citeStructure node lacks citeType/use")
            children = node.get("citeStructure")
            if children:
                if not isinstance(children, list):
                    errors.append("nested citeStructure is not a list")
                else:
                    stack.extend(children)
            if seen > 200:
                errors.append("citeStructure too deep / cyclic")
                break
    dts = doc.get("dts")
    if not isinstance(dts, dict) or DTS_NS not in str(dts.get("conformsTo", "")):
        errors.append("missing dts.conformsTo")
    return (len(errors) == 0), errors


def fetch(url: str, timeout: int = 10) -> object:
    req = urllib.request.Request(url, headers={"Accept": "application/ld+json, application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def receipt(mode: str, target: str, ok: bool, errors: list[str]) -> str:
    doc = {
        "schemaVersion": SCHEMA_VERSION,
        "handoff": "H8428",
        "mode": mode,
        "target": target,
        "conforms": ok,
        "errors": errors,
        "verdict": "PASS" if ok else "FAIL",
        "note": (
            "offline: validates the committed DTS Collection manifest; "
            "live: GETs the endpoint. No estate DTS endpoint exists as of 18-11-2026."
        ),
    }
    return json.dumps(doc, ensure_ascii=False, indent=2) + "\n"


def run(mode: str, url: str | None, write: bool) -> int:
    if mode == "offline":
        target = str(MANIFEST.relative_to(ROOT))
        try:
            doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            ok, errors = False, [f"cannot read manifest: {exc}"]
        else:
            ok, errors = validate_collection(doc)
    else:
        if not url:
            print("--url is required in live mode", file=sys.stderr)
            return 2
        target = url
        try:
            doc = fetch(url)
        except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
            ok, errors = False, [f"fetch failed: {exc}"]
        else:
            ok, errors = validate_collection(doc)
    text = receipt(mode, target, ok, errors)
    if write:
        RECEIPT.write_text(text, encoding="utf-8")
    print(text.strip())
    return 0 if ok else 1


def selftest() -> int:
    good = json.loads(MANIFEST.read_text(encoding="utf-8"))
    bad = dict(good)
    bad["citeStructure"] = [{"citeType": "pb"}]  # missing `use`
    results = [
        ("positive: generated DTS manifest conforms", validate_collection(good)[0]),
        ("negative: missing `use` is refused", not validate_collection(bad)[0]),
    ]
    for name, passed in results:
        print(f"{'PASS' if passed else 'FAIL'} {name}")
    return 0 if all(p for _, p in results) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--selftest", action="store_true")
    group.add_argument("--offline", action="store_true")
    group.add_argument("--url", metavar="URL", help="probe a live DTS endpoint")
    parser.add_argument("--no-write", action="store_true", help="do not write the receipt")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    return run("live" if args.url else "offline", args.url, not args.no_write)


if __name__ == "__main__":
    sys.exit(main())
