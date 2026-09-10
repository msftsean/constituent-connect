import unittest
import os
from unittest.mock import patch

from fastapi.testclient import TestClient

from constituent_connect.fastapi_adapter import CORRELATION_HEADER, create_app
from constituent_connect.workflow import ConstituentConnectWorkflow


class FastApiAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["CONSTITUENT_CONNECT_APPROVER_TOKEN"] = "test-approver-token"
        self.client = TestClient(create_app(ConstituentConnectWorkflow()))
        self.payload = {
            "channel": "web",
            "message": "Where do I apply for a replacement professional license?",
        }

    def test_health_propagates_supplied_correlation_id(self) -> None:
        response = self.client.get("/health", headers={CORRELATION_HEADER: "test-correlation"})

        self.assertEqual(200, response.status_code)
        self.assertEqual("test-correlation", response.headers[CORRELATION_HEADER])
        self.assertEqual("test-correlation", response.json()["correlation_id"])
        self.assertEqual("local-synthetic", response.json()["mode"])

    def test_workflow_stage_endpoints_and_approval_gate(self) -> None:
        intake = self.client.post("/api/intake", json=self.payload)
        classify = self.client.post("/api/classify", json=self.payload)
        route = self.client.post("/api/route", json=self.payload)
        response = self.client.post("/api/respond", json=self.payload)

        self.assertEqual(200, intake.status_code)
        self.assertEqual(200, classify.status_code)
        self.assertEqual(200, route.status_code)
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            "professional-licensing",
            route.json()["data"]["route"]["primary_service_id"],
        )
        response_id = response.json()["data"]["response"]["response_id"]

        blocked = self.client.post("/api/cases", json={"response_id": response_id})
        self.assertEqual(400, blocked.status_code)
        self.assertIn("approval", blocked.json()["error"].lower())

        approved = self.client.post(
            "/api/approval",
            json={"response_id": response_id, "reviewer": "ignored"},
            headers={"X-Authenticated-Reviewer-ID": "api-reviewer", "X-Approval-Role": "approver", "X-Approver-Token": "test-approver-token"},
        )
        case = self.client.post("/api/cases", json={"response_id": response_id})
        self.assertEqual(200, approved.status_code)
        self.assertEqual(201, case.status_code)

    def test_legacy_approval_path_does_not_require_duplicate_response_id(self) -> None:
        response = self.client.post("/api/respond", json=self.payload)
        response_id = response.json()["data"]["response"]["response_id"]

        approved = self.client.post(
            f"/api/responses/{response_id}/approve",
            json={"reviewer": "ignored"},
            headers={"X-Authenticated-Reviewer-ID": "legacy-reviewer", "X-Approval-Role": "approver", "X-Approver-Token": "test-approver-token"},
        )

        self.assertEqual(200, approved.status_code)
        self.assertEqual("approved", approved.json()["data"]["approval_status"])

    def test_errors_are_explicit_and_correlated(self) -> None:
        missing = self.client.post(
            "/api/cases",
            json={"response_id": "response-does-not-exist"},
            headers={CORRELATION_HEADER: "error-correlation"},
        )
        invalid = self.client.post("/api/intake", json={"message": ""})

        self.assertEqual(404, missing.status_code)
        self.assertEqual("error-correlation", missing.json()["correlation_id"])
        self.assertEqual(422, invalid.status_code)
        self.assertIn("validation", invalid.json()["error"].lower())

    def test_approval_requires_authorized_approver_and_response_redacts_raw_pii(self) -> None:
        response = self.client.post(
            "/api/respond",
            json={"channel": "web", "message": "My SSN is 123-45-6789; I need a license."},
        )
        response_id = response.json()["data"]["response"]["response_id"]
        self.assertNotIn("123-45-6789", response.text)
        unauthorized = self.client.post(
            "/api/approval",
            json={"response_id": response_id, "reviewer": "attacker"},
        )
        self.assertEqual(400, unauthorized.status_code)

    def test_current_emergency_wins_over_historical_reference(self) -> None:
        response = self.client.post(
            "/api/respond",
            json={
                "channel": "web",
                "message": "Last year I read an old report about a fire; today smoke is filling my apartment and someone is trapped.",
            },
        )
        data = response.json()["data"]
        self.assertTrue(data["inquiry"]["emergency_signal"])
        self.assertEqual("emergency_exit", data["route"]["status"])

    @patch("constituent_connect.fastapi_adapter.run_evaluations")
    def test_evaluation_endpoint_returns_report(self, run_evaluations) -> None:
        run_evaluations.return_value = {"summary": {"release_gate": "pass"}}

        response = self.client.post("/api/evals/run")

        self.assertEqual(202, response.status_code)
        self.assertEqual("pass", response.json()["data"]["summary"]["release_gate"])


if __name__ == "__main__":
    unittest.main()
