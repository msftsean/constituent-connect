from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ContextDriftTests(unittest.TestCase):
    def test_canonical_vocabulary_is_present_and_distinct_from_all_clear(self) -> None:
        context = (ROOT / "CONTEXT.md").read_text(encoding="utf-8")
        required = {
            "Inquiry",
            "Message",
            "Intent",
            "Service",
            "Route",
            "Evidence",
            "Citation",
            "Draft",
            "Work item",
            "Emergency exit",
            "Clarification",
            "Case",
        }
        self.assertTrue(all(term in context for term in required))
        self.assertIn("non-emergency constituent communication", context)
        self.assertNotIn("incident triage", context.lower())

    def test_spec_kit_artifacts_share_the_same_boundary_and_lab_path(self) -> None:
        constitution = (
            ROOT / ".specify" / "memory" / "constitution.md"
        ).read_text(encoding="utf-8")
        spec = (
            ROOT / "specs" / "001-constituent-connect" / "spec.md"
        ).read_text(encoding="utf-8")
        tasks = (
            ROOT / "specs" / "001-constituent-connect" / "tasks.md"
        ).read_text(encoding="utf-8")
        for artifact in (constitution, spec, tasks):
            self.assertIn("emergency", artifact.lower())
            self.assertIn("human", artifact.lower())
        self.assertIn("Lab 00-06", tasks)
        self.assertIn("FR-016", spec)
        self.assertIn("FR-017", spec)


if __name__ == "__main__":
    unittest.main()
