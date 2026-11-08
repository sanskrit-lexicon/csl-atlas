"""H7316 offline pins for the one-entry KoshaSHRI fixture export.

The all-rights-reserved JSON stays local-only. Full-fixture tests skip when it
is absent; the synthetic multi-reference/nested-sense test always runs.
"""
import csv
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import pd_koshashri_fixture_export as h7316
from pd_koshashri_vocable import citation_records, parse_response

csv.field_size_limit(10_000_000)

DATA = ROOT / "data" / "pd"
FIXTURE = DATA / "koshashri_vocable.json"
SCRIPT = ROOT / "scripts" / "pd_koshashri_fixture_export.py"
requires_fixture = pytest.mark.skipif(not FIXTURE.is_file(),
                                      reason="restricted local agni response not staged")


def _tsv(name):
    with (DATA / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def _raw():
    return parse_response(FIXTURE.read_text(encoding="utf-8"))


@requires_fixture
def test_check_mode_exits_zero():
    proc = subprocess.run([sys.executable, str(SCRIPT), "--check"],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr


@requires_fixture
def test_artifacts_rebuild_byte_identically():
    built = h7316.build()
    for path, content in built.items():
        assert path.read_text(encoding="utf-8") == content, f"stale artifact: {path}"


@requires_fixture
def test_canaries_and_tsv_shape():
    outer, vocable, nested = _raw()
    entries = _tsv("pd_koshashri_entries.tsv")
    citations = _tsv("pd_koshashri_citations.tsv")
    assert len(entries) == 1
    assert len(citations) == 1400
    assert len(vocable["meaning"]) == 29
    assert len(vocable["meaning"][0]["citations"]) == 242
    first = [row for row in citations if row["sense_id"].endswith(":1")]
    assert len(first) == 248
    assert first[0]["source_siglum"] == "ṚV."
    assert first[0]["work_id"] == h7316.RV_WORK_ID
    assert json.loads(first[0]["locus"]) == ["i.12.6;"]
    assert first[0]["locus_scheme"] == "Maṇḍala.Sūkta.Ṛc."
    assert first[0]["work_date_raw"] == "1400BCE"
    assert json.loads(entries[0]["source_volume"]) == {"volumeNumber": 4, "name": "Volume 2"}
    assert len(json.loads(entries[0]["nested_vocables"])) == 1 == len(nested)
    assert entries[0]["grammatical_note_raw_html"].startswith("<s<small>")
    assert {row["work_resolution_status"] for row in citations
            if row["source_siglum"] != "ṚV."} == {"unresolved"}
    assert {row["validation_state"] for row in citations} == {h7316.VALIDATION}
    assert len({row["source_citation_id"] for row in citations}) == len(citations)


@requires_fixture
def test_changed_canary_fails_check(tmp_path):
    outer = json.loads(FIXTURE.read_text(encoding="utf-8"))
    vocable = json.loads(outer["object"])
    vocable["meaning"][0]["citations"].pop()
    outer["object"] = json.dumps(vocable, ensure_ascii=False)
    changed = tmp_path / "changed.json"
    changed.write_text(json.dumps(outer, ensure_ascii=False), encoding="utf-8")
    proc = subprocess.run([sys.executable, str(SCRIPT), "--check", "--input", str(changed)],
                          capture_output=True, text=True)
    assert proc.returncode == 2
    assert "STOP_CANARY_MISMATCH" in proc.stderr


def test_synthetic_multi_reference_and_nested_sense():
    outer = {
        "id": "synthetic",
        "object": json.dumps({
            "meaning": [{
                "meaningKey": "2",
                "citations": [{"citationText": "same", "references": [
                    {"referenceBook": "A."}, {"referenceBook": "B."}
                ]}],
                "shades": [{
                    "shadeKey": "i",
                    "citations": [{"citationText": "same", "references": [
                        {"referenceBook": "A."}
                    ]}],
                }],
            }]
        }),
        "nestedVocables": [],
    }
    outer_obj, vocable, nested = parse_response(json.dumps(outer))
    rows = citation_records(outer_obj, vocable)
    assert len(rows) == 3
    assert [row["sense_id"].rsplit(":", 1)[-1] for row in rows] == ["2", "2", "2i"]
    assert [row["quotation_text"] for row in rows] == ["same", "same", "same"]
    assert len({row["source_citation_id"] for row in rows}) == 3
