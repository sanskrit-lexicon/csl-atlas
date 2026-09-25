"""Tests for the review-pool merge/adjudication truth table (H5483/B7)."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("merge-review-pool-decisions.py")
SPEC = importlib.util.spec_from_file_location("merge_review_pool_decisions", MODULE_PATH)
MERGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MERGE)

SHEET_ID = "csl-atlas-r2-checkpoint_10rows"


def _export(reviewer, decisions):
    """decisions: {row_id: (decision, note)}."""
    return reviewer, {
        row_id: {"id": row_id, "decision": decision, "note": note}
        for row_id, (decision, note) in decisions.items()
    }


class MergeTruthTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected = MERGE.expected_sheets()[SHEET_ID]
        cls.row_ids = list(cls.expected)

    def one_row(self, row_id, a, b):
        exp_a = _export("pool-a01", {row_id: a})
        exp_b = _export("pool-a02", {row_id: b})
        records = MERGE.merge_packet(SHEET_ID, [exp_a, exp_b])
        return next(r for r in records if r["reviewId"] == row_id)

    def test_a1_same_label_both_approve_is_reviewed_ok(self):
        row_id = self.row_ids[0]
        record = self.one_row(row_id, ("approve", ""), ("approve", ""))
        self.assertEqual(record["reviewStatus"], "reviewed-ok")
        self.assertFalse(record["singleKey"])

    def test_a2_same_corrected_label_both_reject_is_reviewed_corrected(self):
        row_id = self.row_ids[0]
        label = next(iter(self.expected[row_id][1]))
        record = self.one_row(
            row_id,
            ("reject", f"{label}: matches the vocabulary"),
            ("reject", f"{label}: independently the same reading"),
        )
        self.assertEqual(record["reviewStatus"], "reviewed-corrected")
        self.assertEqual(record["reviewedValue"], label)

    def test_a3_both_defer_is_deferred(self):
        row_id = self.row_ids[0]
        record = self.one_row(row_id, ("defer", "need a second look"), ("defer", "ditto"))
        self.assertEqual(record["reviewStatus"], "deferred")

    def test_a4_reject_reject_different_corrections_needs_review(self):
        row_id = self.row_ids[0]
        labels = list(self.expected[row_id][1])
        record = self.one_row(
            row_id,
            ("reject", f"{labels[0]}: reading one"),
            ("reject", f"{labels[1]}: reading two"),
        )
        self.assertEqual(record["reviewStatus"], "needs-review")
        self.assertFalse(record["adjudicated"])

    def test_a4_approve_reject_is_needs_review(self):
        row_id = self.row_ids[0]
        label = next(iter(self.expected[row_id][1]))
        record = self.one_row(row_id, ("approve", ""), ("reject", f"{label}: disagree"))
        self.assertEqual(record["reviewStatus"], "needs-review")

    def test_a5_single_key_is_needs_review_and_flagged(self):
        row_id = self.row_ids[0]
        exp_a = _export("pool-a01", {row_id: ("approve", "")})
        records = MERGE.merge_packet(SHEET_ID, [exp_a])
        record = next(r for r in records if r["reviewId"] == row_id)
        self.assertEqual(record["reviewStatus"], "needs-review")
        self.assertTrue(record["singleKey"])
        self.assertIsNone(record["reviewedValue"])

    def test_a4_adjudication_promotes_with_rationale_and_by(self):
        row_id = self.row_ids[0]
        labels = list(self.expected[row_id][1])
        exp_a = _export("pool-a01", {row_id: ("reject", f"{labels[0]}: reading one")})
        exp_b = _export("pool-a02", {row_id: ("reject", f"{labels[1]}: reading two")})
        adjudications = {row_id: {
            "reviewId": row_id, "verdict": "reviewed-corrected",
            "reviewedValue": labels[0], "adjudicatedBy": "pool-adj01",
            "note": "source line settles it in favour of reading one",
        }}
        records = MERGE.merge_packet(SHEET_ID, [exp_a, exp_b], adjudications)
        record = next(r for r in records if r["reviewId"] == row_id)
        self.assertEqual(record["reviewStatus"], "reviewed-corrected")
        self.assertEqual(record["reviewedValue"], labels[0])
        self.assertTrue(record["adjudicated"])
        self.assertEqual(record["adjudicatedBy"], "pool-adj01")

    def test_adjudication_missing_adjudicated_by_is_refused(self):
        row_id = self.row_ids[0]
        labels = list(self.expected[row_id][1])
        exp_a = _export("pool-a01", {row_id: ("reject", f"{labels[0]}: reading one")})
        exp_b = _export("pool-a02", {row_id: ("reject", f"{labels[1]}: reading two")})
        adjudications = {row_id: {
            "reviewId": row_id, "verdict": "reviewed-corrected",
            "reviewedValue": labels[0], "note": "no adjudicator named",
        }}
        with self.assertRaisesRegex(MERGE.MergeError, "adjudicatedBy"):
            MERGE.merge_packet(SHEET_ID, [exp_a, exp_b], adjudications)

    def test_adjudication_missing_rationale_is_refused(self):
        row_id = self.row_ids[0]
        labels = list(self.expected[row_id][1])
        exp_a = _export("pool-a01", {row_id: ("reject", f"{labels[0]}: reading one")})
        exp_b = _export("pool-a02", {row_id: ("reject", f"{labels[1]}: reading two")})
        adjudications = {row_id: {
            "reviewId": row_id, "verdict": "reviewed-corrected",
            "reviewedValue": labels[0], "adjudicatedBy": "pool-adj01", "note": "",
        }}
        with self.assertRaisesRegex(MERGE.MergeError, "rationale"):
            MERGE.merge_packet(SHEET_ID, [exp_a, exp_b], adjudications)

    def test_tie_does_not_silently_default_to_machine_label(self):
        # design §8 rule 4: a blocked verdict must not smuggle in the proposed
        # label as reviewedValue.
        row_id = self.row_ids[0]
        labels = list(self.expected[row_id][1])
        exp_a = _export("pool-a01", {row_id: ("reject", f"{labels[0]}: reading one")})
        exp_b = _export("pool-a02", {row_id: ("reject", f"{labels[1]}: reading two")})
        adjudications = {row_id: {
            "reviewId": row_id, "verdict": "blocked",
            "adjudicatedBy": "pool-adj01", "note": "source is illegible, cannot settle",
        }}
        records = MERGE.merge_packet(SHEET_ID, [exp_a, exp_b], adjudications)
        record = next(r for r in records if r["reviewId"] == row_id)
        self.assertEqual(record["reviewStatus"], "blocked")
        self.assertIsNone(record["reviewedValue"])

    def test_more_than_two_keys_is_refused(self):
        row_id = self.row_ids[0]
        exp_a = _export("pool-a01", {row_id: ("approve", "")})
        exp_b = _export("pool-a02", {row_id: ("approve", "")})
        exp_c = _export("pool-a03", {row_id: ("approve", "")})
        with self.assertRaisesRegex(MERGE.MergeError, "more than two keys"):
            MERGE.merge_packet(SHEET_ID, [exp_a, exp_b, exp_c])

    def test_contact_bearing_note_refuses_the_whole_file(self, tmp_path=None):
        payload = {
            "sheet_id": SHEET_ID, "reviewer": "pool-a01", "complete": True, "decided": 1,
            "items": [{"id": self.row_ids[0], "decision": "reject",
                       "note": "label: ask на почту ivanov@example.com"}],
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
            json.dump(payload, fh)
            path = Path(fh.name)
        try:
            with self.assertRaisesRegex(MERGE.MergeError, "contact-bearing"):
                MERGE.load_export(path)
        finally:
            path.unlink()

    def test_non_pool_pseudonym_reviewer_is_refused(self):
        payload = {
            "sheet_id": SHEET_ID, "reviewer": "gasyoun", "complete": True, "decided": 0, "items": [],
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
            json.dump(payload, fh)
            path = Path(fh.name)
        try:
            with self.assertRaisesRegex(MERGE.MergeError, "pool pseudonym"):
                MERGE.load_export(path)
        finally:
            path.unlink()

    def test_h5308_dry_run_canary_merges_all_approve_to_reviewed_ok(self):
        canary_dir = Path(MODULE_PATH).resolve().parent.parent / "data" / "review" / "pool_dry_run"
        files = sorted(canary_dir.glob(f"{SHEET_ID}__*__DRY-RUN.json"))
        self.assertEqual(len(files), 2, "H5308 dry-run canary must exist for the R2 pilot")
        report = MERGE.build_report(SHEET_ID, files)
        self.assertEqual(report["rows"], 10)
        self.assertEqual(report["rowsDoubleKeyed"], 10)
        self.assertEqual(report["counts"], {"reviewed-ok": 10})


if __name__ == "__main__":
    unittest.main()
