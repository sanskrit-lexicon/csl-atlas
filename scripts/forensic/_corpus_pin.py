"""Pin every forensic figure to ONE recorded csl-orig revision (H5248).

`.source.json` sidecars used to record only the csl-atlas commit, so F1/F5
figures drifted silently with upstream csl-orig corrections (587 -> 598 rare
refs, 3,593 -> 3,583 order entries; EVIDENCE_DEPENDENCE_AUDIT.md §7). A figure
is now written only when the corpus revision behind it is known exactly:

* `cache_revision(codes)`  — for scripts that read `data/forensic/parsed/*.tsv`
  (F1, F2, F3 …): every cache needs a `_parse_provenance.json` record whose
  `tsv_sha256` still matches the file, built from a clean checkout, and all
  caches must share one revision. Unrecorded / hash-mismatch / dirty -> None,
  several revisions -> MIXED; both REFUSE.
* `live_revision()`        — for scripts that re-read `../csl-orig` bodies
  directly (F5, F10): HEAD of that checkout, which must be clean. Call it
  before AND after the run (`assert_unmoved`) so a checkout that moved mid-run
  refuses instead of producing a figure from two revisions.

`write_pinned_source()` writes the sidecar with the pin under `csl_orig`.
"""

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone

from parse_cslorig import CSL_ORIG, PARSED_DIR


class CorpusPinError(RuntimeError):
    """The csl-orig revision behind a figure is None, MIXED, dirty or moved."""


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def cache_revision(codes, parsed_dir=None):
    """One csl-orig revision behind the parsed caches of `codes`, or refuse."""
    parsed_dir = parsed_dir or PARSED_DIR
    prov_path = os.path.join(parsed_dir, "_parse_provenance.json")
    caches = {}
    if os.path.exists(prov_path):
        with open(prov_path, encoding="utf-8") as fh:
            caches = (json.load(fh) or {}).get("caches", {}) or {}
    per_cache, bad = {}, []
    for code in sorted(c.lower() for c in codes):
        rec = caches.get(code)
        tsv = os.path.join(parsed_dir, f"{code}.tsv")
        if not rec or not rec.get("revision"):
            bad.append(f"{code}: unrecorded")
        elif not os.path.exists(tsv) or rec.get("tsv_sha256") != _sha256(tsv):
            bad.append(f"{code}: hash-mismatch")
        elif rec.get("dirty") is not False:
            bad.append(f"{code}: built from a dirty or unknown checkout")
        else:
            per_cache[code] = rec["revision"]
    if not codes:
        bad.append("no caches named")
    if bad:
        raise CorpusPinError("csl-orig revision is None — rebuild with "
                             "`python3 scripts/forensic/parse_cslorig.py --all`: " + "; ".join(bad))
    revs = sorted(set(per_cache.values()))
    if len(revs) != 1:
        raise CorpusPinError(f"csl-orig revision is MIXED across caches: {per_cache}")
    return {"revision": revs[0], "via": "parse_provenance",
            "caches": {c: caches[c]["tsv_sha256"] for c in per_cache}}


def live_revision(csl_orig=None):
    """HEAD of the csl-orig checkout a script reads bodies from; must be clean."""
    csl_orig = csl_orig or CSL_ORIG
    try:
        r = subprocess.run(["git", "-C", csl_orig, "rev-parse", "HEAD"],
                           capture_output=True, text=True, encoding="utf-8", timeout=30)
        d = subprocess.run(["git", "-C", csl_orig, "status", "--porcelain", "-uno"],
                           capture_output=True, text=True, encoding="utf-8", timeout=120)
    except Exception as exc:                                   # noqa: BLE001
        raise CorpusPinError(f"csl-orig revision is None: {exc!r}"[:300]) from exc
    if r.returncode != 0 or d.returncode != 0 or not r.stdout.strip():
        raise CorpusPinError(f"csl-orig revision is None: {csl_orig} is not a readable git checkout")
    if d.stdout.strip():
        raise CorpusPinError(f"csl-orig checkout {csl_orig} is dirty; a figure from "
                             "uncommitted corpus edits cannot be reproduced")
    return {"revision": r.stdout.strip(), "via": "live_checkout"}


def assert_unmoved(before, csl_orig=None):
    """Refuse if the checkout moved (or got dirty) while the script read it."""
    after = live_revision(csl_orig)
    if after["revision"] != before["revision"]:
        raise CorpusPinError(f"csl-orig moved mid-run: {before['revision']} -> {after['revision']}")
    return before


def write_pinned_source(out_path, script, stage, pin):
    """The L0 sidecar shape plus the csl-orig pin. `pin` must carry a revision."""
    if not pin or not pin.get("revision") or pin["revision"] == "MIXED":
        raise CorpusPinError(f"refusing to write {out_path}.source.json without one csl-orig revision")
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True,
                                         stderr=subprocess.DEVNULL).strip()
    except Exception:                                          # noqa: BLE001
        commit = "unknown"
    data = {"stage": stage, "commit": commit,
            "utc_iso": datetime.now(timezone.utc).isoformat(),
            "script": script, "csl_orig": pin}
    with open(f"{out_path}.source.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
