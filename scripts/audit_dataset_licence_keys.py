"""Count data/**.json files that declare a top-level licence key.

Feeds the coverage line of docs/DATASET_LICENCE_MATRIX.md (H5302).
Usage: python scripts/audit_dataset_licence_keys.py
"""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
KEYS = ("license", "licence")


def main() -> int:
    total = 0
    declared = []
    undeclared_families = {}
    for path in sorted(DATA.rglob("*.json")):
        if path.name.endswith(".source.json"):
            continue
        total += 1
        family = path.relative_to(DATA).parts[0] if len(path.relative_to(DATA).parts) > 1 else "(root)"
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            obj = None
        value = None
        if isinstance(obj, dict):
            for key in KEYS:
                if isinstance(obj.get(key), str):
                    value = obj[key]
                    break
        if value:
            declared.append((str(path.relative_to(ROOT)).replace("\\", "/"), value))
        else:
            undeclared_families[family] = undeclared_families.get(family, 0) + 1

    print(f"data/**.json (excluding .source.json sidecars): {total}")
    print(f"declaring a top-level licence key: {len(declared)}")
    for rel, value in declared:
        print(f"  {rel} -> {value}")
    print("undeclared, by family:")
    for family, count in sorted(undeclared_families.items(), key=lambda kv: -kv[1]):
        print(f"  {family}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
