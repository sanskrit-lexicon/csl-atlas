"""Pins for ``f11_evidence_dependence`` (H5073).

Same discipline as the H4352 pins: every expected value below is derived BY HAND
from the miniature fixture and written literally into the test; the fixture is
written by the test in real parsed-cache shapes; nothing runs against
``../csl-orig``; a null fixture asserts exactly zero.

The fixture corpus (parsed-cache TSVs, ``cites`` pipe-joined in source order)
-----------------------------------------------------------------------------
    MW    agni  : P. 1,1,14 | MBH. 1,2 | RV. 7,96          -> sigils P MBH RV
          deva  : MBH. 3,4 | RV. 1,1 | HARIV. 855 | HARIV. 900 -> MBH RV HARIV
          indra : RV. 2,12 | MBH. 5,6 | VS. 7,8 | TS. 1,2   -> RV MBH VS TS
          soma  : RV. 9,1                                   -> RV
    PWG   agni  : P. 1,1,14 | MBH. 1,2 | RV. 7,96           -> P MBH RV   (same order)
          deva  : HARIV. 855 | RV. 1,1 | MBH. 3,4 | HARIV. 900 -> HARIV RV MBH (reversed)
          indra : RV. 2,12 | MBH. 5,6 | TS. 1,2 | VS. 9,9   -> RV MBH TS VS (one swap)
          soma  : RV. 9,1 | AV. 1,1                          -> RV AV
    PW    deva  : HARIV. 900                       (the second Petersburg witness)
    AP    agni  : AV. 2,2                          (independent control, no shared sigil)
    BEN   agni  : P. 1,1,14
    FILL  f1..f4: every "common" reference, so it is cited by 5 distinct lemmas
                  corpus-wide and therefore NOT rare (F1's threshold is <= 4).

Hand-derived expectations
-------------------------
L-CIT-LEMMA  = MW-cited & PWG-cited = {agni, deva, indra, soma}          = 4
L-ORD-ENTRY  = those with >= 3 shared sigils: agni 3, deva 3, indra 4;
               soma shares only {RV}                                     = 3
L-RARE-EVENT = shared exact refs cited by <= 4 lemmas corpus-wide:
               (deva, HARIV. 855, PWG) · (deva, HARIV. 900, PWG)
             · (indra, TS. 1,2, PWG)   · (deva, HARIV. 900, PW)          = 4
               independent source events (witness dropped)               = 3
L-ANCHOR-WORD= SKD & VCP = {agni, deva, soma, indra, varuRa, mitra}      = 6

concordant_fraction, per entry:
    agni  a=[P,MBH,RV]      b=[P,MBH,RV]      3 pairs, 3 concordant   -> 1.0
    deva  a=[MBH,RV,HARIV]  b=[HARIV,RV,MBH]  3 pairs, 0 concordant   -> 0.0
    indra a=[RV,MBH,VS,TS]  b=[RV,MBH,TS,VS]  6 pairs, 5 concordant   -> 5/6
    mean = (1.0 + 0.0 + 5/6) / 3 = 0.6111 ; identical 1/3 = 33.33 %

global_convention = mean normalised position (i / (len-1)) per sigil, over
entries with >= 2 distinct sigils:
    MW  : P 0 · MBH (0.5+0+1/3)/3 = 0.2778 · RV (1+0.5+0)/3 = 0.5
        · HARIV 1 · VS 2/3 = 0.6667 · TS 1        (soma has 1 sigil -> skipped)
    PWG : P 0 · MBH (0.5+1+1/3)/3 = 0.6111 · RV (1+0.5+0+0)/4 = 0.375
        · HARIV 0 · TS 2/3 · VS 1 · AV 1

convention_split — every scored pair classified by whether the two GLOBAL
conventions agree on its direction, then checked against the observed order:
    agni  (P,MBH) conc/agree · (P,RV) conc/agree · (MBH,RV) disc/agree
    deva  (MBH,RV) disc/disagree · (MBH,HARIV) disc/disagree
        · (RV,HARIV) disc/disagree
    indra (RV,MBH) disc/agree · (RV,VS) conc/agree · (RV,TS) conc/agree
        · (MBH,VS) conc/agree · (MBH,TS) conc/agree · (VS,TS) disc/disagree
    -> concordant 6 pairs, 6 agree = 1.0 ; discordant 6 pairs, 2 agree = 0.3333

contingency (identical hand derivation to the f9 pin):
    R = {agni, deva, soma, indra, varuRa, mitra}   PWG = {agni,deva,soma,indra}
    MW = {agni,deva,soma,mitra} -> 3/1/1/1 ; P(lack|has)=1/4 ; P(lack|lacks)=1/2 -> 2.0
    AP = {agni,varuRa,mitra}    -> 1/3/2/0 ; P(lack|has)=3/4 ; P(lack|lacks)=0   -> 0.0

mean_jaccard(PWG, MW) over the four shared cited lemmas:
    agni 3/3 · deva 3/3 · indra 4/4 · soma {RV,AV} vs {RV} = 1/2
    -> (1 + 1 + 1 + 0.5) / 4 = 0.875
"""

import csv
import json

import pytest

from conftest import write_text, write_tsv

MW_ROWS = [
    (1, "agni", "agni", "", "", 3, "P. 1,1,14|MBH. 1,2|RV. 7,96"),
    (2, "deva", "deva", "", "", 4, "MBH. 3,4|RV. 1,1|HARIV. 855|HARIV. 900"),
    (3, "indra", "indra", "", "", 4, "RV. 2,12|MBH. 5,6|VS. 7,8|TS. 1,2"),
    (4, "soma", "soma", "", "", 1, "RV. 9,1"),
]
PWG_ROWS = [
    (1, "agni", "agni", "", "", 3, "P. 1,1,14|MBH. 1,2|RV. 7,96"),
    (2, "deva", "deva", "", "", 4, "HARIV. 855|RV. 1,1|MBH. 3,4|HARIV. 900"),
    (3, "indra", "indra", "", "", 4, "RV. 2,12|MBH. 5,6|TS. 1,2|VS. 9,9"),
    (4, "soma", "soma", "", "", 2, "RV. 9,1|AV. 1,1"),
]
PW_ROWS = [(1, "deva", "deva", "", "", 1, "HARIV. 900")]
AP_ROWS = [(1, "agni", "agni", "", "", 1, "AV. 2,2")]
BEN_ROWS = [(1, "agni", "agni", "", "", 1, "P. 1,1,14")]
COMMON_REFS = ("P. 1,1,14|MBH. 1,2|RV. 7,96|MBH. 3,4|RV. 1,1|"
               "RV. 2,12|MBH. 5,6|RV. 9,1")
FILL_ROWS = [(i, f"f{i}", f"f{i}", "", "", 8, COMMON_REFS) for i in range(1, 5)]

KEY1 = {
    "MW-unique-key1-194084.txt": ["agni", "deva", "soma", "mitra"],
    "PWG-unique-key1-106082.txt": ["agni", "deva", "soma", "indra"],
    "AP-unique-key1-88867.txt": ["agni", "varuRa", "mitra"],
    "SKD-unique-key1-40817.txt": ["agni", "deva", "soma", "indra", "varuRa", "mitra", "SabdaX"],
    "VCP-unique-key1-48636.txt": ["agni", "deva", "soma", "indra", "varuRa", "mitra", "vAcaspatiX"],
}


@pytest.fixture(scope="module")
def f11():
    import f11_evidence_dependence as mod
    return mod


def _corpus(tmp_path, rows_by_code):
    parsed = tmp_path / "data" / "forensic" / "parsed"
    for code, rows in rows_by_code.items():
        write_tsv(parsed / f"{code}.tsv", rows)
    return parsed


def _key1(tmp_path, table=None):
    hw = tmp_path / "hw"
    for name, words in (table or KEY1).items():
        write_text(hw / name, "\n".join(words) + "\n")
    return hw


@pytest.fixture
def fixture_corpus(forensic_cwd, monkeypatch, f11):
    """The miniature corpus above, with every path constant repointed at tmp."""
    _corpus(forensic_cwd, {
        "mw": MW_ROWS, "pwg": PWG_ROWS, "pw": PW_ROWS,
        "ap": AP_ROWS, "ben": BEN_ROWS, "fill": FILL_ROWS,
    })
    hw = _key1(forensic_cwd)
    monkeypatch.setattr(f11, "HW_DIR", str(hw))
    monkeypatch.setattr(f11, "OUT_DIR", str(forensic_cwd / "data" / "forensic"))
    monkeypatch.setattr(f11, "ANALYSIS_CODES", ["MW", "PWG", "PW", "AP", "BEN"])
    monkeypatch.setattr(f11, "RARITY_CODES", ["MW", "PWG", "PW", "AP", "BEN", "FILL"])
    return forensic_cwd


@pytest.fixture
def graphs(fixture_corpus, f11):
    pool = {c: f11.load_dict(c.lower()) for c in f11.RARITY_CODES}
    dicts = {c: pool[c] for c in f11.ANALYSIS_CODES}
    return dicts, f11.build_graphs(dicts, pool)


# --------------------------------------------------------------------------
# pure primitives
# --------------------------------------------------------------------------

def test_ref_normalisation(f11, pin):
    pin("f11", "norm_ref.trailing_stop", "P. 1,1,14", f11.norm_ref("p. 1,1,14."))
    pin("f11", "norm_ref.collapses_space", "RV. 7, 96", f11.norm_ref("RV.  7,  96"))
    pin("f11", "source_of.HARIV", "HARIV", f11.source_of("HARIV. 855"))
    pin("f11", "source_of.no_digit", "PAÑCAT. II", f11.source_of("PAÑCAT. II"))
    pin("f11", "dedup.first_wins", ["MBH", "RV", "HARIV"],
        f11.dedup(["MBH", "RV", "HARIV", "RV", "", "HARIV"]))


def test_concordant_fraction(f11, pin):
    identical = (["P", "MBH", "RV"], ["P", "MBH", "RV"])
    reversed_ = (["MBH", "RV", "HARIV"], ["HARIV", "RV", "MBH"])
    one_swap = (["RV", "MBH", "VS", "TS"], ["RV", "MBH", "TS", "VS"])
    pin("f11", "concordant.identical", (1.0, 3), f11.concordant_fraction(*identical))
    pin("f11", "concordant.reversed", (0.0, 3), f11.concordant_fraction(*reversed_))
    pin("f11", "concordant.one_swap", (5 / 6, 6), f11.concordant_fraction(*one_swap))
    pin("f11", "concordant.too_few", (None, 0),
        f11.concordant_fraction(["A", "B"], ["A", "B"]))
    pin("f11", "concordant.restricted_to_one_pair", (1.0, 1),
        f11.concordant_fraction(*one_swap, restrict={frozenset(("RV", "MBH"))}))


def test_contingency_matches_the_f9_hand_derivation(f11, pin):
    anchor = {"agni", "deva", "soma", "indra", "varuRa", "mitra"}
    pwg = {"agni", "deva", "soma", "indra"}
    mw = f11.contingency(anchor, pwg, {"agni", "deva", "soma", "mitra"})
    ap = f11.contingency(anchor, pwg, {"agni", "varuRa", "mitra"})
    pin("f11", "contingency.MW.cells",
        (3, 1, 1, 1), (mw["pwg_has_probe_has"], mw["pwg_has_probe_lacks"],
                       mw["pwg_lacks_probe_has"], mw["pwg_lacks_probe_lacks"]))
    pin("f11", "contingency.MW.gap_sensitivity", 2.0, mw["gap_sensitivity"])
    pin("f11", "contingency.AP.cells",
        (1, 3, 2, 0), (ap["pwg_has_probe_has"], ap["pwg_has_probe_lacks"],
                       ap["pwg_lacks_probe_has"], ap["pwg_lacks_probe_lacks"]))
    pin("f11", "contingency.AP.gap_sensitivity", 0.0, ap["gap_sensitivity"])


# --------------------------------------------------------------------------
# claim → signal → locus graphs
# --------------------------------------------------------------------------

def test_locus_counts(graphs, pin):
    _dicts, g = graphs
    pin("f11", "L-CIT-LEMMA", 4, len(g["c1_lemmas"]))
    pin("f11", "L-ORD-ENTRY", 3, len(g["c2_entries"]))
    pin("f11", "L-RARE-EVENT", 4, len(g["rare_events"]))
    pin("f11", "L-ANCHOR-WORD", 6, len(g["anchor"]))
    pin("f11", "rare_events.exact", {
        ("deva", "HARIV. 855", "PWG"),
        ("deva", "HARIV. 900", "PWG"),
        ("deva", "HARIV. 900", "PW"),
        ("indra", "TS. 1,2", "PWG"),
    }, g["rare_events"])
    pin("f11", "anchor_sources.SKD", "key1-export", g["anchor_sources"]["SKD"])


def test_C2_is_nested_inside_C1(graphs, pin):
    """The audit's headline: every order-bearing entry is already a C1 locus."""
    _dicts, g = graphs
    c1, c2 = g["c1_lemmas"], g["c2_entries"]
    pin("f11", "C2_in_C1.intersection", 3, len(c2 & c1))
    pin("f11", "C2_in_C1.share", 1.0, len(c2 & c1) / len(c2))
    pin("f11", "C2_loci_not_in_C1", 0, len(c2 - c1))


def test_anchor_overlap(graphs, pin):
    _dicts, g = graphs
    anchor, c1, c2 = g["anchor"], g["c1_lemmas"], g["c2_entries"]
    pin("f11", "C3_in_C1.intersection", 4, len(anchor & c1))
    pin("f11", "C3_in_C2.intersection", 3, len(anchor & c2))
    pin("f11", "C3_loci_not_in_C1_or_C2", 2, len(anchor - c1 - c2))


# --------------------------------------------------------------------------
# controls
# --------------------------------------------------------------------------

def test_ctrl_dup_seeded_duplicate_witness(graphs, f11, pin):
    """A verbatim duplicate witness must inflate the naive count and NOTHING else."""
    _dicts, g = graphs
    out = f11.seeded_duplicate_witness(g["rare_events"])
    pin("f11", "CTRL-DUP.before.naive", 4, out["before"]["naive_witness_events"])
    pin("f11", "CTRL-DUP.before.independent", 3, out["before"]["independent_source_events"])
    pin("f11", "CTRL-DUP.after.naive", 7,
        out["after_seeding_verbatim_PWG_duplicate"]["naive_witness_events"])
    pin("f11", "CTRL-DUP.after.independent", 3,
        out["after_seeding_verbatim_PWG_duplicate"]["independent_source_events"])
    pin("f11", "CTRL-DUP.independent_support_delta", 0, out["independent_support_delta"])
    pin("f11", "CTRL-DUP.control_passes", True, out["control_passes"])


def test_ctrl_novel_can_fail_where_ctrl_dup_cannot(graphs, f11, pin):
    """CTRL-DUP's Δ=0 is structural; this is its falsifiable twin.

    Fixture rare_events (module docstring): 4 triples over 3 distinct
    (lemma, ref) keys. Sorted, they are (deva, HARIV. 855, PWG),
    (deva, HARIV. 900, PW), (deva, HARIV. 900, PWG), (indra, TS. 1,2, PWG).
    With n_inject=3 the injector suffixes the refs of the first three, so the
    last TWO injected triples land on ONE new key (deva, HARIV. 900 [SEEDED]) —
    3 triples, 2 distinct keys. Independent support must rise by exactly 2:
    an accounting that counted triples (keyed on the witness) would rise by 3,
    one that dropped the ref would not rise at all. (H5073 Astra finding 5: the
    earlier n_inject=2 hit two distinct keys and could not tell these apart.)
    """
    _dicts, g = graphs
    out = f11.seeded_novel_witness(g["rare_events"], n_inject=3)
    pin("f11", "CTRL-NOVEL.injected_triples", 3, out["injected_novel_triples"])
    pin("f11", "CTRL-NOVEL.distinct_new_events", 2, out["distinct_new_source_events"])
    pin("f11", "CTRL-NOVEL.after.naive", 7, out["after_seeding_novel_events"]["naive_witness_events"])
    pin("f11", "CTRL-NOVEL.after.independent", 5,
        out["after_seeding_novel_events"]["independent_source_events"])
    pin("f11", "CTRL-NOVEL.independent_support_delta", 2, out["independent_support_delta"])
    pin("f11", "CTRL-NOVEL.delta_below_triple_count", True,
        out["independent_support_delta"] < out["injected_novel_triples"])
    pin("f11", "CTRL-NOVEL.control_passes", True, out["control_passes"])


def test_independent_support_drops_the_witness(f11, pin):
    events = {("deva", "HARIV. 900", "PWG"), ("deva", "HARIV. 900", "PW")}
    out = f11.independent_support(events)
    pin("f11", "independent_support.naive", 2, out["naive_witness_events"])
    pin("f11", "independent_support.deduped", 1, out["independent_source_events"])


def test_global_convention(graphs, f11, pin):
    dicts, _g = graphs
    mw = {k: round(v, 4) for k, v in f11.global_convention(dicts["MW"]).items()}
    pwg = {k: round(v, 4) for k, v in f11.global_convention(dicts["PWG"]).items()}
    pin("f11", "convention.MW",
        {"P": 0.0, "MBH": 0.2778, "RV": 0.5, "HARIV": 1.0, "VS": 0.6667, "TS": 1.0}, mw)
    pin("f11", "convention.PWG",
        {"P": 0.0, "MBH": 0.6111, "RV": 0.375, "HARIV": 0.0, "TS": 0.6667,
         "VS": 1.0, "AV": 1.0}, pwg)


def test_ctrl_conv_splits_convention_from_per_entry_agreement(graphs, f11, pin):
    dicts, g = graphs
    conv_mw = f11.global_convention(dicts["MW"])
    conv_pwg = f11.global_convention(dicts["PWG"])
    out = f11.convention_split(dicts["MW"], dicts["PWG"], g["c2_entries"], conv_mw, conv_pwg)
    pin("f11", "CTRL-CONV.entries_scored", 3, out["entries_scored"])
    pin("f11", "CTRL-CONV.concordant_pairs", 6, out["convention_concordant_pairs"])
    pin("f11", "CTRL-CONV.agreement_concordant", 1.0,
        out["agreement_on_convention_concordant"])
    pin("f11", "CTRL-CONV.discordant_pairs", 6, out["convention_discordant_pairs"])
    pin("f11", "CTRL-CONV.agreement_discordant", 0.3333,
        out["agreement_on_convention_discordant"])


def test_ctrl_perm_is_seed_deterministic(graphs, f11, pin):
    """Not a hand-derived value: a permutation mean is statistical. What IS
    hand-derivable is that the same seed gives the same answer, that the entry
    population is the three order-bearing entries, and that the expected
    concordance of a uniformly random within-entry order is 0.5 by symmetry."""
    import random
    dicts, g = graphs
    a = f11.permutation_null(dicts["MW"], dicts["PWG"], g["c2_entries"],
                             random.Random(f11.SEED), 50)
    b = f11.permutation_null(dicts["MW"], dicts["PWG"], g["c2_entries"],
                             random.Random(f11.SEED), 50)
    pin("f11", "CTRL-PERM.entries", 3, a["entries"])
    pin("f11", "CTRL-PERM.iters", 50, a["iters"])
    pin("f11", "CTRL-PERM.seed_deterministic", a, b)
    # H5073 pre-review finding 3: same-process determinism (a == b above) is the
    # WEAK property. The entry set arrives as a `set`, whose iteration order is
    # hash-randomised per process; unsorted, the shared RNG is consumed in a
    # different order each run and the band moves under a fixed seed. Feeding
    # the SAME entries in a deliberately different container order must now give
    # a byte-identical block — that is the property a rerun in another process
    # actually needs.
    reordered = list(g["c2_entries"])[::-1]
    c = f11.permutation_null(dicts["MW"], dicts["PWG"], reordered,
                             random.Random(f11.SEED), 50)
    pin("f11", "CTRL-PERM.order_independent", a, c)
    assert 0.35 <= a["mean_concordance"] <= 0.65, (
        f"permutation mean {a['mean_concordance']} is far from the symmetry "
        "expectation of 0.5 — the shuffle is not destroying the order signal"
    )


def test_mean_jaccard_via_main_surface(fixture_corpus, f11, pin, monkeypatch):
    """main() dry-run surface: run the whole pipeline in tmp and read the report."""
    monkeypatch.setattr(f11, "PERM_ITERS", 20)
    monkeypatch.setattr(f11, "ABLATE_TOP_SIGILS", 1)
    out_dir = fixture_corpus / "data" / "forensic"
    write_text(out_dir / "f1_report.json", json.dumps(
        {"n_smoking_guns": 4, "smoking_gun_sources": {"HARIV": 3, "TS": 1}}))
    write_text(out_dir / "f5_report.json", json.dumps(
        {"pairs": [{"vs": "PWG", "entries_with_order_signal": 3,
                    "mean_citation_order_agreement": 0.6111,
                    "pct_identical_order": 33.33}]}))
    write_text(out_dir / "shared_omission_test.csv",
               "probe,gap_sensitivity\nMW,2.0\nAP,0.0\n")

    f11.main()
    rep = json.loads((out_dir / "f11_report.json").read_text(encoding="utf-8"))

    pin("f11", "main.claims.C1.L-CIT-LEMMA", 4, rep["claims"]["A10-C1"]["loci"]["L-CIT-LEMMA"])
    pin("f11", "main.claims.C2.L-ORD-ENTRY", 3, rep["claims"]["A10-C2"]["loci"]["L-ORD-ENTRY"])
    pin("f11", "main.claims.C3.L-ANCHOR-WORD", 6,
        rep["claims"]["A10-C3"]["loci"]["L-ANCHOR-WORD"])
    pin("f11", "main.c2_observed.PWG.mean", 0.6111,
        rep["c2_observed"]["PWG"]["mean_concordance"])
    pin("f11", "main.c2_observed.PWG.pct_identical", 33.33,
        rep["c2_observed"]["PWG"]["pct_identical"])
    pin("f11", "main.c2_observed.AP.entries", 0, rep["c2_observed"]["AP"]["entries"])
    pin("f11", "main.jaccard.PWG/MW", 0.875,
        rep["controls"]["CTRL-ABL-S"]["pairs"]["PWG/MW"]["mean_source_jaccard"])
    pin("f11", "main.jaccard.AP/MW", 0.0,
        rep["controls"]["CTRL-ABL-S"]["pairs"]["AP/MW"]["mean_source_jaccard"])
    pin("f11", "main.jaccard.BEN/MW", 0.3333,
        rep["controls"]["CTRL-ABL-S"]["pairs"]["BEN/MW"]["mean_source_jaccard"])
    pin("f11", "main.CTRL-ABL-H.harivamsa_share", 0.75,
        rep["controls"]["CTRL-ABL-H"]["harivamsa_share"])
    pin("f11", "main.CTRL-ABL-H.residue", {"TS": 1},
        rep["controls"]["CTRL-ABL-H"]["residue_by_sigil"])
    pin("f11", "main.CTRL-PWDUP.pw_already_in_pwg", 1.0,
        rep["controls"]["CTRL-PWDUP"]["pw_events_already_in_pwg"])
    # naive sum 4 + 3 + 6 = 13 ; union {agni,deva,indra,soma,varuRa,mitra} = 6
    pin("f11", "main.accounting.naive_sum", 13,
        rep["deduplicated_accounting"]["naive_sum_of_loci"])
    pin("f11", "main.accounting.union", 6,
        rep["deduplicated_accounting"]["union_of_loci"])
    pin("f11", "main.accounting.double_counted", 7,
        rep["deduplicated_accounting"]["double_counted_by_naive_sum"])
    # the delta block must report ZERO drift when the corpus matches the frozen run
    pin("f11", "main.repro.rare", {"published": 4, "reproduced": 4},
        rep["reproduction_delta"]["S-F1-RARE"])
    pin("f11", "main.repro.f9_mw", 2.0, rep["reproduction_delta"]["S-F9-GAPSENS"]["reproduced_mw"])

    with open(out_dir / "evidence_dependence_loci.csv", encoding="utf-8") as fh:
        loci = {r["locus_a"] + "|" + r["locus_b"]: r for r in csv.DictReader(fh)}
    pin("f11", "main.loci_csv.C2_in_C1_share", "1.0",
        loci["L-ORD-ENTRY|L-CIT-LEMMA"]["share_of_a"])


# --------------------------------------------------------------------------
# null fixture — the correct answer is exactly zero
# --------------------------------------------------------------------------

def test_null_fixture_scores_exactly_zero(forensic_cwd, monkeypatch, f11, pin):
    """Disjoint apparatus on both sides: no shared cited lemma, so no C1 locus,
    no order-bearing entry, no rare shared reference — and the duplicate-witness
    control still passes, because zero cannot be inflated."""
    _corpus(forensic_cwd, {
        "mw": [(1, "agni", "agni", "", "", 1, "P. 1,1,14")],
        "pwg": [(1, "soma", "soma", "", "", 1, "RV. 9,1")],
        "pw": [(1, "indra", "indra", "", "", 1, "AV. 2,2")],
        "ap": [(1, "mitra", "mitra", "", "", 1, "TS. 3,3")],
        "ben": [(1, "varuRa", "varuRa", "", "", 1, "VS. 4,4")],
        "fill": [(1, "f1", "f1", "", "", 1, "SV. 5,5")],
    })
    hw = _key1(forensic_cwd, {
        "MW-unique-key1-194084.txt": ["agni"],
        "PWG-unique-key1-106082.txt": ["agni"],
        "AP-unique-key1-88867.txt": ["agni"],
        "SKD-unique-key1-40817.txt": ["agni", "deva"],
        "VCP-unique-key1-48636.txt": ["agni", "soma"],
    })
    monkeypatch.setattr(f11, "HW_DIR", str(hw))
    monkeypatch.setattr(f11, "ANALYSIS_CODES", ["MW", "PWG", "PW", "AP", "BEN"])
    monkeypatch.setattr(f11, "RARITY_CODES", ["MW", "PWG", "PW", "AP", "BEN", "FILL"])

    pool = {c: f11.load_dict(c.lower()) for c in f11.RARITY_CODES}
    dicts = {c: pool[c] for c in f11.ANALYSIS_CODES}
    g = f11.build_graphs(dicts, pool)

    pin("f11", "null.L-CIT-LEMMA", 0, len(g["c1_lemmas"]))
    pin("f11", "null.L-ORD-ENTRY", 0, len(g["c2_entries"]))
    pin("f11", "null.L-RARE-EVENT", 0, len(g["rare_events"]))
    pin("f11", "null.L-ANCHOR-WORD", 1, len(g["anchor"]))      # SKD & VCP = {agni}

    dup = f11.seeded_duplicate_witness(g["rare_events"])
    pin("f11", "null.CTRL-DUP.naive_inflation", 0, dup["naive_inflation"])
    pin("f11", "null.CTRL-DUP.independent_support_delta", 0, dup["independent_support_delta"])
    pin("f11", "null.CTRL-DUP.control_passes", True, dup["control_passes"])

    import random
    perm = f11.permutation_null(dicts["MW"], dicts["PWG"], g["c2_entries"],
                                random.Random(f11.SEED), 10)
    pin("f11", "null.CTRL-PERM.entries", 0, perm["entries"])
    pin("f11", "null.CTRL-PERM.mean", None, perm["mean_concordance"])

    conv_mw = f11.global_convention(dicts["MW"])
    conv_pwg = f11.global_convention(dicts["PWG"])
    split = f11.convention_split(dicts["MW"], dicts["PWG"], g["c2_entries"], conv_mw, conv_pwg)
    pin("f11", "null.CTRL-CONV.entries_scored", 0, split["entries_scored"])
    pin("f11", "null.CTRL-CONV.agreement_discordant", None,
        split["agreement_on_convention_discordant"])


def test_ctrl_conv_conditional_convention_counterexample(f11, pin):
    """H5073 Astra findings 3 (round 1) and 3 (round 2): agreement on
    convention-discordant pairs is not a copying rate. Every sequence below
    obeys ONE fixed shared ordering X < A < B < Y < C, and nothing is copied —
    the two dictionaries merely cite different companions in `u` and `v`. That
    different source membership alone reverses the *marginal* A/B positions,
    so the target's (A,B) pair is scored "discordant" and still agrees: 1.0.

    Hand derivation (normalised position i/(n-1), averaged over every entry
    the sigil appears in, `target` included):
      a: A=(0+1)/2=0.5   B=(0.5+0)/2=0.25  C=1
      b: A=(0+0)/2=0     B=(0.5+1)/2=0.75  C=1
    target pairs over A,B,C:
      (A,B) a: 0.5<0.25 no ; b: 0<0.75 yes -> DISCORDANT; b has A before B -> agree
      (A,C) a yes ; b yes -> concordant      (B,C) a yes ; b yes -> concordant
    So 1 discordant pair, agreement 1.0.
    """
    order = "XABYC"
    a = {"target": {"sigils": ["A", "B", "C"]},
         "u": {"sigils": ["X", "A"]}, "v": {"sigils": ["B", "Y"]}}
    b = {"target": {"sigils": ["A", "B", "C"]},
         "u": {"sigils": ["A", "Y"]}, "v": {"sigils": ["X", "B"]}}
    respects = all(order.index(x) < order.index(y)
                   for d in (a, b) for e in d.values()
                   for x, y in zip(e["sigils"], e["sigils"][1:]))
    pin("f11", "CTRL-CONV.counterexample.one_fixed_order", True, respects)
    out = f11.convention_split(a, b, {"target"},
                               f11.global_convention(a), f11.global_convention(b))
    pin("f11", "CTRL-CONV.counterexample.discordant_pairs", 1,
        out["convention_discordant_pairs"])
    pin("f11", "CTRL-CONV.counterexample.agreement_discordant", 1.0,
        out["agreement_on_convention_discordant"])


def test_corpus_revision_is_per_cache_and_hash_bound(f11, pin, tmp_path, monkeypatch):
    """H5073 Astra round-2 finding 4: a partial rebuild must not relabel the
    whole cache. Records are per cache and bound to the TSV's SHA-256.

    mw.tsv + pwg.tsv, both recorded at rev R1 with matching hashes -> "R1".
    Rebuild only mw at R2 (record + file change together)       -> "MIXED".
    Edit pwg.tsv without re-recording (hash no longer matches)  -> None.
    """
    import json
    import parse_cslorig
    monkeypatch.setattr(f11, "PARSED_DIR", str(tmp_path))
    monkeypatch.setattr(parse_cslorig, "PARSED_DIR", str(tmp_path))
    monkeypatch.setattr(parse_cslorig, "CSL_ORIG", str(tmp_path / "no-such-csl-orig"))
    mw, pwg = tmp_path / "mw.tsv", tmp_path / "pwg.tsv"
    mw.write_text("L\tk1\n1\tagni\n", encoding="utf-8")
    pwg.write_text("L\tk1\n1\tdeva\n", encoding="utf-8")
    prov = tmp_path / "_parse_provenance.json"

    def record(code, rev):
        data = json.loads(prov.read_text(encoding="utf-8")) if prov.exists() else {"caches": {}}
        data["caches"][code] = {"revision": rev, "dirty": False,
                                "tsv_sha256": f11.sha256_file(str(tmp_path / f"{code}.tsv"))}
        prov.write_text(json.dumps(data), encoding="utf-8")

    paths = [str(mw), str(pwg)]
    record("mw", "R1")
    record("pwg", "R1")
    pin("f11", "corpus_revision.all_R1", "R1", f11.corpus_revision(paths)["cache_generating_revision"])

    mw.write_text("L\tk1\n1\tagni\n2\tsoma\n", encoding="utf-8")
    record("mw", "R2")
    out = f11.corpus_revision(paths)
    pin("f11", "corpus_revision.partial_rebuild", "MIXED", out["cache_generating_revision"])
    pin("f11", "corpus_revision.partial_rebuild.pwg_kept", "R1", out["per_cache"]["pwg"]["revision"])

    pwg.write_text("L\tk1\n1\tdeva\n2\tindra\n", encoding="utf-8")
    out = f11.corpus_revision(paths)
    pin("f11", "corpus_revision.stale_record", None, out["cache_generating_revision"])
    pin("f11", "corpus_revision.stale_record.status", "hash-mismatch", out["per_cache"]["pwg"]["status"])

    # the writer: a partial rebuild updates only its own record
    parse_cslorig.write_provenance(["mw"])
    caches = json.loads(prov.read_text(encoding="utf-8"))["caches"]
    pin("f11", "write_provenance.partial.keeps_pwg", "R1", caches["pwg"]["revision"])
    pin("f11", "write_provenance.partial.mw_hash_bound", f11.sha256_file(str(mw)),
        caches["mw"]["tsv_sha256"])


def test_arm_comparison_matched_and_population(f11, pin):
    """Hand fixture for the matched-loci comparison (H5073 Astra finding 2).

    arm a: e1 (P,Q)=agree (P,R)=agree ; e2 (S,T)=disagree      -> 3 pairs, 2 entries, 2/3
    arm b: e1 (P,Q)=disagree ; e3 (U,V)=agree                  -> 2 pairs, 2 entries, 1/2
    shared loci = {(e1,P,Q)} -> matched a=1.0, b=0.0 ; shared entries 1
    unmatched difference = 2/3 - 1/2 = 0.1667
    """
    import random
    a = {("e1", "P", "Q"): True, ("e1", "P", "R"): True, ("e2", "S", "T"): False}
    b = {("e1", "P", "Q"): False, ("e3", "U", "V"): True}
    out = f11.arm_comparison(a, b, random.Random(1), iters=200)
    pin("f11", "arm_comparison.contributing_entries", {"a": 2, "b": 2}, out["contributing_entries"])
    pin("f11", "arm_comparison.discordant_pairs", {"a": 3, "b": 2}, out["discordant_pairs"])
    pin("f11", "arm_comparison.shared_loci", 1, out["shared_discordant_loci"])
    pin("f11", "arm_comparison.shared_entries", 1, out["shared_entries"])
    pin("f11", "arm_comparison.matched", {"a": 1.0, "b": 0.0}, out["matched_agreement"])
    pin("f11", "arm_comparison.unmatched_difference", 0.1667, out["unmatched_difference"])
