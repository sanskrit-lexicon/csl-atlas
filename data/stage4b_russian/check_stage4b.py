#!/usr/bin/env python3
"""H7518 Stage 4b check: validate the Russian-analogue executability artefact set.

Exit 0 + "N checks" on pass; non-zero + named failure on any miss. No network, no
redistribution of the unlicensed RusDict.db — this validates the committed artefacts
only (internal consistency, evidence presence, denominator coherence).
"""
import hashlib
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
VERDICT = HERE / "stage4b_executability_verdict.json"
REPORT = HERE / "REPORT_stage4b_russian_executability_2026-10-30.md"
EVIDENCE = HERE / "probe_evidence"

DB_SHA256 = "532cad47eb4e3a2c12161a2402ae645d166ea35dcf96d2a7429c8e84400685fc"
DB_BYTES = 25174016

failures = []
checks = 0


def check(name, ok):
    global checks
    checks += 1
    if not ok:
        failures.append(name)


def main():
    check("verdict JSON parses", VERDUCT_OK() if (VERDICT.exists()) else False)

    v = json.loads(VERDICT.read_text(encoding="utf-8"))

    # schema identity
    check("schema is stage4b-executability-verdict/1", v.get("schema") == "stage4b-executability-verdict/1")
    check("handoff is H7518", v.get("handoff") == "H7518")
    check("verdict non-empty", bool(v.get("verdict")))

    # the dump is dated + hashed everywhere it appears
    probes_blob = json.dumps(v.get("probes", [])) + v.get("verdict_detail", "")
    check("DB sha256 recorded", DB_SHA256 in probes_blob)
    check("DB byte size recorded", str(DB_BYTES) in probes_blob)

    # every probe carries a UTC timestamp and a network attribution
    for i, p in enumerate(v.get("probes", [])):
        check(f"probe[{i}] ts_utc", bool(re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", p.get("ts_utc", ""))))
        check(f"probe[{i}] network/kind", bool(p.get("network") or p.get("kind")))

    # kill-exit logic: dump exists => kill-exit must NOT fire
    ke = v.get("kill_exit_check", {})
    check("kill-exit fired=false with a dump present", ke.get("fired") is False)
    check("kill-exit reason names the dump arm", "dump" in ke.get("reason", "").lower())

    # denominators: internal coherence
    d = v.get("dump_denominators", {})
    check("words within 1% of live 6284 (same generation)", abs(d.get("words", 0) - 6284) <= 63)
    check("examples >= joined", d.get("examples", 0) >= d.get("examples_joining_sources", 0))
    jf = d.get("join_fraction", 1)
    expected_jf = round(d.get("examples_joining_sources", 0) / max(d.get("examples", 1), 1), 4)
    check("join_fraction recomputes", abs(jf - expected_jf) <= 0.001)
    check("sources rows positive", d.get("sources_rows", 0) > 0)
    check("partial apparatus named (S..T)", "S..T" in d.get("alphabet_span", "") or "С..Т" in d.get("alphabet_span", ""))
    check("siglum unit convention set", "siglum" in v.get("preregistration_russian_analogues", {}).get("unit_convention", "").lower())

    # pre-registration completeness: R1-R5 fixed in advance, each with analogue + hypothesis
    pre = v.get("preregistration_russian_analogues", {})
    check("preregistration marked fixed-in-advance unexecuted", "FIXED IN ADVANCE" in pre.get("status", "").upper())
    for rid in ("R1", "R2", "R3", "R4", "R5"):
        r = pre.get(rid, {})
        check(f"{rid} present with hypothesis", bool(r.get("hypothesis")))
        check(f"{rid} names its P-analogue", bool(r.get("analogue_of")))
    check("R3 is the partial-apparatus test", "half" in pre.get("R3", {}).get("hypothesis", "").lower())
    check("licence gate before run declared", bool(pre.get("gate_before_any_run")))

    # bias register adaptations present (s11): at least the 3 named classes
    br = " ".join(v.get("bias_register_s11_adaptations", []))
    for token in ("licence", "provenance", "rot"):
        check(f"bias register covers '{token}'", token in br.lower())

    # export surface: no export route + the route list from source
    es = v.get("export_surface", {})
    check("no export/api route claimed", es.get("export_or_api_route_exists") is False)
    check("route list non-empty", len(es.get("wsgi_routes", [])) >= 5)

    # evidence files exist and carry their required markers
    required = {
        "github_repo_census_2026-10-30.md": [DB_SHA256, "6,307", "24,405", "8,400"],
        "deployed_code_identity_2026-10-30.md": ["Проект на GitHub", "Sokureo/RusDict", "2,262"],
        "oldrus_lists_live_2026-10-30.md": ["6284", "Дополнения по буквам С и Т"],
        "oldrus_wsgi_live_2026-10-30.md": ["Поиск по источникам", "Язык оригинала"],
    }
    for fname, markers in required.items():
        f = EVIDENCE / fname
        check(f"evidence {fname} exists", f.exists())
        if f.exists():
            body = f.read_text(encoding="utf-8")
            for m in markers:
                check(f"evidence {fname} contains {m[:32]!r}", m in body)

    # report: verdict + byline + no relative hrefs
    if REPORT.exists():
        rb = REPORT.read_text(encoding="utf-8")
        check("report states kill-exit did not fire", "did not\nfire" in rb or "did not fire" in rb)
        check("report byline present", "Dr. Mārcis Gasūns" in rb)
        check("report has no relative hrefs", not re.search(r"\]\((?!http)[^)]+\)", rb))
        check("report names R1-R5 table", all(f"**{r}**" in rb for r in ("R1", "R2", "R3", "R4", "R5")))
    else:
        check("report exists", False)

    if failures:
        print(f"FAIL ({len(failures)} of {checks} checks): " + "; ".join(failures[:10]))
        return 1
    print(f"OK: {checks} checks")
    return 0


def VERDUCT_OK():
    try:
        json.loads(VERDICT.read_text(encoding="utf-8"))
        return True
    except Exception:
        return False


if __name__ == "__main__":
    sys.exit(main())
