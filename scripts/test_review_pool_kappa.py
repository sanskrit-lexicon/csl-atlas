"""Fixture tests for the review-pool kappa report tool (H5309).

Coverage required by the handoff: kappa = 1 (perfect), kappa near 0
(chance-level) and the degenerate single-class case — plus the join/coverage
semantics (only-in-one-file, unvoted, disagreements, sheet-id mismatch) and the
CLI end-to-end smoke.
"""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("review_pool_kappa.py")
SPEC = importlib.util.spec_from_file_location("review_pool_kappa", MODULE_PATH)
KAPPA = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(KAPPA)


def decisions_payload(sheet_id, votes):
    """votes: {id: decision-or-None} -> emitter-shaped decisions.json payload."""
    return {
        "sheet_id": sheet_id,
        "generated": "23-09-2026",
        "decided": sum(1 for v in votes.values() if v is not None),
        "items": [{"id": item_id, "decision": decision, "note": f"note {item_id}"}
                  for item_id, decision in votes.items()],
    }


class AgreementStatsTests(unittest.TestCase):
    def test_perfect_agreement_kappa_is_one(self):
        pairs = [("approve", "approve"), ("reject", "reject"),
                 ("defer", "defer"), ("approve", "approve")]
        stats = KAPPA.agreement_stats(pairs)
        self.assertEqual(stats["n"], 4)
        self.assertAlmostEqual(stats["observed"], 1.0)
        self.assertLess(stats["expected"], 1.0)
        self.assertAlmostEqual(stats["kappa"], 1.0)
        self.assertEqual(stats["ci95"], [1.0, 1.0])
        self.assertEqual(stats["band"], "almost-perfect")
        self.assertFalse(stats["degenerate"])

    def test_chance_level_kappa_is_zero(self):
        # Balanced 2x2 design: po == pe exactly, so kappa == 0.
        pairs = [("approve", "approve"), ("approve", "reject"),
                 ("reject", "approve"), ("reject", "reject")]
        stats = KAPPA.agreement_stats(pairs)
        self.assertAlmostEqual(stats["observed"], 0.5)
        self.assertAlmostEqual(stats["expected"], 0.5)
        self.assertAlmostEqual(stats["kappa"], 0.0, places=9)
        # κ lands on a float residual of 0, so the band may round either side.
        self.assertIn(stats["band"], ("poor", "slight"))
        # CI must bracket 0 and stay within [-1, 1].
        lo, hi = stats["ci95"]
        self.assertLessEqual(lo, 0.0)
        self.assertGreaterEqual(hi, 0.0)
        self.assertGreaterEqual(lo, -1.0)
        self.assertLessEqual(hi, 1.0)

    def test_single_class_is_degenerate_not_one(self):
        # Every paired opinion is 'approve': pe = 1, kappa is UNDEFINED.
        pairs = [("approve", "approve")] * 6
        stats = KAPPA.agreement_stats(pairs)
        self.assertTrue(stats["degenerate"])
        self.assertIsNone(stats["kappa"])
        self.assertIsNone(stats["ci95"])
        self.assertIsNone(stats["band"])
        self.assertAlmostEqual(stats["observed"], 1.0)  # raw agreement still stands

    def test_empty_pairs(self):
        stats = KAPPA.agreement_stats([])
        self.assertEqual(stats["n"], 0)
        self.assertIsNone(stats["kappa"])
        self.assertTrue(stats["degenerate"] is None)

    def test_ci_stays_in_range_for_negative_kappa(self):
        # Worse than chance: perfect disagreement on a balanced 2x2.
        pairs = [("approve", "reject"), ("reject", "approve")]
        stats = KAPPA.agreement_stats(pairs)
        self.assertLess(stats["kappa"], 0)
        lo, hi = stats["ci95"]
        self.assertGreaterEqual(lo, -1.0)
        self.assertLessEqual(hi, 1.0)


class BuildReportTests(unittest.TestCase):
    def setUp(self):
        votes_a = {"i1": "approve", "i2": "reject", "i3": "defer",
                   "i4": "approve", "i5": "reject", "i6": None}
        votes_b = {"i1": "approve", "i2": "approve", "i3": "defer",
                   "i4": "approve", "i6": "reject", "i7": "defer"}
        self.load_a = KAPPA.load_decisions(self._dump("a.json", decisions_payload("sht", votes_a)))
        self.load_b = KAPPA.load_decisions(self._dump("b.json", decisions_payload("sht", votes_b)))

    def _dump(self, name, payload):
        tmp = tempfile.NamedTemporaryFile("w", suffix=name, delete=False, encoding="utf-8")
        json.dump(payload, tmp)
        tmp.close()
        self.addCleanup(Path(tmp.name).unlink)
        return tmp.name

    def test_join_counts_and_disagreements(self):
        report = KAPPA.build_report(self.load_a, self.load_b)
        pk = report["packet"]
        # i1, i2, i3, i4 shared+voted; i5 only in A; i6 unvoted in A; i7 only in B.
        self.assertEqual(pk["pairedVoted"], 4)
        self.assertEqual(pk["onlyInA"], ["i5"])
        self.assertEqual(pk["onlyInB"], ["i7"])
        self.assertEqual(pk["unvotedEither"], ["i6"])
        self.assertEqual(len(report["disagreements"]), 1)
        d = report["disagreements"][0]
        self.assertEqual(d["id"], "i2")
        self.assertEqual(d["decisionA"], "reject")
        self.assertEqual(d["decisionB"], "approve")
        self.assertEqual(d["noteA"], "note i2")
        self.assertEqual(d["noteB"], "note i2")

    def test_kappa_on_mixed_sample_is_between_bounds(self):
        report = KAPPA.build_report(self.load_a, self.load_b)
        ag = report["agreement"]
        self.assertEqual(ag["rawAgreementPct"], 75.0)  # 3 of 4 paired agree
        self.assertIsNotNone(ag["cohenKappa"])
        self.assertTrue(-1.0 <= ag["kappaCi95"][0] <= ag["cohenKappa"] <= ag["kappaCi95"][1] <= 1.0)

    def test_confusion_matrix_counts(self):
        report = KAPPA.build_report(self.load_a, self.load_b)
        m = report["confusion"]["matrix"]
        self.assertEqual(m["approve"]["approve"], 2)
        self.assertEqual(m["reject"]["approve"], 1)
        self.assertEqual(m["defer"]["defer"], 1)
        self.assertEqual(sorted(report["confusion"]["rows"]), ["approve", "defer", "reject"])

    def test_sheet_id_mismatch_is_warning_not_error(self):
        load_c = KAPPA.load_decisions(self._dump("c.json", decisions_payload("OTHER", {"i1": "approve"})))
        report = KAPPA.build_report(self.load_a, load_c)
        self.assertTrue(any("sheet_id mismatch" in w for w in report["warnings"]))
        self.assertEqual(report["packet"]["pairedVoted"], 1)

    def test_both_single_class_degenerate_flows_through_report(self):
        load_x = KAPPA.load_decisions(self._dump("x.json", decisions_payload("sht", {f"u{i}": "approve" for i in range(5)})))
        load_y = KAPPA.load_decisions(self._dump("y.json", decisions_payload("sht", {f"u{i}": "approve" for i in range(5)})))
        report = KAPPA.build_report(load_x, load_y)
        ag = report["agreement"]
        self.assertTrue(ag["degenerate"])
        self.assertIsNone(ag["cohenKappa"])
        self.assertIsNotNone(ag["degenerateNote"])
        self.assertEqual(ag["rawAgreementPct"], 100.0)
        md = KAPPA.render_markdown(report)
        self.assertIn("undefined", md)

    def test_duplicate_id_is_rejected(self):
        bad = decisions_payload("sht", {"i1": "approve"})
        bad["items"].append({"id": "i1", "decision": "reject", "note": ""})
        path = self._dump("dup.json", bad)
        with self.assertRaises(KAPPA.KappaInputError):
            KAPPA.load_decisions(path)

    def test_unknown_decision_value_is_rejected(self):
        bad = decisions_payload("sht", {"i1": "maybe"})
        path = self._dump("unknown.json", bad)
        with self.assertRaises(KAPPA.KappaInputError):
            KAPPA.load_decisions(path)

    def test_zero_paired_opinions_render_is_not_none_pct(self):
        # Verifier finding: with no paired opinions the markdown must not read "None%".
        load_e = KAPPA.load_decisions(self._dump("e.json", decisions_payload("sht", {"only_a": "approve"})))
        load_f = KAPPA.load_decisions(self._dump("f.json", decisions_payload("sht", {"only_b": "reject"})))
        report = KAPPA.build_report(load_e, load_f)
        md = KAPPA.render_markdown(report)
        self.assertIn("not computable", md)
        self.assertNotIn("None%", md)

    def test_missing_file_is_rejected(self):
        with self.assertRaises(KAPPA.KappaInputError):
            KAPPA.load_decisions("/nonexistent/decisions.json")


class CliTests(unittest.TestCase):
    def _write(self, tmpdir, name, payload):
        path = Path(tmpdir) / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        return str(path)

    def test_cli_end_to_end_perfect_and_degenerate(self):
        with tempfile.TemporaryDirectory() as tmp:
            perfect_a = decisions_payload("sheet-x", {"r1": "approve", "r2": "reject", "r3": "defer"})
            perfect_b = decisions_payload("sheet-x", {"r1": "approve", "r2": "reject", "r3": "defer"})
            deg_a = decisions_payload("sheet-y", {"d1": "approve", "d2": "approve"})
            deg_b = decisions_payload("sheet-y", {"d1": "approve", "d2": "approve"})
            fa = self._write(tmp, "a_decisions.json", perfect_a)
            fb = self._write(tmp, "b_decisions.json", perfect_b)
            ga = self._write(tmp, "c_decisions.json", deg_a)
            gb = self._write(tmp, "d_decisions.json", deg_b)
            out = Path(tmp) / "report.json"
            script = str(Path(__file__).with_name("review_pool_kappa.py"))

            proc = subprocess.run([sys.executable, script, fa, fb, "--out", str(out)],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            report = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(report["agreement"]["cohenKappa"], 1.0)
            self.assertEqual(report["disagreements"], [])
            md = proc.stdout
            self.assertIn("Cohen κ: **1.0**", md)
            self.assertIn("Disagreements (0)", md)

            proc2 = subprocess.run([sys.executable, script, ga, gb, "--json"],
                                   capture_output=True, text=True)
            self.assertEqual(proc2.returncode, 0, proc2.stderr)
            deg_report = json.loads(proc2.stdout)
            self.assertTrue(deg_report["agreement"]["degenerate"])
            self.assertIsNone(deg_report["agreement"]["cohenKappa"])

    def test_cli_bad_input_exit_code_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = self._write(tmp, "bad.json", {"items": [{"id": "x", "decision": "nope"}]})
            good = self._write(tmp, "good.json", decisions_payload("s", {"x": "approve"}))
            script = str(Path(__file__).with_name("review_pool_kappa.py"))
            proc = subprocess.run([sys.executable, script, bad, good],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2)
            self.assertIn("not in", proc.stderr)


if __name__ == "__main__":
    unittest.main()
