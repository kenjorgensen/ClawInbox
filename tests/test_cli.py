import json

from typer.testing import CliRunner

from email_mcp import cli


runner = CliRunner()


def test_cli_init_db(monkeypatch, tmp_path):
    monkeypatch.setenv("EMAIL_MCP_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("EMAIL_MCP_CACHE_DIR", str(tmp_path / "cache"))
    result = runner.invoke(cli.app, ["init"])
    assert result.exit_code == 0


def test_cli_register_list(monkeypatch, tmp_path):
    monkeypatch.setenv("EMAIL_MCP_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("EMAIL_MCP_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv(
        "EMAIL_MCP_ACCOUNTS_JSON",
        '[{"name":"a","host":"imap.example.com","user":"a@example.com"}]',
    )
    result = runner.invoke(cli.app, ["register"])
    assert result.exit_code == 0
    result = runner.invoke(cli.app, ["list"])
    assert result.exit_code == 0


def test_cli_status(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.sync_status_impl", lambda account: {"account": account, "emails": 0})
    result = runner.invoke(cli.app, ["status"])
    assert result.exit_code == 0


def test_cli_search(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.search_messages_impl", lambda query, limit=20, account_name=None: [])
    result = runner.invoke(cli.app, ["search", "invoice"])
    assert result.exit_code == 0


def test_cli_label_create(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.create_label_impl", lambda name, account_name=None: "ok")
    result = runner.invoke(cli.app, ["label-create", "finance"])
    assert result.exit_code == 0


def test_cli_rules_create(monkeypatch):
    monkeypatch.setattr(
        "email_mcp.cli.create_rule_impl",
        lambda name, field, pattern, label, enabled=True, account_name=None: "ok",
    )
    result = runner.invoke(cli.app, ["rules-create", "r1", "subject", "invoice", "finance"])
    assert result.exit_code == 0


def test_cli_rules_create_with_enabled(monkeypatch):
    monkeypatch.setattr(
        "email_mcp.cli.create_rule_impl",
        lambda name, field, pattern, label, enabled=True, account_name=None: f"Created rule {name} enabled={enabled}",
    )
    result = runner.invoke(cli.app, ["rules-create", "r1", "subject", "invoice", "finance", "--no-enabled"])
    assert result.exit_code == 0


def test_cli_purge(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.purge_messages_impl", lambda account_name=None, label=None, older_than_days=None: "ok")
    result = runner.invoke(cli.app, ["purge"])
    assert result.exit_code == 0


def test_cli_set_sync_enabled(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.set_sync_enabled_impl", lambda enabled, account: "ok")
    result = runner.invoke(cli.app, ["set-sync-enabled", "true"])
    assert result.exit_code == 0


def test_cli_sync(monkeypatch, tmp_path):
    monkeypatch.setenv("EMAIL_MCP_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("EMAIL_MCP_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setattr("email_mcp.main._sync_mailbox", lambda *args, **kwargs: 1)
    result = runner.invoke(cli.app, ["sync", "--mailbox", "INBOX", "--account", "a"])
    assert result.exit_code == 0


# --- New command tests ---

def test_cli_search_exact(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.search_messages_exact_impl", lambda from_addr, account_name=None: [])
    result = runner.invoke(cli.app, ["search-exact", "user@example.com"])
    assert result.exit_code == 0


def test_cli_search_by_label(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.search_messages_by_label_impl", lambda label, account_name=None: [])
    result = runner.invoke(cli.app, ["search-by-label", "finance"])
    assert result.exit_code == 0


def test_cli_search_hybrid(monkeypatch):
    monkeypatch.setattr(
        "email_mcp.cli.search_messages_hybrid_impl",
        lambda query, limit=20, vector_limit=10, account_name=None: [],
    )
    result = runner.invoke(cli.app, ["search-hybrid", "invoice"])
    assert result.exit_code == 0


def test_cli_label_list(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.list_labels_impl", lambda account_name=None: ["finance", "work"])
    result = runner.invoke(cli.app, ["label-list"])
    assert result.exit_code == 0
    assert "finance" in result.output


def test_cli_label_apply(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.apply_label_impl", lambda message_id, label_name, account_name=None: "Applied label")
    result = runner.invoke(cli.app, ["label-apply", "1", "finance"])
    assert result.exit_code == 0


def test_cli_label_remove(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.remove_label_impl", lambda message_id, label_name, account_name=None: "Removed label")
    result = runner.invoke(cli.app, ["label-remove", "1", "finance"])
    assert result.exit_code == 0


def test_cli_rules_list(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.list_rules_impl", lambda account_name=None: ["r1", "r2"])
    result = runner.invoke(cli.app, ["rules-list"])
    assert result.exit_code == 0
    assert "r1" in result.output


def test_cli_rules_apply(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.apply_rules_to_message_impl", lambda message_id, account_name=None: ["finance"])
    result = runner.invoke(cli.app, ["rules-apply", "1"])
    assert result.exit_code == 0


# --- Output format tests ---

def test_cli_json_flag_status(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.sync_status_impl", lambda account: {"account": account, "emails": 5})
    result = runner.invoke(cli.app, ["--json", "status"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["emails"] == 5


def test_cli_ndjson_flag_label_list(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.list_labels_impl", lambda account_name=None: ["finance", "work"])
    result = runner.invoke(cli.app, ["--ndjson", "label-list"])
    assert result.exit_code == 0
    lines = [line for line in result.output.strip().splitlines() if line]
    assert len(lines) == 2
    assert json.loads(lines[0]) == "finance"
    assert json.loads(lines[1]) == "work"


def test_cli_json_flag_label_create(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.create_label_impl", lambda name, account_name=None: "Created label finance")
    result = runner.invoke(cli.app, ["--json", "label-create", "finance"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "message" in data


def test_cli_json_flag_purge(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.purge_messages_impl", lambda account_name=None, label=None, older_than_days=None: "Deleted 3 messages.")
    result = runner.invoke(cli.app, ["--json", "purge"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["message"] == "Deleted 3 messages."


def test_cli_ndjson_flag_search(monkeypatch):
    monkeypatch.setattr(
        "email_mcp.cli.search_messages_impl",
        lambda query, limit=20, account_name=None: [{"id": 1, "subject": "A"}, {"id": 2, "subject": "B"}],
    )
    result = runner.invoke(cli.app, ["--ndjson", "search", "invoice"])
    assert result.exit_code == 0
    lines = [line for line in result.output.strip().splitlines() if line]
    assert len(lines) == 2
    assert json.loads(lines[0])["id"] == 1
    assert json.loads(lines[1])["id"] == 2


def test_cli_json_flag_sync(monkeypatch, tmp_path):
    monkeypatch.setenv("EMAIL_MCP_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("EMAIL_MCP_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setattr("email_mcp.main._sync_mailbox", lambda *args, **kwargs: 42)
    result = runner.invoke(cli.app, ["--json", "sync", "--mailbox", "INBOX", "--account", "a"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["mailbox"] == "INBOX"
    assert data["job_id"] == 42
