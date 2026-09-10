from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:12]}"


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(slots=True)
class ConstituentMessage:
    message_id: str
    channel: str
    received_at: str
    language: str
    raw_content: str
    attachments: list[str] = field(default_factory=list)
    consent_flags: dict[str, bool] = field(default_factory=dict)


@dataclass(slots=True)
class PiiFinding:
    category: str
    count: int


@dataclass(slots=True)
class IntentCandidate:
    service_id: str
    agency_id: str
    score: float
    matched_terms: list[str] = field(default_factory=list)


@dataclass(slots=True)
class TraceEvent:
    stage: str
    outcome: str
    at: str = field(default_factory=now_iso)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class NormalizedInquiry:
    inquiry_id: str
    message_id: str
    summary: str
    redacted_content: str
    detected_language: str
    intent_candidates: list[IntentCandidate]
    urgency: str
    emergency_signal: bool
    pii_findings: list[PiiFinding]
    injection_detected: bool = False
    discriminatory_instruction_detected: bool = False
    emergency_guidance: str | None = None
    trace_id: str = field(default_factory=lambda: new_id("trace"))
    transformation_history: list[TraceEvent] = field(default_factory=list)


@dataclass(slots=True)
class AgencyService:
    service_id: str
    agency_id: str
    name: str
    description: str
    eligibility_disclaimer: str
    geography: str
    queue_id: str
    owner_id: str
    public_urls: list[str]
    effective_date: str
    keywords: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RouteRecommendation:
    primary_service_id: str | None
    secondary_service_ids: list[str]
    confidence: float
    reason: str
    clarifying_question: str | None
    human_review_required: bool
    status: str


@dataclass(slots=True)
class Citation:
    title: str
    public_url: str
    excerpt: str


@dataclass(slots=True)
class GroundedResponse:
    response_id: str
    inquiry_id: str
    channel: str
    language: str
    draft: str
    citations: list[Citation]
    prohibited_commitment_check: bool
    approval_status: str
    ai_disclosure: str
    quality_issues: list[str] = field(default_factory=list)
    approved_text: str | None = None
    approved_by: str | None = None
    approved_at: str | None = None


@dataclass(slots=True)
class AgencyWorkItem:
    service_id: str
    queue_id: str
    summary: str
    disclosure_note: str


@dataclass(slots=True)
class AuditEvent:
    action: str
    actor: str
    at: str = field(default_factory=now_iso)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CaseRecord:
    case_id: str
    inquiry_id: str
    response_id: str
    approved_summary: str
    agency_work_items: list[AgencyWorkItem]
    status: str
    assigned_queues: list[str]
    audit_events: list[AuditEvent]


@dataclass(slots=True)
class WorkflowResult:
    message: ConstituentMessage
    inquiry: NormalizedInquiry
    route: RouteRecommendation
    response: GroundedResponse
    case: CaseRecord | None = None


def to_dict(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return {key: to_dict(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {key: to_dict(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_dict(item) for item in value]
    return value
