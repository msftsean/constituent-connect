from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"


def read_env_file(path: Path = ENV_PATH) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def write_env_values(values: dict[str, str], path: Path = ENV_PATH) -> None:
    existing = read_env_file(path)
    merged = {**existing, **values}
    lines = [
        "# Local generated workshop settings. Do not commit this file.",
        *[f"{key}={value}" for key, value in sorted(merged.items())],
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def load_env(path: Path = ENV_PATH) -> dict[str, str]:
    values = read_env_file(path)
    import os

    for key, value in values.items():
        os.environ.setdefault(key, value)
    return values
