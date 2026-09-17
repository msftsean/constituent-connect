from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class InquiryRequest(BaseModel):
    message: str = Field(min_length=1, max_length=100_000)
    channel: Literal["web", "chat", "email", "voice"] = "web"
    language: str | None = Field(default=None, max_length=32)


class ApprovalRequest(BaseModel):
    response_id: str | None = Field(default=None, min_length=1)
    reviewer: str = Field(default="api-human-reviewer", max_length=200)
    edited_text: str | None = Field(default=None, max_length=100_000)
    decision: Literal["approve", "edit", "reject", "reroute", "escalate"] = "approve"
    target_service_id: str | None = Field(default=None, max_length=200)
    reason: str | None = Field(default=None, max_length=1_000)


class CaseRequest(BaseModel):
    response_id: str = Field(min_length=1)


class ErrorResponse(BaseModel):
    error: str
    correlation_id: str
    details: Any | None = None


class HealthResponse(BaseModel):
    status: Literal["healthy"]
    mode: Literal["local-synthetic"]
    correlation_id: str


class ApiResponse(BaseModel):
    data: Any
    correlation_id: str
