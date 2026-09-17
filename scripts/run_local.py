from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from local_env import load_env  # noqa: E402


if __name__ == "__main__":
    load_env()
    from constituent_connect.server import main

    main()
