---
name: clawinbox-installation
description: Install ClawInbox from GitHub, configure DB, and choose CLI or MCP workflow on init.
---

## What this skill does
Provides a start-to-finish install guide including repo setup, venv, database init, account registration, and gateway choice.

## When to use
Use when setting up a new machine or fresh environment for ClawInbox.

## Steps
1. Clone repo: `git clone https://github.com/kenjorgensen/ClawInbox.git`
1. Create venv: `python -m venv .venv`
1. Install deps: `.venv\\Scripts\\python -m pip install -e .[dev]`
1. Initialize DB and set gateway flags:
1. Enable both: `email-mcp-init`
1. CLI only: `email-mcp-init --enable-cli --disable-mcp`
1. MCP only: `email-mcp-init --disable-cli --enable-mcp`
1. Register account: `email-mcp-register --name NAME --host HOST --user USER --credential APP_CREDENTIAL`
1. Choose a pathway:
1. CLI: `email-mcp-cli sync --mailbox INBOX --since-date 01-Feb-2026`
1. MCP stdio: `.venv\\Scripts\\python -m email_mcp.main`
1. MCP HTTP: `set EMAIL_MCP_TRANSPORT=streamable-http` then run the same command above

## Examples
1. `email-mcp-init --enable-cli --disable-mcp`
1. `email-mcp-register --name primary --host imap.gmail.com --user me@gmail.com --credential APP_CREDENTIAL`
1. `email-mcp-cli sync --mailbox INBOX --since-date 01-Feb-2026`

## Notes
1. CLI and MCP enablement are stored in `config.json` under the data directory.
1. Use `--ndjson` for line-delimited JSON output in CLI commands.
