from __future__ import annotations

from ..config import Catalog
from ..models import (
    Citation,
    GroundedResponse,
    NormalizedInquiry,
    RouteRecommendation,
    TraceEvent,
    new_id,
)


class ResponseAgent:
    AI_DISCLOSURE = (
        "This draft was generated with AI assistance and requires human review."
    )

    def __init__(self, catalog: Catalog) -> None:
        self.catalog = catalog

    def draft(
        self,
        inquiry: NormalizedInquiry,
        route: RouteRecommendation,
        citations: list[Citation],
        channel: str,
    ) -> GroundedResponse:
        if inquiry.emergency_signal:
            text = inquiry.emergency_guidance or (
                "Call 911 for immediate danger. This application does not dispatch."
            )
        elif inquiry.discriminatory_instruction_detected:
            text = (
                "I cannot recommend different service levels based on protected "
                "characteristics or neighborhood. A human reviewer can help identify "
                "the correct service using only the service need."
            )
        elif any(item.category == "sensitive_data_request" for item in inquiry.pii_findings):
            text = (
                "For your privacy, do not send passwords, Social Security numbers, "
                "or other credentials. Sensitive details are excluded from this draft. "
            )
            text += self._supported_next_step(route, citations)
        elif route.status == "clarification_required":
            text = (
                "I do not have enough approved information to choose a service. "
                + (route.clarifying_question or "Please provide more detail.")
            )
        elif not citations:
            text = (
                "I cannot answer this from the approved public information currently "
                "available. A human agent must review the request."
            )
        else:
            service = self.catalog.service_by_id[route.primary_service_id or ""]
            lead = (
                f"The proposed service is {service.name}. "
                f"{citations[0].excerpt} [1]"
            )
            if len(citations) > 1:
                lead += f" {citations[1].excerpt} [2]"
            if route.secondary_service_ids:
                names = [
                    self.catalog.service_by_id[item].name
                    for item in route.secondary_service_ids
                ]
                lead += (
                    " Your request may also involve "
                    + ", ".join(names)
                    + "; a human reviewer will coordinate the handoff."
                )
            text = lead + " Review the cited public page before submitting."

        if inquiry.detected_language == "es":
            text = (
                "Borrador en lenguaje sencillo: "
                + text
                + " Un agente humano debe revisar esta respuesta."
            )

        response = GroundedResponse(
            response_id=new_id("resp"),
            inquiry_id=inquiry.inquiry_id,
            channel=channel,
            language=inquiry.detected_language,
            draft=text,
            citations=citations,
            prohibited_commitment_check=False,
            approval_status="pending",
            ai_disclosure=self.AI_DISCLOSURE,
        )
        inquiry.transformation_history.append(
            TraceEvent(
                stage="response",
                outcome="emergency_guidance"
                if inquiry.emergency_signal
                else "draft_created",
                details={
                    "response_id": response.response_id,
                    "citations": len(citations),
                    "approval_status": response.approval_status,
                },
            )
        )
        return response

    def _supported_next_step(
        self, route: RouteRecommendation, citations: list[Citation]
    ) -> str:
        if route.primary_service_id and citations:
            service = self.catalog.service_by_id[route.primary_service_id]
            return f"A human reviewer can help with {service.name}; see [1]."
        return "A human reviewer can help identify the correct public service."
