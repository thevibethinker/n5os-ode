---
created: 2025-12-17
last_edited: 2025-12-17
version: 1.0
provenance: con_XKiLRFt7ycFixjsH
---

# Content Library Consolidation Analysis

## Current State: 3 Databases

### 1. `/home/workspace/N5/data/content_library.db` — **CANONICAL** (111 items)
- Schema: `items` table with `type` (link/snippet)
- 102 links, 9 snippets
- Most recently updated, has the most items
- Used by `N5/scripts/content_library.py` and `content_library_db.py`

### 2. `/home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db` (80 items)
- Schema: `items` table with `item_type` (article/framework/link/snippet/video)
- More complex schema with blocks, topics, relationships
- 15 unique items NOT in canonical db (mostly test articles + some real content)

### 3. `/home/workspace/Personal/Knowledge/ContentLibrary/content-library.db` (16 items) — **LEGACY**
- Schema: `content` table with `source_type` (meeting)
- Contains 16 old meeting references from 2025-09-08
- This is old meeting metadata that predates the current meeting system

## Recommendation

1. **Keep**: `N5/data/content_library.db` as canonical
2. **Migrate**: 15 unique items from v3 → canonical (if valuable)
3. **Quarantine**: Both Personal/Knowledge/ContentLibrary/*.db files
4. **Delete**: After 7-day quarantine if no issues

## Items in v3 NOT in canonical (15 total)
```
article_e2e-ingest-test-article_4cae2c46   (test)
article_summarizer-test-item_7d9b1465     (test)
article_test-article_c250cffc             (test)
builtin_ai-anxiety-higher-education       (real)
cursor_building-with-cursor-public        (real)
... +10 more
```

## Quarantine Plan
- Move to `N5/quarantine/deprecated-content-library/`
- Create manifest with deletion trigger date (7 days out)
- No permanent deletes without V's explicit approval

