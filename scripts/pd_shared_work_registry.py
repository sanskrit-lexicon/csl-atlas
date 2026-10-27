#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PD shared work-and-edition identity registry (H7296, Q3 ruling).

Builds one registry over the PD printed Index of Works (H6992, 2,031 rows), the
AOB declared-work / edition census (H6707), the H6720 printed-vs-harvested
reconciliation, the PD harvested siglum families, and the PW / PWG bibliographies
(`pd_pwbib_extract.py` output).  The identity rule is deliberately conservative:

* A work is a set of *identity claims*.  An Index claim is keyed by the printed
  siglum plus the printed Devanagari title (`title_deva`), falling back to the
  IAST title only when the Devanagari cell is blank.  Two different printed works
  that share one abbreviation therefore stay separate (the `AVPari.` family), and
  two rows that print the same Devanagari title under one abbreviation collapse.
* Claims are joined across sources by EXACT folded-siglum equality and only when
  that fold names one work in the Index and one work in the AOB census.  A fold
  that names several works in either source is recorded as `shared_siglum` and is
  never used to merge — no skeleton/fuzzy match exists here.
* Work IDs are `PDW-` + sha256(canonical seed)[:10], where the seed is chosen by
  a fixed source priority (Index > AOB > PWG bib > PW bib > harvested family), so
  adding a lower-priority source cannot move an existing ID.
* Nothing is ever titled by this script.  Every label is copied verbatim from a
  source cell and carries `label_kind` / `label_source`; unresolved identity rows
  keep an empty `work_id` and an explicit class.

Validation (Q5 contract): every record is `unvalidated_pending_double_annotation`.
Blank abbreviation cells, `vision-low` rows and one seeded ordinary control stay
visibly unvalidated; no kappa and no adjudication are fabricated.

Outputs (all regenerated, byte-stable):
    data/pd/pd_work_registry.tsv
    data/pd/pd_work_edition_map.tsv
    data/pd/pd_work_registry.json
    data/pd/pd_work_registry_diagnostics.json

Usage:
    python3 scripts/pd_shared_work_registry.py --write
    python3 scripts/pd_shared_work_registry.py --check   # exits 0 only if byte-identical
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import os
import re
import sys
import unicodedata

ROOT_DEFAULT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from dataset_meta import license_fields  # noqa: E402

INDEX = "data/pd/pd_index_works.tsv"
AOB_WORKS = "data/pd/pd_aob_declared_works.tsv"
AOB_ENTRIES = "data/pd/pd_aob_entries.tsv"
FAMILIES = "data/pd/pd_siglum_families.tsv"
RECON = "data/pd/pd_aob_sigla_reconciliation.tsv"
PWG = "data/pd/pd_pwgbib_sigla.tsv"
PW = "data/pd/pd_pwbib_sigla.tsv"

OUT_REGISTRY = "data/pd/pd_work_registry.tsv"
OUT_MAP = "data/pd/pd_work_edition_map.tsv"
OUT_JSON = "data/pd/pd_work_registry.json"
OUT_DIAG = "data/pd/pd_work_registry_diagnostics.json"

REGISTRY_FIELDS = [
    "registry_id", "work_id", "identity_status", "label", "label_kind", "label_source",
    "label_variants", "n_index_rows", "n_index_blank", "n_index_vision_low",
    "n_aob_editions", "n_harvest_sigla", "n_dictionary_sigla", "siglum_folds",
    "validation_state", "sample_role", "unresolved_class", "provenance",
]
MAP_FIELDS = [
    "record_id", "work_id", "related_work_id", "relation", "source", "source_locator",
    "dictionary", "dictionary_siglum", "siglum_fold", "edition_ordinal",
    "n_editions_in_source", "citation_count", "confidence", "validation_state",
    "sample_role", "unresolved_class", "provenance",
]
VALIDATION_STATE = "unvalidated_pending_double_annotation"

SOURCE_PRIORITY = {"index": 0, "aob": 1, "pwg": 2, "pw": 3, "harvest": 4}
RECON_PRIORITY = [
    "join_confirmed_printed_text", "join_miss_siglum_equal", "join_unconfirmed_at_entry",
    "aob_never_cited_near_miss", "aob_never_cited", "aob_fragment_or_garble",
    "junk_ocr", "harvest_not_in_aob",
]


def fold(text):
    """Lossless-for-identity fold: NFKD, strip combining, casefold, trim punctuation."""
    s = unicodedata.normalize("NFKD", text or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.casefold()
    s = re.sub(r"[\s\u00a0]+", " ", s).strip()
    s = s.strip(".,;:()[]{}*")
    s = re.sub(r"\.+$", "", s).strip()
    return s


def digest(text):
    if isinstance(text, bytes):
        return hashlib.sha256(text).hexdigest()
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_tsv(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(fields, rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, delimiter="\t", lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in fields})
    return buf.getvalue()


def work_id_for(seed):
    return "PDW-" + digest(seed)[:10]


def relation_id(seed):
    return "PDR-" + digest(seed)[:10]


def skeleton(siglum):
    """Same consonant skeleton as scripts/pd_mahabha_trap_gate.py (canary only)."""
    s = siglum.rstrip(".")
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    s = s.lower()
    return re.sub(r"[aeiou]", "", s)


class UnionFind:
    def __init__(self):
        self.parent = {}

    def add(self, key):
        self.parent.setdefault(key, key)

    def find(self, key):
        root = key
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[key] != root:
            self.parent[key], key = root, self.parent[key]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            if rb < ra:
                ra, rb = rb, ra
            self.parent[rb] = ra


def build(root):
    index_rows = read_tsv(os.path.join(root, INDEX))
    aob_rows = read_tsv(os.path.join(root, AOB_WORKS))
    fam_rows = read_tsv(os.path.join(root, FAMILIES))
    recon_rows = read_tsv(os.path.join(root, RECON))
    pwg_rows = read_tsv(os.path.join(root, PWG))
    pw_rows = read_tsv(os.path.join(root, PW))

    structural = {fold(r["siglum"]) for r in fam_rows if r.get("class") == "structural"}
    structural |= {"a", "b"}

    claims = {}          # seed -> claim dict
    index_claim_seed = {}  # (page,row) -> seed or None
    map_rows = []
    unresolved_registry = []

    # ---- Index claims -----------------------------------------------------
    for r in index_rows:
        loc = f"{r['page']}:{r['row']}"
        sig = (r["abbreviation_siglum"] or "").strip()
        prov = f"{INDEX}:{loc}"
        base = {
            "source": "pd_index_works", "source_locator": loc, "dictionary": "PD",
            "dictionary_siglum": sig, "siglum_fold": fold(sig) if sig else "",
            "confidence": r.get("confidence", ""), "provenance": prov,
        }
        if not sig:
            index_claim_seed[(r["page"], r["row"])] = None
            unresolved_registry.append({
                "registry_id": "UNRES-" + digest(f"blank:{loc}")[:10],
                "work_id": "", "identity_status": "unresolved",
                "label": (r["title_iast"] or "").strip(),
                "label_kind": "index_title_iast" if (r["title_iast"] or "").strip() else "",
                "label_source": prov, "label_variants": (r["title_iast"] or "").strip(),
                "n_index_rows": "1", "n_index_blank": "1", "n_index_vision_low":
                    "1" if r.get("confidence") == "vision-low" else "0",
                "n_aob_editions": "0", "n_harvest_sigla": "0", "n_dictionary_sigla": "0",
                "siglum_folds": "", "validation_state": VALIDATION_STATE,
                "sample_role": "blank_cell",
                "unresolved_class": "blank_abbreviation_cell",
                "provenance": prov,
            })
            map_rows.append({
                "record_id": relation_id(f"idx:{loc}"), "work_id": "", "related_work_id": "",
                "relation": "unresolved_blank", **base, "edition_ordinal": "1",
                "n_editions_in_source": "1", "citation_count": "",
                "validation_state": VALIDATION_STATE, "sample_role": "blank_cell",
                "unresolved_class": "blank_abbreviation_cell",
            })
            continue

        f = fold(sig)
        if f in structural:
            index_claim_seed[(r["page"], r["row"])] = None
            unresolved_registry.append({
                "registry_id": "UNRES-" + digest(f"structural:{loc}")[:10],
                "work_id": "", "identity_status": "unresolved",
                "label": (r["title_iast"] or "").strip(), "label_kind": "index_title_iast",
                "label_source": prov, "label_variants": (r["title_iast"] or "").strip(),
                "n_index_rows": "1", "n_index_blank": "0", "n_index_vision_low":
                    "1" if r.get("confidence") == "vision-low" else "0",
                "n_aob_editions": "0", "n_harvest_sigla": "0", "n_dictionary_sigla": "0",
                "siglum_folds": f, "validation_state": VALIDATION_STATE, "sample_role": "none",
                "unresolved_class": "structural_siglum", "provenance": prov,
            })
            map_rows.append({
                "record_id": relation_id(f"idx:{loc}"), "work_id": "", "related_work_id": "",
                "relation": "unresolved_structural", **base, "edition_ordinal": "1",
                "n_editions_in_source": "1", "citation_count": "",
                "validation_state": VALIDATION_STATE, "sample_role": "none",
                "unresolved_class": "structural_siglum",
            })
            continue

        title_deva = (r["title_deva"] or "").strip()
        title_iast = (r["title_iast"] or "").strip()
        title_key = fold(title_deva) or fold(title_iast) or f
        seed = f"IDX:{f}:{title_key}"
        index_claim_seed[(r["page"], r["row"])] = seed
        c = claims.setdefault(seed, {
            "seed": seed, "source": "index", "siglum_fold": f, "raw_sigla": set(),
            "rows": [], "editions": [], "bib": [], "harvest": [],
        })
        c["raw_sigla"].add(sig)
        c["rows"].append({
            "loc": loc, "siglum": sig, "confidence": r.get("confidence", ""),
            "title_iast": title_iast, "title_deva": title_deva,
            "nature_deva": (r["nature_deva"] or "").strip(), "prov": prov,
        })

    # ---- AOB declared works / editions ------------------------------------
    aob_claim_by_fold = collections.defaultdict(list)
    for r in aob_rows:
        seed = "AOB:" + fold(r["work_fold"])
        sigla = [s.strip() for s in (r["sigla"] or "").split(";") if s.strip()]
        c = claims.setdefault(seed, {
            "seed": seed, "source": "aob", "siglum_fold": fold(sigla[0]) if sigla else "",
            "raw_sigla": set(), "rows": [], "editions": [], "bib": [], "harvest": [],
            "aob_title": (r.get("sample_title") or "").strip(),
            "aob_author": (r.get("sample_author") or "").strip(),
            "aob_fold": r["work_fold"],
        })
        for i, sig in enumerate(sigla, 1):
            c["raw_sigla"].add(sig)
            c["editions"].append({"ordinal": i, "siglum": sig, "fold": fold(sig)})
            aob_claim_by_fold[fold(sig)].append(seed)

    index_folds = {c["siglum_fold"] for c in claims.values() if c["source"] == "index"}
    aob_folds = set(aob_claim_by_fold)
    index_fold_claims = collections.defaultdict(list)
    for c in claims.values():
        if c["source"] == "index":
            index_fold_claims[c["siglum_fold"]].append(c["seed"])

    shared_folds = set()
    for f, seeds in index_fold_claims.items():
        if len(seeds) > 1:
            shared_folds.add(f)
    for f, seeds in aob_claim_by_fold.items():
        if len(seeds) > 1:
            shared_folds.add(f)

    # ---- PW / PWG bibliography claims (PD-scoped, title-evidenced) ---------
    # A bibliography siglum is attached to a work only when the bibliography's
    # own reference string contains that work's sourced title (or vice versa).
    # Siglum equality alone is NOT enough: PWG prints `MAHĀBH.` for the epic
    # while PD prints `MahāBh.` for the Mahābhāṣya, and those two folds collide.
    def compact(text):
        return re.sub(r"[^a-z0-9]+", "", fold(text))

    title_seeds = collections.defaultdict(set)
    for seed, c in claims.items():
        if c["source"] == "index":
            for row in c["rows"]:
                t = compact(row["title_iast"])
                if len(t) >= 4:
                    title_seeds[t].add(seed)
        elif c["source"] == "aob":
            t = compact(c.get("aob_title", ""))
            if len(t) >= 4:
                title_seeds[t].add(seed)

    bib_unlinked = collections.Counter()
    for dictionary, rows in (("pwg", pwg_rows), ("pw", pw_rows)):
        for r in rows:
            sig = (r["siglum"] or "").strip()
            f = fold(sig)
            ref_raw = (r["reference"] or "").strip()
            ref = compact(ref_raw)
            lead = compact(re.split(r"[,;]", ref_raw)[0]) if ref_raw else ""
            if not f or len(ref) < 4:
                bib_unlinked[dictionary] += 1
                continue
            cands = set()
            for t, seeds in title_seeds.items():
                if t in ref or (len(lead) >= 4 and lead in t):
                    cands |= seeds
            if len(cands) != 1:
                bib_unlinked[dictionary + ("_ambiguous" if cands else "_no_title")] += 1
                continue
            target = next(iter(cands))
            seed = f"BIB:{dictionary.upper()}:{f}:{compact(ref[:40])}"
            c = claims.setdefault(seed, {
                "seed": seed, "source": dictionary, "siglum_fold": f, "raw_sigla": set(),
                "rows": [], "editions": [], "bib": [], "harvest": [], "pinned_to": target,
            })
            c["raw_sigla"].add(sig)
            c["bib"].append({
                "siglum": sig, "reference": ref_raw,
                "line": r.get("source_line", ""), "dictionary": dictionary.upper(),
            })

    # ---- harvested siglum families (attestation evidence only) ------------
    harvest_unlinked = 0
    for r in fam_rows:
        sig = (r["siglum"] or "").strip()
        f = fold(sig)
        if not f or (f not in index_folds and f not in aob_folds):
            harvest_unlinked += 1
            continue
        if f in shared_folds:
            harvest_unlinked += 1
            continue
        if (r.get("class") or "") == "structural":
            continue
        seed = f"HARV:{f}"
        c = claims.setdefault(seed, {
            "seed": seed, "source": "harvest", "siglum_fold": f, "raw_sigla": set(),
            "rows": [], "editions": [], "bib": [], "harvest": [],
        })
        c["raw_sigla"].add(sig)
        c["harvest"].append({
            "siglum": sig, "count": (r.get("count") or "").strip(),
            "class": (r.get("class") or "").strip(),
            "dcs_title": (r.get("dcs_title") or "").strip(),
            "display_title": (r.get("display_title") or "").strip(),
        })

    # ---- union by exact fold, refused on any shared fold ------------------
    uf = UnionFind()
    for seed in claims:
        uf.add(seed)
    by_fold = collections.defaultdict(list)
    for seed, c in claims.items():
        by_fold[c["siglum_fold"]].append(seed)
    for f, seeds in by_fold.items():
        if f in shared_folds or len(seeds) < 2:
            continue
        seeds = [s for s in seeds if not claims[s].get("pinned_to")]
        for other in seeds[1:]:
            uf.union(seeds[0], other)
    for seed, c in claims.items():
        if c.get("pinned_to"):
            uf.union(seed, c["pinned_to"])

    components = collections.defaultdict(list)
    for seed in claims:
        components[uf.find(seed)].append(seed)

    # ---- seeded ordinary control (Q5) -------------------------------------
    ordinary = [
        r for r in index_rows
        if (r.get("confidence") == "vision" and (r["abbreviation_siglum"] or "").strip()
            and fold(r["abbreviation_siglum"]) not in structural)
    ]
    control_row = min(
        ordinary,
        key=lambda r: digest(f"H7296-control|{r['page']}|{r['row']}"),
    ) if ordinary else None
    control_loc = f"{control_row['page']}:{control_row['row']}" if control_row else ""

    recon_best = collections.defaultdict(str)
    for r in recon_rows:
        f = fold(r.get("aob_siglum", ""))
        kind = r.get("kind", "")
        if not f or not kind:
            continue
        cur = recon_best[f]
        if not cur or (kind in RECON_PRIORITY and RECON_PRIORITY.index(kind)
                       < (RECON_PRIORITY.index(cur) if cur in RECON_PRIORITY else 99)):
            recon_best[f] = kind

    registry_rows = []
    rel_rows = []
    work_of_seed = {}

    for root_seed, seeds in sorted(components.items()):
        canonical = min(seeds, key=lambda s: (SOURCE_PRIORITY[claims[s]["source"]], s))
        wid = work_id_for(canonical)
        for s in seeds:
            work_of_seed[s] = wid

        members = [claims[s] for s in seeds]
        idx_members = [c for c in members if c["source"] == "index"]
        aob_members = [c for c in members if c["source"] == "aob"]
        bib_members = [c for c in members if c["source"] in ("pwg", "pw")]
        harv_members = [c for c in members if c["source"] == "harvest"]

        label = label_kind = label_source = ""
        variants = []
        for c in idx_members:
            for row in c["rows"]:
                if row["title_iast"]:
                    variants.append(row["title_iast"])
            first = c["rows"][0]
            if first["title_iast"]:
                label, label_kind = first["title_iast"], "index_title_iast"
                label_source = first["prov"]
                break
        if not label and aob_members:
            a = aob_members[0]
            if a.get("aob_title"):
                label = a["aob_title"]
                label_kind = "aob_declared_sample_title"
                label_source = f"{AOB_WORKS}:{a['aob_fold']}"
        if not label and bib_members:
            b = sorted(bib_members, key=lambda c: (SOURCE_PRIORITY[c["source"]], c["seed"]))[0]
            if b["bib"] and b["bib"][0]["reference"]:
                label = b["bib"][0]["reference"]
                label_kind = "bibliography_reference"
                label_source = f"{PWG if b['source'] == 'pwg' else PW}:{b['bib'][0]['line']}"
        if not label and harv_members:
            hv = harv_members[0]["harvest"][0]
            title = hv["dcs_title"] or hv["display_title"]
            if title:
                label = title
                label_kind = "harvest_dcs_title"
                label_source = f"{FAMILIES}:{hv['siglum']}"

        index_rows_n = sum(len(c["rows"]) for c in idx_members)
        blank_n = 0
        vision_low_n = sum(1 for c in idx_members for r in c["rows"] if r["confidence"] == "vision-low")
        aob_ed_n = sum(len(c["editions"]) for c in aob_members)
        harv_n = sum(len(c["harvest"]) for c in harv_members)
        dict_sigla = sum(len(c["raw_sigla"]) for c in members)
        folds = sorted({c["siglum_fold"] for c in members if c["siglum_fold"]})
        prov = sorted({r["prov"] for c in idx_members for r in c["rows"]}
                      | {f"{AOB_WORKS}:{c['aob_fold']}" for c in aob_members}
                      | {f"{PWG if c['source'] == 'pwg' else PW}:{b['line']}"
                         for c in bib_members for b in c["bib"]}
                      | {f"{FAMILIES}:{h['siglum']}" for c in harv_members for h in c["harvest"]})

        unresolved = set()
        if any(f in shared_folds for f in folds):
            unresolved.add("shared_siglum")
        for c in aob_members:
            kinds = [recon_best.get(e["fold"], "") for e in c["editions"]]
            kinds = [k for k in kinds if k]
            if kinds:
                best = min(kinds, key=lambda k: RECON_PRIORITY.index(k)
                           if k in RECON_PRIORITY else 99)
                if best != "join_confirmed_printed_text":
                    unresolved.add("aob_join_" + best)

        role = "none"
        if any(r["loc"] == control_loc for c in idx_members for r in c["rows"]):
            role = "seeded_ordinary_control"
        elif any(r["confidence"] == "vision-low" for c in idx_members for r in c["rows"]):
            role = "vision_low"

        registry_rows.append({
            "registry_id": wid, "work_id": wid, "identity_status": "resolved",
            "label": label, "label_kind": label_kind, "label_source": label_source,
            "label_variants": ";".join(sorted(set(variants))),
            "n_index_rows": str(index_rows_n), "n_index_blank": str(blank_n),
            "n_index_vision_low": str(vision_low_n),
            "n_aob_editions": str(aob_ed_n), "n_harvest_sigla": str(harv_n),
            "n_dictionary_sigla": str(dict_sigla),
            "siglum_folds": ";".join(folds),
            "validation_state": VALIDATION_STATE, "sample_role": role,
            "unresolved_class": ";".join(sorted(unresolved)),
            "provenance": ";".join(prov),
        })

        # map rows: Index
        for c in idx_members:
            for row in c["rows"]:
                is_control = row["loc"] == control_loc
                is_low = row["confidence"] == "vision-low"
                row_role = ("seeded_ordinary_control" if is_control
                            else "vision_low" if is_low else "none")
                map_rows.append({
                    "record_id": relation_id(f"idx:{row['loc']}"), "work_id": wid,
                    "related_work_id": "", "relation": "primary_work",
                    "source": "pd_index_works", "source_locator": row["loc"],
                    "dictionary": "PD", "dictionary_siglum": row["siglum"],
                    "siglum_fold": c["siglum_fold"], "edition_ordinal": "1",
                    "n_editions_in_source": "1", "citation_count": "",
                    "confidence": row["confidence"], "validation_state": VALIDATION_STATE,
                    "sample_role": row_role,
                    "unresolved_class": "shared_siglum" if c["siglum_fold"] in shared_folds else "",
                    "provenance": row["prov"],
                })
        # map rows: AOB editions
        for c in aob_members:
            for e in c["editions"]:
                map_rows.append({
                    "record_id": relation_id(f"aob:{c['aob_fold']}:{e['ordinal']}"),
                    "work_id": wid, "related_work_id": "", "relation": "edition_of_declared_work",
                    "source": "pd_aob_declared_works", "source_locator": f"{c['aob_fold']}:{e['ordinal']}",
                    "dictionary": "AOB", "dictionary_siglum": e["siglum"],
                    "siglum_fold": e["fold"], "edition_ordinal": str(e["ordinal"]),
                    "n_editions_in_source": str(len(c["editions"])), "citation_count": "",
                    "confidence": "", "validation_state": VALIDATION_STATE,
                    "sample_role": "none",
                    "unresolved_class": "shared_siglum" if e["fold"] in shared_folds else "",
                    "provenance": f"{AOB_WORKS}:{c['aob_fold']}",
                })
        # map rows: bibliography identity
        for c in bib_members:
            for b in c["bib"]:
                map_rows.append({
                    "record_id": relation_id(f"bib:{b['dictionary']}:{b['siglum']}"),
                    "work_id": wid, "related_work_id": "", "relation": "bibliography_identity",
                    "source": PWG if c["source"] == "pwg" else PW,
                    "source_locator": b["line"], "dictionary": b["dictionary"],
                    "dictionary_siglum": b["siglum"], "siglum_fold": c["siglum_fold"],
                    "edition_ordinal": "", "n_editions_in_source": "", "citation_count": "",
                    "confidence": "", "validation_state": VALIDATION_STATE,
                    "sample_role": "none", "unresolved_class": "",
                    "provenance": f"{PWG if c['source'] == 'pwg' else PW}:{b['line']}",
                })
        # map rows: harvested attestation
        for c in harv_members:
            for h in c["harvest"]:
                map_rows.append({
                    "record_id": relation_id(f"harv:{h['siglum']}"), "work_id": wid,
                    "related_work_id": "", "relation": "harvest_attestation",
                    "source": FAMILIES, "source_locator": h["siglum"], "dictionary": "PD-harvest",
                    "dictionary_siglum": h["siglum"], "siglum_fold": c["siglum_fold"],
                    "edition_ordinal": "", "n_editions_in_source": "",
                    "citation_count": h["count"], "confidence": "",
                    "validation_state": VALIDATION_STATE, "sample_role": "none",
                    "unresolved_class": "", "provenance": f"{FAMILIES}:{h['siglum']}",
                })

    # ---- commentary relations (sourced from the printed nature cell) ------
    index_title_to_work = collections.defaultdict(list)
    for c in claims.values():
        if c["source"] != "index":
            continue
        wid = work_of_seed[c["seed"]]
        for row in c["rows"]:
            if row["title_deva"]:
                index_title_to_work[row["title_deva"]].append(wid)
            if row["title_iast"]:
                index_title_to_work[row["title_iast"]].append(wid)
    commentary = []
    for c in claims.values():
        if c["source"] != "index":
            continue
        wid = work_of_seed[c["seed"]]
        for row in c["rows"]:
            m = re.match(r"^comm\. on\s+(.+)$", row["nature_deva"], re.I)
            if not m:
                continue
            base = m.group(1).strip()
            targets = sorted({w for w in index_title_to_work.get(base, []) if w != wid})
            rel_rows.append({
                "record_id": relation_id(f"comm:{row['loc']}"), "work_id": wid,
                "related_work_id": targets[0] if targets else "", "relation": "commentary_on",
                "source": "pd_index_works", "source_locator": row["loc"], "dictionary": "PD",
                "dictionary_siglum": sorted(c["raw_sigla"])[0], "siglum_fold": c["siglum_fold"],
                "edition_ordinal": "", "n_editions_in_source": "", "citation_count": "",
                "confidence": row["confidence"], "validation_state": VALIDATION_STATE,
                "sample_role": "none",
                "unresolved_class": "" if targets else "commentary_base_unresolved",
                "provenance": row["prov"],
            })
            commentary.append({
                "siglum": sorted(c["raw_sigla"])[0], "work_id": wid,
                "related_work_id": targets[0] if targets else "",
                "base_candidates": len(targets), "base": base,
            })
    map_rows.extend(rel_rows)

    # ---- counts and canaries ----------------------------------------------
    index_blank = sum(1 for r in index_rows if not (r["abbreviation_siglum"] or "").strip())
    index_low = sum(1 for r in index_rows if r.get("confidence") == "vision-low")
    map_rows = sorted(map_rows, key=lambda r: (r["work_id"] or "zzz", r["source"], r["record_id"]))
    registry_rows = sorted(registry_rows, key=lambda r: r["work_id"])
    unresolved_registry = sorted(unresolved_registry, key=lambda r: r["registry_id"])

    def wid_of_siglum(sig):
        f = fold(sig)
        seeds = [s for s in claims if claims[s]["siglum_fold"] == f]
        if not seeds:
            return ""
        wids = {work_of_seed[s] for s in seeds}
        return wids.pop() if len(wids) == 1 else ""

    mahabha = wid_of_siglum("MahāBhā.")
    mahabh = wid_of_siglum("MahāBh.")
    mahabha_canary = {
        "epic_siglum": "MahāBhā.", "epic_work_id": mahabha,
        "grammar_siglum": "MahāBh.", "grammar_work_id": mahabh,
        "distinct": bool(mahabha and mahabh and mahabha != mahabh),
        "merged": bool(mahabha and mahabh and mahabha == mahabh),
    }

    near = []
    for r in recon_rows:
        if r.get("kind") != "aob_never_cited_near_miss":
            continue
        partner = (r.get("harvest_siglum") or "").strip()
        if not partner:
            m = re.search(r"nearest harvested siglum '([^']+)'", r.get("evidence", ""))
            partner = m.group(1) if m else ""
        if partner:
            near.append((r.get("aob_siglum", ""), partner))
    near_merged, near_skeleton = 0, 0
    for a_sig, b_sig in near:
        a, b = fold(a_sig), fold(b_sig)
        if a == b:
            near_merged += 1
        if skeleton(a_sig) == skeleton(b_sig):
            near_skeleton += 1
        wa, wb = wid_of_siglum(a_sig), wid_of_siglum(b_sig)
        if wa and wa == wb:
            near_merged += 1
    near_canary = {
        "pairs": len(near), "skeleton_collisions": near_skeleton,
        "merged": near_merged, "distinct": near_merged == 0,
    }

    repeated = []
    for wid in sorted({r["work_id"] for r in map_rows
                       if r["source"] == "pd_aob_declared_works"}):
        eds = [r for r in map_rows if r["source"] == "pd_aob_declared_works"
               and r["work_id"] == wid]
        if len(eds) > 1:
            repeated.append({
                "work_id": wid, "editions": len(eds),
                "sigla": sorted({e["dictionary_siglum"] for e in eds}),
                "one_work": len({e["work_id"] for e in eds}) == 1,
            })
    repeated_canary = {
        "works": len(repeated), "rows": sum(x["editions"] for x in repeated),
        "all_one_work": all(x["one_work"] for x in repeated),
        "examples": repeated[:3],
    }

    ama = [x for x in commentary if x["siglum"].startswith("AmaKoUd")]
    ama_canary = {
        "siglum": "AmaKoUd.", "found": bool(ama),
        "relation": "commentary_on",
        "own_work_id": ama[0]["work_id"] if ama else "",
        "base_work_id": ama[0]["related_work_id"] if ama else "",
        "is_relation_not_merge": bool(ama and ama[0]["related_work_id"]
                                      and ama[0]["work_id"] != ama[0]["related_work_id"]),
        "base_candidates": ama[0]["base_candidates"] if ama else 0,
    }

    canaries = {
        "mahabha_homograph": mahabha_canary,
        "near_homograph": near_canary,
        "repeated_editions": repeated_canary,
        "commentary_inherited_siglum": ama_canary,
        "blank_and_vision_low_preserved": {
            "index_rows": len(index_rows), "blank_cells": index_blank,
            "vision_low_rows": index_low,
            "blank_expected": 409, "vision_low_expected": 434,
            "pass": index_blank == 409 and index_low == 434 and len(index_rows) == 2031,
        },
        "validation_contract": {
            "kappa": None, "kappa_status": "not_measured_no_double_annotation",
            "adjudicated_rows": 0,
            "control_row": control_loc,
            "all_unvalidated": all(r["validation_state"] == VALIDATION_STATE
                                   for r in registry_rows + map_rows + unresolved_registry),
        },
    }
    canaries["all_pass"] = bool(
        mahabha_canary["distinct"] and not mahabha_canary["merged"]
        and near_canary["distinct"] and repeated_canary["all_one_work"]
        and ama_canary["is_relation_not_merge"]
        and canaries["blank_and_vision_low_preserved"]["pass"]
        and canaries["validation_contract"]["all_unvalidated"]
    )

    unresolved_counts = collections.Counter()
    for r in registry_rows + unresolved_registry:
        for cls in (r["unresolved_class"] or "").split(";"):
            if cls:
                unresolved_counts[cls] += 1

    diagnostics = {
        "schema_version": "1.0",
        "generated_by": "scripts/pd_shared_work_registry.py",
        "handoff": "H7296",
        "identity_rule": {
            "index_claim_key": "folded printed siglum + folded printed Devanagari title "
                               "(IAST fallback when the Devanagari cell is blank)",
            "cross_source_join": "exact folded-siglum equality, refused when the fold names "
                                 "more than one work in the Index or in the AOB declared canon",
            "no_fuzzy_matching": True,
            "work_id": "PDW- + sha256(canonical seed)[:10]; seed priority "
                       "Index > AOB > PWG bib > PW bib > harvested",
            "labels": "verbatim source cells only; never generated",
        },
        "inputs": [
            {"path": p, "sha256": digest(open(os.path.join(root, p), "rb").read()),
             "rows": sum(1 for _ in csv.DictReader(open(os.path.join(root, p),
                                                        encoding="utf-8", newline=""),
                                                   delimiter="\t"))}
            for p in (INDEX, AOB_WORKS, FAMILIES, RECON, PWG, PW)
        ],
        "counts": {
            "index_rows": len(index_rows),
            "index_blank_abbreviation_cells": index_blank,
            "index_vision_rows": sum(1 for r in index_rows if r.get("confidence") == "vision"),
            "index_vision_low_rows": index_low,
            "aob_declared_works": len(aob_rows),
            "aob_editions": sum(len(c["editions"]) for c in claims.values()
                                if c["source"] == "aob"),
            "pwgbib_sigla": len(pwg_rows),
            "pwbib_sigla": len(pw_rows),
            "works": len(registry_rows),
            "unresolved_registry_rows": len(unresolved_registry),
            "edition_map_rows": len(map_rows),
            "shared_siglum_folds": len(shared_folds),
            "bib_sigla_out_of_pd_scope": dict(bib_unlinked),
            "harvest_sigla_out_of_pd_scope": harvest_unlinked,
        },
        "works_by_label_kind": dict(collections.Counter(
            r["label_kind"] for r in registry_rows)),
        "unresolved_classes": dict(sorted(unresolved_counts.items())),
        "validation": {
            "state": VALIDATION_STATE,
            "kappa": None,
            "kappa_status": "not_measured_no_double_annotation",
            "adjudicated_rows": 0,
            "sample_roles": dict(collections.Counter(
                r["sample_role"] for r in map_rows if r["sample_role"] != "none")),
            "blank_cells": index_blank,
            "vision_low_rows": index_low,
            "seeded_ordinary_control": control_loc,
        },
        "canaries": canaries,
        "preliminary_figures": {
            "figures": ["3.11%", "4.03%", "breadth/depth headline bands"],
            "status": "preliminary_until_rerun",
            "rerun_in_this_unit": False,
            "note": "This unit builds identity only; it does not rerun coverage, "
                    "breadth/depth or effective-coverage claims.",
        },
    }

    payload = {
        "data/pd/pd_work_registry.tsv": write_tsv(REGISTRY_FIELDS,
                                                  registry_rows + unresolved_registry),
        "data/pd/pd_work_edition_map.tsv": write_tsv(MAP_FIELDS, map_rows),
        "data/pd/pd_work_registry.json": json.dumps({
            **license_fields(),
            "schema_version": "1.0", "handoff": "H7296",
            "works": registry_rows, "unresolved": unresolved_registry,
            "counts": diagnostics["counts"],
        }, ensure_ascii=False, indent=1) + "\n",
        "data/pd/pd_work_registry_diagnostics.json": json.dumps(
            {**license_fields(), **diagnostics}, ensure_ascii=False, indent=1) + "\n",
    }
    return payload, diagnostics


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    args = ap.parse_args(argv)
    root = os.path.abspath(args.root)

    payload, diag = build(root)

    if not diag["canaries"]["all_pass"]:
        print("STOP_CANARY_MISMATCH", file=sys.stderr)
        print(json.dumps(diag["canaries"], ensure_ascii=False, indent=1), file=sys.stderr)
        return 2

    rc = 0
    for rel, text in payload.items():
        path = os.path.join(root, rel)
        if args.check:
            try:
                with open(path, encoding="utf-8", newline="") as fh:
                    on_disk = fh.read()
            except FileNotFoundError:
                print(f"CHECK FAIL: missing {rel}", file=sys.stderr)
                rc = 1
                continue
            if on_disk != text:
                for i, (a, b) in enumerate(zip(on_disk.splitlines(), text.splitlines()), 1):
                    if a != b:
                        print(f"CHECK FAIL: {rel}:{i} differs", file=sys.stderr)
                        print(f"  on disk: {a[:160]}", file=sys.stderr)
                        print(f"  rebuilt: {b[:160]}", file=sys.stderr)
                        break
                else:
                    print(f"CHECK FAIL: {rel}: line count differs "
                          f"({len(on_disk.splitlines())} vs {len(text.splitlines())})",
                          file=sys.stderr)
                rc = 1
            else:
                print(f"OK {rel}: {len(text.splitlines()) - 1} rows")
        elif args.write:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(text)
            print(f"wrote {rel}: {len(text.splitlines()) - 1} rows")
    if not args.check and not args.write:
        print(json.dumps(diag["counts"], ensure_ascii=False, indent=1))
    return rc


if __name__ == "__main__":
    sys.exit(main())
