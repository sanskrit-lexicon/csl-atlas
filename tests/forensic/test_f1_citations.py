"""Pins for ``f1_citations`` (H4352).

``norm_ref`` / ``source_of`` / ``build`` are pure (build reads the parsed cache,
repointed at tmp). main() is the dry-run surface: it reads
``_parse_stats.json`` + ``<code>.tsv`` from ``PARSED_DIR`` and writes
``f1_report.json`` + two CSVs into the cwd. Limitation: ``MIN_CIT`` (500) is
lowered to 1 so four-citation fixtures join; every other constant is the
script's own. main() hard-codes ``smoking("PW","MW")`` so a ``pw.tsv`` must be
present or it raises KeyError — recorded as a script limitation.

Hand derivation, positive fixture (parsed caches):
    pwg  agni: P. 1,1,14 | MBH. 3,45      deva: R. 2,2      indra: MBH. 1,1
    mw   agni: P. | MBH. 3,45             deva: AV. 1,1     soma:  R. 5,5
    pw   soma: R. 5,5
    ap   agni: MBH. 3,45
norm_ref: upper, trailing ". ,;" stripped -> mw "P." becomes the bare sigil "P".
source_of: text before the first digit -> P / MBH / R / AV.
codes (>=1 <ls>) sorted: AP, MW, PW, PWG -> 6 pair combinations, 4 with a shared
cited lemma:
    AP/MW   agni: src {MBH} vs {P,MBH} -> jaccard 1/2 ; exact {MBH. 3,45}=1 ; no trunc
    AP/PWG  agni: {MBH} vs {P,MBH}     -> 1/2 ; exact 1 ; no trunc
    MW/PW   soma: {R} vs {R}           -> 1.0 ; exact {R. 5,5}=1 ; comparable 1
    MW/PWG  agni: {P,MBH} vs {P,MBH}   -> 1.0 ; exact {MBH. 3,45}=1 ;
                  source P: PWG has the full "P. 1,1,14", MW only the bare "P"
                  -> a_truncates_b (a=MW) += 1 ; comparable 2
            deva: {AV} vs {R}          -> 0 ; exact 0
            mean jaccard (1.0+0)/2 = 0.5 ; shared lemmas 2 (indra/soma unshared)
Smoking guns (ref cited for <=4 lemmas corpus-wide, exact match on the same lemma):
    PWG->MW agni MBH. 3,45 (1 lemma cites it) ; PW->MW soma R. 5,5 (1) -> 2 guns
"""

import csv
import json

import f1_citations as f1
import parse_cslorig
from conftest import write_text, write_tsv


def _stats(parsed, cites):
    write_text(parsed / "_parse_stats.json",
               json.dumps([{"code": c, "entries": 3, "citations": n, "with_homonym": 0}
                           for c, n in cites.items()]))


def _positive(parsed):
    write_tsv(parsed / "pwg.tsv", [
        (1, "agni", "agni", "", "", 2, "P. 1,1,14|MBH. 3,45"),
        (2, "deva", "deva", "", "", 1, "R. 2,2"),
        (3, "indra", "indra", "", "", 1, "MBH. 1,1"),
    ])
    write_tsv(parsed / "mw.tsv", [
        (1, "agni", "agni", "", "", 2, "P.|MBH. 3,45"),
        (2, "deva", "deva", "", "", 1, "AV. 1,1"),
        (3, "soma", "soma", "", "", 1, "R. 5,5"),
    ])
    write_tsv(parsed / "pw.tsv", [(1, "soma", "soma", "", "", 1, "R. 5,5")])
    write_tsv(parsed / "ap.tsv", [(1, "agni", "agni", "", "", 1, "MBH. 3,45")])
    _stats(parsed, {"pwg": 4, "mw": 4, "pw": 1, "ap": 1})


def _null(parsed):
    """Shared lemmas, disjoint apparatus: zero shared sources, zero exact refs."""
    write_tsv(parsed / "pwg.tsv", [(1, "agni", "agni", "", "", 1, "P. 1,1")])
    write_tsv(parsed / "mw.tsv", [(1, "agni", "agni", "", "", 1, "AV. 2,2")])
    write_tsv(parsed / "pw.tsv", [(1, "soma", "soma", "", "", 1, "R. 1")])
    _stats(parsed, {"pwg": 1, "mw": 1, "pw": 1})


def _run(tmp_path, monkeypatch, forensic_cwd, build):
    parsed = tmp_path / "parsed"
    build(parsed)
    monkeypatch.setattr(parse_cslorig, "PARSED_DIR", str(parsed))
    monkeypatch.setattr(f1, "PARSED_DIR", str(parsed))
    monkeypatch.setattr(f1, "MIN_CIT", 1)
    f1.main()
    report = json.loads((forensic_cwd / "data/forensic/f1_report.json").read_text(encoding="utf-8"))
    with open(forensic_cwd / "data/forensic/citation_pair_overlap.csv", encoding="utf-8") as fh:
        pairs = list(csv.DictReader(fh))
    with open(forensic_cwd / "data/forensic/shared_rare_citations.csv", encoding="utf-8") as fh:
        guns = list(csv.DictReader(fh))
    return report, pairs, guns


def test_norm_ref_and_source_of():
    assert f1.norm_ref("  p.  1,1,14 . ") == "P. 1,1,14"
    assert f1.norm_ref("P.") == "P"
    assert f1.source_of("P. 1,1,14") == "P"
    assert f1.source_of("CHĀND. UP. 4,4,5") == "CHĀND. UP"
    assert f1.source_of("P") == "P"


def test_build_maps(tmp_path, monkeypatch, pin):
    parsed = tmp_path / "parsed"
    _positive(parsed)
    monkeypatch.setattr(parse_cslorig, "PARSED_DIR", str(parsed))
    full, src = f1.build("pwg")
    pin("f1", "build.pwg.cited_lemmas", 3, len(full))
    pin("f1", "build.pwg.agni.full", {"P. 1,1,14", "MBH. 3,45"}, full["agni"])
    pin("f1", "build.pwg.agni.src", {"P", "MBH"}, src["agni"])
    full_mw, src_mw = f1.build("mw")
    pin("f1", "build.mw.agni.full", {"P", "MBH. 3,45"}, full_mw["agni"])


def test_positive_fixture_pairs_and_guns(tmp_path, monkeypatch, forensic_cwd, pin):
    report, pairs, guns = _run(tmp_path, monkeypatch, forensic_cwd, _positive)
    pin("f1", "citation_dicts", ["AP", "MW", "PW", "PWG"], report["citation_dicts"])
    pin("f1", "n_pairs", 4, report["n_pairs"])
    pin("f1", "csv.pairs_rows", 4, len(pairs))
    by = {(r["dict_a"], r["dict_b"]): r for r in pairs}
    pin("f1", "MW/PWG.shared_cited_lemmas", "2", by[("MW", "PWG")]["shared_cited_lemmas"])
    pin("f1", "MW/PWG.mean_source_jaccard", "0.5", by[("MW", "PWG")]["mean_source_jaccard"])
    pin("f1", "MW/PWG.shared_exact_refs", "1", by[("MW", "PWG")]["shared_exact_refs"])
    pin("f1", "MW/PWG.truncation(a=MW trunc b, b trunc a)", ("1", "0"),
        (by[("MW", "PWG")]["a_truncates_b"], by[("MW", "PWG")]["b_truncates_a"]))
    pin("f1", "MW/PWG.comparable_sources", "2", by[("MW", "PWG")]["comparable_sources"])
    pin("f1", "MW/PW.row", ("1", "1.0", "1", "0", "0", "1"),
        tuple(by[("MW", "PW")][k] for k in ("shared_cited_lemmas", "mean_source_jaccard",
                                            "shared_exact_refs", "b_truncates_a",
                                            "a_truncates_b", "comparable_sources")))
    pin("f1", "AP/MW.row", ("1", "0.5", "1", "0", "0", "1"),
        tuple(by[("AP", "MW")][k] for k in ("shared_cited_lemmas", "mean_source_jaccard",
                                            "shared_exact_refs", "b_truncates_a",
                                            "a_truncates_b", "comparable_sources")))
    pin("f1", "csv.first_row_is_top_jaccard", ("MW", "PW"), (pairs[0]["dict_a"], pairs[0]["dict_b"]))
    pin("f1", "n_smoking_guns", 2, report["n_smoking_guns"])
    pin("f1", "guns", [("agni", "MBH. 3,45", "PWG", "MW", "1"), ("soma", "R. 5,5", "PW", "MW", "1")],
        [(g["lemma"], g["shared_ref"], g["source_dict"], g["inheritor"], g["corpus_lemmas_with_ref"]) for g in guns])
    pin("f1", "smoking_gun_sources", {"MBH": 1, "R": 1}, report["smoking_gun_sources"])
    pin("f1", "lineage.PWG/MW.exact", 1, report["lineage"]["PWG/MW"]["shared_exact_refs"])
    pin("f1", "lineage.keys", ["PWG/MW", "PW/MW"], list(report["lineage"]))
    pin("f1", "nulls.keys", ["AP/MW"], list(report["nulls"]))
    pin("f1", "top_pairs(>=500 shared)", [], report["top_pairs"])


def test_null_fixture_zero_shared_apparatus(tmp_path, monkeypatch, forensic_cwd, pin):
    report, pairs, guns = _run(tmp_path, monkeypatch, forensic_cwd, _null)
    pin("f1", "null.n_pairs", 1, report["n_pairs"])
    row = pairs[0]
    pin("f1", "null.pair", ("MW", "PWG"), (row["dict_a"], row["dict_b"]))
    pin("f1", "null.shared_cited_lemmas", "1", row["shared_cited_lemmas"])
    pin("f1", "null.mean_source_jaccard", "0.0", row["mean_source_jaccard"])
    pin("f1", "null.shared_exact_refs", "0", row["shared_exact_refs"])
    pin("f1", "null.comparable_sources", "0", row["comparable_sources"])
    pin("f1", "null.n_smoking_guns", 0, report["n_smoking_guns"])
    pin("f1", "null.csv.guns_rows", 0, len(guns))
    pin("f1", "null.smoking_gun_sources", {}, report["smoking_gun_sources"])
