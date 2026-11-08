#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7507 pins — the Stage 4 external-portability gate census.

Drift here is a broken artefact, not news. The census is the dated record:
verdicts, timestamps, content hashes and evidence files are pinned exactly
as committed; any post-hoc edit to a verdict or an evidence transcript
fails here and in scripts/stage4_portability_check.py.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = os.path.join(ROOT, "data", "stage4_portability")

# sha256 of the census JSON at commit time — the dated-verdict freeze.
CENSUS_SHA = "11e19928350de484cdd1c4e91f4e562bb77cb041c6d4e8f0cec979e355ef1820"

EVIDENCE_SHA = {
    "menota_catalogue_rendered_2026-10-30.txt": "3e936f19ecec2478b6b874235c10c75b0c3cb114f6d308b149f360b4e069cfb3",
    "oldrus_wsgi_reader_2026-10-30.md": "669dd5b53c10e1b7b756cc4671e31b752580ca67ce2d9a3ab9775b09cb630b6e",
    "onp_interstitial_reader_2026-10-30.md": "4d7f67940b0875a7c030ff36e8fc790e5bb668c057dae57ffc39318e5c675113",
    "tlio_gattoweb_reader_2026-10-30.md": "829babb386231a5ac1cd04457dd16425ccff1cf279df24d8b7a2e2f26e7607f1",
    "webcorpora_root_reader_2026-10-30.md": "5c16c2b3b001d7d741ed777d1a024210a02fba6679f97c093d1545682a0e396b",
}


def test_census_frozen():
    text = open(os.path.join(D, "stage4_gate_census.json"), encoding="utf-8").read()
    assert hashlib.sha256(text.encode("utf-8")).hexdigest() == CENSUS_SHA


def test_evidence_frozen():
    for name, sha in EVIDENCE_SHA.items():
        p = os.path.join(D, "probe_evidence", name)
        assert os.path.exists(p), f"missing evidence {name}"
        assert hashlib.sha256(open(p, "rb").read()).hexdigest() == sha, name


def test_census_verdict_pins():
    d = json.load(open(os.path.join(D, "stage4_gate_census.json"), encoding="utf-8"))
    v = d["verdict_summary"]
    assert d["part2_onp_menota_executed"] is False
    assert "gate closed" in v["onp_menota"]
    assert "gate closed" in v["cad_isac"]
    assert "FIRED" in v["russian_slovar"]
    assert "held to medieval slice" in v["gdli_tlio"]
    assert v["menota_corpus_side"].startswith("public, 394 texts")
    # the ONP live-host refinement must stay (it corrects §9's flat unreachable)
    onp = next(c for c in d["candidates"] if c["candidate"] == "ONP↔Menota")
    assert "browser-verification" in onp["live_host_refinement"]
    # Menota counts pin
    counts = onp["menota_corpus_side"]["probes"][-1]["counts"]
    assert counts == {
        "main_codices": 91,
        "charters": 196,
        "runic_inscriptions": 100,
        "le_lingue_nordiche": 7,
        "total": 394,
    }
    # TLIO dated count pin
    tlio = next(c for c in d["candidates"] if c["candidate"] == "GDLI↔OVI/TLIO")
    assert "3295 testi" in json.dumps(tlio, ensure_ascii=False)
    # P1-P5 carried verbatim, unexecuted
    pre = d["preregistrations_onp_menota_p1_p5"]
    assert pre["status"].startswith("fixed in advance")
    assert "≈2.6×" in pre["P3"]
