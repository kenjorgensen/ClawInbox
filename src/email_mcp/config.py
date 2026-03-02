from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .settings import Settings


@dataclass
class ServiceConfig:
    cli_enabled: bool = True
    mcp_enabled: bool = True


def _config_path(settings: Settings) -> Path:
    return settings.data_dir / "config.json"


def load_config(settings: Settings) -> ServiceConfig:
    path = _config_path(settings)
    if not path.exists():
        return ServiceConfig()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return ServiceConfig()
    return ServiceConfig(
        cli_enabled=bool(data.get("cli_enabled", True)),
        mcp_enabled=bool(data.get("mcp_enabled", True)),
    )


def save_config(settings: Settings, config: ServiceConfig) -> None:
    path = _config_path(settings)
    payload = {
        "cli_enabled": config.cli_enabled,
        "mcp_enabled": config.mcp_enabled,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
