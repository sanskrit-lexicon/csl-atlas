"""Two-model mode for the review-pool alpha report: blind cross-model second annotator.

Protocol: Uprava docs/PROTOCOL_BLIND_LLM_SECOND_ANNOTATOR_RELIABILITY_2026.md
(§2.2 different models with exact versions, §2.3 blindness as a build step,
§2.5 bootstrap CI, §2.7 flip-rate, §4 gate ladder).

Split out of scripts/lexico/review_pool_kappa.py to stay inside the repo's
5 000-token file budget (Uprava tools/token_size_gate).
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict

import pool_kappa_stats
from pool_kappa_stats import BOOTSTRAP_RESAMPLES, bootstrap_ci, krippendorff_alpha_nominal, landis_koch

# --- two-model mode: blind cross-model second annotator (C3 discipline) -----
# Protocol: Uprava PROTOCOL_BLIND_LLM_SECOND_ANNOTATOR_RELIABILITY_2026 (§2.2, §2.3,
# §2.5, §2.7, §4). The two passes live in separate committed files and are joined
# only here, at scoring time; the blind view that Pass B read carries no decision,
# provenance or note field (see docs/PROTOCOL_POOL_ALPHA_H4_2026-11-18.md).

TWO_MODEL_CHANNEL = "model x model"
TWO_MODEL_CAVEAT = (
    "Cross-model inter-annotator agreement, not human-validated reliability: two models "
    "agreeing shows the codebook is executable and the labels are stable, nothing more "
    "(protocol §3)."
)
HUMAN_ANCHOR_NOTE = (
    "No human × model figure is reported: the agenda's Wave-2 61-row human residue was checked "
    "and is an outstanding human ask (docs/H1684_B2_ADJUDICATION.md § 'The remaining human ask "
    "— 61 rows'), not a set of human labels, and it belongs to a different packet. The human "
    "anchor stays a GTD @WAITING residual."
)
GATE_CLEAR_CI_LOW = 0.80
GATE_BLOCK_POINT = 0.40
FLIP_RATE_UNSTABLE_PCT = 10.0
STRATUM_BY_LABELS = {
    ("parser-gap", "prose-present", "true-low", "variant-headword"): "skd-false-low",
    ("normalization-risk", "thin-entry", "true-covered"): "vcp-high-coverage",
    ("edition-delta", "normalization-risk", "parser-gap", "true-delta"): "ap-ap90-delta",
    ("incidental-match", "scope-match", "scope-mismatch"): "specialized-baseline",
    ("direction-artifact", "index-artifact", "meaningful-exception"): "index-reverse-control",
}


def read_json_file(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def pass_a_decisions(payload):
    """Pass A out of a review packet (sampleRows/rows with reviewedValue) or a merge report."""
    rows = payload.get("sampleRows") or payload.get("rows") or payload.get("records") or []
    decisions = {}
    for row in rows:
        review_id = row.get("reviewId") or row.get("checkpointId") or row.get("id")
        value = row.get("reviewedValue")
        if review_id and value:
            decisions[review_id] = value
    return decisions


def pass_b_labels(payload):
    labels, allowed = {}, {}
    for item in payload.get("items", []):
        review_id = item.get("reviewId")
        label = item.get("label")
        if review_id and label:
            labels[review_id] = label
            allowed[review_id] = item.get("allowed") or []
    return labels, allowed


def stratum_of(allowed):
    return STRATUM_BY_LABELS.get(tuple(sorted(allowed or [])), "unmapped")


def alpha_and_ci(units, rng):
    alpha = krippendorff_alpha_nominal(units)
    ci = bootstrap_ci(units, rng) if alpha is not None else None
    return (round(alpha, 4) if alpha is not None else None), ci


def gate_band(alpha, ci, flip_rate_pct):
    """§4 ladder at L0. No coarser level is pre-registered, so RESTATE is unavailable."""
    if alpha is None:
        return "UNDEFINED", "α is undefined (degenerate label distribution); no gate applies"
    if flip_rate_pct is not None and flip_rate_pct > FLIP_RATE_UNSTABLE_PCT:
        return (
            "PROVISIONAL-UNSTABLE",
            f"flip-rate {flip_rate_pct} % exceeds the {FLIP_RATE_UNSTABLE_PCT} % §2.7 ceiling; "
            "the α cannot clear the gate whatever its value",
        )
    low = ci[0] if ci else None
    if low is not None and low >= GATE_CLEAR_CI_LOW:
        return "CLEAR", f"α CI lower bound {low} ≥ {GATE_CLEAR_CI_LOW}"
    if alpha < GATE_BLOCK_POINT:
        return (
            "BLOCK",
            f"α point estimate {alpha} < {GATE_BLOCK_POINT} and no coarser pre-registered level "
            "exists; §2.6 applies — publish the measured α, demote the dependent headline, "
            "write the disagreement rows out for codebook repair",
        )
    return (
        "DEMOTE",
        f"α CI lower bound {low} < {GATE_CLEAR_CI_LOW}: publish the measured α and restate any "
        "dependent headline as a bounded estimate (§2.6)",
    )


def two_model_packet(packet_id, payload_a, payload_b, blind_payload, flip_payload, model_a, rng, paths):
    a = pass_a_decisions(payload_a)
    b, allowed = pass_b_labels(payload_b)
    ids = [review_id for review_id in b if review_id in a]
    units = [[a[review_id], b[review_id]] for review_id in ids]
    alpha, ci = alpha_and_ci(units, rng)
    agreements = sum(1 for x, y in zip([a[i] for i in ids], [b[i] for i in ids]) if x == y)

    flip_rate = flip_payload.get("flipRatePct") if flip_payload else None
    band, band_reason = gate_band(alpha, ci, flip_rate)

    by_stratum = defaultdict(list)
    for review_id in ids:
        by_stratum[stratum_of(allowed.get(review_id))].append([a[review_id], b[review_id]])
    stratum_rows = []
    for name in sorted(by_stratum):
        s_alpha, s_ci = alpha_and_ci(by_stratum[name], rng)
        stratum_rows.append({"stratum": name, "n": len(by_stratum[name]), "alpha": s_alpha, "alphaCI95": s_ci})

    evidence_rows = []
    has_evidence = None
    if blind_payload:
        has_evidence = {
            item.get("reviewId"): bool(item.get("evidence"))
            for item in blind_payload.get("items", [])
        }
        split = defaultdict(list)
        for review_id in ids:
            if review_id in has_evidence:
                split["excerpt present" if has_evidence[review_id] else "no excerpt"].append(
                    [a[review_id], b[review_id]]
                )
        for name in ("excerpt present", "no excerpt"):
            if split.get(name):
                e_alpha, e_ci = alpha_and_ci(split[name], rng)
                evidence_rows.append({"evidence": name, "n": len(split[name]), "alpha": e_alpha, "alphaCI95": e_ci})

    sensitivity = []
    excluded = {row["item"] for row in (payload_b.get("sensitivityExclusions") or [])}
    if excluded:
        kept_ids = [review_id for review_id in ids if _item_of(payload_b, review_id) not in excluded]
        s_alpha, s_ci = alpha_and_ci([[a[i], b[i]] for i in kept_ids], rng)
        sensitivity.append({
            "excludedItems": sorted(excluded),
            "reason": " / ".join(row.get("reason", "") for row in payload_b["sensitivityExclusions"]),
            "n": len(kept_ids),
            "alpha": s_alpha,
            "alphaCI95": s_ci,
        })

    labels_a = Counter(a[i] for i in ids)
    labels_b = Counter(b[i] for i in ids)
    disagreements = [
        {"reviewId": review_id, "passA": a[review_id], "passB": b[review_id], "stratum": stratum_of(allowed.get(review_id))}
        for review_id in ids
        if a[review_id] != b[review_id]
    ]

    return {
        "packetId": packet_id,
        "channel": TWO_MODEL_CHANNEL,
        "passA": {"model": model_a, "source": paths["a"]},
        "passB": {"model": (payload_b.get("model") or {}), "source": paths["b"]},
        "blindInput": paths.get("blind"),
        "preRegistration": payload_b.get("preRegistration"),
        "rows": len(ids),
        "denominator": (
            f"{len(ids)} of {len(b)} Pass-B rows joined to Pass A "
            f"({payload_a.get('rows', len(a))} decision-bearing rows in the packet)"
        ),
        "observedAgreement": round(agreements / len(ids), 4) if ids else None,
        "krippendorffAlpha": alpha,
        "alphaCI95": ci,
        "band": landis_koch(alpha),
        "gate": {"outcome": band, "reason": band_reason},
        "flipRatePct": flip_rate,
        "flipRate": flip_payload,
        "labelCounts": {"passA": dict(labels_a), "passB": dict(labels_b)},
        "byStratum": stratum_rows,
        "byEvidencePresence": evidence_rows,
        "sensitivity": sensitivity,
        "disagreements": disagreements,
        "limitations": [TWO_MODEL_CAVEAT, HUMAN_ANCHOR_NOTE],
    }


def _item_of(payload_b, review_id):
    for item in payload_b.get("items", []):
        if item.get("reviewId") == review_id:
            return item.get("item")
    return None
