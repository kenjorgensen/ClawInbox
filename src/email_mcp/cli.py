from __future__ import annotations

import json

import typer

from .db.migrate import is_initialized, migrate
from .main import sync_mailbox_across_accounts
from .mcp_tools.status_tools import sync_status_impl, set_sync_enabled_impl
from .registry import list_registered_accounts, register_accounts_from_env
from .settings import Settings
from .mcp_tools.search_tools import search_messages_impl
from .mcp_tools.label_tools import create_label_impl
from .mcp_tools.rules_tools import create_rule_impl
from .mcp_tools.maintenance_tools import purge_messages_impl


app = typer.Typer(add_completion=False)


@app.command("register")
def register_accounts() -> None:
    settings = Settings()
    settings.ensure_dirs()
    count = register_accounts_from_env(settings)
    print(f"Registered {count} accounts.")


@app.command("list")
def list_accounts() -> None:
    settings = Settings()
    settings.ensure_dirs()
    accounts = list_registered_accounts(settings)
    print(json.dumps(accounts, indent=2))


@app.command("init")
def init_db() -> None:
    settings = Settings()
    settings.ensure_dirs()
    db_path = settings.data_dir / "email.db"
    if is_initialized(db_path):
        print("Database already initialized.")
        return
    migrate(db_path)
    print("Database initialized.")


@app.command("sync")
def sync(
    mailbox: str = "INBOX",
    account: str | None = None,
    since_date: str | None = None,
    before_date: str | None = None,
) -> None:
    settings = Settings()
    settings.ensure_dirs()
    migrate(settings.data_dir / "email.db")
    if account:
        from .main import _sync_mailbox, _apply_overrides

        _apply_overrides(settings, account_name=account)
        _sync_mailbox(settings, mailbox, since_date=since_date, before_date=before_date)
        print(f"Synced {mailbox} for {account}")
        return
    count = sync_mailbox_across_accounts(mailbox, settings, since_date=since_date, before_date=before_date)
    print(f"Synced {mailbox} for {count} accounts")


@app.command("status")
def status(account: str | None = None) -> None:
    result = sync_status_impl(account)
    print(json.dumps(result, indent=2))


@app.command("search")
def search(query: str, account: str | None = None) -> None:
    result = search_messages_impl(query, account_name=account)
    print(json.dumps(result, indent=2))


@app.command("label-create")
def label_create(name: str, account: str | None = None) -> None:
    result = create_label_impl(name, account_name=account)
    print(result)


@app.command("rules-create")
def rules_create(name: str, field: str, pattern: str, label: str, account: str | None = None) -> None:
    result = create_rule_impl(name, field, pattern, label, account_name=account)
    print(result)


@app.command("purge")
def purge(account: str | None = None, label: str | None = None, older_than_days: int | None = None) -> None:
    result = purge_messages_impl(account_name=account, label=label, older_than_days=older_than_days)
    print(result)


@app.command("set-sync-enabled")
def set_sync_enabled(enabled: bool, account: str | None = None) -> None:
    result = set_sync_enabled_impl(enabled, account)
    print(result)


def main() -> None:
    app()
