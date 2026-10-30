#!/usr/bin/env python3
"""Hand-derived controls and population pins for PD C3 scan links."""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import pd_aob_scan_links as c3


class ScanLinkRuleTests(unittest.TestCase):
    def test_devanagari_and_ascii_page_labels(self):
        self.assertEqual(c3.numeric_page("३८६"), 386)
        self.assertEqual(c3.numeric_page("७०9"), 709)
        self.assertIsNone(c3.numeric_page("३८६a"))

    def test_monotonic_run_rejects_isolated_and_reversed_tail(self):
        xml = """<book><pageData>
        <page leafNum="5"><pageType>Normal</pageType><pageNumber>386</pageNumber></page>
        <page leafNum="6"><pageType>Normal</pageType><pageNumber>387</pageNumber></page>
        <page leafNum="7"><pageType>Normal</pageType><pageNumber>388</pageNumber></page>
        <page leafNum="8"><pageType>Normal</pageType><pageNumber>383</pageNumber></page>
        </pageData></book>"""
        accepted, labelled = c3.monotonic_page_candidates(xml)
        self.assertEqual(labelled, 4)
        self.assertEqual(accepted, [(5, 386), (6, 387), (7, 388)])

    def test_short_run_is_not_enough(self):
        xml = """<book><pageData>
        <page leafNum="5"><pageType>Normal</pageType><pageNumber>1</pageNumber></page>
        <page leafNum="6"><pageType>Normal</pageType><pageNumber>2</pageNumber></page>
        </pageData></book>"""
        self.assertEqual(c3.monotonic_page_candidates(xml), ([], 2))

    def test_page_line_parse(self):
        self.assertEqual(c3.parse_page_locus("17. 5.", "page_line"), ("", 17, "ok"))
        self.assertEqual(c3.parse_page_locus("284. 10-11", "page_sloka"), ("", 284, "ok"))

    def test_volume_page_line_parse_and_missing_volume(self):
        self.assertEqual(c3.parse_page_locus("ii(1). 122. 17", "volume_page_line"), ("ii", 122, "ok"))
        self.assertEqual(c3.parse_page_locus("99. 16", "volume_page_line"), (None, None, "missing_volume"))

    def test_non_page_scheme_never_becomes_a_page_guess(self):
        self.assertEqual(c3.parse_page_locus("31. 9", "sarga_sloka"),
                         (None, None, "non_page_locus_scheme"))
        self.assertEqual(c3.parse_page_locus("2349", "sloka_only"),
                         (None, None, "non_page_locus_scheme"))

    def test_two_page_visual_range_expands_both_sides(self):
        ranges = [{"siglum": "X.", "archive_id": "item", "volume": "",
                   "leaf_first": "5", "leaf_last": "5", "printed_page_first": "2",
                   "printed_page_step": "2", "map_basis": "visual_test"}]
        rows = c3.visual_range_candidates(ranges)
        self.assertEqual([(r["leaf"], r["printed_page"]) for r in rows], [(5, 2)])
        ranges[0]["printed_page_first"] = "3"
        rows = c3.visual_range_candidates(ranges)
        self.assertEqual(rows[0]["printed_page"], 3)
        self.assertEqual(rows[0]["map_basis"], "visual_test")


class ScanLinkPopulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.targets, cls.loci, cls.summary = c3.build()

    def test_index_population_and_three_separate_measures(self):
        index = self.summary["index"]
        self.assertEqual(len(self.targets), 1622)
        self.assertEqual(index["work_identity_resolved"], 1615)
        self.assertEqual(index["aob_edition_identity_resolved"], 815)
        self.assertEqual(index["aob_edition_identity_by_source"]["resolved_registry"], 814)
        self.assertEqual(index["aob_edition_identity_by_source"]["resolved_c1_exact"], 1)
        self.assertEqual(index["aob_exact_scan_targets"], 14)
        self.assertEqual(index["aob_exact_scan_works"], 13)
        self.assertEqual(index["index_scan_targets"], 1622)

    def test_c2_population_reconciles_exactly(self):
        loci = self.summary["loci"]
        self.assertEqual(loci["c2_total"], 391444)
        self.assertEqual(len(self.loci), loci["aob_exact"])
        self.assertEqual(sum(loci["by_reason"].values()), len(self.loci))
        self.assertEqual(loci["by_reason"]["printed_page_unique"], loci["resolved_scan_pages"])
        self.assertEqual(loci["resolved_scan_pages"], 5323)

    def test_multipart_and_late_reset_scans_are_not_promoted(self):
        resolved = {r["principal_siglum"] for r in self.loci if r["resolution_status"] == "resolved"}
        self.assertEqual(resolved, {"VīraMi.", "SmṛtiCan.", "RasGaṅ.", "Prasā.",
                                    "Bhām.", "Aparā.", "Vaija."})
        for siglum in ("BālamBha.", "VedāntKa.", "HarVi.", "Subhāṣi."):
            self.assertEqual(self.summary["loci"]["by_siglum"][siglum]["resolved"], 0)

    def test_vaija_stops_before_the_unmapped_two_page_gap(self):
        targets = [r for r in self.loci if r["principal_siglum"] == "Vaija." and r["resolution_status"] == "resolved"]
        self.assertEqual(len(targets), 1169)
        self.assertTrue(all(int(r["printed_page"]) <= 293 for r in targets))
        self.assertTrue(all("/page/n" in r["scan_url"] for r in targets))

    def test_every_resolved_locus_has_a_distinct_page_image_target(self):
        for row in self.loci:
            if row["resolution_status"] == "resolved":
                self.assertIn("/page/n", row["scan_url"])
                self.assertTrue(row["printed_page"])
                self.assertEqual(row["reason"], "printed_page_unique")

    def test_all_fourteen_title_page_probes_are_live_images(self):
        probes = c3.live_probe_index()
        self.assertEqual(len(probes), 14)
        self.assertTrue(all(probes.values()))


if __name__ == "__main__":
    unittest.main()
