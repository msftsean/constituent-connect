from __future__ import annotations

from ..config import Catalog
from ..models import NormalizedInquiry, RouteRecommendation, TraceEvent


class RoutingAgent:
    authoritative = True
    uses_generation = False

    def __init__(self, catalog: Catalog) -> None:
        self.catalog = catalog
        self.threshold = float(catalog.settings["routing"]["minimum_confidence"])
        self.secondary_threshold = float(
            catalog.settings["routing"]["secondary_confidence"]
        )

    def recommend(self, inquiry: NormalizedInquiry) -> RouteRecommendation:
        if inquiry.emergency_signal:
            route = RouteRecommendation(
                primary_service_id=None,
                secondary_service_ids=[],
                confidence=1.0,
                reason=(
                    "Emergency language requires immediate guidance and human "
                    "escalation; no routine queue or dispatch action was created."
                ),
                clarifying_question=None,
                human_review_required=True,
                status="emergency_exit",
            )
            self._trace(inquiry, route)
            return route

        candidates = inquiry.intent_candidates
        if not candidates or candidates[0].score < self.threshold:
            route = RouteRecommendation(
                primary_service_id=None,
                secondary_service_ids=[],
                confidence=candidates[0].score if candidates else 0.0,
                reason="No configured service has enough evidence for a reliable route.",
                clarifying_question=(
                    "Which Maryland service or type of permit, license, payment, "
                    "or registration do you need help with?"
                ),
                human_review_required=True,
                status="clarification_required",
            )
            self._trace(inquiry, route)
            return route

        primary = candidates[0]
        secondaries = [
            candidate.service_id
            for candidate in candidates[1:]
            if candidate.score >= self.secondary_threshold
            and candidate.agency_id != primary.agency_id
        ]
        service = self.catalog.service_by_id[primary.service_id]
        route = RouteRecommendation(
            primary_service_id=primary.service_id,
            secondary_service_ids=secondaries,
            confidence=primary.score,
            reason=(
                f"Matched configured terms for {service.name}; "
                f"accountable agency is {self.catalog.agency_name(service.agency_id)}."
            ),
            clarifying_question=None,
            human_review_required=True,
            status="route_proposed",
        )
        self._trace(inquiry, route)
        return route

    @staticmethod
    def _trace(
        inquiry: NormalizedInquiry, route: RouteRecommendation
    ) -> None:
        inquiry.transformation_history.append(
            TraceEvent(
                stage="routing",
                outcome=route.status,
                details={
                    "primary_service_id": route.primary_service_id,
                    "secondary_service_ids": route.secondary_service_ids,
                    "confidence": route.confidence,
                    "human_review_required": route.human_review_required,
                },
            )
        )
