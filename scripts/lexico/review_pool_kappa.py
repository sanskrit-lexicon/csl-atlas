"""Community review-pool κ report (H5483/B8) — design: docs/REVIEW_POOL_V1_DESIGN.md §9.

Reads one or more merge reports produced by scripts/merge-review-pool-decisions.py
(H5483/B7) and, per packet, computes:

  * Krippendorff's alpha (nominal), the headline statistic -- raters rotate
    (design §5), so a single fixed-dyad Cohen's kappa is the wrong instrument.
  * Cohen's kappa per dyad, reported only where the dyad shares >= 30 rows,
    else the point estimate is suppressed and n is printed instead.
  * Raw observed agreement, chance-expected agreement, and the modal-label
    share (base-rate control, reused from root_agreement_kappa.py).
  * Button-level (approve/reject/defer) 3-way agreement, a secondary figure.
  * A bootstrap 95% CI over rows (2000 resamples, deterministically seeded).
  * Landis-Koch bands.

Honesty rules fixed by the design and enforced here, not left to the caller:
R2's n=10 carries an explicit sentence that it cannot support a reliability
claim; there is no pooled alpha across packets (different label spaces); an
expert baseline (e.g. MG's recorded R2 decisions) is reported separately,
never mixed into the pool-internal alpha; the public-prior-art contamination
risk is named in the report's limitations, not claimed away.

Usage:
  python scripts/lexico/review_pool_kappa.py MERGE_REPORT.json [MERGE_REPORT2.json ...] \
      [--expert-baseline PACKET_ID=FILE.json] [--seed 20260925]

Writes data/review/pool_kappa_report.json and docs/REVIEW_POOL_KAPPA_REPORT.md.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))  # csl-atlas
sys.path.insert(0, os.path.join(ROOT, "scripts", "lib"))
from dataset_meta import license_fields, generated_at_for_payload, read_json_if_exists  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

JSON_OUT = os.path.join(ROOT, "data", "review", "pool_kappa_report.json")
MD_OUT = os.path.join(ROOT, "docs", "REVIEW_POOL_KAPPA_REPORT.md")

MIN_COHEN_DYAD_N = 30
BOOTSTRAP_RESAMPLES = 2000
DEFAULT_SEED = 20260925

R2_N_CAVEAT = (
    "R2's n=10 cannot support a reliability claim on its own: the alpha reported here is a "
    "machinery pilot (design §10 P4/P5 gate), not a measurement of the packet's true reliability."
)
NO_POOLING_NOTE = (
    "No pooled alpha across packets is reported: R2, H4, and xref use different label spaces, "
    "so a single combined number would be meaningless (design §9 honesty rule 2)."
)
CONTAMINATION_NOTE = (
    "R2 and H4 prior decisions are public in this repo; the student guide forbids consulting "
    "them but nothing enforces it. Measurable-looking agreement could be agreement with a "
    "copied answer, not independent judgment (design §9 honesty rule 4 / §11 risk 2)."
)


def landis_koch(alpha):
    if alpha is None:
        return None
    if alpha < 0:
        return "poor"
    if alpha < 0.20:
        return "slight"
    if alpha < 0.40:
        return "fair"
    if alpha < 0.60:
        return "moderate"
    if alpha < 0.80:
        return "substantial"
    return "almost-perfect"


def krippendorff_alpha_nominal(units):
    """units: list of list-of-labels, one list per row (>=1 keys per row).

    Standard nominal Krippendorff's alpha via the coincidence-matrix method
    (Hayes & Krippendorff 2007). Rows with fewer than 2 keys contribute no
    pairs and are silently excluded (they carry no disagreement information).
    Returns None when there is not enough pairable data, or when the expected
    disagreement is zero (every key falls in a single category -- alpha is
    undefined by the formula, not zero).
    """
    o = defaultdict(float)
    n_total = 0
    for labels in units:
        m = len(labels)
        if m < 2:
            continue
        counts = Counter(labels)
        denom = m - 1
        for c, n_c in counts.items():
            for k, n_k in counts.items():
                if c == k:
                    o[(c, k)] += n_c * (n_c - 1) / denom
                else:
                    o[(c, k)] += n_c * n_k / denom
        n_total += m
    if n_total < 2:
        return None
    categories = sorted({c for c, _ in o} | {k for _, k in o})
    n_c = {c: sum(o.get((c, k), 0.0) for k in categories) for c in categories}
    n = sum(n_c.values())
    if n < 2:
        return None
    diag = sum(o.get((c, c), 0.0) for c in categories)
    do_ = (n - diag) / n
    de_num = n * (n - 1) - sum(v * (v - 1) for v in n_c.values())
    de_ = de_num / (n * (n - 1))
    if de_ == 0:
        return None
    return 1.0 - do_ / de_


def bootstrap_ci(units, rng, resamples=BOOTSTRAP_RESAMPLES):
    """95% CI over rows for Krippendorff's alpha; None if the point estimate
    itself is undefined or too few rows carry >=2 keys to resample."""
    pairable = [u for u in units if len(u) >= 2]
    if len(pairable) < 2:
        return None
    samples = []
    n = len(pairable)
    for _ in range(resamples):
        draw = [pairable[rng.randrange(n)] for _ in range(n)]
        alpha = krippendorff_alpha_nominal(draw)
        if alpha is not None:
            samples.append(alpha)
    if len(samples) < resamples // 2:
        return None
    samples.sort()
    lo = samples[int(0.025 * len(samples))]
    hi = samples[min(len(samples) - 1, int(0.975 * len(samples)))]
    return [round(lo, 4), round(hi, 4)]


def cohen_kappa(pairs):
    n = len(pairs)
    if n == 0:
        return None
    observed = sum(1 for a, b in pairs if a == b) / n
    ca = Counter(a for a, _ in pairs)
    cb = Counter(b for _, b in pairs)
    expected = sum((ca[c] / n) * (cb[c] / n) for c in set(ca) | set(cb))
    if expected >= 1.0 - 1e-12:
        return {"n": n, "kappa": None, "band": None}
    kappa = (observed - expected) / (1 - expected)
    return {"n": n, "kappa": round(kappa, 3), "band": landis_koch(kappa)}


def cohen_kappa_by_dyad(records):
    """Cohen's kappa per (annotator, annotator) dyad, >= MIN_COHEN_DYAD_N rows only."""
    by_dyad = defaultdict(list)
    for record in records:
        keys = record["keys"]
        if len(keys) != 2:
            continue
        a, b = keys
        dyad = tuple(sorted((a["annotator"], b["annotator"])))
        pair = (a["resolvedLabel"], b["resolvedLabel"]) if a["annotator"] == dyad[0] else (b["resolvedLabel"], a["resolvedLabel"])
        by_dyad[dyad].append(pair)
    rows = []
    for dyad, pairs in sorted(by_dyad.items()):
        if len(pairs) >= MIN_COHEN_DYAD_N:
            result = cohen_kappa(pairs)
            rows.append({"dyad": list(dyad), "n": result["n"], "kappa": result["kappa"], "band": result["band"]})
        else:
            rows.append({"dyad": list(dyad), "n": len(pairs), "kappa": None, "band": None})
    return rows


def button_level_agreement(records):
    doubled = [r for r in records if len(r["keys"]) == 2]
    if not doubled:
        return None
    matches = sum(1 for r in doubled if r["keys"][0]["decision"] == r["keys"][1]["decision"])
    return round(matches / len(doubled), 4)


def modal_label_share(records):
    labels = [k["resolvedLabel"] for r in records for k in r["keys"]]
    if not labels:
        return None
    counts = Counter(labels)
    _, top_n = counts.most_common(1)[0]
    return round(top_n / len(labels), 4)


def observed_chance_agreement(records):
    doubled = [r for r in records if len(r["keys"]) == 2]
    pairs = [(r["keys"][0]["resolvedLabel"], r["keys"][1]["resolvedLabel"]) for r in doubled]
    if not pairs:
        return None, None
    n = len(pairs)
    observed = sum(1 for a, b in pairs if a == b) / n
    ca = Counter(a for a, _ in pairs)
    cb = Counter(b for _, b in pairs)
    expected = sum((ca[c] / n) * (cb[c] / n) for c in set(ca) | set(cb))
    return round(observed, 4), round(expected, 4)


def expert_baseline(records, expert_path):
    """design §9 honesty rule 3: an expert key (e.g. MG's recorded R2 decisions)
    reported as agreement against the pool keys, never mixed into pool-internal
    alpha. expert_path is a review-report style file keyed by reviewId with a
    'reviewedValue' field."""
    if expert_path is None:
        return None
    payload = json.loads(open(expert_path, encoding="utf-8").read())
    rows = payload.get("checkpointRows") or payload.get("rows") or payload.get("records") or []
    expert_by_id = {}
    for row in rows:
        row_id = row.get("checkpointId") or row.get("reviewId") or row.get("id")
        value = row.get("reviewedValue")
        if row_id and value is not None:
            expert_by_id[row_id] = value
    if not expert_by_id:
        return None
    pairs = []
    for record in records:
        expert_value = expert_by_id.get(record["reviewId"])
        if expert_value is None:
            continue
        for key in record["keys"]:
            pairs.append((expert_value, key["resolvedLabel"]))
    if not pairs:
        return None
    n = len(pairs)
    agreement = sum(1 for a, b in pairs if a == b) / n
    return {"n": n, "sourceFile": os.path.relpath(expert_path, ROOT).replace(os.sep, "/"),
            "agreementWithPool": round(agreement, 4)}


def packet_report(merge_report, rng, expert_path=None):
    records = merge_report["records"]
    units = [[k["resolvedLabel"] for k in r["keys"]] for r in records]
    alpha = krippendorff_alpha_nominal(units)
    ci = bootstrap_ci(units, rng) if alpha is not None else None
    observed, chance = observed_chance_agreement(records)
    categories = sorted({k["resolvedLabel"] for r in records for k in r["keys"]})
    counts = Counter(r["reviewStatus"] for r in records)

    limitations = []
    if merge_report["rows"] <= 10:
        limitations.append(R2_N_CAVEAT)
    limitations.append(CONTAMINATION_NOTE)

    return {
        "packetId": merge_report["sheetId"],
        "rows": merge_report["rows"],
        "rowsDoubleKeyed": merge_report["rowsDoubleKeyed"],
        "rowsSingleKey": merge_report["rowsSingleKey"],
        "categories": categories,
        "observedAgreement": observed,
        "chanceAgreement": chance,
        "modalLabelShare": modal_label_share(records),
        "krippendorffAlpha": round(alpha, 4) if alpha is not None else None,
        "alphaCI95": ci,
        "band": landis_koch(alpha),
        "buttonLevelAgreement": button_level_agreement(records),
        "cohenKappaByDyad": cohen_kappa_by_dyad(records),
        "disagreements": counts.get("needs-review", 0),
        "adjudicated": sum(1 for r in records if r.get("adjudicated")),
        "blockedByAdjudicator": sum(1 for r in records if r.get("reviewStatus") == "blocked"),
        "expertBaseline": expert_baseline(records, expert_path),
        "limitations": limitations,
    }


def build_payload(merge_reports, source_paths, expert_baselines, seed):
    rng = random.Random(seed)
    packets = [
        packet_report(report, rng, expert_baselines.get(report["sheetId"]))
        for report in merge_reports
    ]
    payload = {
        "schemaVersion": "1.0.0",
        **license_fields(),
        "evidenceLabel": "derived",
        "reviewStatus": "machine-reviewed",
        "ownerRepo": "csl-atlas",
        "generatedBy": "python scripts/lexico/review_pool_kappa.py",
        "sourceFiles": [os.path.relpath(p, ROOT).replace(os.sep, "/") for p in source_paths],
        "method": (
            "Krippendorff's alpha (nominal, coincidence-matrix method) as the headline statistic "
            "because raters rotate across rows (design §5); Cohen's kappa per dyad only where the "
            "dyad shares >= 30 rows; bootstrap 95% CI over rows (2000 resamples, seeded); "
            "Landis-Koch bands reused from scripts/lexico/root_agreement_kappa.py."
        ),
        "packets": packets,
        "limitations": [NO_POOLING_NOTE, CONTAMINATION_NOTE],
        "warnings": [],
    }
    payload["generatedAt"] = generated_at_for_payload(read_json_if_exists(JSON_OUT), payload)
    return payload


def render_markdown(payload):
    lines = [
        "# Review Pool v1 — κ Report",
        "",
        "Date: " + payload["generatedAt"][:10],
        "",
        "Status: generated machine-reviewed analysis over the community review pool's "
        "double-keyed decisions; see docs/REVIEW_POOL_V1_DESIGN.md §9.",
        "",
        "## Chart Trust Block",
        "",
        "- Claim: Inter-annotator reliability of the community review pool's double-keyed "
        "packets, reported per packet with Krippendorff's alpha as the headline statistic.",
        f"- Evidence label: `{payload['evidenceLabel']}`",
        "- Source files: " + ", ".join(f"`{p}`" for p in payload["sourceFiles"]),
        f"- Generated by: `{payload['generatedBy']}`",
        "- Validation: `npm run test-review-pool-kappa` (fixture-checked alpha/kappa); "
        "wired into `npm run verify`.",
        "- Known false positives: a rotating-partner dyad below n=30 has its Cohen's kappa "
        "suppressed, not fabricated.",
        "- Known false negatives: alpha is undefined (reported `null`) when every key in a "
        "packet falls in one category (degenerate agreement), including the current synthetic "
        "all-approve dry-run canary.",
        f"- Review status: `{payload['reviewStatus']}`",
        f"- Owner repo: `{payload['ownerRepo']}`",
        "- Next action: recruit real annotators (design §10 P6) and re-run this builder; a "
        "degenerate report before recruitment is machinery verification, not a measurement.",
        "- External dependencies: none.",
        "- Boundary note: derived from committed pool merge reports only; no source/corpus "
        "read, no public page, no recruitment or consent handling.",
        "",
        "## Method",
        "",
        payload["method"],
        "",
    ]
    for packet in payload["packets"]:
        lines += [
            f"## {packet['packetId']}",
            "",
            f"Rows: {packet['rows']} ({packet['rowsDoubleKeyed']} double-keyed, "
            f"{packet['rowsSingleKey']} single-key).",
            "",
            "| Statistic | Value |",
            "|---|---|",
            f"| Observed agreement | {packet['observedAgreement']} |",
            f"| Chance-expected agreement | {packet['chanceAgreement']} |",
            f"| Modal-label share | {packet['modalLabelShare']} |",
            f"| Krippendorff's α (nominal) | {packet['krippendorffAlpha']} |",
            f"| α 95% CI (bootstrap, n={BOOTSTRAP_RESAMPLES}) | {packet['alphaCI95']} |",
            f"| Band | `{packet['band']}` |",
            f"| Button-level (approve/reject/defer) agreement | {packet['buttonLevelAgreement']} |",
            f"| Disagreements queued for adjudication | {packet['disagreements']} |",
            f"| Adjudicated | {packet['adjudicated']} |",
            f"| Blocked by adjudicator | {packet['blockedByAdjudicator']} |",
            "",
            "| Dyad | n | Cohen's κ | Band |",
            "|---|---:|---:|---|",
        ]
        for dyad in packet["cohenKappaByDyad"]:
            lines.append(f"| {' × '.join(dyad['dyad'])} | {dyad['n']} | {dyad['kappa']} | `{dyad['band']}` |")
        if packet["expertBaseline"]:
            eb = packet["expertBaseline"]
            lines += ["", f"Expert baseline (`{eb['sourceFile']}`, n={eb['n']}): "
                          f"pool-key agreement {eb['agreementWithPool']} (never mixed into the pool-internal α)."]
        lines += ["", "**Limitations for this packet:**", ""]
        lines += [f"- {x}" for x in packet["limitations"]]
        lines.append("")
    lines += ["## Report-level limitations", ""] + [f"- {x}" for x in payload["limitations"]]
    lines += ["", "_Auto-generated by `python scripts/lexico/review_pool_kappa.py`._", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("merge_reports", nargs="+")
    parser.add_argument("--expert-baseline", action="append", default=[],
                        help="PACKET_ID=FILE.json, repeatable")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()

    reports = [json.loads(open(path, encoding="utf-8").read()) for path in args.merge_reports]

    expert_baselines = {}
    for spec in args.expert_baseline:
        packet_id, _, file_path = spec.partition("=")
        if not file_path:
            sys.exit(f"--expert-baseline must be PACKET_ID=FILE.json, got {spec!r}")
        expert_baselines[packet_id] = file_path

    payload = build_payload(reports, args.merge_reports, expert_baselines, args.seed)

    os.makedirs(os.path.dirname(JSON_OUT), exist_ok=True)
    with open(JSON_OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    with open(MD_OUT, "w", encoding="utf-8") as fh:
        fh.write(render_markdown(payload))

    print(f"wrote {JSON_OUT} and {MD_OUT}")
    for packet in payload["packets"]:
        print(f"  {packet['packetId']}: α={packet['krippendorffAlpha']} band={packet['band']} "
              f"rows={packet['rows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
