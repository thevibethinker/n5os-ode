# Build Orchestrator: Team Status Career Progression System
**Project:** N5 Productivity Tracking - Career Management Layer  
**Orchestrator Thread:** con_MuvXIR7jXZjZxlND  
**Started:** 2025-10-30 01:33 ET  
**Status:** PLANNING → EXECUTION

---

## Mission

Transform the N5 productivity tracker from a stats dashboard into a **career simulator** with dynamic team status, automated coaching alerts, and elite tier progression.

**Core Mechanic:** 365 "game days" per year. Performance over rolling 7-day windows determines your squad status in the Arsenal team hierarchy.

---

## System Architecture

### Components (Workers)

```
┌─────────────────────────────────────────────────────────┐
│                   BUILD ORCHESTRATOR                     │
│                  (This Thread/Document)                  │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼────┐         ┌────▼────┐        ┌────▼────┐
   │ SCHEMA  │         │  CALC   │        │  EMAIL  │
   │ WORKER  │────────▶│ WORKER  │───────▶│ WORKER  │
   └─────────┘         └─────────┘        └─────────┘
        │                   │                   │
        │                   └───────┬───────────┘
        │                           │
   ┌────▼────┐                 ┌────▼────┐
   │   UI    │◀────────────────│   QA    │
   │ WORKER  │                 │ WORKER  │
   └─────────┘                 └─────────┘
```

---

## Worker Assignments

### **W1: Schema Worker** (BLOCKING - Must complete first)
**Handoff Doc:** `SCHEMA_WORKER_HANDOFF.md`  
**Task:** Design and implement database schema for team status tracking  
**Blocks:** W2, W3, W4, W5  
**Status:** 🔴 NOT STARTED

**Deliverables:**
- Migration SQL script
- Updated schema documentation
- Test data insertion script

---

### **W2: Calculator Worker** (Depends on W1)
**Handoff Doc:** `CALCULATOR_WORKER_HANDOFF.md`  
**Task:** Build team_status_calculator.py with top-5-of-7 logic  
**Blocks:** W3, W5  
**Status:** 🔴 NOT STARTED

**Deliverables:**
- `team_status_calculator.py` (standalone, testable)
- Unit tests with edge cases
- CLI interface for manual testing

---

### **W3: Integration Worker** (Depends on W1, W2)
**Handoff Doc:** `INTEGRATION_WORKER_HANDOFF.md`  
**Task:** Wire team status into rpi_calculator.py daily run  
**Blocks:** W4, W5  
**Status:** 🔴 NOT STARTED

**Deliverables:**
- Modified `rpi_calculator.py`
- Status history logging
- Dry-run mode tested

---

### **W4: Email Worker** (Depends on W1, W3)
**Handoff Doc:** `EMAIL_WORKER_HANDOFF.md`  
**Task:** Build coaching email system with Arsenal manager voice  
**Blocks:** W5  
**Status:** 🔴 NOT STARTED

**Deliverables:**
- `coaching_emailer.py`
- Email templates (5 types)
- Rate limiting logic
- Gmail integration tested

---

### **W5: UI Worker** (Depends on W1, W2)
**Handoff Doc:** `UI_WORKER_HANDOFF.md`  
**Task:** Update dashboard to display team status, career stats  
**Blocks:** W6  
**Status:** 🔴 NOT STARTED

**Deliverables:**
- Modified `Sites/productivity-dashboard/index.tsx`
- Mobile-responsive status banner
- Career stats section
- API endpoint for status history

---

### **W6: QA Worker** (Depends on W1-W5)
**Handoff Doc:** `QA_WORKER_HANDOFF.md`  
**Task:** Integration testing, validation, production readiness  
**Blocks:** NONE (Final step)  
**Status:** 🔴 NOT STARTED

**Deliverables:**
- End-to-end test results
- Edge case validation
- Performance check
- Deployment approval

---

## Execution Strategy

### Phase 1: Foundation (Sequential)
1. **W1 (Schema)** - Must complete first
2. **W2 (Calculator)** - Can start immediately after W1
3. V reviews foundation before proceeding

### Phase 2: Integration (Parallel)
4. **W3 (Integration)** + **W4 (Email)** - Can run in parallel
5. V reviews integration logic and email tone

### Phase 3: Frontend + QA (Sequential)
6. **W5 (UI)** - After integration confirmed working
7. **W6 (QA)** - Final validation before go-live

---

## Design Principles (Applied)

**P0 (Simple Over Easy):** Each worker builds ONE thing well  
**P1 (Code Is Free):** Isolated components, easy to replace  
**P3 (Flow Over Pools):** Status flows from daily RPI → career stats  
**P7 (Dry-Run First):** Every worker must support --dry-run mode  
**P15 (Complete Before Claiming):** Workers return with tests passing

---

## Key Requirements

### Team Status Rules (Top 5 of 7)
- Take best 5 days out of last 7 days
- Average must be ≥90% to maintain/promote
- If <90%: apply demotion with probation buffer
- Asymmetric movement: Easier to climb than fall

### Status Hierarchy
1. 🚫 Transfer List (bottom)
2. 🟠 Reserves
3. 🟡 Squad Member (probation period)
4. 🟢 First Team Starter
5. 🌟 Invincible (unlock: 6/8 weeks >125%)
6. 🏆 Legend (unlock: sustained Invincible)

### Email Triggers
- **Demotion:** Immediate alert
- **Promotion:** Immediate congrats
- **Warning:** 3 days <90% in rolling window
- **Grace Period:** 2nd grace day used
- **Achievement:** Elite tier unlocked

### Email Voice (Arsenal Manager)
- Firm but motivational
- Specific metrics referenced
- Clear expectations
- Believes in V's potential
- Signs as "The Gaffer"

---

## Current System State

### Database
**File:** `/home/workspace/productivity_tracker.db`

**Existing Tables:**
- `daily_stats` - RPI, emails, XP, level, streak
- `sent_emails` - Individual email records
- `expected_load` - Calendar meetings, workload
- `xp_ledger` - XP transaction history

**Current Columns (daily_stats):**
```sql
date, rpi_score, email_count, total_words, created_at,
emails_sent, emails_new, emails_followup, emails_response,
expected_emails, rpi, xp_earned, xp_multiplier, level, streak_days
```

### Scripts
**Main Calculator:** `file 'N5/scripts/productivity/rpi_calculator.py'`
- Runs daily via scheduled task
- Calculates RPI, XP, level, streak
- Updates `daily_stats` table

**Email Scanner:** `file 'N5/scripts/productivity/email_scanner.py'`
- Scans Gmail via API
- Populates `sent_emails` table

**Meeting Scanner:** `file 'N5/scripts/productivity/meeting_scanner.py'`
- Scans Google Calendar
- Populates `expected_load` table

### Dashboard
**File:** `file 'Sites/productivity-dashboard/index.tsx'`
- Hono + Bun server
- Arsenal FC themed (red/white)
- Currently shows: RPI, emails, XP, level, streak
- Public URL: https://productivity-dashboard-va.zocomputer.io

---

## Success Criteria (Overall)

- [ ] Team status updates daily based on performance
- [ ] Status visible on dashboard with career stats
- [ ] Coaching emails sent at appropriate triggers
- [ ] Elite tiers unlock with sustained excellence
- [ ] Manual status override available for corrections
- [ ] All components tested with historical data
- [ ] V approves email tone and timing
- [ ] System runs in production without errors

---

## Orchestrator Actions

### Before Worker Spawn
- [x] Create BUILD_ORCHESTRATOR.md
- [ ] Create all 6 worker handoff documents
- [ ] Load current system state into handoffs
- [ ] Define clear success criteria per worker
- [ ] Map dependencies explicitly

### During Execution
- [ ] Spawn W1 (Schema Worker) first
- [ ] Review W1 deliverables before proceeding
- [ ] Spawn W2-W4 as dependencies clear
- [ ] Integrate worker outputs
- [ ] Validate cross-worker compatibility
- [ ] Update this doc with progress

### After Completion
- [ ] W6 (QA) sign-off received
- [ ] V approval for production deploy
- [ ] Service restarted with new code
- [ ] Documentation updated
- [ ] Demo video ready

---

## Risk Management

### Trap Doors Identified
1. **Grace day calculation complexity** - Could get confusing fast
   - Mitigation: W2 writes extensive unit tests
2. **Email spam** - Could annoy V with too many alerts
   - Mitigation: Rate limiting + dry-run approval first
3. **Status flapping** - Bouncing between tiers daily
   - Mitigation: Probation periods + asymmetric rules
4. **Database corruption** - Historical data could break
   - Mitigation: Migrations tested with backups

---

## Communication Protocol

### V → Orchestrator
- Review worker outputs: "Approved" or "Changes needed: [specifics]"
- Priority adjustments: "Pause W4, prioritize W5 instead"
- Scope changes: Update this doc + affected handoffs

### Orchestrator → Workers
- Via handoff docs (complete, immutable context)
- Workers don't see each other's work
- All coordination happens here

### Workers → Orchestrator
- Return artifacts to this thread
- Format: "W[N] Complete - [Summary] - [Files changed]"
- Include test results + any blockers discovered

---

## Notes

- **Database extensibility:** NOT over-engineering for LinkedIn now. Clean schema allows easy extension later.
- **Email dry-run:** MUST test with V before enabling auto-send
- **Mobile-first:** Dashboard must work on phone (V checks daily)
- **Arsenal branding:** Maintain red/white theme, football terminology

---

**Next Action:** Create 6 worker handoff documents, then spawn W1 (Schema Worker).

**Orchestrator:** Vibe Operator (Vrijen's Zo)  
**Last Updated:** 2025-10-30 01:33 ET
