---
created: 2026-01-09
last_edited: 2026-01-09
version: 1
provenance: con_5tYCDyhaRiYR0EGI
build: content-library-v4
wave: 1
---
# Content Library v4 — Wave 1 Worker Assignment

## Context

You are executing Wave 1 of the Content Library v4 redesign. This build consolidates a fragmented content system into a unified architecture.

**Build workspace:** `file 'N5/builds/content-library-v4/'`
**Orchestrator:** `python3 N5/scripts/build_orchestrator_v2.py`

### Background (Why This Build Exists)

The Content Library system is broken:
- **3 disconnected storage locations:** `Articles/`, `Knowledge/content-library/`, and references to non-existent `Personal/Knowledge/ContentLibrary/`
- **Database only tracks links/snippets** — articles saved via `save_webpage` never get registered
- **Semantic memory has stale paths** — searches fail silently
- **Documentation describes a v3 system that was never built**

We are fixing this with a clean v4 redesign.

---

## Your Assignment: Execute Both Wave 1 Workers

Wave 1 has no dependencies. Execute both workers in sequence.

---

### Worker 1: `worker_schema` (Database Schema Migration)

**Component:** database_schema  
**Estimated time:** 1 hour  
**Output:** `N5/scripts/migrations/content_library_v4_schema.py`

**Task:**
Migrate `N5/data/content_library.db` schema:
1. Rename `type` column to `content_type` (better semantics)
2. Remove CHECK constraint to allow new content types
3. Add new columns: `source_url`, `source_file_path`, `ingested_at`, `word_count`, `has_embedding`
4. Preserve all existing data (127 items: 114 links, 13 snippets)

**Current schema (for reference):**
```sql
CREATE TABLE items (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('link','snippet')),
    content TEXT,
    source TEXT,
    tags TEXT,
    notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deprecated INTEGER DEFAULT 0,
    confidence INTEGER DEFAULT 3,
    has_content INTEGER DEFAULT 0,
    has_summary INTEGER DEFAULT 0
);
```

**Target schema:**
```sql
CREATE TABLE items (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content_type TEXT NOT NULL,  -- No CHECK constraint, allows: link, snippet, article, deck, social-post, podcast, video, book, paper, framework, quote
    content TEXT,
    source TEXT,
    source_url TEXT,             -- NEW: Original URL if from web
    source_file_path TEXT,       -- NEW: Path to file in Knowledge/content-library/
    tags TEXT,
    notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    ingested_at TEXT,            -- NEW: When file was ingested into system
    deprecated INTEGER DEFAULT 0,
    confidence INTEGER DEFAULT 3,
    has_content INTEGER DEFAULT 0,
    has_summary INTEGER DEFAULT 0,
    word_count INTEGER,          -- NEW: For articles/content
    has_embedding INTEGER DEFAULT 0  -- NEW: Tracks if embedded in semantic memory
);
```

**Acceptance criteria:**
- [ ] Existing 127 items preserved with data intact
- [ ] New `content_type` column allows all specified types
- [ ] Migration script is idempotent (can run twice safely)
- [ ] Schema documented in migration script header

**When complete:**
```bash
python3 N5/scripts/build_orchestrator_v2.py complete --project content-library-v4 --worker worker_schema
```

---

### Worker 2: `worker_canonical_paths` (Filesystem Consolidation)

**Component:** filesystem_consolidation  
**Estimated time:** 1 hour  
**Output:** `N5/builds/content-library-v4/move_manifest.json`

**Task:**
Consolidate content storage to single canonical location:

1. **Move all articles:**
   - `Articles/*` → `Knowledge/content-library/articles/`
   - Preserve filenames

2. **Ensure directory structure exists:**
   ```
   Knowledge/content-library/
   ├── articles/
   │   └── vrijen/          # V's authored content (already has 3 Medium articles)
   ├── decks/
   ├── social-posts/
   ├── papers/
   ├── books/
   └── frameworks/
   ```

3. **Protect the directory:**
   - Create `.n5protected` at `Knowledge/content-library/` with reason: "Canonical content storage - do not move or delete"

4. **Document moves:**
   - Create manifest at `N5/builds/content-library-v4/move_manifest.json`

**Current state (for reference):**
```
Articles/                              # 4 files (Zo's save_webpage default)
├── Capital in the 22nd Century...md
├── Recursive Language Models...md     # Just saved today
├── The Art of Finishing...md
└── Understanding the Professional...md

Knowledge/content-library/
├── articles/
│   └── vrijen-medium/                 # 3 of V's Medium articles
│       ├── talent-agent-economy.md
│       └── ...
└── personal/
```

**Acceptance criteria:**
- [ ] `Articles/` directory empty (or removed)
- [ ] All articles now in `Knowledge/content-library/articles/`
- [ ] V's Medium articles remain in `Knowledge/content-library/articles/vrijen/` (rename from `vrijen-medium/`)
- [ ] `.n5protected` exists at `Knowledge/content-library/`
- [ ] Move manifest created with before/after paths

**When complete:**
```bash
python3 N5/scripts/build_orchestrator_v2.py complete --project content-library-v4 --worker worker_canonical_paths
```

---

## Completion Checklist

After both workers are done:

1. [ ] Run `python3 N5/scripts/build_orchestrator_v2.py status --project content-library-v4` to verify Wave 1 complete
2. [ ] Report back: "Wave 1 complete. Ready for Wave 2."

Wave 2 workers (`worker_ingest_script`, `worker_backfill`, `worker_cli_upgrade`) depend on Wave 1 and will be spawned separately.

---

## Reference Files

If you need more context:
- **Full audit:** `file '/home/.z/workspaces/con_5tYCDyhaRiYR0EGI/content-library-system-audit.md'`
- **Build plan:** `file 'N5/builds/content-library-v4/plan.json'`
- **Current DB:** `file 'N5/data/content_library.db'`
- **Current CLI:** `file 'N5/scripts/content_library.py'`
- **v3 capability doc (stale):** `file 'N5/capabilities/internal/content-library-v3.md'`

