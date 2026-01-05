---
created: 2026-01-04
last_edited: 2026-01-04
version: 1.0
provenance: con_zGQhfwqIoAIKek4Q
---

# Reflection Engine v2 Configuration

## Input Sources

### Primary: SyncThing (Local)
- **Path:** `Inbox/Voice Thoughts/`
- **Sync:** Connected to Google Drive via SyncThing when laptop is open
- **File types:** `.m4a`, `.mp3`, `.wav`, `.txt`

### Fallback: Google Drive
- **Folder ID:** `116Myv-EXxf8P8udqIh_zlbMk2uJtnD90`
- **Folder Name:** Voice Thoughts
- **Account:** attawar.v@gmail.com
- **Use when:** SyncThing not synced (laptop closed)

## Output Location

- **Canonical Path:** `Personal/Reflections/YYYY/MM/`
- **Per-reflection structure:**
  ```
  Personal/Reflections/2026/01/
  └── 2026-01-04_<slug>/
      ├── source.m4a          # Original audio (moved here)
      ├── transcript.md       # Full transcript
      └── analysis.md         # R-blocks output
  ```

## Trigger Methods

1. **Chat:** `@Process Reflection` → checks local folder first, then prompts for input
2. **Text/SMS:** "Process reflection" → fetches from GDrive, runs engine
3. **Direct:** `@Process Reflection [filename or path]` → processes specific file

## Processing Flow

1. **Locate input** (local → GDrive fallback)
2. **Transcribe** (if audio) using AssemblyAI
3. **Classify** content → determine applicable R-blocks
4. **Generate** R-blocks (R01-R09, R00 if needed)
5. **Create output folder** with transcript + analysis
6. **Archive source** (move from input to output folder)
7. **Clean input folder** (remove processed file)

## Google Recorder Naming

Google Recorder typically names files:
- `YYYY-MM-DD_HH_MM_SS.m4a` (timestamp format)
- Or custom title if renamed

The slug is derived from:
1. Custom title if present
2. First 5 words of transcript if timestamp-named

