"""Pins for ``f3_gloss`` (H4352).

``corr`` is pure; ``gloss_len_map`` reads ``CSL_ORIG/<code>/<code>.txt``
(repointed at tmp). main() iterates its fixed PAIRS list, so the tmp corpus
carries all five dicts (pwg, pw, ap, ben, mw); ``f3_report.json`` and the CSV
are the dry-run surface.

Hand derivation. Gloss lengths chosen so log1p values are equally spaced
(1+L = 2, 4, 8 -> log2·{1,2,3}), which makes the reversed order an EXACT
Pearson of -1:
    mw   a:"x" 1   b:"xxx" 3   c:"xxxxxxx" 7   e:"q" (no partner)
    pwg  a:{%y%} 1  b:{%yyy%} 3  c:{%yyyyyyy%} 7  d:{%w%} (not in MW)
         f: no German span -> length 0 -> excluded from "shared glossed"
    pw   a 1  b 3                     -> shared 2 (<3) -> corr returns (0,0)
    ap   a 7  b 3  c 1                -> reversed -> pearson -1, spearman -1
    ben  a 1  b 1  c 1                -> constant -> both 0
    PWG->MW shared 3, 1.0/1.0 ; differential = spearman(PWG) - spearman(AP)
                                              = 1.0 - (-1.0) = 2.0
"""

import csv
import json

import pytest

import f3_gloss as f3
from conftest import write_text


def _entry(k1, body):
    return f"<L>1<pc>1-1<k1>{k1}<k2>{k1}\n{body}\n<LEND>\n"


def _corpus(root, spec):
    for code, entries in spec.items():
        write_text(root / code / f"{code}.txt", "".join(_entry(k, b) for k, b in entries))


POSITIVE = {
    "mw": [("a", "x"), ("b", "xxx"), ("c", "xxxxxxx"), ("e", "q")],
    "pwg": [("a", "{%y%}"), ("b", "{%yyy%}"), ("c", "{%yyyyyyy%}"), ("d", "{%w%}"), ("f", "no german")],
    "pw": [("a", "{%y%}"), ("b", "{%yyy%}")],
    "ap": [("a", "xxxxxxx"), ("b", "xxx"), ("c", "x")],
    "ben": [("a", "{%y%}"), ("b", "{%y%}"), ("c", "{%y%}")],
}
NULL = {
    "mw": [("a", "x"), ("b", "xxx"), ("c", "xxxxxxx")],
    "pwg": [("p", "{%y%}"), ("q", "{%yyy%}")],
    "pw": [("p", "{%y%}")],
    "ap": [("p", "xxxxxxx"), ("q", "xxx")],
    "ben": [("p", "{%y%}")],
}


def _run(tmp_path, monkeypatch, forensic_cwd, spec):
    root = tmp_path / "csl-orig"
    _corpus(root, spec)
    monkeypatch.setattr(f3, "CSL_ORIG", str(root))
    f3.main()
    report = json.loads((forensic_cwd / "data/forensic/f3_report.json").read_text(encoding="utf-8"))
    with open(forensic_cwd / "data/forensic/gloss_length_correlation.csv", encoding="utf-8") as fh:
        rows = {r["source"]: r for r in csv.DictReader(fh)}
    return report, rows


def test_corr_hand_values(pin):
    pin("f3", "corr.proportional", (1.0, 1.0), tuple(round(v, 6) for v in f3.corr([1, 2, 3], [2, 4, 6])))
    pin("f3", "corr.reversed", (-1.0, -1.0), tuple(round(v, 6) for v in f3.corr([1, 2, 3], [3, 2, 1])))
    pin("f3", "corr.too_few", (0.0, 0.0), f3.corr([1, 2], [1, 2]))
    pin("f3", "corr.constant", (0.0, 0.0), f3.corr([1, 1, 1], [1, 2, 3]))
    # tie handling: ranks of [1,1,2] are [1.5,1.5,3]; both coefficients = 1/sqrt(4/3) = 0.866
    p, s = f3.corr([1, 1, 2], [1, 2, 3])
    pin("f3", "corr.tied_ranks", (pytest.approx(0.866025, abs=1e-6), pytest.approx(0.866025, abs=1e-6)), (p, s))


def test_gloss_len_map_sums_entries_per_k1(tmp_path, monkeypatch, pin):
    root = tmp_path / "csl-orig"
    write_text(root / "pwg" / "pwg.txt",
               _entry("agni", "{#agni#} {%Feuer%} und {%Gott%}") + _entry("agni", "{%Glut%}")
               + _entry("deva", "kein deutsch"))
    write_text(root / "mw" / "mw.txt", _entry("agni", "agni ¦ <b>fire</b> the god") + _entry("agni", "x"))
    monkeypatch.setattr(f3, "CSL_ORIG", str(root))
    de = f3.gloss_len_map("PWG", "de")
    # "Feuer Gott" (10) + "Glut" (4) = 14 ; deva has no {%..%} span -> 0
    pin("f3", "gloss_len.de.agni", 14, de["agni"])
    pin("f3", "gloss_len.de.deva", 0, de["deva"])
    en = f3.gloss_len_map("MW", "en")
    # "agni fire the god" (17) + "x" (1) = 18 (tags, braces and ¦ stripped, spaces collapsed)
    pin("f3", "gloss_len.en.agni", 18, en["agni"])


def test_positive_fixture_differential(tmp_path, monkeypatch, forensic_cwd, pin):
    report, rows = _run(tmp_path, monkeypatch, forensic_cwd, POSITIVE)
    pin("f3", "rows", 4, len(rows))
    pin("f3", "PWG.shared_glossed_lemmas", "3", rows["PWG"]["shared_glossed_lemmas"])
    pin("f3", "PWG.corr", ("1.0", "1.0"), (rows["PWG"]["pearson_loglen"], rows["PWG"]["spearman_loglen"]))
    pin("f3", "PW.shared_glossed_lemmas", "2", rows["PW"]["shared_glossed_lemmas"])
    pin("f3", "PW.corr(<3 -> 0)", ("0.0", "0.0"), (rows["PW"]["pearson_loglen"], rows["PW"]["spearman_loglen"]))
    pin("f3", "AP.corr", ("-1.0", "-1.0"), (rows["AP"]["pearson_loglen"], rows["AP"]["spearman_loglen"]))
    pin("f3", "BEN.corr(constant)", ("0.0", "0.0"), (rows["BEN"]["pearson_loglen"], rows["BEN"]["spearman_loglen"]))
    pin("f3", "differential_pwg_minus_ap_spearman", 2.0, report["differential_pwg_minus_ap_spearman"])
    pin("f3", "report.pairs.source_lang", ["de", "de", "en", "de"], [p["source_lang"] for p in report["pairs"]])


def test_null_fixture_no_shared_lemmas(tmp_path, monkeypatch, forensic_cwd, pin):
    report, rows = _run(tmp_path, monkeypatch, forensic_cwd, NULL)
    pin("f3", "null.shared", ["0", "0", "0", "0"],
        [rows[c]["shared_glossed_lemmas"] for c in ("PWG", "PW", "AP", "BEN")])
    pin("f3", "null.PWG.corr", ("0.0", "0.0"), (rows["PWG"]["pearson_loglen"], rows["PWG"]["spearman_loglen"]))
    pin("f3", "null.differential", 0.0, report["differential_pwg_minus_ap_spearman"])
