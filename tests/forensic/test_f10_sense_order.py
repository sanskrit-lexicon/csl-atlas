"""Pins for ``f10_sense_order`` (H4352).

f10's segmentation, alignment and concordance functions are pure and pinned
directly. Its full main() needs argos-translate (offline MT) — not exercised;
the ``--census`` branch returns before any MT and is pinned as the dry-run
surface via captured stdout. ``null_concordance`` draws from an RNG, so it is
pinned with two hand-controlled shufflers (reverse / identity) instead of a seed.

Hand derivation, mini corpus (MIN_GLOSS_TOK=2: a chunk is a sense only with
>=2 English tokens of >=3 letters outside the STOP list):
  MW  go   record 1: "m. a cow bull ox"           -> {cow,bull}          (ox: 2 letters)
                     <div n="to"> "a ray of light beam" -> {ray,light,beam}
                     <div n="to"> "the earth ground<ls>MBh.</ls>" -> {earth,ground}
           record 1.1: "speech words language"    -> {speech,words,language}
           => 4 senses ;  deva "god deity" -> 1 sense
  PWG go   pre-<div> head dropped ; <div n=1> {%Rind, Kuh%} ; <div n=2> {%Strahl%} ;
           <div n=3> {%Erde%}                    => 3 senses ; deva {%Gott%} -> 1
  AP  go   head before the first ∙ dropped ; 4 bullets -> {cow,bull} {ray,beam}
           {earth,ground} {speech,words}         => 4 senses
  candidates (>=3 senses in both): MW∩PWG {go}=1 ; MW∩AP {go}=1
MW-vs-AP bags (no MT needed): jaccard (0,0)=1 (1,1)=2/3 (2,2)=1 (3,3)=2/3, rest 0
  -> greedy 1:1 matches all four on the diagonal -> concordance 1.0 ;
     mean match similarity (1+1+2/3+2/3)/4 = 0.8333 ; AP reversed -> 0.0
"""

import sys

import pytest

import f10_sense_order as f10
from conftest import write_text

MW_TXT = """<L>1<pc>1-1<k1>go<k2>go
go ¦ m. a cow bull ox <div n="to">a ray of light beam</div><div n="to">the earth ground<ls>MBh.</ls>
<LEND>
<L>1.1<pc>1-1<k1>go<k2>go
¦ speech words language
<LEND>
<L>2<pc>1-1<k1>deva<k2>deva
deva ¦ god deity
<LEND>
"""
PWG_TXT = """<L>1<pc>1-1<k1>go<k2>go
{#go#} ¦ m. <div n="1">1) {%Rind, Kuh%} <ls>MBH. 1,2</ls></div> <div n="2">2) {%Strahl%}</div> <div n="3">3) {%Erde%}</div>
<LEND>
<L>2<pc>1-1<k1>deva<k2>deva
{#deva#} ¦ {%Gott%}
<LEND>
"""
PWG_NULL_TXT = """<L>1<pc>1-1<k1>go<k2>go
{#go#} ¦ m. <div n="1">1) {%Rind, Kuh%}</div> <div n="2">2) {%Strahl%}</div>
<LEND>
"""
AP_TXT = """<L>1<pc>1-1<k1>go<k2>go
go ¦ m. ∙ a cow bull ∙ a ray beam ∙ the earth ground ∙ speech words
<LEND>
"""


def _corpus(tmp_path, pwg=PWG_TXT):
    root = tmp_path / "csl-orig"
    write_text(root / "mw" / "mw.txt", MW_TXT)
    write_text(root / "pwg" / "pwg.txt", pwg)
    write_text(root / "ap" / "ap.txt", AP_TXT)
    return root


def test_token_helpers():
    assert f10.toks_en("The Cow, a bull; ox and light") == {"cow", "bull", "light"}
    assert f10.toks_skt("<s>deva</s> {#agni/#} <s1>go\\</s1>") == {"deva", "agni", "go"}
    assert f10.strip_markup_en("fire <ls>MBh. 1</ls> <s>deva</s> {#x#} <b>god</b>") == "fire god"
    assert f10.jaccard({"a", "b"}, {"b", "c"}) == pytest.approx(1 / 3)
    assert f10.jaccard(set(), set()) == 0.0


def test_segmentation_hand_counts(tmp_path, pin):
    root = _corpus(tmp_path)
    mw = f10.group_by_k1(str(root / "mw" / "mw.txt"))
    pwg = f10.group_by_k1(str(root / "pwg" / "pwg.txt"))
    ap = f10.group_by_k1(str(root / "ap" / "ap.txt"))
    pin("f10", "group_by_k1.mw", {"go": 2, "deva": 1}, {k: len(v) for k, v in mw.items()})
    mw_go = f10.senses_mw(mw["go"])
    pin("f10", "senses_mw.go", 4, len(mw_go))
    pin("f10", "senses_mw.go.en",
        [{"cow", "bull"}, {"ray", "light", "beam"}, {"earth", "ground"}, {"speech", "words", "language"}],
        [s["en"] for s in mw_go])
    pin("f10", "senses_mw.deva", 1, len(f10.senses_mw(mw["deva"])))
    pwg_go = f10.senses_pwg(pwg["go"])
    pin("f10", "senses_pwg.go", 3, len(pwg_go))
    pin("f10", "senses_pwg.go.de", ["Rind, Kuh", "Strahl", "Erde"], [s["de"] for s in pwg_go])
    pin("f10", "senses_pwg.deva", 1, len(f10.senses_pwg(pwg["deva"])))
    ap_go = f10.senses_ap(ap["go"])
    pin("f10", "senses_ap.go", 4, len(ap_go))
    pin("f10", "senses_ap.go.en",
        [{"cow", "bull"}, {"ray", "beam"}, {"earth", "ground"}, {"speech", "words"}],
        [s["en"] for s in ap_go])


def test_concordance_and_matching(pin):
    cf = f10.concordant_fraction
    pin("f10", "concordant.identity", 1.0, cf([(0, 0), (1, 1), (2, 2)]))
    pin("f10", "concordant.reversed", 0.0, cf([(0, 2), (1, 1), (2, 0)]))
    pin("f10", "concordant.one_swap", pytest.approx(2 / 3), cf([(0, 0), (1, 2), (2, 1)]))
    pin("f10", "concordant.too_few", None, cf([(0, 0)]))
    # pairs sharing an index are skipped, leaving nothing to score -> None
    pin("f10", "concordant.shared_index_only", None, cf([(0, 0), (0, 1)]))
    sim = {(0, 0): 0.9, (0, 1): 0.8, (1, 1): 0.7, (1, 0): 0.1}
    pin("f10", "greedy_match", [(0, 0), (1, 1)], f10.greedy_match(sim))
    pin("f10", "greedy_match.empty", [], f10.greedy_match({}))


def test_score_headword_mw_vs_ap(tmp_path, pin):
    root = _corpus(tmp_path)
    mw = f10.senses_mw(f10.group_by_k1(str(root / "mw" / "mw.txt"))["go"])
    ap = f10.senses_ap(f10.group_by_k1(str(root / "ap" / "ap.txt"))["go"])
    mw_bags = [s["en"] | s["skt"] for s in mw]
    ap_bags = [s["en"] | s["skt"] for s in ap]
    cf, matches, n_other, msim = f10.score_headword(mw_bags, ap_bags)
    pin("f10", "score.concordance", 1.0, cf)
    pin("f10", "score.matches", 4, len(matches))
    pin("f10", "score.n_other", 4, n_other)
    pin("f10", "score.mean_sim", pytest.approx((1 + 1 + 2 / 3 + 2 / 3) / 4), msim)
    cf_rev, matches_rev, _, _ = f10.score_headword(mw_bags, list(reversed(ap_bags)))
    pin("f10", "score.reversed.concordance", 0.0, cf_rev)
    pin("f10", "score.reversed.matches", 4, len(matches_rev))
    # two senses only -> fewer than MIN_MATCHED matches -> no order verdict
    pin("f10", "score.too_few", None, f10.score_headword(mw_bags[:2], ap_bags[:2])[0])
    pin("f10", "score_floor.0.7_drops_two", None, f10.score_floor(mw_bags, ap_bags, 0.7))
    pin("f10", "score_floor.0.5_keeps_all", 1.0, f10.score_floor(mw_bags, ap_bags, 0.5))


def test_null_concordance_with_controlled_shuffle(pin):
    class Reverse:
        def shuffle(self, seq):
            seq.reverse()

    class Identity:
        def shuffle(self, seq):
            pass

    matches = [(0, 0), (1, 1), (2, 2)]
    pin("f10", "null_concordance.reversed", 0.0, f10.null_concordance(matches, 3, Reverse()))
    pin("f10", "null_concordance.identity", 1.0, f10.null_concordance(matches, 3, Identity()))
    pin("f10", "null_concordance.too_few", None, f10.null_concordance(matches[:2], 3, Identity()))


def test_census_surface_positive(tmp_path, monkeypatch, capsys, pin):
    root = _corpus(tmp_path)
    monkeypatch.setattr(f10, "CSL_ORIG", str(root))
    monkeypatch.setattr(sys, "argv", ["f10_sense_order.py", "--census"])
    f10.main()
    out = capsys.readouterr().out
    pin("f10", "census.k1_counts", True, "MW k1=2  PWG k1=2  AP k1=1" in out)
    pin("f10", "census.MW_vs_PWG", True, "MW vs PWG : 1" in out)
    pin("f10", "census.MW_vs_AP", True, "MW vs AP  : 1" in out)
    pin("f10", "census.pwg_glosses_to_translate", True, "to translate ~ 3" in out)


def test_census_surface_null(tmp_path, monkeypatch, capsys, pin):
    """PWG's go has only two Bedeutungen -> below MIN_SENSES -> zero candidates."""
    root = _corpus(tmp_path, pwg=PWG_NULL_TXT)
    monkeypatch.setattr(f10, "CSL_ORIG", str(root))
    monkeypatch.setattr(sys, "argv", ["f10_sense_order.py", "--census"])
    f10.main()
    out = capsys.readouterr().out
    pin("f10", "census.null.MW_vs_PWG", True, "MW vs PWG : 0" in out)
    pin("f10", "census.null.MW_vs_AP", True, "MW vs AP  : 1" in out)
