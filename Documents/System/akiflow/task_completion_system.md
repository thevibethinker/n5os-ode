# Akiflow Task Auto-Completion System
**Status:** Ready to build | **Date:** 2025-10-22

---

## Overview

Automatically complete Akiflow tasks when Zo detects you've done them (sent emails, created files, etc.).

**Flow:**
```
Your Action → Zo Detection → Check Akiflow Tasks (IFTTT) → Match → Complete → Notify
```

---

## Architecture

### Phase 1: IFTTT Setup (You do this - 5 min)

**Applet 1: Query Today's Tasks**
- **Trigger:** Webhook from Zo
- **Query:** Akiflow "List Tasks for a Date" 
- **Action:** Webhook back to Zo with task list

**Setup Steps:**
1. Go to https://ifttt.com/create
2. **If:** Webhooks → Receive a web request
   - Event name: `zo_check_tasks`
3. **Then:** Akiflow → List Tasks for a Date
   - Date: `{{OccurredAt}}`
4. **Then:** Webhooks → Make a web request
   - URL: `https://zo-n8n-api-va.zocomputer.io/akiflow/tasks`
   - Method: POST
   - Content Type: application/json
   - Body: `{"tasks": {{TasksJson}}}`

**Applet 2: Complete Task (Alternative to email)**
- **Trigger:** Webhook from Zo with task ID
- **Action:** Mark task complete in Akiflow (if supported)
- **Fallback:** Email Aki to complete

---

### Phase 2: Detection Engine (Zo builds this - 60 min)

**Service:** `zo-task-completion` running on port 8771

**Monitors:**
1. **Gmail Sent** (via Gmail API polling every 5 min)
2. **Files Created** (via filesystem watcher)
3. **Calendar Events Ended** (via Google Calendar API)

**Detection Rules:**
```python
{
    "email_sent": {
        "match_fields": ["to", "subject", "body_keywords"],
        "task_patterns": ["Send intro", "Email", "Draft", "Reply to"]
    },
    "file_created": {
        "match_fields": ["filename", "path", "content_keywords"],
        "task_patterns": ["Draft", "Create doc", "Write"]
    },
    "calendar_ended": {
        "match_fields": ["title", "attendees"],
        "task_patterns": ["Meeting with", "Call with", "Sync with"]
    }
}
```

---

### Phase 3: Matching Logic (Zo builds this - 30 min)

**Matching Algorithm:**
```python
def match_action_to_task(action, tasks):
    scores = []
    for task in tasks:
        score = 0
        # Exact title match
        if normalize(action.description) == normalize(task.title):
            score += 100
        # Keyword overlap
        action_words = set(tokenize(action.description))
        task_words = set(tokenize(task.title))
        overlap = len(action_words & task_words)
        score += overlap * 10
        # Time proximity (tasks due soon score higher)
        if task.due_today:
            score += 20
        # Context match (email addresses, file paths)
        if action.type == "email" and task.notes:
            if action.to_addr in task.notes:
                score += 30
        scores.append((task, score))
    
    # Return best match if score > threshold
    best_match = max(scores, key=lambda x: x[1])
    if best_match[1] > 50:  # Threshold
        return best_match[0]
    return None
```

**Confidence Levels:**
- **HIGH (80+):** Auto-complete, notify V
- **MEDIUM (50-79):** Ask V for confirmation
- **LOW (<50):** Ignore, log for review

---

### Phase 4: Completion Actions (Zo builds this - 15 min)

**Option A: Email to Aki**
```
To: aki+qztlypb6-d@aki.akiflow.com
Subject: Complete task
Body: Complete: [Task Title]
```

**Option B: IFTTT Webhook (if supported)**
```json
POST https://maker.ifttt.com/trigger/zo_complete_task/with/key/YOUR_KEY
{
  "value1": "task_id_here",
  "value2": "completed_by_zo_auto"
}
```

**Notification to V:**
```
✓ Auto-closed: Send intro Sarah→Marcus
  Reason: Detected email sent to sarah@..., marcus@...
  Confidence: 85%
  [Undo] [Details]
```

---

## Example Scenarios

### Scenario 1: Warm Intro
**Task:** "Send intro: Sarah Chen → Marcus Rodriguez"
**Action:** Email sent to sarah@product.com, marcus@recruiting.com
**Match:** 95% (email addresses + keywords)
**Result:** ✓ Auto-completed

### Scenario 2: Meeting Recap
**Task:** "Draft recap for Leadership Team Sync"
**Action:** Created `Records/Company/Meetings/2025-10-22-Leadership-Team-Sync.md`
**Match:** 88% (filename + keywords)
**Result:** ✓ Auto-completed

### Scenario 3: False Positive Prevention
**Task:** "Review McKinsey proposal"
**Action:** Opened McKinsey-proposal.pdf (just reading, not done)
**Match:** 45% (filename match, but no edit/completion signal)
**Result:** Not completed (below threshold)

---

## Implementation Phases

### Phase A: IFTTT Setup (V does this - 5 min)
- [ ] Create Webhooks → Akiflow → Webhook applet
- [ ] Get IFTTT Webhook key
- [ ] Test with manual trigger

### Phase B: Basic Detection (Zo builds - 60 min)
- [ ] Gmail sent monitor service
- [ ] Task matching engine
- [ ] Completion via email to Aki
- [ ] Notification system

### Phase C: Enhanced Detection (Zo builds - 60 min)
- [ ] File system watcher
- [ ] Calendar event monitor
- [ ] Multi-signal fusion (Gmail + file + calendar)
- [ ] Confidence scoring improvements

### Phase D: Feedback Loop (Zo builds - 30 min)
- [ ] V can confirm/reject auto-completions
- [ ] Learn from corrections
- [ ] Adjust matching rules

---

## Configuration

```json
{
  "enabled": true,
  "confidence_threshold": 50,
  "auto_complete_threshold": 80,
  "check_interval": 300,
  "monitors": {
    "gmail": true,
    "files": true,
    "calendar": true
  },
  "ifttt": {
    "webhook_key": "YOUR_IFTTT_KEY",
    "query_event": "zo_check_tasks",
    "complete_event": "zo_complete_task"
  }
}
```

---

## Next Steps

1. **V:** Set up IFTTT applet (5 min)
2. **V:** Share IFTTT Webhook key with Zo
3. **Zo:** Build detection service (90 min)
4. **Test:** Run through 3-5 scenarios
5. **Refine:** Adjust thresholds based on accuracy

---

## Success Metrics

- **Accuracy:** >90% true positives (correctly completed tasks)
- **Recall:** >70% coverage (detected completed tasks)
- **False positives:** <10% (incorrectly completed tasks)
- **Time saved:** Estimated 5-10 min/day

---

## References
- IFTTT Akiflow: https://ifttt.com/akiflow/queries/task_for_date
- IFTTT Webhooks: https://ifttt.com/maker_webhooks
- Aki email commands: file 'Knowledge/AI/Profiles/akiflow_aki.md'

---

## Change Log
- 2025-10-22: Initial design
