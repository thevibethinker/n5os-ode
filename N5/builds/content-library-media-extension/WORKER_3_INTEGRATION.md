# Worker 3: Integration & Query - Content Library Media Extension

**Goal:** Update query tools and system prompts to expose the new media capabilities.

## Context
Media files are now in the Content Library. We need to be able to find them and use them.

## Tasks

### 1. Update Query Script
Update or create `/home/workspace/N5/scripts/content_query.py`.
- Ensure it can filter by the new `content_type` values (audio, video).
- Add support for filtering by `needs-transcription` tag (useful for finding work to do).
- Display duration/dimensions in output if available.

### 2. Update Prompts
Update `/home/workspace/Prompts/Knowledge Find.prompt.md` (and others if relevant).
- Add examples of searching for media.
  - "Find audio recordings about X"
  - "Show me video content from last week"
- Explain that transcripts are linked and searched automatically.

### 3. Integration Tests
Create `/home/workspace/N5/scripts/test_content_library_media.py`.
- A simple python script using `unittest`.
- Test:
  - DB connection and schema check.
  - Insertion of a mock media record.
  - Query retrieval of that record.
  - Clean up mock data.

## Deliverable
- Updated `content_query.py`
- Updated Prompts
- `test_content_library_media.py`
- `WORKER_3_COMPLETE.md` with summary.

