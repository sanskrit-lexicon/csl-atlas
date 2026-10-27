#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7300 — PD KoshaSHRI staleness audit: three panels, four separate verdicts.

Thin wrapper over the pd_koshashri_staleness_audit/ package (token-gate split):
part01 = inputs + markup panel + coverage panel; part02 = verdicts, canaries,
emit, --check, main.

Extends H6698 C7 (14-10-2026) and the 25-10-2026 two-digitisations markup
audit.  PANEL A markup capability (schema-staleness verdict); PANEL B dated
content coverage, the 35-volume KoshaSHRI JSON snapshot (27-10-2026) joined to
the H7275 publication ledger (content-coverage verdict); PANEL C the v7/v8
bracketed-source-mark control — print marks present but absent from the
machine text mean conversion loss, marks absent from both support editorial
change only after the print check (conversion-loss and editorial-change
verdicts); the 2009-2019 print record is STOP_NO_PRINT_ACCESS.

Rights: KoshaSHRI all-rights-reserved — public per-volume JSON metadata only,
no entry text, no circumvention; Cologne CC BY-NC-SA 3.0 — derived counts only.

Usage:
    python scripts/pd_koshashri_staleness_audit.py            # rebuild artifacts
    python scripts/pd_koshashri_staleness_audit.py --check    # verify, no writes
    python scripts/pd_koshashri_staleness_audit.py --fetch    # live re-probe docs

Exit codes: 0 ok, 2 --check mismatch, 3 committed snapshot missing.
Stdlib only.  --check needs no network and no pd.txt.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "pd_koshashri_staleness_audit"))

from part01 import *  # noqa: F401,F403
from part02 import *  # noqa: F401,F403
from part02 import build_all, canary_pins_ok, main

if __name__ == "__main__":
    sys.exit(main())
