# Team Status System - Launch Checklist
**Project:** Career Progression Layer for N5 Productivity Tracking  
**Orchestrator:** con_MuvXIR7jXZjZxlND  
**Created:** 2025-10-30 01:40 ET

---

## Worker Completion Status

| Worker | Status | Thread | Deliverable | Blocker For |
|--------|--------|--------|-------------|-------------|
| W1: Schema | ⏳ PENDING | - | DB migration script | W2, W3, W4, W5, W6 |
| W2: Calculator | ⏳ PENDING | - | team_status_calculator.py | W3, W5, W6 |
| W3: Integration | ⏳ PENDING | - | Updated rpi_calculator.py | W4, W6 |
| W4: Email | ⏳ PENDING | - | coaching_email_system.py | W6 |
| W5: UI | ⏳ PENDING | - | Updated dashboard | W6 |
| W6: Testing | ⏳ PENDING | - | TESTING_REPORT.md | Launch |

---

## Spawn Order

**Phase 1: Foundation (Blocking)**
1. Spawn W1 (Schema) → Wait for completion
2. Spawn W2 (Calculator) → Wait for completion

**Phase 2: Integration (Parallel)**
3. Spawn W3 (Integration) + W4 (Email) + W5 (UI) in parallel
4. Wait for all 3 to complete

**Phase 3: Validation**
5. Spawn W6 (Testing)
6. Wait for sign-off

**Phase 4: Launch**
7. Review W6 report with V
8. Deploy to production if green light

---

## Pre-Launch Validation

Before enabling for V's daily use:

### Database Safety
- [ ] Backup created: `/home/workspace/productivity_tracker.db.backup-YYYYMMDD`
- [ ] Schema migrations tested
- [ ] Rollback procedure documented

### Email System
- [ ] Dry-run tested with all 5 email types
- [ ] V approved email voice/tone
- [ ] Rate limiting configured (max 2 emails/day)
- [ ] Disable flag exists (can turn off emails)

### Dashboard
- [ ] Tested on mobile (375px width)
- [ ] Tested on desktop (1920px width)
- [ ] All 6 status colors verified
- [ ] API endpoints secured

### Calculator Logic
- [ ] Top 5 of 7 math validated
- [ ] Asymmetric movement verified
- [ ] Elite tier unlock tested
- [ ] Edge cases handled

---

## Launch Day Procedure

### Step 1: Backfill Historical Data
```bash
# Run backfill for October
python3 /home/workspace/N5/scripts/productivity/backfill_team_status.py \
  --start-date 2025-10-01 \
  --end-date 2025-10-29 \
  --execute

# Verify results
sqlite3 /home/workspace/productivity_tracker.db \
  "SELECT date, status FROM team_status_history ORDER BY date DESC LIMIT 10;"
```

### Step 2: Enable Daily Auto-Run
```bash
# Confirm rpi_calculator.py includes team status logic
grep -A5 "team_status" /home/workspace/N5/scripts/productivity/rpi_calculator.py

# Test manual run
python3 /home/workspace/N5/scripts/productivity/rpi_calculator.py
```

### Step 3: Verify Dashboard
```bash
# Restart dashboard service
# (Already auto-restarts via user service)

# Check live
curl https://productivity-dashboard-va.zocomputer.io | grep "status-banner"
```

### Step 4: Enable Emails (After V Approval)
```bash
# Set dry-run to false in config
# V will approve after seeing sample emails from W6
```

---

## Post-Launch Monitoring (First Week)

**Daily Checks:**
- [ ] Status calculation runs successfully
- [ ] No duplicate emails sent
- [ ] Dashboard displays correctly
- [ ] Career stats increment properly

**Weekly Review:**
- [ ] V reviews status changes (fair and accurate?)
- [ ] Email tone appropriate?
- [ ] Any bugs or edge cases discovered?

---

## Rollback Procedure (If Needed)

```bash
# 1. Restore database
cp /home/workspace/productivity_tracker.db.backup-YYYYMMDD \
   /home/workspace/productivity_tracker.db

# 2. Revert rpi_calculator.py
git checkout HEAD~1 /home/workspace/N5/scripts/productivity/rpi_calculator.py

# 3. Revert dashboard
git checkout HEAD~1 /home/workspace/Sites/productivity-dashboard/index.tsx

# 4. Restart services
# Dashboard auto-restarts via user service
```

---

## Success Metrics (30 Days Post-Launch)

**Engagement:**
- [ ] V checks dashboard daily
- [ ] V responds positively to coaching emails
- [ ] System motivates consistent performance

**Accuracy:**
- [ ] Status changes align with V's perception
- [ ] No false promotions/demotions
- [ ] Elite tier feels earned, not arbitrary

**Reliability:**
- [ ] Zero crashes or data corruption
- [ ] Email system doesn't spam
- [ ] Dashboard always accessible

---

## Notes for Orchestrator

**Remember:**
- W1 is BLOCKING - don't spawn others until schema is done
- W6 gets final say on launch readiness
- V must approve email tone before enabling auto-send
- Keep BUILD_ORCHESTRATOR.md updated as workers complete

**Communication:**
- Update worker status in real-time
- Flag blockers immediately
- Celebrate completions (this is a big build!)

---

**Last Updated:** 2025-10-30 01:40 ET  
**Status:** Ready to spawn W1
