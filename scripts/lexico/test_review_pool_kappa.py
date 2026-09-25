"""Tests for the review-pool κ report builder (H5483/B8)."""
import importlib.util
import random
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("review_pool_kappa.py")
SPEC = importlib.util.spec_from_file_location("review_pool_kappa", MODULE_PATH)
KAPPA = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(KAPPA)


def fake_record(row_id, a_label, b_label, a="pool-a01", b="pool-a02", status="reviewed-ok"):
    return {
        "reviewId": row_id,
        "singleKey": False,
        "reviewStatus": status,
        "reviewedValue": a_label if a_label == b_label else None,
        "adjudicated": False,
        "keys": [
            {"annotator": a, "decision": "approve", "resolvedLabel": a_label, "note": ""},
            {"annotator": b, "decision": "approve", "resolvedLabel": b_label, "note": ""},
        ],
    }


class LandisKochTests(unittest.TestCase):
    def test_bands(self):
        self.assertEqual(KAPPA.landis_koch(None), None)
        self.assertEqual(KAPPA.landis_koch(-0.1), "poor")
        self.assertEqual(KAPPA.landis_koch(0.1), "slight")
        self.assertEqual(KAPPA.landis_koch(0.3), "fair")
        self.assertEqual(KAPPA.landis_koch(0.5), "moderate")
        self.assertEqual(KAPPA.landis_koch(0.7), "substantial")
        self.assertEqual(KAPPA.landis_koch(0.95), "almost-perfect")


class KrippendorffAlphaHandComputedFixtureTests(unittest.TestCase):
    """A small synthetic 2-annotator dataset with a hand-computable α.

    10 rows, fixed dyad (A,B). Rows 1-7: both label "x". Row 8: both label "y".
    Rows 9-10: one "x" one "y" (disagreement). Pooled marginal: n=20 opinions,
    n_x=16, n_y=4. diag (matching contribution) = 16 (14 from rows1-7 + 2 from
    row8), so Do = (20-16)/20 = 0.2. De = [n(n-1) - sum(n_c(n_c-1))]/(n(n-1))
    = [380 - (16*15 + 4*3)] / 380 = [380-252]/380 = 128/380. alpha = 1 - Do/De
    = 1 - (76/380)/(128/380) = 1 - 76/128 = 13/32 = 0.40625.
    """

    def test_alpha_matches_hand_computation(self):
        units = [["x", "x"]] * 7 + [["y", "y"]] + [["x", "y"]] * 2
        alpha = KAPPA.krippendorff_alpha_nominal(units)
        self.assertAlmostEqual(alpha, 13 / 32, places=9)

    def test_degenerate_single_category_is_none(self):
        units = [["x", "x"]] * 10
        self.assertIsNone(KAPPA.krippendorff_alpha_nominal(units))

    def test_rows_with_one_key_are_excluded_not_crashing(self):
        units = [["x", "x"]] * 7 + [["y", "y"]] + [["x", "y"]] * 2 + [["x"]]
        alpha = KAPPA.krippendorff_alpha_nominal(units)
        self.assertAlmostEqual(alpha, 13 / 32, places=9)

    def test_empty_input_is_none(self):
        self.assertIsNone(KAPPA.krippendorff_alpha_nominal([]))


class CohenKappaFixtureTests(unittest.TestCase):
    def test_perfect_agreement_is_kappa_one(self):
        pairs = [("x", "x")] * 10 + [("y", "y")] * 10
        result = KAPPA.cohen_kappa(pairs)
        self.assertEqual(result["kappa"], 1.0)
        self.assertEqual(result["band"], "almost-perfect")

    def test_chance_level_balanced_2x2_is_kappa_zero(self):
        # Balanced 2x2 with independent marginals: kappa == 0.
        pairs = [("x", "x"), ("x", "y"), ("y", "x"), ("y", "y")] * 5
        result = KAPPA.cohen_kappa(pairs)
        self.assertAlmostEqual(result["kappa"], 0.0, places=9)

    def test_degenerate_single_class_kappa_is_none(self):
        pairs = [("x", "x")] * 5
        result = KAPPA.cohen_kappa(pairs)
        self.assertIsNone(result["kappa"])


class DyadReportingThresholdTests(unittest.TestCase):
    def test_dyad_below_30_rows_suppresses_point_estimate(self):
        records = [fake_record(f"r{i}", "x", "x") for i in range(29)]
        rows = KAPPA.cohen_kappa_by_dyad(records)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["n"], 29)
        self.assertIsNone(rows[0]["kappa"])

    def test_dyad_at_30_rows_reports_a_point_estimate(self):
        records = [fake_record(f"r{i}", "x" if i % 2 else "y", "x" if i % 2 else "y") for i in range(30)]
        rows = KAPPA.cohen_kappa_by_dyad(records)
        self.assertEqual(rows[0]["n"], 30)
        self.assertIsNotNone(rows[0]["kappa"])


class ButtonLevelAndModalShareTests(unittest.TestCase):
    def test_button_level_agreement_counts_matching_decisions_only(self):
        records = [
            {"keys": [{"annotator": "pool-a01", "decision": "approve", "resolvedLabel": "x"},
                      {"annotator": "pool-a02", "decision": "approve", "resolvedLabel": "y"}]},
            {"keys": [{"annotator": "pool-a01", "decision": "reject", "resolvedLabel": "x"},
                      {"annotator": "pool-a02", "decision": "approve", "resolvedLabel": "x"}]},
        ]
        self.assertEqual(KAPPA.button_level_agreement(records), 0.5)

    def test_modal_label_share(self):
        records = [fake_record("r1", "x", "x"), fake_record("r2", "x", "y")]
        # labels across all keys: x,x,x,y -> modal x, share 3/4
        self.assertEqual(KAPPA.modal_label_share(records), 0.75)


class BootstrapCiTests(unittest.TestCase):
    def test_bootstrap_ci_is_deterministic_for_a_fixed_seed(self):
        units = [["x", "x"]] * 7 + [["y", "y"]] + [["x", "y"]] * 2
        ci_a = KAPPA.bootstrap_ci(units, random.Random(20260925))
        ci_b = KAPPA.bootstrap_ci(units, random.Random(20260925))
        self.assertEqual(ci_a, ci_b)
        self.assertIsNotNone(ci_a)
        self.assertLessEqual(ci_a[0], ci_a[1])

    def test_bootstrap_ci_none_when_alpha_undefined(self):
        units = [["x", "x"]] * 10
        self.assertIsNone(KAPPA.bootstrap_ci(units, random.Random(1)))


class PacketReportOnRealCanaryTests(unittest.TestCase):
    """Exercises the whole packet_report() path against the real H5308 dry-run
    canary merged by B7 -- degenerate output is expected and must be labelled
    as such, not crash or silently fabricate a number (H5483)."""

    def test_r2_dry_run_merge_report_produces_labelled_degenerate_alpha(self):
        merge_module_path = MODULE_PATH.parent.parent / "merge-review-pool-decisions.py"
        spec = importlib.util.spec_from_file_location("merge_review_pool_decisions", merge_module_path)
        merge = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(merge)

        canary_dir = MODULE_PATH.parent.parent.parent / "data" / "review" / "pool_dry_run"
        files = sorted(canary_dir.glob("csl-atlas-r2-checkpoint_10rows__*__DRY-RUN.json"))
        self.assertEqual(len(files), 2)
        report = merge.build_report("csl-atlas-r2-checkpoint_10rows", files)

        packet = KAPPA.packet_report(report, random.Random(20260925))
        self.assertEqual(packet["rows"], 10)
        self.assertIsNone(packet["krippendorffAlpha"])  # all-approve canary: single category
        self.assertEqual(packet["observedAgreement"], 1.0)
        self.assertIn(KAPPA.R2_N_CAVEAT, packet["limitations"])


if __name__ == "__main__":
    unittest.main()
