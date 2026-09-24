"""Tests for strict review-decision validation."""
import copy
import importlib.util
import unittest
from datetime import datetime, timezone
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("validate_review_decisions.py")
SPEC = importlib.util.spec_from_file_location("validate_review_decisions", MODULE_PATH)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class ReviewDecisionValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sheets = VALIDATOR.expected_sheets()
        cls.sheet_id = "csl-atlas-skd-iti_100units"
        cls.expected = cls.sheets[cls.sheet_id]

    def payload(self):
        return {
            "sheet_id": self.sheet_id,
            "generated": "17-07-2026",
            "decided": len(self.expected),
            "reviewer": "gasyoun",
            "reviewedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "complete": True,
            "items": [
                {"id": item_id, "decision": "approve", "note": ""}
                for item_id in self.expected
            ],
        }

    def assert_invalid(self, payload, pattern):
        with self.assertRaisesRegex(VALIDATOR.ValidationError, pattern):
            VALIDATOR.validate_export(payload, self.sheets)

    def test_expected_queue_counts_are_stable(self):
        self.assertEqual(
            {sheet_id: len(items) for sheet_id, items in self.sheets.items()},
            {
                "csl-atlas-skd-iti_100units": 102,
                "csl-atlas-tradition-tags_119texts": 114,  # H5407: 5 duplicate variant rows folded; the 119texts stem is the sheet-ID contract
                # H5308 B1 (design §3.1): fallback to the reviewed-ok set —
                # H1621 left 0 open rows, and a 0-row expectation rejected every
                # returned H4 export while the builder emitted 89 cards.
                "csl-atlas-h4-semantic-field_89rows": 89,
                "csl-atlas-xref-shared-core_40edges": 40,
                "csl-atlas-r2-checkpoint_10rows": 10,  # H5308 B5: R2's first sheet
            },
        )

    def test_complete_export_matches_all_102_stable_ids(self):
        self.assertEqual(VALIDATOR.validate_export(self.payload(), self.sheets), 102)

    def test_incomplete_export_is_rejected(self):
        payload = self.payload()
        payload["complete"] = False
        self.assert_invalid(payload, "complete:true")

    def test_reviewer_and_utc_timestamp_are_required(self):
        payload = self.payload()
        payload["reviewer"] = ""
        self.assert_invalid(payload, "reviewer")
        payload = self.payload()
        payload["reviewedAt"] = "2026-07-17T12:00:00"
        self.assert_invalid(payload, "UTC offset")

    def test_missing_duplicate_and_unknown_ids_are_rejected(self):
        payload = self.payload()
        payload["items"].pop()
        self.assert_invalid(payload, "1:1")

        payload = self.payload()
        payload["items"][-1]["id"] = payload["items"][0]["id"]
        self.assert_invalid(payload, "unique")

        payload = self.payload()
        payload["items"][-1]["id"] = "skd-iti:unknown:0"
        self.assert_invalid(payload, "differ from source packet")

    def test_closed_verdict_vocabulary_is_enforced(self):
        payload = self.payload()
        payload["items"][0]["decision"] = "yes"
        self.assert_invalid(payload, "invalid or missing verdict")

    def test_rejection_needs_alternative_label_and_rationale(self):
        item_id, (proposed, allowed) = next(iter(self.expected.items()))
        corrected = next(label for label in allowed if label != proposed)
        payload = self.payload()
        item = next(row for row in payload["items"] if row["id"] == item_id)
        item["decision"] = "reject"
        item["note"] = ""
        self.assert_invalid(payload, "requires a note")

        item["note"] = f"{proposed}: no change"
        self.assert_invalid(payload, "must differ")

        item["note"] = f"{corrected}: source context contradicts the proposal"
        self.assertEqual(VALIDATOR.validate_export(payload, self.sheets), 102)


class PoolModeTests(unittest.TestCase):
    """H5308 B2/B4: per-annotator slices validated against the pool manifest."""

    @classmethod
    def setUpClass(cls):
        cls.sheets = VALIDATOR.expected_sheets()
        cls.pool = {
            "annotators": ["pool-a01", "pool-a02"],
            "packets": {
                "csl-atlas-r2-checkpoint_10rows": {
                    "rows": {row_id: ["pool-a01", "pool-a02"]
                             for row_id in cls.sheets["csl-atlas-r2-checkpoint_10rows"]},
                },
            },
        }
        cls.sheet_id = "csl-atlas-r2-checkpoint_10rows"
        cls.expected = VALIDATOR.pool_expected(cls.pool, cls.sheet_id, "pool-a01")

    def payload(self, reviewer="pool-a01"):
        return {
            "sheet_id": self.sheet_id,
            "decided": len(self.expected),
            "reviewer": reviewer,
            "reviewedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "complete": True,
            "items": [{"id": item_id, "decision": "approve", "note": ""}
                      for item_id in self.expected],
        }

    def test_slice_equals_assigned_rows_not_whole_sheet(self):
        self.assertEqual(len(self.expected), 10)
        self.assertEqual(VALIDATOR.validate_export(self.payload(), self.sheets, self.pool), 10)

    def test_unknown_pseudonym_is_rejected(self):
        with self.assertRaisesRegex(VALIDATOR.ValidationError, "not a known pool pseudonym"):
            VALIDATOR.validate_export(self.payload("gasyoun"), self.sheets, self.pool)

    def test_slice_must_carry_exactly_the_assigned_rows(self):
        payload = self.payload()
        payload["items"] = payload["items"][:-1]
        payload["decided"] -= 1
        with self.assertRaisesRegex(VALIDATOR.ValidationError, "decided must equal the full sheet count"):
            VALIDATOR.validate_export(payload, self.sheets, self.pool)

    def test_pool_defer_requires_note(self):
        payload = self.payload()
        payload["items"][0] = {"id": payload["items"][0]["id"], "decision": "defer", "note": ""}
        with self.assertRaisesRegex(VALIDATOR.ValidationError, "defer requires a note"):
            VALIDATOR.validate_export(payload, self.sheets, self.pool)
        payload["items"][0]["note"] = "словарь меток не подходит к этой строке"
        self.assertEqual(VALIDATOR.validate_export(payload, self.sheets, self.pool), 10)

    def test_r2_vocabulary_is_the_rows_proposed_parser_labels(self):
        packet = VALIDATOR.read_json("data/lexico/r2_checkpoint_review_packet.json")
        by_id = {r["checkpointId"]: r for r in packet["checkpointRows"]}
        for row_id, (_, allowed) in self.expected.items():
            self.assertEqual(allowed, set(by_id[row_id]["proposedParserLabels"]))


if __name__ == "__main__":
    unittest.main()
