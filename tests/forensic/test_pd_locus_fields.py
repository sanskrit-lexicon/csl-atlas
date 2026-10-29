#!/usr/bin/env python3
"""Hand-derived controls for H7458/C2 locus-field extraction.

Expected values are read from the miniature printed citations in each test, not
from a previous run of the parser.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "scripts", "lib"))
import pd_locus_fields as plf


class LocusFieldTests(unittest.TestCase):
    def parse(self, tail, known=None):
        return plf.parse_citation_tail(tail, known or set())

    def test_basic_locus_and_two_continuations(self):
        records, diagnostics = self.parse(" ManuSm. 2. 181; 9. 242; 11. 45")
        self.assertEqual([(r["siglum"], r["locus"], r["kind"]) for r in records], [
            ("ManuSm.", "2. 181", "siglum"),
            ("ManuSm.", "9. 242", "continuation"),
            ("ManuSm.", "11. 45", "continuation"),
        ])
        self.assertEqual(diagnostics, [])

    def test_lowercase_discourse_is_not_a_siglum_even_with_digits(self):
        records, diagnostics = self.parse(" cf. 10; comm. 20")
        self.assertEqual(records, [])
        self.assertEqual([d[1] for d in diagnostics], ["discourse_not_siglum", "discourse_not_siglum"])

    def test_census_known_lowercase_token_remains_a_candidate(self):
        self.assertTrue(plf.candidate_siglum("a.", {"a."}))
        self.assertFalse(plf.candidate_siglum("cf.", set()))

    def test_bare_siglum_is_not_a_locus_pair(self):
        records, diagnostics = self.parse(" Nāg. ")
        self.assertEqual(records, [])
        self.assertEqual(diagnostics[0][:2], ("Nāg.", "siglum_without_locus"))

    def test_uppercase_roman_locus_is_not_a_second_siglum(self):
        records, diagnostics = self.parse(" TaiS. V. v. 1. 6")
        self.assertEqual(len(records), 1)
        self.assertEqual((records[0]["siglum"], records[0]["locus"]), ("TaiS.", "V. v. 1. 6"))
        self.assertEqual([d[1] for d in diagnostics], ["marker_consumed_by_locus"])

    def test_census_confirmed_line_wrap_is_rejoined(self):
        records, _diagnostics = self.parse(" Śiśu-  Va. 3. 4", {"ŚiśuVa."})
        self.assertEqual(records[0]["siglum"], "ŚiśuVa.")
        self.assertEqual(records[0]["locus"], "3. 4")

    def test_page_marker_does_not_truncate_a_locus(self):
        records, diagnostics = self.parse(" ṚV. vi. [Page1-0001b+ 54]  17. 8")
        self.assertEqual(records[0]["locus"], "vi. 17. 8")
        self.assertEqual(diagnostics, [])

    def test_page_number_is_not_a_continuation(self):
        records, diagnostics = self.parse(" PañcBr. xxi. 1. 2; [Page1-0003b+ 64]")
        self.assertEqual(len(records), 1)
        self.assertEqual([d[1] for d in diagnostics], ["page_marker_only_continuation"])

    def test_page_split_qualifier_is_not_a_second_siglum(self):
        records, diagnostics = self.parse(" NyāySu. [Page1-0011b+ 64] (So.) 72. 2")
        self.assertEqual([(r["siglum"], r["locus"]) for r in records], [("NyāySu.", "72. 2")])
        self.assertEqual([d[1] for d in diagnostics], ["page_separated_qualifier"])

    def test_appendix_qualifier_with_spaces_stays_inside_locus(self):
        records, diagnostics = self.parse(" MahāBhā. i. (App.) 64. 27")
        self.assertEqual(records[0]["locus"], "i. (App.) 64. 27")
        self.assertEqual(diagnostics, [])

    def test_prose_digits_do_not_become_a_continuation(self):
        records, diagnostics = self.parse(" MahāBh. i. 15. 14; it stands for all its 18 varieties")
        self.assertEqual(len(records), 1)
        self.assertEqual([d[1] for d in diagnostics], ["continuation_without_locus"])

    def test_variant_and_editor_note_are_not_locus_fields(self):
        records, diagnostics = self.parse(" Hitopa. 2. 137 (3) v. l. (M.  Müller Ed.)")
        self.assertEqual([(r["siglum"], r["locus"]) for r in records], [("Hitopa.", "2. 137 (3)")])
        self.assertNotIn("M.", [r["siglum"] for r in records])
        self.assertTrue(all(r["locus"] != "M" for r in records))

    def test_sense_marker_ends_citation_tail(self):
        records, _diagnostics = self.parse(" ManuSm. 1. 2; {@2@} next sense AgniP. 3. 4")
        self.assertEqual([(r["siglum"], r["locus"]) for r in records], [("ManuSm.", "1. 2")])

    def test_unassigned_continuation_stays_visible(self):
        records, diagnostics = self.parse(" ; 1. 2. 3")
        self.assertEqual(records, [])
        self.assertEqual(diagnostics[0][:2], ("__UNASSIGNED_CONTINUATION__", "unassigned_continuation"))


if __name__ == "__main__":
    unittest.main()
