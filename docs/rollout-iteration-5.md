1. Add a script to regenerate the README test table from pytest JSON output.
1. Add CI to run pytest with JSON reporting and fail if README table is stale.
1. Implement expunge detection/resync policy.
1. Implement vector-store cleanup during retention/purge.
1. Add a manual live IMAP smoke test checklist for multi-account pulls.
1. Add account registry via env JSON and OS keyring credential storage.
1. Add access logging for action and result auditing.
1. Add CLI command to register/list accounts and credential status.
1. Add `email-mcp-init` CLI to initialize DB only when missing.
1. Add job tracking for sync operations with status lookup.
1. Fix CLI status/search to invoke internal handlers directly (avoid Tool.call).
1. Standardize CLI output as JSON with structured error payloads.
1. Add agent skill doc with CLI vs MCP gateway guidance.
1. Consolidate account registration into `email-mcp-register` (remove CLI subcommand).
1. Add prefixed env account registry format (e.g. `PRIMARY_EMAIL_MCP_HOST`).
1. Standardize MCP tool outputs as structured JSON objects.
1. Remove IMAP host/user overrides from MCP list/sync tools (registry-only).
1. Add tests for prefixed env parsing and NDJSON list/status outputs.
1. Add config gating for CLI/MCP enablement and store in local config.
1. Add account unregister with optional purge.
1. Add CLI equivalents for all MCP tools.
1. Allow backfill sync when `since_date` is provided (skip UID-only filter).
1. Improve README quick start with explicit CLI and MCP service entrypoints.
1. Add CLI placeholder guidance (PowerShell note) to prevent parser errors.
1. Add integration tests for auth config and multi-account flows.
1. Tag release: `v0.5-iter5`.
