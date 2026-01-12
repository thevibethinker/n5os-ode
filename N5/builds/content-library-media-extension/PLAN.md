---
created: 2026-01-11
last_edited: 2026-01-11
version: 1.0
provenance: con_DhmWU9cxqi6McEiA
---

# Content Library v4 Media Extension — Build Plan

**Build ID:** content-library-media-extension  
**Priority:** HIGH (execute today)  
**Estimated Time:** 4-5 hours (3 phases)  
**Architect:** Vibe Architect  
**Status:** Ready for Builder

---

## Open Questions

<!-- All resolved via V's decisions 2026-01-11 -->
None — all architecture decisions confirmed.

---

## V's Decisions (Locked)

| Decision | Answer |
|----------|--------|
| Architecture | Extend Content Library v4 (single source of truth) |
| Legacy DB | Archive `documents_media.db` → delete after migration verification |
| Essential Links | ✅ Already migrated to CL v4 (no action needed) |
| Media Storage | `Knowledge/content-library/media/` |
| Taxonomy | Hybrid: 6 pre-defined domains + organic tags within |
| Tag Creation | Semantic deduplication check before creating new tags |
| Tag Consolidation | Build in re-clustering capability (just-in-time execution) |

---

## Checklist

### Phase 1: Schema & Tag System (~1.5 hours)
- [ ] P1.1: Add media columns to items table (file_path, file_size, mime_type, duration_seconds, dimensions)
- [ ] P1.2: Expand content_type CHECK to include: image, audio, video, document, pdf
- [ ] P1.3: Create tag_domains table with 6 pre-defined domains
- [ ] P1.4: Create tag_registry table for semantic deduplication
- [ ] P1.5: Implement `find_similar_tags()` function (embedding-based or fuzzy match)
- [ ] P1.6: Implement `suggest_tag()` with semantic check + domain assignment
- [ ] P1.7: Add `consolidate_tags()` stub for future re-clustering
- [ ] P1.8: Write migration script with rollback
- [ ] P1.9: Test: verify schema, tag dedup, domain assignment

### Phase 2: Media Ingest & Storage (~1.5 hours)
- [ ] P2.1: Create `Knowledge/content-library/media/` directory structure
- [ ] P2.2: Extend `content_ingest.py` to handle media types (image, audio, video, pdf, document)
- [ ] P2.3: Implement file copy/move to canonical location with deduplication
- [ ] P2.4: Extract metadata (dimensions, duration, file size, mime type)
- [ ] P2.5: Auto-suggest tags based on filename + content analysis
- [ ] P2.6: Add `--media` flag to content_library.py CLI
- [ ] P2.7: Test: ingest image, audio, pdf → verify DB records + file placement

### Phase 3: Cleanup & Integration (~1 hour)
- [ ] P3.1: Archive deprecated essential-links.json to Documents/Archive/
- [ ] P3.2: Migrate any useful records from documents_media.db → content_library.db
- [ ] P3.3: Archive documents_media.db to Documents/Archive/
- [ ] P3.4: Remove obsolete scripts (documents_media_*.py) or mark deprecated
- [ ] P3.5: Update capability doc (`N5/capabilities/internal/content-library-v4.md`)
- [ ] P3.6: Final integration test: end-to-end ingest workflow
- [ ] P3.7: Update STATUS.md with completion report

---

## Phase 1: Schema & Tag System

### Affected Files
- `N5/data/content_library.db` — schema migration
- `N5/scripts/content_library.py` — add tag functions
- `N5/scripts/content_library_migrate_v4.1.py` — NEW migration script
- `N5/config/content_library_domains.json` — NEW domain definitions

### Changes

#### 1.1 Schema Migration

Add columns to `items` table:
```sql
ALTER TABLE items ADD COLUMN file_path TEXT;
ALTER TABLE items ADD COLUMN file_size INTEGER;
ALTER TABLE items ADD COLUMN mime_type TEXT;
ALTER TABLE items ADD COLUMN duration_seconds REAL;
ALTER TABLE items ADD COLUMN dimensions TEXT;  -- JSON: {"width": 1920, "height": 1080}
```

Expand content_type (via migration — recreate table if needed):
```sql
-- New valid types: link, snippet, article, deck, paper, book, framework, 
--                  social-post, podcast, video, quote, image, audio, document, pdf
```

#### 1.2 Tag Domain Table

```sql
CREATE TABLE tag_domains (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Pre-populate 6 domains
INSERT INTO tag_domains (id, name, description, sort_order) VALUES
    ('business-strategy', 'Business & Strategy', 'Strategic thinking, planning, business models', 1),
    ('career-talent', 'Career & Talent', 'Career development, hiring, talent management', 2),
    ('product-technology', 'Product & Technology', 'Product development, engineering, tech trends', 3),
    ('customer-community', 'Customer & Community', 'Customer success, community building, engagement', 4),
    ('industry-insights', 'Industry Insights', 'Market trends, competitor intel, industry news', 5),
    ('personal-meta', 'Personal & Meta', 'Personal development, productivity, meta-learning', 6);
```

#### 1.3 Tag Registry Table

```sql
CREATE TABLE tag_registry (
    tag TEXT PRIMARY KEY,
    domain_id TEXT,
    canonical_form TEXT,  -- normalized lowercase
    embedding BLOB,       -- for semantic similarity (optional)
    usage_count INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (domain_id) REFERENCES tag_domains(id)
);

CREATE INDEX idx_tag_registry_domain ON tag_registry(domain_id);
CREATE INDEX idx_tag_registry_canonical ON tag_registry(canonical_form);
```

#### 1.4 Tag Functions in content_library.py

```python
def find_similar_tags(self, proposed_tag: str, threshold: float = 0.8) -> List[Tuple[str, float]]:
    """Find existing tags similar to proposed tag.
    
    Returns list of (tag, similarity_score) above threshold.
    Uses fuzzy string matching (Levenshtein) as baseline.
    Embedding-based similarity is optional enhancement.
    """
    pass

def suggest_tag(self, proposed_tag: str, domain_hint: str = None) -> Dict[str, Any]:
    """Suggest a tag with semantic deduplication.
    
    Returns:
        {
            "action": "use_existing" | "create_new",
            "tag": "the-tag",
            "similar": [...],  # if action is create_new, shows what was checked
            "domain": "domain-id"
        }
    """
    pass

def consolidate_tags(self, dry_run: bool = True) -> Dict[str, Any]:
    """Re-cluster tags and suggest merges.
    
    Returns mapping of proposed merges for human review.
    Actual merge requires explicit confirmation.
    """
    pass
```

### Unit Tests
```bash
# After migration
sqlite3 N5/data/content_library.db ".schema items" | grep -E "file_path|mime_type"
sqlite3 N5/data/content_library.db "SELECT * FROM tag_domains"
sqlite3 N5/data/content_library.db "SELECT COUNT(*) FROM tag_registry"

# Tag dedup test
python3 -c "
from N5.scripts.content_library import ContentLibrary
lib = ContentLibrary()
result = lib.suggest_tag('career-coaching')
print(result)
result2 = lib.suggest_tag('Career Coaching')  # Should dedupe
print(result2)
"
```

---

## Phase 2: Media Ingest & Storage

### Affected Files
- `N5/scripts/content_ingest.py` — extend for media
- `N5/scripts/content_library.py` — add media CLI commands
- `Knowledge/content-library/media/` — NEW directory structure

### Changes

#### 2.1 Directory Structure

```
Knowledge/content-library/
├── articles/          # existing
├── media/
│   ├── images/
│   ├── audio/
│   ├── video/
│   ├── documents/     # Word, etc.
│   └── pdf/
└── .content-library-root  # marker file
```

#### 2.2 Extend content_ingest.py

Add media type detection and handling:

```python
MEDIA_TYPES = {
    'image': ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'],
    'audio': ['.mp3', '.wav', '.m4a', '.ogg', '.flac'],
    'video': ['.mp4', '.mov', '.avi', '.mkv', '.webm'],
    'pdf': ['.pdf'],
    'document': ['.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt'],
}

def ingest_media(file_path: Path, content_type: str = None, move: bool = False) -> Dict:
    """Ingest a media file into the content library.
    
    1. Detect type from extension if not specified
    2. Extract metadata (size, dimensions, duration)
    3. Copy/move to canonical location
    4. Create DB record with metadata
    5. Auto-suggest tags
    """
    pass

def extract_media_metadata(file_path: Path) -> Dict:
    """Extract metadata from media file.
    
    - Images: dimensions, format
    - Audio: duration, bitrate
    - Video: duration, dimensions, codec
    - PDF: page count
    - Documents: page count (if possible)
    """
    pass
```

#### 2.3 CLI Extension

```bash
# New commands
python3 N5/scripts/content_library.py ingest /path/to/image.png --type image
python3 N5/scripts/content_library.py ingest /path/to/doc.pdf --type pdf --move
python3 N5/scripts/content_library.py search --type image --tags "domain:product-technology"
python3 N5/scripts/content_library.py list-media  # List all media items
```

### Unit Tests
```bash
# Test image ingest
cp /home/workspace/Images/test.png /tmp/test_ingest.png
python3 N5/scripts/content_ingest.py /tmp/test_ingest.png --type image --dry-run

# Verify file placement
ls -la Knowledge/content-library/media/images/

# Verify DB record
sqlite3 N5/data/content_library.db "SELECT id, title, content_type, file_path, mime_type FROM items WHERE content_type='image'"
```

---

## Phase 3: Cleanup & Integration

### Affected Files
- `N5/prefs/communication/deprecated/essential-links.json` → Archive
- `N5/data/documents_media.db` → Archive after migration
- `N5/scripts/documents_media_*.py` → Mark deprecated
- `N5/capabilities/internal/content-library-v4.md` → Update
- `Documents/Archive/` — destination for archived files

### Changes

#### 3.1 Archive Essential Links JSON

```bash
mkdir -p Documents/Archive/deprecated-2026-01
mv N5/prefs/communication/deprecated/essential-links.json \
   Documents/Archive/deprecated-2026-01/essential-links.json
```

#### 3.2 Migrate documents_media.db Records

```python
# Migration script checks for any records worth keeping
# Current state: 2 documents, 0 media — likely test data
# If real content exists, migrate to content_library.db
```

#### 3.3 Archive documents_media.db

```bash
mv N5/data/documents_media.db Documents/Archive/deprecated-2026-01/
```

#### 3.4 Mark Obsolete Scripts

Add deprecation headers to:
- `N5/scripts/documents_media_query.py`
- `N5/scripts/documents_media_db_init.py`
- `N5/scripts/document_media_curator.py`
- `N5/scripts/documents_media_migrate_v1.1.py`
- `N5/scripts/document_processor.py`

#### 3.5 Update Capability Doc

Update `N5/capabilities/internal/content-library-v4.md` with:
- New media types supported
- Tag system documentation
- Media ingest workflow
- Storage locations

### Unit Tests
```bash
# Verify archives exist
ls -la Documents/Archive/deprecated-2026-01/

# Verify no broken imports
grep -r "documents_media" N5/scripts/*.py | grep -v "DEPRECATED" | grep -v ".pyc"

# End-to-end test
python3 N5/scripts/content_library.py stats
python3 N5/scripts/content_library.py list-types
python3 N5/scripts/content_library.py search --type image --limit 5
```

---

## Success Criteria

1. **Schema extended**: `items` table has media columns; content_type includes image/audio/video/pdf/document
2. **Tag system working**: `suggest_tag()` performs semantic dedup; 6 domains pre-populated
3. **Media ingest functional**: Can ingest image/audio/video/pdf via CLI with metadata extraction
4. **Files organized**: Media stored in `Knowledge/content-library/media/<type>/`
5. **Legacy cleaned up**: `documents_media.db` archived; deprecated scripts marked
6. **Documentation updated**: Capability doc reflects new functionality
7. **All tests pass**: Unit tests in each phase verify functionality

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Schema migration breaks existing queries | Low | High | Run migration on copy first; test all importers |
| Tag dedup too aggressive (false positives) | Medium | Medium | Use 0.85 threshold; always allow override |
| Large media files slow ingest | Low | Low | Stream metadata extraction; don't load full file |
| Embedding computation slow | Medium | Low | Make embeddings optional; fuzzy match as fallback |

---

## Trap Doors (Irreversible Decisions)

⚠️ **Schema changes**: Adding columns is safe; changing content_type CHECK constraint requires table recreation. Mitigation: create new table, migrate data, drop old.

⚠️ **Tag consolidation merges**: Once tags are merged, original granularity is lost. Mitigation: `consolidate_tags()` is dry-run by default; requires explicit confirmation.

---

## Alternatives Considered (Nemawashi)

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **A: Extend CL v4** ⭐ | Single source of truth; existing tooling works | Schema migration needed | ✅ Selected |
| **B: Keep documents_media.db** | No migration; already has media schema | Two systems to maintain; already obsolete | ❌ Rejected |
| **C: New media-only DB** | Clean separation | Third system; complicates queries | ❌ Rejected |

---

## Handoff to Builder

**Plan location:** `file 'N5/builds/content-library-media-extension/PLAN.md'`

**Execute phases in order:** 1 → 2 → 3

**Context:**
- Current CL v4 schema is in `N5/data/content_library.db`
- Current CL v4 code is in `N5/scripts/content_library.py`
- Essential Links already migrated (20+ records exist)
- `documents_media.db` has only 2 test records — safe to archive

**Start command:**
```
set_active_persona("567cc602-060b-4251-91e7-40be591b9bc3")  # Builder
```

---

*Plan created by Vibe Architect · 2026-01-11 17:25 ET*

