---
created: 2025-12-24
last_edited: 2025-12-24
version: 1.0
provenance: con_wne5ccsJoVnFSW6f
---
# Plan: 3x Daily HRV Tracking System

## Open Questions
- Does the Fitbit API provide a reliable "current" HRV (rmssd) for intraday requests, or does it only update post-sleep? (Fitbit's standard HRV API is usually a single value derived from sleep, though intraday heart rate is available).
- If Fitbit only provides sleep-based HRV, should we allow manual input for the 8am/6pm checks via the SMS reply or pull the "latest available"?

## Checklist
- ☑ Initialize build workspace
- ☐ Research Fitbit Intraday HRV availability (RMSSD)
- ☐ Update `file 'N5/data/journal.db'` schema for `hrv` in snapshots
- ☐ Modify `file 'N5/scripts/log_bio_reply.py'` to capture HRV during bio-log snapshots
- ☐ Update `file 'Personal/Health/WorkoutTracker/fitbit_sync.py'` if intraday HRV is possible
- ☐ Verify 3x daily tracking works (test with mock data)

## Phase 1: Research & Schema Update
### Affected Files
- `file 'Personal/Health/WorkoutTracker/workout_tracker.py'`
- `file 'N5/data/journal.db'` (sqlite3)

### Changes
1. **Research:** Confirm if Fitbit Web API supports `hrv` intraday series. (Most likely it does not, usually it's a daily summary).
2. **Schema:** Update `bio_snapshots` table in `file 'N5/data/journal.db'` to include an `hrv` column.
3. **Storage:** Update `workout_tracker.py` to ensure it can handle multiple HRV points per day if we find a source.

### Unit Tests
- `sqlite3 /home/workspace/N5/data/journal.db "PRAGMA table_info(bio_snapshots);"` (verify column exists)

## Phase 2: Logic Integration
### Affected Files
- `file 'N5/scripts/log_bio_reply.py'`
- `file 'Personal/Health/WorkoutTracker/fitbit_sync.py'`

### Changes
1. Modify `get_current_vitals` in `log_bio_reply.py` to retrieve the latest HRV.
2. Ensure `save_bio_snapshot` persists the HRV value.
3. Update `fitbit_sync.py` to support fetching recent HRV if supported.

### Unit Tests
- Run `python3 N5/scripts/log_bio_reply.py "Test 🍎"` and verify HRV is captured in the log output.

## Success Criteria
- Bio-log snapshots (morning/evening) now include an HRV reading.
- Data is visible in the `bio_snapshots` table and can be correlated with mood.

## Risks & Mitigations
- **Risk:** Fitbit doesn't support intraday RMSSD. **Mitigation:** Pull the "latest available" (usually from the previous night) but label it correctly so we can still correlate "morning agility" with evening mood.

