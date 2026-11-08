#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7096 — the PD regeneration gate (derive-don't-store parity for data/pd).

The PD generators in ``scripts/`` write committed artifacts under ``data/pd/``.
Each of them carries a ``--check`` mode that re-derives those artifacts and
compares them byte-for-byte with what is committed.  Those modes were run by
hand, so a hand edit to a *generated* file landed silently: #598 stripped two
ZWNJ artifacts out of ``data/pd/pd_aob_entries.tsv`` and
``data/pd/pd_aob_declared_entries.tsv`` by hand instead of teaching the
generator the rule, and every downstream parity gate went red for a week
without anything in CI noticing.

This gate runs the PD parity gates as part of the acceptance pipeline.  The
house rule for a source that is not vendored in this repo is the one the
review-artifact regeneration already follows for a missing ``csl-orig``
checkout ("expected in CI"): a gate whose source is absent is SKIPPED, a gate
whose source is present and whose artifacts drifted is RED.

Sources each gate needs (none of them are vendored here):

  * ``pd_aob_sigla_reconciliation.py`` -- the sibling ``PD`` checkout:
    ``AOB.md`` plus the two printed-book text witnesses ``AOB.pdf`` and
    ``AOB_ocr.md`` (the witness block is part of the compared JSON, so the
    gate needs all three or the comparison is not the committed one);
  * ``pd_aob_declared_entries.py`` -- only files committed in this repo;
  * ``pd_attestation_decomposition.py`` -- PDScan's ``pd.txt`` and
    ``csl-orig``'s ``pwg.txt``.

Run:
  python3 scripts/pd_regen_gate.py            # run every gate
  python3 scripts/pd_regen_gate.py --list     # show the gate + its sources

Exit codes: 0 ok-or-skipped / 1 drift in a gate whose sources are present.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"

#: the sibling PD checkout (OCR of the KoshaSHRI official PDF) and the
#: printed-book text witnesses the reconciliation gate compares against
PD_DIR = Path(os.environ.get(
    "PD_REPO", str(Path.home() / "Documents" / "GitHub" / "PD")))
PD_TXT = Path(os.environ.get(
    "PD_TXT", str(Path.home() / "Documents" / "GitHub" / "SanskritSpellCheck"
                  / "external_src" / "pd" / "pd.txt")))
PWG_TXT = Path(os.environ.get(
    "PWG_TXT", str(Path.home() / "Documents" / "GitHub" / "csl-orig"
                   / "v02" / "pwg" / "pwg.txt")))

#: (script, required sources, human label, extra CLI args for the gate)
GATES = (
    ("pd_aob_sigla_reconciliation.py",
     (PD_DIR / "AOB.md", PD_DIR / "AOB.pdf", PD_DIR / "AOB_ocr.md"),
     "AOB entry inventory + sigla reconciliation",
     ("--aob", PD_DIR / "AOB.md",
      "--witness", PD_DIR / "AOB.pdf",
      "--witness", PD_DIR / "AOB_ocr.md")),
    ("pd_aob_declared_entries.py",
     (),
     "AOB declared-canon entry table",
     ()),
    ("pd_attestation_decomposition.py",
     (PD_TXT, PWG_TXT),
     "PD/PWG attestation decomposition",
     ("--pd", PD_TXT, "--pwg", PWG_TXT)),
    ("pd_shared_work_registry.py",
     (),
     "PD shared work-and-edition identity registry",
     ()),
)


def run_gate(script, sources, extra_args):
    """Run one parity gate.  Returns (status, detail).

    status is "ok", "skip" or "drift"; never raises for a red gate -- the
    caller decides what to do with it.
    """
    missing = [p for p in sources if not p.exists()]
    if missing:
        return "skip", "source absent: %s" % ", ".join(str(p) for p in missing)
    args = [str(a) for a in extra_args]
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / script), "--check"] + args,
        cwd=str(ROOT), capture_output=True, text=True)
    out = (proc.stdout + proc.stderr).strip()
    if proc.returncode == 0:
        return "ok", out.splitlines()[-1] if out else "ok"
    return "drift", out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", action="store_true",
                    help="print the gates and their sources, then exit")
    args = ap.parse_args(argv)

    if args.list:
        for script, sources, label, _ in GATES:
            print("%-38s %-46s %s"
                  % (script, label,
                     ", ".join(str(p) for p in sources) or "(repo files only)"))
        return 0

    failed = []
    for script, sources, label, extra_args in GATES:
        status, detail = run_gate(script, sources, extra_args)
        if status == "ok":
            print("[OK  ] %-38s %s" % (script, detail))
        elif status == "skip":
            print("[SKIP] %-38s %s" % (script, detail))
        else:
            print("[FAIL] %-38s %s" % (script, detail))
            failed.append(script)
    if failed:
        print("\nPD regeneration gate: %d gate(s) drifted: %s"
              % (len(failed), ", ".join(failed)), file=sys.stderr)
        print("Regenerate with the owning script (no --check) and commit the "
              "result, or teach the generator the rule the hand edit encoded.",
              file=sys.stderr)
        return 1
    print("PD regeneration gate: every present source reproduces its "
          "committed artifacts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
