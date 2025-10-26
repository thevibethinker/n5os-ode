# Phase 2B Preparation: Zo Infrastructure Build

**Date:** 2025-10-12  
**Status:** READY TO EXECUTE  
**Context:** While waiting for Howie to confirm Phase 2A calendar configuration  
**Objective:** Build foundational infrastructure so Zo is ready when Howie completes Phase 2A

---

## EXECUTIVE SUMMARY

**What's Happening:**
- Phase 2A (Howie configuration) is in progress - waiting for Howie's confirmation
- V sent intro email to Howie on Oct 12 at 4:19 AM
- Howie acknowledged and requested until "tomorrow" (Oct 13) to implement
- V approved the delay
- Zo will send detailed config request once Howie confirms ready

**What We're Doing Now:**
- Building Zo's foundational infrastructure (Phase 2B prep)
- Two core systems: State tracking + Stakeholder profiles
- Zero dependency on Howie - can build and test with mocks
- When Howie confirms Phase 2A, we immediately proceed to API integration

---

## BACKGROUND: THE FULL PLAN

### Phase 2 Goal
Enable automated meeting prep pipeline from scheduling to intelligence delivery with zero manual work.

### Architecture Decision: Calendar Polling (NOT Push Notifications)

**Chosen Approach:** Zo polls calendar directly every 15 minutes

**Why:**
- Reduces email noise in V's inbox
- Leverages existing digest polling infrastructure
- Simpler architecture (fewer moving parts)
- Howie only needs to populate tags in calendar descriptions

**The Complete Pipeline:**
```
1. Person emails V requesting meeting
   ↓
2. Howie schedules meeting, adds V-OS tags to calendar description
   ↓
3. Calendar event sits there with tags (no notification)
   ↓
4. Zo polls calendar every 15 minutes, detects new meeting
   ↓
5. Zo determines priority from tags ([!!] or [LD-INV] = urgent)
   ↓
6. Zo searches Gmail for context by attendee email
   ↓
7. Zo begins research, creates/updates stakeholder profile
   ↓
8. Daily digest includes full pre-researched intel
```

**Key:** Zero manual work, zero email noise

---

## PHASE 2B COMPONENTS (What Needs to Be Built)

### Priority 1: Foundations (BUILD NOW)
1. **State Tracking System** - `.processed.json` to track processed events
2. **Stakeholder Profile System** - Directory structure + templates + CRUD functions

### Priority 2: API Integration (BUILD AFTER HOWIE CONFIRMS)
3. **Google Calendar API** - Replace mock data in `meeting_prep_digest.py`
4. **Gmail API** - Replace mock data in `meeting_prep_digest.py`

### Priority 3: Polling Logic (BUILD AFTER API INTEGRATION)
5. **Meeting Monitor Script** - `meeting_monitor.py` with polling loop
6. **Priority Queue System** - Handle urgent vs. normal meetings

### Priority 4: Automation (BUILD AFTER TESTING)
7. **Scheduled Execution** - Cron/scheduled task every 15 minutes

---

## PRIORITY 1A: STATE TRACKING SYSTEM

### Purpose
Track which calendar events have already been processed to prevent duplicate research.

### File Location
`/home/workspace/N5/records/meetings/.processed.json`

### Schema
```json
{
  "last_poll": "2025-10-11T23:45:00-04:00",
  "processed_events": {
    "abc123xyz": {
      "title": "Series A Discussion - Jane Smith",
      "processed_at": "2025-10-11T14:30:00-04:00",
      "priority": "urgent",
      "stakeholder_profiles": [
        "N5/records/meetings/2025-10-15-jane-smith-acme-ventures/profile.md"
      ]
    },
    "def456uvw": {
      "title": "Engineering Interview - Alex Chen",
      "processed_at": "2025-10-11T15:00:00-04:00",
      "priority": "normal",
      "stakeholder_profiles": [
        "N5/records/meetings/2025-10-16-alex-chen/profile.md"
      ]
    }
  }
}
```

### Required Functions

#### `load_state() -> dict`
```python
def load_state():
    """
    Load last poll state from .processed.json
    Returns: dict with 'last_poll' and 'processed_events'
    Creates file if doesn't exist
    """
```

#### `save_state(state: dict) -> None`
```python
def save_state(state):
    """
    Save updated state to .processed.json
    Args:
        state: dict with 'last_poll' and 'processed_events'
    """
```

#### `add_processed_event(event_id: str, event_data: dict) -> None`
```python
def add_processed_event(event_id, event_data):
    """
    Mark event as processed
    Args:
        event_id: Calendar event ID
        event_data: dict with title, priority, stakeholder_profiles, etc.
    """
```

#### `is_event_processed(event_id: str) -> bool`
```python
def is_event_processed(event_id):
    """
    Check if event already processed
    Args:
        event_id: Calendar event ID
    Returns: True if already processed
    """
```

### Implementation Details

**File Management:**
- Create directory `N5/records/meetings/` if doesn't exist
- Initialize `.processed.json` with empty structure on first run
- Use atomic writes (write to temp file, then rename) for safety
- Never delete this file (permanent audit trail)

**Timestamp Handling:**
- All timestamps in ISO 8601 format with ET timezone
- Use `datetime.now(pytz.timezone('America/New_York')).isoformat()`

**Error Handling:**
- If file corrupted, create backup and reinitialize
- Log all state changes for debugging
- Graceful degradation if file missing (reprocess all events)

### Testing Strategy

**Unit Tests:**
1. Test file creation on first run
2. Test load/save roundtrip
3. Test add event
4. Test is_event_processed lookup
5. Test concurrent access safety

**Integration Tests:**
1. Test with mock event IDs
2. Test state persistence across "polls"
3. Test recovery from corrupted file

---

## PRIORITY 1B: STAKEHOLDER PROFILE SYSTEM

### Purpose
Create and manage stakeholder profiles for meeting attendees with relationship tracking and research caching.

### Directory Structure
```
/home/workspace/N5/records/meetings/
├── .processed.json
├── 2025-10-15-jane-smith-acme-ventures/
│   └── profile.md
├── 2025-10-16-alex-chen/
│   └── profile.md
└── 2025-10-17-maria-lopez-state-university/
    └── profile.md
```

**Naming Convention:**
`YYYY-MM-DD-firstname-lastname-organization/`
- Use meeting date (not creation date)
- Lowercase, hyphens for spaces
- Organization optional if unknown
- If same person multiple meetings, use earliest meeting date

### Profile Template

```markdown
# [Full Name] — [Organization]

**Role:** [Job Title]  
**Email:** [email@example.com]  
**Organization:** [Organization Name (Type)]  
**Stakeholder Type:** [Investor/Candidate/Partner/Community/General]  
**First Meeting:** [YYYY-MM-DD H:MM AM/PM ET]  
**Status:** [Active/Past]

---

## Context from Howie

Howie scheduled this meeting with V-OS tags: [LD-X] [timing] *

Purpose: [One sentence from calendar]

Context: [1-2 sentences from calendar]

---

## Email Interaction History

### [YYYY-MM-DD] — [Subject/Description]
[Summary of email interaction]

### [YYYY-MM-DD] — [Subject/Description]
[Summary of email interaction]

---

## Research Notes

### Background
- [Key professional background]
- [Current role and organization]
- [Relevant experience]

### [Stakeholder-Specific Section]
*This section varies by stakeholder type:*
- **Investors:** Investment thesis, portfolio companies, check sizes
- **Candidates:** Skills, experience, interview stage
- **Partners:** Organization focus, decision makers, pilot details
- **Community:** Association focus, membership, events

### Recent Activity
- [LinkedIn activity]
- [News mentions]
- [Company developments]

---

## Meeting History

### [YYYY-MM-DD] — [Meeting Title] (Status)
- **Type:** [Discovery/Follow-up/Decision/etc.]
- **Accommodation:** [A-0/A-1/A-2]
- **Priority:** [Critical/Normal]
- **Prep Status:** [Research complete/In progress]

---

## Relationship Notes

- [First touchpoint]
- [Engagement level]
- [Key discussion topics]
- [Next steps or follow-ups]

---

**Last Updated:** [YYYY-MM-DD] by Zo ([script name])
```

### Required Functions

#### `create_stakeholder_profile(name, email, organization, stakeholder_type, meeting, tags, email_context) -> str`
```python
def create_stakeholder_profile(
    name: str,
    email: str,
    organization: str,
    stakeholder_type: str,
    meeting: dict,
    tags: dict,
    email_context: dict
) -> str:
    """
    Create new stakeholder profile
    
    Args:
        name: Full name
        email: Email address
        organization: Organization name
        stakeholder_type: investor/candidate/partner/community/general
        meeting: dict with meeting details (title, date, time, description)
        tags: dict with V-OS tags extracted from meeting
        email_context: dict with Gmail thread summaries
    
    Returns:
        str: Path to created profile.md
    """
```

#### `find_stakeholder_profile(email: str) -> str | None`
```python
def find_stakeholder_profile(email: str) -> str | None:
    """
    Search for existing profile by email
    
    Args:
        email: Stakeholder email to search for
    
    Returns:
        str: Path to profile.md if found, None otherwise
    """
```

#### `update_stakeholder_profile(profile_path: str, meeting: dict, tags: dict) -> None`
```python
def update_stakeholder_profile(
    profile_path: str,
    meeting: dict,
    tags: dict
) -> None:
    """
    Update existing profile with new meeting
    
    Args:
        profile_path: Path to existing profile.md
        meeting: dict with new meeting details
        tags: dict with V-OS tags
    """
```

#### `append_meeting_to_profile(profile_path: str, meeting: dict, tags: dict) -> None`
```python
def append_meeting_to_profile(
    profile_path: str,
    meeting: dict,
    tags: dict
) -> None:
    """
    Add new meeting to existing profile's meeting history
    
    Args:
        profile_path: Path to profile.md
        meeting: dict with meeting details
        tags: dict with V-OS tags
    """
```

### Implementation Details

**Directory Creation:**
- Sanitize name and organization for filesystem
- Handle special characters, spaces, case
- Create directory if doesn't exist
- Handle naming collisions (append number if needed)

**Email Matching:**
- Case-insensitive search
- Search all profile.md files in subdirectories
- Use grep or file scanning
- Cache results for performance

**Profile Updates:**
- Append to meeting history section
- Update "Last Updated" footer
- Preserve existing research notes
- Don't duplicate information

**Stakeholder Type Detection:**
```python
STAKEHOLDER_TYPE_MAP = {
    'LD-INV': 'Investor',
    'LD-HIR': 'Candidate',
    'LD-COM': 'Community',
    'LD-NET': 'Partner',
    'LD-GEN': 'General'
}
```

### Testing Strategy

**Unit Tests:**
1. Test directory name sanitization
2. Test profile creation with all fields
3. Test email lookup (case insensitive)
4. Test profile update/append
5. Test handling of missing organization

**Integration Tests:**
1. Create profile for new stakeholder
2. Find existing profile by email
3. Append new meeting to existing profile
4. Test with mock meeting data
5. Verify markdown formatting

---

## TESTING WITH MOCK DATA

Since we don't have real calendar events yet, create mock data structures.

### Mock Calendar Event
```python
MOCK_CALENDAR_EVENT = {
    'id': 'test123abc',
    'summary': 'Series A Discussion - Jane Smith',
    'description': '''[LD-INV] [D5+] *

Purpose: Discuss Series A funding timeline

Context: Jane replied to Mike's intro, expressed strong interest in Careerspan's ed-tech traction, wants to discuss funding terms and timeline.

---
Please send pitch deck in advance to vrijen@mycareerspan.com.

Zoom: https://zoom.us/j/...''',
    'start': {
        'dateTime': '2025-10-15T14:00:00-04:00'
    },
    'attendees': [
        {
            'email': 'jane@acmeventures.com',
            'displayName': 'Jane Smith',
            'responseStatus': 'accepted'
        }
    ]
}
```

### Mock Gmail Context
```python
MOCK_GMAIL_CONTEXT = {
    'threads': [
        {
            'date': '2025-10-10',
            'subject': 'Introduction - Vrijen Attawar (Careerspan)',
            'snippet': 'Jane replied to intro, expressed interest...'
        }
    ]
}
```

### Test Execution Flow
```python
# 1. Create state tracking file
state = load_state()
assert state['processed_events'] == {}

# 2. Create mock event
event_id = MOCK_CALENDAR_EVENT['id']
assert not is_event_processed(event_id)

# 3. Create stakeholder profile
profile_path = create_stakeholder_profile(
    name='Jane Smith',
    email='jane@acmeventures.com',
    organization='Acme Ventures',
    stakeholder_type='Investor',
    meeting=MOCK_CALENDAR_EVENT,
    tags={'stakeholder': 'investor', 'priority': 'critical'},
    email_context=MOCK_GMAIL_CONTEXT
)
assert os.path.exists(profile_path)

# 4. Mark event as processed
add_processed_event(event_id, {
    'title': MOCK_CALENDAR_EVENT['summary'],
    'processed_at': datetime.now().isoformat(),
    'priority': 'urgent',
    'stakeholder_profiles': [profile_path]
})
assert is_event_processed(event_id)

# 5. Test profile lookup
found_path = find_stakeholder_profile('jane@acmeventures.com')
assert found_path == profile_path

# 6. Test profile update with second meeting
MOCK_CALENDAR_EVENT_2 = {...}  # Different meeting, same attendee
append_meeting_to_profile(profile_path, MOCK_CALENDAR_EVENT_2, tags)

print("✅ All tests passed!")
```

---

## FILE STRUCTURE

After building Priority 1, the file structure should be:

```
/home/workspace/N5/
├── scripts/
│   ├── meeting_prep_digest.py (existing)
│   └── meeting_state_manager.py (NEW - state tracking functions)
│   └── stakeholder_profile_manager.py (NEW - profile CRUD functions)
├── records/
│   └── meetings/
│       ├── .processed.json (NEW)
│       ├── 2025-10-15-jane-smith-acme-ventures/ (TEST)
│       │   └── profile.md
│       └── 2025-10-16-alex-chen/ (TEST)
│           └── profile.md
└── tests/
    ├── test_state_manager.py (NEW)
    └── test_profile_manager.py (NEW)
```

---

## IMPLEMENTATION CHECKLIST

### Phase 1: State Tracking System
- [ ] Create `N5/scripts/meeting_state_manager.py`
- [ ] Implement `load_state()` function
- [ ] Implement `save_state()` function
- [ ] Implement `add_processed_event()` function
- [ ] Implement `is_event_processed()` function
- [ ] Create `N5/records/meetings/` directory
- [ ] Initialize `.processed.json` file
- [ ] Create `N5/tests/test_state_manager.py`
- [ ] Write unit tests for all functions
- [ ] Test with mock event IDs
- [ ] Verify state persistence
- [ ] Test error handling (corrupted file, missing file)

### Phase 2: Stakeholder Profile System
- [ ] Create `N5/scripts/stakeholder_profile_manager.py`
- [ ] Implement `create_stakeholder_profile()` function
- [ ] Implement `find_stakeholder_profile()` function
- [ ] Implement `update_stakeholder_profile()` function
- [ ] Implement `append_meeting_to_profile()` function
- [ ] Create profile template string
- [ ] Implement directory name sanitization
- [ ] Implement email search/matching
- [ ] Create `N5/tests/test_profile_manager.py`
- [ ] Write unit tests for all functions
- [ ] Test profile creation with mock data
- [ ] Test profile lookup by email
- [ ] Test profile update/append
- [ ] Verify markdown formatting
- [ ] Test with multiple stakeholder types

### Phase 3: Integration Testing
- [ ] Create test script with mock calendar event
- [ ] Create test script with mock Gmail context
- [ ] Test full flow: detect → lookup → create/update → mark processed
- [ ] Verify state tracking works end-to-end
- [ ] Verify profile creation works end-to-end
- [ ] Test with multiple events (same attendee)
- [ ] Test with multiple events (different attendees)
- [ ] Verify no duplicates created
- [ ] Document any issues or edge cases
- [ ] Create summary report of functionality

---

## SUCCESS CRITERIA

### Phase 1 Complete When:
- [ ] `.processed.json` created and persists
- [ ] Can load/save state reliably
- [ ] Can add events and check if processed
- [ ] All unit tests passing
- [ ] Error handling robust

### Phase 2 Complete When:
- [ ] Profile directories created correctly
- [ ] Profile markdown well-formatted
- [ ] Can create profiles for new stakeholders
- [ ] Can find existing profiles by email
- [ ] Can update profiles with new meetings
- [ ] All unit tests passing

### Integration Complete When:
- [ ] Full mock flow works end-to-end
- [ ] State tracking prevents duplicates
- [ ] Profile caching works (finds existing)
- [ ] Multiple meetings handled correctly
- [ ] Ready for API integration (Phase 2B Priority 2)

---

## NEXT STEPS AFTER COMPLETION

Once Priority 1 is complete:

**Wait for Howie Phase 2A confirmation**
- Howie implements calendar format changes
- Test calendar event has V-OS tags
- Verify Purpose and Context fields

**Then proceed to Priority 2:**
- Integrate Google Calendar API in `meeting_prep_digest.py`
- Integrate Gmail API in `meeting_prep_digest.py`
- Test with real calendar events
- Verify tag extraction from real data

**Then proceed to Priority 3:**
- Build `meeting_monitor.py` using state + profile managers
- Implement polling loop (every 15 min)
- Implement priority queue
- Test with real events

**Then proceed to Priority 4:**
- Set up scheduled execution
- Deploy to production
- Monitor for first real detection

---

## NOTES

**Key Principles:**
- Build incrementally with tests at each stage
- Use mock data until Howie confirms
- Keep functions modular and reusable
- Document any assumptions or decisions
- Graceful error handling throughout

**Dependencies:**
- Python 3.12
- Standard library (json, os, pathlib, datetime)
- pytz for timezone handling
- No external API calls yet (mocks only)

**Timeline:**
- Priority 1: 2-4 hours to build and test
- Ready for Priority 2 as soon as Howie confirms

---

## HANDOFF TO NEW THREAD

**Load this document and execute:**

```
Load file 'N5/docs/PHASE-2B-PREP-HANDOFF.md' and execute Priority 1.

Build the state tracking system and stakeholder profile system per the specifications.

Create all required functions, test with mock data, and verify everything works end-to-end.

Report back with completion status and any issues encountered.
```

---

**Status:** READY TO EXECUTE  
**Date:** 2025-10-12  
**Next Action:** Build Priority 1 (State Tracking + Stakeholder Profiles)
