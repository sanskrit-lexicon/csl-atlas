#!/usr/bin/env python3
"""Stage 4 external-portability gate census check (H7507).

Exit 0 iff the committed census is complete and internally consistent:
schema, licence envelope, all four §9 candidates present, every probe
timestamped (ISO-8601 UTC), every successful fetch hashed (sha256, 64 hex),
evidence files present with matching hashes, P1-P5 pre-registrations carried
verbatim, reversal conditions each dated, Part 2 skip consistent with the
ONP gate verdict.
"""
import hashlib
import json
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parent.parent
CENSUS = ROOT / "data" / "stage4_portability" / "stage4_gate_census.json"

TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")

REQUIRED_CANDIDATES = {
    "ONP↔Menota",
    "CAD↔Oracc/CDLI",
    "Russian Словарь XI–XVII вв.↔web-corpora.net",
    "GDLI↔OVI/TLIO",
}

ALLOWED_VERDICTS = {
    "closed",
    "held (unchanged) — no post-1375 independent Italian inventory appeared",
    "verification precondition now satisfied — host and dictionary interface VERIFIED from an external network",
    "public and structured-accessible (not the binding gate)",
}

P_KEYS = ("P1", "P2", "P3", "P4", "P5")

checks = 0


def ok(cond: bool, label: str) -> None:
    global checks
    checks += 1
    if not cond:
        print(f"FAIL: {label}", file=sys.stderr)
        raise SystemExit(1)


def main() -> int:
    d = json.loads(CENSUS.read_text(encoding="utf-8"))

    ok(d.get("schema") == "stage4-gate-census/1", "schema")
    ok(d.get("license") == "CC-BY-SA-4.0" and "licenseUrl" in d, "licence envelope (H5303)")
    ok(d.get("handoff") == "H7507", "handoff pin")
    ok(TS_RE.match(d.get("census_window_utc", "").split("/")[0] or ""), "census window start timestamp")
    ok(d.get("part2_onp_menota_executed") is False, "Part 2 execution flag")

    names = [c["candidate"] for c in d["candidates"]]
    ok(set(names) == REQUIRED_CANDIDATES, f"candidate set exactly the four §9 rows (got {sorted(names)})")

    for c in d["candidates"]:
        label = c["candidate"]
        ok(c.get("gate_verdict") in ALLOWED_VERDICTS, f"{label}: verdict vocabulary")
        ok(bool(c.get("probes")), f"{label}: at least one probe")
        for p in c["probes"]:
            ok(bool(TS_RE.match(p.get("ts_utc", ""))), f"{label}: probe timestamp {p.get('ts_utc')!r}")
            ok("url" in p, f"{label}: probe url")
            status = p.get("http_status")
            if status == 200:
                ok(
                    SHA_RE.match(p.get("sha256", "")) or "evidence" in p,
                    f"{label}: 200-probe hashed or evidenced ({p['url']})",
                )
            else:
                ok(bool(p.get("transport")), f"{label}: failed probe carries transport error ({p['url']})")
            if "evidence" in p:
                evp = ROOT / "data" / "stage4_portability" / p["evidence"]["file"]
                ok(evp.exists(), f"{label}: evidence file {evp.name}")
                if evp.exists():
                    digest = hashlib.sha256(evp.read_bytes()).hexdigest()
                    ok(digest == p["evidence"]["sha256"], f"{label}: evidence sha256 {evp.name}")
                    ok(evp.stat().st_size == p["evidence"]["bytes"], f"{label}: evidence bytes {evp.name}")

    onp = next(c for c in d["candidates"] if c["candidate"] == "ONP↔Menota")
    ok(onp["gate_verdict"] == "closed", "ONP gate closed")
    ok("dated_permission" in onp["gate_arms"] and "reachable_structured_deposit" in onp["gate_arms"], "ONP gate arms named")
    ok("metadata-only" in d["part2_skip_reason"], "skip reason names the metadata-only deposit")

    menota = onp["menota_corpus_side"]
    counts = menota["probes"][-1]["counts"]
    ok(counts["total"] == sum(counts[k] for k in ("main_codices", "charters", "runic_inscriptions", "le_lingue_nordiche")), "Menota counts sum")
    ok(counts["total"] == 394, "Menota total 394")

    rus = next(c for c in d["candidates"] if c["candidate"].startswith("Russian"))
    ok("VERIFIED from an external network" in rus["gate_verdict"], "Russian verdict records external verification")

    rr = d["reversal_conditions_recheck"]
    ok(len(rr) == 4, "four reversal conditions re-checked")
    ok(all(r.get("fired") is False or r.get("fired") is None for r in rr), "no reversal fired")
    ok(all(TS_RE.match(r.get("ts_utc", "")) for r in rr), "reversal evidence dated (ts_utc)")

    pre = d["preregistrations_onp_menota_p1_p5"]
    ok(pre["status"].startswith("fixed in advance"), "P1-P5 status fixed-in-advance")
    ok(all(k in pre for k in P_KEYS), "P1-P5 all present")
    ok("falsif" in pre["P1"] and "falsif" in pre["P2"], "P1/P2 carry falsification clauses")
    ok(bool(d.get("section9_reading_printed_alongside")), "§9 reading printed alongside")

    print(f"stage4_portability_check: OK ({checks} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
