---
created: 2025-11-18
last_edited: 2025-11-18
version: 1.0
---

# Worker 4: Enrichment Execution

**Orchestrator:** con_rMaSw6rzVNkWvsQ4
**Mission:** Execute enrichment worker with real integrations, process 9 queued jobs
**Status:** BLOCKED - Waiting for Workers 1-3

## Prerequisites

**Must be complete before starting:**
- ✅ Worker 1: Aviato integration functional
- ✅ Worker 2: Gmail integration functional
- ✅ Worker 3: LinkedIn strategy implemented

**Validation:**
```bash
# Test that all integrations work
cd /home/workspace/N5/scripts/enrichment
python3 aviato_enricher.py --test
python3 gmail_enricher.py --test

# Verify worker updated
grep -A 5 "# 1. Aviato enrichment (REAL)" /home/workspace/N5/scripts/crm_enrichment_worker.py
```

## Context

**Queued Jobs:**
```sql
SELECT 
    eq.id,
    eq.profile_id,
    p.email,
    p.name,
    eq.checkpoint,
    eq.priority,
    eq.status
FROM enrichment_queue eq
JOIN profiles p ON eq.profile_id = p.id
WHERE eq.status = 'queued'
ORDER BY eq.priority DESC, eq.created_at ASC;
```

**Expected:** 9 jobs queued (as of 2025-11-18)

**Target Profiles:**
- Priority 100: CLI test profiles (debugger verification)
- Priority 25: Gmail-triggered profiles
- Priority 50: Calendar-triggered profiles

## Mission

Execute enrichment on all queued jobs with:
1. Real Aviato API calls
2. Real Gmail thread analysis
3. LinkedIn intelligence (via Aviato)
4. Proper YAML appending
5. Database status tracking

## Deliverables

### 1. Pre-Flight Checks

**Verify integrations:**
```bash
# Check Aviato API key
cat /home/workspace/Integrations/Aviato/.env | grep AVIATO_API_KEY

# Check Gmail connection
# (Will be verified by Worker 2's tests)

# Check database connectivity
sqlite3 /home/workspace/N5/data/crm_v3.db "SELECT COUNT(*) FROM enrichment_queue WHERE status='queued';"
```

### 2. Run Enrichment Worker

**Command:**
```bash
cd /home/workspace/N5/scripts
python3 crm_enrichment_worker.py --batch-size 5 --dry-run

# If dry-run looks good:
python3 crm_enrichment_worker.py --batch-size 5
```

**Monitor output for:**
- Aviato API calls successful
- Gmail threads retrieved
- Intelligence appended to YAML
- Database updated (status: queued → processing → completed)
- No "STUB DATA" in output

### 3. Validate Enrichment Quality

**Semantic validation (not scripts!):**

**Step 1:** Read enriched YAML files
```bash
# Pick 3 enriched profiles
sqlite3 /home/workspace/N5/data/crm_v3.db "
SELECT p.yaml_path, p.email, p.enrichment_status 
FROM profiles p
JOIN enrichment_queue eq ON p.id = eq.profile_id
WHERE eq.status = 'completed'
LIMIT 3;"
```

**Step 2:** Review intelligence quality
For each file, check:
- ✅ Real Aviato data (not stub)
- ✅ Real Gmail threads (or "No threads found")
- ✅ LinkedIn section clear
- ✅ Properly formatted markdown
- ✅ Timestamps accurate
- ✅ No hallucination

**Step 3:** Database consistency
```sql
-- Verify status sync
SELECT 
    p.enrichment_status,
    eq.status as queue_status,
    COUNT(*) as count
FROM profiles p
JOIN enrichment_queue eq ON p.id = eq.profile_id
GROUP BY p.enrichment_status, eq.status;

-- Should show: enriched/completed pairing
```

### 4. Generate Enrichment Report

**Create:** `/home/.z/workspaces/con_rMaSw6rzVNkWvsQ4/ENRICHMENT_EXECUTION_REPORT.md`

**Template:**
```markdown
# CRM V3 Enrichment Execution Report
**Worker 4** | **Date:** 2025-11-18

## Execution Summary

**Jobs Processed:** X/9
**Success Rate:** X%
**Duration:** X minutes
**API Calls Made:**
- Aviato: X calls (X successes, X failures)
- Gmail: X searches (X with threads, X empty)

## Profile Quality Assessment

**Sample 1:** {email}
- Aviato: ✅/❌ {result}
- Gmail: ✅/❌ {threads found}
- Intelligence quality: {good/fair/poor}
- Issues: {if any}

**Sample 2:** {email}
... 

**Sample 3:** {email}
...

## Issues Encountered

{List any errors, API failures, rate limits, etc.}

## Database State

**Before:**
- pending: 58
- enriched: 3

**After:**
- pending: {X}
- enriched: {X}

## Validation Criteria

- [ ] All 9 jobs attempted
- [ ] No stub data in outputs
- [ ] Real Aviato intelligence present
- [ ] Real Gmail analysis present (or clear "not found")
- [ ] Database status tracking accurate
- [ ] YAML files properly formatted
- [ ] No errors in worker logs

## Handoff to Worker 5

{Status: READY / BLOCKED}
{Blockers: if any}
```

## Execution Strategy

**Batch Processing:**
- Process jobs in priority order
- Handle errors gracefully (don't stop on failure)
- Log each enrichment attempt
- Update database after each job

**Error Handling:**
- Aviato 404 → Mark as "person not found" but complete
- Aviato 429 → Implement backoff, retry
- Gmail API error → Log but continue
- YAML write error → Critical, stop and investigate

**Rate Limiting:**
- Aviato: Unknown limits, monitor
- Gmail: Google API limits, should be fine for 9 jobs
- Add 1-2 second delay between jobs to be safe

## Validation Criteria

**Before handoff to Worker 5:**
- [ ] All 9 queued jobs processed
- [ ] Enrichment report generated
- [ ] Sample profiles manually reviewed (quality check)
- [ ] No stub data remaining
- [ ] Database consistency verified
- [ ] Error log clean (or documented)

**Quality Metrics:**
- Success rate: >80% target
- Aviato data present: 100% (or documented why not)
- Gmail threads: >50% should find threads
- Intelligence usefulness: Semantic assessment

## Monitoring

**During execution:**
```bash
# Watch worker output
tail -f /home/workspace/N5/logs/enrichment_worker.log

# Monitor queue status
watch -n 5 'sqlite3 /home/workspace/N5/data/crm_v3.db "SELECT status, COUNT(*) FROM enrichment_queue GROUP BY status;"'
```

## Rollback Plan

**If enrichment goes wrong:**
1. Stop worker immediately
2. Check git status of YAML files
3. Revert YAML changes: `git checkout HEAD -- N5/crm_v3/profiles/*.yaml`
4. Reset queue status: 
```sql
UPDATE enrichment_queue 
SET status='queued', attempt_count=0 
WHERE status='processing';
```
5. Investigate and fix integration issue
6. Re-run

## Key Resources

**Files:**
- `file 'N5/scripts/crm_enrichment_worker.py'` - Main worker
- `file 'N5/scripts/enrichment/aviato_enricher.py'` - Aviato integration
- `file 'N5/scripts/enrichment/gmail_enricher.py'` - Gmail integration

**Database:**
- `file 'N5/data/crm_v3.db'` - Queue and profiles

**Profiles:**
- `/home/workspace/N5/crm_v3/profiles/*.yaml` - Enrichment targets

## Handoff to Worker 5

**Success Message:**
```
✅ Worker 4 Complete: Enrichment Execution

Jobs Processed: 9/9 (100%)
Success Rate: X%

Sample Results:
- Aviato: X profiles enriched
- Gmail: X with threads, X without
- Quality: {assessment}

Issues: {none / list}

Ready for Worker 5 production certification.

Report: file '/home/.z/workspaces/con_rMaSw6rzVNkWvsQ4/ENRICHMENT_EXECUTION_REPORT.md'
```

---

**Load this file in a new conversation to execute Worker 4.**

**Start Command:**
```
I am Worker 4 in the CRM V3 Enrichment build orchestration.

Load and execute: file 'N5/builds/crm-v3-enrichment/WORKER_4_EXECUTION.md'

Prerequisites: Workers 1-3 complete.

Execute enrichment worker on 9 queued jobs with real Aviato and Gmail integrations. Validate quality semantically.
```

