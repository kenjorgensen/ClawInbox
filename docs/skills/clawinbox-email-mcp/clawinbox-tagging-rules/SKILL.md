---
name: email-mcp-tagging-rules
description: Create labels and rules for automated tagging.
---

## What this skill does
Creates labels and rules, and applies them to messages.

## When to use
Use when you want structured classification for emails.

## Steps
1. Create label (CLI): `email-mcp-cli label-create LABEL_NAME`
1. Create rule (CLI): `email-mcp-cli rules-create RULE_NAME subject pattern LABEL_NAME`
1. Apply rules (CLI): `email-mcp-cli rules-apply MESSAGE_ID`
1. Apply label (CLI): `email-mcp-cli label-apply MESSAGE_ID LABEL_NAME`
1. Remove label (CLI): `email-mcp-cli label-remove MESSAGE_ID LABEL_NAME`
1. MCP equivalent: `apply_rules_to_message`

## Examples
1. `email-mcp-cli label-create finance`
1. `email-mcp-cli rules-create invoices subject invoice finance`
1. `email-mcp-cli rules-apply 123`

## Notes
1. Rules match against normalized fields like subject/from/to/text.
