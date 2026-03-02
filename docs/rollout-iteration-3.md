1. Add HTTP server mode with bearer token auth: `auth/auth_bearer.py`, `scripts/dev_run_http.sh`.
1. Implement OAuth 2.1 hooks: `auth/auth_oauth.py` with placeholder integration points and docs.
1. Add multi-account support: multiple IMAP accounts with per-account config and isolation in DB.
1. Implement incremental sync: UID tracking, deleted/expunged handling, and resync policies.
1. Add data retention and purge: remove cached bodies/embeddings by label or date range.
1. Add observability: structured logs for sync, indexing, search latency, and errors.
1. Improve resiliency: retry/backoff, timeouts, and safe cancellation.
1. Add documentation: README with setup, configuration, and example MCP tool usage.
1. Final test pass: integration tests for sync + search + labels + rules.
