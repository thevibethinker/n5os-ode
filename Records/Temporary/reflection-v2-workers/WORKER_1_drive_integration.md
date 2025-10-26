# Worker 1: Drive Integration & Transcription

**Mission:** Pull files from Drive folder, transcribe audio, stage for processing  
**Time Estimate:** 45 minutes  
**Dependencies:** None (can start immediately)  
**Parallelizable:** Yes (with Worker 2)

---

## Objectives

1. ✅ Pull new files from Drive folder `16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV`
2. ✅ Transcribe audio files automatically
3. ✅ Stage text files (txt, md, docx) for processing
4. ✅ Track state to prevent re-processing
5. ✅ Save to `N5/records/reflections/incoming/`

---

## Deliverables

### Script: `N5/scripts/reflection_ingest_v2.py`

**Requirements:**
- Drive-only (no email)
- Pull new files from folder ID
- Detect file types: audio (.mp3, .m4a, .wav, .opus) + text (.txt, .md, .docx, .gdoc)
- Auto-transcribe audio using existing transcription tools
- Save to incoming directory with metadata
- Track processed file IDs in state file
- Dry-run support

**State File:** `N5/records/reflections/.state_v2.json`
```json
{
  "last_run_iso": "2025-10-24T20:15:00Z",
  "processed_file_ids": ["file_id_1", "file_id_2"],
  "last_sync_token": "optional_drive_sync_token"
}
```

**Output Format:**
```
N5/records/reflections/incoming/
├── 2025-10-24_pricing-strategy.txt
├── 2025-10-24_pricing-strategy.json  # metadata
├── 2025-10-24_founder-reflection.m4a
├── 2025-10-24_founder-reflection.m4a.transcript.jsonl
└── 2025-10-24_founder-reflection.json  # metadata
```

**Metadata JSON:**
```json
{
  "drive_file_id": "xyz123",
  "original_name": "Pricing Strategy Reflection.txt",
  "downloaded_at_iso": "2025-10-24T20:15:00Z",
  "file_type": "text",
  "size_bytes": 4523,
  "has_transcript": false
}
```

---

## Implementation Details

### Drive Integration
- Use `use_app_google_drive` tool
- List files in folder with `trashed=False`
- Filter by: not in processed_file_ids, modified after last_run
- Download each new file

### Transcription
```python
if file_ext in {".mp3", ".m4a", ".wav", ".opus"}:
    # Use existing transcription
    result = subprocess.run(
        ["python3", "/home/workspace/N5/scripts/transcribe_helper.py", audio_path],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        logger.error(f"Transcription failed: {result.stderr}")
        continue
```

### Text Wrapping
Text files should be wrapped in transcript-like format for classifier:
```json
{
  "text": "Full reflection content here...",
  "source_file": "/path/to/original.txt",
  "file_size_bytes": 4523
}
```

---

## Testing

1. Dry-run mode lists files without downloading
2. Download 1 text file, verify metadata
3. Download 1 audio file, verify transcription
4. Re-run, verify no re-processing
5. Error handling: network failure, transcription failure

---

## Principles Applied

- **P7 (Dry-Run):** `--dry-run` flag implemented
- **P18 (Verify State):** Check downloads exist and valid
- **P19 (Error Handling):** Try/except with logging
- **P5 (Anti-Overwrite):** Skip if already processed

---

## Success Criteria

Worker 1 is complete when:
1. ✅ Script pulls new files from Drive folder
2. ✅ Audio files are transcribed automatically
3. ✅ State tracking prevents re-processing
4. ✅ Dry-run flag works
5. ✅ Error handling covers all failure modes
6. ✅ Logging is comprehensive
7. ✅ All tests pass

---

**Status:** Ready to start  
**Created:** 2025-10-24
