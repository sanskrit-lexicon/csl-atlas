"""m9_xref_marker_agreement — are MW's `cf.` and PWG's `Vgl.` independent witnesses?

The xref shared-core review sheet asked a human to confirm an MW/PWG edge on the
grounds that "both dictionaries, independently, print a cross-reference from this
headword to this target — two editorial traditions made the same link". MG rejected
that justification outright (26-07-2026): **MW depends on PWG and PW.** Monier-Williams
1899 was built on Böhtlingk–Roth; a shared cross-reference is therefore not
automatically two witnesses.

This script tests the claim on the data instead of asserting it, by measuring how
often MW's `cf.` targets and PWG's `Vgl.`/`s.` targets agree for the SAME headword,
against a null in which MW's cross-reference targets are reshuffled while each
headword keeps its out-degree.

Result (26-07-2026, full `xref_edges.csv`): on the 2,750 headwords that carry a
cross-reference in both dictionaries, MW's target is also a PWG target **21.8%** of
the time, versus **0.01%** expected by chance — a ~4,300x enrichment, 0/200 null
draws at or above observed (p < 0.005). The two cross-reference systems are
emphatically **not** independent.

What that does and does not establish:

* It refutes "independent witnesses" as a reason to confirm an edge. That was the
  wrong justification and is now removed from the label vocabulary.
* It does NOT by itself prove the direction (MW copying PWG rather than both
  recording the same language facts). Direction comes from the bibliographic record —
  MW's own preface credits Böhtlingk–Roth — not from this statistic.
* It leaves MG's other judgement intact: a shared edge can still be *real and
  lexical*. That, not double attestation, is what `lexical-shared-core` now asserts.

Reads:  data/lexico/xref_edges.csv  (via m6_xref_lineage.load_edges / normalize —
        the same normalisation the shared-edge intersection uses; do not re-derive it)
Writes: data/lexico/xref_marker_agreement.json

Usage: python scripts/lexico/m9_xref_marker_agreement.py [--draws 200]
"""
import argparse
import collections
import csv
import json
import os
import random
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import m6_xref_lineage as m6  # noqa: E402  — canonical normalize()/load_edges()

ROOT = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(ROOT, "data", "lexico")
EDGES_CSV = os.path.join(DATA, "xref_edges.csv")
OUT_JSON = os.path.join(DATA, "xref_marker_agreement.json")

#: Fixed so a re-run reproduces the published figures exactly.
SEED = 20260726


def edges_by_kind(dict_code):
    """Normalized (src, tgt) edge sets for one dictionary, split by marker kind."""
    out = collections.defaultdict(set)
    with open(EDGES_CSV, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["dict"] != dict_code:
                continue
            src, tgt = m6.normalize(row["k1"]), m6.normalize(row["target"])
            if src and tgt:
                out[row["kind"]].add((src, tgt))
    return out


def by_source(edge_set):
    index = collections.defaultdict(set)
    for src, tgt in edge_set:
        index[src].add(tgt)
    return index


def null_agreement(mw_by_src, pwg_by_src, shared_sources, target_pool, draws, seed=SEED):
    """Reshuffle MW's targets, keeping each headword's out-degree, and recount
    agreement. Answers: how much of the observed overlap is just two large target
    vocabularies colliding?"""
    rng = random.Random(seed)
    pool_size = len(target_pool)
    sims = []
    for _ in range(draws):
        hit = 0
        for src in shared_sources:
            k = len(mw_by_src[src])
            picks = {target_pool[rng.randrange(pool_size)] for _ in range(k)}
            hit += len(picks & pwg_by_src[src])
        sims.append(hit)
    return sims


def build(draws=200):
    edges, _raw = m6.load_edges()
    mw_all, pwg_all = edges["mw"], edges["pwg"]
    pwg_kinds = edges_by_kind("pwg")
    vgl, s_kind = pwg_kinds["vgl"], pwg_kinds["s"]

    mw_by_src, pwg_by_src = by_source(mw_all), by_source(pwg_all)
    shared_sources = sorted(set(mw_by_src) & set(pwg_by_src))

    opportunity = sum(len(mw_by_src[s]) for s in shared_sources)
    agree = sum(len(mw_by_src[s] & pwg_by_src[s]) for s in shared_sources)

    target_pool = [tgt for _src, tgt in mw_all]
    sims = null_agreement(mw_by_src, pwg_by_src, shared_sources, target_pool, draws)
    expected = sum(sims) / len(sims)
    ge = sum(1 for x in sims if x >= agree)

    # Direction-blind containment. Reported WITH the size caveat: PWG carries ~3.4x
    # more edges than MW, so a raw containment asymmetry of about that size is what
    # set sizes alone predict and is NOT evidence of direction.
    pwg_undirected = pwg_all | {(b, a) for a, b in pwg_all}
    mw_undirected = mw_all | {(b, a) for a, b in mw_all}

    return {
        "schemaVersion": "1.0.0",
        "status": "xref-marker-agreement",
        "claim": (
            "MW `cf.` and PWG `Vgl.` cross-references are NOT independent witnesses: "
            "where both dictionaries cross-reference the same headword they agree on the "
            "target far more often than chance allows."
        ),
        "evidenceLabel": "derived-measurement",
        "ownerRepo": "csl-atlas",
        "generatedBy": "python scripts/lexico/m9_xref_marker_agreement.py",
        "sourceFiles": ["data/lexico/xref_edges.csv", "scripts/lexico/m6_xref_lineage.py"],
        "counts": {
            "mwCfEdges": len(mw_all),
            "pwgVglEdges": len(vgl),
            "pwgSEdges": len(s_kind),
            "pwgAllEdges": len(pwg_all),
            "mwHeadwordsWithXref": len(mw_by_src),
            "pwgHeadwordsWithXref": len(pwg_by_src),
            "headwordsInBoth": len(shared_sources),
            "intersectionEdges": len(mw_all & pwg_all),
        },
        "agreement": {
            "opportunityEdges": opportunity,
            "agreeingEdges": agree,
            "agreementRate": round(agree / opportunity, 6) if opportunity else None,
            "expectedByChance": round(expected, 3),
            "expectedRate": round(expected / opportunity, 8) if opportunity else None,
            "enrichment": round(agree / expected, 1) if expected else None,
            "nullDraws": draws,
            "nullDrawsAtOrAboveObserved": ge,
            "pValue": f"< {1 / draws:.3f}" if ge == 0 else round(ge / draws, 4),
            "seed": SEED,
        },
        "containment": {
            "mwEdgesFoundInPwgEitherDirection": len(mw_all & pwg_undirected),
            "mwShareFoundInPwg": round(len(mw_all & pwg_undirected) / len(mw_all), 4),
            "pwgEdgesFoundInMwEitherDirection": len(pwg_all & mw_undirected),
            "pwgShareFoundInMw": round(len(pwg_all & mw_undirected) / len(pwg_all), 4),
            "pwgToMwEdgeCountRatio": round(len(pwg_all) / len(mw_all), 2),
            "caveat": (
                "The containment asymmetry (~3.2x) is almost exactly the edge-count ratio "
                "(~3.4x), so it is what set sizes alone predict. Do NOT read it as directional "
                "evidence. The agreement enrichment above is the result that carries weight."
            ),
        },
        "interpretation": [
            "Refutes 'two dictionaries independently made the same link' as grounds for "
            "confirming a shared-core edge; that justification has been removed from the "
            "label vocabulary.",
            "Does NOT establish direction on its own. MW's dependence on Boehtlingk-Roth is a "
            "bibliographic fact (MW 1899 preface), not something this statistic shows.",
            "A shared edge can still be real and lexical — that, not double attestation, is "
            "what lexical-shared-core asserts.",
            "Normalization is a live confound throughout: MW and PWG follow different headword "
            "conventions (Patel 2016), so folding them together can both create and hide edges. "
            "See docs/XREF_SHARED_CORE_LABEL_TAXONOMY.md.",
        ],
        "limitations": [
            "Agreement is measured on normalized (accent-stripped, ring-stripped) forms; the "
            "normalisation itself can manufacture agreement.",
            "The null reshuffles MW targets from MW's own target pool, so it preserves MW's "
            "target frequency profile but not its phonological or semantic structure.",
            "Marker semantics are not identical: PWG's `Vgl.` and `s.` are distinct referring "
            "conventions and MW's `cf.` spans both; they are pooled here.",
            "No per-edge causal claim: a high overall enrichment says nothing about whether any "
            "ONE card's edge was copied.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--draws", type=int, default=200, help="null-model draws (default 200)")
    args = parser.parse_args()

    payload = build(args.draws)
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    a = payload["agreement"]
    c = payload["counts"]
    print(f"wrote {os.path.relpath(OUT_JSON, ROOT)}")
    print(f"  headwords cross-referenced in both dicts : {c['headwordsInBoth']:,}")
    print(f"  MW cf-edges on those headwords           : {a['opportunityEdges']:,}")
    print(f"  ...also a PWG target                     : {a['agreeingEdges']:,} "
          f"({100 * a['agreementRate']:.1f}%)")
    print(f"  expected by chance                       : {a['expectedByChance']} "
          f"({100 * a['expectedRate']:.3f}%)")
    print(f"  enrichment                               : {a['enrichment']}x, p {a['pValue']}")


if __name__ == "__main__":
    main()
