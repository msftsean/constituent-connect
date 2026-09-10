from __future__ import annotations

import importlib.util
import time
from dataclasses import dataclass, field
from typing import Callable, TypeVar


T = TypeVar("T")
Stage = Callable[[], T]


class OrchestrationLimitError(RuntimeError):
    """Raised when bounded orchestration cannot safely complete."""


@dataclass(slots=True)
class OrchestrationContext:
    correlation_id: str
    max_steps: int = 16
    timeout_seconds: float = 10.0
    steps: int = 0
    stage_names: list[str] = field(default_factory=list)
    started_at: float = field(default_factory=time.perf_counter)


class BoundedOrchestrator:
    """Small execution contract compatible with agent-framework style pipelines."""

    framework_name = "local-deterministic"
    framework_available = False

    def __init__(self, max_steps: int = 16, timeout_seconds: float = 10.0) -> None:
        if max_steps < 1:
            raise ValueError("max_steps must be positive")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.max_steps = max_steps
        self.timeout_seconds = timeout_seconds

    def new_context(self, correlation_id: str) -> OrchestrationContext:
        return OrchestrationContext(
            correlation_id=correlation_id,
            max_steps=self.max_steps,
            timeout_seconds=self.timeout_seconds,
        )

    def execute(
        self, context: OrchestrationContext, name: str, stage: Stage[T]
    ) -> T:
        if context.steps >= context.max_steps:
            raise OrchestrationLimitError("Workflow step limit exceeded.")
        if time.perf_counter() - context.started_at > context.timeout_seconds:
            raise OrchestrationLimitError("Workflow timeout exceeded.")
        context.steps += 1
        context.stage_names.append(name)
        return stage()


class LocalDeterministicOrchestrator(BoundedOrchestrator):
    """The default fallback: bounded, synchronous, and deterministic."""


class MicrosoftAgentFrameworkOrchestrator(BoundedOrchestrator):
    """Compatibility seam for Microsoft Agent Framework installations.

    Safety and routing remain local calls even when this class is selected. The
    framework is deliberately not required at import time and is not used to
    make policy or routing decisions.
    """

    framework_name = "microsoft-agent-framework"

    def __init__(self, max_steps: int = 16, timeout_seconds: float = 10.0) -> None:
        super().__init__(max_steps=max_steps, timeout_seconds=timeout_seconds)
        self.framework_available = importlib.util.find_spec("agent_framework") is not None


AgentFrameworkOrchestrator = MicrosoftAgentFrameworkOrchestrator
DeterministicOrchestrator = LocalDeterministicOrchestrator


def create_orchestrator(
    *,
    prefer_framework: bool = True,
    max_steps: int = 16,
    timeout_seconds: float = 10.0,
) -> BoundedOrchestrator:
    if prefer_framework and importlib.util.find_spec("agent_framework") is not None:
        return MicrosoftAgentFrameworkOrchestrator(
            max_steps=max_steps, timeout_seconds=timeout_seconds
        )
    return LocalDeterministicOrchestrator(
        max_steps=max_steps, timeout_seconds=timeout_seconds
    )
