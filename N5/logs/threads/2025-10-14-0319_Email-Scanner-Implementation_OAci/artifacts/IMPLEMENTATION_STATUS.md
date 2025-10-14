# Email Scanner Implementation Status

## Phase 1: Core Structure ✅
- Logging, state tracking, error handling framework complete
- File: `N5/scripts/background_email_scanner.py`

## Phase 2: Gmail Integration (IN PROGRESS)
- Need to implement actual Gmail API calls
- Need to implement participant extraction logic
- Need to implement profile queue/creation

## TODO Next:
1. Implement Gmail query via use_app_gmail
2. Parse calendar invite participants
3. Test with dry-run
4. Integrate with stakeholder system
5. Clean up duplicate scheduled tasks

## Key Assumptions:
- Query: calendar invites + meeting links (Zoom/Meet/Calendly)
- Scan window: last 30 min (20 min frequency + buffer)
- Exclude internal domains: mycareerspan.com, theapply.ai, zo.computer
- Dedup: check against N5/stakeholders/index.jsonl
- Queue: Write to N5/stakeholders/.pending_updates/
