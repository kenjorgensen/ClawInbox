---
name: email-mcp-pull-recent
description: Sync recent messages for one account or all accounts using CLI.
---

## What this skill does
Pulls recent messages into local storage for one account or all registered accounts.

## When to use
Use for daily or periodic syncs after initial registration.

## Steps
1. Sync all accounts: `email-mcp-cli sync --mailbox INBOX --since-date 01-Feb-2026`
1. Sync one account: `email-mcp-cli sync --mailbox INBOX --account ACCOUNT_NAME --since-date 01-Feb-2026`

## Examples
1. `email-mcp-cli sync --mailbox INBOX --since-date 01-Feb-2026`
1. `email-mcp-cli sync --mailbox INBOX --account primary --since-date 01-Feb-2026`

## Notes
1. Use `--before-date` to limit the upper bound of a date range.
1. Job IDs are returned for tracking.
