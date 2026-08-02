"""Unit tests for the `<ls>` abbreviation-token splitter (csl-atlas#222).

`scripts/obs/ls_abbreviation_frequency.py` ports `normalizeSource` +
`baseForm` from `scripts/lib/mw-classifiers.mjs` / `scripts/lib/mw-source-layers.mjs`.
These cases pin the port to the .mjs semantics and to the one-token-per-citation
invariant the artifact test in `test/ls-abbreviation-frequency.test.mjs` checks
against `data/obs/citation_registers.json`.

Run from the repo root:  python -m unittest scripts.test_ls_abbreviation_frequency
"""
import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("obs") / "ls_abbreviation_frequency.py"
SPEC = importlib.util.spec_from_file_location("ls_abbreviation_frequency", MODULE_PATH)
FREQ = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FREQ)


class AbbreviationTokenTests(unittest.TestCase):
    def test_cuts_at_the_first_locator_separator(self):
        # The shape build-citation-apparatus.mjs documents: "MBh. iii,5" -> "MBh".
        self.assertEqual(FREQ.abbreviation_token("MBh. iii,5"), "MBh")
        self.assertEqual(FREQ.abbreviation_token("Pāṇ. vi, 2, 161"), "Pāṇ")
        self.assertEqual(FREQ.abbreviation_token("RV. viii, 96, 15"), "RV")
        self.assertEqual(FREQ.abbreviation_token("Kathās,12"), "Kathās")

    def test_drops_only_a_trailing_period(self):
        self.assertEqual(FREQ.abbreviation_token("L."), "L")
        self.assertEqual(FREQ.abbreviation_token("Chr"), "Chr")

    def test_collapses_whitespace_and_trims(self):
        # `@n` is joined to the tag content by parse_cslorig.clean_citation, so
        # multi-space joins reach the splitter routinely.
        self.assertEqual(FREQ.abbreviation_token("  S  I  "), "S I")
        self.assertEqual(FREQ.abbreviation_token("Śrīk\n"), "Śrīk")

    def test_case_and_diacritics_are_preserved(self):
        # Raw form, not a fold key: MW's "MBh" and PWG's "MBH" stay distinct,
        # and "ṚV" is not flattened to "RV" (that is canonicalSiglum's job).
        self.assertNotEqual(FREQ.abbreviation_token("MBh."), FREQ.abbreviation_token("MBH."))
        self.assertEqual(FREQ.abbreviation_token("ṚV. i, 1"), "ṚV")

    def test_punctuation_only_citation_keeps_a_non_empty_token(self):
        # An empty base form would silently drop a citation and break the
        # sum-equals-<ls>-total invariant, so it falls back to the raw text.
        self.assertEqual(FREQ.abbreviation_token("."), ".")
        self.assertEqual(FREQ.abbreviation_token(",5"), ",5")

    def test_one_token_per_citation(self):
        citations = ["MBh. iii,5", "L.", ".", "RV. viii, 96, 15"]
        self.assertEqual(len([FREQ.abbreviation_token(c) for c in citations]), len(citations))
        self.assertTrue(all(FREQ.abbreviation_token(c) for c in citations))


if __name__ == "__main__":
    unittest.main()
