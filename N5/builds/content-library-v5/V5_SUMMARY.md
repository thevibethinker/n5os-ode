---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_GwpdTRRuFJGuT9Qv
---

# Content Library v5 — Release Summary

**Build Slug:** `content-library-v5`  
**Completed:** 2026-01-19  
**Orchestrator:** con_GiPSVev8LxpKdAcO

---

## What Changed in v5

### 1. Subtypes for Hierarchical Classification
- Added `subtype` column to database schema
- Links can now be classified as: `tool`, `product`, `resource`, `profile`, `scheduling-link`
- Enables more precise queries (e.g., "find all scheduling links")

### 2. Normalization Pipeline
- **trafilatura extraction** for clean article text from HTML companions
- **Heuristic boilerplate stripping** removes navigation, subscribe boxes, cookie banners
- **Summary generation** creates 2-3 sentence summaries in frontmatter
- Two standards:
  - **Standard A (articles):** Heavy normalization
  - **Standard B (social posts):** Light stripping, preserve voice

### 3. Calendly DB Sync
- `sync_links.py` now writes directly to content_library.db
- Merge-safe enrichment: automation fills defaults, curated fields never overwritten
- 18 Calendly links synced with `subtype: scheduling-link`

### 4. Migration & Deduplication
- Resolved 9 URL duplicates using ID redirect system
- Deprecated 14 legacy items
- Backfilled subtypes for 24 items
- `id_redirects` table enables graceful old-ID lookups

### 5. Auto-Ingest Enhancement
- User rule updated to remove explicit `--type article`
- Auto-detection now classifies content by URL patterns
- `--normalize` flag on by default (can disable with `--no-normalize`)

---

## Migration Steps Completed

| Step | Description | Status |
|------|-------------|--------|
| 1 | Schema migration (subtype, summary columns) | ✅ |
| 2 | Calendly sync with DB upsert | ✅ |
| 3 | URL deduplication (9 resolved) | ✅ |
| 4 | ID redirects table populated | ✅ |
| 5 | Subtype backfill (24 items) | ✅ |
| 6 | Normalization functions implemented | ✅ |
| 7 | Auto-ingest rule updated | ✅ |
| 8 | Documentation updated to v5 | ✅ |

---

## Known Limitations

1. **CLI `--subtype` flag not implemented**
   - Subtype data exists in DB, searchable via SQL
   - CLI search command doesn't yet expose `--subtype` filter
   - Workaround: `sqlite3 N5/data/content_library.db "SELECT * FROM items WHERE subtype='scheduling-link'"`

2. **Normalization requires HTML companion**
   - trafilatura extraction only works when HTML file exists alongside markdown
   - save_webpage creates both; manual ingestion may lack HTML

3. **Summary generation is heuristic**
   - Uses first-substantive-paragraph extraction
   - LLM-based summarization could improve quality (deferred)

4. **Social post fallback**
   - trafilatura often fails on JS-rendered content (X/Twitter, LinkedIn)
   - Heuristic stripping used as fallback

---

## Future Improvements (Deferred)

| Enhancement | Description | Priority |
|-------------|-------------|----------|
| CLI subtype filter | Add `--subtype` flag to `content_library.py search` | Medium |
| LLM summarization | Use Claude/GPT for better summaries | Low |
| Embedding generation | Auto-generate embeddings on ingest | Medium |
| Scheduled content refresh | Periodic re-fetch of mutable content | Low |
| UI for curated fields | Web interface for editing Calendly context | Low |

---

## Verification Results

| Test | Result |
|------|--------|
| Calendly sync dry-run | ✅ 18 files, all with scheduling-link subtype |
| URL duplicates check | ✅ No duplicates (empty result) |
| Subtype query | ✅ 18 scheduling-links, 6 trial-codes |
| Normalization functions | ✅ Heuristic stripping and summary generation work |
| trafilatura import | ✅ v2.0.0 available |
| Auto-ingest rule | ✅ Updated, removes `--type article` |

---

## File Changes

### Modified
- `N5/scripts/content_ingest.py` — normalization pipeline
- `N5/scripts/content_library.py` — subtype support in schema
- `N5/data/content_library.db` — schema migration
- `Integrations/calendly/sync_links.py` — DB upsert
- `Documents/System/guides/content-library-system.md` — v5 docs

### Created
- `N5/scripts/content_backfill.py` — bulk sync tool
- `id_redirects` table in content_library.db

---

## References

- **System Guide:** `file 'Documents/System/guides/content-library-system.md'`
- **Build Folder:** `file 'N5/builds/content-library-v5/'`
- **Worker Completions:** `file 'N5/builds/content-library-v5/completions/'`

---

*Content Library v5 — Shipped 2026-01-19*
