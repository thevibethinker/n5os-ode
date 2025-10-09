# n5OS Maintenance System - Quick Start

**Status:** 🟢 ACTIVE & OPERATIONAL

---

## What Just Happened?

Your n5OS now has 5 automated maintenance routines running on schedule:

1. ✅ **Daily File Guardian** - Monitors critical files (starts tomorrow 05:30 ET)
2. ✅ **Weekly Workspace Cleanup** - Cleans temp files (starts Monday 03:00 ET)
3. ✅ **Weekly List Health Check** - Validates lists (starts Sunday 20:00 ET)
4. ✅ **Monthly System Audit** - Full system check (starts Nov 1st 20:00 ET)
5. ✅ **Squawk Auto-Proposer** - Generates solutions (starts TODAY 20:30 ET!)

---

## What to Expect Today

### 🎯 First Proposal Generation: TODAY at 20:30 ET

The squawk auto-proposer will:

1. **Analyze** your squawk and system-upgrades lists
2. **Select** the best item (likely `squawk-001: AutoIndex Schema Validation Errors`)
3. **Generate** a comprehensive proposal with:
   - Root cause analysis
   - Step-by-step solution
   - Risk assessment
   - Test validation steps
   - Rollback procedure
   - Clarifying questions for you

4. **Save** to: `N5/maintenance/proposals/squawk_squawk-001_2025-10-09.md`

**You'll need to:** Review the proposal, answer clarifying questions, and approve/modify

---

## What to Expect Tomorrow

### 🛡️ First Daily Guardian: Tomorrow at 05:30 ET

Will check:
- ✅ All critical files exist and non-empty
- ✅ Essential knowledge files intact
- ✅ Git status clean
- ✅ Recent backups exist

**You'll see:** A log at `N5/logs/maintenance/daily/2025-10-10.log`

---

## How to Use the System

### 📝 Add Issues to Be Fixed

**For urgent/critical issues:**
```bash
# Add to squawk list manually, or use the lists-add command
# Items with HIGH priority get addressed first
```

**For planned enhancements:**
```bash
# Add to system-upgrades list
# Items with H (High) priority get addressed first
```

### 📋 Review Proposals

Check `N5/maintenance/proposals/` every 3 days for new proposals:

1. Read the proposal
2. Answer clarifying questions
3. Approve or request modifications
4. Follow implementation steps
5. Run validation tests
6. Mark original item as "completed"

### 📊 Check System Health

```bash
# View latest daily log
tail -50 N5/logs/maintenance/daily/$(date +%Y-%m-%d).log

# View latest list health
ls -lt N5/logs/maintenance/weekly/ | head -3
```

### 🎛️ Manage Scheduled Tasks

Visit: **https://va.zo.computer/schedule**

---

## Manual Testing (Optional)

Want to see it work right now?

```bash
# Test daily guardian
python3 N5/scripts/maintenance/daily_guardian.py

# Test squawk proposer (dry run)
python3 N5/scripts/maintenance/squawk_proposer.py --dry-run

# Generate a proposal right now (for real)
python3 N5/scripts/maintenance/squawk_proposer.py
```

---

## Key Benefits

### 🔄 Passive Functionality Building
- Every 3 days, system proposes solutions to your backlog
- You approve what makes sense
- System capabilities grow incrementally
- Zero pressure, full control

### 🛡️ System Protection
- Critical files monitored daily
- Automatic cleanup prevents bloat
- Git health tracked
- Backups verified

### 📈 Health Visibility
- Lists stay healthy (validated weekly)
- Stale items flagged
- Duplicates detected
- Health scores calculated

### 🧹 Automatic Maintenance
- Old files cleaned automatically
- Logs rotated
- Backups pruned
- Workspace stays tidy

---

## Important Safety Features

### ✅ Conservative Auto-Fix
- Only deletes temp/transient files automatically
- Critical files are **report-only** (never auto-fixed)
- All changes reversible via git/backups

### ✅ Proposal-Based Changes
- Complex changes go through proposal workflow
- You review and approve everything
- Clarifying questions prevent misunderstandings
- Rollback procedures included

### ✅ Full Transparency
- All activities logged
- Can be run manually anytime
- Scheduled tasks visible at va.zo.computer/schedule
- No hidden automation

---

## Quick Reference

### 📁 Key Locations

```
N5/
├── maintenance/
│   ├── README.md ← Proposal system docs
│   ├── QUICKSTART.md ← This file
│   └── proposals/ ← Generated proposals appear here
├── scripts/maintenance/
│   ├── README.md ← Scripts technical docs
│   └── [5 maintenance scripts]
└── logs/maintenance/
    ├── daily/ ← Daily guardian logs
    ├── weekly/ ← Cleanup & list health logs
    ├── monthly/ ← Audit logs
    └── squawk/ ← Proposal generation logs
```

### 🔗 Important Links

- **Scheduled Tasks:** https://va.zo.computer/schedule
- **System Overview:** `file 'N5/MAINTENANCE_SYSTEM.md'`
- **Scripts Docs:** `file 'N5/scripts/maintenance/README.md'`
- **Proposals Docs:** `file 'N5/maintenance/README.md'`

### 📋 Source Lists

- **Squawk List:** `Lists/squawk.jsonl` (critical issues)
- **System Upgrades:** `Lists/system-upgrades.jsonl` (planned enhancements)

---

## Troubleshooting

### ❓ How do I know it's working?

1. Check scheduled tasks: https://va.zo.computer/schedule
2. Look for logs after scheduled runs
3. Check for new proposals in `N5/maintenance/proposals/`

### ❓ What if a task fails?

1. Check the log file for error details
2. Run the script manually to reproduce
3. Add issue to squawk list if it's a bug
4. System will auto-propose a fix!

### ❓ Can I change the schedules?

Yes! Edit them at https://va.zo.computer/schedule

### ❓ What if I don't like a proposal?

- Ignore it (no action required)
- Request modifications by adding clarifying notes
- Add your own implementation approach
- Mark the source item as "won't fix"

---

## Next Actions

1. ✅ **Wait for first proposal** (today at 20:30 ET)
2. ✅ **Review it** when it appears in `N5/maintenance/proposals/`
3. ✅ **Answer clarifying questions** in the proposal
4. ✅ **Decide** whether to implement, modify, or skip
5. ✅ **Monitor logs** after first few runs to ensure health

---

## Philosophy

This maintenance system embodies:

- **Passive progress** - Functionality builds up automatically
- **You're in control** - Nothing happens without your approval
- **Low cognitive load** - Review one proposal every 3 days
- **System health** - Automated monitoring and cleanup
- **Conservative** - Safety first, always reversible

The system works **for you**, not against you. It proposes, you decide.

---

**🎉 Your n5OS maintenance system is live!**

First proposal arriving in ~13 hours. Check back at 20:30 ET today.

**Questions?** Review the docs linked above or ask me!
