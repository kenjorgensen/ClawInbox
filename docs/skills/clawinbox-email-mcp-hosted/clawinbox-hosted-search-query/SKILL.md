---
name: clawinbox-hosted-search-query
description: Search emails via MCP tool calls (keyword, label, semantic).
---

## What this skill does
Searches stored messages using MCP tools.

## When to use
Use when searching through the hosted MCP service.

## Steps
1. Keyword search: MCP tool `search_messages`.
2. Exact sender: MCP tool `search_messages_exact`.
3. Label search: MCP tool `search_messages_by_label`.
4. Semantic/hybrid: MCP tool `search_messages_hybrid`.

## Examples
1. MCP tool `search_messages` with `{"query":"invoice"}`
2. MCP tool `search_messages_by_label` with `{"label":"finance"}`
3. MCP tool `search_messages_hybrid` with `{"query":"quarterly report"}`

## Notes
1. Hybrid search requires vector dependencies (`[vector]`).
