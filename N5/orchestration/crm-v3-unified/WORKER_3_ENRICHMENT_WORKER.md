# Worker 3: Enrichment Worker

**Orchestrator:** con_RxzhtBdWYFsbQueb  
**Task ID:** W3-ENRICHMENT  
**Estimated Time:** 60 minutes  
**Dependencies:** Worker 1 ✅ Complete, Worker 2 ✅ Complete

---

## Mission

Build the async enrichment worker that processes the enrichment queue, calls external APIs (Aviato, Gmail, LinkedIn), and appends intelligence to profile YAML files in append-only format.

---

## Context

**Workers 1-2 Status:** ✅ Complete  
- Database schema ready with `enrichment_queue` table
- 50 profiles migrated and ready for enrichment
- YAML profile files exist in `/home/workspace/N5/crm_v3/profiles/`

**This is Worker 3 of 7** in the CRM V3 unified system build orchestration.

**Architecture reference:** `file 'N5/orchestration/crm-v3-unified/crm-v3-design.md'`

---

## Task Breakdown

### 1. Create Enrichment Worker Script

**File:** `/home/workspace/N5/scripts/crm_enrichment_worker.py`

**Core Functionality:**
```python
async def enrichment_worker():
    """
    Background worker that processes enrichment queue.
    Runs continuously, checking queue every 60 seconds.
    """
    while True:
        # 1. Fetch next job from queue (highest priority, scheduled_for <= now)
        job = fetch_next_enrichment_job()
        
        if not job:
            await asyncio.sleep(60)
            continue
        
        # 2. Mark job as 'processing'
        update_job_status(job.id, 'processing')
        
        try:
            # 3. Enrich based on checkpoint
            if job.checkpoint == 'checkpoint_1':
                await enrich_checkpoint_1(job.profile_id)
            elif job.checkpoint == 'checkpoint_2':
                await enrich_checkpoint_2(job.profile_id)
            
            # 4. Mark job as 'completed'
            update_job_status(job.id, 'completed')
            
        except Exception as e:
            # 5. Handle errors (retry logic)
            handle_enrichment_error(job.id, str(e))
```

**Key Components:**

1. **Queue Fetcher**
   - Query: `SELECT * FROM enrichment_queue WHERE status='queued' AND scheduled_for <= datetime('now') ORDER BY priority DESC, scheduled_for ASC LIMIT 1`
   - Atomic update to 'processing' status

2. **Checkpoint 1 Enricher** (3 days before meeting)
   - Call Aviato API (stub for now with TODO)
   - Call Gmail API for email threads
   - Call LinkedIn API (stub for now with TODO)
   - Append intelligence to YAML

3. **Checkpoint 2 Enricher** (morning-of meeting)
   - Delta check: New emails since checkpoint 1?
   - Generate meeting brief (synthesize all sources)
   - Email brief to V (use `send_email_to_user`)

4. **Append-Only Intelligence Format**
```yaml
## Intelligence Log

### 2025-11-18 | Aviato Enrichment
**Source:** aviato_api  
**Checkpoint:** checkpoint_1

- Current role: Senior PM at Company X
- Location: San Francisco, CA  
- LinkedIn: linkedin.com/in/example
- Recent activity: Posted about AI product launches

### 2025-11-18 | Gmail Thread Analysis
**Source:** gmail_api  
**Checkpoint:** checkpoint_1

Recent email thread (2025-11-15):
- Discussed potential collaboration on hiring platform
- Offered intro to Series A investors
- Warm relationship, expects follow-up
```

5. **Error Handling & Retries**
   - Max 3 attempts per job
   - Exponential backoff (60s, 300s, 900s)
   - After 3 fails → mark as 'failed' with error message

### 2. Create Aviato API Stub

**File:** `/home/workspace/N5/scripts/utils/aviato_client.py`

```python
async def enrich_via_aviato(email: str) -> dict:
    """
    Stub for Aviato API enrichment.
    TODO: Replace with actual Aviato API integration in future.
    
    For now, returns mock data to test workflow.
    """
    # TODO: Implement actual Aviato API call
    # response = await aviato_api.enrich(email)
    
    return {
        "name": "Mock Name",
        "title": "Mock Title",
        "company": "Mock Company",
        "location": "Mock Location",
        "linkedin": None,
        "note": "STUB DATA - Replace with real Aviato API"
    }
```

### 3. Create Gmail Thread Retriever

**File:** `/home/workspace/N5/scripts/utils/gmail_thread_retriever.py`

**Functionality:**
- Use `use_app_gmail` tool to search for email threads
- Query: `from:{email} OR to:{email}` with `maxResults=5`
- Extract recent threads (last 90 days)
- Identify V's replies (not just received emails)
- Return thread summaries

### 4. Create Intelligence Appender

**File:** `/home/workspace/N5/scripts/utils/intelligence_appender.py`

**Functionality:**
```python
def append_intelligence(yaml_path: str, source_type: str, checkpoint: str, content: str):
    """
    Append intelligence to YAML profile without editing existing content.
    Creates ## Intelligence Log section if it doesn't exist.
    """
    with open(yaml_path, 'r') as f:
        existing = f.read()
    
    # Check if Intelligence Log section exists
    if "## Intelligence Log" not in existing:
        existing += "\n\n## Intelligence Log\n"
    
    # Append new intelligence entry
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n### {timestamp} | {source_type}\n"
    entry += f"**Checkpoint:** {checkpoint}\n\n"
    entry += content + "\n"
    
    with open(yaml_path, 'a') as f:
        f.write(entry)
```

### 5. CLI Testing Interface

Add `--test` mode to enrichment worker:

```bash
# Test mode: Process one job and exit
python3 /home/workspace/N5/scripts/crm_enrichment_worker.py --test

# Dry-run mode: Fetch jobs but don't process
python3 /home/workspace/N5/scripts/crm_enrichment_worker.py --dry-run

# Production mode: Run continuously
python3 /home/workspace/N5/scripts/crm_enrichment_worker.py
```

### 6. Create Test Job

Insert a test enrichment job:

```python
def create_test_enrichment_job():
    """Create a test job for the first profile"""
    conn = sqlite3.connect('/home/workspace/N5/data/crm_v3.db')
    c = conn.cursor()
    
    # Get first profile
    c.execute("SELECT id, email FROM profiles LIMIT 1")
    profile_id, email = c.fetchone()
    
    # Insert test job (scheduled for now, high priority)
    c.execute("""
        INSERT INTO enrichment_queue 
        (profile_id, priority, scheduled_for, checkpoint, trigger_source, trigger_metadata)
        VALUES (?, 100, datetime('now'), 'checkpoint_1', 'manual_test', ?)
    """, (profile_id, f'{{"email": "{email}"}}'))
    
    conn.commit()
    conn.close()
    
    print(f"✓ Created test job for profile {profile_id} ({email})")
```

---

## Success Criteria

### Required Deliverables

1. ✅ `crm_enrichment_worker.py` - Main worker script
2. ✅ `utils/aviato_client.py` - Aviato API stub
3. ✅ `utils/gmail_thread_retriever.py` - Gmail integration
4. ✅ `utils/intelligence_appender.py` - YAML append utility
5. ✅ Test job creation + execution
6. ✅ Validation tests pass

### Tests to Pass

```bash
# Test 1: Create test job
python3 -c "from crm_enrichment_worker import create_test_enrichment_job; create_test_enrichment_job()"

# Test 2: Run worker in test mode
python3 /home/workspace/N5/scripts/crm_enrichment_worker.py --test

# Test 3: Verify intelligence appended
cat /home/workspace/N5/crm_v3/profiles/*.yaml | grep "## Intelligence Log"

# Test 4: Check job status
sqlite3 /home/workspace/N5/data/crm_v3.db "SELECT status, completed_at FROM enrichment_queue WHERE trigger_source='manual_test'"
```

**Expected Results:**
- Job status = 'completed'
- Intelligence Log section exists in YAML
- Aviato stub data appended
- Gmail threads retrieved (or error logged)
- No crashes or exceptions

---

## Validation Checklist

Before marking Worker 3 complete:

- [ ] `crm_enrichment_worker.py` created with all core functions
- [ ] Aviato API stub working (returns mock data)
- [ ] Gmail thread retriever implemented
- [ ] Intelligence appender working (append-only, no edits)
- [ ] Test job created and processed successfully
- [ ] Intelligence appended to at least 1 YAML profile
- [ ] Queue processing works (fetch → process → complete)
- [ ] Priority ordering correct (high → low)
- [ ] Error handling tested (simulated API failure)
- [ ] All tests pass without errors

---

## Notes for Builder

**Bias Towards:**
- Simple, readable code (async/await pattern)
- Stub APIs clearly marked with TODO comments
- Comprehensive error logging
- CLI test modes for validation

**Architecture Principles:**
- **P0.1 LLM-First:** Intelligence is AI-queryable, not human-greppable
- **Append-Only:** Never edit existing YAML content, only append
- **Simple Over Easy:** Straightforward async loop, not complex orchestration
- **Flow Over Pools:** Queue-based processing creates natural flow

**Known TODOs for Future Workers:**
- Actual Aviato API integration (Worker 4+)
- Actual LinkedIn API integration (Worker 4+)
- Meeting brief generation logic (Worker 4+)
- Email delivery of morning-of briefs (Worker 4+)

---

## Handoff Instructions

Report back to orchestrator with:

1. Worker 3 conversation ID
2. All deliverables created (file paths)
3. Test execution results
4. Sample intelligence log entry (show append-only working)
5. Any issues or blockers encountered

**Ready for Worker 4:** After validation passes, Worker 4 (Calendar Webhook) can begin.

---

**Orchestrator Contact:** con_RxzhtBdWYFsbQueb  
**Created:** 2025-11-18 03:00 ET  
**Status:** Ready to Execute  
**Workers 1-2 Validation:** ✅ Complete

