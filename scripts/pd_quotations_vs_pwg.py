#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H6949 — PD versus PWG at the quotation level, for the same lemmas.

Both dictionaries are measured with the *same* unit rule
(scripts/lib/quotation_units.py): a quotation is a run of consecutive
``{#...#}`` blocks followed by a citation marker — an inline siglum in PD, an
``<ls>…</ls>`` tag in PWG — and an attestation is one citation marker (plus, in
PD, the bare further references that inherit a siglum after a ``;``).

    python scripts/pd_quotations_vs_pwg.py --pd /path/to/pd.txt --pwg /path/to/pwg.txt

Writes data/pd/pd_quotations_vs_pwg.tsv (one row per lemma present in both) and
refreshes the comparison block of data/pd/pd_quotations_summary.json.

The anchor is Wright 1978 (BSOAS 41(2), 388–389) on *akāmataḥ*: PW three lines
and six Manu attestations against PD 47 lines, which he calls "a twelvefold
increase in bulk". This script tests that twelvefold basis.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import statistics
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts", "lib"))
import quotation_units

OUT_DIR = os.path.join(ROOT, "data", "pd")
OUT_TSV = os.path.join(OUT_DIR, "pd_quotations_vs_pwg.tsv")
SUMMARY = os.path.join(OUT_DIR, "pd_quotations_summary.json")
PD_TSV = os.path.join(OUT_DIR, "pd_quotations_by_entry.tsv")

DEFAULT_PD = os.environ.get(
    "PD_TXT",
    os.path.join(os.path.expanduser("~"), "Documents", "GitHub", "SanskritSpellCheck",
                 "external_src", "pd", "pd.txt"),
)
DEFAULT_PWG = os.environ.get(
    "PWG_TXT",
    os.path.join(os.path.dirname(ROOT), "csl-orig", "v02", "pwg", "pwg.txt"),
)

RE_HDR = re.compile(r"^<L>([\d.]+)<pc>([^<]*)<k1>([^<\s]*)<k2>([^<\s]*)")
RE_LS = re.compile(r"<ls([^>]*)>(.*?)</ls>", re.S)
RE_LS_N = re.compile(r'n="([^"]*)"')

# PWG's machine text has no printed-line markup (one long line per entry), so a
# printed-line ratio is not measurable on its side; Wright 1978 supplies PW's
# three printed lines as an external witness and only PD's 47 are counted here.
COLUMNS = [
    "k1", "pd_entries", "pd_quotations", "pd_attestations", "pd_lines",
    "pwg_entries", "pwg_quotations", "pwg_attestations",
    "quotation_ratio", "attestation_ratio",
]


def iter_entries(path):
    cur = None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith("<L>"):
                if cur is not None:
                    yield cur[0], cur[1]
                cur = [line, []]
            elif cur is not None:
                if line.startswith("<LEND>"):
                    yield cur[0], cur[1]
                    cur = None
                else:
                    cur[1].append(line)
    if cur is not None:
        yield cur[0], cur[1]


def pwg_marker(tail):
    """PWG citation marker: an <ls> tag, whose payload is the locus."""
    hits = RE_LS.findall(tail)
    return len(hits), 0, [a + ">" + b for a, b in hits]


def pwg_entry(body_lines):
    body = " ".join(body_lines).replace('<div n="lb">', " ")
    u = quotation_units.count_units(body, pwg_marker)
    return {
        "printed_lines": len(body_lines),
        "slp1_blocks": u["slp1_blocks"],
        "quotations": u["quotations"],
        "attestations": u["attestations"],
    }


def load_pd_counts(path):
    """Aggregate the committed per-entry TSV by k1."""
    agg = {}
    with open(path, encoding="utf-8") as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        idx = {c: i for i, c in enumerate(hdr)}
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) < len(hdr):
                continue
            k1 = f[idx["k1"]]
            a = agg.setdefault(k1, {"entries": 0, "quotations": 0, "attestations": 0, "lines": 0})
            a["entries"] += 1
            a["quotations"] += int(f[idx["quotations"]])
            a["attestations"] += int(f[idx["attestations"]])
            a["lines"] += int(f[idx["printed_lines"]])
    return agg


def load_pwg_counts(path):
    agg = {}
    total_ls = 0
    total_quotations = 0
    total_lines = 0
    entries = 0
    for hdr, body in iter_entries(path):
        m = RE_HDR.match(hdr)
        if not m:
            continue
        k1 = m.group(3)
        rec = pwg_entry(body)
        nls = len(RE_LS.findall(" ".join(body)))
        total_ls += nls
        total_quotations += rec["quotations"]
        total_lines += rec["printed_lines"]
        entries += 1
        a = agg.setdefault(k1, {"entries": 0, "quotations": 0, "attestations": 0, "lines": 0})
        a["entries"] += 1
        a["quotations"] += rec["quotations"]
        a["attestations"] += rec["attestations"]
        a["lines"] += rec["printed_lines"]
    return agg, {"entries": entries, "ls_tags": total_ls,
                 "quotations": total_quotations, "machine_text_lines": total_lines}


def ratio(a, b):
    return round(a / b, 3) if b else ""


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def anchor_detail(pd_path, pwg_path, lemma="akAmatas"):
    """The Manu loci PD and PWG actually carry for the anchor lemma."""
    out = {"pd_manu_loci": [], "pwg_manu_loci": [], "pd_quotations": 0, "pwg_quotations": 0}
    for hdr, body in iter_entries(pd_path):
        m = RE_HDR.match(hdr)
        if not m or m.group(3) != lemma:
            continue
        text = " ".join(body).replace('<div n="lb">', " ")
        for hit in re.finditer(r"ManuSm\.\s*([\d.\s;]+)", text):
            nums = [n for n in re.findall(r"\d+(?:\.\s*\d+)*", hit.group(1))]
            for n in nums:
                lone = re.sub(r"[\s.]+", ".", n).strip(".")
                if lone and lone not in out["pd_manu_loci"]:
                    out["pd_manu_loci"].append(lone)
    for hdr, body in iter_entries(pwg_path):
        m = RE_HDR.match(hdr)
        if not m or m.group(3) != lemma:
            continue
        for attr, payload in RE_LS.findall(" ".join(body)):
            n = RE_LS_N.search(attr)
            locus = ((n.group(1) if n else "") + payload).replace(" ", "")
            if locus.startswith("M."):
                out["pwg_manu_loci"].append(locus)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pd", default=DEFAULT_PD)
    ap.add_argument("--pwg", default=DEFAULT_PWG)
    ap.add_argument("--out-dir", default=OUT_DIR)
    args = ap.parse_args(argv)

    for p, label in ((args.pd, "pd.txt"), (args.pwg, "pwg.txt")):
        if not os.path.exists(p):
            sys.exit(f"{label} not found: {p}")

    pd_agg = load_pd_counts(os.path.join(args.out_dir, os.path.basename(PD_TSV)))
    pwg_agg, pwg_tot = load_pwg_counts(args.pwg)

    shared = sorted(set(pd_agg) & set(pwg_agg))
    rows = []
    for k1 in shared:
        pd, pwg = pd_agg[k1], pwg_agg[k1]
        rows.append({
            "k1": k1,
            "pd_entries": pd["entries"], "pd_quotations": pd["quotations"],
            "pd_attestations": pd["attestations"], "pd_lines": pd["lines"],
            "pwg_entries": pwg["entries"], "pwg_quotations": pwg["quotations"],
            "pwg_attestations": pwg["attestations"],
            "quotation_ratio": ratio(pd["quotations"], pwg["quotations"]),
            "attestation_ratio": ratio(pd["attestations"], pwg["attestations"]),
        })
    rows.sort(key=lambda r: (-(r["attestation_ratio"] or 0), r["k1"]))

    out_tsv = os.path.join(args.out_dir, os.path.basename(OUT_TSV))
    with open(out_tsv, "w", encoding="utf-8", newline="") as fh:
        fh.write("\t".join(COLUMNS) + "\n")
        for r in rows:
            fh.write("\t".join(str(r[c]) for c in COLUMNS) + "\n")

    att_ratios = sorted(r["attestation_ratio"] for r in rows
                        if isinstance(r["attestation_ratio"], float))
    quo_ratios = sorted(r["quotation_ratio"] for r in rows
                        if isinstance(r["quotation_ratio"], float))
    anchor = anchor_detail(args.pd, args.pwg)

    def pct(v, p):
        if not v:
            return 0
        return v[min(len(v) - 1, round(p / 100.0 * (len(v) - 1)))]

    pd_tot = {k: sum(a[k] for a in pd_agg.values()) for k in ("entries", "quotations", "attestations", "lines")}
    comparison = {
        "unit": "same rule both sides (scripts/lib/quotation_units.py); PD marker = inline "
                "siglum + inherited further references, PWG marker = <ls> tag",
        "pwg_totals": pwg_tot,
        "pd_totals": pd_tot,
        "shared_lemmas": len(shared),
        "pd_only_lemmas": len(set(pd_agg) - set(pwg_agg)),
        "pwg_only_lemmas": len(set(pwg_agg) - set(pd_agg)),
        "attestation_ratio": {
            "median": statistics.median(att_ratios) if att_ratios else 0,
            "mean": round(sum(att_ratios) / len(att_ratios), 3) if att_ratios else 0,
            "p25": pct(att_ratios, 25), "p75": pct(att_ratios, 75),
            "share_ge_12": round(100.0 * sum(1 for v in att_ratios if v >= 12) / len(att_ratios), 1)
            if att_ratios else 0,
        },
        "quotation_ratio": {
            "median": statistics.median(quo_ratios) if quo_ratios else 0,
            "mean": round(sum(quo_ratios) / len(quo_ratios), 3) if quo_ratios else 0,
        },
        "aggregate_over_shared_lemmas": {
            "pd_attestations": sum(r["pd_attestations"] for r in rows),
            "pwg_attestations": sum(r["pwg_attestations"] for r in rows),
            "attestation_ratio": ratio(sum(r["pd_attestations"] for r in rows),
                                       sum(r["pwg_attestations"] for r in rows)),
            "pd_quotations": sum(r["pd_quotations"] for r in rows),
            "pwg_quotations": sum(r["pwg_quotations"] for r in rows),
            "quotation_ratio": ratio(sum(r["pd_quotations"] for r in rows),
                                     sum(r["pwg_quotations"] for r in rows)),
        },
        "attestation_ratio_buckets": {
            "lt_1": sum(1 for v in att_ratios if v < 1),
            "1_to_3": sum(1 for v in att_ratios if 1 <= v < 3),
            "3_to_12": sum(1 for v in att_ratios if 3 <= v < 12),
            "ge_12": sum(1 for v in att_ratios if v >= 12),
        },
        "anchor_akamatas": {
            "wright": "PW three lines, six Manu attestations; PD 47 lines; "
                      "'a twelvefold increase in bulk' (BSOAS 41(2), 388-389)",
            "pd": {k: pd_agg["akAmatas"][k] for k in pd_agg["akAmatas"]}
            if "akAmatas" in pd_agg else {},
            "pwg": {k: pwg_agg["akAmatas"][k] for k in pwg_agg["akAmatas"]}
            if "akAmatas" in pwg_agg else {},
            "manu_loci": anchor,
        },
        "inputs": {
            "pd_sha256": sha256(args.pd),
            "pwg_sha256": sha256(args.pwg),
        },
    }

    if os.path.exists(SUMMARY):
        with open(SUMMARY, encoding="utf-8") as fh:
            summary = json.load(fh)
    else:
        summary = {}
    summary["comparison_pwg"] = comparison
    with open(SUMMARY, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    print(f"shared lemmas={len(shared)}  PWG ls total={pwg_tot['ls_tags']:,} "
          f"PD attestations={pd_tot['attestations']:,}")
    print(f"attestation ratio: median={comparison['attestation_ratio']['median']} "
          f"mean={comparison['attestation_ratio']['mean']} "
          f"share>=12x={comparison['attestation_ratio']['share_ge_12']}%")
    a = comparison["anchor_akamatas"]
    print(f"akAmatas  PD {a['pd']}  PWG {a['pwg']}")
    print(f"  PD Manu loci: {anchor['pd_manu_loci']}")
    print(f"  PWG Manu loci: {anchor['pwg_manu_loci']}")
    print(f"wrote {out_tsv}\nupdated {os.path.join(args.out_dir, os.path.basename(SUMMARY))}")


if __name__ == "__main__":
    main()
