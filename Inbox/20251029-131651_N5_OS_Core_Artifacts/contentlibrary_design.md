# Content Library Design

**Version:** 0.1  
**Status:** Design Specification  
**Last Updated:** 2025-10-28

## Overview

The Content Library is a centralized content management system for N5 that provides:
- Unified interface for all content types (articles, notes, media, code)
- Metadata-driven organization with tags and categories
- Full-text search with optional vector embeddings
- Version control and audit trails
- Automated workflows (archival, cleanup, promotion)

## Design Principles

1. **SQLite-First** - Single-user, portable, zero-config database
2. **File-System-Backed** - Database indexes files, doesn't replace them
3. **Metadata-Rich** - Capture context at creation, not organization time
4. **Flow-Based** - Content moves through stages with time bounds
5. **AI-Friendly** - Optimized for AI search and summarization

## Architecture

### Database Schema

```sql
-- Core content table
CREATE TABLE content (
    id TEXT PRIMARY KEY,  -- con_XYZ123... format
    path TEXT NOT NULL UNIQUE,  -- Absolute file path
    kind TEXT NOT NULL,  -- doc, sheet, code, media, service, note
    title TEXT,
    summary TEXT,  -- max 220 chars
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    accessed_at TEXT,
    size_bytes INTEGER,
    mime_type TEXT,
    stage TEXT DEFAULT 'active',  -- active, archived, deleted
    archived_at TEXT,
    CONSTRAINT valid_kind CHECK (kind IN ('doc', 'sheet', 'code', 'media', 'service', 'note'))
);

-- Tags (many-to-many)
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE content_tags (
    content_id TEXT NOT NULL,
    tag_id INTEGER NOT NULL,
    added_at TEXT NOT NULL,
    PRIMARY KEY (content_id, tag_id),
    FOREIGN KEY (content_id) REFERENCES content(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Full-text search index
CREATE VIRTUAL TABLE content_fts USING fts5(
    content_id UNINDEXED,
    title,
    summary,
    content_text
);

-- Relationships (references, dependencies, related items)
CREATE TABLE content_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL,  -- references, depends_on, related_to, supersedes
    created_at TEXT NOT NULL,
    FOREIGN KEY (source_id) REFERENCES content(id) ON DELETE CASCADE,
    FOREIGN KEY (target_id) REFERENCES content(id) ON DELETE CASCADE,
    CONSTRAINT valid_relationship CHECK (
        relationship_type IN ('references', 'depends_on', 'related_to', 'supersedes')
    )
);

-- Version history
CREATE TABLE content_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id TEXT NOT NULL,
    version_num INTEGER NOT NULL,
    snapshot_path TEXT,  -- Path to versioned copy
    size_bytes INTEGER,
    created_at TEXT NOT NULL,
    created_by TEXT,  -- user or system
    change_summary TEXT,
    FOREIGN KEY (content_id) REFERENCES content(id) ON DELETE CASCADE
);

-- Metadata key-value store
CREATE TABLE content_metadata (
    content_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (content_id, key),
    FOREIGN KEY (content_id) REFERENCES content(id) ON DELETE CASCADE
);

-- Access audit trail
CREATE TABLE content_access_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id TEXT NOT NULL,
    action TEXT NOT NULL,  -- read, write, delete, archive
    timestamp TEXT NOT NULL,
    context TEXT,  -- Conversation ID or system process
    FOREIGN KEY (content_id) REFERENCES content(id)
);

-- Indices for performance
CREATE INDEX idx_content_kind ON content(kind);
CREATE INDEX idx_content_stage ON content(stage);
CREATE INDEX idx_content_updated ON content(updated_at DESC);
CREATE INDEX idx_content_created ON content(created_at DESC);
CREATE INDEX idx_tags_name ON tags(name);
CREATE INDEX idx_relationships_source ON content_relationships(source_id);
CREATE INDEX idx_relationships_target ON content_relationships(target_id);
CREATE INDEX idx_versions_content ON content_versions(content_id, version_num DESC);
```

### API Interface

```python
class ContentLibrary:
    """Content Library API for N5."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
    
    # Core CRUD
    def add_content(
        self,
        path: str,
        kind: str,
        title: str = None,
        summary: str = None,
        tags: List[str] = None,
        metadata: Dict[str, str] = None
    ) -> str:
        """Add new content to library. Returns content ID."""
        pass
    
    def get_content(self, content_id: str) -> Dict:
        """Retrieve content by ID."""
        pass
    
    def update_content(
        self,
        content_id: str,
        **kwargs  # title, summary, tags, metadata
    ) -> bool:
        """Update content metadata."""
        pass
    
    def delete_content(self, content_id: str, permanent: bool = False) -> bool:
        """Soft delete (archive) or permanent delete."""
        pass
    
    # Search & Discovery
    def search(
        self,
        query: str = None,
        kind: List[str] = None,
        tags: List[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Full-text search with filters."""
        pass
    
    def search_by_tags(
        self,
        tags: List[str],
        match_all: bool = True
    ) -> List[Dict]:
        """Find content by tags."""
        pass
    
    def get_related(
        self,
        content_id: str,
        relationship_type: str = None
    ) -> List[Dict]:
        """Find related content."""
        pass
    
    # Tags
    def add_tags(self, content_id: str, tags: List[str]) -> bool:
        """Add tags to content."""
        pass
    
    def remove_tags(self, content_id: str, tags: List[str]) -> bool:
        """Remove tags from content."""
        pass
    
    def list_tags(self, min_count: int = 1) -> List[Tuple[str, int]]:
        """List all tags with usage count."""
        pass
    
    # Relationships
    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        rel_type: str
    ) -> bool:
        """Create relationship between content items."""
        pass
    
    # Versioning
    def create_version(
        self,
        content_id: str,
        change_summary: str = None
    ) -> int:
        """Snapshot current version. Returns version number."""
        pass
    
    def get_versions(self, content_id: str) -> List[Dict]:
        """List all versions of content."""
        pass
    
    def restore_version(self, content_id: str, version_num: int) -> bool:
        """Restore content to specific version."""
        pass
    
    # Lifecycle Management
    def archive_content(
        self,
        content_id: str = None,
        older_than_days: int = None,
        stage: str = 'active'
    ) -> List[str]:
        """Archive content by ID or age."""
        pass
    
    def cleanup_deleted(self, older_than_days: int = 30) -> int:
        """Permanently delete soft-deleted content after retention period."""
        pass
    
    # Analytics
    def get_stats(self) -> Dict:
        """Get library statistics."""
        pass
    
    def get_stale_content(self, days: int = 90) -> List[Dict]:
        """Find content not accessed in X days."""
        pass
```

## File Organization

Content Library supplements (doesn't replace) filesystem organization:

```
/home/workspace/
├── Documents/          # Managed by content library
├── Knowledge/          # Managed by content library
├── Lists/             # Managed by content library
├── Records/           # Managed by content library
│   ├── Company/
│   ├── Personal/
│   └── Temporary/     # Auto-archived after 14 days
└── N5/
    └── data/
        └── content_library.db  # Content library database
```

## Workflows

### Auto-Indexing

When files are created/modified:
1. Detect file change (filesystem watcher or periodic scan)
2. Extract metadata (title from first heading, summary)
3. Add/update content library entry
4. Auto-tag based on path and content
5. Index for full-text search

### Auto-Archival

Scheduled task (daily):
1. Find content in `Records/Temporary/` older than 14 days
2. Archive to `Records/Archive/YYYY/MM/`
3. Update content library stage to 'archived'
4. Log archival action

### Cleanup

Scheduled task (weekly):
1. Find soft-deleted content older than 30 days
2. Permanently delete files
3. Remove from content library (cascade deletes relationships, tags, versions)

### Search

User searches via command or AI:
1. Parse query (keywords, filters)
2. Run FTS query on content_fts table
3. Apply filters (kind, tags, date ranges)
4. Rank results by relevance
5. Return with snippets and metadata

## Integration Points

### With N5 Commands

```markdown
---
name: library-search
triggers:
  - /search
  - /find
---

# Search Content Library

Search all indexed content.

**Usage:**
- `/search machine learning` - Full-text search
- `/search tag:ai tag:research` - Search by tags
- `/search kind:doc recent:7d` - Search docs from last 7 days
```

### With Session State

When conversation references files:
1. Add to `content_access_log`
2. Update `accessed_at` timestamp
3. Create relationships if appropriate

### With AI Summarization

Scheduled task (nightly):
1. Find new content without summaries
2. Generate summaries via AI
3. Update content library entries
4. Extract and add tags

## Migration Plan

### Phase 1: Core Schema (Week 1)
- Create database schema
- Implement basic CRUD operations
- Write unit tests

### Phase 2: Search & Indexing (Week 2)
- Implement full-text search
- Build auto-indexing workflow
- Filesystem watcher integration

### Phase 3: Workflows (Week 3)
- Auto-archival system
- Cleanup processes
- Version control

### Phase 4: Integration (Week 4)
- N5 commands integration
- Session state integration
- AI summarization pipeline

## Testing Strategy

### Unit Tests
- Database operations (CRUD, search, tags, relationships)
- API interface methods
- Edge cases (missing files, corrupted data)

### Integration Tests
- End-to-end workflows (index → search → archive)
- Filesystem watcher integration
- Command system integration

### Performance Tests
- Large library (10k+ items)
- Concurrent access
- Search query performance

## Open Questions

1. **Vector embeddings?** - For semantic search beyond keyword matching
2. **Deduplication?** - Detect and merge duplicate content
3. **External content?** - Index web articles, emails, external files
4. **Collaboration?** - Multi-user access (future, requires PostgreSQL)
5. **Backup strategy?** - Regular database backups, version snapshots

## References

- SQLite FTS5 docs: https://www.sqlite.org/fts5.html
- N5 architectural principles: `Knowledge/architectural/planning_prompt.md`
- Session state schema: `N5/schemas/index.schema.json`

---

**Status:** Ready for implementation  
**Next Steps:** Begin Phase 1 (core schema and CRUD)
