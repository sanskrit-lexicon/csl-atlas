"""Pins for ``_corpus_pin`` (H5248): a forensic figure is written only against
ONE recorded csl-orig revision — None, MIXED, dirty or moved all refuse."""

import json

import pytest

import _corpus_pin as cp
from conftest import FIXTURE_REVISION, git_commit_all, write_parse_provenance, write_text, write_tsv


def _caches(parsed, codes=("mw", "pwg")):
    for code in codes:
        write_tsv(parsed / f"{code}.tsv", [(1, "agni", "agni", "", "", 1, "P. 1")])


def test_cache_revision_one_clean_revision(tmp_path, pin):
    _caches(tmp_path)
    write_parse_provenance(tmp_path, ["mw", "pwg"])
    got = cp.cache_revision(["MW", "PWG"], str(tmp_path))
    pin("corpus_pin", "cache.revision", FIXTURE_REVISION, got["revision"])
    pin("corpus_pin", "cache.caches", ["mw", "pwg"], sorted(got["caches"]))


@pytest.mark.parametrize("case", ["unrecorded", "hash-mismatch", "dirty", "mixed", "empty"])
def test_cache_revision_refuses(tmp_path, case):
    _caches(tmp_path)
    if case == "unrecorded":
        write_parse_provenance(tmp_path, ["mw"])
    elif case == "hash-mismatch":
        write_parse_provenance(tmp_path, ["mw", "pwg"])
        write_tsv(tmp_path / "pwg.tsv", [(1, "deva", "deva", "", "", 1, "R. 2")])
    elif case == "dirty":
        write_parse_provenance(tmp_path, ["mw", "pwg"], dirty=True)
    elif case == "mixed":
        write_parse_provenance(tmp_path, ["mw", "pwg"])
        prov = json.loads((tmp_path / "_parse_provenance.json").read_text(encoding="utf-8"))
        prov["caches"]["pwg"]["revision"] = "e" * 40
        write_text(tmp_path / "_parse_provenance.json", json.dumps(prov))
    with pytest.raises(cp.CorpusPinError, match="MIXED" if case == "mixed" else "None"):
        cp.cache_revision([] if case == "empty" else ["mw", "pwg"], str(tmp_path))


def test_live_revision_clean_then_dirty_then_moved(tmp_path, pin):
    root = tmp_path / "csl-orig"
    write_text(root / "mw" / "mw.txt", "<L>1<pc>1<k1>a<k2>a\nx\n<LEND>\n")
    head = git_commit_all(root)
    got = cp.live_revision(str(root / "mw"))          # a subdir, like ../csl-orig/v02
    pin("corpus_pin", "live.revision", (head, "live_checkout"), (got["revision"], got["via"]))
    write_text(root / "mw" / "mw.txt", "edited\n")
    with pytest.raises(cp.CorpusPinError, match="dirty"):
        cp.live_revision(str(root))
    with pytest.raises(cp.CorpusPinError, match="dirty"):
        cp.assert_unmoved(got, str(root))


def test_live_revision_not_a_checkout(tmp_path):
    with pytest.raises(cp.CorpusPinError, match="None"):
        cp.live_revision(str(tmp_path))


def test_write_pinned_source_refuses_without_revision(tmp_path):
    for bad in (None, {}, {"revision": None}, {"revision": "MIXED"}):
        with pytest.raises(cp.CorpusPinError):
            cp.write_pinned_source(str(tmp_path / "x.csv"), "s.py", 1, bad)
    assert not (tmp_path / "x.csv.source.json").exists()
