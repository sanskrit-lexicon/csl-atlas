"""Apply M.G.'s LRV/FRI Patel annotation from the review sheet into the fingerprint.

Closes the human gate opened by gen_lrv_fri_annotation_sheet.py. Two-layer design
so the annotation is DURABLE — re-running s2d (Patel gold) resets LRV/FRI dims
1,3,5,6,7 to "unknown" (they are not in Patel's member sets), which would silently
wipe this hand assignment. To prevent that overlay-wipe, the assignment is stored
in a committed overlay (data/L0/manual_annotations.csv) and re-applied on top of the
fingerprint every run. Pipeline order becomes:  s2 → s2b → s2d → THIS → s3 → s5.

Flow:
  1. If review/lrv_fri_patel_decisions.json exists, upsert its assigned items into
     the overlay (deferred / unassigned items are skipped, left "unknown").
  2. Apply the overlay onto data/L0/convention_fingerprint.csv
     (dim value = '+'-joined sorted Patel option set; source = 'mg-annot').
  3. With --rerun: run s3_cladogram.py then s5_bayesian.py and print LRV/FRI
     nearest neighbours + validation summary so placement can be eyeballed.

Run from repo root:
  python scripts/L0/apply_lrv_fri_annotation.py            # ingest + apply
  python scripts/L0/apply_lrv_fri_annotation.py --rerun    # + rebuild trees
"""

import os
import sys
import csv
import json
import subprocess

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(REPO, "data", "L0")
DECISIONS = os.path.join(REPO, "review", "lrv_fri_patel_decisions.json")
OVERLAY = os.path.join(DATA, "manual_annotations.csv")
FINGERPRINT = os.path.join(DATA, "convention_fingerprint.csv")
ALLOWED_DIMS = {1, 3, 5, 6, 7}
ALLOWED_DICTS = {"LRV", "FRI"}
SOURCE_TAG = "mg-annot"
CONFIDENCE = 0.8


def ingest_decisions():
    """decisions.json -> upsert assigned rows into the committed overlay."""
    if not os.path.isfile(DECISIONS):
        return None
    with open(DECISIONS, encoding="utf-8") as f:
        doc = json.load(f)
    decided = doc.get("decided", "")
    # load existing overlay keyed (dict,dim)
    overlay = {}
    if os.path.isfile(OVERLAY):
        with open(OVERLAY, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                overlay[(r["dict"], int(r["dim"]))] = r
    applied, deferred, skipped = 0, 0, 0
    for it in doc.get("items", []):
        d, dim = it.get("dict"), it.get("dim")
        if d not in ALLOWED_DICTS or dim not in ALLOWED_DIMS:
            print(f"  ! ignoring out-of-scope item {it.get('id')}")
            skipped += 1
            continue
        if it.get("status") == "assigned" and it.get("selected"):
            val = "+".join(sorted(it["selected"]))
            overlay[(d, dim)] = {"dict": d, "dim": dim, "value": val,
                                 "confidence": CONFIDENCE, "note": it.get("note", ""),
                                 "decided": decided}
            applied += 1
        else:
            deferred += 1  # deferred or unvoted -> stays unknown
    with open(OVERLAY, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["dict", "dim", "value", "confidence", "note", "decided"])
        w.writeheader()
        for k in sorted(overlay):
            w.writerow(overlay[k])
    print(f"Ingested decisions.json: {applied} assigned, {deferred} deferred/unvoted, {skipped} out-of-scope.")
    print(f"Overlay -> {OVERLAY} ({len(overlay)} rows)")
    return applied


def apply_overlay():
    """Patch the fingerprint from the overlay. Returns count of cells written."""
    if not os.path.isfile(OVERLAY):
        print("No overlay yet — nothing to apply. Produce review/lrv_fri_patel_decisions.json first.")
        return 0
    ann = {}
    with open(OVERLAY, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ann[(r["dict"], int(r["dim"]))] = r
    with open(FINGERPRINT, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        fields = rows[0].keys()
    written = 0
    for r in rows:
        for (d, dim), a in ann.items():
            if r["dict"] == d:
                r[f"dim_{dim}_value"] = a["value"]
                r[f"dim_{dim}_source"] = SOURCE_TAG
                r[f"dim_{dim}_confidence"] = a["confidence"]
                written += 1
    with open(FINGERPRINT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(fields))
        w.writeheader()
        w.writerows(rows)
    print(f"Applied overlay: {written} cells patched in convention_fingerprint.csv.")
    for (d, dim), a in sorted(ann.items()):
        print(f"    {d} dim {dim} = {a['value']}  ({a['note'] or 'no note'})")
    return written


def rerun_and_report():
    for stage in ("s3_cladogram.py", "s5_bayesian.py"):
        print(f"\n=== running {stage} ===")
        p = subprocess.run([sys.executable, os.path.join("scripts", "L0", stage)],
                           cwd=REPO, encoding="utf-8", capture_output=True)
        sys.stdout.write(p.stdout[-1500:] if p.stdout else "")
        if p.returncode != 0:
            sys.stderr.write(p.stderr[-2000:])
            print(f"!! {stage} failed (rc={p.returncode})")
            return
    # nearest-neighbour readout for LRV/FRI from the whamming distance matrix
    dm = os.path.join(DATA, "distances", "B_whamming.csv")
    if os.path.isfile(dm):
        with open(dm, encoding="utf-8") as f:
            rd = list(csv.reader(f))
        hdr = rd[0][1:]
        M = {row[0]: {hdr[i]: float(row[i + 1]) for i in range(len(hdr))} for row in rd[1:]}
        for d in ("LRV", "FRI"):
            if d in M:
                nn = sorted(((o, v) for o, v in M[d].items() if o != d), key=lambda x: x[1])[:5]
                print(f"\n{d} nearest neighbours:", ", ".join(f"{o}({v:.2f})" for o, v in nn))


def main():
    ingest_decisions()
    apply_overlay()
    if "--rerun" in sys.argv:
        rerun_and_report()


if __name__ == "__main__":
    main()
