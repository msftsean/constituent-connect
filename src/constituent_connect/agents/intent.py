from __future__ import annotations

import re

from ..config import Catalog
from ..models import IntentCandidate, NormalizedInquiry, TraceEvent


class IntentAgent:
    def __init__(self, catalog: Catalog) -> None:
        self.catalog = catalog

    def classify(self, inquiry: NormalizedInquiry) -> list[IntentCandidate]:
        if inquiry.emergency_signal:
            inquiry.transformation_history.append(
                TraceEvent(stage="intent", outcome="skipped_for_emergency")
            )
            return []

        text = inquiry.redacted_content.lower()
        candidates: list[IntentCandidate] = []
        for service in self.catalog.services:
            matched: list[str] = []
            points = 0.0
            for keyword in service.keywords:
                if re.search(rf"\b{re.escape(keyword.lower())}\b", text):
                    matched.append(keyword)
                    points += 1.0 if " " in keyword else 0.45
            if matched:
                score = min(0.99, 0.25 + (points * 0.22))
                candidates.append(
                    IntentCandidate(
                        service_id=service.service_id,
                        agency_id=service.agency_id,
                        score=round(score, 3),
                        matched_terms=matched,
                    )
                )

        candidates.sort(key=lambda item: item.score, reverse=True)
        inquiry.intent_candidates = candidates
        inquiry.transformation_history.append(
            TraceEvent(
                stage="intent",
                outcome="classified" if candidates else "no_supported_intent",
                details={
                    "candidate_count": len(candidates),
                    "top_service": candidates[0].service_id if candidates else None,
                },
            )
        )
        return candidates
