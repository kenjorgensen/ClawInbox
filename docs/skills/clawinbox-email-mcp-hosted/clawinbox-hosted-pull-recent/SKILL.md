---
name: clawinbox-hosted-pull-recent
description: Pull recent emails via MCP tool calls.
---

## What this skill does
Runs a sync for one account or all accounts via MCP.

## When to use
Use when operating via hosted MCP instead of CLI.

## Steps
1. Call MCP tool `sync_mailbox` with `mailbox="INBOX"` and `since_date`.
2. For a single account, include `account_name`.

## Examples
1. MCP tool `sync_mailbox` with `{"mailbox":"INBOX","since_date":"01-Feb-2026"}`
2. MCP tool `sync_mailbox` with `{"mailbox":"INBOX","account_name":"primary","since_date":"01-Feb-2026"}`

## Notes
1. Use `before_date` to bound the sync range.
