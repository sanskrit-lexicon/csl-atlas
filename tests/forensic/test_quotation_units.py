"""Pins for the PD quotation-level unit (H6949).

Every expected count below is derived BY HAND from the miniature entry body in
the test, never produced by running the parser. The rule under test is
``scripts/lib/quotation_units.py``: a quotation is a run of consecutive
``{#...#}`` blocks separated only by whitespace, immediately followed by a
citation marker; block 1 is the headword and is never a quotation.

Rationale and the corpus-level numbers: reports/PD_QUOTATION_UNIT_2026-10-18.md.
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
for p in (str(ROOT / "scripts"), str(ROOT / "scripts" / "lib")):
    if p not in sys.path:
        sys.path.insert(0, p)

import pd_quotation_units as pdq
import quotation_units


def _pd(body):
    return quotation_units.count_units(body, pdq.citation_tail)


def test_line_wrapped_quotation_is_one_quotation():
    # blocks 2 and 3 are one printed quotation split at a line wrap; 1 siglum
    body = "{#hw#} (%n.%) gloss {#a b#} {#c d#} ManuSm. 1. 2"
    u = _pd(body)
    assert u["slp1_blocks"] == 3
    assert u["quotations"] == 1
    assert u["blocks_in_quotations"] == 2
    assert u["attestations"] == 1


def test_block_count_is_not_the_quotation_count():
    # two quotations, three blocks: the block unit would report 3, the unit 2
    body = "{#hw#} {%n.%} {#q1#} {#q1b#} ManuSm. 1. 2; {#q2#} AgniP. 3. 4"
    u = _pd(body)
    assert u["slp1_blocks"] == 4
    assert u["quotations"] == 2
    assert u["blocks_in_quotations"] == 3


def test_headword_block_is_never_a_quotation():
    body = "{#hw#} {%n.%} {#q#} ManuSm. 1. 2"
    u = _pd(body)
    assert u["headword_block"] == 1
    assert u["quotations"] == 1
    assert u["blocks_in_quotations"] == 1


def test_etymology_morphemes_are_not_quotations():
    # ({#a#} + {#kAmatas#}) is an etymology, not a citation-bearing passage
    body = "{#a-kAmatas#}\u00a6 ({#a#} + {#kAmatas#}) {%adv.%} {#svapne siktvA#} ManuSm. 2. 181"
    u = _pd(body)
    assert u["slp1_blocks"] == 4
    assert u["quotations"] == 1


def test_uncited_block_is_not_a_quotation():
    body = "{#hw#} {%n.%} {#q#} plain gloss, no citation"
    u = _pd(body)
    assert u["quotations"] == 0
    assert u["attestations"] == 0


def test_further_references_after_semicolon_are_attestations():
    # RG X.v: one siglum, further references added after it
    body = "{#hw#} {%n.%} {#q#} ManuSm. 2. 181; 9. 242; 11. 45"
    u = _pd(body)
    assert u["loci"] == 1
    assert u["continuation_loci"] == 2
    assert u["attestations"] == 3


def test_lowercase_roman_locus_is_not_a_siglum():
    body = "{#hw#} {%n.%} {#q#} Su\u015bruS. iii. 3. 15"
    u = _pd(body)
    assert u["loci"] == 1
    assert u["attestations"] == 1
    assert u["tokens"] == ["Su\u015bruS."]


def test_both_siglum_qualifier_shapes_count_once():
    body = ("{#hw#} {%n.%} {#q#} P\u0101\u00f1caR\u0101(N\u0101.) i. 4. 74; "
            "V\u012braMi. (Sa\u1e43sk\u0101ra.) 150. 12")
    u = _pd(body)
    assert u["loci"] == 2
    assert u["tokens"] == ["P\u0101\u00f1caR\u0101(N\u0101.)", "V\u012braMi."]


def test_sense_marker_ends_the_citation_tail():
    body = "{#hw#} {%n.%} {#q1#} ManuSm. 1. 2; {@2@} next sense {#q2#} AgniP. 3. 4"
    u = _pd(body)
    assert u["quotations"] == 2
    assert u["loci"] == 2


def test_pwg_marker_is_the_ls_tag():
    import pd_quotations_vs_pwg as pdc

    body = "{#hw#} {%de%} {#q#} <ls>M. 2,181</ls>. <ls n=\"M.\">9,242</ls>."
    u = quotation_units.count_units(body, pdc.pwg_marker)
    assert u["quotations"] == 1
    assert u["attestations"] == 2
