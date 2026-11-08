#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7096 — negative control for the PD regeneration gate.

A gate that is never exercised is a gate that may be blind.  This control
proves the PD parity gate actually refuses a hand edit to a generated file:
it re-introduces the exact #598 edit (a ZWNJ stripped out of a generated AOB
title by hand instead of taught to the generator), requires the gate to go
RED over it, then restores the file byte-for-byte and requires the gate to go
GREEN again.

The edit is made on a copy of the file's bytes held in memory and the
original bytes are written back in a ``finally`` block, so the control never
depends on git state and never leaves the tree changed -- not even if the
gate misbehaves.

The sentinel is a hand edit to ``data/pd/pd_aob_entries.tsv``; the gate that
must catch it is ``scripts/pd_aob_declared_entries.py --check``, whose
recorded input hash and derived title both move with the edit.  The
reconciliation gate catches it too when the sibling ``PD`` checkout is
present.

Run:
  python3 scripts/pd_regen_gate_selftest.py

Exit codes: 0 the gate proved itself / 1 the gate is blind or misbehaved.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "data" / "pd" / "pd_aob_entries.tsv"
GATE = ROOT / "scripts" / "pd_regen_gate.py"

#: the #598 hand edit, reversed: the committed file has the ZWNJ stripped,
#: the control puts it back to prove the gate notices a hand edit
CLEAN = "W. Calan — त्."
DIRTY = "W. Calan — त्‌."


def gate_runs():
    proc = subprocess.run(
        [sys.executable, str(GATE)], cwd=str(ROOT),
        capture_output=True, text=True)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def main() -> int:
    if not TARGET.exists():
        print("FAIL: %s is absent" % TARGET, file=sys.stderr)
        return 1

    original = TARGET.read_bytes()
    try:
        text = original.decode("utf-8")
        if text.count(CLEAN) != 1:
            print("FAIL: the %r sentinel is not unique in %s "
                  "(%d hits) -- the control cannot place its edit"
                  % (CLEAN, TARGET.name, text.count(CLEAN)), file=sys.stderr)
            return 1

        # Baseline: the gate must be GREEN over the committed tree.
        code, out = gate_runs()
        if code != 0:
            print("FAIL: the gate is already RED over the committed tree:\n%s"
                  % out, file=sys.stderr)
            return 1

        # Simulate the #598 failure mode: a committed hand edit.
        TARGET.write_text(text.replace(CLEAN, DIRTY), encoding="utf-8")

        code, out = gate_runs()
        if code == 0:
            print("FAIL: gate BLIND -- it stayed GREEN over a hand-edited "
                  "generated file:\n%s" % out, file=sys.stderr)
            return 1
        print("ok  the gate went RED over the hand edit")
        for line in out.splitlines():
            if line.startswith("[FAIL]"):
                print("    %s" % line)
    finally:
        TARGET.write_bytes(original)

    # Restoring the file must turn the gate GREEN again.
    code, out = gate_runs()
    if code != 0:
        print("FAIL: the gate stayed RED after the file was restored:\n%s"
              % out, file=sys.stderr)
        return 1
    print("ok  the gate is GREEN again over the restored file")
    print("negative control OK: a hand edit to a generated PD file goes RED "
          "on the regeneration gate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
