#!/usr/bin/env python3
"""H6963 — deterministic evidence for the compound-depth correction (Q6, Q10, Q11).

Reads the committed remote snapshot (no new model calls) and the MW/PWG
headword inventories and writes three reproducible artefacts:

  1. data/compound-depth/depth-distribution-2026-10-18.json
     Corrected distribution for markup depths 3-8: the markup (joint) count,
     model-read (immediate-constituent) counts, validity and Wilson CIs.
  2. data/compound-depth/ci-bounds-2026-10-18.json
     Wilson CI for p2 per markup depth plus a censoring bounds table. The
     snapshot's "truncated" rows dropped the first member, so the returned
     token count is a lower bound on the true depth; only rows that returned
     <= 1 token can still be a 2-member read. Empty/garbage rows are unbounded.
  3. data/compound-depth/headword-join-2026-10-18.tsv
     Deterministic join of the 2,121 markup-3 rows the model reads as 2: does
     a plain concatenation of the first two markup members occur as an MW or
     PWG headword? Same input -> same TSV (sorted, no wall clock).

Usage:
  python3 scripts/build-compound-depth-evidence.py --csl-orig /path/to/csl-orig
  python3 scripts/build-compound-depth-evidence.py            # default sibling csl-orig

The script never touches csl-orig; it only reads v02/mw/mw.txt and
v02/pwg/pwg.txt. Paths may also be given with --mw / --pwg.
"""

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data" / "compound-depth" / "typography-probe-2026-10-17.json"
DIST_OUT = ROOT / "data" / "compound-depth" / "depth-distribution-2026-10-18.json"
BOUNDS_OUT = ROOT / "data" / "compound-depth" / "ci-bounds-2026-10-18.json"
JOIN_OUT = ROOT / "data" / "compound-depth" / "headword-join-2026-10-18.tsv"
JOIN_JSON = ROOT / "data" / "compound-depth" / "headword-join-2026-10-18.json"

GENERATED_BY = "python3 scripts/build-compound-depth-evidence.py"
GENERATED_AT = "2026-10-18"  # fixed: output must be byte-identical across runs
MARKERS = re.compile(r"[—\-+]")
Z = 1.96


def wilson(k, n, z=Z):
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return [round((c - h) / d, 4), round((c + h) / d, 4)]


def share(k, n):
    return round(k / n, 4) if n else None


def segments(k2):
    return [s for s in MARKERS.split(str(k2).replace("/", "")) if s]


def raw_tokens(raw):
    """Token count the model actually returned, including a dropped first member."""
    if not raw:
        return 0
    return len([t for t in raw.replace("_", " ").split() if t.strip("_ ")])


def read_output_text(raw, surf):
    """Local copy of the probe's validator, used only to size the censoring bound.

    We do not re-classify the committed status; we only need the token count the
    endpoint returned for truncated rows, which the snapshot stores as raw text.
    """
    toks = (raw or "").replace("_", " ").split()
    while toks and re.match(r"^[A-Z]$", toks[0]):
        toks.pop(0)
    return toks


def load_snapshot():
    snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    rows = snap["rows"]
    sha = hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest()
    return snap, rows, sha


def load_records_by_depth(mw_path):
    """Record counts per marker depth, recomputed from MW (the snapshot omits them)."""
    counts = Counter()
    for line in open(mw_path, encoding="utf-8"):
        if not line.startswith("<L>"):
            continue
        m = re.search(r"<k2>([^<]*)", line)
        if not m:
            continue
        segs = segments(m.group(1).strip())
        if len(segs) >= 3:
            counts[len(segs)] += 1
    return counts


def load_headwords(path):
    """Return the set of <k1> headwords (SLP1, no markup), plus its own digest."""
    heads = set()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.startswith("<L>"):
                continue
            m = re.search(r"<k1>([^<]*)", line)
            if m:
                h = m.group(1).strip()
                if h:
                    heads.add(h)
    return heads


def distribution(rows, snapshot_sha, record_counts, mw_path, mw_sha):
    a = [r for r in rows if r["population"] == "A"]
    by_markup = {}
    for d in range(3, 11):
        sub = [r for r in a if r["markupSegments"] == d]
        if not sub:
            continue
        ok = [r for r in sub if r["status"] == "ok"]
        reads = Counter(r["modelSegments"] for r in ok)
        recs = record_counts.get(d, 0)
        dist = {}
        for m in range(1, 9):
            k = reads.get(m, 0)
            dist[str(m)] = {"n": k, "share": share(k, len(ok)),
                            "ci95": wilson(k, len(ok))}
        by_markup[str(d)] = {
            "markupDepth": d,
            "records": recs,
            "surfaces": len(sub),
            "valid": len(ok),
            "validRate": share(len(ok), len(sub)),
            "validRateCi95": wilson(len(ok), len(sub)),
            "status": dict(sorted(Counter(r["status"] for r in sub).items())),
            "modelReads": dist,
            "pRead2": share(reads.get(2, 0), len(ok)),
            "pRead2Ci95": wilson(reads.get(2, 0), len(ok)),
        }

    # The corrected (IC) distribution over all 3+ surfaces: model reads among
    # valid rows, then two denomators for the headline (valid-only, and all
    # surfaces with the missing rows left out of the numerator).
    ok = [r for r in a if r["status"] == "ok"]
    reads = Counter(r["modelSegments"] for r in ok)
    ic = {str(m): {"n": reads.get(m, 0), "shareOfValid": share(reads.get(m, 0), len(ok)),
                   "shareOfAllSurfaces": share(reads.get(m, 0), len(a)),
                   "ci95OfValid": wilson(reads.get(m, 0), len(ok))}
          for m in range(1, 9)}
    ic3plus = sum(v for k, v in reads.items() if k >= 3)
    totals = {
        "surfaces": len(a),
        "valid": len(ok),
        "validRate": share(len(ok), len(a)),
        "validRateCi95": wilson(len(ok), len(a)),
        "modelRead3Plus": {"n": ic3plus,
                           "shareOfValid": share(ic3plus, len(ok)),
                           "shareOfAllSurfaces": share(ic3plus, len(a)),
                           "ci95OfValid": wilson(ic3plus, len(ok)),
                           "scaledToAllSurfacesPoint": round(ic3plus / len(ok) * len(a)) if ok else None},
    }
    return {
        "schemaVersion": "1.0.0",
        "generatedAt": GENERATED_AT,
        "generatedBy": GENERATED_BY,
        "question": "Q6: corrected compound-depth distribution, depths 3-8 (no new model calls)",
        "source": {"snapshot": str(SNAPSHOT.relative_to(ROOT)), "sha256": snapshot_sha,
                   "model": "Dharmamitra ByT5-Sanskrit (unsandhied), remote API",
                   "markupRecordsFrom": str(mw_path), "markupRecordsSha256": mw_sha},
        "units": {"markupDepth": "joints: em-dash/hyphen-separated <k2> members",
                  "modelRead": "immediate constituents as read by the segmenter",
                  "records": "MW records (a surface may repeat)",
                  "surfaces": "distinct surfaces"},
        "markupDepths": by_markup,
        "icDistribution": ic,
        "totals": totals,
        "caveat": ("The snapshot is a remote API run; Q9 makes the pinned local model "
                   "canonical for new runs. These are derived tabs from the committed "
                   "snapshot, which the ruling explicitly permits (no new model calls)."),
    }


def bounds(rows, snapshot_sha, record_counts, mw_path, mw_sha):
    a = [r for r in rows if r["population"] == "A"]
    table = []
    for d in range(3, 11):
        sub = [r for r in a if r["markupSegments"] == d]
        if not sub:
            continue
        ok = [r for r in sub if r["status"] == "ok"]
        k2 = sum(1 for r in ok if r["modelSegments"] == 2)
        trunc = [r for r in sub if r["status"] == "truncated"]
        empty = [r for r in sub if r["status"] == "empty"]
        garbage = [r for r in sub if r["status"] == "garbage"]
        # A truncated row lost its first member: true depth >= returned + 1.
        # It can still be a 2-read only if it returned at most one token.
        trunc_can_be_2 = sum(1 for r in trunc if len(read_output_text(r.get("raw"), "")) <= 1)
        n = len(sub)
        # Manski-style bounds on p2 over all rows (not only valid).
        lower_k = k2
        upper_k = k2 + trunc_can_be_2 + len(empty) + len(garbage)
        # Same bounds expressed on the valid denominator, to show what the
        # 47.3 % cell can move to under any assumption about missingness.
        valid_n = len(ok)
        lower_valid = k2 / valid_n if valid_n else None
        # If every eligible unknown row were valid and read 2, the valid set grows.
        upper_valid = (k2 + trunc_can_be_2 + len(empty) + len(garbage)) / \
            (valid_n + trunc_can_be_2 + len(empty) + len(garbage)) \
            if (valid_n + trunc_can_be_2 + len(empty) + len(garbage)) else None
        table.append({
            "markupDepth": d,
            "rows": n,
            "valid": valid_n,
            "reads2": k2,
            "p2OfValid": share(k2, valid_n),
            "p2OfValidCi95": wilson(k2, valid_n),
            "truncated": len(trunc),
            "truncatedCouldBe2": trunc_can_be_2,
            "empty": len(empty),
            "garbage": len(garbage),
            "p2LowerAllRows": share(lower_k, n),
            "p2UpperAllRows": share(upper_k, n),
            "p2LowerAllRowsCi95": wilson(lower_k, n),
            "p2UpperAllRowsCi95": wilson(upper_k, n),
            "p2LowerValidDenominator": round(lower_valid, 4) if lower_valid is not None else None,
            "p2UpperEligibleValidDenominator": round(upper_valid, 4) if upper_valid is not None else None,
            "censoringRule": ("truncated true depth >= returned+1, so only returned<=1 "
                              "rows remain candidates for a 2-read; empty/garbage unbounded"),
        })
    return {
        "schemaVersion": "1.0.0",
        "generatedAt": GENERATED_AT,
        "generatedBy": GENERATED_BY,
        "question": "Q10: Wilson CI for p2 plus censoring bounds, markup depths 3-8",
        "source": {"snapshot": str(SNAPSHOT.relative_to(ROOT)), "sha256": snapshot_sha,
                   "markupRecordsFrom": str(mw_path), "markupRecordsSha256": mw_sha},
        "method": {
            "p2": "share of valid rows the model reads as exactly 2 members",
            "ci": "Wilson score interval, 95 %",
            "bounds": "Manski worst-case over non-valid rows, narrowed by the truncation rule",
            "why": ("truncation drops the first member, so missingness is depth-correlated; "
                    "the bounds state exactly what the missing rows can and cannot move"),
        },
        "table": table,
        "reading": ("The published 47.3 % (CI 45.8-48.7) is the markup-depth-3 cell; "
                    "its censoring upper bound is in the table and is the number to quote "
                    "when the missing third of rows is treated adversarially."),
    }


def join(rows, mw_path, pwg_path):
    mw = load_headwords(mw_path)
    pwg = load_headwords(pwg_path)
    a = [r for r in rows if r["population"] == "A" and r["markupSegments"] == 3
         and r["status"] == "ok" and r["modelSegments"] == 2]
    out = []
    for r in a:
        segs = segments(r["k2"])
        if len(segs) < 2:
            continue
        first_two = "".join(segs[:2])
        in_mw = first_two in mw
        in_pwg = first_two in pwg
        match = "both" if in_mw and in_pwg else "mw" if in_mw else "pwg" if in_pwg else "none"
        out.append({
            "surface": r["surface"],
            "k2": r["k2"],
            "mwLine": r.get("line"),
            "firstTwo": first_two,
            "third": "".join(segs[2:]),
            "modelRaw": r.get("raw"),
            "match": match,
            "residual": "" if match != "none" else "no_mw_or_pwg_headword",
        })
    out.sort(key=lambda x: (x["k2"], x["surface"]))
    n = len(out)
    matched = sum(1 for x in out if x["match"] != "none")
    lines = ["surface\tk2\tmw_line\tfirst_two_joined\tthird_member\tmodel_raw\tmatch\tresidual"]
    for x in out:
        lines.append("\t".join(str(x[k]) for k in
                               ("surface", "k2", "mwLine", "firstTwo", "third",
                                "modelRaw", "match", "residual")))
    JOIN_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    digest = hashlib.sha256(JOIN_OUT.read_bytes()).hexdigest()
    summary = {
        "schemaVersion": "1.0.0",
        "generatedAt": GENERATED_AT,
        "generatedBy": GENERATED_BY,
        "question": "Q11: deterministic MW/PWG headword join of the 2,121 markup-3 rows read as 2",
        "rows": n,
        "matched": matched,
        "matchRate": share(matched, n),
        "matchRateCi95": wilson(matched, n),
        "bySource": dict(sorted(Counter(x["match"] for x in out).items())),
        "residuals": [{"surface": x["surface"], "k2": x["k2"], "firstTwo": x["firstTwo"]}
                      for x in out if x["match"] == "none"],
        "tsv": {"path": str(JOIN_OUT.relative_to(ROOT)), "sha256": digest},
        "inputs": {"snapshot": str(SNAPSHOT.relative_to(ROOT)),
                   "mw": str(mw_path), "pwg": str(pwg_path),
                   "mwHeadwords": len(mw), "pwgHeadwords": len(pwg)},
        "method": ("plain SLP1 concatenation of the first two em-dash members "
                   "(no sandhi rewrite); a hit means the lexicalised pair is an "
                   "independent dictionary headword. Sorted by (k2, surface)."),
    }
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csl-orig", default=str(ROOT.parent / "csl-orig"),
                    help="csl-orig checkout (default: sibling of the worktree)")
    ap.add_argument("--mw", default=None)
    ap.add_argument("--pwg", default=None)
    args = ap.parse_args()
    mw_path = Path(args.mw or Path(args.csl_orig) / "v02" / "mw" / "mw.txt")
    pwg_path = Path(args.pwg or Path(args.csl_orig) / "v02" / "pwg" / "pwg.txt")
    for p in (mw_path, pwg_path):
        if not p.exists():
            sys.exit(f"missing headword inventory: {p}")

    snap, rows, sha = load_snapshot()
    record_counts = load_records_by_depth(mw_path)
    mw_sha = hashlib.sha256(mw_path.read_bytes()).hexdigest()
    dist = distribution(rows, sha, record_counts, mw_path, mw_sha)
    bnd = bounds(rows, sha, record_counts, mw_path, mw_sha)
    jn = join(rows, mw_path, pwg_path)
    DIST_OUT.write_text(json.dumps(dist, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    BOUNDS_OUT.write_text(json.dumps(bnd, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    JOIN_JSON.write_text(json.dumps(jn, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"snapshot {SNAPSHOT.name} sha256 {sha[:12]}; A rows "
          f"{dist['totals']['surfaces']:,} ({dist['totals']['valid']:,} valid)")
    for d, row in dist["markupDepths"].items():
        print(f"  markup {d}: {row['surfaces']:,} surfaces, valid {row['valid']:,} "
              f"({row['validRate'] or 0:.1%}), p2 {row['pRead2'] or 0:.1%}")
    print(f"IC 3+ among valid: {dist['totals']['modelRead3Plus']['n']:,} "
          f"({dist['totals']['modelRead3Plus']['shareOfValid'] or 0:.1%})")
    print(f"join: {jn['matched']:,}/{jn['rows']:,} = {jn['matchRate']:.1%} "
          f"(CI {jn['matchRateCi95'][0]:.1%}-{jn['matchRateCi95'][1]:.1%}), "
          f"residuals {len(jn['residuals'])}")
    print(f"wrote {DIST_OUT.relative_to(ROOT)}, {BOUNDS_OUT.relative_to(ROOT)}, "
          f"{JOIN_OUT.relative_to(ROOT)}, {JOIN_JSON.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
