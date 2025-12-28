# CRM V3 Deployment Guide

**Project:** crm-v3-unified  
**Orchestrator:** con_RxzhtBdWYFsbQueb  
**Version:** 1.0  
**Date:** 2025-11-17

---

## Pre-Flight Checklist

Before launching workers:

- [x] Orchestration directory created (`N5/builds/crm-v3-unified/`)
- [x] Worker briefs created and stored permanently
- [x] Monitor file initialized
- [x] Architecture design documented
- [ ] V ready to launch workers in new conversations

---

## Launch Sequence

### Step 1: Launch Worker 1 (Database Schema)

**Action:** Open NEW conversation, paste:

```
Load file 'N5/builds/crm-v3-unified/WORKER_1_DATABASE_SCHEMA.md' and execute this task.
Report back when complete.
```

**What this does:**
- Creates `/home/workspace/N5/data/crm_v3.db`
- Creates 5 tables with foreign keys
- Runs validation tests
- Inserts sample data

**Validation (run in orchestrator):**
```bash
ls -lh /home/workspace/N5/data/crm_v3.db
sqlite3 /home/workspace/N5/data/crm_v3.db ".tables"
```

**Expected:** Database exists, 5 tables listed

**Update Monitor:**
- Record conversation ID
- Mark W1 tests complete
- Unblock W2

---

### Step 2: Launch Worker 2 (Migration Scripts)

**Blocked until:** W1 complete

**Action:** Open NEW conversation, paste:

```
Load file 'N5/builds/crm-v3-unified/WORKER_2_MIGRATION_SCRIPTS.md' and execute this task.
Report back when complete.
```

**What this does:**
- Creates migration scripts for 3 legacy systems
- Implements entity deduplication logic
- Documents rollback procedures
- Runs dry-run migration

**Validation:**
```bash
python3 /home/workspace/N5/scripts/crm_migrate_to_v3.py --dry-run
```

**Expected:** Dry-run completes, shows migration plan

**Update Monitor:**
- Record conversation ID
- Mark W2 tests complete
- Unblock W3

---

### Step 3: Launch Worker 3 (Enrichment Worker)

**Blocked until:** W1 complete

**Action:** Open NEW conversation (can launch in parallel with W2)

**What this does:**
- Creates async enrichment queue worker
- Implements priority reordering
- Integrates Aviato API stub
- Sets up append-only intelligence logging

**Validation:**
```bash
python3 /home/workspace/N5/scripts/crm_enrichment_worker.py --test
```

**Update Monitor:**
- Record conversation ID
- Mark W3 tests complete
- Unblock W4

---

### Step 4: Launch Worker 4 (Calendar Webhook)

**Blocked until:** W1, W3 complete

**Action:** Open NEW conversation

**What this does:**
- Creates Google Calendar webhook receiver
- Implements event processor
- Queues enrichment jobs with correct priorities

**Validation:**
```bash
python3 /home/workspace/N5/scripts/crm_calendar_webhook.py --test-payload
```

**Update Monitor:**
- Record conversation ID
- Mark W4 tests complete

---

### Step 5: Launch Workers 5 & 6 (Parallel)

**Blocked until:** W3 complete

**Action:** Open TWO NEW conversations simultaneously

**Worker 5 (Email Tracker):**
- Gmail watcher script
- Spam filter implementation
- Low-priority CRM enrichment

**Worker 6 (CLI Interface):**
- Query commands
- Manual profile creation
- Intelligence log access

**Validation:**
```bash
# W5
python3 /home/workspace/N5/scripts/crm_email_tracker.py --test --dry-run

# W6
python3 /home/workspace/N5/scripts/crm_cli.py search --email "test@example.com"
```

**Update Monitor:**
- Record both conversation IDs
- Mark W5, W6 tests complete
- Unblock W7

---

### Step 6: Launch Worker 7 (Integration Testing)

**Blocked until:** W1-W6 complete

**Action:** Open NEW conversation

**What this does:**
- Creates end-to-end test suite
- Validates full workflow
- Checks architectural principles
- Generates documentation

**Validation:**
```bash
python3 /home/workspace/N5/tests/test_crm_v3_integration.py
bash /home/workspace/N5/builds/crm-v3-unified/integration_test.sh
```

**Update Monitor:**
- Record conversation ID
- Mark W7 tests complete
- Mark project COMPLETE

---

## Blocker Resolution

### If Worker Encounters Issue:

1. **Worker reports** in their conversation
2. **V notifies orchestrator** (con_RxzhtBdWYFsbQueb) with:
   - Worker number
   - Issue description
   - Error messages
3. **Orchestrator analyzes** and creates:
   - Patch brief (if minor fix)
   - Updated worker brief (if spec change)
   - Micro-worker (if isolated fix needed)
4. **V launches** fix in new conversation
5. **Retest** and continue

---

## Rollback Procedures

### If Critical Issue Found:

**Database:**
```bash
# Backup exists automatically (N5/backups/databases/)
# Restore if needed
cp N5/backups/databases/crm_YYYYMMDD_*.db N5/data/crm_v3.db
```

**Legacy Systems:**
- Remain intact until V3 validated
- No destructive operations until final cutover

**Services:**
- Stop any registered user services
- Remove from service registry

---

## Post-Deployment Validation

### After All Workers Complete:

1. **End-to-End Test:**
   - Mock calendar event arrives
   - Enrichment job processed
   - Profile created with intelligence
   - Meeting brief generated

2. **Architectural Compliance:**
   - Review P2, P0.1, P8, P12, P15, P28, P33
   - Verify principles followed

3. **Fresh Conversation Test (P12):**
   - Open brand new conversation
   - Query CRM without context
   - System should work independently

4. **Documentation Check:**
   - README exists
   - API documented
   - CLI help comprehensive

---

## Cutover to Production

### When Ready:

1. **Run final migration:**
   ```bash
   python3 /home/workspace/N5/scripts/crm_migrate_to_v3.py --execute
   ```

2. **Register services:**
   - Enrichment worker as scheduled task
   - Calendar webhook as user service

3. **Update integration points:**
   - Meeting intelligence → CRM V3
   - Email processing → CRM V3
   - Voice memo ingestion → CRM V3

4. **Archive legacy systems:**
   ```bash
   mv Knowledge/crm Knowledge/.archived_crm_legacy_$(date +%Y%m%d)
   mv N5/stakeholders N5/.archived_stakeholders_legacy_$(date +%Y%m%d)
   ```

5. **Monitor for 48 hours:**
   - Check enrichment queue processing
   - Verify webhook triggers
   - Validate profile quality

---

## Success Criteria

Project complete when:

- [ ] All 7 workers reported completion
- [ ] All deliverables created and validated
- [ ] Integration tests passing
- [ ] No blockers remaining
- [ ] Documentation complete
- [ ] Architectural principles verified
- [ ] Fresh conversation test passed
- [ ] V approves for production use

---

**Orchestrator:** con_RxzhtBdWYFsbQueb  
**Status:** 🔵 Ready to Begin  
**Next:** Launch Worker 1  
**Updated:** 2025-11-17 22:00 ET

