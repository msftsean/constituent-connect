from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from .models import TraceEvent, now_iso


@dataclass(slots=True)
class TraceMetadata:
    correlation_id: str
    orchestrator: str
    started_at: str = field(default_factory=now_iso)
    completed_at: str | None = None
    total_latency_ms: float | None = None
    stage_latency_ms: dict[str, float] = field(default_factory=dict)
    model_calls: int = 0
    estimated_cost: float = 0.0
    _started_clock: float = field(default_factory=time.perf_counter, repr=False)

    def finish(self) -> None:
        self.completed_at = now_iso()
        self.total_latency_ms = round(
            (time.perf_counter() - self._started_clock) * 1000, 3
        )

    def stage(self, name: str, started_clock: float) -> float:
        latency = round((time.perf_counter() - started_clock) * 1000, 3)
        self.stage_latency_ms[name] = latency
        return latency


def trace_details(
    metadata: TraceMetadata, stage: str, latency_ms: float | None = None
) -> dict[str, Any]:
    details: dict[str, Any] = {
        "correlation_id": metadata.correlation_id,
        "orchestrator": metadata.orchestrator,
        "model_calls": metadata.model_calls,
        "estimated_cost": metadata.estimated_cost,
    }
    if latency_ms is not None:
        details["latency_ms"] = latency_ms
    if stage in metadata.stage_latency_ms:
        details["stage_latency_ms"] = metadata.stage_latency_ms[stage]
    return details


def append_trace_metadata(
    history: list[TraceEvent], metadata: TraceMetadata
) -> None:
    for event in history:
        event.details.setdefault("correlation_id", metadata.correlation_id)
        event.details.setdefault("orchestrator", metadata.orchestrator)
        event.details.setdefault("model_calls", metadata.model_calls)
        event.details.setdefault("estimated_cost", metadata.estimated_cost)
        if event.stage in metadata.stage_latency_ms:
            event.details.setdefault(
                "latency_ms", metadata.stage_latency_ms[event.stage]
            )
