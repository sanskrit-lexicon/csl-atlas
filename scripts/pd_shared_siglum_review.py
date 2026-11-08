#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export the source evidence for every shared PD siglum fold.

This is a read-only review aid for Y0Q.  It reconstructs the shared-fold set
with the registry's own fold rule, then places the printed Index rows, AOB
claims, harvested families, reconciliation rows and affected registry records
side by side.  It makes no identity decision and writes nothing unless
--output is supplied.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import os
import sys

from pd_shared_work_registry import (
    AOB_WORKS,
    FAMILIES,
    INDEX,
    RECON,
    ROOT_DEFAULT,
    fold,
)

REGISTRY = "data/pd/pd_work_registry.tsv"


def read_tsv(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def review(root):
    index = read_tsv(root, INDEX)
    aob = read_tsv(root, AOB_WORKS)
    families = read_tsv(root, FAMILIES)
    reconciliation = read_tsv(root, RECON)
    registry = read_tsv(root, REGISTRY)

    index_by_fold = collections.defaultdict(list)
    for row in index:
        siglum = (row["abbreviation_siglum"] or "").strip()
        if siglum:
            index_by_fold[fold(siglum)].append(row)
    aob_by_fold = collections.defaultdict(list)
    for row in aob:
        for siglum in (s.strip() for s in (row["sigla"] or "").split(";")):
            if siglum:
                aob_by_fold[fold(siglum)].append(row)

    index_seeds = collections.defaultdict(set)
    for f, rows in index_by_fold.items():
        for r in rows:
            title_key = fold(r["title_deva"]) or fold(r["title_iast"]) or f
            index_seeds[f].add(f"IDX:{f}:{title_key}")
    aob_seeds = collections.defaultdict(list)
    for f, rows in aob_by_fold.items():
        for r in rows:
            matching = [s for s in (r["sigla"] or "").split(";") if fold(s) == f]
            aob_seeds[f].extend(["AOB:" + fold(r["work_fold"])] * len(matching))
    shared = {f for f, seeds in index_seeds.items() if len(seeds) > 1}
    shared |= {f for f, seeds in aob_seeds.items() if len(seeds) > 1}

    groups = []
    for f in sorted(shared):
        idx = index_by_fold.get(f, [])
        ao = aob_by_fold.get(f, [])
        affected = [
            r for r in registry
            if "shared_siglum" in (r["unresolved_class"] or "").split(";")
            and f in (r["siglum_folds"] or "").split(";")
        ]
        groups.append({
            "siglum_fold": f,
            "printed_sigla": sorted({
                (r["abbreviation_siglum"] or "").strip() for r in idx
            } | {
                s.strip() for r in ao for s in (r["sigla"] or "").split(";")
                if fold(s) == f
            }),
            "index_rows": [{
                "locator": f"{r['page']}:{r['row']}",
                "title_iast": r["title_iast"],
                "title_deva": r["title_deva"],
                "nature_deva": r["nature_deva"],
                "qualifier": r["abbreviation_qualifier"],
                "confidence": r["confidence"],
            } for r in idx],
            "aob_claims": [{
                "work_fold": r["work_fold"],
                "sample_title": r["sample_title"],
                "sample_author": r["sample_author"],
                "sigla": r["sigla"],
            } for r in ao],
            "harvest": [{
                "siglum": r["siglum"],
                "count": r["count"],
                "class": r["class"],
                "dcs_title": r["dcs_title"],
                "display_title": r["display_title"],
            } for r in families if fold(r["siglum"]) == f],
            "reconciliation": [{
                "kind": r["kind"],
                "aob_siglum": r["aob_siglum"],
                "aob_title": r["aob_title"],
                "harvest_siglum": r["harvest_siglum"],
                "evidence": r["evidence"],
            } for r in reconciliation if fold(r["aob_siglum"]) == f],
            "registry_records": [{
                "work_id": r["work_id"],
                "label": r["label"],
                "unresolved_class": r["unresolved_class"],
                "provenance": r["provenance"],
            } for r in affected],
        })
    remaining = sum(len(g["registry_records"]) for g in groups)
    diagnostics_path = os.path.join(root, "data/pd/pd_work_registry_diagnostics.json")
    baseline = remaining
    if os.path.exists(diagnostics_path):
        with open(diagnostics_path, encoding="utf-8") as fh:
            adjudication = json.load(fh).get("shared_siglum_adjudication", {})
        baseline = adjudication.get("baseline_shared_siglum_registry_records", remaining)
    return {
        "shared_siglum_folds": len(groups),
        "shared_siglum_registry_records": baseline,
        "shared_siglum_registry_records_remaining": remaining,
        "groups": groups,
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--output")
    args = ap.parse_args(argv)
    payload = json.dumps(review(os.path.abspath(args.root)), ensure_ascii=False, indent=1) + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="") as fh:
            fh.write(payload)
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
