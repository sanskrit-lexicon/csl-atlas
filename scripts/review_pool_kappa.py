#!/usr/bin/env python3
"""Review-pool kappa report — Cohen's κ between two decisions.json files of the
same review-sheet packet (double-keying / inter-annotator agreement).

Two annotators independently fill the same review sheet; each exports a
decisions.json shaped exactly like the shared emitter's download payload
(csl_pyutil review_sheet.py: {sheet_id, generated, decided, items:[{id, decision,
note}]}, decision ∈ {approve, reject, defer} or null when unvoted). This tool
joins the two files on item id and reports:

  * raw agreement (percent observed identical votes),
  * Cohen's κ with a 95% confidence interval (asymptotic normal SE, Fleiss:
    SE = sqrt(po(1-po)) / ((1-pe)·√n), CI clipped to [-1, 1]),
  * the confusion table (annotator A rows × annotator B columns),
  * the disagreement rows with both notes, for adjudication.

Degenerate inputs are reported honestly, never fudged: if every paired opinion
falls in a single class (pe = 1) κ is undefined — the report carries
"cohenKappa": null with a degenerate note, and the raw agreement still stands.
Items seen by only one annotator, or left unvoted by either, are excluded from
κ and listed under coverage warnings.

Prior art: scripts/lexico/root_agreement_kappa.py (marginal-based pe, Landis-
Koch bands) and csl-observatory scripts/obs_t_gold.py (cohen_kappa over paired
labels, confusion Counter). House schema validation: scripts/validate_review_decisions.py.

Usage:
  python scripts/review_pool_kappa.py FILE_A.json FILE_B.json [--out report.json] [--json]

Exit codes: 0 report produced (including degenerate-κ); 2 schema/validation error.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

VALID_DECISIONS = ("approve", "reject", "defer")
Z_95 = 1.959963984540054  # two-sided 95% normal quantile


class KappaInputError(ValueError):
    """A decisions file is not an admissible review-sheet export."""


def landis_koch(kappa):
    if kappa is None:
        return None
    if kappa < 0:
        return "poor"
    if kappa < 0.20:
        return "slight"
    if kappa < 0.40:
        return "fair"
    if kappa < 0.60:
        return "moderate"
    if kappa < 0.80:
        return "substantial"
    return "almost-perfect"


def load_decisions(path):
    """Validate and load one decisions.json -> {meta, votes: {id: (decision, note)}}."""
    try:
        with open(path, encoding="utf-8") as fh:
            payload = json.load(fh)
    except FileNotFoundError:
        raise KappaInputError(f"file not found: {path}") from None
    except json.JSONDecodeError as exc:
        raise KappaInputError(f"{path}: not valid JSON ({exc})") from None
    if not isinstance(payload, dict):
        raise KappaInputError(f"{path}: top level must be an object")
    items = payload.get("items")
    if not isinstance(items, list):
        raise KappaInputError(f"{path}: 'items' must be a list")
    votes = {}
    for idx, item in enumerate(items):
        if not isinstance(item, dict) or "id" not in item:
            raise KappaInputError(f"{path}: items[{idx}] lacks an 'id'")
        item_id = str(item["id"])
        if item_id in votes:
            raise KappaInputError(f"{path}: duplicate item id {item_id!r}")
        decision = item.get("decision")
        if decision is not None and decision not in VALID_DECISIONS:
            raise KappaInputError(
                f"{path}: items[{idx}] decision {decision!r} not in {VALID_DECISIONS} (or null)"
            )
        votes[item_id] = (decision, str(item.get("note") or ""))
    meta = {
        "path": os.path.abspath(path),
        "sheetId": payload.get("sheet_id"),
        "generated": payload.get("generated"),
        "decided": payload.get("decided"),
        "reviewer": payload.get("reviewer"),
        "reviewedAt": payload.get("reviewedAt"),
        "complete": payload.get("complete"),
    }
    return {"meta": meta, "votes": votes}


def agreement_stats(pairs):
    """Cohen's κ + 95% CI over [(label_a, label_b), ...].

    Returns dict with n, observed (po), expected (pe), kappa, ci95 [lo, hi],
    band, and a degenerate flag. κ is None exactly when pe == 1 (single class on
    both sides — chance agreement saturates and κ is undefined).
    """
    n = len(pairs)
    if n == 0:
        return {"n": 0, "observed": None, "expected": None, "kappa": None,
                "ci95": None, "band": None, "degenerate": None}
    observed = sum(1 for a, b in pairs if a == b) / n
    from collections import Counter
    ca = Counter(a for a, _ in pairs)
    cb = Counter(b for _, b in pairs)
    expected = sum((ca[c] / n) * (cb[c] / n) for c in set(ca) | set(cb))
    degenerate = expected >= 1.0 - 1e-12
    if degenerate:
        return {"n": n, "observed": observed, "expected": expected, "kappa": None,
                "ci95": None, "band": None, "degenerate": True}
    kappa = (observed - expected) / (1 - expected)
    se = math.sqrt(observed * (1 - observed)) / ((1 - expected) * math.sqrt(n))
    lo = max(-1.0, kappa - Z_95 * se)
    hi = min(1.0, kappa + Z_95 * se)
    return {"n": n, "observed": observed, "expected": expected, "kappa": kappa,
            "ci95": [lo, hi], "band": landis_koch(kappa), "degenerate": False}


def build_report(load_a, load_b, label_a="annotator A", label_b="annotator B"):
    """Join two loaded decisions files and build the full report dict."""
    meta_a, meta_b = load_a["meta"], load_b["meta"]
    votes_a, votes_b = load_a["votes"], load_b["votes"]

    ids_a, ids_b = set(votes_a), set(votes_b)
    only_a = sorted(ids_a - ids_b)
    only_b = sorted(ids_b - ids_a)
    shared = sorted(ids_a & ids_b)

    pairs, disagreements, unvoted = [], [], []
    for item_id in shared:
        dec_a, note_a = votes_a[item_id]
        dec_b, note_b = votes_b[item_id]
        if dec_a is None or dec_b is None:
            unvoted.append({"id": item_id, "decisionA": dec_a, "decisionB": dec_b})
            continue
        pairs.append((dec_a, dec_b))
        if dec_a != dec_b:
            disagreements.append({"id": item_id, "decisionA": dec_a,
                                  "decisionB": dec_b, "noteA": note_a, "noteB": note_b})

    stats = agreement_stats(pairs)

    labels = sorted({d for p in pairs for d in p})
    confusion = {a: {b: 0 for b in labels} for a in labels}
    for a, b in pairs:
        confusion[a][b] += 1

    warnings = []
    if meta_a["sheetId"] != meta_b["sheetId"]:
        warnings.append(
            f"sheet_id mismatch: {meta_a['sheetId']!r} vs {meta_b['sheetId']!r} — "
            "confirm both files describe the same packet"
        )
    if only_a:
        warnings.append(f"{len(only_a)} id(s) only in {label_a} (excluded): {only_a[:10]}"
                        + (" …" if len(only_a) > 10 else ""))
    if only_b:
        warnings.append(f"{len(only_b)} id(s) only in {label_b} (excluded): {only_b[:10]}"
                        + (" …" if len(only_b) > 10 else ""))
    if unvoted:
        warnings.append(f"{len(unvoted)} id(s) unvoted by at least one annotator (excluded)")
    if stats["n"] == 0:
        warnings.append("no paired opinions — κ not computable")

    return {
        "schemaVersion": "1.0.0",
        "generatedBy": "python scripts/review_pool_kappa.py",
        "fileA": meta_a,
        "fileB": meta_b,
        "labelA": label_a,
        "labelB": label_b,
        "packet": {
            "idsInA": len(ids_a),
            "idsInB": len(ids_b),
            "idsShared": len(shared),
            "pairedVoted": stats["n"],
            "onlyInA": only_a,
            "onlyInB": only_b,
            "unvotedEither": [r["id"] for r in unvoted],
        },
        "agreement": {
            "rawAgreementPct": round(100 * stats["observed"], 1) if stats["observed"] is not None else None,
            "chanceExpectedPct": round(100 * stats["expected"], 1) if stats["expected"] is not None else None,
            "cohenKappa": round(stats["kappa"], 4) if stats["kappa"] is not None else None,
            "kappaCi95": ([round(stats["ci95"][0], 4), round(stats["ci95"][1], 4)]
                          if stats["ci95"] is not None else None),
            "band": stats["band"],
            "degenerate": stats["degenerate"],
            "degenerateNote": ("single class on both sides (chance agreement = 1): "
                               "κ undefined, raw agreement stands" if stats["degenerate"] else None),
        },
        "confusion": {"rows": labels, "columns": labels, "matrix": confusion},
        "disagreements": disagreements,
        "warnings": warnings,
    }


def render_markdown(report):
    """Human-readable summary of the report dict (what MG reads)."""
    L = []
    A = L.append
    ag = report["agreement"]
    sheet = report["fileA"].get("sheetId") or "(unnamed sheet)"
    A(f"# Review-pool kappa report — {sheet}")
    A("")
    A(f"Files: `{os.path.basename(report['fileA']['path'])}` ({report['labelA']}) vs "
      f"`{os.path.basename(report['fileB']['path'])}` ({report['labelB']}).")
    A("")
    pk = report["packet"]
    A(f"Paired opinions: **{pk['pairedVoted']}** of {pk['idsShared']} shared ids "
      f"({len(pk['onlyInA'])} only in {report['labelA']}, {len(pk['onlyInB'])} only in "
      f"{report['labelB']}, {len(pk['unvotedEither'])} unvoted by either).")
    A("")
    if ag["rawAgreementPct"] is None:
        A("Raw agreement and Cohen κ: **not computable** (no paired opinions).")
    elif ag["cohenKappa"] is None:
        note = ag.get("degenerateNote") or "kappa undefined"
        A(f"Raw agreement: **{ag['rawAgreementPct']}%** — Cohen κ: **undefined** ({note}).")
    else:
        lo, hi = ag["kappaCi95"]
        A(f"Raw agreement: **{ag['rawAgreementPct']}%** (chance-expected "
          f"{ag['chanceExpectedPct']}%) — Cohen κ: **{ag['cohenKappa']}** "
          f"(95% CI {lo}–{hi}, band `{ag['band']}`).")
    A("")
    A(f"## Confusion ({report['labelA']} rows × {report['labelB']} columns)")
    A("")
    if report["confusion"]["rows"]:
        A("| A \\ B | " + " | ".join(report["confusion"]["columns"]) + " | total |")
        A("|---|" + "---:|" * (len(report["confusion"]["columns"]) + 1))
        for row_label in report["confusion"]["rows"]:
            cells = report["confusion"]["matrix"][row_label]
            total = sum(cells.values())
            A(f"| **{row_label}** | " + " | ".join(str(cells[c]) for c in report["confusion"]["columns"])
              + f" | {total} |")
    else:
        A("_(no paired opinions)_")
    A("")
    A(f"## Disagreements ({len(report['disagreements'])}) — for adjudication")
    A("")
    if report["disagreements"]:
        A("| id | " + report["labelA"] + " | " + report["labelB"]
          + " | note A | note B |")
        A("|---|---|---|---|---|")
        for r in report["disagreements"]:
            A(f"| `{r['id']}` | {r['decisionA']} | {r['decisionB']} "
              f"| {r['noteA'] or '—'} | {r['noteB'] or '—'} |")
    else:
        A("_(none — full agreement on paired opinions)_")
    A("")
    if report["warnings"]:
        A("## Warnings")
        A("")
        for w in report["warnings"]:
            A(f"- {w}")
        A("")
    A("_Generated by `python scripts/review_pool_kappa.py`._")
    A("")
    return "\n".join(L)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Cohen kappa report from two decisions.json files of the same packet"
    )
    parser.add_argument("file_a", help="first annotator's decisions.json")
    parser.add_argument("file_b", help="second annotator's decisions.json")
    parser.add_argument("--out", default=None, help="write the JSON report to this path")
    parser.add_argument("--json", action="store_true", help="print the JSON report instead of markdown")
    parser.add_argument("--label-a", default="annotator A")
    parser.add_argument("--label-b", default="annotator B")
    args = parser.parse_args(argv)

    try:
        report = build_report(load_decisions(args.file_a), load_decisions(args.file_b),
                              label_a=args.label_a, label_b=args.label_b)
    except KappaInputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        print(f"wrote {args.out}")

    print(render_markdown(report) if not args.json else json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
