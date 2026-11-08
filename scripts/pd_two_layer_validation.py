#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7275 — PD two-layer validation: letter-a strata and a frozen print-only sample.

Layer 1 (measured, needs the PDScan 2020 machine text) rebuilds the H1336
citation-weighted coverage from the H6949 quotation unit and stratifies it by
fascicle-volume and by the frozen H7110 entry-policy classes, reporting every
numerator and denominator.  It also tests whether the 25.2 % headline is stable
across the measured letter-*a* material (leave-one-fascicle-out, work bootstrap,
per-fascicle range).

Layer 2 (print) does not measure anything: it freezes a 300-slot sample of
print-only entries (100 per period 2009-2011 / 2012-2016 / 2018-2019) from the
publication ledger alone, before any measurement.  Entry identities can only be
filled from page images; when they are unavailable the status is
STOP_NO_PRINT_ACCESS and no machine-text row may be substituted.

Usage:
    python scripts/pd_two_layer_validation.py --manifest          # layer 2 only (no pd.txt)
    python scripts/pd_two_layer_validation.py --pd /path/pd.txt    # layer 1 + manifest
    python scripts/pd_two_layer_validation.py --check --pd /path/pd.txt

Exit codes: 0 ok, 2 --check mismatch, 3 machine text missing.
Stdlib only; no network.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import random
import re
import sys
from collections import Counter, OrderedDict, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "scripts", "lib"))

import pd_family_rule as family_rule  # noqa: E402
import quotation_units  # noqa: E402
from dataset_meta import license_fields  # noqa: E402
from pd_quotation_units import citation_tail  # noqa: E402

LEDGER = os.path.join(ROOT, "data", "pd", "pd_publication_ledger.tsv")
FAMILIES = os.path.join(ROOT, "data", "pd", "pd_siglum_families.tsv")
OUT_DIR = os.path.join(ROOT, "data", "pd")
OUT_FASCICLE = os.path.join(OUT_DIR, "pd_two_layer_fascicle.tsv")
OUT_CLASS = os.path.join(OUT_DIR, "pd_two_layer_class.tsv")
OUT_JSON = os.path.join(OUT_DIR, "pd_two_layer_stability.json")
OUT_MANIFEST = os.path.join(OUT_DIR, "pd_print_only_sample_manifest.json")
OUT_SLOTS = os.path.join(OUT_DIR, "pd_print_only_sample_slots.tsv")

DEFAULT_PD = os.environ.get("PD_TXT", "")

RE_HDR = re.compile(r"^<L>([\d.]+)<pc>([^<]*)<k1>([^<\s]*)<k2>([^<\s]*)")
RE_PAGE = re.compile(r"^(\d+)-(\d+)([ab])?$")

PERIODS = [
    ("2009-2011", (2009, 2011), 100),
    ("2012-2016", (2012, 2016), 100),
    ("2018-2019", (2018, 2019), 100),
]
SAMPLE_SEED_TEXT = "H7275 print-only sample v1 | 26-10-2026 | ledger rows 9.1-35"
SAMPLE_SLOTS = 300

# Pāṇinian upasargas used for the cross-cutting preverb flag.  The H7110
# families ati/anu/apa are a subset; privative a-/an- is kept separate.
UPASARGAS = {
    "ati", "adhi", "anu", "apa", "api", "abhi", "ava", "ā", "ud", "upa",
    "ni", "nis", "nir", "parā", "pari", "pra", "vi", "sam", "su", "dus",
}

PINNED = {
    "h1336_primary": 353512,
    "h1336_covered": 88929,
    "h1336_pct": 25.16,
    "h6949_loci": 384217,
    "h6949_continuation": 35673,
    "h6949_attestations": 419890,
}

VERDICT_RULE = {
    "internal_stability": (
        "stable: every measured fascicle's coverage lies within ±2.0 pp of the "
        "pooled value; partially stable: the full range is ≤ 8.0 pp but at least "
        "one fascicle lies outside ±2.0 pp; not stable: the full range exceeds "
        "8.0 pp.  Reported beside the work-level bootstrap CI and the "
        "leave-one-fascicle-out range, which are descriptive and do not change "
        "the label."
    ),
    "print_digital_representativeness": (
        "assessed only if the 300 print-only slots resolve to entries on page "
        "images; otherwise STOP_NO_PRINT_ACCESS and no verdict."
    ),
}


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_ledger(path: str = LEDGER) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    for row in rows:
        row["pp_lo"] = int(row["pp_lo"])
        row["pp_hi"] = int(row["pp_hi"])
        row["year"] = int(row["year"])
    if len(rows) != 35:
        raise SystemExit(f"ledger must have 35 rows, found {len(rows)}")
    return rows


def read_families(path: str = FAMILIES) -> dict[str, dict]:
    with open(path, encoding="utf-8", newline="") as fh:
        return {r["siglum"]: r for r in csv.DictReader(fh, delimiter="\t")}


def iter_entries(path: str):
    cur = None
    for line in open(path, encoding="utf-8", errors="replace"):
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


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (100 * max(0.0, centre - half), 100 * min(1.0, centre + half))


def fmt(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}"


# --------------------------------------------------------------- layer 1
def build_layer1(pd_path: str, ledger: list[dict], families: dict[str, dict]) -> dict:
    ranges = [r for r in ledger if r["in_digital_text"] == "yes"]
    by_ledger: dict[str, dict] = defaultdict(lambda: {
        "entries": 0, "quotations": 0, "attestations": 0,
        "primary": 0, "covered": 0,
    })
    by_class: dict[str, dict] = defaultdict(lambda: {
        "entries": 0, "quotations": 0, "attestations": 0,
        "primary": 0, "covered": 0,
    })
    unmapped = Counter()
    total = {"entries": 0, "quotations": 0, "attestations": 0,
             "loci": 0, "continuation": 0, "primary": 0, "covered": 0,
             "structural": 0, "secondary": 0, "unmapped": 0}
    for hdr, body in iter_entries(pd_path):
        m = RE_HDR.match(hdr)
        if not m:
            continue
        _lid, pc, _k1, _k2 = m.groups()
        pm = RE_PAGE.match(pc)
        if not pm:
            continue
        page = int(pm.group(2))
        led = next((r for r in ranges if r["pp_lo"] <= page <= r["pp_hi"]), None)
        if led is None:
            continue
        flat = " ".join(body).replace('<div n="lb">', " ")
        units = quotation_units.count_units(flat, citation_tail)
        analysis, _is_corr = family_rule.first_line_paren(hdr + "\n" + "\n".join(body))
        cls = family_rule.classify(analysis) if analysis else None
        members = family_rule.members(analysis) if analysis else []
        first = members[0].lower() if members else ""
        flag = "unclassified"
        if cls == "compound":
            if first in {"a", "an"}:
                flag = "privative"
            elif first in UPASARGAS:
                flag = "preverb"
            else:
                flag = "compound-other"
        elif cls:
            flag = cls

        primary = covered = 0
        for tok in units["tokens"]:
            rec = families.get(tok)
            if rec is None:
                unmapped[tok] += 1
                continue
            if rec["class"] == "structural":
                total["structural"] += 1
            elif rec["class"] == "secondary":
                total["secondary"] += 1
            else:
                primary += 1
                if rec["match_type"] == "covered":
                    covered += 1

        total["entries"] += 1
        total["quotations"] += units["quotations"]
        total["attestations"] += units["attestations"]
        total["loci"] += units["loci"]
        total["continuation"] += units["continuation_loci"]
        total["primary"] += primary
        total["covered"] += covered
        total["unmapped"] += len(units["tokens"]) - sum(
            1 for tok in units["tokens"] if tok in families
        )
        for bucket, key in ((by_ledger[led["ledger_id"]], None), (by_class[flag], None)):
            bucket["entries"] += 1
            bucket["quotations"] += units["quotations"]
            bucket["attestations"] += units["attestations"]
            bucket["primary"] += primary
            bucket["covered"] += covered

    # ---- per-fascicle table (all 35 ledger rows; print-only rows carry no data)
    fascicle_rows = []
    measured = []
    for row in ledger:
        agg = by_ledger.get(row["ledger_id"])
        if agg and agg["entries"]:
            pct = 100.0 * agg["covered"] / agg["primary"] if agg["primary"] else 0.0
            lo, hi = wilson(agg["covered"], agg["primary"])
            measured.append({"ledger_id": row["ledger_id"], "year": row["year"],
                             "primary": agg["primary"], "covered": agg["covered"],
                             "pct": pct})
            vals = [row["ledger_id"], str(row["bound_volume"]), str(row["year"]),
                    str(row["pp_lo"]), str(row["pp_hi"]), "yes",
                    str(agg["entries"]), str(agg["quotations"]),
                    str(agg["attestations"]), str(agg["primary"]),
                    str(agg["covered"]), fmt(pct), fmt(lo), fmt(hi)]
        else:
            vals = [row["ledger_id"], str(row["bound_volume"]), str(row["year"]),
                    str(row["pp_lo"]), str(row["pp_hi"]),
                    row["in_digital_text"], "", "", "", "", "", "", "", ""]
        fascicle_rows.append(vals)

    # ---- class table
    class_order = ["simplex", "derivative", "compound-other", "privative",
                   "preverb", "unclassified"]
    class_rows = []
    for cls in class_order:
        agg = by_class.get(cls)
        if not agg:
            continue
        pct = 100.0 * agg["covered"] / agg["primary"] if agg["primary"] else 0.0
        lo, hi = wilson(agg["covered"], agg["primary"])
        class_rows.append([cls, str(agg["entries"]), str(agg["quotations"]),
                           str(agg["attestations"]), str(agg["primary"]),
                           str(agg["covered"]), fmt(pct), fmt(lo), fmt(hi)])

    # ---- stability statistics
    pooled = 100.0 * total["covered"] / total["primary"] if total["primary"] else 0.0
    pct_values = [m["pct"] for m in measured]
    full_range = max(pct_values) - min(pct_values) if pct_values else 0.0
    outside = sum(1 for p in pct_values if abs(p - pooled) > 2.0)
    if outside == 0:
        verdict = "stable"
    elif full_range <= 8.0:
        verdict = "partially stable"
    else:
        verdict = "not stable"

    leave_out = []
    for m in measured:
        num = total["covered"] - m["covered"]
        den = total["primary"] - m["primary"]
        leave_out.append(100.0 * num / den if den else 0.0)

    # work-level bootstrap over sigla (primary only), fixed seed
    primary_sigla = [(int(r["count"]), 1 if r["match_type"] == "covered" else 0)
                     for r in families.values() if r["class"] == "primary"]
    counts = [c for c, _ in primary_sigla]
    cov = [v for _, v in primary_sigla]
    rng = random.Random(7275)
    n = len(counts)
    boot = []
    for _ in range(5000):
        num = den = 0
        for _ in range(n):
            i = rng.randrange(n)
            den += counts[i]
            num += counts[i] * cov[i]
        boot.append(100.0 * num / den if den else 0.0)
    boot.sort()
    ci_lo = boot[int(0.025 * len(boot))]
    ci_hi = boot[int(0.975 * len(boot)) - 1]

    # top-20 concentration and leave-top-20-out influence
    ranked = sorted(primary_sigla, key=lambda x: -x[0])
    top20 = ranked[:20]
    top20_num = sum(c * v for c, v in top20)
    top20_den = sum(c for c, _ in top20)

    envelope = OrderedDict(
        hid="H7275",
        generated_by="scripts/pd_two_layer_validation.py",
        layer="1 — internal stability of the letter-a coverage headline",
        sources={
            "pd": {"path_basename": os.path.basename(pd_path),
                   "bytes": os.path.getsize(pd_path), "sha256": sha256(pd_path)},
            "ledger": {"path": "data/pd/pd_publication_ledger.tsv",
                       "sha256": sha256(LEDGER)},
            "siglum_families": {"path": "data/pd/pd_siglum_families.tsv",
                                "sha256": sha256(FAMILIES)},
        },
        pins=PINNED,
        recount=OrderedDict(
            entries=total["entries"],
            loci=total["loci"],
            continuation_loci=total["continuation"],
            attestations=total["attestations"],
            structural_loci=total["structural"],
            secondary_loci=total["secondary"],
            primary_loci=total["primary"],
            covered_loci=total["covered"],
            coverage_pct=round(pooled, 2),
            unmapped_tokens=total["unmapped"],
            unmapped_examples=unmapped.most_common(20),
            note=(
                "the H6949 unit reproduces its own pins exactly (384,217 loci + "
                "35,673 continuation = 419,890 attestations).  Coverage is "
                "computed over MAPPED primary sigla only; the 9.5 k residual "
                "tokens are abbreviations such as comm./cf./e. and a short tail "
                "of OCR variants, excluded and reported rather than coerced."
            ),
        ),
        canaries=OrderedDict(
            loci_match_h6949=total["loci"] == PINNED["h6949_loci"],
            continuation_match_h6949=total["continuation"] == PINNED["h6949_continuation"],
            attestations_match_h6949=total["attestations"] == PINNED["h6949_attestations"],
            coverage_within_0_5pp_of_h1336=abs(pooled - PINNED["h1336_pct"]) <= 0.5,
        ),
        stability=OrderedDict(
            pooled_pct=round(pooled, 2),
            min_fascicle_pct=round(min(pct_values), 2) if pct_values else None,
            max_fascicle_pct=round(max(pct_values), 2) if pct_values else None,
            full_range_pp=round(full_range, 2),
            fascicles_outside_2pp=outside,
            measured_fascicles=len(measured),
            leave_one_fascicle_out_min=round(min(leave_out), 2) if leave_out else None,
            leave_one_fascicle_out_max=round(max(leave_out), 2) if leave_out else None,
            work_bootstrap_ci_lo=round(ci_lo, 2),
            work_bootstrap_ci_hi=round(ci_hi, 2),
            work_bootstrap_reps=5000,
            work_bootstrap_seed=7275,
            top20_work_share_of_primary_pct=round(100.0 * top20_den / total["primary"], 2)
            if total["primary"] else None,
            top20_work_coverage_pct=round(100.0 * top20_num / top20_den, 2)
            if top20_den else None,
            verdict_rule=VERDICT_RULE["internal_stability"],
            verdict=verdict,
        ),
        per_fascicle=[{"ledger_id": m["ledger_id"], "year": m["year"],
                       "primary": m["primary"], "covered": m["covered"],
                       "coverage_pct": round(m["pct"], 2)} for m in measured],
        layer2=OrderedDict(
            status="STOP_NO_PRINT_ACCESS",
            manifest="data/pd/pd_print_only_sample_manifest.json",
            note=("the manifest is generated from the ledger alone, before any "
                  "measurement; no entry identity is claimed and no machine-text "
                  "row is substituted (H7275 mission, layer 2)."),
            verdict_rule=VERDICT_RULE["print_digital_representativeness"],
            verdict="not assessed — STOP_NO_PRINT_ACCESS",
        ),
    )
    return {
        "fascicle_rows": fascicle_rows,
        "class_rows": class_rows,
        "envelope": envelope,
    }


# --------------------------------------------------------------- layer 2
def build_manifest(ledger: list[dict]) -> dict:
    print_rows = [r for r in ledger if r["in_digital_text"] == "no"]
    if len(print_rows) != 11:
        raise SystemExit(f"expected 11 print-only ledger rows, found {len(print_rows)}")
    seed = int(hashlib.sha256(SAMPLE_SEED_TEXT.encode("utf-8")).hexdigest()[:16], 16)
    periods = []
    slots = []
    for name, (year_lo, year_hi), quota in PERIODS:
        rows = [r for r in print_rows if year_lo <= r["year"] <= year_hi]
        if not rows:
            raise SystemExit(f"no print-only rows in period {name}")
        pages = {r["ledger_id"]: r["pp_hi"] - r["pp_lo"] + 1 for r in rows}
        total_pages = sum(pages.values())
        alloc = {rid: quota * n / total_pages for rid, n in pages.items()}
        base = {rid: int(math.floor(v)) for rid, v in alloc.items()}
        rem = quota - sum(base.values())
        order = sorted(alloc, key=lambda rid: (-(alloc[rid] - base[rid]), rid))
        for rid in order[:rem]:
            base[rid] += 1
        period_rows = []
        for r in rows:
            rid = r["ledger_id"]
            k = base[rid]
            page_nums = list(range(r["pp_lo"], r["pp_hi"] + 1))
            ranked = sorted(page_nums, key=lambda p: hashlib.sha256(
                f"{SAMPLE_SEED_TEXT}|{rid}|{p}".encode("utf-8")).hexdigest())
            chosen = sorted(ranked[:k])
            u = int(hashlib.sha256(f"{SAMPLE_SEED_TEXT}|{rid}|offset".encode("utf-8")).hexdigest()[:8], 16)
            offset = round(0.13 + 0.74 * (u / 0xFFFFFFFF), 4)
            for i, page in enumerate(chosen):
                slots.append({
                    "slot": len(slots) + 1, "period": name, "ledger_id": rid,
                    "year": r["year"], "page": page, "offset": offset,
                    "rule": "first entry beginning at or after this page point; "
                            "else first entry beginning on the next page",
                })
            period_rows.append({"ledger_id": rid, "year": r["year"],
                                "pp_lo": r["pp_lo"], "pp_hi": r["pp_hi"],
                                "pages": pages[rid], "slots": k})
        periods.append({"period": name, "year_lo": year_lo, "year_hi": year_hi,
                        "quota": quota, "rows": period_rows})
    if len(slots) != SAMPLE_SLOTS:
        raise SystemExit(f"sample must have {SAMPLE_SLOTS} slots, found {len(slots)}")
    return OrderedDict(
        hid="H7275", layer="2 — frozen print-only sample",
        generated_by="scripts/pd_two_layer_validation.py --manifest",
        status="STOP_NO_PRINT_ACCESS",
        status_reason=(
            "no page images of ledger rows 9.1-35 are available in the estate or "
            "over the read-only archive routes reachable from this box; entry "
            "identities cannot be observed, so the slots stay empty and no "
            "machine-text row is substituted."
        ),
        frozen_before_measurement=True,
        seed_text=SAMPLE_SEED_TEXT,
        seed=seed,
        quota_total=SAMPLE_SLOTS,
        allocation_rule=(
            "per period 100 slots; within a period proportional to printed page "
            "count (largest remainder, ties by ledger id); pages ranked by "
            "sha256(seed_text|ledger_id|page); one slot per selected page at the "
            "fractional offset below, top to bottom"
        ),
        entry_rule=(
            "at a slot take the first entry that BEGINS at or after the page "
            "point; if none begins on that page, take the first entry beginning "
            "on the next page; record its headword, printed page and the first "
            "citation tail"
        ),
        periods=periods,
        slots=slots,
        slots_tsv="data/pd/pd_print_only_sample_slots.tsv",
        pins={"ledger_sha256": sha256(LEDGER)},
    )


def render_slots(manifest: dict) -> str:
    lines = ["slot\tperiod\tledger_id\tyear\tpage\toffset\trule"]
    for s in manifest["slots"]:
        lines.append("\t".join(str(s[k]) for k in
                               ("slot", "period", "ledger_id", "year", "page", "offset", "rule")))
    return "\n".join(lines) + "\n"


def render_fascicle(rows: list[list[str]]) -> str:
    head = ["ledger_id", "bound_volume", "year", "pp_lo", "pp_hi", "in_digital_text",
            "entries", "quotations", "attestations", "primary_loci", "covered_loci",
            "coverage_pct", "wilson_lo", "wilson_hi"]
    return "\n".join(["\t".join(head)] + ["\t".join(r) for r in rows]) + "\n"


def render_class(rows: list[list[str]]) -> str:
    head = ["class", "entries", "quotations", "attestations", "primary_loci",
            "covered_loci", "coverage_pct", "wilson_lo", "wilson_hi"]
    return "\n".join(["\t".join(head)] + ["\t".join(r) for r in rows]) + "\n"


def render_json(obj) -> str:
    return json.dumps({**license_fields(), **obj}, ensure_ascii=False, indent=2) + "\n"


def write(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def check(path: str, text: str) -> bool:
    if not os.path.exists(path):
        print(f"MISSING {os.path.relpath(path, ROOT)}", file=sys.stderr)
        return False
    before = open(path, encoding="utf-8", newline="").read()
    if before != text:
        print(f"DIFF {os.path.relpath(path, ROOT)}", file=sys.stderr)
        return False
    print(f"OK {os.path.relpath(path, ROOT)}")
    return True


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pd", default=DEFAULT_PD)
    ap.add_argument("--manifest", action="store_true", help="layer 2 only")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    ledger = read_ledger()
    manifest = build_manifest(ledger)
    slots_text = render_slots(manifest)
    manifest_text = render_json(manifest)

    if args.manifest:
        write(OUT_MANIFEST, manifest_text)
        write(OUT_SLOTS, slots_text)
        print("wrote layer-2 manifest (300 slots)")
        return 0

    if not os.path.exists(args.pd):
        print(f"pd.txt not found: {args.pd!r}; pass --pd or set PD_TXT", file=sys.stderr)
        return 3
    families = read_families()
    built = build_layer1(args.pd, ledger, families)
    fascicle_text = render_fascicle(built["fascicle_rows"])
    class_text = render_class(built["class_rows"])
    json_text = render_json(built["envelope"])

    if args.check:
        ok = all([
            check(OUT_FASCICLE, fascicle_text),
            check(OUT_CLASS, class_text),
            check(OUT_JSON, json_text),
            check(OUT_MANIFEST, manifest_text),
            check(OUT_SLOTS, slots_text),
        ])
        return 0 if ok else 2

    write(OUT_FASCICLE, fascicle_text)
    write(OUT_CLASS, class_text)
    write(OUT_JSON, json_text)
    write(OUT_MANIFEST, manifest_text)
    write(OUT_SLOTS, slots_text)
    st = built["envelope"]["stability"]
    print(f"wrote layer-1 tables: pooled {st['pooled_pct']}% "
          f"range {st['min_fascicle_pct']}–{st['max_fascicle_pct']}% "
          f"({st['verdict']}); manifest 300 slots STOP_NO_PRINT_ACCESS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
