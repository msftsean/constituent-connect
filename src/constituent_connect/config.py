from __future__ import annotations

import json
import os
from dataclasses import fields
from pathlib import Path
from typing import Any

from .models import AgencyService
from .retention import RetentionPolicy


_PACKAGE_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _resolve_project_root() -> Path:
    configured = os.getenv("CC_PROJECT_ROOT")
    if configured:
        return Path(configured)
    working_directory = Path.cwd()
    if (working_directory / "config" / "app.json").exists():
        return working_directory
    return _PACKAGE_PROJECT_ROOT


PROJECT_ROOT = _resolve_project_root()


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class Catalog:
    """Configuration-backed synthetic agency, service, and public-content catalog."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or PROJECT_ROOT
        data_dir = self.root / "data"
        config_path = Path(os.getenv("CC_CONFIG_PATH", self.root / "config" / "app.json"))
        self.settings: dict[str, Any] = _load_json(config_path)
        self.agencies: list[dict[str, Any]] = _load_json(data_dir / "agencies.json")
        service_fields = {item.name for item in fields(AgencyService)}
        self.services = [
            AgencyService(**{key: value for key, value in item.items() if key in service_fields})
            for item in _load_json(data_dir / "services.json")
        ]
        self.public_knowledge: list[dict[str, Any]] = _load_json(
            data_dir / "public_knowledge.json"
        )
        self.sample_inquiries: list[dict[str, Any]] = _load_json(
            data_dir / "inquiries.json"
        )
        self.service_by_id = {service.service_id: service for service in self.services}
        self.retention_policy = RetentionPolicy.from_settings(self.settings)
        orchestration = self.settings.get("orchestration", {})
        self.orchestration = {
            "prefer_agent_framework": bool(
                orchestration.get("prefer_agent_framework", True)
            ),
            "max_steps": max(1, int(orchestration.get("max_steps", 16))),
            "timeout_seconds": max(
                0.1, float(orchestration.get("timeout_seconds", 10.0))
            ),
        }

    def agency_name(self, agency_id: str) -> str:
        agency = next(
            (item for item in self.agencies if item["agency_id"] == agency_id), None
        )
        return agency["name"] if agency else agency_id
