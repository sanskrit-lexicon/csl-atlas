#!/usr/bin/env python3
"""Syntax-check the ```js fences of an Observable page without a full build.

The Observable CLI is not always installed in a worktree; a fenced block with a
syntax error would then only surface in CI. This extracts each ```js fence into
a temp module and runs `node --check` over it.

Usage: python scripts/check_md_js_blocks.py src/tools/<page>.md [...]
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

FENCE = re.compile(r"^```js\s*$(.*?)^```\s*$", re.M | re.S)


def check(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    bad = 0
    for i, block in enumerate(FENCE.findall(text), 1):
        with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False, encoding="utf-8") as fh:
            fh.write(block)
            tmp = fh.name
        proc = subprocess.run(["node", "--check", tmp], capture_output=True, text=True, encoding="utf-8")
        Path(tmp).unlink(missing_ok=True)
        if proc.returncode != 0:
            bad += 1
            print(f"FAIL {path}: js block #{i}\n{proc.stderr}")
    if bad == 0:
        print(f"PASS {path}: {len(FENCE.findall(text))} js block(s) parse")
    return bad


if __name__ == "__main__":
    raise SystemExit(1 if sum(check(Path(p)) for p in sys.argv[1:]) else 0)
