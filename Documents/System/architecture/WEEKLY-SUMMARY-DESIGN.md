# Weekly Summary System — Design Specification

**Date:** 2025-10-12\
**Status:** Design Phase\
**Aligned with:** Architectural Principles v2.0

---

## Phase 1: Requirements & Context

### Problem Statement

Automate weekly calendar and email summary generation to provide advance visibility into the upcoming week, building compounding understanding of relationships over time.

### Success Criteria

- [x]  Digest generated every Sunday at 8pm ET

- [x]  Includes external calendar events for next 7 days (Monday-Sunday)

- [x]  Respects N5OS tags (formerly V-OS)

- [x]  Includes relevant emails from meeting participants + CRM contacts

- [x]  Builds dossiers on individuals over time

- [x]  Delivered via email

- [x]  Structured sections following existing digest format

- [x]  Reuses existing meeting monitor infrastructure

- [x]  State management and logging included

---

## Requirements Summary

### Calendar Scope

- **External meetings only** (exclude @mycareerspan.com, @theapply.ai)
- **Respect N5OS tags** (same logic as meeting monitor)
- **Date range:** Next 7 days starting Monday
- **Source:** Google Calendar API

### Email Scope

- **Relevant emails defined as:**
  1. Emails from/to people you have meetings with this week
  2. Emails from/to existing CRM contacts (e.g., Hamoon)
- **Time window:** Last 2 months
- **Purpose:** Build compounding understanding (dossiers)
- **Source:** Gmail API

### Output Format

- **Structure:** Sections (like meeting prep digest)
- **Style:** Simple list within each section
- **No prioritization** (you'll skim anyway)
- **Format:** Markdown delivered via email

### System Integration

- **Reuse:** Meeting monitor code, profile manager, API integrator
- **Minimize:** Points of change
- **Leverage:** Existing N5OS tag logic, external event filtering

### State & Logging

- **State management:** Track digest generation history
- **Logging:** Record all operations
- **Error recovery:** Basic (less critical than real-time monitoring)

---

## Phase 2: Architectural Review

### Principles Compliance Check

✅ **Principle 2: Single Source of Truth**

- Meeting profiles are SSOT for individuals
- Weekly digest references existing profiles

✅ **Principle 5: Anti-Overwrite**

- Digests dated and versioned
- No overwriting previous weeks

✅ **Principle 7: Dry-Run Mode**

- `--dry-run` flag for testing
- Preview before scheduling

✅ **Principle 11 & 19: Error Handling**

- Try-catch around API calls
- Log errors, continue if possible
- Email error summary if generation fails

✅ **Principle 17: Production Config**

- Test with actual APIs before scheduling
- Use same code path for manual and scheduled

✅ **Principle 18: State Verification**

- Verify email sent successfully
- Verify digest file created
- Log file updated

✅ **Principle 20: Modular Design**

- Separate: calendar gathering, email gathering, digest generation, delivery
- Can run each phase independently

---

## Phase 3: Design Specification

### System Architecture

```markdown
┌─────────────────────────────────────────┐
│     Weekly Summary System               │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │ 1. Calendar Event Gathering      │  │
│  │    - Get next 7 days (Mon-Sun)   │  │
│  │    - Filter external only        │  │
│  │    - Extract N5OS tags           │  │
│  └──────────────────────────────────┘  │
│              ↓                          │
│  ┌──────────────────────────────────┐  │
│  │ 2. Participant Extraction        │  │
│  │    - Get all attendees           │  │
│  │    - Identify stakeholders       │  │
│  └──────────────────────────────────┘  │
│              ↓                          │
│  ┌──────────────────────────────────┐  │
│  │ 3. Email Gathering               │  │
│  │    - Query Gmail for each person │  │
│  │    - Last 1 month window         │  │
│  │    - Also query CRM contacts     │  │
│  └──────────────────────────────────┘  │
│              ↓                          │
│  ┌──────────────────────────────────┐  │
│  │ 4. Dossier Update                │  │
│  │    - Update existing profiles    │  │
│  │    - Create new if needed        │  │
│  │    - Track email interactions    │  │
│  └──────────────────────────────────┘  │
│              ↓                          │
│  ┌──────────────────────────────────┐  │
│  │ 5. Digest Generation             │  │
│  │    - Calendar section            │  │
│  │    - Email highlights section    │  │
│  │    - Key relationships section   │  │
│  └──────────────────────────────────┘  │
│              ↓                          │
│  ┌──────────────────────────────────┐  │
│  │ 6. Delivery                      │  │
│  │    - Email to V                  │  │
│  │    - Save to N5/digests/         │  │
│  │    - Update state file           │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

### File Structure

```markdown
N5/
├── scripts/
│   ├── weekly_summary.py           # New: Main orchestrator
│   ├── meeting_api_integrator.py   # Reuse: Calendar & Gmail APIs
│   ├── stakeholder_profile_manager.py  # Reuse: Profile updates
│   └── email_analyzer.py           # New: Email analysis logic
│
├── digests/
│   └── weekly-summary-YYYY-MM-DD.md  # Output files
│
├── records/
│   ├── meetings/                   # Existing profiles (reuse)
│   └── weekly_summaries/
│       └── .state.json             # Track generation history
│
└── logs/
    └── weekly_summary.log          # Operation logs
```

### Data Flow

**1. Calendar Events (Next Monday-Sunday)**

```python
{
    "event_id": "cal_xyz",
    "title": "Meeting with Logan",
    "date": "2025-10-14",
    "attendees": ["logan@example.com"],
    "n5os_tags": ["LD-HIR", "!!"],
    "is_external": true
}
```

**2. Email Threads (Last 30 days)**

```python
{
    "thread_id": "thread_abc",
    "participants": ["logan@example.com"],
    "subject": "Q4 Hiring Plans",
    "date": "2025-09-28",
    "snippet": "Let's discuss...",
    "unread": false
}
```

**3. Dossier Update**

```python
{
    "person": "logan@example.com",
    "profile_path": "N5/records/meetings/logan-example/profile.md",
    "recent_emails": 3,
    "last_contact": "2025-10-10",
    "upcoming_meetings": 1,
    "relationship_summary": "Co-founder, hiring discussions ongoing"
}
```

**4. Digest Output**

```markdown
# Weekly Summary — Oct 14-20, 2025

## Calendar Overview (7 External Meetings)

### Monday, Oct 14
- **10:00am** - Logan Chen | Hiring Review | [LD-HIR] [!!]
- **2:00pm** - Michael Maher | Investment Discussion | [LD-INV]

### Tuesday, Oct 15
...

## Email Activity (Last 30 Days)

### High Activity Contacts
- **Logan Chen** (3 emails) - Hiring plans, role definitions
- **Hamoon Ekhtiari** (2 emails) - FutureFit integration update

### Key Threads
1. Q4 Hiring Plans (with Logan) - 5 messages
2. Investment Terms (with Michael) - 3 messages

## Relationship Dossiers Updated

✓ Logan Chen - Updated with recent hiring discussions
✓ Michael Maher - Added investment context
✓ Hamoon Ekhtiari - CRM contact, integration status tracked
```

---

## Code Reuse Strategy

### From Existing Meeting Monitor:

**1. Calendar API Integration** (`file meeting_api_integrator.py` )

- `get_upcoming_meetings()` - Already filters external
- `extract_n5os_tags()` - Already extracts tags
- `is_external_event()` - Already checks domains

**2. Gmail API Integration** (`file meeting_api_integrator.py` )

- Extend `search_gmail_for_stakeholder()`
- Add `get_emails_in_timeframe()` method

**3. Profile Management** (`file stakeholder_profile_manager.py` )

- `load_or_create_profile()` - Reuse for dossiers
- `update_profile_from_email()` - New method to add

**4. N5OS Tag Logic** (`file meeting_prep_digest.py` )

- `extract_n5os_tags()` - Already working
- `is_tag_active()` - Already checks asterisk

### New Components Needed:

**1. Email Analyzer** (`file email_analyzer.py` )

```python
def get_recent_emails_for_person(gmail_tool, email, days=30):
    """Get email threads involving this person in last N days"""
    
def analyze_email_activity(emails):
    """Summarize: volume, topics, recency"""
    
def identify_key_threads(emails, top_n=5):
    """Surface most important conversations"""
```

**2. Weekly Summary Orchestrator** (`file weekly_summary.py` )

```python
def gather_calendar_events(lookahead_days=7):
    """Get next week's external events with N5OS tags"""
    
def gather_email_activity(participants, lookback_days=30):
    """Get email threads for meeting participants + CRM"""
    
def update_dossiers(people_data):
    """Update or create profiles with new information"""
    
def generate_digest(calendar, emails, dossiers):
    """Create markdown digest"""
    
def deliver_digest(digest_content):
    """Email to V and save to N5/digests/"""
```

---

## Error Handling

### Graceful Degradation

```python
try:
    calendar_events = gather_calendar_events()
except CalendarAPIError as e:
    log.error(f"Calendar API failed: {e}")
    calendar_events = []
    # Continue with email analysis

try:
    email_data = gather_email_activity(participants)
except GmailAPIError as e:
    log.error(f"Gmail API failed: {e}")
    email_data = []
    # Continue with partial data

# Always generate digest with whatever data we have
if not calendar_events and not email_data:
    # Send error notification email
    send_email_to_user(
        subject="Weekly Summary Generation Failed",
        body="Both Calendar and Gmail APIs failed. Check logs."
    )
    sys.exit(1)
else:
    # Generate with available data
    generate_digest(calendar_events, email_data)
```

---

## State Management

**File:** `file N5/records/weekly_summaries/.state.json` 

```json
{
    "last_generated": "2025-10-06T20:00:00Z",
    "generation_history": [
        {
            "date": "2025-10-06",
            "week_start": "2025-10-07",
            "week_end": "2025-10-13",
            "events_included": 5,
            "emails_analyzed": 23,
            "profiles_updated": 8,
            "status": "success",
            "digest_path": "N5/digests/weekly-summary-2025-10-06.md"
        }
    ],
    "next_scheduled": "2025-10-13T20:00:00Z"
}
```

---

## Testing Strategy

### Phase 4: Implementation Testing

**Test 1: Dry-Run (Manual)**

```bash
python3 N5/scripts/weekly_summary.py --dry-run

Expected output:
- Calendar events listed (no writes)
- Email queries shown (no API calls)
- Digest preview generated
- No state file updated
- No email sent
```

**Test 2: Real Run (One-time)**

```bash
python3 N5/scripts/weekly_summary.py --week-of 2025-10-14

Expected output:
- Real API calls
- Digest generated
- Email sent to V
- State file updated
- Logs written
```

**Test 3: Scheduled Task (Production)**

```bash
# Create Zo scheduled task
Schedule: Weekly on Sunday at 8pm ET
Model: openai:gpt-5-mini-2025-08-07
Command: python3 N5/scripts/weekly_summary.py --auto
```

---

## CLI Design

```bash
python3 N5/scripts/weekly_summary.py [OPTIONS]

Options:
  --dry-run           Preview without API calls or writes
  --auto              Auto-detect next week (default for scheduled task)
  --week-of DATE      Generate for specific week (YYYY-MM-DD)
  --lookback-days N   Email analysis window (default: 30)
  --no-email          Skip email delivery (save to file only)
  --verbose           Detailed logging output
```

---

## Digest Template

```markdown
# Weekly Summary — [Week of Oct 14-20, 2025]

**Generated:** [Timestamp]  
**External Events:** [Count]  
**Email Threads Analyzed:** [Count]  
**Profiles Updated:** [Count]

---

## 📅 Calendar Overview

### Monday, October 14
- **10:00 AM** - Logan Chen | Hiring Review | `[LD-HIR] [!!]`
  - **Context:** Co-founder, ongoing hiring discussions
  - **Recent emails:** 3 threads (last: Oct 10)

- **2:00 PM** - Michael Maher | Investment Discussion | `[LD-INV]`
  - **Context:** Potential investor, first substantive meeting
  - **Recent emails:** 2 threads (last: Oct 12)

### Tuesday, October 15
...

---

## 📧 Email Activity (Last 30 Days)

### High Activity Contacts
1. **Logan Chen** (3 emails, 5 messages)
   - Topics: Q4 hiring, role definitions, candidate pipeline
   - Last contact: Oct 10

2. **Hamoon Ekhtiari** (2 emails, 7 messages)
   - Topics: FutureFit integration, technical questions
   - Last contact: Oct 8 (CRM contact)

### Key Email Threads
- **"Q4 Hiring Strategy"** with Logan (5 messages)
  - Status: Active discussion
  - Next: Finalize job descriptions

- **"Investment Terms Discussion"** with Michael (3 messages)
  - Status: Awaiting V's response
  - Next: Review term sheet

---

## 👥 Relationship Dossiers Updated

✓ **Logan Chen** - Added recent hiring context  
✓ **Michael Maher** - Created new profile with investment focus  
✓ **Hamoon Ekhtiari** - Updated integration status (CRM contact)  
✓ **Ilse van der Linde** - Added technical discussion notes  

**Profiles refreshed:** 4  
**New profiles created:** 1

---

## 📊 Week Ahead Summary

**External meetings:** 7  
**N5OS tag breakdown:**
- `[LD-HIR]` (Hiring): 2 meetings
- `[LD-INV]` (Investment): 2 meetings  
- `[!!]` (Urgent): 1 meeting

**Busiest day:** Tuesday (3 meetings)  
**Preparation needed:** Review hiring pipeline, investment terms

---

*Generated by N5 Weekly Summary System v1.0*
```

---

## Implementation Plan

### Step 1: Email Analyzer (New Component)

- Create `file N5/scripts/email_analyzer.py` 
- Implement Gmail query functions
- Add email summarization logic

### Step 2: Weekly Summary Script (Main Orchestrator)

- Create `file N5/scripts/weekly_summary.py` 
- Integrate with existing APIs
- Implement digest generation

### Step 3: Extend Profile Manager

- Add `update_profile_from_email()` method
- Track email interaction history
- Build dossier sections

### Step 4: Testing

- Dry-run test
- Manual one-time test
- Validate output quality

### Step 5: Scheduled Task

- Create Zo scheduled task
- Sunday 8pm ET recurring
- Monitor first few runs

---

## Success Criteria (Phase 5: Validation)

### Must Pass

- [ ]  Calendar events for next 7 days retrieved

- [ ]  External-only filtering works

- [ ]  N5OS tags extracted correctly

- [ ]  Email threads gathered for participants

- [ ]  CRM contacts included (Hamoon, etc.)

- [ ]  Digest generated in structured format

- [ ]  Email delivered to V

- [ ]  Digest saved to N5/digests/

- [ ]  State file updated

- [ ]  Logs written

### Ideal

- [ ]  Dossiers meaningfully updated

- [ ]  Email summaries helpful

- [ ]  No redundancy with meeting prep digest

- [ ]  Takes &lt;60 seconds to generate

- [ ]  Error handling tested and working

---

## Next Steps

**V, please confirm:**

1. ✅ Design looks good?
2. ✅ 30-day email window acceptable? (can expand to 60 later)
3. ✅ Digest template structure works?
4. ✅ Ready to proceed with implementation?

Once approved, I'll:

1. Create `file email_analyzer.py` 
2. Create `file weekly_summary.py` 
3. Extend profile manager
4. Test with dry-run
5. Validate with real run
6. Create scheduled task

---

**Status:** Awaiting approval to proceed with implementation