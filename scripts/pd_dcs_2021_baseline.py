#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The 2021 DCS baseline: like-for-like against the raw text set.

19-10-2026, for the A68 §5.4 delta. DCS-2021 carried six texts that DCS-2026
does not — four commentaries (Cakra on Suśr, Comm. on the Kāvyālaṃkāravṛtti,
Hārāṇacandara on Suśr, Khādiragṛhyasūtrarudraskandavyākhyā) and two zero-token
stubs (Ekākṣarakoṣa, Nāḍīvijñāna) — carrying **892 tokens** between them.

The committed metric already excludes them: the frozen spine's
``total_dcs_tok_2021 = 4,577,021`` is the 2021 token sum *without* those six,
against 4,577,913 with them, so the published 74.06 % (74.1 %) is the
like-for-like baseline and 74.04 % (74.0 %) is the raw one. This probe makes
both ends reproducible, so the manuscript can name which one it quotes.

    python scripts/pd_dcs_2021_baseline.py

Writes ``data/pd/pd_dcs_2021_baseline.json``. Read-only over the committed
crosswalk and the VisualDCS per-text delta table.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "pd", "pd_dcs_2021_baseline.json")
CROSSWALK = os.path.join(ROOT, "data", "pd", "pd_dcs_text_crosswalk.tsv")
SPINE = os.path.join(ROOT, "data", "pd", "pd_dcs_metrics.json")
DEFAULT_DELTA = os.path.expanduser(
    "~/Documents/GitHub/VisualDCS/derived-data/Corpus-Delta-2021-2026/per_text_token_delta.csv")

# The frozen spine (data/pd/pd_dcs_metrics.json) — the numbers the A68 canary
# pins. A probe that does not reproduce them is a broken probe, not news.
COMMITTED = {
    "total_dcs_tok_2021": 4577021,
    "total_dcs_tok_2026": 5688416,
    "covered_dcs_tok_2021": 3389516,
    "covered_dcs_tok_2026": 4430111,
    "metric_dcs_token_weighted_2021_pct": 74.06,
    "metric_dcs_token_weighted_2026_pct": 77.88,
}


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def num(raw) -> int:
    raw = (raw or "").strip()
    return int(raw) if raw.isdigit() else 0


def is_commentary(title: str) -> bool:
    """A dropped text is a commentary when its title names one."""
    t = (title or "").strip()
    return t.startswith("Comm.") or " on " in t or t.endswith("vyākhyā")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--delta", default=os.environ.get("DCS_DELTA_CSV", DEFAULT_DELTA))
    ap.add_argument("--crosswalk", default=CROSSWALK)
    ap.add_argument("--spine", default=SPINE)
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()

    with open(args.delta, encoding="utf-8") as fh:
        delta = list(csv.DictReader(fh))
    with open(args.crosswalk, encoding="utf-8") as fh:
        cov = list(csv.DictReader(fh, delimiter="\t"))

    raw_2021 = sum(num(r["tok_2021"]) for r in delta)
    raw_2026 = sum(num(r["tok_2026"]) for r in delta)
    only_2021 = [r for r in delta if not (r["text_2026"] or "").strip()]
    dropped_tokens = sum(num(r["tok_2021"]) for r in only_2021)
    like_2021 = raw_2021 - dropped_tokens

    covered_2021 = sum(num(r["dcs_tok_2021"]) for r in cov)
    covered_2026 = sum(num(r["dcs_tok_2026"]) for r in cov)

    raw_pct = covered_2021 / raw_2021 * 100
    like_pct = covered_2021 / like_2021 * 100
    pct_2026 = covered_2026 / raw_2026 * 100

    spine = json.load(open(args.spine, encoding="utf-8"))
    checks = {
        "total_dcs_tok_2021": (like_2021, spine["total_dcs_tok_2021"]),
        "total_dcs_tok_2026": (raw_2026, spine["total_dcs_tok_2026"]),
        "covered_dcs_tok_2021": (covered_2021, spine["covered_dcs_tok_2021"]),
        "covered_dcs_tok_2026": (covered_2026, spine["covered_dcs_tok_2026"]),
        "metric_dcs_token_weighted_2021_pct": (round(like_pct, 2),
                                               spine["metric_dcs_token_weighted_2021_pct"]),
        "metric_dcs_token_weighted_2026_pct": (round(pct_2026, 2),
                                               spine["metric_dcs_token_weighted_2026_pct"]),
    }

    out = {
        "dataset": "pd_dcs_2021_baseline",
        "created": "2026-10-19",
        "why": ("name which 2021 baseline the A68 §5.4 delta quotes: the like-for-like "
                "one (the six texts DCS-2021 carried and DCS-2026 dropped are excluded "
                "from the 2021 denominator) or the raw one"),
        "sources": {
            "delta_csv": {"path": args.delta, "bytes": os.path.getsize(args.delta),
                          "sha256": sha256(args.delta), "rows": len(delta)},
            "crosswalk": {"path": args.crosswalk, "sha256": sha256(args.crosswalk),
                          "rows": len(cov)},
            "spine": {"path": args.spine, "sha256": sha256(args.spine)},
        },
        "dropped_since_2021": {
            "count": len(only_2021),
            "tokens_2021": dropped_tokens,
            "commentaries": sum(1 for r in only_2021 if is_commentary(r["text_2021"])),
            "zero_token_stubs": sum(1 for r in only_2021 if num(r["tok_2021"]) == 0),
            "rows": [{"text_2021": r["text_2021"], "tok_2021": num(r["tok_2021"]),
                      "class": "commentary" if is_commentary(r["text_2021"]) else "stub"}
                     for r in only_2021],
        },
        "totals": {
            "total_dcs_tok_2021_raw": raw_2021,
            "total_dcs_tok_2021_like_for_like": like_2021,
            "total_dcs_tok_2026": raw_2026,
            "covered_dcs_tok_2021": covered_2021,
            "covered_dcs_tok_2026": covered_2026,
        },
        "baselines": {
            "like_for_like_2021_pct": round(like_pct, 2),
            "raw_2021_pct": round(raw_pct, 2),
            "pct_2026": round(pct_2026, 2),
            "delta_like_for_like_pp": round(pct_2026 - like_pct, 2),
            "delta_raw_pp": round(pct_2026 - raw_pct, 2),
        },
        "committed_checks": {
            key: {"measured": m, "committed": c, "ok": m == c} for key, (m, c) in checks.items()
        },
        "reading": ("the committed spine (and therefore the A68 canary) holds the LIKE-FOR-LIKE "
                    "baseline: 74.06 % (74.1 %). The raw 2021 baseline, keeping the six texts "
                    "DCS-2026 dropped, is 74.04 % (74.0 %). Both deltas to 2026 round to +3.8 pp."),
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")

    d = out["dropped_since_2021"]
    print("DCS 2021 baseline")
    print(f"  dropped since 2021 .. {d['count']} texts, {d['tokens_2021']} tokens "
          f"({d['commentaries']} commentaries, {d['zero_token_stubs']} zero-token stubs)")
    for r in d["rows"]:
        print(f"     - {r['text_2021']}  ({r['tok_2021']} tok, {r['class']})")
    print(f"  total 2021 raw ....... {raw_2021:,}")
    print(f"  total 2021 like-for-like {like_2021:,}   <- the committed denominator")
    print(f"  covered 2021 ......... {covered_2021:,}")
    print(f"  baseline like-for-like  {like_pct:.4f} %  -> {like_pct:.1f} %")
    print(f"  baseline raw ......... {raw_pct:.4f} %  -> {raw_pct:.1f} %")
    print(f"  2026 ................. {pct_2026:.4f} %  -> {pct_2026:.1f} %")
    print(f"  delta like-for-like ... +{pct_2026 - like_pct:.2f} pp ; raw +{pct_2026 - raw_pct:.2f} pp")
    print("  committed checks: " + ", ".join(
        f"{k}={'ok' if v['ok'] else 'DRIFT'}" for k, v in out["committed_checks"].items()))
    print(f"  wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
