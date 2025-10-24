# Akiflow Aki Multi-Task Email Test

**Sent:** 2025-10-22 20:57 ET  
**From:** va@zo.computer (Zo - V's AI)  
**To:** aki+qztlypb6-d@aki.akiflow.com  
**Message ID:** 19a0e952342724be

## Email Content
**Subject:** [N5] Batch tasks test | Tomorrow

**Body:**
```
Task: Draft recap for Leadership Team Sync
When: Tomorrow 9:30am ET
Duration: 20m
Priority: Normal
Project: Careerspan
Tags: meeting, recap
Notes: Action items from 2025-10-22 LT sync - file 'Records/Company/Meetings/2025-10-22-Leadership-Team-Sync.md'

---

Task: Send warm intro Sarah Chen → Marcus Rodriguez
When: Tomorrow 10:00am ET
Duration: 15m
Priority: High
Project: Networking
Tags: warm_intro
Notes: Connect Sarah (Product) with Marcus (Recruiting leader). Context: both expanding teams Q1 2026.

---

Task: Review candidate pipeline for SWE role
When: Tomorrow 11:00am ET
Duration: 30m
Priority: Normal
Project: Careerspan
Tags: recruiting
Notes: Screen top 5 candidates, prepare interview schedule for next week.
```

## Expected Results
- **Tasks created:** 3
- **Task 1:** "Draft recap for Leadership Team Sync"
  - Scheduled: 2025-10-23 09:30 ET
  - Duration: 20m
  - Priority: Normal
  - Project: Careerspan
  - Tags: meeting, recap
  
- **Task 2:** "Send warm intro Sarah Chen → Marcus Rodriguez"
  - Scheduled: 2025-10-23 10:00 ET
  - Duration: 15m
  - Priority: High
  - Project: Networking
  - Tags: warm_intro
  
- **Task 3:** "Review candidate pipeline for SWE role"
  - Scheduled: 2025-10-23 11:00 ET
  - Duration: 30m
  - Priority: Normal
  - Project: Careerspan
  - Tags: recruiting

## Actual Results
*Pending V's verification in Akiflow*

### Success Criteria
- [ ] 3 distinct tasks created (not merged into 1)
- [ ] Each task has correct title
- [ ] Scheduling accurate (date + time)
- [ ] Duration captured
- [ ] Priority set correctly
- [ ] Projects assigned correctly
- [ ] Tags assigned correctly
- [ ] Notes preserved

### Observations
*To be filled after verification*

## Next Steps
Based on results:
- **Success (3/3 tasks):** Package `akiflow-push` command, wire playbooks
- **Partial (1-2 tasks):** Adjust format, iterate
- **Failure (0 tasks):** Switch to one-task-per-email pattern
