from __future__ import annotations

import json
import os

import typer

from .config import ServiceConfig, load_config, save_config
from .db.migrate import is_initialized, migrate
from .main import list_mailboxes_impl, sync_mailbox_across_accounts
from .mcp_tools.label_tools import apply_label_impl, create_label_impl, list_labels_impl, remove_label_impl
from .mcp_tools.maintenance_tools import purge_messages_impl
from .mcp_tools.rules_tools import apply_rules_to_message_impl, create_rule_impl, list_rules_impl
from .mcp_tools.search_tools import (
    search_messages_by_label_impl,
    search_messages_exact_impl,
    search_messages_hybrid_impl,
    search_messages_impl,
)
from .mcp_tools.status_tools import job_status_impl, set_sync_enabled_impl, sync_status_impl
from .registry import list_registered_accounts, register_accounts_from_env, unregister_account
from .settings import Settings


app = typer.Typer(add_completion=False)

OUTPUT_MODE = "text"


@app.callback()
def configure_output(
    ctx: typer.Context,
    json_flag: bool = typer.Option(False, "--json", help="Output JSON (default)."),
    ndjson: bool = typer.Option(False, "--ndjson", help="Output NDJSON (one JSON object per line)."),
) -> None:
    global OUTPUT_MODE
    if json_flag and ndjson:
        raise typer.BadParameter("Choose only one of --json or --ndjson.")
    if ndjson:
        OUTPUT_MODE = "ndjson"
    elif json_flag:
        OUTPUT_MODE = "json"
    else:
        OUTPUT_MODE = "text"
    ctx.ensure_object(dict)
    ctx.obj["output_mode"] = OUTPUT_MODE
    settings = Settings()
    settings.ensure_dirs()
    config = load_config(settings)
    if ctx.invoked_subcommand != "init" and not config.cli_enabled:
        _print_json({"status": "error", "message": "CLI is disabled by config."})
        raise typer.Exit(2)


def _ndjson_lines(payload: object) -> list[str]:
    if isinstance(payload, list):
        return [json.dumps(item) for item in payload]
    if not isinstance(payload, dict):
        return [json.dumps(payload)]
    list_keys = [key for key, value in payload.items() if isinstance(value, list)]
    if list_keys:
        key = next((k for k in list_keys if k in {"data", "accounts", "job_ids", "results"}), list_keys[0])
        meta = {k: v for k, v in payload.items() if k != key}
        lines = []
        for item in payload[key]:
            lines.append(json.dumps({**meta, key: item}))
        return lines or [json.dumps(meta)]
    return [json.dumps(payload)]


def _print_text(payload: object) -> None:
    if isinstance(payload, dict):
        if "message" in payload and isinstance(payload["message"], str):
            print(payload["message"])
            return
        if "result" in payload and isinstance(payload["result"], str):
            print(payload["result"])
            return
        for key, value in payload.items():
            if isinstance(value, list):
                print(f"{key}:")
                _print_text(value)
            else:
                print(f"{key}={value}")
        return
    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict):
                parts = [f"{key}={value}" for key, value in item.items()]
                print(", ".join(parts))
            else:
                print(item)
        return
    print(payload)


def _print_json(payload: dict) -> None:
    if OUTPUT_MODE == "text":
        _print_text(payload)
        return
    if OUTPUT_MODE == "ndjson":
        for line in _ndjson_lines(payload):
            print(line)
        return
    print(json.dumps(payload, indent=2))


def _error_payload(exc: Exception) -> dict:
    payload = {"status": "error", "error_type": type(exc).__name__}
    if os.getenv("EMAIL_MCP_DEBUG_ERRORS", "").strip().lower() in {"1", "true", "yes"}:
        payload["message"] = str(exc)
    else:
        payload["message"] = "Operation failed. See logs for details."
    return payload


@app.command("register")
def register_accounts(
    name: str | None = None,
    host: str | None = None,
    user: str | None = None,
    credential: str | None = None,
) -> None:
    settings = Settings()
    settings.ensure_dirs()
    if any([name, host, user, credential]):
        if not all([name, host, user, credential]):
            raise typer.BadParameter("Provide name, host, user, and credential together.")
        from .registry import register_account as register_single

        register_single(settings, name=name, host=host, user=user, credential=credential)
        _print_json({"status": "ok", "account": name})
        return
    count = register_accounts_from_env(settings)
    _print_json({"status": "ok", "registered": count})


@app.command("list")
def list_accounts() -> None:
    settings = Settings()
    settings.ensure_dirs()
    accounts = list_registered_accounts(settings)
    _print_json({"status": "ok", "accounts": accounts})


@app.command("init")
def init_db(
    enable_cli: bool = typer.Option(False, "--enable-cli", help="Enable CLI usage."),
    disable_cli: bool = typer.Option(False, "--disable-cli", help="Disable CLI usage."),
    enable_mcp: bool = typer.Option(False, "--enable-mcp", help="Enable MCP service."),
    disable_mcp: bool = typer.Option(False, "--disable-mcp", help="Disable MCP service."),
) -> None:
    settings = Settings()
    settings.ensure_dirs()
    db_path = settings.data_dir / "email.db"
    config = load_config(settings)
    if enable_cli and disable_cli:
        raise typer.BadParameter("Choose only one of --enable-cli or --disable-cli.")
    if enable_mcp and disable_mcp:
        raise typer.BadParameter("Choose only one of --enable-mcp or --disable-mcp.")
    cli_enabled = config.cli_enabled if not (enable_cli or disable_cli) else enable_cli
    if disable_cli:
        cli_enabled = False
    mcp_enabled = config.mcp_enabled if not (enable_mcp or disable_mcp) else enable_mcp
    if disable_mcp:
        mcp_enabled = False
    was_initialized = is_initialized(db_path)
    if not was_initialized:
        migrate(db_path)
    config = ServiceConfig(cli_enabled=cli_enabled, mcp_enabled=mcp_enabled)
    save_config(settings, config)
    _print_json(
        {
            "status": "ok",
            "initialized": True,
            "message": "Database initialized." if not was_initialized else "Database already initialized.",
            "cli_enabled": config.cli_enabled,
            "mcp_enabled": config.mcp_enabled,
        }
    )


@app.command("list-mailboxes")
def list_mailboxes(account: str | None = None) -> None:
    result = list_mailboxes_impl(account)
    _print_json(result)


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
        _print_json({"status": "ok", "mailbox": mailbox, "account": account, "job_id": job_id})
        return
    job_ids = sync_mailbox_across_accounts(mailbox, settings, since_date=since_date, before_date=before_date)
    _print_json({"status": "ok", "mailbox": mailbox, "accounts": len(job_ids), "job_ids": job_ids})


@app.command("status")
def status(account: str | None = None) -> None:
    result = sync_status_impl(account)
    _print_json({"status": "ok", "data": result})


@app.command("search")
def search(query: str, limit: int = 20, account: str | None = None) -> None:
    result = search_messages_impl(query, limit=limit, account_name=account)
    _print_json({"status": "ok", "data": result})


@app.command("search-exact")
def search_exact(from_addr: str, account: str | None = None) -> None:
    result = search_messages_exact_impl(from_addr, account_name=account)
    _print_json({"status": "ok", "data": result})


@app.command("search-label")
def search_label(label: str, account: str | None = None) -> None:
    result = search_messages_by_label_impl(label, account_name=account)
    _print_json({"status": "ok", "data": result})


@app.command("search-by-label")
def search_by_label(label: str, account: str | None = None) -> None:
    search_label(label, account)


@app.command("search-hybrid")
def search_hybrid(
    query: str,
    limit: int = 20,
    vector_limit: int = 10,
    account: str | None = None,
) -> None:
    result = search_messages_hybrid_impl(query, limit=limit, vector_limit=vector_limit, account_name=account)
    _print_json({"status": "ok", "data": result})


@app.command("label-create")
def label_create(name: str, account: str | None = None) -> None:
    result = create_label_impl(name, account_name=account)
    _print_json({"status": "ok", "result": result})


@app.command("label-list")
def label_list(account: str | None = None) -> None:
    result = list_labels_impl(account_name=account)
    _print_json({"status": "ok", "data": result})


@app.command("label-apply")
def label_apply(message_id: int, label_name: str, account: str | None = None) -> None:
    result = apply_label_impl(message_id, label_name, account_name=account)
    _print_json({"status": "ok", "result": result})


@app.command("label-remove")
def label_remove(message_id: int, label_name: str, account: str | None = None) -> None:
    result = remove_label_impl(message_id, label_name, account_name=account)
    _print_json({"status": "ok", "result": result})


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
    _print_json({"status": "ok", "result": result})


@app.command("rules-list")
def rules_list(account: str | None = None) -> None:
    result = list_rules_impl(account_name=account)
    _print_json({"status": "ok", "data": result})


@app.command("rules-apply")
def rules_apply(message_id: int, account: str | None = None) -> None:
    result = apply_rules_to_message_impl(message_id, account_name=account)
    _print_json({"status": "ok", "data": result})


@app.command("purge")
def purge(account: str | None = None, label: str | None = None, older_than_days: int | None = None) -> None:
    result = purge_messages_impl(account_name=account, label=label, older_than_days=older_than_days)
    _print_json({"status": "ok", "result": result})


@app.command("set-sync-enabled")
def set_sync_enabled(enabled: bool, account: str | None = None) -> None:
    result = set_sync_enabled_impl(enabled, account)
    _print_json({"status": "ok", "result": result})


@app.command("job-status")
def job_status(job_id: int) -> None:
    result = job_status_impl(job_id)
    _print_json({"status": "ok", "data": result})


@app.command("unregister")
def unregister(name: str, purge: bool = False) -> None:
    settings = Settings()
    settings.ensure_dirs()
    result = unregister_account(settings, name=name, purge=purge)
    _print_json({"status": "ok", "result": result})


def main() -> None:
    try:
        app()
    except typer.Exit:
        raise
    except Exception as exc:
        _print_json(_error_payload(exc))
        raise SystemExit(1)
