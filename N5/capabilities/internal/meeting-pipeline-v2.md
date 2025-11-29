---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Meeting Pipeline v2

```yaml
capability_id: meeting-pipeline-v2
name: "Meeting Pipeline v2 – Transcript → Intelligence → Archive"
category: internal
status: active
confidence: high
last_verified: 2025-11-29
tags:
  - meetings
  - intelligence
  - pipeline
  - blocks
entry_points:
  - type: script
    id: "N5/scripts/meeting_pipeline/transcript_processor_v4.py"
  - type: script
    id: "N5/scripts/meeting_pipeline/finalize_meeting_intelligence.py"
  - type: script
    id: "N5/scripts/meeting_pipeline/archive_completed_meetings.py"
  - type: script
    id: "N5/scripts/meeting_pipeline/health_scanner.py"
  - type: agent
    id: "76b56ced-8931-46c3-8164-ee89ae9c650b"  # Daily Meeting System Health
owner: "V"
```

## What This Does

The meeting pipeline is the end-to-end system that turns raw meeting transcripts (primarily from Google Drive) into structured intelligence blocks, updates the meeting lifecycle database, and archives completed meetings into `Personal/Meetings/Archive/` on a reliable cadence.

It owns detection of new meetings, AI block generation, lifecycle status tracking in SQLite, health checks, and automated archive of `[C]` (complete) meetings.

## How to Use It

### Normal, fully-automated mode

In steady state, this system is driven by Zo scheduled tasks and does not require manual intervention:

- **Inbox / Detection orchestrator (Zo agent)** pulls `.transcript.md` files from Google Drive into `Personal/Meetings/Inbox/` using `use_app_google_drive`.
- **Transcript processor** (`transcript_processor_v4.py`) scans Inbox, detects new/changed meetings, and queues AI requests.
- **AI processing tasks** generate B-blocks and responses.
- **Finalization** (`finalize_meeting_intelligence.py` + `response_handler.py`) marks meetings complete, updates `meeting_pipeline.db`, and writes intelligence blocks.
- **Archive automation** (`archive_completed_meetings.py`) moves `[C]` meetings into the correct quarterly archive.

### Common manual operations

From `/home/workspace`:

```bash
# Force process all Inbox transcripts → queue for AI
python3 N5/scripts/meeting_pipeline/transcript_processor_v4.py

# Check system health
python3 N5/scripts/meeting_pipeline/health_scanner.py

# Find duplicate meetings
python3 N5/scripts/meeting_pipeline/duplicate_detector_v2.py

# Manually run C-state archive (MG-7C)
python3 N5/scripts/meeting_pipeline/archive_completed_meetings.py

# Mark a processed meeting as C-state (ready for archive)
python3 N5/scripts/meeting_pipeline/mark_meeting_c_state.py 2025-11-20_laurensalitangmailcom
```

### When something looks wrong

- **No new meetings detected** – Confirm `.transcript.md` files exist under `file 'Personal/Meetings/Inbox/'`; run `transcript_processor_v4.py` and inspect output.
- **C-state meeting not archiving** – Check that the folder name ends with `_[C]`, not `_[P]`, and manually run `archive_completed_meetings.py`.
- **Google Drive issues** – Ensure the Zo scheduled task that pulls Drive transcripts is active in [Agents](/agents); the pipeline expects local `.transcript.md` files, not to call Drive directly from Python.

## Associated Files & Assets

### Databases & data folders

- `file 'N5/data/meeting_pipeline.db'` – Primary lifecycle DB (`meetings`, `blocks`, `feedback` tables).
- `file 'N5/data/block_registry.db'` – Block work queue and completed blocks for meetings and other pipelines.
- `file 'N5/data/executables.db'` – Registry of block generation tools (15+ block generators + selector).
- `file 'N5/data/meeting_pipeline'` – Staging and temporary data for meeting processing.
- `file 'N5/runtime/meeting_pipeline'` – Runtime markers / flags used by scheduled jobs.

### Scripts (core pipeline)

- `file 'N5/scripts/meeting_pipeline/transcript_processor_v4.py'` – Detects new Inbox transcripts, normalizes paths, and queues AI requests.
- `file 'N5/scripts/meeting_pipeline/finalize_meeting_intelligence.py'` – Marks meetings complete and registers outputs in the DB.
- `file 'N5/scripts/meeting_pipeline/response_handler.py'` – Handles AI responses and ties them back to meeting records.
- `file 'N5/scripts/meeting_pipeline/block_selector.py'` – Selects which B-blocks to generate per meeting.
- `file 'N5/scripts/meeting_pipeline/queue_manager.py'` – Queue management and prioritization.
- `file 'N5/scripts/meeting_pipeline/archive_completed_meetings.py'` – MG-7C archive automation.
- `file 'N5/scripts/meeting_pipeline/health_scanner.py'` – Daily health checks and summary reports.

### Configuration & prompts

- `file 'N5/scripts/meeting_pipeline/README.md'` – Canonical architecture description and operational notes.
- `file 'N5/scripts/meeting_pipeline/ARCHIVE_AUTOMATION.md'` – Details for MG-7C archive behavior.
- `file 'N5/orchestration/meeting-pipeline-v2-BUILD/BUILD_PLAN_FINAL.md'` – Original build plan.
- `file 'N5/orchestration/meeting-pipeline-v2-BUILD/FINAL_STATUS.md'` – Final architecture & edge cases.
- `file 'N5/prompts/blocks'` – B-block prompt library referenced by block selector and generators.

### Entry/exit folders

- `file 'Personal/Meetings/Inbox/'` – Meeting Inbox, primary entrypoint for `.transcript.md` files.
- `file 'Personal/Meetings/'` – Canonical SSOT for active meeting folders.
- `file 'Personal/Meetings/Archive/'` – Final home for `[C]` meetings, partitioned as `{YYYY}-Q{Q}/`.
- `file 'N5/inbox/ai_requests/'` – JSON AI request queue (meeting_* payloads).

## Workflow

### High-level flow

```mermaid
flowchart TD
  A[Google Drive transcripts
  + manual uploads] --> B[Personal/Meetings/Inbox/]
  B --> C[transcript_processor_v4.py
  - detect & normalize]
  C --> D[Queue in
  meeting_pipeline.db
  + ai_requests/]
  D --> E[Zo AI tasks
  - generate B-blocks]
  E --> F[finalize_meeting_intelligence.py
  + response_handler.py]
  F --> G[Meeting folders updated
  + status=complete]
  G --> H[mark_meeting_c_state.py
  folder suffix _[C]]
  H --> I[archive_completed_meetings.py
  → Personal/Meetings/Archive/YYYY-Q/]
```

### Database lifecycle

1. **Detection** – New Inbox folders and transcripts registered in `meetings` with `status='detected'`.
2. **Queueing** – `transcript_processor_v4.py` moves meetings to `queued_for_ai`, creates JSON requests.
3. **Processing** – AI runs block generators; `blocks` table accumulates B01–B31 outputs.
4. **Completion** – `finalize_meeting_intelligence.py` moves rows to `status='complete'` once required blocks are present.
5. **Archival** – When folders are renamed to `_[C]`, MG-7C sets `status='complete'` and moves the folder into Archive.

## Notes / Gotchas

- **Subprocess → tools is forbidden.** Legacy scripts that tried to call Zo tools (e.g. `gdrive_transcript_fetcher.py`, `pipedream_helper.py`) are explicitly deprecated; orchestration must happen from Zo scheduled tasks.
- **C-state naming is authoritative.** Archive automation depends entirely on the `_[C]` suffix; mismatched naming will strand meetings in Inbox.
- **Duplicate handling:** Duplicate detection/merging is handled by dedicated scripts (`duplicate_detector_v2.py`, `merge_meetings_v2.py`) and conventions like "_2" suffix; rely on these instead of manual folder surgery.
- **Health first:** When something looks off, run `health_scanner.py` and inspect `meeting_pipeline.db` before touching files manually.

