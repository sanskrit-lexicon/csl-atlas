# Bounded local replication of the compound-depth typography probe.
#
# The remote API truncated/emptied ~33 % of out-of-sentence compounds, which is
# the probe's main caveat. This script re-runs a small deterministic slice on the
# pinned local HF model (chronbmm/sanskrit5-multitask) and compares validity and
# segment counts against the committed remote snapshot. It does NOT replace the
# snapshot: it is a robustness check on the API's failure mode.
#
# Usage:
#   /tmp/dmvenv/bin/python scripts/verify-compound-probe-local.py --per-population 80
#   /tmp/dmvenv/bin/python scripts/verify-compound-probe-local.py --device cpu

import argparse
import importlib.util
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import dharmamitra_infer as dm  # noqa: E402

SNAPSHOT = ROOT / "data" / "compound-depth" / "typography-probe-2026-10-17.json"
OUT = ROOT / "data" / "compound-depth" / "local-replication-2026-10-17.json"


def load_probe_module():
    spec = importlib.util.spec_from_file_location(
        "probe", ROOT / "scripts" / "probe-compound-depth-privative.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-population", type=int, default=80)
    ap.add_argument("--device", default=None)
    ap.add_argument("--batch-size", type=int, default=16)
    args = ap.parse_args()

    probe = load_probe_module()
    snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    rows = snap["rows"]
    picked = []
    for pop in ("A", "B"):
        picked += [r for r in rows if r["population"] == pop][:args.per_population]

    class Args:
        pass
    A = Args()
    A.source, A.batch_size, A.revision = "local", args.batch_size, dm.PINNED_REVISION
    A.device = args.device

    print(f"Local {dm.HF_MODEL_ID}@{dm.PINNED_REVISION[:12]} on "
          f"{args.device or 'auto'}; {len(picked)} rows", flush=True)
    raw, extra = dm.run([(r["surface"], r["surface"]) for r in picked],
                        pypi_mode="unsandhied",
                        local_prefix=dm.LOCAL_PREFIX["unsandhied"], args=A)

    out = []
    for r in picked:
        rec = raw.get(r["surface"]) or {}
        toks, status = probe.read_output(rec.get("raw"), r["surface"])
        out.append({
            "surface": r["surface"], "population": r["population"],
            "markupSegments": r["markupSegments"],
            "api": {"raw": r["raw"], "status": r["status"],
                    "segments": r["modelSegments"]},
            "local": {"raw": rec.get("raw"), "status": status,
                      "segments": len(toks) if status == "ok" else None},
        })

    def summary(sub):
        n = len(sub)
        ok = [x for x in sub if x["local"]["status"] == "ok"]
        return {"rows": n, "valid": len(ok),
                "validRate": round(len(ok) / n, 3) if n else 0,
                "status": dict(Counter(x["local"]["status"] for x in sub)),
                "segments": dict(sorted(Counter(
                    x["local"]["segments"] for x in ok).items()))}

    both = [x for x in out if x["api"]["status"] == "ok" and x["local"]["status"] == "ok"]
    agree = sum(1 for x in both if x["api"]["segments"] == x["local"]["segments"])
    payload = {
        "schemaVersion": "1.0.0",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "generatedBy": "python scripts/verify-compound-probe-local.py",
        "model": {"id": dm.HF_MODEL_ID, "revision": dm.PINNED_REVISION,
                  "device": extra.get("device"), **extra},
        "slice": {p: args.per_population for p in ("A", "B")},
        "summary": {"A": summary([x for x in out if x["population"] == "A"]),
                    "B": summary([x for x in out if x["population"] == "B"]),
                    "bothValid": len(both), "agree": agree,
                    "agreement": round(agree / len(both), 3) if both else None},
        "rows": out,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    s = payload["summary"]
    print(f"A local: {s['A']['valid']}/{s['A']['rows']} valid, segments {s['A']['segments']}")
    print(f"B local: {s['B']['valid']}/{s['B']['rows']} valid, segments {s['B']['segments']}")
    print(f"both valid {s['bothValid']}, agree {s['agree']} ({s['agreement']})")
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
