---
created: 2025-12-02
last_edited: 2026-01-19
version: 5.0
provenance: con_GwpdTRRuFJGuT9Qv
---

# Content Library v5 — System Guide

System-level documentation for the **Content Library v5** used across N5 workflows.

- **Canonical DB:** `file 'N5/data/content_library.db'`  
- **Content Storage:** `file 'Knowledge/content-library/'`  
- **CLI:** `file 'N5/scripts/content_library.py'`  
- **Capability Doc:** `file 'N5/capabilities/internal/content-library-v5.md'`

---

## 1. Overview

### 1.1 Purpose

The Content Library is the **first port of call for shareable assets**—links, articles, snippets, and resources that V shares in emails, follow-ups, intros, and communications.

**What it IS:**
- Repository of things to share (Calendly links, articles, bio snippets, decks, trial codes)
- Queryable index for communication workflows (email composer, follow-up generation)
- Normalized storage for web-saved content

**What it is NOT:**
- A routing brain or decision engine
- A CRM or contact database
- A to-do or task tracker

### 1.2 Key Features

- **Unified storage:** All content in `Knowledge/content-library/`
- **Auto-ingest:** `save_webpage` automatically triggers ingestion with auto-detection
- **Content types + subtypes:** Hierarchical classification for precise queries
- **Normalization (v5):** Clean text extraction + summary generation for articles
- **Semantic search:** Integrated with N5 Memory Client
- **Calendly sync:** Automatic DB synchronization with merge-safe enrichment

---

## 2. Architecture

### 2.1 File Layout

```
Knowledge/content-library/
├── .n5protected           # Protection marker (do not delete)
├── articles/              # Substantive articles, blog posts (V's authored + reference)
│   └── vrijen/            # V's authored articles
├── audio/                 # Podcast episodes
├── books/                 # Book references
├── decks/                 # Presentations
├── frameworks/            # Conceptual frameworks
├── images/                # Image assets
├── inspiration/           # Inspirational content
├── links/                 # Web links, profiles, resources (default for web-saved)
│   ├── calendly/          # Calendly links (auto-synced)
│   ├── profiles/          # Person/company profiles
│   └── resources/         # Tools, products, reference pages
├── papers/                # Research papers
├── personal/              # Personal content
├── quotes/                # Notable quotes
├── snippets/              # Reusable text (bios, signatures)
├── social-posts/          # X/Twitter, LinkedIn posts
├── transcripts/           # Transcriptions
└── video/                 # Video content

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
    subtype TEXT,                    -- v5: hierarchical classification
    content TEXT,
    summary TEXT,                    -- v5: normalized summary
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

### 2.3 Content Types and Subtypes

| Type | Subtype | Folder | Description |
|------|---------|--------|-------------|
| `link` | `tool` | links/ | Software tools, apps |
| `link` | `product` | links/ | Products, services |
| `link` | `resource` | links/resources/ | Reference pages, documentation |
| `link` | `profile` | links/profiles/ | Person or company profiles |
| `link` | `scheduling-link` | links/calendly/ | Calendly and scheduling URLs |
| `article` | — | articles/ | Substantive articles, blog posts |
| `snippet` | — | snippets/ | Reusable text (bios, signatures) |
| `social-post` | — | social-posts/ | X/Twitter, LinkedIn posts |
| `deck` | — | decks/ | Presentations |
| `podcast` | — | audio/ | Podcast episodes |
| `video` | — | video/ | Video content |
| `book` | — | books/ | Book references |
| `paper` | — | papers/ | Research papers |
| `framework` | — | frameworks/ | Conceptual frameworks |
| `quote` | — | quotes/ | Notable quotes |
| `inspiration` | — | inspiration/ | Inspirational content |
| `personal` | — | personal/ | Personal content |
| `transcript` | — | transcripts/ | Transcriptions |

**Auto-detection logic:** 
- Web-saved content with `url:` in frontmatter defaults to `link` type
- Calendly URLs → `subtype: scheduling-link`
- Override with `--type` flag when ingesting

---

## 3. CLI Reference

### 3.1 Main CLI (`content_library.py`)

```bash
python3 N5/scripts/content_library.py <command> [options]
```

| Command | Description |
|---------|-------------|
| `search` | Search items by type, subtype, and/or query |
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

# Search by type
python3 N5/scripts/content_library.py search --type article

# Search by subtype (v5)
python3 N5/scripts/content_library.py search --subtype scheduling-link

# Search with query
python3 N5/scripts/content_library.py search --query "recursive language"

# Combined search
python3 N5/scripts/content_library.py search --type link --subtype tool --query "scheduling"

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
# Auto-detect type and ingest
python3 N5/scripts/content_ingest.py /path/to/file.md --move

# Force type (override auto-detection)
python3 N5/scripts/content_ingest.py /path/to/article.md --type article --move

# Dry run
python3 N5/scripts/content_ingest.py /path/to/file.md --dry-run

# Add tags
python3 N5/scripts/content_ingest.py /path/to/file.md --tags "vrijen-authored,medium"
```

---

## 4. Operator Workflows

### 4.1 Add a Link (Structured, Minimal Content)

**When:** Adding a URL resource (tool, product, app, reference page) that doesn't need full article preservation.

1. Create markdown file at `Knowledge/content-library/links/<slug>.md`
2. Add frontmatter with required fields:
   ```yaml
   ---
   created: YYYY-MM-DD
   last_edited: YYYY-MM-DD
   version: 1.0
   provenance: <conversation_id>
   type: link
   subtype: tool|product|resource|profile|scheduling-link
   url: https://example.com/resource
   ---
   ```
3. Add H1 title and brief 'about' section (50-200 chars)
4. Run: `python3 N5/scripts/content_ingest.py Knowledge/content-library/links/<slug>.md`
5. Verify: `python3 N5/scripts/content_library.py get <id>`

**Expected artifacts:**
- Markdown file at `links/<slug>.md`
- DB record with `content_type=link`, `source_file_path` pointing to file

### 4.2 Add an Article (Full Content Preservation)

**When:** Saving a substantive article, blog post, newsletter, or essay for future reference or sharing.

1. Use `save_webpage` to save the article:
   ```
   save_webpage https://example.com/great-article
   ```
2. Auto-ingest rule triggers automatically with type auto-detection
3. File moves to `articles/` folder
4. DB record created with extracted content

**For manual ingestion:**
```bash
python3 N5/scripts/content_ingest.py <saved_file_path> --move
```

### 4.3 Add a Profile or Reference

**When:** Storing information about a person, company, or reference resource.

1. Create file in appropriate subfolder:
   - Profiles: `links/profiles/<name-slug>.md`
   - Resources: `links/resources/<slug>.md`
   - References: `papers/` or `books/`
2. Add structured frontmatter:
   ```yaml
   ---
   created: YYYY-MM-DD
   last_edited: YYYY-MM-DD
   version: 1.0
   provenance: <conversation_id>
   type: link
   subtype: profile|resource|reference
   url: https://example.com/profile
   entity: <person-name or company>
   ---
   ```
3. Add structured 'About' section with key facts
4. Run: `python3 N5/scripts/content_ingest.py <file_path>`

**For profiles, include:**
- Name
- Role/Title
- Company
- Key expertise areas
- LinkedIn URL (if available)
- Brief 1-2 sentence bio

### 4.4 Add Media (Audio/Video/Deck)

**When:** Storing media files with searchable metadata.

1. Place media file in appropriate folder:
   - Audio: `audio/<slug>.mp3`
   - Video: `video/<slug>.mp4`
   - Decks: `decks/<slug>.pdf`
2. Create companion markdown metadata file (same name, .md extension):
   ```yaml
   ---
   created: YYYY-MM-DD
   last_edited: YYYY-MM-DD
   type: podcast|video|deck
   media_file: <filename.ext>
   duration: <duration in minutes>
   ---
   
   # Title
   
   ## Description
   Brief description of the media content.
   ```
3. Run: `python3 N5/scripts/content_ingest.py <metadata_file.md>`

---

## 5. Calendly Usage Workflow

Calendly links are stored as `subtype: scheduling-link` under `type: link`. Each active event type has:
- A markdown file at `Knowledge/content-library/links/calendly/<slug>.md`
- A DB record with `content_type=link` and subtype `scheduling-link`

### 5.1 Storage Locations

- **Files:** `Knowledge/content-library/links/calendly/`
- **Database:** `N5/data/content_library.db` → items table
- **Sync Script:** `Integrations/calendly/sync_links.py`

### 5.2 Curated Context Fields

These fields provide usage context and are **curated** (never overwritten by automation if already set):

| Field | Purpose | Values |
|-------|---------|--------|
| `audience` | Who this link is for | personal, professional, investors, founders, enterprise, general |
| `priority` | Relative importance when multiple links match | high, medium, low |
| `use_when` | Contextual guidance for when to share this link | Free text description |

**Examples:**
- `audience: professional` → Client/prospect meetings
- `audience: investors` → Investor pitch meetings
- `use_when: General scheduling for new contacts`
- `use_when: Existing clients who need extended time`

### 5.3 Merge-Safe Behavior

**Principle:** Automation fills defaults; humans curate context. Existing values are NEVER overwritten.

| Field Type | Behavior |
|------------|----------|
| **Managed fields** (automation updates) | `duration`, `entity`, `provider`, `url`, `slug` |
| **Curated fields** (fill if missing only) | `audience`, `priority`, `use_when`, `purpose`, `context` |

```yaml
# Example: Original file has audience: investors
# Sync infers: audience: professional (from name pattern)
# Result: audience: investors (original preserved)
```

### 5.4 Adding Curated Context to Calendly Links

1. Open the file: `Knowledge/content-library/links/calendly/<slug>.md`
2. Add curated fields to frontmatter:
   ```yaml
   audience: professional
   priority: high
   use_when: Schedule with enterprise prospects who need extended time
   ```
3. Save — sync will preserve these values on future runs

---

## 6. Normalization (v5)

### 6.1 Overview

v5 introduces content normalization for web-saved articles:
- **Standard A (articles):** Heavy normalization — trafilatura extraction, heuristic stripping, summary generation
- **Standard B (social posts):** Light normalization — minimal stripping, preserve voice/style

### 6.2 Standard A: Article Normalization

For substantive articles:

1. **Clean text extraction** using trafilatura
2. **Remove:** Navigation, footer, subscribe boxes, ads, cookie banners
3. **Generate summary:** 2-3 sentence summary in frontmatter
4. **Update DB:** Set `has_summary=1`, populate `summary` column

### 6.3 Standard B: Social Post Normalization

For social media content:

1. **Light stripping:** Remove only clear boilerplate (follower counts, engagement metrics)
2. **Preserve:** Voice, tone, hashtags, mentions — post content IS the value
3. **No summary generation** — content is typically short enough

### 6.4 When Normalization Runs

Normalization is applied during ingestion when:
- Content type is `article` or `social-post`
- A companion HTML file exists (saved by `save_webpage`)
- The `--normalize` flag is not explicitly disabled

---

## 7. Integration Points

### 7.1 Semantic Memory

The `content-library` profile enables semantic search:

```python
from N5.cognition.n5_memory_client import N5MemoryClient

client = N5MemoryClient()
results = client.search_profile('content-library', 'recursive language', limit=3)
for r in results:
    print(r['path'], r['score'])
```

### 7.2 Auto-Ingest Rule

A Zo rule (user rule) triggers after `save_webpage`:

> After using save_webpage, automatically ingest the saved article into the Content Library:
> 1. Run: `python3 N5/scripts/content_ingest.py "<saved_file_path>" --move`
> 2. The script auto-detects content type from URL patterns and content
> 3. File moves to appropriate `Knowledge/content-library/<type>/` folder
> 4. Confirm: "Ingested to Content Library as <type>"

### 7.3 N5 Communication Workflows

Content library integrates with:
- Follow-up email generation (calendly links, trial codes)
- Email composer (signatures, bios)
- Meeting intelligence (reference links)

---

## 8. Maintenance

### 8.1 Health Checks

```bash
# Database integrity
sqlite3 N5/data/content_library.db "PRAGMA integrity_check;"

# Content type counts
python3 N5/scripts/content_library.py list-types

# Statistics
python3 N5/scripts/content_library.py stats

# Check for URL duplicates
sqlite3 N5/data/content_library.db "
SELECT url, COUNT(*) FROM items 
WHERE deprecated=0 AND url IS NOT NULL 
GROUP BY url HAVING COUNT(*) > 1;
"
```

### 8.2 Verify File-DB Consistency

```bash
# Count files in storage
find Knowledge/content-library -name "*.md" | wc -l

# Count DB records with file paths
sqlite3 N5/data/content_library.db "SELECT COUNT(*) FROM items WHERE source_file_path IS NOT NULL;"

# Run sync to detect/fix orphans
python3 N5/scripts/content_library.py sync
```

### 8.3 Backup

```bash
cp N5/data/content_library.db N5/data/backups/content_library_$(date +%Y%m%d).db
```

---

## 9. Best Practices

### 9.1 Content Organization

- Articles go in `Knowledge/content-library/articles/`
- V's authored content goes in `Knowledge/content-library/articles/vrijen/` with `vrijen-authored` tag
- Calendly links go in `Knowledge/content-library/links/calendly/`
- Use descriptive filenames (auto-generated from URL is fine)

### 9.2 Tags Convention

| Tag | Use Case |
|-----|----------|
| `vrijen-authored` | Content written by V |
| `careerspan` | Careerspan-related content |
| `reference` | Reference material |
| `archived` | Older content kept for reference |
| `scheduling-link` | Calendly and scheduling URLs |

### 9.3 ID Conventions

- Use descriptive slugs: `trial_code_general`, `vrijen_calendly_founders`
- Include entity prefix when relevant: `careerspan_deck_v2`
- Avoid dates in IDs unless truly necessary

---

## 10. Troubleshooting

### File Not Found After Ingest

```bash
# Check if file was moved
sqlite3 N5/data/content_library.db "SELECT source_file_path FROM items WHERE title LIKE '%keyword%';"
```

### Duplicate Detection

```bash
# Check for potential duplicates by title
sqlite3 N5/data/content_library.db "SELECT title, COUNT(*) as cnt FROM items GROUP BY title HAVING cnt > 1;"

# Check for URL duplicates
sqlite3 N5/data/content_library.db "SELECT url, COUNT(*) as cnt FROM items WHERE url IS NOT NULL GROUP BY url HAVING cnt > 1;"
```

### Reset Database (⚠️ Destructive)

```bash
# Only if truly needed - backs up first
cp N5/data/content_library.db N5/data/content_library.db.backup
rm N5/data/content_library.db
python3 N5/scripts/migrations/content_library_v5_schema.py  # Recreate schema
python3 N5/scripts/content_library.py sync  # Re-import all files
```

---

## 11. Migration History

| Version | Date | Key Changes |
|---------|------|-------------|
| v1 | Pre-2025 | JSON-based system |
| v2 | 2025-11 | Split SQLite DBs |
| v3 | 2025-12-02 | Unified DB, complex cutover |
| v4 | 2026-01-09 | Simplified: single DB, single storage location, auto-ingest |
| **v5** | **2026-01-19** | Subtypes, normalization (clean text + summary), Calendly DB sync, merge-safe enrichment |

---

*Content Library v5 — Last updated: 2026-01-19*
