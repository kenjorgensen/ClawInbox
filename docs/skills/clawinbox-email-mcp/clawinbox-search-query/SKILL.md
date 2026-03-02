---
name: email-mcp-search-query
description: Search emails by keyword, label, or semantic/hybrid queries using CLI or MCP tools.
---

## What this skill does
Runs keyword search via CLI and label/semantic search via MCP tools.

## When to use
Use when querying stored messages for retrieval or downstream workflows.

## Steps
1. Keyword search (CLI): `email-mcp-cli search "invoice"`
1. Exact from search (CLI): `email-mcp-cli search-exact me@example.com`
1. Label search (CLI): `email-mcp-cli search-label finance`
1. Semantic/hybrid search (CLI): `email-mcp-cli search-hybrid "quarterly report"`
1. MCP equivalents: `search_messages`, `search_messages_exact`, `search_messages_by_label`, `search_messages_hybrid`

## Examples
1. `email-mcp-cli search "invoice"`
1. `email-mcp-cli search-label finance`
1. MCP tool: `search_messages_hybrid` with `query="quarterly report"`

## Notes
1. Hybrid search requires vector dependencies (`[vector]` extra).
