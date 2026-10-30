#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7476 — regeneration gate: every published NWS-layer Stage 2 number
regenerates from the committed row-level TSVs or the check exits non-zero.

Re-derives all three roles' measurements (attestation-mass vs PW under H5,
declared-vs-exercised under H6, dependence tracer) exactly as
scripts/nws_layer_join.py derives them, pin-compares against
data/nws_layer/nws_layer_metrics.json, verifies the substrate pins and the
dated-scrape provenance, re-runs the declared H5 verdict mapping (mirrored
here on purpose: a threshold edit must touch both files or this gate fails),
and enforces the H6 retraction guard (the filename-stem-derived 82.7 figure
must never appear).

    python scripts/nws_layer_check.py
"""
from __future__ import annotations

import csv
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "nws_layer")

# H5 mapping — deliberate mirror of scripts/nws_layer_join.py (two-place gate)
H5_TRACKS_RHO = 0.60
H5_DIVERGENT_RHO = 0.40
H5_TRACKS_MAX_INV = 1
H5_DIVERGENT_MIN_INV = 3

SCRAPE_FETCHED = "2026-10-06"
SCRAPE_HTML_SHA = "86c9495e0cbe7824d9d1496974f245fab4d3cfb873cee1ce225defb20bbb8aa7"
TAR_SHA = "054b05da96df2f1af2c95c02b7e15d87f8a616d4eaa339f93e3ed7430e07f00c"
PWG_SHA = "430c910f8b0c9229d89ef1580b2385883ce5f4e2ee83dfc6ecb7d6251bb62166"


def load_tsv(path):
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def rankdata(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j + 2) / 2.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def pearson(xs, ys):
    n = len(xs)
    if n == 0:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return None
    return sxy / (sxx ** 0.5 * syy ** 0.5)


def spearman(xs, ys):
    r = pearson(rankdata(xs), rankdata(ys))
    return None if r is None else round(r, 4)


def verdict_from(rho, inv):
    if rho is None:
        return "undetermined"
    if rho >= H5_TRACKS_RHO and inv <= H5_TRACKS_MAX_INV:
        return "tracks"
    if rho < H5_DIVERGENT_RHO or inv >= H5_DIVERGENT_MIN_INV:
        return "divergent"
    return "mixed"


def main() -> int:
    hw = load_tsv(os.path.join(D, "nws_headword_mass.tsv"))
    works = load_tsv(os.path.join(D, "nws_works_attestation.tsv"))
    pwg = load_tsv(os.path.join(D, "pwg_headword_ql.tsv"))
    env = load_tsv(os.path.join(D, "nws_letter_envelope.tsv"))
    census = load_tsv(os.path.join(D, "nws_x_mw_census.tsv"))
    pins = json.load(open(os.path.join(D, "nws_layer_pins.json"), encoding="utf-8"))
    registry = json.load(open(os.path.join(D, "nws_works_registry.json"),
                              encoding="utf-8"))
    metrics_text = open(os.path.join(D, "nws_layer_metrics.json"),
                        encoding="utf-8").read()
    m = json.loads(metrics_text)
    fails: list[str] = []

    def pin(name, got, want):
        if got != want:
            fails.append(f"{name}: regenerated {got!r} != published {want!r}")

    # ---- substrate pins ----------------------------------------------------
    prov = registry["provenance"]
    pin("registry.works", len(registry["works"]), 174)
    pin("registry.fetched", prov["fetched"], SCRAPE_FETCHED)
    pin("registry.html_sha256", prov["html_sha256"], SCRAPE_HTML_SHA)
    if not registry.get("license"):
        fails.append("registry copy: no licence envelope (H5303)")
    pin("pins.nws_tar.sha256", pins["nws_tar"]["sha256"], TAR_SHA)
    pin("pins.pwg_txt.sha256", pins["pwg_txt"]["sha256"], PWG_SHA)
    pin("pins.scrape_echo", pins["works_registry_scrape"]["html_sha256"], SCRAPE_HTML_SHA)
    pin("rows.headword", len(hw), 34101)
    pin("rows.works", len(works), 174)
    pin("rows.pwg", len(pwg), 123366)
    pin("envelope.keys_total", sum(int(r["keys_total"]) for r in env), 167990)
    pin("envelope.keys_prose", sum(int(r["keys_prose"]) for r in env), 34101)
    pin("hw.page_refs", sum(int(r["page_refs"]) for r in hw), 8440)
    pin("hw.lit_refs", sum(int(r["lit_refs"]) for r in hw), 8937)
    pin("hw.dict_marker_entries", sum(1 for r in hw if int(r["dict_markers"]) > 0), 4941)
    pin("pwg.ql_total", sum(int(r["ql_tags"]) for r in pwg), 729719)
    pin("pwg.raw_total", sum(int(r["raw_tags"]) for r in pwg), 801788)

    # ---- role 1 regeneration -------------------------------------------------
    pwg_ql: dict[str, int] = {}
    for r in pwg:
        pwg_ql[r["k1"]] = pwg_ql.get(r["k1"], 0) + int(r["ql_tags"])
    shared = [r for r in hw if r["key1"] in pwg_ql]
    mass_total = [int(r["sigla"]) + int(r["page_refs"]) + int(r["lit_refs"])
                  for r in shared]
    ql = [pwg_ql[r["key1"]] for r in shared]
    n = len(shared)
    r1 = m["role1_attestation_mass"]
    pin("r1.shared", n, r1["shared_headwords"])
    pin("r1.containment_pct", round(100.0 * n / len(hw), 2), r1["containment_pct"])
    pin("r1.outside", len(hw) - n, r1["nws_keys_outside_pwg"])
    rho_total = spearman(mass_total, ql)
    pin("r1.rho_total", rho_total, r1["spearman_vs_pwg_ql"]["mass_total"])
    rho_own = spearman([m_ - int(r["x_mw_family"]) for m_, r in zip(mass_total, shared)], ql)
    pin("r1.rho_own", rho_own, r1["spearman_vs_pwg_ql"]["mass_own_ex_mw"])

    order = sorted(range(n), key=lambda i: ql[i])
    means, inv_check = [], 0
    B = 10
    tot_mass = sum(mass_total)
    for b in range(B):
        seg = order[b * n // B:(b + 1) * n // B]
        if not seg:
            continue
        mean = round(sum(mass_total[i] for i in seg) / len(seg), 3)
        if means and mean < means[-1]:
            inv_check += 1
        means.append(mean)
        pin(f"r1.decile{b + 1}.mean", mean,
            r1["decile_profile"][b]["nws_mass_mean"])
        pin(f"r1.decile{b + 1}.share",
            round(100.0 * sum(mass_total[i] for i in seg) / max(1, tot_mass), 2),
            r1["decile_profile"][b]["nws_mass_share_pct"])
    pin("r1.inversions", inv_check, r1["decile_inversions"])

    treated = {r["key1"] for r in hw}
    pw_treated = sum(v for k, v in pwg_ql.items() if k in treated)
    pin("r1.treated_ql", pw_treated, r1["pwg_ql_on_nws_treated_keys"]["treated"])
    pin("r1.treated_share_pct", round(100.0 * pw_treated / sum(pwg_ql.values()), 2),
        r1["pwg_ql_on_nws_treated_keys"]["share_pct"])
    pin("r1.envelope_pct", round(100.0 * sum(int(r["keys_prose"]) for r in env)
                                 / sum(int(r["keys_total"]) for r in env), 2),
        r1["denominators"]["digitized_envelope_pct"])

    # ---- role 2 regeneration (H6) ---------------------------------------------
    r2 = m["role2_declared_vs_exercised"]
    att = sum(1 for r in works if r["attested"] == "1")
    pin("r2.declared", len(works), r2["declared_works"])
    pin("r2.attested", att, r2["attested_works"])
    pin("r2.attested_pct", round(100.0 * att / len(works), 2), r2["attested_pct"])
    pin("r2.zero", sum(1 for r in works if r["attested"] == "0"),
        r2["zero_citation_works"])
    pin("r2.scrape.sha", r2["scrape"]["html_sha256"], SCRAPE_HTML_SHA)
    pin("r2.scrape.fetched", r2["scrape"]["fetched"], SCRAPE_FETCHED)
    # H6 retraction guard: the filename-stem artefact figure must never appear
    # as a published NUMBER (the ban declaration itself may spell it out).
    def numbers(o):
        if isinstance(o, dict):
            for v in o.values():
                yield from numbers(v)
        elif isinstance(o, list):
            for v in o:
                yield from numbers(v)
        elif isinstance(o, (int, float)):
            yield float(o)
    if any(abs(x - 82.7) < 1e-9 for x in numbers(m)):
        fails.append("H6 guard: retracted 82.7 figure used as a published number")
    if "filename stem" not in r2["method"] and "filename stems" not in r2["method"]:
        fails.append("H6 guard: method string lost its never-from-stems contract")

    # ---- role 3 regeneration ----------------------------------------------------
    r3 = m["role3_dependence_tracer"]
    pure = [r for r in hw
            if int(r["x_mw_family"]) == int(r["sigla"]) and int(r["sigla"]) > 0
            and int(r["page_refs"]) == 0 and int(r["lit_refs"]) == 0]
    pin("r3.lex_mw", sum(int(r["lex_mw"]) for r in hw), r3["lex_mw_markers"])
    pin("r3.family", sum(int(r["x_mw_family"]) for r in hw), r3["x_mw_family_total"])
    pin("r3.kinds", len(census), r3["x_mw_kinds"])
    pin("r3.census_lexmw", int(census[0]["count"]) if census else -1, 5873)
    pin("r3.fam_entries", sum(1 for r in hw if int(r["x_mw_family"]) > 0),
        r3["entries_with_family_marker"])
    pin("r3.pure", len(pure), r3["pure_mw_mediated_entries"])

    # ---- H5 verdict: re-derive through the mirrored mapping -------------------
    got_verdict = verdict_from(rho_total, inv_check)
    pin("h5.verdict", got_verdict, m["h5"]["verdict"])
    pin("h5.remainder_quantified", m["h5"]["upgrade_conditional"] is not None,
        True)

    if fails:
        print("NWS_LAYER_CHECK: FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("NWS_LAYER_CHECK: OK — every published number regenerates from rows; "
          f"H5={got_verdict} (rho={rho_total}), H6={att}/174, scrape "
          f"{SCRAPE_FETCHED} sha {SCRAPE_HTML_SHA[:8]}…")
    return 0


if __name__ == "__main__":
    sys.exit(main())
