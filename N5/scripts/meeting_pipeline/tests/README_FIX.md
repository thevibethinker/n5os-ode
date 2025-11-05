---
created: 2025-11-03
last_edited: 2025-11-03
version: 1.0
---

# Meeting Pipeline Path Resolution Fix

## Problem

**Root Cause:** AI request JSONs store transcript paths WITHOUT `[IMPORTED-TO-ZO]` prefix, but actual files HAVE the prefix (added by `mark_processed()` in transcript_processor_v4.py).

**Symptom:** Scheduled task fails with "file not found" because it tries to read path from JSON, which doesn't match filesystem reality.

**Example:**
```
JSON stores:    /Inbox/meeting.transcript.md
File exists at: /Inbox/[IMPORTED-TO-ZO] meeting.transcript.md
```

## Solution

**Strategy:** Dynamic path resolution at processing time.

**Implementation:**
1. `resolve_transcript_path.py` - Helper function that tries:
   - Original path as-is
   - Path with `[IMPORTED-TO-ZO]` prefix added
   - Returns None if neither exists

2. Updated scheduled task instruction to use path resolution before reading transcript

3. Comprehensive unit tests validating fix

## Files Changed

### New Files
- `resolve_transcript_path.py` - Path resolution helper (CLI + importable function)
- `tests/test_path_resolution.py` - Unit tests for path resolution logic
- `tests/test_integration.py` - Integration tests for full workflow
- `tests/run_tests.sh` - Test runner script

### Modified Files
- Scheduled task `e321bdd7-361b-4b91-954b-bba6fd0abc5b` instruction updated

## Testing

Run tests:
```bash
cd /home/workspace/N5/scripts/meeting_pipeline/tests
./run_tests.sh
```

Or individually:
```bash
python3 -m pytest test_path_resolution.py -v
python3 -m pytest test_integration.py -v
```

## Test Coverage

**Path Resolution (test_path_resolution.py):**
- ✅ T1.1: File exists with prefix, request has path without prefix
- ✅ T1.2: File exists without prefix
- ✅ T1.3: File doesn't exist (either version)
- ✅ Edge: Both versions exist (prefers original)
- ✅ CLI interface tests

**Integration (test_integration.py):**
- ✅ T5.1: End-to-end with prefix resolution
- ✅ T5.2: Multiple pending requests (processes oldest)
- ✅ T4.2: Error handling for missing files

## Usage

### As CLI Tool
```bash
# Returns resolved path or exits with error
RESOLVED=$(python3 resolve_transcript_path.py "/path/to/file.transcript.md")
```

### As Python Module
```python
from resolve_transcript_path import resolve_transcript_path

path = resolve_transcript_path("/path/to/file.transcript.md")
if path:
    content = path.read_text()
else:
    # Handle error
```

## Principles Applied

- **P5 (Safety):** Non-destructive path resolution, no file modifications
- **P7 (Idempotence):** Resolution is pure function, same input → same output
- **P11 (Failure Modes):** Returns None for missing files, clear error handling
- **P19 (Error Handling):** All error paths tested and documented
- **P28 (Plan DNA):** Clear design → clean implementation → comprehensive tests

## Status

**Implementation:** 4/4 complete (100%)
- ✅ Path resolution helper created
- ✅ Scheduled task updated
- ✅ Unit tests written
- ✅ Documentation complete

**Next:** Debugger validation
