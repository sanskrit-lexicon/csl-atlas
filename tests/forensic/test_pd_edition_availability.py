#!/usr/bin/env python3
"""Hand-derived controls for the C1 availability aggregation."""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "scripts", "lib"))
import pd_edition_availability as pea
import quotation_units


class EditionAvailabilityTests(unittest.TestCase):
    def test_continuation_inherits_immediately_preceding_siglum(self):
        loci, continuations, tokens = pea.citation_tail_detailed(
            " MahāBhā. 1.2.3; 4.5.6; ṚV. 2.3.4; 5.6.7")
        self.assertEqual((loci, continuations), (2, 2))
        self.assertEqual(tokens, ["MahāBhā.", "MahāBhā.", "ṚV.", "ṚV."])

    def test_unassigned_continuation_stays_visible(self):
        loci, continuations, tokens = pea.citation_tail_detailed(" ; 1.2.3")
        self.assertEqual((loci, continuations), (0, 1))
        self.assertEqual(tokens, ["__UNASSIGNED_CONTINUATION__"])

    def test_quotation_counter_preserves_attestation_mass(self):
        body = "{#headword#} {#arthaH#} MahāBhā. 1.2.3; 4.5.6"
        units = quotation_units.count_units(body, pea.citation_tail_detailed)
        self.assertEqual(units["quotations"], 1)
        self.assertEqual(units["loci"], 1)
        self.assertEqual(units["continuation_loci"], 1)
        self.assertEqual(units["tokens"], ["MahāBhā.", "MahāBhā."])

    def test_continuation_only_nonquotation_is_not_an_attestation(self):
        body = "{#headword#} {#arthaH#} ; 1.2.3"
        units = quotation_units.count_units(body, pea.citation_tail_detailed)
        self.assertEqual(units["quotations"], 0)
        self.assertEqual(units["tokens"], [])

    def test_availability_never_silently_includes_unknown(self):
        self.assertNotIn("unresolved", pea.AVAILABLE)
        self.assertNotIn("unavailable_verified", pea.AVAILABLE)
        self.assertIn("available_partial", pea.AVAILABLE)

    def test_blank_and_shared_identities_have_no_registry_title(self):
        _families, _crosswalk, registry, index_titles, siglum_work, _work_sigla, _aob = pea.load_context()
        self.assertNotIn("", registry)
        self.assertNotIn("LaCandr.", siglum_work)
        self.assertNotIn("LaCandr.", index_titles)

    def test_aob_projection_never_promotes_shared_sigla(self):
        rows = pea.read_tsv("pd_edition_availability_by_siglum.tsv")
        for row in rows:
            row["attestations"] = int(row["attestations"])
        _families, _crosswalk, _registry, _index_titles, _siglum_work, _work_sigla, aob = pea.load_context()
        projected = pea.project_aob(rows, aob)
        self.assertEqual(len(projected), 1437)
        for row in projected:
            if row["shared_raw_siglum"] == "yes":
                self.assertEqual(row["availability"], "ambiguous_shared_siglum")
                self.assertGreater(row["attestations_direct"], 0)


if __name__ == "__main__":
    unittest.main()
