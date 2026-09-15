from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from local_env import ENV_PATH, load_env, read_env_file, write_env_values  # noqa: E402
from constituent_connect.approval import (  # noqa: E402
    APPROVER_ID_ENV,
    APPROVER_ROLE,
    APPROVER_TOKEN_ENV,
    LOCAL_WORKSHOP_APPROVAL_ENV,
    resolve_approver,
)
from constituent_connect.eval_runner import run_evaluations  # noqa: E402
from constituent_connect.workflow import ConstituentConnectWorkflow  # noqa: E402


AZURE_ENV_NAMES = (
    "AZURE_CLIENT_ID",
    "AZURE_TENANT_ID",
    "AZURE_CLIENT_SECRET",
    "AZURE_SUBSCRIPTION_ID",
)
TEAM_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def ensure_local_workshop_env(team_id: str) -> dict[str, str]:
    values = read_env_file()
    updates: dict[str, str] = {}
    if values.get(LOCAL_WORKSHOP_APPROVAL_ENV, "").lower() != "true":
        updates[LOCAL_WORKSHOP_APPROVAL_ENV] = "true"
    if not values.get(APPROVER_ID_ENV):
        updates[APPROVER_ID_ENV] = "local-workshop-reviewer"
    if not values.get(APPROVER_TOKEN_ENV):
        updates[APPROVER_TOKEN_ENV] = secrets.token_urlsafe(32)
    if values.get("CC_TEAM_ID") != team_id:
        updates["CC_TEAM_ID"] = team_id
    if updates:
        write_env_values(updates)
    return load_env()


def check_json(path: Path) -> None:
    with path.open(encoding="utf-8") as handle:
        json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run local workshop readiness checks without Azure credentials."
    )
    parser.add_argument(
        "--full-eval",
        action="store_true",
        help="Also run the full synthetic evaluation release gate.",
    )
    parser.add_argument(
        "--team-id",
        default=os.environ.get("CC_TEAM_ID", "local"),
        help="Local team namespace for generated readiness artifacts.",
    )
    args = parser.parse_args()
    if not TEAM_ID_PATTERN.fullmatch(args.team_id):
        raise SystemExit("TEAM_ID may contain only letters, numbers, dot, underscore, or hyphen.")

    start = time.perf_counter()
    for relative in (
        "config/app.json",
        "data/agencies.json",
        "data/services.json",
        "data/public_knowledge.json",
        "data/inquiries.json",
    ):
        check_json(ROOT / relative)

    workflow = ConstituentConnectWorkflow()
    result = workflow.process(
        "Where do I apply for a replacement professional license?",
        "web",
    )
    if result.route.primary_service_id != "professional-licensing":
        raise AssertionError("Routine license inquiry did not route to professional licensing.")
    if result.response.approval_status != "pending":
        raise AssertionError("Draft response was not pending human approval.")
    try:
        workflow.create_case(result.response.response_id)
    except ValueError as exc:
        if "approval" not in str(exc).lower():
            raise
    else:
        raise AssertionError("Case creation succeeded before approval.")

    saved_env = {
        name: os.environ.get(name)
        for name in (
            APPROVER_ID_ENV,
            APPROVER_TOKEN_ENV,
            LOCAL_WORKSHOP_APPROVAL_ENV,
        )
    }
    for name in saved_env:
        os.environ.pop(name, None)
    try:
        resolve_approver(workflow.catalog.settings, None, None)
    except PermissionError:
        pass
    else:
        raise AssertionError("Approval resolved without a configured approver token.")
    try:
        resolve_approver(workflow.catalog.settings, APPROVER_ROLE, None)
    except PermissionError:
        pass
    else:
        raise AssertionError("Bare approver role header bypassed the approval token gate.")
    for name, value in saved_env.items():
        if value is not None:
            os.environ[name] = value

    env_values = ensure_local_workshop_env(args.team_id)
    reviewer = resolve_approver(
        workflow.catalog.settings,
        APPROVER_ROLE,
        env_values[APPROVER_TOKEN_ENV],
    )
    approved = workflow.approve_response(result.response.response_id, reviewer)
    if approved.approved_by != "local-workshop-reviewer":
        raise AssertionError("Approval did not use the configured local workshop identity.")
    case = workflow.create_case(result.response.response_id)
    if not case.case_id or not case.agency_work_items:
        raise AssertionError("Approved response did not create a synthetic case.")

    emergency = workflow.process(
        "There is smoke filling my apartment and someone is trapped.",
        "web",
    )
    if emergency.route.status != "emergency_exit" or emergency.route.primary_service_id:
        raise AssertionError("Emergency inquiry did not exit routine routing.")

    eval_summary = None
    if args.full_eval:
        team_id = env_values.get("CC_TEAM_ID", "local")
        output_dir = (
            ROOT / "reports" / "readiness"
            if team_id == "local"
            else ROOT / "reports" / "teams" / team_id / "readiness"
        )
        eval_summary = run_evaluations(output_dir=output_dir)["summary"]
        if eval_summary["release_gate"] != "pass":
            raise AssertionError("Synthetic evaluation release gate failed.")

    elapsed = round(time.perf_counter() - start, 2)
    azure_env_present = [name for name in AZURE_ENV_NAMES if os.environ.get(name)]
    output = {
        "status": "ready",
        "mode": workflow.catalog.settings["application"]["mode"],
        "seconds": elapsed,
        "azure_credentials_required": False,
        "azure_credential_env_present": azure_env_present,
        "approval": {
            "case_blocked_before_approval": True,
            "local_workshop_identity": approved.approved_by,
            "case_created_after_approval": case.case_id,
            "bare_role_rejected_by_default": True,
            "local_env": str(ENV_PATH),
        },
        "team_id": env_values.get("CC_TEAM_ID", "local"),
        "emergency_boundary": emergency.route.status,
        "evaluation": eval_summary,
    }
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
