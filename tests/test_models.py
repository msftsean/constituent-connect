import unittest

from constituent_connect.config import Catalog
from constituent_connect.models import to_dict


class ModelAndConfigurationTests(unittest.TestCase):
    def test_catalog_is_configuration_backed_and_synthetic(self) -> None:
        catalog = Catalog()
        self.assertGreaterEqual(len(catalog.agencies), 3)
        self.assertGreaterEqual(len(catalog.services), 3)
        self.assertTrue(
            all("Synthetic" in agency["name"] for agency in catalog.agencies)
        )
        self.assertFalse(catalog.settings["application"]["emergency_dispatch_enabled"])

    def test_dataclass_serialization(self) -> None:
        from constituent_connect.workflow import ConstituentConnectWorkflow

        result = ConstituentConnectWorkflow().process(
            "Explain the application steps in plain language.", "web"
        )
        payload = to_dict(result)
        self.assertEqual("web", payload["message"]["channel"])
        self.assertIn("response_id", payload["response"])


if __name__ == "__main__":
    unittest.main()
