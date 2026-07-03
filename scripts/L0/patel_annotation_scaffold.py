"""Patel annotation scaffold: emit data/L0/patel_annotation_scaffold.csv with
up to three exemplar entries from each dict for each of the nine Patel-schema
dimensions (1-8 + 16). The annotator (M.G.) fills `annotator_value` per row,
optionally a new label in `annotator_label_if_new`, plus confidence and notes,
and the result is merged back into `data/L0/convention_fingerprint.csv` to
unblock the gated Stage 3 of phase L0.

32 dicts have local source under ../csl-orig/v02; the three absent (KNA, KOW,
AMAR) get rows with empty exemplars and source_available=no.
"""

import os
import sys
import csv
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from s2_fingerprint import iter_entries, SRC_ROOT, DIMS, CAP, ANNOTATION_ONLY  # noqa

N_EXEMPLARS = 3

# SLP1 consonant class (excludes vowels, anusvāra M, visarga H, avagraha ')
CONS_CLASS = r"[kKgGNcCjJYtTdDqQRpPbBmnvyrlSzsh]"

# Per-dim feature pattern. The annotator's task is to look at the exemplars and
# decide which option of the dim_schema (or which new label) describes the
# convention this dict uses.
EXEMPLAR_PATTERNS = {
    1: re.compile(r"M" + CONS_CLASS),                # anusvāra M + consonant in headword
    2: re.compile(r"r" + CONS_CLASS),                # r + consonant cluster
    3: re.compile(r"at$"),                            # headword ending -at
    4: None,                                          # any headword (form question is structural)
    5: None,                                          # verb entries with anusvāra: handled inline
    6: re.compile(r"f$"),                             # SLP1 f = ṛ-ending
    7: re.compile(r"(?:vas|yas)$"),                   # vas/yas suffixes
    8: re.compile(r"[-—]"),                           # compound boundary in k2
    16: re.compile(r"\b(?:Mbh|MBh|MahA|Mah\.|Mahābh|MBH)"),  # MBh edition citation
}


def find_exemplars(path):
    """Return {dim_id: [exemplar_string, ...]} from the dict's sampled entries."""
    out = {d: [] for d in sorted(ANNOTATION_ONLY)}
    if not os.path.isfile(path):
        return out
    for k1, k2, body in iter_entries(path, CAP):
        k1, k2 = k1.strip(), k2.strip()
        if len(out[1]) < N_EXEMPLARS and EXEMPLAR_PATTERNS[1].search(k1):
            out[1].append(k1)
        if len(out[2]) < N_EXEMPLARS and EXEMPLAR_PATTERNS[2].search(k1):
            out[2].append(k1)
        if len(out[3]) < N_EXEMPLARS and EXEMPLAR_PATTERNS[3].search(k1):
            out[3].append(k1)
        if len(out[4]) < N_EXEMPLARS:
            # show any 3 headwords -- annotator inspects the citation form
            out[4].append(k1)
        if len(out[5]) < N_EXEMPLARS and "M" in k1 and re.search(r"\b(?:cl|r)\.", body):
            snippet = re.sub(r"\s+", " ", body)[:90].strip()
            out[5].append(f"{k1} :: {snippet}")
        if len(out[6]) < N_EXEMPLARS and EXEMPLAR_PATTERNS[6].search(k1):
            out[6].append(k1)
        if len(out[7]) < N_EXEMPLARS and EXEMPLAR_PATTERNS[7].search(k1):
            out[7].append(k1)
        if len(out[8]) < N_EXEMPLARS and k2 and EXEMPLAR_PATTERNS[8].search(k2):
            out[8].append(k2)
        if len(out[16]) < N_EXEMPLARS:
            m = EXEMPLAR_PATTERNS[16].search(body)
            if m:
                ctx = body[max(0, m.start() - 25): m.end() + 35]
                ctx = re.sub(r"\s+", " ", ctx).strip()
                out[16].append(ctx)
        if all(len(v) >= N_EXEMPLARS for v in out.values()):
            break
    return out


def main():
    codes = []
    with open("data/L0/inventory_subset.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            codes.append(r["code"])

    rows = []
    n_dicts_with_source = 0
    for code in codes:
        path = os.path.join(SRC_ROOT, code.lower(), code.lower() + ".txt")
        present = os.path.isfile(path)
        if present:
            n_dicts_with_source += 1
        ex = find_exemplars(path) if present else {d: [] for d in sorted(ANNOTATION_ONLY)}
        for dim_id in sorted(ANNOTATION_ONLY):
            dim_meta = next(d for d in DIMS if d["dim_id"] == dim_id)
            exemplars = ex.get(dim_id, [])
            rows.append({
                "dict": code,
                "dim_id": dim_id,
                "dim_name": dim_meta["name"],
                "options_available": "|".join(dim_meta["options"]),
                "source_available": "yes" if present else "no",
                "exemplar_1": exemplars[0] if len(exemplars) > 0 else "",
                "exemplar_2": exemplars[1] if len(exemplars) > 1 else "",
                "exemplar_3": exemplars[2] if len(exemplars) > 2 else "",
                "annotator_value": "",
                "annotator_label_if_new": "",
                "annotator_confidence": "",
                "annotator_notes": "",
            })

    out_path = "data/L0/patel_annotation_scaffold.csv"
    fieldnames = list(rows[0].keys())
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    n_rows_with_ex = sum(1 for r in rows if r["exemplar_1"])
    n_per_dim = {d: 0 for d in sorted(ANNOTATION_ONLY)}
    for r in rows:
        if r["exemplar_1"]:
            n_per_dim[r["dim_id"]] += 1
    print(f"Wrote {out_path}")
    print(f"  {len(rows)} rows = {len(codes)} dicts x {len(ANNOTATION_ONLY)} Patel dims")
    print(f"  {n_dicts_with_source}/{len(codes)} dicts have local source")
    print(f"  {n_rows_with_ex}/{len(rows)} rows carry at least one exemplar")
    print("  exemplars per dim (across dicts):")
    for d, n in n_per_dim.items():
        dn = next(x["name"] for x in DIMS if x["dim_id"] == d)
        print(f"    dim {d:>2d} ({dn:<42s})  {n}/{len(codes)}")

    try:
        from _provenance import write_source
        write_source(out_path, "patel_annotation_scaffold.py", 2)
    except Exception as e:
        print(f"Provenance error: {e}")


if __name__ == "__main__":
    main()
