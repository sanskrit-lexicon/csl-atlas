"""Stage 2d — ingest Patel 2016's authoritative per-dict convention assignments.

Patel (2016, "Normalizing headwords of Cologne digital dictionaries") does not
merely define conventions 1–7; he classifies **every Cologne dictionary** into the
options of each convention. That is gold-standard ground truth from the convention
author, so it supersedes our mechanical guesses (s2b) and closes the annotation gate
for every dict Patel covers (all of ours except LRV, FRI — not in his 36 — and the
3 source-less ones). English-headword dicts (BOR, AE) are excluded by Patel from the
Sanskrit-headword conventions → their dims 1–7 are set N/A (unknown).

Conventions are multi-valued (a dict can follow several options of conv. 1/3/5/7),
so each cell stores the `+`-joined option set, e.g. AP90 dim 1 = `1.1+1.3+1.5`.
`s3_cladogram.py` expands these into per-option one-hot tokens (encoding A) and uses
cell-level Jaccard inside the Hamming metrics — the faithful binary-character model.

Patches dims 1–7 of data/L0/convention_fingerprint.csv (source = `patel2016`,
confidence 0.95; inconsistent cells get both options at 0.6). Also writes the
ground-truth table data/L0/patel2016_assignments.csv. Run after s2 + s2b.
"""

import os
import sys
import csv
import json
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

FP = "data/L0/convention_fingerprint.csv"

# ---- Patel 2016 option → member dictionaries (transcribed from the paper) ----
# Each convention maps option-code -> set of dict codes.
PATEL = {
    1: {  # Anusvāra before consonants
        "1.1": {"AP90"},
        "1.2": {"ACC", "AP", "BEN", "BHS", "BOP", "BUR", "CAE", "CCS", "GRA", "GST",
                "IEG", "INM", "MCI", "MD", "MW", "MW72", "PD", "PE", "PGN", "PUI",
                "PW", "PWG", "SCH", "SHS", "SKD", "SNP", "STC", "VCP", "VEI", "WIL", "YAT"},
        "1.3": {"AP90", "SKD"},
        "1.4": {"YAT"},
        "1.5": {"ACC", "AP", "AP90", "BEN", "BHS", "CAE", "CCS", "MCI", "MD", "PD",
                "PW", "PWG", "SCH", "STC", "VEI", "WIL"},
        "1.6": {"BOP", "BUR", "GRA", "GST", "KRM", "IEG", "INM", "MW72", "PGN", "PUI",
                "SKD", "VCP", "YAT"},
    },
    2: {  # Duplication of consonants after r
        "2.1": {"SKD", "WIL"},
        "2.2": {"ACC", "AP", "AP90", "BEN", "BHS", "BOP", "BUR", "CAE", "CCS", "GRA",
                "GST", "IEG", "INM", "KRM", "MCI", "MD", "MW", "MW72", "PD", "PE",
                "PGN", "PUI", "PW", "PWG", "SCH", "SNP", "STC", "VCP", "VEI"},
        # SHS, YAT explicitly inconsistent → handled as 2.1+2.2 below
    },
    3: {  # Words ending with -at (śatṛ 3.1–3.3 + vatup/matup 3.4–3.5)
        "3.1": {"AP", "AP90", "BOP", "BUR", "GRA", "GST", "MD", "MW", "MW72", "PD",
                "SHS", "VCP", "WIL", "YAT"},
        "3.2": {"BEN", "BHS", "CAE", "CCS", "PW", "PWG", "SCH", "STC", "VEI"},
        "3.3": {"SKD"},
        "3.4": {"ACC", "AP", "AP90", "BOP", "BUR", "GRA", "GST", "IEG", "INM", "MCI",
                "MD", "MW", "PD", "SHS", "VCP", "WIL", "YAT"},
        "3.5": {"BEN", "BHS", "CAE", "CCS", "PW", "PWG", "SCH", "STC"},
    },
    4: {  # Uninflected / inflected
        "4.1": {"AP", "AP90", "SKD"},
        "4.2": {"BEN", "BHS", "BOP", "BUR", "CAE", "CCS", "GRA", "GST", "IEG", "INM",
                "MCI", "MD", "MW", "MW72", "PD", "PE", "PGN", "PUI", "PW", "PWG",
                "SCH", "SHS", "SNP", "STC", "VCP", "VEI", "WIL", "YAT"},
        # ACC inconsistent → 4.1+4.2 below
    },
    5: {  # Anusvāra of verb
        "5.1": {"KRM", "PD", "SKD", "VCP", "WIL"},
        "5.2": {"AP", "BEN", "BOP", "BUR", "CAE", "CCS", "GRA", "GST", "MD", "MW",
                "MW72", "PD", "PW", "PWG", "SCH", "SHS", "STC", "YAT"},
        "5.3": {"AP90"},
    },
    6: {  # ṛkārānta
        "6.1": {"BHS", "CCS", "PW", "PWG", "SCH"},
        "6.2": {"ACC", "AP", "AP90", "BEN", "BOP", "BUR", "CAE", "GRA", "GST", "IEG",
                "INM", "MD", "MW", "MW72", "PD", "SHS", "STC", "VCP", "VEI", "WIL", "YAT"},
        "6.3": {"PUI", "SKD"},
    },
    7: {  # vas/yas suffixes
        "7.1": {"AP", "AP90", "BOP", "BUR", "CCS", "GRA", "GST", "INM", "MCI", "MD",
                "MW", "MW72", "PD", "PE", "SHS", "VCP", "WIL", "YAT"},
        "7.2": {"BHS", "STC"},
        "7.3": {"PUI", "SKD"},
        "7.4": {"CAE", "PW", "PWG", "SCH"},
    },
}

# Explicit per-(dict,conv) inconsistencies noted by Patel (union of options, low conf).
INCONSISTENT = {
    ("SHS", 2): ["2.1", "2.2"],
    ("YAT", 2): ["2.1", "2.2"],
    ("ACC", 4): ["4.1", "4.2"],
}

# English-Sanskrit dicts: Patel excludes them from Sanskrit-headword conventions.
ENGLISH_HEADWORD = {"BOR", "AE", "MWE"}
# Standardized convention recommended by Patel (for the reference table).
STANDARD = {1: "1→anusvāra internal; final→म्", 2: "2.2 (no duplication)",
            3: "3.1 (-at)", 4: "4.2 (uninflected)", 5: "5.3 (remove anubandha, keep anusvāra)",
            6: "6.2 (-ṛ)", 7: "7.1 (-vas/-yas)"}
DEFN = {
    "1.1": "internal nasal → anusvāra (AP90)",
    "1.2": "internal nasal → fifth letter of varga (homorganic)",
    "1.3": "final anusvāra denotes neuter gender",
    "1.4": "final anusvāra denotes avyaya (where म् expected)",
    "1.5": "compound-final म् + jhar-initial 2nd member → anusvāra",
    "1.6": "compound-final म् → fifth letter of varga",
    "2.1": "duplication after r in all cases (pūrvva)",
    "2.2": "no duplication (pūrva)",
    "3.1": "śatṛ → -at (gacchat)", "3.2": "śatṛ → -ant (…gacchant)", "3.3": "śatṛ → -an (paśyan)",
    "3.4": "vatup/matup → -vat/-mat (bhagavat)", "3.5": "vatup/matup → -vant/-mant (bhagavant)",
    "4.1": "inflected (nom. sg., dharmaḥ)", "4.2": "uninflected stem (dharma)",
    "5.1": "verbs as in Dhātupāṭha", "5.2": "remove anubandha + fifth letter",
    "5.3": "remove anubandha, keep anusvāra (AP90)",
    "6.1": "ṛ-stem → -ar (kartar)", "6.2": "ṛ-stem → -ṛ (kartṛ)", "6.3": "ṛ-stem → -ā inflected (kartā)",
    "7.1": "-vas/-yas (vidvas)", "7.2": "-vāṃs/-yāṃs", "7.3": "-vān/-yān (vidvān)", "7.4": "-vaṃs/-yaṃs",
}


def dict_options(code, conv):
    """Return sorted option list this dict belongs to for a convention (incl. inconsistency)."""
    if (code, conv) in INCONSISTENT:
        return INCONSISTENT[(code, conv)]
    opts = sorted(o for o, members in PATEL[conv].items() if code in members)
    return opts


def main():
    rows = []
    with open(FP, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    patched = defaultdict(int)
    na = 0
    report = {}
    for r in rows:
        code = r["dict"]
        rep = {}
        if code in ENGLISH_HEADWORD:
            # conventions about Sanskrit headwords do not apply
            for conv in range(1, 8):
                r[f"dim_{conv}_value"] = "unknown"
                r[f"dim_{conv}_source"] = "unknown"
                r[f"dim_{conv}_confidence"] = ""
            na += 1
            report[code] = "english-headword → dims 1-7 N/A"
            continue
        for conv in range(1, 8):
            opts = dict_options(code, conv)
            if not opts:
                rep[conv] = None
                continue  # not covered / not-enough-data → leave as-is (unknown)
            val = "+".join(opts)
            inconsistent = (code, conv) in INCONSISTENT
            r[f"dim_{conv}_value"] = val
            r[f"dim_{conv}_source"] = "patel2016"
            r[f"dim_{conv}_confidence"] = 0.6 if inconsistent else 0.95
            patched[conv] += 1
            rep[conv] = val
        report[code] = rep

    with open(FP, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    # ground-truth assignment table
    with open("data/L0/patel2016_assignments.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["convention", "option", "definition", "member_dicts"])
        for conv in range(1, 8):
            for opt in sorted(PATEL[conv]):
                members = sorted(PATEL[conv][opt])
                w.writerow([conv, opt, DEFN.get(opt, ""), " ".join(members)])
        for (code, conv), opts in INCONSISTENT.items():
            w.writerow([conv, "+".join(opts), f"INCONSISTENT ({code})", code])

    with open("data/L0/patel_gold_report.json", "w", encoding="utf-8") as f:
        json.dump({"patched_per_conv": dict(patched), "english_na": na,
                   "standard_convention": STANDARD, "per_dict": report},
                  f, indent=2, ensure_ascii=False)

    # regenerate annotation_todo (what still needs a human / source)
    with open("data/L0/dim_schema.json", "r", encoding="utf-8") as f:
        dims = json.load(f)
    nm = {d["dim_id"]: d["name"] for d in dims}
    op = {d["dim_id"]: "|".join(d["options"]) for d in dims}
    todos = []
    for r in rows:
        for d in range(1, 31):
            if r[f"dim_{d}_source"] == "unknown":
                todos.append({"dict": r["dict"], "dim_id": d, "dim_name": nm[d],
                              "options_available": op[d]})
    with open("data/L0/annotation_todo.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["dict", "dim_id", "dim_name", "options_available"])
        w.writeheader()
        w.writerows(todos)

    print("Patel-2016 gold patched per convention:", dict(patched))
    print(f"English-headword dicts set N/A for dims 1-7: {na}")
    print(f"annotation_todo rows remaining: {len(todos)}\n")
    print("Per-dict convention fingerprint (dims 1-7):")
    print(f"{'dict':6s} {'c1':10s} {'c2':9s} {'c3':10s} {'c4':5s} {'c5':9s} {'c6':5s} {'c7':5s}")
    for code, rep in report.items():
        if isinstance(rep, str):
            print(f"{code:6s} {rep}")
            continue
        def g(c):
            return rep.get(c) or "—"
        print(f"{code:6s} {g(1):10s} {g(2):9s} {g(3):10s} {g(4):5s} {g(5):9s} {g(6):5s} {g(7):5s}")

    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from _provenance import write_source
        write_source(FP, "s2d_patel_gold.py", 2)
        write_source("data/L0/patel2016_assignments.csv", "s2d_patel_gold.py", 2)
    except Exception as e:
        print(f"Provenance error: {e}")


if __name__ == "__main__":
    main()
