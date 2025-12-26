---
created: 2025-12-02
last_edited: 2025-12-02
version: 1.0
status: ARCHITECTURE DRAFT
author: Vibe Architect
---

# Content Library v3: Unified Architecture

## Executive Summary

**Problem:** Two separate "Content Library" systems exist with overlapping names but distinct purposes:

1. **N5 Links & Snippets Library** (`N5/data/content_library.db`)
   - 67 items: calendly links, trial codes, bio snippets
   - Used by: email composer, follow-up generator, meeting intelligence
   - Schema: `items` (id, type, title, content, url, lifecycle) + `tags`

2. **Personal Content Library** (`Personal/Knowledge/ContentLibrary/content-library.db`)
   - 16 items: articles, decks, social posts, podcasts
   - Used by: knowledge management, content curation
   - Schema: `content` (id, source_type, title, url, topics, etc.) + `blocks` + `topics`

**Solution:** Merge into a **single unified Content Library v3** with a superset schema that:
- Supports ALL existing use cases (links, snippets, articles, decks, social posts, etc.)
- Lives at a single canonical location
- Has one CLI interface
- Supports both "operational lookup" and "knowledge asset" workflows

---

## Design Principles

1. **One Library, Multiple Views**
   - Everything is a "content item" with a type
   - Types: `link`, `snippet`, `article`, `deck`, `social-post`, `podcast`, `video`, `book`, `paper`, `framework`, `quote`, `resource`
   - Views filter by type (e.g., "give me all links" vs. "give me all articles")

2. **Handle + Asset Model**
   - Some items are **handles** (lightweight pointers): links, snippets
   - Some items are **assets** (rich content): articles, decks with stored full text
   - Unified schema supports both with optional fields

3. **Provenance is First-Class**
   - Every item knows: `source_type` (created | discovered), `platform`, `author`
   - Critical for distinguishing V's content from curated external content

4. **Topics + Tags (Dual Taxonomy)**
   - **Topics**: Controlled vocabulary for semantic categorization
   - **Tags**: Free-form key:value pairs for operational filtering

5. **Lifecycle Management**
   - `deprecated`, `expires_at`, `last_used_at` for operational items
   - `confidence`, `has_content`, `has_summary` for assets

6. **Copy-Not-Edit Migration**
   - All new files created fresh
   - Old files untouched until final cutover
   - Rollback = delete new files, keep old

---

## Unified Schema (v3)

### Core Tables

```sql
-- Main content table (superset of both schemas)
CREATE TABLE items (
    -- Identity
    id TEXT PRIMARY KEY,               -- Unique ID (slug format)
    item_type TEXT NOT NULL,           -- link, snippet, article, deck, social-post, podcast, video, book, paper, framework, quote, resource
    title TEXT NOT NULL,
    
    -- Content (handle vs asset)
    url TEXT,                          -- External URL (for links, articles, etc.)
    content TEXT,                      -- Inline content (for snippets, quotes)
    content_path TEXT,                 -- Path to stored full-text file (for assets)
    summary TEXT,                      -- Brief summary
    summary_path TEXT,                 -- Path to stored summary file
    word_count INTEGER,
    
    -- Provenance
    source_type TEXT NOT NULL DEFAULT 'manual',  -- created, discovered, manual, migration
    platform TEXT,                     -- gamma.app, twitter, medium, etc.
    author TEXT,                       -- Original author (for discovered content)
    
    -- Lifecycle (operational)
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    deprecated INTEGER NOT NULL DEFAULT 0,
    expires_at TEXT,
    last_used_at TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    
    -- Quality (assets)
    confidence INTEGER DEFAULT 3,      -- 1-5 scale
    has_content INTEGER DEFAULT 0,     -- Has stored full-text?
    has_summary INTEGER DEFAULT 0,     -- Has stored summary?
    
    -- Metadata
    notes TEXT,
    source TEXT                        -- Migration source: 'n5_links', 'personal_cl', 'new'
);

-- Tags table (key:value pairs for operational filtering)
CREATE TABLE tags (
    item_id TEXT NOT NULL,
    tag_key TEXT NOT NULL,
    tag_value TEXT NOT NULL,
    PRIMARY KEY (item_id, tag_key, tag_value),
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
);

-- Topics table (controlled vocabulary)
CREATE TABLE topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Item-Topic junction
CREATE TABLE item_topics (
    item_id TEXT NOT NULL,
    topic_id INTEGER NOT NULL,
    PRIMARY KEY (item_id, topic_id),
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

-- Blocks table (for rich assets with extractable chunks)
CREATE TABLE blocks (
    id TEXT PRIMARY KEY,
    item_id TEXT NOT NULL,
    block_code TEXT,                   -- B01, B02, etc.
    block_type TEXT,                   -- quote, insight, action, resource
    content TEXT NOT NULL,
    context TEXT,
    speaker TEXT,
    file_path TEXT,
    line_start INTEGER,
    line_end INTEGER,
    extracted_at TEXT,
    confidence INTEGER DEFAULT 3,
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
);

-- Block-Topic junction
CREATE TABLE block_topics (
    block_id TEXT NOT NULL,
    topic_id INTEGER NOT NULL,
    PRIMARY KEY (block_id, topic_id),
    FOREIGN KEY (block_id) REFERENCES blocks(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

-- Knowledge promotion tracking
CREATE TABLE knowledge_refs (
    block_id TEXT PRIMARY KEY,
    knowledge_type TEXT,
    knowledge_id TEXT,
    source_type TEXT,
    source_id TEXT,
    promoted_at TEXT,
    notes TEXT,
    FOREIGN KEY (block_id) REFERENCES blocks(id)
);

-- Relationships between items
CREATE TABLE relationships (
    from_id TEXT NOT NULL,
    to_id TEXT NOT NULL,
    rel_type TEXT NOT NULL,            -- related_to, references, derived_from
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (from_id, to_id, rel_type),
    FOREIGN KEY (from_id) REFERENCES items(id) ON DELETE CASCADE,
    FOREIGN KEY (to_id) REFERENCES items(id) ON DELETE CASCADE
);

-- Schema version tracking
CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_items_type ON items(item_type);
CREATE INDEX idx_items_source_type ON items(source_type);
CREATE INDEX idx_items_deprecated ON items(deprecated);
CREATE INDEX idx_items_title ON items(title COLLATE NOCASE);
CREATE INDEX idx_items_updated ON items(updated_at DESC);
CREATE INDEX idx_tags_key_value ON tags(tag_key, tag_value);
CREATE INDEX idx_blocks_item ON blocks(item_id);
```

### Type Mappings

| Old System | Old Type | New item_type |
|------------|----------|---------------|
| N5 Links DB | link | link |
| N5 Links DB | snippet | snippet |
| Personal CL | article | article |
| Personal CL | social-post | social-post |
| Personal CL | podcast | podcast |
| Personal CL | video | video |
| Personal CL | book | book |
| Personal CL | paper | paper |
| Personal CL | framework | framework |
| Personal CL | case-study | case-study |
| Personal CL | quote | quote |
| Personal CL | resource | resource |
| Personal CL | newsletter | newsletter |
| NEW | deck | deck |

---

## Canonical Locations

### New Unified System

```
Personal/Knowledge/ContentLibrary/       # Canonical home (knowledge layer)
├── content-library-v3.db                # NEW unified database
├── content/                             # Stored full-text content
│   └── *.md
├── scripts/
│   └── content_library_v3.py            # NEW unified CLI
├── README.md                            # Updated documentation
└── settings.json                        # Configuration
```

### Migration Artifacts (temporary)

```
N5/data/
├── content_library.db                   # OLD - keep until cutover
└── content_library.db.pre_v3_backup     # Backup before migration

Personal/Knowledge/ContentLibrary/
├── content-library.db                   # OLD - keep until cutover
└── content-library.db.pre_v3_backup     # Backup before migration
```

### Symlinks for Backwards Compatibility

```
N5/data/content_library.db → Personal/Knowledge/ContentLibrary/content-library-v3.db
```

(Or: update all N5 scripts to point to the new location directly)

---

## Migration Plan

### Phase 1: Create New Schema & Scripts (Copy)

1. Create `content-library-v3.db` with new schema
2. Create `content_library_v3.py` CLI (new file, doesn't touch old)
3. Create migration script `migrate_to_v3.py`

### Phase 2: Migrate Data (Copy)

1. Export all items from N5 `content_library.db` → insert into v3
2. Export all items from Personal `content-library.db` → insert into v3
3. Validate counts match: (67 + 16) = 83 items
4. Validate no duplicate IDs (if any, prefix with source)

### Phase 3: Update Consumers (Copy-then-Replace)

1. Create new versions of scripts that import from v3:
   - `email_composer_v3.py` → test → replace `email_composer.py`
   - `content_library_db_v3.py` → test → replace `content_library_db.py`
   - etc.
2. Update workflow prompts to reference new paths

### Phase 4: Cutover

1. Create backups of old DBs
2. Replace old files with new
3. Update symlinks/paths
4. Archive old files

### Phase 5: Cleanup

1. Delete temporary migration artifacts
2. Update documentation
3. Mark migration complete

---

## Files Requiring Changes

### REPLACE WHOLESALE (create new → swap)

| Current File | New File | Action |
|--------------|----------|--------|
| `N5/scripts/content_library.py` | `N5/scripts/content_library.py.new` | Rewrite for v3 API |
| `N5/scripts/content_library_db.py` | `N5/scripts/content_library_db.py.new` | Rewrite for v3 API |
| `Personal/Knowledge/ContentLibrary/scripts/ingest.py` | `Personal/Knowledge/ContentLibrary/scripts/ingest.py.new` | Rewrite for v3 schema |
| `Personal/Knowledge/ContentLibrary/scripts/enhance.py` | `Personal/Knowledge/ContentLibrary/scripts/enhance.py.new` | Rewrite for v3 schema |
| `Personal/Knowledge/ContentLibrary/scripts/summarize.py` | `Personal/Knowledge/ContentLibrary/scripts/summarize.py.new` | Rewrite for v3 schema |
| `Personal/Knowledge/ContentLibrary/README.md` | `Personal/Knowledge/ContentLibrary/README.md.new` | Rewrite for v3 |
| `Documents/System/guides/content-library-system.md` | `Documents/System/guides/content-library-system.md.new` | Rewrite for v3 |
| `Documents/System/guides/content-library-quickstart.md` | `Documents/System/guides/content-library-quickstart.md.new` | Rewrite for v3 |
| `Personal/Knowledge/Architecture/specs/systems/content_library_integration.md` | `Personal/Knowledge/Architecture/specs/systems/content_library_integration.md.new` | Rewrite for v3 |
| `Personal/schemas/content-library-entry.schema.json` | `Personal/schemas/content-library-v3.schema.json` | New schema |

### EDIT IN PLACE (after cutover)

| File | Lines/Sections to Update |
|------|-------------------------|
| `N5/scripts/email_composer.py` | Import path for content_library |
| `N5/scripts/knowledge_integrator.py` | Import path for content_library |
| `N5/scripts/auto_populate_content.py` | Import path for content_library |
| `N5/scripts/voice_transformer.py` | Import path for content_library |
| `N5/scripts/email_corrections.py` | Import path for content_library |
| `N5/scripts/document_media_curator.py` | Import path for content_library |
| `N5/scripts/knowledge_preflight.py` | Import path if applicable |
| `N5/scripts/b_block_parser.py` | Import path if applicable |
| `N5/prefs/knowledge/lookup.md` | Reference paths |
| `Prompts/Follow-Up Email Generator.prompt.md` | Reference paths |
| `Documents/DOCUMENTS_MEDIA_SYSTEM.md` | Content Library references |

### ARCHIVE (after cutover)

| File | Archive Location |
|------|------------------|
| `N5/data/content_library.db` | `N5/data/archive/content_library.db.pre_v3` |
| `Personal/Knowledge/ContentLibrary/content-library.db` | `Personal/Knowledge/ContentLibrary/archive/content-library.db.pre_v3` |
| `Personal/Knowledge/ContentLibrary/content-library.json` | `Personal/Knowledge/ContentLibrary/archive/content-library.json.pre_v3` |
| `N5/scripts/migrate_content_library_to_db.py` | `N5/scripts/archive/` |

---

## CLI Interface (v3)

```bash
# Unified CLI
python3 Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py <command>

# Commands
search --query <text> --type <type> --tag <key=value> --topic <topic>
get --id <id>
add --type <type> --title <title> [--url <url>] [--content <text>] [--tag <k=v>] [--topic <t>]
ingest --url <url> --type <type> --title <title>  # For articles, decks, etc.
update --id <id> [fields...]
deprecate --id <id>
list --type <type> --limit <n>
export --format json|markdown --type <type>
lint  # Run quality checks
stats  # Show counts by type
migrate  # Run v3 migration
```

### Backwards Compatibility Wrapper

For N5 scripts expecting the old path:

```python
# N5/scripts/content_library.py (thin wrapper)
from Personal.Knowledge.ContentLibrary.scripts.content_library_v3 import *
```

---

## Validation Checklist

Before cutover:

- [ ] All 67 N5 items migrated (check: `SELECT COUNT(*) FROM items WHERE source='n5_links'`)
- [ ] All 16 Personal items migrated (check: `SELECT COUNT(*) FROM items WHERE source='personal_cl'`)
- [ ] No duplicate IDs
- [ ] All tags preserved
- [ ] All topics preserved
- [ ] All content files still accessible via content_path
- [ ] Email composer works with new DB
- [ ] Follow-up generator works with new DB
- [ ] Ingest workflow works for new articles
- [ ] Search returns correct results for both link-type and asset-type queries

---

## Rollback Plan

If migration fails:

1. All `.new` files can be deleted
2. Old DBs are untouched
3. Old scripts continue to work
4. No data loss possible

---

## Timeline Estimate

| Phase | Duration | Notes |
|-------|----------|-------|
| 1. Create schema + scripts | 30 min | Architect designs, Builder implements |
| 2. Migrate data | 15 min | Script-driven |
| 3. Update consumers | 45 min | Create .new versions, test |
| 4. Cutover | 10 min | Swap files, update paths |
| 5. Cleanup | 10 min | Archive, docs |
| **Total** | ~2 hours | |

---

## Decision Points for V

1. **Canonical location:** Keep at `Personal/Knowledge/ContentLibrary/` (my recommendation) or move to `N5/data/`?
   - **Recommendation:** Personal/Knowledge/ContentLibrary/ – this is knowledge, not infrastructure

2. **ID collision handling:** If both DBs have an item with same ID, what to do?
   - **Recommendation:** Prefix with source (`n5_` or `pcl_`) only if collision detected

3. **Symlink or update paths?** For N5 scripts, symlink the old DB path or update all import paths?
   - **Recommendation:** Update paths directly (cleaner, no symlink maintenance)

4. **Archive old DBs or delete?**
   - **Recommendation:** Archive with `.pre_v3` suffix for 30 days, then delete

---

## Next Steps

1. **V confirms architecture** (this document)
2. **Hand off to Builder** to implement:
   - Schema creation script
   - Migration script
   - New CLI
   - Updated consumer scripts
3. **Run migration** (V present for go/no-go)
4. **Cutover** (V confirms)

---

*Designed by Vibe Architect | 2025-12-02*

