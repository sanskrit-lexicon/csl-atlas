"""Pins for ``pd_dcs_residue_status_queue`` (H7298).

Discipline (per tests/forensic/conftest.py): every expected number below is
derived BY HAND from the named sources — never by running the builder:

* H6722 (Uprava papers/A68/sweeps/2026-10-15-H6722-…md): missing-everywhere =
  exactly 6 works / 9,229 cites {PadmP. 3506, BhaviP. 1558, Prasā. 1333,
  Vaija. 1155, GaṇeP. 915, NānārthāSaṃ. 762}; GRETIL-full+embedded = 9 works /
  10,262; GRETIL-partial = 5 works / 5,348; rows 21–44 uncrossed = 24 works /
  9,685 cites; top-20 mass 24,839; named total 34,524.
* csl-atlas data/pd/pd_siglum_families.tsv: SkandP. = 3,335 cites, covered.
* dcs_text_inventory.tsv (27-10-2026): SkPuR 113,333 tok + SkPu 16,479 tok.
* MSI E:\\Tools\\wisdomlib-scrape probes (27-10-2026): books.json 75 books;
  skanda-purana-sanskrit 95,556 chapters, text layer = sitemap.txt marker
  only (40 B); stats.json 23-07-2026 "Chapter bodies CF-blocked".

The five hand spot-check rows pinned below: SkandP., PadmP., MahāBh., NaiṣC.,
VāyuP.
"""
import csv
import importlib.util
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
DATA = REPO / "data" / "pd"
SCRIPT = REPO / "scripts" / "pd_dcs_residue_status_queue.py"

spec = importlib.util.spec_from_file_location("pd_dcs_residue_status_queue", SCRIPT)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def _queue_rows():
    with open(DATA / "pd_dcs_residue_status_queue.tsv", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def _families_named():
    with open(DATA / "pd_siglum_families.tsv", encoding="utf-8", newline="") as fh:
        return {r["siglum"]: int(r["count"]) for r in csv.DictReader(fh, delimiter="\t")
                if r["match_type"] == "residue" and (r["dcs_title"] or r["display_title"])}


def test_check_gate_green():
    proc = subprocess.run([sys.executable, str(SCRIPT), "--check"],
                          capture_output=True, text=True, cwd=str(REPO))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert proc.stdout.startswith("PASS")


def test_committed_outputs_byte_identical_to_rebuild():
    tsv, js = builder.build()
    assert (DATA / "pd_dcs_residue_status_queue.tsv").read_text(encoding="utf-8") == tsv
    assert (DATA / "pd_dcs_residue_status_queue.json").read_text(encoding="utf-8") == js


def test_lane_invariants_hand_derived():
    rows = _queue_rows()
    assert len(rows) == 45
    lanes = {}
    for r in rows:
        lane = lanes.setdefault(r["lane"], [0, 0, 0])
        lane[0] += 1
        lane[1] += int(r["pd_cites"])
        lane[2] += int(r["expected_pd_citation_gain"])
    assert lanes["acquire-digitise"] == [6, 9229, 9229]
    assert lanes["ingest-annotate"] == [9, 10262, 10262]
    assert lanes["fragment-completion"] == [6, 8683, 5348]
    assert lanes["unverified"] == [24, 9685, 9685]
    assert sum(v[1] for v in lanes.values()) == 34524 + 3335


def test_missing_everywhere_class_is_exactly_h6722():
    rows = _queue_rows()
    missing = {r["siglum"] for r in rows if r["lane"] == "acquire-digitise"}
    assert missing == {"PadmP.", "BhaviP.", "Prasā.", "Vaija.", "GaṇeP.", "NānārthāSaṃ."}
    for r in rows:
        if r["lane"] == "acquire-digitise":
            assert r["dcs_status"] == "absent (residue)"
            assert r["gretil_status"] == "absent"


def test_named_residue_parity_against_families():
    named = _families_named()
    assert len(named) == 44
    rows = {r["siglum"]: r for r in _queue_rows() if r["dcs_status"] == "absent (residue)"}
    assert set(rows) == set(named)
    for sig, count in named.items():
        assert int(rows[sig]["pd_cites"]) == count


def test_no_unverified_field_promoted():
    for r in _queue_rows():
        assert r["rights"].strip(), r["siglum"]
        assert r["annotation"].strip(), r["siglum"]
        # fail-mode guard: no unverified rights/annotation promoted to a claim
        assert "public domain" not in r["rights"].lower()
        assert "public domain" not in r["annotation"].lower()
        # DCS-absent works are never called globally undigitised
        if r["dcs_status"].startswith("absent"):
            assert "undigitised" not in r["notes"].lower()
            assert "missing everywhere" not in r["fragment_status"].lower()
        # fragments are never called complete
        if "only" in r["fragment_status"] or "fragment" in r["dcs_status"]:
            assert "complete" not in r["fragment_status"].lower()


def test_five_spot_check_rows():
    rows = {r["siglum"]: r for r in _queue_rows()}
    # 1. Skandapurāṇa: covered context row, fragmentary DCS witnesses, wisdomlib
    #    link-index only, 0 citation gain (mass already attributed).
    sk = rows["SkandP."]
    assert int(sk["pd_cites"]) == 3335
    assert sk["lane"] == "fragment-completion"
    assert int(sk["expected_pd_citation_gain"]) == 0
    assert "113,333" in sk["dcs_status"] and "16,479" in sk["dcs_status"]
    assert "95,556" in sk["wisdomlib_portal"]
    assert sk["wisdomlib_estate"].startswith("link-index-only")
    # 2. Padmapurāṇa: missing-everywhere, wisdomlib portal + estate link index.
    pp = rows["PadmP."]
    assert int(pp["pd_cites"]) == 3506 and pp["lane"] == "acquire-digitise"
    assert "padma-purana-sanskrit" in pp["wisdomlib_portal"]
    assert "700 chapters" in pp["wisdomlib_estate"]
    # 3. Mahābhāṣya: GRETIL full, Cardona input witness.
    mb = rows["MahāBh."]
    assert mb["lane"] == "ingest-annotate" and mb["gretil_status"] == "full"
    assert "vyakaranamahabhasya" in mb["source_ref"]
    # 4. Naiṣadhīyacarita: uncrossed row with a verified estate manifest hit.
    ns = rows["NaiṣC."]
    assert ns["lane"] == "unverified" and ns["gretil_status"] == "uncrossed"
    assert "2,860 chapters" in ns["wisdomlib_portal"]
    assert ns["wisdomlib_estate"].startswith("link-index-only")
    # 5. Vāyupurāṇa: GRETIL partial (Revākhaṇḍa only) + DCS/Skandapurāṇa
    #    cross-source title discrepancy recorded.
    vy = rows["VāyuP."]
    assert vy["lane"] == "fragment-completion" and vy["gretil_status"] == "partial"
    assert "Revākhaṇḍa only" in vy["fragment_status"]
    assert "Skandapurāṇa" in vy["fragment_status"]


def test_skandapurana_verdict_in_json():
    data = json.loads((DATA / "pd_dcs_residue_status_queue.json").read_text(encoding="utf-8"))
    v = data["skandapurana_verdict"]
    assert v["pd_cites"] == 3335
    assert "INCONCLUSIVE" in v["edition_identity"]
    assert "link-index" in v["wisdomlib_estate"]
    assert "CC BY 4.0" in v["rights"]
    assert v["annotation"].startswith("none")
