# Phase 2B: Handoff to Priority 4 (Automation)

**Date:** 2025-10-12  
**From:** Priority 3 (Polling Loop)  
**To:** Priority 4 (Automation & Deployment)  
**Status:** Ready to proceed once Priority 3 tested with real data

---

## Current State

### Completed ✅
- ✅ **Priority 1:** State Tracking + Stakeholder Profiles
- ✅ **Priority 2:** API Integration (Google Calendar + Gmail)
- ✅ **Priority 3:** Polling Loop (15-minute monitoring)

### Next ⏭️
- ⏸️ **Priority 4:** Automation (scheduled execution & deployment)

---

## What's Available for Priority 4

### Complete Infrastructure

**All systems operational:**
1. State tracking (prevents duplicates)
2. Profile management (creates/updates stakeholder profiles)
3. API integration (fetches calendar & Gmail)
4. Meeting processor (orchestrates workflow)
5. Meeting monitor (15-minute polling loop)
6. Digest integration (formatted output)

**Ready-to-deploy entry point:**
```python
from run_meeting_monitor import run_monitor_with_zo_tools

summary = run_monitor_with_zo_tools(
    use_app_google_calendar,
    use_app_gmail,
    poll_interval_minutes=15,
    lookahead_days=7,
    max_cycles=None  # Run forever
)
```

---

## Priority 4 Requirements

### What Needs to Be Built

#### 1. Scheduled Execution

**Option A: Zo Scheduled Task (Recommended)**
- Use Zo's built-in scheduling system
- Create recurring task every 15 minutes
- Easier to manage and monitor

**Option B: Cron Job**
- Traditional cron setup
- More complex but flexible
- Requires root access

**Recommended: Option A (Zo Scheduled Task)**

**Implementation:**
```python
# Zo will create a scheduled task:
Rule: "FREQ=HOURLY;INTERVAL=0;BYMINUTE=0,15,30,45"
Instruction: "Run the meeting monitor for one cycle and append results to digest"
```

---

#### 2. Production Deployment Script

**File:** `N5/scripts/deploy_meeting_monitor.py`

**Purpose:** Set up monitoring for production

**Features Needed:**
- Initialize all directories
- Create log rotation config
- Set up scheduled task
- Verify API access
- Run health check
- Generate deployment report

---

#### 3. Health Check & Monitoring

**File:** `N5/scripts/monitor_health.py`

**Purpose:** Verify system is running correctly

**Checks:**
- Is scheduled task running?
- When was last successful cycle?
- Any errors in last 24 hours?
- Is log file growing?
- Are profiles being created?
- Is state file being updated?

**Alert Conditions:**
- No cycles in last hour → Send alert
- Errors > 10 in last 24h → Send alert
- API failures > 5 → Send alert
- Disk space < 1GB → Send alert

---

#### 4. Log Rotation

**File:** `N5/scripts/rotate_logs.py`

**Purpose:** Prevent logs from growing too large

**Configuration:**
- Keep last 30 days
- Rotate daily at midnight
- Compress logs older than 7 days
- Delete logs older than 30 days

---

#### 5. Performance Dashboard

**File:** `N5/scripts/generate_dashboard.py`

**Purpose:** Show monitoring metrics

**Metrics to Track:**
- Cycles per day
- Meetings processed
- Urgent meetings detected
- Errors encountered
- Average cycle time
- API response times
- Profile creation rate

**Output:** Markdown report for daily digest

---

### Architecture for Priority 4

```
Priority 4 Architecture
=======================

Zo Scheduled Task (every 15 min)
  ↓
  Triggers run_meeting_monitor.py
  ↓
  Calls meeting_monitor.py
    → Runs single cycle
    → Generates digest section
    → Logs metrics
  ↓
  Appends to daily digest
  ↓
  Updates dashboard metrics
  ↓
  Health check validates
  ↓
  Sleeps until next trigger
```

---

## Implementation Plan for Priority 4

### Phase 1: Basic Automation (1 hour)
1. Create deployment script
2. Set up Zo scheduled task
3. Test scheduled execution
4. Verify logging works
5. Check digest integration

### Phase 2: Monitoring (1 hour)
1. Create health check script
2. Add error alerting
3. Build performance dashboard
4. Test alert conditions

### Phase 3: Log Management (30 min)
1. Create log rotation script
2. Set up daily rotation schedule
3. Test compression
4. Verify old logs deleted

### Phase 4: Production Deploy (30 min)
1. Run full deployment
2. Monitor for 24 hours
3. Validate all systems
4. Generate completion report

**Total estimated time: 3 hours**

---

## Testing Strategy for Priority 4

### Deployment Tests
1. Test deployment script creates all resources
2. Verify scheduled task triggers correctly
3. Check that cycles run every 15 minutes
4. Confirm logs are created
5. Validate digest sections are appended

### Health Check Tests
1. Test with healthy system (all passing)
2. Test with missing cycles (alert triggered)
3. Test with errors (alert triggered)
4. Test with API failures (alert triggered)

### Log Rotation Tests
1. Test daily rotation works
2. Verify compression works
3. Check old logs are deleted
4. Validate no data loss

### End-to-End Tests
1. Deploy to production
2. Run for 24 hours
3. Verify 96 cycles (24h * 4 per hour)
4. Check all meetings detected
5. Validate no errors

---

## Configuration for Priority 4

### Scheduled Task Config
```python
SCHEDULE_RULE = "FREQ=HOURLY;INTERVAL=0;BYMINUTE=0,15,30,45"
TASK_NAME = "meeting-monitor-cycle"
TASK_INSTRUCTION = """
Run a single cycle of the meeting monitor.
Fetch calendar events, process new meetings, 
generate digest section, and log metrics.
"""
```

### Health Check Config
```python
MAX_CYCLE_GAP_MINUTES = 60        # Alert if no cycle in 1 hour
MAX_ERRORS_PER_DAY = 10           # Alert if >10 errors/day
MAX_API_FAILURES = 5              # Alert if >5 API fails
MIN_DISK_SPACE_GB = 1             # Alert if <1GB free
```

### Log Rotation Config
```python
LOG_RETENTION_DAYS = 30           # Keep logs for 30 days
LOG_COMPRESS_AFTER_DAYS = 7       # Compress logs after 7 days
LOG_ROTATION_HOUR = 0             # Rotate at midnight ET
```

---

## Dependencies for Priority 4

### New Dependencies (maybe)
- `schedule` (for cron-like scheduling) - only if not using Zo scheduled tasks
- All existing dependencies from P1-P3

### Zo Dependencies
- Zo scheduled task system
- Zo email notification (for alerts)
- Zo file system access

---

## Success Criteria for Priority 4

### Deployment Complete ✅
- [ ] Scheduled task created and active
- [ ] Runs every 15 minutes automatically
- [ ] Logs all activity
- [ ] Digest sections appended
- [ ] Health checks passing

### Monitoring Active ✅
- [ ] Health check runs daily
- [ ] Alerts trigger on errors
- [ ] Dashboard shows metrics
- [ ] Performance tracked
- [ ] Issues detected early

### Production Ready ✅
- [ ] Runs continuously without intervention
- [ ] Handles errors gracefully
- [ ] Logs rotated automatically
- [ ] Disk space managed
- [ ] Ready for long-term operation

---

## Potential Challenges

### Challenge 1: Scheduled Task Reliability
**Issue:** Zo scheduled tasks might not run exactly on time  
**Solution:** Accept ±1 minute variance, monitor for missed cycles

### Challenge 2: API Rate Limits
**Issue:** Polling every 15 min might approach limits  
**Solution:** Current usage is well below limits (verified), monitor anyway

### Challenge 3: Disk Space
**Issue:** Logs and profiles will grow over time  
**Solution:** Log rotation + profile archiving (old profiles after 90 days)

### Challenge 4: Long-Running Process
**Issue:** If using continuous loop, process might die  
**Solution:** Use scheduled task (preferred) or supervisord (if needed)

---

## Deployment Checklist

### Before Deploying
- [x] Priority 1 complete and tested
- [x] Priority 2 complete and tested
- [x] Priority 3 complete and tested
- [ ] Priority 3 tested with real calendar data
- [ ] At least one full cycle successful with V-OS tags
- [ ] Digest integration verified

### During Deployment
- [ ] Run deployment script
- [ ] Verify all directories created
- [ ] Check scheduled task created
- [ ] Test one manual cycle
- [ ] Wait for first scheduled cycle
- [ ] Verify cycle ran successfully
- [ ] Check logs for errors
- [ ] Validate digest section created

### After Deployment
- [ ] Monitor for 24 hours
- [ ] Verify 96 cycles ran (4 per hour)
- [ ] Check no errors accumulated
- [ ] Validate profiles being created
- [ ] Confirm digest sections appearing
- [ ] Review performance metrics

---

## Quick Start for Priority 4

### When Ready to Build:

1. **Tell Zo:**
   "Build Priority 4: deployment and automation for meeting monitor"

2. **Zo will create:**
   - `N5/scripts/deploy_meeting_monitor.py`
   - `N5/scripts/monitor_health.py`
   - `N5/scripts/rotate_logs.py`
   - `N5/scripts/generate_dashboard.py`
   - Zo scheduled task configuration

3. **Test deployment:**
   - Run deployment script
   - Verify scheduled task active
   - Wait for first cycle
   - Check logs

4. **Monitor for 24 hours:**
   - Check health every 6 hours
   - Review dashboard metrics
   - Validate no issues

---

## Example: Full Production Setup

### Step 1: Deploy
```
Tell Zo: "Deploy the meeting monitor to production"
```

Zo will:
- Create scheduled task (every 15 min)
- Set up log rotation (daily)
- Initialize health checks
- Generate first dashboard
- Run first cycle

### Step 2: Monitor
```
Tell Zo: "Show meeting monitor health status"
```

Zo will show:
- Last cycle: 5 minutes ago ✅
- Cycles today: 42 ✅
- Errors today: 0 ✅
- Meetings processed: 3 ✅
- System status: Healthy ✅

### Step 3: Review
```
Tell Zo: "Generate meeting monitor dashboard"
```

Zo will create:
- Metrics for last 7 days
- Cycle success rate
- Processing times
- Error breakdown
- Top meeting types

---

## Conclusion

**Priority 3 complete. Priority 4 ready to build.**

All infrastructure operational. Just need:
1. Scheduled execution (Zo task)
2. Health monitoring
3. Log rotation
4. Performance dashboard

Estimated time: 3 hours to build and deploy.

**Blocked by:** Testing Priority 3 with real calendar data  
**Expected:** Once Howie adds V-OS tags  
**Next:** Test P3 end-to-end, then build P4

---

**Status:** ✅ READY FOR PRIORITY 4  
**Handoff Date:** 2025-10-12  
**Prepared By:** Zo
