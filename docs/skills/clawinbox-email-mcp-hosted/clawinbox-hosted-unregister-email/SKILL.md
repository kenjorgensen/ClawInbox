---
name: clawinbox-hosted-unregister-email
description: Unregister an account via hosted MCP tool calls.
---

## What this skill does
Removes an account and optionally purges stored data via MCP.

## When to use
Use when operating purely via the MCP service without CLI access.

## Steps
1. Call MCP tool `unregister_account_tool` with `account_name` and optional `purge`.

## Examples
1. MCP tool `unregister_account_tool` with `{"account_name":"primary"}`
2. MCP tool `unregister_account_tool` with `{"account_name":"primary","purge":true}`

## Notes
1. Without `purge`, the account is disabled and data remains.
