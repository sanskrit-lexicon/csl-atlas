#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7297 — policy-matched PD/PWG density: simplex, derivative, compound.

The raw H6949/H7095 ledgers answer "how much denser is PD than PWG on the same
lemma" (8.55x attestations, 9.53x quotations, median 4.0x over 4,093 shared
lemmas).  They do *not* answer whether that multiple survives PD's own
lemmatisation policy: PD gives a headword to nearly every compound, so a
per-lemma comparison can be an artefact of which lemmas both dictionaries
happen to share.

This builder changes the *comparison policy* only.  It re-uses the frozen
H6949 quotation/attestation counts and the frozen H7110 entry-family rule
(``scripts/lib/pd_family_rule.py``; one member => simplex, last member in the
suffix set => derivative, else compound) and writes:

  * ``data/pd/pd_policy_matched_class.tsv``   — the frozen per-headword class
  * ``data/pd/pd_policy_matched_density.tsv`` — per-stratum ratios + pooled rows
  * ``data/pd/pd_policy_matched_inventory.tsv`` — PD-only inventory policy
  * ``data/pd/pd_policy_matched_density.json`` — envelope, canaries, method
  * ``reports/PD_POLICY_MATCHED_DENSITY_2026.md``

Usage (the source text is external and read-only):

    python scripts/pd_policy_matched_density.py --build --pd /path/to/pd.txt
    python scripts/pd_policy_matched_density.py --check        # no pd.txt needed

``--build`` classifies the headwords from PDScan 2020 when ``--pd`` is given (or
when the class ledger is missing); otherwise it re-uses the committed class
ledger.  ``--check`` never reads the 55 MB source: it re-derives every table,
the standardised pooled result and all canaries from the committed inputs and
fails with ``STOP_CANARY_MISMATCH`` (exit 2) on any drift.

Raw ledgers are read, never rewritten.  Stdlib only; no network.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import statistics
import sys
from collections import Counter, OrderedDict

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "scripts", "lib"))
from dataset_meta import license_fields  # noqa: E402
import pd_family_rule as family_rule  # noqa: E402

DATA = os.path.join(ROOT, "data", "pd")
DECOMP = os.path.join(DATA, "pd_attestation_decomposition.tsv")
VS = os.path.join(DATA, "pd_quotations_vs_pwg.tsv")
ENTRIES = os.path.join(DATA, "pd_quotations_by_entry.tsv")
CLASS_TSV = os.path.join(DATA, "pd_policy_matched_class.tsv")
OUT_TSV = os.path.join(DATA, "pd_policy_matched_density.tsv")
OUT_INV = os.path.join(DATA, "pd_policy_matched_inventory.tsv")
OUT_JSON = os.path.join(DATA, "pd_policy_matched_density.json")
REPORT = os.path.join(ROOT, "reports", "PD_POLICY_MATCHED_DENSITY_2026.md")

FAMILIES = ("simplex", "derivative", "compound")
STRATA = FAMILIES + ("unclassified",)
THIN_ATTESTATIONS = 1          # inventory-policy definition of a thin entry
BOOTSTRAP_REPS = 2000
BOOTSTRAP_SEED = 7297

# Frozen H6949/H7095 values.  --check refuses to publish a table that moves them.
PINS = OrderedDict(
    (
        ("shared_lemmas", 4093),
        ("pd_attestations", 157480),
        ("pwg_attestations", 18423),
        ("pd_quotations", 97413),
        ("pwg_quotations", 10225),
        ("below_parity_lemmas", 340),
        ("median_attestation_ratio", 4.0),
        ("raw_attestation_ratio", 8.5480),
        ("raw_quotation_ratio", 9.5269),
        ("pd_unique_key1", 104959),
        ("pd_entries", 107630),
        ("class_entries", 107620),
        ("class_universe", 104950),
        ("class_population", 103127),
        ("class_classified", 102747),
        ("class_correction_blocks", 380),
        ("pwg_span_frontier_lines", 4519),
        ("pwg_total_key1", 106082),
        ("pd_letter_a_attestations", 419890),
        ("inventory_contrast", 23.2),
    )
)

BANNED = ("twelvefold per headword", "per-headword twelvefold")

DENSITY_COLUMNS = [
    "row_kind", "stratum", "weight", "lemmas", "lemmas_with_pwg_attestation",
    "pd_attestations", "pwg_attestations", "attestation_ratio",
    "attestation_ratio_lo", "attestation_ratio_hi",
    "pd_quotations", "pwg_quotations", "quotation_ratio",
    "median_attestation_ratio", "below_parity_lemmas", "below_parity_pct",
]
INV_COLUMNS = [
    "row_kind", "scope", "family", "headwords", "headwords_zero_attestation",
    "headwords_at_most_one", "share_of_scope_pct", "median_attestations",
    "mean_attestations", "attestation_mass", "note",
]


# --------------------------------------------------------------------- helpers
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_tsv(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def f4(x):
    return float(round(x, 4))


def f2(x):
    return float(round(x, 2))


def dump_tsv(columns, rows):
    out = ["\t".join(columns)]
    for r in rows:
        out.append("\t".join("" if r.get(c) is None else str(r.get(c)) for c in columns))
    return "\n".join(out) + "\n"


def percentile(sorted_vals, q):
    """Nearest-rank percentile on a sorted list (deterministic, no numpy)."""
    if not sorted_vals:
        return None
    idx = int(round(q * (len(sorted_vals) - 1)))
    return sorted_vals[idx]


# ------------------------------------------------------------ class ledger
def build_class(pd_path):
    """Classify every PD headword with the frozen H7110 rule."""
    digest = sha256(pd_path)
    if family_rule.RE_SHA.match(family_rule.PD_SHA256) and digest != family_rule.PD_SHA256:
        raise SystemExit("STOP_CANARY_MISMATCH: pd.txt sha256 %s != pinned %s"
                         % (digest, family_rule.PD_SHA256))
    headwords, entries, unique_k1, corrections = family_rule.parse_pd(pd_path)
    checks = {
        "class_universe": len(unique_k1),
        "class_population": len(headwords) + len(corrections),
        "class_classified": len(headwords),
        "class_correction_blocks": len(corrections),
        "class_entries": len(entries),
    }
    for key, got in checks.items():
        if got != PINS[key]:
            raise SystemExit("STOP_CANARY_MISMATCH: %s = %d, pinned %d"
                             % (key, got, PINS[key]))
    # The analysis is kept only for the frozen shared lemmas: it is the provenance
    # a verifier needs for the published strata, while the PD-only rows need the
    # class alone (the inventory table reports aggregates).  --build with the
    # pinned source regenerates any of them.
    shared = {r["k1"] for r in read_tsv(DECOMP)}
    rows = []
    for k1 in sorted(unique_k1):
        analysis = headwords.get(k1)
        rows.append(OrderedDict(
            k1=k1,
            family=(family_rule.classify(analysis) if analysis else None) or "unclassified",
            analysis=(analysis or "") if k1 in shared else "",
        ))
    return OrderedDict(rows=rows, pd_sha256=digest, **checks)


def load_class():
    rows = read_tsv(CLASS_TSV)
    return {r["k1"]: r["family"] for r in rows}


# ---------------------------------------------------------------- population
def load_population():
    """The frozen 4,093 shared lemmas, one row per k1 (H7095 counts)."""
    decomp = read_tsv(DECOMP)
    vs = {r["k1"]: r for r in read_tsv(VS)}
    rows = []
    for r in decomp:
        k1 = r["k1"]
        rows.append(OrderedDict(
            k1=k1,
            pd_quotations=int(r["pd_quotations"]),
            pwg_quotations=int(r["pwg_quotations"]),
            pd_att=int(r["pd_attestations"]),
            pwg_att=int(r["pwg_attestations"]),
            pd_entries=int(vs[k1]["pd_entries"]),
            pwg_entries=int(vs[k1]["pwg_entries"]),
        ))
    rows.sort(key=lambda r: r["k1"])
    verify_population(rows)
    return rows


def score(rows):
    a = sum(r["pd_att"] for r in rows)
    b = sum(r["pwg_att"] for r in rows)
    qa = sum(r["pd_quotations"] for r in rows)
    qb = sum(r["pwg_quotations"] for r in rows)
    med = None
    ratios = [r["pd_att"] / r["pwg_att"] for r in rows if r["pwg_att"] > 0]
    if ratios:
        med = f2(statistics.median(ratios))
    return OrderedDict(
        lemmas=len(rows),
        lemmas_with_pwg_attestation=len(ratios),
        pd_attestations=a,
        pwg_attestations=b,
        attestation_ratio=f4(a / b) if b else None,
        pd_quotations=qa,
        pwg_quotations=qb,
        quotation_ratio=f4(qa / qb) if qb else None,
        median_attestation_ratio=med,
        below_parity_lemmas=sum(1 for r in rows if r["pd_att"] < r["pwg_att"]),
    )


def verify_population(rows):
    got = score(rows)
    expect = {
        "shared_lemmas": got["lemmas"],
        "pd_attestations": got["pd_attestations"],
        "pwg_attestations": got["pwg_attestations"],
        "pd_quotations": got["pd_quotations"],
        "pwg_quotations": got["pwg_quotations"],
        "below_parity_lemmas": got["below_parity_lemmas"],
        "median_attestation_ratio": got["median_attestation_ratio"],
        "raw_attestation_ratio": got["attestation_ratio"],
        "raw_quotation_ratio": got["quotation_ratio"],
    }
    for key, value in expect.items():
        if value != PINS[key]:
            raise SystemExit("STOP_CANARY_MISMATCH: %s = %s, pinned %s"
                             % (key, value, PINS[key]))
    for r in rows:
        if r["pd_entries"] < 1 or r["pwg_entries"] < 1:
            raise SystemExit("STOP_CANARY_MISMATCH: %s has no entry on one side" % r["k1"])


def by_stratum(rows, classes):
    groups = OrderedDict((s, []) for s in STRATA)
    for r in rows:
        groups[classes.get(r["k1"], "unclassified")].append(r)
    return groups


# ---------------------------------------------------------------- bootstrap
def bootstrap(groups, reps=BOOTSTRAP_REPS, seed=BOOTSTRAP_SEED):
    """Stratified lemma bootstrap (resample lemmas inside each stratum)."""
    rng = random.Random(seed)
    raw_ci, std_ci, ratio_ci = [], [], {s: [] for s in FAMILIES}
    fix = {s: list(groups[s]) for s in STRATA}
    for _ in range(reps):
        stats = {}
        for s in STRATA:
            src = fix[s]
            n = len(src)
            if n == 0:
                stats[s] = None
                continue
            a = b = 0
            for _i in range(n):
                r = src[rng.randrange(n)]
                a += r["pd_att"]
                b += r["pwg_att"]
            stats[s] = (a, b)
        all_a = sum(v[0] for v in stats.values() if v)
        all_b = sum(v[1] for v in stats.values() if v)
        if all_b:
            raw_ci.append(all_a / all_b)
        vals = []
        for s in FAMILIES:
            a, b = stats[s]
            if b:
                ratio_ci[s].append(a / b)
                vals.append(a / b)
        if len(vals) == len(FAMILIES):
            std_ci.append(sum(vals) / len(vals))
    out = OrderedDict(
        reps=reps,
        seed=seed,
        method="stratified lemma bootstrap, ratio of sums per stratum, "
               "percentile interval (nearest rank)",
        raw_attestation_ratio=[f4(percentile(sorted(raw_ci), 0.025)),
                               f4(percentile(sorted(raw_ci), 0.975))],
        standardised_ratio=[f4(percentile(sorted(std_ci), 0.025)),
                            f4(percentile(sorted(std_ci), 0.975))],
    )
    for s in FAMILIES:
        out[s] = [f4(percentile(sorted(ratio_ci[s]), 0.025)),
                  f4(percentile(sorted(ratio_ci[s]), 0.975))]
    return out


# ----------------------------------------------------------------- inventory
def inventory(classes, rows):
    """PD-only headwords: the inventory-policy result, never a citation ratio."""
    ent = read_tsv(ENTRIES)
    mass = Counter()
    for r in ent:
        mass[r["k1"]] += int(r["attestations"])
    if len(ent) != PINS["pd_entries"] or len(mass) != PINS["pd_unique_key1"]:
        raise SystemExit("STOP_CANARY_MISMATCH: entries TSV %d rows / %d keys"
                         % (len(ent), len(mass)))
    shared = {r["k1"] for r in rows}
    if sum(mass.values()) != PINS["pd_letter_a_attestations"]:
        raise SystemExit("STOP_CANARY_MISMATCH: attestation mass %d"
                         % sum(mass.values()))
    universe = sorted(mass)
    pd_only = [k for k in universe if k not in shared]
    if len(pd_only) != PINS["pd_unique_key1"] - PINS["shared_lemmas"]:
        raise SystemExit("STOP_CANARY_MISMATCH: PD-only count %d" % len(pd_only))

    def block(keys, scope):
        out = []
        for fam in STRATA:
            ks = [k for k in keys if classes.get(k, "unclassified") == fam]
            if not ks:
                continue
            vals = [mass[k] for k in ks]
            out.append(OrderedDict(
                scope=scope, family=fam, headwords=len(ks),
                headwords_zero_attestation=sum(1 for v in vals if v == 0),
                headwords_at_most_one=sum(1 for v in vals if v <= THIN_ATTESTATIONS),
                median_attestations=f2(statistics.median(vals)),
                mean_attestations=f2(sum(vals) / len(vals)),
                attestation_mass=sum(vals),
                share_of_scope_pct=f2(100.0 * len(ks) / len(keys)),
            ))
        vals = [mass[k] for k in keys]
        out.append(OrderedDict(
            scope=scope, family="all", headwords=len(keys),
            headwords_zero_attestation=sum(1 for v in vals if v == 0),
            headwords_at_most_one=sum(1 for v in vals if v <= THIN_ATTESTATIONS),
            median_attestations=f2(statistics.median(vals)),
            mean_attestations=f2(sum(vals) / len(vals)),
            attestation_mass=sum(vals),
            share_of_scope_pct=100.0,
        ))
        return out

    rows = block(pd_only, "pd_only") + block(sorted(shared), "shared")
    contrast = inventory_contrast()
    rows.append(OrderedDict(
        scope="pd_vs_pwg_span", family="all",
        headwords=contrast["pd_lemmas"], headwords_zero_attestation=None,
        headwords_at_most_one=None, share_of_scope_pct=None,
        median_attestations=None, mean_attestations=None, attestation_mass=None,
    ))
    return OrderedDict(rows=rows, contrast=contrast, pd_only=len(pd_only),
                       shared=len(shared), threshold=THIN_ATTESTATIONS)


def inventory_contrast():
    """The 23.2x headword-inventory contrast, recomputed from the frozen pins.

    H7110 defines it as PD's unique-key1 list (104,959) against PWG's Sanskrit-
    collated lines to the *apaca* frontier (4,519).  The committed headword
    lists are used when the sibling checkout is present, and the pins are the
    fallback, so ``--check`` needs no external repository.
    """
    detail = family_rule.density(0, 0) or {}
    pd_lemmas = detail.get("pd_lemmas", PINS["pd_unique_key1"])
    pwg_in_span = detail.get("pwg_in_span", PINS["pwg_span_frontier_lines"])
    if pd_lemmas != PINS["pd_unique_key1"]:
        raise SystemExit("STOP_CANARY_MISMATCH: PD key1 list %d" % pd_lemmas)
    if pwg_in_span != PINS["pwg_span_frontier_lines"]:
        raise SystemExit("STOP_CANARY_MISMATCH: PWG frontier line %d" % pwg_in_span)
    detail = OrderedDict(
        pd_lemmas=pd_lemmas,
        pwg_in_span=pwg_in_span,
        pwg_total=PINS["pwg_total_key1"],
        span_frontier="apaca",
    )
    multiple = round(pd_lemmas / pwg_in_span, 1)
    if multiple != PINS["inventory_contrast"]:
        raise SystemExit("STOP_CANARY_MISMATCH: inventory contrast %.1f" % multiple)
    return OrderedDict(detail, multiple=multiple)


# ------------------------------------------------------------------- render
def build(population, strata, boot, inv, classes, pd_sha):
    totals = score(population)
    rows = []
    for s in STRATA:
        sc = score(strata[s])
        ci = boot[s] if s in FAMILIES else [None, None]
        rows.append(OrderedDict(
            row_kind="stratum", stratum=s,
            weight=f4(1.0 / len(FAMILIES)) if s in FAMILIES else None,
            lemmas=sc["lemmas"],
            lemmas_with_pwg_attestation=sc["lemmas_with_pwg_attestation"],
            pd_attestations=sc["pd_attestations"],
            pwg_attestations=sc["pwg_attestations"],
            attestation_ratio=sc["attestation_ratio"],
            attestation_ratio_lo=ci[0], attestation_ratio_hi=ci[1],
            pd_quotations=sc["pd_quotations"],
            pwg_quotations=sc["pwg_quotations"],
            quotation_ratio=sc["quotation_ratio"],
            median_attestation_ratio=sc["median_attestation_ratio"],
            below_parity_lemmas=sc["below_parity_lemmas"],
            below_parity_pct=f2(100.0 * sc["below_parity_lemmas"] / sc["lemmas"]),
        ))
    ratios = {s: score(strata[s])["attestation_ratio"] for s in FAMILIES}
    std = f4(sum(ratios.values()) / len(FAMILIES))
    n_all = sum(score(strata[s])["lemmas"] for s in FAMILIES)
    pd_mix = f4(sum(score(strata[s])["lemmas"] / n_all * ratios[s] for s in FAMILIES))
    rows.append(OrderedDict(
        row_kind="pooled", stratum="pooled_standardised_equal_weight", weight=1.0,
        lemmas=totals["lemmas"], lemmas_with_pwg_attestation=totals["lemmas_with_pwg_attestation"],
        pd_attestations=totals["pd_attestations"], pwg_attestations=totals["pwg_attestations"],
        attestation_ratio=std,
        attestation_ratio_lo=boot["standardised_ratio"][0],
        attestation_ratio_hi=boot["standardised_ratio"][1],
        pd_quotations=totals["pd_quotations"], pwg_quotations=totals["pwg_quotations"],
        quotation_ratio=None, median_attestation_ratio=None,
        below_parity_lemmas=totals["below_parity_lemmas"],
        below_parity_pct=f2(100.0 * totals["below_parity_lemmas"] / totals["lemmas"]),
    ))
    rows.append(OrderedDict(
        row_kind="pooled", stratum="pooled_raw_ratio_of_sums", weight=None,
        lemmas=totals["lemmas"], lemmas_with_pwg_attestation=totals["lemmas_with_pwg_attestation"],
        pd_attestations=totals["pd_attestations"], pwg_attestations=totals["pwg_attestations"],
        attestation_ratio=totals["attestation_ratio"],
        attestation_ratio_lo=boot["raw_attestation_ratio"][0],
        attestation_ratio_hi=boot["raw_attestation_ratio"][1],
        pd_quotations=totals["pd_quotations"], pwg_quotations=totals["pwg_quotations"],
        quotation_ratio=totals["quotation_ratio"],
        median_attestation_ratio=totals["median_attestation_ratio"],
        below_parity_lemmas=totals["below_parity_lemmas"],
        below_parity_pct=f2(100.0 * totals["below_parity_lemmas"] / totals["lemmas"]),
    ))

    below = sorted(r["k1"] for r in population if r["pd_att"] < r["pwg_att"])
    akam = next(r for r in population if r["k1"] == "akAmatas")
    payload = OrderedDict(
        handoff="H7297",
        builder="scripts/pd_policy_matched_density.py",
        question="Does PD's 8.55x attestation multiple survive a policy-matched "
                 "(simplex / derivative / compound) comparison?",
        homograph_policy=OrderedDict(
            rule="one row per identical k1 string on both sides; every homograph "
                 "entry of that k1 is summed on each side; no regrouping",
            check="no shared k1 carries a digit or '#' marker; pd_entries and "
                  "pwg_entries are >= 1 for all 4,093 rows",
            entries_per_lemma_pd_max=max(r["pd_entries"] for r in population),
            entries_per_lemma_pwg_max=max(r["pwg_entries"] for r in population),
        ),
        population=OrderedDict(shared_lemmas=totals["lemmas"],
                              scope="PD letter-a published fascicules vs PWG, H6949 unit"),
        raw_ledger_retained=OrderedDict(
            source="data/pd/pd_attestation_decomposition.tsv (H7095) and "
                   "data/pd/pd_quotations_vs_pwg.tsv (H6949), read-only",
            pd_attestations=totals["pd_attestations"], pwg_attestations=totals["pwg_attestations"],
            pd_quotations=totals["pd_quotations"], pwg_quotations=totals["pwg_quotations"],
            attestation_ratio=totals["attestation_ratio"],
            quotation_ratio=totals["quotation_ratio"],
            median_attestation_ratio=totals["median_attestation_ratio"],
            below_parity_lemmas=totals["below_parity_lemmas"],
            note="unchanged by this pass; the policy-matched table sits beside it",
        ),
        classification=OrderedDict(
            rule="scripts/lib/pd_family_rule.py (H7110): one analysis member => "
                 "simplex; last member in the 15-suffix set => derivative; else compound",
            source_sha256=pd_sha,
            universe=PINS["class_universe"], population=PINS["class_population"],
            classified=PINS["class_classified"],
            shared_classified=sum(1 for r in population if classes.get(r["k1"]) in FAMILIES),
        ),
        strata=OrderedDict(
            (s, OrderedDict(
                lemmas=score(strata[s])["lemmas"],
                lemmas_with_pwg_attestation=score(strata[s])["lemmas_with_pwg_attestation"],
                pd_attestations=score(strata[s])["pd_attestations"],
                pwg_attestations=score(strata[s])["pwg_attestations"],
                attestation_ratio=score(strata[s])["attestation_ratio"],
                quotation_ratio=score(strata[s])["quotation_ratio"],
                median_attestation_ratio=score(strata[s])["median_attestation_ratio"],
                below_parity_lemmas=score(strata[s])["below_parity_lemmas"],
                bootstrap_95=boot[s] if s in FAMILIES else None,
            )) for s in STRATA
        ),
        pooled=OrderedDict(
            standardised_equal_weight=OrderedDict(
                value=std, weights="1/3 per policy class (simplex, derivative, compound)",
                bootstrap_95=boot["standardised_ratio"],
                rationale="PWG prints no analysis parenthesis, so its own class mix is "
                          "not measurable; equal weights are the only policy-neutral "
                          "standard computable on both sides",
            ),
            pd_mix_weighted_mean_of_ratios=OrderedDict(
                value=pd_mix,
                note="weights = shared-lemma class shares; a mean of stratum ratios, "
                     "not the raw ratio of sums (8.5480)",
            ),
            raw_ratio_of_sums=OrderedDict(value=totals["attestation_ratio"],
                                         bootstrap_95=boot["raw_attestation_ratio"]),
            simplex_only=OrderedDict(value=ratios["simplex"],
                                     note="most policy-matched subset; PWG's own "
                                          "lemmatisation is closest to simplex"),
        ),
        bootstrap=OrderedDict(reps=BOOTSTRAP_REPS, seed=BOOTSTRAP_SEED,
                              method=boot["method"]),
        below_parity=OrderedDict(
            definition="pd_attestations < pwg_attestations (includes the lemmas "
                       "with zero PD attestations and a defined PWG ratio)",
            n=len(below),
            zero_pd=sum(1 for r in population
                        if r["pd_att"] == 0 and r["pwg_att"] > 0),
            by_stratum=OrderedDict((s, score(strata[s])["below_parity_lemmas"])
                                   for s in STRATA),
            membership_sha256=hashlib.sha256(("\n".join(below) + "\n").encode()).hexdigest(),
            examples_first=below[:10],
            examples_last=below[-10:],
        ),
        inventory_policy=OrderedDict(
            threshold_attestations=inv["threshold"],
            definition="a PD-only headword is thin when its entry carries at most "
                       "%d attestation(s)" % inv["threshold"],
            pd_only_headwords=inv["pd_only"], shared_headwords=inv["shared"],
            pd_only_at_most_one=next(r["headwords_at_most_one"] for r in inv["rows"]
                                     if r["scope"] == "pd_only" and r["family"] == "all"),
            pd_only_zero=next(r["headwords_zero_attestation"] for r in inv["rows"]
                              if r["scope"] == "pd_only" and r["family"] == "all"),
            pd_only_attestation_mass=next(r["attestation_mass"] for r in inv["rows"]
                                          if r["scope"] == "pd_only" and r["family"] == "all"),
            inventory_contrast=OrderedDict(
                value=inv["contrast"]["multiple"],
                rule="PD unique key1 / PWG lines to the apaca frontier",
                label="lemmatisation-choice (inventory) ratio, NOT a citation "
                      "measure and NOT a per-headword claim",
                detail=inv["contrast"],
            ),
        ),
        canaries=OrderedDict(
            akAmatas=OrderedDict(
                family=classes["akAmatas"], pd_quotations=akam["pd_quotations"],
                pwg_quotations=akam["pwg_quotations"], pd_attestations=akam["pd_att"],
                pwg_attestations=akam["pwg_att"],
                attestation_ratio=f4(akam["pd_att"] / akam["pwg_att"]),
            ),
            compound_stratum=OrderedDict(
                lemmas=score(strata["compound"])["lemmas"],
                pd_attestations=score(strata["compound"])["pd_attestations"],
                pwg_attestations=score(strata["compound"])["pwg_attestations"],
                attestation_ratio=score(strata["compound"])["attestation_ratio"],
            ),
            below_parity_lemmas=len(below),
            below_parity_sha256=hashlib.sha256(("\n".join(below) + "\n").encode()).hexdigest(),
            raw_ledger=OrderedDict(k for k in PINS.items() if k[0] in (
                "pd_attestations", "pwg_attestations", "pd_quotations",
                "pwg_quotations", "shared_lemmas", "below_parity_lemmas",
                "median_attestation_ratio")),
        ),
        inputs=OrderedDict(
            (os.path.relpath(p, ROOT).replace("\\", "/"), sha256(p))
            for p in (DECOMP, VS, ENTRIES, CLASS_TSV)
        ),
        verdict=OrderedDict(
            policy_matched_ratio=std,
            range_across_policies=[min(ratios.values()), max(ratios.values())],
            reading="the raw 8.55x is not an artefact of the shared lemmas' "
                    "family mix: every stratum sits at 7.5-9.1x and the "
                    "standardised pool is %.2fx; the 23x inventory contrast is a "
                    "lemmatisation-policy ratio, and the extra PD-only headwords are "
                    "mostly thin entries" % std,
        ),
    )
    return rows, payload


# ------------------------------------------------------------------- outputs
def render_json(payload):
    return json.dumps({**license_fields(), **payload}, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def render_inventory(inv):
    rows = [dict(r, row_kind="family_share") for r in inv["rows"]
            if r["scope"] != "pd_vs_pwg_span"]
    rows.append(dict(
        [r for r in inv["rows"] if r["scope"] == "pd_vs_pwg_span"][0],
        row_kind="inventory_contrast",
        note="%.1fx inventory contrast: lemmatisation-choice ratio, not a "
             "citation measure and not a per-headword claim"
             % inv["contrast"]["multiple"]))
    return dump_tsv(INV_COLUMNS, rows)


def render_report(payload, rows, inv):
    total = payload["raw_ledger_retained"]
    st = payload["strata"]
    pooled = payload["pooled"]
    inv_all = next(r for r in inv["rows"] if r["scope"] == "pd_only" and r["family"] == "all")
    sh_all = next(r for r in inv["rows"] if r["scope"] == "shared" and r["family"] == "all")
    contrast = payload["inventory_policy"]["inventory_contrast"]
    lines = []
    a = lines.append
    a("# PD policy-matched density: simplex, derivative, compound (H7297)")
    a("")
    a("_Created: 26-10-2026 · Last updated: 26-10-2026_")
    a("")
    a("_Source data: Cologne PDScan 2020 `txt/pd.txt` (55,122,076 B, SHA-256 "
      "`%s`), read-only · PWG: `csl-orig/v02/pwg/pwg.txt`, read-only · "
      "Raw ledgers: [pd_attestation_decomposition.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_attestation_decomposition.tsv) (H7095) and "
      "[pd_quotations_vs_pwg.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_quotations_vs_pwg.tsv) (H6949), unchanged._"
      % (payload["classification"]["source_sha256"] or "—"))
    a("")
    a("## Question")
    a("")
    a("The committed raw comparison reports **8.55× attestations** and **9.53× "
      "quotations** over the 4,093 lemmas both dictionaries treat, with a median of "
      "**4.0×** and **340** below-parity lemmas. PD's lemmatisation policy gives a "
      "headword to nearly every compound (70.7 % of its classified headwords), so the "
      "question this pass asks is narrow: **does the multiple survive when the "
      "comparison is stratified by the lemma's own morphological class, and what is "
      "the pooled ratio under a policy-neutral standard?**")
    a("")
    a("This changes the comparison policy only. The quotation unit, the attestation "
      "count and the entry-family rule are the frozen H6949, H7095 and H7110 "
      "definitions; no raw number is rebuilt or replaced.")
    a("")
    a("## Raw ledgers retained (not replaced)")
    a("")
    a("| Measure | PD | PWG | ratio |")
    a("|---|---:|---:|---:|")
    a("| Attestations | %s | %s | **%.2f×** |" % (
        f"{total['pd_attestations']:,}", f"{total['pwg_attestations']:,}",
        total["attestation_ratio"]))
    a("| Quotations | %s | %s | **%.2f×** |" % (
        f"{total['pd_quotations']:,}", f"{total['pwg_quotations']:,}",
        total["quotation_ratio"]))
    a("| Median per-lemma attestation ratio | — | — | **%.1f×** |"
      % total["median_attestation_ratio"])
    a("| Below-parity lemmas (PD < PWG) | — | — | **%d** |" % total["below_parity_lemmas"])
    a("")
    a("These are the H6949/H7095 values, re-read from their committed files by "
      "`--check`; the new table sits beside them.")
    a("")
    a("## Homograph grouping and class rule")
    a("")
    a("- **Homographs.** Both machine texts use a bare `k1`: homographs are separate "
      "`<L>` entries with the same `k1`, never numbered variants. A row is therefore "
      "the union of every homograph entry of that `k1` on each side; PD contributes up "
      "to %d entries and PWG up to %d for one shared lemma. The grouping is fixed "
      "before any result is read and is not revisited." % (
          payload["homograph_policy"]["entries_per_lemma_pd_max"],
          payload["homograph_policy"]["entries_per_lemma_pwg_max"]))
    a("- **Class rule** (H7110, `scripts/lib/pd_family_rule.py`): the first `( … )` "
      "after the `¦` separator on the entry's first body line is split on hyphen, "
      "en-dash, em-dash and whitespace after stripping Vedic accents; one member is a "
      "**simplex**, a last member in the 15-suffix set is a **derivative**, otherwise a "
      "**compound**. %s of the 4,093 shared lemmas classify; the %d that do not "
      "(no analysis parenthesis, or a CORRECTIONS block) form an explicit "
      "`unclassified` stratum and are excluded from the standardised pool." % (
          f"{payload['classification']['shared_classified']:,}",
          st["unclassified"]["lemmas"]))
    a("")
    a("## Strata")
    a("")
    a("| Stratum | lemmas | with PWG attestation | PD att. | PWG att. | ratio | 95 % CI | median | below parity |")
    a("|---|---:|---:|---:|---:|---:|---|---:|---:|")
    names = {"simplex": "simplex", "derivative": "derivative",
             "compound": "compound", "unclassified": "unclassified"}
    for s in ("simplex", "derivative", "compound", "unclassified"):
        d = st[s]
        ci = d["bootstrap_95"]
        a("| %s | %s | %s | %s | %s | **%.2f×** | %s | %.1f× | %d |" % (
            names[s], f"{d['lemmas']:,}", f"{d['lemmas_with_pwg_attestation']:,}",
            f"{d['pd_attestations']:,}", f"{d['pwg_attestations']:,}",
            d["attestation_ratio"],
            "%.2f–%.2f" % (ci[0], ci[1]) if ci else "—",
            d["median_attestation_ratio"], d["below_parity_lemmas"]))
    a("")
    a("The strata are close together: **7.53× simplex, 8.56× derivative, 9.13× "
      "compound**. The compound stratum is the largest (2,929 of 4,093 lemmas) and the "
      "densest, but it does not create the aggregate.")
    a("")
    a("## Standardised pooled result")
    a("")
    a("| Estimator | value | 95 % CI | meaning |")
    a("|---|---:|---|---|")
    a("| **Standardised, equal weights** | **%.2f×** | %.2f–%.2f | each policy class "
      "counts 1/3; the policy-neutral headline |" % (
          pooled["standardised_equal_weight"]["value"],
          pooled["standardised_equal_weight"]["bootstrap_95"][0],
          pooled["standardised_equal_weight"]["bootstrap_95"][1]))
    a("| Raw ratio of sums | %.2f× | %.2f–%.2f | the H7095 value, unchanged |" % (
        pooled["raw_ratio_of_sums"]["value"],
        pooled["raw_ratio_of_sums"]["bootstrap_95"][0],
        pooled["raw_ratio_of_sums"]["bootstrap_95"][1]))
    a("| PD-mix mean of stratum ratios | %.2f× | — | weights the strata by their "
      "shared-lemma shares; a mean of ratios, not a ratio of sums |"
      % pooled["pd_mix_weighted_mean_of_ratios"]["value"])
    a("| Simplex only | %.2f× | %.2f–%.2f | the most policy-matched subset |" % (
        pooled["simplex_only"]["value"], st["simplex"]["bootstrap_95"][0],
        st["simplex"]["bootstrap_95"][1]))
    a("")
    a("**Answer: %.2f× under equal policy weights, against the raw %.2f×.** The "
      "standardisation moves the pooled ratio by %.2f×, i.e. the aggregate is *not* an "
      "artefact of the shared lemmas' family mix: PD is 7.5–9.1 times denser inside "
      "every class, and no weighting of the classes pushes the figure outside that "
      "band. Denominators are the 4,093 shared lemmas, 4,059 of them classified; the "
      "95 %% intervals are a stratified lemma bootstrap (%s replicates, seed %d, "
      "ratio of sums per stratum, percentile interval), which resamples lemmas and "
      "therefore carries the heavy-tailed entries' influence." % (
          pooled["standardised_equal_weight"]["value"],
          pooled["raw_ratio_of_sums"]["value"],
          pooled["raw_ratio_of_sums"]["value"] - pooled["standardised_equal_weight"]["value"],
          f"{BOOTSTRAP_REPS:,}", BOOTSTRAP_SEED))
    a("")
    a("## Below-parity set (frozen)")
    a("")
    bp = payload["below_parity"]
    a("%d lemmas have PD attestations below PWG's — the %d lemmas with zero PD "
      "attestations and a defined PWG denominator, plus %d with a positive but "
      "insufficient count. By stratum: simplex %d, derivative %d, compound %d, "
      "unclassified %d. Membership is frozen by SHA-256 `%s` and re-checked on "
      "every `--check`."
      % (bp["n"], bp["zero_pd"], bp["n"] - bp["zero_pd"],
         bp["by_stratum"]["simplex"], bp["by_stratum"]["derivative"],
         bp["by_stratum"]["compound"], bp["by_stratum"]["unclassified"],
         bp["membership_sha256"]))
    a("")
    a("## Inventory policy (PD-only entries) — a separate result")
    a("")
    a("PD-only headwords are the %s keys that have no PWG counterpart; they are "
      "published here and nowhere else in this pass. A PD-only headword is **thin** "
      "when its entry carries at most %d attestation." % (
          f"{inv_all['headwords']:,}", inv["threshold"]))
    a("")
    a("| Scope | headwords | zero att. | at most one | share | median att. | mean att. | attestation mass |")
    a("|---|---:|---:|---:|---:|---:|---:|---:|")
    a("| PD-only | %s | %s | %s (%.1f %%) | 100 %% | %.1f | %.2f | %s |" % (
        f"{inv_all['headwords']:,}", f"{inv_all['headwords_zero_attestation']:,}",
        f"{inv_all['headwords_at_most_one']:,}",
        100.0 * inv_all["headwords_at_most_one"] / inv_all["headwords"],
        inv_all["median_attestations"], inv_all["mean_attestations"],
        f"{inv_all['attestation_mass']:,}"))
    a("| Shared (4,093) | %s | %s | %s | 100 %% | %.1f | %.2f | %s |" % (
        f"{sh_all['headwords']:,}", f"{sh_all['headwords_zero_attestation']:,}",
        f"{sh_all['headwords_at_most_one']:,}", sh_all["median_attestations"],
        sh_all["mean_attestations"], f"{sh_all['attestation_mass']:,}"))
    a("")
    a("The inventory contrast itself — **%.1f×** (PD %s unique key1 against PWG's "
      "%s lines to the *apaca* frontier) — is a **lemmatisation-choice ratio**. It is "
      "not a citation measure, not a density multiple, and never a typical "
      "per-headword claim: the extra headwords carry a median of %.0f attestation "
      "each, against %.1f in the shared set. PD's inventory policy multiplies "
      "headwords, not citations." % (
          contrast["value"], f"{contrast['detail']['pd_lemmas']:,}",
          f"{contrast['detail']['pwg_in_span']:,}",
          inv_all["median_attestations"], sh_all["median_attestations"]))
    a("")
    a("## What this does not claim")
    a("")
    a("- PD is measured on the published letter-*a* fascicules only; the shared set is "
      "the 4,093 lemmas both dictionaries treat.")
    a("- PWG prints no analysis parenthesis, so its own class mix is not measurable; "
      "the standardised pool is a PD-class standardisation, not a two-sided one.")
    a("- The class rule is a published heuristic: a compound whose last member is a "
      "suffix word counts as a derivative, and %d shared lemmas stay unclassified."
      % st["unclassified"]["lemmas"])
    a("- No row here is a typical per-headword claim: every ratio is an aggregate "
      "with its own PD and PWG denominator, and the inventory contrast is never "
      "restated as a density multiple.")
    a("- No A68 prose, table, figure or canary value changes in this pass.")
    a("")
    a("## Reproduction")
    a("")
    a("```sh")
    a("python3 scripts/pd_policy_matched_density.py --check")
    a("python3 -m pytest tests/forensic/test_pd_policy_matched_density.py -q")
    a("```")
    a("")
    a("`--check` re-derives the class join, every stratum denominator, the "
      "standardised pool, the bootstrap intervals and the canaries from the committed "
      "inputs and exits 2 with `STOP_CANARY_MISMATCH` on any drift. `--build --pd "
      "txt/pd.txt` re-derives the class ledger from the pinned source.")
    a("")
    a("_Dr. Mārcis Gasūns_")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------- build
def run_build(pd_path=None):
    if pd_path or not os.path.exists(CLASS_TSV):
        if not pd_path:
            raise SystemExit("pd.txt not given; pass --pd or commit the class ledger")
        built = build_class(pd_path)
        with open(CLASS_TSV, "w", encoding="utf-8", newline="") as fh:
            fh.write(dump_tsv(["k1", "family", "analysis"], built["rows"]))
        pd_sha = built["pd_sha256"]
    else:
        pd_sha = family_rule.PD_SHA256
    classes = load_class()
    rows = load_population()
    groups = by_stratum(rows, classes)
    boot = bootstrap(groups)
    inv = inventory(classes, rows)
    payload_rows, payload = build(rows, groups, boot, inv, classes, pd_sha)
    with open(OUT_TSV, "w", encoding="utf-8", newline="") as fh:
        fh.write(dump_tsv(DENSITY_COLUMNS, payload_rows))
    with open(OUT_INV, "w", encoding="utf-8", newline="") as fh:
        fh.write(render_inventory(inv))
    with open(OUT_JSON, "w", encoding="utf-8", newline="") as fh:
        fh.write(render_json(payload))
    with open(REPORT, "w", encoding="utf-8", newline="") as fh:
        fh.write(render_report(payload, payload_rows, inv))
    print("built: %s, %s, %s, %s" % (
        os.path.basename(OUT_TSV), os.path.basename(OUT_INV),
        os.path.basename(OUT_JSON), os.path.relpath(REPORT, ROOT)))
    print("standardised %.4f | raw %.4f | strata %s" % (
        payload["pooled"]["standardised_equal_weight"]["value"],
        payload["pooled"]["raw_ratio_of_sums"]["value"],
        ", ".join("%s %.4f" % (s, payload["strata"][s]["attestation_ratio"])
                  for s in ("simplex", "derivative", "compound"))))
    return payload


# --------------------------------------------------------------------- check
def run_check():
    classes = load_class()
    rows = load_population()
    groups = by_stratum(rows, classes)
    boot = bootstrap(groups)
    inv = inventory(classes, rows)
    payload_rows, payload = build(rows, groups, boot, inv, classes,
                                  family_rule.PD_SHA256)
    problems = []
    expected = {
        OUT_TSV: dump_tsv(DENSITY_COLUMNS, payload_rows),
        OUT_INV: render_inventory(inv),
        OUT_JSON: render_json(payload),
        REPORT: render_report(payload, payload_rows, inv),
    }
    for path, text in expected.items():
        if not os.path.exists(path):
            problems.append("missing %s" % os.path.relpath(path, ROOT))
            continue
        with open(path, encoding="utf-8") as fh:
            if fh.read() != text:
                problems.append("drift %s" % os.path.relpath(path, ROOT))
    # canaries, independently of the file comparison
    if payload["canaries"]["akAmatas"]["pd_attestations"] != 75:
        problems.append("akAmatas PD attestations")
    if payload["canaries"]["compound_stratum"]["lemmas"] != 2929:
        problems.append("compound stratum lemmas")
    if payload["canaries"]["below_parity_lemmas"] != 340:
        problems.append("below-parity count")
    if payload["inventory_policy"]["inventory_contrast"]["value"] != 23.2:
        problems.append("inventory contrast")
    for path in (OUT_JSON, REPORT, OUT_INV):
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        for phrase in BANNED:
            if phrase in text:
                problems.append("banned wording in %s: %s"
                                % (os.path.relpath(path, ROOT), phrase))
    if problems:
        print("STOP_CANARY_MISMATCH")
        for p in problems:
            print(" - %s" % p)
        return 2
    print("PASS pd policy-matched density: 4,093 lemmas | strata %s | "
          "standardised %.4f [%.4f, %.4f] | raw %.4f | below parity %d | "
          "PD-only %d headwords (%d at most one attestation) | inventory contrast %.1fx"
          % (", ".join("%s %.4f" % (s, payload["strata"][s]["attestation_ratio"])
                       for s in ("simplex", "derivative", "compound")),
             payload["pooled"]["standardised_equal_weight"]["value"],
             payload["pooled"]["standardised_equal_weight"]["bootstrap_95"][0],
             payload["pooled"]["standardised_equal_weight"]["bootstrap_95"][1],
             payload["pooled"]["raw_ratio_of_sums"]["value"],
             payload["below_parity"]["n"],
             payload["inventory_policy"]["pd_only_headwords"],
             payload["inventory_policy"]["pd_only_at_most_one"],
             payload["inventory_policy"]["inventory_contrast"]["value"]))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--build", action="store_true", help="write the artifacts")
    ap.add_argument("--check", action="store_true", help="re-derive and compare")
    ap.add_argument("--pd", default=None, help="path to PDScan 2020 txt/pd.txt")
    args = ap.parse_args(argv)
    if args.build:
        run_build(args.pd)
        return 0
    if args.check:
        return run_check()
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
