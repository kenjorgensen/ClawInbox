# ClawInbox Email MCP Server

> WARNING: Beta software. This project has not been security reviewed or stability tested. Use at your own risk.

Email MCP server for syncing IMAP inboxes, normalizing message content, and enabling search and labeling. This is the foundation for hybrid search (FTS + vector), label management, and security tiers described in `Plan.md`.

## Quick Start
1. Create a venv: `python -m venv .venv`
1. Install deps: `.venv\\Scripts\\python -m pip install -e .[dev]`
1. Optional vector deps: `.venv\\Scripts\\python -m pip install -e .[dev,vector]`
1. Configure accounts via env: `EMAIL_MCP_ACCOUNTS_JSON` (see Account Registry).
1. Initialize the DB: `email-mcp-init`
1. Register accounts from env: `email-mcp-register`
1. Register one account manually: `email-mcp-register --name NAME --host HOST --user USER --credential APP_CREDENTIAL`
1. CLI entrypoint: `.venv\\Scripts\\email-mcp-cli --help` (or `email-mcp-cli --help` if your venv is active)
1. MCP service entrypoint (stdio): `.venv\\Scripts\\python -m email_mcp.main`
1. MCP service entrypoint (HTTP): `set EMAIL_MCP_TRANSPORT=streamable-http` then run the same command above

PowerShell note: avoid angle-bracket placeholders like `<job_id>`; use a literal value, e.g. `email-mcp-cli job-status 123`.

## CLI Output
1. CLI commands return JSON with a top-level `status` field.
1. Set `EMAIL_MCP_DEBUG_ERRORS=true` to include error details in JSON output.
1. Use `--ndjson` to emit one JSON object per line (NDJSON).

## Service Config
1. `email-mcp-init` writes a local `config.json` under the data directory.
1. Use `email-mcp-init --enable-cli/--disable-cli` and `--enable-mcp/--disable-mcp` to control pathways.

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
1. Pass `account_name` to tool calls (optional). If omitted, operations apply across all accounts when supported.
1. Sync uses registered accounts and loads credentials from the OS keyring.
1. Example: `sync_mailbox("INBOX", account_name="primary")`
1. Optional date filtering: use `since_date` (required) and `before_date` (optional) in IMAP `DD-Mon-YYYY` format.
1. Cross-account searches include an `account` field in results.
1. If `since_date` is provided, UID-based incremental sync is bypassed to allow backfill.
1. Optional resync cleanup: set `EMAIL_MCP_RESYNC_MISSING=true` to remove local messages that no longer exist on the server.

## Account Registry
1. Register accounts from env JSON by setting `EMAIL_MCP_ACCOUNTS_JSON`.
1. Each entry supports `name`, `host`, `user`, optional `port`, and optional `credential_env` for the IMAP credential.
1. Alternative env format: use per-account prefixes with `_EMAIL_MCP_*` suffixes.
1. Disable automatic registration with `EMAIL_MCP_REGISTER_ACCOUNTS=false`.
1. Credentials are stored in the OS keyring and loaded at runtime.
1. CLI: `email-mcp-init` (init DB), `email-mcp-register` (register from env), `email-mcp-list` (list accounts + credential status).
1. Full CLI entrypoint: `email-mcp-cli` (run `email-mcp-cli --help` for subcommands).

Example JSON (single line):
`[{"name":"primary","host":"imap.gmail.com","user":"me@gmail.com","credential_env":"EMAIL_MCP_CRED_PRIMARY"}]`

Example prefixed env:
1. `PRIMARY_EMAIL_MCP_HOST=imap.gmail.com`
1. `PRIMARY_EMAIL_MCP_USER=me@gmail.com`
1. `PRIMARY_EMAIL_MCP_CRED=...`
1. Optional: `PRIMARY_EMAIL_MCP_NAME=Primary`
1. Optional: `PRIMARY_EMAIL_MCP_PORT=993`

## Access Log
1. Writes JSON lines to `access.log` under the data directory.
1. Logs action, account, result, and minimal details.

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
- `sync_status`
- `set_sync_enabled`
- `job_status`
- `unregister_account_tool`

## Test Results
Generated from pytest JSON report.

<!-- TEST_TABLE_START -->
| Category | Test | Pass? |
| --- | --- | --- |
| CLI | Cli Init Db | Yes |
| CLI | Cli Label Apply Remove | Yes |
| CLI | Cli Label Create | Yes |
| CLI | Cli Label List | Yes |
| CLI | Cli List Mailboxes | Yes |
| CLI | Cli Ndjson List | Yes |
| CLI | Cli Ndjson List Output | Yes |
| CLI | Cli Ndjson Status Output | Yes |
| CLI | Cli Purge | Yes |
| CLI | Cli Register From Prefixed Env | Yes |
| CLI | Cli Register List | Yes |
| CLI | Cli Register Manual | Yes |
| CLI | Cli Rules Create | Yes |
| CLI | Cli Rules List Apply | Yes |
| CLI | Cli Search | Yes |
| CLI | Cli Search Exact | Yes |
| CLI | Cli Search Hybrid | Yes |
| CLI | Cli Search Label | Yes |
| CLI | Cli Set Sync Enabled | Yes |
| CLI | Cli Status | Yes |
| CLI | Cli Sync | Yes |
| CLI | Cli Unregister | Yes |
| Database | Account Defaults | Yes |
| Database | Db Roundtrip | Yes |
| IMAP | Imap Connect Missing Settings | Yes |
| IMAP | Imap Fetch Builds Criteria | Yes |
| Integration | Build Server Bearer | Yes |
| Integration | Build Server Oauth | Yes |
| Integration | Sync Across Accounts | Yes |
| Maintenance | Delete Messages By Uids | Yes |
| Maintenance | Purge Messages | Yes |
| Maintenance | Purge Messages No Label Match | Yes |
| Normalization | Normalize Plain Text | Yes |
| Normalization | Normalize Property | Yes |
| Other | Parse Accounts From Prefixed Env With Custom Name And Port | Yes |
| Other | Parse Accounts From Prefixed Env With Multi Prefix | Yes |
| Rules | Rules Apply | Yes |
| Rules | Rules Disabled | Yes |
| Search | Fts No Results | Yes |
| Search | Fts Search | Yes |
| Search | Hybrid Rank Combines | Yes |
| Settings | Settings Ensure Dirs | Yes |
| Settings | Settings Resolved Store Dir | Yes |
| Status | Set Sync Enabled All Accounts | Yes |
| Status | Sync Status All Accounts | Yes |
| Storage | Store Message | Yes |
| Storage | Store Sanitizes Names | Yes |
<!-- TEST_TABLE_END -->

## Engineering Guide
See `docs/engineering-guide.md` for general process and project-specific notes.
