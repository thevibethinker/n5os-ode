# Phase 2B: Handoff to Priority 3

**Date:** 2025-10-12  
**From:** Priority 2 (API Integration)  
**To:** Priority 3 (Polling Loop)  
**Status:** Ready to proceed once Howie confirms Phase 2A

---

## Current State

### Completed ✅
- ✅ **Priority 1:** State Tracking + Stakeholder Profiles
- ✅ **Priority 2:** API Integration (Google Calendar + Gmail)

### Next ⏭️
- ⏸️ **Priority 3:** Polling Loop (15-minute intervals)
- ⏸️ **Priority 4:** Automation (scheduled execution)

---

## What's Available for Priority 3

### Core Infrastructure
1. **State Manager** (`meeting_state_manager.py`)
   - Tracks processed events
   - Prevents duplicates
   - Persistent state file
   
2. **Profile Manager** (`stakeholder_profile_manager.py`)
   - Creates/updates stakeholder profiles
   - Email-based lookup
   - Meeting history tracking
   
3. **API Integrator** (`meeting_api_integrator.py`)
   - Fetches calendar events
   - Searches Gmail for context
   - Extracts V-OS tags
   
4. **Meeting Processor** (`meeting_processor.py`)
   - Orchestrates full workflow
   - Returns processing results
   - Error handling

### Ready-to-Use Functions
```python
# In Priority 3, you can use:

from meeting_api_integrator import MeetingAPIIntegrator
from meeting_processor import MeetingProcessor

# Create integrator
api = MeetingAPIIntegrator(
    calendar_tool=use_app_google_calendar,
    gmail_tool=use_app_gmail
)

# Create processor
processor = MeetingProcessor(api)

# Process meetings
results = processor.process_upcoming_meetings(days_ahead=7)
```

---

## Priority 3 Requirements

### What Needs to Be Built

#### 1. Meeting Monitor Script
**File:** `N5/scripts/meeting_monitor.py`

**Purpose:** Continuous polling loop that runs every 15 minutes

**Key Functions:**
```python
def monitor_loop(interval_minutes=15):
    """
    Continuously poll calendar every N minutes
    Detect new meetings, process them, sleep, repeat
    """
    
def detect_urgent_meetings(results):
    """
    Identify critical priority meetings from results
    Send immediate notifications if needed
    """
    
def generate_processing_report(results):
    """
    Create summary of what was processed
    Include in daily digest
    """
```

**Logic:**
1. Run processor every 15 minutes
2. Check for urgent meetings (priority = critical)
3. Log all processing activity
4. Sleep until next poll
5. Handle errors gracefully (don't crash)

#### 2. Priority Queue System
**Purpose:** Handle urgent vs. normal meetings differently

**Urgent Meetings (priority = critical):**
- Marked with `*` in calendar description
- Process immediately
- Send notification to V
- Include in next digest with **[URGENT]** marker

**Normal Meetings:**
- Process normally
- Include in daily digest
- No immediate notification

#### 3. Integration with Daily Digest
**Purpose:** Include meeting prep intel in existing digest

**What to Add:**
- New stakeholder profiles created today
- Upcoming meetings detected (next 7 days)
- Urgent meetings flagged
- Link to profile files

**Example Digest Section:**
```markdown
## 📅 Meeting Prep Intelligence

### Upcoming Meetings (Next 7 Days)

**[URGENT] Oct 15, 2:00 PM - Series A Discussion with Jane Smith**
- Stakeholder: Investor (Acme Ventures)
- Profile: file 'N5/records/meetings/2025-10-15-jane-smith-acme-ventures/profile.md'
- Email History: 2 threads
- Prep Status: Research in progress

**Oct 16, 10:00 AM - Engineering Interview with Alex Chen**
- Stakeholder: Candidate
- Profile: file 'N5/records/meetings/2025-10-16-alex-chen/profile.md'
- Email History: 1 thread
- Prep Status: Research in progress

---
*Detected 2 new meetings this cycle. 1 urgent, 1 normal.*
```

---

## Architecture for Priority 3

```
Priority 3 Architecture
=======================

meeting_monitor.py (NEW)
  ↓
  Runs every 15 minutes (polling loop)
  ↓
  Calls meeting_processor.py
  ↓
  meeting_processor.py (Priority 2)
    → Uses meeting_api_integrator.py
    → Uses meeting_state_manager.py
    → Uses stakeholder_profile_manager.py
  ↓
  Returns results
  ↓
  meeting_monitor.py
    → Checks for urgent meetings
    → Generates digest section
    → Logs processing metrics
  ↓
  Sleep 15 minutes
  ↓
  Repeat
```

---

## Implementation Plan for Priority 3

### Phase 1: Basic Monitor
1. Create `meeting_monitor.py`
2. Implement polling loop (15-min interval)
3. Call existing processor
4. Add logging
5. Test with manual runs

### Phase 2: Priority Queue
1. Add urgent meeting detection
2. Implement notification logic
3. Add flagging in results
4. Test with urgent/normal mix

### Phase 3: Digest Integration
1. Format results for digest
2. Create digest section template
3. Integrate with existing digest script
4. Test full flow

### Phase 4: Error Handling
1. Add retry logic for API failures
2. Add fallback for network issues
3. Add monitoring for stuck processes
4. Test failure scenarios

---

## Testing Strategy for Priority 3

### Unit Tests
1. Test polling loop starts/stops correctly
2. Test interval timing (15 minutes)
3. Test urgent meeting detection
4. Test digest section generation

### Integration Tests
1. Test full cycle (poll → process → sleep → repeat)
2. Test with multiple meetings
3. Test with mix of urgent/normal
4. Test error recovery

### End-to-End Tests
1. Run monitor for 1 hour (4 cycles)
2. Add new meeting mid-cycle
3. Verify detection and processing
4. Check digest output

---

## Configuration for Priority 3

### Environment Variables
```python
POLL_INTERVAL_MINUTES = 15  # How often to poll
LOOKHEAD_DAYS = 7           # How far ahead to look
MAX_RETRIES = 3             # Retry failed API calls
RETRY_DELAY_SECONDS = 60    # Wait between retries
```

### Logging
```python
LOG_FILE = "/home/workspace/N5/logs/meeting_monitor.log"
LOG_LEVEL = "INFO"  # DEBUG for development, INFO for production
```

---

## Dependencies for Priority 3

### New Dependencies
- None! Uses existing infrastructure from P1 + P2

### Existing Dependencies (from P1 + P2)
- `meeting_api_integrator` (P2)
- `meeting_processor` (P2)
- `meeting_state_manager` (P1)
- `stakeholder_profile_manager` (P1)

### System Dependencies
- `time` (sleep between polls)
- `logging` (monitoring and debugging)
- `schedule` (optional - for cron-like scheduling)

---

## Success Criteria for Priority 3

### Monitor Running ✅
- [ ] Polling loop runs continuously
- [ ] Polls every 15 minutes
- [ ] Doesn't crash on errors
- [ ] Logs all activity

### Detection Working ✅
- [ ] Detects new meetings with V-OS tags
- [ ] Processes each meeting once
- [ ] Identifies urgent vs. normal
- [ ] Handles recurring events correctly

### Integration Complete ✅
- [ ] Results included in daily digest
- [ ] Urgent meetings flagged
- [ ] Profile links working
- [ ] Email context included

### Production Ready ✅
- [ ] Error handling robust
- [ ] Logging comprehensive
- [ ] Performance acceptable (< 5 min per cycle)
- [ ] Ready for automated execution (P4)

---

## Potential Challenges

### Challenge 1: Long-Running Process
**Issue:** Monitor needs to run continuously  
**Solution:** Use `nohup` or scheduled task (Priority 4)

### Challenge 2: API Rate Limits
**Issue:** Polling every 15 min might hit limits  
**Solution:** Current usage well below limits (verified in P2)

### Challenge 3: Error Recovery
**Issue:** API failures could stop monitoring  
**Solution:** Implement retry logic with exponential backoff

### Challenge 4: Duplicate Detection
**Issue:** Recurring events might be processed multiple times  
**Solution:** Already handled by state manager (P1)

---

## Timing Considerations

### When to Poll
- **Every 15 minutes** during business hours (8 AM - 6 PM ET)
- **Every 30 minutes** during off-hours (optional optimization)
- **Skip overnight** (11 PM - 6 AM ET) (optional optimization)

### When to Process
- **Immediately** for urgent meetings (priority = critical)
- **Next cycle** for normal meetings

### When to Notify
- **Immediately** for urgent meetings detected
- **Daily digest** for all meetings

---

## Example: Full Cycle Walkthrough

### Cycle 1 (9:00 AM)
1. Monitor wakes up
2. Calls processor with 7-day lookahead
3. Processor finds 2 new meetings:
   - Meeting A: Oct 15, urgent
   - Meeting B: Oct 16, normal
4. Creates 2 profiles
5. Marks both as processed
6. Returns results to monitor
7. Monitor detects urgent meeting
8. Adds both to digest queue
9. Logs: "Processed 2 meetings, 1 urgent"
10. Sleeps 15 minutes

### Cycle 2 (9:15 AM)
1. Monitor wakes up
2. Calls processor with 7-day lookahead
3. Processor finds same 2 meetings
4. State manager says "already processed"
5. Skips both
6. Returns results: 0 new
7. Monitor logs: "No new meetings"
8. Sleeps 15 minutes

### Cycle 3 (9:30 AM)
1. Monitor wakes up
2. Calls processor
3. Howie just added a new meeting (Oct 17)
4. Processor detects new meeting
5. Creates profile
6. Marks as processed
7. Returns results: 1 new
8. Monitor adds to digest
9. Logs: "Processed 1 meeting"
10. Sleeps 15 minutes

---

## Handoff Checklist

### Before Starting Priority 3
- [x] Priority 1 complete and tested
- [x] Priority 2 complete and tested
- [ ] Howie Phase 2A confirmed (V-OS tags in calendar)
- [ ] At least one real tagged event tested successfully
- [ ] Gmail search verified working

### Ready to Build
- [ ] All existing functions working
- [ ] API connections stable
- [ ] State tracking reliable
- [ ] Profile creation validated

### Documentation Ready
- [x] Architecture defined
- [x] Requirements specified
- [x] Success criteria clear
- [x] Examples provided

---

## Quick Start for Priority 3

### When Ready to Build:

1. **Tell Zo:**
   "Build Priority 3: meeting monitor with 15-minute polling"

2. **Zo will create:**
   - `N5/scripts/meeting_monitor.py`
   - `N5/tests/test_meeting_monitor.py`
   - Integration with digest

3. **Test locally:**
   - Run monitor for 1 hour
   - Verify polling works
   - Check logs

4. **Deploy (Priority 4):**
   - Set up scheduled execution
   - Monitor for errors
   - Validate production

---

## Conclusion

**Priority 2 complete. Priority 3 ready to build.**

All infrastructure in place. Just need polling loop, priority queue, and digest integration.

Estimated time: 2-3 hours to build and test Priority 3.

**Blocked by:** Howie Phase 2A confirmation  
**Expected:** Oct 13, 2025  
**Next:** Test P2 with real data, then build P3

---

**Status:** ✅ READY FOR PRIORITY 3  
**Handoff Date:** 2025-10-12  
**Prepared By:** Zo
