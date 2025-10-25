# Worker 1: Drive Integration & Transcription

**Mission:** Pull files from Drive folder, transcribe audio, stage for processing  
**Time Estimate:** 45 minutes  
**Dependencies:** None (can start immediately)  
**Parallelizable:** Yes (with Worker 2)

---

## Objectives

1. ✅ Pull new files from Drive folder `16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV`
2. ✅ Download to `N5/records/reflections/incoming/`
3. ✅ Auto-transcribe audio files (mp3, m4a, wav, opus)
4. ✅ Track processed file IDs in `N5/.state/reflection_drive_state.json`
5. ✅ Idempotent: never re-process same file
6. ✅ Support `--dry-run` flag

---

## Deliverables

### Primary
- `N5/scripts/reflection_ingest_v2.py` - Drive polling + transcription script
- `N5/.state/reflection_drive_state.json` - State tracker (create if missing)

### Secondary
- Error handling for Drive API failures
- Logging with timestamps
- Exit codes (0 = success, 1 = error)

---

## Technical Requirements

### Script: `reflection_ingest_v2.py`

**Functionality:**
```python
# 1. Load state file
state = load_state("N5/.state/reflection_drive_state.json")

# 2. Query Drive folder for new files
new_files = drive.list_files(
    folder_id="16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV",
    exclude_ids=state["processed_files"].keys()
)

# 3. Download each file
for file in new_files:
    download_to("N5/records/reflections/incoming/", file)
    
    # 4. Transcribe if audio
    if is_audio(file):
        transcribe_audio(file)
        # Creates .transcript.jsonl alongside
    
    # 5. Update state
    state["processed_files"][file.id] = {
        "name": file.name,
        "processed_at": now(),
        "mime_type": file.mime_type
    }

# 6. Save state
save_state(state)
```

**Supported File Types:**
- Text: `.txt`, `.md`
- Documents: `.docx`, `.gdoc` (export as txt)
- Audio: `.mp3`, `.m4a`, `.wav`, `.opus` (transcribe)

**State File Format:**
```json
{
  "last_poll": "2025-10-24T18:00:00Z",
  "processed_files": {
    "1aBC123xyz": {
      "name": "2025-10-24-pricing-strategy.txt",
      "processed_at": "2025-10-24T18:05:00Z",
      "mime_type": "text/plain",
      "transcribed": false
    },
    "2dEF456abc": {
      "name": "2025-10-23-market-thoughts.m4a",
      "processed_at": "2025-10-24T18:07:00Z",
      "mime_type": "audio/mp4",
      "transcribed": true,
      "transcript_file": "N5/records/reflections/incoming/2025-10-23-market-thoughts.m4a.transcript.jsonl"
    }
  }
}
```

---

## Drive API Integration

### Use Existing Google Drive App Tool

```python
from use_app_google_drive import list_files, download_file

# List new files
files = use_app_google_drive(
    tool_name="google_drive-list-files",
    configured_props={
        "folderId": "16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV",
        "pageSize": 100,
        "trashed": False
    }
)

# Download file
use_app_google_drive(
    tool_name="google_drive-download-file",
    configured_props={
        "fileId": file_id
    },
    download_path=f"/home/workspace/N5/records/reflections/incoming/{filename}"
)
```

---

## Transcription Integration

### Use Existing Transcription Tools

```python
import subprocess

def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio file, return path to .transcript.jsonl"""
    result = subprocess.run(
        ["python3", "/home/workspace/N5/scripts/transcribe_helper.py", audio_path],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise Exception(f"Transcription failed: {result.stderr}")
    
    # Transcript saved as {audio_path}.transcript.jsonl
    return f"{audio_path}.transcript.jsonl"
```

**Note:** Check if `transcribe_helper.py` exists, if not, use Zo's built-in transcription:

```python
# Alternative: Use Zo's transcribe_audio tool directly
# (This will be called by the orchestrator, not the script)
```

---

## Error Handling

### Drive API Errors
- **403 Forbidden:** Log error, skip file, continue
- **404 Not Found:** Log warning, continue
- **500 Server Error:** Retry 3x with exponential backoff, then fail

### Transcription Errors
- **File too large:** Log error, save file without transcript
- **Unsupported format:** Log error, save file as-is
- **API failure:** Retry 2x, then log error and continue

### File System Errors
- **Disk full:** Exit with code 1, log critical error
- **Permission denied:** Exit with code 1, log critical error

---

## Logging Format

```
2025-10-24T18:05:00Z INFO Starting Drive poll
2025-10-24T18:05:02Z INFO Found 3 new files
2025-10-24T18:05:03Z INFO Downloading: 2025-10-24-pricing-strategy.txt
2025-10-24T18:05:04Z INFO Downloading: 2025-10-23-market-thoughts.m4a
2025-10-24T18:05:05Z INFO Transcribing: 2025-10-23-market-thoughts.m4a
2025-10-24T18:05:45Z INFO Transcription complete: 2025-10-23-market-thoughts.m4a.transcript.jsonl
2025-10-24T18:05:46Z INFO Updated state: 3 files processed
2025-10-24T18:05:46Z INFO ✓ Complete: 3 new reflections ingested
```

---

## CLI Usage

```bash
# Normal run
python3 /home/workspace/N5/scripts/reflection_ingest_v2.py

# Dry-run (shows what would be downloaded)
python3 /home/workspace/N5/scripts/reflection_ingest_v2.py --dry-run

# Force re-download specific file
python3 /home/workspace/N5/scripts/reflection_ingest_v2.py --force-file-id 1aBC123xyz
```

---

## Testing Checklist

- [ ] Dry-run shows new files without downloading
- [ ] Downloads text files correctly
- [ ] Downloads audio files correctly
- [ ] Transcribes audio files (creates .transcript.jsonl)
- [ ] Updates state file after each file
- [ ] Doesn't re-download already processed files
- [ ] Handles Drive API errors gracefully
- [ ] Handles transcription errors gracefully
- [ ] Logs all actions with timestamps
- [ ] Exit code 0 on success, 1 on critical failure

---

## Principles Applied

- **P0 (Rule-of-Two):** Only load state file + Drive API, minimal context
- **P2 (SSOT):** State file is single source of truth for processed files
- **P5 (Anti-Overwrite):** Never re-process files already in state
- **P7 (Dry-Run):** Support `--dry-run` flag
- **P11 (Failure Modes):** Graceful degradation on API errors
- **P15 (Complete Before Claiming):** Only update state after successful download
- **P18 (Verify State):** Verify file exists before marking as processed
- **P19 (Error Handling):** Comprehensive error handling with retries

---

## Success Criteria

Worker 1 is complete when:
1. Script pulls new files from Drive folder
2. Audio files are transcribed automatically
3. State tracking prevents re-processing
4. Dry-run flag works
5. Error handling covers all failure modes
6. Logging is comprehensive
7. All tests pass

---

**Status:** Ready to start  
**Created:** 2025-10-24 18:08 ET
