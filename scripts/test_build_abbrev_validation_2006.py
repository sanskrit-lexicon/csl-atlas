#!/usr/bin/env python3
"""Tests for the H6459 A72 validation-table builder.

Locks the verdict engine against the committed census payload: verdict
vocabulary, the acceptance spot-check class, the corrected-class flagship
rows, and byte-stable regeneration. Runs from the repo root:
    python -m unittest scripts.test_build_abbrev_validation_2006
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

import build_abbrev_validation_2006 as builder  # noqa: E402


class Validation2006Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.census = builder.load_census()
        cls.rows = builder.build_rows(cls.census)
        cls.by_label_sense = {(r["label"], r["sense_2006"]): r for r in cls.rows}

    def test_rows_match_claim_table(self):
        self.assertEqual(len(self.rows), len(builder.CLAIMS))

    def test_verdict_vocabulary(self):
        for row in self.rows:
            self.assertIn(row["verdict"],
                          ("confirmed", "extended", "corrected", "unmappable"),
                          f"bad verdict for {row['label']}: {row['verdict']}")
            self.assertTrue(row["evidence"], f"empty evidence for {row['label']}")

    def test_denominators_sum(self):
        counts, _ = builder.denominators(self.rows)
        self.assertEqual(sum(counts.values()), len(builder.CLAIMS))

    def test_spot_check_class_present_with_verdicts(self):
        # Acceptance: V./c./M./P./N. and the Petersburg sigla each carry a
        # computed verdict, and the denominators line is stated.
        for label in ("V.", "c.", "M.", "P.", "N.", "BR", "pw"):
            rows = [r for r in self.rows if r["label"] == label]
            self.assertTrue(rows, f"no claim rows for spot-check label {label}")
            self.assertTrue(all(r["verdict"] for r in rows))
        counts, _ = builder.denominators(self.rows)
        self.assertGreater(counts["confirmed"] + counts["extended"], 0)
        self.assertGreater(counts["unmappable"], 0)

    def test_mw_contradictions_corrected(self):
        # MW is digitized and its c. legends carry only "case" — the 2006
        # conjugation/class attribution is the computed corrected class.
        for sense in ("conjugation", "class"):
            row = self.by_label_sense[("c.", sense)]
            self.assertEqual(row["verdict"], "corrected", row)
            self.assertIn("case", row["evidence"])
        # int. carries intensiv/intransitive, not the 2006 interjection sense.
        row = self.by_label_sense[("int.", "interjection")]
        self.assertEqual(row["verdict"], "corrected", row)

    def test_petersburg_sigla(self):
        self.assertEqual(
            self.by_label_sense[("BR", "Böhtlingk–Roth Petersburg Wörterbuch")]["verdict"],
            "confirmed")
        self.assertEqual(
            self.by_label_sense[("pw", "Petersburg Wörterbuch (kleines)")]["verdict"],
            "confirmed")
        row = self.by_label_sense[("PW", "Petersburg Wörterbuch (großes)")]
        self.assertEqual(row["verdict"], "unmappable")
        self.assertIn("U1", row["evidence"])

    def test_dict_level_confirmed_on_mapped_witnesses(self):
        row = self.by_label_sense[("irreg.", "irregular")]  # MW digitized
        self.assertEqual(row["verdict"], "confirmed")
        self.assertIn("dict-level", row["evidence"])
        row = self.by_label_sense[("Comp.", "Compound")]  # Bf -> BEN digitized
        self.assertEqual(row["verdict"], "extended")
        self.assertIn("dict-level", row["evidence"])

    def test_witnessless_unattested_sense_is_corrected_not_u3(self):
        # M. = Murti names no witness; the digitized M. legends contradict it.
        row = self.by_label_sense[("M.", "Murti")]
        self.assertEqual(row["verdict"], "corrected", row)
        self.assertIn("no witness named", row["evidence"])

    def test_tsv_regeneration_is_byte_stable(self):
        first = builder.render_tsv(self.rows)
        second = builder.render_tsv(builder.build_rows(self.census))
        self.assertEqual(first, second)
        for line in first.splitlines():
            self.assertNotIn("\t\t", line)


if __name__ == "__main__":
    unittest.main()
