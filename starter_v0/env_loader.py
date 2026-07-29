from __future__ import annotations

import os
from pathlib import Path


def load_dotenv(path: Path, *, override: bool = True) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if key and (override or key not in os.environ):
            os.environ[key] = value


def load_lab_env(root: Path) -> None:
    external_path = os.getenv("DAY04_ENV_FILE")
    if external_path:
        load_dotenv(Path(external_path).expanduser())
        return
    local_env = root / ".env"
    if local_env.exists():
        load_dotenv(local_env)
        return

    # The submitted app lives in ``starter_v0`` while workshop users often keep
    # one shared, gitignored .env at the repository root. Supporting that layout
    # avoids copying secrets and keeps the local starter contract intact.
    load_dotenv(root.parent / ".env")
