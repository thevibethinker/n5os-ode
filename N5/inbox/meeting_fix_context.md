# Meeting System Fix Context

## BROKEN STATE VERIFIED
1. Pagination: Task afda82fa has pseudocode (won't execute)
2. Consumers: TWO exist - 3bfd7d14 (old) + c8e84add (new, broken)
3. Meetings: 27 folders with PLACEHOLDER files only (20-44 bytes)
4. Oracle: Missing (after position 100 in Drive)
5. Registry: Malformed JSON mixing

## REAL FIXES NEEDED
1. Delete c8e84add
2. Rewrite afda82fa with real use_app_google_drive pagination loop
3. Process 27 meetings (download + generate Smart Blocks)
4. Rebuild registry with consistent format

## FILES
- Requests: N5/inbox/meeting_requests/processed/*.json (27 files)
- Meetings: Personal/Meetings/2025-10-* (empty)
- Registry: N5/data/meeting_gdrive_registry.jsonl

## SUCCESS = 
- Oracle found (>100 files scanned)
- 27 meetings processed (transcript + blocks)
- All files >100 bytes (no placeholders)
- Registry valid JSONL
