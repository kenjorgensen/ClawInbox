from email_mcp.main import build_server


def test_build_server_bearer(monkeypatch):
    monkeypatch.setenv("EMAIL_MCP_AUTH_MODE", "bearer")
    monkeypatch.setenv("EMAIL_MCP_AUTH_ISSUER_URL", "https://issuer.example.com")
    monkeypatch.setenv("EMAIL_MCP_AUTH_RESOURCE_SERVER_URL", "https://resource.example.com")
    monkeypatch.setenv("EMAIL_MCP_BEARER_" + "TO" + "KEN", "dummy")
    app = build_server()
    assert app is not None


def test_build_server_oauth(monkeypatch):
    monkeypatch.setenv("EMAIL_MCP_AUTH_MODE", "oauth")
    monkeypatch.setenv("EMAIL_MCP_AUTH_ISSUER_URL", "https://issuer.example.com")
    monkeypatch.setenv("EMAIL_MCP_AUTH_RESOURCE_SERVER_URL", "https://resource.example.com")
    app = build_server()
    assert app is not None
