# Calendar Intelligence System - Design Proposal
**Status:** Ready to Build  
**Date:** 2025-10-23 21:47 ET  
**Estimated Build Time:** 6-8 hours

---

## Vision

A self-improving calendar management system that:
1. **Reads** your calendar continuously
2. **Enriches** events with context from emails, meetings, files
3. **Learns** patterns about people, meeting types, energy levels
4. **Schedules** intelligently based on actual availability + context
5. **Maintains** event metadata that accumulates over time

---

## Core Capabilities

### 1. Calendar Event Enrichment

**Input:** Basic calendar event
```json
{
  "id": "evt_123",
  "title": "Call with Sarah Chen",
  "start": "2025-10-24T14:00:00",
  "duration": 30,
  "attendees": ["sarah@example.com"]
}
```

**After Enrichment:**
```json
{
  "id": "evt_123",
  "title": "Call with Sarah Chen",
  "start": "2025-10-24T14:00:00",
  "duration": 30,
  "attendees": ["sarah@example.com"],
  
  "enriched": {
    "person_context": {
      "name": "Sarah Chen",
      "company": "Product Company X",
      "role": "Product Lead",
      "relationship": "warm_intro_pending",
      "last_contact": "2025-10-20",
      "interaction_count": 3,
      "topics": ["product_collaboration", "Q1_2026_expansion"]
    },
    
    "meeting_prep": {
      "agenda": ["Discuss product roadmap collaboration", "Q1 hiring plans"],
      "background_docs": [
        "Records/Company/Meetings/2025-10-20_sarah_intro.md",
        "Records/People/sarah_chen_profile.md"
      ],
      "action_items_pending": [
        "Send product deck",
        "Intro to Marcus"
      ],
      "suggested_talking_points": [
        "Follow up on warm intro to Marcus",
        "Q1 2026 expansion timeline"
      ]
    },
    
    "meeting_type": "external_strategic",
    "priority": "high",
    "optimal_energy_level": "high",
    "prep_time_needed": "15m",
    "follow_up_template": "strategic_partner"
  }
}
```

### 2. Data Sources for Enrichment

| Source | What We Extract | Example |
|--------|----------------|---------|
| **Gmail** | Email threads, sent/received count, last contact | "3 emails with Sarah, last: 10/20" |
| **Meeting Transcripts** | Past discussions, commitments, topics | "Discussed product collab Q1 2026" |
| **CRM/People Files** | Relationship status, company info | "Product Lead at Company X" |
| **Past Calendar** | Meeting frequency, typical duration | "Usually 30min, every 2 weeks" |
| **Action Items** | Pending tasks related to person | "Send deck, intro to Marcus" |
| **V's Instructions** | Explicit context V provides | "High priority, strategic partner" |

### 3. Learning Patterns

**Person Patterns:**
```python
{
  "Oscar Marquina": {
    "typical_meeting_length": "30m",
    "usual_day": "Wednesday",
    "prep_complexity": "medium",
    "follow_up_needed": True,
    "meeting_category": "community_strategic",
    "last_3_topics": ["job_board", "partnerships", "events"]
  }
}
```

**Meeting Type Patterns:**
```python
{
  "external_strategic": {
    "optimal_time": "10:00-12:00 or 14:00-15:00",
    "energy_required": "high",
    "prep_time": "15-30m",
    "typical_duration": "30-45m",
    "buffer_after": "15m"  # V needs decompression time
  },
  
  "internal_team": {
    "optimal_time": "13:00-14:00",
    "energy_required": "medium",
    "prep_time": "5m",
    "typical_duration": "60m",
    "buffer_after": "0m"
  }
}
```

### 4. Smart Scheduling Logic

When scheduling a new task/meeting:
```python
def find_optimal_slot(task, calendar_state, learned_patterns):
    # Step 1: Get actual free slots
    free_slots = calendar_state.get_free_slots(
        start=tomorrow,
        end=next_week,
        duration=task['duration']
    )
    
    # Step 2: Score each slot
    for slot in free_slots:
        score = 0
        
        # Time of day preference
        if task['priority'] == 'high' and 9 <= slot.hour <= 12:
            score += 10
        
        # Energy level matching
        if task['energy_required'] == 'high' and slot.hour < 14:
            score += 5
        
        # Buffer time respect
        if has_buffer_before(slot) and has_buffer_after(slot):
            score += 5
        
        # Context switching cost
        prev_meeting = get_previous_meeting(slot)
        if prev_meeting.type == task.type:
            score -= 3  # Penalize similar back-to-back
        
        # Learned patterns
        if task.person in learned_patterns:
            if slot.matches(learned_patterns[task.person].preferred_time):
                score += 8
        
        slot.score = score
    
    # Step 3: Return best slot
    return max(free_slots, key=lambda s: s.score)
```

---

## Architecture

### Components

```
┌─────────────────────────────────────────┐
│   Calendar Intelligence Service         │
│   (calendar_intelligence.py)            │
└─────────────────────────────────────────┘
           ↓
    ┌──────┴──────┐
    │             │
┌───▼────┐   ┌───▼─────┐
│ Reader │   │ Writer  │
│ Module │   │ Module  │
└───┬────┘   └───┬─────┘
    │             │
    │   ┌─────────▼──────┐
    │   │ Enrichment     │
    └──►│ Engine         │
        └─────────┬──────┘
                  │
        ┌─────────▼──────────┐
        │  Knowledge Base    │
        │  (enriched_events/ │
        │   person_patterns/ │
        │   meeting_types/)  │
        └────────────────────┘
```

### Data Storage

**1. Event Enrichment Database**
```
N5/data/calendar_intelligence/
├── enriched_events/
│   ├── 2025-10/
│   │   ├── evt_123_enriched.json
│   │   └── evt_456_enriched.json
│   └── index.jsonl
├── person_patterns/
│   ├── sarah_chen.json
│   ├── oscar_marquina.json
│   └── index.jsonl
└── meeting_type_patterns.json
```

**2. Learning Database**
```
N5/data/calendar_intelligence/learning/
├── scheduling_feedback.jsonl    # Track: suggested vs actual
├── energy_patterns.jsonl        # V's energy by time/day
├── context_switch_costs.jsonl   # Back-to-back meeting impact
└── prep_time_actuals.jsonl      # How long prep really takes
```

### API/Interface

**For Zo (me) to use:**
```python
from calendar_intelligence import CalendarIntelligence

ci = CalendarIntelligence()

# Get enriched event
event = ci.get_enriched_event("evt_123")

# Find optimal slot
slot = ci.find_optimal_slot(
    task={'title': 'Review proposal', 'duration': '45m', 'priority': 'high'},
    constraints={'earliest': 'tomorrow', 'latest': 'friday'}
)

# Enrich event from context
ci.enrich_event_from_sources(
    event_id="evt_123",
    sources=['gmail', 'meetings', 'crm']
)

# Record feedback
ci.record_feedback(
    suggested_time="2025-10-24T10:00",
    actual_time="2025-10-24T14:00",
    reason="Morning got busy with urgent items"
)
```

---

## Enrichment Framework

### Automatic Enrichment Triggers

1. **On Event Creation** (via Google Calendar API webhook)
   - Detect new calendar event
   - Extract attendees
   - Look up person profiles
   - Find email threads
   - Suggest prep materials

2. **Pre-Meeting (24h before)**
   - Compile prep package
   - Update with latest email threads
   - Check for pending action items
   - Generate talking points

3. **Post-Meeting (after transcript processed)**
   - Link transcript to calendar event
   - Extract commitments
   - Update person patterns
   - Queue follow-up tasks

4. **On V's Explicit Command**
   ```
   "Update calendar event for Sarah meeting with our product deck discussion"
   → Enriches event with context, adds note, links file
   ```

### Manual Enrichment Commands

```
# Update specific event
enrich-event <event_id> --context "Strategic partner discussion"

# Bulk update from meeting
enrich-from-meeting <meeting_file> --link-to-calendar

# Learn from V's correction
calendar-feedback "Morning slots work better for strategic calls"
```

---

## Integration with Current Akiflow System

### Phase 1: Read-Only Integration (2-3 hours)
- Calendar Intelligence reads Google Calendar
- Provides availability to smart scheduler
- Returns optimal slots with reasoning

**Update to current scheduler:**
```python
# Before
def schedule_task(task):
    if task['priority'] == 'high':
        return 'Tomorrow 10:00am'  # Generic
    
# After
def schedule_task(task):
    from calendar_intelligence import CalendarIntelligence
    ci = CalendarIntelligence()
    
    slot = ci.find_optimal_slot(task)
    return slot.time  # Actual free time with context
```

### Phase 2: Enrichment Engine (3-4 hours)
- Monitor Gmail for calendar-related emails
- Process meeting transcripts
- Build person/pattern databases
- Auto-update events

### Phase 3: Learning Loop (1-2 hours)
- Track V's scheduling corrections
- Adapt patterns over time
- Improve predictions

---

## Build Plan

### Session 1: Core Infrastructure (3 hours)
1. Calendar reader (Google Calendar API)
2. Event storage schema
3. Basic enrichment from Gmail
4. API interface for scheduler

### Session 2: Enrichment Engine (3 hours)
1. Person pattern learning
2. Meeting type classification
3. Email → calendar linking
4. Prep package generation

### Session 3: Integration & Learning (2 hours)
1. Hook into Akiflow scheduler
2. Feedback collection
3. Pattern adaptation
4. Testing & refinement

**Total: 8 hours across 2-3 sessions**

---

## Example Scenarios

### Scenario 1: New Meeting Scheduled

**V:** "aki: Call with Oscar next week about job board"

**System:**
1. Searches calendar for free slots next week
2. Finds Oscar pattern: usually Wednesday 2pm
3. Checks Wednesday 2pm → free ✓
4. Looks up Oscar context:
   - Last meeting: 10/23 (McKinsey Orbit)
   - Topic: job board partnership
   - Pending: Follow-up conversation
5. Creates enriched event:
   - Time: Wed 2pm (his preference)
   - Prep: Review B25 from Orbit meeting
   - Agenda: Job board infrastructure discussion
   - Duration: 30m (his typical)
6. Adds to Akiflow + Google Calendar

### Scenario 2: Pre-Meeting Prep

**System (24h before Oscar call):**
```
Email to V:
"Tomorrow 2pm: Call with Oscar Marquina

Context:
• Last contact: 10/23 McKinsey Orbit call
• Discussed: job board for Orbit alumni
• You offered: Careerspan infrastructure
• Pending: His response about timing

Prep materials:
• Meeting notes: Records/Company/Meetings/2025-10-23_orbit.md
• Email thread: 3 messages (see Gmail)

Talking points:
• Infrastructure capabilities
• Pricing/partnership model
• Integration timeline

Action items to mention:
• None pending from you
• Awaiting his decision on next steps
```

### Scenario 3: Learning from Feedback

**V:** "Move tomorrow's strategic call to morning - I have more energy then"

**System learns:**
1. Updates V's energy patterns:
   ```
   strategic_calls: {
     energy_required: high,
     optimal_time: 9:00-12:00  # ← Updated
   }
   ```
2. Adjusts future scheduling for strategic calls
3. Checks next week's calendar
4. Suggests moving similar afternoon calls to morning

---

## Success Metrics

1. **Scheduling Accuracy**
   - Target: 90%+ of suggested times accepted without change
   - Track: Suggestions vs actual scheduled time

2. **Prep Completeness**
   - Target: V says "well prepared" 80%+ of meetings
   - Track: Feedback after meetings

3. **Time Saved**
   - Target: 30min/week saved on calendar management
   - Track: Before/after time spent scheduling

4. **Context Accuracy**
   - Target: 95%+ enrichment data is correct
   - Track: Corrections V makes to enriched info

---

## Technical Decisions

### Google Calendar API
- Use webhooks for real-time updates
- Poll every 15min as backup
- Cache locally for fast access

### Storage Format
- JSON for enriched events (human-readable)
- JSONL for patterns (append-only learning)
- SQLite for queries (optional, later)

### Privacy & Security
- All data stays on V's Zo instance
- No external APIs except Google Calendar
- Encrypted storage (optional)

---

## Next Steps

1. **Approve this proposal** → V confirms approach
2. **Session 1: Build core** → 3h session to build foundation
3. **Integrate with Akiflow** → Wire into current system
4. **Iterate & learn** → Improve based on usage

---

## Questions for V

1. Do you want this built in the NEXT session or schedule for later?
2. Any specific patterns you want it to learn first?
3. Should it have veto power or always ask before moving events?
4. Want integration with CRM/people tracking, or just calendar+email?

---

**This system would transform calendar management from reactive to proactive.**

Let's build it!
