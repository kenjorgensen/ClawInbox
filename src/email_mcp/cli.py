from __future__ import annotations

import json

from .registry import list_registered_accounts, register_accounts_from_env
from .settings import Settings


def register_accounts() -> None:
    settings = Settings()
    settings.ensure_dirs()
    count = register_accounts_from_env(settings)
    print(f"Registered {count} accounts.")


def list_accounts() -> None:
    settings = Settings()
    settings.ensure_dirs()
    accounts = list_registered_accounts(settings)
    print(json.dumps(accounts, indent=2))
