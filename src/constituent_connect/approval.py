from __future__ import annotations

import os
from typing import Any


APPROVER_ID_ENV = "CONSTITUENT_CONNECT_APPROVER_ID"
APPROVER_TOKEN_ENV = "CONSTITUENT_CONNECT_APPROVER_TOKEN"
APPROVER_TOKEN_HEADER = "X-Approver-Token"
APPROVER_ROLE = "approver"


def resolve_approver(
    settings: dict[str, Any],
    approval_role: str | None,
    approver_token: str | None,
) -> str:
    configured_token = os.environ.get(APPROVER_TOKEN_ENV)
    configured_reviewer = os.environ.get(APPROVER_ID_ENV)
    if configured_token or configured_reviewer:
        if (
            not configured_token
            or not approver_token
            or approver_token != configured_token
            or not configured_reviewer
            or approval_role != APPROVER_ROLE
        ):
            raise PermissionError(
                "A configured approval token, approver identity, and approver role are required."
            )
        return configured_reviewer

    approval = settings.get("approval", {})
    mode = settings.get("application", {}).get("mode")
    required_role = str(approval.get("required_role", APPROVER_ROLE))
    local_enabled = bool(approval.get("local_workshop_enabled", False))
    local_reviewer = str(
        approval.get("local_workshop_approver_id", "local-workshop-reviewer")
    ).strip()
    if (
        mode == "local-synthetic"
        and local_enabled
        and approval_role == required_role
        and local_reviewer
    ):
        return local_reviewer

    raise PermissionError(
        "Local workshop approval requires the configured approver role; token-backed "
        "approval also requires configured approver identity and token environment variables."
    )
