# CRM V3 Unified System - Orchestration Plan

**Project:** crm-v3-unified  
**Orchestrator:** con_RxzhtBdWYFsbQueb  
**Started:** 2025-11-17 21:35 ET  
**Status:** Planning Complete → Ready to Launch Workers

---

## Architecture Overview

**Goal:** Migrate 3 parallel CRM systems → 1 unified webhook-triggered, queue-based, AI-queryable system

**Three Legacy Systems:**
1. `Knowledge/crm/` (57 profiles, SQLite-backed)
2. `N5/stakeholders/` (10 profiles, YAML frontmatter)
3. `N5/data/profiles.db` (44 records, meeting-centric)

**New Unified System:**
- SQLite database (5 tables) = queryable index
- YAML profiles = source of truth
- Append-only intelligence logs
- Google Calendar webhook triggers
- Async enrichment queue with Aviato API

---

## Dependency Graph

```
W1 (Database Schema)
  ↓
W2 (Migration Scripts) ←── [BLOCKED until W1]
  ↓
W3 (Enrichment Worker) ←── [BLOCKED until W1]
  ↓
W4 (Calendar Webhook) ←── [BLOCKED until W1, W3]
  ↓
W5 (Email Reply Tracker) ←── [BLOCKED until W1]
  ↓
W6 (CLI Interface) ←── [BLOCKED until W1]
  ↓
W7 (Integration & Testing) ←── [BLOCKED until W1-W6]
```

---

## Worker Breakdown

### Phase 1: Foundation (Sequential)

**W1: Database Schema Creation**
- **Duration:** 30 min
- **Dependency:** None
- **Deliverable:** `/home/workspace/N5/data/crm_v3.db` with 5 tables
- **Test:** Schema validation, sample inserts

**W2: Migration Scripts**
- **Duration:** 45 min
- **Dependency:** W1
- **Deliverable:** Scripts to migrate 3 legacy systems → V3
- **Test:** Dry-run migration, entity deduplication logic

### Phase 2: Core Services (Sequential after W2)

**W3: Enrichment Worker**
- **Duration:** 60 min
- **Dependency:** W1
- **Deliverable:** Async queue worker (`N5/scripts/crm_enrichment_worker.py`)
- **Test:** Queue processing, Aviato API stub integration

**W4: Calendar Webhook Integration**
- **Duration:** 45 min
- **Dependency:** W1, W3
- **Deliverable:** Webhook receiver + event processor
- **Test:** Mock webhook payload handling

### Phase 3: Ingestion Sources (Parallel after W3)

**W5: Email Reply Tracker**
- **Duration:** 30 min
- **Dependency:** W1
- **Deliverable:** Gmail watcher script + spam filter
- **Test:** Detect V's replies, filter spam patterns

**W6: CLI Interface**
- **Duration:** 30 min
- **Dependency:** W1
- **Deliverable:** Query + manual entry commands
- **Test:** Profile creation, search, updates

### Phase 4: Integration & Validation

**W7: Integration Testing + Documentation**
- **Duration:** 45 min
- **Dependency:** W1-W6
- **Deliverable:** End-to-end test suite + README
- **Test:** Full workflow validation, rollback procedures

---

## File Organization

```
/home/workspace/N5/orchestration/crm-v3-unified/
├── ORCHESTRATOR_PLAN.md (this file)
├── ORCHESTRATOR_MONITOR.md (status tracking)
├── ORCHESTRATOR_DEPLOYMENT_GUIDE.md (step-by-step)
├── WORKER_1_DATABASE_SCHEMA.md
├── WORKER_2_MIGRATION_SCRIPTS.md
├── WORKER_3_ENRICHMENT_WORKER.md
├── WORKER_4_CALENDAR_WEBHOOK.md
├── WORKER_5_EMAIL_TRACKER.md
├── WORKER_6_CLI_INTERFACE.md
├── WORKER_7_INTEGRATION_TESTING.md
└── crm-v3-design.md (full architecture reference)
```

---

## Launch Sequence

### Day 1: Foundation
1. Launch W1 (Database Schema) → Validate
2. Launch W2 (Migration Scripts) → Validate with dry-run

### Day 2: Core Services
3. Launch W3 (Enrichment Worker) → Test with stub API
4. Launch W4 (Calendar Webhook) → Test with mock payloads

### Day 3: Ingestion + CLI
5. Launch W5 & W6 in parallel → Validate both

### Day 4: Integration
6. Launch W7 (Integration Testing) → Full system validation

---

## Success Criteria

### W1: Database Schema
- [ ] `crm_v3.db` created with 5 tables
- [ ] All foreign keys working
- [ ] Sample data inserts successful

### W2: Migration Scripts
- [ ] Dry-run migration completes without errors
- [ ] Entity deduplication logic correct
- [ ] Rollback procedures documented

### W3: Enrichment Worker
- [ ] Queue processor handles priority reordering
- [ ] Aviato API integration stub working
- [ ] Append-only intelligence log format correct

### W4: Calendar Webhook
- [ ] Webhook receives Google Calendar events
- [ ] Event processor extracts attendees correctly
- [ ] Enrichment jobs queued with correct priorities

### W5: Email Reply Tracker
- [ ] Detects V's replies (not received emails)
- [ ] Spam filter blocks "fuck off" messages
- [ ] Low-priority CRM enrichment queued

### W6: CLI Interface
- [ ] Create profile manually
- [ ] Search by name/email
- [ ] Query intelligence logs

### W7: Integration Testing
- [ ] End-to-end workflow test passes
- [ ] Architectural principles compliance
- [ ] Fresh conversation test (P12)
- [ ] Documentation complete

---

## Rollback Plan

If issues arise:
1. **Database:** Keep `crm_v3.db` separate, don't touch legacy
2. **Migration:** Dry-run first, manual review before execution
3. **Services:** Register as user services, easy to stop/restart
4. **Fallback:** Legacy systems remain intact until V3 validated

---

## Architectural Principles Checklist

- [ ] P2: Single Source of Truth (YAML profiles)
- [ ] P0.1: LLM-First (AI-queryable intelligence)
- [ ] P8: Minimal Context (Database stores pointers)
- [ ] P12: Fresh Conversation Test (Documentation complete)
- [ ] P15: Honest Completion (No false "done")
- [ ] P28: Think Before Build (This plan!)
- [ ] P33: Test-First (Every worker includes tests)

---

## Timeline Estimate

**Total:** 4-5 hours of worker execution time  
**Calendar:** 4 days (allowing for validation between phases)  
**Ready:** Week of 2025-11-18

---

**Orchestrator:** con_RxzhtBdWYFsbQueb  
**Created:** 2025-11-17 21:40 ET  
**Status:** ✅ Plan Complete, Ready to Generate Worker Briefs

