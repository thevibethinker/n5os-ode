# Quick Start Guide: Automated Meeting Prep System

**For:** V (Vrijen Attawar)  
**System:** Phase 2B - Complete and Ready  
**Last Updated:** 2025-10-12

---

## What This System Does

Your new automated meeting prep system:

1. **Monitors your calendar every 15 minutes**
2. **Finds meetings with V-OS tags** (LD-INV, LD-HIR, etc.)
3. **Searches your Gmail** for context about each attendee
4. **Creates stakeholder profiles** automatically
5. **Generates digest sections** for your daily briefing
6. **Detects urgent meetings** (marked with *)
7. **Tracks everything** to prevent duplicates

---

## Status: Ready to Activate ✅

Everything is built, tested, and deployed. 

**Only one step remaining:** Create the Zo scheduled task (5 minutes)

---

## Step 1: Create Scheduled Task (Required)

### Go to Zo Schedule

1. Visit: https://va.zo.computer/schedule
2. Click **"Create Task"** button

### Task Configuration

**Name:** Meeting Monitor Cycle

**Schedule (RRULE):**
```
FREQ=HOURLY;INTERVAL=0;BYMINUTE=0,15,30,45
```
(This runs every 15 minutes: on 0, 15, 30, and 45 of each hour)

**Instruction:**
```
Run a single cycle of the meeting monitor system:

1. Call the meeting monitor to check for new meetings
2. Process any meetings with V-OS tags  
3. Generate digest section if new meetings found
4. Log all activity to N5/logs/meeting_monitor.log

Use the run_meeting_monitor.py script with:
- poll_interval_minutes: 15
- lookahead_days: 7

Report any errors or urgent meetings detected.
```

**Model:** `anthropic:claude-sonnet-4-20250514`

**Save the task**

---

## Step 2: Wait for First Cycle (15 minutes)

The task will run at the next 15-minute mark (e.g., 2:00, 2:15, 2:30, 2:45).

**What happens:**
- System checks your calendar
- Looks for events with V-OS tags
- Processes any new meetings
- Creates profiles for stakeholders
- Logs activity

---

## Step 3: Verify It Worked (2 minutes)

### Check the log file:

View: `file 'N5/logs/meeting_monitor.log'`

**You should see:**
```
[2025-10-12 02:15 PM ET] INFO: === Cycle 1 started ===
[2025-10-12 02:15 PM ET] INFO: Cycle complete: X events checked...
[2025-10-12 02:15 PM ET] INFO: Cycle duration: 3.2s
```

### Run health check:

```bash
python3 N5/scripts/monitor_health.py
```

**You should see:**
```
Status: 🟢 HEALTHY

Check Results:
  ✓ Last Cycle Time
  ✓ Log File Status
  ✓ Error Rate
  ✓ Disk Space
  ✓ Profiles
```

---

## What to Expect

### With V-OS Tags (When Howie Adds Them)

When a calendar event has tags like:
```
[LD-INV] [D5+] *

Purpose: Discuss Series A funding

Context: Jane expressed strong interest after intro
```

The system will:
1. ✅ Detect it's a new meeting
2. ✅ Identify stakeholder type (Investor)
3. ✅ See it's urgent (has * marker)
4. ✅ Search Gmail for jane@example.com
5. ✅ Create profile: `N5/records/meetings/2025-10-XX-jane-smith-company/profile.md`
6. ✅ Generate digest section with urgent flag

### Without V-OS Tags (Current State)

If no events have V-OS tags:
- System runs normally
- Checks calendar
- Finds no tagged events
- Logs "0 new events"
- Waits for next cycle

**This is normal!** Once Howie adds V-OS tags, the system will process them automatically.

---

## Daily Workflow

### Morning: Check Dashboard

```bash
python3 N5/scripts/generate_dashboard.py
```

Or view: `file 'N5/records/dashboards/latest-dashboard.md'`

**You'll see:**
- How many cycles ran yesterday (should be ~96)
- How many meetings processed
- Any urgent meetings detected
- System health status

### As Needed: Check Health

```bash
python3 N5/scripts/monitor_health.py
```

**Status meanings:**
- 🟢 **Healthy** - Everything working perfectly
- 🟡 **Warnings** - Minor issues, monitor
- 🔴 **Critical** - Needs attention now

### Weekly: Review Profiles

Browse: `N5/records/meetings/`

You'll find directories like:
```
2025-10-15-jane-smith-acme-ventures/
  └── profile.md
```

Each profile includes:
- Contact info
- Context from Howie
- Email history from Gmail
- Meeting history
- Relationship notes

---

## Where Things Are Stored

### Logs
- **Main log:** `N5/logs/meeting_monitor.log`
- **Health checks:** `N5/logs/health_check.log`
- **Archived logs:** `N5/logs/archived/`

### Data
- **State tracking:** `N5/records/meetings/.processed.json`
- **Stakeholder profiles:** `N5/records/meetings/{date-name-org}/profile.md`
- **Digests:** `N5/records/digests/`
- **Dashboards:** `N5/records/dashboards/`

### Configuration
- **System config:** `N5/config/meeting_monitor_config.json`
- **Task spec:** `N5/config/scheduled_task_spec.json`

---

## Common Questions

### Q: When will I see profiles created?

**A:** As soon as you have calendar events with V-OS tags. Once Howie implements Phase 2A and starts adding tags like `[LD-INV]` or `[LD-HIR]` to your meetings, profiles will be created automatically within 15 minutes.

### Q: What if I see errors in the log?

**A:** Run the health check (`python3 N5/scripts/monitor_health.py`). It will tell you what's wrong and recommend fixes. Most common issues are:
- API access problems (need to reconnect Google)
- Network connectivity
- Malformed calendar data

### Q: How do I know if the system is working?

**A:** Three ways:
1. Check the log file (should show regular cycles)
2. Run health check (should show 🟢 healthy)
3. View dashboard (should show recent cycles)

### Q: Can I change the polling interval?

**A:** Yes! Edit `N5/config/meeting_monitor_config.json` and change `poll_interval_minutes`. Then update the scheduled task's RRULE to match.

### Q: How much disk space does this use?

**A:** Very little:
- Logs: ~1 MB per day (auto-rotated after 30 days)
- Profiles: ~5-10 KB each
- State file: ~100 KB
- Total: < 100 MB even after months of use

---

## Maintenance

### Daily (Automatic)
- ✅ Cycles run every 15 minutes
- ✅ State file updated
- ✅ Profiles created/updated
- ✅ Logs written

### Weekly (Manual - 2 minutes)
- Run dashboard: `python3 N5/scripts/generate_dashboard.py`
- Review for trends
- Check for errors

### Monthly (Manual - 5 minutes)
- Review full dashboard
- Rotate logs: `python3 N5/scripts/rotate_logs.py`
- Check disk usage
- Archive old profiles if needed

---

## Troubleshooting

### Issue: Health check shows red status

**Fix:**
1. Look at the specific check that failed
2. View recent log entries
3. Most common: scheduled task isn't running
4. Solution: Check task is active in Zo

### Issue: No profiles being created

**Possible causes:**
1. No calendar events with V-OS tags yet ← Most likely
2. API access issue
3. Scheduled task not running

**Check:**
- Look at log file - are cycles running?
- Do you have events with tags like `[LD-INV]`?
- Is Gmail search working?

### Issue: Dashboard shows low coverage

**Meaning:** Not all expected cycles ran

**Fix:**
1. Check scheduled task is active
2. Look for patterns (e.g., missing during certain hours)
3. Check for API rate limiting
4. Monitor for 24 hours

---

## Support

### Check Documentation
- `file 'N5/docs/PHASE-2B-COMPLETE.md'` - Full system overview
- `file 'N5/docs/DEPLOYMENT-REPORT.md'` - Deployment details
- `file 'N5/docs/PHASE-2B-PRIORITY-X-COMPLETE.md'` - Priority-specific docs

### Run Diagnostics
```bash
# Health check
python3 N5/scripts/monitor_health.py

# Dashboard
python3 N5/scripts/generate_dashboard.py

# Check logs
tail -50 N5/logs/meeting_monitor.log
```

### Contact Zo Team
Use the "Report an issue" button in Zo if you encounter problems.

---

## Next Steps

1. ✅ **Create scheduled task** (Step 1 above)
2. ⏰ **Wait 15 minutes** for first cycle
3. ✓ **Verify it worked** (check logs)
4. 📊 **Check dashboard daily**
5. 🎉 **Enjoy automated meeting prep!**

---

## System is Ready! 🎉

Everything is built and deployed. Just create the scheduled task and you're live.

**Questions?** Check the documentation in `file 'N5/docs/'` or run health checks.

**Enjoy your automated meeting intelligence system!**

---

**Quick Start Guide**  
**Version:** 1.0  
**Last Updated:** 2025-10-12  
**System Status:** ✅ Ready for Production
