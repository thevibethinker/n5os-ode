---
created: 2025-12-02
last_edited: 2026-01-09
version: 4.0
provenance: content-library-v4-build
---

# Content Library v4 — System Guide

System-level documentation for the **Content Library v4** used across N5 workflows.

- **Canonical DB:** `file 'N5/data/content_library.db'`  
- **Content Storage:** `file 'Knowledge/content-library/'`  
- **CLI:** `file 'N5/scripts/content_library.py'`  
- **Capability Doc:** `file 'N5/capabilities/internal/content-library-v4.md'`

---

## 1. Overview

### 1.1 Purpose

Content Library v4 provides a **single source of truth** for:

- **Operational handles:** Links and snippets used in email, follow-ups, and automations
- **Knowledge assets:** Articles, decks, social posts, podcasts, videos, books, papers, frameworks, and quotes

### 1.2 Key Features

- **Unified storage:** All content in `Knowledge/content-library/`
- **Auto-ingest:** `save_webpage` automatically triggers ingestion
- **Semantic search:** Integrated with N5 Memory Client
- **Streamlined CLI:** Simple commands for search, ingest, sync

---

## 2. Architecture

### 2.1 File Layout

```
Knowledge/content-library/
├── .n5protected           # Protection marker (do not delete)
├── articles/              # Saved articles from web
│   └── vrijen/            # V's authored articles
├── books/                 # Book references
├── decks/                 # Presentations
├── frameworks/            # Conceptual frameworks
├── papers/                # Research papers
├── personal/              # Personal content
└── social-posts/          # X/Twitter, LinkedIn posts

N5/data/
└── content_library.db     # SQLite database (single canonical source)

N5/scripts/
├── content_library.py     # Main CLI
├── content_ingest.py      # File ingestion script
└── content_backfill.py    # Bulk sync script
```

### 2.2 Database Schema

```sql
CREATE TABLE items (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content_type TEXT NOT NULL,
    content TEXT,
    url TEXT,
    source TEXT,
    source_url TEXT,
    source_file_path TEXT,
    tags TEXT,
    notes TEXT,
    created_at TEXT,
    updated_at TEXT,
    ingested_at TEXT,
    deprecated INTEGER DEFAULT 0,
    expires_at TEXT,
    version INTEGER DEFAULT 1,
    last_used_at TEXT,
    confidence INTEGER DEFAULT 3,
    has_content INTEGER DEFAULT 0,
    has_summary INTEGER DEFAULT 0,
    word_count INTEGER,
    has_embedding INTEGER DEFAULT 0
);
```

### 2.3 Content Types

| Type | Count | Description |
|------|-------|-------------|
| `link` | 114 | URLs (calendly, demos, resources) |
| `snippet` | 13 | Reusable text (bios, signatures) |
| `article` | 10 | Reference articles, blog posts |
| `social-post` | 1 | X/Twitter posts |
| `deck` | - | Presentations |
| `podcast` | - | Podcast episodes |
| `video` | - | Video content |
| `book` | - | Book references |
| `paper` | - | Research papers |
| `framework` | - | Conceptual frameworks |
| `quote` | - | Notable quotes |

---

## 3. CLI Reference

### 3.1 Main CLI (`content_library.py`)

```bash
python3 N5/scripts/content_library.py <command> [options]
```

| Command | Description |
|---------|-------------|
| `search` | Search items by type and/or query |
| `get` | Get item by ID |
| `stats` | Show statistics |
| `tags` | List all tags |
| `list-types` | List content types with counts |
| `ingest` | Ingest a content file |
| `sync` | Run backfill to sync all content files |

#### Examples

```bash
# List content types with counts
python3 N5/scripts/content_library.py list-types

# Search for articles
python3 N5/scripts/content_library.py search --type article

# Search with query
python3 N5/scripts/content_library.py search --query "recursive language"

# Combined search
python3 N5/scripts/content_library.py search --type article --query "RLM"

# View statistics
python3 N5/scripts/content_library.py stats

# Sync files to DB (backfill)
python3 N5/scripts/content_library.py sync
```

### 3.2 Ingest CLI (`content_ingest.py`)

```bash
python3 N5/scripts/content_ingest.py <file> [options]
```

| Option | Description |
|--------|-------------|
| `--type, -t` | Content type (auto-detected if not specified) |
| `--dry-run, -n` | Show what would happen without making changes |
| `--move, -m` | Move file to canonical location |
| `--tags` | Comma-separated tags to add |
| `--quiet, -q` | Suppress output except errors |

#### Examples

```bash
# Ingest an article
python3 N5/scripts/content_ingest.py /path/to/article.md --type article

# Ingest and move to canonical location
python3 N5/scripts/content_ingest.py /path/to/article.md --type article --move

# Dry run
python3 N5/scripts/content_ingest.py /path/to/file.md --dry-run

# Add tags
python3 N5/scripts/content_ingest.py /path/to/file.md --tags "vrijen-authored,medium"
```

---

## 4. Workflows

### 4.1 Save Article from Web (Automatic)

The recommended workflow uses the auto-ingest rule:

1. In conversation: `save_webpage https://example.com/article`
2. File initially saves to `Articles/`
3. **Auto-ingest rule triggers automatically:**
   - Runs `python3 N5/scripts/content_ingest.py "<file>" --type article --move`
   - File moves to `Knowledge/content-library/articles/`
   - DB record created
4. Confirmation: "Article ingested to Content Library"

### 4.2 Manual Ingest

For files not captured by auto-ingest:

```bash
python3 N5/scripts/content_ingest.py /path/to/file.md --type article --move
```

### 4.3 Bulk Sync

Ensure all files in `Knowledge/content-library/` have DB records:

```bash
python3 N5/scripts/content_library.py sync
```

This is idempotent — running multiple times creates no duplicates.

### 4.4 Search and Retrieve

```bash
# Find all articles about a topic
python3 N5/scripts/content_library.py search --type article --query "career"

# Get specific item by ID
python3 N5/scripts/content_library.py get vrijen_bio_medium
```

---

## 5. Integration Points

### 5.1 Semantic Memory

The `content-library` profile enables semantic search:

```python
from N5.cognition.n5_memory_client import N5MemoryClient

client = N5MemoryClient()
results = client.search_profile('content-library', 'recursive language', limit=3)
for r in results:
    print(r['path'], r['score'])
```

### 5.2 Auto-Ingest Rule

A Zo rule (user rule) triggers after `save_webpage`:

> After using save_webpage to save an article to Articles/ or any local path, automatically ingest the saved article into the Content Library by running `python3 N5/scripts/content_ingest.py "<saved_file_path>" --type article --move`

### 5.3 N5 Communication Workflows

Content library integrates with:
- Follow-up email generation (calendly links, trial codes)
- Email composer (signatures, bios)
- Meeting intelligence (reference links)

---

## 6. Maintenance

### 6.1 Health Checks

```bash
# Database integrity
sqlite3 N5/data/content_library.db "PRAGMA integrity_check;"

# Content type counts
python3 N5/scripts/content_library.py list-types

# Statistics
python3 N5/scripts/content_library.py stats
```

### 6.2 Verify File-DB Consistency

```bash
# Count files in storage
find Knowledge/content-library -name "*.md" | wc -l

# Count DB records with file paths
sqlite3 N5/data/content_library.db "SELECT COUNT(*) FROM items WHERE source_file_path IS NOT NULL;"

# Run sync to detect/fix orphans
python3 N5/scripts/content_library.py sync
```

### 6.3 Backup

```bash
cp N5/data/content_library.db N5/data/backups/content_library_$(date +%Y%m%d).db
```

---

## 7. Best Practices

### 7.1 Content Organization

- Articles go in `Knowledge/content-library/articles/`
- V's authored content goes in `Knowledge/content-library/articles/vrijen/` with `vrijen-authored` tag
- Use descriptive filenames (auto-generated from URL is fine)

### 7.2 Tags Convention

| Tag | Use Case |
|-----|----------|
| `vrijen-authored` | Content written by V |
| `careerspan` | Careerspan-related content |
| `reference` | Reference material |
| `archived` | Older content kept for reference |

### 7.3 ID Conventions

- Use descriptive slugs: `trial_code_general`, `vrijen_calendly_founders`
- Include entity prefix when relevant: `careerspan_deck_v2`
- Avoid dates in IDs unless truly necessary

---

## 8. Troubleshooting

### File Not Found After Ingest

```bash
# Check if file was moved
sqlite3 N5/data/content_library.db "SELECT source_file_path FROM items WHERE title LIKE '%keyword%';"
```

### Duplicate Detection

```bash
# Check for potential duplicates by title
sqlite3 N5/data/content_library.db "SELECT title, COUNT(*) as cnt FROM items GROUP BY title HAVING cnt > 1;"
```

### Reset Database (⚠️ Destructive)

```bash
# Only if truly needed - backs up first
cp N5/data/content_library.db N5/data/content_library.db.backup
rm N5/data/content_library.db
python3 N5/scripts/migrations/content_library_v4_schema.py  # Recreate schema
python3 N5/scripts/content_library.py sync  # Re-import all files
```

---

## 9. Migration History

| Version | Date | Key Changes |
|---------|------|-------------|
| v1 | Pre-2025 | JSON-based system |
| v2 | 2025-11 | Split SQLite DBs |
| v3 | 2025-12-02 | Unified DB, complex cutover |
| **v4** | **2026-01-09** | Simplified: single DB, single storage location, auto-ingest |

---

*Content Library v4 System Guide · 2026-01-09*

