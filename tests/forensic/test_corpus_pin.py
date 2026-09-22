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


def _sidecar(path, revision):
    write_text(path.parent / f"{path.name}.source.json",
               json.dumps({"csl_orig": {"revision": revision}} if revision else {"stage": 8}))


def test_inherited_revision_one_upstream_revision(tmp_path, pin):
    """H5260: F8 presence/verify read only derived CSVs and inherit their pin."""
    _sidecar(tmp_path / "a.csv", FIXTURE_REVISION)
    _sidecar(tmp_path / "b.csv", FIXTURE_REVISION)
    got = cp.inherited_revision([str(tmp_path / "a.csv"), str(tmp_path / "b.csv")])
    pin("corpus_pin", "inherited.revision", (FIXTURE_REVISION, "inherited"), (got["revision"], got["via"]))


@pytest.mark.parametrize("case", ["unpinned", "missing", "mixed", "empty"])
def test_inherited_revision_refuses(tmp_path, case):
    _sidecar(tmp_path / "a.csv", FIXTURE_REVISION)
    if case == "unpinned":
        _sidecar(tmp_path / "b.csv", None)
    elif case == "mixed":
        _sidecar(tmp_path / "b.csv", "e" * 40)
    paths = [] if case == "empty" else [str(tmp_path / "a.csv"), str(tmp_path / "b.csv")]
    with pytest.raises(cp.CorpusPinError, match="MIXED" if case == "mixed" else "None"):
        cp.inherited_revision(paths)


def test_assert_same_refuses_a_live_read_on_another_revision():
    live = {"revision": "a" * 40, "via": "live_checkout"}
    cp.assert_same(live, {"revision": "a" * 40, "via": "inherited"})
    with pytest.raises(cp.CorpusPinError, match="MIXED"):
        cp.assert_same(live, {"revision": "b" * 40, "via": "inherited"})


def test_input_revisions_mode_flip_is_not_dirt_but_an_edit_is(tmp_path, pin):
    """H5260: a hook installer's chmod on a tracked file changes no corpus byte and
    must not refuse; a content edit must (live probe on ../csl-corrections, 22-09-2026)."""
    root = tmp_path / "csl-corrections"
    write_text(root / "hook.sh", "#!/bin/sh\n")
    write_text(root / "mw" / "printchange_mw.txt", "x\n")
    head = git_commit_all(root)
    (root / "hook.sh").chmod(0o755)
    got = cp.input_revisions({"csl-corrections": str(root)})
    pin("corpus_pin", "inputs.mode_flip_clean", head, got["csl-corrections"]["revision"])
    write_text(root / "mw" / "printchange_mw.txt", "edited\n")
    with pytest.raises(cp.CorpusPinError, match="csl-corrections: input checkout .* is dirty"):
        cp.input_revisions({"csl-corrections": str(root)})


def test_write_pinned_source_with_inputs(tmp_path, pin):
    inputs = {"PWG/pwgissues": {"revision": "a" * 40, "via": "live_checkout"}}
    cp.write_pinned_source(str(tmp_path / "x.csv"), "s.py", 4, None, inputs=inputs)
    side = json.loads((tmp_path / "x.csv.source.json").read_text(encoding="utf-8"))
    pin("corpus_pin", "inputs.sidecar", (False, None, inputs),
        (side["csl_orig"]["read"], side["csl_orig"]["revision"], side["inputs"]))
    for bad in ({}, {"PWG": {"revision": None}}):
        with pytest.raises(cp.CorpusPinError, match="every input revision"):
            cp.write_pinned_source(str(tmp_path / "y.csv"), "s.py", 4, None, inputs=bad)
    assert not (tmp_path / "y.csv.source.json").exists()
