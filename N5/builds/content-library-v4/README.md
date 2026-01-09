---
created: 2026-01-09
last_edited: 2026-01-09
version: 1.0
---

# Content Library v4 Redesign

Complete redesign of the Content Library system. Consolidates fragmented storage, fixes broken pipelines, unifies the schema, and connects Zo's save_webpage to N5's knowledge layer.

## Objective

A single, coherent system where: (1) All content lives in one canonical location, (2) All content is tracked in one database, (3) Semantic memory can retrieve content, (4) save_webpage automatically ingests, (5) Documentation matches reality.

## Workers

| ID | Component | Status | Dependencies | Est. Hours |
|----|-----------|--------|--------------|------------|
| worker_schema | database_schema | completed | - | 1h |
| worker_canonical_paths | filesystem_consolidation | completed | - | 1h |
| worker_ingest_script | ingest_pipeline | completed | worker_schema, worker_canonical_paths | 2h |
| worker_backfill | data_migration | completed | worker_schema, worker_canonical_paths, worker_ingest_script | 1h |
| worker_cli_upgrade | cli_interface | completed | worker_schema, worker_ingest_script | 2h |
| worker_semantic_memory | memory_integration | completed | worker_canonical_paths | 1h |
| worker_auto_ingest_hook | automation | completed | worker_ingest_script, worker_canonical_paths | 1h |
| worker_docs_update | documentation | completed | worker_schema, worker_cli_upgrade, worker_semantic_memory | 2h |
| worker_cleanup | cleanup | completed | worker_backfill, worker_docs_update, worker_auto_ingest_hook | 1h |

## Key Decisions

- Canonical storage location: Knowledge/content-library/ (not Personal/Knowledge/ContentLibrary/ or Articles/)
- Single database: N5/data/content_library.db (upgrade in place, don't create v3.db)
- Content types: link, snippet, article, deck, social-post, podcast, video, book, paper, framework, quote
- Auto-ingest: New articles from save_webpage should automatically enter the system
- Semantic profiles: Update n5_memory_client.py to include correct paths
- Archive failed v3: Move N5/builds/content-library-v3/ to quarantine

## Relevant Files

- `N5/data/content_library.db`
- `N5/scripts/content_library.py`
- `N5/cognition/n5_memory_client.py`
- `N5/capabilities/internal/content-library-v3.md`
- `Documents/System/guides/content-library-system.md`
- `Articles/`
- `Knowledge/content-library/`
