"""Foundation pins for ``parse_cslorig`` (H4352).

Not one of the nine scripts named by the handoff, but every parsed-cache
fixture the f1 / f2 / f4b pins feed through ``load_entries`` has the shape this
module writes, so its arithmetic is pinned first. All counts below are counted
by hand on the fixture text.
"""

import parse_cslorig as pc
from conftest import write_text

# Three entries. Hand count: entry "a" carries 2 <ls> (one bare, one attributed
# through @n), entry "agni" carries 2 (one with an inner <i> tag, one whose @n
# holds a stray literal ">"), entry "soma" carries 0 and no homonym number.
MINI = """<L>1<pc>1-0001<k1>a<k2>a<h>1
1. {#a#} the first letter <ls>P. 1,1,14</ls> and <ls n="RV.">vii, 96, 3</ls>
<LEND>
<L>2<pc>1-0002<k1>agni<k2>agni
fire <ls><i>MBh.</i> 1, 2</ls>
second body line <ls n=">Dhātup. iii,">4</ls>
<LEND>
<L>3<pc>1-0003<k1>soma<k2>soma
no citations here
<LEND>
"""


def test_iter_entries_counts_and_citations(tmp_path, pin):
    src = write_text(tmp_path / "mini.txt", MINI)
    entries = list(pc.iter_entries(src))
    pin("parse_cslorig", "entries", 3, len(entries))
    a, agni, soma = entries
    pin("parse_cslorig", "a.L", "1", a["L"])
    pin("parse_cslorig", "a.h", "1", a["h"])
    pin("parse_cslorig", "a.citations", ["P. 1,1,14", "RV. vii, 96, 3"], a["citations"])
    pin("parse_cslorig", "agni.h", None, agni["h"])
    # inner <i> stripped; the malformed @n keeps its literal ">" (the regex only
    # guards against truncation, it does not sanitise the attribute).
    pin("parse_cslorig", "agni.citations", ["MBh. 1, 2", ">Dhātup. iii, 4"], agni["citations"])
    pin("parse_cslorig", "soma.citations", [], soma["citations"])
    pin("parse_cslorig", "total_ls", 4, sum(len(e["citations"]) for e in entries))


def test_clean_citation_joins_attr_and_content():
    assert pc.clean_citation("RV.", "vii, 96, 3") == "RV. vii, 96, 3"
    assert pc.clean_citation(None, "<i>MBh.</i>  1,  2") == "MBh. 1, 2"
    assert pc.clean_citation("", "") == ""


def test_null_unterminated_entry_yields_nothing(tmp_path, pin):
    """A header with no <LEND> is never emitted; an empty file yields zero."""
    src = write_text(tmp_path / "open.txt", "<L>1<pc>1-1<k1>a<k2>a\nbody\n")
    pin("parse_cslorig", "null.unterminated", 0, len(list(pc.iter_entries(src))))
    empty = write_text(tmp_path / "empty.txt", "")
    pin("parse_cslorig", "null.empty_file", 0, len(list(pc.iter_entries(empty))))


def test_build_cache_stats_and_roundtrip(tmp_path, monkeypatch, pin, capsys):
    root = tmp_path / "csl-orig"
    write_text(root / "mini" / "mini.txt", MINI)
    parsed = tmp_path / "parsed"
    monkeypatch.setattr(pc, "CSL_ORIG", str(root))
    monkeypatch.setattr(pc, "PARSED_DIR", str(parsed))
    stats = pc.build_cache("mini")
    pin("parse_cslorig", "cache.entries", 3, stats["entries"])
    pin("parse_cslorig", "cache.citations", 4, stats["citations"])
    pin("parse_cslorig", "cache.with_homonym", 1, stats["with_homonym"])
    rows = pc.load_entries("mini")
    pin("parse_cslorig", "roundtrip.rows", 3, len(rows))
    pin("parse_cslorig", "roundtrip.agni.n_cit", "2", rows[1]["n_cit"])
    pin("parse_cslorig", "roundtrip.agni.citations",
        ["MBh. 1, 2", ">Dhātup. iii, 4"], rows[1]["citations"])
    pin("parse_cslorig", "roundtrip.soma.citations", [], rows[2]["citations"])
    assert pc.build_cache("absent") is None
    assert "SOURCE MISSING" in capsys.readouterr().err
