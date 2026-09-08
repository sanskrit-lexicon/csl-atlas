"""Pins for ``f2_structure`` (H4352).

``hcount_map`` is pinned directly against a parsed-cache fixture. main() is the
dry-run surface: it reads ``_parse_stats.json`` + every ``*.tsv`` in
``PARSED_DIR`` and writes ``f2_report.json`` + two CSVs. Limitation:
``MIN_HOM`` (1000) is lowered to 1 so a small stats file admits MW and PWG; the
``len(split) < 20`` pair floor is hard-coded inside main(), so the fixture
carries 22+ shared split headwords. The fixture rows are written by a test-side
loop (not by any script); the counts below are hand-derived from that loop.

Hand derivation (parsed caches mw / pwg; ap carries every shared key unsplit so
they stay out of the raw pool; pw carries only pool probes):
    h01..h20  2 homonyms in BOTH                 -> split, agree        (20)
    h21, h22  PWG 2 homonyms, MW unsplit (=1)    -> split, disagree     (2)
    d1        3 in both                          -> split+deep, agree   (1)
    d2        PWG 3, MW 4                        -> split+deep, disagree(1)
    u1        unsplit in both                    -> shared, not split
    zz1 mw+pwg only ; zz2 mw+pw only ; zz3 mw+pwg+pw ; zz4 pwg+pw
  shared(MW,PWG) = 22+2+1 + zz1 + zz3 = 27
  split_in_either = 24 ; agree_on_count = 21 ; rate 21/24 = 0.875
  deep_split_both_3plus = 2 ; deep_agree = 1 ; rate 0.5
  raw pool (k1 in exactly {MW, one Petersburg}) = zz2 (PW), zz1 (PWG) -> 2
"""

import csv
import json

import f2_structure as f2
import parse_cslorig
from conftest import write_text, write_tsv


def _rows(spec):
    """spec: list of (k1, n_homonyms). n=1 -> one row with an empty <h>."""
    out, L = [], 0
    for k1, n in spec:
        if n == 1:
            L += 1
            out.append((L, k1, k1, "", "", 0, ""))
        else:
            for h in range(1, n + 1):
                L += 1
                out.append((L, k1, k1, h, "", 0, ""))
    return out


SHARED = [f"h{i:02d}" for i in range(1, 21)] + ["h21", "h22", "d1", "d2", "u1"]


def _positive(parsed):
    pwg = [(f"h{i:02d}", 2) for i in range(1, 21)] + [("h21", 2), ("h22", 2), ("d1", 3), ("d2", 3),
                                                       ("u1", 1), ("zz1", 1), ("zz3", 1), ("zz4", 1)]
    mw = [(f"h{i:02d}", 2) for i in range(1, 21)] + [("h21", 1), ("h22", 1), ("d1", 3), ("d2", 4),
                                                      ("u1", 1), ("zz1", 1), ("zz2", 1), ("zz3", 1)]
    write_tsv(parsed / "pwg.tsv", _rows(pwg))
    write_tsv(parsed / "mw.tsv", _rows(mw))
    write_tsv(parsed / "ap.tsv", _rows([(k, 1) for k in SHARED]))
    write_tsv(parsed / "pw.tsv", _rows([("zz2", 1), ("zz3", 1), ("zz4", 1)]))
    # with_homonym counted by hand from the rows above: pwg 40+4+3+3 = 50, mw 40+0+3+4 = 47
    write_text(parsed / "_parse_stats.json", json.dumps([
        {"code": "pwg", "entries": 52, "citations": 0, "with_homonym": 50},
        {"code": "mw", "entries": 50, "citations": 0, "with_homonym": 47},
        {"code": "ap", "entries": 25, "citations": 0, "with_homonym": 0},
        {"code": "pw", "entries": 3, "citations": 0, "with_homonym": 0},
    ]))


def _null(parsed):
    """PWG splits twenty headwords MW never splits: zero agreement, zero deep
    splits, and every shared key also in AP so the raw pool is empty."""
    keys = [f"h{i:02d}" for i in range(1, 21)]
    write_tsv(parsed / "pwg.tsv", _rows([(k, 2) for k in keys]))
    write_tsv(parsed / "mw.tsv", _rows([(k, 1) for k in keys]))
    write_tsv(parsed / "ap.tsv", _rows([(k, 1) for k in keys]))
    write_text(parsed / "_parse_stats.json", json.dumps([
        {"code": "pwg", "entries": 40, "citations": 0, "with_homonym": 40},
        {"code": "mw", "entries": 20, "citations": 0, "with_homonym": 1},
        {"code": "ap", "entries": 20, "citations": 0, "with_homonym": 0},
    ]))


def _run(tmp_path, monkeypatch, forensic_cwd, build):
    parsed = tmp_path / "parsed"
    build(parsed)
    monkeypatch.setattr(parse_cslorig, "PARSED_DIR", str(parsed))
    monkeypatch.setattr(f2, "PARSED_DIR", str(parsed))
    monkeypatch.setattr(f2, "MIN_HOM", 1)
    f2.main()
    report = json.loads((forensic_cwd / "data/forensic/f2_report.json").read_text(encoding="utf-8"))
    with open(forensic_cwd / "data/forensic/homonym_concordance.csv", encoding="utf-8") as fh:
        conc = list(csv.DictReader(fh))
    with open(forensic_cwd / "data/forensic/raw_headword_pool.csv", encoding="utf-8") as fh:
        pool = list(csv.DictReader(fh))
    return report, conc, pool


def test_hcount_map_hand_counts(tmp_path, monkeypatch, pin):
    parsed = tmp_path / "parsed"
    write_tsv(parsed / "x.tsv", _rows([("a", 3), ("b", 1), ("c", 2)]) + [(99, "c", "c", 2, "", 0, "")])
    monkeypatch.setattr(parse_cslorig, "PARSED_DIR", str(parsed))
    hc = f2.hcount_map("x")
    # c has two rows with <h>2 -> DISTINCT homonym numbers = 2, not 3
    pin("f2", "hcount_map", {"a": 3, "b": 1, "c": 2}, hc)


def test_positive_fixture_concordance_and_pool(tmp_path, monkeypatch, forensic_cwd, pin):
    report, conc, pool = _run(tmp_path, monkeypatch, forensic_cwd, _positive)
    pin("f2", "homonym_dicts", ["MW", "PWG"], report["homonym_dicts"])
    pin("f2", "n_pairs", 1, report["n_pairs"])
    row = conc[0]
    pin("f2", "pair", ("MW", "PWG"), (row["dict_a"], row["dict_b"]))
    pin("f2", "shared_headwords", "27", row["shared_headwords"])
    pin("f2", "split_in_either", "24", row["split_in_either"])
    pin("f2", "agree_on_count", "21", row["agree_on_count"])
    pin("f2", "agreement_rate", "0.875", row["agreement_rate"])
    pin("f2", "deep_split_both_3plus", "2", row["deep_split_both_3plus"])
    pin("f2", "deep_agree", "1", row["deep_agree"])
    pin("f2", "deep_agreement_rate", "0.5", row["deep_agreement_rate"])
    pin("f2", "raw_pool", (2, 1, 1), (report["raw_pool_total"], report["raw_pool_pwg"], report["raw_pool_pw"]))
    pin("f2", "raw_pool.csv", [("zz2", "PW"), ("zz1", "PWG")], [(p["raw_k1"], p["shared_with"]) for p in pool])
    pin("f2", "lineage.PWG/MW.agree", 21, report["lineage"]["PWG/MW"]["agree_on_count"])
    pin("f2", "nulls", {}, report["nulls"])


def test_null_fixture_zero_agreement_zero_pool(tmp_path, monkeypatch, forensic_cwd, pin):
    report, conc, pool = _run(tmp_path, monkeypatch, forensic_cwd, _null)
    row = conc[0]
    pin("f2", "null.shared_headwords", "20", row["shared_headwords"])
    pin("f2", "null.split_in_either", "20", row["split_in_either"])
    pin("f2", "null.agree_on_count", "0", row["agree_on_count"])
    pin("f2", "null.agreement_rate", "0.0", row["agreement_rate"])
    pin("f2", "null.deep", ("0", "0", "0.0"), (row["deep_split_both_3plus"], row["deep_agree"], row["deep_agreement_rate"]))
    pin("f2", "null.raw_pool_total", 0, report["raw_pool_total"])
    pin("f2", "null.raw_pool.csv_rows", 0, len(pool))
