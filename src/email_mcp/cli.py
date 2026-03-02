from __future__ import annotations

import json

import typer

from .db.migrate import is_initialized, migrate
from .main import build_server, sync_mailbox_across_accounts
from .mcp_tools.status_tools import register_status_tools
from .registry import list_registered_accounts, register_accounts_from_env
from .settings import Settings
from .mcp_tools.search_tools import register_search_tools
from .mcp_tools.label_tools import register_label_tools
from .mcp_tools.rules_tools import register_rules_tools
from .mcp_tools.maintenance_tools import register_maintenance_tools


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
    server = build_server()
    register_status_tools(server)
    status_tool = server._tool_manager.get_tool("sync_status")  # type: ignore[attr-defined]
    result = status_tool.call(account_name=account)  # type: ignore[call-arg]
    print(json.dumps(result, indent=2))


@app.command("search")
def search(query: str, account: str | None = None) -> None:
    server = build_server()
    register_search_tools(server)
    tool = server._tool_manager.get_tool("search_messages")  # type: ignore[attr-defined]
    result = tool.call(query=query, account_name=account)  # type: ignore[call-arg]
    print(json.dumps(result, indent=2))


@app.command("label-create")
def label_create(name: str, account: str | None = None) -> None:
    server = build_server()
    register_label_tools(server)
    tool = server._tool_manager.get_tool("create_label")  # type: ignore[attr-defined]
    result = tool.call(name=name, account_name=account)  # type: ignore[call-arg]
    print(result)


@app.command("rules-create")
def rules_create(name: str, field: str, pattern: str, label: str, account: str | None = None) -> None:
    server = build_server()
    register_rules_tools(server)
    tool = server._tool_manager.get_tool("create_rule")  # type: ignore[attr-defined]
    result = tool.call(name=name, field=field, pattern=pattern, label=label, account_name=account)  # type: ignore[call-arg]
    print(result)


@app.command("purge")
def purge(account: str | None = None, label: str | None = None, older_than_days: int | None = None) -> None:
    server = build_server()
    register_maintenance_tools(server)
    tool = server._tool_manager.get_tool("purge_messages")  # type: ignore[attr-defined]
    result = tool.call(account_name=account, label=label, older_than_days=older_than_days)  # type: ignore[call-arg]
    print(result)


def main() -> None:
    app()
