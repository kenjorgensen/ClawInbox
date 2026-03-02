from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .settings import Settings


def log_action(action: str, account: str | None, result: str, details: dict | None = None) -> None:
    settings = Settings()
    settings.ensure_dirs()
    path = settings.data_dir / "access.log"
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "account": account,
        "result": result,
        "details": details or {},
    }
    Path(path).write_text("", encoding="utf-8") if not path.exists() else None
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload) + "\n")
