# Project State

## Status
- Phase: iteration 2 in progress
- Current iteration: Iteration 2
- Last updated: 2026-03-02

## Scope
Email MCP server with hybrid search, labels, rules, and security tiers.

## Current Progress
- Added FTS5 indexing and search queries.
- Added labels and rules MCP tools.
- Added hybrid ranking utilities and optional vector dependencies.

## Deliverables
- Plan: `Plan.md`
- Rollout iterations: `docs/rollout-iteration-1.md`, `docs/rollout-iteration-2.md`, `docs/rollout-iteration-3.md`
- README: `README.md` (beta warning and quick start)

## Decisions
- Target stack: Python 3.11+, `mcp[cli]`, IMAP via `imapclient`
- Storage: SQLite + FTS5, local file store
- Vector search: start with Chroma + sentence-transformers
- Security tiers: stdio (no auth), HTTP bearer, OAuth 2.1 hooks

## Open Items
- Define schema details and indices
- Define sync semantics (UID tracking, expunges, resync policies)
- Define hybrid ranking strategy
- Confirm embedding lifecycle (sync vs async)
