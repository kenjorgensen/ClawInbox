import json

from typer.testing import CliRunner

from email_mcp import cli


runner = CliRunner()


def test_cli_disabled_by_config(monkeypatch, tmp_path):
    monkeypatch.setenv("EMAIL_MCP_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("EMAIL_MCP_CACHE_DIR", str(tmp_path / "cache"))
    config_path = tmp_path / "config.json"
    config_path.write_text('{"cli_enabled": false, "mcp_enabled": true}', encoding="utf-8")
    result = runner.invoke(cli.app, ["status"])
    assert result.exit_code == 2


def test_cli_init_db(monkeypatch, tmp_path):
    monkeypatch.setenv("EMAIL_MCP_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("EMAIL_MCP_CACHE_DIR", str(tmp_path / "cache"))
    result = runner.invoke(cli.app, ["--json", "init"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"


def test_cli_register_list(monkeypatch, tmp_path):
    monkeypatch.setenv("EMAIL_MCP_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("EMAIL_MCP_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv(
        "EMAIL_MCP_ACCOUNTS_JSON",
        '[{"name":"a","host":"imap.example.com","user":"a@example.com"}]',
    )
    result = runner.invoke(cli.app, ["--json", "register"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"
    result = runner.invoke(cli.app, ["--json", "list"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"
    assert isinstance(payload["accounts"], list)


def test_cli_register_manual(monkeypatch, tmp_path):
    monkeypatch.setenv("EMAIL_MCP_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("EMAIL_MCP_CACHE_DIR", str(tmp_path / "cache"))
    called = {}

    def fake_register(settings, name, host, user, credential):
        called["name"] = name
        called["host"] = host
        called["user"] = user
        called["credential"] = credential

    monkeypatch.setattr("email_mcp.registry.register_account", fake_register)
    result = runner.invoke(
        cli.app,
        [
            "--json",
            "register",
            "--name",
            "primary",
            "--host",
            "imap.example.com",
            "--user",
            "a@example.com",
            "--credential",
            "cred",
        ],
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"
    assert called["name"] == "primary"


def test_cli_status(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.sync_status_impl", lambda account: {"account": account, "emails": 0})
    result = runner.invoke(cli.app, ["--json", "status"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"


def test_cli_search(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.search_messages_impl", lambda query, limit=20, account_name=None: [])
    result = runner.invoke(cli.app, ["--json", "search", "invoice"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"


def test_cli_search_exact(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.search_messages_exact_impl", lambda from_addr, account_name=None: [])
    result = runner.invoke(cli.app, ["--json", "search-exact", "me@example.com"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"


def test_cli_search_label(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.search_messages_by_label_impl", lambda label, account_name=None: [])
    result = runner.invoke(cli.app, ["--json", "search-label", "finance"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"


def test_cli_search_by_label_alias(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.search_messages_by_label_impl", lambda label, account_name=None: [])
    result = runner.invoke(cli.app, ["search-by-label", "finance"])
    assert result.exit_code == 0


def test_cli_search_hybrid(monkeypatch):
    monkeypatch.setattr(
        "email_mcp.cli.search_messages_hybrid_impl",
        lambda query, limit=20, vector_limit=10, account_name=None: [],
    )
    result = runner.invoke(cli.app, ["--json", "search-hybrid", "invoice"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"


def test_cli_label_create(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.create_label_impl", lambda name, account_name=None: "ok")
    result = runner.invoke(cli.app, ["--json", "label-create", "finance"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"


def test_cli_label_list(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.list_labels_impl", lambda account_name=None: ["finance"])
    result = runner.invoke(cli.app, ["--json", "label-list"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"


def test_cli_label_apply_remove(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.apply_label_impl", lambda message_id, label_name, account_name=None: "ok")
    monkeypatch.setattr("email_mcp.cli.remove_label_impl", lambda message_id, label_name, account_name=None: "ok")
    result = runner.invoke(cli.app, ["label-apply", "1", "finance"])
    assert result.exit_code == 0
    result = runner.invoke(cli.app, ["label-remove", "1", "finance"])
    assert result.exit_code == 0


def test_cli_rules_create(monkeypatch):
    monkeypatch.setattr(
        "email_mcp.cli.create_rule_impl",
        lambda name, field, pattern, label, enabled=True, account_name=None: "ok",
    )
    result = runner.invoke(cli.app, ["--json", "rules-create", "r1", "subject", "invoice", "finance"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"


def test_cli_rules_list_apply(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.list_rules_impl", lambda account_name=None: ["r1"])
    monkeypatch.setattr("email_mcp.cli.apply_rules_to_message_impl", lambda message_id, account_name=None: ["finance"])
    result = runner.invoke(cli.app, ["rules-list"])
    assert result.exit_code == 0
    result = runner.invoke(cli.app, ["rules-apply", "1"])
    assert result.exit_code == 0


def test_cli_purge(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.purge_messages_impl", lambda account_name=None, label=None, older_than_days=None: "ok")
    result = runner.invoke(cli.app, ["--json", "purge"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"


def test_cli_set_sync_enabled(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.set_sync_enabled_impl", lambda enabled, account: "ok")
    result = runner.invoke(cli.app, ["--json", "set-sync-enabled", "true"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"


def test_cli_sync(monkeypatch, tmp_path):
    monkeypatch.setenv("EMAIL_MCP_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("EMAIL_MCP_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setattr("email_mcp.main._sync_mailbox", lambda *args, **kwargs: 1)
    result = runner.invoke(cli.app, ["--json", "sync", "--mailbox", "INBOX", "--account", "a"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"


def test_cli_job_status(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.job_status_impl", lambda job_id: {"job_id": job_id})
    result = runner.invoke(cli.app, ["--json", "job-status", "1"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"


def test_cli_unregister(monkeypatch, tmp_path):
    monkeypatch.setenv("EMAIL_MCP_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("EMAIL_MCP_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setattr("email_mcp.cli.unregister_account", lambda settings, name, purge=False: {"removed": True})
    result = runner.invoke(cli.app, ["--json", "unregister", "--purge", "name"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"


def test_cli_ndjson_list(monkeypatch, tmp_path):
    monkeypatch.setenv("EMAIL_MCP_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("EMAIL_MCP_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv(
        "EMAIL_MCP_ACCOUNTS_JSON",
        '[{"name":"a","host":"imap.example.com","user":"a@example.com"}, {"name":"b","host":"imap.example.com","user":"b@example.com"}]',
    )
    result = runner.invoke(cli.app, ["--ndjson", "register"])
    assert result.exit_code == 0
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["status"] == "ok"


def test_cli_ndjson_list_output(monkeypatch, tmp_path):
    monkeypatch.setenv("EMAIL_MCP_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("EMAIL_MCP_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv(
        "EMAIL_MCP_ACCOUNTS_JSON",
        '[{"name":"a","host":"imap.example.com","user":"a@example.com"}, {"name":"b","host":"imap.example.com","user":"b@example.com"}]',
    )
    runner.invoke(cli.app, ["register"])
    result = runner.invoke(cli.app, ["--ndjson", "list"])
    assert result.exit_code == 0
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert len(lines) == 2
    payloads = [json.loads(line) for line in lines]
    assert all(payload["status"] == "ok" for payload in payloads)


def test_cli_ndjson_status_output(monkeypatch):
    monkeypatch.setattr("email_mcp.cli.sync_status_impl", lambda account: [{"account": "a", "emails": 0}])
    result = runner.invoke(cli.app, ["--ndjson", "status"])
    assert result.exit_code == 0
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["status"] == "ok"
