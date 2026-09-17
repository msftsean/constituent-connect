from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class CommunicationServicesDisabledError(RuntimeError):
    """Raised when the optional ACS integration is not explicitly enabled."""


@dataclass(frozen=True, slots=True)
class ACSOutboundMessage:
    channel: str
    recipient: str
    text: str
    correlation_id: str


class CommunicationServicesAdapter:
    """Optional ACS seam; no Azure SDK or network call is required locally."""

    def __init__(self, settings: dict[str, Any]) -> None:
        features = settings.get("features", {})
        self.enabled = bool(features.get("communication_services", False))

    def send(self, message: ACSOutboundMessage) -> None:
        if not self.enabled:
            raise CommunicationServicesDisabledError(
                "Communication Services integration is disabled."
            )
        raise NotImplementedError(
            "ACS delivery requires an explicitly configured production adapter."
        )


def create_acs_adapter(settings: dict[str, Any]) -> CommunicationServicesAdapter:
    return CommunicationServicesAdapter(settings)
