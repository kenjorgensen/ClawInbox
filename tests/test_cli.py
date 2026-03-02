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
    monkeypatch.setattr("email_mcp.cli.search_messages_impl", lambda query, account_name=None: [])
    result = runner.invoke(cli.app, ["search", "invoice"])
    assert result.exit_code == 0


def test_cli_label_create(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.create_label_impl", lambda name, account_name=None: "ok")
    result = runner.invoke(cli.app, ["label-create", "finance"])
    assert result.exit_code == 0


def test_cli_rules_create(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.create_rule_impl", lambda name, field, pattern, label, account_name=None: "ok")
    result = runner.invoke(cli.app, ["rules-create", "r1", "subject", "invoice", "finance"])
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
