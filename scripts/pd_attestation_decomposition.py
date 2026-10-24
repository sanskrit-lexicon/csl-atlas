#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7095 — split the PD/PWG attestation ratio into breadth x depth.

Attestations = loci on both sides (H6949 unit), so breadth x depth = 8.55x.
``raw`` merges nothing; ``fold`` applies a diacritic/case/punctuation skeleton
and is the headline.  Writes data/pd/pd_attestation_decomposition.{tsv,json};
``--check`` re-derives both files, the 20 gold rows and the report numbers.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import statistics
import sys
import unicodedata

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts", "lib"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import quotation_units  # noqa: E402
import pd_quotation_units as pqu  # noqa: E402

DATA = os.path.join(ROOT, "data", "pd")
OUT_TSV = os.path.join(DATA, "pd_attestation_decomposition.tsv")
OUT_JSON = os.path.join(DATA, "pd_attestation_decomposition.json")
VS_TSV = os.path.join(DATA, "pd_quotations_vs_pwg.tsv")
CLASSES_TSV = os.path.join(DATA, "pd_siglum_families.tsv")
GOLD_TSV = os.path.join(ROOT, "tests", "forensic",
                        "h7095_pd_attestation_decomposition_gold.tsv")
REPORT = os.path.join(ROOT, "reports", "PD_ATTESTATION_DECOMPOSITION_2026.md")

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
RE_DIGIT = re.compile(r"[0-9].*")
RE_QUALIFIER = re.compile(r"\([^)]*\)$")

RECONCILE = {
    "pd_attestations": 157480,
    "pwg_attestations": 18423,
    "pd_quotations": 97413,
    "pwg_quotations": 10225,
    "shared_lemmas": 4093,
}
TOLERANCE = 0.001  # 0.1 %

COLUMNS = [
    "k1", "pd_quotations", "pwg_quotations", "pd_attestations", "pwg_attestations",
    "pd_loci", "pwg_loci",
    "pd_distinct_works_raw", "pwg_distinct_works_raw",
    "pd_distinct_works_fold", "pwg_distinct_works_fold",
    "breadth_ratio_raw", "depth_ratio_raw",
    "breadth_ratio_fold", "depth_ratio_fold", "attestation_ratio",
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


def fold_siglum(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", s.lower())


def load_classes(path):
    classes = {}
    with open(path, encoding="utf-8") as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        si, ci = hdr.index("siglum"), hdr.index("class")
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) > max(si, ci):
                classes[f[si]] = f[ci]
    return classes


def normalize_siglum(tok):
    base = RE_QUALIFIER.sub("", tok).strip()
    if base and not base.endswith("."):
        base += "."
    return base


def primary_form(tok, classes):
    if classes.get(tok) == "primary":
        return tok
    base = normalize_siglum(tok)
    if classes.get(base) == "primary":
        return base
    return None


def pwg_siglum(attr, payload):
    n = RE_LS_N.search(attr)
    text = ((n.group(1) if n else "") + payload).replace(" ", "")
    return RE_DIGIT.sub("", text).strip(" .,;:()[]-–—")


def pwg_marker(tail):
    hits = RE_LS.findall(tail)
    return len(hits), 0, [pwg_siglum(a, b) for a, b in hits]


def parse_side(path, marker, classes=None):
    out = {}
    for hdr, body in iter_entries(path):
        m = RE_HDR.match(hdr)
        if not m:
            continue
        k1 = m.group(3)
        u = quotation_units.count_units(
            " ".join(body).replace('<div n="lb">', " "), marker)
        rec = out.setdefault(k1, {"quotations": 0, "attestations": 0, "loci": 0,
                                  "raw": set(), "fold": set()})
        rec["quotations"] += u["quotations"]
        rec["attestations"] += u["attestations"]
        rec["loci"] += u["loci"] + u["continuation_loci"]
        for tok in u["tokens"]:
            ok = bool(tok) if classes is None else primary_form(tok, classes) is not None
            if ok:
                rec["raw"].add(tok)
                rec["fold"].add(fold_siglum(tok))
    return out


def load_shared(path):
    shared = []
    with open(path, encoding="utf-8") as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        ki = hdr.index("k1")
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) == len(hdr):
                shared.append(f[ki])
    return shared


def ratio(a, b):
    return round(a / b, 4) if b else ""


def pct(values, p):
    if not values:
        return 0
    v = sorted(values)
    return v[min(len(v) - 1, round(p / 100.0 * (len(v) - 1)))]


def build(pd_path, pwg_path):
    classes = load_classes(CLASSES_TSV)
    shared = load_shared(VS_TSV)
    pd = parse_side(pd_path, pqu.citation_tail, classes)
    pwg = parse_side(pwg_path, pwg_marker)

    rows = []
    for k1 in shared:
        p = pd.get(k1, {"quotations": 0, "attestations": 0, "loci": 0,
                        "raw": set(), "fold": set()})
        w = pwg.get(k1, {"quotations": 0, "attestations": 0, "loci": 0,
                         "raw": set(), "fold": set()})
        rows.append({
            "k1": k1,
            "pd_quotations": p["quotations"], "pwg_quotations": w["quotations"],
            "pd_attestations": p["attestations"], "pwg_attestations": w["attestations"],
            "pd_loci": p["loci"], "pwg_loci": w["loci"],
            "pd_distinct_works_raw": len(p["raw"]), "pwg_distinct_works_raw": len(w["raw"]),
            "pd_distinct_works_fold": len(p["fold"]), "pwg_distinct_works_fold": len(w["fold"]),
            "breadth_ratio_raw": ratio(len(p["raw"]), len(w["raw"])),
            "depth_ratio_raw": ratio((p["loci"] / len(p["raw"])) if p["raw"] else 0,
                                     (w["loci"] / len(w["raw"])) if w["raw"] else 0),
            "breadth_ratio_fold": ratio(len(p["fold"]), len(w["fold"])),
            "depth_ratio_fold": ratio((p["loci"] / len(p["fold"])) if p["fold"] else 0,
                                      (w["loci"] / len(w["fold"])) if w["fold"] else 0),
            "attestation_ratio": ratio(p["attestations"], w["attestations"]),
        })

    pd_att = sum(r["pd_attestations"] for r in rows)
    pwg_att = sum(r["pwg_attestations"] for r in rows)
    pd_q = sum(r["pd_quotations"] for r in rows)
    pwg_q = sum(r["pwg_quotations"] for r in rows)
    pd_loci = sum(r["pd_loci"] for r in rows)
    pwg_loci = sum(r["pwg_loci"] for r in rows)
    attestation_ratio = pd_att / pwg_att

    def side(name):
        if name == "raw":
            dr, wr = "pd_distinct_works_raw", "pwg_distinct_works_raw"
        else:
            dr, wr = "pd_distinct_works_fold", "pwg_distinct_works_fold"
        d_union = len({t for k in shared if k in pd for t in
                       (pd[k]["raw"] if name == "raw" else pd[k]["fold"])})
        w_union = len({t for k in shared if k in pwg for t in
                       (pwg[k]["raw"] if name == "raw" else pwg[k]["fold"])})
        d_sum = sum(r[dr] for r in rows)
        w_sum = sum(r[wr] for r in rows)
        breadth = d_union / w_union if w_union else 0
        depth = (pd_loci / d_union) / (pwg_loci / w_union) if d_union and w_union else 0
        return {
            "pd_distinct_works_union": d_union,
            "pwg_distinct_works_union": w_union,
            "pd_distinct_sum_over_lemmas": d_sum,
            "pwg_distinct_sum_over_lemmas": w_sum,
            "pd_loci": pd_loci, "pwg_loci": pwg_loci,
            "pd_loci_per_work": round(pd_loci / d_union, 4) if d_union else 0,
            "pwg_loci_per_work": round(pwg_loci / w_union, 4) if w_union else 0,
            "breadth_ratio": round(breadth, 4),
            "depth_ratio": round(depth, 4),
            "breadth_x_depth": round(breadth * depth, 6),
        }

    def medians(name):
        br, dr, ar = [], [], []
        for r in rows:
            if name == "raw":
                d, w = r["pd_distinct_works_raw"], r["pwg_distinct_works_raw"]
            else:
                d, w = r["pd_distinct_works_fold"], r["pwg_distinct_works_fold"]
            if w:
                br.append(d / w)
                if d and r["pd_loci"] and r["pwg_loci"]:
                    dr.append((r["pd_loci"] / d) / (r["pwg_loci"] / w))
            if r["pwg_attestations"]:
                ar.append(r["pd_attestations"] / r["pwg_attestations"])

        def block(v):
            return {"n": len(v),
                    "median": round(statistics.median(v), 4) if v else 0,
                    "p25": round(pct(v, 25), 4), "p75": round(pct(v, 75), 4)}

        return {"breadth_ratio": block(br), "depth_ratio": block(dr),
                "attestation_ratio": block(ar)}

    below = [r for r in rows
             if r["pwg_attestations"] and r["pd_attestations"] / r["pwg_attestations"] < 1]
    zero_pd = [r for r in below if r["pd_attestations"] == 0]
    near = [r for r in below if r["pd_attestations"] > 0]
    diffs = {}
    for r in near:
        delta = r["pwg_attestations"] - r["pd_attestations"]
        diffs[delta] = diffs.get(delta, 0) + 1

    summary = {
        "dataset": "pd_attestation_decomposition",
        "handoff": "H7095",
        "generated_by": "python scripts/pd_attestation_decomposition.py",
        "generated_on": "2026-10-19",
        "population": {
            "shared_lemmas": len(shared),
            "pd_entries_scanned": len(pd),
            "pwg_entries_scanned": len(pwg),
            "unit": "H6949 quotation unit: attestation = locus = a PD siglum+locus "
                    "(plus semicolon continuations) or a PWG <ls> tag",
        },
        "conventions": {
            "pd_works": "A68 §4.2 class `primary` in data/pd/pd_siglum_families.tsv; "
                        "trailing commentary qualifiers stripped to the base siglum",
            "pwg_works": "distinct sigla of <ls> tags counted as loci (n attribute joined "
                         "to payload; prefix before the first digit)",
            "raw": "no variant merging; an upper bound on PD breadth",
            "fold": "diacritic/case/punctuation skeleton (fold_siglum); approximates "
                    "A68 §5.2's skeleton-merged work count and is the headline convention",
        },
        "reconciliation": {
            "shared_lemmas": len(shared),
            "pd_attestations": pd_att, "pwg_attestations": pwg_att,
            "pd_quotations": pd_q, "pwg_quotations": pwg_q,
            "pd_loci": pd_loci, "pwg_loci": pwg_loci,
            "attestations_equal_loci_pd": pd_att == pd_loci,
            "attestations_equal_loci_pwg": pwg_att == pwg_loci,
            "attestation_ratio": round(attestation_ratio, 3),
            "targets": RECONCILE,
            "within_tolerance": all(
                abs((pd_att if k == "pd_attestations" else
                     pwg_att if k == "pwg_attestations" else
                     pd_q if k == "pd_quotations" else
                     pwg_q if k == "pwg_quotations" else len(shared)) - v)
                <= max(1, v * TOLERANCE) for k, v in RECONCILE.items()),
        },
        "aggregate": {"raw": side("raw"), "fold": side("fold")},
        "per_lemma_medians": {"raw": medians("raw"), "fold": medians("fold")},
        "below_parity": {
            "n": len(below),
            "pct_of_shared": round(100.0 * len(below) / len(shared), 2),
            "zero_pd_attestations": len(zero_pd),
            "zero_pd_pwg_attestations": sum(r["pwg_attestations"] for r in zero_pd),
            "near_parity": len(near),
            "delta_histogram": {str(k): diffs[k] for k in sorted(diffs)},
            "delta_le_2": sum(v for k, v in diffs.items() if k <= 2),
            "pwg_zero_attestation_lemmas": sum(1 for r in rows if r["pwg_attestations"] == 0),
        },
        "gold_rows": {"path": os.path.relpath(GOLD_TSV, ROOT), "n": 20},
        "inputs": {
            "pd_sha256": sha256(pd_path),
            "pwg_sha256": sha256(pwg_path),
        },
    }
    return rows, summary


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_outputs(rows, summary, out_tsv, out_json):
    with open(out_tsv, "w", encoding="utf-8", newline="") as fh:
        fh.write("\t".join(COLUMNS) + "\n")
        for r in rows:
            fh.write("\t".join(str(r[c]) for c in COLUMNS) + "\n")
    with open(out_json, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


def committed_per_lemma_problems(rows):
    problems = []
    vs = {}
    with open(VS_TSV, encoding="utf-8") as fh:
        rd = csv.DictReader(fh, delimiter="\t")
        for r in rd:
            vs[r["k1"]] = r
    pd_agg = {}
    with open(os.path.join(DATA, "pd_quotations_by_entry.tsv"), encoding="utf-8") as fh:
        rd = csv.DictReader(fh, delimiter="\t")
        for r in rd:
            a = pd_agg.setdefault(r["k1"], {"quotations": 0, "attestations": 0})
            a["quotations"] += int(r["quotations"])
            a["attestations"] += int(r["attestations"])
    for r in rows:
        k = r["k1"]
        if k in vs:
            if (int(r["pwg_attestations"]) != int(vs[k]["pwg_attestations"]) or
                    int(r["pwg_quotations"]) != int(vs[k]["pwg_quotations"])):
                problems.append(f"{k}: PWG counts differ from pd_quotations_vs_pwg.tsv")
        else:
            problems.append(f"{k}: missing from pd_quotations_vs_pwg.tsv")
        a = pd_agg.get(k)
        if a is None:
            problems.append(f"{k}: missing from pd_quotations_by_entry.tsv")
        elif (r["pd_attestations"] != a["attestations"] or
              r["pd_quotations"] != a["quotations"]):
            problems.append(f"{k}: PD counts differ from pd_quotations_by_entry.tsv")
    return problems


def check_gold(rows):
    by_k1 = {r["k1"]: r for r in rows}
    problems = []
    seen = 0
    with open(GOLD_TSV, encoding="utf-8") as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        idx = {c: i for i, c in enumerate(hdr)}
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) < len(hdr):
                continue
            seen += 1
            r = by_k1.get(f[idx["k1"]])
            if r is None:
                problems.append(f"{f[idx['k1']]}: not a shared lemma")
                continue
            for c in hdr:
                if c in ("k1", "note"):
                    continue
                if str(r[c]) != f[idx[c]]:
                    problems.append(f"{r['k1']}.{c}: gold {f[idx[c]]} != {r[c]}")
    if seen != 20:
        problems.append(f"gold rows: {seen} != 20")
    return problems


def check_report(summary):
    with open(REPORT, encoding="utf-8") as fh:
        text = fh.read()
    rec = summary["reconciliation"]
    agg = summary["aggregate"]["fold"]
    raw = summary["aggregate"]["raw"]
    med = summary["per_lemma_medians"]["fold"]
    bp = summary["below_parity"]
    pinned = [
        f"{rec['pd_attestations']:,}", f"{rec['pwg_attestations']:,}",
        f"{rec['pd_quotations']:,}", f"{rec['pwg_quotations']:,}",
        f"{agg['breadth_ratio']:.2f}", f"{agg['depth_ratio']:.2f}",
        f"{rec['attestation_ratio']:.2f}",
        f"{raw['breadth_ratio']:.2f}", f"{raw['depth_ratio']:.2f}",
        f"{med['breadth_ratio']['median']:.1f}",
        f"{med['depth_ratio']['median']:.2f}",
        f"{bp['pct_of_shared']:.2f}%", str(bp["n"]),
        f"{agg['pd_distinct_works_union']:,}", f"{agg['pwg_distinct_works_union']:,}",
        f"{agg['pd_distinct_sum_over_lemmas']:,}",
        f"{agg['pwg_distinct_sum_over_lemmas']:,}",
    ]
    return [f"report missing {p}" for p in pinned if p not in text]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pd", default=DEFAULT_PD, help="path to PDScan 2020 txt/pd.txt")
    ap.add_argument("--pwg", default=DEFAULT_PWG, help="path to csl-orig/v02/pwg/pwg.txt")
    ap.add_argument("--check", action="store_true",
                    help="verify committed outputs instead of writing them")
    args = ap.parse_args(argv)

    for path, label in ((args.pd, "pd.txt"), (args.pwg, "pwg.txt")):
        if not os.path.exists(path):
            sys.exit(f"{label} not found: {path}")

    rows, summary = build(args.pd, args.pwg)
    rec = summary["reconciliation"]
    if not rec["within_tolerance"]:
        sys.exit(f"FAIL reconciliation: {rec}")
    if not (rec["attestations_equal_loci_pd"] and rec["attestations_equal_loci_pwg"]):
        sys.exit("FAIL attestations != loci")

    if not args.check:
        write_outputs(rows, summary, OUT_TSV, OUT_JSON)
        agg = summary["aggregate"]
        med = summary["per_lemma_medians"]
        print(f"shared lemmas={len(rows)}  PD att={rec['pd_attestations']:,}  "
              f"PWG att={rec['pwg_attestations']:,}  ratio={rec['attestation_ratio']:.2f}x")
        for name in ("fold", "raw"):
            a, m = agg[name], med[name]
            print(f"  {name:4s}: breadth={a['breadth_ratio']:.2f}x "
                  f"({a['pd_distinct_works_union']}/{a['pwg_distinct_works_union']})  "
                  f"depth={a['depth_ratio']:.2f}x  "
                  f"product={a['breadth_x_depth']:.3f}  "
                  f"median breadth={m['breadth_ratio']['median']:g} "
                  f"median depth={m['depth_ratio']['median']:.2f}")
        b = summary["below_parity"]
        print(f"  below parity={b['n']} ({b['pct_of_shared']}%): "
              f"zero-PD={b['zero_pd_attestations']}, near={b['near_parity']}")
        print(f"wrote {OUT_TSV}\nwrote {OUT_JSON}")
        return

    problems = committed_per_lemma_problems(rows)
    with open(OUT_TSV, encoding="utf-8") as fh:
        committed = fh.read().splitlines()
    expected = ["\t".join(COLUMNS)]
    for r in rows:
        expected.append("\t".join(str(r[c]) for c in COLUMNS))
    if committed != expected:
        problems.append("TSV differs from committed file")
    with open(OUT_JSON, encoding="utf-8") as fh:
        committed_summary = json.load(fh)
    if committed_summary != summary:
        problems.append("JSON summary differs from committed file")
    problems.extend(check_gold(rows))
    problems.extend(check_report(summary))

    if problems:
        print("FAIL")
        for p in problems:
            print(f"  {p}")
        sys.exit(1)
    print(f"PASS reconciliation {rec['pd_attestations']:,}/{rec['pwg_attestations']:,}")
    print(f"PASS attestations=loci on both sides; breadth x depth="
          f"{summary['aggregate']['fold']['breadth_x_depth']:.6f}")
    print("PASS 20 gold rows and report numbers regenerate from the TSV")


if __name__ == "__main__":
    main()
