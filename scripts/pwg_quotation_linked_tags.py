#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PWG ``<ls>`` tags: the raw count against the quotation-linked count.

19-10-2026, for the A68 four-ledger table. The quotation-unit report
(``reports/PD_QUOTATION_UNIT_2026-10-18.md``) prints PWG's **801,788** as
"``<ls>`` attestations", but 801,788 is the **raw tag count** in ``pwg.txt``:
the unit's own counter (``scripts/lib/quotation_units.py``) only counts an
``<ls>`` tag that *closes a quotation* — a run of consecutive ``{#...#}``
blocks followed by a citation marker. The two numbers are different objects
and the report used one word for both.

This probe separates them and classifies the residue, so that any table which
compares PD's 419,890 attestations with PWG can name the denominator it uses.

    python scripts/pwg_quotation_linked_tags.py

Writes ``data/pd/pwg_quotation_linked_tags.json``. Read-only over the PWG
machine text.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "scripts", "lib"))

import pd_quotations_vs_pwg as pvg  # noqa: E402  (the committed PWG reader)

OUT = os.path.join(ROOT, "data", "pd", "pwg_quotation_linked_tags.json")

# Committed values the probe must reproduce (reports/PD_QUOTATION_UNIT_2026-10-18.md
# §4, and the H6949 changelog row). Any drift here is a broken probe, not news.
COMMITTED = {
    "entries": 123366,
    "raw_ls_tags": 801788,
    "quotations": 329623,
}


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pwg", default=os.environ.get("PWG_TXT", pvg.DEFAULT_PWG))
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()

    entries = raw_tags = linked = quotations = 0
    residue_tags = 0
    entries_with_residue = 0
    residue_sample = []
    zero_quote_entries = 0
    per_entry_residue = {}

    for hdr, body in pvg.iter_entries(args.pwg):
        if not pvg.RE_HDR.match(hdr):
            continue
        k1 = pvg.RE_HDR.match(hdr).group(3)
        text = " ".join(body)
        n_tags = len(pvg.RE_LS.findall(text))
        rec = pvg.pwg_entry(body)
        entries += 1
        raw_tags += n_tags
        linked += rec["attestations"]
        quotations += rec["quotations"]
        diff = n_tags - rec["attestations"]
        if diff:
            residue_tags += diff
            entries_with_residue += 1
            per_entry_residue[k1] = diff
            if rec["quotations"] == 0:
                zero_quote_entries += 1
            if len(residue_sample) < 25:
                residue_sample.append({
                    "k1": k1,
                    "raw_tags": n_tags,
                    "quotation_linked": rec["attestations"],
                    "quotations": rec["quotations"],
                    "residue": diff,
                })

    out = {
        "dataset": "pwg_quotation_linked_tags",
        "created": "2026-10-19",
        "why": ("separate the raw <ls> tag count from the quotation-linked count "
                "(the unit's attestations) so the A68 four-ledger table can name "
                "its denominator"),
        "source": {
            "path": args.pwg,
            "bytes": os.path.getsize(args.pwg),
            "sha256": sha256(args.pwg),
        },
        "rule": ("an <ls> tag counts as a quotation-linked attestation only when it "
                 "closes a run of consecutive {#...#} blocks "
                 "(scripts/lib/quotation_units.py)"),
        "totals": {
            "entries": entries,
            "raw_ls_tags": raw_tags,
            "quotation_linked_attestations": linked,
            "non_quotation_linked_tags": raw_tags - linked,
            "quotations": quotations,
        },
        "residue": {
            "tags": residue_tags,
            "entries_with_residue": entries_with_residue,
            "entries_with_residue_and_no_quotation": zero_quote_entries,
            "share_of_raw_tags": round(residue_tags / raw_tags * 100, 2) if raw_tags else None,
            "sample": residue_sample,
        },
        "committed_checks": {
            key: {"committed": COMMITTED[key], "measured": measured, "ok": measured == COMMITTED[key]}
            for key, measured in (
                ("entries", entries),
                ("raw_ls_tags", raw_tags),
                ("quotations", quotations),
            )
        },
        "ratios": {
            "pd_attestations_over_raw_pwg_tags": round(419890 / raw_tags * 100, 1) if raw_tags else None,
            "pd_attestations_over_quotation_linked_pwg_tags":
                round(419890 / linked * 100, 1) if linked else None,
            "pd_quotations_over_pwg_quotations": round(302442 / quotations * 100, 1) if quotations else None,
        },
        "provenance": {
            "pd_attestations": 419890,
            "pd_quotations": 302442,
            "pd_source": ("reports/PD_QUOTATION_UNIT_2026-10-18.md — PD letter-a canon, "
                          "measured with the same unit"),
        },
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")

    t = out["totals"]
    print("PWG <ls> tags — raw vs quotation-linked")
    print(f"  entries ................. {t['entries']:,}")
    print(f"  raw <ls> tags .......... {t['raw_ls_tags']:,}")
    print(f"  quotation-linked ....... {t['quotation_linked_attestations']:,}")
    print(f"  not quotation-linked ... {t['non_quotation_linked_tags']:,} "
          f"({out['residue']['share_of_raw_tags']} % of raw) in "
          f"{out['residue']['entries_with_residue']:,} entries")
    print(f"  quotations ............. {t['quotations']:,}")
    print("  committed checks: " + ", ".join(
        f"{k}={'ok' if v['ok'] else 'DRIFT'}" for k, v in out["committed_checks"].items()))
    print(f"  PD 419,890 over raw {raw_tags:,} = {out['ratios']['pd_attestations_over_raw_pwg_tags']} %")
    print(f"  PD 419,890 over linked {linked:,} = {out['ratios']['pd_attestations_over_quotation_linked_pwg_tags']} %")
    print(f"  wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
