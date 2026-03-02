1. Initialize repository scaffolding: `pyproject.toml`, `src/email_mcp`, basic package metadata.
1. Implement configuration layer: `settings.py` with pydantic-settings; set data/cache dirs via `platformdirs`.
1. Implement logging: stderr logger with structured formatting in `logging.py`.
1. Build IMAP sync core: connect, list mailboxes, search, fetch headers + full message in `imap_sync.py`.
1. Implement MIME normalization: prefer `text/plain`, HTML fallback to text via `html2text` in `normalize.py`.
1. Create file store: deterministic `.eml` pathing and safe filenames in `store.py`.
1. Implement SQLite schema: SQLModel tables for accounts, mailboxes, messages, labels, and rule metadata in `db/models.py`.
1. Create DB engine/migration: `db/engine.py` and `db/migrate.py` to init tables.
1. Build minimal MCP server: `main.py` with `mcp[cli]` and one or two basic tools (`list_mailboxes`, `sync_inbox`).
1. Add local stdio auth mode: `auth/auth_none.py`.
1. Add smoke tests: basic normalization tests and DB roundtrip.
1. Provide dev scripts: `scripts/dev_run_stdio.sh`.
