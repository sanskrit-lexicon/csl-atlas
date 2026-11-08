#!/usr/bin/env python3
"""Tests for the H6465 A72 label-reading guide generator.

Core invariant under test: every guide row is traceable to a computed census
payload row (data/abbrev/abbrev_census.json) — expansions verbatim, sense
counts from the census's own polysemy semantics, and labels absent from the
payload explicitly flagged «нет в цензе», never glossed.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import build_abbrev_label_guide as gen  # noqa: E402

PAYLOAD = gen.load_payload()
ROWS = gen.label_rows(PAYLOAD)
GUIDE_MD = gen.render_guide(PAYLOAD, ROWS)
TSV = gen.render_tsv(ROWS)


class TestTraceability(unittest.TestCase):
    def test_every_expansion_row_exists_verbatim_in_payload(self):
        """Each in-census guide row (expansion, dict) must appear in labelTable legends."""
        lt = PAYLOAD["labelTable"]
        for r in ROWS:
            if not r["in_census"]:
                continue
            legends = lt[r["label"]]["legends"]
            pairs = {(lg["expansion"], lg["dict"]) for lg in legends}
            for d in r["legend_dicts"].split(";"):
                self.assertIn(
                    (r["expansion"], d),
                    pairs,
                    msg=f"{r['label']}: legend row not found verbatim in payload",
                )

    def test_census_sense_counts_come_from_polysemy_field(self):
        """TSV sense count must equal the census's own nExpansions, not a re-derivation."""
        for r in ROWS:
            if not r["in_census"]:
                continue
            expected = PAYLOAD["polysemy"][r["label"]]["nExpansions"]
            self.assertEqual(r["distinct_expansions"], expected, msg=f"{r['label']} sense count drifted")

    def test_pinned_c_row(self):
        """c. = 4 census senses: case / causal / causativ / causatif (Gasūns 2006 exhibit)."""
        c_rows = [r for r in ROWS if r["label"] == "c."]
        self.assertEqual(PAYLOAD["polysemy"]["c."]["nExpansions"], 4)
        joined = " | ".join(r["expansion"].lower() for r in c_rows)
        for needle in ("case", "causal", "causativ", "causatif"):
            self.assertIn(needle, joined)
        self.assertEqual(c_rows[0]["distinct_expansions"], 4)


class TestNotInCensus(unittest.TestCase):
    def test_flagged_labels_are_genuinely_absent(self):
        flagged = [r["label"] for r in ROWS if not r["in_census"]]
        self.assertTrue(flagged, "generator must exercise the not-in-census path")
        for label in flagged:
            self.assertNotIn(label, PAYLOAD["labelTable"], msg=f"{label} is in the payload after all")

    def test_inj_marked_not_in_census_in_guide(self):
        self.assertNotIn("inj.", PAYLOAD["labelTable"])
        self.assertIn("Нет в цензе", GUIDE_MD)
        self.assertIn("`inj.`", GUIDE_MD)


class TestHeadlines(unittest.TestCase):
    def test_headline_numbers_match_census_rows(self):
        den = PAYLOAD["denominators"]
        polysemous = sum(1 for v in PAYLOAD["polysemy"].values() if v["nExpansions"] >= 2)
        for needle in (str(den["distinctLabelsInTable"]), str(len(PAYLOAD["polysemy"])), str(polysemous)):
            self.assertIn(needle, GUIDE_MD)

    def test_feedback_route_present_in_guide(self):
        self.assertIn("label-misread-feedback.schema.json", GUIDE_MD)
        self.assertIn("pool-aNN", GUIDE_MD)

    def test_tsv_wellformed(self):
        lines = TSV.rstrip("\n").split("\n")
        self.assertEqual(lines[0], "\t".join(gen.TSV_HEADER))
        self.assertEqual(len(lines) - 1, len(ROWS))


class TestByteStability(unittest.TestCase):
    def test_check_mode_passes(self):
        proc = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "build_abbrev_label_guide.py"), "--check"],
            capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + proc.stderr)
        self.assertIn("CHECK PASS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
