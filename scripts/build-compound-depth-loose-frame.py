#!/usr/bin/env python3
"""H6963 Q7 — the full loose frame (30,703 marker-3+ MW records).

Population A in the 2026-10-17 probe was em-dash-only 3+, so the preverb-joint
class (pra-kASa---karman) was never model-tested. This script extracts the full
marker-3+ frame from MW and runs it.

Canonical path (Q9) is the pinned local model. The remote API path exists only
as a recorded cross-check; it is not reproducible and must never be the sole
source of a published number. On a 1-vCPU box the local run of 28,977 surfaces
takes many hours, so `--source pypi` is what fits a bounded unit.

Outputs
  data/compound-depth/loose-frame-2026-10-18.json         (frame + run)
  data/compound-depth/loose-frame-2026-10-18.tsv           (deterministic rows)

Usage
  python3 scripts/build-compound-depth-loose-frame.py --csl-orig /tmp/csl-orig --source pypi
  python3 scripts/build-compound-depth-loose-frame.py --csl-orig /tmp/csl-orig --source local --limit 500
"""

import argparse
import hashlib
import json
import re
import sys
import threading
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import dharmamitra_infer as dm  # noqa: E402

OUT = ROOT / "data" / "compound-depth" / "loose-frame-2026-10-18.json"
TSV = ROOT / "data" / "compound-depth" / "loose-frame-2026-10-18.tsv"
GENERATED_AT = "2026-10-18"
MARKERS = re.compile(r"[—\-+]")
TAG_TOKEN = re.compile(r"^[A-Z]$")


def wilson(k, n, z=1.96):
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return [round((c - h) / d, 4), round((c + h) / d, 4)]


def share(k, n):
    return round(k / n, 4) if n else None


def parse_mw(path):
    """Distinct surfaces over every marker-3+ MW record."""
    frame = {}
    records = 0
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.startswith("<L>"):
            continue
        m2 = re.search(r"<k2>([^<]*)", line)
        if not m2:
            continue
        k2 = m2.group(1).strip()
        clean = k2.replace("/", "")
        segs = [s for s in MARKERS.split(clean) if s]
        if len(segs) < 3:
            continue
        records += 1
        surf = MARKERS.sub("", clean).strip()
        if not surf:
            continue
        row = frame.setdefault(surf, {"surface": surf, "k2": k2, "records": 0,
                                      "markupSegments": len(segs),
                                      "markers": Counter()})
        row["records"] += 1
        row["markupSegments"] = max(row["markupSegments"], len(segs))
        for ch in ("—", "-", "+"):
            if ch in clean:
                row["markers"][ch] += 1
    rows = []
    for r in frame.values():
        r["markers"] = dict(sorted(r["markers"].items()))
        rows.append(r)
    rows.sort(key=lambda r: r["surface"])
    return rows, records


def read_output(raw, surf):
    toks = (raw or "").replace("_", " ").split()
    while toks and TAG_TOKEN.match(toks[0]):
        toks.pop(0)
    joined = "".join(toks)
    if not toks or not joined.strip("_ "):
        return [], "empty"
    if not (0.75 * len(surf) <= len(joined) <= 1.30 * len(surf)):
        return toks, "garbage"
    if joined[:1].lower() != surf[:1].lower():
        return toks, "truncated"
    return toks, "ok"


def run_remote(rows):
    import concurrent.futures as cf
    import requests
    chunk = 60
    chunks = [rows[i:i + chunk] for i in range(0, len(rows), chunk)]
    got = {}
    lock = threading.Lock()
    done = [0]

    def call(part):
        inputs = [dm.slp1_to_iast(r["surface"]) for r in part]
        last = None
        for attempt in (1, 2, 3):
            try:
                resp = requests.post(dm.API_URL, json={
                    "texts": inputs, "mode": "unsandhied",
                    "human_readable_tags": True}, timeout=60)
                resp.raise_for_status()
                results = resp.json().get("results", [])
                if len(results) != len(part):
                    raise ValueError(f"{len(results)} results for {len(part)} inputs")
                return part, inputs, results
            except Exception as e:  # noqa: BLE001 - transient
                last = e
                time.sleep(1.5 * attempt)
        raise last

    with cf.ThreadPoolExecutor(max_workers=12) as pool:
        futures = [pool.submit(call, part) for part in chunks]
        for fut in cf.as_completed(futures):
            try:
                part, inputs, results = fut.result()
            except Exception as e:  # noqa: BLE001
                print(f"  chunk skipped: {type(e).__name__}", file=sys.stderr)
                continue
            with lock:
                for r, inp, raw in zip(part, inputs, results):
                    raw = raw if isinstance(raw, str) else json.dumps(raw, ensure_ascii=False)
                    got[r["surface"]] = {"input": inp, "raw": raw}
                done[0] += len(part)
                if done[0] % 3000 < chunk:
                    print(f"  ... {done[0]:,}/{len(rows):,}", flush=True)
    return got, {"endpoint": dm.API_URL, "note": "remote, not reproducible; cross-check only"}


def run_local(rows, batch_size, device):
    class Args:
        pass
    A = Args()
    A.source, A.batch_size, A.revision, A.device = \
        "local", batch_size, dm.PINNED_REVISION, device
    return dm.run([(r["surface"], r["surface"]) for r in rows],
                  pypi_mode="unsandhied",
                  local_prefix=dm.LOCAL_PREFIX["unsandhied"], args=A)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csl-orig", default=str(ROOT.parent / "csl-orig"))
    ap.add_argument("--mw", default=None)
    ap.add_argument("--source", choices=["local", "pypi"], default="pypi")
    ap.add_argument("--limit", type=int, default=0, help="cap distinct surfaces (0=all)")
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--device", default=None)
    ap.add_argument("--frame-only", action="store_true",
                    help="write the deterministic frame and stop before inference")
    args = ap.parse_args()
    mw_path = Path(args.mw or Path(args.csl_orig) / "v02" / "mw" / "mw.txt")
    if not mw_path.exists():
        sys.exit(f"missing MW inventory: {mw_path}")

    rows, records = parse_mw(mw_path)
    frame_sha = hashlib.sha256(json.dumps(
        [(r["surface"], r["k2"], r["records"], r["markupSegments"]) for r in rows],
        ensure_ascii=False).encode()).hexdigest()
    print(f"loose frame: {records:,} records, {len(rows):,} distinct surfaces")
    if args.limit:
        rows = rows[:args.limit]
    if args.frame_only:
        TSV.write_text("\n".join(
            ["surface\tk2\trecords\tmarkup_segments\tmarkers"] +
            [f"{r['surface']}\t{r['k2']}\t{r['records']}\t{r['markupSegments']}\t"
             f"{','.join(r['markers'])}" for r in rows]) + "\n", encoding="utf-8")
        print(f"wrote {TSV.relative_to(ROOT)}")
        return

    if args.source == "local":
        got, extra = run_local(rows, args.batch_size, args.device)
    else:
        got, extra = run_remote(rows)

    out = []
    for r in rows:
        rec = got.get(r["surface"]) or {}
        toks, status = read_output(rec.get("raw"), r["surface"])
        out.append({**r, "input": rec.get("input"), "raw": rec.get("raw"),
                    "status": status,
                    "modelSegments": len(toks) if status == "ok" else None})
    ok = [x for x in out if x["status"] == "ok"]
    reads = Counter(x["modelSegments"] for x in ok)
    p2 = sum(1 for x in ok if x["modelSegments"] == 2)
    p3 = sum(1 for x in ok if x["modelSegments"] >= 3)
    stats = {
        "rows": len(out), "valid": len(ok), "validRate": share(len(ok), len(out)),
        "validRateCi95": wilson(len(ok), len(out)),
        "status": dict(sorted(Counter(x["status"] for x in out).items())),
        "modelSegments": {str(k): v for k, v in sorted(reads.items())},
        "p1": share(reads.get(1, 0), len(ok)),
        "p2": share(p2, len(ok)), "p2Ci95": wilson(p2, len(ok)),
        "p3plus": share(p3, len(ok)), "p3plusCi95": wilson(p3, len(ok)),
        "readCompoundAtLeast2": share(sum(1 for x in ok if x["modelSegments"] >= 2), len(ok)),
    }
    payload = {
        "schemaVersion": "1.0.0",
        "generatedAt": GENERATED_AT,
        "generatedBy": "python3 scripts/build-compound-depth-loose-frame.py",
        "question": ("Q7: the full loose frame (marker-3+), including the "
                     "preverb-joint class population A never sampled"),
        "source": "local" if args.source == "local" else "remote API (recorded cross-check, not canonical)",
        "model": {"id": dm.HF_MODEL_ID if args.source == "local" else "remote",
                  "revision": dm.PINNED_REVISION if args.source == "local" else None,
                  **extra},
        "frame": {"records": records, "distinctSurfaces": len(rows),
                  "sha256": frame_sha,
                  "markerDepthDistribution": dict(sorted(Counter(
                      r["markupSegments"] for r in rows).items())),
                  "markerTypes": dict(sorted(Counter(
                      "+".join(r["markers"]) for r in rows).items()))},
        "stats": stats,
        "verdict": "LOOSE-FRAME-VALID" if stats["validRate"] and stats["validRate"] >= 0.5
                   else "LOOSE-FRAME-LOW-COVERAGE",
        "rows": out,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    TSV.write_text("\n".join(
        ["surface\tk2\trecords\tmarkup_segments\tstatus\tmodel_segments\traw"] +
        [f"{x['surface']}\t{x['k2']}\t{x['records']}\t{x['markupSegments']}\t"
         f"{x['status']}\t{x['modelSegments'] if x['modelSegments'] is not None else ''}\t"
         f"{x['raw'] or ''}" for x in out]) + "\n", encoding="utf-8")
    print(f"valid {stats['valid']:,}/{stats['rows']:,} ({stats['validRate']:.1%}), "
          f"p2 {stats['p2']:.1%}, p3+ {stats['p3plus']:.1%}")
    print(f"wrote {OUT.relative_to(ROOT)} and {TSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
