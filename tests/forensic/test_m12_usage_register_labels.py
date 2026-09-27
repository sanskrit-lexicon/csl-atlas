"""Pins for M12 — usage/register-label census (H5333, 24-09-2026).

Hand derivations (from the published mapping table, scripts/lexico/m12_usage_register_labels.py):

* normalisation runs AFTER stripping paired bracket punctuation `().,:;` from both
  ends — so `(Ved.` → `Ved` → VEDIC; `Fig.` → `Fig` → FIGURATIVE (case kept:
  `fig`/`Fig` are two raw rows of one label); `Lexicogrr.` → LEXICOGRAPHERS_ONLY.
* a `<lang>` token absent from the mapping is a true language name
  (`Lat.` → unmapped → language_name_tags), never a register row.
* bare (tag-stripped) residue counting is by label iteration order
  VEDIC, EPIC, POETIC, LEXICOGRAPHERS_ONLY — one pass per label, in that order.
* fixture dictionary (3 records, synthetic `mw`):
  - rec1: `<lang>Ved.</lang> <ab>fig.</ab>`          → VEDIC lang 1, FIGURATIVE ab 1
  - rec2: `(<ab>Ved.</ab>) <ab>Lexicogrr.</ab> poet.` → VEDIC ab 1, LEXICOGRAPHERS_ONLY ab 1,
    bare POETIC 1 (the bare `poet.` sits OUTSIDE any tag)
  - rec3: `<lang>Lat.</lang>`                        → language_name_tags 1, no register row
  → records 3; VEDIC total 2 → rate 2×1000/3 = 666.67/1k; totals 5 tagged + 1 bare + 1 language name.
"""

import json
import pathlib
import sys
from collections import Counter

LEXICO = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "lexico"
if str(LEXICO) not in sys.path:
    sys.path.insert(0, str(LEXICO))

import m12_usage_register_labels as m12  # noqa: E402

S = "m12_usage_register_labels"


def test_normalization_strips_brackets_keeps_case(pin):
    pin(S, "normalize((Ved.)", ("VEDIC", "register"), m12.normalize_token("(Ved."))
    pin(S, "normalize(ved.)", ("VEDIC", "register"), m12.normalize_token("ved."))
    pin(S, "normalize(epic.)", ("EPIC", "register"), m12.normalize_token("epic."))
    pin(S, "normalize(klass.)", ("CLASSICAL", "register"), m12.normalize_token("klass."))
    pin(S, "normalize(nachved.)", ("POST_VEDIC", "register"), m12.normalize_token("nachved."))
    pin(S, "normalize(Lexicogrr.)", ("LEXICOGRAPHERS_ONLY", "register"),
        m12.normalize_token("Lexicogrr."))
    pin(S, "normalize(Lexicc.)", ("LEXICOGRAPHERS_ONLY", "register"),
        m12.normalize_token("Lexicc."))
    pin(S, "normalize(liturg.)", ("LITURGICAL", "register"), m12.normalize_token("liturg."))
    pin(S, "normalize(Fig.)", ("FIGURATIVE", "register"), m12.normalize_token("Fig."))
    pin(S, "normalize(Prākṛt)", ("PRAKRIT", "middle_indic"), m12.normalize_token("Prākṛt"))
    pin(S, "normalize(Pāli)", ("PALI", "middle_indic"), m12.normalize_token("Pāli"))
    pin(S, "normalize(Apabhraṃśa.)", ("APABHRAMSA", "middle_indic"),
        m12.normalize_token("Apabhraṃśa."))


def test_unmapped_lang_token_is_not_a_register(pin):
    pin(S, "normalize(Lat.)", (None, None), m12.normalize_token("Lat."))
    pin(S, "normalize(Mar.)", (None, None), m12.normalize_token("Mar."))
    pin(S, "normalize(English)", (None, None), m12.normalize_token("English"))


def test_scan_line_surfaces(pin):
    line = "{#aMhUraRa#}¦ {%<lex>a.</lex>%} (<ab>Ved.</ab>) <lang>Lat.</lang> trouble"
    ab, lang = m12.scan_line(line)
    pin(S, "scan_line(ab)", ["Ved."], ab)
    pin(S, "scan_line(lang)", ["Lat."], lang)


def test_scan_bare_counts_by_label_order(pin):
    line = "<lex>m.</lex> a poet. word, Ved. too; ep. usage, lex. hedge"
    pin(S, "scan_bare(order)",
        ["VEDIC", "EPIC", "POETIC", "LEXICOGRAPHERS_ONLY"], m12.scan_bare(line))
    pin(S, "scan_bare(none)", [], m12.scan_bare("<ab>cf.</ab> plain text only"))


def test_fixture_census(tmp_path, pin):
    csl = tmp_path / "v02"
    d = csl / "mw"
    d.mkdir(parents=True)
    (d / "mw.txt").write_text(
        "<L>1<pc>1,1</pc><k1>a<1>k1</k1>¦ <lang>Ved.</lang> <ab>fig.</ab> tending\n"
        "<L>2<pc>1,1</pc><k1>b<1>k2</k1>¦ (<ab>Ved.</ab>) <ab>Lexicogrr.</ab> poet.\n"
        "<L>3<pc>1,2</pc><k1>c<1>k3</k1>¦ <lang>Lat.</lang> language name only\n",
        encoding="utf-8")
    out = tmp_path / "out"
    m12.main(["--dicts", "mw", "--csl", str(csl), "--out", str(out)])
    env = json.loads((out / "usage_register_labels.json").read_text(encoding="utf-8"))
    mw = env["perDict"][0]
    pin(S, "fixture(records)", 3, mw["records"])
    pin(S, "fixture(vedic.ab)", 1, mw["tagged"]["VEDIC"]["ab"])
    pin(S, "fixture(vedic.lang)", 1, mw["tagged"]["VEDIC"]["lang"])
    pin(S, "fixture(figurative.ab)", 1, mw["tagged"]["FIGURATIVE"]["ab"])
    pin(S, "fixture(lexicographers.ab)", 1, mw["tagged"]["LEXICOGRAPHERS_ONLY"]["ab"])
    pin(S, "fixture(untagged.poetic)", 1, mw["untagged_core"]["POETIC"])
    pin(S, "fixture(language_name_tags)", 1, mw["language_name_tags"])
    rows = (out / "usage_register_labels_counts.csv").read_text(encoding="utf-8").splitlines()
    vedic = [r for r in rows if "VEDIC" in r][0]
    pin(S, "fixture(rate.vedic_per_1000)", "666.67", vedic.split(",")[-1])
    mrows = (out / "usage_register_labels_map.csv").read_text(encoding="utf-8").splitlines()
    pin(S, "fixture(map.rows)", 4, len(mrows) - 1)  # Ved/lang, fig, Ved/ab, Lexicogrr
    assert Counter(mw["tagged"])  # structure sanity: tagged is a non-empty dict
