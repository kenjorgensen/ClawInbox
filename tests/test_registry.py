from email_mcp.registry import _parse_accounts_from_prefixed_env


def test_parse_accounts_from_prefixed_env_with_multi_prefix():
    values = {
        "MY_WORK_EMAIL_EMAIL_MCP_HOST": "imap.example.com",
        "MY_WORK_EMAIL_EMAIL_MCP_USER": "me@example.com",
        "MY_WORK_EMAIL_EMAIL_MCP_CRED": "cred",
    }
    specs = _parse_accounts_from_prefixed_env(values)
    assert len(specs) == 1
    spec = specs[0]
    assert spec.name == "MY_WORK_EMAIL"
    assert spec.imap_host == "imap.example.com"
    assert spec.imap_user == "me@example.com"
    assert spec.credential_value == "cred"


def test_parse_accounts_from_prefixed_env_with_custom_name_and_port():
    values = {
        "PRIMARY_EMAIL_MCP_NAME": "Primary",
        "PRIMARY_EMAIL_MCP_HOST": "imap.example.com",
        "PRIMARY_EMAIL_MCP_USER": "a@example.com",
        "PRIMARY_EMAIL_MCP_PORT": "993",
    }
    specs = _parse_accounts_from_prefixed_env(values)
    assert len(specs) == 1
    spec = specs[0]
    assert spec.name == "Primary"
    assert spec.imap_port == 993
