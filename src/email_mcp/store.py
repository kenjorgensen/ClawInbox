from __future__ import annotations

import re
from pathlib import Path


_SAFE_CHARS = re.compile(r"[^a-zA-Z0-9._-]+")


def _safe_name(value: str) -> str:
    value = value.strip().replace(" ", "_")
    value = _SAFE_CHARS.sub("_", value)
    return value or "unknown"


def store_message(base_dir: Path, account: str, mailbox: str, uid: int, raw: bytes) -> Path:
    account_dir = base_dir / _safe_name(account) / _safe_name(mailbox)
    account_dir.mkdir(parents=True, exist_ok=True)
    path = account_dir / f"{uid}.eml"
    path.write_bytes(raw)
    return path
