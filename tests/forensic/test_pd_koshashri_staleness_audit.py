"""Pins for H7300: PD KoshaSHRI staleness audit.

Everything is checked offline against the committed snapshots: the artifacts
must rebuild byte-identically from them, the five canary pins are hand-derived
literals (never produced by the script under test), the four verdicts must be
distinct labels, and the rights fence is asserted structurally — the committed
KoshaSHRI snapshot may carry only per-volume metadata keys, never entry text.
"""

import csv
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
for p in (str(ROOT / "scripts"), str(ROOT / "scripts" / "lib")):
    if p not in sys.path:
        sys.path.insert(0, p)

import pd_koshashri_staleness_audit as h7300

DATA = ROOT / "data" / "pd"
SCRIPT = ROOT / "scripts" / "pd_koshashri_staleness_audit.py"


def _json(name):
    with open(DATA / name, encoding="utf-8") as fh:
        return json.load(fh)


def _tsv(name):
    with open(DATA / name, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def test_check_mode_exits_zero():
    proc = subprocess.run([sys.executable, str(SCRIPT), "--check"],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr


def test_artifacts_rebuild_byte_identically():
    built = h7300.build_all()
    for path, content in built.items():
        committed = pathlib.Path(path).read_text(encoding="utf-8")
        assert committed == content, "stale artifact: %s" % path


def test_five_canary_pins():
    snap = _json("pd_koshashri_volume_snapshot_2026-10-27.json")
    census = _json("pd_cologne_tag_census_2026-10-27.json")
    vols = {v["id"]: v for v in snap["volumes"]}
    # K1 — hand-derived from the C7 audit (14-10-2026) and re-pinned here
    assert vols[1]["year_of_publish"] == 1976
    assert (vols[1]["start_page"], vols[1]["end_page"]) == (1, 216)
    assert vols[1]["name_of_ge"] == "A.M. Ghatage"
    # K2
    assert vols[35]["year_of_publish"] == 2019
    assert (vols[35]["start_page"], vols[35]["end_page"]) == (5881, 6056)
    assert vols[35]["eng_closing_entry"] == "abhigamyamānaparadārādi"
    # K3 — the 25-10-2026 census, incl. the <ls> correction
    assert census["tag_counts"]["<L>"] == 107630
    assert census["tag_counts"]["<ls>"] == 0
    assert census["tag_counts"]["<div n=\"lb\">"] == 440003
    # K4 — the constant-100 trap
    assert {v["total_vocables_raw"] for v in snap["volumes"]
            if v["status"] == "ok"} == {100}
    # K5 — the portal gap
    assert [v["id"] for v in snap["volumes"] if v["status"] != "ok"] == [12, 14]
    assert snap["ok"] == 33
    # the canary artifact carries exactly five rows
    assert len(_tsv("pd_koshashri_canaries.tsv")) == 5


def test_four_verdicts_are_distinct_and_gated():
    v = _json("pd_koshashri_staleness_verdicts.json")
    verdicts = v["verdicts"]
    assert set(verdicts) == {"schema_staleness", "content_coverage",
                             "conversion_loss", "editorial_change"}
    assert len(set(verdicts.values())) == 4  # no shared boilerplate verdict
    assert verdicts["editorial_change"].startswith("NO_POSITIVE_CLAIM")
    assert verdicts["conversion_loss"].startswith("NOT_DETECTED_IN_V78_SAMPLE")
    assert (v["panels"]["C_print_fidelity_2009_2019"]["verdict"]
            == "STOP_NO_PRINT_ACCESS")
    # no editorial verdict may be derived from tags alone
    assert "tags alone prove nothing" in verdicts["editorial_change"]


def test_coverage_panel_shape_and_split():
    rows = _tsv("pd_koshashri_content_coverage.tsv")
    assert len(rows) == 35
    digital = [r for r in rows if r["in_cologne_digital_text"] == "yes"]
    pune = [r for r in rows if r["in_cologne_digital_text"] == "no"]
    assert len(digital) == 24 and len(pune) == 11
    assert all(int(r["koshashri_vol"]) <= 24 for r in digital)
    assert all(int(r["koshashri_vol"]) >= 25 for r in pune)
    v = _json("pd_koshashri_staleness_verdicts.json")
    b = v["panels"]["B_dated_content_coverage"]
    assert b["pune_only_pages"] == 1728          # deduped union
    assert b["pune_only_pages_naive_sum"] == 1816  # portal overlap visible
    assert b["print_record_final_page"] == 6056
    assert b["cologne_digital_ends"] == "vol 24, 2008, p. 4328"


def test_v78_control_all_consistent():
    rows = _tsv("pd_v78_bracket_mark_control.tsv")
    assert len(rows) == 20
    assert {r["cell"] for r in rows} == {"consistent"}
    assert {r["page"] for r in rows} <= {
        "7-3485a", "7-3485b", "7-3549a", "7-3559a", "8-4168a"}
    v = _json("pd_koshashri_staleness_verdicts.json")
    c = v["panels"]["C_print_fidelity_v78_control"]
    assert c["marks_checked"] == 20
    assert c["print_only_marks_missing_from_machine"] == 0


def test_rights_fence_no_koshashri_entry_text():
    snap = _json("pd_koshashri_volume_snapshot_2026-10-27.json")
    allowed = {"id", "status", "vol_num", "year_of_publish", "start_page",
               "end_page", "name_of_ge", "eng_opening_entry",
               "eng_closing_entry", "san_opening_entry", "san_closing_entry",
               "total_vocables_raw", "note"}
    for v in snap["volumes"]:
        assert set(v) <= allowed, "unexpected key in snapshot: %s" % set(v)
    # no artifact may embed a KoshaSHRI entry payload or gated HTML
    for name in ("pd_koshashri_markup_comparison.tsv",
                 "pd_koshashri_content_coverage.tsv",
                 "pd_koshashri_staleness_verdicts.json",
                 "pd_koshashri_canaries.tsv"):
        body = (DATA / name).read_text(encoding="utf-8")
        assert "Sign in - Digital KoshaSHRI" not in body
        assert "SockJS" not in body or name.endswith("markup_comparison.tsv")
