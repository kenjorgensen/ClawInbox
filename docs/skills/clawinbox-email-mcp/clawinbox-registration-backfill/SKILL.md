---
name: email-mcp-registration-backfill
description: Register an email account and backfill messages with a date range using CLI and MCP service conventions.
---

## What this skill does
Registers a single account, ensures storage is initialized, and performs a backfill sync with job tracking.

## When to use
Use when onboarding a new mailbox or reloading history into local storage.

## Steps
1. Initialize storage: `email-mcp-init`
2. Register account: `email-mcp-register --name NAME --host HOST --user USER --credential APP_CREDENTIAL`
3. Backfill: `email-mcp-cli sync --mailbox INBOX --since-date 01-Feb-2026`
4. Check job: `email-mcp-cli job-status 123`

## Examples
1. `email-mcp-register --name primary --host imap.gmail.com --user me@gmail.com --credential APP_CREDENTIAL`
2. `email-mcp-cli sync --mailbox INBOX --since-date 01-Feb-2026`

## Notes
1. CLI outputs structured JSON by default; use `--ndjson` for line-delimited output.
2. Backfill ignores UID-only incremental filtering when `--since-date` is provided.
