from __future__ import annotations

import json
import threading
from typing import Any

import typer

from .db.migrate import is_initialized, migrate
from .main import sync_mailbox_across_accounts
from .mcp_tools.label_tools import (
    apply_label_impl,
    create_label_impl,
    list_labels_impl,
    remove_label_impl,
)
from .mcp_tools.maintenance_tools import purge_messages_impl
from .mcp_tools.rules_tools import (
    apply_rules_to_message_impl,
    create_rule_impl,
    list_rules_impl,
)
from .mcp_tools.search_tools import (
    search_messages_by_label_impl,
    search_messages_exact_impl,
    search_messages_hybrid_impl,
    search_messages_impl,
)
from .mcp_tools.status_tools import job_status_impl, set_sync_enabled_impl, sync_status_impl
from .registry import list_registered_accounts, register_accounts_from_env
from .settings import Settings


app = typer.Typer(add_completion=False)

# Thread-local storage so concurrent test runs don't share output-format state.
_state = threading.local()


@app.callback()
def _global_options(
    json_flag: bool = typer.Option(False, "--json", help="Output results as JSON."),
    ndjson: bool = typer.Option(False, "--ndjson", help="Output results as newline-delimited JSON."),
) -> None:
    _state.json_out = json_flag
    _state.ndjson_out = ndjson


def _out(data: Any) -> None:
    """Print *data* according to the active output-format flags."""
    json_out = getattr(_state, "json_out", False)
    ndjson_out = getattr(_state, "ndjson_out", False)
    if ndjson_out:
        if isinstance(data, list):
            for item in data:
                print(json.dumps(item))
        else:
            print(json.dumps(data))
    elif json_out or isinstance(data, (dict, list)):
        print(json.dumps(data, indent=2))
    else:
        print(data)


@app.command("register")
def register_accounts() -> None:
    settings = Settings()
    settings.ensure_dirs()
    count = register_accounts_from_env(settings)
    _out({"count": count, "message": f"Registered {count} accounts."})


@app.command("register-account")
def register_account(
    name: str,
    host: str,
    user: str,
    credential: str,
) -> None:
    settings = Settings()
    settings.ensure_dirs()
    from .registry import register_account as register_single

    register_single(settings, name=name, host=host, user=user, credential=credential)
    _out({"name": name, "message": f"Registered account {name}."})


@app.command("list")
def list_accounts() -> None:
    settings = Settings()
    settings.ensure_dirs()
    accounts = list_registered_accounts(settings)
    _out(accounts)


@app.command("init")
def init_db() -> None:
    settings = Settings()
    settings.ensure_dirs()
    db_path = settings.data_dir / "email.db"
    if is_initialized(db_path):
        _out({"message": "Database already initialized."})
        return
    migrate(db_path)
    _out({"message": "Database initialized."})


@app.command("list-mailboxes")
def list_mailboxes(account: str | None = None) -> None:
    from .main import _apply_overrides, _hydrate_account_settings
    from .imap_sync import ImapSync

    settings = Settings()
    settings.ensure_dirs()
    _apply_overrides(settings, account_name=account)
    _hydrate_account_settings(settings)
    imap = ImapSync(settings)
    try:
        result = imap.list_mailboxes()
    finally:
        imap.disconnect()
    _out(result)


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
        from .main import _apply_overrides, _sync_mailbox

        _apply_overrides(settings, account_name=account)
        job_id = _sync_mailbox(settings, mailbox, since_date=since_date, before_date=before_date)
        _out({"mailbox": mailbox, "account": account, "job_id": job_id})
        return
    job_ids = sync_mailbox_across_accounts(mailbox, settings, since_date=since_date, before_date=before_date)
    _out({"mailbox": mailbox, "accounts": len(job_ids), "job_ids": job_ids})


@app.command("status")
def status(account: str | None = None) -> None:
    result = sync_status_impl(account)
    _out(result)


@app.command("search")
def search(query: str, limit: int = 20, account: str | None = None) -> None:
    result = search_messages_impl(query, limit=limit, account_name=account)
    _out(result)


@app.command("search-exact")
def search_exact(from_addr: str, account: str | None = None) -> None:
    result = search_messages_exact_impl(from_addr, account_name=account)
    _out(result)


@app.command("search-by-label")
def search_by_label(label: str, account: str | None = None) -> None:
    result = search_messages_by_label_impl(label, account_name=account)
    _out(result)


@app.command("search-hybrid")
def search_hybrid(
    query: str,
    limit: int = 20,
    vector_limit: int = 10,
    account: str | None = None,
) -> None:
    result = search_messages_hybrid_impl(query, limit=limit, vector_limit=vector_limit, account_name=account)
    _out(result)


@app.command("label-create")
def label_create(name: str, account: str | None = None) -> None:
    result = create_label_impl(name, account_name=account)
    _out({"message": result})


@app.command("label-list")
def label_list(account: str | None = None) -> None:
    result = list_labels_impl(account_name=account)
    _out(result)


@app.command("label-apply")
def label_apply(message_id: int, label_name: str, account: str | None = None) -> None:
    result = apply_label_impl(message_id, label_name, account_name=account)
    _out({"message": result})


@app.command("label-remove")
def label_remove(message_id: int, label_name: str, account: str | None = None) -> None:
    result = remove_label_impl(message_id, label_name, account_name=account)
    _out({"message": result})


@app.command("rules-create")
def rules_create(
    name: str,
    field: str,
    pattern: str,
    label: str,
    enabled: bool = True,
    account: str | None = None,
) -> None:
    result = create_rule_impl(name, field, pattern, label, enabled=enabled, account_name=account)
    _out({"message": result})


@app.command("rules-list")
def rules_list(account: str | None = None) -> None:
    result = list_rules_impl(account_name=account)
    _out(result)


@app.command("rules-apply")
def rules_apply(message_id: int, account: str | None = None) -> None:
    result = apply_rules_to_message_impl(message_id, account_name=account)
    _out(result)


@app.command("purge")
def purge(account: str | None = None, label: str | None = None, older_than_days: int | None = None) -> None:
    result = purge_messages_impl(account_name=account, label=label, older_than_days=older_than_days)
    _out({"message": result})


@app.command("set-sync-enabled")
def set_sync_enabled(enabled: bool, account: str | None = None) -> None:
    result = set_sync_enabled_impl(enabled, account)
    _out({"message": result})


@app.command("job-status")
def job_status(job_id: int) -> None:
    result = job_status_impl(job_id)
    _out(result)


def main() -> None:
    app()
