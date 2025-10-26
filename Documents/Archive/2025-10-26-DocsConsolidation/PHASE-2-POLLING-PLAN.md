# Phase 2: Calendar Polling Architecture

**Date:** 2025-10-11  
**Status:** Ready to execute  
**Architecture:** Calendar polling (no push notifications)

---

## Decision: Option A (Calendar Polling)

**Rationale:**
- Reduces email noise in V's inbox
- Leverages existing digest polling infrastructure
- Simpler architecture (no notification plumbing)
- Howie only CCs V on actual discussions, not data forwarding

---

## Phase 2 Scope

### What We're Implementing

**Howie Side:**
- ✅ Populate calendar event descriptions with V-OS tags
- ✅ Include full name and organization of all attendees
- ❌ No auto-notifications to Zo

**Zo Side:**
- ✅ Poll calendar regularly (every 15-60 minutes, configurable)
- ✅ Detect new meetings since last run
- ✅ Extract V-OS tags from event descriptions
- ✅ Trigger immediate research for new meetings
- ✅ Priority bump for urgent meetings (`[!!]`, `[LD-INV]`)
- ✅ Pre-populate stakeholder profiles/CRM
- ✅ Generate daily digest with contextualized intel

---

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Person emails requesting meeting                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Howie schedules meeting                                   │
│    - Adds V-OS tags to calendar description                  │
│    - No email to Zo, no CC to V                              │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Calendar event sits there with tags                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Zo polls calendar every [configurable interval]          │
│    - Detects new meeting                                     │
│    - Reads V-OS tags                                         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Zo determines priority from tags                          │
│    - [!!] or [LD-INV] → Research immediately                 │
│    - Other tags → Research in next scheduled batch           │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Zo begins research                                        │
│    - Stakeholder background                                  │
│    - Gmail interaction history                               │
│    - Pre-populate CRM profile                                │
│    - Tag-aware framing (investor vs candidate vs partner)    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. Daily digest includes full intel                          │
│    - BLUF adapted to stakeholder type                        │
│    - Prep actions adapted to accommodation level             │
│    - Priority protection for critical meetings               │
└─────────────────────────────────────────────────────────────┘
```

**Key:** No routine Howie → Zo emails, no CC spam for V

---

## Email Communication Rules

### When Howie Emails Zo (Rare)

**DO CC V:**
- Actual questions/discussions
- Coordination needed
- Clarifications on workflow
- Edge cases requiring decision

**DON'T CC V:**
- ~~Routine meeting scheduled notifications~~ (we're not doing this)
- ~~Data forwarding~~ (we're not doing this)

### When Zo Emails Howie

**DO CC V:**
- Preference change requests
- Workflow suggestions
- Questions about calendar behavior
- Coordination on edge cases

**Result:** V's inbox only has **actual coordination**, not routine notifications

---

## Technical Implementation Plan

### Phase 2A: Howie Configuration (This Week)

**Action:** Zo sends Request #1 to Howie

**Request:** Calendar event description format with V-OS tags

**File:** `file 'N5/docs/zo-to-howie-request-1-FINAL.txt'`

**Expected flow:**
1. Zo sends request to Howie (CC V)
2. Howie asks V: "Should I implement this?"
3. V confirms
4. Howie updates preferences
5. Test with mock scheduling request
6. Verify tags appear correctly in calendar

---

### Phase 2B: Zo Polling Enhancement (Next Week)

**Goal:** Adapt `meeting_prep_digest.py` for continuous polling + research triggering

**Current State:**
- Script runs daily via cron/scheduled task
- Fetches today's meetings
- Generates digest
- No concept of "new" vs "already processed"

**Target State:**
- Script runs every [15 min / 1 hour / configurable]
- Tracks which meetings already processed
- Detects new meetings since last run
- Triggers immediate research for new meetings
- Priority queue: urgent first, then others
- Pre-populates stakeholder profiles

**Files to Modify:**

1. **`meeting_prep_digest.py`**
   - Add "last processed" tracking (SQLite or JSON state file)
   - Add "detect new meetings" function
   - Add "trigger research" function for new meetings
   - Add priority queue (urgent vs normal)

2. **New: `meeting_monitor.py`** (Alternative: separate polling script)
   - Runs on faster cadence (15-60 min)
   - Calls `meeting_prep_digest.py` functions
   - Focuses on new meeting detection + research trigger
   - Daily digest still runs once per day for full report

3. **`N5/records/meetings/.processed.json`** (New state file)
   ```json
   {
     "last_poll": "2025-10-11T23:45:00Z",
     "processed_events": [
       {
         "event_id": "abc123",
         "title": "Meeting with Jane Smith",
         "processed_at": "2025-10-11T14:30:00Z",
         "research_status": "complete"
       }
     ]
   }
   ```

**Implementation Approach:**

**Option 1: Enhance existing script**
- Modify `meeting_prep_digest.py` to track processed meetings
- Add `--monitor` mode for continuous polling
- Add `--digest` mode for daily full report
- Single script, two modes

**Option 2: Separate scripts**
- Keep `meeting_prep_digest.py` for daily digest
- Create `meeting_monitor.py` for polling + research trigger
- Shared functions via module
- Cleaner separation of concerns

**Recommendation:** Option 2 (separate scripts) for cleaner separation

---

## Phase 2B Technical Spec

### New Script: `meeting_monitor.py`

**Purpose:** Continuously monitor calendar for new meetings and trigger research

**Cadence:** Every 30 minutes (configurable)

**Logic:**
```python
1. Load last poll state from .processed.json
2. Fetch calendar events from last_poll to now
3. Filter to external meetings with V-OS tags
4. Compare to processed_events list
5. Identify new meetings
6. For each new meeting:
   a. Extract V-OS tags
   b. Determine priority ([!!] or [LD-INV] = urgent)
   c. Add to research queue
7. Process research queue (urgent first)
8. For each meeting in queue:
   a. Research stakeholder
   b. Pull Gmail history
   c. Create/update stakeholder profile
   d. Mark as processed
9. Update .processed.json with new state
10. Log activity
```

**Priority Queue:**
```python
urgent_queue = []    # [!!] or [LD-INV]
normal_queue = []    # Everything else

# Process urgent immediately
for meeting in urgent_queue:
    research_stakeholder(meeting)

# Process normal in batch
for meeting in normal_queue:
    research_stakeholder(meeting)
```

**Integration with Daily Digest:**
- Monitor script runs every 30 min: detects + researches
- Digest script runs daily at 6 AM: compiles + formats
- Both read from same stakeholder profiles
- Digest benefits from pre-populated research

---

## Assumptions & Design Decisions

### Assumption 1: Anyone Scheduled via Howie = Research Needed
**Implication:** All external meetings with V-OS tags trigger research

### Assumption 2: Calendar is Source of Truth
**Implication:** No separate notification system needed

### Assumption 3: 30-Minute Polling is Sufficient
**Rationale:** 
- Most meetings scheduled hours/days in advance
- 30 min delay acceptable for research trigger
- Urgent meetings ([!!], [LD-INV]) still get immediate research on next poll

**Override:** If true real-time needed in future, add push notifications (Phase 2C)

### Assumption 4: Pre-Populate CRM Profiles
**Implication:** Every researched stakeholder gets a profile in `N5/records/meetings/`

---

## Testing Plan

### Test 1: Calendar Format
1. Send Howie test scheduling request
2. Verify calendar event has V-OS tags with `*`
3. Verify Purpose line is clear
4. Verify full name + organization of attendees

### Test 2: Polling Detection
1. Howie schedules meeting with tags
2. Wait for next poll cycle (30 min)
3. Verify Zo detects new meeting
4. Verify Zo extracts tags correctly
5. Check logs for detection event

### Test 3: Priority Handling
1. Schedule urgent meeting with `[LD-INV]`
2. Schedule normal meeting with `[LD-GEN]`
3. Verify urgent researched first
4. Verify both eventually researched

### Test 4: CRM Pre-Population
1. New stakeholder scheduled via Howie
2. Verify profile created in `N5/records/meetings/`
3. Verify profile includes basic info from calendar
4. Verify profile ready for Gmail history enrichment

### Test 5: Daily Digest Integration
1. Monitor runs throughout day (detects + researches)
2. Daily digest runs at 6 AM
3. Verify digest includes pre-researched intel
4. Verify BLUF adapts to V-OS tags
5. Verify prep actions adapt to tags

---

## Success Criteria

**Phase 2 Complete When:**
- [x] Howie populates calendar with V-OS tags
- [x] Zo polls calendar every 30 minutes
- [x] Zo detects new meetings since last poll
- [x] Zo triggers research for new meetings
- [x] Urgent meetings prioritized
- [x] Stakeholder profiles pre-populated
- [x] Daily digest uses tag-aware intel
- [x] V's inbox free of routine notifications

---

## Timeline

**This Week (Phase 2A):**
1. V sends intro email to Howie (5 min)
2. Zo sends Request #1 to Howie (immediate)
3. Howie asks V for confirmation (5 min)
4. V confirms (5 min)
5. Howie updates preferences (5 min)
6. Test calendar format (15 min)

**Next Week (Phase 2B):**
1. Design meeting_monitor.py (1 hour)
2. Implement polling + detection (2 hours)
3. Implement research trigger (2 hours)
4. Implement priority queue (1 hour)
5. Test end-to-end (1 hour)
6. Deploy + monitor (ongoing)

**Total Phase 2:** ~8-10 hours development time

---

## Future Enhancements (Post Phase 2)

### Phase 3: Real-Time Gmail Integration
- Replace mock Gmail data with real API calls
- Pull full email thread context
- Analyze email sentiment and urgency

### Phase 4: Stakeholder Database
- Evolve file-based profiles to SQLite database
- Track relationship history over time
- Learn optimal meeting patterns

### Phase 5: Feedback Loop
- Post-meeting outcomes inform future prep
- A/B test prep approaches
- Adaptive accommodation levels

---

## Files Reference

**Email Scripts:**
- `file 'N5/docs/zo-to-howie-request-1-FINAL.txt'` — Request #1 (calendar format)

**Technical Specs:**
- `file 'N5/scripts/meeting_prep_digest.py'` — Existing daily digest (Phase 1 complete)
- `N5/scripts/meeting_monitor.py` — New polling script (Phase 2B, to be created)
- `N5/records/meetings/.processed.json` — State tracking (Phase 2B, to be created)

**Documentation:**
- `file 'N5/docs/PHASE-1-COMPLETE.md'` — Phase 1 summary
- `file 'N5/docs/howie-zo-implementation-plan.md'` — Full 5-phase plan

---

**Status:** Ready to execute Phase 2A  
**Next Action:** Zo sends Request #1 to Howie after V sends intro  
**Architecture:** Calendar polling ✓  
**Email Noise:** Minimized ✓
