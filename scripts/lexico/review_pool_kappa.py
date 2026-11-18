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
from dataset_meta import (  # noqa: E402
    generated_at_for_payload,
    license_fields,
    read_json_if_exists,
)

sys.path.insert(0, HERE)

import pool_kappa_stats  # noqa: E402
from pool_kappa_stats import (  # noqa: E402
    BOOTSTRAP_RESAMPLES,
    bootstrap_ci,
    krippendorff_alpha_nominal,
    landis_koch,
)
from pool_kappa_report_md import render_markdown  # noqa: E402
from pool_kappa_two_model import (  # noqa: E402,F401
    HUMAN_ANCHOR_NOTE,
    STRATUM_BY_LABELS,
    TWO_MODEL_CAVEAT,
    TWO_MODEL_CHANNEL,
    gate_band,
    pass_a_decisions,
    pass_b_labels,
    read_json_file,
    stratum_of,
    two_model_packet,
)

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


def build_payload(merge_reports, source_paths, expert_baselines, seed, model_pairs=None, pass_a_models=None):
    rng = random.Random(seed)
    packets = [
        packet_report(report, rng, expert_baselines.get(report["sheetId"]))
        for report in merge_reports
    ]
    model_pairs = model_pairs or {}
    pass_a_models = pass_a_models or {}
    two_model_packets = []
    pair_sources = []
    for packet_id, spec in model_pairs.items():
        payload_a = read_json_file(spec["a"])
        payload_b = read_json_file(spec["b"])
        blind_payload = read_json_file(spec["blind"]) if spec.get("blind") else None
        flip_payload = read_json_file(spec["flip"]) if spec.get("flip") else None
        paths = {
            "a": os.path.relpath(spec["a"]).replace(os.sep, "/"),
            "b": os.path.relpath(spec["b"]).replace(os.sep, "/"),
            "blind": os.path.relpath(spec["blind"]).replace(os.sep, "/") if spec.get("blind") else None,
            "flip": os.path.relpath(spec["flip"]).replace(os.sep, "/") if spec.get("flip") else None,
        }
        pair_sources += [p for p in paths.values() if p]
        two_model_packets.append(
            two_model_packet(
                packet_id, payload_a, payload_b, blind_payload, flip_payload,
                pass_a_models.get(packet_id, "unrecorded"), rng, paths,
            )
        )
    payload = {
        "schemaVersion": "1.0.0",
        **license_fields(),
        "evidenceLabel": "derived",
        "reviewStatus": "machine-reviewed",
        "ownerRepo": "csl-atlas",
        "generatedBy": "python scripts/lexico/review_pool_kappa.py",
        "sourceFiles": [os.path.relpath(p, ROOT).replace(os.sep, "/") for p in source_paths] + pair_sources,
        "method": (
            "Krippendorff's alpha (nominal, coincidence-matrix method) as the headline statistic "
            "because raters rotate across rows (design §5); Cohen's kappa per dyad only where the "
            "dyad shares >= 30 rows; bootstrap 95% CI over rows (2000 resamples, seeded); "
            "Landis-Koch bands reused from scripts/lexico/root_agreement_kappa.py. Two-model "
            "packets add a blind cross-model second pass under Uprava "
            "PROTOCOL_BLIND_LLM_SECOND_ANNOTATOR_RELIABILITY_2026 (channel = model x model)."
        ),
        "packets": packets,
        "twoModelPackets": two_model_packets,
        "limitations": [NO_POOLING_NOTE, CONTAMINATION_NOTE],
        "warnings": [],
    }
    payload["generatedAt"] = generated_at_for_payload(read_json_if_exists(JSON_OUT), payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("merge_reports", nargs="+")
    parser.add_argument("--expert-baseline", action="append", default=[],
                        help="PACKET_ID=FILE.json, repeatable")
    parser.add_argument("--model-pair", action="append", default=[],
                        help="PACKET_ID=PASS_A.json=PASS_B.json — blind cross-model second-annotator "
                             "pair (protocol PROTOCOL_BLIND_LLM_SECOND_ANNOTATOR_RELIABILITY_2026)")
    parser.add_argument("--blind", action="append", default=[],
                        help="PACKET_ID=BLIND.json — the blind view Pass B read (evidence-presence split)")
    parser.add_argument("--flip-rate", action="append", default=[],
                        help="PACKET_ID=FLIP_RATE.json — §2.7 flip-rate artifact")
    parser.add_argument("--pass-a-model", action="append", default=[],
                        help="PACKET_ID=TIER AND EXACT VERSION (protocol §2.2)")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()

    reports = [json.loads(open(path, encoding="utf-8").read()) for path in args.merge_reports]

    expert_baselines = {}
    for spec in args.expert_baseline:
        packet_id, _, file_path = spec.partition("=")
        if not file_path:
            sys.exit(f"--expert-baseline must be PACKET_ID=FILE.json, got {spec!r}")
        expert_baselines[packet_id] = file_path

    def keyed(specs, flag):
        out = {}
        for spec in specs:
            key, _, value = spec.partition("=")
            if not value or "=" in value:
                sys.exit(f"{flag} must be KEY=VALUE, got {spec!r}")
            out[key] = value
        return out

    model_pairs = {}
    for spec in args.model_pair:
        packet_id, _, rest = spec.partition("=")
        parts = rest.split("=")
        if len(parts) != 2 or not packet_id:
            sys.exit(f"--model-pair must be PACKET_ID=PASS_A.json=PASS_B.json, got {spec!r}")
        model_pairs[packet_id] = {"a": parts[0], "b": parts[1]}

    for packet_id, path in keyed(args.blind, "--blind").items():
        model_pairs.setdefault(packet_id, {})["blind"] = path
    for packet_id, path in keyed(args.flip_rate, "--flip-rate").items():
        model_pairs.setdefault(packet_id, {})["flip"] = path
    incomplete = [pid for pid, spec in model_pairs.items() if not (spec.get("a") and spec.get("b"))]
    if incomplete:
        sys.exit(f"--blind/--flip-rate named packet(s) with no --model-pair: {', '.join(incomplete)}")

    payload = build_payload(
        reports, args.merge_reports, expert_baselines, args.seed,
        model_pairs=model_pairs, pass_a_models=keyed(args.pass_a_model, "--pass-a-model"),
    )

    os.makedirs(os.path.dirname(JSON_OUT), exist_ok=True)
    # newline="": write LF on every host, so a Windows re-run leaves the committed
    # report byte-identical instead of rewriting CRLF (reproducibility contract).
    with open(JSON_OUT, "w", encoding="utf-8", newline="") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    with open(MD_OUT, "w", encoding="utf-8", newline="") as fh:
        fh.write(render_markdown(payload))

    print(f"wrote {JSON_OUT} and {MD_OUT}")
    for packet in payload["packets"]:
        print(f"  {packet['packetId']}: α={packet['krippendorffAlpha']} band={packet['band']} "
              f"rows={packet['rows']}")
    for pair in payload.get("twoModelPackets", []):
        print(f"  {pair['packetId']} [{pair['channel']}]: α={pair['krippendorffAlpha']} "
              f"CI={pair['alphaCI95']} gate={pair['gate']['outcome']} n={pair['rows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
