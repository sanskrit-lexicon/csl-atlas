#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7463 — Stage 1: the PWG↔DCS join under the pre-registered protocol.

Implements §8 of the PWG–NWS–PD–DCS methods report
(research/notes/final_report_pwg-nws-pd-dcs-8294e5.md): coverage(PWG_α) and
coverage(PWG_Ω) with mandatory strata, the per-class DCS-holdings check
(pre-reg (c)), and the G5 sensitivity battery — interpreted against the
committed convergence/divergence/contradiction grid, which was written before
this join ran and is NOT retuned here.

Inputs (all committed):
  data/pwg_dcs/pwg_work_register.tsv       (scripts/pwg_work_register.py)
  data/pwg_dcs/pwg_work_by_letter.tsv
  data/pwg_dcs/pwg_siglum_adjudications.tsv
  data/pwg_dcs/dcs_catalogue_2026-10-30.tsv (scripts/dcs_catalogue_parse.py)
  data/pd/pd_pwgbib_sigla.tsv              (PWG bibliography sigla)
  data/pd/pd_dcs_text_crosswalk.tsv        (118-text token anchor)

Outputs:
  data/pwg_dcs/pwg_dcs_works_joined.tsv    one row per register siglum
  data/pwg_dcs/pwg_dcs_coverage_by_letter.tsv
  data/pwg_dcs/pwg_dcs_join_metrics.json   every published number

    python scripts/pwg_dcs_join.py
"""
from __future__ import annotations

import csv
import json
import os
import random
import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "pwg_dcs")
PD = os.path.join(ROOT, "data", "pd")

# The committed grid thresholds (report §8, written before the join):
PD_BOOTSTRAP_BAND = (19.15, 31.52)          # A68 work-bootstrap band, %
NON_TEXT_STRATA = {"catalogue_journal", "edition_marker", "second_hand",
                   "manuscript"}            # structurally unholdable / mediated
REPORTABLE_STRATA = ["primary", "kosha_lexicon", "grammar", "edition_split",
                     "second_hand", "catalogue_journal", "edition_marker",
                     "manuscript"]
BOOTSTRAP_SEED = 20261030
BOOTSTRAP_B = 2000


def load_tsv(path):
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def norm_title(s: str) -> str:
    s = s.strip().casefold()
    s = re.sub(r"[\s\-–—]+", "", s)
    return s


def bib_leading_title(reference: str) -> str:
    """The leading caps main title of a PWG bibliography reference."""
    cut = re.split(r"[,.(\u2014]", reference, 1)[0]
    return cut.strip()


def main() -> int:
    register = load_tsv(os.path.join(D, "pwg_work_register.tsv"))
    by_letter = load_tsv(os.path.join(D, "pwg_work_by_letter.tsv"))
    adjud = {r["key"]: r for r in load_tsv(
        os.path.join(D, "pwg_siglum_adjudications.tsv"))}
    bib = {}
    for r in load_tsv(os.path.join(PD, "pd_pwgbib_sigla.tsv")):
        bib.setdefault(r["siglum"].rstrip(".").strip(), r["reference"])
    catalogue = load_tsv(os.path.join(D, "dcs_catalogue_2026-10-30.tsv"))
    dcs_titles = {r["title"]: r for r in catalogue}
    dcs_norm = {norm_title(r["title"]): r for r in catalogue}
    crosswalk = load_tsv(os.path.join(PD, "pd_dcs_text_crosswalk.tsv"))
    tok_by_title = {}
    for r in crosswalk:
        tok_by_title[norm_title(r["dcs_title"])] = int(r["dcs_tok_2026"] or 0)

    rows = []
    auto_exact = 0
    for r in register:
        key = r["base_siglum"]
        ql = int(r["ql_tags"])
        alpha_ql = int(r["alpha_ql"])
        raw = int(r["raw_tags"])
        a = adjud.get(key)
        if a:
            work, stratum, dcs_title = a["work"], a["stratum"], a["dcs_title"]
            resolution = "manual" if a["match_type"] == "manual" else "bib"
        else:
            ref = bib.get(key)
            work, stratum, dcs_title, resolution = key, "primary", "", "unresolved"
            if ref and not ref.startswith("?"):
                t = bib_leading_title(ref)
                if t:
                    work = t
                    hit = dcs_norm.get(norm_title(t))
                    if hit:
                        dcs_title = hit["title"]
                        resolution = "bib_exact"
                        auto_exact += 1
                    else:
                        resolution = "bib_no_dcs"
                # stratum patterns from the reference prose
                rl = ref.lower()
                if "verzeichnis" in rl or "zeitschrift" in rl or "journal" in rl or ref.startswith("Index"):
                    stratum = "catalogue_journal"
                elif "handschrift" in rl or "hdschr" in rl:
                    stratum = "manuscript"
                elif "nach anführungen" in rl:
                    stratum = "second_hand"
        held = bool(dcs_title) and dcs_title in dcs_titles
        genre = dcs_titles[dcs_title]["genre"] if held else ""
        tok = tok_by_title.get(norm_title(dcs_title), 0) if held else 0
        rows.append({
            "base_siglum": key, "raw_tags": raw, "ql_tags": ql,
            "alpha_ql": alpha_ql, "work": work, "stratum": stratum,
            "resolution": resolution, "dcs_title": dcs_title if held else "",
            "dcs_genre": genre, "held": "1" if held else "0",
            "dcs_tok_2026_anchor": str(tok),
        })

    with open(os.path.join(D, "pwg_dcs_works_joined.tsv"), "w", encoding="utf-8") as out:
        w = csv.DictWriter(out, fieldnames=list(rows[0].keys()), delimiter="\t")
        w.writeheader()
        w.writerows(rows)

    total_ql = sum(r["ql_tags"] for r in rows)
    total_alpha = sum(r["alpha_ql"] for r in rows)
    cov_ql = sum(r["ql_tags"] for r in rows if r["held"] == "1")
    cov_alpha = sum(r["alpha_ql"] for r in rows if r["held"] == "1")
    text_rows = [r for r in rows if r["stratum"] not in NON_TEXT_STRATA]
    text_ql = sum(r["ql_tags"] for r in text_rows)
    text_alpha = sum(r["alpha_ql"] for r in text_rows)
    text_cov_ql = sum(r["ql_tags"] for r in text_rows if r["held"] == "1")
    text_cov_alpha = sum(r["alpha_ql"] for r in text_rows if r["held"] == "1")

    def pct(x, y):
        return round(100.0 * x / y, 2) if y else None

    coverage = {
        "pooled_omega": pct(cov_ql, total_ql),
        "pooled_alpha": pct(cov_alpha, total_alpha),
        "stratum_excluded_omega": pct(text_cov_ql, text_ql),
        "stratum_excluded_alpha": pct(text_cov_alpha, text_alpha),
        "denominators": {"total_ql": total_ql, "cov_ql": cov_ql,
                         "total_alpha": total_alpha, "cov_alpha": cov_alpha,
                         "text_ql": text_ql, "text_cov_ql": text_cov_ql,
                         "text_alpha": text_alpha, "text_cov_alpha": text_cov_alpha},
    }

    # per-stratum holdings check (pre-reg (c)) — never pooled
    strata = {}
    for s in REPORTABLE_STRATA:
        srows = [r for r in rows if r["stratum"] == s]
        s_ql = sum(r["ql_tags"] for r in srows)
        s_cov = sum(r["ql_tags"] for r in srows if r["held"] == "1")
        strata[s] = {"works": len(srows), "ql": s_ql,
                     "ql_share_pct": pct(s_ql, total_ql),
                     "held_works": sum(1 for r in srows if r["held"] == "1"),
                     "coverage_pct": pct(s_cov, s_ql)}

    # work-level coverage (declared-canon analogue): held works / resolvable works
    resolvable = [r for r in rows if r["resolution"] != "unresolved"]
    work_level = {"resolved_works": len(resolvable),
                  "held_works": sum(1 for r in resolvable if r["held"] == "1"),
                  "held_share_pct": pct(
                      sum(1 for r in resolvable if r["held"] == "1"), len(resolvable)),
                  "unresolved_works": len(rows) - len(resolvable),
                  "unresolved_ql": sum(r["ql_tags"] for r in rows
                                       if r["resolution"] == "unresolved"),
                  "auto_exact_bib_hits": auto_exact}

    # G5 battery on the stratum-excluded omega coverage
    se_omega = coverage["stratum_excluded_omega"]
    loo = []
    for r in text_rows:
        num = text_cov_ql - (r["ql_tags"] if r["held"] == "1" else 0)
        den = text_ql - r["ql_tags"]
        if den > 0:
            loo.append(100.0 * num / den)
    rng = random.Random(BOOTSTRAP_SEED)
    boots = []
    wq = [(r["ql_tags"], 1 if r["held"] == "1" else 0) for r in text_rows if r["ql_tags"] > 0]
    for _ in range(BOOTSTRAP_B):
        num = den = 0
        for _ in range(len(wq)):
            q, h = wq[rng.randrange(len(wq))]
            den += q
            num += q if h else 0
        boots.append(100.0 * num / den if den else 0.0)
    boots.sort()
    battery = {
        "leave_one_out_min": round(min(loo), 2),
        "leave_one_out_max": round(max(loo), 2),
        "bootstrap_p2_5": round(boots[int(0.025 * BOOTSTRAP_B)], 2),
        "bootstrap_p97_5": round(boots[int(0.975 * BOOTSTRAP_B)], 2),
        "bootstrap_seed": BOOTSTRAP_SEED, "bootstrap_B": BOOTSTRAP_B,
        "denominator_band": {
            "pooled_751_canon": coverage["pooled_omega"],
            "stratum_excluded": se_omega},
    }

    # per-letter dispersion (H2) on the stratum-excluded basis
    key2row = {r["base_siglum"]: r for r in rows}
    letter_tbl = []
    by_lit = defaultdict(lambda: [0, 0])   # letter -> [den, num] text-strata only
    for r in by_letter:
        row = key2row.get(r["base_siglum"])
        if not row or row["stratum"] in NON_TEXT_STRATA:
            continue
        q = int(r["ql_tags"])
        by_lit[r["letter"]][0] += q
        if row["held"] == "1":
            by_lit[r["letter"]][1] += q
    for lit, (den, num) in sorted(by_lit.items(), key=lambda kv: -kv[1][0]):
        if den >= 1000:
            letter_tbl.append({"letter": lit, "ql": den,
                               "coverage_pct": pct(num, den)})
    with open(os.path.join(D, "pwg_dcs_coverage_by_letter.tsv"), "w",
              encoding="utf-8") as out:
        out.write("letter\tql\tcoverage_pct\n")
        for r in letter_tbl:
            out.write(f"{r['letter']}\t{r['ql']}\t{r['coverage_pct']}\n")
    disp = [r["coverage_pct"] for r in letter_tbl]
    pd_fascicle_span = 36.90 - 16.91     # A68 layer-1 span, pp
    h2_dispersion_exceeds_pd = (max(disp) - min(disp)) > pd_fascicle_span

    # token-weighted corroboration over the 118-text anchor (its own denominator)
    anchor_tok_total = sum(tok_by_title.values())
    anchor_tok_pwgcited = sum(
        int(r["dcs_tok_2026_anchor"]) for r in rows if r["held"] == "1")
    token_view = {
        "anchor_texts": len(tok_by_title),
        "anchor_tokens_2026": anchor_tok_total,
        "anchor_tokens_pwgcited": anchor_tok_pwgcited,
        "anchor_share_pct": pct(anchor_tok_pwgcited, anchor_tok_total),
        "note": "PWG-cited share of the 118-text anchored DCS token mass only; "
                "full-corpus token weighting needs a per-text token dump",
    }

    # committed-grid interpretation (thresholds fixed before the join)
    grid = {
        "PD_bootstrap_band": PD_BOOTSTRAP_BAND,
        "coverage_omega_stratum_excluded": se_omega,
        "coverage_alpha_stratum_excluded": coverage["stratum_excluded_alpha"],
        "A68_headline_25_2": 25.16,
        "convergence": None, "divergence_branch": None, "contradiction": None,
    }
    if se_omega is not None:
        lo, hi = PD_BOOTSTRAP_BAND
        grid["convergence"] = lo <= se_omega <= hi
        if not grid["convergence"]:
            grid["divergence_branch"] = (
                "above_band" if se_omega > hi else "below_band")
        a, o = coverage["stratum_excluded_alpha"], se_omega
        if a is not None and o is not None:
            if abs(a - o) > 5:
                grid["divergence_branch"] = (grid["divergence_branch"] or "") + \
                    "+scope_artefact(alpha!=omega)"
        grid["contradiction"] = bool(se_omega > 60)   # "three-quarters outside" fails
    grid["H2_per_letter_dispersion_exceeds_PD_fascicles"] = h2_dispersion_exceeds_pd

    metrics = {
        "license": "CC-BY-SA-4.0",
        "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0/",
        "dataset": "pwg_dcs/pwg_dcs_join_metrics",
        "created": "2026-10-30",
        "generated_by": "scripts/pwg_dcs_join.py",
        "protocol": "report pwg-nws-pd-dcs-8294e5 §8, pre-registered",
        "coverage": coverage,
        "strata": strata,
        "work_level": work_level,
        "g5_battery": battery,
        "per_letter": letter_tbl,
        "h2": {"dispersion_pp": round(max(disp) - min(disp), 2),
               "pd_fascicle_span_pp": round(pd_fascicle_span, 2),
               "exceeds": h2_dispersion_exceeds_pd},
        "token_view": token_view,
        "grid": grid,
        "register_sigla": len(rows),
    }
    with open(os.path.join(D, "pwg_dcs_join_metrics.json"), "w", encoding="utf-8") as out:
        json.dump(metrics, out, ensure_ascii=False, indent=2, sort_keys=True)
        out.write("\n")

    print(json.dumps({"coverage": coverage, "work_level": work_level,
                      "h2": metrics["h2"], "token_view_anchor": token_view["anchor_share_pct"],
                      "grid": grid}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
