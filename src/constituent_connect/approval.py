from __future__ import annotations

import hmac
import os
from typing import Any


APPROVER_ID_ENV = "CONSTITUENT_CONNECT_APPROVER_ID"
APPROVER_TOKEN_ENV = "CONSTITUENT_CONNECT_APPROVER_TOKEN"
APPROVER_TOKEN_HEADER = "X-Approver-Token"
APPROVER_ROLE = "approver"
LOCAL_WORKSHOP_APPROVAL_ENV = "CC_LOCAL_WORKSHOP_APPROVAL"


def local_workshop_approval_enabled() -> bool:
    return os.environ.get(LOCAL_WORKSHOP_APPROVAL_ENV, "").lower() in {
        "1",
        "true",
        "yes",
    }


def workshop_approval_session(settings: dict[str, Any]) -> dict[str, str]:
    if not local_workshop_approval_enabled():
        raise PermissionError("Local workshop approval is not enabled.")
    approval = settings.get("approval", {})
    configured_token = os.environ.get(APPROVER_TOKEN_ENV)
    configured_reviewer = os.environ.get(APPROVER_ID_ENV)
    if not configured_token or not configured_reviewer:
        raise PermissionError(
            "Local workshop approval requires a generated approver token and identity."
        )
    return {
        "approval_role": str(approval.get("required_role", APPROVER_ROLE)),
        "approver_token": configured_token,
        "approver_id": configured_reviewer,
    }


def resolve_approver(
    settings: dict[str, Any],
    approval_role: str | None,
    approver_token: str | None,
) -> str:
    configured_token = os.environ.get(APPROVER_TOKEN_ENV)
    configured_reviewer = os.environ.get(APPROVER_ID_ENV)
    approval = settings.get("approval", {})
    required_role = str(approval.get("required_role", APPROVER_ROLE))
    if (
        configured_token
        and approver_token
        and configured_reviewer
        and approval_role == required_role
        and hmac.compare_digest(approver_token, configured_token)
    ):
        return configured_reviewer

    raise PermissionError(
        "A configured approval token, approver identity, and approver role are required."
    )
