from __future__ import annotations

from datetime import UTC, datetime
from threading import RLock
import time
from typing import Any

from .agents import (
    CaseAgent,
    ChannelIntakeAgent,
    IntentAgent,
    PublicKnowledgeAgent,
    QualityAgent,
    ResponseAgent,
    RoutingAgent,
    SafetyPrivacyAgent,
)
from .config import Catalog
from .acs import CommunicationServicesAdapter, create_acs_adapter
from .models import (
    AuditEvent,
    CaseRecord,
    GroundedResponse,
    NormalizedInquiry,
    RouteRecommendation,
    TraceEvent,
    WorkflowResult,
    new_id,
    now_iso,
)
from .orchestration import BoundedOrchestrator, create_orchestrator
from .telemetry import TraceMetadata, append_trace_metadata, trace_details


class ConstituentConnectWorkflow:
    """Local orchestration with transport-neutral agent boundaries."""

    def __init__(
        self,
        catalog: Catalog | None = None,
        orchestrator: BoundedOrchestrator | None = None,
    ) -> None:
        self.catalog = catalog or Catalog()
        self.orchestrator = orchestrator or create_orchestrator(
            prefer_framework=self.catalog.orchestration["prefer_agent_framework"],
            max_steps=self.catalog.orchestration["max_steps"],
            timeout_seconds=self.catalog.orchestration["timeout_seconds"],
        )
        self.acs_adapter: CommunicationServicesAdapter = create_acs_adapter(
            self.catalog.settings
        )
        self.intake_agent = ChannelIntakeAgent()
        self.safety_agent = SafetyPrivacyAgent()
        self.intent_agent = IntentAgent(self.catalog)
        self.routing_agent = RoutingAgent(self.catalog)
        self.retrieval_agent = PublicKnowledgeAgent(self.catalog)
        self.response_agent = ResponseAgent(self.catalog)
        self.quality_agent = QualityAgent()
        self.case_agent = CaseAgent(self.catalog)
        self.results_by_response: dict[str, WorkflowResult] = {}
        self.inquiries: dict[str, NormalizedInquiry] = {}
        self.cases: dict[str, CaseRecord] = {}
        self.trace_metadata_by_response: dict[str, TraceMetadata] = {}
        self.review_events: list[dict[str, Any]] = []
        self._created_at_by_response: dict[str, datetime] = {}
        self._lock = RLock()

    def assess_intake(
        self, content: str, channel: str = "web", language: str | None = None
    ) -> NormalizedInquiry:
        message = self.intake_agent.normalize(content, channel, language)
        inquiry = self.safety_agent.assess(
            message,
            self.intake_agent.trace(message),
            self.catalog.retention_policy,
        )
        if not inquiry.emergency_signal:
            self.intent_agent.classify(inquiry)
        with self._lock:
            self.inquiries[inquiry.inquiry_id] = inquiry
        return inquiry

    def process(
        self, content: str, channel: str = "web", language: str | None = None
    ) -> WorkflowResult:
        correlation_id = new_id("corr")
        context = self.orchestrator.new_context(correlation_id)
        metadata = TraceMetadata(
            correlation_id=correlation_id,
            orchestrator=self.orchestrator.framework_name,
        )
        message = self._execute_stage(
            context,
            metadata,
            "channel_intake",
            lambda: self.intake_agent.normalize(content, channel, language),
        )
        inquiry = self._execute_stage(
            context,
            metadata,
            "safety_privacy",
            lambda: self.safety_agent.assess(
                message,
                self.intake_agent.trace(message),
                self.catalog.retention_policy,
            ),
        )
        if not inquiry.emergency_signal:
            self._execute_stage(
                context, metadata, "intent", lambda: self.intent_agent.classify(inquiry)
            )
        route = self._execute_stage(
            context, metadata, "routing", lambda: self.routing_agent.recommend(inquiry)
        )
        citations = self._execute_stage(
            context,
            metadata,
            "retrieval",
            lambda: self.retrieval_agent.retrieve(inquiry, route),
        )
        response = self._execute_stage(
            context,
            metadata,
            "response",
            lambda: self.response_agent.draft(
                inquiry, route, citations, message.channel
            ),
        )
        response = self._execute_stage(
            context,
            metadata,
            "quality",
            lambda: self.quality_agent.review(inquiry, route, response),
        )
        metadata.finish()
        inquiry.transformation_history.append(
            TraceEvent(
                stage="orchestration",
                outcome="bounded_complete",
                details={
                    **trace_details(metadata, "orchestration", metadata.total_latency_ms),
                    "steps": context.steps,
                    "stage_names": context.stage_names,
                },
            )
        )
        append_trace_metadata(inquiry.transformation_history, metadata)
        result = WorkflowResult(
            message=message,
            inquiry=inquiry,
            route=route,
            response=response,
        )
        with self._lock:
            self.inquiries[inquiry.inquiry_id] = inquiry
            self.results_by_response[response.response_id] = result
            self.trace_metadata_by_response[response.response_id] = metadata
            self._created_at_by_response[response.response_id] = datetime.now(UTC)
        return result

    def _execute_stage(
        self,
        context: Any,
        metadata: TraceMetadata,
        name: str,
        stage: Any,
    ) -> Any:
        started = time.perf_counter()
        result = self.orchestrator.execute(context, name, stage)
        metadata.stage(name, started)
        return result

    def approve_response(
        self,
        response_id: str,
        reviewer: str,
        edited_text: str | None = None,
        decision: str = "approve",
    ) -> GroundedResponse:
        with self._lock:
            result = self._result(response_id)
            response = result.response
            if response.approval_status != "pending":
                raise ValueError("This response already has a human decision.")
            if decision not in {"approve", "reject"}:
                raise ValueError("Decision must be 'approve' or 'reject'.")
            candidate = (edited_text or response.draft).strip()
            if decision == "approve" and response.ai_disclosure not in candidate:
                candidate = f"{candidate} {response.ai_disclosure}".strip()
            if decision == "approve" and self.quality_agent.PROHIBITED.search(candidate):
                raise ValueError("Edited response contains a prohibited commitment.")
            response.approval_status = "approved" if decision == "approve" else "rejected"
            response.approved_text = candidate if decision == "approve" else None
            response.approved_by = reviewer.strip() or "human-reviewer"
            response.approved_at = now_iso()
            result.inquiry.transformation_history.append(
                TraceEvent(
                    stage="human_approval",
                    outcome=response.approval_status,
                    details={
                        "response_id": response_id,
                        "edited": bool(edited_text and edited_text != response.draft),
                    },
                )
            )
            self.review_events.append(
                {
                    "event_id": new_id("review"),
                    "type": "approval" if decision == "approve" else "rejection",
                    "response_id": response_id,
                    "reviewer": response.approved_by,
                    "edited": bool(edited_text and edited_text != response.draft),
                    "correlation_id": self._correlation_id(response_id),
                    "at": response.approved_at,
                }
            )
            return response

    def record_correction(
        self,
        response_id: str,
        reviewer: str,
        corrected_text: str,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """Capture a human correction as an evaluation signal only."""
        with self._lock:
            result = self._result(response_id)
            corrected = corrected_text.strip()
            if not corrected:
                raise ValueError("Corrected text is required.")
            event = {
                "event_id": new_id("correction"),
                "type": "correction",
                "response_id": response_id,
                "reviewer": reviewer.strip() or "human-reviewer",
                "original_text": self._redact_review_text(result.response.draft),
                "corrected_text": self._redact_review_text(corrected),
                "reason": reason,
                "correlation_id": self._correlation_id(response_id),
                "at": now_iso(),
            }
            self.review_events.append(event)
            result.inquiry.transformation_history.append(
                TraceEvent(
                    stage="human_review",
                    outcome="correction_captured",
                    details={
                        "event_id": event["event_id"],
                        "correlation_id": event["correlation_id"],
                        "reason": reason,
                    },
                )
            )
            return dict(event)

    capture_correction = record_correction

    def reroute_response(
        self,
        response_id: str,
        reviewer: str,
        primary_service_id: str,
        reason: str | None = None,
    ) -> RouteRecommendation:
        """Apply an explicit human reroute without mutating catalog policy."""
        with self._lock:
            result = self._result(response_id)
            if primary_service_id not in self.catalog.service_by_id:
                raise ValueError(f"Unknown service ID: {primary_service_id}")
            if result.case is not None:
                raise ValueError("A created case cannot be rerouted.")
            previous = result.route.primary_service_id
            result.route.primary_service_id = primary_service_id
            result.route.secondary_service_ids = [
                item
                for item in result.route.secondary_service_ids
                if item != primary_service_id
            ]
            result.route.status = "route_proposed"
            result.route.human_review_required = True
            result.inquiry.transformation_history.append(
                TraceEvent(
                    stage="human_review",
                    outcome="reroute_captured",
                    details={
                        "from_service_id": previous,
                        "to_service_id": primary_service_id,
                        "correlation_id": self._correlation_id(response_id),
                        "reason": reason,
                    },
                )
            )
            self.review_events.append(
                {
                    "event_id": new_id("reroute"),
                    "type": "reroute",
                    "response_id": response_id,
                    "reviewer": reviewer.strip() or "human-reviewer",
                    "from_service_id": previous,
                    "to_service_id": primary_service_id,
                    "reason": reason,
                    "correlation_id": self._correlation_id(response_id),
                    "at": now_iso(),
                }
            )
            return result.route

    def purge_expired(self, now: datetime | None = None) -> int:
        """Drop in-memory workflow records after the configured trace retention."""
        current = now or datetime.now(UTC)
        removed = 0
        with self._lock:
            for response_id, created_at in list(self._created_at_by_response.items()):
                result = self.results_by_response.get(response_id)
                if (
                    result is not None
                    and not self.catalog.retention_policy.should_keep(
                        created_at, current, raw=True
                    )
                ):
                    result.message.raw_content = self.catalog.retention_policy.redaction_marker
                if not self.catalog.retention_policy.should_keep(created_at, current):
                    result = self.results_by_response.pop(response_id, None)
                    if result is not None:
                        self.inquiries.pop(result.inquiry.inquiry_id, None)
                    self.trace_metadata_by_response.pop(response_id, None)
                    self._created_at_by_response.pop(response_id, None)
                    removed += 1
            self.review_events = [
                event
                for event in self.review_events
                if event.get("at") is None
                or self.catalog.retention_policy.should_keep(
                    datetime.fromisoformat(str(event["at"])), current
                )
            ]
        return removed

    def _correlation_id(self, response_id: str) -> str | None:
        metadata = self.trace_metadata_by_response.get(response_id)
        return metadata.correlation_id if metadata else None

    def _redact_review_text(self, text: str) -> str:
        from .security import redact_pii

        return redact_pii(
            text, marker=self.catalog.retention_policy.redaction_marker
        ).text

    def create_case(self, response_id: str) -> CaseRecord:
        with self._lock:
            result = self._result(response_id)
            case = self.case_agent.create(
                result.inquiry, result.route, result.response
            )
            result.case = case
            result.inquiry.transformation_history.append(
                TraceEvent(
                    stage="case",
                    outcome="created",
                    details={"case_id": case.case_id, "work_items": len(case.agency_work_items)},
                )
            )
            case.audit_events.append(
                AuditEvent(
                    action="route_recorded",
                    actor=result.response.approved_by or "human-reviewer",
                    details={
                        "primary_service_id": result.route.primary_service_id,
                        "secondary_service_ids": result.route.secondary_service_ids,
                    },
                )
            )
            self.cases[case.case_id] = case
            return case

    def _result(self, response_id: str) -> WorkflowResult:
        try:
            return self.results_by_response[response_id]
        except KeyError as exc:
            raise KeyError(f"Unknown response ID: {response_id}") from exc
