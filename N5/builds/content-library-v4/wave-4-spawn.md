---
created: 2026-01-09
last_edited: 2026-01-09
version: 1
provenance: con_5tYCDyhaRiYR0EGI
build: content-library-v4
wave: 4
---
# Content Library v4 — Wave 4 Worker Assignment (FINAL)

## Context

You are executing Wave 4 (final wave) of the Content Library v4 redesign.

**Completed:**
- ✅ Wave 1: Schema migrated, files consolidated to `Knowledge/content-library/`
- ✅ Wave 2: Ingest pipeline created, backfill complete, CLI upgraded
- ✅ Wave 3: Semantic memory fixed, auto-ingest rule created

**Current state:**
- 138 items in DB (114 links, 13 snippets, 10 articles, 1 social-post)
- All articles have `source_file_path` set
- V's 3 Medium articles tagged `vrijen-authored`
- CLI commands: `list-types`, `search`, `ingest`, `sync`
- Auto-ingest rule active: saves to `Articles/` → auto-moved to `Knowledge/content-library/articles/`
- Semantic memory profile `content-library` points to correct path

**Build workspace:** `file 'N5/builds/content-library-v4/'`  
**Orchestrator:** `python3 N5/scripts/build_orchestrator_v2.py`

---

## Your Assignment: Execute Wave 4 Workers (2 total)

Both workers can run in sequence (docs first, then cleanup).

---

### Worker 1: `worker_docs_update` (Documentation)

**Component:** documentation  
**Estimated time:** 1.5 hours  
**Output:** Updated docs across multiple locations

**Task:**
Update ALL documentation to reflect the new Content Library v4 system.

**Files to update:**

1. **Capability doc (PRIMARY):** `file 'N5/capabilities/internal/content-library-v3.md'`
   - Rename to `content-library-v4.md`
   - Update to reflect actual current state
   - Document the new schema, paths, and workflows
   - Remove references to aspirational features that don't exist

2. **System guide:** `file 'Documents/System/guides/content-library-system.md'`
   - Update to match v4 reality
   - Include CLI command reference
   - Include auto-ingest workflow

3. **Quarantine old docs:**
   - Move stale v1/v2 docs to `N5/quarantine/deprecated-content-library/`
   - Include timestamp in quarantine folder name

**New capability doc structure:**
```markdown
---
created: 2025-12-02
last_edited: 2026-01-09
version: 4.0
provenance: content-library-v4-build
---

# Content Library v4

## Overview
Single source of truth for saved content: articles, links, snippets, social posts, etc.

## Architecture
- **Database:** N5/data/content_library.db
- **Content storage:** Knowledge/content-library/
- **CLI:** N5/scripts/content_library.py
- **Ingest:** N5/scripts/content_ingest.py

## Content Types
- article, link, snippet, social-post, deck, podcast, video, book, paper, framework, quote

## Workflows
### Save an article
1. `save_webpage <url>` → auto-triggers ingest rule
2. File moves to Knowledge/content-library/articles/
3. DB record created with metadata

### Manual ingest
`python3 N5/scripts/content_ingest.py <file> --type article --move`

### Search
`python3 N5/scripts/content_library.py search --type article --query "RLM"`

### Sync all files to DB
`python3 N5/scripts/content_library.py sync`

## Schema
(document current schema from migration script)

## Integration Points
- Semantic memory: `content-library` profile
- Auto-ingest rule: triggers after save_webpage
- Global index: files indexed by n5_index_rebuild.py
```

**Acceptance criteria:**
- [ ] `N5/capabilities/internal/content-library-v4.md` exists with accurate content
- [ ] Old v3 doc moved to quarantine
- [ ] `Documents/System/guides/content-library-system.md` updated
- [ ] All paths, commands, and schema descriptions accurate
- [ ] No references to non-existent features or paths

**When complete:**
```bash
python3 N5/scripts/build_orchestrator_v2.py complete --project content-library-v4 --worker worker_docs_update
```

---

### Worker 2: `worker_cleanup` (Final Verification)

**Component:** cleanup  
**Estimated time:** 1 hour  
**Output:** Verification report

**Task:**
Final cleanup and comprehensive verification of the entire Content Library v4 system.

**Verification checklist:**

1. **Database integrity:**
   ```bash
   sqlite3 N5/data/content_library.db "PRAGMA integrity_check;"
   sqlite3 N5/data/content_library.db "SELECT COUNT(*), content_type FROM items GROUP BY content_type;"
   ```

2. **File-DB consistency:**
   - Every file in `Knowledge/content-library/articles/` has a DB record
   - Every DB record with `source_file_path` points to existing file

3. **CLI functionality:**
   ```bash
   python3 N5/scripts/content_library.py list-types
   python3 N5/scripts/content_library.py search --type article
   python3 N5/scripts/content_library.py stats
   ```

4. **Semantic memory:**
   ```bash
   python3 -c "
   from N5.cognition.n5_memory_client import N5MemoryClient
   client = N5MemoryClient()
   results = client.search_profile('content-library', 'recursive language', limit=3)
   print('Found:', len(results), 'results')
   "
   ```

5. **Auto-ingest rule:**
   - Verify rule exists: check Zo rules for content ingest
   - Document rule ID for future reference

6. **Cleanup tasks:**
   - Remove any empty directories
   - Ensure `Articles/` directory removed (all content migrated)
   - Verify `.n5protected` on `Knowledge/content-library/`

**Generate verification report:**
Create `N5/builds/content-library-v4/verification_report.md` with:
- All checks passed/failed
- Final item counts by type
- Any remaining issues
- Recommendations for future improvements

**Acceptance criteria:**
- [ ] All verification checks pass
- [ ] verification_report.md created with comprehensive results
- [ ] No orphaned files or DB records
- [ ] Build can be marked fully complete

**When complete:**
```bash
python3 N5/scripts/build_orchestrator_v2.py complete --project content-library-v4 --worker worker_cleanup
```

---

## After Wave 4

When both workers complete:

1. Run final status check:
   ```bash
   python3 N5/scripts/build_orchestrator_v2.py status --project content-library-v4
   ```

2. All 9 workers should show `completed`

3. Report back to orchestrator thread:
   > "Content Library v4 build complete. 9/9 workers done. System verified and documented."

4. The build is then officially closed.

---

## Reference Files

- **Build plan:** `file 'N5/builds/content-library-v4/plan.json'`
- **Migration script:** `file 'N5/scripts/migrations/content_library_v4_schema.py'`
- **Ingest script:** `file 'N5/scripts/content_ingest.py'`
- **Backfill script:** `file 'N5/scripts/content_backfill.py'`
- **CLI:** `file 'N5/scripts/content_library.py'`
- **Memory client:** `file 'N5/cognition/n5_memory_client.py'`
- **Database:** `file 'N5/data/content_library.db'`
- **Content location:** `file 'Knowledge/content-library/'`
- **Current capability doc:** `file 'N5/capabilities/internal/content-library-v3.md'`
- **System guide:** `file 'Documents/System/guides/content-library-system.md'`

