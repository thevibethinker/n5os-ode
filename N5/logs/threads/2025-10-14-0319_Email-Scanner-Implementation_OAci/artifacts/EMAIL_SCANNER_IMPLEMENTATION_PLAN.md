# Email Scanner Implementation Plan

**Date:** 2025-10-13  
**Thread:** con_M0nOf33r18BtOAci  
**Status:** Phase 1 - Core Implementation In Progress

---

## Context

The `background_email_scanner.py` was deployed as a **stub** on 2025-10-12 with 3 scheduled tasks running every ~20 minutes. Purpose: discover new stakeholders from meeting-related emails in Gmail.

**Key Finding:** Script has ALWAYS been a stub (git history confirms). Never had actual implementation.

**Deployment Documentation States:**
- "Function: Discover new stakeholders from meeting emails"
- "21-day Gmail scan complete" (git commit message - likely refers to initial manual scan)
- Active hours: 8 AM - 10 PM ET
- Frequency: 3x/hour (:00, :20, :40)

---

## System Design (Following Architectural Principles)

### Phase 0: Principles Loaded ✅

**Core principles applied:**
- P0 (Rule-of-Two): Minimal context loading
- P5 (Anti-Overwrite): State file protection
- P7 (Dry-Run): `--dry-run` flag implemented
- P15 (Complete Before Claiming): Explicit completion criteria defined
- P16 (Accuracy Over Sophistication): No invented API limits
- P18 (State Verification): State file validation required
- P19 (Error Handling): Try-catch with specific error paths
- P21 (Document Assumptions): All placeholders documented below

---

## Requirements & Constraints

### What It MUST Do

1. **Scan Gmail** for meeting-related emails (invites, confirmations, Zoom/Meet/Calendly links)
2. **Extract external participants** (name, email, organization if available)
3. **Check for existing stakeholders** via `N5/stakeholders/index.jsonl`
4. **Queue new discoveries** for profile creation (integrate with stakeholder system)
5. **Track state** to avoid reprocessing (last scan time, processed message IDs)
6. **Log discoveries** with counts and details
7. **Handle errors** gracefully (API failures, malformed emails, network issues)

### What It Does NOT Do

- ❌ Process meeting transcripts (that's `meeting-transcript-scan.md`)
- ❌ Create profiles directly (delegates to stakeholder_manager.py)
- ❌ Scan internal team emails (filters by domain)
- ❌ Modify existing profiles (only discovers NEW stakeholders)

### Integration Points

- **Gmail API:** via `use_app_gmail` tool with `gmail-find-email` action
- **Stakeholder System:** `N5/stakeholders/index.jsonl` (read only for deduplication)
- **Profile Creation:** Queue to `N5/stakeholders/.pending_updates/` (or call stakeholder_manager.py)
- **State Tracking:** `N5/.state/email_scanner_state.json`

---

## Implementation Phases

### Phase 1: Core Gmail Integration (CURRENT)

**Status:** Skeleton complete, Gmail API integration PLACEHOLDER

**Files Modified:**
- ✅ `N5/scripts/background_email_scanner.py` - Core logic skeleton
- ⏳ Gmail API integration (PLACEHOLDER - needs implementation)

**What's Done:**
- [x] Logging infrastructure
- [x] State file structure
- [x] Stakeholder index loading
- [x] Internal domain filtering
- [x] Dry-run mode
- [x] Error handling framework

**What's Needed:**
- [ ] Actual Gmail API call using `use_app_gmail`
- [ ] Email parsing logic (extract participants from calendar invites)
- [ ] Query construction (time-based filtering)
- [ ] Message deduplication logic

**ASSUMPTIONS / PLACEHOLDERS (P21):**

1. **Line 135-155: Gmail API Integration PLACEHOLDER**
   - Status: STUB - returns empty list
   - What's needed: Call `use_app_gmail('gmail-find-email', {...})`
   - Query: `after:{timestamp} AND (calendar invite OR zoom.us OR meet.google.com ...)`
   - Estimated effort: 2-3 hours (need to test query syntax, handle pagination)

2. **Email Parsing: Participant Extraction MISSING**
   - Status: NOT IMPLEMENTED
   - What's needed: Parse email body/headers for external participant emails
   - Challenges: Different formats (Google Calendar, Outlook, Zoom, Calendly)
   - Estimated effort: 3-4 hours (regex patterns, format handling, testing)

3. **Profile Creation Queue: Integration Method UNDEFINED**
   - Status: ASSUMPTION - queue to .pending_updates/
   - What's needed: Decide if we:
     - Option A: Write to `.pending_updates/` for batch processing
     - Option B: Call `stakeholder_manager.py` directly
     - Option C: Write to `N5/inbox/stakeholder_discoveries/` for separate workflow
   - Estimated effort: 1-2 hours depending on choice

4. **Query Time Range: 30 minutes ASSUMED**
   - Status: HARDCODED assumption
   - What's needed: Confirm optimal window (20 min frequency = last 30 min scan?)
   - Fallback: Use `last_scan_time` from state file
   - Risk: Missing emails if scan fails/delays

---

### Phase 2: Profile Integration

**Dependencies:** Phase 1 complete

**Tasks:**
1. Implement profile creation queue
2. Test deduplication logic
3. Verify existing stakeholder index format
4. Add organization inference (from email signature/domain)
5. Test with real Gmail data (dry-run first)

**Estimated Time:** 3-4 hours

---

### Phase 3: Testing & Validation

**Requirements:**
- [ ] Dry-run test with Gmail API
- [ ] Process 10-20 real emails
- [ ] Verify deduplication works
- [ ] Confirm no internal emails processed
- [ ] Check state file persistence
- [ ] Validate logging output

**Success Criteria (P15):**
- [ ] Gmail API successfully queried
- [ ] External participants extracted correctly
- [ ] New stakeholders identified (not in index)
- [ ] State file updated with message IDs
- [ ] No duplicates created
- [ ] Logs show discovery counts
- [ ] Error handling tested (API failure, malformed email)

---

### Phase 4: Cleanup & Documentation

**Tasks:**
1. Delete 2 duplicate scheduled tasks:
   - `52493359-62c4-4f9f-afa3-f90a58dcf5a0` (Email Stakeholder Scan - :20)
   - `8d411052-0aa7-47a7-9a84-eec5be85479a` (Stakeholder Discovery from Gmail - :40)

2. Update remaining task (ae9dd6f5-3052-4081-b6d7-cc82c9d652cc):
   - Rename: "🔍 Stakeholder Email Scan" (per protocol)
   - Verify schedule: FREQ=MINUTELY;INTERVAL=20 (every 20 min, 8am-10pm ET)
   - Confirm instruction references updated script

3. Documentation:
   - Update `N5/DEPLOYMENT-STATUS-2025-10-12.md`
   - Document in `N5/stakeholders/README.md`
   - Log implementation in thread export

---

## Technical Decisions

### Gmail Query Strategy

**Decision:** Time-based progressive scan with keyword filters

**Rationale:**
- Every 20 minutes = scan last 30 minutes to overlap (safety margin)
- Keywords: "calendar invite", "zoom.us", "meet.google.com", "calendly.com", etc.
- Exclude: `from:mycareerspan.com OR from:theapply.ai`

**Query Example:**
```
after:{last_scan_timestamp} 
AND (calendar invite OR zoom.us OR meet.google.com OR calendly.com OR "invited you to")
AND NOT from:mycareerspan.com
AND NOT from:theapply.ai
```

### State Tracking Strategy

**Decision:** JSON file with message IDs + timestamp

**Rationale:**
- Simple, file-based (no DB needed)
- Rolling window (keep last 1000 message IDs to prevent unbounded growth)
- Timestamp fallback if message IDs fail

**State Schema:**
```json
{
  "last_scan_time": "2025-10-13T22:41:00.000Z",
  "processed_message_ids": ["msg_id_1", "msg_id_2", ...],
  "discovered_count": 15,
  "last_discoveries": [
    {"email": "external@company.com", "name": "John Doe", "timestamp": "..."},
    ...
  ]
}
```

### Deduplication Strategy

**Decision:** Two-level check (state file + stakeholder index)

**Rationale:**
- Level 1: Skip messages already in `processed_message_ids`
- Level 2: Skip emails already in `N5/stakeholders/index.jsonl`
- Result: No duplicate profile creation attempts

---

## Error Handling (P19)

### Failure Scenarios

**1. Gmail API Failure**
- Error: Network timeout, auth failure, rate limit
- Recovery: Log error, skip this scan, retry in 20 minutes
- Alert: Log warning if 3+ consecutive failures

**2. Malformed Email**
- Error: Can't parse participant info
- Recovery: Log warning, skip email, continue with others
- No crash: Graceful degradation

**3. State File Corruption**
- Error: JSON parse error
- Recovery: Log error, use default state (start fresh)
- Backup: Keep `.backup` copy of last good state

**4. Stakeholder Index Missing**
- Error: `index.jsonl` not found
- Recovery: Treat as empty (all discoveries = new)
- Alert: Log warning (system misconfiguration)

---

## Monitoring & Observability

### Logs

**Location:** `N5/logs/email_scanner.log`

**Key Metrics:**
- Scan start/end timestamps
- Emails scanned count
- New stakeholders discovered
- Errors encountered
- State file updates

**Example Output:**
```
2025-10-13T22:41:00Z - INFO - === Email Scanner: Starting Background Scan ===
2025-10-13T22:41:02Z - INFO - Loaded state: last_scan=2025-10-13T22:21:00Z, processed_count=450
2025-10-13T22:41:03Z - INFO - Loaded 6 existing stakeholder emails
2025-10-13T22:41:05Z - INFO - Gmail query: after:2025-10-13T22:21:00Z AND (calendar invite OR zoom.us...)
2025-10-13T22:41:08Z - INFO - Retrieved 12 emails from Gmail
2025-10-13T22:41:10Z - INFO - Processed 12 emails: 2 new stakeholders discovered
2025-10-13T22:41:10Z - INFO - 🎯 Discovered 2 new stakeholder(s): john@acme.com, jane@startup.io
2025-10-13T22:41:10Z - INFO - State saved: N5/.state/email_scanner_state.json
2025-10-13T22:41:10Z - INFO - ✅ Scan complete: 12 emails processed, 2 new stakeholders discovered
2025-10-13T22:41:10Z - INFO - Next scan in ~20 minutes
```

### Success Indicators

- **Healthy:** 2-5 new stakeholders/week (realistic for active networking)
- **Warning:** 0 new for 7+ days (may indicate query issue or low email activity)
- **Error:** 3+ consecutive scan failures (requires investigation)

---

## Next Steps (Immediate)

1. **Implement Gmail API integration** (replace PLACEHOLDER)
2. **Test with dry-run** against real Gmail data
3. **Implement participant extraction logic**
4. **Decide on profile creation queue method**
5. **Test end-to-end** with 10 real emails
6. **Deploy and monitor** for 24 hours
7. **Clean up duplicate scheduled tasks**

---

## Related Files

**Implementation:**
- `file 'N5/scripts/background_email_scanner.py'` - Main script

**State & Data:**
- `N5/.state/email_scanner_state.json` - Scan state tracking
- `N5/stakeholders/index.jsonl` - Existing stakeholders (read-only)
- `N5/logs/email_scanner.log` - Execution logs

**Documentation:**
- `file 'N5/DEPLOYMENT-STATUS-2025-10-12.md'` - System deployment status
- `file 'N5/stakeholders/README.md'` - Stakeholder system overview
- `file 'Document Inbox/Temporary/EMAIL_SCANNER_IMPLEMENTATION_NEEDED.md'` - Original handoff

**Scheduled Tasks:**
- ae9dd6f5-3052-4081-b6d7-cc82c9d652cc (keep, rename)
- 52493359-62c4-4f9f-afa3-f90a58dcf5a0 (delete after implementation)
- 8d411052-0aa7-47a7-9a84-eec5be85479a (delete after implementation)

---

**Implementation Status:** Phase 1 skeleton complete, Gmail API integration needed next

*Plan created: 2025-10-13 22:42 ET*
