# Worker 1: Schema & Foundation - Content Library Media Extension

**Goal:** Update the Content Library database schema to support media files and create the necessary directory structure.

## Context
We are extending Content Library v4 (items table) to support media.
Existing DB: `/home/workspace/N5/data/content_library.db`
Current columns: id, title, content_type, content, url, source, source_url, source_file_path, tags, notes, created_at, updated_at, ingested_at, deprecated, expires_at, version, last_used_at, confidence, has_content, has_summary, word_count, has_embedding.

## Tasks

### 1. Schema Migration Script
Create `/home/workspace/N5/scripts/content_library_media_migrate.py`.
This script should:
- Connect to `/home/workspace/N5/data/content_library.db`
- Add the following columns to the `items` table if they don't exist:
  - `file_path TEXT` (canonical path in Knowledge/content-library/)
  - `mime_type TEXT` (e.g. audio/mpeg, video/mp4)
  - `duration_seconds INTEGER`
  - `dimensions TEXT` (e.g. "1920x1080" for video/images)
  - `transcript_path TEXT` (path to .transcript.jsonl file)
  - `media_metadata TEXT` (JSON blob for extra technical details)
- Ensure execution is idempotent (checks if column exists before adding).
- Log success/failure to stdout.

### 2. Media Taxonomy Setup
In the same migration script (or a separate function within it):
- Add canonical tags to the `tags` table (if your system uses a separate tags table, otherwise just define them as standard constants in a python file for the ingest worker).
- **Taxonomy to support:**
  - Types: `audio`, `video`, `image`, `podcast`, `webinar`, `presentation-recording`
  - Sources: `meeting-recording`, `loom`, `youtube`, `podcast-feed`, `voice-memo`
  - Status: `needs-transcription`, `transcribed`, `reviewed`

### 3. Directory Structure
Create the following directory structure (use `pathlib.Path.mkdir(parents=True, exist_ok=True)`):
- `/home/workspace/Knowledge/content-library/audio`
- `/home/workspace/Knowledge/content-library/video`
- `/home/workspace/Knowledge/content-library/images`
- `/home/workspace/Knowledge/content-library/transcripts`

### 4. Execution
- Run the migration script.
- Verify schema changes using `sqlite3`.

## deliverable
- `/home/workspace/N5/scripts/content_library_media_migrate.py`
- Verified schema update on `content_library.db`
- Created directories.
- `WORKER_1_COMPLETE.md` with summary.

