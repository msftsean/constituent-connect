from __future__ import annotations

import re

from ..models import GroundedResponse, NormalizedInquiry, RouteRecommendation, TraceEvent


class QualityAgent:
    PROHIBITED = re.compile(
        r"\b(?:guarantee|you qualify|will receive payment|promise payment|"
        r"legal advice|medical diagnosis|we dispatched|officers are on the way)\b",
        re.IGNORECASE,
    )

    def review(
        self,
        inquiry: NormalizedInquiry,
        route: RouteRecommendation,
        response: GroundedResponse,
    ) -> GroundedResponse:
        issues: list[str] = []
        if self.PROHIBITED.search(response.draft):
            issues.append("prohibited_commitment")
        if route.primary_service_id and not inquiry.emergency_signal and not response.citations:
            issues.append("unsupported_factual_response")
        if response.approval_status != "pending":
            issues.append("approval_gate_state_invalid")
        if not response.ai_disclosure:
            issues.append("missing_ai_disclosure")
        if inquiry.injection_detected:
            issues.append("prompt_injection_ignored")
        if inquiry.discriminatory_instruction_detected:
            issues.append("discriminatory_routing_refused")

        response.prohibited_commitment_check = "prohibited_commitment" in issues
        response.quality_issues = issues
        inquiry.transformation_history.append(
            TraceEvent(
                stage="quality",
                outcome="blocked" if response.prohibited_commitment_check else "review_complete",
                details={"issues": issues},
            )
        )
        return response
