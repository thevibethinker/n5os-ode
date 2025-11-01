# W6: Testing & Validation Worker Handoff
**Worker ID:** W6-TESTING  
**Spawned From:** con_MuvXIR7jXZjZxlND (Build Orchestrator)  
**Dependencies:** W1, W2, W3, W4, W5 must ALL complete first  
**Estimated Time:** 60 minutes

---

## Your Mission

Validate the entire team status system end-to-end using **historical data and simulated scenarios** to ensure the rules work correctly before V uses it in production.

You're the **quality gate** - nothing goes live until you verify it works.

---

## Context: What Was Built

The team has built 5 components:

1. **W1 (Schema):** Database tables for team_status_history, career_stats, status_change_log
2. **W2 (Calculator):** `team_status_calculator.py` with top-5-of-7 logic
3. **W3 (Integration):** Wired into `rpi_calculator.py` for daily runs
4. **W4 (Email):** `coaching_email_system.py` with Arsenal manager voice
5. **W5 (UI):** Dashboard updated with status banner and career stats

---

## Your Task Breakdown

### 1. Historical Data Testing

**Goal:** Run calculator against last 30 days of real data

**Steps:**
```bash
# Backup current DB
cp /home/workspace/productivity_tracker.db /home/workspace/productivity_tracker.db.backup-pretest

# Run backfill script (you'll create this)
python3 /home/workspace/N5/scripts/productivity/backfill_team_status.py --start-date 2025-10-01 --end-date 2025-10-30 --dry-run

# Review output:
# - Did promotions/demotions happen at correct times?
# - Are probation periods working?
# - Are grace days calculated correctly?
```

**Expected Results:**
- V's actual October data should show 1-2 status changes
- Elite tier (Invincible/Legend) should NOT unlock unless he had sustained excellence
- Status changes should align with performance patterns

**Create:** `/home/workspace/N5/scripts/productivity/backfill_team_status.py`

### 2. Scenario-Based Testing

**Test each promotion/demotion path:**

**Scenario A: Promotion from Squad → First Team**
```python
# Simulate 14 days: 5/7 days at 90%+ for 2 weeks
test_data = [
    {'date': '2025-11-01', 'rpi': 95.0, 'expected': 5.0},
    {'date': '2025-11-02', 'rpi': 100.0, 'expected': 5.0},
    {'date': '2025-11-03', 'rpi': 92.0, 'expected': 5.0},
    {'date': '2025-11-04', 'rpi': 88.0, 'expected': 5.0},  # grace day
    {'date': '2025-11-05', 'rpi': 91.0, 'expected': 5.0},
    {'date': '2025-11-06', 'rpi': 85.0, 'expected': 5.0},  # grace day
    {'date': '2025-11-07', 'rpi': 93.0, 'expected': 5.0},
    # Repeat for week 2...
]

# Expected: Promotion to First Team after 14 days
# Expected: Email sent with promotion celebration
```

**Scenario B: Demotion with Probation Buffer**
```python
# Simulate: In First Team, has 4-day buffer, 3 bad days should NOT demote
test_data = [
    # Start in First Team with 20 days tenure
    {'date': '2025-11-15', 'rpi': 75.0},  # Bad day 1
    {'date': '2025-11-16', 'rpi': 70.0},  # Bad day 2
    {'date': '2025-11-17', 'rpi': 68.0},  # Bad day 3
    # Still First Team (buffer protecting)
    {'date': '2025-11-18', 'rpi': 95.0},  # Recovery
]

# Expected: No demotion (buffer absorbed bad days)
# Expected: Warning email sent on day 3
```

**Scenario C: Elite Tier Unlock**
```python
# Simulate: 2/4 weeks hitting 125%+ twice per week
test_data = [
    # Week 1: 2x 125%+
    {'date': '2025-11-20', 'rpi': 130.0},
    {'date': '2025-11-21', 'rpi': 128.0},
    # Week 2: 2x 125%+
    {'date': '2025-11-27', 'rpi': 135.0},
    {'date': '2025-11-28', 'rpi': 140.0},
    # Week 3: Only 1x
    {'date': '2025-12-04', 'rpi': 127.0},
    # Week 4: 2x 125%+
    {'date': '2025-12-11', 'rpi': 132.0},
    {'date': '2025-12-12', 'rpi': 150.0},
]

# Expected: After week 4, unlock Invincible status
# Expected: Achievement email sent
```

**Create:** `/home/workspace/N5/scripts/productivity/test_status_scenarios.py`

### 3. Calculator Unit Tests

**Test the math directly:**

```python
# Test: Top 5 of 7 calculation
rpis = [95, 88, 92, 75, 90, 85, 93]  # 7 days
top_5_avg = calculate_top_5_average(rpis)
assert top_5_avg == 92.6  # (95+92+93+90+92)/5

# Test: Asymmetric movement
promotion_threshold = 90.0
demotion_threshold = 85.0
assert promotion_threshold > demotion_threshold  # Easier to climb

# Test: Probation buffer
days_in_status = 20
buffer = calculate_probation_buffer(days_in_status)
assert buffer == 4  # 20 days ÷ 5 = 4 day buffer
```

**Create:** `/home/workspace/N5/scripts/productivity/test_calculator_units.py`

### 4. Email System Testing

**Test email triggers WITHOUT sending:**

```bash
# Run with dry-run flag
python3 /home/workspace/N5/scripts/productivity/coaching_email_system.py \
  --trigger promotion \
  --from-status squad_member \
  --to-status first_team \
  --dry-run

# Output should show:
# ✓ Email generated
# ✓ Subject: [Arsenal Performance] PROMOTED to First Team!
# ✓ Body contains motivational content
# ✓ Signed by "The Gaffer"
# ✗ NOT SENT (dry-run mode)
```

**Test all 5 email types:**
- [ ] Promotion email
- [ ] Demotion email
- [ ] Warning email (2 days from demotion)
- [ ] Critical warning (1 day from demotion)
- [ ] Achievement email (elite tier unlock)

**Verify:**
- Arsenal manager voice is consistent
- No generic AI language ("I hope this message finds you well")
- Specific metrics included in each email
- Appropriate emoji usage (minimal, tasteful)

### 5. Dashboard UI Testing

**Visual Inspection:**
```bash
# Start dashboard
curl http://localhost:3000

# Check these views:
1. Desktop (1920x1080): Status banner prominent, stats readable
2. Tablet (768x1024): Layout adapts correctly
3. Mobile (375x667): Single column, touch-friendly

# Test data scenarios:
- Set status to Transfer List → Banner should be dark red
- Set status to Legend → Banner should be gold with sparkle
- Set trajectory to "falling" → Should show ↘️ icon
```

**API Endpoint Testing:**
```bash
# Test status endpoint
curl http://localhost:3000/api/status | jq

# Expected output:
{
  "current_status": "first_team",
  "days_in_status": 12,
  "trajectory": "stable",
  "last_changed": "2025-10-18",
  "reason": "Consistent performance"
}

# Test career endpoint
curl http://localhost:3000/api/career | jq

# Expected output:
{
  "total_days_first_team": 45,
  "total_promotions": 5,
  ...
}
```

### 6. Integration Testing

**End-to-End Flow:**
```bash
# 1. Simulate a day with good performance
sqlite3 /home/workspace/productivity_tracker.db \
  "INSERT INTO daily_stats (date, rpi, emails_sent, expected_emails) 
   VALUES ('2025-11-01', 120.0, 6, 5);"

# 2. Run calculator
python3 /home/workspace/N5/scripts/productivity/rpi_calculator.py

# 3. Check results
sqlite3 /home/workspace/productivity_tracker.db \
  "SELECT * FROM team_status_history WHERE date='2025-11-01';"

# 4. Check dashboard
curl http://localhost:3000 | grep "status-banner"

# Expected: Status updated, dashboard reflects change
```

---

## Files You'll Create

1. `/home/workspace/N5/scripts/productivity/backfill_team_status.py` - Historical data processor
2. `/home/workspace/N5/scripts/productivity/test_status_scenarios.py` - Scenario simulator
3. `/home/workspace/N5/scripts/productivity/test_calculator_units.py` - Unit test suite
4. `/home/.z/workspaces/con_MuvXIR7jXZjZxlND/TESTING_REPORT.md` - Final validation report

---

## Success Criteria

**Calculator:**
- [ ] Top 5 of 7 math is correct
- [ ] Promotion thresholds work as designed
- [ ] Demotion thresholds work with buffers
- [ ] Elite tier unlocks at correct milestones
- [ ] No edge cases cause crashes

**Email System:**
- [ ] All 5 email types generate correctly
- [ ] Arsenal manager voice is authentic
- [ ] Dry-run mode works (no actual sends during testing)
- [ ] Rate limiting prevents spam

**Dashboard:**
- [ ] Status banner displays correctly for all 6 statuses
- [ ] Career stats are accurate
- [ ] Mobile-responsive
- [ ] API endpoints return valid JSON
- [ ] Performance <500ms

**Integration:**
- [ ] Daily run updates all tables correctly
- [ ] Historical backfill produces expected results
- [ ] No data corruption or conflicts

---

## Validation Report Template

**Create:** `/home/.z/workspaces/con_MuvXIR7jXZjZxlND/TESTING_REPORT.md`

```markdown
# Team Status System - Validation Report

**Tested By:** W6-TESTING  
**Date:** 2025-10-30  
**Status:** ✅ PASS / ⚠️ PASS WITH ISSUES / ❌ FAIL

---

## Test Results Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Calculator Logic | ✅ | Top 5 of 7 math verified |
| Historical Backfill | ✅ | 30 days processed correctly |
| Promotion Scenarios | ✅ | All paths tested |
| Demotion Scenarios | ✅ | Buffer working as designed |
| Elite Tier Unlock | ✅ | Triggers at correct milestone |
| Email Generation | ✅ | All 5 types validated |
| Dashboard UI | ✅ | Mobile + desktop tested |
| API Endpoints | ✅ | JSON responses valid |
| Integration E2E | ✅ | Daily run completes successfully |

---

## Issues Found

### Critical (Blockers)
- [None] or [List any showstoppers]

### Non-Critical (Can launch with)
- [List any minor issues]

---

## Performance Metrics

- Calculator execution time: X.X seconds
- Dashboard load time: X.X seconds
- API response time: X ms

---

## Recommendations

**Before Launch:**
1. [Any must-fix items]

**Post-Launch Monitoring:**
1. Watch for email spam (rate limiting)
2. Monitor DB growth (status_change_log table)
3. Check dashboard performance under load

---

## Sign-Off

This system is ready for production use: ✅ YES / ❌ NO

Reason: [Brief justification]

**Tester:** W6-TESTING  
**Date:** 2025-10-30
```

---

## Return Deliverable Format

Post your TESTING_REPORT.md to the orchestrator thread with:
- Summary of all test results
- Any critical issues that block launch
- Green light (✅) or red light (❌) for production

---

**Orchestrator:** con_MuvXIR7jXZjZxlND  
**Your Mission:** Be thorough. Find the bugs before V does. Give honest assessment.  
**Priority:** CRITICAL - Nothing launches without your sign-off.

Good luck! 🧪

---
**Created:** 2025-10-30 01:40 ET
