#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7298 — PD × DCS residue status queue (three action lanes + unverified).

Extends H6722's GRETIL-only acquisition queue into a status-aware programme:
every named-residue work carries its DCS / GRETIL / wisdomlib-portal /
wisdomlib-estate state, rights, annotation and fragment status, and is routed
into exactly one lane:

  * ``ingest-annotate``      — machine-readable full text exists (GRETIL full
    or embedded) but the work is not in DCS;
  * ``acquire-digitise``     — H6722's missing-everywhere class (absent in DCS
    AND GRETIL), now with the wisdomlib portal/estate state recorded;
  * ``fragment-completion``  — only a fragment is machine-readable anywhere
    (GRETIL partial rows, plus the covered-but-fragmentary Skandapurāṇa
    context row);
  * ``unverified``           — H6722 rows 21–44, never crossed against GRETIL;
    retained unresolved, never dropped.

Inputs (all committed, read-only — the builder is deterministic and offline):
  * data/pd/pd_siglum_families.tsv       (residue source of truth; the 44
    named rows and their PD citation masses are re-derived from it and must
    match the frozen evidence input exactly — a parity gate, not a copy)
  * data/pd/pd_residue_source_status.tsv (frozen per-work source-status
    evidence: C5 §2 GRETIL verdicts 14-10-2026, C6 wisdomlib live probes
    14-10-2026, MSI wisdomlib-scrape store manifest + text-layer probes
    27-10-2026, dcs_text_inventory.tsv rows 9/282)

Outputs:
  * data/pd/pd_dcs_residue_status_queue.tsv
  * data/pd/pd_dcs_residue_status_queue.json

Usage:
  python3 scripts/pd_dcs_residue_status_queue.py            # build
  python3 scripts/pd_dcs_residue_status_queue.py --check    # byte-parity gate

--check re-derives both outputs in memory and byte-compares them with the
committed files; it also re-verifies the lane counts and citation masses
against hand-computed invariants (H6722: 6 missing-everywhere works / 9,229
cites; Skandapurāṇa 3,335 cites distinct as a covered context row).
"""
import argparse
import csv
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "scripts", "lib"))
from dataset_meta import license_fields  # noqa: E402

DATA = os.path.join(HERE, "data", "pd")

FAMILIES = os.path.join(DATA, "pd_siglum_families.tsv")
EVIDENCE = os.path.join(DATA, "pd_residue_source_status.tsv")
OUT_TSV = os.path.join(DATA, "pd_dcs_residue_status_queue.tsv")
OUT_JSON = os.path.join(DATA, "pd_dcs_residue_status_queue.json")

AS_OF = "2026-10-27"
GENERATED_BY = "H7298 pd_dcs_residue_status_queue.py (Kimi K3.1 Pro, kimi-code-plan-global/k3.1-pro)"

# Lane assignment rules (deterministic, fail-loud on unknown states).
def lane_of(row):
    if row["dcs_status"].startswith("covered-fragment"):
        return "fragment-completion"
    g = row["gretil_status"]
    if g in ("full", "embedded"):
        return "ingest-annotate"
    if g == "partial":
        return "fragment-completion"
    if g == "absent":
        return "acquire-digitise"
    if g == "uncrossed":
        return "unverified"
    raise ValueError("no lane rule for gretil_status=%r (siglum %s)"
                     % (g, row["siglum"]))


def expected_gain(row, lane):
    # The covered context row's citation mass is already attributed to DCS;
    # fragment completion adds textual completeness, not citation coverage.
    if lane == "fragment-completion" and row["dcs_status"].startswith("covered-fragment"):
        return 0
    return int(row["pd_cites"])


def read_tsv(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def build():
    families = read_tsv(FAMILIES)
    evidence = read_tsv(EVIDENCE)

    # Parity gate: re-derive the 44 named residue rows from the families file
    # and require exact agreement with the frozen evidence input.
    named = {}
    for row in families:
        if row.get("match_type") == "residue" and (row.get("dcs_title") or row.get("display_title")):
            named[row["siglum"]] = int(row["count"])
    if len(named) != 44:
        raise SystemExit("FAIL: expected 44 named residue rows in pd_siglum_families.tsv, got %d" % len(named))

    residue_evidence = [r for r in evidence if r["dcs_status"] == "absent (residue)"]
    context_rows = [r for r in evidence if r["dcs_status"].startswith("covered-fragment")]
    if len(residue_evidence) != 44 or len(context_rows) != 1:
        raise SystemExit("FAIL: evidence input must hold 44 residue rows + 1 context row, got %d + %d"
                         % (len(residue_evidence), len(context_rows)))
    for row in residue_evidence:
        sig = row["siglum"]
        if sig not in named:
            raise SystemExit("FAIL: evidence siglum %r not a named residue row" % sig)
        if int(row["pd_cites"]) != named[sig]:
            raise SystemExit("FAIL: pd_cites mismatch for %s: evidence %s vs families %d"
                             % (sig, row["pd_cites"], named[sig]))
    skanda = context_rows[0]
    fam_skanda = [r for r in families if r["siglum"] == "SkandP."]
    if not fam_skanda or int(fam_skanda[0]["count"]) != int(skanda["pd_cites"]):
        raise SystemExit("FAIL: SkandP. citation mass mismatch between evidence and families file")

    rows = []
    for row in evidence:
        lane = lane_of(row)
        rows.append({
            "siglum": row["siglum"],
            "work": row["work"],
            "pd_cites": int(row["pd_cites"]),
            "lane": lane,
            "expected_pd_citation_gain": expected_gain(row, lane),
            "dcs_status": row["dcs_status"],
            "gretil_status": row["gretil_status"],
            "wisdomlib_portal": row["wisdomlib_portal"],
            "wisdomlib_estate": row["wisdomlib_estate"],
            "source_ref": row["source_ref"],
            "rights": row["rights"],
            "annotation": row["annotation"],
            "fragment_status": row["fragment_status"],
            "evidence_refs": row["evidence_refs"],
            "notes": row["notes"],
        })

    lanes = {}
    for row in rows:
        lane = lanes.setdefault(row["lane"], {"works": 0, "pd_cites": 0, "expected_pd_citation_gain": 0})
        lane["works"] += 1
        lane["pd_cites"] += row["pd_cites"]
        lane["expected_pd_citation_gain"] += row["expected_pd_citation_gain"]

    summary = {
        "as_of": AS_OF,
        "generated_by": GENERATED_BY,
        "inputs": {
            "pd_siglum_families.tsv": sha256(FAMILIES),
            "pd_residue_source_status.tsv": sha256(EVIDENCE),
        },
        "rows": len(rows),
        "lanes": lanes,
        "skandapurana_verdict": {
            "pd_cites": int(skanda["pd_cites"]),
            "dcs": "covered-fragment: SkPuR 113,333 tok + SkPu 16,479 tok (dcs_text_inventory.tsv, 27-10-2026)",
            "wisdomlib_portal": "skanda-purana-sanskrit, 95,556 chapters in manifest (books.json, 27-10-2026)",
            "wisdomlib_estate": "link-index only (sitemap.txt 40 B marker; no chapter bodies; CF-blocked per store stats.json 23-07-2026)",
            "edition_identity": "INCONCLUSIVE — no book-page meta in store; live probe CF-blocked (HTTP 403, 27-10-2026)",
            "rights": "derived layers CC BY 4.0 (LICENSE-DATA; Zenodo 10.5281/zenodo.22117833); underlying print edition unverified",
            "annotation": "none (no text layer for this book)",
        },
    }

    # H5303 (G6): the JSON envelope declares the matrix licence (first keys,
    # matching the licenseFields() envelope order every dataset carries).
    summary = {**license_fields(), **summary}

    header = ["siglum", "work", "pd_cites", "lane", "expected_pd_citation_gain",
              "dcs_status", "gretil_status", "wisdomlib_portal", "wisdomlib_estate",
              "source_ref", "rights", "annotation", "fragment_status",
              "evidence_refs", "notes"]
    import io
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=header, delimiter="\t", lineterminator="\n")
    w.writeheader()
    for row in rows:
        w.writerow(row)
    return buf.getvalue(), json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def check():
    tsv, js = build()
    ok = True
    for path, content in ((OUT_TSV, tsv), (OUT_JSON, js)):
        if not os.path.exists(path):
            print("FAIL: %s missing" % path)
            ok = False
            continue
        with open(path, encoding="utf-8") as fh:
            committed = fh.read()
        if committed != content:
            print("FAIL: %s differs from regenerated content" % path)
            ok = False
    # Hand-computed invariants (never derived by running this script blindly):
    data = json.loads(js)
    expect = {
        "acquire-digitise": (6, 9229, 9229),
        "ingest-annotate": (9, 10262, 10262),
        "fragment-completion": (6, 5348 + 3335, 5348),
        "unverified": (24, 9685, 9685),
    }
    for lane, (works, cites, gain) in expect.items():
        got = data["lanes"].get(lane)
        if got is None or (got["works"], got["pd_cites"], got["expected_pd_citation_gain"]) != (works, cites, gain):
            print("FAIL: lane %s invariant mismatch: got %s want (%d, %d, %d)" % (lane, got, works, cites, gain))
            ok = False
    if data["rows"] != 45:
        print("FAIL: rows != 45")
        ok = False
    if data["skandapurana_verdict"]["pd_cites"] != 3335:
        print("FAIL: Skandapurāṇa verdict mass moved")
        ok = False
    print("PASS" if ok else "FAIL", "(as_of %s)" % AS_OF)
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if args.check:
        return check()
    tsv, js = build()
    with open(OUT_TSV, "w", encoding="utf-8", newline="") as fh:
        fh.write(tsv)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        fh.write(js)
    print("wrote %s and %s" % (OUT_TSV, OUT_JSON))
    return 0


if __name__ == "__main__":
    sys.exit(main())
