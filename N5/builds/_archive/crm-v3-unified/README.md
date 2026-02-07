# CRM V3 Unified System - Orchestration Project

**Status:** ✅ Ready to Launch  
**Orchestrator:** con_RxzhtBdWYFsbQueb  
**Date:** 2025-11-17  
**Estimated Duration:** 4-5 hours worker time, 4 days calendar time

---

## Quick Start

### Launch Worker 1 (Database Schema)

**Option A: Automated Script**
```bash
bash /home/workspace/N5/builds/crm-v3-unified/launch_worker_1.sh
```

**Option B: Manual Launch**
1. Open new conversation
2. Paste: `Load file 'N5/builds/crm-v3-unified/WORKER_1_DATABASE_SCHEMA.md' and execute this task.`
3. Record conversation ID in `ORCHESTRATOR_MONITOR.md`

---

## Project Overview

### Problem
3 parallel CRM systems with overlapping functionality:
1. `Knowledge/crm/` (57 profiles, SQLite-backed)
2. `N5/stakeholders/` (10 profiles, YAML frontmatter)
3. `N5/data/profiles.db` (44 records, meeting-centric)

### Solution
Single unified system:
- **SQLite database** = Queryable index
- **YAML profiles** = Source of truth
- **Append-only intelligence** = LLM-friendly logs
- **Calendar webhooks** = Proactive enrichment
- **Async queue** = Priority-based processing

---

## Worker Breakdown

| Worker | Task | Duration | Depends On | Status |
|--------|------|----------|------------|--------|
| W1 | Database Schema | 30 min | None | 🔵 Ready |
| W2 | Migration Scripts | 45 min | W1 | ⚪ Blocked |
| W3 | Enrichment Worker | 60 min | W1 | ⚪ Blocked |
| W4 | Calendar Webhook | 45 min | W1, W3 | ⚪ Blocked |
| W5 | Email Tracker | 30 min | W1 | ⚪ Blocked |
| W6 | CLI Interface | 30 min | W1 | ⚪ Blocked |
| W7 | Integration Tests | 45 min | W1-W6 | ⚪ Blocked |

**Total:** 4h 45m execution time

---

## File Structure

```
N5/builds/crm-v3-unified/
├── README.md (this file)
├── ORCHESTRATOR_PLAN.md (full project plan)
├── ORCHESTRATOR_MONITOR.md (status tracking)
├── ORCHESTRATOR_DEPLOYMENT_GUIDE.md (step-by-step)
├── WORKER_1_DATABASE_SCHEMA.md (ready to launch)
├── WORKER_2_MIGRATION_SCRIPTS.md (todo)
├── WORKER_3_ENRICHMENT_WORKER.md (todo)
├── WORKER_4_CALENDAR_WEBHOOK.md (todo)
├── WORKER_5_EMAIL_TRACKER.md (todo)
├── WORKER_6_CLI_INTERFACE.md (todo)
├── WORKER_7_INTEGRATION_TESTING.md (todo)
├── crm-v3-design.md (full architecture)
└── launch_worker_1.sh (automated launcher)
```

---

## Key Features

### Calendar-First Enrichment
- Google Calendar webhook triggers enrichment
- 3-day advance checkpoint (full enrichment)
- Morning-of checkpoint (delta + meeting brief)

### Multi-Source Intelligence
- B08 stakeholder blocks from meetings
- Aviato API enrichment
- Gmail thread context
- LinkedIn profile data
- Voice memo ingestion
- Manual notes

### Quality States
- **Stub:** Name + email only
- **Basic:** + role + company
- **Enriched:** + Aviato data + meeting context
- **Comprehensive:** + multi-source synthesis

### Entity Deduplication
- Email exact match (primary key)
- Name fuzzy matching (Levenshtein)
- Manual review queue for ambiguous

### Spam Filtering
- Pattern matching ("fuck off", "unsubscribe")
- Hostile tone detection
- Domain blocklist

---

## Architecture Principles

✅ **P2:** Single Source of Truth (YAML profiles)  
✅ **P0.1:** LLM-First (AI-queryable intelligence)  
✅ **P8:** Minimal Context (Database stores pointers)  
✅ **P12:** Fresh Conversation Test (Documentation complete)  
✅ **P15:** Honest Completion (Test-first approach)  
✅ **P28:** Think Before Build (This orchestration!)  
✅ **P33:** Test-First (Every worker includes tests)

---

## Monitoring & Validation

### After Each Worker

Update `ORCHESTRATOR_MONITOR.md` with:
- Conversation ID
- Test results ✓
- Blockers resolved
- Next worker unblocked

### Validation Commands

See `ORCHESTRATOR_DEPLOYMENT_GUIDE.md` for worker-specific commands.

---

## Rollback Safety

### Non-Destructive Approach

1. **New database:** `crm_v3.db` (legacy untouched)
2. **Migration dry-run:** Validate before execution
3. **Legacy systems:** Remain intact until cutover approved
4. **Backup restore:** Automated daily backups in `N5/backups/`

### If Critical Issue

```bash
# Stop services
rm /home/workspace/N5/data/crm_v3.db

# Legacy systems still functional
# No data lost
```

---

## Success Criteria

Project complete when:

- [ ] All 7 workers completed
- [ ] Integration tests passing
- [ ] Fresh conversation test passed
- [ ] Documentation complete
- [ ] V approves for production

---

## Next Steps

1. **Launch Worker 1** (you are here!)
2. Record conversation ID in monitor
3. Validate database creation
4. Generate remaining worker briefs (W2-W7)
5. Continue sequential/parallel launch
6. Final integration testing
7. Production cutover

---

## Support

**Orchestrator Conversation:** con_RxzhtBdWYFsbQueb  
**Architecture Design:** `file 'N5/builds/crm-v3-unified/crm-v3-design.md'`  
**Worker Protocol:** `file 'N5/prefs/operations/orchestrator-protocol.md'`

---

**Status:** 🚀 Ready to Launch Worker 1  
**Created:** 2025-11-17 22:05 ET  
**Version:** 1.0

