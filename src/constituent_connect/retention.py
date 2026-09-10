from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any


@dataclass(frozen=True, slots=True)
class RetentionPolicy:
    retain_raw_message_in_memory_only: bool = True
    include_raw_message_in_traces: bool = False
    case_summary_redacted: bool = True
    trace_retention_seconds: int = 86_400
    raw_message_retention_seconds: int = 3_600
    redaction_marker: str = "[REDACTED]"

    @classmethod
    def from_settings(cls, settings: dict[str, Any]) -> "RetentionPolicy":
        privacy = settings.get("privacy", {})
        return cls(
            retain_raw_message_in_memory_only=bool(
                privacy.get("retain_raw_message_in_memory_only", True)
            ),
            include_raw_message_in_traces=bool(
                privacy.get("include_raw_message_in_traces", False)
            ),
            case_summary_redacted=bool(privacy.get("case_summary_redacted", True)),
            trace_retention_seconds=max(
                0, int(privacy.get("trace_retention_seconds", 86_400))
            ),
            raw_message_retention_seconds=max(
                0, int(privacy.get("raw_message_retention_seconds", 3_600))
            ),
            redaction_marker=str(privacy.get("redaction_marker", "[REDACTED]")),
        )

    def expires_at(self, created_at: datetime, *, raw: bool = False) -> datetime:
        seconds = (
            self.raw_message_retention_seconds
            if raw
            else self.trace_retention_seconds
        )
        return created_at + timedelta(seconds=seconds)

    def should_keep(self, created_at: datetime, now: datetime | None = None, *, raw: bool = False) -> bool:
        current = now or datetime.now(UTC)
        return current < self.expires_at(created_at, raw=raw)
