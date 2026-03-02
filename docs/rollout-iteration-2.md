1. Implement FTS5: create virtual table and triggers in `db/migrate.py`.
1. Add query layer: keyword search, exact match, label filters in `db/queries.py`.
1. Implement label operations: CRUD + apply/remove in `mcp_tools/label_tools.py`.
1. Implement rules engine: regex rules schema and apply flow in `rules/rules_models.py` and `rules/rules_engine.py`.
1. Add rule tools: manage rules and run classification in `mcp_tools/rules_tools.py`.
1. Add vector search: embeddings wrapper and Chroma store in `vector/embedder.py` and `vector/chroma_store.py`.
1. Add optional vector dependencies in `pyproject.toml`.
1. Implement hybrid search: combine FTS + semantic results in `vector/hybrid.py`.
1. Add search tools: `mcp_tools/search_tools.py` exposing hybrid/keyword/exact endpoints.
1. Backfill embeddings on sync: update `imap_sync.py` to enqueue or process embeddings on new messages.
1. Add tests: FTS queries, hybrid ranking, rule classification.
