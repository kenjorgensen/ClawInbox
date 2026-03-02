# Email MCP Server (Hybrid Search + Labels + Security Tiers) — Install + Coding Plan

## Purpose

Build an Email MCP server that can:

- Connect to multiple IMAP inboxes
- Sync/download messages into an internal file store
- Normalize bodies (text/plain preferred, HTML → plain text fallback)
- Cache metadata + body text in SQLite
- Provide:
  - semantic search (vector)
  - keyword search (FTS5)
  - exact match (case-insensitive)
  - label management + message labeling
  - regex-based classification rules for recurring emails
- Support multiple security deployment modes:
  - local stdio (no network)
  - local HTTP + bearer token
  - OAuth 2.1 (remote / multi-user)

This is designed to integrate into OpenClaw as an MCP tool provider (typically wrapped by an OpenClaw skill).

---

## Target Stack

### Core
- Python 3.11+ (3.12 ok)
- `mcp[cli]` (FastMCP server)
- `imapclient` (IMAP)
- `sqlmodel` + SQLite (metadata cache)
- SQLite FTS5 (keyword search)
- `platformdirs` (data/cache dirs)
- `pydantic-settings` (configuration)
- `keyring` (credential storage) + fallback plan if needed
- `html2text` (HTML → plain text)

### Environment
- Use a Python virtual environment (`.venv`) for installing dependencies.

### Vector search
Pick one (start with Chroma for simplest local persistence):
- `chromadb`
- `sentence-transformers` (local embeddings)

Optional later:
- Qdrant (docker) for scale

### Optional utilities
- `pathvalidate` (safe filenames)
- `rapidfuzz` (fuzzy title/sender matching)
- `beautifulsoup4` (fallback HTML text extraction)

---

## Directory Layout (Repo)

```text
email-mcp/
  pyproject.toml
  README.md
  src/
    email_mcp/
      __init__.py
      main.py                 # entrypoint
      settings.py             # pydantic-settings
      logging.py              # stderr logger
      imap_sync.py            # IMAP connect/search/fetch
      normalize.py            # MIME parsing + html->text
      store.py                # .eml file store
      db/
        engine.py
        models.py             # SQLModel tables
        migrate.py            # schema init (incl. FTS5)
        queries.py            # search queries (fts/exact/labels)
      vector/
        embedder.py           # sentence-transformers wrapper
        chroma_store.py       # vector upsert/query
        hybrid.py             # combine fts + semantic
      rules/
        rules_models.py       # regex rule schema
        rules_engine.py       # apply rules to messages
      auth/
        auth_none.py          # for stdio / no auth
        auth_bearer.py        # bearer token (http)
        auth_oauth.py         # oauth hooks (http)
      mcp_tools/
        email_tools.py        # mcp tool funcs
        search_tools.py
        label_tools.py
        rules_tools.py
  tests/
  scripts/
    dev_run_stdio.sh
    dev_run_http.sh
