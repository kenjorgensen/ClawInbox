# ClawInbox Email MCP Server

> WARNING: Beta software. This project has not been security reviewed or stability tested. Use at your own risk.

Email MCP server for syncing IMAP inboxes, normalizing message content, and enabling search and labeling. This is the foundation for hybrid search (FTS + vector), label management, and security tiers described in `Plan.md`.

## Quick Start
1. Create a venv: `python -m venv .venv`
1. Install deps: `.venv\\Scripts\\python -m pip install -e .[dev]`
1. Configure IMAP via environment variables:
   - `EMAIL_MCP_IMAP_HOST`
   - `EMAIL_MCP_IMAP_USER`
   - `EMAIL_MCP_IMAP_PASSWORD`
1. Run: `.venv\\Scripts\\python -m email_mcp.main`

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

## Test Results
- Iteration 1 (2026-03-02): `pytest` -> 2 passed.
- Iteration 2 (2026-03-02): `pytest` -> 5 passed.
