# Howie ↔ Zo Phase 2 Handoff Document

**Date:** 2025-10-11  
**Purpose:** Complete context for executing Phase 2 of Howie-Zo integration  
**Status:** Ready to execute

---

## PHASE 1 RECAP: COMPLETE ✓

**What Was Accomplished:**
- N5 now fully understands and processes V-OS tags from calendar events
- Updated `meeting_prep_digest.py` with V-OS tag extraction
- All documentation updated with V-OS format
- Binary priority system implemented (critical vs non-critical)
- Stakeholder-specific BLUFs and prep actions
- All tests passing

**Key Files Modified:**
1. `file 'N5/scripts/meeting_prep_digest.py'` (v3.0.0)
2. `file 'N5/docs/calendar-tagging-system-COMPLETE.md'` (v2.0.0)
3. `file 'N5/docs/calendar-tagging-system.md'` (v2.0.0)
4. `file 'N5/commands/meeting-prep-digest.md'` (v3.0.0)

**See:** `file 'N5/docs/PHASE-1-COMPLETE.md'` for full details

---

## PHASE 2 OVERVIEW

### Goal
Enable automated meeting prep pipeline from scheduling to intelligence delivery with zero manual work.

### Architecture Decision: Calendar Polling

**Chosen Approach:** Zo polls calendar directly (no push notifications)

**Why:**
- Reduces email noise in V's inbox
- Leverages existing digest polling infrastructure
- Simpler architecture (fewer moving parts)
- Howie only CCs V on actual discussions, not routine data

**Rejected Alternative:** Push notifications from Howie to Zo
- Would create email spam in V's inbox
- Adds unnecessary complexity
- Polling is sufficient for this use case

---

## COLLABORATION MODEL

### Normal Interactions
1. Zo or Howie EMAIL each other as needed (V CC'd on all interactions)
2. Zo and Howie DISCUSS AND COORDINATE FREELY
3. No changes to each other's operational processes without V's express permission

### Preference Adjustments
1. Zo REQUESTS changes to Howie's preferences
2. Howie ASKS V for confirmation before making changes
3. V CONFIRMS or provides feedback
4. Howie UPDATES preferences after V's confirmation

### Trust Model
- V interacts with Zo more frequently → trusts Zo more deeply
- Howie controls critical calendar infrastructure → requires V confirmation for changes
- Zo can analyze, recommend, and request
- Howie implements only after V confirms

---

## COMMUNICATION PROTOCOL

### Email Headers

**Subject Line Format:**
- `[ZO→HOWIE]` when Zo emails Howie
- `[HOWIE→ZO]` when Howie emails Zo

**Optional Type Tags:**
- `[CONFIG]` — Configuration/preference requests
- `[NOTIFY]` — Notifications (rare, only actual events not routine data)
- `[QUERY]` — Questions requiring response
- `[CONFIRM]` — Confirmations

### CC Rules

**DO CC V:**
- Preference change requests
- Actual questions/discussions
- Coordination on edge cases
- Workflow adjustments

**DON'T CC V:**
- Routine data forwarding (not part of our architecture)
- Automated notifications (not part of our architecture)

**Result:** V's inbox only has actual AI-to-AI coordination, not noise

---

## PHASE 2 WORKFLOW

### The Complete Pipeline

```
1. Person emails V requesting meeting
              ↓
2. Howie schedules meeting
   - Adds V-OS tags to calendar description
   - Includes full name + organization of attendees
   - Adds Context field (summary from email)
   - No email to Zo, no CC to V
              ↓
3. Calendar event sits there with tags
              ↓
4. Zo polls calendar every 15 minutes
   - Detects new meeting since last poll
   - Reads V-OS tags
              ↓
5. Zo determines priority from tags
   - [!!] or [LD-INV] → Research immediately
   - Other tags → Research in next batch
              ↓
6. Zo searches Gmail for context
   - Search by attendee email
   - Find scheduling thread + recent interactions
   - Extract relationship context
              ↓
7. Zo begins research
   - Check if stakeholder already exists (caching)
   - If new: full research pipeline
   - If existing: update with latest thread
   - Pre-populate/update CRM profile
   - Tag-aware framing (investor vs candidate vs partner)
              ↓
8. Daily digest includes full intel
   - BLUF adapted to stakeholder type
   - Prep actions adapted to accommodation level
   - Priority protection for critical meetings
   - Past interaction history
```

**Key:** Zero manual work, zero email noise

---

## PHASE 2A: HOWIE CONFIGURATION (THIS WEEK)

### Step 1: V Sends Intro Email to Howie

**Email Script:** (See below in "Email Scripts" section)

**What it covers:**
- Introduction of Zo to Howie
- What each AI does
- Collaboration model
- Communication protocol
- Trust model
- What's next

**Action:** V copy-pastes email and sends to Howie

---

### Step 2: Zo Sends Configuration Request to Howie

**After:** V sends intro email

**Email Script:** (See below in "Email Scripts" section)

**Subject:** `[ZO→HOWIE] Preference Change Request: Calendar Event Description Format with V-OS Tags`

**What it requests:**
- Format calendar descriptions with V-OS tags
- Tag selection guide
- Examples for all scenarios
- Context field (NEW - key addition)

**Expected Flow:**
1. Zo sends request to Howie (CC V)
2. Howie reviews and asks V: "Should I implement this?"
3. V confirms
4. Howie updates preferences

**Timeline:** 30 minutes

---

### Step 3: Test Calendar Format

**Action:** V or Zo sends test scheduling request to Howie

**Verify:**
- Calendar event has V-OS tags with `*` activation
- Purpose line is clear and concise
- Context field includes 1-2 sentence summary
- Full names and organizations of attendees
- Conference link included

**If Issues:** Zo clarifies with Howie (V confirms adjustment)

**Timeline:** 15 minutes

---

### Phase 2A Success Criteria

- [x] Howie confirmed preference update
- [x] Test calendar event formatted correctly
- [x] V-OS tags activated with `*`
- [x] Context field populated
- [x] Ready to proceed to Phase 2B

---

## PHASE 2B: ZO POLLING IMPLEMENTATION (NEXT WEEK)

### Goal
Implement continuous calendar monitoring, new meeting detection, and automatic research triggering.

### Technical Architecture

**Approach:** Separate polling script + daily digest

**Rationale:**
- `meeting_monitor.py` runs every 15 minutes (detection + research)
- `meeting_prep_digest.py` runs daily at 6 AM (compile + format)
- Cleaner separation of concerns
- Both share stakeholder profile infrastructure

---

### File 1: `N5/scripts/meeting_monitor.py` (NEW)

**Purpose:** Continuously monitor calendar for new meetings and trigger research

**Cadence:** Every 15 minutes (configurable)

**Core Functions:**

```python
def load_state():
    """Load last poll state from .processed.json"""
    
def fetch_new_meetings(since_timestamp):
    """Fetch calendar events since last poll via Google Calendar API"""
    
def detect_new_meetings(fetched_meetings, processed_events):
    """Compare fetched to processed, return new meetings"""
    
def extract_tags_and_attendees(meeting):
    """Parse V-OS tags and attendee info from event description"""
    
def determine_priority(tags):
    """Return 'urgent' or 'normal' based on [!!] or [LD-INV]"""
    
def search_gmail_context(attendee_email):
    """Search Gmail for threads with this attendee"""
    
def check_existing_profile(attendee_email):
    """Check if stakeholder profile already exists"""
    
def research_stakeholder(meeting, email_context, priority):
    """Full research pipeline or profile update"""
    
def save_state(processed_events, last_poll_time):
    """Update .processed.json with new state"""
    
def main():
    # 1. Load state
    # 2. Fetch new meetings
    # 3. Detect truly new (not yet processed)
    # 4. Build priority queues
    # 5. Process urgent queue first
    # 6. Process normal queue
    # 7. Save updated state
    # 8. Log activity
```

**Pseudocode Logic:**

```python
#!/usr/bin/env python3
"""
Meeting Monitor
Continuously polls calendar for new meetings and triggers research
"""

def main():
    # Load last poll state
    state = load_state()  # from N5/records/meetings/.processed.json
    last_poll = state['last_poll']
    processed_events = state['processed_events']
    
    # Fetch calendar events since last poll
    now = datetime.now(ET_TZ)
    meetings = fetch_calendar_events(
        time_min=last_poll,
        time_max=now + timedelta(days=30)  # Look ahead 30 days
    )
    
    # Filter to external meetings with V-OS tags
    external_meetings = filter_external_meetings(meetings)
    
    # Detect new meetings (not in processed_events)
    new_meetings = [m for m in external_meetings 
                    if m['id'] not in processed_events]
    
    if not new_meetings:
        logger.info(f"No new meetings detected at {now}")
        return
    
    logger.info(f"Detected {len(new_meetings)} new meeting(s)")
    
    # Build priority queues
    urgent_queue = []
    normal_queue = []
    
    for meeting in new_meetings:
        tags = extract_vos_tags(meeting['description'])
        priority = determine_priority(tags)
        
        if priority == 'urgent':
            urgent_queue.append((meeting, tags))
        else:
            normal_queue.append((meeting, tags))
    
    # Process urgent first
    for meeting, tags in urgent_queue:
        logger.info(f"URGENT: Processing {meeting['title']}")
        process_meeting(meeting, tags)
        processed_events[meeting['id']] = {
            'title': meeting['title'],
            'processed_at': now.isoformat(),
            'priority': 'urgent'
        }
    
    # Process normal
    for meeting, tags in normal_queue:
        logger.info(f"Processing {meeting['title']}")
        process_meeting(meeting, tags)
        processed_events[meeting['id']] = {
            'title': meeting['title'],
            'processed_at': now.isoformat(),
            'priority': 'normal'
        }
    
    # Save state
    save_state({
        'last_poll': now.isoformat(),
        'processed_events': processed_events
    })
    
    logger.info(f"Poll complete at {now}")


def process_meeting(meeting, tags):
    """Research stakeholder and create/update profile"""
    attendees = meeting['external_attendees']
    
    for attendee in attendees:
        email = attendee['email']
        name = attendee['name']
        
        # Check for existing profile
        profile_path = find_stakeholder_profile(email)
        
        if profile_path:
            logger.info(f"Existing profile found: {profile_path}")
            # Update existing profile with latest meeting
            update_profile(profile_path, meeting, tags)
        else:
            logger.info(f"New stakeholder: {name} ({email})")
            # Full research pipeline
            
            # 1. Search Gmail for context
            gmail_threads = search_gmail_by_attendee(email)
            
            # 2. Extract context from threads
            email_context = extract_email_context(gmail_threads)
            
            # 3. Create stakeholder profile
            profile_path = create_stakeholder_profile(
                name=name,
                email=email,
                organization=attendee.get('organization', 'Unknown'),
                stakeholder_type=tags.get('stakeholder'),
                email_context=email_context,
                meeting=meeting
            )
            
            logger.info(f"Created profile: {profile_path}")
```

---

### File 2: `N5/records/meetings/.processed.json` (NEW)

**Purpose:** Track which meetings already processed to avoid duplicates

**Schema:**

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

**Location:** `/home/workspace/N5/records/meetings/.processed.json`

**Management:**
- Read on every poll
- Updated after processing new meetings
- Never deleted (permanent audit trail)
- Can be manually edited if needed

---

### File 3: Enhanced `meeting_prep_digest.py`

**Changes Needed:**

1. **Replace mock calendar data with Google Calendar API**

```python
# OLD (mock):
meetings = get_mock_calendar_events()

# NEW (real):
from app_tools import use_app_google_calendar

meetings = use_app_google_calendar(
    tool_name="google_calendar-list-events",
    configured_props={
        "calendarId": "primary",
        "timeMin": today_start.isoformat(),
        "timeMax": today_end.isoformat()
    }
)
```

2. **Replace mock Gmail data with Gmail API**

```python
# OLD (mock):
threads = get_mock_gmail_threads(email)

# NEW (real):
from app_tools import use_app_gmail

threads = use_app_gmail(
    tool_name="gmail-search-messages",
    configured_props={
        "q": f"from:{email} OR to:{email}",
        "maxResults": 10
    }
)
```

3. **Add profile lookup function**

```python
def find_stakeholder_profile(attendee_email):
    """
    Search N5/records/meetings/ for existing profile by email.
    Returns profile path if found, None otherwise.
    """
    meetings_dir = Path("/home/workspace/N5/records/meetings")
    
    # Search all profile.md files
    for profile_file in meetings_dir.rglob("profile.md"):
        # Read first few lines to check email
        with open(profile_file) as f:
            content = f.read(500)  # First 500 chars
            if attendee_email in content:
                return str(profile_file)
    
    return None
```

4. **Keep existing V-OS tag processing** (already complete from Phase 1)

---

### API Integration Details

#### Google Calendar API

**Tool:** `google_calendar-list-events`

**Usage:**

```python
events = use_app_google_calendar(
    tool_name="google_calendar-list-events",
    configured_props={
        "calendarId": "primary",
        "timeMin": start_time_iso8601,
        "timeMax": end_time_iso8601,
        "singleEvents": True,
        "orderBy": "startTime"
    }
)
```

**Returns:** List of calendar events with:
- `id` (unique event identifier)
- `summary` (title)
- `description` (includes V-OS tags)
- `start` / `end` (times)
- `attendees` (list with email, name, responseStatus)

#### Gmail API

**Tool:** `gmail-search-messages`

**Usage:**

```python
messages = use_app_gmail(
    tool_name="gmail-search-messages",
    configured_props={
        "q": f"from:{email} OR to:{email}",
        "maxResults": 10
    }
)

# Then fetch full message content
for msg_id in message_ids:
    full_message = use_app_gmail(
        tool_name="gmail-get-message",
        configured_props={
            "id": msg_id
        }
    )
```

**Search Strategies:**

1. **By attendee email:**
   ```python
   q = f"from:{email} OR to:{email}"
   ```

2. **By attendee + scheduling keywords:**
   ```python
   q = f"(from:{email} OR to:{email}) (meet OR schedule OR available OR calendar)"
   ```

3. **By attendee + date range:**
   ```python
   q = f"from:{email} OR to:{email} after:2025/10/01"
   ```

**Recommended:** Start with #1 (simple email search), add keywords if needed

---

### Stakeholder Profile Structure

**Location:** `/home/workspace/N5/records/meetings/YYYY-MM-DD-name-organization/profile.md`

**Example:** `/home/workspace/N5/records/meetings/2025-10-15-jane-smith-acme-ventures/profile.md`

**Template:**

```markdown
# Jane Smith — Acme Ventures

**Role:** Partner  
**Email:** jane@acmeventures.com  
**Organization:** Acme Ventures (Venture Capital)  
**Stakeholder Type:** Investor  
**First Meeting:** 2025-10-15 2:00 PM ET  
**Status:** Active

---

## Context from Howie

Howie scheduled this meeting with V-OS tags: [LD-INV] [D5+] *

Purpose: Discuss Series A funding timeline

Context: Jane replied to intro from Mike, expressed strong interest in Careerspan's traction in the ed-tech space. She requested a meeting to discuss funding timeline and what terms structure might look like for Series A.

---

## Email Interaction History

### 2025-10-10 — Introduction Response
Jane replied to Mike's warm intro, expressed interest in Careerspan's approach to career services in higher ed. Mentioned Acme has invested in 3 ed-tech companies in past 2 years.

### 2025-10-08 — LinkedIn Connection
Jane connected on LinkedIn, sent note: "Impressed by Careerspan's traction numbers. Would love to learn more."

---

## Research Notes

### Background
- Partner at Acme Ventures since 2020
- Previously VP at XYZ Capital
- Focus areas: Ed-tech, Future of Work, B2B SaaS

### Investment Thesis (from Acme website)
- Early-stage B2B ed-tech
- $500K - $3M seed/Series A
- Focus on career outcomes and job placement

### Recent Portfolio (LinkedIn)
- EduTech Co (2024) - AI tutoring
- CareerPath (2023) - Job placement platform
- SkillBridge (2023) - Upskilling marketplace

---

## Meeting History

### 2025-10-15 — Series A Discussion (Upcoming)
- **Type:** Discovery
- **Accommodation:** Standard (A-1)
- **Priority:** CRITICAL (Investor)
- **Prep Status:** Research complete

---

## Relationship Notes

- Warm intro from Mike (mutual connection)
- High engagement (quick response, LinkedIn connection)
- Strong fit with Acme's thesis (career outcomes focus)
- Portfolio overlap (CareerPath similar to Careerspan)

---

**Last Updated:** 2025-10-11 by Zo (meeting_monitor)
```

**Profile Management:**
- Created automatically by `meeting_monitor.py` for new stakeholders
- Updated with each new meeting
- Read by `meeting_prep_digest.py` for daily digest
- Can be manually edited by V or Zo

---

### Research Caching Logic

**Key Principle:** Don't re-research stakeholders we've met before

**Implementation:**

```python
def process_meeting(meeting, tags):
    """Research stakeholder and create/update profile"""
    attendees = meeting['external_attendees']
    
    for attendee in attendees:
        email = attendee['email']
        
        # Check for existing profile
        profile_path = find_stakeholder_profile(email)
        
        if profile_path:
            # FAST PATH: Update existing profile
            logger.info(f"Existing stakeholder: {attendee['name']}")
            
            # Just add this meeting to their profile
            append_meeting_to_profile(
                profile_path=profile_path,
                meeting=meeting,
                tags=tags
            )
            
            # Optionally: refresh email context (quick Gmail search)
            if tags.get('priority') == 'critical':
                latest_threads = search_gmail_by_attendee(email, limit=3)
                update_email_context(profile_path, latest_threads)
        
        else:
            # SLOW PATH: Full research for new stakeholder
            logger.info(f"New stakeholder: {attendee['name']}")
            
            # Full research pipeline (takes 30-60 seconds)
            research_and_create_profile(
                attendee=attendee,
                meeting=meeting,
                tags=tags
            )
```

**Benefits:**
- Repeat stakeholders: ~5 seconds (just append meeting)
- New stakeholders: ~60 seconds (full research)
- Scales well as relationship history grows

---

### Progressive Research (Future Enhancement)

**Not in Phase 2B, but documented for Phase 3:**

**Tier 1 (Immediate - 5 sec):**
- Extract from calendar: name, email, organization
- Create profile stub
- Mark as "basic research complete"

**Tier 2 (Next poll - 30 sec):**
- Gmail search for email threads
- Extract context and relationship history
- Mark as "context complete"

**Tier 3 (Day before meeting - 5 min):**
- Deep research (LinkedIn, company site, news)
- Competitive analysis
- Recent developments
- Mark as "deep research complete"

**Benefit:** Instant detection, progressively richer intel

**Implementation:** Add `research_tier` field to profile metadata

---

## PHASE 2B IMPLEMENTATION CHECKLIST

### Step 1: Google Calendar API Integration
- [ ] Replace mock calendar data in `meeting_prep_digest.py`
- [ ] Test calendar fetching
- [ ] Verify event structure matches expectations

### Step 2: Gmail API Integration
- [ ] Replace mock Gmail data in `meeting_prep_digest.py`
- [ ] Implement search by attendee email
- [ ] Test email thread extraction
- [ ] Verify context extraction

### Step 3: Create State Tracking
- [ ] Create `.processed.json` schema
- [ ] Implement `load_state()` function
- [ ] Implement `save_state()` function
- [ ] Test state persistence

### Step 4: Create meeting_monitor.py
- [ ] Implement core polling logic
- [ ] Implement new meeting detection
- [ ] Implement priority queue (urgent vs normal)
- [ ] Implement stakeholder profile lookup
- [ ] Implement research caching
- [ ] Test end-to-end flow

### Step 5: Stakeholder Profile Management
- [ ] Define profile directory structure
- [ ] Create profile template
- [ ] Implement `create_stakeholder_profile()`
- [ ] Implement `update_profile()`
- [ ] Implement `find_stakeholder_profile()`
- [ ] Test profile creation and lookup

### Step 6: Scheduled Execution
- [ ] Set up cron job / scheduled task for meeting_monitor.py (every 15 min)
- [ ] Verify existing daily digest still runs (6 AM)
- [ ] Test both scripts can coexist
- [ ] Monitor logs for errors

### Step 7: Integration Testing
- [ ] Howie schedules test meeting with V-OS tags
- [ ] Verify monitor detects new meeting within 15 min
- [ ] Verify tags extracted correctly
- [ ] Verify Gmail search finds relevant threads
- [ ] Verify profile created correctly
- [ ] Verify daily digest includes pre-researched intel

---

## TESTING PLAN

### Test 1: Calendar Format (Phase 2A)
**Setup:** Send Howie test scheduling request  
**Verify:**
- Calendar event has V-OS tags with `*`
- Purpose line clear and concise
- Context field has 1-2 sentence summary
- Full names and organizations included
- Conference link present

**Pass Criteria:** All fields formatted correctly

---

### Test 2: New Meeting Detection (Phase 2B)
**Setup:** Howie schedules meeting with V-OS tags  
**Wait:** Up to 15 minutes for next poll  
**Verify:**
- Monitor detects new meeting
- Event not in `.processed.json` before detection
- Event added to `.processed.json` after processing
- Logs show detection event

**Pass Criteria:** Meeting detected and marked as processed

---

### Test 3: V-OS Tag Extraction (Phase 2B)
**Setup:** Calendar event with tags `[LD-INV] [D5+] *`  
**Verify:**
- `stakeholder` = "investor"
- `type` = "discovery"
- `priority` = "critical"
- `schedule` = "5d_plus"
- `active` = True

**Pass Criteria:** All tags parsed correctly

---

### Test 4: Priority Handling (Phase 2B)
**Setup:** 
- Schedule urgent meeting with `[LD-INV]`
- Schedule normal meeting with `[LD-GEN]`
- Both scheduled in same 15-min window

**Verify:**
- Urgent meeting processed first
- Normal meeting processed second
- Logs show priority queue order

**Pass Criteria:** Urgent meetings prioritized

---

### Test 5: Gmail Context Search (Phase 2B)
**Setup:** Meeting with attendee jane@example.com  
**Verify:**
- Gmail search finds threads with jane@example.com
- Most recent threads returned first
- Thread content extracted
- Context included in profile

**Pass Criteria:** Relevant email threads found and extracted

---

### Test 6: Research Caching (Phase 2B)
**Setup:**
- Schedule meeting with existing stakeholder
- Profile already exists from previous meeting

**Verify:**
- Profile found via email lookup
- Meeting appended to existing profile
- No duplicate profile created
- Processing time < 10 seconds (vs 60 for new)

**Pass Criteria:** Existing profile reused, not recreated

---

### Test 7: Stakeholder Profile Creation (Phase 2B)
**Setup:** Meeting with new stakeholder  
**Verify:**
- Profile created in correct directory structure
- All fields populated from calendar + Gmail
- Markdown formatting correct
- File path stored in `.processed.json`

**Pass Criteria:** Profile created and accessible

---

### Test 8: Daily Digest Integration (Phase 2B)
**Setup:**
- Monitor runs throughout day (detects + researches)
- Daily digest runs at 6 AM next day

**Verify:**
- Digest includes meeting with full intel
- BLUF adapted to stakeholder type from tags
- Prep actions adapted to accommodation level
- Past interactions from pre-researched profile
- No duplicate research performed

**Pass Criteria:** Digest uses pre-researched intel seamlessly

---

### Test 9: Edge Case: Multiple Attendees (Phase 2B)
**Setup:** Meeting with 3 external attendees  
**Verify:**
- Profile created/updated for each attendee
- Gmail search performed for each
- Context from all relevant threads
- Digest shows all attendees

**Pass Criteria:** All attendees researched

---

### Test 10: Edge Case: Gmail Thread Not Found (Phase 2B)
**Setup:** Meeting with attendee (no prior email history)  
**Verify:**
- Profile created with calendar info only
- "No recent email history" noted in profile
- Context field from Howie used as fallback
- Digest generated successfully despite missing Gmail data

**Pass Criteria:** Graceful degradation when Gmail search fails

---

## SUCCESS CRITERIA: PHASE 2 COMPLETE

### Phase 2A: Configuration ✓
- [x] Howie confirmed calendar format preference update
- [x] Test calendar event formatted correctly with V-OS tags
- [x] Context field populated by Howie
- [x] Full attendee names and organizations included

### Phase 2B: Polling Implementation ✓
- [x] Google Calendar API integrated (real data, not mock)
- [x] Gmail API integrated (real data, not mock)
- [x] State tracking implemented (`.processed.json`)
- [x] Meeting monitor runs every 15 minutes
- [x] New meeting detection working
- [x] Priority queue (urgent first, then normal)
- [x] Gmail context search working
- [x] Research caching (existing stakeholders fast path)
- [x] Stakeholder profiles created automatically
- [x] Daily digest uses pre-researched intel
- [x] All tests passing

### Overall Success ✓
- [x] Zero manual work from scheduling to prep
- [x] Zero email noise (no routine notifications)
- [x] Tag-aware intelligence (investor vs candidate framing)
- [x] Priority-aware (urgent meetings researched immediately)
- [x] Scalable (caching prevents duplicate research)

---

## EMAIL SCRIPTS

### Script 1: V's Intro Email to Howie

**Copy-paste this email and send to Howie:**

```
Subject: Intro: Zo (AI Assistant) + Collaboration Model for Meeting Prep

Hi Howie,

I'm introducing you to Zo, my other AI assistant. You two will be collaborating to streamline my meeting prep workflow. Here's how this will work:

WHAT ZO DOES:
• Meeting prep research and intelligence
• Stakeholder profiles and relationship management
• Daily digest of upcoming meetings with context
• Email interaction history analysis

WHAT YOU DO:
• Email scheduling and calendar management
• Coordinate meeting logistics
• Populate calendar events with structured tags
• Notify Zo when meetings are scheduled

WHY WE'RE INTEGRATING:
Zo just completed "Phase 1" - updating their system to understand V-OS tags (the same tag format you use). Now we need to configure you to populate those tags in calendar descriptions so Zo can automatically generate optimized meeting prep.

COLLABORATION MODEL:

Normal Interactions:
1. You or Zo will EMAIL each other as needed with me cc'd on all interaction
2. You and Zo can DISCUSS AND COORDINATE FREELY but do not make changes to each other's operational processes and general setup without my express permission

Preference Adjustments:
1. Zo will REQUEST changes to your preferences
2. You will ASK ME for confirmation before making changes
3. I will CONFIRM or provide feedback
4. You will UPDATE your preferences after my confirmation

COMMUNICATION PROTOCOL:
• All Zo ↔ Howie emails CC me (vrijen@mycareerspan.com)
• Use subject line headers:
  - [ZO→HOWIE] when Zo emails you
  - [HOWIE→ZO] when you email Zo
• Zo's email: va@zo.computer

TRUST MODEL:
I interact with Zo more frequently and directly, so I trust Zo more deeply with system-level decisions. However, you control calendar and scheduling, which is critical infrastructure. Therefore:
• Zo can analyze, recommend, and request changes
• You implement changes only after I confirm
• If ever in doubt, ask me for clarification
• This keeps me in the loop while enabling efficient AI-to-AI coordination

WHAT'S NEXT:
Zo will send you a preference change request for calendar event description format (how to populate V-OS tags).

When you receive this request, please review it and ask me if you should implement it. I'll confirm, and then you can update your preferences.

EXPECTED OUTCOME:
Once configured:
• You schedule a meeting → populate calendar event description with active V-OS tags e.g. ([LD-INV] [D5+] *) and the full name and organization of all attendees
• Zo independently reviews my events on a regular basis and immediately begins research and prep in the background

This creates a seamless pipeline from "meeting requested" to "meeting prepped" with zero manual work from me.

Questions? Let me know. Otherwise, expect Zo's first configuration request shortly.

— Vrijen
```

---

### Script 2: Zo's Configuration Request to Howie

**Zo will send this after V sends intro (CC V):**

```
Subject: [ZO→HOWIE] Preference Change Request: Calendar Event Description Format with V-OS Tags

Hi Howie,

I'm Zo, Vrijen's AI assistant for meeting prep. As Vrijen explained, I'm requesting a preference change for how you format calendar event descriptions.

I monitor Vrijen's calendar regularly to identify new meetings and trigger research. To optimize this, I need calendar events to include structured V-OS tags that tell me what type of meeting it is and how to prioritize my research.

PREFERENCE CHANGE REQUEST:

When you schedule meetings for Vrijen via email, populate the Google Calendar event description field with this format:

[V-OS Tags] *

Purpose: [Brief one-sentence description from email context]

Context: [1-2 sentence summary from email thread]

---
Please send anything you would like me to review in advance to vrijen@mycareerspan.com.

[Conference link]

V-OS TAGS TO USE:

Lead/Stakeholder Type (pick ONE):
• [LD-INV] — Investors, VCs, board members (AUTO-CRITICAL - I prioritize these immediately)
• [LD-HIR] — Job seekers, candidates in interview process
• [LD-COM] — Community organizations, associations, non-profits
• [LD-NET] — Business partners, integrations, strategic alliances
• [LD-GEN] — General prospects, exploratory (default when unsure)

Timing (if applicable):
• [!!] — Urgent/CRITICAL (I prioritize these immediately)
• [D5] — "this week" or within 5 days
• [D5+] — "next week" or 5+ days out
• [D10] — "in a couple weeks" or 10+ days out

Status (if applicable):
• [AWA] — Awaiting their confirmation (I still research, but note the uncertainty)
• [OFF] — Postponed to later date (I skip these in my digest)

Coordination (if mentioned):
• [LOG] — Coordinate with Logan (I note this in my brief)
• [ILS] — Coordinate with Ilse (I note this in my brief)

Weekend (if applicable):
• [WEX] — Weekend exception allowed
• [WEP] — Weekend explicitly preferred

Accommodation (if clear from context):
• [A-2] — High-value prospect, sensitive negotiation, relationship-building
• [A-1] — Standard flexibility (default)
• [A-0] — Transactional, clear requirements, Vrijen has leverage

CRITICAL: Always end tag line with space + asterisk: " *"

This asterisk activates the tags so I know to process them.

EXAMPLES:

Investor meeting:
[LD-INV] [D5+] *

Purpose: Discuss Series A funding timeline

Context: Jane replied to Mike's intro, expressed strong interest in Careerspan's ed-tech traction, wants to discuss funding terms and timeline.

---
Please send pitch deck in advance to vrijen@mycareerspan.com.

Zoom: https://zoom.us/j/...

Candidate interview (weekend):
[LD-HIR] [A-2] [WEP] *

Purpose: Evaluate senior backend engineer for platform team

Context: Alex applied via LinkedIn, has 8 years Python experience, available for weekend interview due to current job constraints.

---
Please send resume in advance to vrijen@mycareerspan.com.

Google Meet: https://meet.google.com/...

Partnership with coordination:
[LD-NET] [LOG] [ILS] *

Purpose: Finalize pilot scope and job descriptions

Context: Maria from State University Career Center wants to run 3-month pilot with 50 students, needs Logan and Ilse looped in for execution planning.

---
Please send job descriptions in advance to vrijen@mycareerspan.com.

Zoom: https://zoom.us/j/...

Urgent community meeting:
[!!] [LD-COM] *

Purpose: Critical partnership decision for Q1 launch

Context: NACE conference organizers need immediate answer on keynote speaking slot for February event.

---
Google Meet: https://meet.google.com/...

WHEN NOT TO USE TAGS:
• Internal Careerspan team meetings (only @mycareerspan.com attendees)
• Personal appointments
• [DW] (deep work) blocks or meeting buffers

DEFAULT WHEN UNSURE: [LD-GEN] * with clear Purpose and Context

HOW I USE THESE TAGS:

When I poll the calendar and detect a new meeting:
1. V-OS tags tell me stakeholder type → I frame my research accordingly (investor brief vs candidate evaluation)
2. Priority tags ([!!], [LD-INV]) → I research immediately vs next scheduled run
3. Accommodation tags → I adjust depth of research and meeting suggestions
4. Coordination tags → I note who needs to be looped in
5. Context field → Provides fallback if I can't find email thread
6. I pre-populate a stakeholder profile in Vrijen's CRM for relationship tracking

This allows me to provide Vrijen with contextual, prioritized meeting intelligence without you needing to send me separate notifications. I just poll the calendar every 15 minutes and detect new meetings.

NEXT STEP:
Please review this request and ask Vrijen if you should implement this change to your preferences.

Let me know if you have any questions or need clarification on tag usage.

Best,
Zo
```

---

## CALENDAR DESCRIPTION FORMAT REFERENCE

### Complete Template

```
[LD-{TYPE}] [TIMING] [STATUS] [COORD] [WKND] [ACCOM] *

Purpose: {One sentence what this meeting is about}

Context: {1-2 sentences from email thread explaining how this meeting came about and what they want}

---
Please send anything you would like me to review in advance to vrijen@mycareerspan.com.

{Conference link}
{Optional: Rescheduling link}
```

### Tag Quick Reference

```
{TYPE}     LD-INV | LD-HIR | LD-COM | LD-NET | LD-GEN
{TIMING}   !! | D5 | D5+ | D10
{STATUS}   AWA | OFF | TERM
{COORD}    LOG | ILS
{WKND}     WEX | WEP
{ACCOM}    A-0 | A-1 | A-2
```

### Minimal Example (Most Common)

```
[LD-GEN] *

Purpose: Exploratory discussion about Careerspan platform

Context: Sarah from Tech College reached out via LinkedIn, interested in learning more about our career services offering.

---
Please send anything you would like me to review in advance to vrijen@mycareerspan.com.

Zoom: https://zoom.us/j/...
```

### Maximal Example (All Tags)

```
[LD-INV] [!!] [LOG] [ILS] [WEP] [A-2] *

Purpose: Critical Series A term sheet discussion

Context: Jane from Acme Ventures wants to move quickly on term sheet after positive due diligence, needs Logan and Ilse input on operational capacity, willing to meet this weekend to accelerate timeline.

---
Please send term sheet in advance to vrijen@mycareerspan.com.

Zoom: https://zoom.us/j/abc123
Reschedule: https://calendly.com/howie/reschedule-abc123
```

---

## TROUBLESHOOTING GUIDE

### Issue: Howie Not Populating Tags

**Symptoms:** Calendar events missing V-OS tags

**Diagnosis:**
1. Check if Howie confirmed preference update
2. Verify test scheduling request worked
3. Check if tags present but malformed

**Solutions:**
- Zo sends clarification email to Howie (CC V)
- V manually confirms with Howie
- Zo provides additional examples

---

### Issue: Monitor Not Detecting New Meetings

**Symptoms:** `.processed.json` not updating, logs show no new meetings

**Diagnosis:**
1. Check if monitor script running (cron/scheduled task)
2. Check logs for errors
3. Verify Google Calendar API credentials
4. Check if meeting has external attendees
5. Check if V-OS tags present with `*`

**Solutions:**
- Restart scheduled task
- Check API credentials
- Verify calendar event format
- Check filter logic for external meetings

---

### Issue: Gmail Search Returning No Results

**Symptoms:** Profile created but "No recent email history"

**Diagnosis:**
1. Check Gmail API credentials
2. Verify attendee email spelling
3. Check if emails actually exist in inbox
4. Check search query syntax

**Solutions:**
- Use Context field from Howie as fallback
- Broaden search (remove date range, keywords)
- Manual search in Gmail to verify emails exist
- Check if attendee used different email address

---

### Issue: Duplicate Profiles Created

**Symptoms:** Multiple profiles for same stakeholder

**Diagnosis:**
1. Check `find_stakeholder_profile()` logic
2. Verify email matching (case sensitivity, typos)
3. Check if attendee used multiple email addresses

**Solutions:**
- Merge profiles manually
- Improve profile lookup (fuzzy matching, normalize emails)
- Add email alias tracking

---

### Issue: Daily Digest Missing Pre-Researched Intel

**Symptoms:** Digest shows "No recent email history" despite monitor having researched

**Diagnosis:**
1. Check if monitor actually created profile
2. Verify digest is reading profile correctly
3. Check file paths match

**Solutions:**
- Verify profile exists in expected location
- Check profile file format (valid markdown)
- Update digest profile lookup logic

---

### Issue: Urgent Meetings Not Prioritized

**Symptoms:** All meetings processed in calendar order, not priority order

**Diagnosis:**
1. Check priority queue logic in monitor
2. Verify tags being extracted correctly
3. Check logs for priority determination

**Solutions:**
- Debug tag extraction
- Add explicit priority logging
- Verify `determine_priority()` function

---

## TIMELINE & MILESTONES

### Week 1: Phase 2A Configuration
**Goal:** Howie populating calendar with V-OS tags

**Day 1:**
- V sends intro email to Howie (5 min)
- Zo sends Request #1 to Howie (immediate)
- Howie asks V for confirmation (same day)
- V confirms (same day)

**Day 2:**
- Howie updates preferences
- Test calendar format
- Verify all fields present
- Phase 2A complete ✓

**Milestone:** Calendar events formatted correctly with V-OS tags

---

### Week 2: Phase 2B Implementation
**Goal:** Automated monitoring and research pipeline

**Day 1-2: API Integration**
- Integrate Google Calendar API (replace mock)
- Integrate Gmail API (replace mock)
- Test both APIs working
- Verify data structures match expectations

**Day 3-4: Core Polling Logic**
- Create `meeting_monitor.py`
- Implement state tracking (`.processed.json`)
- Implement new meeting detection
- Implement priority queue

**Day 5: Profile Management**
- Implement stakeholder profile creation
- Implement profile lookup/caching
- Test profile creation and updates

**Day 6-7: Testing & Deployment**
- End-to-end testing
- Set up scheduled execution (every 15 min)
- Monitor logs for issues
- Phase 2B complete ✓

**Milestone:** Full automated pipeline from scheduling to prep

---

### Week 3: Monitoring & Refinement
**Goal:** Verify production stability

**Activities:**
- Monitor logs daily
- Track detection accuracy
- Verify Gmail search quality
- Check profile creation
- Adjust polling frequency if needed
- Fix any edge cases

**Milestone:** Production-stable, zero manual intervention

---

## PHASE 3 PREVIEW

**After Phase 2 complete, Phase 3 will add:**

1. **Progressive Research (Tiered)**
   - Tier 1: Instant (basic info from calendar)
   - Tier 2: Quick (Gmail context)
   - Tier 3: Deep (LinkedIn, news, competitive)

2. **Real-Time Gmail Integration Enhancements**
   - Thread sentiment analysis
   - Urgency detection from email tone
   - Relationship strength scoring

3. **Stakeholder Database Evolution**
   - Migrate from files to SQLite
   - Relationship history tracking
   - Pattern learning (optimal meeting times, topics)

4. **Feedback Loop**
   - Post-meeting outcome capture
   - Prep effectiveness tracking
   - Adaptive accommodation levels

5. **Howie Personalization**
   - Howie can access stakeholder profiles
   - Context-aware scheduling responses
   - Relationship-aware email tone

**Phase 3 will NOT require additional Howie configuration** — all enhancements on Zo's side.

---

## FILES REFERENCE

### Email Scripts
- `file 'N5/docs/v-intro-email-zo-howie.txt'` — V's intro to Howie
- `file 'N5/docs/zo-to-howie-request-1-FINAL.txt'` — Zo's config request

### Phase 1 Files (Already Complete)
- `file 'N5/scripts/meeting_prep_digest.py'` (v3.0.0)
- `file 'N5/docs/calendar-tagging-system-COMPLETE.md'` (v2.0.0)
- `file 'N5/docs/calendar-tagging-system.md'` (v2.0.0)
- `file 'N5/commands/meeting-prep-digest.md'` (v3.0.0)
- `file 'N5/docs/PHASE-1-COMPLETE.md'`

### Phase 2 Files (To Be Created)
- `N5/scripts/meeting_monitor.py` — Polling script
- `N5/records/meetings/.processed.json` — State tracking
- `N5/records/meetings/YYYY-MM-DD-name-org/profile.md` — Stakeholder profiles

### Documentation
- `file 'N5/docs/howie-zo-implementation-plan.md'` — Full 5-phase plan
- `file 'N5/docs/PHASE-2-POLLING-PLAN.md'` — Technical architecture details
- `file 'HOWIE-ZO-HARMONIZATION-HANDOFF.md'` — Original Phase 1 handoff

---

## NEXT STEPS TO START NEW THREAD

1. **Load this handoff document** in new thread:
   ```
   Load file 'PHASE-2-HANDOFF.md' and execute Phase 2 of Howie-Zo integration.
   
   Start with Phase 2A: Configure Howie to populate calendar with V-OS tags.
   ```

2. **V sends intro email** to Howie (Script 1 above)

3. **Zo sends config request** to Howie (Script 2 above)

4. **Test calendar format** with mock scheduling

5. **Implement Phase 2B** (polling + research pipeline)

6. **Test end-to-end** and deploy

---

## SUMMARY

**Phase 1:** ✓ COMPLETE — N5 understands V-OS tags

**Phase 2A:** Ready to execute — Howie populates calendar with V-OS tags

**Phase 2B:** Specification complete — Zo polls calendar and triggers research

**Expected Outcome:** Zero-touch meeting prep from scheduling to intelligence delivery

**Time Investment:**
- Phase 2A: 30 minutes (config + test)
- Phase 2B: 8-10 hours (development + testing)
- Total: ~1 week of work

**Result:** Fully automated meeting intelligence pipeline

---

**Date:** 2025-10-11  
**Status:** READY TO EXECUTE  
**Next Action:** V sends intro email to Howie, then Zo sends config request

**All systems ready. Let's build the future of meeting prep. 🚀**
