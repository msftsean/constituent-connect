from __future__ import annotations

from ..config import Catalog
from ..models import (
    AgencyWorkItem,
    AuditEvent,
    CaseRecord,
    GroundedResponse,
    NormalizedInquiry,
    RouteRecommendation,
    new_id,
)


class CaseAgent:
    def __init__(self, catalog: Catalog) -> None:
        self.catalog = catalog

    def create(
        self,
        inquiry: NormalizedInquiry,
        route: RouteRecommendation,
        response: GroundedResponse,
    ) -> CaseRecord:
        if inquiry.emergency_signal:
            raise ValueError(
                "Emergency inquiries cannot become routine cases; provide guidance "
                "and complete human escalation outside this application."
            )
        if response.approval_status != "approved":
            raise ValueError("Human approval is required before case creation.")
        if route.status != "route_proposed" or not route.primary_service_id:
            raise ValueError("A confirmed proposed route is required before case creation.")

        service_ids = [route.primary_service_id, *route.secondary_service_ids]
        work_items = []
        for service_id in service_ids:
            service = self.catalog.service_by_id[service_id]
            work_items.append(
                AgencyWorkItem(
                    service_id=service_id,
                    queue_id=service.queue_id,
                    summary=self._scoped_summary(inquiry, service.service_id, service.name),
                    disclosure_note=(
                        "Contains only the redacted constituent summary needed for "
                        "this synthetic service handoff."
                    ),
                )
            )
        return CaseRecord(
            case_id=new_id("case"),
            inquiry_id=inquiry.inquiry_id,
            response_id=response.response_id,
            approved_summary=inquiry.summary,
            agency_work_items=work_items,
            status="open",
            assigned_queues=[item.queue_id for item in work_items],
            audit_events=[
                AuditEvent(
                    action="case_created_after_human_approval",
                    actor=response.approved_by or "human-reviewer",
                    details={"response_id": response.response_id},
                )
            ],
        )

    @staticmethod
    def _scoped_summary(
        inquiry: NormalizedInquiry, service_id: str, service_name: str
    ) -> str:
        candidate = next(
            (item for item in inquiry.intent_candidates if item.service_id == service_id),
            None,
        )
        terms = [term.lower() for term in (candidate.matched_terms if candidate else [])]
        clauses = [
            clause.strip()
            for clause in inquiry.redacted_content.replace(";", ".").split(".")
            if clause.strip()
        ]
        scoped = [
            clause for clause in clauses
            if terms and any(term in clause.lower() for term in terms)
        ]
        detail = f"Matched service terms: {', '.join(terms)}" if terms else ""
        if not detail:
            detail = f"Constituent requested help with {service_name}."
        return f"Service-specific handoff for {service_name}: {detail}"
