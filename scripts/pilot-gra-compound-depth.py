#!/usr/bin/env python3
"""H6963 Q8 — GRA marker-convention audit, then a 500-row compound-depth pilot.

The audit runs first and is written before any model number: it states which
character is GRA's compound-member marker. Only then does the pilot sample 500
hyphenated GRA headwords, run the pinned local model, and compare its segment
count with the GRA markup.

Outputs
  data/compound-depth/gra-marker-audit-2026-10-18.json
  data/compound-depth/gra-pilot-2026-10-18.json

Usage
  python3 scripts/pilot-gra-compound-depth.py --csl-orig /tmp/csl-orig
  python3 scripts/pilot-gra-compound-depth.py --source pypi --limit 500   # cross-check
"""

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import dharmamitra_infer as dm  # noqa: E402

AUDIT_OUT = ROOT / "data" / "compound-depth" / "gra-marker-audit-2026-10-18.json"
PILOT_OUT = ROOT / "data" / "compound-depth" / "gra-pilot-2026-10-18.json"
GENERATED_AT = "2026-10-18"
SEED = 20261018
SAMPLE_N = 500
MARKERS = re.compile(r"[—\-+]")


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


def parse_gra(path):
    rows = []
    text = Path(path).read_text(encoding="utf-8")
    for line in text.splitlines():
        if not line.startswith("<L>"):
            continue
        m2 = re.search(r"<k2>([^<]*)", line)
        if not m2:
            continue
        k2 = m2.group(1).strip()
        k1 = re.search(r"<k1>([^<]*)", line)
        line_no = re.search(r"<L>([^<]*)", line)
        surface = MARKERS.sub("", k2.replace("/", "")).strip()
        if not surface:
            continue
        rows.append({"k2": k2, "surface": surface,
                     "k1": k1.group(1).strip() if k1 else "",
                     "line": line_no.group(1) if line_no else "",
                     "markupSegments": len([s for s in MARKERS.split(k2.replace("/", "")) if s])})
    return text, rows


def audit(text, rows):
    body = text
    k2_with_hyphen = [r for r in rows if "-" in r["k2"]]
    k2_with_emdash = [r for r in rows if "—" in r["k2"]]
    depth = Counter(r["markupSegments"] for r in rows)
    return {
        "schemaVersion": "1.0.0",
        "generatedAt": GENERATED_AT,
        "generatedBy": "python3 scripts/pilot-gra-compound-depth.py",
        "question": "Q8 gate: which character marks compound members in GRA <k2>?",
        "convention": {
            "k2MemberMarker": "hyphen '-' (U+002D)",
            "emDashInK2": "absent; U+2014 occurs only in running text/phrase brackets",
            "rule": ("GRA segments a compound headword with '-'; '/' is a spelling "
                     "variant separator, not a member boundary. No depth metric may "
                     "read U+2014 as a GRA member marker."),
            "statedBefore": "no model was called before this audit was written",
        },
        "counts": {
            "headwords": len(rows),
            "k2WithHyphen": len(k2_with_hyphen),
            "k2WithEmDash": len(k2_with_emdash),
            "k2HyphenCharacters": sum(r["k2"].count("-") for r in rows),
            "k2EmDashCharacters": sum(r["k2"].count("—") for r in rows),
            "wholeFileHyphens": body.count("-"),
            "wholeFileEmDashes": body.count("—"),
            "hyphenatedDepthDistribution": dict(sorted(Counter(
                r["markupSegments"] for r in k2_with_hyphen).items())),
            "allHeadwordDepthDistribution": dict(sorted(depth.items())),
        },
        "finding": ("The cited 5,497 hyphens vs 1,045 em dashes cannot be a GRA <k2> "
                    "comparison: GRA <k2> has zero em dashes. The em dashes are text "
                    "punctuation (phrase brackets and ellipses), so only the hyphen "
                    "column is a segmentation convention. The pilot therefore samples "
                    "hyphenated headwords and asks whether the model reads the same "
                    "two-member split GRA marks."),
        "pilotFrame": {"universe": "GRA <k2> containing at least one hyphen",
                       "rows": len(k2_with_hyphen), "sample": SAMPLE_N, "seed": SEED},
    }


def sample(rows, n, seed):
    frame = [r for r in rows if "-" in r["k2"]]
    ranked = sorted(frame, key=lambda r: hashlib.sha256(
        f"{seed}:{r['surface']}:{r['k2']}".encode()).hexdigest())
    return ranked[:n]


def read_output(raw, surf):
    """Same validator as the probe (kept local so the pilot is self-contained)."""
    toks = (raw or "").replace("_", " ").split()
    while toks and re.match(r"^[A-Z]$", toks[0]):
        toks.pop(0)
    joined = "".join(toks)
    if not toks or not joined.strip("_ "):
        return [], "empty"
    if not (0.75 * len(surf) <= len(joined) <= 1.30 * len(surf)):
        return toks, "garbage"
    if joined[:1].lower() != surf[:1].lower():
        return toks, "truncated"
    return toks, "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csl-orig", default=str(ROOT.parent / "csl-orig"))
    ap.add_argument("--gra", default=None)
    ap.add_argument("--source", choices=["local", "pypi"], default="local")
    ap.add_argument("--limit", type=int, default=SAMPLE_N)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--device", default=None)
    ap.add_argument("--audit-only", action="store_true",
                    help="write the convention audit and stop before any model call")
    args = ap.parse_args()
    gra_path = Path(args.gra or Path(args.csl_orig) / "v02" / "gra" / "gra.txt")
    if not gra_path.exists():
        sys.exit(f"missing GRA inventory: {gra_path}")

    text, rows = parse_gra(gra_path)
    audit_payload = audit(text, rows)
    audit_payload["source"] = {"gra": str(gra_path), "sha256": hashlib.sha256(
        gra_path.read_bytes()).hexdigest()}
    AUDIT_OUT.write_text(json.dumps(audit_payload, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    print(f"audit: {audit_payload['counts']['headwords']:,} headwords, "
          f"{audit_payload['counts']['k2WithHyphen']:,} hyphenated, "
          f"{audit_payload['counts']['k2WithEmDash']} with em dash -> "
          f"{AUDIT_OUT.relative_to(ROOT)}")
    if args.audit_only:
        return

    picked = sample(rows, args.limit, SEED)

    class Args:
        pass
    A = Args()
    A.source = args.source
    A.batch_size = args.batch_size
    A.revision = dm.PINNED_REVISION
    A.device = args.device

    raw, extra = dm.run([(r["surface"], r["surface"]) for r in picked],
                        pypi_mode="unsandhied",
                        local_prefix=dm.LOCAL_PREFIX["unsandhied"], args=A)
    out = []
    for r in picked:
        rec = raw.get(r["surface"]) or {}
        toks, status = read_output(rec.get("raw"), r["surface"])
        out.append({"surface": r["surface"], "k2": r["k2"], "line": r["line"],
                    "markupSegments": r["markupSegments"], "input": rec.get("input"),
                    "raw": rec.get("raw"), "status": status,
                    "modelSegments": len(toks) if status == "ok" else None})
    out.sort(key=lambda x: (x["surface"], x["k2"]))

    ok = [x for x in out if x["status"] == "ok"]
    reads = Counter(x["modelSegments"] for x in ok)
    p2 = sum(1 for x in ok if x["modelSegments"] == 2)
    p3 = sum(1 for x in ok if x["modelSegments"] >= 3)
    # GRA's own split: two members = one hyphen. Agreement is exact-depth and
    # >=2 (does the model see a compound at all).
    exact = sum(1 for x in ok if x["modelSegments"] == x["markupSegments"])
    atleast2 = sum(1 for x in ok if x["modelSegments"] >= 2)
    payload = {
        "schemaVersion": "1.0.0",
        "generatedAt": GENERATED_AT,
        "generatedBy": "python3 scripts/pilot-gra-compound-depth.py",
        "question": "Q8: do GRA's hyphen-marked compound splits survive the segmenter?",
        "source": "local" if args.source == "local" else "remote API (recorded cross-check)",
        "model": {"id": dm.HF_MODEL_ID if args.source == "local" else "remote",
                  "revision": dm.PINNED_REVISION if args.source == "local" else None,
                  **extra},
        "audit": str(AUDIT_OUT.relative_to(ROOT)),
        "frame": audit_payload["pilotFrame"],
        "sample": {"rows": len(out), "seed": SEED,
                   "selection": "sha256(seed:surface:k2) rank, first N"},
        "stats": {
            "rows": len(out), "valid": len(ok),
            "validRate": share(len(ok), len(out)),
            "validRateCi95": wilson(len(ok), len(out)),
            "status": dict(sorted(Counter(x["status"] for x in out).items())),
            "modelSegments": {str(k): v for k, v in sorted(reads.items())},
            "p1": share(reads.get(1, 0), len(ok)),
            "p2": share(p2, len(ok)), "p2Ci95": wilson(p2, len(ok)),
            "p3plus": share(p3, len(ok)), "p3plusCi95": wilson(p3, len(ok)),
            "exactMarkupAgreement": share(exact, len(ok)),
            "exactMarkupAgreementCi95": wilson(exact, len(ok)),
            "readsCompoundAtLeast2": share(atleast2, len(ok)),
            "readsCompoundAtLeast2Ci95": wilson(atleast2, len(ok)),
        },
        "rows": out,
    }
    PILOT_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    s = payload["stats"]
    print(f"pilot: {s['valid']}/{s['rows']} valid ({s['validRate']:.1%}); "
          f"p2 {s['p2']:.1%} {s['p2Ci95']}; p3+ {s['p3plus']:.1%}; "
          f"exact agreement {s['exactMarkupAgreement']:.1%}")
    print(f"wrote {PILOT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
