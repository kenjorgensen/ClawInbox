---
name: clawinbox-hosted-registration-backfill
description: Register and backfill via hosted MCP service using tool calls.
---

## What this skill does
Explains registration and backfill using MCP tools in a hosted service mode.

## When to use
Use when your agent talks to MCP over HTTP or stdio (no CLI).

## Steps
1. Ensure MCP is enabled: `email-mcp-init --enable-mcp`
2. Start MCP service:
2.a Stdio: `.venv\\Scripts\\python -m email_mcp.main`
2.b HTTP: `set EMAIL_MCP_TRANSPORT=streamable-http` then run the same command above
3. Register account (hosted): use `register` CLI once or provision via env; MCP tools assume registry exists.
4. Backfill: call MCP tool `sync_mailbox` with `mailbox="INBOX"` and `since_date="01-Feb-2026"`.
5. Check job: call MCP tool `job_status` with `job_id`.

## Examples
1. MCP tool `sync_mailbox` with `{"mailbox":"INBOX","account_name":"primary","since_date":"01-Feb-2026"}`
2. MCP tool `job_status` with `{"job_id":123}`

## Notes
1. Hosted MCP uses registry + keyring; register accounts before sync.
