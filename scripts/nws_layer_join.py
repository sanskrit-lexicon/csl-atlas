#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7476 — Stage 2: the NWS layer in its three delimited roles (§8, NWS roles).

Implements the PWG–NWS–PD–DCS programme's Stage 2 exactly as pre-registered
(report pwg-nws-pd-dcs-8294e5 §8): the NWS layer enters in THREE roles, each
with its denominator — (1) attestation-mass on shared headwords tracked
against PW's distribution under H5; (2) the declared-vs-exercised test
(H6, 82/174) recomputed ONLY from the dated scrape with its hash; (3) the
dependence tracer (X(MW) internal-source family). The NWS↔DCS inventory join
stays PRE-REGISTERED OUT. Runs ONLY on committed row-level TSVs — no private
inputs — so scripts/nws_layer_check.py can gate every number.

H5 operationalization (protocol pins the direction, not a number; this
mapping was declared before the join ran on the measured rows and is NOT
retuned after): tracks = rho(total mass vs PW ql) >= 0.60 AND decile-profile
inversions <= 1; divergent = rho < 0.40 OR inversions >= 3; else mixed.

Inputs (all committed under data/nws_layer/):
  nws_headword_mass.tsv  nws_works_attestation.tsv  nws_works_registry.json
  pwg_headword_ql.tsv    nws_letter_envelope.tsv    nws_x_mw_census.tsv
  nws_layer_pins.json

Output: data/nws_layer/nws_layer_metrics.json (every published number).

    python scripts/nws_layer_join.py
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

# Declared H5 mapping (mirrored — deliberately — in scripts/nws_layer_check.py:
# a threshold edit must touch both files or the gate fails).
H5_TRACKS_RHO = 0.60
H5_DIVERGENT_RHO = 0.40
H5_TRACKS_MAX_INV = 1
H5_DIVERGENT_MIN_INV = 3


def load_tsv(path):
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def rankdata(xs):
    """Average ranks (1-based), ties share the mean rank."""
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


def main() -> int:
    hw = load_tsv(os.path.join(D, "nws_headword_mass.tsv"))
    works = load_tsv(os.path.join(D, "nws_works_attestation.tsv"))
    pwg = load_tsv(os.path.join(D, "pwg_headword_ql.tsv"))
    env = load_tsv(os.path.join(D, "nws_letter_envelope.tsv"))
    census = load_tsv(os.path.join(D, "nws_x_mw_census.tsv"))
    pins = json.load(open(os.path.join(D, "nws_layer_pins.json"), encoding="utf-8"))
    registry = json.load(open(os.path.join(D, "nws_works_registry.json"),
                              encoding="utf-8"))
    prov = registry["provenance"]

    # ---- role 1: attestation-mass on shared headwords vs PW (H5) ----------
    # entry-family grouping (§8 unit of analysis): PWG homographs share k1 —
    # a headword's PW mass is the SUM over its entries, never last-wins.
    pwg_ql: dict[str, int] = {}
    for r in pwg:
        pwg_ql[r["k1"]] = pwg_ql.get(r["k1"], 0) + int(r["ql_tags"])
    nws_keys = [r["key1"] for r in hw]
    shared = [r for r in hw if r["key1"] in pwg_ql]
    outside = [r["key1"] for r in hw if r["key1"] not in pwg_ql]

    mass_total = [int(r["sigla"]) + int(r["page_refs"]) + int(r["lit_refs"])
                  for r in shared]
    mass_own = [m - int(r["x_mw_family"]) for m, r in zip(mass_total, shared)]
    ql = [pwg_ql[r["key1"]] for r in shared]

    rho_total = spearman(mass_total, ql)
    rho_own = spearman(mass_own, ql)
    rho_page = spearman([int(r["page_refs"]) for r in shared], ql)
    rho_lit = spearman([int(r["lit_refs"]) for r in shared], ql)
    rho_sig = spearman([int(r["sigla"]) for r in shared], ql)
    n = len(shared)
    t_stat = None
    if rho_total is not None and rho_total < 1:
        t_stat = round(rho_total * ((n - 2) / (1 - rho_total ** 2)) ** 0.5, 1)

    # decile profile: shared keys bucketed by PW ql rank (equal counts)
    order = sorted(range(n), key=lambda i: ql[i])
    deciles = []
    B = 10
    for b in range(B):
        lo, hi = b * n // B, (b + 1) * n // B
        seg = order[lo:hi]
        if not seg:
            continue
        deciles.append({
            "decile": b + 1,
            "pwg_ql_mean": round(sum(ql[i] for i in seg) / len(seg), 2),
            "nws_mass_mean": round(sum(mass_total[i] for i in seg) / len(seg), 3),
            "nws_mass_share_pct": round(
                100.0 * sum(mass_total[i] for i in seg) / max(1, sum(mass_total)), 2),
        })
    means = [d["nws_mass_mean"] for d in deciles]
    inversions = sum(1 for a, b in zip(means, means[1:]) if b < a)
    top_decile_mass_share = deciles[-1]["nws_mass_share_pct"]
    top_decile_ql_share = round(100.0 * sum(sorted(ql)[9 * n // B:]) / max(1, sum(ql)), 2)

    # letter-aggregate view (secondary): NWS prose mass per letter vs PWG ql
    lit_nws, lit_pw = {}, {}
    for r in hw:
        lit_nls = lit_nws.setdefault(r["letter"], [0, 0])
        lit_nls[0] += int(r["sigla"]) + int(r["page_refs"]) + int(r["lit_refs"])
        lit_nls[1] += 1
    for r in pwg:
        lit_pw.setdefault(r["k1"][:1], [0, 0])[0] += int(r["ql_tags"])
    letters = sorted(set(lit_nws) & set(lit_pw))
    rho_letters = spearman([lit_nws[l][0] for l in letters],
                           [lit_pw[l][0] for l in letters])

    # the digitized envelope + the undigitized Halle remainder (bounded, gated)
    keys_total = sum(int(r["keys_total"]) for r in env)
    keys_prose = sum(int(r["keys_prose"]) for r in env)
    treated_keys = {r["key1"] for r in hw}
    pw_treated = sum(v for k, v in pwg_ql.items() if k in treated_keys)
    pw_all = sum(pwg_ql.values())

    if rho_total is None:
        verdict = "undetermined"
    elif rho_total >= H5_TRACKS_RHO and inversions <= H5_TRACKS_MAX_INV:
        verdict = "tracks"
    elif rho_total < H5_DIVERGENT_RHO or inversions >= H5_DIVERGENT_MIN_INV:
        verdict = "divergent"
    else:
        verdict = "mixed"

    role1 = {
        "denominators": {
            "nws_prose_entries": len(hw),
            "nws_key_space": keys_total,
            "digitized_envelope_pct": round(100.0 * keys_prose / keys_total, 2),
            "page_precise_refs": sum(int(r["page_refs"]) for r in hw),
            "literature_refs": sum(int(r["lit_refs"]) for r in hw),
        },
        "shared_headwords": n,
        "containment_pct": round(100.0 * n / len(hw), 2),
        "nws_keys_outside_pwg": len(outside),
        "spearman_vs_pwg_ql": {
            "mass_total": rho_total, "mass_own_ex_mw": rho_own,
            "page_refs": rho_page, "lit_refs": rho_lit, "sigla": rho_sig,
            "t_stat": t_stat, "n": n,
        },
        "decile_profile": deciles,
        "decile_inversions": inversions,
        "concentration_top_decile_pct": {
            "nws_mass": top_decile_mass_share, "pwg_ql": top_decile_ql_share},
        "letter_aggregate_rho": rho_letters,
        "pwg_ql_on_nws_treated_keys": {
            "treated": pw_treated, "all": pw_all,
            "share_pct": round(100.0 * pw_treated / pw_all, 2)},
        "undigitized_halle_remainder": {
            "print_remainder_quantified": False,
            "gate": "H5940 (MG visa pending) — H6067 OCR route built, page "
                    "images rights-gated; not quantifiable in entries until "
                    "the gate opens",
            "digitized_envelope_note": "the dump treats 34,101 of 167,990 "
                                       "keys across ALL letters — full-alphabet, "
                                       "not letter-limited; editorial silence "
                                       "vs undigitized print is not separable "
                                       "from the dump alone",
        },
    }
    h5 = {
        "protocol_text": "NWS attestation mass on shared headwords tracks PW's "
                         "distribution; divergence — with the undigitized Halle "
                         "remainder quantified — upgrades NWS toward a delimited "
                         "witness (report §8, written before the join)",
        "operationalization": f"declared at Stage-2 execution (protocol pins the "
                              f"direction, not a number; not retuned): tracks = "
                              f"rho>={H5_TRACKS_RHO} and inversions<={H5_TRACKS_MAX_INV}; "
                              f"divergent = rho<{H5_DIVERGENT_RHO} or "
                              f"inversions>={H5_DIVERGENT_MIN_INV}; else mixed",
        "rho_total": rho_total,
        "inversions": inversions,
        "verdict": verdict,
        "upgrade_conditional": "divergence upgrades NWS toward a delimited "
                               "witness ONLY together with a quantified "
                               "undigitized remainder — the remainder is "
                               "H5940-gated and NOT quantified on this "
                               "substrate, so no upgrade is claimed here",
    }

    # ---- role 2: declared-vs-exercised (H6) --------------------------------
    declared = len(works)
    attested = sum(1 for r in works if r["attested"] == "1")
    zero = [r for r in works if r["attested"] == "0"]
    top = sorted(works, key=lambda r: -(int(r["exact"]) + int(r["fuzzy"])))[:8]
    role2 = {
        "declared_works": declared,
        "attested_works": attested,
        "attested_pct": round(100.0 * attested / declared, 2),
        "zero_citation_works": len(zero),
        "top_attested": [{"siglum": r["siglum"], "citations": int(r["exact"]) + int(r["fuzzy"])}
                         for r in top],
        "scrape": {"url": prov["url"], "fetched": prov["fetched"],
                   "html_sha256": prov["html_sha256"]},
        "method": "recomputed ONLY from the dated scrape (registry JSON with "
                  "html sha) + parsed sigla match against its 174 rows — "
                  "NEVER from filename stems",
        "retracted_figures_banned": [
            "82.7% absence (filename-stem artefact — H6050 retraction, never reused)",
            "NWS 82.7% absence figure in any role",
        ],
    }
    h6 = {
        "verdict": f"{attested}/{declared} attested "
                   f"({round(100.0 * attested / declared, 2)}%) recomputed from "
                   f"the dated scrape (fetched {prov['fetched']}, html sha "
                   f"{prov['html_sha256'][:8]}…), hash-pinned; filename-stem "
                   f"method not used",
    }

    # ---- role 3: the dependence tracer --------------------------------------
    fam_entries = [r for r in hw if int(r["x_mw_family"]) > 0]
    pure = [r for r in hw
            if int(r["x_mw_family"]) == int(r["sigla"]) and int(r["sigla"]) > 0
            and int(r["page_refs"]) == 0 and int(r["lit_refs"]) == 0]
    dict_marker_entries = sum(1 for r in hw if int(r["dict_markers"]) > 0)
    role3 = {
        "lex_mw_markers": sum(int(r["lex_mw"]) for r in hw),
        "x_mw_family_total": sum(int(r["x_mw_family"]) for r in hw),
        "x_mw_kinds": len(census),
        "top_family": [{"marker": r["marker"], "count": int(r["count"])}
                       for r in census[:6]],
        "entries_with_family_marker": len(fam_entries),
        "family_marker_entry_share_pct": round(100.0 * len(fam_entries) / len(hw), 2),
        "dict_marker_entries": dict_marker_entries,
        "pure_mw_mediated_entries": len(pure),
        "pure_mw_mediated_share_pct": round(100.0 * len(pure) / len(hw), 2),
        "note": "X(MW) = NWS internal MW-source citations; DCS's own "
                "lexicographic layer is MW-derived, so this material is "
                "MW-mediated on BOTH sides — the corpus is blind to it by "
                "construction (report §8)",
    }

    metrics = {
        "license": "CC-BY-SA-4.0",
        "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0/",
        "dataset": "nws_layer/nws_layer_metrics",
        "created": "2026-10-30",
        "generated_by": "scripts/nws_layer_join.py",
        "protocol": "report pwg-nws-pd-dcs-8294e5 §8 Stage 2 — NWS in its "
                    "three delimited roles; pre-registered, not retuned",
        "substrate": {
            "pins_echo": {k: pins[k] for k in ("nws_tar", "pwg_txt",
                                               "works_registry_scrape")},
            "rows": pins["rows"],
            "rights_nws": pins["rights_nws"],
        },
        "role1_attestation_mass": role1,
        "role2_declared_vs_exercised": role2,
        "role3_dependence_tracer": role3,
        "h5": h5,
        "h6": h6,
        "pre_registered_out": {
            "nws_dcs_inventory_join": "OUT — NWS's inventory is the Petersburg "
                                      "inventory (22 of 167,991 keys outside) and "
                                      "its citations are transferred, not "
                                      "re-attested: the join would carry no "
                                      "independent information while adding "
                                      "transfer noise (report §8)",
        },
    }
    with open(os.path.join(D, "nws_layer_metrics.json"), "w", encoding="utf-8") as out:
        json.dump(metrics, out, ensure_ascii=False, indent=2, sort_keys=True)
        out.write("\n")

    print(json.dumps({
        "shared": n, "containment_pct": role1["containment_pct"],
        "rho_total": rho_total, "rho_own": rho_own, "inversions": inversions,
        "letter_rho": rho_letters, "h5_verdict": verdict,
        "h6": h6["verdict"],
        "tracer": {k: role3[k] for k in ("lex_mw_markers", "x_mw_family_total",
                                         "pure_mw_mediated_entries")},
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
