# Akiflow Advanced Features - Design
**Date:** 2025-10-23 21:41 ET

---

## 1. Task Completion Detection System

### Architecture

**Task Tracking Database**
```json
{
  "task_id": "uuid",
  "title": "Send intro: Sarah Chen → Marcus Rodriguez",
  "created_at": "2025-10-23T10:00:00Z",
  "created_in_akiflow": true,
  "status": "open",
  "signals_to_watch": [
    {"type": "email", "pattern": "to:sarah.*marcus|subject:intro.*sarah"},
    {"type": "calendar", "pattern": "Sarah.*Marcus"},
    {"type": "file", "pattern": "Records/Company/Networking/*Sarah*Marcus*"}
  ],
  "completion_confidence": 0,
  "completion_detected_at": null
}
```

### Signal Monitors (Running Services)

**1. Gmail Monitor** (every 5 min)
- Query recent sent emails
- Match against open task patterns
- Score confidence: 0-100

**2. Calendar Monitor** (every 10 min)
- Query recent calendar events
- Match completed meetings against tasks
- Score confidence: 0-100

**3. File Monitor** (every 15 min)
- Watch Records/ for new files
- Match deliverables against tasks
- Score confidence: 0-100

### Confidence Scoring
- **95-100%:** Auto-mark complete, notify V
- **70-94%:** Suggest completion, ask V
- **<70%:** Log but don't notify

### Completion Actions
1. **Update our database:** mark complete
2. **Email Aki:** "Complete: [task title]" (test if this works)
3. **Notify V:** "✓ Auto-completed: Send intro task"
4. **Log:** For review and tuning

---

## 2. Calendar-Aware Scheduling

### Architecture

**When creating/suggesting tasks:**

1. **Query availability** (via Google Calendar API)
   ```python
   # Get next 7 days of calendar
   events = get_calendar_events(start=now, end=now+7days)
   free_slots = find_gaps(events, min_duration=task.duration)
   ```

2. **Smart slot selection**
   - **High priority:** Next available slot
   - **Normal priority:** Prefer morning/afternoon based on type
   - **Low priority:** Fill gaps between meetings

3. **Task type heuristics**
   - "Review/Read" → Morning (focus time)
   - "Call/Meeting" → Afternoon (existing meeting blocks)
   - "Quick/Send" → Between meetings (15min gaps)
   - "Deep work" → 2+ hour blocks

4. **Output format**
   ```
   Suggested: Tomorrow 9:30am (2h free slot before 11:30 meeting)
   Alt: Friday 2pm (afternoon focus block)
   ```

### Integration Points
- **Meeting extraction:** Auto-suggest times when creating tasks
- **aki: command:** "aki: Review proposal" → checks calendar → "Friday 2pm (free 2h block)"
- **Email approval:** Shows suggested time, V can override

---

## 3. Howie Integration

### First: What is Howie?

**Need to clarify with V:**
- What service/tool is Howie?
- What does it do?
- How does V currently use it?
- What's its API/interface?

### Potential Integration Patterns (Based on Common Tools)

**If Howie is a scheduling assistant:**
- Howie books meetings → Creates prep tasks in Akiflow
- Akiflow tasks need meetings → Send to Howie to schedule
- Bidirectional sync

**If Howie is a workflow automation:**
- Howie triggers → Create Akiflow tasks
- Akiflow completion → Trigger Howie workflows
- Use n8n as bridge

**If Howie is an AI assistant:**
- Howie and Zo collaborate via shared context
- Howie creates tasks → Zo manages in Akiflow
- Zo completes tasks → Howie gets notified

**If Howie is a CRM/contact manager:**
- Contact interactions → Follow-up tasks in Akiflow
- Warm intros in Akiflow → Update Howie records
- Relationship management sync

### Design Once We Know
1. **Profile:** Create file 'Knowledge/AI/Profiles/howie.md'
2. **Interface:** Email, API, webhook, or chat?
3. **Workflows:** What should trigger what?
4. **Data sync:** What needs to be bidirectional?

---

## Implementation Plan

### Phase 1: Task Completion Detection (3 hours)

**Step 1: Database (45 min)**
- Create `/home/workspace/N5/data/akiflow_tasks.jsonl`
- CRUD operations
- Migration for existing tasks

**Step 2: Signal Monitors (90 min)**
- Gmail monitor service
- Calendar monitor service  
- File monitor service
- Register all 3 as user services

**Step 3: Matching Engine (45 min)**
- Pattern matching logic
- Confidence scoring
- Completion actions (email Aki, notify V)

---

### Phase 2: Calendar-Aware Scheduling (2 hours)

**Step 1: Calendar Query Module (45 min)**
- Google Calendar API integration
- Find free slots function
- Parse existing events

**Step 2: Smart Scheduler (60 min)**
- Task type detection
- Slot selection heuristics
- Format suggestions

**Step 3: Integration (15 min)**
- Hook into action extractor
- Hook into aki: command
- Update email approval format

---

### Phase 3: Howie Integration (TBD)

**Step 1: Discovery (30 min)**
- V explains Howie
- Research API/interface
- Design integration points

**Step 2: Implementation (2-4 hours)**
- Build connectors
- Create workflows
- Test bidirectional sync

---

## Questions for V

1. **Howie:** What is it? How do you use it? What's the interface?

2. **Priorities:** Which feature first?
   - Completion detection?
   - Calendar scheduling?
   - Howie integration?

3. **Confidence threshold:** What % confidence to auto-complete tasks?
   - Conservative (95%+)?
   - Balanced (80%+)?
   - Aggressive (70%+)?

4. **Time:** Build all 3 tonight (5-7 more hours) or prioritize?

---

## Change Log
- 2025-10-23 21:41: Initial design for advanced features
