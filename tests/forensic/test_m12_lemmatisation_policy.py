"""Pins for M12 — lemmatisation policy census (H5332, 24-09-2026).

Hand derivations (SLP1: ā=A ī=I ū=U ṛ=f ṭ=w ḍ=q ṅ=N ñ=Y ṇ=R ś=S ṣ=z ṃ=M ḥ=H, aspirates
uppercase K G C J W Q T D P B):

* transliteration: `bhū` → `BU` (bh is one aspirate, ū one vowel — a naive per-character
  map would give `bhU`); `kṛṣ` → `kfz`; `ṭhā` → `WA`; `saṃskṛta` → `saMskfta`.
* key shape: `akzaraH` visarga, `akzaraM` anusvāra, `akzara` vowel, `nAman` consonant.
* fixture dictionary (10 level-1 keys + 2 nested): deva, rAja, putra, devaputra (nested),
  rAjaputra, devatA, devatva, nAman, akzaraH, BU, gam, gacCati.
  - citation_policy: 1 of 11 level-1 keys inflected = 9.1 % → the mixed band (2–20 %);
    two keys are consonant-final (nAman and the root gam).
  - compounds: devaputra = deva+putra (both ≥ 3 chars, both keys) and rAjaputra =
    rAja+putra. Two hits, one nested (devaputra, `<e>2`) → nested_share 0.5, and 0.5 is
    below the 0.5-inclusive nesting threshold only if strictly less — it is not, so the
    verdict is the nested one. deva/rAja/putra themselves never split (a 4-char key cannot
    give two ≥ 3-char pieces).
  - derivatives: devatA = deva+tA and devatva = deva+tva; nAman does not end in a listed
    suffix with a key remainder. Both own heads → nested_share 0.
  - verbs against the roots [BU, gam, pac]: BU exact; gam exact; pac absent (no key starts
    with it). With BU removed from the keys, BU falls to `derived_only` only if some key
    extends it — none does, so it is `absent`; adding `BUmi` makes it `derived_only`, while
    adding `BUti` instead makes it `finite_form` (-ti is a tested present ending, -mi is not).
  - DCS bands {deva: 5, putra: 4, xyz: 1}: deva and putra exact, xyz absent → band 5
    covered 1.0, band 4 covered 1.0, band 1 covered 0.0.
"""

import pathlib
import sys

LEXICO = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "lexico"
if str(LEXICO) not in sys.path:
    sys.path.insert(0, str(LEXICO))

import m12_lemmatisation_policy as m12  # noqa: E402


def rec(k1, e="", L="1", pc="1"):
    return {"L": L, "pc": pc, "k1": k1, "e": e, "alias": False, "root": False}


FIXTURE = [
    rec("deva"), rec("rAja"), rec("putra"), rec("devaputra", e="2"), rec("rAjaputra"),
    rec("devatA"), rec("devatva"), rec("nAman"), rec("akzaraH"), rec("BU"), rec("gam"),
    rec("gacCati"),
]
KEYS = {r["k1"] for r in FIXTURE}
LEVEL1 = [r for r in FIXTURE if m12.e_level(r["e"]) == 1]


def test_iast_to_slp1_longest_match_first():
    assert m12.iast_to_slp1("bhū") == "BU"
    assert m12.iast_to_slp1("kṛṣ") == "kfz"
    assert m12.iast_to_slp1("ṭhā") == "WA"
    assert m12.iast_to_slp1("saṃskṛta") == "saMskfta"
    assert m12.iast_to_slp1("gam") == "gam"


def test_slp1_to_iast_round_trip_on_the_roots():
    for iast in ("bhū", "kṛṣ", "ṭhā", "saṃskṛta"):
        assert m12.slp1_to_iast(m12.iast_to_slp1(iast)) == iast


def test_final_shape():
    assert m12.final_shape("akzaraH") == "visarga"
    assert m12.final_shape("akzaraM") == "anusvara"
    assert m12.final_shape("akzara") == "vowel"
    assert m12.final_shape("nAman") == "consonant"
    assert m12.final_shape("") == "empty"


def test_citation_policy_counts_and_band():
    block, off = m12.citation_policy(LEVEL1)
    assert block["headwords"] == 11
    assert block["shapes"]["visarga"] == 1
    assert block["shapes"]["consonant"] == 2          # nAman, gam
    assert round(block["inflected_share"], 4) == round(1 / 11, 4)
    assert block["verdict"].startswith("mixed")
    assert [r["k1"] for r in off] == ["akzaraH"]      # the minority side


def test_compound_split_is_self_referential():
    block, off = m12.split_policy(FIXTURE, KEYS, "compound")
    assert block["detected"] == 2                     # devaputra, rAjaputra
    assert block["nested"] == 1 and block["own_head"] == 1
    assert block["nested_share"] == 0.5
    assert block["nesting_recorded"] is True
    assert [r["k1"] for r in off] == ["rAjaputra"]    # own head is the minority


def test_derivative_suffix_test():
    block, off = m12.split_policy(FIXTURE, KEYS, "derivative")
    assert block["detected"] == 2                     # devatA, devatva
    assert block["nested"] == 0
    assert block["verdict"].startswith("own head")
    assert list(block["suffix_profile"]) == ["tva", "tā"]
    assert off == []


def test_nesting_not_recorded_qualifies_the_verdict():
    flat = [rec(r["k1"]) for r in FIXTURE]
    block, _ = m12.split_policy(flat, KEYS, "compound")
    assert block["nesting_recorded"] is False
    assert "csl-orig records" in block["verdict"]


def prefix_index(keys):
    idx = {}
    for k in keys:
        idx.setdefault(k[:m12.MIN_ROOT], []).append(k)
    return idx


def test_verb_buckets():
    roots = ["BU", "gam", "pac"]
    block, buckets = m12.verb_policy(KEYS, prefix_index(KEYS), roots, 0)
    assert buckets["root_exact"] == ["BU", "gam"]
    assert buckets["absent"] == ["pac"]
    assert block["whitney_roots_tested"] == 3

    without = {k for k in KEYS if k != "BU"}
    _, b2 = m12.verb_policy(without, prefix_index(without), roots, 0)
    assert b2["absent"] == ["BU", "pac"]

    with_deriv = without | {"BUmi"}                   # -mi is not a tested present ending
    _, b3 = m12.verb_policy(with_deriv, prefix_index(with_deriv), roots, 0)
    assert b3["derived_only"] == ["BU"]

    with_finite = without | {"BUti"}                  # -ti is, so the same shape moves bucket
    _, b4 = m12.verb_policy(with_finite, prefix_index(with_finite), roots, 0)
    assert b4["finite_form"] == ["BU"] and b4["derived_only"] == []
    assert b4["root_exact"] == ["gam"]                # gam keeps its own exact headword


def test_citation_root_branch():
    keys = {"BUH", "gamH"}
    block, buckets = m12.verb_policy(keys, prefix_index(keys), ["BU", "gam"], 0)
    assert buckets["citation_root"] == ["BU", "gam"]
    assert block["verdict"].startswith("citation-form root")


def test_dcs_bands_are_the_strata():
    block, missing = m12.dcs_policy(KEYS, {"deva": 5, "putra": 4, "xyz": 1})
    assert block["bands"][5]["covered_share"] == 1.0
    assert block["bands"][4]["exact"] == 1
    assert block["bands"][1]["absent"] == 1
    assert block["covered"] == 2 and block["lemmas"] == 3
    assert missing[1] == ["xyz"]


def test_whitney_parse(tmp_path):
    src = tmp_path / "whitney.txt"
    src.write_text(
        "====\n"
        "   1. aṃh                    —\n"
        "   2. 1 √akṣ                 I\n"
        "   3. 2 √akṣ                 I\n"
        "   4. √aṅg                   I\n"
        "  99. ā                      —\n",
        encoding="utf-8")
    roots = m12.whitney_roots(str(src))
    assert roots == ["aMh", "akz", "aNg"]             # homonyms collapse, 1-char ā drops


def test_thresholds_are_declared():
    assert m12.THRESH["citation_form_min"] == 0.20
    assert m12.THRESH["root_form_min"] == 0.60
    assert m12.THRESH["nesting_min"] == 0.50
