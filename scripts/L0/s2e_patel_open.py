"""Stage 2e (Phase L0.9) — operationalise Patel 2016's *open* conventions.

Patel's paper §TODO flags four conventions he did not finish:
  takārānta (mahat / mahant / mahā / mahān) — he gives a per-dict split for the
            single probe word महत्, calling it preliminary.
  sakārānta (s-final neuter stems) — analysis pending.
  rephānta  (r-final stems)        — analysis pending.
  ṛ-nipātita (e.g. jāmātṛ)          — flagged as possibly distinct from conv. 6.

We complete the first three using **Patel's own method**: probe a small set of
diagnostic lemmas and record which citation variant each dictionary actually lists
(more reliable than blind pattern-matching — cf. the L0 "validate detectors against
real entries" lesson). Each becomes a fingerprint dim (31 takārānta, 32 sakārānta,
33 rephānta), multi-valued, source `patel-open`. ṛ-nipātita needs a curated
nipātita lemma list and is left documented, not yet a dim.

The takārānta dim is **validated against Patel's published महत् split** (agreement
printed). Outputs feed both the cladogram (re-run s3) and the hwnorm1 contribution.

Appends dim_31..dim_33 to data/L0/convention_fingerprint.csv + dim_schema.json;
writes data/L0/patel_open_assignments.csv, patel_open_evidence.json.
Run after s2/s2b/s2d.
"""

import os
import sys
import re
import csv
import json
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_ROOT = os.path.normpath(os.path.join(REPO, "..", "csl-orig", "v02"))
FP = "data/L0/convention_fingerprint.csv"
CAP = None  # probe lemmas (manas, mahat, antar…) are mid/late-alphabet → scan the WHOLE file

# Probe lemmas (SLP1) → {variant_form: option_code}. A dict "follows" an option if
# it lists that headword form. Multiple options → multi-valued cell.
PROBES = {
    31: {  # takārānta (mahat-type त्-stems)
        "name": "takārānta words (mahat-type)",
        "options": {"31.1": "-at (mahat)", "31.2": "-ant (mahant)",
                    "31.3": "-ān (mahān)", "31.4": "-ānt (mahānt)"},
        "lemmas": {
            "mahat": {"mahat": "31.1", "mahant": "31.2", "mahAn": "31.3", "mahAnt": "31.4"},
            "bfhat": {"bfhat": "31.1", "bfhant": "31.2", "bfhAn": "31.3"},
        },
    },
    32: {  # sakārānta (s-final neuter stems)
        "name": "sakārānta words (s-final stems)",
        "options": {"32.1": "-as (manas)", "32.2": "-aH (manaH visarga)", "32.3": "-a (stem)"},
        "lemmas": {
            "manas": {"manas": "32.1", "manaH": "32.2"},
            "tejas": {"tejas": "32.1", "tejaH": "32.2"},
            "payas": {"payas": "32.1", "payaH": "32.2"},
            "yaSas": {"yaSas": "32.1", "yaSaH": "32.2"},
            "Danus": {"Danus": "32.1", "DanuH": "32.2"},
            "cakzus": {"cakzus": "32.1", "cakzuH": "32.2"},
        },
    },
    33: {  # rephānta (r-final stems)
        "name": "rephānta words (r-final stems)",
        "options": {"33.1": "-ar/-r (antar)", "33.2": "-aH (antaH visarga)"},
        "lemmas": {
            "antar": {"antar": "33.1", "antaH": "33.2"},
            "punar": {"punar": "33.1", "punaH": "33.2"},
            "prAtar": {"prAtar": "33.1", "prAtaH": "33.2"},
            "svar": {"svar": "33.1", "svaH": "33.2"},
        },
    },
}
# Documented-only (needs curated list) — recorded, not a dim yet.
NIPATITA_PROBES = ["jAmAtf", "naptf", "duhitf"]

ENGLISH = {"BOR", "AE", "MWE"}

# Patel's published महत् split (PDF §TODO) — for validating dim 31.
PATEL_MAHAT = {
    "31.1": {"AP", "AP90", "BHS", "BOP", "BUR", "GRA", "INM", "MD", "MW", "MW72",
             "PUI", "PW", "SHS", "SKD", "VCP", "WIL", "YAT"},
    "31.2": {"BEN", "CAE", "CCS", "IEG", "PW", "PWG", "SCH"},
    "31.3": {"PE", "PUI", "SKD"},
    "31.4": {"STC"},
}


def headword_set(path, cap):
    hws = set()
    n = 0
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("<L>") or line.startswith("<L "):
                m = re.search(r"<k1>([^<]*)", line)
                if m:
                    hw = m.group(1).strip()
                    if hw:
                        hws.add(hw)
                n += 1
                if cap is not None and n >= cap:
                    break
    return hws


def detect(hws, probes):
    """Return (sorted option list, hits dict) for one convention's probe set."""
    opt_hits = defaultdict(list)
    for lemma, variants in probes["lemmas"].items():
        for form, opt in variants.items():
            if form in hws:
                opt_hits[opt].append(form)
    return sorted(opt_hits), dict(opt_hits)


def main():
    rows = []
    with open(FP, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    # add new columns if absent
    for d in (31, 32, 33):
        for suf in ("value", "source", "confidence"):
            col = f"dim_{d}_{suf}"
            if col not in fieldnames:
                fieldnames.append(col)

    evidence = {}
    assign = {31: defaultdict(list), 32: defaultdict(list), 33: defaultdict(list)}
    patched = defaultdict(int)
    for r in rows:
        code = r["dict"]
        path = os.path.join(SRC_ROOT, code.lower(), code.lower() + ".txt")
        ev = {}
        if code in ENGLISH or not os.path.isfile(path):
            for d in (31, 32, 33):
                r[f"dim_{d}_value"] = "unknown"
                r[f"dim_{d}_source"] = "unknown"
                r[f"dim_{d}_confidence"] = ""
            evidence[code] = "english/no-source"
            continue
        hws = headword_set(path, CAP)
        for d in (31, 32, 33):
            opts, hits = detect(hws, PROBES[d])
            ev[f"dim{d}"] = {"options": opts, "hits": hits}
            if opts:
                r[f"dim_{d}_value"] = "+".join(opts)
                r[f"dim_{d}_source"] = "patel-open"
                # confidence scales with number of probe lemmas that resolved
                nlem = len({f for hs in hits.values() for f in hs})
                r[f"dim_{d}_confidence"] = round(min(0.9, 0.55 + 0.12 * nlem), 2)
                patched[d] += 1
                for o in opts:
                    assign[d][o].append(code)
            else:
                r[f"dim_{d}_value"] = "unknown"
                r[f"dim_{d}_source"] = "unknown"
                r[f"dim_{d}_confidence"] = ""
        # ṛ-nipātita probe (documented only)
        ev["nipatita_forms"] = [w for w in NIPATITA_PROBES if w in hws]
        evidence[code] = ev

    with open(FP, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    # extend dim_schema.json
    with open("data/L0/dim_schema.json", "r", encoding="utf-8") as f:
        schema = json.load(f)
    have = {d["dim_id"] for d in schema}
    for d in (31, 32, 33):
        if d not in have:
            schema.append({"dim_id": d, "name": PROBES[d]["name"],
                           "options": list(PROBES[d]["options"])})
    with open("data/L0/dim_schema.json", "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)

    # assignments table (hwnorm1-ready)
    with open("data/L0/patel_open_assignments.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["convention", "option", "definition", "member_dicts", "source"])
        for d in (31, 32, 33):
            for opt, defn in PROBES[d]["options"].items():
                members = sorted(assign[d].get(opt, []))
                w.writerow([d, opt, defn, " ".join(members), "computed (probe-lemma)"])

    with open("data/L0/patel_open_evidence.json", "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2, ensure_ascii=False)

    # ---- validate dim 31 against Patel's published महत् split ----
    mine31 = {}
    for code, ev in evidence.items():
        if isinstance(ev, dict) and "dim31" in ev:
            mine31[code] = set(ev["dim31"]["options"])
    agree = disagree = both = 0
    val_rows = []
    for code, opts in mine31.items():
        patel_opts = {o for o, members in PATEL_MAHAT.items() if code in members}
        if not patel_opts and not opts:
            continue
        both += 1
        inter = opts & patel_opts
        if inter:
            agree += 1
        else:
            disagree += 1
        val_rows.append((code, "+".join(sorted(opts)) or "—",
                         "+".join(sorted(patel_opts)) or "—", "✓" if inter else "✗"))
    val_rate = agree / both if both else 0.0

    print("Patel-open conventions patched:", dict(patched))
    print(f"\ndim 31 takārānta — validation vs Patel's published महत् split:")
    print(f"  {'dict':6s} {'mine(probe)':14s} {'patel(mahat)':14s} ok")
    for code, m, p, ok in sorted(val_rows):
        print(f"  {code:6s} {m:14s} {p:14s} {ok}")
    print(f"  agreement: {agree}/{both} = {val_rate*100:.0f}%")

    print("\nComputed per-dict assignments (completing Patel's TODO):")
    for d in (31, 32, 33):
        print(f"\n  dim {d} — {PROBES[d]['name']}:")
        for opt, defn in PROBES[d]["options"].items():
            members = sorted(assign[d].get(opt, []))
            if members:
                print(f"    {opt} {defn:22s} : {' '.join(members)}")

    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from _provenance import write_source
        write_source(FP, "s2e_patel_open.py", 2)
        write_source("data/L0/patel_open_assignments.csv", "s2e_patel_open.py", 2)
    except Exception as e:
        print(f"Provenance error: {e}")


if __name__ == "__main__":
    main()
