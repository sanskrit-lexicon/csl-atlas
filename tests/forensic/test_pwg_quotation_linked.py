"""Pins for the PWG quotation-linked count and the DCS 2021 baseline (19-10-2026).

Two distinctions the A68 manuscript now leans on, each pinned twice: once by
hand on a miniature entry (the rule), once against the committed artifact (the
corpus-level numbers).

1. **Raw ``<ls>`` tags vs quotation-linked attestations.** The unit
   (``scripts/lib/quotation_units.py``) counts an ``<ls>`` tag only when it
   closes a run of ``{#...#}`` blocks. A tag that hangs off the headword, or
   off plain text, is a reference, not an attestation — and PWG's 801,788 raw
   tags are 729,719 quotation-linked. Probe: ``scripts/pwg_quotation_linked_tags.py``;
   artifact: ``data/pd/pwg_quotation_linked_tags.json``.

2. **The 2021 baseline has two ends.** DCS-2021 carried six texts DCS-2026
   dropped (892 tokens: four commentaries, two zero-token stubs). The frozen
   spine's 2021 denominator (4,577,021) already excludes them, so the published
   74.06 % (74.1 %) is the like-for-like baseline and 74.04 % (74.0 %) is the
   raw one. Probe: ``scripts/pd_dcs_2021_baseline.py``; artifact:
   ``data/pd/pd_dcs_2021_baseline.json``.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
for p in (str(ROOT / "scripts"), str(ROOT / "scripts" / "lib")):
    if p not in sys.path:
        sys.path.insert(0, p)

import pd_quotations_vs_pwg as pdc
import quotation_units


def _load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


# --- 1. the rule, by hand ---------------------------------------------------

def test_pwg_tag_off_the_headword_is_not_an_attestation():
    # <ls> right after the headword block: a reference, no quotation closes it.
    # The second <ls> closes the block run {#q#} and IS an attestation.
    body = "{#hw#} <ls>M. 1</ls> {#q#} <ls>M. 2</ls>"
    u = quotation_units.count_units(body, pdc.pwg_marker)
    assert u["quotations"] == 1
    assert u["attestations"] == 1
    # ... while the raw tag count sees both
    import re
    assert len(re.findall(r"<ls([^>]*)>(.*?)</ls>", body, re.S)) == 2


def test_pwg_tag_after_plain_text_is_not_an_attestation():
    # the block run {#q#} is followed by prose, and only then the tag
    body = "{#hw#} {#q#} some prose <ls>M. 3</ls>"
    u = quotation_units.count_units(body, pdc.pwg_marker)
    assert u["quotations"] == 1
    assert u["attestations"] == 1


# --- 1b. the corpus-level split, against the committed artifact -------------

def test_pwg_quotation_linked_artifact_pins():
    art = _load("data/pd/pwg_quotation_linked_tags.json")
    t = art["totals"]
    assert t["entries"] == 123366
    assert t["raw_ls_tags"] == 801788
    assert t["quotation_linked_attestations"] == 729719
    assert t["non_quotation_linked_tags"] == 72069
    assert t["quotations"] == 329623
    assert art["committed_checks"]["raw_ls_tags"]["ok"]
    assert art["committed_checks"]["quotations"]["ok"]
    # the two denominators the A68 four-ledger table may use
    assert art["ratios"]["pd_attestations_over_raw_pwg_tags"] == 52.4
    assert art["ratios"]["pd_attestations_over_quotation_linked_pwg_tags"] == 57.5


# --- 2. the 2021 baseline, both ends ----------------------------------------

def test_2021_baseline_artifact_pins():
    art = _load("data/pd/pd_dcs_2021_baseline.json")
    d = art["dropped_since_2021"]
    assert d["count"] == 6
    assert d["tokens_2021"] == 892
    assert d["commentaries"] == 4
    assert d["zero_token_stubs"] == 2
    t = art["totals"]
    assert t["total_dcs_tok_2021_raw"] == 4577913
    assert t["total_dcs_tok_2021_like_for_like"] == 4577021
    b = art["baselines"]
    assert b["like_for_like_2021_pct"] == 74.06
    assert b["raw_2021_pct"] == 74.04
    assert b["pct_2026"] == 77.88
    assert all(v["ok"] for v in art["committed_checks"].values())


def test_2021_dropped_texts_are_the_six_named_in_the_report():
    art = _load("data/pd/pd_dcs_2021_baseline.json")
    names = {r["text_2021"] for r in art["dropped_since_2021"]["rows"]}
    assert names == {
        "Cakra ?) on Suśr",
        "Comm. on the Kāvyālaṃkāravṛtti",
        "Ekākṣarakoṣa",
        "Hārāṇacandara on Suśr",
        "Khādiragṛhyasūtrarudraskandavyākhyā",
        "Nāḍīvijñāna",
    }
