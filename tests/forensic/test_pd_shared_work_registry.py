"""H7296 — pins for the shared PD work-and-edition identity registry.

The suite proves the acceptance contract, not the shape of the code: 2,031 Index
rows / 409 blank abbreviation cells / 434 `vision-low` rows preserved; the
MahāBhā./MahāBh. homograph stays split; the near-homograph near-misses are never
merged; repeated AOB editions join one work without losing either siglum; the
AmaKoUd. commentary siglum is a relation, not a merge or a guessed title; the Q5
validation states stay visibly unvalidated with no kappa; and a single mutated
unresolved cell makes `--check` fail.
"""

from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(ROOT, "scripts", "pd_shared_work_registry.py")
DATA = os.path.join(ROOT, "data", "pd")


def run_check(root=ROOT):
    return subprocess.run(
        [sys.executable, SCRIPT, "--check", "--root", root],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
    )


def read_tsv(name):
    with open(os.path.join(DATA, name), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def diagnostics():
    with open(os.path.join(DATA, "pd_work_registry_diagnostics.json"), encoding="utf-8") as fh:
        return json.load(fh)


def map_rows():
    return read_tsv("pd_work_edition_map.tsv")


def registry_rows():
    return read_tsv("pd_work_registry.tsv")


def test_check_regenerates_green():
    proc = run_check()
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.count("OK ") == 4


def test_acceptance_counts_preserved():
    d = diagnostics()["counts"]
    assert d["index_rows"] == 2031
    assert d["index_blank_abbreviation_cells"] == 409
    assert d["index_vision_low_rows"] == 434
    assert d["aob_declared_works"] == 1112
    assert d["aob_editions"] == 1118
    # every blank cell is preserved as its own unresolved registry row
    blanks = [r for r in registry_rows() if r["unresolved_class"] == "blank_abbreviation_cell"]
    assert len(blanks) == 409
    blank_map = [r for r in map_rows() if r["relation"] == "unresolved_blank"]
    assert len(blank_map) == 409
    assert all(r["dictionary_siglum"] == "" for r in blank_map)


def test_mahabha_homograph_stays_split():
    canary = diagnostics()["canaries"]["mahabha_homograph"]
    assert canary["distinct"] is True
    assert canary["merged"] is False
    rows = [r for r in map_rows() if r["dictionary_siglum"] in ("MahāBhā.", "MahāBh.")
            and r["relation"] == "primary_work"]
    by_siglum = {r["dictionary_siglum"]: r["work_id"] for r in rows}
    assert by_siglum["MahāBhā."] != by_siglum["MahāBh."]


def test_near_homographs_never_merged():
    canary = diagnostics()["canaries"]["near_homograph"]
    assert canary["pairs"] == 142
    assert canary["skeleton_collisions"] > 0
    assert canary["merged"] == 0
    assert canary["distinct"] is True


def test_repeated_editions_one_work_and_both_sigla():
    canary = diagnostics()["canaries"]["repeated_editions"]
    assert canary["works"] == 6 and canary["rows"] == 12
    assert canary["all_one_work"] is True
    rows = [r for r in map_rows() if r["source"] == "pd_aob_declared_works"]
    atma = [r for r in rows if r["dictionary_siglum"] in ("AtmaU.1", "AtmaU")]
    assert len({r["work_id"] for r in atma}) == 1
    assert {r["dictionary_siglum"] for r in atma} == {"AtmaU.1", "AtmaU"}


def test_commentary_inherited_siglum_is_a_relation():
    canary = diagnostics()["canaries"]["commentary_inherited_siglum"]
    assert canary["found"] is True
    assert canary["is_relation_not_merge"] is True
    relations = [r for r in map_rows() if r["relation"] == "commentary_on"
                 and r["dictionary_siglum"] == "AmaKoUd."]
    assert len(relations) == 1
    assert relations[0]["related_work_id"] == canary["base_work_id"]
    assert relations[0]["work_id"] == canary["own_work_id"]


def test_validation_contract_is_not_fabricated():
    d = diagnostics()
    assert d["validation"]["kappa"] is None
    assert d["validation"]["kappa_status"] == "not_measured_no_double_annotation"
    assert d["validation"]["adjudicated_rows"] == 0
    assert d["validation"]["seeded_ordinary_control"]
    assert all(r["validation_state"] == "unvalidated_pending_double_annotation"
               for r in registry_rows() + map_rows())
    control = [r for r in map_rows() if r["sample_role"] == "seeded_ordinary_control"]
    assert len(control) == 1
    assert control[0]["work_id"]


def test_changed_unresolved_cell_fails_check():
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copytree(DATA, os.path.join(tmp, "data", "pd"))
        path = os.path.join(tmp, "data", "pd", "pd_work_edition_map.tsv")
        with open(path, encoding="utf-8", newline="") as fh:
            table = list(csv.DictReader(fh, delimiter="\t"))
        target = next(r for r in table if r["relation"] == "unresolved_blank")
        target["dictionary_siglum"] = "Guessed."
        with open(path, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=table[0].keys(), delimiter="\t",
                               lineterminator="\n")
            w.writeheader()
            w.writerows(table)
        proc = run_check(tmp)
        assert proc.returncode == 1
        assert "CHECK FAIL" in proc.stderr


def test_shared_siglum_adjudication_counts_and_residue():
    d = diagnostics()["shared_siglum_adjudication"]
    assert d["baseline_shared_siglum_folds"] == 57
    assert d["baseline_shared_siglum_registry_records"] == 230
    assert d["folds_resolved"] == 55
    assert d["folds_partial"] == 2
    assert d["registry_records_adjudicated"] == 228
    assert d["registry_records_remaining"] == 2
    assert d["unresolved_claims"] == [
        "AOB:1962",
        "AOB:aryasiddhantamahasiddhanta148",
    ]
    assert d["split_index_rows"] == 22
    assert d["alias_groups"] == 50
    assert d["rejected_non_work_aob_claims"] == 2
    assert d["ordinary_fold_join_blocked_for_all_shared_folds"] is True
    remaining = [r for r in registry_rows()
                 if "shared_siglum" in r["unresolved_class"].split(";")]
    assert len(remaining) == 2
    assert {r["provenance"] for r in remaining} == {
        "data/pd/pd_aob_declared_works.tsv:1962",
        "data/pd/pd_aob_declared_works.tsv:aryasiddhantamahasiddhanta148",
    }
    residue = {r["siglum_fold"]: r for r in read_tsv("pd_shared_siglum_adjudications.tsv")
               if r["status"] == "partial"}
    assert set(residue) == {"aryasi", "tantrsa"}
    assert all("STOP_INSUFFICIENT_TITLE_EVIDENCE" in r["rationale"]
               for r in residue.values())


def test_shared_siglum_aliases_splits_and_quarantine():
    rows = registry_rows()
    sudha = [r for r in rows if r["label"] == "nyāyasudhā"]
    assert len(sudha) == 2
    assert len({r["work_id"] for r in sudha}) == 2
    pari = [r for r in rows if r["label"] in ("dhūrtakalpa", "skandayoga")]
    assert len(pari) == 1
    assert pari[0]["label"] in ("dhūrtakalpa", "skandayoga")
    quarantine = [r for r in rows if r["unresolved_class"] == "aob_ocr_non_work"]
    assert len(quarantine) == 2
    assert all(not r["work_id"] for r in quarantine)

    claim_work = {}
    by_work_fold = {}
    overlay = read_tsv("pd_shared_siglum_adjudications.tsv")
    shared_folds = {row["siglum_fold"] for row in overlay}
    for r in map_rows():
        if r["source"] == "pd_index_works":
            key = "IDX:" + r["source_locator"]
        elif r["source"] == "pd_aob_declared_works":
            key = "AOB:" + r["source_locator"].rsplit(":", 1)[0]
        else:
            continue
        claim_work.setdefault(key, set()).add(r["work_id"])
        if r["work_id"] and r["siglum_fold"] in shared_folds:
            by_work_fold.setdefault((r["siglum_fold"], r["work_id"]), set()).add(key)
    alias_membership = {}
    for row in overlay:
        f = row["siglum_fold"]
        for i, group in enumerate(row["alias_groups"].split("|")):
            if not group:
                continue
            claims = group.split(",")
            work_ids = set().union(*(claim_work.get(c, set()) for c in claims))
            assert len(work_ids) == 1 and "" not in work_ids, (f, claims, work_ids)
            for c in claims:
                alias_membership[(f, c)] = i
    for (f, wid), claims in by_work_fold.items():
        sources = {c.split(":", 1)[0] for c in claims}
        if sources == {"IDX", "AOB"}:
            groups = {alias_membership.get((f, c)) for c in claims}
            assert len(groups) == 1 and None not in groups, (f, wid, claims, groups)
