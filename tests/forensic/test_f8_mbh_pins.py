"""Pins for the F8 csl-orig revision pin (H5260).

F8a (``f8_mbh_census``) re-reads PWG/MW bodies live, so it pins the clean
checkout HEAD before and after. F8e presence and F8b verify read only derived
CSVs, so they inherit the pin from those CSVs' ``.source.json`` sidecars and
refuse an unpinned upstream. The resolvers that also need the rights-restricted
vulgate/BORI witness texts (resolve, quote lane, Droṇa, F7) share the same
helpers, pinned in ``test_corpus_pin.py``.

Hand derivation (census). PWG carries one entry with one full MBh reference
``<ls>MBH. 3,45</ls>`` -> book 3, verse 45: 1 PWG citation, parvan 3 max
verse 45. MW carries one entry with no ``<ls>``: 0 MW citations. No correction
marker sits next to the reference: 0 notes.
"""

import json

import pytest

import _corpus_pin
import f8_mbh_census as f8a
from conftest import git_commit_all, write_text


def _corpus(root):
    write_text(root / "pwg" / "pwg.txt", "<L>1<pc>1-1<k1>agni<k2>agni\n{%Feuer%} <ls>MBH. 3,45</ls>.\n<LEND>\n")
    write_text(root / "mw" / "mw.txt", "<L>1<pc>1,1<k1>agni<k2>agni\nfire\n<LEND>\n")


def test_census_pins_the_live_head(tmp_path, monkeypatch, forensic_cwd, pin):
    root = tmp_path / "csl-orig"
    _corpus(root)
    head = git_commit_all(root)
    monkeypatch.setattr(f8a, "CSL_ORIG", str(root))
    f8a.main()
    report = json.loads((forensic_cwd / "data/forensic/f8_report.json").read_text(encoding="utf-8"))
    pin("f8", "census.pwg_mbh_citations", 1, report["pwg_mbh_citations"])
    pin("f8", "census.mw_mbh_citations", 0, report["mw_mbh_citations"])
    pin("f8", "census.pwg_parvan_max_verse", {"3": 45}, report["pwg_parvan_max_verse"])
    pin("f8", "census.pwg_correction_notes", 0, report["pwg_correction_notes"])
    pin("f8", "csl_orig_revision(H5260)", head, report["csl_orig_revision"])
    for out in ("mbh_citation_inventory.csv", "mbh_parvan_distribution.csv",
                "mbh_correction_notes.csv", "mbh_candidate_numeric_typos.csv"):
        side = json.loads((forensic_cwd / f"data/forensic/{out}.source.json").read_text(encoding="utf-8"))
        pin("f8", f"sidecar.{out}.csl_orig", (head, "live_checkout"),
            (side["csl_orig"]["revision"], side["csl_orig"]["via"]))


def test_census_refuses_a_dirty_checkout(tmp_path, monkeypatch, forensic_cwd):
    root = tmp_path / "csl-orig"
    _corpus(root)
    git_commit_all(root)
    write_text(root / "pwg" / "pwg.txt", "<L>1<pc>1-1<k1>agni<k2>agni\nedited\n<LEND>\n")
    monkeypatch.setattr(f8a, "CSL_ORIG", str(root))
    with pytest.raises(_corpus_pin.CorpusPinError, match="dirty"):
        f8a.main()
    assert not (forensic_cwd / "data/forensic/f8_report.json").exists()


def test_presence_refuses_an_unpinned_upstream(tmp_path, monkeypatch, forensic_cwd):
    """The concordance/inventory it reads carry no csl-orig pin -> refuse before any read."""
    f8e = pytest.importorskip("f8_mbh_presence")
    out = forensic_cwd / "data" / "forensic"
    for name in ("_mbh_vulgate_verses.jsonl", "_mbh_bori_halfverse.jsonl",
                 "mbh_vulgate_concordance.csv", "mbh_citation_inventory.csv"):
        write_text(out / name, "")
    write_text(out / "mbh_citation_inventory.csv.source.json", json.dumps({"csl_orig": {"revision": "f" * 40}}))
    with pytest.raises(_corpus_pin.CorpusPinError, match="mbh_vulgate_concordance.csv.source.json: unpinned"):
        f8e.main()
    assert not (out / "f8_presence_report.json").exists()


def test_verify_inherits_the_census_pin_or_refuses(tmp_path, monkeypatch, forensic_cwd):
    f8b = pytest.importorskip("f8_mbh_verify")
    monkeypatch.setattr(f8b, "build_corpus", lambda: [])
    monkeypatch.setattr(f8b, "build_ngram_index", lambda corpus: ([], {}))
    notes = forensic_cwd / "data" / "forensic" / "mbh_correction_notes.csv"
    write_text(notes, "L,k1,parvan,verse\n")
    with pytest.raises(_corpus_pin.CorpusPinError, match="mbh_correction_notes.csv.source.json: unpinned"):
        f8b.main()
    write_text(notes.parent / "mbh_correction_notes.csv.source.json",
               json.dumps({"csl_orig": {"revision": "MIXED"}}))
    with pytest.raises(_corpus_pin.CorpusPinError, match="unpinned"):
        f8b.main()
