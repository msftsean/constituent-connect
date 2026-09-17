import unittest
import os
from unittest.mock import patch

from fastapi.testclient import TestClient

from constituent_connect.approval import (
    APPROVER_ID_ENV,
    APPROVER_TOKEN_ENV,
    LOCAL_WORKSHOP_APPROVAL_ENV,
)
from constituent_connect.fastapi_adapter import CORRELATION_HEADER, create_app
from constituent_connect.workflow import ConstituentConnectWorkflow


class FastApiAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        os.environ.pop(APPROVER_TOKEN_ENV, None)
        os.environ.pop(APPROVER_ID_ENV, None)
        os.environ.pop(LOCAL_WORKSHOP_APPROVAL_ENV, None)
        self.client = TestClient(create_app(ConstituentConnectWorkflow()))
        self.payload = {
            "channel": "web",
            "message": "Where do I apply for a replacement professional license?",
        }

    def tearDown(self) -> None:
        os.environ.pop(APPROVER_TOKEN_ENV, None)
        os.environ.pop(APPROVER_ID_ENV, None)
        os.environ.pop(LOCAL_WORKSHOP_APPROVAL_ENV, None)

    def configure_approver(self) -> None:
        os.environ[APPROVER_TOKEN_ENV] = "test-approver-token"
        os.environ[APPROVER_ID_ENV] = "test-configured-reviewer"

    def test_health_propagates_supplied_correlation_id(self) -> None:
        response = self.client.get("/health", headers={CORRELATION_HEADER: "test-correlation"})

        self.assertEqual(200, response.status_code)
        self.assertEqual("test-correlation", response.headers[CORRELATION_HEADER])
        self.assertEqual("test-correlation", response.json()["correlation_id"])
        self.assertEqual("local-synthetic", response.json()["mode"])

    def test_workflow_stage_endpoints_and_approval_gate(self) -> None:
        self.configure_approver()
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
            headers={
                "X-Approval-Role": "approver",
                "X-Approver-Token": "test-approver-token",
            },
        )
        case = self.client.post("/api/cases", json={"response_id": response_id})
        self.assertEqual(200, approved.status_code)
        self.assertEqual("test-configured-reviewer", approved.json()["data"]["approved_by"])
        self.assertEqual(201, case.status_code)

    def test_legacy_approval_path_does_not_require_duplicate_response_id(self) -> None:
        self.configure_approver()
        response = self.client.post("/api/respond", json=self.payload)
        response_id = response.json()["data"]["response"]["response_id"]

        approved = self.client.post(
            f"/api/responses/{response_id}/approve",
            json={"reviewer": "ignored"},
            headers={
                "X-Approval-Role": "approver",
                "X-Approver-Token": "test-approver-token",
            },
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
        self.assertEqual(403, unauthorized.status_code)

    def test_bare_approver_role_is_rejected_under_default_config(self) -> None:
        response = self.client.post("/api/respond", json=self.payload)
        response_id = response.json()["data"]["response"]["response_id"]

        rejected = self.client.post(
            "/api/approval",
            json={"response_id": response_id},
            headers={"X-Approval-Role": "approver"},
        )

        self.assertEqual(403, rejected.status_code)
        self.assertIn("approval token", rejected.json()["error"])

    def test_configured_approval_token_is_required(self) -> None:
        self.configure_approver()
        response = self.client.post("/api/respond", json=self.payload)
        response_id = response.json()["data"]["response"]["response_id"]

        missing_token = self.client.post(
            "/api/approval",
            json={"response_id": response_id},
            headers={"X-Approval-Role": "approver"},
        )
        approved = self.client.post(
            "/api/approval",
            json={"response_id": response_id},
            headers={
                "X-Approval-Role": "approver",
                "X-Approver-Token": "test-approver-token",
            },
        )

        self.assertEqual(403, missing_token.status_code)
        self.assertEqual(200, approved.status_code)
        self.assertEqual("test-configured-reviewer", approved.json()["data"]["approved_by"])

    def test_authenticated_reviewer_can_reroute_without_approving(self) -> None:
        self.configure_approver()
        response = self.client.post("/api/respond", json=self.payload)
        response_id = response.json()["data"]["response"]["response_id"]

        rerouted = self.client.post(
            "/api/approval",
            json={
                "response_id": response_id,
                "decision": "reroute",
                "target_service_id": "general-service-navigation",
                "reason": "Synthetic reviewer correction.",
            },
            headers={
                "X-Approval-Role": "approver",
                "X-Approver-Token": "test-approver-token",
            },
        )

        self.assertEqual(200, rerouted.status_code)
        self.assertEqual(
            "general-service-navigation",
            rerouted.json()["data"]["primary_service_id"],
        )
        blocked = self.client.post("/api/cases", json={"response_id": response_id})
        self.assertEqual(400, blocked.status_code)

    def test_emergency_approval_is_rejected_but_escalation_is_recorded(self) -> None:
        self.configure_approver()
        response = self.client.post(
            "/api/respond",
            json={"channel": "web", "message": "Someone is not breathing and needs help now."},
        )
        response_id = response.json()["data"]["response"]["response_id"]

        approved = self.client.post(
            "/api/approval",
            json={"response_id": response_id},
            headers={
                "X-Approval-Role": "approver",
                "X-Approver-Token": "test-approver-token",
            },
        )
        escalated = self.client.post(
            "/api/approval",
            json={"response_id": response_id, "decision": "escalate"},
            headers={
                "X-Approval-Role": "approver",
                "X-Approver-Token": "test-approver-token",
            },
        )

        self.assertEqual(400, approved.status_code)
        self.assertEqual(200, escalated.status_code)
        self.assertEqual("escalated", escalated.json()["data"]["approval_status"])

    def test_workshop_approval_session_requires_explicit_local_opt_in(self) -> None:
        disabled = self.client.get("/api/workshop/approval-session")
        self.assertEqual(403, disabled.status_code)

        os.environ[LOCAL_WORKSHOP_APPROVAL_ENV] = "true"
        self.configure_approver()
        enabled = self.client.get("/api/workshop/approval-session")

        self.assertEqual(200, enabled.status_code)
        self.assertEqual("test-approver-token", enabled.json()["data"]["approver_token"])

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
