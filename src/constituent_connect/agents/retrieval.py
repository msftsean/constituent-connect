from __future__ import annotations

import re

from ..config import Catalog
from ..models import Citation, NormalizedInquiry, RouteRecommendation, TraceEvent
from ..security import contains_prompt_injection


class PublicKnowledgeAgent:
    def __init__(self, catalog: Catalog) -> None:
        self.catalog = catalog

    def retrieve(
        self, inquiry: NormalizedInquiry, route: RouteRecommendation, limit: int = 3
    ) -> list[Citation]:
        if inquiry.emergency_signal or not route.primary_service_id:
            inquiry.transformation_history.append(
                TraceEvent(stage="retrieval", outcome="skipped")
            )
            return []

        service_ids = {
            route.primary_service_id,
            *route.secondary_service_ids,
        }
        query_terms = self._terms(inquiry.redacted_content)
        ranked: list[tuple[float, dict[str, object]]] = []
        blocked = 0
        for document in self.catalog.public_knowledge:
            if not document.get("approved", False):
                continue
            content = str(document["content"])
            if contains_prompt_injection(content):
                blocked += 1
                continue
            if document["service_id"] not in service_ids:
                continue
            overlap = len(query_terms & self._terms(content + " " + str(document["title"])))
            score = 1.0 + overlap
            ranked.append((score, document))
        ranked.sort(key=lambda item: item[0], reverse=True)
        citations = [
            Citation(
                title=str(document["title"]),
                public_url=str(document["public_url"]),
                excerpt=str(document["content"]),
            )
            for _, document in ranked[:limit]
        ]
        inquiry.transformation_history.append(
            TraceEvent(
                stage="retrieval",
                outcome="evidence_found" if citations else "abstain_no_evidence",
                details={"citation_count": len(citations), "unsafe_documents_blocked": blocked},
            )
        )
        return citations

    @staticmethod
    def _terms(text: str) -> set[str]:
        return {
            token
            for token in re.findall(r"[a-z0-9]+", text.lower())
            if len(token) > 2
        }
