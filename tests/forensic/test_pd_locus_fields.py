#!/usr/bin/env python3
"""Hand-derived controls for C2 locus extraction and structural flags."""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "scripts", "lib"))
import pd_locus_fields as plf
import quotation_units


class LocusFieldTests(unittest.TestCase):
    def test_continuation_inherits_siglum_and_locus(self):
        loci, continuations, records = plf.citation_records(" ManuSm. 2. 181; 9. 242; 11. 45")
        self.assertEqual((loci, continuations), (1, 2))
        self.assertEqual(records, [("ManuSm.", "2. 181", "siglum"),
                                   ("ManuSm.", "9. 242", "continuation"),
                                   ("ManuSm.", "11. 45", "continuation")])

    def test_multiple_sigla_split_at_their_own_boundaries(self):
        _loci, _cont, records = plf.citation_records(" MahāBhā. 1.2.3, ṚV. 4.5.6")
        self.assertEqual(records, [("MahāBhā.", "1.2.3", "siglum"),
                                   ("ṚV.", "4.5.6", "siglum")])

    def test_empty_locus_is_not_a_pair(self):
        self.assertEqual(plf.classify("PadMañ.", ""), ("empty", "empty"))

    def test_structural_review_flags(self):
        self.assertEqual(plf.classify("P.", "i. 2. 3 ("), ("alphanumeric", "unbalanced_parentheses"))
        self.assertEqual(plf.classify("P.", "uses the technical term"), ("textual", "textual"))
        self.assertEqual(plf.classify("__UNASSIGNED_CONTINUATION__", "1.2"), ("unassigned", "unassigned"))

    def test_h6949_boundary_is_unchanged(self):
        units = quotation_units.count_units("{#headword#} {#arthaH#} ManuSm. 2.181; 9.242", plf.citation_records)
        self.assertEqual(units["quotations"], 1)
        self.assertEqual(units["attestations"], 2)
        self.assertEqual(len(units["tokens"]), 2)

    def test_committed_entry_statuses_sum_to_population(self):
        summary = __import__("json").load(open(os.path.join(ROOT, "data", "pd", "pd_locus_summary.json"), encoding="utf-8"))
        statuses = summary["by_entry_status"]
        self.assertEqual(sum(statuses.values()), 107630)
        self.assertEqual(statuses["clean"] + statuses["nonempty_only"], 105890)


if __name__ == "__main__":
    unittest.main()
