# Reflections System

**Purpose:** Automated ingestion, classification, and processing of reflection content from Google Drive

---

## System Overview

```
Google Drive Folder
       ↓
[Worker 1] Drive Integration & Transcription
       ↓
   incoming/  (staged files)
       ↓
[Worker 2] Classification & Tagging
       ↓
[Worker 3] Processing & Synthesis
       ↓
  outputs/  (processed knowledge)
```

---

## Directory Structure

```
N5/records/reflections/
├── .state.json              # State tracking (processed file IDs)
├── incoming/                # Staged files from Drive
│   ├── *.txt               # Text reflections
│   ├── *.m4a               # Audio reflections
│   ├── *.transcript.jsonl  # Audio transcripts
│   └── *.json              # Metadata files
├── processed/               # Classified reflections
├── outputs/                 # Synthesized knowledge
└── README.md               # This file
```

---

## Worker 1: Drive Integration (COMPLETE ✅)

**Script:** `N5/scripts/reflection_ingest_v2.py`

**What it does:**
1. Lists files from Google Drive folder `16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV`
2. Downloads new files (not in `.state.json`)
3. Transcribes audio files using Zo's `transcribe_audio` tool
4. Creates metadata JSON for each file
5. Updates state to prevent re-processing

**Usage:**
```bash
# Normal run (requires Zo execution with Drive API)
python3 N5/scripts/reflection_ingest_v2.py

# Dry-run (show what would be done)
python3 N5/scripts/reflection_ingest_v2.py --dry-run

# Verify system
bash N5/scripts/verify_reflection_ingest.sh
```

**Output:**
- Text files: `.txt` with metadata `.json`
- Audio files: `.m4a` with `.transcript.jsonl` and metadata `.json`

---

## State File (`.state.json`)

Tracks processed files to prevent re-downloading:

```json
{
  "last_run_iso": "2025-10-26T00:51:06.424704Z",
  "processed_file_ids": ["file_id_1", "file_id_2", ...],
  "last_sync_token": null
}
```

---

## Metadata File Format (`.json`)

Each downloaded file has a companion metadata file:

```json
{
  "drive_file_id": "1W_CV9ZQTklugXNjS4HN8OKd6OrVGWee2",
  "original_name": "Oct 24 at 14-46.m4a",
  "downloaded_at_iso": "2025-10-26T00:51:06.424704Z",
  "file_type": "audio",
  "mime_type": "audio/mpeg",
  "size_bytes": 5022677,
  "has_transcript": true,
  "local_path": "/home/workspace/N5/records/reflections/incoming/Oct-24-at-14-46.m4a"
}
```

---

## Current Status

### ✅ Worker 1 Complete
- 9 files downloaded from Drive
- 1 audio file transcribed
- 9 metadata files created
- State tracking active

### ⏳ Worker 2 Pending
- Classification and tagging
- Ready to start

### ⏳ Worker 3 Pending
- Processing and synthesis
- Depends on Worker 2

---

## Verification

Run the verification script to check system health:

```bash
bash /home/workspace/N5/scripts/verify_reflection_ingest.sh
```

Expected output: All checks passed ✅

---

## Files in `incoming/` Directory

**Current Contents:**
- 8 text files (`.txt`)
- 1 audio file (`.m4a`)
- 6 transcripts (`.transcript.jsonl`)
- 9 metadata files (`.json`)

**Total Size:** ~5.2 MB

---

## Principles Applied

- **P5 (Anti-Overwrite):** State tracking prevents re-processing
- **P7 (Dry-Run):** `--dry-run` flag for safe testing
- **P18 (Verify State):** File existence and validity checked
- **P19 (Error Handling):** Comprehensive try/except with logging

---

## Next Steps

1. **Worker 2:** Classify and tag reflections
2. **Worker 3:** Process and synthesize into knowledge artifacts
3. **Automation:** Schedule periodic runs to pull new files

---

**Last Updated:** 2025-10-25 20:51 ET  
**Status:** System operational, Worker 1 complete
