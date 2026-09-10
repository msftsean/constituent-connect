import shutil
import unittest
from pathlib import Path

from constituent_connect.config import PROJECT_ROOT
from constituent_connect.eval_runner import run_evaluations


class EvaluationTests(unittest.TestCase):
    def test_approved_datasets_pass_release_gate(self) -> None:
        output = PROJECT_ROOT / "reports" / "unit-test"
        shutil.rmtree(output, ignore_errors=True)
        try:
            report = run_evaluations(output_dir=output)
            self.assertEqual("pass", report["summary"]["release_gate"])
            self.assertGreaterEqual(report["summary"]["total"], 20)
            assertions = report["summary"]["release_assertions"]
            self.assertTrue(all(item["passed"] for item in assertions.values()))
            self.assertTrue((output / "evaluation.json").exists())
            self.assertTrue((output / "evaluation.html").exists())
        finally:
            shutil.rmtree(output, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
