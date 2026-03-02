---
name: clawinbox-hosted-tagging-rules
description: Manage labels and rules via MCP tool calls.
---

## What this skill does
Creates labels, manages rules, and applies labels via MCP tools.

## When to use
Use when managing labels and rules through hosted MCP.

## Steps
1. Create label: MCP tool `create_label`.
2. List labels: MCP tool `list_labels`.
3. Apply label: MCP tool `apply_label`.
4. Remove label: MCP tool `remove_label`.
5. Create rule: MCP tool `create_rule`.
6. List rules: MCP tool `list_rules`.
7. Apply rules: MCP tool `apply_rules_to_message`.

## Examples
1. MCP tool `create_label` with `{"name":"finance"}`
2. MCP tool `create_rule` with `{"name":"invoices","field":"subject","pattern":"invoice","label":"finance"}`
3. MCP tool `apply_rules_to_message` with `{"message_id":123}`

## Notes
1. Rules operate on normalized message fields.
