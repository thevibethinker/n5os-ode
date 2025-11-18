# Worker 4B: Calendar Webhook Patches

**Orchestrator:** con_RxzhtBdWYFsbQueb  
**Task ID:** W4B-PATCHES  
**Estimated Time:** 25 minutes  
**Dependencies:** Worker 4 ✅ Complete (with bugs)  
**Type:** Bug Fix / Patch Worker

---

## Mission

Fix 3 critical bugs in Worker 4's calendar webhook integration that are preventing full operation. Implement missing helper functions, fix test suite, and validate all services operational.

---

## Context

**Worker 4 Status:** Infrastructure deployed, services running, but **3 bugs blocking operation:**

1. **CRITICAL:** Missing `get_or_create_profile()` and `schedule_enrichment_job()` in helpers
2. **MINOR:** `load_config()` signature mismatch breaking tests
3. **MINOR:** Test database constraint violation (missing expiration_time)

**Current State:**
- ✅ Services registered: crm-calendar-webhook (8765), renewal (8766), health (8767)
- ✅ Database schema complete
- ✅ Config file created
- ❌ Import errors blocking webhook handler
- ❌ Test suite: 4/7 passing

**Error Evidence:**
```
Failed to import helpers: cannot import name 'get_or_create_profile'
Failed to import helpers: cannot import name 'schedule_enrichment_job'
```

---

## Bug #1: Missing Helper Functions (CRITICAL)

**File:** `N5/scripts/crm_calendar_helpers.py`

### Function 1: `get_or_create_profile()`

**Signature:**
```python
def get_or_create_profile(email: str, name: str, source: str = 'calendar') -> int:
    """
    Get existing profile or create new one.
    
    Args:
        email: Contact email address
        name: Contact name
        source: Source system (default: 'calendar')
        
    Returns:
        int: profile_id
        
    Behavior:
        1. Query profiles table for existing email
        2. If found, return existing profile_id
        3. If not found:
           a. Generate yaml_path (N5/crm_v3/profiles/{Name}_{email_prefix}.yaml)
           b. Create stub YAML file with frontmatter
           c. INSERT INTO profiles (email, name, yaml_path, source, enrichment_status, profile_quality)
           d. Return new profile_id
    """
```

**Implementation Requirements:**
- Use `DB_PATH = '/home/workspace/N5/data/crm_v3.db'`
- YAML path format: `N5/crm_v3/profiles/{FirstName}_{LastName}_{email_prefix}.yaml`
  - Example: `epak171@gmail.com` + "Elaine Pak" → `Elaine_Pak_epak171.yaml`
- Stub YAML format:
```yaml
---
created: YYYY-MM-DD
last_edited: YYYY-MM-DD
version: 1.0
source: calendar
email: {email}
category: NETWORKING
relationship_strength: weak
---

# {Name}

## Contact Information
- **Email:** {email}
- **Organization:** To be determined

## Metadata
- **Sources:** calendar
- **Source Count:** 1
- **Total Meetings:** 0

## Notes

*Awaiting enrichment.*
```

- Set `enrichment_status = 'pending'`
- Set `profile_quality = 'stub'`
- Use proper error handling (file I/O, database operations)

### Function 2: `schedule_enrichment_job()`

**Signature:**
```python
def schedule_enrichment_job(
    profile_id: int,
    scheduled_for: str,
    checkpoint: str,
    priority: int,
    trigger_source: str,
    trigger_metadata: str = None
) -> int:
    """
    Queue enrichment job for profile.
    
    Args:
        profile_id: Profile database ID
        scheduled_for: ISO datetime string (when to process)
        checkpoint: 'checkpoint_1' or 'checkpoint_2'
        priority: 1-100 (higher = sooner, 75 for checkpoint_1, 100 for checkpoint_2)
        trigger_source: 'calendar' | 'gmail' | 'manual'
        trigger_metadata: JSON string with additional context (optional)
        
    Returns:
        int: job_id (enrichment_queue.id)
        
    Behavior:
        1. Check if duplicate job exists (same profile_id, checkpoint, status='queued')
        2. If duplicate exists, return existing job_id (don't create duplicate)
        3. If no duplicate:
           a. INSERT INTO enrichment_queue (profile_id, scheduled_for, checkpoint, priority, trigger_source, trigger_metadata, status)
           b. Return new job_id
    """
```

**Implementation Requirements:**
- Use `DB_PATH = '/home/workspace/N5/data/crm_v3.db'`
- Duplicate detection prevents queue flooding
- Default `status = 'queued'`
- Error handling for database operations

### Function 3: Fix `load_config()`

**Current signature:**
```python
def load_config() -> dict:
```

**New signature:**
```python
def load_config(config_path: str = CONFIG_PATH) -> dict:
    """
    Load webhook configuration from YAML file.
    
    Args:
        config_path: Path to config file (default: N5/config/calendar_webhook.yaml)
        
    Returns:
        dict: Parsed configuration
    """
```

**Why:** Test suite passes custom path, helper expects none. Add optional parameter with default.

---

## Bug #2: Test Suite Database Constraint (MINOR)

**File:** `N5/scripts/test_calendar_webhook.py`

**Location:** `test_database_operations()` function

**Current code (around line 150-170):**
```python
cursor.execute(
    "INSERT INTO webhook_health (service, status) VALUES (?, ?)",
    ('test_service', 'ACTIVE')
)
```

**Fixed code:**
```python
cursor.execute(
    "INSERT INTO webhook_health (service, status, expiration_time) VALUES (?, ?, datetime('now', '+7 days'))",
    ('test_service', 'ACTIVE')
)
```

**Why:** `webhook_health.expiration_time` is NOT NULL, test insert violates constraint.

---

## Bug #3: Import Error Propagation (SIDE EFFECT)

**No code changes needed** - fixing Bugs #1 and #2 resolves this automatically.

**Services will auto-recover** once helpers exist. If not, manual restart:
```bash
# Services should auto-restart on file changes
# If needed, restart via Zo service management or:
pkill -f crm_calendar_webhook_handler.py
# Service manager will restart it
```

---

## Implementation Steps

### Step 1: Implement Helper Functions (15 min)

**Target:** `file 'N5/scripts/crm_calendar_helpers.py'`

1. Add `get_or_create_profile()` function (full implementation)
2. Add `schedule_enrichment_job()` function (full implementation)
3. Update `load_config()` signature (add default parameter)
4. Test imports work: `python3 -c "from crm_calendar_helpers import get_or_create_profile, schedule_enrichment_job"`

### Step 2: Fix Test Suite (5 min)

**Target:** `file 'N5/scripts/test_calendar_webhook.py'`

1. Locate `test_database_operations()` function
2. Fix webhook_health INSERT statement (add expiration_time)
3. Verify syntax: `python3 -m py_compile test_calendar_webhook.py`

### Step 3: Restart Services (2 min)

```bash
# Check if services auto-restarted (wait 10 seconds)
sleep 10

# Verify no import errors in logs
tail -n 20 /dev/shm/crm-calendar-webhook.log
tail -n 20 /dev/shm/crm-webhook-renewal.log
tail -n 20 /dev/shm/crm-webhook-health.log

# If import errors persist, manual restart:
pkill -f crm_calendar_webhook_handler.py
pkill -f crm_calendar_webhook_renewal.py
pkill -f crm_calendar_health_monitor.py
# Services should auto-restart within 5-10 seconds
```

### Step 4: Re-run Validation (3 min)

```bash
python3 /home/workspace/N5/scripts/test_calendar_webhook.py
```

**Expected output:**
```
✓ Config file exists and valid
✓ Database schema complete
✓ Webhook services registered
✓ Helper functions importable
✓ Test profile creation works
✓ Test enrichment job scheduling works
✓ Webhook handler accepts test notification

7/7 tests passed
```

---

## Success Criteria

**All must be TRUE:**

1. ✅ Helper functions exist and importable
2. ✅ Test suite runs without errors
3. ✅ All 7 tests pass
4. ✅ No import errors in service logs
5. ✅ Services running and healthy (8765, 8766, 8767)

---

## Validation Commands

```bash
# Test imports
python3 -c "from crm_calendar_helpers import get_or_create_profile, schedule_enrichment_job, load_config; print('✓ All imports successful')"

# Run test suite
python3 /home/workspace/N5/scripts/test_calendar_webhook.py

# Check service health
tail -n 50 /dev/shm/crm-calendar-webhook.log | grep -i error
tail -n 50 /dev/shm/crm-webhook-renewal.log | grep -i error
tail -n 50 /dev/shm/crm-webhook-health.log | grep -i error

# Verify services running
curl -s http://localhost:8765/health
curl -s http://localhost:8766/health
curl -s http://localhost:8767/health
```

---

## Deliverables

**Report back to Orchestrator:**

1. Implementation status (completed functions)
2. Test suite results (X/7 passing)
3. Service health status
4. Any remaining issues or blockers

**Ready for Worker 5:** After all tests pass, Workers 5 & 6 can proceed in parallel.

---

## Notes

**Google Search Console NOT Required:**
- That's for SEO/search data (different service)
- Calendar webhooks use Calendar API (already have credentials)
- Domain ownership proven by hosting on `va.zo.computer`

**Architecture Context:**
- `file 'N5/orchestration/crm-v3-unified/WORKER_4_CALENDAR_WEBHOOK.md'` - Original Worker 4 brief
- `file 'N5/orchestration/crm-v3-unified/crm-v3-design.md'` - Full CRM V3 architecture
- `file 'N5/config/calendar_webhook.yaml'` - Webhook configuration

---

**Orchestrator Contact:** con_RxzhtBdWYFsbQueb  
**Created:** 2025-11-18 03:15 ET  
**Status:** Ready to Execute  
**Worker 4 Status:** Complete (with bugs blocking operation)

