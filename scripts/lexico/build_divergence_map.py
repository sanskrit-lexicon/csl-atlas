"""Build sense_divergence.json — cross-dict entry-coverage divergence worklist.

Reads microstructure_profile.csv (one row per dictionary entry) and counts
how many entries each of the 7 core CDSL dicts devotes to each normalized
headword (k1).  High divergence = one dict splits a lemma into many entries
while another gives it just one — a flag for editorial review.

Metric: entry-count divergence = max(entry_counts) - min(entry_counts)
across all core dicts that contain the lemma.

Output: data/lexico/sense_divergence.json

Run from the csl-atlas repo root:
    python scripts/lexico/build_divergence_map.py
"""

import csv
import json
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

SRC = "data/lexico/microstructure_profile.csv"
OUT = "data/lexico/sense_divergence.json"
SCHEMA_VERSION = "1.0.0"
GENERATED_AT = "2026-06-10"

# The 7 dictionaries used in the core comparison layer
CORE_DICTS = {"mw", "ap", "pwg", "pwk", "wil", "vcp", "skd"}

DICT_LABELS = {
    "mw":  "Monier-Williams 1899",
    "ap":  "Apte 1957",
    "pwg": "PW Grosses 1855",
    "pwk": "PW Kürzeres 1879",
    "wil": "Wilson 1832",
    "vcp": "Vācaspatya 1873",
    "skd": "Śabdakalpadruma 1822",
}

# ── Load entry counts per (dict, k1) ─────────────────────────────────────────

entry_count: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
total_rows = 0

with open(SRC, encoding="utf-8") as fh:
    reader = csv.DictReader(fh)
    for row in reader:
        d = row["dict"]
        if d not in CORE_DICTS:
            continue
        k1 = row["k1"].strip()
        if k1:
            entry_count[k1][d] += 1
            total_rows += 1

print(f"Loaded {total_rows:,} core-dict rows, {len(entry_count):,} unique k1 values")

# ── Compute divergence ────────────────────────────────────────────────────────

results = []
for k1, dc in entry_count.items():
    if len(dc) < 2:
        continue  # need at least 2 dicts to compute divergence
    counts = list(dc.values())
    rng = max(counts) - min(counts)
    total_entries = sum(counts)
    results.append(
        {
            "k1": k1,
            "nDicts": len(dc),
            "entryCounts": dict(sorted(dc.items())),
            "range": rng,
            "totalEntries": total_entries,
        }
    )

# Sort: primary = range descending; secondary = nDicts descending; tertiary = k1 alpha
results.sort(key=lambda r: (-r["range"], -r["nDicts"], r["k1"]))

# Distribution summary
from collections import Counter
dist = Counter(r["range"] for r in results)
print("Range distribution:", dict(sorted(dist.items())))
print(f"Lemmas with range > 0: {sum(v for k,v in dist.items() if k > 0)}")

# ── Write output ─────────────────────────────────────────────────────────────

out = {
    "schemaVersion": SCHEMA_VERSION,
    "generatedBy": "scripts/lexico/build_divergence_map.py",
    "generatedAt": GENERATED_AT,
    "sourceFile": SRC,
    "coreDicts": sorted(CORE_DICTS),
    "dictLabels": DICT_LABELS,
    "metric": (
        "entry-count divergence: max(entry_counts_per_dict) - min(entry_counts_per_dict). "
        "Counts how many main-entry lines each dict devotes to this headword. "
        "High divergence = one dict splits the lemma into many entries while "
        "another gives it one — an editorial review signal."
    ),
    "lemmaCount": len(results),
    "lemmas": results,
}

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, separators=(",", ":"))

size_kb = len(json.dumps(out, ensure_ascii=False, separators=(",", ":"))) / 1024
print(f"\nWrote {OUT}: {len(results):,} lemmas, {size_kb:.0f} KB")
