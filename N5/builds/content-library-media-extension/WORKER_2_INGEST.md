# Worker 2: Media Ingest - Content Library Media Extension

**Goal:** Create ingestion tools for media files that populate the updated Content Library.

## Context
Worker 1 has added media columns to `content_library.db`.
Existing ingest script: `/home/workspace/N5/scripts/content_ingest.py`.
We need to handle media files, extracting metadata like duration and linking transcripts.

## Tasks

### 1. Media Ingest Script
Create `/home/workspace/N5/scripts/media_ingest.py`.
(Alternatively, extend `content_ingest.py` if it's cleaner, but a dedicated script is often safer to start).

**Requirements:**
- **Input:** File path to a media file (audio/video/image).
- **Metadata Extraction:**
  - Use `ffprobe` (via `subprocess`) to get duration, dimensions, and mime type.
  - `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 <file>`
- **Transcript Linking:**
  - Check if a `.transcript.jsonl` file exists next to the source file (e.g., `foo.mp3` -> `foo.mp3.transcript.jsonl`).
  - If yes, read it to get text content for the `content` column (or a summary/snippet) and store the path in `transcript_path`.
  - If no, tag as `needs-transcription`.
- **File Handling:**
  - Copy/Move file to canonical location: `/home/workspace/Knowledge/content-library/<type>/`.
  - Use a UUID-based filename or clean slug to avoid collisions.
- **DB Insertion:**
  - Insert into `items` table.
  - `content_type` = 'audio', 'video', or 'image'.
  - `file_path` = new canonical path.
  - `source_file_path` = original path.

### 2. Batch Ingest Script
Create `/home/workspace/N5/scripts/media_batch_ingest.py`.
- **Input:** Directory path.
- **Logic:**
  - Recursively find media files (mp3, m4a, mp4, mov, png, jpg, etc.).
  - Call `media_ingest.py` logic for each.
  - Support `--dry-run`.
  - Skip files already in DB (check by hash or source path).

### 3. Execution
- Test with a dummy media file (you can create a text file and name it .mp3 for basic path testing, or ask Orchestrator for a real file).
- Verify DB record creation.

## Deliverable
- `/home/workspace/N5/scripts/media_ingest.py`
- `/home/workspace/N5/scripts/media_batch_ingest.py`
- `WORKER_2_COMPLETE.md` with summary.

