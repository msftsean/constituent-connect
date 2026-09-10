from __future__ import annotations

from typing import Protocol

from .models import CaseRecord, GroundedResponse, WorkflowResult


class ConstituentConnectService(Protocol):
    """Transport-neutral application interface for a future FastAPI adapter."""

    def process(
        self, content: str, channel: str = "web", language: str | None = None
    ) -> WorkflowResult: ...

    def approve_response(
        self,
        response_id: str,
        reviewer: str,
        edited_text: str | None = None,
        decision: str = "approve",
    ) -> GroundedResponse: ...

    def create_case(self, response_id: str) -> CaseRecord: ...
