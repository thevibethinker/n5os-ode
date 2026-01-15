# Content Library Media Extension - Orchestrator

**Orchestrator Thread:** con_oLxcuAiX3K6tbxBL
**Created:** 2026-01-13 18:00 ET
**Status:** READY FOR EXECUTION

---

## Project Summary

Extend Content Library v4 to support media files (audio, video, images) alongside existing article/document tracking. This is an **extension** of the working system, not a parallel build.

**Why this approach (not the old `media-documents-system`):**
- Content Library v4 already exists and works (`content_library.db` with items/metadata/tags)
- Extending is cleaner than creating a parallel `media_documents.db`
- Existing `content_ingest.py` provides the pattern to follow

---

## Current State

**Exists:**
- `/home/workspace/N5/data/content_library.db` — working DB with items, metadata, tags tables
- `/home/workspace/N5/scripts/content_ingest.py` — article ingestion script
- `/home/workspace/Knowledge/content-library/articles/` — article storage
- 3 older scripts: `documents_media_db_init.py`, `documents_media_migrate_v1.1.py`, `documents_media_query.py` (partial work, can reference)

**Needs to be built:**
- Schema migration adding media columns
- Media-specific taxonomy tags  
- Media ingest workflow
- Directory structure for media storage
- Integration with meeting system (transcripts → media library)

---

## Worker Assignments

### Worker 1: Schema & Foundation (45 min)
**File:** `WORKER_1_SCHEMA.md`

**Deliverables:**
1. Schema migration script: `/home/workspace/N5/scripts/content_library_media_migrate.py`
   - Add to `items` table: `file_path TEXT`, `mime_type TEXT`, `duration_seconds INTEGER`, `dimensions TEXT`, `transcript_path TEXT`
   - Add to `tags` table: media-specific taxonomy (see below)
   - Preserve all existing data

2. Media taxonomy tags (insert into tags table):
   - Types: `audio`, `video`, `image`, `podcast`, `webinar`, `presentation-recording`
   - Sources: `meeting-recording`, `loom`, `youtube`, `podcast-feed`, `voice-memo`
   - Status: `needs-transcription`, `transcribed`, `reviewed`

3. Directory structure:
   ```
   Knowledge/content-library/
   ├── articles/     (existing)
   ├── audio/        (new)
   ├── video/        (new)
   ├── images/       (new)
   └── transcripts/  (new)
   ```

**Success criteria:**
- Migration runs without data loss
- `sqlite3 content_library.db '.schema items'` shows new columns
- Tags queryable: `SELECT * FROM tags WHERE name LIKE 'audio%'`
- All directories created

---

### Worker 2: Media Ingest (60 min)
**File:** `WORKER_2_INGEST.md`

**Deliverables:**
1. Extend `/home/workspace/N5/scripts/content_ingest.py` OR create `/home/workspace/N5/scripts/media_ingest.py`
   - Accept: file path, URL, or meeting folder
   - Detect media type from MIME/extension
   - Extract metadata: duration (ffprobe), dimensions (for images/video)
   - Move to canonical location (audio/, video/, images/)
   - Create DB record with proper tags
   - Handle transcripts: if `.transcript.jsonl` exists alongside, link it

2. Batch ingest script: `/home/workspace/N5/scripts/media_batch_ingest.py`
   - Scan a directory for media files
   - Ingest all with `--dry-run` support
   - Report: X files found, Y ingested, Z skipped (duplicates)

3. Meeting transcript linker:
   - Given a meeting folder, find recordings + transcripts
   - Ingest recordings, link to transcripts
   - Tag with `meeting-recording` + meeting metadata

**Success criteria:**
- `media_ingest.py /path/to/video.mp4` creates record + moves file
- `media_batch_ingest.py --dry-run /path/to/folder` reports correctly
- Meeting recordings linked to transcripts

---

### Worker 3: Query & Integration (45 min)
**File:** `WORKER_3_INTEGRATION.md`

**Deliverables:**
1. Update `/home/workspace/N5/scripts/content_query.py` (or create if missing):
   - `--type audio|video|image|article|all`
   - `--source meeting|loom|youtube|etc`
   - `--needs-transcription` flag
   - Output: table or JSON

2. Prompt update: `/home/workspace/Prompts/Knowledge Find.prompt.md`
   - Document new media query capabilities
   - Examples for common queries

3. Integration test suite: `/home/workspace/N5/scripts/test_content_library_media.py`
   - Test schema
   - Test ingest (with temp file)
   - Test query filters
   - Test transcript linking

**Success criteria:**
- `content_query.py --type audio` returns only audio
- Prompt updated with examples
- Tests pass

---

## Execution Order

```
Worker 1 (Schema) ──▶ Worker 2 (Ingest) ──▶ Worker 3 (Integration)
     │                      │
     └── blocks ────────────┘
```

Workers 2 and 3 depend on Worker 1 completing first.
Workers 2 and 3 can run in parallel after Worker 1.

---

## Spawn Commands

**Worker 1:**
```
Open new thread. Read file 'N5/builds/content-library-media-extension/WORKER_1_SCHEMA.md' and execute.
```

**Worker 2:** (after Worker 1 completes)
```
Open new thread. Read file 'N5/builds/content-library-media-extension/WORKER_2_INGEST.md' and execute.
```

**Worker 3:** (after Worker 1 completes, can parallel with Worker 2)
```
Open new thread. Read file 'N5/builds/content-library-media-extension/WORKER_3_INTEGRATION.md' and execute.
```

---

## Reporting

Workers report back by creating `WORKER_N_COMPLETE.md` in this build directory with:
- Deliverables completed (with file paths)
- Test results
- Any blockers or deviations
- Time taken

Orchestrator (this thread) monitors and coordinates.

---

## Reference: Existing Scripts to Study

- `/home/workspace/N5/scripts/content_ingest.py` — pattern for ingest workflow
- `/home/workspace/N5/scripts/documents_media_db_init.py` — schema ideas (separate tables approach, not used)
- `/home/workspace/N5/scripts/documents_media_query.py` — query patterns

---

*Created: 2026-01-13 18:00 ET*

