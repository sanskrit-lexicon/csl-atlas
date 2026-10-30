#!/usr/bin/env python3
"""H7523 Stage 4c check: validate the R1-R5 run artefact set.

Exit 0 + "OK: N checks" on pass; non-zero + named failures. Validates the committed
aggregates only (no network, no DB redistribution).
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "r1_r5_results.json"
REPORT = HERE / "REPORT_stage4c_r1_r5_run_2026-10-30.md"
RECHECK = HERE / "identity_recheck_2026-10-30.md"
COMPUTE = HERE / "compute_r1_r5.py"

DUMP_SHA = "532cad47eb4e3a2c12161a2402ae645d166ea35dcf96d2a7429c8e84400685fc"

failures = []
checks = 0


def check(name, ok):
    global checks
    checks += 1
    if not ok:
        failures.append(name)


def main():
    check("results JSON parses", RESULTS.exists())
    d = json.loads(RESULTS.read_text(encoding="utf-8"))

    meta = d.get("run_meta", {})
    check("handoff is H7523", meta.get("handoff") == "H7523")
    check("preregistration names H7518/#687", "H7518" in meta.get("preregistration", "") and "687" in meta.get("preregistration", ""))
    check("MG ruling recorded in licence_gate", "MG ruling" in meta.get("licence_gate", ""))
    check("dump hash pinned", meta.get("dump_expected_sha256") == DUMP_SHA)
    check("computed_utc dated", bool(re.match(r"^2026-10-30T", meta.get("computed_utc", ""))))
    check("siglum unit convention declared", "siglum" in meta.get("unit_convention", "").lower())

    jv = d.get("join_view", {})
    check("joined examples 10318", jv.get("joined_examples") == 10318)
    check("siglum groups 825", jv.get("distinct_siglum_groups_cited") == 825)

    r1 = d["R1"]
    check("R1 SUPPORTED", r1["adjudication"].startswith("SUPPORTED"))
    check("R1 top-decile >= 0.20 (falsifier bar)", r1["top_decile_mass_share"] >= 0.20)
    check("R1 falsifier not fired", r1["falsifier_fired"] is False)
    check("R1 gini present 0..1", 0 < r1["gini"] < 1)
    check("R1 deciles sum ~1", abs(sum(r1["decile_shares_desc"]) - 1.0) < 0.01)

    r2 = d["R2"]
    check("R2 UNTESTABLE pre-declared", "UNTESTABLE-ON-THIS-SUBSTRATE" in r2["adjudication"])
    check("R2 no declaration hits", r2["declaration_hits"] == [])
    check("R2 fallback text carried", "never silently adapted" in r2["pre_declared_fallback"])

    r3 = d["R3"]
    check("R3 SUPPORTED", r3["adjudication"].startswith("SUPPORTED"))
    check("R3 rho < 0.90 (divergence)", r3["spearman_rho"] < 0.90)
    check("R3 shared sigla >= 100", r3["n_shared_sigla"] >= 100)
    check("R3 p-value tiny", r3["p_value"] < 1e-30)

    r4 = d["R4"]
    check("R4 SUPPORTED", r4["adjudication"].startswith("SUPPORTED"))
    check("R4 min pairwise < 0.95", r4["min_pairwise_rho"] < 0.95)
    check("R4 count-family mutually >= 0.99", all(v >= 0.99 for k, v in r4["pairwise_spearman"].items() if "row_density" not in k))
    check("R4 density-family < 0.65", all(v < 0.65 for k, v in r4["pairwise_spearman"].items() if "row_density" in k))

    r5 = d["R5"]
    check("R5 vacuous-direction recorded", "UNTESTABLE-IN-PRE-REGISTERED-DIRECTION" in r5["adjudication"])
    check("R5 evidence 8400/8399/1", r5["evidence"]["declared_source_rows"] == 8400 and r5["evidence"]["cited_source_rows"] == 8399 and r5["evidence"]["never_cited_source_rows"] == 1)
    check("R5 no post-hoc pivot language", "no post-hoc pivot" in r5["reason"].lower() or "never" in r5["reason"].lower() or "vacuous" in r5["reason"].lower())

    # report: table carries all five adjudications + no relative hrefs
    rb = REPORT.read_text(encoding="utf-8")
    for tok in ("SUPPORTED", "UNTESTABLE-ON-THIS-SUBSTRATE", "UNTESTABLE-IN-PRE-REGISTERED-DIRECTION", "0.744", "57.0%", "family-structured"):
        check(f"report carries {tok!r}", tok in rb)
    check("report no relative hrefs", not re.search(r"\]\((?!http)[^)]+\)", rb))
    check("report byline", "Dr. Mārcis Gasūns" in rb)

    # identity re-check + compute script present with pinned hash + seed
    check("identity recheck exists", RECHECK.exists())
    if RECHECK.exists():
        check("recheck hash matches", DUMP_SHA in RECHECK.read_text(encoding="utf-8"))
        check("recheck count 6284", "6284" in RECHECK.read_text(encoding="utf-8"))
    cb = COMPUTE.read_text(encoding="utf-8")
    check("compute pins hash", DUMP_SHA in cb)
    check("compute seed 7523", "7523" in cb)

    if failures:
        print(f"FAIL ({len(failures)} of {checks} checks): " + "; ".join(failures[:10]))
        return 1
    print(f"OK: {checks} checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
