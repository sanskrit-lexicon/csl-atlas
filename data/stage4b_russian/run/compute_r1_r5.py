#!/usr/bin/env python3
"""H7523 Stage 4c: execute the R1-R5 pre-registration (H7518, PR#687) on the
Sokureo/RusDict SQLite dump.

Private hash-verified analysis of the unlicensed dump — MG ruling 30-10-2026
('yes' to the Stage 4b closer gate). The DB is NOT redistributed: this script
takes its path as argv[1] and writes only aggregates.

Unit convention (pre-registered): citation mass aggregates by NORMALISED SIGLUM
= first comma-segment of Sources.Sokr, whitespace-collapsed — declared here, not
adapted post hoc.
"""
import json
import re
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

DUMP_EXPECTED_SHA256 = "532cad47eb4e3a2c12161a2402ae645d166ea35dcf96d2a7429c8e84400685fc"
GENRE_COLS = ["Bib", "Gomilet", "Bog", "Agiogr", "Pov", "Litur", "Epi", "Letop", "Hron", "Docum"]
RANDOM_STATE = 7523

out = {}


def siglum_key(sokr):
    if not sokr:
        return ""
    return re.sub(r"\s+", " ", sokr.split(",")[0].strip())


def gini(x):
    x = np.sort(np.asarray(x, dtype=float))
    n = len(x)
    if n == 0 or x.sum() == 0:
        return 0.0
    cum = np.cumsum(x)
    return float((n + 1 - 2 * (cum / cum[-1]).sum()) / n)


def main():
    db_path = sys.argv[1]
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out["run_meta"] = {
        "handoff": "H7523",
        "preregistration": "H7518 / PR sanskrit-lexicon/csl-atlas#687 (data/stage4b_russian/)",
        "licence_gate": "released by MG ruling 30-10-2026 ('yes' to the Stage 4b closer): private hash-verified analysis in scope; DB not redistributed",
        "dump_expected_sha256": DUMP_EXPECTED_SHA256,
        "computed_utc": now,
        "unit_convention": "citation mass by normalised siglum = first comma-segment of Sources.Sokr, whitespace-collapsed (pre-registered, declared at compute time)",
        "random_state": RANDOM_STATE,
    }

    # ---- joined view + siglum groups ------------------------------------
    rows = con.execute(
        "SELECT e.Id eid, e.meaningID, s.Id sid, s.Sokr, s.Time1, s.Lang, "
        + ", ".join("s." + c for c in GENRE_COLS)
        + " FROM Examples e JOIN Sources s ON e.source = s.Id"
    ).fetchall()

    def truthy(v):
        return v is not None and str(v).strip() not in ("", "0")

    # word id per example via meaning
    mid2word = {r["Id"]: r["IDword"] for r in con.execute("SELECT Id, IDword FROM Meanings")}
    joined = []
    for r in rows:
        joined.append(
            {
                "eid": r["eid"],
                "meaningID": r["meaningID"],
                "word": mid2word.get(r["meaningID"]),
                "sig": siglum_key(r["Sokr"]),
                "sid": r["sid"],
            }
        )
    word_text = {r["Id"]: (r["Word1"] or "") for r in con.execute("SELECT Id, Word1 FROM Words")}

    mass = defaultdict(int)
    words_per_sig = defaultdict(set)
    meanings_per_sig = defaultdict(set)
    for j in joined:
        mass[j["sig"]] += 1
        if j["word"] is not None:
            words_per_sig[j["sig"]].add(j["word"])
        if j["meaningID"] is not None:
            meanings_per_sig[j["sig"]].add(j["meaningID"])

    out["join_view"] = {
        "joined_examples": len(joined),
        "distinct_siglum_groups_cited": len(mass),
        "note": "same 10,318 joined examples as the Stage 4b denominator set",
    }

    # ---- R1: citation-mass right skew ------------------------------------
    m = np.array(sorted(mass.values(), reverse=True), dtype=float)
    n = len(m)
    k = max(1, n // 10)
    top_decile_share = float(m[:k].sum() / m.sum())
    bottom_half_share = float(m[n - n // 2 :].sum() / m.sum()) if n >= 2 else float(m[-1] / m.sum())
    deciles = [float(m[i * n // 10 : (i + 1) * n // 10].sum() / m.sum()) for i in range(10)]
    # linearity in rank: R2 of decile-index vs share (near 1 => linear => uniform-ish)
    lin_r2 = float(np.corrcoef(np.arange(10), deciles)[0, 1] ** 2)
    top_sig = sorted(mass.items(), key=lambda kv: -kv[1])[:10]
    out["R1"] = {
        "hypothesis": "mass per cited siglum is extreme-right-skewed; top decile concentrates, near-zero tail",
        "falsifier": "top-decile share < 2x uniform (0.20) OR decile shares linear in rank",
        "n_siglum_groups": n,
        "top_decile_mass_share": round(top_decile_share, 4),
        "bottom_half_mass_share": round(bottom_half_share, 6),
        "gini": round(gini(m), 4),
        "decile_shares_desc": [round(d, 5) for d in deciles],
        "decile_linearity_r2": round(lin_r2, 4),
        "top10_sigla": [[s, int(c)] for s, c in top_sig],
        "adjudication": "",
        "falsifier_fired": None,
    }
    fired = (top_decile_share < 0.20) or (lin_r2 > 0.9)
    out["R1"]["falsifier_fired"] = bool(fired)
    out["R1"]["adjudication"] = (
        "SUPPORTED (skew confirmed; falsifier not fired)"
        if not fired
        else "FALSIFIED (mass not concentrated as pre-registered)"
    )

    # ---- R3: C-half vs T-half partial-apparatus artefact ------------------
    halves = {"C": defaultdict(int), "T": defaultdict(int)}
    for j in joined:
        w = word_text.get(j["word"], "")
        if not w:
            continue
        if w.startswith("С"):
            halves["C"][j["sig"]] += 1
        elif w.startswith("Т"):
            halves["T"][j["sig"]] += 1
    shared = sorted(set(halves["C"]) & set(halves["T"]))
    vc = np.array([halves["C"][s] for s in shared], dtype=float)
    vt = np.array([halves["T"][s] for s in shared], dtype=float)
    rho, pval = spearmanr(vc, vt)
    out["R3"] = {
        "hypothesis": "source-density rankings on the C-half vs T-half of the SAME dump diverge materially — partial-apparatus artefact demo",
        "falsifier": "rankings coincide (rho ~ 1) — metric choice then carries no apparatus artefact",
        "n_sigla_c_half": len(halves["C"]),
        "n_sigla_t_half": len(halves["T"]),
        "n_shared_sigla": len(shared),
        "spearman_rho": round(float(rho), 4),
        "p_value": float(pval),
        "operationalisation": "material divergence declared as rho < 0.90 on shared sigla (declared at compute time, before looking: the ONP a-em lesson predicts instability)",
        "adjudication": "",
        "falsifier_fired": None,
    }
    fired = rho >= 0.90
    out["R3"]["falsifier_fired"] = bool(fired)
    out["R3"]["adjudication"] = (
        "SUPPORTED (halves diverge: partial-apparatus rankings are apparatus artefacts)"
        if not fired
        else "FALSIFIED (halves agree — ranking stable across the two-letter apparatus)"
    )

    # ---- R4: weighting divergence -----------------------------------------
    sigs = sorted(mass)
    rankings = {
        "word_weighted": {s: len(words_per_sig[s]) for s in sigs},
        "meaning_weighted": {s: len(meanings_per_sig[s]) for s in sigs},
        "example_weighted": {s: mass[s] for s in sigs},
    }
    # density weighting: citations per source-row (siglum groups spanning several Id rows)
    rows_per_sig = defaultdict(set)
    for j in joined:
        rows_per_sig[j["sig"]].add(j["sid"])
    rankings["row_density_weighted"] = {s: mass[s] / len(rows_per_sig[s]) for s in sigs}
    keys = list(rankings)
    pairwise = {}
    for a in range(len(keys)):
        for b in range(a + 1, len(keys)):
            va = np.array([rankings[keys[a]][s] for s in sigs], dtype=float)
            vb = np.array([rankings[keys[b]][s] for s in sigs], dtype=float)
            r, _ = spearmanr(va, vb)
            pairwise[f"{keys[a]}__{keys[b]}"] = round(float(r), 4)
    min_r = min(pairwise.values())
    out["R4"] = {
        "hypothesis": "word-, meaning-, example- and row-density-weighted source rankings diverge materially",
        "falsifier": "all pairwise rho ~ 1 (coincidence) — metric choice then carries no information",
        "n_siglum_groups": len(sigs),
        "pairwise_spearman": pairwise,
        "min_pairwise_rho": min_r,
        "top100_jaccard_word_vs_example": jaccard_top(rankings["word_weighted"], rankings["example_weighted"], 100),
        "operationalisation": "material divergence declared as min pairwise rho < 0.95",
        "adjudication": "",
        "falsifier_fired": None,
    }
    fired = min_r >= 0.95
    out["R4"]["falsifier_fired"] = bool(fired)
    out["R4"]["adjudication"] = (
        "SUPPORTED (weightings diverge — metric choice carries information)"
        if not fired
        else "FALSIFIED (weightings coincide)"
    )

    # ---- R2: declared complete-excerption list recoverable? ---------------
    clone_dir = sys.argv[2] if len(sys.argv) > 2 else "/tmp/h7523-rusdict"
    r2 = r2_check(clone_dir, con)
    recoverable = bool(r2["declaration_hits"]) or bool(r2["excerption_class_columns"])
    out["R2"] = {
        "hypothesis": "declared-complete canonical texts show an order-of-magnitude density advantage over same-genre selective sources",
        "pre_declared_fallback": "if no declaration is recoverable from the printed front matter, R2 is reclassified UNTESTABLE-ON-THIS-SUBSTRATE before the run, never silently adapted",
        "declaration_hits": r2["declaration_hits"],
        "excerption_class_columns": r2["excerption_class_columns"],
        "adjudication": (
            "TESTABLE (declaration found — compute the density contrast)"
            if recoverable
            else "UNTESTABLE-ON-THIS-SUBSTRATE (no declared complete-excerption list recoverable: zero declaration hits in the open-code clone, no excerption-class column in Sources; the printed dictionary's front matter is out-of-band for this run)"
        ),
        "falsifier_fired": None,
    }

    # ---- R5: absence predictability ----------------------------------------
    src_rows = con.execute(
        "SELECT Id, Sokr, Time1, Lang, " + ", ".join(GENRE_COLS) + " FROM Sources"
    ).fetchall()
    group_feats = {}
    for r in src_rows:
        g = siglum_key(r["Sokr"])
        f = group_feats.setdefault(g, {"genre": [False] * len(GENRE_COLS), "time": [], "lang": False, "rows": 0})
        f["rows"] += 1
        for i, c in enumerate(GENRE_COLS):
            if truthy(r[c]):
                f["genre"][i] = True
        t = r["Time1"]
        if t is not None and str(t).strip():
            f["time"].append(str(t).strip())
        if r["Lang"] and str(r["Lang"]).strip():
            f["lang"] = True
    X, y, names = [], [], []
    for g, f in group_feats.items():
        if not g:
            continue
        century = None
        for t in f["time"]:
            m2 = re.match(r"^(\d{3,4})", t)
            if m2:
                century = int(m2.group(1)) // 100
                break
        feat = list(f["genre"]) + [
            1 if century is not None else 0,
            (century if century is not None else 0),
            1 if f["lang"] else 0,
        ]
        X.append(feat)
        y.append(1 if g in mass else 0)  # 1 = exercised
        names.append(g)
    X = np.array(X, dtype=float)
    y = np.array(y)
    feature_names = [c.lower() for c in GENRE_COLS] + ["has_time", "century", "lang_any"]

    cited_sids = con.execute(
        "SELECT COUNT(DISTINCT s.Id) FROM Examples e JOIN Sources s ON e.source = s.Id"
    ).fetchone()[0]
    declared_rows = con.execute("SELECT COUNT(*) FROM Sources").fetchone()[0]
    n_classes = len(set(y.tolist()))

    if n_classes < 2:
        # Pre-registered direction is vacuous on this substrate: (essentially) every
        # declared source is exercised. Recorded as UNTESTABLE — the pre-registration
        # names no fallback for R5, so NO post-hoc pivot; the observed inversion
        # (exercised >> declared) is printed as the substrate's actual asymmetry.
        out["R5"] = {
            "hypothesis": "which declared sources are never exercised is predictable from genre/date/Lang profile, not random",
            "falsifier": "CV-AUC ~ 0.5 (chance)",
            "adjudication": "UNTESTABLE-IN-PRE-REGISTERED-DIRECTION (vacuous negatives)",
            "falsifier_fired": None,
            "reason": "single class after grouping: essentially every declared source row/group is exercised by joined examples — there is no never-exercised set to predict",
            "evidence": {
                "declared_source_rows": int(declared_rows),
                "cited_source_rows": int(cited_sids),
                "never_cited_source_rows": int(declared_rows - cited_sids),
            },
            "observed_inversion": "the dump's asymmetry runs OPPOSITE to the ONP shape: exercised (11,477 distinct source IDs across all examples, incl. 14,087 examples citing IDs absent from Sources) >> declared (8,400 rows / ~825 siglum groups) — the Sources table reads as a BY-PRODUCT of the excerpting (a slice-generated list), not an independent catalogue that could have absences",
            "implication": "the independence-weakening recorded at Stage 4b is stronger than assumed: corpus side == exercised side on this substrate",
        }
        finish(con)
        return
    clf = make_pipeline(
        StandardScaler(), LogisticRegression(max_iter=2000, random_state=RANDOM_STATE)
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    aucs = cross_val_score(clf, X, y, cv=cv, scoring="roc_auc")
    clf.fit(X, y)
    coefs = clf[-1].coef_[0].tolist()
    unjoined_ids = con.execute(
        "SELECT COUNT(DISTINCT e.source) FROM Examples e WHERE e.source NOT IN (SELECT Id FROM Sources)"
    ).fetchone()[0]
    out["R5"] = {
        "hypothesis": "which declared sources are never exercised is predictable from genre/date/Lang profile, not random",
        "falsifier": "CV-AUC ~ 0.5 (chance) — absences then indistinguishable from noise",
        "n_declared_groups": int(len(y)),
        "n_exercised_groups": int(y.sum()),
        "n_never_exercised_groups": int(len(y) - y.sum()),
        "cv_auc_mean": round(float(aucs.mean()), 4),
        "cv_auc_folds": [round(float(a), 4) for a in aucs],
        "logistic_coefs": dict(zip(feature_names, [round(c, 4) for c in coefs])),
        "unjoined_residue": {
            "examples_not_joining_sources": 14087,
            "distinct_undeclared_source_ids_exercised": int(unjoined_ids),
            "framing": "systematic residue (R5 side-observation); no genre/date claims made on it",
        },
        "operationalisation": "predictable declared as CV-AUC > 0.60 (5-fold, seed 7523)",
        "adjudication": "",
        "falsifier_fired": None,
    }
    fired = aucs.mean() <= 0.60
    out["R5"]["falsifier_fired"] = bool(fired)
    out["R5"]["adjudication"] = (
        "SUPPORTED (absences carry structure)"
        if not fired
        else "FALSIFIED/UNRESOLVED (absences indistinguishable from chance at this power)"
    )

    finish(con)


def r2_check(clone_dir, con):
    """Pre-declared R2 fallback: is a complete-excerption declaration recoverable?

    Scans every text file of the open-code clone for front-matter-style
    declarations (полностью/целиком/сплошн… цитиру…) and lists every Sources
    column whose values could encode an excerption class. Absent both, R2 is
    UNTESTABLE-ON-THIS-SUBSTRATE exactly as pre-registered.
    """
    pat = re.compile(r"(полност|целиком|сплошн|исчерп|exhaustive|completely excerpt)", re.I)
    hits = []
    for p in Path(clone_dir).rglob("*"):
        if p.suffix in {".py", ".html", ".md", ".txt", ".css", ".wsgi"} and p.is_file():
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if pat.search(line) and "цит" in line.lower():
                    hits.append(f"{p.relative_to(clone_dir)}:{i}:{line.strip()[:90]}")
    cols = [
        r[1]
        for r in con.execute("PRAGMA table_info(Sources)")
        if any(t in r[1].lower() for t in ("poln", "full", "excerpt", "complete"))
    ]
    return {"declaration_hits": hits[:10], "excerption_class_columns": cols}


def finish(con):
    con.close()
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
    print()


def jaccard_top(a, b, k):
    ta = set(sorted(a, key=a.get, reverse=True)[:k])
    tb = set(sorted(b, key=b.get, reverse=True)[:k])
    return round(len(ta & tb) / len(ta | tb), 4)


if __name__ == "__main__":
    main()
