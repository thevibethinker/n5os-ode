---
created: 2025-12-02
last_edited: 2025-12-17
version: 1.0
capability_id: content-library-v3
name: Content Library v3 (Unified)
category: internal
status: active
confidence: high
last_verified: 2025-12-02
tags:
  - content
  - links
  - snippets
  - articles
  - reference
owner: V
---

# Content Library v3 (Unified)

**Capability ID:** `content-library-v3`  
**Category:** Internal System  
**Status:** Active  
**Confidence:** High  
**Last Verified:** 2025-12-02

---
```yaml
# Zone 2: Capability metadata (machine-readable)
capability_id: content-library-v3
name: Content Library v3 (Unified, Canonical DB)
category: internal
status: active
confidence: high
last_verified: 2025-12-17
tags:
- content
- links
- snippets
- reference
- consolidation
entry_points:
- type: script
  id: N5/scripts/content_library_v3.py
- type: script
  id: N5/scripts/auto_populate_content.py
- type: script
  id: N5/scripts/b_block_parser.py
- type: script
  id: N5/scripts/email_composer.py
- type: script
  id: N5/scripts/email_corrections.py
owner: V
change_type: update
capability_file: N5/capabilities/internal/content-library-v3.md
description: 'Consolidated Content Library v3 onto a single canonical SQLite database
  at N5/data/content_library.db,

  removed vestigial v3/local DBs and wrapper scripts, and wired consumers to a unified
  implementation.

  Email composer, B-block parser, auto-populate, and Exa research now all use the
  same underlying store,

  reducing duplication and failure modes.

  '
associated_files:
- N5/data/content_library.db
- N5/capabilities/internal/content-library-v3.md
- N5/scripts/content_library_v3.py
- N5/scripts/auto_populate_content.py
- N5/scripts/b_block_parser.py
- N5/scripts/email_composer.py
- N5/scripts/email_corrections.py
- N5/scripts/exa_research.py
```



## What It Does

Unified content library system that consolidates:
- **Operational links** (Calendly URLs, trial codes, demo links)
- **Snippets** (bios, signatures, blurbs)
- **Reference articles** (decks, social posts, papers, podcasts)

Single database, single CLI, single API for all content lookup and management.

---

## Entry Points

| Type | ID | Description |
|------|----|-------------|
| script | `Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py` | Unified CLI |
| script | `Personal/Knowledge/ContentLibrary/scripts/ingest.py` | Article ingestion |
| script | `N5/scripts/content_library.py` | Backward-compat wrapper |
| script | `N5/scripts/lint_js_shell_tweets.py` | X.com capture validator |
| database | `Personal/Knowledge/ContentLibrary/content-library-v3.db` | SQLite database |

---

## How to Use

### CLI Commands

```bash
# Stats
python3 Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py stats

# Search
python3 Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py search --query "calendly"

# Get by ID
python3 Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py get vrijen_bio_medium

# Add item
python3 Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py add \
  --id my_link --type link --title "My Link" --url "https://example.com" \
  --tag work --topic meetings

# Ingest article
python3 Personal/Knowledge/ContentLibrary/scripts/ingest.py \
  "https://example.com/article" "Article Title" \
  --type article --source discovered --topics AI productivity
```

### Python API

```python
from content_library_v3 import ContentLibraryV3

lib = ContentLibraryV3()

# Search
results = lib.search(query="calendly", item_type="link", limit=5)

# Get by ID
item = lib.get("vrijen_bio_medium")

# Add
lib.add(
    item_id="new_link",
    item_type="link",
    title="New Link",
    url="https://example.com",
    tags={"category": "work"},
    topics=["meetings"]
)

# Stats
stats = lib.stats()
```

---

## Database Schema

**Tables:**
- `items` — Core content items (id, type, title, url, content, etc.)
- `tags` — Key-value tags per item
- `topics` — Topic associations
- `blocks` — Sub-content blocks (for articles)
- `relationships` — Item-to-item relationships
- `knowledge_refs` — Links to knowledge base entries

**Item Types:**
- `link` — URLs (calendly, demos, resources)
- `snippet` — Reusable text (bios, signatures)
- `article` — Reference articles, decks, posts
- `meeting` — Meeting records (deprecated, use Meeting Pipeline)

---

## Integration Points

### Consumers
- `email_composer.py` — Looks up signatures, calendly links
- `auto_populate_content.py` — Ingests content from B-blocks
- `b_block_parser.py` — Stores meeting blocks
- `email_corrections.py` — Correction lookups

### Ingest Pipeline
- `ingest.py` — Add new articles/decks
- `enhance.py` — Add summaries
- `summarize.py` — AI summarization
- `content_to_knowledge.py` — Extract facts

---

## Migration History

**v3 (2025-12-02):** Unified two systems:
- N5/data/content_library.db (67 links/snippets)
- Personal/Knowledge/ContentLibrary/content-library.db (16 articles)

Into single unified database with:
- Consolidated schema
- Single CLI
- Single API
- Backward-compatible wrappers

---

## Associated Files

- `file 'Personal/Knowledge/ContentLibrary/README.md'` — Primary documentation
- `file 'Documents/System/guides/content-library-system.md'` — System guide
- `file 'Documents/System/guides/content-library-quickstart.md'` — Quickstart
- `file 'N5/orchestration/content-library-v3/'` — Build orchestration docs
- `file 'Personal/schemas/content-library-v3.schema.json'` — JSON schema

---

## Maintenance

**Lint for broken X.com captures:**
```bash
python3 N5/scripts/lint_js_shell_tweets.py
```

**Backup:**
```bash
cp Personal/Knowledge/ContentLibrary/content-library-v3.db \
   Personal/Knowledge/ContentLibrary/backups/content-library-v3_$(date +%Y%m%d).db
```

