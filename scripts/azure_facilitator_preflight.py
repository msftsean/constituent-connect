from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from typing import Any


PROVIDERS = (
    "Microsoft.App",
    "Microsoft.ContainerRegistry",
    "Microsoft.ManagedIdentity",
    "Microsoft.Authorization",
    "Microsoft.Insights",
    "Microsoft.KeyVault",
    "Microsoft.OperationalInsights",
    "Microsoft.Storage",
    "Microsoft.DocumentDB",
    "Microsoft.Search",
)


def az_json(args: list[str]) -> Any:
    completed = subprocess.run(
        ["az", *args, "--output", "json"],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout or "null")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Facilitator-only read-only Azure preflight. Does not deploy or mutate resources."
    )
    parser.add_argument("--location", default="eastus2")
    args = parser.parse_args()
    if not shutil.which("az"):
        raise SystemExit("Azure CLI is not installed.")

    account = az_json(["account", "show"])
    subscription_id = account["id"]
    provider_states = {
        provider: az_json(["provider", "show", "--namespace", provider]).get(
            "registrationState"
        )
        for provider in PROVIDERS
    }
    user_name = account.get("user", {}).get("name")
    role_assignments = []
    if user_name:
        role_assignments = az_json(
            [
                "role",
                "assignment",
                "list",
                "--assignee",
                user_name,
                "--scope",
                f"/subscriptions/{subscription_id}",
            ]
        )
    privileged_roles = {
        item.get("roleDefinitionName")
        for item in role_assignments
        if item.get("roleDefinitionName") in {"Owner", "User Access Administrator"}
    }
    usage = az_json(["vm", "list-usage", "--location", args.location])
    cores = [
        item
        for item in usage
        if "cores" in str(item.get("name", {}).get("value", "")).lower()
    ][:5]
    output = {
        "subscription": subscription_id,
        "location": args.location,
        "provider_registration": provider_states,
        "role_assignment_write_likely": bool(privileged_roles),
        "subscription_roles_checked": sorted(privileged_roles),
        "regional_core_usage_sample": cores,
        "mutated_resources": False,
        "participant_action_required": False,
    }
    print(json.dumps(output, indent=2))
    missing = [
        provider
        for provider, state in provider_states.items()
        if state != "Registered"
    ]
    return 1 if missing or not privileged_roles else 0


if __name__ == "__main__":
    raise SystemExit(main())
