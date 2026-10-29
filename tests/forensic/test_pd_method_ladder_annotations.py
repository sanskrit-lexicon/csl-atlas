#!/usr/bin/env python3
import csv
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
M1 = os.path.join(ROOT, "scripts", "pd_siglum_work_m1.py")
M2 = os.path.join(ROOT, "scripts", "pd_blank_siglum_adjudication.py")
PASS_B = os.path.join(ROOT, "data", "pd", "pd_siglum_work_m1_annotator_b.tsv")


class MethodLadderAnnotationTests(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run(
            [sys.executable, *args], cwd=ROOT, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )

    def test_m2_complete(self):
        result = self.run_script(M2, "--check", "--complete")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("annotated=50", result.stdout)

    def test_m1_complete(self):
        result = self.run_script(M1, "--check", "--complete")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("B annotated=200", result.stdout)

    def test_kappa_perfect_agreement_is_a_synthetic_fixture(self):
        result = self.run_script(M1, "--kappa", PASS_B, PASS_B)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Cohen κ=1.000000", result.stdout)

    def test_kappa_refuses_missing_note(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            pass_a = os.path.join(tmp, "a.tsv")
            with open(PASS_B, encoding="utf-8", newline="") as src:
                rows = list(csv.DictReader(src, delimiter="\t"))
            rows[0]["note"] = ""
            with open(pass_a, "w", encoding="utf-8", newline="") as dst:
                writer = csv.DictWriter(dst, fieldnames=["sample_id", "label", "note"], delimiter="\t", lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
            result = self.run_script(M1, "--kappa", pass_a, PASS_B)
            self.assertEqual(result.returncode, 2)
            self.assertIn("κ refused", result.stderr)


if __name__ == "__main__":
    unittest.main()
