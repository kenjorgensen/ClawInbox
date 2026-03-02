# Project State

## Status
- Phase: iteration 5 complete
- Current iteration: Iteration 6
- Last updated: 2026-03-02

## Scope
Email MCP server with hybrid search, labels, rules, and security tiers.

## Current Progress
- Added FTS5 indexing and search queries.
- Added labels and rules MCP tools.
- Added hybrid ranking utilities and optional vector dependencies.
- Added incremental sync (UID tracking) and basic IMAP retries.
- Added HTTP transport settings and bearer/OAuth hooks.
- Added maintenance tool for purging messages.
- Added cross-account operations when `account_name` is omitted.
- Added account registry from env JSON and OS keyring credential storage.
- Added access log for actions and results.
- Added optional resync cleanup to remove local messages missing on server.
- Added integration tests for auth config and multi-account sync.
- Added vector cleanup during purge/resync when vector search is enabled.
- OAuth provider integration deferred to Iteration 6.

## Deliverables
- Plan: `Plan.md`
- Rollout iterations: `docs/rollout-iteration-1.md`, `docs/rollout-iteration-2.md`, `docs/rollout-iteration-3.md`, `docs/rollout-iteration-4.md`, `docs/rollout-iteration-5.md`, `docs/rollout-iteration-6.md`
- README: `README.md` (beta warning and quick start)
- Engineering guide: `docs/engineering-guide.md`
- Live IMAP smoke test: `docs/live-imap-smoke-test.md`

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
- Implement real OAuth provider integration (Iteration 6)
