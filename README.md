# ClawInbox Email MCP Server

> WARNING: Beta software. This project has not been security reviewed or stability tested. Use at your own risk.

Email MCP server for syncing IMAP inboxes, normalizing message content, and enabling search and labeling. This is the foundation for hybrid search (FTS + vector), label management, and security tiers described in `Plan.md`.

## Quick Start
1. Create a venv: `python -m venv .venv`
1. Install deps: `.venv\\Scripts\\python -m pip install -e .[dev]`
1. Optional vector deps: `.venv\\Scripts\\python -m pip install -e .[dev,vector]`
1. Configure IMAP via env: `EMAIL_MCP_IMAP_HOST`, `EMAIL_MCP_IMAP_USER`, `EMAIL_MCP_IMAP_PASSWORD`
1. Run: `.venv\\Scripts\\python -m email_mcp.main`

## HTTP Transport
1. Set `EMAIL_MCP_TRANSPORT=streamable-http`
1. Optional: `EMAIL_MCP_HTTP_HOST` and `EMAIL_MCP_HTTP_PORT`
1. Run: `.venv\\Scripts\\python -m email_mcp.main`

## Auth Modes
1. None (default): `EMAIL_MCP_AUTH_MODE=none`
1. Bearer:
1. `EMAIL_MCP_AUTH_MODE=bearer`
1. `EMAIL_MCP_BEARER_TOKEN=...`
1. `EMAIL_MCP_AUTH_ISSUER_URL=...`
1. `EMAIL_MCP_AUTH_RESOURCE_SERVER_URL=...`
1. OAuth (hooks only):
1. `EMAIL_MCP_AUTH_MODE=oauth`
1. `EMAIL_MCP_AUTH_ISSUER_URL=...`
1. `EMAIL_MCP_AUTH_RESOURCE_SERVER_URL=...`

## Multi-Account
1. Pass `account_name` to tool calls.
1. For sync, pass `account_name`, `imap_host`, `imap_user`, and `imap_password`.

## MCP Tools (Current)
- `list_mailboxes`
- `sync_mailbox`
- `search_messages`
- `search_messages_exact`
- `search_messages_by_label`
- `search_messages_hybrid`
- `create_label`
- `list_labels`
- `apply_label`
- `remove_label`
- `create_rule`
- `list_rules`
- `apply_rules_to_message`
- `purge_messages`

## Test Results
- Iteration 1 (2026-03-02): `pytest` -> 2 passed.
- Iteration 2 (2026-03-02): `pytest` -> 5 passed.
- Iteration 3 (2026-03-02): `pytest` -> 6 passed.
