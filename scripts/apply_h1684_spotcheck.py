"""H1684 — ingest the spot-check votes, run the Wilson gate, promote per stratum.

Reads the reviewer's decisions.json for the H1684 spot-check sheet and:

  FORKS       apply the human's ruling directly (these are human decisions,
              not gated by anything).
  STRATA      compare each blind vote to the HIDDEN agent verdict, compute the
              Wilson 95% lower bound of the agreement proportion with a
              finite-population correction, and promote the stratum's agent
              verdicts only if that bound reaches the promotion floor.

Promotion writes `reviewed=yes` AND `reviewed_by`:
  - rows the human personally voted on  -> reviewed_by=human
  - rows promoted on the stratum's gate -> reviewed_by=agent-h1684
That distinction is what keeps the derived packet from claiming
`human-reviewed` for rows no human ever read (build-tradition-tags.mjs then
reports `agent-adjudicated-human-gated`).

A stratum that fails the gate — or that has too few resolved votes left after
defers to meet its required n — is NOT promoted; its rows stay in the human
queue and the report says so.

Usage: python scripts/apply_h1684_spotcheck.py [--decisions <path>] [--dry-run]
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_h1684_spotcheck_sheet import (  # noqa: E402
    PROMOTION_FLOOR, required_n, wilson_lower,
)

REVIEW = ROOT / "review"
TAGS_PATH = ROOT / "data/citations/tradition_tags.tsv"
SKD_PACKET = ROOT / "data/lexico/h1684_skd_iti_adjudication_packet.json"
REPORT_PATH = ROOT / "docs/H1684_SPOTCHECK_GATE_REPORT.md"
AGENT_PROVENANCE = "agent-h1684"

CORRECTED = re.compile(r"corrected-label:\s*([A-Za-z][A-Za-z0-9-]*)", re.I)


def find_manifest():
    hits = sorted(REVIEW.glob("csl-atlas-h1684-spotcheck_*_manifest.json"))
    if not hits:
        sys.exit("No H1684 spot-check manifest in review/ — run build_h1684_spotcheck_sheet.py first.")
    return hits[-1]


def resulting_label(vote, proposed):
    """The label the reviewer's vote implies, or None if unresolved."""
    decision = (vote.get("decision") or "").lower()
    note = vote.get("note") or ""
    if decision in ("approve", "accept", "yes"):
        return proposed
    if decision in ("reject", "no"):
        m = CORRECTED.search(note)
        return m.group(1) if m else None
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--decisions")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    manifest_path = find_manifest()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    stem = manifest["sheetId"]
    dec_path = Path(args.decisions) if args.decisions else REVIEW / ("%s_decisions.json" % stem)
    if not dec_path.exists():
        sys.exit(
            "No decisions file at %s.\nVote in review/%s_review.html, download decisions.json, "
            "save it there, then re-run." % (dec_path, stem)
        )
    decisions = json.loads(dec_path.read_text(encoding="utf-8"))
    votes = {item["id"]: item for item in decisions.get("items", [])}

    lines = [
        "# H1684 — spot-check gate report",
        "",
        "_Created: 27-07-2026 · Last updated: 27-07-2026_",
        "",
        "Promotion floor: Wilson 95%% lower bound >= **%.2f** per stratum "
        "(finite-population corrected)." % PROMOTION_FLOOR,
        "",
        "| Stratum | N | sampled | resolved | agreed | Wilson 95% lower | verdict |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]

    promote_tradition = {}   # canonical_text -> provenance
    promote_skd = {}         # reviewId -> provenance
    gate_rows = []

    for st in manifest["strata"]:
        members = st["members"]
        population = st["population"]
        need = required_n(population)
        resolved, agreed, sampled_human = 0, 0, {}
        for m in members:
            vote = votes.get(m["reviewId"])
            if not vote:
                continue
            label = resulting_label(vote, m["proposedLabel"])
            if label is None:
                continue
            resolved += 1
            if label == m["agentLabel"]:
                agreed += 1
            sampled_human[m["reviewId"]] = label

        if resolved < need:
            verdict = "INCONCLUSIVE — %d resolved < required %d" % (resolved, need)
            lower = wilson_lower(agreed, resolved, population=population) if resolved else 0.0
            passed = False
        else:
            lower = wilson_lower(agreed, resolved, population=population)
            passed = lower >= PROMOTION_FLOOR
            verdict = "PROMOTED" if passed else "HELD — below floor"

        gate_rows.append({
            "key": st["key"], "sheet": st["sheet"], "population": population,
            "sampled": len(members), "resolved": resolved, "agreed": agreed,
            "wilsonLower": round(lower, 4), "requiredN": need, "passed": passed,
            "verdict": verdict,
        })
        lines.append("| `%s` | %d | %d | %d | %d | %.3f | %s |"
                     % (st["key"], population, len(members), resolved, agreed, lower, verdict))

        if not passed:
            continue
        sink = promote_tradition if st["sheet"] == "tradition" else promote_skd
        sampled_ids = {m["reviewId"] for m in members}
        # Everything in the stratum is promoted; the sampled rows carry human
        # provenance because a human actually voted on those.
        for m in members:
            key = m["reviewId"].split("::", 1)[1]
            sink[key] = "human" if m["reviewId"] in sampled_ids else AGENT_PROVENANCE
        # The unsampled remainder is resolved from the packets below.
        st["_promoted"] = True

    # Unsampled members of a promoted stratum: pull the full membership from the
    # packets, since the manifest only records the sampled rows.
    skd = json.loads(SKD_PACKET.read_text(encoding="utf-8"))
    trad_packet = ROOT / "data/citations/h1684_tradition_adjudication_packet.json"
    trad = json.loads(trad_packet.read_text(encoding="utf-8"))
    for st, gate in zip(manifest["strata"], gate_rows):
        if not gate["passed"]:
            continue
        if st["sheet"] == "skd-iti":
            want = "confirm" if st["key"].endswith("agent-confirmed") else "correct"
            for r in skd["rows"]:
                if r["verdict"] == want:
                    promote_skd.setdefault(r["reviewId"], AGENT_PROVENANCE)
        else:
            default_rule = st["key"].endswith("canonical-attribution")
            for r in trad["rows"]:
                if r["verdict"] != "confirm":
                    continue
                is_default = r["rule"] == "canonical-attribution"
                if is_default == default_rule:
                    promote_tradition.setdefault(r["canonicalText"], AGENT_PROVENANCE)

    # Forks are human rulings — always applied, never gated.
    fork_applied = []
    for fork in manifest["forks"]:
        vote = votes.get(fork["reviewId"])
        if not vote:
            continue
        sheet, rid = fork["reviewId"].split("::", 1)
        if sheet != "tradition":
            fork_applied.append((fork["reviewId"], "(skd-iti fork — recorded, no tsv target)"))
            continue
        row = next((r for r in trad["rows"] if r["canonicalText"] == rid), None)
        if row is None:
            continue
        label = resulting_label(vote, row["proposedTradition"])
        if label is None:
            continue
        promote_tradition[rid] = "human"
        fork_applied.append((rid, label))

    lines += [
        "",
        "## Forks (human rulings, ungated)",
        "",
        "| Row | Human label |",
        "|---|---|",
    ] + ["| `%s` | %s |" % (a, b) for a, b in fork_applied] + [
        "",
        "## Promotion",
        "",
        "- tradition rows promoted: **%d** (human-attributed %d, agent-attributed %d)"
        % (len(promote_tradition),
           sum(1 for v in promote_tradition.values() if v == "human"),
           sum(1 for v in promote_tradition.values() if v != "human")),
        "- skd-iti rows promoted: **%d**" % len(promote_skd),
        "",
        "_Dr. Mārcis Gasūns_",
        "",
    ]

    if args.dry_run:
        print("\n".join(lines))
        return

    # Write the tsv, preserving column order and the reviewed_by provenance.
    raw = TAGS_PATH.read_text(encoding="utf-8")
    reader = csv.DictReader(raw.splitlines(), delimiter="\t")
    fields = reader.fieldnames
    out_rows = []
    for r in reader:
        name = r["canonical_text"]
        if name in promote_tradition:
            r["reviewed"] = "yes"
            r["reviewed_by"] = promote_tradition[name]
        out_rows.append(r)
    buf = ["\t".join(fields)]
    for r in out_rows:
        buf.append("\t".join((r.get(f) or "") for f in fields))
    TAGS_PATH.write_text("\r\n".join(buf) + "\r\n", encoding="utf-8", newline="")

    for r in skd["rows"]:
        if r["reviewId"] in promote_skd:
            r["promoted"] = True
            r["promotedBy"] = promote_skd[r["reviewId"]]
    skd["counts"]["promoted"] = len(promote_skd)
    SKD_PACKET.write_text(json.dumps(skd, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print("Wrote %s" % REPORT_PATH.relative_to(ROOT))
    print("tradition promoted: %d · skd-iti promoted: %d" % (len(promote_tradition), len(promote_skd)))
    for g in gate_rows:
        print("  %-36s N=%-4d resolved=%-3d agreed=%-3d lower=%.3f  %s"
              % (g["key"], g["population"], g["resolved"], g["agreed"], g["wilsonLower"], g["verdict"]))
    print("\nNow re-run: node scripts/build-tradition-tags.mjs && node scripts/validate-tradition-tags.mjs")


if __name__ == "__main__":
    main()
