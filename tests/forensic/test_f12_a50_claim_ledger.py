"""Pins for ``f12_a50_claim_ledger`` (H5295).

Same discipline as the H4352/H5073 pins: every expected value below is derived
BY HAND from the miniature fixture and written literally into the test; the
fixture is written by the test in the committed TSV shapes; nothing runs
against ``../csl-orig`` (the script never reads it anyway); the offline guard
in ``conftest.py`` is autouse.

The fixture graph (dict · text · count)
---------------------------------------
    A: X 10 · Y 5 · Rigveda 3 · Zprivate 1        (4 texts)
    B: X 4  · Y 2 · Ṛgveda 6                      (3 texts)
    C: X 1  · Ṛgveda 2 · Wprivate 7               (3 texts)

Hand-derived expectations
-------------------------
    totals      cites 41 · edges 10 · nodes 6
    by text     X 15 · Ṛgveda 8 · Y 7 · Wprivate 7 · Rigveda 3 · Zprivate 1
    top-k share sorted [15, 8, 7, 7, 3, 1] → top1 15/41 = 36.6 % · top2 23/41 = 56.1 %
    reach       X 3 · Y 2 · Ṛgveda 2 · Rigveda 1 · Zprivate 1 · Wprivate 1
                → {3: 1, 2: 2, 1: 3}
    private     3 of 6 = 50.0 % · volume (3 + 1 + 7) / 41 = 26.8 %
    named fold  Rigveda → Ṛgveda (both present) · union dicts {A} ∪ {B, C} = 3
    ascii fold  ascii_fold("Rigveda") = "rgveda" = ascii_fold("Ṛgveda") → the
                same pair, already covered by the named tier → 4 named rows
                are 1 (only Rigveda exists in the fixture), ascii rows 0
    after fold  nodes 5 · Ṛgveda cited by A, B, C → cited by every dict
                reach {3: 2, 2: 1, 1: 2} · private 2 of 5 = 40.0 %
    private variants of shared texts: Rigveda (A only; union > 1) → 1
    THIN_ROWS   {mw, md} absent → usable rows 3, every-usable-row texts = [X]
                (pre-fold Ṛgveda is B and C only)
    kośas       absent → total 0, absent True
    Table 1     A 4 · B 3 · C 3 distinct texts

Plus arithmetic pins on the COMMITTED report — the figures the ledger doc and
the paper edits quote, so a regeneration that moves them fails loudly.
"""

import importlib
import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load(monkeypatch, tmp_path):
    mod = importlib.import_module("f12_a50_claim_ledger")
    importlib.reload(mod)
    edges = tmp_path / "edges.tsv"
    nodes = tmp_path / "nodes.tsv"
    canon = tmp_path / "canon.json"
    edges.write_text(
        "dict\tcanonical_text\tcount\n"
        "A\tX\t10\nA\tY\t5\nA\tRigveda\t3\nA\tZprivate\t1\n"
        "B\tX\t4\nB\tY\t2\nB\tṚgveda\t6\n"
        "C\tX\t1\nC\tṚgveda\t2\nC\tWprivate\t7\n",
        encoding="utf-8",
    )
    nodes.write_text(
        "canonical_text\ttotal_cites\tn_dicts\tvariant_forms\n"
        "X\t15\t3\tX\nṚgveda\t8\t2\tṚgveda\nY\t7\t2\tY\nWprivate\t7\t1\tWprivate\n"
        "Rigveda\t3\t1\tRigveda\nZprivate\t1\t1\tZprivate\n",
        encoding="utf-8",
    )
    canon.write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(mod, "EDGES", str(edges))
    monkeypatch.setattr(mod, "NODES", str(nodes))
    monkeypatch.setattr(mod, "CANON", str(canon))
    monkeypatch.setattr(mod, "OUT_JSON", str(tmp_path / "report.json"))
    monkeypatch.setattr(mod, "OUT_FOLD", str(tmp_path / "fold.tsv"))
    monkeypatch.setattr(mod, "REGEN", str(tmp_path / "absent_regen.tsv"))
    return mod


def test_ascii_fold_collapses_transliteration_variants(pin):
    mod = importlib.import_module("f12_a50_claim_ledger")
    pin("f12", "fold Rigveda", "rgveda", mod.ascii_fold("Rigveda"))
    pin("f12", "fold Ṛgveda", "rgveda", mod.ascii_fold("Ṛgveda"))
    pin("f12", "fold Naishadhacharita", mod.ascii_fold("Naiṣadhacarita"), mod.ascii_fold("Naishadhacharita"))
    # ṃ/n is NOT collapsed on purpose (it separates real titles): that is why
    # Raghuvanśa/Raghuvaṃśa needs the hand-named tier the paper's §5.5 supplies.
    assert mod.ascii_fold("Raghuvaṃśa") != mod.ascii_fold("Raghuvanśa")
    # Non-Latin noise nodes fold to the empty key and must never pair up.
    pin("f12", "fold cyrillic", "", mod.ascii_fold("Ѳ"))
    # Distinct texts stay distinct.
    assert mod.ascii_fold("Mahābhārata") != mod.ascii_fold("Rāmāyaṇa")


def test_fixture_ledger(pin, monkeypatch, tmp_path):
    mod = _load(monkeypatch, tmp_path)
    assert mod.main() == 0
    rep = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))

    pin("f12", "totals.cites", 41, rep["totals"]["cites"])
    pin("f12", "totals.edges", 10, rep["totals"]["edges"])
    pin("f12", "totals.nodes", 6, rep["totals"]["nodes"])
    pin("f12", "top1/top2 share", {"1": 36.6, "2": 56.1},
        mod.topk_share(__import__("collections").Counter({"X": 15, "R": 8, "Y": 7, "W": 7, "r": 3, "Z": 1}), (1, 2)))
    pin("f12", "reach", {"3": 1, "2": 2, "1": 3}, rep["C2_reach"]["reach_all_11"])
    pin("f12", "private nodes", 3, rep["C2_reach"]["private_nodes"])
    pin("f12", "private pct", 50.0, rep["C2_reach"]["private_nodes_pct"])
    pin("f12", "private volume pct", 26.8, rep["C2_reach"]["private_volume_pct"])
    pin("f12", "usable rows", 3, rep["C2_reach"]["usable_rows"])
    # pre-fold: Ṛgveda is cited by B and C only, so X alone reaches every row
    pin("f12", "every-usable-row texts", ["X"], rep["C2_reach"]["texts_cited_by_every_usable_row"])

    fold = rep["C2b_variant_fold"]
    pin("f12", "fold rows named", 1, fold["fold_rows_named"])
    pin("f12", "fold rows ascii", 0, fold["fold_rows_ascii"])
    pin("f12", "private variants of shared", 1, fold["private_nodes_that_are_variants_of_shared_texts"])
    pin("f12", "nodes after fold", 5, fold["nodes_after_fold"])
    pin("f12", "private after fold", 2, fold["private_after_fold"])
    pin("f12", "private after fold pct", 40.0, fold["private_after_fold_pct"])
    # Zprivate 1 + Wprivate 7 = 8 of 41 (Rigveda folds into the shared Ṛgveda).
    pin("f12", "private after fold volume pct", 19.5, fold["private_after_fold_volume_pct"])
    pin("f12", "reach after fold", {"3": 2, "2": 1, "1": 2}, fold["reach_after_fold"])
    # after fold: X (A, B, C) and Ṛgveda (A via Rigveda, B, C) reach every dict
    pin("f12", "every-dict after fold", ["X", "Ṛgveda"], fold["texts_cited_by_every_dict_after_fold"])
    pin("f12", "Rigveda union dicts", 3, fold["named_variants"]["Rigveda"]["union_dicts"])

    pin("f12", "kośa absent", True, rep["C5_kosa_citers"]["Amarakoṣa"]["absent"])
    pin("f12", "table1 distinct", {"A": 4, "B": 3, "C": 3}, rep["reproduction"]["table1_distinct_texts"])
    # Rigveda is the one private variant of a shared text, found by the named tier;
    # no private label merges into another private label in the fixture.
    pin("f12", "private variants by tier", {"named": 1, "ascii": 0}, fold["private_variants_of_shared_by_tier"])
    pin("f12", "private→private merges", 0, fold["private_variants_merging_into_private_canonical"])
    # No regenerated edge list is monkeypatched in → no drift block.
    pin("f12", "drift absent", None, rep["drift"])

    fold_tsv = (tmp_path / "fold.tsv").read_text(encoding="utf-8").splitlines()
    pin("f12", "fold tsv rows", 2, len(fold_tsv))
    pin("f12", "fold tsv row", "Rigveda\tṚgveda\tnamed\t3\tA\tB,C", fold_tsv[1])


def test_null_fixture_no_variants(pin, monkeypatch, tmp_path):
    """Two dictionaries citing the same two texts under identical names: no
    fold rows, no private nodes, both texts cited by every dict."""
    mod = _load(monkeypatch, tmp_path)
    (tmp_path / "edges.tsv").write_text(
        "dict\tcanonical_text\tcount\nA\tX\t1\nA\tY\t1\nB\tX\t1\nB\tY\t1\n", encoding="utf-8")
    (tmp_path / "nodes.tsv").write_text(
        "canonical_text\ttotal_cites\tn_dicts\tvariant_forms\nX\t2\t2\tX\nY\t2\t2\tY\n", encoding="utf-8")
    assert mod.main() == 0
    rep = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    pin("f12", "null fold rows", 0, rep["C2b_variant_fold"]["fold_rows"])
    pin("f12", "null private", 0, rep["C2_reach"]["private_nodes"])
    pin("f12", "null every-dict", ["X", "Y"], rep["C2b_variant_fold"]["texts_cited_by_every_dict_after_fold"])


@pytest.mark.skipif(not (REPO / "data" / "forensic" / "f12_a50_report.json").exists(), reason="committed report absent")
def test_committed_report_pins(pin):
    """The figures the ledger doc and the A50 edits quote (24-09-2026 re-freeze, H5407:
    csl-orig@f4c08c57 + csl-guides@64c967d, 37-pair fold in CANON_ALIAS)."""
    rep = json.loads((REPO / "data" / "forensic" / "f12_a50_report.json").read_text(encoding="utf-8"))
    pin("f12", "committed cites", 826752, rep["totals"]["cites"])
    pin("f12", "committed edges", 1699, rep["totals"]["edges"])
    pin("f12", "committed nodes", 874, rep["totals"]["nodes"])
    pin("f12", "pwg volume share", 64.9, rep["C1_concentration"]["per_dict_volume_share_pct"]["pwg"])
    pin("f12", "top10 pooled", 34.9, rep["C1_concentration"]["topk_share_pooled_pct"]["10"])
    pin("f12", "top50 pooled", 72.5, rep["C1_concentration"]["topk_share_pooled_pct"]["50"])
    pin("f12", "top10 excl pwg", 40.3, rep["C1_concentration"]["topk_share_excluding_pwg_pct"]["10"])
    pin("f12", "private 567", 567, rep["C2_reach"]["private_nodes"])
    pin("f12", "private volume pct", 9.6, rep["C2_reach"]["private_volume_pct"])
    pin("f12", "ge7 texts", 38, rep["C2_reach"]["texts_ge7_dicts"])
    pin("f12", "reach all 11", 1, rep["C2_reach"]["reach_all_11"]["11"])
    pin("f12", "every usable row", ["Bhagavadgītā", "Kathāsaritsāgara", "Mārkandeyapuraṇa", "Rāmāyaṇa", "Ṛgveda"],
        rep["C2_reach"]["texts_cited_by_every_usable_row"])
    pin("f12", "Ṛgveda reaches all 11 after fold", ["Ṛgveda"], rep["C2b_variant_fold"]["texts_cited_by_every_dict_after_fold"])
    pin("f12", "Rigveda union", 11, rep["C2b_variant_fold"]["named_variants"]["Rigveda"]["union_dicts"])
    pin("f12", "Śabdakalpadruma pwg share", 99.5, rep["C5_kosa_citers"]["Śabdakalpadruma"]["pwg_share_pct"])
    pin("f12", "Aṣṭādhyāyī pwg", 21509, rep["reproduction"]["astadhyayi_pwg_cites"])
    # C2′ accounting after the re-freeze: the 37 fold pairs live in CANON_ALIAS, so the
    # residual fold table is empty and the folded floor equals the raw private count.
    fold = rep["C2b_variant_fold"]
    pin("f12", "residual fold rows", 0, fold["fold_rows"])
    pin("f12", "private variants by tier", {"named": 0, "ascii": 0}, fold["private_variants_of_shared_by_tier"])
    pin("f12", "private→private merges", 0, fold["private_variants_merging_into_private_canonical"])
    pin("f12", "private after fold", 567, fold["private_after_fold"])
    pin("f12", "private after fold volume pct", 9.6, fold["private_after_fold_volume_pct"])
    assert fold["private_after_fold"] == rep["C2_reach"]["private_nodes"]
    assert fold["nodes_after_fold"] == rep["totals"]["nodes"]
    # Provenance drift block: regenerated at the recorded pair == committed, byte-identical.
    drift = rep["drift"]
    pin("f12", "drift regen sha == committed edges sha",
        "41bee9315b730009874b163ce266e81a998360602788edb4552ebcc703203bd0", drift["regen_sha256"])
    pin("f12", "drift regenerated cites", 826752, drift["regenerated"]["cites"])
    pin("f12", "drift regenerated nodes", 874, drift["regenerated"]["nodes"])
    pin("f12", "drift topk moves", {}, drift["topk_moves"])
    pin("f12", "drift dicts changed", {}, drift["dicts_with_changed_cites"])
    pin("f12", "drift nodes only committed", [], drift["nodes_only_committed"])
    pin("f12", "drift nodes only regenerated", [], drift["nodes_only_regenerated"])
    pin("f12", "drift edges changed", 0, drift["edges_changed"])


@pytest.mark.skipif(not (REPO / "data" / "forensic" / "f12_a50_topology_arms.json").exists(), reason="arms report absent")
def test_arms_json_pins(pin):
    """The topology figures the ledger doc and A50 §4 quote, from the committed
    arms report (seed 0x5eedca11, 1,000 nulls per arm)."""
    arms = json.loads((REPO / "data" / "forensic" / "f12_a50_topology_arms.json").read_text(encoding="utf-8"))
    by = {a["name"]: a for a in arms["arms"]}
    pin("f12", "arms input edges sha", "41bee9315b730009874b163ce266e81a998360602788edb4552ebcc703203bd0",
        arms["inputs"]["data/citations/ls_citation_edges.tsv"])
    pin("f12", "arms regen == committed", arms["inputs"]["data/citations/ls_citation_edges.tsv"],
        arms["inputs"]["data/forensic/f12_a50_regen_edges.tsv"])
    pin("f12", "A0 Q", 0.4757, by["A0-committed"]["modularity"]["observed"])
    pin("f12", "A0 Q null", 0.4094, by["A0-committed"]["modularity"]["nullMean"])
    pin("f12", "A0 margin", 0.0663, by["A0-committed"]["modularity"]["marginOverNull"])
    pin("f12", "A0 NODF", 26.857, by["A0-committed"]["nodf"]["observed"])
    pin("f12", "A0 NODF null", 31.356, by["A0-committed"]["nodf"]["nullMean"])
    pin("f12", "A0 verdict", "modular", by["A0-committed"]["verdict"])
    pin("f12", "A0 modules", [["ap", "ap90"], ["bhs", "md"], ["pwkvn", "sch"], ["ben"], ["lrv"], ["mw"], ["pw"], ["pwg"]],
        by["A0-committed"]["dictModules"])
    # The fold is in the committed data since H5407 and the regeneration IS the committed
    # data, so the folded and regenerated arms coincide with A0 exactly.
    for name in ("A1a-folded-named", "A1b-folded-ascii", "A5-regen-f4c08c57"):
        pin("f12", f"{name} == A0 Q", by["A0-committed"]["modularity"]["observed"], by[name]["modularity"]["observed"])
        pin("f12", f"{name} == A0 margin", by["A0-committed"]["modularity"]["marginOverNull"], by[name]["modularity"]["marginOverNull"])
        pin("f12", f"{name} == A0 NODF", by["A0-committed"]["nodf"]["observed"], by[name]["nodf"]["observed"])
        pin("f12", f"{name} == A0 modules", by["A0-committed"]["dictModules"], by[name]["dictModules"])
    pin("f12", "A2 nine rows margin", 0.0667, by["A2-nine-rows"]["modularity"]["marginOverNull"])
    # C7: the one-canon construction sits on the null on both statistics.
    pin("f12", "A3 verdict", "neither-detected", by["A3-one-canon"]["verdict"])
    assert by["A3-one-canon"]["modularity"]["p"] > 0.05 and by["A3-one-canon"]["nodf"]["p"] > 0.05
    # mw is a singleton in every real-data arm (no "Vedic pair"); the constructed
    # one-canon arms pair it arbitrarily and A2 drops it.
    for name in ("A0-committed", "A1a-folded-named", "A1b-folded-ascii", "A5-regen-f4c08c57"):
        assert ["mw"] in by[name]["dictModules"], name
    # The two key-borrow pairs are modules in every real-data arm (bhs+md joins them on the
    # re-frozen data — one heuristic run, see ledger C4 / A50 §4).
    for name in ("A0-committed", "A1a-folded-named", "A1b-folded-ascii", "A5-regen-f4c08c57"):
        for pair in (["ap", "ap90"], ["pwkvn", "sch"]):
            assert pair in by[name]["dictModules"], (name, pair)
    # The sweep exists, and every run's margin is far below the real graph's.
    assert arms["sweepSummary"]["runs"] == 12
    assert arms["sweepSummary"]["maxMarginOverNull"] < 0.01
    pin("f12", "sweep max margin", 0.0016, arms["sweepSummary"]["maxMarginOverNull"])
    # Provenance binding (delta pass D3.4): script hash + atlas checkout recorded.
    assert len(arms["scriptSha256"]) == 64 and "revision" in arms["cslAtlas"]
    # The two A4 arms are the same construction with the arm seed; one reads "modular" alone.
    pin("f12", "A4 f0.1 verdict", "modular", by["A4-one-canon-spell-0.1"]["verdict"])
    pin("f12", "A4 f0.1 margin", 0.0015, by["A4-one-canon-spell-0.1"]["modularity"]["marginOverNull"])
    pin("f12", "A4 f0.3 verdict", "nested", by["A4-one-canon-spell-0.3"]["verdict"])
    pin("f12", "sweep verdict counts", {"modular": 1, "nested": 2, "nestedAndModular": 3, "neither": 6},
        {k: arms["sweepSummary"][k] for k in ("modular", "nested", "nestedAndModular", "neither")})
