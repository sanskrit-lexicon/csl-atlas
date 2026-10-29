#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C1 — PD edition availability weighted by the H6949 attestation unit.

Rebuilds per-siglum counts from the read-only PDScan text, then joins only
committed or explicitly curated evidence. Work-level e-text availability and
identity of the exact AOB edition are separate measures. Unprobed is never
counted as absent.

    python scripts/pd_edition_availability.py --pd /path/to/pd.txt
    python scripts/pd_edition_availability.py --check --pd /path/to/pd.txt
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "scripts", "lib"))
import pd_quotation_units as pqu  # noqa: E402
import quotation_units  # noqa: E402

DATA = os.path.join(ROOT, "data", "pd")
OUT_TSV = os.path.join(DATA, "pd_edition_availability_by_siglum.tsv")
OUT_AOB_TSV = os.path.join(DATA, "pd_edition_availability_by_aob.tsv")
OUT_JSON = os.path.join(DATA, "pd_edition_availability_summary.json")
REPORT = os.path.join(ROOT, "reports", "PD_EDITION_AVAILABILITY_C1_2026-10-29.md")
EVIDENCE = os.path.join(DATA, "pd_edition_availability_evidence.tsv")
TOTALS = {"attestations": 419890, "loci": 384217, "continuations": 35673}
AVAILABLE = {"available_full", "available_partial", "available_embedded"}
STATUSES = AVAILABLE | {"unavailable_verified", "unresolved"}
COLUMNS = [
    "siglum", "attestations", "siglum_loci", "continuation_loci", "class",
    "work_id", "work_title", "aob_entry_ids", "aob_titles", "availability",
    "source", "edition_identity", "evidence_ref", "notes",
]
AOB_COLUMNS = [
    "entry_id", "siglum", "title", "year", "attestations_direct",
    "available_full", "available_partial", "available_embedded", "unresolved",
    "availability", "sources", "shared_raw_siglum",
]


def read_tsv(name):
    with open(os.path.join(DATA, name), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def citation_tail_detailed(tail):
    """H6949 counts, with every continuation assigned to its preceding siglum."""
    tail = tail.split("{@", 1)[0]
    plain = pqu.RE_ITAL.sub(" ", pqu.RE_TAG.sub(" ", tail))
    tokens = []
    previous = None
    loci = continuations = 0
    for seg in plain.split(";"):
        hits = pqu.sigla_in(seg)
        if hits:
            tokens.extend(hits)
            previous = hits[-1]
            loci += len(hits)
        elif seg.strip() and re.search(r"\d", seg):
            tokens.append(previous or "__UNASSIGNED_CONTINUATION__")
            continuations += 1
    return loci, continuations, tokens


def attestation_counts(pd_path):
    counts = collections.Counter()
    loci = continuations = 0
    for _hdr, body in pqu.iter_entries(pd_path):
        text = " ".join(body).replace('<div n="lb">', " ")
        units = quotation_units.count_units(text, citation_tail_detailed)
        counts.update(units["tokens"])
        loci += units["loci"]
        continuations += units["continuation_loci"]
    return counts, loci, continuations


def load_context():
    families = {r["siglum"]: r for r in read_tsv("pd_siglum_families.tsv")}
    crosswalk = {r["dcs_title"]: r for r in read_tsv("pd_dcs_text_crosswalk.tsv")}
    registry = {r["work_id"]: r for r in read_tsv("pd_work_registry.tsv") if r["work_id"]}
    index_title_candidates = collections.defaultdict(set)
    for r in read_tsv("pd_index_works.tsv"):
        if r["abbreviation_siglum"] and r["title_iast"]:
            index_title_candidates[r["abbreviation_siglum"]].add(r["title_iast"])
    index_titles = {s: next(iter(titles)) for s, titles in index_title_candidates.items()
                    if len(titles) == 1}
    edition_map = read_tsv("pd_work_edition_map.tsv")
    siglum_work_candidates = collections.defaultdict(set)
    work_sigla = collections.defaultdict(set)
    for r in edition_map:
        if r["relation"] == "harvest_attestation":
            siglum_work_candidates[r["dictionary_siglum"]].add(r["work_id"])
            work_sigla[r["work_id"]].add(r["dictionary_siglum"])
    # A shared siglum has no safe work-level title or evidence propagation target.
    siglum_work = {s: next(iter(ids)) for s, ids in siglum_work_candidates.items() if len(ids) == 1}
    aob = collections.defaultdict(list)
    for r in read_tsv("pd_aob_declared_entries.tsv"):
        for siglum in r["harvested_sigla"].split(";"):
            if siglum:
                aob[siglum].append(r)
    return families, crosswalk, registry, index_titles, siglum_work, work_sigla, aob


def curated_evidence():
    rows = read_tsv("pd_edition_availability_evidence.tsv")
    for r in rows:
        if r["availability"] not in STATUSES:
            raise ValueError(f"bad availability for {r['siglum']}: {r['availability']}")
        if not r["source"] or not r["evidence_ref"]:
            raise ValueError(f"incomplete evidence for {r['siglum']}")
        if r["edition_identity"] not in {"work_level", "aob_exact", "different_edition", "unverified"}:
            raise ValueError(f"bad edition identity for {r['siglum']}")
    return rows


def project_aob(rows, aob):
    """Project raw-siglum evidence onto every AOB row without merging shared sigla."""
    by_siglum = {r["siglum"]: r for r in rows}
    projected = []
    for entry in read_tsv("pd_aob_declared_entries.tsv"):
        raw_sigla = [s for s in entry["harvested_sigla"].split(";") if s]
        selected = [by_siglum[s] for s in raw_sigla if s in by_siglum]
        rec = {key: "" for key in AOB_COLUMNS}
        rec.update({key: entry[key] for key in ("entry_id", "siglum", "title", "year")})
        rec["attestations_direct"] = sum(r["attestations"] for r in selected)
        for status in (*AVAILABLE, "unresolved"):
            rec[status] = sum(r["attestations"] for r in selected if r["availability"] == status)
        shared = bool(rec["attestations_direct"]) and any(len(aob[s]) > 1 for s in raw_sigla)
        available = sum(rec[status] for status in AVAILABLE)
        if shared:
            rec["availability"] = "ambiguous_shared_siglum"
        elif not available:
            rec["availability"] = "unresolved"
        elif not rec["unresolved"] and not rec["available_partial"] and not rec["available_embedded"]:
            rec["availability"] = "available_full"
        else:
            rec["availability"] = "available_partial"
        rec["sources"] = ";".join(sorted({r["source"] for r in selected if r["source"]}))
        rec["shared_raw_siglum"] = "yes" if shared else "no"
        projected.append(rec)
    return projected


def build(pd_path):
    counts, total_loci, total_continuations = attestation_counts(pd_path)
    families, crosswalk, registry, index_titles, siglum_work, work_sigla, aob = load_context()

    # H7298 supplies hand-checked work-level GRETIL evidence for the named residue.
    residue = read_tsv("pd_residue_source_status.tsv")
    evidence_by_siglum = {}
    for r in residue:
        status = r["gretil_status"]
        if status in {"full", "partial", "embedded"}:
            availability = "available_" + status
            record = (availability, "GRETIL", "work_level", r["gretil_evidence"], r["notes"])
        elif status == "absent":
            record = ("unresolved", "DCS+GRETIL", "unverified",
                      r["gretil_evidence"], "absent in DCS/GRETIL; archive.org not probed")
        else:
            continue
        work_id = siglum_work.get(r["siglum"], "")
        targets = work_sigla.get(work_id, {r["siglum"]})
        for siglum in targets:
            evidence_by_siglum[siglum] = record

    for r in curated_evidence():
        record = (r["availability"], r["source"], r["edition_identity"],
                  r["evidence_ref"], r["notes"])
        work_id = r["work_id"] or siglum_work.get(r["siglum"], "")
        targets = work_sigla.get(work_id, {r["siglum"]}) if work_id else {r["siglum"]}
        for siglum in targets:
            evidence_by_siglum[siglum] = record

    rows = []
    for siglum, attestations in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        family = families.get(siglum, {})
        family_class = family.get("class", "unclassified")
        work_id = siglum_work.get(siglum, "") if family_class == "primary" else ""
        aob_rows = aob.get(siglum, [])
        aob_titles = []
        for r in aob_rows:
            if r["title"] not in aob_titles:
                aob_titles.append(r["title"])
        work_title = (index_titles.get(siglum)
                      or (aob_titles[0] if len(aob_titles) == 1 else "")
                      or registry.get(work_id, {}).get("label", ""))
        source = edition_identity = evidence_ref = notes = ""
        availability = "unresolved"
        if family.get("match_type") == "covered":
            grade = crosswalk.get(family.get("dcs_title", ""), {}).get("coverage_grade", "")
            availability = "available_partial" if grade.startswith("partial") else "available_full"
            source = "DCS"
            edition_identity = "work_level"
            evidence_ref = "data/pd/pd_dcs_text_crosswalk.tsv:" + family.get("dcs_title", "")
            notes = grade
        elif siglum in evidence_by_siglum:
            availability, source, edition_identity, evidence_ref, notes = evidence_by_siglum[siglum]
        continuation_loci = 0  # filled below from the locus/continuation split pass
        rows.append({
            "siglum": siglum,
            "attestations": attestations,
            "siglum_loci": 0,
            "continuation_loci": continuation_loci,
            "class": family.get("class", "unclassified"),
            "work_id": work_id,
            "work_title": work_title,
            "aob_entry_ids": ";".join(r["entry_id"] for r in aob_rows),
            "aob_titles": ";".join(aob_titles),
            "availability": availability,
            "source": source,
            "edition_identity": edition_identity,
            "evidence_ref": evidence_ref,
            "notes": notes,
        })

    # A second, cheap parser pass preserves the exact per-siglum locus/continuation split.
    locus_counts = collections.Counter()
    continuation_counts = collections.Counter()

    def marker(tail):
        n_loci, n_cont, tokens = citation_tail_detailed(tail)
        if n_loci:  # count_units ignores continuation-only non-quotation tails too
            for token in tokens[:n_loci]:
                locus_counts[token] += 1
            for token in tokens[n_loci:]:
                continuation_counts[token] += 1
        return n_loci, n_cont, []

    for _hdr, body in pqu.iter_entries(pd_path):
        quotation_units.count_units(" ".join(body).replace('<div n="lb">', " "), marker)
    for r in rows:
        r["siglum_loci"] = locus_counts[r["siglum"]]
        r["continuation_loci"] = continuation_counts[r["siglum"]]

    assert sum(r["attestations"] for r in rows) == TOTALS["attestations"]
    assert sum(r["siglum_loci"] for r in rows) == TOTALS["loci"] == total_loci
    assert sum(r["continuation_loci"] for r in rows) == TOTALS["continuations"] == total_continuations
    assert all(r["attestations"] == r["siglum_loci"] + r["continuation_loci"] for r in rows)
    aob_projection = project_aob(rows, aob)

    def mass(predicate):
        return sum(r["attestations"] for r in rows if predicate(r))

    by_status = {}
    for status in sorted(STATUSES):
        selected = [r for r in rows if r["availability"] == status]
        by_status[status] = {
            "sigla": len(selected),
            "attestations": sum(r["attestations"] for r in selected),
            "pct": round(100 * sum(r["attestations"] for r in selected) / TOTALS["attestations"], 4),
        }
    by_source = {}
    for source in sorted({r["source"] for r in rows if r["source"]}):
        selected = [r for r in rows if r["source"] == source]
        by_source[source] = {
            "sigla": len(selected),
            "attestations": sum(r["attestations"] for r in selected),
            "pct": round(100 * sum(r["attestations"] for r in selected) / TOTALS["attestations"], 4),
        }
    available_mass = mass(lambda r: r["availability"] in AVAILABLE)
    exact_mass = mass(lambda r: r["availability"] in AVAILABLE and r["edition_identity"] == "aob_exact")
    summary = {
        "license": "CC-BY-SA-4.0",
        "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0/",
        "dataset": "pd_edition_availability_c1",
        "generated_by": "python scripts/pd_edition_availability.py",
        "generated_on": "2026-10-29",
        "protocol": {
            "population": "all H6949 attestations in the published letter-a PD machine text",
            "continuation_rule": "a semicolon continuation inherits the immediately preceding siglum in its citation tail",
            "availability_rule": "DCS crosswalk, hand-checked H7298 GRETIL rows, and curated evidence only",
            "partial_rule": "partial and embedded witnesses are reported separately from full witnesses",
            "unknown_rule": "unprobed or unresolved sigla are never counted as absent",
            "edition_rule": "work-level e-text presence is not identity with the AOB edition; aob_exact is a separate numerator",
        },
        "evidenceLevels": {
            "attestation_counts": "derived",
            "live_text_probes": "observed",
            "availability_aggregates": "derived",
            "human_review": "none",
        },
        "warnings": [
            "unresolved mass is not evidence of absence",
            "work-level availability does not establish AOB edition identity",
            "partial and embedded witnesses are not full-work coverage",
            "104 continuation loci have no assignable preceding siglum and stay unresolved",
        ],
        "totals": {
            **TOTALS,
            "raw_sigla": len(rows),
            "available_work_level": available_mass,
            "available_work_level_pct": round(100 * available_mass / TOTALS["attestations"], 4),
            "available_aob_exact": exact_mass,
            "available_aob_exact_pct": round(100 * exact_mass / TOTALS["attestations"], 4),
            "aob_mapped": mass(lambda r: bool(r["aob_entry_ids"])),
            "unassigned_continuations": counts["__UNASSIGNED_CONTINUATION__"],
        },
        "aob_entries": {
            "rows": len(aob_projection),
            "with_direct_attestations": sum(bool(r["attestations_direct"]) for r in aob_projection),
            "by_availability": {
                status: sum(r["availability"] == status for r in aob_projection)
                for status in sorted({r["availability"] for r in aob_projection})
            },
        },
        "by_status": by_status,
        "by_source": by_source,
        "by_class": {
            cls: {
                "attestations": mass(lambda r, c=cls: r["class"] == c),
                "available": mass(lambda r, c=cls: r["class"] == c and r["availability"] in AVAILABLE),
            }
            for cls in sorted({r["class"] for r in rows})
        },
        "inputs": {
            "pd_txt_sha256": sha256(pd_path),
            **{name: sha256(os.path.join(DATA, name)) for name in (
                "pd_siglum_families.tsv", "pd_dcs_text_crosswalk.tsv",
                "pd_residue_source_status.tsv", "pd_aob_declared_entries.tsv",
                "pd_index_works.tsv", "pd_work_registry.tsv", "pd_work_edition_map.tsv",
                "pd_edition_availability_evidence.tsv",
                "pd_edition_availability_probes_2026-10-29.json",
            )},
        },
        "top_unresolved": [
            {k: r[k] for k in ("siglum", "attestations", "class", "work_title", "aob_entry_ids", "aob_titles", "notes")}
            for r in sorted((r for r in rows if r["availability"] == "unresolved"),
                            key=lambda x: (-x["attestations"], x["siglum"]))[:100]
        ],
    }
    return rows, aob_projection, summary


def write_outputs(rows, aob_rows, summary):
    for path, columns, records in ((OUT_TSV, COLUMNS, rows), (OUT_AOB_TSV, AOB_COLUMNS, aob_rows)):
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write("\t".join(columns) + "\n")
            for record in records:
                fh.write("\t".join(str(record[c]) for c in columns).rstrip("\t") + "\n")
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


def check(rows, aob_rows, summary):
    problems = []
    expected_rows, expected_summary = rows, summary
    with open(OUT_TSV, encoding="utf-8", newline="") as fh:
        committed = list(csv.DictReader(fh, delimiter="\t"))
    if len(committed) != len(expected_rows):
        problems.append(f"TSV row count {len(committed)} != {len(expected_rows)}")
    else:
        for old, new in zip(committed, expected_rows):
            for key in COLUMNS:
                if old[key] != str(new[key]):
                    problems.append(f"TSV drift {new['siglum']}.{key}")
                    break
    with open(OUT_AOB_TSV, encoding="utf-8", newline="") as fh:
        committed_aob = list(csv.DictReader(fh, delimiter="\t"))
    if committed_aob != [{key: str(value) for key, value in row.items()} for row in aob_rows]:
        problems.append("AOB TSV differs from rebuilt projection")
    with open(OUT_JSON, encoding="utf-8") as fh:
        if json.load(fh) != expected_summary:
            problems.append("JSON summary differs from rebuilt summary")
    if os.path.exists(REPORT):
        with open(REPORT, encoding="utf-8") as fh:
            report = fh.read()
        t = expected_summary["totals"]
        for needle in (f"{t['available_work_level']:,}", f"{t['available_work_level_pct']:.2f}",
                       f"{t['available_aob_exact']:,}", f"{t['available_aob_exact_pct']:.2f}"):
            if needle not in report:
                problems.append(f"report missing {needle}")
    else:
        problems.append("report missing")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pd", required=True, help="path to the PDScan 2020 txt/pd.txt")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    rows, aob_rows, summary = build(args.pd)
    if args.check:
        problems = check(rows, aob_rows, summary)
        if problems:
            print("FAIL")
            for problem in problems:
                print(" ", problem)
            return 1
        print(f"PASS C1 {summary['totals']['available_work_level']:,}/{TOTALS['attestations']:,} "
              f"= {summary['totals']['available_work_level_pct']:.2f}% work-level; "
              f"{summary['totals']['available_aob_exact_pct']:.2f}% AOB-exact")
        return 0
    write_outputs(rows, aob_rows, summary)
    print(f"wrote {OUT_TSV}\nwrote {OUT_AOB_TSV}\nwrote {OUT_JSON}")
    print(json.dumps(summary["totals"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
