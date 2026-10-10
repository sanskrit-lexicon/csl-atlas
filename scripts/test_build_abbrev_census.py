"""Unit tests for the A72 abbreviation-census builders (H6409).

Pins the collision/polysemy semantics on tiny fixtures: raw-string keys
(case-sensitive), casefold+NFC expansion comparison, and the reused `<ls>`
invariant check. No corpus access — everything runs on synthetic payloads.

Run from the repo root:  python -m unittest scripts.test_build_abbrev_census
"""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("build_abbrev_census.py")
SPEC = importlib.util.spec_from_file_location("build_abbrev_census", MODULE_PATH)
CENSUS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CENSUS)


def table_fixture():
    legends = {
        "MW": [{"abbr": "N.", "expansion": "noun.", "category": "grammatical"},
               {"abbr": "c.", "expansion": "conjugation", "category": "grammatical"},
               {"abbr": "V.", "expansion": "Vedic", "category": "works"}],
        "SHS": [{"abbr": "N.", "expansion": "Neuter", "category": "grammatical"},
                {"abbr": "c.", "expansion": "causal", "category": "grammatical"}],
        "PWG": [{"abbr": "N.", "expansion": "N. pr.", "category": "works"}],
    }
    scan = {"mw": {"entries": 10,
                   "tags": {"ab": {"N.": 5, "cf.": 2}, "lex": {"m.": 3}, "lang": {}},
                   "tagTotals": {"ab": 7, "lex": 3, "lang": 0},
                   "frontMatterFile": {"front": 0, "back": 0}},
            "shs": {"entries": 4,
                    "tags": {"ab": {"N.": 1}, "lex": {"f.": 2}, "lang": {"Gk.": 1}},
                    "tagTotals": {"ab": 1, "lex": 2, "lang": 1},
                    "frontMatterFile": {"front": 12, "back": 0}}}
    return CENSUS.build_label_table(legends, scan)


class ExpansionKeyTests(unittest.TestCase):
    def test_casefold_and_trailing_period(self):
        self.assertEqual(CENSUS.expansion_key("Neuter."), CENSUS.expansion_key("neuter"))
        self.assertEqual(CENSUS.expansion_key("N. pr."), "n. pr")

    def test_nfc_and_whitespace(self):
        self.assertEqual(CENSUS.expansion_key("  saṃ\u0301khya "), CENSUS.expansion_key("saṃ́khya"))

    def test_raw_keys_stay_case_sensitive(self):
        table = table_fixture()
        # "N." (noun/neuter/N. pr.) and a hypothetical lowercase "n." never merge.
        self.assertIn("N.", table)
        table2 = CENSUS.build_label_table({"X": [{"abbr": "n.", "expansion": "neuter",
                                                  "category": "grammatical"}]}, {})
        self.assertNotIn("N.", table2)
        self.assertIn("n.", table2)


class CollisionMatrixTests(unittest.TestCase):
    def test_cross_dictionary_collision_computed(self):
        matrix = CENSUS.build_collision_matrix(table_fixture())
        by_label = {row["label"]: row for row in matrix}
        # 2006's "N.": noun (MW) vs neuter (SHS) vs N. pr. (PWG) — three senses.
        self.assertEqual(by_label["N."]["polysemy"], 3)
        # Same-string same-meaning across dicts must NOT collide.
        self.assertNotIn("cf.", by_label)
        # Sorted by polysemy desc then label.
        self.assertEqual(matrix[0]["label"], "N.")

    def test_within_dictionary_collision_counts(self):
        legends = {"GRA": [{"abbr": "c.", "expansion": "causal", "category": "grammatical"},
                           {"abbr": "c.", "expansion": "conjugation", "category": "grammatical"}]}
        matrix = CENSUS.build_collision_matrix(CENSUS.build_label_table(legends, {}))
        self.assertEqual(len(matrix), 1)
        self.assertEqual(matrix[0]["polysemy"], 2)
        # Each sense lists its own dict; both senses come from GRA alone.
        self.assertEqual(sorted(s["dicts"] for s in matrix[0]["senses"]), [["GRA"], ["GRA"]])

    def test_identical_expansion_folded_together(self):
        legends = {"A": [{"abbr": "pl.", "expansion": "plural.", "category": "grammatical"}],
                   "B": [{"abbr": "pl.", "expansion": "Plural", "category": "grammatical"}]}
        matrix = CENSUS.build_collision_matrix(CENSUS.build_label_table(legends, {}))
        self.assertEqual(matrix, [])


class PolysemyTests(unittest.TestCase):
    def test_counts_and_uses_only_legend_rows(self):
        polysemy = CENSUS.build_polysemy(table_fixture())
        self.assertEqual(polysemy["N."]["nExpansions"], 3)
        self.assertEqual(polysemy["N."]["nDicts"], 3)
        # Tags-only strings carry no legend row and stay out of polysemy.
        self.assertNotIn("cf.", polysemy)


class LsInvariantTests(unittest.TestCase):
    def test_sum_equals_register_total(self):
        ls_freq = {"dicts": {"mw": {"MBh": 3, "RV": 2}}}
        registers = {"dicts": {"mw": {"ls": 5}, "pw": {"ls": 9}}}
        self.assertEqual(CENSUS.check_ls_invariant(ls_freq, registers), [])

    def test_violation_reported(self):
        ls_freq = {"dicts": {"mw": {"MBh": 3}}}
        registers = {"dicts": {"mw": {"ls": 4}}}
        violations = CENSUS.check_ls_invariant(ls_freq, registers)
        self.assertEqual(violations, [{"dict": "mw", "sumTokens": 3, "registerLs": 4}])


class LoadLegendsTests(unittest.TestCase):
    def test_status_data_rows_categorised(self):
        payload = {"dicts": [
            {"code": "MW", "status": "data", "grammatical": [{"abbr": "N.", "expansion": "noun"}],
             "works": [{"abbr": "V.", "expansion": "Vedas"}], "mixed": []},
            {"code": "WIL", "status": "none"},
        ], "counts": {"total": 2, "withData": 1, "tokensOnly": 0, "none": 1}}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
            json.dump(payload, fh)
            path = fh.name
        try:
            layer = CENSUS.load_legends(path)
            self.assertEqual(layer["catalogued"], 2)
            self.assertEqual(len(layer["legends"]["MW"]), 2)
            self.assertEqual(layer["legends"]["MW"][0]["category"], "grammatical")
            self.assertNotIn("WIL", layer["legends"])
        finally:
            Path(path).unlink()


class StripMarkupTests(unittest.TestCase):
    def test_inner_tags_and_whitespace(self):
        self.assertEqual(CENSUS.strip_markup("<s>a</s>  q.v."), "a q.v.")
        self.assertEqual(CENSUS.strip_markup(None), "")


if __name__ == "__main__":
    unittest.main()
