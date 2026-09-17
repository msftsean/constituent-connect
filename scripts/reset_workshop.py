from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GLOBAL_TARGETS = (
    "reports/evaluation.json",
    "reports/evaluation.html",
    "reports/readiness",
    "infra/main.json",
    "reports/unit-test",
    "reports/ci",
    "frontend/dist",
    "frontend/tsconfig.tsbuildinfo",
    ".pytest_cache",
)
TEAM_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def remove(target: Path, dry_run: bool) -> None:
    if not target.exists():
        return
    relative = target.relative_to(ROOT)
    if dry_run:
        print(f"would remove {relative}")
        return
    if target.is_dir():
        shutil.rmtree(target)
    else:
        target.unlink()
    print(f"removed {relative}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Remove generated local workshop artifacts so a team can restart."
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--team-id",
        help="Clean only generated artifacts under reports/teams/TEAM_ID for a shared workshop instance.",
    )
    parser.add_argument(
        "--include-node-modules",
        action="store_true",
        help="Also remove frontend/node_modules for a dependency-clean frontend reset.",
    )
    args = parser.parse_args()
    if args.team_id:
        if not TEAM_ID_PATTERN.fullmatch(args.team_id):
            raise SystemExit("TEAM_ID may contain only letters, numbers, dot, underscore, or hyphen.")
        targets = [f"reports/teams/{args.team_id}"]
    else:
        targets = list(GLOBAL_TARGETS)
    if args.include_node_modules:
        if args.team_id:
            raise SystemExit("--include-node-modules cannot be combined with --team-id.")
        targets.append("frontend/node_modules")
    for relative in targets:
        remove(ROOT / relative, args.dry_run)
    for cache in ROOT.rglob("__pycache__"):
        remove(cache, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
