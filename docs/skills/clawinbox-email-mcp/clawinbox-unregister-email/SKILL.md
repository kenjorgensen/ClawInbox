---
name: email-mcp-unregister-email
description: Remove a registered email account and stored credential (not yet implemented).
---

## What this skill does
Unregisters an account and removes its stored credential, with optional purge of stored emails.

## When to use
Use when you need to stop syncing a mailbox and remove its stored credential.

## Steps
1. Disable account and remove credential: `email-mcp-cli unregister NAME`
1. Optional purge: `email-mcp-cli unregister NAME --purge`

## Examples
1. `email-mcp-cli unregister primary`
1. `email-mcp-cli unregister primary --purge`

## Notes
1. Without `--purge`, the account is disabled and data remains in the DB.
