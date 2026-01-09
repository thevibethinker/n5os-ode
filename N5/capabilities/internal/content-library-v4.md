---
created: 2025-12-02
last_edited: 2026-01-09
version: 4.0
capability_id: content-library-v4
name: Content Library v4
category: internal
status: active
confidence: high
last_verified: 2026-01-09
provenance: content-library-v4-build
tags:
  - content
  - links
  - snippets
  - articles
  - reference
owner: V
---

# Content Library v4

**Capability ID:** `content-library-v4`  
**Category:** Internal System  
**Status:** Active  
**Confidence:** High  
**Last Verified:** 2026-01-09

---

## Overview

Single source of truth for saved content: articles, links, snippets, social posts, decks, podcasts, videos, books, papers, frameworks, and quotes.

**Key improvements in v4:**
- Consolidated all content to single canonical location
- Streamlined schema with `content_type` column (vs legacy `type`)
- Auto-ingest rule: `save_webpage` automatically triggers ingestion
- Semantic memory integration via `content-library` profile

---

## Architecture

| Component | Location |
|-----------|----------|
| **Database** | `file 'N5/data/content_library.db'` |
| **Content Storage** | `file 'Knowledge/content-library/'` |
| **CLI** | `file 'N5/scripts/content_library.py'` |
| **Ingest Script** | `file 'N5/scripts/content_ingest.py'` |
| **Backfill Script** | `file 'N5/scripts/content_backfill.py'` |

### Directory Structure

```
Knowledge/content-library/
├── .n5protected           # Protection marker
├── articles/              # Saved articles
│   └── vrijen/            # V's authored articles
├── books/
├── decks/
├── frameworks/
├── papers/
├── personal/              # Personal content
└── social-posts/
```

---

## Content Types

| Type | Description |
|------|-------------|
| `link` | URLs (calendly, demos, resources, references) |
| `snippet` | Reusable text (bios, signatures, blurbs) |
| `article` | Reference articles, blog posts, guides |
| `social-post` | X/Twitter posts, LinkedIn posts |
| `deck` | Presentations, slide decks |
| `podcast` | Podcast episodes |
| `video` | Video content, transcripts |
| `book` | Book references |
| `paper` | Research papers, academic content |
| `framework` | Conceptual frameworks |
| `quote` | Notable quotes |

**Current counts (2026-01-09):** 138 items (114 links, 13 snippets, 10 articles, 1 social-post)

---

## Workflows

### Save an Article (Automatic)

The auto-ingest rule triggers after `save_webpage`:

1. Use `save_webpage <url>` in conversation
2. File saves to `Articles/` initially
3. Auto-ingest rule executes: `python3 N5/scripts/content_ingest.py "<file>" --type article --move`
4. File moves to `Knowledge/content-library/articles/`
5. DB record created with metadata

### Manual Ingest

```bash
# Ingest an article
python3 N5/scripts/content_ingest.py /path/to/article.md --type article

# Ingest and move to canonical location
python3 N5/scripts/content_ingest.py /path/to/article.md --type article --move

# Dry run to see what would happen
python3 N5/scripts/content_ingest.py /path/to/file.md --dry-run

# Add tags during ingest
python3 N5/scripts/content_ingest.py /path/to/file.md --type article --tags "vrijen-authored,medium"
```

### Search Content

```bash
# Search by type
python3 N5/scripts/content_library.py search --type article

# Search by query
python3 N5/scripts/content_library.py search --query "RLM"

# Combined search
python3 N5/scripts/content_library.py search --type article --query "recursive"
```

### List Content Types

```bash
python3 N5/scripts/content_library.py list-types
```

Output:
```
Content types:
  link: 114
  snippet: 13
  article: 10
  social-post: 1
```

### View Statistics

```bash
python3 N5/scripts/content_library.py stats
```

### Sync All Files to DB

Run backfill to ensure all files in `Knowledge/content-library/` have DB records:

```bash
python3 N5/scripts/content_library.py sync
```

---

## Database Schema

```sql
CREATE TABLE items (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content_type TEXT NOT NULL,      -- article, link, snippet, etc.
    content TEXT,                     -- Full content (for snippets/links)
    url TEXT,                         -- Source URL
    source TEXT,                      -- Origin system
    source_url TEXT,                  -- Original fetch URL
    source_file_path TEXT,            -- Path to local file
    tags TEXT,                        -- Comma-separated tags
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    ingested_at TEXT,                 -- When file was ingested
    deprecated INTEGER NOT NULL DEFAULT 0,
    expires_at TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    last_used_at TEXT,
    confidence INTEGER DEFAULT 3,
    has_content INTEGER DEFAULT 0,
    has_summary INTEGER DEFAULT 0,
    word_count INTEGER,
    has_embedding INTEGER DEFAULT 0
);

-- Indexes
CREATE INDEX idx_items_content_type ON items(content_type);
CREATE INDEX idx_items_deprecated ON items(deprecated);
CREATE INDEX idx_items_title ON items(title COLLATE NOCASE);
CREATE INDEX idx_items_updated ON items(updated_at DESC);
CREATE INDEX idx_items_has_embedding ON items(has_embedding);
```

---

## Integration Points

### Semantic Memory

The `content-library` profile in N5 Memory Client points to `Knowledge/content-library/`:

```python
from N5.cognition.n5_memory_client import N5MemoryClient

client = N5MemoryClient()
results = client.search_profile('content-library', 'recursive language', limit=3)
```

### Auto-Ingest Rule

A Zo rule automatically ingests content saved via `save_webpage`:

```
After using save_webpage to save an article to Articles/ or any local path:
→ Run: python3 N5/scripts/content_ingest.py "<saved_file_path>" --type article --move
→ File moves to Knowledge/content-library/articles/
→ Confirm: "Article ingested to Content Library"
```

### Global Index

Files in `Knowledge/content-library/` are indexed by `n5_index_rebuild.py` for workspace-wide search.

---

## CLI Reference

```bash
python3 N5/scripts/content_library.py <command> [options]

Commands:
  search      Search items (--type, --query)
  get         Get item by ID
  stats       Show statistics
  tags        List all tags
  list-types  List content types with counts
  ingest      Ingest a content file
  sync        Run backfill to sync all content files

Ingest script:
  python3 N5/scripts/content_ingest.py <file> [options]

Options:
  --type, -t    Content type (auto-detected if not specified)
  --dry-run, -n Show what would happen
  --move, -m    Move file to canonical location
  --tags        Comma-separated tags
  --quiet, -q   Suppress output except errors
```

---

## Migration History

| Version | Date | Changes |
|---------|------|---------|
| v1 | Pre-2025 | JSON-based system |
| v2 | 2025-11 | Split SQLite DBs (N5 + Personal) |
| v3 | 2025-12-02 | Unified DB, wrapper scripts |
| **v4** | **2026-01-09** | Consolidated storage, auto-ingest, streamlined schema |

**v4 migration included:**
- Schema migration (type → content_type, new columns)
- File consolidation to `Knowledge/content-library/`
- Backfill of all existing content
- Auto-ingest rule creation
- Semantic memory profile fix

---

## Maintenance

### Verify Database Integrity

```bash
sqlite3 N5/data/content_library.db "PRAGMA integrity_check;"
```

### Check File-DB Consistency

```bash
# Run sync to detect orphaned files
python3 N5/scripts/content_library.py sync
```

### Backup

```bash
cp N5/data/content_library.db N5/data/backups/content_library_$(date +%Y%m%d).db
```

---

## Associated Files

- `file 'N5/builds/content-library-v4/'` — Build workspace
- `file 'N5/scripts/migrations/content_library_v4_schema.py'` — Schema migration
- `file 'Documents/System/guides/content-library-system.md'` — System guide

---

*Content Library v4 · Last verified 2026-01-09*

